import { createServer } from 'node:http';
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join, resolve, extname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { randomBytes, timingSafeEqual } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { PhotoshopQueue, QueueError, fileEvidence, digest } from './queue-core.mjs';
import { binding } from './runtime-config.mjs';

const here = dirname(fileURLToPath(import.meta.url));
export { binding };
const executeFile = promisify(execFile);
const envelope = (value, isError = false) => ({ content: [{ type: 'text', text: JSON.stringify(value) }], structuredContent: value, ...(isError ? { isError: true } : {}) });
const objectSchema = properties => ({ type: 'object', additionalProperties: false, properties });
const string = { type: 'string', minLength: 1 };
const definitions = {
  enqueue: ['Join the shared Photoshop FIFO when inputs are ready. One pending request per task.', { task_id: string, asset_id: string, description: string, ready: { type: 'boolean' } }],
  acquire: ['Acquire only the head ticket; polling renews this unacquired ticket even while busy. Poll about every 30 seconds while actively waiting; unused tickets expire after 5 minutes by default. Expired tickets must enqueue again. Owner/manual reservations never expire through this mechanism.', { task_id: string, ticket: { type: 'integer' } }],
  status: ['Inspect queue, owner, progress and suspected abnormal occupation without touching Photoshop.', {}],
  heartbeat: ['Report the current owner is alive. Does not count as useful progress or extend a running command deadline.', {}],
  checkpoint: ['Verify actual MCP-exported PSD and PNG and recovery instructions before release.', { files: { type: 'array', items: objectSchema({ path: string, role: { enum: ['working', 'review', 'view'] } }) }, document_id: { type: ['number', 'string'] }, resume: string }],
  release: ['Release a saved or unchanged slot. Does not approve the image. Running/unknown commands block release.', {}],
  cancel: ['Cancel this task\'s waiting ticket, never cancel an active Photoshop operation.', { task_id: string, ticket: { type: 'integer' } }],
  review: ['Register an existing real NDC visual record for the released snapshot. Never generates artistic PASS.', { task_id: string, asset_id: string, record: string }],
  recover: ['Fence a stale owner and appoint one recovery operator. A running request cannot be stolen.', { task_id: string }],
  probe: ['Recovery-only serialized live state barrier. Success reconciles execution order, not image quality.', {}],
  lost_document: ['Recovery-only quarantine after a fresh zero-open-documents probe. Marks unsaved work failed.', {}],
  external: ['Reserve manual Photoshop use. Its declarer may release it; another task must record an explicit current user completion instruction with user_confirmed_finished and confirmation_note. No timeout or automatic manual release.', { task_id: string, active: { type: 'boolean' }, note: string, user_confirmed_finished: { type: 'boolean' }, confirmation_note: string }],
};
export function queueDefinitions() {
  const required = { external: ['task_id', 'active'], recover: ['task_id'], acquire: ['task_id', 'ticket'] };
  return Object.entries(definitions).map(([name, [description, properties]]) => ({ name: `photoshop_queue_${name}`, description, inputSchema: { ...objectSchema(properties), ...(required[name] ? { required: required[name] } : {}) } }));
}
const diagnostic = new Set(['photoshop_command_search', 'photoshop_command_describe']);
const nativeAliases = { photoshop_document_create: 'document.create', photoshop_document_open: 'document.open_allowed', photoshop_document_export: 'document.export', photoshop_layer_create: 'layer.create', photoshop_layer_rename: 'layer.rename', photoshop_selection_select_all: 'selection.select_all', photoshop_selection_deselect: 'selection.deselect', photoshop_history_undo: 'history.undo', photoshop_image_resize: 'image.resize' };
const dataOf = r => r.structuredContent ?? JSON.parse(r.content.find(x => x.type === 'text').text);
const stableJson = value => JSON.stringify(value, (_key, item) => item && typeof item === 'object' && !Array.isArray(item) ? Object.fromEntries(Object.keys(item).sort().map(key => [key, item[key]])) : item);
export class QueueService {
  constructor(queue, native) {
    this.queue = queue; this.native = native; this.busy = false;
    queue.db.exec(`CREATE TABLE IF NOT EXISTS native_requests (
      task_id TEXT NOT NULL, asset_id TEXT NOT NULL, external_key TEXT NOT NULL,
      scoped_key TEXT NOT NULL UNIQUE, request_hash TEXT NOT NULL, tool_name TEXT NOT NULL,
      status TEXT NOT NULL CHECK(status IN ('running','unknown','completed')),
      lease_epoch INTEGER NOT NULL, operation_id TEXT, result_json TEXT, error_json TEXT,
      started_at INTEGER NOT NULL, updated_at INTEGER NOT NULL,
      PRIMARY KEY(task_id, asset_id, external_key)
    )`);
    // QueueService is constructed only after the broker's singleton endpoint is held.
    // A request that outlived its process has an unknown external outcome.
    queue.db.prepare("UPDATE native_requests SET status='unknown', error_json=?, updated_at=? WHERE status='running'").run(JSON.stringify({ code: 'BROKER_RESTARTED', message: 'The broker restarted before this request was settled.' }), queue.now());
  }
  requestIdentity(name, args, owner) {
    if (args.idempotency_key === undefined) return null;
    if (name !== 'photoshop_command_execute') throw new QueueError('IDEMPOTENCY_UNSUPPORTED_TOOL', 'Use photoshop_command_execute for a durable idempotency key.');
    if (typeof args.idempotency_key !== 'string' || !args.idempotency_key.trim() || args.idempotency_key.length > 250) throw new QueueError('INVALID_IDEMPOTENCY_KEY', 'Provide a non-empty key of at most 250 characters.');
    const { idempotency_key: external_key, ...payload } = args;
    const task_id = owner.original_task_id || owner.task_id, asset_id = owner.asset_id;
    const scoped_key = `ndc:${digest(stableJson([task_id, asset_id, external_key]))}`;
    const request_hash = digest(stableJson({ name, args: payload }));
    const prior = this.queue.db.prepare('SELECT * FROM native_requests WHERE task_id=? AND asset_id=? AND external_key=?').get(task_id, asset_id, external_key);
    if (prior && prior.request_hash !== request_hash) throw new QueueError('IDEMPOTENCY_PAYLOAD_MISMATCH', 'This key was already bound to a different native tool request.');
    if (prior && prior.status !== 'completed') throw new QueueError(prior.status === 'running' ? 'NATIVE_REQUEST_RUNNING' : 'NATIVE_REQUEST_UNKNOWN', 'Do not replay this request; inspect its recorded outcome and the Photoshop document.');
    return { task_id, asset_id, external_key, scoped_key, request_hash, prior };
  }
  startRequest(identity, name, owner) {
    if (!identity) return;
    const { task_id, asset_id, external_key, scoped_key, request_hash } = identity, now = this.queue.now();
    this.queue.db.prepare("INSERT INTO native_requests(task_id,asset_id,external_key,scoped_key,request_hash,tool_name,status,lease_epoch,started_at,updated_at) VALUES(?,?,?,?,?,?,'running',?,?,?)")
      .run(task_id, asset_id, external_key, scoped_key, request_hash, name, owner.epoch, now, now);
  }
  settleRequest(identity, status, result, error) {
    if (!identity) return;
    this.queue.db.prepare('UPDATE native_requests SET status=?,result_json=?,error_json=?,updated_at=? WHERE scoped_key=? AND request_hash=?')
      .run(status, result === undefined ? null : JSON.stringify(result), error === undefined ? null : JSON.stringify(error), this.queue.now(), identity.scoped_key, identity.request_hash);
  }
  closeCheckpoint(owner) {
    const cp = owner.checkpoint;
    if (!cp || owner.document_id === null || cp.document_id !== owner.document_id || cp.mutation !== owner.mutation ||
        !cp.files.some(f => f.role === 'working' && extname(f.path).toLowerCase() === '.psd') ||
        !cp.files.some(f => f.role === 'review' && extname(f.path).toLowerCase() === '.png')) throw new QueueError('CLOSE_CHECKPOINT_REQUIRED', 'Save the owned document as a recoverable PSD and review PNG before closing it.');
    for (const f of cp.files) {
      if (fileEvidence(f.path, this.queue.roots).sha256 !== f.sha256) throw new QueueError('CHECKPOINT_CHANGED', f.path);
      if (!owner.exports.some(x => x.path.toLowerCase() === f.path.toLowerCase() && x.sha256 === f.sha256 && x.document_id === owner.document_id && x.mutation === owner.mutation)) throw new QueueError('UNVERIFIED_SAVE', 'Closing requires actual exports from the current owned document.');
    }
  }
  list() { return [...this.native.tools.values()].map(x => x.definition).concat(queueDefinitions()); }
  async call(name, args = {}, context = {}) {
    if (name.startsWith('photoshop_queue_')) return envelope(await this.control(name.slice(16), args, context));
    const tool = this.native.tools.get(name); if (!tool) throw new QueueError('UNKNOWN_TOOL', name);
    // Metadata can be queried without taking the document. Do not dispatch runtime probes here.
    if (diagnostic.has(name)) return tool.handler(args);
    if (name === 'photoshop_host_describe') return envelope({ queue: this.queue.diagnose(), bridge: this.native.bridge.status(), runtime_binding: binding.version, note: 'Acquire a lease for live Photoshop state. Queue count alone does not prove idleness.' });
    if (name === 'photoshop_capability_list') return envelope({ commands: this.native.catalog.list(args), bridge: this.native.bridge.status() });
    if (name === 'photoshop_pairing_begin') throw new QueueError('PAIRING_NOT_A_QUEUE_OPERATION', 'Existing pairing is preserved. Diagnose the bridge before any explicit re-pairing.');
    if (name.startsWith('photoshop_job_') || name === 'photoshop_approval_request') throw new QueueError('USER_ASSISTED_NOT_QUEUED', 'This queue supports completed silent commands. Keep user-assisted jobs in an explicit manual reservation.');
    const owner = this.queue.auth(this.queue.read(), context);
    const commandId = name === 'photoshop_command_execute' ? args.command_id : nativeAliases[name];
    const command = commandId ? this.native.catalog.get(commandId) : null;
    if (!command && !['photoshop_state_get', 'photoshop_preview_get'].includes(name)) throw new QueueError('UNADAPTED_NATIVE_TOOL', 'This native tool has no verified queue effect classification; use the catalog command entrypoint.');
    if (command) {
      this.native.catalog.validate(commandId, name === 'photoshop_command_execute' ? args.args ?? {} : args);
      if (command.engine === 'user_assisted' || args.dialog_mode === 'display') throw new QueueError('MANUAL_RESERVATION_REQUIRED', 'Do not leave the automatic queue occupied by a native dialog.');
    }
    const identity = this.requestIdentity(name, args, owner);
    if (identity?.prior) return JSON.parse(identity.prior.result_json);
    if (this.busy) throw new QueueError('COMMAND_STILL_RUNNING', 'A native tool handler is still running.');
    if (owner.recovering && !['photoshop_state_get', 'photoshop_preview_get'].includes(name) && !['document.export', 'document.close'].includes(commandId)) throw new QueueError('RECOVERY_SAVE_ONLY', 'Recovery may inspect, save, and safely close the owned document; resume production in a fresh ticket.');
    const resourceCleanup = commandId === 'document.close';
    const mutates = !!command && command.risk !== 'read' && commandId !== 'document.export' && !resourceCleanup;
    this.busy = true; let op, ended = false, requestStarted = false;
    try {
      this.startRequest(identity, name, owner); requestStarted = !!identity;
      // Preserve the installed catalog, policy/permission gates, import/export protections,
      // native precondition checks and post-command checks. Never dispatch raw batchPlay.
      // Check the active document every time after the first binding. A user or
      // an un-migrated legacy client may have changed it outside this queue.
      if (owner.document_id !== null && !['document.create', 'document.open_allowed'].includes(commandId)) {
        const response = await this.native.tools.get('photoshop_state_get').handler({}), before = dataOf(response);
        if (response.isError || typeof before.hasDocument !== 'boolean') throw new QueueError('STATE_PROBE_FAILED', 'The live document identity could not be checked.');
        if (before.activeDocument?.id !== owner.document_id) throw new QueueError('ACTIVE_DOCUMENT_CHANGED', 'Current Photoshop document differs from this lease. Inspect and restore the intended document through a new safe acquisition.');
      }
      if (resourceCleanup) this.closeCheckpoint(owner);
      op = this.queue.begin(context, { tool: name, command_id: commandId, mutates, resource_cleanup: resourceCleanup, expected_until: Date.now() + (command?.risk === 'credit' ? 190000 : 70000) });
      if (identity) this.queue.db.prepare('UPDATE native_requests SET operation_id=? WHERE scoped_key=?').run(op.id, identity.scoped_key);
      const nativeArgs = identity ? { ...args, idempotency_key: identity.scoped_key } : args;
      const result = await tool.handler(nativeArgs), d = dataOf(result);
      const code = d.error?.code || d.code;
      const uncertain = ['TIMEOUT', 'CANCELLED', 'HOST_ERROR'].includes(code) || d.status === 'awaiting_user';
      const commandResult = d.result?.result ?? d.result;
      let documentId = d.after?.activeDocument?.id ?? d.result?.after?.activeDocument?.id ?? commandResult?.documentId ?? d.activeDocument?.id;
      if (resourceCleanup) documentId = owner.document_id;
      let exported;
      if (commandId === 'document.export' && d.ok === true) {
        if (documentId === undefined) { const state = dataOf(await this.native.tools.get('photoshop_state_get').handler({})); documentId = state.activeDocument?.id; }
        const path = commandResult?.path;
        if (!path || documentId === undefined) throw new QueueError('EXPORT_EVIDENCE_MISSING', 'Export response lacks a verifiable path or document identity.');
        exported = fileEvidence(path, this.queue.roots);
      }
      this.queue.end(context, op.id, { uncertain, documentId, exported, error: code, result: { ok: !result.isError, status: d.status } });
      ended = true;
      this.settleRequest(identity, uncertain ? 'unknown' : 'completed', result, code ? { code } : undefined);
      return result;
    } catch (e) {
      // A failed preflight never invalidates the image. After submission, preserve
      // uncertainty only if this exact operation still belongs to this lease.
      if (op && !ended) {
        try {
          const current = this.queue.read().owner;
          if (current?.task_id === context.task_id && current?.epoch === context.epoch && current?.token === context.token && current?.in_flight?.id === op.id) this.queue.end(context, op.id, { uncertain: true, error: `${e.code || 'ERROR'}: ${e.message}` });
        } catch (settlementError) { e.queue_settlement_error = { code: settlementError.code || 'ERROR', message: settlementError.message }; }
      }
      if (requestStarted) {
        try { this.settleRequest(identity, 'unknown', undefined, { code: e.code || 'ERROR', message: e.message }); }
        catch (recordError) { e.request_record_error = { code: recordError.code || 'ERROR', message: recordError.message }; }
      }
      throw e;
    } finally { this.busy = false; }
  }
  async control(action, args, context) {
    const q = this.queue;
    switch (action) {
      case 'status': return { ...q.diagnose(), automatic_recovery: { version: 1, abandoned_ms: q.abandonedMs, driver: 'waiting-head-acquire' }, bridge: this.native.bridge.status(), handler_running: this.busy };
      case 'enqueue': return q.enqueue(args);
      case 'acquire': {
        const result = q.acquire(args);
        if (result.reason !== 'BUSY' && result.reason !== 'ALREADY_HELD') return result;
        const recovered = await this.recoverForWaiter(args);
        return recovered?.released ? { ...q.acquire(args), recovery: recovered } : { ...result, ...(recovered ? { recovery: recovered } : {}) };
      }
      case 'cancel': return q.cancel(args);
      case 'heartbeat': return q.heartbeat(context);
      case 'checkpoint': if (this.busy) throw new QueueError('COMMAND_STILL_RUNNING', 'Wait for the live state probe or native operation before checkpointing.'); return q.checkpoint(context, args);
      case 'release': if (this.busy) throw new QueueError('COMMAND_STILL_RUNNING', 'Wait for the live state probe or native operation before releasing.'); return q.release(context);
      case 'external': return q.external(args);
      case 'recover': if (this.busy) throw new QueueError('COMMAND_STILL_RUNNING', 'No takeover while native handler is running.'); return q.recoverClaim(args);
      case 'probe':
      case 'lost_document': {
        const o = q.auth(q.read(), context);
        if (!o.recovering || this.busy) throw new QueueError('RECOVERY_REQUIRED', 'Acquire the single recovery lease first.');
        this.busy = true;
        try {
          // The same bridge worker awaits prior execution before polling this request.
          // A successful state response is a serialized barrier, unlike queuedCommands=0.
          const response = await this.native.tools.get('photoshop_state_get').handler({});
          const state = dataOf(response);
          if (response.isError || typeof state.hasDocument !== 'boolean') throw new QueueError('BARRIER_FAILED', 'No trustworthy live state response.');
          q.recoveryBarrier(context, { ok: true, state });
          if (action === 'lost_document') return q.recoverLostDocument(context, { no_documents: state.hasDocument === false && state.documentCount === 0 });
          return { reconciled: true, state, next: 'Inspect and save existing work, then checkpoint/release; never replay the timed-out command blindly.' };
        } finally { this.busy = false; }
      }
      case 'review': {
        const evidence = fileEvidence(args.record, q.roots), record = JSON.parse(readFileSync(evidence.path, 'utf8'));
        const released = q.read().reviews[args.task_id];
        const snapshot = released?.checkpoint?.files.find(f => f.role === 'review');
        if (!snapshot) throw new QueueError('NO_REVIEW_SNAPSHOT', 'No released image snapshot.');
        const status = record.visual_check_status;
        // The existing validator returns nonzero on FAIL. Validate its complete record
        // structure separately while preserving the true FAIL status.
        const { stdout } = await executeFile(binding.python, ['-X', 'utf8', '-B', join(here, 'validate-queue-review.py'), evidence.path, snapshot.path], { windowsHide: true, timeout: 30000 });
        const validation = JSON.parse(stdout);
        return q.review(args, { valid: validation.valid, status, sha256: snapshot.sha256, path: evidence.path, record_sha256: evidence.sha256 });
      }
      default: throw new QueueError('UNKNOWN_QUEUE_ACTION', action);
    }
  }

  async recoverForWaiter(args) {
    const q = this.queue, s = q.read(), o = s.owner;
    if (!o || s.external || this.busy || this.autoRecovering || o.in_flight ||
        s.waiting[0]?.task_id !== args.task_id || s.waiting[0]?.ticket !== args.ticket) return null;
    const resuming = o.recovering && o.task_id === args.task_id;
    if (!resuming && q.now() - o.heartbeat_at <= q.staleMs && q.now() - o.progress_at <= q.abandonedMs) return null;
    this.autoRecovering = true;
    try {
      const lease = resuming ? o : q.recoverClaim(args, true);
      const ctx = { task_id: lease.task_id, epoch: lease.epoch, token: lease.token };
      const { state } = await this.control('probe', {}, ctx);
      if (state.hasDocument === false && state.documentCount === 0 && lease.dirty) {
        if (lease.checkpoint?.mutation === lease.mutation) q.release(ctx);
        else await this.control('lost_document', {}, ctx);
      } else {
        if (lease.dirty) {
          if (state.activeDocument?.id !== lease.document_id) throw new QueueError('RECOVERY_DOCUMENT_MISMATCH', 'Keep the saved lease; do not export or close another document.');
          // Re-export even an old checkpoint: the live document may contain the
          // result of a previously unknown operation. No image edit is replayed.
          for (const format of ['psd', 'png']) {
            const response = await this.call('photoshop_command_execute', {
              command_id: 'document.export', args: { format, file_name: `queue_rescue_${lease.epoch}.${format}` },
              idempotency_key: `queue-rescue-${lease.epoch}-${format}`,
            }, ctx);
            if (response.isError || dataOf(response).ok === false) throw new QueueError('RECOVERY_EXPORT_FAILED', 'Rescue export failed; retry diagnosis without an approval dialog.');
          }
          const current = q.read().owner;
          const files = ['psd', 'png'].map(ext => {
            const f = current.exports.filter(x => x.mutation === current.mutation && extname(x.path).toLowerCase() === `.${ext}`).at(-1);
            if (!f) throw new QueueError('RECOVERY_EXPORT_MISSING', 'No current rescue export.');
            return { path: f.path, role: ext === 'psd' ? 'working' : 'review' };
          });
          q.checkpoint(ctx, { document_id: current.document_id, files, resume: 'Reopen rescue PSD, verify original source and cumulative counts, inspect current image before continuing. Automatic recovery is not visual approval.' });
          const closed = await this.call('photoshop_command_execute', { command_id: 'document.close', args: {}, idempotency_key: `queue-rescue-${lease.epoch}-close` }, ctx);
          if (closed.isError || dataOf(closed).ok === false) throw new QueueError('RECOVERY_CLOSE_FAILED', 'Keep rescue checkpoint; reconcile close result.');
        }
        q.release(ctx);
      }
      q.tx('recovery_waiter_renewed', current => {
        const waiter = current.waiting.find(x => x.task_id === args.task_id && x.ticket === args.ticket);
        if (waiter) waiter.waiting_last_seen_at = q.now();
        return { task_id: args.task_id, ticket: args.ticket };
      });
      return { released: true, original_task_id: lease.original_task_id, asset_id: lease.asset_id, epoch: lease.epoch };
    } catch (e) {
      return { released: false, code: e.code || 'RECOVERY_ERROR', message: e.message, next: 'Retry acquire to continue the same recovery; do not request routine approval or replay image edits.' };
    } finally { this.autoRecovering = false; }
  }
}

export async function createNative() {
  if (!binding.runtime || !existsSync(binding.runtime)) throw new QueueError('RUNTIME_NOT_FOUND', 'Photoshop MCP runtime was not found. Install the approved runtime or set NDC_PS_MCP_RUNTIME.');
  for (const [rel, sha] of Object.entries(binding.hashes)) {
    if (digest(readFileSync(join(binding.runtime, rel))) !== sha) throw new QueueError('RUNTIME_CHANGED', `Revalidate the native adapter before using changed runtime file: ${rel}`);
  }
  const { loadConfig } = await import(pathToFileURL(join(binding.runtime, 'dist/src/config.js')));
  const { CommandCatalog } = await import(pathToFileURL(join(binding.runtime, 'dist/src/catalog.js')));
  const { PhotoshopFullMcpServer } = await import(pathToFileURL(join(binding.runtime, 'dist/src/server.js')));
  const config = await loadConfig({ allowedRoots: binding.allowed_roots, exportDir: join(binding.state_dir, 'exports') });
  const native = await PhotoshopFullMcpServer.create(config, await CommandCatalog.load());
  await native.bridge.start();
  return native;
}
export async function startBroker({ native, stateDir = binding.state_dir, port = binding.port } = {}) {
  let key, q, api;
  const server = createServer(async (req, res) => {
    if (!api) { res.writeHead(503); res.end(); return; }
    const supplied = Buffer.from(String(req.headers.authorization || '').replace(/^Bearer /, '')), expected = Buffer.from(key);
    if (req.headers.origin || supplied.length !== expected.length || !timingSafeEqual(supplied, expected)) { res.writeHead(403); res.end(); return; }
    if (req.method !== 'POST' || req.url !== '/mcp') { res.writeHead(404); res.end(); return; }
    let request;
    try {
      let body = ''; for await (const c of req) { body += c; if (Buffer.byteLength(body) > 4 * 1024 * 1024) throw new Error('Request too large'); }
      request = JSON.parse(body);
      let result;
      if (request.method === 'initialize') result = { protocolVersion: '2024-11-05', capabilities: { tools: {} }, serverInfo: { name: 'ndc-photoshop-queue', version: '1.0.0' } };
      else if (request.method === 'tools/list') result = { tools: api.list() };
      else if (request.method === 'tools/call') result = await api.call(request.params.name, request.params.arguments || {}, request.params._queue || {});
      else if (request.method === 'ping') result = {};
      else throw new QueueError('METHOD_NOT_FOUND', request.method);
      res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ jsonrpc: '2.0', id: request.id, result }));
    } catch (e) {
      res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(JSON.stringify({ jsonrpc: '2.0', id: request?.id, result: envelope({ ok: false, code: e.code || 'ERROR', message: e.message }, true) }));
    }
  });
  // Bind the singleton endpoint BEFORE touching the shared journal or native bridge.
  // A second launcher must not mark the live broker's current command unknown.
  await new Promise((yes, no) => { server.once('error', no); server.listen(port, '127.0.0.1', yes); });
  try {
    mkdirSync(stateDir, { recursive: true });
    const keyPath = join(stateDir, 'client-key');
    try { key = readFileSync(keyPath, 'utf8').trim(); }
    catch (e) { if (e.code !== 'ENOENT') throw e; key = randomBytes(32).toString('hex'); writeFileSync(keyPath, key, { flag: 'wx', mode: 0o600 }); }
    q = new PhotoshopQueue(join(stateDir, 'queue.sqlite'), { roots: binding.allowed_roots }); q.recoverAfterRestart();
    api = new QueueService(q, native || await createNative());
  } catch (e) { await new Promise(r => server.close(r)); q?.close(); throw e; }
  writeFileSync(join(stateDir, 'broker.json'), JSON.stringify({ pid: process.pid, port, started_at: new Date().toISOString(), script: fileURLToPath(import.meta.url) }, null, 2));
  // Suspicion is observable even with no client polling. Recovery never replays work.
  let recovering = false;
  const monitor = setInterval(async () => {
    q.expireWaiting();
    const diagnosis = api.queue.diagnose();
    writeFileSync(join(stateDir, 'occupation-status.json'), JSON.stringify({ checked_at: new Date().toISOString(), ...diagnosis, handler_running: api.busy, bridge: api.native.bridge.status() }, null, 2));
    // Only provably unchanged or already checkpointed stale work is auto-recovered.
    // A live serialized probe must still succeed. Unknown/unsaved work needs diagnosis.
    if (diagnosis.owner_diagnosis === 'STALE_SAFE' && !api.busy && !recovering) {
      recovering = true;
      try {
        const recovery = q.recoverClaim({ task_id: 'ps-queue-watchdog' });
        const context = { task_id: recovery.task_id, epoch: recovery.epoch, token: recovery.token };
        await api.control('probe', {}, context);
        q.release(context);
      } catch (e) {
        writeFileSync(join(stateDir, 'recovery-needed.json'), JSON.stringify({ at: new Date().toISOString(), code: e.code || 'ERROR', message: e.message, action: 'Inspect status; resume the single recovery lease after the bridge responds.' }, null, 2));
      } finally { recovering = false; }
    }
  }, 5000);
  return { api, server, async close() { clearInterval(monitor); await new Promise(r => server.close(r)); await api.native.bridge.stop(); q.close(); } };
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const running = await startBroker();
  process.stderr.write('NDC Photoshop shared queue ready. No image has been opened.\n');
  for (const signal of ['SIGINT', 'SIGTERM']) process.once(signal, async () => { await running.close(); process.exit(0); });
}
