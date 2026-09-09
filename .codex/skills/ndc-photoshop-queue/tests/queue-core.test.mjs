import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Worker } from 'node:worker_threads';
import { PhotoshopQueue, fileEvidence } from '../scripts/queue-core.mjs';

// Synthetic files/command receipts exercise state transitions only: no Photoshop,
// generated artwork, or actual visual PASS is produced by this suite.
const scratch = resolve(dirname(fileURLToPath(import.meta.url)), '.test-data');
mkdirSync(scratch, { recursive: true });
function fixture(t) {
  const root = mkdtempSync(join(scratch, 'queue-'));
  const path = join(root, 'queue.sqlite');
  let clock = 1000;
  const options = { roots: [root], now: () => clock, idleMs: 50, staleMs: 100 };
  const connections = [];
  const open = () => { const q = new PhotoshopQueue(path, options); connections.push(q); return q; };
  const q = open();
  t.after(() => {
    for (const c of connections) { try { c.close(); } catch {} }
    assert.equal(dirname(resolve(root)), scratch, 'cleanup must remain under this suite scratch directory');
    rmSync(root, { recursive: true, force: true });
  });
  return { q, open, root, path, options, advance: ms => { clock += ms; } };
}
function ticket(q, task = 'task-A', asset = 'image-A') {
  return q.enqueue({ task_id: task, asset_id: asset, description: `Prepare ${asset}`, ready: true });
}
function lease(q, task = 'task-A', asset = 'image-A') {
  const item = ticket(q, task, asset);
  const result = q.acquire({ task_id: task, ticket: item.ticket });
  assert.equal(result.acquired, true);
  return result;
}
function code(expected, fn) { assert.throws(fn, e => e?.code === expected); }
function operation(q, owner, { mutates = true, doc = 101, uncertain = false, expected_until = 1050 } = {}) {
  const command = q.begin(owner, { command_id: 'synthetic.command', mutates, expected_until });
  q.end(owner, command.id, { uncertain, documentId: doc, result: { synthetic: true } });
  return command;
}
function exportFile(q, owner, root, name, doc = 101) {
  const path = join(root, name);
  writeFileSync(path, `synthetic export: ${name}; document=${doc}`);
  const command = q.begin(owner, { command_id: 'document.export', mutates: false, expected_until: 1050 });
  q.end(owner, command.id, { documentId: doc, exported: fileEvidence(path, [root]) });
  return { path, role: name.endsWith('.psd') ? 'working' : 'review' };
}
function saved(q, owner, root, doc = 101) {
  const files = [exportFile(q, owner, root, 'working.psd', doc), exportFile(q, owner, root, 'review.png', doc)];
  const spec = { files, document_id: doc, resume: 'Reopen this PSD; inspect the frozen review PNG.' };
  return { spec, checkpoint: q.checkpoint(owner, spec) };
}
function barrier(q, owner, doc = 101) { return q.recoveryBarrier(owner, { ok: true, document_id: doc, synthetic: true }); }

test('constructor resolves multiple roots without passing map indices to path.resolve', t => {
  const f = fixture(t);
  const other = join(f.root, 'second-root'); mkdirSync(other);
  const q = new PhotoshopQueue(join(f.root, 'other.sqlite'), { roots: [f.root, other] });
  try { assert.deepEqual(q.roots, [resolve(f.root), resolve(other)]); } finally { q.close(); }
});

test('FIFO, duplicate enqueue, one ticket per task, and stale release', t => {
  const { q } = fixture(t);
  const a = ticket(q), b = ticket(q, 'task-B', 'image-B');
  assert.deepEqual(ticket(q), { ticket: a.ticket, duplicate: true });
  code('ONE_REQUEST_PER_TASK', () => ticket(q, 'task-A', 'another-image'));
  assert.equal(q.acquire({ task_id: 'task-B', ticket: b.ticket }).reason, 'WAIT_TURN');
  const owner = q.acquire({ task_id: 'task-A', ticket: a.ticket });
  assert.equal(q.acquire({ task_id: 'task-A', ticket: a.ticket }).reason, 'ALREADY_HELD');
  assert.equal(q.acquire({ task_id: 'task-B', ticket: b.ticket }).reason, 'BUSY');
  q.release(owner);
  const next = q.acquire({ task_id: 'task-B', ticket: b.ticket });
  assert.equal(next.acquired, true);
  assert.ok(next.epoch > owner.epoch);
  code('STALE_LEASE', () => q.release(owner));
  code('STALE_LEASE', () => q.begin(owner, { mutates: true }));
});

test('independent SQLite connections share one durable queue', t => {
  const { q, open } = fixture(t); const other = open();
  const a = ticket(q);
  assert.deepEqual(ticket(other), { ticket: a.ticket, duplicate: true });
  const owner = other.acquire({ task_id: 'task-A', ticket: a.ticket });
  assert.equal(owner.acquired, true);
  assert.equal(q.diagnose().owner.task_id, 'task-A');
  assert.equal(q.acquire({ task_id: 'task-A', ticket: a.ticket }).reason, 'ALREADY_HELD');
});

test('concurrent clients can claim a ticket only once', async t => {
  const f = fixture(t); const item = ticket(f.q);
  const moduleUrl = new URL('../scripts/queue-core.mjs', import.meta.url).href;
  const workers = [0, 1].map(() => new Worker(`
    const { parentPort, workerData } = require('node:worker_threads');
    (async () => {
      const { PhotoshopQueue } = await import(workerData.moduleUrl);
      const q = new PhotoshopQueue(workerData.path, { roots: [workerData.root], now: () => workerData.now });
      parentPort.postMessage({ ready: true });
      parentPort.once('message', () => {
        try { parentPort.postMessage({ result: q.acquire({ task_id: 'task-A', ticket: workerData.ticket }) }); }
        catch (e) { parentPort.postMessage({ error: e.code || e.message }); }
        finally { q.close(); }
      });
    })().catch(e => { throw e; });
  `, { eval: true, workerData: { moduleUrl, path: f.path, root: f.root, ticket: item.ticket, now: 1000 } }));
  t.after(async () => { await Promise.all(workers.map(w => w.terminate())); });
  await Promise.all(workers.map(w => new Promise((res, rej) => { w.once('message', res); w.once('error', rej); })));
  const results = workers.map(w => new Promise((res, rej) => { w.once('message', res); w.once('error', rej); }));
  workers.forEach(w => w.postMessage('acquire'));
  const values = await Promise.all(results);
  assert.ok(values.every(v => !v.error));
  assert.equal(values.filter(v => v.result.acquired).length, 1);
  assert.equal(values.filter(v => v.result.reason === 'ALREADY_HELD').length, 1);
});

test('a released snapshot waits for its own review while the next task can use Photoshop', t => {
  const { q, root } = fixture(t); const a = lease(q);
  const b = ticket(q, 'task-B', 'image-B');
  operation(q, a); saved(q, a, root);
  assert.equal(q.release(a).status, 'WAITING_REVIEW');
  code('CURRENT_IMAGE_UNREVIEWED', () => ticket(q, 'task-A', 'another-image'));
  assert.equal(q.acquire({ task_id: 'task-B', ticket: b.ticket }).acquired, true);
  assert.equal(q.read().reviews['task-A'].status, 'WAITING_REVIEW');
});

test('recorded FAIL permits an independent image without pretending the failed image passed', t => {
  const { q, root } = fixture(t); const a = lease(q);
  operation(q, a); const { checkpoint } = saved(q, a, root); q.release(a);
  const reviewFile = checkpoint.files.find(f => f.role === 'review');
  q.review({ task_id: 'task-A', asset_id: 'image-A' }, { valid: true, status: 'FAIL', sha256: reviewFile.sha256, synthetic: true });
  assert.equal(ticket(q, 'task-A', 'independent-image').asset_id, 'independent-image');
  assert.equal(q.read().reviews['task-A'].status, 'FAIL');
});

test('an overdue in-flight command never grants release or recovery ownership', t => {
  const { q, advance } = fixture(t); const a = lease(q);
  const command = q.begin(a, { mutates: true, expected_until: 1050 });
  advance(1000);
  assert.equal(q.diagnose().diagnosis, 'COMMAND_OVERDUE');
  code('UNRESOLVED_COMMAND', () => q.release(a));
  code('COMMAND_STILL_RUNNING', () => q.recoverClaim({ task_id: 'recovery' }));
  assert.equal(q.read().owner.in_flight.id, command.id);
});

test('an unknown command blocks replay and release until a serialized recovery barrier', t => {
  const { q, advance } = fixture(t); const a = lease(q);
  operation(q, a, { uncertain: true }); advance(101);
  assert.equal(q.diagnose().diagnosis, 'UNKNOWN_COMMAND');
  code('UNRESOLVED_COMMAND', () => q.release(a));
  code('UNRESOLVED_COMMAND', () => q.begin(a, { mutates: true }));
  const r = q.recoverClaim({ task_id: 'recovery' });
  code('UNRESOLVED_COMMAND', () => q.release(r));
  code('BARRIER_REQUIRED', () => q.recoveryBarrier(r, { ok: false }));
  barrier(q, r);
  assert.equal(q.read().owner.unknown, null);
  assert.equal(q.read().owner.dirty, true);
  code('CHECKPOINT_REQUIRED', () => q.release(r));
});

test('recovery is unique, advances epoch, and fences old command and heartbeat tokens', t => {
  const { q, advance } = fixture(t); const a = lease(q);
  code('OWNER_ALIVE', () => q.recoverClaim({ task_id: 'recovery-1' }));
  advance(101);
  const r = q.recoverClaim({ task_id: 'recovery-1' });
  assert.ok(r.epoch > a.epoch); assert.notEqual(r.token, a.token);
  code('RECOVERY_OWNED', () => q.recoverClaim({ task_id: 'recovery-2' }));
  code('STALE_LEASE', () => q.heartbeat(a));
  code('STALE_LEASE', () => q.end(a, 'old-command', {}));
  assert.equal(q.read().owner.task_id, 'recovery-1');
});

test('a task with an existing waiting ticket cannot also own another task recovery ticket', t => {
  const { q, advance } = fixture(t); const a = lease(q);
  const b = ticket(q, 'task-B', 'image-B'); advance(101);
  code('RECOVERY_TASK_QUEUED', () => q.recoverClaim({ task_id: 'task-B' }));
  assert.equal(q.read().owner.task_id, a.task_id);
  assert.equal(q.read().waiting[0].ticket, b.ticket);
  q.cancel({ task_id: 'task-B', ticket: b.ticket });
  assert.equal(q.recoverClaim({ task_id: 'task-B' }).original_task_id, a.task_id);
});

test('a recovery operator crash can be fenced after becoming stale, preserving the original task', t => {
  const { q, advance, open } = fixture(t); const a = lease(q);
  advance(101); const r1 = q.recoverClaim({ task_id: 'recovery-1' }); barrier(q, r1);
  const restarted = open(); restarted.recoverAfterRestart();
  code('RECOVERY_OWNED', () => restarted.recoverClaim({ task_id: 'recovery-2' }));
  advance(101); const r2 = restarted.recoverClaim({ task_id: 'recovery-2' });
  assert.ok(r2.epoch > r1.epoch); assert.equal(r2.original_task_id, a.task_id);
  assert.equal(r2.barrier, null);
  code('STALE_LEASE', () => q.heartbeat(r1));
});

test('even a clean recovered owner must pass a fresh live barrier before mutation or release', t => {
  const { q, advance, open } = fixture(t); lease(q); advance(101);
  const r = q.recoverClaim({ task_id: 'recovery' });
  code('BARRIER_REQUIRED', () => q.begin(r, { mutates: true }));
  code('BARRIER_REQUIRED', () => q.checkpoint(r, { files: [], resume: 'Resume after live inspection.' }));
  code('BARRIER_REQUIRED', () => q.release(r));
  barrier(q, r);
  const restarted = open(); restarted.recoverAfterRestart();
  code('BARRIER_REQUIRED', () => restarted.release(r));
  barrier(restarted, r); assert.equal(restarted.release(r).status, 'NO_IMAGE_CHANGE');
});

test('recovered dirty output and its review remain assigned to the original production task', t => {
  const { q, advance, root } = fixture(t); const a = lease(q);
  operation(q, a); advance(101); const r = q.recoverClaim({ task_id: 'recovery' }); barrier(q, r);
  code('ONE_REQUEST_PER_TASK', () => ticket(q, 'task-A', 'another-image'));
  saved(q, r, root); const result = q.release(r);
  assert.equal(result.task_id, 'task-A'); assert.equal(result.recovered_by, 'recovery');
  assert.equal(q.read().reviews['task-A'].status, 'WAITING_REVIEW');
  assert.equal(q.read().reviews.recovery, undefined);
  code('CURRENT_IMAGE_UNREVIEWED', () => ticket(q, 'task-A', 'another-image'));
});

test('checkpoint requires actual exports from the latest mutation, with both PSD and PNG', t => {
  const { q, root } = fixture(t); const a = lease(q); operation(q, a);
  const psd = join(root, 'unverified.psd'), png = join(root, 'unverified.png');
  writeFileSync(psd, 'synthetic'); writeFileSync(png, 'synthetic');
  const spec = { files: [{ path: psd, role: 'working' }, { path: png, role: 'review' }], document_id: 101, resume: 'Resume from this PSD.' };
  code('UNVERIFIED_SAVE', () => q.checkpoint(a, spec));
  const only = exportFile(q, a, root, 'working.psd');
  code('SAVE_REQUIRED', () => q.checkpoint(a, { ...spec, files: [only] }));
  saved(q, a, root);
  assert.equal(q.release(a).status, 'WAITING_REVIEW');
});

test('exports from two different Photoshop documents cannot be combined into a checkpoint', t => {
  const { q, root } = fixture(t); const a = lease(q); operation(q, a);
  const files = [exportFile(q, a, root, 'working.psd', 101), exportFile(q, a, root, 'review.png', 202)];
  code('UNVERIFIED_SAVE', () => q.checkpoint(a, { files, document_id: 202, resume: 'Resume from this PSD.' }));
  assert.equal(q.read().owner.checkpoint, null);
});

test('a subsequent mutation invalidates both the checkpoint and old exports before submission', t => {
  const { q, root } = fixture(t); const a = lease(q); operation(q, a);
  const { spec } = saved(q, a, root);
  const command = q.begin(a, { mutates: true, expected_until: 1050 });
  assert.equal(q.read().owner.checkpoint, null); assert.deepEqual(q.read().owner.exports, []);
  q.end(a, command.id, { documentId: 101 });
  code('UNVERIFIED_SAVE', () => q.checkpoint(a, spec));
  code('CHECKPOINT_REQUIRED', () => q.release(a));
});

test('changing a checkpoint file blocks release and cannot be hidden by a new hash assertion', t => {
  const { q, root } = fixture(t); const a = lease(q); operation(q, a);
  const { spec } = saved(q, a, root); writeFileSync(spec.files[1].path, 'changed externally');
  code('CHECKPOINT_CHANGED', () => q.release(a));
  code('UNVERIFIED_SAVE', () => q.checkpoint(a, spec));
});

test('broker restart preserves an in-flight mutation as UNKNOWN without releasing its owner', t => {
  const { q, open, advance } = fixture(t); const a = lease(q);
  const command = q.begin(a, { mutates: true, expected_until: 1050 });
  const restarted = open(); assert.equal(restarted.recoverAfterRestart().requires_recovery, true);
  const state = restarted.read(); assert.equal(state.owner.unknown.id, command.id);
  assert.equal(state.owner.in_flight, null); assert.equal(state.owner.dirty, true);
  assert.equal(restarted.diagnose().diagnosis, 'UNKNOWN_COMMAND');
  code('UNRESOLVED_COMMAND', () => restarted.release(a));
  advance(101); const recovery = restarted.recoverClaim({ task_id: 'recovery' }); barrier(restarted, recovery);
  code('STALE_LEASE', () => q.end(a, command.id, { documentId: 101 }));
});

test('a lost document is recorded against its original task, without claiming a successful save', t => {
  const { q, advance } = fixture(t); const a = lease(q); operation(q, a, { uncertain: true });
  advance(101); const r = q.recoverClaim({ task_id: 'recovery' });
  code('NO_DOCUMENT_PROOF_REQUIRED', () => q.recoverLostDocument(r, { no_documents: true }));
  barrier(q, r, null);
  code('NO_DOCUMENT_PROOF_REQUIRED', () => q.recoverLostDocument(r, { no_documents: false }));
  const result = q.recoverLostDocument(r, { no_documents: true, synthetic: true });
  assert.equal(result.task_id, 'task-A'); assert.equal(result.status, 'FAIL');
  assert.equal(result.reason, 'UNSAVED_DOCUMENT_LOST'); assert.equal(q.read().owner, null);
});

test('manual reservation prevents acquisition and only its declared operator releases it', t => {
  const { q } = fixture(t); const item = ticket(q);
  q.external({ active: true, task_id: 'manual-operator', note: 'Manual shoulder completion.' });
  assert.equal(q.acquire({ task_id: 'task-A', ticket: item.ticket }).reason, 'EXTERNAL_USE');
  code('EXTERNAL_OWNER_MISMATCH', () => q.external({ active: false, task_id: 'another-task' }));
  q.external({ active: false, task_id: 'manual-operator' });
  const a = q.acquire({ task_id: 'task-A', ticket: item.ticket });
  assert.equal(q.external({ active: true, task_id: 'manual-operator' }).external.status, 'REQUESTED');
  q.release(a);
  assert.equal(q.diagnose().diagnosis, 'EXTERNAL_USE');
});

test('manual request preserves the in-flight operation, then permits read/export only until a saved release', t => {
  const { q, root } = fixture(t); const a = lease(q); const b = ticket(q, 'task-B', 'image-B');
  const command = q.begin(a, { mutates: true, expected_until: 1050 });
  const reservation = q.external({ active: true, task_id: 'human', note: 'Manual edit requested.' });
  assert.equal(reservation.external.status, 'REQUESTED');
  assert.equal(q.diagnose().diagnosis, 'MANUAL_PENDING');
  assert.equal(q.read().owner.in_flight.id, command.id);
  code('UNRESOLVED_COMMAND', () => q.release(a));
  q.end(a, command.id, { documentId: 101 });
  code('MANUAL_PENDING', () => q.begin(a, { mutates: true }));
  assert.equal(q.read().owner.in_flight, null);
  operation(q, a, { mutates: false }); saved(q, a, root); q.release(a);
  assert.equal(q.read().external.status, 'ACTIVE');
  assert.equal(q.diagnose().diagnosis, 'EXTERNAL_USE');
  assert.equal(q.acquire({ task_id: 'task-B', ticket: b.ticket }).reason, 'EXTERNAL_USE');
  q.external({ active: false, task_id: 'human' });
  assert.equal(q.acquire({ task_id: 'task-B', ticket: b.ticket }).acquired, true);
});

test('another task cannot replace or clear a requested manual reservation', t => {
  const { q } = fixture(t); const a = lease(q);
  q.external({ active: true, task_id: 'human', note: 'Manual work requested.' });
  code('EXTERNAL_OWNER_MISMATCH', () => q.external({ active: true, task_id: 'other-human' }));
  code('EXTERNAL_OWNER_MISMATCH', () => q.external({ active: false, task_id: 'other-human' }));
  q.external({ active: false, task_id: 'human' });
  operation(q, a);
  assert.equal(q.read().external, null);
});

test('manual-pending diagnostics preserve the owner stale-safe or unknown diagnosis for recovery', t => {
  const { q, advance } = fixture(t); const a = lease(q);
  q.external({ active: true, task_id: 'human' }); advance(101);
  assert.equal(q.diagnose().diagnosis, 'MANUAL_PENDING');
  assert.equal(q.diagnose().owner_diagnosis, 'STALE_SAFE');
  const command = q.begin(a, { mutates: false, expected_until: 1050 });
  q.end(a, command.id, { uncertain: true });
  assert.equal(q.diagnose().diagnosis, 'MANUAL_PENDING');
  assert.equal(q.diagnose().owner_diagnosis, 'UNKNOWN_COMMAND');
});

test('another task can end manual use only with a recorded explicit user completion instruction', t => {
  const { q, advance } = fixture(t);
  q.external({ active: true, task_id: 'task-A', note: 'User is completing the portrait manually.' });
  advance(24 * 60 * 60 * 1000);
  assert.equal(q.diagnose().diagnosis, 'EXTERNAL_USE');
  assert.equal(q.diagnose().owner_diagnosis, 'IDLE');
  code('EXTERNAL_OWNER_MISMATCH', () => q.external({ active: false, task_id: 'task-B' }));
  code('EXTERNAL_OWNER_MISMATCH', () => q.external({ active: false, task_id: 'task-B', user_confirmed_finished: true, confirmation_note: '  ' }));
  code('EXTERNAL_OWNER_MISMATCH', () => q.external({ active: false, task_id: 'task-B', confirmation_note: 'The operator has been idle.' }));
  const released = q.external({ active: false, task_id: 'task-B', user_confirmed_finished: true, confirmation_note: 'Current user message in task-B: manual Photoshop work is finished.' });
  assert.equal(released.external, null);
  assert.equal(released.manual_release.declarer_task_id, 'task-A');
  assert.equal(released.manual_release.released_by, 'task-B');
  assert.equal(released.manual_release.user_confirmed_finished, true);
  const event = JSON.parse(q.db.prepare("SELECT body FROM events WHERE kind='external_use' ORDER BY seq DESC LIMIT 1").get().body);
  assert.deepEqual(event.manual_release, released.manual_release);
  assert.equal(q.diagnose().diagnosis, 'IDLE');
});

test('missing or malformed manual action and recovery identity never change current ownership', t => {
  const { q, advance } = fixture(t); lease(q); advance(101);
  const ownerBefore = q.read().owner;
  for (const request of [{}, { task_id: '' }, { task_id: '  ' }]) code('INVALID_REQUEST', () => q.recoverClaim(request));
  assert.deepEqual(q.read().owner, ownerBefore);
  q.external({ active: true, task_id: 'human' }); const before = q.read();
  for (const request of [{ task_id: 'human' }, { task_id: 'human', active: 'false' }, { task_id: '', active: false }, { active: false }]) code('INVALID_REQUEST', () => q.external(request));
  assert.deepEqual(q.read(), before);
});

test('zero-document recovery activates a pending manual reservation after quarantining the lost work', t => {
  const { q, advance } = fixture(t); const a = lease(q); operation(q, a, { uncertain: true });
  q.external({ active: true, task_id: 'human' }); advance(101);
  const r = q.recoverClaim({ task_id: 'recovery' }); barrier(q, r, null);
  q.recoverLostDocument(r, { no_documents: true, synthetic: true });
  assert.equal(q.read().external.status, 'ACTIVE');
  assert.equal(q.diagnose().diagnosis, 'EXTERNAL_USE');
});

test('an abandoned expired head cannot block a fresh later waiting task', t => {
  const { q, advance } = fixture(t); const a = ticket(q);
  advance(200000); const b = ticket(q, 'task-B', 'image-B'); advance(100001);
  const owner = q.acquire({ task_id: 'task-B', ticket: b.ticket });
  assert.equal(owner.acquired, true); assert.equal(owner.task_id, 'task-B');
  const expired = JSON.parse(q.db.prepare("SELECT body FROM events WHERE kind='waiting_expired' ORDER BY seq DESC LIMIT 1").get().body);
  assert.equal(expired.expired[0].ticket, a.ticket); assert.equal(expired.waiting_timeout_ms, 300000);
  assert.equal(expired.expired[0].reason, 'UNACQUIRED_WAITING_TICKET_EXPIRED');
});

test('acquire polling renews a waiting ticket while busy without renewing or releasing the owner', t => {
  const { q, advance } = fixture(t); const owner = lease(q, 'owner-task', 'owned-image');
  const a = ticket(q); advance(200000);
  const renewed = q.acquire({ task_id: 'task-A', ticket: a.ticket });
  assert.equal(renewed.reason, 'BUSY'); assert.equal(renewed.renew_after_ms, 30000);
  advance(200000); assert.deepEqual(q.expireWaiting().expired, []);
  assert.equal(q.read().waiting[0].ticket, a.ticket);
  advance(100000); assert.equal(q.expireWaiting().expired[0].ticket, a.ticket);
  assert.equal(q.read().owner.token, owner.token); assert.equal(q.read().owner.heartbeat_at, owner.heartbeat_at);
});

test('WAIT_TURN polling keeps a live follower while the abandoned head expires', t => {
  const { q, advance } = fixture(t); const a = ticket(q), b = ticket(q, 'task-B', 'image-B');
  advance(200000); assert.equal(q.acquire({ task_id: 'task-B', ticket: b.ticket }).reason, 'WAIT_TURN');
  advance(100001); assert.equal(q.expireWaiting().expired[0].ticket, a.ticket);
  assert.equal(q.acquire({ task_id: 'task-B', ticket: b.ticket }).acquired, true);
});

test('expired tickets cannot be revived and re-enqueue joins behind still-live work', t => {
  const { q, advance } = fixture(t); lease(q, 'owner-task', 'owned-image'); const a = ticket(q);
  advance(200000); const b = ticket(q, 'task-B', 'image-B'); advance(100001); q.expireWaiting();
  const old = q.acquire({ task_id: 'task-A', ticket: a.ticket });
  assert.equal(old.reason, 'TICKET_NOT_WAITING'); assert.equal(old.reenqueue_required, true);
  const renewed = ticket(q); assert.ok(renewed.ticket > b.ticket);
  assert.deepEqual(q.read().waiting.map(x => x.ticket), [b.ticket, renewed.ticket]);
});

test('status remains read-only; explicit expiry records only actual removed waiting tickets', t => {
  const { q, advance } = fixture(t); ticket(q); advance(300000);
  const before = q.read(), events = q.db.prepare('SELECT COUNT(*) AS n FROM events').get().n;
  assert.equal(q.diagnose().thresholds.waiting_ms, 300000); assert.deepEqual(q.read(), before);
  assert.equal(q.db.prepare('SELECT COUNT(*) AS n FROM events').get().n, events);
  assert.equal(q.expireWaiting().expired.length, 1); const after = q.db.prepare('SELECT COUNT(*) AS n FROM events').get().n;
  q.expireWaiting(); assert.equal(q.db.prepare('SELECT COUNT(*) AS n FROM events').get().n, after);
});

test('waiting expiry leaves an unknown owner and all manual reservations untouched', t => {
  const { q, advance } = fixture(t); const owner = lease(q, 'owner-task', 'owned-image');
  operation(q, owner, { uncertain: true }); ticket(q);
  q.external({ active: true, task_id: 'human' }); const before = q.read(); advance(24 * 60 * 60 * 1000);
  assert.equal(q.expireWaiting().expired.length, 1);
  assert.deepEqual(q.read().owner, before.owner); assert.deepEqual(q.read().external, before.external);
  assert.equal(q.diagnose().owner_diagnosis, 'UNKNOWN_COMMAND');
});

test('legacy waiting tickets use their enqueue time while records with acquired work never expire', t => {
  const { q, advance } = fixture(t); const a = ticket(q), b = ticket(q, 'task-B', 'image-B');
  q.tx('synthetic_legacy_record', s => { delete s.waiting[0].waiting_last_seen_at; s.waiting[1].document_id = 202; return {}; });
  advance(300001); const expired = q.expireWaiting().expired;
  assert.deepEqual(expired.map(x => x.ticket), [a.ticket]); assert.equal(q.read().waiting[0].ticket, b.ticket);
});

test('acquire polling renews waiting during manual use without ending the manual reservation', t => {
  const { q, advance } = fixture(t); q.external({ active: true, task_id: 'human' }); const a = ticket(q);
  advance(200000); const pending = q.acquire({ task_id: 'task-A', ticket: a.ticket });
  assert.equal(pending.reason, 'EXTERNAL_USE'); advance(200000);
  assert.equal(q.expireWaiting().expired.length, 0); assert.equal(q.read().external.status, 'ACTIVE');
});

test('enqueue distinguishes missing, overlong identifier, and overlong description errors', t => {
  const { q } = fixture(t);
  code('INVALID_REQUEST', () => q.enqueue({ task_id: 'task-A', asset_id: 'image-A', description: '', ready: true }));
  code('IDENTIFIER_TOO_LONG', () => q.enqueue({ task_id: 'x'.repeat(251), asset_id: 'image-A', description: 'Ready.', ready: true }));
  code('DESCRIPTION_TOO_LONG', () => q.enqueue({ task_id: 'task-A', asset_id: 'image-A', description: 'x'.repeat(251), ready: true }));
});

test('a copied queue cannot authenticate or auto-recover a lease owned by another computer', t => {
  const root = mkdtempSync(join(scratch, 'device-')), path = join(root, 'queue.sqlite');
  const a = new PhotoshopQueue(path, { roots: [root], deviceId: 'device-A', brokerInstanceId: 'broker-A' });
  const item = ticket(a), owner = a.acquire({ task_id: 'task-A', ticket: item.ticket });
  const b = new PhotoshopQueue(path, { roots: [root], deviceId: 'device-B', brokerInstanceId: 'broker-B' });
  t.after(() => { a.close(); b.close(); rmSync(root, { recursive: true, force: true }); });
  code('FOREIGN_DEVICE_LEASE', () => b.heartbeat(owner));
  code('DEVICE_HANDOFF_REQUIRED', () => b.recoverClaim({ task_id: 'task-B' }));
  assert.equal(b.read().owner.device_id, 'device-A');
});

test('a broker restart fences the old process but permits immediate same-device client rebind', t => {
  const root = mkdtempSync(join(scratch, 'broker-instance-')), path = join(root, 'queue.sqlite');
  const first = new PhotoshopQueue(path, { roots: [root], deviceId: 'device-A', brokerInstanceId: 'broker-A' });
  const item = ticket(first), owner = first.acquire({ task_id: 'task-A', ticket: item.ticket });
  const restarted = new PhotoshopQueue(path, { roots: [root], deviceId: 'device-A', brokerInstanceId: 'broker-B' }); restarted.recoverAfterRestart();
  t.after(() => { first.close(); restarted.close(); rmSync(root, { recursive: true, force: true }); });
  code('BROKER_INSTANCE_CHANGED', () => restarted.heartbeat(owner));
  const rebound = restarted.rebind({ task_id: owner.task_id, ticket: owner.ticket });
  assert.ok(rebound.epoch > owner.epoch); assert.equal(rebound.broker_instance_id, 'broker-B');
  barrier(restarted, rebound); assert.equal(restarted.read().owner.recovering, false);
});
