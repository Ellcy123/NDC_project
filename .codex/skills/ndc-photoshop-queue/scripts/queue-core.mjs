import { DatabaseSync } from 'node:sqlite';
import { randomUUID, createHash } from 'node:crypto';
import { readFileSync, statSync, realpathSync, mkdirSync } from 'node:fs';
import { dirname, resolve, relative, extname, isAbsolute } from 'node:path';

export class QueueError extends Error {
  constructor(code, message) { super(message); this.code = code; }
}
const fail = (code, message) => { throw new QueueError(code, message); };
const id = value => typeof value === 'string' && value.trim().length > 0 && value.length <= 250;
export const digest = value => createHash('sha256').update(value).digest('hex');
export function fileEvidence(path, roots) {
  const p = realpathSync(path);
  if (!roots.some(root => { const rel = relative(realpathSync(root), p); return rel === '' || (!rel.startsWith('..') && !isAbsolute(rel)); })) fail('PATH_OUTSIDE_ROOT', p);
  if (!statSync(p).isFile()) fail('FILE_REQUIRED', p);
  return { path: p, sha256: digest(readFileSync(p)), bytes: statSync(p).size };
}

// One durable authority per physical Photoshop bridge. Time never grants a second owner.
export class PhotoshopQueue {
  constructor(path, { roots, now = Date.now, idleMs = 120000, staleMs = 180000, waitingMs = 300000 } = {}) {
    mkdirSync(dirname(resolve(path)), { recursive: true });
    this.db = new DatabaseSync(path); this.roots = roots.map(root => resolve(root)); this.now = now;
    this.idleMs = idleMs; this.staleMs = staleMs; this.waitingMs = waitingMs;
    this.db.exec('PRAGMA journal_mode=WAL; PRAGMA busy_timeout=5000; CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY CHECK(id=1), body TEXT NOT NULL); CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT, at INTEGER NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL)');
    this.db.prepare('INSERT OR IGNORE INTO state VALUES(1,?)').run(JSON.stringify({ version: 1, epoch: 0, next: 1, waiting: [], owner: null, reviews: {}, external: null }));
  }
  read() { return JSON.parse(this.db.prepare('SELECT body FROM state WHERE id=1').get().body); }
  tx(kind, fn) {
    this.db.exec('BEGIN IMMEDIATE');
    try {
      const state = this.read(), value = fn(state);
      this.db.prepare('UPDATE state SET body=? WHERE id=1').run(JSON.stringify(state));
      // Private lease tokens are not copied into the human-readable audit trail.
      this.db.prepare('INSERT INTO events(at,kind,body) VALUES(?,?,?)').run(this.now(), kind, JSON.stringify(value, (k, v) => k === 'token' ? '[private]' : v));
      this.db.exec('COMMIT'); return value;
    } catch (e) { this.db.exec('ROLLBACK'); throw e; }
  }
  auth(state, a) {
    const o = state.owner;
    if (!o || o.task_id !== a.task_id || o.token !== a.token || o.epoch !== a.epoch) fail('STALE_LEASE', 'Acquire the current queue ticket; an expired owner cannot send commands.');
    return o;
  }
  waitingExpired(item) {
    // Waiting-only expiry must never be reused for an acquired document or work.
    const hasWork = item.acquired_at != null || item.document_id != null || item.in_flight || item.unknown || item.dirty || item.checkpoint || item.exports?.length || item.mutation > 0;
    const seen = item.waiting_last_seen_at ?? item.enqueued_at;
    return !hasWork && Number.isFinite(seen) && this.now() - seen >= this.waitingMs;
  }
  pruneWaiting(state, record = true) {
    const expired = state.waiting.filter(x => this.waitingExpired(x));
    if (!expired.length) return [];
    const tickets = new Set(expired.map(x => x.ticket));
    state.waiting = state.waiting.filter(x => !tickets.has(x.ticket));
    const evidence = expired.map(x => ({ ticket: x.ticket, task_id: x.task_id, asset_id: x.asset_id, enqueued_at: x.enqueued_at, last_seen_at: x.waiting_last_seen_at ?? x.enqueued_at, expired_at: this.now(), reason: 'UNACQUIRED_WAITING_TICKET_EXPIRED' }));
    if (record) this.db.prepare('INSERT INTO events(at,kind,body) VALUES(?,?,?)').run(this.now(), 'waiting_expired', JSON.stringify({ expired: evidence, waiting_timeout_ms: this.waitingMs }));
    return evidence;
  }
  expireWaiting() {
    // Status remains read-only; the watchdog and queue mutations call this explicitly.
    if (!this.read().waiting.some(x => this.waitingExpired(x))) return { expired: [], waiting_timeout_ms: this.waitingMs };
    return this.tx('waiting_expired', s => ({ expired: this.pruneWaiting(s, false), waiting_timeout_ms: this.waitingMs }));
  }
  enqueue(a) {
    if (![a.task_id, a.asset_id, a.description].every(id)) fail('INVALID_REQUEST', 'task_id, asset_id and description are required.');
    if (a.ready !== true) fail('INPUT_NOT_READY', 'Prepare inputs before joining the Photoshop queue.');
    return this.tx('enqueue', s => {
      this.pruneWaiting(s);
      const existing = [s.owner, ...s.waiting].find(x => x?.task_id === a.task_id || x?.original_task_id === a.task_id);
      if (existing) {
        if (existing.asset_id !== a.asset_id) fail('ONE_REQUEST_PER_TASK', 'Finish or cancel this task\'s existing ticket first.');
        return { ticket: existing.ticket, duplicate: true };
      }
      const pending = s.reviews[a.task_id];
      if (pending && pending.asset_id !== a.asset_id && pending.status === 'WAITING_REVIEW') fail('CURRENT_IMAGE_UNREVIEWED', 'Complete the current image review before starting this task\'s next image.');
      const item = { ticket: s.next++, task_id: a.task_id, asset_id: a.asset_id, description: a.description, enqueued_at: this.now(), waiting_last_seen_at: this.now() };
      s.waiting.push(item); return { ...item, position: s.waiting.length, waiting_timeout_ms: this.waitingMs, waiting_expires_at: item.waiting_last_seen_at + this.waitingMs };
    });
  }
  acquire(a) {
    if (!id(a?.task_id) || !Number.isInteger(a.ticket) || a.ticket < 1) fail('INVALID_REQUEST', 'A waiting task_id and positive integer ticket are required.');
    return this.tx('acquire', s => {
      this.pruneWaiting(s);
      if (s.owner?.task_id === a.task_id && s.owner.ticket === a.ticket) return { acquired: false, reason: 'ALREADY_HELD', note: 'Use the originally returned lease; acquire does not disclose its token again.' };
      const requested = s.waiting.find(x => x.task_id === a.task_id && x.ticket === a.ticket);
      if (!requested) return { acquired: false, reason: 'TICKET_NOT_WAITING', reenqueue_required: true, note: 'The unused waiting ticket expired, was cancelled, or is no longer pending. Enqueue again to join the current tail.' };
      requested.waiting_last_seen_at = this.now();
      const renewal = { waiting_expires_at: requested.waiting_last_seen_at + this.waitingMs, waiting_timeout_ms: this.waitingMs, renew_after_ms: Math.min(30000, Math.max(1, Math.floor(this.waitingMs / 3))) };
      if (s.external || s.owner) return { acquired: false, reason: s.external ? (s.external.status === 'REQUESTED' ? 'MANUAL_PENDING' : 'EXTERNAL_USE') : 'BUSY', owner: s.owner?.task_id, ...renewal };
      const first = s.waiting[0];
      if (!first || first.task_id !== a.task_id || first.ticket !== a.ticket) return { acquired: false, reason: 'WAIT_TURN', next: first?.ticket, ...renewal };
      s.waiting.shift(); const t = this.now();
      s.owner = { ...first, epoch: ++s.epoch, token: randomUUID(), acquired_at: t, heartbeat_at: t, progress_at: t, in_flight: null, unknown: null, dirty: false, mutation: 0, exports: [], checkpoint: null, document_id: null, recovering: false };
      return { acquired: true, ...s.owner };
    });
  }
  cancel(a) {
    return this.tx('cancel_waiting', s => {
      if (s.owner?.task_id === a.task_id) fail('OWNER_MUST_RELEASE', 'An active owner must save and release, not cancel its queue record.');
      const n = s.waiting.length; s.waiting = s.waiting.filter(x => !(x.task_id === a.task_id && x.ticket === a.ticket)); return { cancelled: n !== s.waiting.length };
    });
  }
  heartbeat(a) { return this.tx('heartbeat', s => { const o = this.auth(s, a); o.heartbeat_at = this.now(); return { heartbeat_at: o.heartbeat_at }; }); }
  begin(a, operation) {
    return this.tx('command_begin', s => {
      const o = this.auth(s, a);
      if (o.in_flight || o.unknown) fail('UNRESOLVED_COMMAND', 'Reconcile the previous command before issuing another.');
      if (o.recovering && !o.barrier) fail('BARRIER_REQUIRED', 'Probe Photoshop through the recovery barrier before resuming operations.');
      if (s.external && s.external.status !== 'REQUESTED') fail('EXTERNAL_USE', 'Photoshop is in manual use.');
      if (s.external?.status === 'REQUESTED' && operation.mutates) fail('MANUAL_PENDING', 'Manual use has been requested. Inspect/export the current document, checkpoint it, and release before making further changes.');
      o.in_flight = { ...operation, id: randomUUID(), started_at: this.now() };
      o.heartbeat_at = this.now();
      // Invalidate the previous save BEFORE submission. A crash may happen at any later point.
      if (operation.mutates) { o.dirty = true; o.mutation++; o.checkpoint = null; o.exports = []; }
      return o.in_flight;
    });
  }
  end(a, commandId, { uncertain = false, result, documentId, exported, error } = {}) {
    return this.tx('command_end', s => {
      const o = this.auth(s, a);
      if (o.in_flight?.id !== commandId) fail('COMMAND_MISMATCH', 'Completion does not match the running command.');
      const operation = o.in_flight; o.in_flight = null;
      o.heartbeat_at = o.progress_at = this.now();
      if (uncertain) o.unknown = { ...operation, error: error || 'Outcome is unknown' };
      if (documentId !== undefined && documentId !== null) o.document_id = documentId;
      if (exported && !uncertain) o.exports.push({ ...exported, document_id: documentId ?? o.document_id, mutation: o.mutation, at: this.now() });
      return { command_id: commandId, uncertain, result, error };
    });
  }
  checkpoint(a, spec) {
    const files = (spec.files || []).map(f => ({ ...fileEvidence(f.path, this.roots), role: f.role }));
    if (!id(spec.resume)) fail('RESUME_REQUIRED', 'A precise recovery step is required.');
    return this.tx('checkpoint', s => {
      const o = this.auth(s, a);
      if (o.in_flight || o.unknown) fail('UNRESOLVED_COMMAND', 'Cannot checkpoint a running or unknown command.');
      if (o.recovering && !o.barrier) fail('BARRIER_REQUIRED', 'Probe Photoshop through the recovery barrier before accepting a checkpoint.');
      if (o.dirty) {
        if (!files.some(f => f.role === 'working' && extname(f.path).toLowerCase() === '.psd') || !files.some(f => f.role === 'review' && extname(f.path).toLowerCase() === '.png')) fail('SAVE_REQUIRED', 'Modified work requires a recoverable PSD and frozen review PNG.');
        for (const f of files) {
          if (!o.exports.some(x => x.path.toLowerCase() === f.path.toLowerCase() && x.sha256 === f.sha256 && x.mutation === o.mutation && x.document_id === o.document_id)) fail('UNVERIFIED_SAVE', 'Checkpoint files must match actual MCP exports from this document after the latest modification.');
        }
        if (spec.document_id !== o.document_id) fail('DOCUMENT_MISMATCH', 'Checkpoint belongs to a different Photoshop document.');
      }
      o.checkpoint = { files, resume: spec.resume, document_id: o.document_id, mutation: o.mutation, at: this.now() }; o.progress_at = this.now();
      return o.checkpoint;
    });
  }
  release(a) {
    return this.tx('release', s => {
      const o = this.auth(s, a);
      if (o.in_flight || o.unknown) fail('UNRESOLVED_COMMAND', 'Release is blocked until the last command has a known outcome.');
      if (o.recovering && !o.barrier) fail('BARRIER_REQUIRED', 'Probe Photoshop through the recovery barrier before releasing its recovered owner.');
      if (o.dirty && (!o.checkpoint || o.checkpoint.mutation !== o.mutation)) fail('CHECKPOINT_REQUIRED', 'Save a current recoverable checkpoint before releasing Photoshop.');
      for (const f of o.checkpoint?.files || []) if (fileEvidence(f.path, this.roots).sha256 !== f.sha256) fail('CHECKPOINT_CHANGED', f.path);
      const taskId = o.original_task_id || o.task_id;
      const evidence = { task_id: taskId, ...(taskId !== o.task_id ? { recovered_by: o.task_id } : {}), asset_id: o.asset_id, checkpoint: o.checkpoint, status: o.dirty ? 'WAITING_REVIEW' : 'NO_IMAGE_CHANGE', epoch: o.epoch, released_at: this.now() };
      if (o.dirty) s.reviews[taskId] = evidence;
      s.owner = null;
      if (s.external?.status === 'REQUESTED') { s.external.status = 'ACTIVE'; s.external.activated_at = this.now(); }
      return evidence;
    });
  }
  review(a, validated) {
    return this.tx('review_recorded', s => {
      const r = s.reviews[a.task_id];
      if (!r || r.asset_id !== a.asset_id) fail('REVIEW_TARGET_MISMATCH', 'No matching released image is awaiting review.');
      if (!validated?.valid || !['PASS', 'FAIL'].includes(validated.status)) fail('REVIEW_REQUIRED', 'Use the existing NDC visual record validator, not a manually asserted pass.');
      if (!(r.checkpoint?.files || []).some(f => f.sha256 === validated.sha256 && f.role === 'review')) fail('REVIEW_HASH_MISMATCH', 'The review must describe this released snapshot.');
      for (const f of r.checkpoint.files) if (fileEvidence(f.path, this.roots).sha256 !== f.sha256) fail('CHECKPOINT_CHANGED', f.path);
      r.status = validated.status; r.review = validated; return r;
    });
  }
  diagnose() {
    const s = this.read(), o = s.owner; let ownerDiagnosis = 'IDLE';
    if (o?.unknown) ownerDiagnosis = 'UNKNOWN_COMMAND';
    else if (o?.in_flight) ownerDiagnosis = this.now() > o.in_flight.expected_until ? 'COMMAND_OVERDUE' : 'COMMAND_RUNNING';
    else if (o) ownerDiagnosis = this.now() - o.heartbeat_at > this.staleMs ? (o.dirty && !o.checkpoint ? 'STALE_UNSAVED' : 'STALE_SAFE') : this.now() - o.progress_at > this.idleMs ? 'IDLE_HELD' : 'ACTIVE';
    const diagnosis = s.external ? (s.external.status === 'REQUESTED' ? 'MANUAL_PENDING' : 'EXTERNAL_USE') : ownerDiagnosis;
    const owner = o && { ...o }; if (owner) delete owner.token;
    return { diagnosis, owner_diagnosis: ownerDiagnosis, owner, waiting: s.waiting, external: s.external, thresholds: { idle_ms: this.idleMs, stale_ms: this.staleMs, waiting_ms: this.waitingMs }, note: 'Only unused waiting tickets expire. Elapsed time never reassigns in-flight/unknown work or ends manual use.' };
  }
  recoverClaim(a) {
    if (!id(a?.task_id)) fail('INVALID_REQUEST', 'A non-empty recovery task_id is required.');
    return this.tx('recovery_claim', s => {
      const o = s.owner;
      if (!o) fail('NO_OWNER', 'No occupied slot to recover.');
      if (s.waiting.some(x => x.task_id === a.task_id)) fail('RECOVERY_TASK_QUEUED', 'Cancel this recovery task\'s waiting production ticket before claiming another task\'s occupied slot.');
      if (o.in_flight) fail('COMMAND_STILL_RUNNING', 'Wait for the running request or its recorded timeout; do not start a second writer.');
      if (o.recovering && this.now() - o.heartbeat_at <= this.staleMs) fail('RECOVERY_OWNED', 'Only one live recovery operator is allowed.');
      if (o.task_id !== a.task_id && this.now() - o.heartbeat_at <= this.staleMs) fail('OWNER_ALIVE', 'Current owner is still responsive. Ask it to finish and release.');
      o.original_task_id = o.original_task_id || o.task_id;
      o.task_id = a.task_id; o.epoch = ++s.epoch; o.token = randomUUID(); o.recovering = true; o.barrier = null; o.heartbeat_at = this.now();
      return { ...o, note: 'The previous lease is fenced. Probe Photoshop before saving or releasing.' };
    });
  }
  recoveryBarrier(a, evidence) {
    return this.tx('recovery_barrier', s => {
      const o = this.auth(s, a);
      if (!o.recovering || o.in_flight || evidence?.ok !== true) fail('BARRIER_REQUIRED', 'A successful serialized live state probe is required.');
      o.unknown = null; o.barrier = { at: this.now(), ...evidence }; o.heartbeat_at = this.now();
      return { reconciled: true, original_result: 'May still require output inspection; no operation was replayed.', barrier: o.barrier };
    });
  }
  recoverLostDocument(a, evidence) {
    return this.tx('recovery_document_lost', s => {
      const o = this.auth(s, a);
      if (!o.recovering || !o.barrier || o.in_flight || o.unknown || evidence?.no_documents !== true) fail('NO_DOCUMENT_PROOF_REQUIRED', 'Only a fresh live proof of zero open documents permits quarantining unsaved work.');
      const entry = { task_id: o.original_task_id || o.task_id, asset_id: o.asset_id, status: 'FAIL', reason: 'UNSAVED_DOCUMENT_LOST', at: this.now() };
      s.reviews[entry.task_id] = entry; s.owner = null;
      if (s.external?.status === 'REQUESTED') { s.external.status = 'ACTIVE'; s.external.activated_at = this.now(); }
      return entry;
    });
  }
  external(a) {
    if (!id(a?.task_id) || typeof a.active !== 'boolean') fail('INVALID_REQUEST', 'Manual reservation requires a non-empty task_id and an explicit boolean active.');
    return this.tx('external_use', s => {
      let manualRelease;
      if (a.active) {
        if (s.external && s.external.task_id !== a.task_id) fail('EXTERNAL_OWNER_MISMATCH', 'The declared manual operator owns this reservation.');
        s.external = { task_id: a.task_id, note: a.note, since: s.external?.since ?? this.now(), status: s.owner ? 'REQUESTED' : 'ACTIVE' };
      }
      else {
        const prior = s.external;
        if (prior && prior.task_id !== a.task_id && (a.user_confirmed_finished !== true || typeof a.confirmation_note !== 'string' || !a.confirmation_note.trim())) fail('EXTERNAL_OWNER_MISMATCH', 'Another task may end manual use only after an explicit current user completion instruction, with user_confirmed_finished=true and a note identifying that instruction. Elapsed time is not confirmation.');
        if (prior) manualRelease = { declarer_task_id: prior.task_id, released_by: a.task_id, reservation_status: prior.status, reserved_at: prior.since, released_at: this.now(), user_confirmed_finished: a.user_confirmed_finished === true, confirmation_note: typeof a.confirmation_note === 'string' ? a.confirmation_note.trim() : null };
        s.external = null;
      }
      return { external: s.external, ...(manualRelease ? { manual_release: manualRelease } : {}) };
    });
  }
  recoverAfterRestart() { return this.tx('broker_restart', s => { const o = s.owner; if (o?.in_flight) { o.unknown = { ...o.in_flight, error: 'Broker restarted while a command was running' }; o.in_flight = null; } if (o?.recovering) o.barrier = null; return { requires_recovery: !!o }; }); }
  close() { this.db.close(); }
}
