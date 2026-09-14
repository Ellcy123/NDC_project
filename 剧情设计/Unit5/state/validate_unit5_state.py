"""Structural and cross-Loop checks for the Unit5 design State set.

This validates the design documents, not Unity support or narrative quality.
Requires PyYAML>=6. Run from any directory: python -B validate_unit5_state.py
Read-only by default; --report saves only a derived validation JSON.
"""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import re
import sys
import argparse
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

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
    yield path, value
    if isinstance(value, dict):
        for k, v in value.items():
            yield from walk(v, f'{path}.{k}' if path else str(k))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from walk(v, f'{path}[{i}]')

def ref_id(value):
    if isinstance(value, dict):
        value = value.get('id', value.get('param'))
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def validate():
    errors, warnings, states = [], [], []
    def check(ok, message):
        if not ok:
            errors.append(message)
    contract = read(HERE / 'state_contract.yaml')
    registry = read(HERE / 'id_registry.yaml')
    for n in range(1, 6):
        p = HERE / f'loop{n}_state.yaml'
        if not p.exists():
            errors.append(f'L{n}: missing State')
            continue
        try:
            data = read(p)
        except Exception as exc:
            errors.append(f'L{n}: YAML parse: {exc}')
            continue
        states.append(data)
        check(data.get('unit') == 'Unit5' and data.get('episode') == 'EPI05', f'L{n}: Canon mismatch')
        check(data.get('loop') == n and data.get('chapter_id') == 500+n, f'L{n}: loop/chapter ID mismatch')
        for key in contract['format']['root_required']:
            check(key in data, f'L{n}: missing root {key}')
    definitions, testimony, ownership = {}, {}, {}
    counts = []
    for data in states:
        n = data['loop']
        for entry in data.get('evidence_registry', []):
            eid = ref_id(entry)
            if 'ref' in entry:
                check(eid in definitions, f'L{n}: unresolved evidence ref {eid}')
                if eid in definitions:
                    check(entry['ref'] == f'loop{definitions[eid][0]}_state.yaml', f'L{n}: wrong source file for evidence {eid}')
                continue
            acquisition = entry.get('acquisition', {})
            if acquisition.get('kind') == 'dialogue':
                talk = acquisition.get('talk')
                carriers = [v for _, v in walk(data) if isinstance(v, dict) and v.get('talk') == talk and eid in v.get('grants_evidence', [])]
                check(len(carriers) == 1, f'L{n}: dialogue delivery {eid} lacks unique matching grants_evidence')
        scenes = data.get('scenes', [])
        seen_scenes = set()
        for scene in scenes:
            sid = ref_id(scene)
            check(sid in registry['scenes'], f'L{n}: unknown scene {sid}')
            check(sid not in seen_scenes, f'L{n}: repeated scene {sid}')
            seen_scenes.add(sid)
            for field in contract['format']['scene_required']:
                check(field in scene, f'L{n}/scene{sid}: missing {field}')
            for npc_id, npc in scene.get('npcs', {}).items():
                check(int(npc_id) in registry['npcs'], f'L{n}: unregistered NPC {npc_id}')
                for field in contract['format']['npc_required']:
                    check(field in npc, f'L{n}/NPC{npc_id}: missing {field}')
        for entry in data.get('evidence_registry', []):
            eid = ref_id(entry)
            check(eid in registry['items'], f'L{n}: unregistered item {eid}')
            if 'ref' in entry:
                continue
            check(eid not in definitions, f'L{n}: duplicate physical evidence definition {eid}')
            definitions[eid] = (n, entry)
            for field in contract['format']['evidence_required']:
                check(field in entry, f'L{n}/item{eid}: missing {field}')
            check(entry.get('item_type') in contract['format']['item_type_values'], f'L{n}: unknown item_type for {eid}')
            if entry.get('item_type') in ('envir', 2, 'environment'):
                check(entry.get('collectible') is False, f'L{n}: environment {eid} put in bag')
        for path, value in walk(data):
            if path.split('.')[-1] == 'testimony_ids' and isinstance(value, list):
                for item in value:
                    check(isinstance(item, dict), f'L{n}/{path}: bare testimony ID')
                    if not isinstance(item, dict):
                        continue
                    tid = ref_id(item)
                    if 'ref' in item:
                        continue
                    for field in contract['format']['testimony_required']:
                        check(field in item and item[field] not in (None, ''), f'L{n}/testimony{tid}: missing {field}')
                    check('name' not in item, f'L{n}/testimony{tid}: use shortDesc, not name')
                    if tid in testimony:
                        check(testimony[tid][1].get('content') == item.get('content'), f'L{n}: testimony {tid} conflicting content')
                    else:
                        testimony[tid] = (n, item)
                    check(tid is not None and tid // 10000 in registry['npcs'], f'L{n}: testimony prefix {tid}')
            if isinstance(value, dict) and 'source_anchor' in value:
                anchor = str(value['source_anchor'])
                # Approved additions may cite user approval rather than a source line.
                match = re.search(r'(剧情设计/Unit5/[^\n]+?\.md):(\d+)', anchor)
                if match:
                    source = ROOT / match[1]
                    check(source.exists(), f'L{n}: missing source {match[1]}')
                    if source.exists():
                        check(0 < int(match[2]) <= len(source.read_text(encoding='utf-8-sig').splitlines()), f'L{n}: source line out of range {anchor}')
        doubts = data.get('doubts', [])
        check(len(doubts) == 3, f'L{n}: expected 3 doubts, got {len(doubts)}')
        for doubt in doubts:
            did = doubt.get('id')
            check(doubt.get('isFragment') is False, f'L{n}: unexpected fragment {did}')
            conditions = doubt.get('condition', [])
            check(1 <= len(conditions) <= 2, f'L{n}: doubt {did} condition count')
            for condition in conditions:
                key = (condition.get('type'), ref_id(condition))
                check(key not in ownership, f'L{n}: repeated doubt owner for {key}')
                ownership[key] = (n, did)
        expected = list(contract['knowledge']['initial_facts'])
        for previous in range(1, n):
            expected.extend(contract['knowledge']['outcomes'][previous])
        actual = data.get('player_context', {}).get('known_facts', [])
        for fact in expected:
            check(fact in actual, f'L{n}: missing inherited knowledge: {fact}')
        for fact in contract['knowledge']['outcomes'][n]:
            check(fact in data.get('post_expose_knowledge', []), f'L{n}: missing outcome: {fact}')
        counts.append({'loop': n, 'scenes': len(scenes), 'doubts': len(doubts),
                       'coverage_rows': len(data.get('outline_coverage', []))})
    for data in states:
        n = data['loop']
        required_npcs = {
            1: [(5005,505),(5009,503),(5012,511),(5006,506)],
            2: [(5009,503),(5009,504),(5005,505)],
            3: [(5015,504),(5016,506),(5018,508)],
            4: [(5022,505),(5023,513),(5023,509)],
            5: [(5005,505),(5005,512),(5016,506),(5020,502),(5006,507)],
        }
        pairs = {(int(s['id']), int(nid)) for s in data.get('scenes', []) for nid in s.get('npcs', {})}
        for pair in required_npcs[n]:
            check(pair in pairs, f'L{n}: missing explicit free NPC scene/NPC {pair}')
        for doubt in data.get('doubts', []):
            for condition in doubt.get('condition', []):
                eid, kind = ref_id(condition), condition.get('type')
                collection = testimony if kind == 'testimony' else definitions
                check(eid in collection, f'L{n}: unresolved doubt condition {kind}:{eid}')
                if eid in collection:
                    check(collection[eid][0] <= n, f'L{n}: future material {eid}')
        for rnd in data.get('expose', {}).get('rounds', []):
            materials = rnd.get('evidence_set', rnd.get('evidence', []))
            check(bool(materials), f'L{n}: Expose round {rnd.get("round")} has no evidence')
            for material in materials:
                key = (material.get('type'), ref_id(material))
                check(key in ownership, f'L{n}: expose material has no doubt owner {key}')
                if key in ownership:
                    check(ownership[key][0] <= n, f'L{n}: expose material doubt appears later {key}')
        rounds = data.get('expose', {}).get('rounds', [])
        check(data.get('expose', {}).get('id') == 500+n, f'L{n}: Expose ID must be {500+n}')
        check(data.get('expose', {}).get('target_npc') in registry['npcs'], f'L{n}: missing registered target_npc')
        check(len(rounds) == 3, f'L{n}: expected exactly 3 formal Expose rounds')
        if rounds:
            first_lie = ref_id(rounds[0].get('lie_source'))
            check(first_lie in testimony, f'L{n}: R1 has no inline ordinary testimony anchor {first_lie}')
            if first_lie in testimony:
                check(testimony[first_lie][1].get('kind') == 'collectible_lie_anchor', f'L{n}: R1 not collectible_lie_anchor')
            dynamic_ids = data.get('expose', {}).get('expose_lie_ids', [])
            for rnd in rounds[1:]:
                lid = ref_id(rnd.get('lie_source'))
                check(lid in dynamic_ids and bool(rnd.get('lie')), f'L{n}: dynamic lie missing ID/text {lid}')
                check(lid not in testimony, f'L{n}: dynamic lie prematurely collectible {lid}')
        opening = data.get('opening', {})
        sequence = opening.get('sequence', [])
        check(bool(sequence), f'L{n}: missing opening sequence')
        root = opening.get('runtime_root', {})
        if sequence:
            check(root.get('init_talk') == sequence[0].get('talk'), f'L{n}: opening root not first talk')
        check('testimony_registry' not in data, f'L{n}: forbidden root testimony_registry')
        check(n == 5 or 'ending_sequence' not in data, f'L{n}: finale must only be L5')
    if len(states) == 5:
        check(bool(states[-1].get('ending_sequence')), 'L5: missing branching finale')
        by_loop = {s['loop']: s for s in states}
        for n in range(1, 5):
            expected_talk = by_loop[n+1]['opening']['runtime_root']['init_talk']
            exits = [v for _, v in walk(by_loop[n]) if isinstance(v, dict) and v.get('action') == 'loop_end']
            check(len(exits) == 1, f'L{n}: expected one final loop_end after all post-expose events')
            for exit_spec in exits:
                check(exit_spec.get('next_talk') == expected_talk, f'L{n}: next Loop talk must be {expected_talk}')
        declared_talks = {v['talk'] for s in states for _, v in walk(s)
                          if isinstance(v, dict) and isinstance(v.get('talk'), str)}
        for s in states:
            for path, value in walk(s):
                if isinstance(value, dict) and value.get('next_talk'):
                    target = value['next_talk']
                    check(target in declared_talks, f'L{s["loop"]}/{path}: unresolved next_talk {target}')
        outline = (ROOT / '剧情设计/Unit5/Unit5_大纲.md').read_text(encoding='utf-8-sig').splitlines()
        coverage = [r for s in states for r in s.get('outline_coverage', [])]
        for line, content in enumerate(outline, 1):
            npc_marker = bool(re.match(r'^- 角色｜.+（可对话）', content))
            testimony_marker = bool(re.match(r'^\s*- ⚪', content)) and line != 357
            if not (npc_marker or testimony_marker):
                continue
            anchor = f'剧情设计/Unit5/Unit5_大纲.md:{line}'
            field = 'dialogue_required' if npc_marker else 'testimony_required'
            matches = [r for r in coverage if r.get('source_anchor') == anchor and r.get(field)]
            check(len(matches) == 1, f'Outline:{line}: expected unique {field} coverage, got {len(matches)}')
            if testimony_marker and matches:
                check(bool(matches[0].get('source_text')), f'Outline:{line}: missing verbatim source_text')
        finale = by_loop[5]['ending_sequence']
        nodes = {v['event_id']: v for v in finale['sequence']}
        check(len(nodes) == len(finale['sequence']), 'L5: duplicate finale node')
        for node in nodes.values():
            targets = node.get('next', [])
            targets = [targets] if isinstance(targets, str) else targets
            for target in targets:
                check(target == 'chapter_boundary' or target in nodes, f'L5: unresolved finale route {target}')
        check(len(finale.get('endpoints', [])) == 6, 'L5: expected six ending endpoints')
        for endpoint in finale.get('endpoints', []):
            node = nodes.get(endpoint['node'], {})
            check(node.get('runtime_exit', {}).get('ending') == endpoint['ending'], f'L5: endpoint mismatch {endpoint}')
        check(finale.get('entry_talk') == by_loop[5]['expose']['post_expose']['runtime_exit'].get('next_talk'), 'L5: finale entry not last post-expose')
        check(nodes['L5_finale_court_recording'].get('player_control') is False, 'L5: court unexpectedly interactive')
        a = by_loop[5]['special_mechanics']['finale_a']
        b = by_loop[5]['special_mechanics']['finale_b']
        check(len(a['steps']) == 5 and a['pressure']['initial'] == 5 and a['pressure']['timer'] is False, 'L5: A five-step error budget mismatch')
        check(len(b['rounds']) == 3 and b['pressure']['max'] == 3 and b['success_immutable'] is True, 'L5: B risk/lock mismatch')
        correct_levers = [o['id'] for o in b['rounds'][2]['options'] if o.get('correct')]
        check(correct_levers == ['R-42'], 'L5: B unique correct lever changed')
    inventory = json.loads((HERE / 'outline_source_inventory.json').read_text(encoding='utf-8'))
    for source in inventory['sources']:
        check(hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest() == source['sha256'],
              f'Source drift: {source["path"]}')
    return {'status': 'PASS' if not errors else 'FAIL', 'scope': 'design_structural_cross_loop_only',
            'loops_parsed': len(states), 'counts': counts, 'evidence_definitions': len(definitions),
            'testimony_definitions': len(testimony), 'errors': errors, 'warnings': warnings,
            'not_verified': ['Unity execution', 'art legibility', 'full dialogue', 'external item1602 import']}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', action='store_true', help='Save the derived JSON result under reviews/validation_result.json')
    args = parser.parse_args()
    result = validate()
    if args.report:
        report = HERE / 'reviews' / 'validation_result.json'
        report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result['status'] == 'PASS' else 1)
