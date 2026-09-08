import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PhotoshopQueue, QueueError, fileEvidence } from '../scripts/queue-core.mjs';
import { QueueService, startBroker, queueDefinitions } from '../scripts/broker.mjs';

// All native handlers and PSD/PNG bytes here are synthetic. No Photoshop calls.
const scratch = resolve(dirname(fileURLToPath(import.meta.url)), '.test-data');
mkdirSync(scratch, { recursive: true });
const result = (data, isError = false) => ({ content: [{ type: 'text', text: JSON.stringify(data) }], structuredContent: data, ...(isError ? { isError: true } : {}) });
const stateFor = doc => ({ hasDocument: doc !== null, documentCount: doc === null ? 0 : 1, activeDocument: doc === null ? null : { id: doc, title: `Synthetic ${doc}`, saved: false } });
function fakeNative() {
  const fake = { tools: new Map(), calls: [], state: stateFor(101), command: null, probe: null, bridge: { status: () => ({ connected: true }), stop: async () => {} } };
  fake.catalog = { get: id => ({ id, risk: id === 'document.export' ? 'external' : id === 'document.inspect' ? 'read' : 'edit', engine: 'dom' }), validate: (_id, args) => args, list: () => [] };
  const register = (name, handler) => fake.tools.set(name, { definition: { name, inputSchema: { type: 'object' } }, handler });
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
function deferred() { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; }

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
  saved(q, a, root); q.release(a); const b = acquire(q, 'task-B', 'image-B');
  const second = await api.call('photoshop_command_execute', args('shared', 'B'), b);
  assert.equal(first.structuredContent.result.result.marker, 'A'); assert.equal(second.structuredContent.result.result.marker, 'B');
  const records = rows(q); assert.equal(records.length, 2); assert.notEqual(records[0].scoped_key, records[1].scoped_key);
  const calls = native.calls.filter(x => x.kind === 'command'); assert.notEqual(calls[0].args.idempotency_key, calls[1].args.idempotency_key);
});

test('different assets in the same task do not share an idempotency scope', async t => {
  const { api, q, native, root } = fixture(t); const a = acquire(q);
  await api.call('photoshop_command_execute', args('shared'), a);
  const cp = saved(q, a, root); q.release(a);
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

test('a mismatching live document fails before command_begin without dirtying or losing the saved checkpoint', async t => {
  const { api, q, native, root } = fixture(t); const owner = acquire(q); bind(q, owner); saved(q, owner, root);
  native.state = stateFor(202); const before = q.read();
  await rejectCode(api.call('photoshop_command_execute', args(), owner), 'ACTIVE_DOCUMENT_CHANGED');
  assert.deepEqual(q.read(), before); assert.equal(native.calls.filter(x => x.kind === 'command').length, 0);
  assert.equal(rows(q)[0].status, 'unknown'); assert.equal(api.busy, false);
});

test('preflight state awaits hold the broker mutex and block release without creating a mutation', async t => {
  const { api, q, native } = fixture(t); const owner = acquire(q); bind(q, owner);
  const wait = deferred(); native.probe = () => wait.promise;
  const first = api.call('photoshop_command_execute', args(), owner);
  assert.equal(q.read().owner.in_flight, null);
  await rejectCode(api.control('release', {}, owner), 'COMMAND_STILL_RUNNING');
  await rejectCode(api.call('photoshop_state_get', {}, owner), 'COMMAND_STILL_RUNNING');
  wait.reject(new QueueError('TIMEOUT', 'Synthetic preflight timeout.'));
  await rejectCode(first, 'TIMEOUT');
  assert.equal(q.read().owner.dirty, false); assert.equal(q.read().owner.unknown, null);
  assert.equal(rows(q)[0].status, 'unknown');
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
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.close', args: {} }, owner), 'CLOSE_CHECKPOINT_REQUIRED');
  const cp = saved(q, owner, root); writeFileSync(cp.files[0].path, 'changed externally');
  await rejectCode(api.call('photoshop_command_execute', { command_id: 'document.close', args: {} }, owner), 'CHECKPOINT_CHANGED');
  assert.equal(native.calls.filter(x => x.kind === 'command').length, 0); assert.equal(q.read().owner.unknown, null);
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
