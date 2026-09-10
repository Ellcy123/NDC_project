import { readFileSync, writeFileSync, mkdirSync, openSync, closeSync, unlinkSync, renameSync, statSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';
import { spawn } from 'node:child_process';
import { binding as settings } from './runtime-config.mjs';

const here = dirname(fileURLToPath(import.meta.url));
export { settings };
const delay = ms => new Promise(r => setTimeout(r, ms));
export function reclaimStartLock(path, now = Date.now()) {
  let owner, age = Infinity;
  try { owner = JSON.parse(readFileSync(path, 'utf8')); age = Math.max(0, now - statSync(path).mtimeMs); }
  catch (error) { if (error.code === 'ENOENT') return false; try { age = Math.max(0, now - statSync(path).mtimeMs); } catch {} }
  let alive = false;
  if (Number.isInteger(owner?.pid) && owner.pid > 0) {
    try { process.kill(owner.pid, 0); alive = true; } catch (error) { if (!['ESRCH', 'EPERM'].includes(error.code)) throw error; alive = error.code === 'EPERM'; }
  }
  // The TCP endpoint remains the real singleton fence. An invalid/dead lock, or
  // a startup process that has not produced a broker after 30 seconds, must not
  // permanently disable all future clients.
  if ((!alive && age >= 1000) || age >= 30000) { try { unlinkSync(path); return true; } catch (error) { if (error.code !== 'ENOENT') throw error; } }
  return false;
}
export function loadLeaseSession(path, task) {
  try {
    const value = JSON.parse(readFileSync(path, 'utf8'));
    if (!value || typeof value !== 'object' || Array.isArray(value) || (value.task_id && value.task_id !== task)) throw new Error('Invalid or mismatched client lease session.');
    return { ...value, task_id: task };
  } catch (error) {
    if (error.code === 'ENOENT') return { task_id: task };
    const quarantine = `${path}.corrupt-${Date.now()}`;
    try { renameSync(path, quarantine); }
    catch (renameError) { throw new Error(`CLIENT_SESSION_CORRUPT: ${renameError.code || renameError.message}`); }
    return { task_id: task };
  }
}
export function saveLeaseSession(path, context) {
  const temporary = `${path}.tmp-${process.pid}-${randomUUID()}`;
  try {
    writeFileSync(temporary, JSON.stringify(context), { mode: 0o600, flag: 'wx' });
    renameSync(temporary, path);
  } finally { if (existsSync(temporary)) try { unlinkSync(temporary); } catch {} }
}
export function leaseContextChanged(previous, current) {
  return JSON.stringify(previous) !== JSON.stringify(current);
}
export function bindTaskRequest(request, task, context = {}) {
  if (!request || typeof request !== 'object' || Array.isArray(request) || typeof request.name !== 'string' || !request.name.trim()) throw new Error('INVALID_REQUEST_FILE: top-level name and object arguments are required.');
  if (request.arguments === undefined) request.arguments = {};
  if (!request.arguments || typeof request.arguments !== 'object' || Array.isArray(request.arguments)) throw new Error('INVALID_REQUEST_FILE: arguments must be a JSON object.');
  const action = request.name.startsWith('photoshop_queue_') ? request.name.slice(16) : null;
  if (task && ['enqueue', 'acquire', 'recover', 'cancel', 'review', 'external'].includes(action)) request.arguments.task_id = task;
  if (action === 'acquire' || action === 'cancel') request.arguments.ticket ||= context.ticket;
  return request;
}
export async function rpc(method, params = {}, timeout = 240000) {
  const key = readFileSync(join(settings.state_dir, 'client-key'), 'utf8').trim();
  const response = await fetch(`http://127.0.0.1:${settings.port}/mcp`, { method: 'POST', headers: { Authorization: `Bearer ${key}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: randomUUID(), method, params }), signal: AbortSignal.timeout(timeout) });
  if (!response.ok) throw new Error(`Queue HTTP ${response.status}`);
  return (await response.json()).result;
}
export async function ensureBroker() {
  try { await rpc('ping', {}, 1500); return; } catch (e) { if (e.message.includes('HTTP 403')) throw e; }
  mkdirSync(settings.state_dir, { recursive: true });
  const lock = join(settings.state_dir, 'start.lock'); let handle;
  try {
    try { handle = openSync(lock, 'wx'); }
    catch (e) {
      if (e.code !== 'EEXIST') throw e;
      if (reclaimStartLock(lock)) handle = openSync(lock, 'wx');
    }
    if (handle !== undefined) {
      writeFileSync(handle, JSON.stringify({ pid: process.pid, at: Date.now() }));
      try { await rpc('ping', {}, 1000); return; } catch {}
      const out = openSync(join(settings.state_dir, 'broker.stdout.log'), 'a'), err = openSync(join(settings.state_dir, 'broker.stderr.log'), 'a');
      const child = spawn(process.execPath, [join(here, 'broker.mjs')], { detached: true, windowsHide: true, stdio: ['ignore', out, err], env: { ...process.env, PS_MCP_ALLOWED_ROOTS: settings.allowed_roots.join(';') } });
      child.unref(); closeSync(out); closeSync(err);
    }
    for (let i = 0; i < 40; i++) { await delay(250); try { await rpc('ping', {}, 1000); return; } catch {} }
    throw new Error('Shared PS broker did not start; inspect broker.stderr.log. No Photoshop process was stopped.');
  } finally { if (handle !== undefined) { closeSync(handle); unlinkSync(lock); } }
}
export const resultData = result => result.structuredContent ?? {};
export function buildResumeCheck(health, status, task, context = {}, checkedAt = new Date().toISOString()) {
  const waiting = Array.isArray(status?.waiting) ? status.waiting : [];
  const ownWaiting = waiting.find(item => item?.task_id === task) || null;
  const ownsQueue = Boolean(task && status?.owner?.task_id === task);
  const blockers = Array.isArray(health?.blockers) ? health.blockers : [];
  const photoshopOperational = Boolean(
    health?.runtime?.ok &&
    health?.bridge?.paired === true &&
    health?.bridge?.connected === true &&
    health?.storage?.ok &&
    health?.storage?.writable
  );
  let resumeAction;
  if (ownsQueue) resumeAction = 'acquire_existing_owner_to_rebind_and_probe';
  else if (ownWaiting) resumeAction = 'acquire_existing_ticket';
  else if (health?.ok) resumeAction = 'enqueue_prepared_work_then_acquire';
  else if (blockers.some(item => ['IDLE_HELD', 'STALE_SAFE', 'STALE_UNSAVED', 'RECOVERY_REQUIRED'].includes(item?.code))) resumeAction = 'enqueue_prepared_work_then_acquire_to_drive_recovery';
  else resumeAction = 'follow_current_health_next_action';
  return {
    schema: 'ndc-ps-resume-check/v1',
    checked_at: checkedAt,
    task_id: task || null,
    photoshop_operational: photoshopOperational,
    health_ok: health?.ok === true,
    ready_for_new_lease: health?.ready_for_new_lease === true,
    queue_diagnosis: status?.diagnosis || health?.queue?.diagnosis || null,
    owner_task_id: status?.owner?.task_id || null,
    own_waiting_ticket: ownWaiting?.ticket || context?.ticket || null,
    current_blockers: blockers,
    old_failure_snapshot_authoritative: false,
    resume_action: resumeAction,
    next_action: health?.next_action || null,
    health,
    status
  };
}
export function retainLease(context, name, result) {
  const d = resultData(result);
  const empty = { task_id: d.task_id || context.task_id };
  if (result.isError) {
    if (['STALE_LEASE', 'TICKET_NOT_WAITING', 'NO_OWNER', 'FOREIGN_DEVICE_LEASE', 'BROKER_INSTANCE_CHANGED', 'DEVICE_HANDOFF_REQUIRED'].includes(d.code)) return empty;
    return context;
  }
  if (name === 'photoshop_queue_enqueue') return { ...empty, ticket: d.ticket };
  if (name === 'photoshop_queue_acquire' && d.reason === 'TICKET_NOT_WAITING') return empty;
  if (name === 'photoshop_queue_acquire' && d.acquired || name === 'photoshop_queue_recover' && d.token) return { task_id: d.task_id, ticket: d.ticket, epoch: d.epoch, token: d.token, device_id: d.device_id, broker_instance_id: d.broker_instance_id };
  if (['photoshop_queue_release', 'photoshop_queue_lost_document'].includes(name)) return { task_id: context.task_id };
  return context;
}
export async function call(name, args = {}, context = {}) {
  return rpc('tools/call', { name, arguments: args, _queue: context });
}
async function cli() {
  const opts = {};
  for (let i = 2; i < process.argv.length; i += 2) { if (!process.argv[i].startsWith('--') || process.argv[i + 1] === undefined) throw new Error('Use --task ID --request JSON_FILE, or --task ID --action status'); opts[process.argv[i].slice(2)] = process.argv[i + 1]; }
  await ensureBroker();
  const action = opts.action || 'status';
  const request = opts.request ? JSON.parse(readFileSync(opts.request, 'utf8').replace(/^\uFEFF/, '')) : action === 'resume-check' ? null : { name: `photoshop_queue_${action}`, arguments: {} };
  const task = opts.task || request?.arguments?.task_id;
  let context = task ? { task_id: task } : {};
  let session;
  if (task) {
    mkdirSync(settings.client_session_dir, { recursive: true });
    session = join(settings.client_session_dir, `${createHash('sha256').update(task).digest('hex')}.json`);
    context = loadLeaseSession(session, task);
  }
  if (!request) {
    if (!task) throw new Error('RESUME_CHECK_TASK_REQUIRED: use --task with --action resume-check.');
    const health = resultData(await call('photoshop_queue_health', {}, context));
    const status = resultData(await call('photoshop_queue_status', {}, context));
    console.log(JSON.stringify(buildResumeCheck(health, status, task, context), null, 2));
    return;
  }
  bindTaskRequest(request, task, context);
  const priorContext = { ...context };
  const result = await call(request.name, request.arguments, context);
  context = retainLease(context, request.name, result);
  // Read-only observations do not change the private lease context. Avoid an
  // unnecessary session rewrite so health/status remain usable when the
  // sandbox can read shared broker state but cannot write beneath LocalAppData.
  if (session && leaseContextChanged(priorContext, context)) saveLeaseSession(session, context);
  // Do not echo bearer credentials or private lease tokens into conversation logs.
  const output = resultData(result);
  console.log(JSON.stringify(output, (k, v) => k === 'token' ? '[stored in local task session]' : v, 2));
  if (result.isError) process.exitCode = 2;
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) cli().catch(e => { console.error(e.message); process.exitCode = 2; });
