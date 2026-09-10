"""Whole-scene reference handoff using the existing native production ledger.

The journal preserves cost/history; it does not duplicate artistic acceptance.
"""
from pathlib import Path
import importlib.util
import json
import sys
from pipeline import need, read, file_hash, digest, workflow, files_current, INTEGRATION_MODELS


def verify_delivery(path, packet, delivered):
    """Read-only 100% XY reconstruction; native visual gates remain separate."""
    from PIL import Image
    manifest = read(path)
    need(manifest.get('scene_id') == packet['unit_id'], 'Delivery scene identity mismatch')
    expected = {(case, shot) for case, shots in scope_map(packet['unit_scope']).items() for shot in shots}
    snapshots = manifest.get('snapshots', [])
    need(len(snapshots) == len(expected) and {(s['case_id'], s['snapshot_id']) for s in snapshots} == expected, 'Delivery must reconstruct every required snapshot')
    source_ref = next(r for r in packet['files'] if r['role'] == packet['payload']['scene_role'])
    with Image.open(source_ref['path']) as image:
        background = image.convert('RGBA')
    for snapshot in snapshots:
        layers = snapshot.get('layers')
        need(layers and snapshot.get('composite'), 'Actual layers and final composite required')
        canvas = background.copy()
        for layer in layers:
            key = (str(Path(layer['path']).resolve()), layer['sha256'])
            need(key in delivered and file_hash(layer['path']) == layer['sha256'], 'Layer missing from verified assigned outputs')
            need(type(layer['x']) is int and type(layer['y']) is int, 'XY must be original-pixel integers')
            with Image.open(layer['path']) as image:
                need(image.mode == 'RGBA' and image.getchannel('A').getextrema()[0] == 0, 'Layer requires actual transparent RGBA')
                canvas.alpha_composite(image, (layer['x'], layer['y']))
        final = snapshot['composite']
        need((str(Path(final['path']).resolve()), final['sha256']) in delivered and file_hash(final['path']) == final['sha256'], 'Snapshot composite missing from verified outputs')
        with Image.open(final['path']) as image:
            actual = image.convert('RGBA')
            need(actual.size == background.size and actual.tobytes() == canvas.tobytes(), 'Original-resolution XY reconstruction differs from reviewed composite')
    return {'snapshots_reconstructed':len(snapshots)}


def native_gate():
    path = Path(__file__).resolve().parents[2] / 'ndc-character-scene-integration/scripts/production_gate.py'
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location('ndc_integration_native_gate', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def importance_gate():
    path = Path(__file__).resolve().parents[2] / 'ndc-character-scene-integration/scripts/validate_importance_profile.py'
    spec = importlib.util.spec_from_file_location('ndc_importance_gate', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def role_file(refs, role):
    need(role in refs, 'Missing real handoff role: ' + str(role))
    return Path(refs[role]['path'])


def scope_map(scope):
    cases = scope.get('cases')
    need(isinstance(cases, list) and cases, 'Complete requested scene cases required')
    result = {}
    for case in cases:
        key = case['case_id']
        need(key not in result and case.get('snapshots'), 'Distinct cases with all required snapshots needed')
        snapshots = {}
        for shot in case['snapshots']:
            need(shot['snapshot_id'] not in snapshots and shot.get('actor_pose_ids'), 'Unique nonempty whole-cast snapshot needed')
            need(all(isinstance(k, str) and k and isinstance(v, str) and v for k, v in shot['actor_pose_ids'].items()), 'Actor and pose IDs required')
            snapshots[shot['snapshot_id']] = shot['actor_pose_ids']
        result[key] = snapshots
    return result


def ledger_scope(path, scope, source_ref, stage):
    ledger = read(path)
    need(ledger.get('stage') == stage, 'Wrong native ledger stage')
    wanted = scope_map(scope)
    cases = ledger.get('cases', [])
    need(len(cases) == len(wanted) and {c['caseId'] for c in cases} == set(wanted), 'Ledger omits or changes declared whole-scene cases')
    native = native_gate()
    for case in cases:
        need(native.resolve_path(case['sourceScene'], path) == Path(source_ref['path']).resolve() and case['sourceSceneSha256'] == source_ref['sha256'], 'Scene source does not match frozen authority')
        actual = {}
        for ref in case['stagingContracts']:
            staging_path, staging = native.validate_file_ref(ref, 'scene staging', path)
            sid = staging['timelineSnapshotId']
            need(sid not in actual, 'Duplicate snapshot contract')
            actual[sid] = staging.get('combinedWhiteboxReview', {}).get('poseIds', {})
        need(actual == wanted[case['caseId']], 'Complete cast, pose and snapshot scope must match the original request')
    report = native.validate_ledger(path)
    need(report['status'] == 'EVIDENCE_GATE_PASS', 'Native production evidence gate did not pass')
    return ledger, report


def job_binding(job):
    # Cost appends do not rewrite a reference contract; rejection/revision does.
    return digest({k: job.get(k) for k in ('job_id', 'asset_key', 'requirements', 'inputs', 'source_decision', 'revision', 'waiting')})


def validate_job_limits(job, key, packet, refs):
    limits = job['limits']
    need(type(limits.get('model')) is int and type(limits.get('ps')) is int and limits['model'] >= 0 and limits['ps'] >= 0, 'Explicit finite formal limits required')
    if limits['model'] == 6 and limits['ps'] <= 3:
        return
    role = packet['payload'].get('budget_exception_roles', {}).get(key)
    need(role, 'Above-standard limits require the original scoped user exception')
    grant = read(role_file(refs, role))
    need(grant.get('source_kind') == 'user_instruction' and grant.get('instruction') and grant.get('grant_id') and grant.get('source_roles'), 'Actual exception instruction and source evidence required')
    for source_role in grant['source_roles']:
        role_file(refs, source_role)
    need(grant.get('production_id') == packet['payload']['production_id'] and grant.get('scene_id') == packet['unit_id'] and grant.get('job_id') == key and grant.get('phase') == 'formal', 'Exception belongs to another production, scene, job or phase')
    base, extra = grant.get('base_limits', {}), grant.get('additional_limits', {})
    need(base.get('model') == 6 and type(base.get('ps')) is int and 0 <= base['ps'] <= 3, 'Exception must retain the standard base ceiling')
    need(set(extra) == {'model', 'ps'} and all(type(v) is int and v >= 0 for v in extra.values()) and any(extra.values()), 'Exception must specify finite additional calls')
    need(all(limits[k] == base[k] + extra[k] for k in ('model', 'ps')), 'Effective cap differs from the original finite exception; do not re-add consumed grants')


def validate_release(packet, base):
    need(packet['pipeline_kind'] == 'character_scene' and packet['model_policy'] == INTEGRATION_MODELS, 'Fixed Astra medium / Terra xhigh policy required')
    payload = packet['payload']
    refs = {r['role']: r for r in packet['files']}
    files_current(packet['files'])
    scope = packet['unit_scope']
    wanted = scope_map(scope)
    source = refs[payload['scene_role']]
    scope_record = read(role_file(refs, payload['scope_role']))
    need(scope_record.get('scene_id') == packet['unit_id'] and scope_record.get('scope') == scope and scope_record.get('requirement_basis'), 'Original requirement scope and evidence required')
    need(scope_record.get('status') == 'LOCKED', 'Paused, rejected or unresolved scene scope cannot release')
    importance_mode = 'legacy_conservative_h0_h1'
    if scope_record.get('importance_policy_version') == 'ndc-visual-importance/v1':
        profile_path = role_file(refs, payload.get('importance_profile_role'))
        profile = read(profile_path)
        need(profile.get('scene_id') == packet['unit_id'] and profile.get('revision') == packet['revision'], 'Importance profile belongs to another scene or revision')
        result = importance_gate().validate(profile)
        need(result['status'] == 'PASS', 'Importance profile gate failed: ' + '; '.join(result['errors']))
        recorded = read(role_file(refs, payload.get('importance_gate_role')))
        need(recorded.get('status') == 'PASS' and recorded.get('profile_sha256') == file_hash(profile_path), 'Recorded importance gate is stale or does not bind the profile')
        importance_mode = 'tiered_h0_h1_h2_h3'
    for name in ('depth_roles', 'identity_roles'):
        need(payload.get(name), 'Required reference category: ' + name)
        for role in payload[name]:
            role_file(refs, role)
    prompt_path = role_file(refs, payload['prompt_bundle_role'])
    prompts = read(prompt_path)
    all_poses = {pose for shots in wanted.values() for actors in shots.values() for pose in actors.values()}
    need(prompts.get('scene_id') == packet['unit_id'] and set(prompts.get('poses', {})) == all_poses, 'Every declared pose needs an inspected generation-input bundle')
    for pose, bundle in prompts['poses'].items():
        need(bundle.get('prompt') and bundle.get('reference_roles') and bundle.get('checked_by') and bundle.get('findings'), 'Actual assembled prompt and reference review required')
        for role in bundle['reference_roles']:
            role_file(refs, role)
    ledger_path = role_file(refs, payload['pre_ledger_role'])
    ledger, report = ledger_scope(ledger_path, scope, source, 'pre-generation')
    api, jobs = workflow(packet)
    header, _, _ = api['load'](packet['authority']['journal'])
    need(header['plan'].get('production_id') == payload['production_id'], 'Retain original production ID')
    history = read(role_file(refs, payload['history_role']))
    need(history.get('production_id') == payload['production_id'] and history.get('basis') and history.get('source_roles'), 'Original counts need a source-backed import record, including genuine zero counts')
    for role in history['source_roles']:
        role_file(refs, role)
    mapping = payload['budget_jobs']
    need(set(mapping) == set(packet['authority']['downstream_jobs']), 'Retain all original formal actor/interaction jobs')
    covered = set()
    budgets = {}
    for key, poses in mapping.items():
        job = jobs[key]
        need(poses and set(poses) <= all_poses, 'Invalid formal job pose scope')
        covered.update(poses)
        req = job['requirements']
        need(req.get('scene_id') == packet['unit_id'] and req.get('production_id') == payload['production_id'] and req.get('phase') == 'formal' and set(req.get('pose_ids', [])) == set(poses), 'Job identity/history scope changed')
        validate_job_limits(job, key, packet, refs)
        need(key in history['jobs'] and job['history'] == history['jobs'][key], 'Imported history must equal the original frozen plan counts')
        need(not job.get('waiting'), 'Original job is paused; reconcile its existing state')
        unresolved = [k for k, a in job['attempts'].items() if a['result'] in ('pending', 'unknown')]
        budgets[key] = {'model_used': api['used'](job, 'model'), 'ps_used': api['used'](job, 'ps'), 'unknown': unresolved}
    need(covered == all_poses, 'Budget scope omits an actor/interaction pose')
    authorization = read(role_file(refs, payload['authorization_role']))
    granted = authorization.get('allowed') is True and authorization.get('source_kind') == 'user_instruction' and packet['unit_id'] in authorization.get('scene_ids', []) and authorization.get('scope') == 'character_scene_production' and bool(authorization.get('instruction'))
    validation = packet['execution_mode'] == 'validation'
    if validation:
        need(scope_record.get('validation_only') is True, 'Validation requires explicitly identified fixture evidence')
    can_execute = not validation and granted and not any(v['unknown'] for v in budgets.values())
    return {'scene_id': packet['unit_id'], 'validation_only': validation, 'can_execute': bool(can_execute), 'stop_reason': None if can_execute or validation else 'Missing production authorization or unresolved original submission', 'case_ids': list(wanted), 'pre_ledger_sha256': file_hash(ledger_path), 'scope_sha256': digest(scope), 'importance_mode': importance_mode, 'budgets': budgets}


def validate_result(packet, result, base):
    status = result['status']
    payload = result.get('payload', {})
    if status in ('FAIL', 'WAITING_MANUAL', 'STALE'):
        need(payload.get('reason') and payload.get('return_stage') in ('reference', 'production', 'manual'), 'Return an actual failure and responsible stage')
        return {'stopped': True, 'return_stage': payload['return_stage']}
    release = validate_release(packet, base)
    refs = {r['role']: r for r in result['files']}
    if status == 'VALIDATION_COMPLETE':
        need(packet['execution_mode'] == 'validation', 'Validation is not production approval')
        record = read(role_file(refs, payload['validation_record_role']))
        need(record.get('check_kind') == 'contract_only' and record.get('artistic_approval') is False and record.get('generated') is False and record.get('pre_ledger_sha256') == release['pre_ledger_sha256'] and record.get('scope_sha256') == release['scope_sha256'], 'Real contract-only receipt needed')
        return {'validation_only': True}
    need(status == 'PASS' and packet['execution_mode'] == 'production' and release['can_execute'], 'Actual production permission and result required')
    packet_refs = {r['role']: r for r in packet['files']}
    post_path = role_file(refs, payload['post_ledger_role'])
    post, _ = ledger_scope(post_path, packet['unit_scope'], packet_refs[packet['payload']['scene_role']], 'post-generation')
    _, jobs = workflow(packet)
    need(payload.get('job_bindings') == {key:job_binding(jobs[key]) for key in packet['authority']['downstream_jobs']}, 'Result belongs to obsolete or rejected job requirements')
    delivered = {(str(Path(r['path']).resolve()), r['sha256']) for r in result['files']}
    native = native_gate()
    for case in post['cases']:
        for ref in case['finalConformanceContracts']:
            path, contract = native.validate_file_ref(ref, 'final conformance', post_path)
            need(contract.get('finalComposite') and contract.get('finalCompositeSha256'), 'Bind actual final composite, not a report-only PASS')
            final_path = native.resolve_path(contract['finalComposite'], path)
            need((str(final_path), contract['finalCompositeSha256']) in delivered, 'Final reviewed composite missing from assigned result files')
    need(payload.get('delivery_manifest_role') in refs, 'Original layer/XY/reconstruction delivery manifest required')
    verify_delivery(role_file(refs, payload['delivery_manifest_role']), packet, delivered)
    return {'native_post_generation_gate': 'PASS', 'case_ids': release['case_ids']}
