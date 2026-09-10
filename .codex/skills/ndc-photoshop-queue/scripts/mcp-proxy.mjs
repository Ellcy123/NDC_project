#!/usr/bin/env node
import { pathToFileURL } from 'node:url';
import { join } from 'node:path';
import { settings, ensureBroker, rpc, call, retainLease } from './queue-client.mjs';

// Each Codex task has a small stdio frontend; all share one native policy/UXP host.
const moduleUrl = path => pathToFileURL(join(settings.runtime, 'node_modules/@modelcontextprotocol/sdk/dist/esm', path));
const { Server } = await import(moduleUrl('server/index.js'));
const { StdioServerTransport } = await import(moduleUrl('server/stdio.js'));
const { CallToolRequestSchema, ListToolsRequestSchema } = await import(moduleUrl('types.js'));
await ensureBroker();
let context = {};
const server = new Server({ name: 'photoshop-full-mcp', version: '2.0.1-ndc-queue2' }, { capabilities: { tools: {} }, instructions: 'Shared Photoshop queue: read ndc-photoshop-queue. Run health, enqueue the real task and asset, acquire, then use atomic handoff after the final mutation. Different tasks may submit concurrently; Photoshop editing stays serial. Lost client context rebinds through acquire plus a live probe. Tokens, Bridge instances and document IDs never cross computers. Do not bypass or restart this broker, share queue.sqlite, or treat a timeout as release.' });
server.setRequestHandler(ListToolsRequestSchema, () => rpc('tools/list'));
server.setRequestHandler(CallToolRequestSchema, async request => {
  const { name } = request.params, args = request.params.arguments || {};
  if (args.task_id) context.task_id ||= args.task_id;
  const result = await call(name, args, context);
  context = retainLease(context, name, result);
  return result;
});
await server.connect(new StdioServerTransport());
let ending = false;
async function shutdown() {
  if (ending) return; ending = true;
  // This succeeds only for unchanged or safely checkpointed work. Dirty/unknown
  // work remains durably occupied and is recovered by the single recovery path.
  if (context.token) await call('photoshop_queue_release', {}, context).catch(() => {});
  await server.close(); process.exit(0);
}
process.stdin.once('end', shutdown);
process.once('SIGINT', shutdown); process.once('SIGTERM', shutdown);
