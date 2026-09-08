"""Scene handoff/result checks; never submits MJ or writes production approvals."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

from PIL import Image

VIEWS = {'exploration': ['eye_level'], 'non_exploration': ['frontal', 'oblique', 'overhead_45']}
STYLE_KEYS = ('city_rain', 'character_graphic')
LOCK_CHECKS = {'source_lookup', 'exact_prompts', 'shared_space', 'global_style', 'view_set',
               'empty_background', 'deferred_props', 'reference_roles'}
NO_CHARACTERS = {'people', 'person', 'humans', 'characters', 'crowds', 'figures', 'faces', 'bodies', 'silhouettes'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def digest(value):
    return text_sha(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')))


def contract_hashes(handoff, lock, files):
    """Only a shared change invalidates all views; local prompt edits stay local."""
    shared = {key: handoff[key] for key in ('scene', 'master_state', 'visual_brief', 'prop_policy',
              'normalized_requirement', 'texture_contract', 'parameters', 'framing_context', 'references')}
    source_roles = set(lock['source_roles']) | {r for f in lock['shared_space_facts'] for r in f['source_roles']}
    reference_hashes = {}
    for reference in handoff['references']:
        if reference.get('status') == 'use':
            source = Path(reference['file']).resolve()
            match = next((row for row in files.values() if row['path'] == source), None)
            require(match, 'used visual reference must be frozen with its current hash')
            reference_hashes[str(source)] = match['sha256']
    shared.update(shared_space_facts=lock['shared_space_facts'], style_reference_sha256=lock['style_reference_sha256'],
                  source_hashes={r: files[r]['sha256'] for r in sorted(source_roles)})
    if reference_hashes:
        shared['reference_hashes'] = reference_hashes
    return digest(shared), {v['id']: digest(v) for v in handoff['view_prompts']}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def file_map(rows, base):
    require(isinstance(rows, list), 'files must be an explicit role/path/hash array')
    result = {}
    for row in rows:
        require(isinstance(row, dict) and row.get('role') and row['role'] not in result, 'missing or repeated file role')
        path = Path(row['path'])
        path = (base / path).resolve() if not path.is_absolute() else path.resolve()
        require(path.is_file() and sha(path) == row.get('sha256'), 'file missing or changed: ' + row['role'])
        result[row['role']] = dict(row, path=path)
    return result


def role_file(files, role):
    require(role in files, 'missing packet/result file role: ' + str(role))
    return files[role]['path']


def workflow():
    path = Path(__file__).resolve().parents[2] / 'ndc-midjourney-operator/scripts/art_workflow_state.py'
    require(path.is_file(), 'restore the declared MJ production-record dependency')
    spec = importlib.util.spec_from_file_location('ndc_scene_pipeline_workflow', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def project_validator(name):
    for parent in Path(__file__).resolve().parents:
        candidate = parent / 'scripts' / name
        if candidate.is_file():
            return candidate
    raise ValueError('restore existing project validator: ' + name)


def run_validator(name, *args):
    # Executable paths come from the project, never from packet instructions.
    script = project_validator(name)
    outcome = subprocess.run([sys.executable, '-B', str(script), *map(str, args)],
                             capture_output=True, text=True, encoding='utf-8', check=False)
    require(outcome.returncode == 0, name + ': ' + (outcome.stdout + outcome.stderr).strip())


def prompt_checks(view):
    prompt = view.get('prompt_en')
    require(isinstance(prompt, str) and prompt.strip() and view.get('prompt_zh'), 'both exact view prompts are required')
    require(len(re.findall(r'--ar\s+2:1(?=\s|$)', prompt)) == 1 and len(re.findall(r'--ar\b', prompt)) == 1,
            'each exact prompt requires --ar 2:1 once')
    require(not re.search(r'--(?:v|version|model)\b', prompt, re.I), 'model flags must not be baked into exact prompt')
    parts = re.split(r'--no\s+', prompt)
    require(len(parts) == 2 and '--' not in parts[1], 'one final character --no parameter is required')
    require(NO_CHARACTERS <= {x.strip().lower() for x in parts[1].split(',')}, 'character exclusions are incomplete')
    require(not re.search(r'\b(?:people|person|humans?|characters?|crowds?|figures?|faces?|bodies|silhouettes?)\b', parts[0], re.I),
            'character language leaked into the positive scene prompt')
    for key in ('position', 'view_direction', 'perspective', 'camera_height', 'horizon', 'pitch', 'scale_calibration'):
        require(view.get('camera_contract', {}).get(key), 'incomplete camera contract: ' + key)
    for key in ('viewpoint_change', 'foreground', 'middle_ground', 'background', 'lateral_layout', 'architecture_relations', 'camera_calibration'):
        require(view.get('scene_description', {}).get(key), 'incomplete visible scene description: ' + key)


def _release(packet, base):
    require(packet.get('schema') == 'ndc-art-stage-packet/v1' and packet.get('pipeline_kind') == 'scene_mj', 'wrong scene packet kind')
    require(packet.get('execution_mode') in {'validation', 'production'}, 'execution_mode must come from the pipeline plan')
    files = file_map(packet['files'], base)
    payload = packet['payload']
    handoff_path = role_file(files, payload['handoff_role'])
    handoff = read(handoff_path)
    require(handoff.get('handoff_version') == 'ndc-mj-scene/v4' and handoff.get('workflow_end_stage') == 'mj_image_delivery', 'exact v4 MJ-native endpoint required')
    scene = handoff['scene']
    require(scene.get('id') == packet['unit_id'] and scene.get('mode') in VIEWS, 'scene identity/mode mismatch')
    required = VIEWS[scene['mode']]
    require(scene.get('name') and scene.get('canvas_use') in {'primary_exploration', 'story_progression'}, 'scene name/canvas use missing')
    require(handoff.get('original_requirement') and handoff.get('master_state'), 'source requirement/master state missing')
    for section in ('visual_brief', 'normalized_requirement', 'texture_contract', 'framing_context', 'delivery_contract', 'operator_notes'):
        require(isinstance(handoff.get(section), dict) and handoff[section], 'incomplete canonical v4 section: ' + section)
    require(handoff.get('parameters', {}).get('generation_aspect_ratio') == '2:1' and
            handoff['parameters'].get('model') == 'latest' and handoff['parameters'].get('quality') == 'hd_if_available', 'v4 aspect/model/HD policy changed')
    require(handoff['operator_notes'].get('iteration_budget_per_view') == 3, 'retain the cumulative three-round view budget')
    require(handoff.get('prop_policy', {}).get('mode') == 'defer_gameplay_props', 'gameplay-prop deferral boundary missing')
    require(handoff['prop_policy'].get('ambient_dressing') == 'sparse_period_appropriate_noninteractive', 'ambient dressing boundary changed')
    require('empty environment with no visible characters' in handoff['normalized_requirement'].get('hard', []), 'hard empty-background requirement missing')
    require(handoff['texture_contract'].get('style_authority_locked') is True and
            handoff['texture_contract'].get('style_changing_cleanup_language_forbidden') is True, 'global style must be locked before publishing views')
    require(handoff['delivery_contract'].get('artifact') == 'native_mj_image' and
            handoff['delivery_contract'].get('preserve_original_pixels') is True, 'native pixels are the delivery endpoint')
    views = handoff.get('view_prompts', [])
    require([v.get('id') for v in views] == required, 'publish the full ordered view set for one scene')
    for view in views:
        prompt_checks(view)
        camera = view['camera_contract']
        if scene['mode'] == 'exploration':
            require(any(word in camera['perspective'].lower() for word in ('three-point', 'three point', '三点')), 'exploration requires three-point perspective')
            heights = re.findall(r'\d+(?:\.\d+)?', camera['camera_height'])
            require(heights and all(1.7 <= float(n) <= 1.8 for n in heights), 'exploration optical center must stay within 1.7–1.8 meters')
            require(any(word in camera['horizon'].lower() for word in ('upper third', 'upper-third', '上三分之一')), 'exploration upper-third horizon required')
        elif view['id'] == 'overhead_45':
            require('45' in camera['pitch'] and any(word in camera['pitch'].lower() for word in ('down', '向下', '俯')), 'overhead_45 is downward pitch, not horizontal rotation')
    lock = read(role_file(files, payload['prompt_lock_role']))
    require(lock.get('schema') == 'ndc-scene-prompt-lock/v1' and lock.get('status') == 'LOCKED', 'current prompt/source lock required')
    require('visual_check_status' not in lock, 'a textual prompt lock must not manufacture artistic PASS')
    require(lock.get('scene_id') == scene['id'] and lock.get('handoff_sha256') == sha(handoff_path), 'prompt lock has stale scene/handoff bytes')
    require(lock.get('reviewer') and lock.get('checked_at') and lock.get('view_ids') == required, 'reviewer/date/full views missing from prompt lock')
    require(lock.get('prompt_sha256_by_view') == {v['id']: text_sha(v['prompt_en']) for v in views}, 'exact prompts changed after locking')
    checks = lock.get('checks', {})
    require(set(checks) == LOCK_CHECKS and all(isinstance(v, str) and v.strip() for v in checks.values()), 'actual source/prompt/style/space findings required')
    facts = lock.get('shared_space_facts')
    require(isinstance(facts, list) and facts, 'shared source-supported landmark/connection facts required')
    for fact in facts:
        require(fact.get('fact') and fact.get('source_roles'), 'shared facts need exact source evidence')
        for source_role in fact['source_roles']:
            role_file(files, source_role)
    source_roles = lock.get('source_roles', [])
    require(source_roles, 'lock needs source lookup/requirement evidence')
    for source_role in source_roles:
        role_file(files, source_role)
    style_roles = payload.get('style_reference_roles', {})
    require(set(style_roles) == set(STYLE_KEYS), 'both static style references must be locked')
    asset_names = {'city_rain': 'ndc-static-style-city-rain.jpg', 'character_graphic': 'ndc-static-style-character-graphic.png'}
    for key, role in style_roles.items():
        static = Path(__file__).resolve().parents[2] / 'ndc-midjourney-operator/assets' / asset_names[key]
        require(sha(role_file(files, role)) == sha(static), 'mandatory bundled/saved static style identity changed: ' + key)
    require(lock.get('style_reference_sha256') == {key: files[role]['sha256'] for key, role in style_roles.items()}, 'static style binding changed')
    for reference in handoff.get('references', []):
        require(reference.get('role') in {'style', 'environment', 'composition', 'identity', 'reject'} and reference.get('status') in {'use', 'reject'}, 'invalid v4 reference role')
        if reference['status'] == 'use':
            p = Path(reference['file']).resolve()
            require(any(entry['path'] == p for entry in files.values()), 'used reference not frozen in packet files')
    mapping = payload.get('view_jobs', {})
    require(set(mapping) == set(required) and len(set(mapping.values())) == len(required), 'stable budget job required for every view')
    authority = packet['authority']
    require(set(authority.get('downstream_jobs', [])) == set(mapping.values()), 'downstream scope must preserve the whole scene view set')
    journal = Path(authority['journal'])
    require(journal.is_absolute(), 'original authoritative journal must be absolute')
    api = workflow()
    header, events, _ = api.load(journal)
    require(header['plan']['task_id'] == packet['producer_task_id'], 'journal belongs to another producer task')
    jobs = api.state(header, events)
    shared_hash, view_hashes = contract_hashes(handoff, lock, files)
    budgets = {}
    for view, key in mapping.items():
        require(key in jobs, 'view budget job absent from original journal')
        job = jobs[key]
        model_limit = job['limits'].get('model')
        require(model_limit == 3 or (model_limit == 0 and job['source_decision']['mode'] == 'reuse'),
                'retain original three model calls, or zero for an explicit existing-view reuse job')
        requirements = job['requirements']
        require(requirements.get('scene_id') == scene['id'] and requirements.get('view_id') == view and
                requirements.get('master_state') == handoff['master_state'], 'job identity/view/state does not match handoff')
        require(requirements.get('shared_contract_sha256') == shared_hash and
                requirements.get('view_contract_sha256') == view_hashes[view], 'journal contract is stale; revise affected jobs without resetting history')
        try:
            api.current_acceptance(jobs, key)
            current_output = True
        except (ValueError, OSError):
            current_output = False
        budgets[view] = {'job_id': key, 'used': api.used(job, 'model'), 'limit': model_limit, 'current_output': current_output,
                         'unresolved_submissions': [sid for sid, attempt in job['attempts'].items() if attempt['result'] in {'pending', 'unknown'}]}
    authorized = False
    authorization_role = payload.get('generation_authorization_role')
    if authorization_role and authorization_role in files:
        auth = read(role_file(files, authorization_role))
        authorized = (auth.get('allowed') is True and auth.get('mode') == 'production' and auth.get('source_kind') == 'user_instruction' and
                      scene['id'] in auth.get('scene_ids', []) and auth.get('scope') == 'mj_scene_generation' and
                      bool(auth.get('instruction')) and bool(auth.get('source_roles')))
        if authorized:
            for source_role in auth['source_roles']:
                role_file(files, source_role)
    validation = packet['execution_mode'] == 'validation'
    unresolved = any(row['unresolved_submissions'] for row in budgets.values())
    exhausted = any(row['used'] >= row['limit'] and not row['current_output'] for row in budgets.values())
    stop = 'VALIDATION_ONLY_NO_MJ_SUBMISSION' if validation else ('MJ_GENERATION_NOT_AUTHORIZED' if not authorized else
                  'RESOLVE_EXISTING_MJ_SUBMISSION_FIRST' if unresolved else 'ORIGINAL_MJ_BUDGET_EXHAUSTED' if exhausted else None)
    return {'scene_id': scene['id'], 'view_ids': required, 'handoff_sha256': sha(handoff_path),
            'shared_contract_sha256': shared_hash, 'view_contract_sha256': view_hashes,
            'validation_only': validation, 'can_execute': not validation and authorized and not unresolved and not exhausted,
            'stop_reason': stop, 'view_budgets': budgets, 'whole_scene_scope_preserved': True}


def validate_release(packet, base: Path) -> dict:
    try:
        return _release(packet, Path(base))
    except (OSError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as exc:
        raise ValueError('invalid scene release: ' + str(exc)) from exc


def _result(packet, result, base):
    release = validate_release(packet, base)
    files = file_map(result.get('files', []), base)
    status = result.get('status')
    require(status in {'PASS', 'FAIL', 'WAITING_MANUAL', 'VALIDATION_COMPLETE'}, 'unsupported scene result status')
    payload = result.get('payload', {})
    if status == 'VALIDATION_COMPLETE':
        require(packet['execution_mode'] == 'validation', 'validation receipt is not a production result')
        record = read(role_file(files, payload.get('validation_record_role')))
        require(record.get('check_kind') == 'contract_only' and record.get('artistic_approval') is False and
                record.get('mj_submitted') is False, 'validation must not claim artistic approval or MJ submission')
        require(record.get('handoff_sha256') == release['handoff_sha256'] and
                record.get('scene_id') == packet['unit_id'] and record.get('view_ids') == release['view_ids'], 'validation receipt omits or changes scene/view scope')
        return {'status': status, 'scene_id': packet['unit_id'], 'artistic_approval': False, 'mj_submitted': False}
    if status != 'PASS':
        require(isinstance(payload.get('unresolved'), list) and payload['unresolved'], 'blocked result requires concrete unresolved reasons')
        return {'status': status, 'scene_id': packet['unit_id'], 'unresolved': payload['unresolved'], 'artistic_approval': False}
    require(packet['execution_mode'] == 'production' and release['can_execute'], 'validation/unapproved/unresolved submission cannot return production PASS')
    views = payload.get('views', [])
    require([v.get('view_id') for v in views] == release['view_ids'], 'PASS requires all native views of the same scene')
    api = workflow()
    header, events, _ = api.load(Path(packet['authority']['journal']))
    jobs = api.state(header, events)
    handoff_files = file_map(packet['files'], base)
    handoff = read(role_file(handoff_files, packet['payload']['handoff_role']))
    original_prompts = {v['id']: v['prompt_en'] for v in handoff['view_prompts']}
    outputs = []
    comparisons = set()
    for row in views:
        view_id = row['view_id']
        key = packet['payload']['view_jobs'][view_id]
        require(row.get('job_id') == key, 'result must retain its original view budget job')
        native = role_file(files, row['native_role'])
        with Image.open(native) as img:
            img.load()
            width, height = img.size
            image_format = img.format
        require(width > 0 and height > 0 and width == 2 * height, 'native downloaded view must decode at 2:1')
        accepted = api.current_acceptance(jobs, key)
        original = next((o for o in accepted['request_data']['outputs'] if o['sha256'] == sha(native)), None)
        require(original, 'native result is not the current accepted journal output')
        original_native = Path(original['path']).resolve()
        if original_native != native:
            proof = read(role_file(files, row.get('copy_proof_role')))
            require(proof.get('schema') == 'ndc-art-byte-copy/v1' and proof.get('status') == 'BYTE_IDENTITY_ONLY' and
                    proof.get('task_id') == packet['producer_task_id'] and proof.get('job_id') == key and
                    proof.get('source_acceptance') == accepted['event_sha256'] and
                    proof.get('context_sha256') == accepted['request_data']['context_sha256'] and
                    proof.get('sources') == accepted['request_data']['outputs'], 'copy does not bind the current original acceptance')
            require(any(Path(c['path']).resolve() == native and c['sha256'] == sha(native) and c['role'] == original['role']
                        for c in proof.get('copies', [])), 'native copied output missing from existing byte-copy proof')
        stage = role_file(files, row['stage_review_role'])
        original_stage = next((Path(r['path']).resolve() for r in accepted['records'] if r['sha256'] == sha(stage)), None)
        require(original_stage, 'stage review is not the accepted current record')
        run_validator('validate-ndc-stage-visual-self-check.py', '--record', original_stage, '--artifact', original_native)
        texture = role_file(files, row['texture_review_role'])
        texture_data = read(texture)
        require(texture_data.get('workflow') == 'midjourney-scene' and texture_data.get('artifact_sha256') == sha(native) and
                texture_data.get('review', {}).get('coverage_scope') == 'full_image_tiles', 'texture review does not bind this native full view')
        run_validator('validate-ndc-texture-gate.py', '--record', texture)
        provenance = read(role_file(files, row['provenance_role']))
        reuse = jobs[key]['source_decision']['mode'] == 'reuse'
        require(provenance.get('scene_id') == packet['unit_id'] and provenance.get('view_id') == view_id and
                provenance.get('native_sha256') == sha(native) and provenance.get('native_dimensions') == [width, height] and
                provenance.get('native_format') == image_format and provenance.get('download_kind') ==
                ('approved_native_mj_reuse' if reuse else 'native_mj_image'), 'native file provenance mismatch')
        if reuse:
            require(provenance.get('reuse_basis') and provenance.get('reuse_source_evidence_role'), 'approved native reuse requires actual source/approval evidence')
            role_file(files, provenance['reuse_source_evidence_role'])
            require(not provenance.get('submission_id'), 'do not invent a new submission for approved native reuse')
        else:
            require(provenance.get('mj_job_id') and provenance.get('account_verified') is True and provenance.get('account_evidence_role'), 'actual MJ job/account evidence missing')
            role_file(files, provenance['account_evidence_role'])
            require(provenance.get('actual_model') and provenance.get('hd_setting') in {'selected', 'unavailable'} and
                    provenance.get('style_reference_roles') == {'city_rain': 'style', 'character_graphic': 'style'}, 'actual model/HD/dual style settings missing')
            require(provenance.get('static_style_sha256') == {key: handoff_files[role]['sha256'] for key, role in packet['payload']['style_reference_roles'].items()}, 'actual static references do not match the locked pair')
            require(provenance.get('first_round_prompt_sha256') == text_sha(original_prompts[view_id]), 'first-round exact prompt changed')
            submission_id = provenance.get('submission_id')
            attempt = jobs[key]['attempts'].get(submission_id)
            require(attempt and attempt.get('result') == 'produced', 'native result has no resolved produced attempt in the original journal')
            require(provenance.get('exact_submitted_prompt') == attempt['submission']['arguments'].get('prompt'), 'exact submitted prompt differs from the original journal snapshot')
            current_attempts = []
            for event in events:
                if event['job_id'] != key:
                    continue
                if event['action'] == 'revise' and 'requirements' in event['data']['changes']:
                    current_attempts = []
                elif event['action'] == 'attempt':
                    current_attempts.append(jobs[key]['attempts'][event['data']['submission_id']])
            first = next((a for a in current_attempts if a['kind'] == 'model' and a['result'] != 'no_output'), None)
            require(first and first['submission']['arguments'].get('prompt') == original_prompts[view_id], 'first actual prompt differs from the locked v4 text')
        compared = provenance.get('compared_view_ids')
        require(provenance.get('shared_space_review') and isinstance(compared, list) and
                len(compared) == len(set(compared)) and set(compared) <= set(release['view_ids']) - {view_id}, 'actual cross-view/source spatial review missing')
        comparisons.update(tuple(sorted((view_id, other))) for other in compared)
        outputs.append({'view_id': view_id, 'job_id': key, 'native_sha256': sha(native), 'dimensions': [width, height]})
    require(not payload.get('unresolved'), 'PASS cannot conceal unresolved required views')
    expected_pairs = {tuple(sorted((left, right))) for left in release['view_ids'] for right in release['view_ids'] if left != right}
    require(expected_pairs <= comparisons, 'full-scene cross-view spatial comparison is incomplete')
    return {'status': 'PASS', 'scene_id': packet['unit_id'], 'views': outputs, 'whole_scene_scope_preserved': True}


def validate_result(packet, result, base: Path) -> dict:
    try:
        return _result(packet, result, Path(base))
    except (OSError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as exc:
        raise ValueError('invalid scene result: ' + str(exc)) from exc
