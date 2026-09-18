"""Read-only structural and evidence-flow checks for the five-loop Unit1 design.

This validates design YAML, not Unity runtime execution or narrative correctness.
"""
from pathlib import Path
import json
import re
import hashlib
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'U1优化制作/06_State'


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError(f'duplicate YAML key {key!r} at line {key_node.start_mark.line + 1}')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read(path):
    return yaml.load(path.read_text(encoding='utf-8-sig'), Loader=UniqueLoader)


def walk(value, path=''):
    if isinstance(value, dict):
        yield path, value
        for key, child in value.items():
            yield from walk(child, f'{path}.{key}')
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, f'{path}[{index}]')


def resolve_path(state, path):
    """Accept dotted paths with list indices or [id=...] / [key=...] selectors."""
    value = state
    for match in re.finditer(r'([^.\[\]]+)|\[([^\]]+)\]', path):
        key, selector = match.groups()
        if key:
            value = value[key]
        elif '=' in selector:
            field, wanted = selector.split('=', 1)
            wanted = wanted.strip('\"\' ')
            value = next(item for item in value if str(item.get(field.strip())) == wanted)
        elif selector.isdigit():
            value = value[int(selector)]
        else:
            value = value[selector.strip('\"\' ')]
    return value


def main():
    errors, notes = [], []
    states = []
    contract = read(BASE / '五轮State疑点合同.yaml')
    expected_doubts = {str(d['id']): d for d in contract['doubts']}
    source_pack = read(BASE / '五轮State来源覆盖.yaml')
    coverage_counts = {}
    for source in source_pack['sources']:
        path = ROOT / source['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            errors.append(f'source changed since coverage snapshot: {source["path"]}')
    identifiers = read(BASE / '五轮State标识与接口.yaml')
    valid_scene_ids = {str(scene['id']) for scene in identifiers['scenes']}
    for number in range(1, 6):
        path = BASE / f'loop{number}_state.yaml'
        try:
            state = read(path)
            states.append(state)
        except Exception as exc:
            errors.append(f'L{number}: cannot read YAML: {exc}')
            continue
        for field in ('player_context', 'opening', 'scenes', 'expose', 'doubts',
                      'evidence_registry', 'outline_coverage', 'narrative_continuity'):
            if not state.get(field):
                errors.append(f'L{number}: missing/empty {field}')
        if state.get('loop') != number:
            errors.append(f'L{number}: wrong loop identity')
        opening = state.get('opening', {})
        sequence = opening.get('sequence', [])
        if not sequence or opening.get('player_control_restored_after') != sequence[-1].get('event_id'):
            errors.append(f'L{number}: opening control boundary does not name final event')
        if sequence and opening.get('runtime_root', {}).get('init_talk') != sequence[0].get('talk'):
            errors.append(f'L{number}: opening root does not name first talk')
        for index, doubt in enumerate(state.get('doubts', [])):
            conditions = doubt.get('condition', [])
            if not 1 <= len(conditions) <= 3:
                errors.append(f'L{number} doubt {doubt.get("id")}: expected 1..3 conditions')
            for i, condition in enumerate(conditions):
                if condition.get('visible') != (i < 2):
                    errors.append(f'L{number} doubt {doubt.get("id")}: wrong visibility at slot {i+1}')
            if doubt.get('isFragment') is not False:
                errors.append(f'L{number} doubt {doubt.get("id")}: fragments not supported in this design')
            expected = expected_doubts.get(str(doubt.get('id')))
            signature = lambda rows: [(str(c.get('type')), str(c.get('param')), c.get('visible')) for c in rows]
            if not expected or signature(conditions) != signature(expected['condition']):
                errors.append(f'L{number} doubt {doubt.get("id")}: differs from approved ordered conditions')
        expected_ids = {str(d['id']) for d in contract['doubts'] if d['loop'] == number}
        if {str(d.get('id')) for d in state.get('doubts', [])} != expected_ids:
            errors.append(f'L{number}: doubt ID set differs from contract')
        expected_beats = {b['beat_id'] for b in source_pack['coverage'] if b['loop'] == number}
        rows = state.get('outline_coverage', [])
        if isinstance(rows, list):
            actual_beats = {row.get('beat_id') for row in rows}
            coverage_counts[str(number)] = len(actual_beats)
            for missing in sorted(expected_beats - actual_beats):
                errors.append(f'L{number}: missing source beat {missing}')
            for row in rows:
                paths = row.get('state_paths', [row.get('state_path')])
                if isinstance(paths, str):
                    paths = [paths]
                if not paths or any(not path for path in paths):
                    errors.append(f'L{number}: coverage {row.get("beat_id")} has no actual state_path')
                    continue
                for path in paths:
                    try:
                        resolve_path(state, path)
                    except (KeyError, IndexError, TypeError, StopIteration):
                        errors.append(f'L{number}: coverage {row.get("beat_id")} invalid path {path}')
        else:
            errors.append(f'L{number}: outline_coverage must be a list')
        if state.get('testimony_registry'):
            errors.append(f'L{number}: testimony must be inline at acquisition, not a root registry')
        for node_path, obj in walk(state):
            for key in ('scene_id', 'target_scene_id', 'init_scene', 'unlock_scene_id'):
                if key in obj and obj[key] is not None and str(obj[key]) not in valid_scene_ids:
                    errors.append(f'L{number}{node_path}: unknown {key}={obj[key]}')
            if 'testimony_ids' not in obj:
                continue
            for testimony in obj['testimony_ids'] or []:
                if not isinstance(testimony, dict) or not all(testimony.get(k) for k in ('id', 'content', 'source_anchor')):
                    errors.append(f'L{number}{node_path}: incomplete inline testimony')
                elif 'name' in testimony:
                    errors.append(f'L{number}{node_path}: testimony uses name instead of shortDesc')
    owners = {}
    testimony_acquisitions = {}
    items = {}
    for state in states:
        number = state.get('loop')
        for item in state.get('evidence_registry', []):
            item_id = str(item.get('id'))
            items.setdefault(item_id, []).append((number, item))
        for node_path, obj in walk(state):
            for testimony in obj.get('testimony_ids', []) or []:
                if isinstance(testimony, dict):
                    testimony_acquisitions.setdefault(str(testimony.get('id')), []).append((number, node_path, testimony))
        for doubt in state.get('doubts', []):
            for cond in doubt.get('condition', []):
                key = str(cond.get('param'))
                if key in owners:
                    errors.append(f'material {key}: duplicate doubt owner {owners[key]} and L{number}/{doubt.get("id")}')
                owners[key] = (number, doubt.get('id'))
    for key, entries in testimony_acquisitions.items():
        if len(entries) > 1:
            errors.append(f'testimony {key}: multiple acquisition locations {[e[:2] for e in entries]}')
    for key, entries in items.items():
        if len(entries) > 1:
            errors.append(f'item {key}: multiple acquisition definitions; use inherited_evidence_refs for reuse')
    for key, (number, doubt_id) in owners.items():
        if key not in items and key not in testimony_acquisitions:
            errors.append(f'doubt {doubt_id}: material {key} has no evidence/testimony definition')
        for acquired_loop, path, _ in testimony_acquisitions.get(key, []):
            if acquired_loop > number or (acquired_loop == number and ('post_expose' in path or 'ending_sequence' in path)):
                errors.append(f'doubt {doubt_id}: testimony {key} unavailable before expose')
        for defining_loop, item in items.get(key, []):
            acquisition = item.get('acquisition', {})
            acquired_loop = acquisition.get('loop', defining_loop)
            carrier = str(acquisition.get('carrier', ''))
            if acquired_loop > number or (acquired_loop == number and ('post_expose' in carrier or 'ending_sequence' in carrier)):
                errors.append(f'doubt {doubt_id}: item {key} unavailable before expose')
    uses = []
    for state in states:
        number = state.get('loop')
        for node_path, obj in walk(state.get('expose', {}), '.expose'):
            for evidence in obj.get('usable_evidence', []) or []:
                key = str(evidence.get('id') if isinstance(evidence, dict) else evidence)
                uses.append((number, node_path, key))
                if key not in owners:
                    errors.append(f'L{number}{node_path}: exposed material {key} has no doubt owner')
                elif owners[key][0] > number:
                    errors.append(f'L{number}{node_path}: exposed material {key} belongs to future doubt')
    if len(states) == 5:
        ending = states[-1].get('ending_sequence')
        if not ending:
            errors.append('L5: missing locked ending_sequence')
        if (BASE / 'loop6_state.yaml').exists():
            errors.append('old loop6 still in current state directory')
        if ending:
            segments = ending.get('scenes', [])
            for segment in segments:
                if segment.get('npcs'):
                    errors.append('L5 ending segment has unintended free NPC talk entries')
            last_exit = segments[-1].get('runtime_exit', {}) if segments else {}
            if last_exit.get('action') != 'loop_end' or last_exit.get('chapter_boundary') is not True:
                errors.append('L5 ending must finish with loop_end and chapter_boundary=true')
    notes.append('Runtime adapters and semantic source fidelity require separate review; this is not a Unity playtest.')
    result = {'status': 'FAIL' if errors else 'PASS', 'state_count': len(states),
              'doubt_count': sum(len(s.get('doubts', [])) for s in states),
              'source_coverage_counts': coverage_counts,
              'owned_material_count': len(owners), 'expose_evidence_references': len(uses),
              'errors': errors, 'notes': notes}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
