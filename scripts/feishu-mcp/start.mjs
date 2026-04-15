#!/usr/bin/env node
import { writeFileSync, appendFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const logFile = join(__dirname, 'startup.log');

function log(msg) {
  const ts = new Date().toISOString();
  appendFileSync(logFile, `[${ts}] ${msg}\n`);
}

log('=== feishu-mcp starting ===');
log(`cwd: ${process.cwd()}`);
log(`argv: ${JSON.stringify(process.argv)}`);
log(`NODE_ENV: ${process.env.NODE_ENV}`);
log(`FEISHU_APP_ID: ${process.env.FEISHU_APP_ID ? 'set' : 'NOT SET'}`);

// Set defaults
process.env.FEISHU_APP_ID = process.env.FEISHU_APP_ID || 'cli_a9462f8ff6b99cc2';
process.env.FEISHU_APP_SECRET = process.env.FEISHU_APP_SECRET || 'kEYzXf9uYmB8hEifIGxNodhCosdbhNXi';
process.env.FEISHU_BASE_URL = process.env.FEISHU_BASE_URL || 'https://open.feishu.cn/open-apis';
process.env.FEISHU_AUTH_TYPE = process.env.FEISHU_AUTH_TYPE || 'tenant';
process.env.NODE_ENV = process.env.NODE_ENV || 'cli';
process.env.PORT = process.env.PORT || '3334';

log('env set, importing cli.js...');

try {
  await import('./dist/cli.js');
  log('cli.js imported successfully');
} catch (err) {
  log(`ERROR: ${err.message}\n${err.stack}`);
  process.exit(1);
}
