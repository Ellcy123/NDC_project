import { existsSync, mkdirSync, readFileSync, unlinkSync, writeFileSync } from 'node:fs';
import { hostname } from 'node:os';
import { dirname, isAbsolute, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const defaultScriptDir = dirname(fileURLToPath(import.meta.url));

function readJson(path) {
  return JSON.parse(readFileSync(path, 'utf8').replace(/^\uFEFF/, ''));
}

function firstExisting(candidates) {
  return candidates.find(value => value && existsSync(value)) || candidates.find(Boolean);
}

function absolute(value, label) {
  if (!value || !isAbsolute(value)) throw new Error(label + ' must be an absolute path.');
  return resolve(value);
}

function discoverPlanningRoot(scriptDir, environment) {
  if (environment.NDC_PLANNING_ROOT) return absolute(environment.NDC_PLANNING_ROOT, 'NDC_PLANNING_ROOT');
  let current = resolve(scriptDir);
  while (true) {
    if (existsSync(join(current, 'production', 'art_pipeline', 'skill_sources.json'))) return current;
    const nested = join(current, 'NDC_project');
    if (existsSync(join(nested, 'production', 'art_pipeline', 'skill_sources.json'))) return nested;
    const parent = dirname(current);
    if (parent === current) return null;
    current = parent;
  }
}

function readMachineConfig(planningRoot) {
  if (!planningRoot) return {};
  const path = join(planningRoot, 'ndc.local.json');
  return existsSync(path) ? readJson(path) : {};
}

function siblingSkillScript(scriptDir, skillName, relativeScript) {
  const currentSkill = dirname(scriptDir);
  const skillsRoot = dirname(currentSkill);
  return resolve(skillsRoot, skillName, ...relativeScript.split('/'));
}

function writableStateDirectory(path) {
  const probe = join(path, `.ndc-write-probe-${process.pid}-${Date.now()}`);
  try {
    mkdirSync(path, { recursive: true });
    writeFileSync(probe, 'probe', { flag: 'wx' });
    unlinkSync(probe);
    return true;
  } catch {
    try { if (existsSync(probe)) unlinkSync(probe); } catch {}
    return false;
  }
}

function portableHostSegment(value = hostname()) {
  const segment = String(value || 'unknown-host').replace(/[^A-Za-z0-9._-]+/g, '-').replace(/^-+|-+$/g, '');
  return segment || 'unknown-host';
}

export function loadRuntimeBinding(environment = process.env, options = {}) {
  const scriptDir = resolve(options.scriptDir || defaultScriptDir);
  const manifest = readJson(join(scriptDir, 'runtime-binding.json'));
  if (manifest.schema !== 'ndc-photoshop-runtime-binding/v2') throw new Error('runtime-binding.json must use ndc-photoshop-runtime-binding/v2.');

  const planningRoot = discoverPlanningRoot(scriptDir, environment);
  const machineConfig = readMachineConfig(planningRoot);
  const localAppData = environment.LOCALAPPDATA ? absolute(environment.LOCALAPPDATA, 'LOCALAPPDATA') : null;
  const userProfile = environment.USERPROFILE ? absolute(environment.USERPROFILE, 'USERPROFILE') : null;
  const runtimeCandidates = [
    environment.NDC_PS_MCP_RUNTIME && absolute(environment.NDC_PS_MCP_RUNTIME, 'NDC_PS_MCP_RUNTIME'),
    localAppData && join(localAppData, ...manifest.runtime.local_app_data_relative.split('/')),
  ];
  const pythonCandidates = [
    environment.NDC_PYTHON_EXE && absolute(environment.NDC_PYTHON_EXE, 'NDC_PYTHON_EXE'),
    userProfile && join(userProfile, '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies', 'python', 'python.exe'),
    environment.PYTHON,
    'python',
  ];
  const configuredRoots = environment.NDC_PS_ALLOWED_ROOTS
    ? environment.NDC_PS_ALLOWED_ROOTS.split(';').filter(Boolean).map(value => absolute(value, 'NDC_PS_ALLOWED_ROOTS'))
    : [
        environment.NDC_ART_WORK_ROOT || machineConfig.work_root,
        environment.NDC_ENGINE_ROOT || machineConfig.engine_root,
        planningRoot || machineConfig.planning_root,
      ].filter(Boolean).map(value => absolute(value, 'NDC root'));
  if (!configuredRoots.length) throw new Error('Cannot resolve an allowed NDC root. Run through ndc_art.py or set NDC_PLANNING_ROOT/NDC_PS_ALLOWED_ROOTS.');
  const defaultStateDir = localAppData && join(localAppData, ...manifest.state.local_app_data_relative.split('/'));
  const fallbackRoot = environment.NDC_ART_WORK_ROOT || machineConfig.work_root;
  const stateDir = environment.NDC_PS_QUEUE_STATE_DIR
    ? absolute(environment.NDC_PS_QUEUE_STATE_DIR, 'NDC_PS_QUEUE_STATE_DIR')
    : defaultStateDir && writableStateDirectory(defaultStateDir)
      ? defaultStateDir
      : fallbackRoot
        ? join(absolute(fallbackRoot, 'NDC work root'), 'PS_MCP', `queue-state-${portableHostSegment(options.hostname)}`)
        : defaultStateDir;
  if (!stateDir) throw new Error('Cannot resolve the per-user queue state directory. Set NDC_PS_QUEUE_STATE_DIR.');
  const tempRoot = environment.TEMP
    ? absolute(environment.TEMP, 'TEMP')
    : environment.TMP && absolute(environment.TMP, 'TMP');
  const clientSessionDir = environment.NDC_PS_QUEUE_CLIENT_STATE_DIR
    ? absolute(environment.NDC_PS_QUEUE_CLIENT_STATE_DIR, 'NDC_PS_QUEUE_CLIENT_STATE_DIR')
    : tempRoot
      ? join(tempRoot, ...(manifest.state.client_temp_relative || 'NDC/photoshop-queue/clients').split('/'))
      : join(stateDir, 'clients');
  const port = Number(environment.NDC_PS_QUEUE_PORT || manifest.port);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('NDC_PS_QUEUE_PORT must be an integer from 1 to 65535.');

  const exportRoot = join(stateDir, 'exports');
  return {
    schema: manifest.schema,
    version: manifest.version,
    runtime: firstExisting(runtimeCandidates),
    python: firstExisting(pythonCandidates),
    visual_validator: environment.NDC_STAGE_VISUAL_VALIDATOR
      ? absolute(environment.NDC_STAGE_VISUAL_VALIDATOR, 'NDC_STAGE_VISUAL_VALIDATOR')
      : siblingSkillScript(scriptDir, manifest.visual_validator.skill, manifest.visual_validator.script),
    // Native document.export always writes beneath the queue-owned export
    // folder. Authorize only that output subtree, never the state directory
    // that also contains client keys, sessions, and the queue database.
    allowed_roots: [...new Set([...configuredRoots, exportRoot])],
    state_dir: resolve(stateDir),
    state_dir_fallback: !environment.NDC_PS_QUEUE_STATE_DIR && Boolean(defaultStateDir) && resolve(stateDir) !== resolve(defaultStateDir),
    client_session_dir: resolve(clientSessionDir),
    port,
    hashes: manifest.hashes,
  };
}

export const binding = loadRuntimeBinding();
