import { readFileSync, writeFileSync, mkdirSync, openSync, closeSync, unlinkSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash, randomUUID } from 'node:crypto';
import { spawn } from 'node:child_process';

const here = dirname(fileURLToPath(import.meta.url));
export const settings = JSON.parse(readFileSync(join(here, 'runtime-binding.json'), 'utf8'));
const delay = ms => new Promise(r => setTimeout(r, ms));
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
      // Only clear a lock with a recorded, provably dead creator process.
      let owner; try { owner = JSON.parse(readFileSync(lock, 'utf8')); } catch {}
      if (owner?.pid) { try { process.kill(owner.pid, 0); } catch (p) { if (p.code === 'ESRCH') { unlinkSync(lock); handle = openSync(lock, 'wx'); } } }
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
export function retainLease(context, name, result) {
  if (result.isError) return context;
  const d = resultData(result);
  if (name === 'photoshop_queue_enqueue') return { ...context, task_id: d.task_id || context.task_id, ticket: d.ticket };
  if (name === 'photoshop_queue_acquire' && d.acquired || name === 'photoshop_queue_recover' && d.token) return { task_id: d.task_id, ticket: d.ticket, epoch: d.epoch, token: d.token };
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
  const request = opts.request ? JSON.parse(readFileSync(opts.request, 'utf8').replace(/^\uFEFF/, '')) : { name: `photoshop_queue_${opts.action || 'status'}`, arguments: {} };
  const task = opts.task || request.arguments?.task_id;
  let context = task ? { task_id: task } : {};
  let session;
  if (task) {
    mkdirSync(join(settings.state_dir, 'clients'), { recursive: true });
    session = join(settings.state_dir, 'clients', `${createHash('sha256').update(task).digest('hex')}.json`);
    try { context = JSON.parse(readFileSync(session, 'utf8')); } catch (e) { if (e.code !== 'ENOENT') throw e; }
  }
  request.arguments ||= {};
  if (task && ['enqueue', 'acquire', 'recover', 'cancel', 'review', 'external'].some(x => request.name === `photoshop_queue_${x}`)) request.arguments.task_id ||= task;
  if (request.name === 'photoshop_queue_acquire' || request.name === 'photoshop_queue_cancel') request.arguments.ticket ||= context.ticket;
  const result = await call(request.name, request.arguments, context);
  context = retainLease(context, request.name, result);
  if (session) writeFileSync(session, JSON.stringify(context), { mode: 0o600 });
  // Do not echo bearer credentials or private lease tokens into conversation logs.
  const output = resultData(result);
  console.log(JSON.stringify(output, (k, v) => k === 'token' ? '[stored in local task session]' : v, 2));
  if (result.isError) process.exitCode = 2;
}
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) cli().catch(e => { console.error(e.message); process.exitCode = 2; });
