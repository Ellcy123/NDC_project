"""NDC prop batch checks. Validates evidence; never produces artistic PASS.

Init/attempt/history-resolution/scene-index commands append to the same log.
Validation, binding and prerequisite discovery are read-only.
Paths in batch.json are relative to that file; review paths to their record.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

import scene_release as scenes

SCHEMA = 'ndc-prop-batch/v1'
LIMITS = {'master': 6, 'scene': 3, 'menu': 3, 'derived': 3}
HERE = Path(__file__).resolve().parent

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def resolve(base, path):
    p = Path(path)
    return p.resolve() if p.is_absolute() else (base / p).resolve()

def write_json(path, value):
    temp = path.with_name(path.name + '.writing')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    os.replace(temp, path)

@contextmanager
def lock(path):
    p = path.with_name(path.name + '.lock')
    fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        yield
    finally:
        os.close(fd)
        p.unlink()

def load_batch(path):
    b = read(path)
    if b.get('schema') != SCHEMA:
        raise ValueError('unsupported batch schema')
    for key in ('batch_id', 'objective', 'next_action', 'content_archive', 'attempt_log'):
        if not isinstance(b.get(key), str) or not b[key].strip():
            raise ValueError('missing ' + key)
    if b.get('current_stage') not in range(1, 6):
        raise ValueError('current_stage must be 1..5')
    scope = b.get('scope', {})
    for key in ('item_ids', 'scene_ids', 'required_artifacts'):
        if not isinstance(scope.get(key), list) or len(scope[key]) != len(set(scope[key])):
            raise ValueError('scope requires unique ' + key)
    if not scope['item_ids'] or not scope['required_artifacts']:
        raise ValueError('batch scope cannot be empty')
    if not isinstance(b.get('artifacts'), dict) or not isinstance(b.get('jobs'), dict):
        raise ValueError('artifacts and jobs must be objects')
    if not set(scope['required_artifacts']) <= set(b['artifacts']):
        raise ValueError('required artifacts missing from inventory')
    for job_id, j in b['jobs'].items():
        if j.get('kind') not in LIMITS or j.get('item_id') not in scope['item_ids']:
            raise ValueError('invalid job ' + job_id)
        expected = '|'.join([j['item_id'], j['kind'], j.get('scene_id', ''), j.get('state', '')])
        if job_id != expected or not j.get('state'):
            raise ValueError('job ID must be stable item|kind|scene|state: ' + job_id)
        old = j.get('legacy_attempts', 0)
        if type(old) is not int or old < 0 or (old and not j.get('legacy_evidence')):
            raise ValueError('legacy attempts require a nonnegative count and provenance')
    return b

def log_events(path, b):
    log = resolve(path.parent, b['attempt_log'])
    events = [json.loads(s) for s in log.read_text(encoding='utf-8').splitlines() if s.strip()]
    if not events or events[0].get('type') != 'init':
        raise ValueError('missing initialization event')
    first = events[0]
    if first.get('batch_id') != b['batch_id'] or first.get('scope') != b['scope'] or first.get('jobs') != b['jobs']:
        raise ValueError('scope/jobs changed: do not reset or rename a production budget')
    prev = ''
    for e in events:
        body = {k: v for k, v in e.items() if k != 'hash'}
        if e.get('prev') != prev or e.get('hash') != digest(body):
            raise ValueError('attempt log chain damaged')
        prev = e['hash']
    if b.get('attempt_head') != prev:
        raise ValueError('attempt head mismatch: log truncated or interrupted append; inspect before recovery')
    counts = {key: j.get('legacy_attempts', 0) for key, j in b['jobs'].items()}
    resolved = set()
    attempted = set()
    active_scene_index = None
    for e in events[1:]:
        key = e.get('job_id')
        if e.get('type') == 'scene_release_index':
            if e.get('previous_index_sha256') != (active_scene_index or {}).get('sha256'):
                raise ValueError('scene index revision chain changed')
            pointer = e.get('index')
            if not isinstance(pointer, dict) or sha(pointer['path']) != pointer.get('sha256') or not e.get('reason'):
                raise ValueError('scene index snapshot/evidence changed')
            index = read(pointer['path'])
            if index.get('scope_sha256') != digest(b['scope']) or index.get('batch_id') != b['batch_id']:
                raise ValueError('scene index cannot shrink or replace full batch scope')
            active_scene_index = pointer
            continue
        if e.get('type') == 'legacy_resolution':
            if key not in b['jobs'] or key in resolved or key in attempted:
                raise ValueError('invalid or repeated history resolution')
            j = b['jobs'][key]
            if not unknown_hold(j):
                raise ValueError('only an explicit unknown history hold may be resolved')
            evidence_path = Path(e['evidence_path'])
            if sha(evidence_path) != e.get('evidence_sha256'):
                raise ValueError('history resolution evidence changed')
            evidence = read(evidence_path)
            validate_history_evidence(evidence_path, b, key, evidence)
            if e.get('confirmed_count') != evidence['confirmed_count']:
                raise ValueError('history resolution count mismatch')
            counts[key] = evidence['confirmed_count']
            resolved.add(key)
            continue
        if e.get('type') != 'attempt' or key not in b['jobs']:
            raise ValueError('invalid attempt event')
        attempted.add(key)
        counts[key] = counts.get(key, 0) + 1
        if e.get('number') != counts[key] or counts[key] > LIMITS[b['jobs'][key]['kind']]:
            raise ValueError('attempt budget exceeded or reset for ' + key)
        if sha(Path(e['prompt_path'])) != e.get('prompt_sha256'):
            raise ValueError('attempt prompt snapshot changed')
    if b.get('scene_release_index') != active_scene_index:
        raise ValueError('scene index pointer changed outside append-only migration/revision')
    return events

def unknown_hold(job):
    evidence = job.get('legacy_evidence')
    return (isinstance(evidence, dict)
            and evidence.get('status') == 'UNKNOWN_CONSERVATIVE_EXHAUSTION'
            and evidence.get('actual_count') is None
            and job.get('legacy_attempts') == LIMITS[job['kind']])

def validate_history_evidence(path, batch, job_id, evidence):
    count = evidence.get('confirmed_count')
    if (evidence.get('schema') != 'ndc-prop-history-resolution/v1'
            or evidence.get('batch_id') != batch['batch_id']
            or evidence.get('job_id') != job_id
            or type(count) is not int or not 0 <= count <= LIMITS[batch['jobs'][job_id]['kind']]
            or evidence.get('determination') not in ('new', 'known_historical')
            or (evidence.get('determination') == 'new' and count != 0)
            or not evidence.get('reviewer') or not evidence.get('reason')
            or not isinstance(evidence.get('sources'), list) or not evidence['sources']):
        raise ValueError('incomplete history resolution evidence')
    for source in evidence['sources']:
        if sha(resolve(path.parent, source['path'])).lower() != source['sha256'].lower():
            raise ValueError('history source bytes changed')

def effective_count(batch, events, job_id):
    count = batch['jobs'][job_id].get('legacy_attempts', 0)
    for event in events[1:]:
        if event.get('job_id') == job_id and event.get('type') in {'legacy_resolution', 'attempt'}:
            count = event['confirmed_count'] if event['type'] == 'legacy_resolution' else count + 1
    return count

def is_icon(artifact):
    role = artifact.get('role', '').lower()
    return role == 'icon' or role.startswith('icon_') or role.endswith('_icon')

def resolve_history(path, job_id, evidence_path):
    with lock(path):
        b = load_batch(path)
        events = log_events(path, b)
        if job_id not in b['jobs'] or not unknown_hold(b['jobs'][job_id]):
            raise ValueError('only an explicit unknown history hold may be resolved')
        if any(e.get('job_id') == job_id for e in events[1:]):
            raise ValueError('history already resolved or real attempts exist')
        evidence = read(evidence_path)
        validate_history_evidence(evidence_path, b, job_id, evidence)
        # Snapshot uses absolute source paths so moving the JSON cannot change meaning.
        for source in evidence['sources']:
            source['path'] = str(resolve(evidence_path.parent, source['path']))
        snapshot = path.parent / 'history_resolutions' / (digest(job_id)[:16] + '.json')
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if snapshot.exists():
            raise ValueError('history snapshot already exists; inspect interrupted resolution')
        write_json(snapshot, evidence)
        append(path, b, dict(type='legacy_resolution', job_id=job_id,
                            confirmed_count=evidence['confirmed_count'],
                            evidence_path=str(snapshot.resolve()), evidence_sha256=sha(snapshot)))
        return evidence['confirmed_count']

def append(path, b, event):
    log = resolve(path.parent, b['attempt_log'])
    event = dict(event, at=datetime.now(timezone.utc).isoformat(), prev=b.get('attempt_head', ''))
    event['hash'] = digest(event)
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    b['attempt_head'] = event['hash']
    write_json(path, b)

def initialize(path):
    with lock(path):
        b = load_batch(path)
        if resolve(path.parent, b['attempt_log']).exists() or b.get('attempt_head'):
            raise ValueError('already initialized; preserve history')
        if b.get('scene_release_index'):
            raise ValueError('initialize first, then migrate-scene-release without replacing history')
        append(path, b, dict(type='init', batch_id=b['batch_id'], scope=b['scope'], jobs=b['jobs']))

def install_scene_index(path, index_path, reason, revise=False):
    """Migrate/revise scope evidence in the existing journal; never reset jobs/counts."""
    with lock(path):
        b = load_batch(path)
        events = log_events(path, b)
        old = b.get('scene_release_index')
        if bool(old) != bool(revise):
            raise ValueError('use revise-scene-release for an existing index, migrate-scene-release only once')
        if not reason.strip():
            raise ValueError('require concrete association review/migration evidence')
        archive = read(resolve(path.parent, b['content_archive']))
        index = read(index_path)
        errors = scenes.validate_index(index, b, archive)
        if errors:
            raise ValueError('; '.join(errors))
        index = scenes.normalize_sources(index, index_path.parent, archive)
        snapshot = path.parent / 'scene_release_indexes' / (str(len(events)) + '_' + digest(index)[:16] + '.json')
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        if snapshot.exists():
            raise ValueError('scene index snapshot exists; inspect interrupted migration before retry')
        write_json(snapshot, index)
        pointer = {'path': str(snapshot.resolve()), 'sha256': sha(snapshot)}
        b['scene_release_index'] = pointer
        append(path, b, dict(type='scene_release_index', index=pointer,
                            previous_index_sha256=(old or {}).get('sha256'), reason=reason))
        return {'scene_release_index': pointer, 'counts_preserved': {key: effective_count(b, events, key) for key in b['jobs']}}

def scene_readiness(path, scene_id):
    b = load_batch(path)
    log_events(path, b)
    if scene_id not in b['scope']['scene_ids']:
        raise ValueError('scene is outside the unchanged full scope')
    index = scenes.active_index(b)
    if index is None:
        errors = validate(path, 3)
        return {'scene_id': scene_id, 'mode': 'legacy_global', 'ready': not errors, 'failures': errors}
    archive = read(resolve(path.parent, b['content_archive']))
    errors = scenes.validate_index(index, b, archive)
    if errors:
        return {'scene_id': scene_id, 'mode': 'scene_dependency_closure', 'ready': False, 'failures': errors}
    result = scenes.closure(b, archive, index, scene_id)
    result['failures'] = validate(path, 3, scene_id=scene_id)
    result.update(mode='scene_dependency_closure', ready=not result['failures'])
    return result

def reserve_attempt(path, job_id, prompt, reason):
    with lock(path):
        b = load_batch(path)
        events = log_events(path, b)
        if job_id not in b['jobs']:
            raise ValueError('job was not in locked scope')
        j = b['jobs'][job_id]
        prior = [e for e in events if e.get('type') == 'attempt' and e.get('job_id') == job_id]
        n = effective_count(b, events, job_id) + 1
        if n > LIMITS[j['kind']]:
            raise ValueError('generation limit exhausted; no new call permitted')
        if b.get('requirements_locked') is not True:
            raise ValueError('lock content requirements before generation')
        targets = [a for a in b['artifacts'].values() if a.get('job_id') == job_id]
        stage = 2 if j['kind'] == 'master' else 3
        if j['kind'] == 'derived':
            stages = {a.get('stage') for a in targets}
            if len(stages) != 1 or not stages <= {2, 3}:
                raise ValueError('derived job needs artifacts in exactly one producer stage (2 or 3)')
            stage = stages.pop()
        icon_job = any(is_icon(a) for a in targets)
        if icon_job:
            if any(a.get('stage') != 3 or not is_icon(a) for a in targets):
                raise ValueError('Icon production belongs to stage 3; do not mix Icon and other jobs')
            stage = 3
        # The job/owned targets determine scope, never the mutable batch.current_stage.
        index = scenes.active_index(b)
        target_scenes = {j.get('scene_id')} - {None, ''}
        if index is not None:
            target_scenes.update(sid for aid, a in b['artifacts'].items() if a.get('job_id') == job_id
                                 for sid in scenes.owners(b, index, aid))
        if stage == 3 and not icon_job and index is not None:
            if not target_scenes:
                raise ValueError('stage-3 job requires a scene association in the locked index')
            gate_errors = [e for sid in sorted(target_scenes) for e in validate(path, stage, scene_id=sid)]
        else:
            gate_errors = validate(path, stage)
        archive = read(resolve(path.parent, b['content_archive']))
        if icon_job:
            for aid in b['scope']['required_artifacts']:
                artifact = b['artifacts'][aid]
                if artifact.get('stage') == 3 and not is_icon(artifact):
                    gate_errors += review_errors(path, b, archive, aid)
        for parent in {p for a in targets for p in a.get('parents', [])}:
            if parent not in b['artifacts']:
                gate_errors.append('missing generation parent ' + parent)
            else:
                gate_errors += review_errors(path, b, archive, parent)
        if gate_errors:
            raise ValueError('production prerequisites: ' + '; '.join(gate_errors))
        if any(a.get('job_id') == job_id and a.get('status') == 'PASS' and a.get('rejected') is False
               for a in b['artifacts'].values()):
            raise ValueError('job already passed; no speculative extra generation')
        if not reason.strip() or not prompt.is_file():
            raise ValueError('require actual prompt file and a specific reason')
        prompt_hash = sha(prompt)
        new_round = j['kind'] != 'master' or n % 2 == 1
        if prior and new_round and prompt_hash == prior[-1]['prompt_sha256']:
            raise ValueError('retry requires revised actual prompt, not an identical rerun')
        saved_prompt = path.parent / 'attempt_prompts' / (digest(job_id)[:16] + '_' + str(n) + '.txt')
        saved_prompt.parent.mkdir(parents=True, exist_ok=True)
        if saved_prompt.exists():
            raise ValueError('prompt snapshot already exists; inspect interrupted attempt before retrying')
        saved_prompt.write_bytes(prompt.read_bytes())
        append(path, b, dict(type='attempt', job_id=job_id, number=n,
                            round=(n + 1) // 2 if j['kind'] == 'master' else n,
                            prompt_path=str(saved_prompt.resolve()), prompt_sha256=prompt_hash, reason=reason))
        return n

def affected(b, changed, archive=None):
    result = set(changed)
    index = scenes.active_index(b)
    prerequisites = {}
    if index is not None:
        if archive is None:
            base = Path(b['scene_release_index']['path']).parent.parent
            archive = read(resolve(base, b['content_archive']))
        for sid, row in index['scenes'].items():
            closure = scenes.closure(b, archive, index, sid)
            prerequisites[sid] = (set(closure['prerequisite_artifacts']), set(row['artifact_ids']))
    while True:
        new = {key for key, a in b['artifacts'].items() if set(a.get('parents', [])) & result}
        for required, outputs in prerequisites.values():
            if required & result:
                new.update(outputs)
        if new <= result:
            return sorted(result)
        result |= new

def fact_values(archive, refs):
    values = {}
    for ref in refs:
        item_id, field = ref.split('.', 1)
        values[ref] = archive['items'][item_id]['requirements'][field]
    return values

def expected_binding(b, archive, aid):
    a = b['artifacts'][aid]
    binding = {
        'artifact_id': aid, 'role': a['role'], 'output_sha256': a['sha256'].lower(),
        'facts_digest': digest(fact_values(archive, a['fact_refs'])),
        'acceptance_digest': digest(a['acceptance_contract']),
        'parent_hashes': {p: b['artifacts'][p]['sha256'].lower() for p in a['parents']},
    }
    scene_context = scenes.artifact_binding(b, archive, aid)
    if scene_context:
        binding['scene_release_contexts'] = scene_context
    return binding

def review_errors(path, b, archive, aid, trail=None):
    errors = []
    trail = set() if trail is None else set(trail)
    if aid in trail:
        return ['dependency cycle: ' + aid]
    trail.add(aid)
    a = b['artifacts'][aid]
    if a.get('status') != 'PASS' or a.get('rejected') is not False:
        errors.append(aid + ': candidate/rejected/not checked')
    for parent in a.get('parents', []):
        if parent not in b['artifacts']:
            errors.append(aid + ': missing parent ' + parent)
        else:
            errors += review_errors(path, b, archive, parent, trail)
    # Association prerequisites may be absent from the old image-only parent DAG.
    # Keep them live for already-produced scenes as well as new attempts.
    try:
        index = scenes.active_index(b)
        if index is not None:
            for sid in scenes.owners(b, index, aid):
                dependency = scenes.closure(b, archive, index, sid)
                errors += dependency['failures']
                for parent in dependency['prerequisite_artifacts']:
                    if parent not in a.get('parents', []):
                        errors += review_errors(path, b, archive, parent, trail)
    except (OSError, KeyError, ValueError, TypeError) as exc:
        errors.append(aid + ': scene association binding invalid: ' + str(exc))
    try:
        if not isinstance(a['acceptance_contract'], dict) or not a['acceptance_contract']:
            raise ValueError('nonempty acceptance_contract required')
        if not all(isinstance(v, str) and v.strip() for v in a['acceptance_contract'].values()):
            raise ValueError('acceptance criteria require concrete text')
        current = resolve(path.parent, a['path'])
        if sha(current).lower() != a['sha256'].lower():
            errors.append(aid + ': output bytes changed')
        rp = resolve(path.parent, a['review'])
        record = read(rp)
        expected = expected_binding(b, archive, aid)
        if record.get('workflow_binding') != expected:
            errors.append(aid + ': stale facts/requirements/parent/review scope')
        if record.get('role') != a['role']:
            errors.append(aid + ': review role mismatch')
        spec = importlib.util.spec_from_file_location('ndc_prop_stage_check', HERE / 'stage_visual_check.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        errors += [aid + ': ' + e for e in module.validate_record(rp, [])]
        if a['sha256'].lower() not in {x.get('sha256', '').lower() for x in record.get('outputs', [])}:
            errors.append(aid + ': review does not bind current output')
        names = {c.get('name') for c in record.get('criteria', [])
                 if c.get('applicable') is True and c.get('status') == 'PASS'}
        if not set(a['acceptance_contract']) <= names:
            errors.append(aid + ': missing required review criteria')
        # Check all source items; a copied PNG cannot inherit approval for different facts.
        if a.get('item_ids') and not a.get('fact_refs'):
            errors.append(aid + ': item art requires fact bindings')
        if a.get('role') == 'semantic_master':
            must = {iid + '.' + f for iid in a.get('item_ids', [])
                    for f, v in archive['items'][iid]['requirements'].items() if v['level'] == 'A'}
            if not must <= set(a['fact_refs']):
                errors.append(aid + ': semantic master omits A facts')
        if a.get('published_path') and sha(resolve(path.parent, a['published_path'])) != sha(current):
            errors.append(aid + ': published copy differs')
    except (OSError, KeyError, ValueError, TypeError, AttributeError) as exc:
        errors.append(aid + ': incomplete review evidence: ' + str(exc))
    return errors

def validate(path, stage=1, scene_id=None):
    errors = []
    try:
        b = load_batch(path)
        log_events(path, b)
        archive = read(resolve(path.parent, b['content_archive']))
        if archive.get('schema') != 'ndc-prop-content/v1':
            errors.append('unsupported content schema')
        index = scenes.active_index(b)
        dependency = None
        if index is not None:
            errors += scenes.validate_index(index, b, archive)
            if errors:
                return sorted(set(errors))
            if scene_id is not None:
                if stage != 3:
                    return ['scene-scoped validation is supported only at the stage-2 to stage-3 gate']
                dependency = scenes.closure(b, archive, index, scene_id)
                errors += dependency['failures']
        elif scene_id is not None and scene_id not in b['scope']['scene_ids']:
            return ['scene is outside full batch scope']
        for iid in b['scope']['item_ids']:
            item = archive['items'][iid]
            if not item.get('source_references') or not item.get('requirements'):
                errors.append(iid + ': source/content missing')
            inv = item.get('inventory', {})
            dispositions = {'reuse','complete_missing','repair','regenerate','new','blocked'}
            if not inv.get('keywords') or not inv.get('checked_roots') or not inv.get('reason'):
                errors.append(iid + ': existing-asset inventory must precede production')
            if type(inv.get('found')) is not bool or inv.get('disposition') not in dispositions:
                errors.append(iid + ': invalid found/disposition inventory fields')
            found = False
            for root in inv.get('checked_roots', []):
                if found:
                    errors.append(iid + ': inventory searched later root after authoritative hit')
                if not root.get('root') or root.get('result') not in ('found','no_match'):
                    errors.append(iid + ': invalid inventory root/result')
                found = root.get('result') == 'found'
            if found != inv.get('found'):
                errors.append(iid + ': inventory found does not match root evidence')
            if inv.get('found'):
                selected = inv.get('selected', {})
                if not selected.get('path') or not selected.get('sha256'):
                    errors.append(iid + ': found asset needs exact path and hash')
                else:
                    try:
                        if (dependency is None or iid in dependency['production_item_ids']) and sha(resolve(path.parent, selected['path'])).lower() != selected['sha256'].lower():
                            errors.append(iid + ': selected source bytes changed')
                    except OSError:
                        errors.append(iid + ': selected source no longer exists')
            elif inv.get('disposition') == 'reuse':
                errors.append(iid + ': cannot reuse an asset not found')
            for field, fact in item['requirements'].items():
                if fact.get('level') not in ('A', 'B', 'C') or 'value' not in fact or not fact.get('source'):
                    errors.append(iid + '.' + field + ': invalid content requirement')
                if fact.get('level') == 'B' and not fact.get('allowed_difference'):
                    errors.append(iid + '.' + field + ': B requires explicit allowed difference')
        if stage >= 2 and b.get('requirements_locked') is not True:
            errors.append('requirements are not locked')
        required = b['scope']['required_artifacts']
        for aid in required:
            a = b['artifacts'][aid]
            if a.get('stage') not in (2, 3, 4):
                errors.append(aid + ': producer stage must be 2,3,4')
                continue
            if is_icon(a) and a.get('stage') != 3:
                errors.append(aid + ': Icon producer stage must be 3')
            if not isinstance(a.get('parents'), list):
                errors.append(aid + ': explicit parent list required')
                continue
            if a.get('stage') == 4 and not a['parents']:
                errors.append(aid + ': hotspot has no accepted parent')
            if dependency is None and (a['stage'] < stage or (stage == 5)):
                errors += review_errors(path, b, archive, aid)
        if dependency is not None:
            for aid in dependency['prerequisite_artifacts']:
                errors += review_errors(path, b, archive, aid)
        if stage >= 4:
            covered_scenes = {b['artifacts'][a].get('scene_id') for a in required
                       if b['artifacts'][a].get('role') == 'scene_preview'}
            if not set(b['scope']['scene_ids']) <= covered_scenes:
                errors.append('batch scene preview coverage missing')
            for aid in required:
                a = b['artifacts'][aid]
                if a.get('role') in ('scene_preview', 'container_type7') and a.get('frozen') is not True:
                    errors.append(aid + ': scene/menu not frozen')
                if a.get('role') == 'container_type7':
                    previews = [b['artifacts'][k] for k in required
                                if b['artifacts'][k].get('role') == 'scene_menu_preview'
                                and aid in b['artifacts'][k].get('parents', [])]
                    if not previews:
                        errors.append(aid + ': individual scene menu preview missing')
        return sorted(set(errors))
    except (OSError, KeyError, ValueError, TypeError, AttributeError) as exc:
        return ['invalid batch: ' + str(exc)]

def formal_errors(path, folder):
    errors = validate(path, 5)
    if errors:
        return errors
    b = load_batch(path)
    by_path = {}
    for aid in b['scope']['required_artifacts']:
        a = b['artifacts'][aid]
        if a.get('published_path'):
            by_path[resolve(path.parent, a['published_path'])] = a
    pngs = [p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() == '.png']
    if not pngs:
        errors.append('no formal PNGs')
    for p in pngs:
        a = by_path.get(p.resolve())
        if not a or a['sha256'].lower() != sha(p):
            errors.append(str(p) + ': no exact published-path batch binding')
    return errors

def progress(path):
    b = load_batch(path)
    log_events(path, b)
    archive = read(resolve(path.parent, b['content_archive']))
    required = b['scope']['required_artifacts']
    passed = {aid for aid in required
              if b['artifacts'][aid].get('status') == 'PASS'
              and not review_errors(path, b, archive, aid)}
    def metric(ids):
        ids = set(ids)
        return {'passed': len(ids & passed), 'required': len(ids),
                'percent': round(100 * len(ids & passed) / len(ids), 1) if ids else None}
    result = {'overall': metric(required), 'stages': {
        str(stage): metric(aid for aid in required if b['artifacts'][aid].get('stage') == stage)
        for stage in (2, 3, 4)}, 'current_stage': b['current_stage'],
                 'next_action': b['next_action'], 'execution_priority': b.get('execution_priority')}
    index = scenes.active_index(b)
    if index is not None:
        per_scene = {}
        all_scenes_frozen = not validate(path, 4)
        all_outputs_current = not validate(path, 5)
        for sid, row in index['scenes'].items():
            ready = scene_readiness(path, sid)
            owned = set(row['artifact_ids'])
            if not ready['ready']:
                stage, state = 2, 'WAITING_SCENE_PREREQUISITES'
            elif not owned <= passed:
                stage, state = 3, 'SCENE_PRODUCTION_READY'
            elif not all_scenes_frozen:
                stage, state = 3, 'WAITING_GLOBAL_ICON_AND_FREEZE_GATE'
            elif not all_outputs_current:
                stage, state = 4, 'GLOBAL_HOTSPOT_GATE_OPEN'
            else:
                stage, state = 5, 'ALL_REQUIRED_IMAGES_CURRENT'
            per_scene[sid] = {'stage': stage, 'state': state, 'stage3_ready': ready['ready'],
                              'scene_outputs': metric(owned), 'blockers': ready['failures']}
        result.update(declared_current_stage=b['current_stage'], stage_dispatch='per_scene', scenes=per_scene)
        # Keep the compatibility scalar as the earliest actual incomplete phase;
        # it is a report, never the authorization to enter every scene at once.
        if per_scene:
            result['current_stage'] = min(row['stage'] for row in per_scene.values())
    if 'initial_missing_artifacts' in b:
        missing = b['initial_missing_artifacts']
        if not isinstance(missing, list) or len(missing) != len(set(missing)) or not set(missing) <= set(required):
            raise ValueError('invalid missing baseline; preserve required artifact scope')
        result['missing_fill'] = metric(missing)
    else:
        result['missing_fill'] = None
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'attempt', 'validate', 'affected', 'binding', 'progress', 'resolve-history',
                                          'migrate-scene-release', 'revise-scene-release', 'scene-readiness'])
    parser.add_argument('--batch', required=True, type=Path)
    parser.add_argument('--stage', type=int, choices=range(1, 6), default=1)
    parser.add_argument('--job')
    parser.add_argument('--prompt', type=Path)
    parser.add_argument('--reason', default='')
    parser.add_argument('--artifact')
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--scene')
    parser.add_argument('--index', type=Path)
    args = parser.parse_args()
    path = args.batch.resolve()
    try:
        if args.command == 'init':
            initialize(path)
            result = {'initialized': True}
        elif args.command == 'attempt':
            if not args.prompt or not args.job:
                raise ValueError('attempt requires --job and --prompt')
            result = {'reserved_attempt': reserve_attempt(path, args.job, args.prompt, args.reason)}
        elif args.command == 'validate':
            errors = validate(path, args.stage, scene_id=args.scene)
            result = {'technical_workflow_valid': not errors, 'failures': errors}
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return int(bool(errors))
        elif args.command == 'progress':
            result = progress(path)
        elif args.command in {'migrate-scene-release', 'revise-scene-release'}:
            if not args.index:
                raise ValueError('scene release migration/revision requires --index and --reason')
            result = install_scene_index(path, args.index.resolve(), args.reason, args.command == 'revise-scene-release')
        elif args.command == 'scene-readiness':
            if not args.scene:
                raise ValueError('scene-readiness requires --scene')
            result = scene_readiness(path, args.scene)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return int(not result['ready'])
        elif args.command == 'resolve-history':
            if not args.job or not args.evidence:
                raise ValueError('resolve-history requires --job and --evidence')
            result = {'confirmed_legacy_count': resolve_history(path, args.job, args.evidence.resolve())}
        else:
            b = load_batch(path)
            if args.artifact not in b['artifacts']:
                raise ValueError('unknown --artifact')
            result = (affected(b, [args.artifact]) if args.command == 'affected' else
                      expected_binding(b, read(resolve(path.parent, b['content_archive'])), args.artifact))
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'blocked': str(exc)}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    sys.exit(main())
