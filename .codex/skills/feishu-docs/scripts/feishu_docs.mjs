#!/usr/bin/env node

import { existsSync, readFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const skillDir = resolve(scriptDir, '..');
const workspaceRoot = resolve(skillDir, '..', '..', '..');
const envPath = join(workspaceRoot, '.env.feishu.local');
const runtimeCli = join(skillDir, 'runtime', 'dist', 'cli', 'index.js');

function fail(message, exitCode = 1) {
  process.stderr.write(`${message}\n`);
  process.exit(exitCode);
}

function unquote(value) {
  if (value.length < 2) return value;
  const first = value[0];
  const last = value[value.length - 1];
  return (first === last && (first === '"' || first === "'"))
    ? value.slice(1, -1)
    : value;
}

function loadLocalEnvironment() {
  if (!existsSync(envPath)) {
    fail(`Missing local Feishu configuration: ${envPath}`);
  }

  const local = {};
  for (const rawLine of readFileSync(envPath, 'utf8').split(/\r?\n/u)) {
    let line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    if (line.startsWith('export ')) line = line.slice(7).trim();

    const separator = line.indexOf('=');
    if (separator <= 0) continue;

    const key = line.slice(0, separator).trim();
    if (!/^[A-Za-z_][A-Za-z0-9_]*$/u.test(key)) continue;
    local[key] = unquote(line.slice(separator + 1).trim());
  }

  for (const key of ['FEISHU_APP_ID', 'FEISHU_APP_SECRET']) {
    if (!local[key] && !process.env[key]) {
      fail(`Missing required Feishu setting: ${key}`);
    }
  }

  return { ...process.env, ...local };
}

const localEnvironment = loadLocalEnvironment();

function invoke(toolName, params) {
  if (!existsSync(runtimeCli)) {
    fail(`Missing project-local Feishu runtime: ${runtimeCli}`);
  }

  const result = spawnSync(
    process.execPath,
    [runtimeCli, toolName, JSON.stringify(params)],
    {
      cwd: workspaceRoot,
      env: localEnvironment,
      encoding: 'utf8',
      maxBuffer: 64 * 1024 * 1024,
      windowsHide: true,
    },
  );

  if (result.error) fail(`Feishu runtime failed: ${result.error.message}`);

  const stdout = result.stdout.trim();
  let payload;
  try {
    payload = JSON.parse(stdout);
  } catch {
    const detail = result.stderr.trim() || stdout || `exit code ${result.status}`;
    fail(`Feishu runtime returned invalid output: ${detail}`);
  }

  if (result.status !== 0 || payload?.error) {
    fail(`Feishu request failed: ${payload?.error ?? `exit code ${result.status}`}`);
  }

  return payload;
}

function documentInfo(input) {
  const params = { documentId: input };
  if (/\/wiki\//iu.test(input)) params.documentType = 'wiki';
  return invoke('get_feishu_document_info', params);
}

function textFromElements(elements) {
  if (!Array.isArray(elements)) return '';
  return elements.map((element) => {
    if (element?.text_run) return element.text_run.content ?? '';
    if (element?.mention_doc) return element.mention_doc.title ?? '';
    if (element?.mention_user) return element.mention_user.user_id ? `@${element.mention_user.user_id}` : '@user';
    if (element?.equation) return element.equation.content ?? '';
    return '';
  }).join('');
}

function blockText(block) {
  const containers = [
    ['page', ''],
    ['heading1', '# '],
    ['heading2', '## '],
    ['heading3', '### '],
    ['heading4', '#### '],
    ['heading5', '##### '],
    ['heading6', '###### '],
    ['heading7', ''],
    ['heading8', ''],
    ['heading9', ''],
    ['text', ''],
    ['bullet', '- '],
    ['ordered', '1. '],
    ['quote', '> '],
    ['todo', '- [ ] '],
    ['code', ''],
    ['callout', ''],
  ];

  for (const [key, prefix] of containers) {
    const content = textFromElements(block?.[key]?.elements);
    if (content) return `${prefix}${content}`;
  }
  return '';
}

function orderedBlocks(blocks) {
  if (!Array.isArray(blocks) || blocks.length === 0) return [];

  const byId = new Map(blocks.map((block) => [block.block_id, block]));
  const visited = new Set();
  const ordered = [];

  function visit(block) {
    if (!block || visited.has(block.block_id)) return;
    visited.add(block.block_id);
    ordered.push(block);
    for (const childId of block.children ?? []) visit(byId.get(childId));
  }

  const root = blocks.find((block) => block.block_type === 1 && Array.isArray(block.children));
  if (root) {
    visited.add(root.block_id);
    for (const childId of root.children) visit(byId.get(childId));
  }
  for (const block of blocks) visit(block);
  return ordered;
}

function printInfo(info) {
  process.stdout.write(`${JSON.stringify(info, null, 2)}\n`);
}

function printDocument(input) {
  const info = documentInfo(input);
  const documentId = info.documentId ?? info.obj_token ?? input;
  const blocks = invoke('get_feishu_document_blocks', { documentId });
  const lines = orderedBlocks(blocks)
    .map(blockText)
    .filter((line) => line.trim().length > 0);

  const header = [
    `标题：${info.title ?? '(untitled)'}`,
    `文档 ID：${documentId}`,
    `文档类型：${info._type ?? info.obj_type ?? 'document'}`,
    `内容块：${Array.isArray(blocks) ? blocks.length : 0}`,
    '---',
  ];
  process.stdout.write(`${[...header, ...lines].join('\n')}\n`);
}

const [, , command, input] = process.argv;
if (!command || !input || !['read', 'info'].includes(command)) {
  fail('Usage: feishu_docs.mjs <read|info> <Feishu URL or document token>', 2);
}

if (command === 'info') printInfo(documentInfo(input));
else printDocument(input);

