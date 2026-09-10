import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync, readFileSync, statSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PhotoshopQueue, QueueError, fileEvidence } from '../scripts/queue-core.mjs';
import { QueueService, startBroker, queueDefinitions } from '../scripts/broker.mjs';
import { retainLease, bindTaskRequest, loadLeaseSession, saveLeaseSession, reclaimStartLock, buildResumeCheck } from '../scripts/queue-client.mjs';

// All native handlers and PSD/PNG bytes here are synthetic. No Photoshop calls.
const scratch = resolve(dirname(fileURLToPath(import.meta.url)), '.test-data');
mkdirSync(scratch, { recursive: true });
const result = (data, isError = false) => ({ content: [{ type: 'text', text: JSON.stringify(data) }], structuredContent: data, ...(isError ? { isError: true } : {}) });
const stateFor = (doc, saved = false) => ({ hasDocument: doc !== null, documentCount: doc === null ? 0 : 1, activeDocument: doc === null ? null : { id: doc, title: `Synthetic ${doc}`, saved } });
function fakeNative() {
  const fake = { tools: new Map(), calls: [], state: stateFor(101), command: null, probe: null, bridge: { status: () => ({ connected: true }), stop: async () => {} } };
  fake.catalog = { get: id => ({ id, status: 'supported', risk: id === 'document.export' ? 'external' : id === 'document.inspect' ? 'read' : 'edit', engine: 'dom' }), validate: (_id, args) => args, list: () => [] };
  const register = (name, handler) => fake.tools.set(name, { definition: { name, inputSchema: { type: 'object' } }, handler });
  register('photoshop_host_describe', async () => result({ serverVersion: 'synthetic', runtime: { app: 'Photoshop' }, bridge: fake.bridge.status() }));
  register('photoshop_state_get', async () => { fake.calls.push({ kind: 'state' }); return fake.probe ? await fake.probe() : result(fake.state); });
  register('photoshop_preview_get', async () => result({ preview: 'synthetic' }));
  register('photoshop_command_execute', async args => {
    fake.calls.push({ kind: 'command', args });
    if (fake.command) return await fake.command(args);
    return result({ ok: true, status: 'completed', result: { commandId: args.command_id, result: { marker: args.args?.marker }, before: fake.state, after: fake.state }, after: fake.state });
  });
  register('photoshop_advanced_execute', async () => { throw new Error('Unadapted tools must never execute'); });
  register('photoshop_command_validate', async () => { throw new Error('Unadapted tools must never execute'); });
  return fake;
}
function fixture(t) {
  const root = mkdtempSync(join(scratch, 'broker-')), path = join(root, 'queue.sqlite');
  let clock = 1000;
  const connections = [], options = { roots: [root], now: () => clock, idleMs: 50, staleMs: 100 };
  const open = () => { const q = new PhotoshopQueue(path, options); connections.push(q); return q; };
  const q = open(), native = fakeNative(), api = new QueueService(q, native);
  t.after(() => {
    for (const c of connections) { try { c.close(); } catch {} }
    assert.equal(dirname(resolve(root)), scratch);
    rmSync(root, { recursive: true, force: true });
  });
  return { root, path, q, native, api, open, advance: ms => { clock += ms; } };
}
function acquire(q, task = 'task-A', asset = 'image-A') {
  const ticket = q.enqueue({ task_id: task, asset_id: asset, description: 'Synthetic test image.', ready: true });
  const owner = q.acquire({ task_id: task, ticket: ticket.ticket }); assert.equal(owner.acquired, true); return owner;
}
const args = (key = 'request-1', marker = 'first') => ({ command_id: 'layer.rename', args: { marker }, idempotency_key: key });
const rows = q => q.db.prepare('SELECT * FROM native_requests ORDER BY task_id,asset_id,external_key').all();
const rejectCode = (p, expected) => assert.rejects(p, e => e?.code === expected);
function bind(q, owner, doc = 101) {
  const op = q.begin(owner, { mutates: false, expected_until: 1050 }); q.end(owner, op.id, { documentId: doc });
}
function saved(q, owner, root, doc = 101) {
  const files = ['working.psd', 'review.png'].map(name => {
    const path = join(root, name); writeFileSync(path, `synthetic ${name}`);
    const op = q.begin(owner, { command_id: 'document.export', mutates: false, expected_until: 1050 });
    q.end(owner, op.id, { documentId: doc, exported: fileEvidence(path, [root]) });
    return { path, role: name.endsWith('.psd') ? 'working' : 'review' };
  });
  return q.checkpoint(owner, { files, document_id: doc, resume: 'Resume this synthetic test PSD.' });
}
function closeDocument(q, owner) {
  const op = q.begin(owner, { command_id: 'document.close', mutates: false, resource_cleanup: true, expected_until: 1050 });
  q.end(owner, op.id, { applied: true, documentId: q.read().owner.document_id });
}
function deferred() { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; }

test('waiting acquire automatically fences stale unchanged owner and preserves FIFO', async t => {
  const { api, q, native, advance } = fixture(t);
  native.state = stateFor(null);
  const old = acquire(q);
  const b = q.enqueue({ task_id: 'task-B', asset_id: 'image-B', description: 'waiting test', ready: true });
  const c = q.enqueue({ task_id: 'task-C', asset_id: 'image-C', description: 'waiting test', ready: true });
  advance(101);
  assert.equal((await api.control('acquire', { task_id: 'task-C', ticket: c.ticket }, {})).acquired, false);
  const next = await api.control('acquire', { task_id: 'task-B', ticket: b.ticket }, {});
  assert.equal(next.acquired, true);
  assert.equal(next.recovery.released, true);
  assert.throws(() => q.heartbeat(old), e => e.code === 'STALE_LEASE');
  assert.ok(native.calls.some(x => x.kind === 'state'));
});

test('heartbeat cannot perpetuate five-minute idle occupation; live command is preserved', async t => {
  const { api, q, native, advance } = fixture(t); native.state = stateFor(null);
  const old = acquire(q);
  const b = q.enqueue({ task_id: 'task-B', asset_id: 'image-B', description: 'waiting test', ready: true });
  q.abandonedMs = 200;
  advance(201); q.heartbeat(old);
  const op = q.begin(old, { mutates: false, expected_until: 2000 });
  assert.equal((await api.control('acquire', { task_id: 'task-B', ticket: b.ticket }, {})).acquired, false);
  q.end(old, op.id, {});
  advance(201); q.heartbeat(old);
  assert.equal((await api.control('acquire', { task_id: 'task-B', ticket: b.ticket }, {})).acquired, true);
});

test('failed live probe keeps one recovery owner and same waiter retries without approval', async t => {
  const { api, q, native, advance } = fixture(t);
  native.state = stateFor(null); acquire(q); const b = q.enqueue({ task_id: 'task-B', asset_id: 'image-B', description: 'waiting test', ready: true });
  advance(101); native.probe = async () => { throw new Error('offline'); };
  const pending = await api.control('acquire', { task_id: 'task-B', ticket: b.ticket }, {});
  assert.equal(pending.acquired, false); assert.equal(pending.recovery.released, false);
  assert.equal(q.read().owner.recovering, true);
  native.probe = null;
  assert.equal((await api.control('acquire', { task_id: 'task-B', ticket: b.ticket }, {})).acquired, true);
});

test('automatic recovery saves dirty original work before closing and grants waiter', async t => {
  const { api, q, native, advance, root } = fixture(t);
  const old = acquire(q); bind(q, old);
  const edit = q.begin(old, { mutates: true, expected_until: 2000 }); q.end(old, edit.id, { documentId: 101 });
  native.state = { hasDocument: true, documentCount: 1, activeDocument: { id: 101 } };
  native.command = async a => {
    if (a.command_id === 'document.close') {
      assert.ok(q.read().owner.checkpoint);
      native.state = { hasDocument: false, documentCount: 0 };
      return result({ ok: true, after: native.state });
    }
    assert.equal(a.command_id, 'document.export');
    const path = join(root, a.args.file_name); writeFileSync(path, 'rescue fixture');
    return result({ ok: true, result: { result: { path } }, after: native.state });
  };
  const b = q.enqueue({ task_id: 'task-B', asset_id: 'image-B', description: 'waiting', ready: true });
  advance(101);
  const next = await api.control('acquire', { task_id: 'task-B', ticket: b.ticket }, {});
  assert.equal(next.acquired, true);
  assert.equal(q.read().reviews['task-A'].status, 'WAITING_REVIEW');
  assert.equal(q.read().reviews['task-A'].checkpoint.files.length, 2);
  assert.deepEqual(native.calls.filter(x => x.kind === 'command').map(x => x.args.command_id), ['document.export', 'document.export', 'document.close']);
});

test('automatic recovery never exports a different active document', async t => {
  const { api, q, native, advance } = fixture(t);
  const old = acquire(q); bind(q, old);
  const op = q.begin(old, { mutates: true, expected_until: 2000 }); q.end(old, op.id, { documentId: 101 });
  native.state = { hasDocument: true, documentCount: 1, activeDocument: { id: 999 } };
  const b = q.enqueue({ task_id: 'task-B', asset_id: 'image-B', description: 'waiting', ready: true });
  advance(101);
  const r = await api.control('acquire', { task_id: 'task-B', ticket: b.ticket }, {});
  assert.equal(r.recovery.code, 'RECOVERY_DOCUMENT_MISMATCH');
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 0);
});

test('completed same-key replay returns original result without native execution or new queue evidence', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q);
  const first = await api.call('photoshop_command_execute', args(), owner);
  const before = q.read(), eventCount = q.db.prepare('SELECT COUNT(*) AS n FROM events').get().n;
  const second = await api.call('photoshop_command_execute', { idempotency_key: 'request-1', args: { marker: 'first' }, command_id: 'layer.rename' }, owner);
  assert.deepEqual(second, first); assert.deepEqual(q.read(), before);
  assert.equal(q.db.prepare('SELECT COUNT(*) AS n FROM events').get().n, eventCount);
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 1);
  assert.equal(rows(q)[0].status, 'completed');
  assert.notEqual(native.calls.find(x => x.kind === 'command').args.idempotency_key, 'request-1');
});

test('same key with different payload is rejected before invoking native or touching the queue', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q);
  await api.call('photoshop_command_execute', args(), owner); const before = q.read();
  await rejectCode(api.call('photoshop_command_execute', args('request-1', 'different'), owner), 'IDEMPOTENCY_PAYLOAD_MISMATCH');
  assert.deepEqual(q.read(), before); assert.equal(native.calls.filter(x => x.kind === 'command').length, 1);
});

test('different tasks using the same external key get separate durable and native keys', async t => {
  const { api, q, native, root } = fixture(t); const a = acquire(q);
  const first = await api.call('photoshop_command_execute', args('shared', 'A'), a);
  saved(q, a, root); closeDocument(q, a); q.release(a); const b = acquire(q, 'task-B', 'image-B');
  const second = await api.call('photoshop_command_execute', args('shared', 'B'), b);
  assert.equal(first.structuredContent.result.result.marker, 'A'); assert.equal(second.structuredContent.result.result.marker, 'B');
  const records = rows(q); assert.equal(records.length, 2); assert.notEqual(records[0].scoped_key, records[1].scoped_key);
  const calls = native.calls.filter(x => x.kind === 'command'); assert.notEqual(calls[0].args.idempotency_key, calls[1].args.idempotency_key);
});

test('different assets in the same task do not share an idempotency scope', async t => {
  const { api, q, native, root } = fixture(t); const a = acquire(q);
  await api.call('photoshop_command_execute', args('shared'), a);
  const cp = saved(q, a, root); closeDocument(q, a); q.release(a);
  q.review({ task_id: a.task_id, asset_id: a.asset_id }, { valid: true, status: 'FAIL', sha256: cp.files.find(f => f.role === 'review').sha256, synthetic: true });
  const b = acquire(q, 'task-A', 'image-B'); await api.call('photoshop_command_execute', args('shared'), b);
  assert.equal(rows(q).length, 2); assert.equal(native.calls.filter(x => x.kind === 'command').length, 2);
});

test('running duplicate is refused and does not send another Photoshop command', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q), wait = deferred();
  native.command = () => wait.promise;
  const first = api.call('photoshop_command_execute', args(), owner);
  await rejectCode(api.call('photoshop_command_execute', args(), owner), 'NATIVE_REQUEST_RUNNING');
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 1);
  wait.resolve(result({ ok: true, status: 'completed', after: native.state, result: {} })); await first;
});

test('native timeout stays UNKNOWN and is never automatically replayed', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q);
  native.command = async () => result({ ok: false, status: 'failed', error: { code: 'TIMEOUT' } }, true);
  const outcome = await api.call('photoshop_command_execute', args(), owner);
  assert.equal(outcome.isError, true); assert.equal(rows(q)[0].status, 'unknown'); assert.ok(q.read().owner.unknown);
  await rejectCode(api.call('photoshop_command_execute', args(), owner), 'NATIVE_REQUEST_UNKNOWN');
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 1);
});

test('restart turns durable running requests into UNKNOWN and keeps completed receipts reusable', async t => {
  const f = fixture(t); const owner = acquire(f.q);
  await f.api.call('photoshop_command_execute', args('completed'), owner);
  // Simulate the crash window after durable request admission and command begin.
  const identity = f.api.requestIdentity('photoshop_command_execute', args('interrupted'), f.q.read().owner);
  f.api.startRequest(identity, 'photoshop_command_execute', f.q.read().owner);
  f.q.begin(owner, { mutates: true, expected_until: 1050 });
  const q2 = f.open(); q2.recoverAfterRestart(); const native2 = fakeNative(), restarted = new QueueService(q2, native2);
  assert.equal(rows(q2).find(r => r.external_key === 'interrupted').status, 'unknown');
  await rejectCode(restarted.call('photoshop_command_execute', args('interrupted'), owner), 'NATIVE_REQUEST_UNKNOWN');
  const receipt = await restarted.call('photoshop_command_execute', args('completed'), owner);
  assert.equal(receipt.structuredContent.ok, true); assert.equal(native2.calls.length, 0);
  assert.ok(q2.read().owner.unknown);
});

test('a mismatching live document fails before command_begin without dirtying, losing the checkpoint, or leaving an unknown request', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); bind(q, owner); saved(q, owner, root);
  native.state = stateFor(202); const before = q.read();
  await rejectCode(api.call('photoshop_command_execute', args(), owner), 'ACTIVE_DOCUMENT_CHANGED');
  assert.deepEqual(q.read(), before); assert.equal(native.calls.filter(x => x.kind === 'command').length, 0);
  assert.equal(rows(q).length, 0); assert.equal(api.busy, false);
});

test('preflight state awaits hold the broker mutex and block release without creating an unknown request', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q); bind(q, owner);
  const wait = deferred(); native.probe = () => wait.promise;
  const first = api.call('photoshop_command_execute', args(), owner);
  assert.equal(q.read().owner.in_flight, null);
  await rejectCode(api.control('release', {}, owner), 'COMMAND_STILL_RUNNING');
  await rejectCode(api.call('photoshop_state_get', {}, owner), 'COMMAND_STILL_RUNNING');
  wait.reject(new QueueError('TIMEOUT', 'Synthetic preflight timeout.'));
  await rejectCode(first, 'TIMEOUT');
  assert.equal(q.read().owner.dirty, false); assert.equal(q.read().owner.unknown, null);
  assert.equal(rows(q).length, 0);
});

test('native exceptions preserve their original cause when queue settlement also fails', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q);
  const original = new QueueError('NATIVE_ROOT_CAUSE', 'Synthetic native rejection.');
  native.command = async () => { throw original; };
  const realEnd = q.end.bind(q); q.end = () => { throw new QueueError('SETTLEMENT_FAILED', 'Synthetic SQLite failure.'); };
  try {
    await assert.rejects(api.call('photoshop_command_execute', args(), owner), e => e === original && e.queue_settlement_error.code === 'SETTLEMENT_FAILED');
    assert.equal(rows(q)[0].status, 'unknown'); assert.ok(q.read().owner.in_flight);
  } finally { q.end = realEnd; }
});

test('a command completion that already committed is never sent through queue.end twice', async t => {
  const { api, q } = fixture(t); const owner = acquire(q); const realEnd = q.end.bind(q); let count = 0;
  q.end = (...arguments_) => { count++; realEnd(...arguments_); throw new QueueError('AFTER_COMMIT_ERROR', 'Synthetic post-commit failure.'); };
  await rejectCode(api.call('photoshop_command_execute', args(), owner), 'AFTER_COMMIT_ERROR');
  assert.equal(count, 1); assert.equal(q.read().owner.in_flight, null); assert.equal(rows(q)[0].status, 'unknown');
});

test('real nested export receipts are hashed once; completed replay creates no additional export evidence', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); bind(q, owner);
  const path = join(root, 'nested.png'); writeFileSync(path, 'synthetic PNG export');
  native.command = async () => result({ ok: true, status: 'completed', result: { commandId: 'document.export', result: { path, destination: 'default_export_folder' }, after: native.state } });
  const input = { command_id: 'document.export', args: { format: 'png' }, idempotency_key: 'export' };
  await api.call('photoshop_command_execute', input, owner);
  assert.equal(q.read().owner.exports.length, 1); assert.equal(q.read().owner.exports[0].document_id, 101);
  const before = q.read(); await api.call('photoshop_command_execute', input, owner); assert.deepEqual(q.read(), before);
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 1);
});

test('selected-folder export without a path cannot fabricate checkpoint evidence', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q); bind(q, owner);
  native.command = async () => result({ ok: true, status: 'completed', result: { result: { name: 'test.png', destination: 'selected_folder' }, after: native.state } });
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.export', args: {}, idempotency_key: 'export' }, owner), 'EXPORT_EVIDENCE_MISSING');
  assert.deepEqual(q.read().owner.exports, []); assert.ok(q.read().owner.unknown); assert.equal(rows(q)[0].status, 'unknown');
});

test('unadapted advanced and validation tools are rejected before any Photoshop handler', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q);
  await rejectCode(api.call('photoshop_advanced_execute', {}, owner), 'UNADAPTED_NATIVE_TOOL');
  await rejectCode(api.call('photoshop_command_validate', {}, owner), 'UNADAPTED_NATIVE_TOOL');
  assert.equal(native.calls.length, 0); assert.equal(q.read().owner.dirty, false);
});

test('safe document close preserves its current exported checkpoint and original document identity', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q);
  await api.call('photoshop_command_execute', args(), owner); const cp = saved(q, owner, root);
  native.command = async input => { assert.equal(input.command_id, 'document.close'); native.state = stateFor(null); return result({ ok: true, status: 'completed', after: native.state, result: { result: { closed: true }, after: native.state } }); };
  await api.call('photoshop_command_execute', { command_id: 'document.close', args: {}, idempotency_key: 'close' }, owner);
  assert.deepEqual(q.read().owner.checkpoint, cp); assert.equal(q.read().owner.document_id, 101);
  assert.equal(q.read().owner.in_flight, null); assert.equal(q.release(owner).status, 'WAITING_REVIEW');
});

test('document close without checkpoint or with changed saved bytes never reaches Photoshop', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); bind(q, owner);
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.close', args: {}, idempotency_key: 'close-no-checkpoint' }, owner), 'CLOSE_CHECKPOINT_REQUIRED');
  const cp = saved(q, owner, root); writeFileSync(cp.files[0].path, 'changed externally');
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.close', args: {}, idempotency_key: 'close-changed-checkpoint' }, owner), 'CHECKPOINT_CHANGED');
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 0); assert.equal(q.read().owner.unknown, null);
});

test('allowed-root source open binds one clean document and can close without fake save evidence', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); native.state = stateFor(null);
  const source = join(root, 'source.png'); writeFileSync(source, 'synthetic source');
  native.command = async input => {
    if (input.command_id === 'document.open_allowed') {
      native.state = stateFor(202, true);
      return result({ ok: true, status: 'completed', result: { result: { id: 202 } }, after: native.state });
    }
    assert.equal(input.command_id, 'document.close');
    native.state = stateFor(null);
    return result({ ok: true, status: 'completed', result: { result: { closedDocumentId: 202 } }, after: native.state });
  };
  await api.call('photoshop_command_execute', { command_id: 'document.open_allowed', args: { path: source }, idempotency_key: 'open-source' }, owner);
  assert.equal(q.read().owner.document_id, 202);
  assert.equal(q.read().owner.opened_by_queue, true);
  assert.equal(q.read().owner.dirty, false);
  assert.equal(q.read().owner.mutation, 0);
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.open_allowed', args: { path: source }, idempotency_key: 'open-source-again' }, owner), 'LEASE_DOCUMENT_ALREADY_BOUND');
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 1);
  await api.call('photoshop_command_execute', { command_id: 'document.close', args: { save: false }, idempotency_key: 'close-clean-source' }, owner);
  assert.equal(q.release(owner).status, 'NO_IMAGE_CHANGE');
});

test('state and preview reads never create an unknown queue command', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q); bind(q, owner, 101); native.state = stateFor(101, true);
  const state = await api.call('photoshop_state_get', {}, owner);
  const preview = await api.call('photoshop_preview_get', { max_edge: 64 }, owner);
  assert.equal(state.isError, undefined); assert.equal(preview.isError, undefined);
  assert.equal(q.read().owner.in_flight, null); assert.equal(q.read().owner.unknown, null);
});

test('serialized recovery probe must resolve before a recovered lease can release', async t => {
  const { api, q, native, advance } = fixture(t); acquire(q); advance(101);
  const recovery = q.recoverClaim({ task_id: 'recovery' }), wait = deferred(); native.probe = () => wait.promise;
  const probe = api.control('probe', {}, recovery);
  await rejectCode(api.control('release', {}, recovery), 'COMMAND_STILL_RUNNING');
  assert.equal(q.read().owner.barrier, null);
  wait.resolve(result(native.state)); await probe;
  assert.ok(q.read().owner.barrier); assert.equal((await api.control('release', {}, recovery)).status, 'NO_IMAGE_CHANGE');
});

test('the public manual reservation tool accepts explicit user-confirmed release by another task', async t => {
  const { api } = fixture(t);
  const schema = queueDefinitions().find(x => x.name === 'photoshop_queue_external').inputSchema;
  assert.deepEqual(schema.required, ['task_id', 'active']);
  assert.equal(schema.properties.user_confirmed_finished.type, 'boolean');
  assert.equal(schema.properties.confirmation_note.type, 'string');
  await api.control('external', { task_id: 'task-A', active: true, note: 'Manual work.' }, {});
  await rejectCode(api.control('external', { task_id: 'task-B', active: false }, {}), 'EXTERNAL_OWNER_MISMATCH');
  const released = await api.control('external', { task_id: 'task-B', active: false, user_confirmed_finished: true, confirmation_note: 'Current task-B user message says the manual work is finished.' }, {});
  assert.equal(released.external, null); assert.equal(released.manual_release.declarer_task_id, 'task-A');
  assert.equal(released.manual_release.released_by, 'task-B');
});

test('second broker startup cannot reset the first broker in-flight journal', async t => {
  const { root } = fixture(t); const native = fakeNative(); const stateDir = join(root, 'singleton');
  const first = await startBroker({ native, stateDir, port: 0 });
  try {
    const owner = acquire(first.api.queue); const op = first.api.queue.begin(owner, { mutates: true, expected_until: Date.now() + 1000 });
    const port = first.server.address().port;
    await assert.rejects(startBroker({ native: fakeNative(), stateDir, port }), e => e.code === 'EADDRINUSE');
    assert.equal(first.api.queue.read().owner.in_flight.id, op.id); assert.equal(first.api.queue.read().owner.unknown, null);
  } finally { await first.close(); }
});

test('broker watchdog expires unused waiting tickets without touching Photoshop or active manual use', async t => {
  const { root } = fixture(t); const native = fakeNative();
  const broker = await startBroker({ native, stateDir: join(root, 'expiry-watchdog'), port: 0 });
  try {
    const q = broker.api.queue;
    q.external({ task_id: 'human', active: true, note: 'Manual work continues.' });
    q.enqueue({ task_id: 'departed-task', asset_id: 'unused-image', description: 'Unused waiting ticket.', ready: true });
    q.tx('synthetic_expired_waiting_time', s => { s.waiting[0].waiting_last_seen_at = Date.now() - 300001; return {}; });
    assert.equal((await broker.api.control('status', {}, {})).waiting.length, 1);
    await new Promise(resolve => setTimeout(resolve, 5300));
    assert.equal(q.read().waiting.length, 0); assert.equal(q.read().external.status, 'ACTIVE');
    assert.equal(native.calls.length, 0);
    assert.equal(q.db.prepare("SELECT COUNT(*) AS n FROM events WHERE kind='waiting_expired'").get().n, 1);
  } finally { await broker.close(); }
});

test('client discards fenced leases and a new enqueue never inherits stale credentials', () => {
  const stale = { task_id: 'task-A', ticket: 7, epoch: 9, token: 'secret', device_id: 'old-device', broker_instance_id: 'old-broker' };
  const fenced = retainLease(stale, 'photoshop_queue_release', result({ ok: false, code: 'STALE_LEASE' }, true));
  assert.deepEqual(fenced, { task_id: 'task-A' });
  const expired = retainLease(stale, 'photoshop_queue_acquire', result({ acquired: false, reason: 'TICKET_NOT_WAITING' }));
  assert.deepEqual(expired, { task_id: 'task-A' });
  const enqueued = retainLease(stale, 'photoshop_queue_enqueue', result({ task_id: 'task-A', ticket: 12 }));
  assert.deepEqual(enqueued, { task_id: 'task-A', ticket: 12 });
});

test('a lost same-task client context is rebound, probed, and resumed without waiting for stale timeout', async t => {
  const { api, q } = fixture(t); const owner = acquire(q);
  const rebound = await api.control('acquire', { task_id: owner.task_id, ticket: owner.ticket }, {});
  assert.equal(rebound.acquired, true); assert.equal(rebound.rebound, true);
  assert.equal(rebound.probe.production_resumed, true); assert.ok(rebound.epoch > owner.epoch);
  assert.equal(q.read().owner.recovering, false);
  assert.throws(() => q.heartbeat(owner), e => ['STALE_LEASE', 'BROKER_INSTANCE_CHANGED'].includes(e.code));
});

test('a waiting head recovers an idle owner immediately after broker restart', async t => {
  const { q, native } = fixture(t); native.state = stateFor(null); const old = acquire(q);
  const waiting = q.enqueue({ task_id: 'task-B', asset_id: 'image-B', description: 'Ready input.', ready: true });
  q.recoverAfterRestart(); const api = new QueueService(q, native);
  const next = await api.control('acquire', { task_id: 'task-B', ticket: waiting.ticket }, {});
  assert.equal(next.acquired, true); assert.equal(next.recovery.released, true);
  assert.equal(q.read().owner.task_id, 'task-B');
  assert.throws(() => q.heartbeat(old), e => ['STALE_LEASE', 'BROKER_INSTANCE_CHANGED'].includes(e.code));
});

test('a disconnected bridge keeps the head ticket alive instead of creating a stranded owner', async t => {
  const { api, q, native } = fixture(t);
  const waiting = q.enqueue({ task_id: 'task-A', asset_id: 'image-A', description: 'Ready input.', ready: true });
  native.bridge.status = () => ({ paired: true, connected: false, pluginInstanceId: 'bridge-1' });
  const blocked = await api.control('acquire', { task_id: 'task-A', ticket: waiting.ticket }, {});
  assert.equal(blocked.reason, 'HOST_PREFLIGHT_FAILED'); assert.equal(blocked.code, 'BRIDGE_DISCONNECTED');
  assert.equal(q.read().owner, null); assert.equal(q.read().waiting[0].ticket, waiting.ticket);
  native.bridge.status = () => ({ paired: true, connected: true, pluginInstanceId: 'bridge-1' });
  native.state = stateFor(null);
  assert.equal((await api.control('acquire', { task_id: 'task-A', ticket: waiting.ticket }, {})).acquired, true);
});

test('a changed bridge instance requires a live document barrier and then resumes the same lease', async t => {
  const { api, q, native } = fixture(t);
  native.bridge.status = () => ({ paired: true, connected: true, pluginInstanceId: 'bridge-1' });
  const ticket = q.enqueue({ task_id: 'task-A', asset_id: 'image-A', description: 'Ready input.', ready: true });
  const owner = q.acquire({ task_id: 'task-A', ticket: ticket.ticket }, { bridge_instance_id: 'bridge-1' }); bind(q, owner);
  native.bridge.status = () => ({ paired: true, connected: true, pluginInstanceId: 'bridge-2' });
  await rejectCode(api.call('photoshop_command_execute', args('after-reconnect'), owner), 'BRIDGE_SESSION_CHANGED');
  assert.equal(q.read().owner.recovery_mode, 'BRIDGE_RECONNECT');
  const probe = await api.control('probe', {}, owner); assert.equal(probe.production_resumed, true);
  assert.equal((await api.call('photoshop_command_execute', args('after-reconnect'), owner)).structuredContent.ok, true);
});

test('atomic handoff exports both formats, checkpoints, closes, and releases without interleaving', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); bind(q, owner);
  const edit = q.begin(owner, { command_id: 'synthetic.edit', mutates: true, expected_until: 2000 }); q.end(owner, edit.id, { documentId: 101 });
  native.command = async input => {
    if (input.command_id === 'document.close') { native.state = stateFor(null); return result({ ok: true, status: 'completed', result: { result: { closed: true } }, after: native.state }); }
    const path = join(root, input.args.file_name); writeFileSync(path, `synthetic ${input.args.format}`);
    return result({ ok: true, status: 'completed', result: { result: { path } }, after: native.state });
  };
  const handed = await api.control('handoff', { file_prefix: 'asset-A-safe', resume: 'Open the verified PSD and inspect the PNG before further edits.', close: true }, owner);
  assert.equal(handed.handoff, true); assert.equal(handed.closed, true); assert.equal(handed.release.status, 'WAITING_REVIEW');
  assert.equal(q.read().owner, null); assert.equal(handed.checkpoint.files.length, 2);
  assert.equal(handed.checkpoint.device_id, q.deviceId);
  assert.deepEqual(native.calls.filter(x => x.kind === 'command').map(x => x.args.command_id), ['document.export', 'document.export', 'document.close']);
});

test('clean handoff closes a queue-opened source and handoff can never release an open document', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q);
  const open = q.begin(owner, { command_id: 'document.open_allowed', mutates: false, expected_until: 1050 });
  q.end(owner, open.id, { documentId: 606, documentOpened: true }); native.state = stateFor(606, true);
  await rejectCode(api.control('handoff', { resume: 'No changes.', close: false }, owner), 'HANDOFF_CLOSE_REQUIRED');
  assert.throws(() => q.release(owner), error => error.code === 'DOCUMENT_STILL_OPEN');
  native.command = async input => { assert.equal(input.command_id, 'document.close'); native.state = stateFor(null); return result({ ok: true, status: 'completed', result: { result: { closedDocumentId: 606 } }, after: native.state }); };
  const handoff = await api.control('handoff', { resume: 'No changes.' }, owner);
  assert.equal(handoff.closed, true); assert.equal(handoff.release.status, 'NO_IMAGE_CHANGE'); assert.equal(q.read().owner, null);
});

test('an unmanaged open Photoshop document keeps the waiting ticket instead of granting a dangerous lease', async t => {
  const { api, q, native } = fixture(t); native.state = stateFor(999, true);
  const waiting = q.enqueue({ task_id: 'task-A', asset_id: 'image-A', description: 'Ready input.', ready: true });
  const blocked = await api.control('acquire', { task_id: 'task-A', ticket: waiting.ticket }, {});
  assert.equal(blocked.acquired, false); assert.equal(blocked.code, 'UNMANAGED_DOCUMENT_OPEN');
  assert.equal(q.read().owner, null); assert.equal(q.read().waiting[0].ticket, waiting.ticket);
});

test('ambiguous default-folder import and unkeyed or typed commands are rejected before Photoshop', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q); native.state = stateFor(null);
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.open_default', args: { file_name: 'x.png' }, idempotency_key: 'unsafe-default' }, owner), 'OPEN_ALLOWED_REQUIRED');
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.open_allowed', args: { path: 'C:\\missing.png' } }, owner), 'IDEMPOTENCY_KEY_REQUIRED');
  await rejectCode(api.call('photoshop_document_open', { path: 'C:\\missing.png' }, owner), 'DURABLE_COMMAND_REQUIRED');
  assert.equal(api.list().some(definition => definition.name === 'photoshop_document_open'), false);
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 0);
});

test('experimental catalog commands are blocked before production dispatch', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q); native.state = stateFor(null);
  const get = native.catalog.get;
  native.catalog.get = id => ({ ...get(id), status: id === 'document.open_allowed' ? 'experimental' : 'supported' });
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.open_allowed', args: { path: 'C:\\missing.png' }, idempotency_key: 'experimental-open' }, owner), 'CAPABILITY_NOT_PRODUCTION_READY');
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 0);
});

test('missing and outside-root source paths fail before a durable request or queue operation begins', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); native.state = stateFor(null);
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.open_allowed', args: { path: join(root, 'missing.png') }, idempotency_key: 'missing-source' }, owner), 'SOURCE_FILE_NOT_FOUND');
  const outsideRoot = mkdtempSync(join(scratch, 'outside-')); t.after(() => rmSync(outsideRoot, { recursive: true, force: true }));
  const outside = join(outsideRoot, 'outside.png'); writeFileSync(outside, 'outside fixture');
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.open_allowed', args: { path: outside }, idempotency_key: 'outside-source' }, owner), 'PATH_OUTSIDE_ROOT');
  assert.equal(rows(q).length, 0); assert.equal(q.read().owner.in_flight, null); assert.equal(q.read().owner.unknown, null);
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 0);
});

test('a queue-opened source cannot be discarded after untracked unsaved changes', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); native.state = stateFor(null);
  const source = join(root, 'source.png'); writeFileSync(source, 'synthetic source');
  native.command = async input => {
    assert.equal(input.command_id, 'document.open_allowed'); native.state = stateFor(202, false);
    return result({ ok: true, status: 'completed', result: { result: { documentId: 202 } }, after: native.state });
  };
  await api.call('photoshop_command_execute', { command_id: 'document.open_allowed', args: { path: source }, idempotency_key: 'open-unsaved-source' }, owner);
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.close', args: { save: false }, idempotency_key: 'unsafe-clean-close' }, owner), 'UNTRACKED_DOCUMENT_CHANGES');
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 1); assert.equal(q.read().owner.unknown, null);
});

test('document.create is a real mutation and cannot use the clean-source close exemption', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q); native.state = stateFor(null);
  native.command = async input => { assert.equal(input.command_id, 'document.create'); native.state = stateFor(303, false); return result({ ok: true, status: 'completed', result: { result: { documentId: 303 } }, after: native.state }); };
  await api.call('photoshop_command_execute', { command_id: 'document.create', args: { width: 10, height: 10 }, idempotency_key: 'create-document' }, owner);
  assert.equal(q.read().owner.dirty, true); assert.equal(q.read().owner.mutation, 1);
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.close', args: { save: false }, idempotency_key: 'close-created' }, owner), 'CLOSE_CHECKPOINT_REQUIRED');
});

test('a definite native precondition failure restores the prior dirty checkpoint state', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); bind(q, owner); const checkpoint = saved(q, owner, root);
  native.command = async () => result({ ok: false, status: 'failed', error: { code: 'PRECONDITION_FAILED' } }, true);
  const failed = await api.call('photoshop_command_execute', { command_id: 'layer.rename', args: { marker: 'invalid' }, idempotency_key: 'definite-failure' }, owner);
  assert.equal(failed.isError, true); assert.equal(q.read().owner.dirty, false); assert.equal(q.read().owner.mutation, 0);
  assert.deepEqual(q.read().owner.checkpoint, checkpoint); assert.equal(q.read().owner.unknown, null);
});

test('an unknown source open is rebound by the serialized probe and then safely closed', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); native.state = stateFor(null);
  const source = join(root, 'unknown-open.png'); writeFileSync(source, 'synthetic source');
  native.command = async input => {
    if (input.command_id === 'document.open_allowed') { native.state = stateFor(404, true); return result({ ok: false, status: 'failed', error: { code: 'HOST_ERROR' } }, true); }
    assert.equal(input.command_id, 'document.close'); native.state = stateFor(null); return result({ ok: true, status: 'completed', result: { result: { closedDocumentId: 404 } }, after: native.state });
  };
  await api.call('photoshop_command_execute', { command_id: 'document.open_allowed', args: { path: source }, idempotency_key: 'unknown-open' }, owner);
  assert.equal(q.read().owner.unknown.command_id, 'document.open_allowed');
  const recovery = q.recoverClaim({ task_id: owner.task_id });
  const context = { task_id: recovery.task_id, epoch: recovery.epoch, token: recovery.token };
  const { state } = await api.control('probe', {}, context);
  assert.equal(q.read().owner.document_id, 404); assert.equal(q.read().owner.opened_by_queue, true);
  const released = await api.settleRecoveredLease(recovery, context, state);
  assert.equal(released.status, 'NO_IMAGE_CHANGE'); assert.equal(q.read().owner, null);
});

test('stale clean queue-opened source is closed before the next waiting task acquires', async t => {
  const { api, q, native, advance } = fixture(t); const owner = acquire(q);
  const open = q.begin(owner, { command_id: 'document.open_allowed', mutates: false, expected_until: 1050 });
  q.end(owner, open.id, { documentId: 505, documentOpened: true }); native.state = stateFor(505, true);
  native.command = async input => { assert.equal(input.command_id, 'document.close'); native.state = stateFor(null); return result({ ok: true, status: 'completed', result: { result: { closedDocumentId: 505 } }, after: native.state }); };
  const waiting = q.enqueue({ task_id: 'task-B', asset_id: 'image-B', description: 'Ready input.', ready: true }); advance(101);
  const next = await api.control('acquire', { task_id: 'task-B', ticket: waiting.ticket }, {});
  assert.equal(next.acquired, true); assert.equal(next.recovery.released, true);
  assert.deepEqual(native.calls.filter(x => x.kind === 'command').map(x => x.args.command_id), ['document.close']);
});

test('CLI task binding overrides stale review identity and lease sessions recover atomically', t => {
  const request = bindTaskRequest({ name: 'photoshop_queue_review', arguments: { task_id: 'stale-task', asset_id: 'asset-A', record: 'review.json' } }, 'real-task');
  assert.equal(request.arguments.task_id, 'real-task');
  const root = mkdtempSync(join(scratch, 'client-')); t.after(() => rmSync(root, { recursive: true, force: true }));
  const session = join(root, 'session.json'); saveLeaseSession(session, { task_id: 'real-task', ticket: 1 }); saveLeaseSession(session, { task_id: 'real-task', ticket: 2 });
  assert.equal(loadLeaseSession(session, 'real-task').ticket, 2);
  writeFileSync(session, '{broken'); assert.deepEqual(loadLeaseSession(session, 'real-task'), { task_id: 'real-task' });
  assert.equal(readdirSync(root).some(name => name.startsWith('session.json.corrupt-')), true);
  const lock = join(root, 'start.lock'); writeFileSync(lock, '{broken'); const mtime = statSync(lock).mtimeMs;
  assert.equal(reclaimStartLock(lock, mtime + 2000), true); assert.equal(readdirSync(root).includes('start.lock'), false);
});

test('health reports the first actionable bridge blocker and device scope', t => {
  const { api, q, native } = fixture(t);
  native.bridge.status = () => ({ paired: true, connected: false, pluginInstanceId: 'bridge-offline' });
  const health = api.health();
  assert.equal(health.ok, false); assert.equal(health.blockers[0].code, 'BRIDGE_DISCONNECTED');
  assert.equal(health.device_id, q.deviceId); assert.ok(health.next_action.includes('Photoshop'));
});

test('health blocks lease acquisition when a required catalog capability is not supported', t => {
  const { api, native } = fixture(t);
  const get = native.catalog.get;
  native.catalog.get = id => ({ ...get(id), status: id === 'document.open_allowed' ? 'experimental' : 'supported' });
  const health = api.health();
  assert.equal(health.ok, false);
  assert.ok(health.blockers.some(item => item.code === 'CAPABILITY_NOT_PRODUCTION_READY'));
  assert.equal(health.runtime.production_commands.find(item => item.id === 'document.open_allowed').status, 'experimental');
});

test('resume check invalidates historical failure snapshots and selects the current queue action', () => {
  const health = {
    ok: true,
    ready_for_new_lease: true,
    runtime: { ok: true },
    bridge: { paired: true, connected: true },
    storage: { ok: true, writable: true },
    blockers: [],
    next_action: 'Enqueue prepared work and acquire.'
  };
  const idle = buildResumeCheck(health, { diagnosis: 'IDLE', waiting: [], owner: null }, 'task-A', {}, '2026-09-10T00:00:00.000Z');
  assert.equal(idle.photoshop_operational, true);
  assert.equal(idle.old_failure_snapshot_authoritative, false);
  assert.equal(idle.resume_action, 'enqueue_prepared_work_then_acquire');

  const waiting = buildResumeCheck({ ...health, ready_for_new_lease: false }, { diagnosis: 'BUSY', waiting: [{ task_id: 'task-A', ticket: 17 }], owner: { task_id: 'task-B' } }, 'task-A');
  assert.equal(waiting.own_waiting_ticket, 17);
  assert.equal(waiting.resume_action, 'acquire_existing_ticket');

  const disconnected = buildResumeCheck({ ...health, ok: false, ready_for_new_lease: false, bridge: { paired: true, connected: false }, blockers: [{ code: 'BRIDGE_DISCONNECTED' }] }, { diagnosis: 'IDLE', waiting: [], owner: null }, 'task-A');
  assert.equal(disconnected.photoshop_operational, false);
  assert.equal(disconnected.resume_action, 'follow_current_health_next_action');
});
