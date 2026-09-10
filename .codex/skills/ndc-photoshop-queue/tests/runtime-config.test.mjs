import test from 'node:test';
import assert from 'node:assert/strict';
import { copyFileSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadRuntimeBinding } from '../scripts/runtime-config.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const scratch = resolve(here, '.test-data');
mkdirSync(scratch, { recursive: true });

test('runtime binding follows a relocated Skill tree with spaces and Chinese characters', t => {
  const root = mkdtempSync(join(scratch, '跨设备 Skill '));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const planning = join(root, '策划仓库'), engine = join(root, '工程仓库');
  const work = join(root, '美术 工作区'), local = join(root, 'Local App Data');
  const scripts = join(planning, '.codex', 'skills', 'ndc-photoshop-queue', 'scripts');
  const validator = join(planning, '.codex', 'skills', 'ndc-prop-delivery-review', 'scripts', 'stage_visual_check.py');
  mkdirSync(join(planning, 'production', 'art_pipeline'), { recursive: true });
  writeFileSync(join(planning, 'production', 'art_pipeline', 'skill_sources.json'), '{}');
  mkdirSync(scripts, { recursive: true });
  copyFileSync(join(here, '..', 'scripts', 'runtime-binding.json'), join(scripts, 'runtime-binding.json'));
  mkdirSync(dirname(validator), { recursive: true }); writeFileSync(validator, '# fixture');
  const runtime = join(local, 'PS_MCP', 'app', 'versions', '2.0.1-ndc2', 'runtime'); mkdirSync(runtime, { recursive: true });
  for (const path of [engine, work]) mkdirSync(path, { recursive: true });
  const binding = loadRuntimeBinding({ LOCALAPPDATA: local, USERPROFILE: root, NDC_PLANNING_ROOT: planning, NDC_ENGINE_ROOT: engine, NDC_ART_WORK_ROOT: work }, { scriptDir: scripts });
  assert.equal(binding.runtime, runtime);
  assert.equal(binding.visual_validator, validator);
  assert.deepEqual(binding.allowed_roots, [work, engine, planning, join(local, 'NDC', 'photoshop-queue', 'exports')]);
  assert.equal(binding.state_dir, join(local, 'NDC', 'photoshop-queue'));
});

test('explicit runtime and queue paths override per-user defaults', t => {
  const root = mkdtempSync(join(scratch, 'override-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const scripts = join(root, 'skills', 'ndc-photoshop-queue', 'scripts');
  mkdirSync(scripts, { recursive: true });
  copyFileSync(join(here, '..', 'scripts', 'runtime-binding.json'), join(scripts, 'runtime-binding.json'));
  const runtime = join(root, 'custom runtime'), state = join(root, 'custom state'), allowed = join(root, 'allowed');
  const validator = join(root, 'validator.py');
  for (const path of [runtime, state, allowed]) mkdirSync(path, { recursive: true }); writeFileSync(validator, '# fixture');
  const binding = loadRuntimeBinding({ NDC_PS_MCP_RUNTIME: runtime, NDC_PS_QUEUE_STATE_DIR: state, NDC_PS_ALLOWED_ROOTS: allowed, NDC_STAGE_VISUAL_VALIDATOR: validator }, { scriptDir: scripts });
  assert.equal(binding.runtime, runtime); assert.equal(binding.state_dir, state);
  assert.deepEqual(binding.allowed_roots, [allowed, join(state, 'exports')]); assert.equal(binding.visual_validator, validator);
});

test('queue export evidence is authorized without exposing private queue state', t => {
  const root = mkdtempSync(join(scratch, 'export-root-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const scripts = join(root, 'skills', 'ndc-photoshop-queue', 'scripts');
  mkdirSync(scripts, { recursive: true });
  copyFileSync(join(here, '..', 'scripts', 'runtime-binding.json'), join(scripts, 'runtime-binding.json'));
  const runtime = join(root, 'runtime'), state = join(root, 'state'), allowed = join(root, 'allowed');
  const validator = join(root, 'validator.py');
  for (const path of [runtime, state, allowed]) mkdirSync(path, { recursive: true });
  writeFileSync(validator, '# fixture');
  const binding = loadRuntimeBinding({ NDC_PS_MCP_RUNTIME: runtime, NDC_PS_QUEUE_STATE_DIR: state, NDC_PS_ALLOWED_ROOTS: allowed, NDC_STAGE_VISUAL_VALIDATOR: validator }, { scriptDir: scripts });
  assert.equal(binding.allowed_roots.includes(state), false);
  assert.equal(binding.allowed_roots.includes(join(state, 'exports')), true);
});
