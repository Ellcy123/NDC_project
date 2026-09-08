"""Scene-scoped prerequisite discovery. No image approval or file mutation."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

SCHEMA = 'ndc-prop-scene-release/v1'
RELATIONS = {'shared_identity', 'state_variant', 'container_content', 'depicted_content', 'fact_reference'}
PHYSICAL_RELATIONS = {'shared_identity', 'state_variant', 'container_content'}

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def icon(a):
    role = a.get('role', '').lower()
    return role == 'icon' or role.startswith('icon_') or role.endswith('_icon')

def artifact_scene(b, aid):
    a = b['artifacts'][aid]
    return a.get('scene_id') or b['jobs'].get(a.get('job_id'), {}).get('scene_id', '')

def refs_shape(rows):
    return (isinstance(rows, list) and bool(rows) and all(isinstance(r, dict)
            and isinstance(r.get('path'), str) and r['path'] and isinstance(r.get('sha256'), str)
            and len(r['sha256']) == 64 for r in rows))

def string_list(value):
    return isinstance(value, list) and all(isinstance(x, str) and x for x in value) and len(value) == len(set(value))

def validate_index(index, b, archive):
    """Global scope/association shape, without reading unrelated scene source files."""
    errors = []
    if (index.get('schema') != SCHEMA or index.get('batch_id') != b['batch_id']
            or index.get('scope_sha256') != digest(b['scope'])):
        return ['scene index schema/batch/full-scope binding mismatch']
    if not index.get('reviewer') or not index.get('reason'):
        errors.append('scene index needs actual reviewer and reason')
    items, scenes, relations = index.get('items'), index.get('scenes'), index.get('relations')
    if not isinstance(items, dict) or set(items) != set(b['scope']['item_ids']):
        return errors + ['scene index must cover every item in the unchanged full scope']
    if not isinstance(scenes, dict) or set(scenes) != set(b['scope']['scene_ids']):
        return errors + ['scene index must cover every scene in the unchanged full scope']
    if not isinstance(relations, list):
        return errors + ['scene relations must be an explicit list (empty only with item evidence)']
    known = set(items)
    for iid, item in items.items():
        if (not isinstance(item, dict) or item.get('status') not in {'resolved', 'unresolved'}
                or not refs_shape(item.get('sources')) or not string_list(item.get('open_questions'))):
            errors.append(iid + ': association review needs status, source hashes and open_questions')
        elif item['status'] == 'unresolved' and not item['open_questions']:
            errors.append(iid + ': unresolved association requires a concrete question')
    non_icons = {aid for aid in b['scope']['required_artifacts']
                 if b['artifacts'][aid].get('stage') == 3 and not icon(b['artifacts'][aid])}
    for aid in b['scope']['required_artifacts']:
        a = b['artifacts'][aid]
        if a.get('role') != 'source_reference' and (not a.get('item_ids') or not set(a['item_ids']) <= known):
            errors.append(aid + ': item-producing artifact requires complete indexed item membership')
    covered = set()
    for sid, row in scenes.items():
        if (not isinstance(row, dict) or not string_list(row.get('item_ids')) or not string_list(row.get('artifact_ids'))
                or not set(row['item_ids']) <= known or not set(row['artifact_ids']) <= non_icons
                or not refs_shape(row.get('sources'))):
            errors.append(sid + ': scene membership/producer coverage/source evidence invalid')
            continue
        actual = {aid for aid in non_icons if artifact_scene(b, aid) == sid}
        if not actual <= set(row['artifact_ids']):
            errors.append(sid + ': scene index omits a declared scene producer')
        for aid in row['artifact_ids']:
            a = b['artifacts'][aid]
            if artifact_scene(b, aid) not in {'', sid}:
                errors.append(sid + ': producer belongs to another scene: ' + aid)
            used_items = set(a.get('item_ids', []))
            if not used_items <= set(row['item_ids']):
                errors.append(sid + ': scene membership omits producer content: ' + aid)
        covered.update(row['artifact_ids'])
    if covered != non_icons:
        errors.append('scene index must assign every required stage-3 non-Icon producer')
    seen = set()
    for row in relations:
        if (not isinstance(row, dict) or not row.get('id') or row['id'] in seen
                or row.get('kind') not in RELATIONS or row.get('status') not in {'resolved', 'unresolved'}
                or not string_list(row.get('item_ids')) or not row['item_ids'] or not set(row['item_ids']) <= known
                or not string_list(row.get('artifact_ids')) or not set(row['artifact_ids']) <= set(b['artifacts'])
                or not string_list(row.get('consumer_scene_ids', []))
                or not set(row.get('consumer_scene_ids', [])) <= set(scenes)
                or (row['artifact_ids'] and not row.get('consumer_scene_ids'))
                or not string_list(row.get('fact_refs')) or not refs_shape(row.get('sources')) or not row.get('reason')):
            errors.append('invalid, unsupported or unevidenced relation: ' + str(row.get('id') if isinstance(row, dict) else row))
            continue
        seen.add(row['id'])
        if row['kind'] not in PHYSICAL_RELATIONS and not row['fact_refs'] and not row['artifact_ids']:
            errors.append(row['id'] + ': a semantic relation must identify actual facts or image prerequisites')
        referenced_items = set()
        for aid in row['artifact_ids']:
            referenced_items.update(b['artifacts'][aid].get('item_ids', []))
        for value in row['fact_refs']:
            try:
                iid, field = value.split('.', 1)
                archive['items'][iid]['requirements'][field]
                referenced_items.add(iid)
            except (KeyError, ValueError):
                errors.append(row['id'] + ': missing related fact ' + value)
        if not referenced_items <= set(row['item_ids']):
            errors.append(row['id'] + ': relation omits referenced item membership')
    if not errors:
        for sid, scene in scenes.items():
            members = set(scene['item_ids'])
            applicable = [r for r in relations if set(r['item_ids']) & members and
                          (r['kind'] in PHYSICAL_RELATIONS or not r.get('consumer_scene_ids') or sid in r['consumer_scene_ids'])]
            physical_items = {i for r in applicable if r['kind'] in PHYSICAL_RELATIONS for i in r['item_ids']}
            declared_facts = {ref for r in applicable for ref in r['fact_refs']}
            for aid in scene['artifact_ids']:
                for ref in b['artifacts'][aid].get('fact_refs', []):
                    if ref.split('.', 1)[0] not in members | physical_items and ref not in declared_facts:
                        errors.append(sid + ': cross-item fact needs an evidenced association: ' + ref)
    return errors

def normalize_sources(index, base, archive):
    index = copy.deepcopy(index)
    for row in list(index['items'].values()) + list(index['scenes'].values()) + index['relations']:
        for source in row['sources']:
            p = Path(source['path'])
            source['path'] = str((base / p).resolve() if not p.is_absolute() else p.resolve())
            if sha(source['path']).lower() != source['sha256'].lower():
                raise ValueError('scene association source bytes changed: ' + source['path'])
            source['sha256'] = source['sha256'].lower()
    # The command records the facts actually presented for this association
    # review, so a later archive edit cannot retain an old resolved declaration.
    for iid, item in index['items'].items():
        item['requirements_sha256'] = digest(archive['items'][iid]['requirements'])
    for relation in index['relations']:
        relation['fact_values_sha256'] = digest({ref: archive['items'][ref.split('.', 1)[0]]['requirements'][ref.split('.', 1)[1]]
                                                for ref in relation['fact_refs']})
    return index

def active_index(b):
    pointer = b.get('scene_release_index')
    if pointer is None:
        return None
    if not isinstance(pointer, dict) or not pointer.get('path') or sha(pointer['path']) != pointer.get('sha256'):
        raise ValueError('scene release index snapshot changed or incomplete')
    return read(pointer['path'])

def owners(b, index, aid):
    return sorted(sid for sid, row in index['scenes'].items() if aid in row['artifact_ids'])

def closure(b, archive, index, sid):
    """Keep production dependencies separate from referenced facts/context.

    Physical identity/state/container groups require their stage-2 assets. A date
    or depicted identity reference locks its named facts, not unrelated images.
    """
    if sid not in index['scenes']:
        raise ValueError('scene is not in the locked index: ' + sid)
    row = index['scenes'][sid]
    production_items = set(row['item_ids'])
    context_items = set(production_items)
    related = {}
    roots = set()
    referenced_facts = set()
    while True:
        before = (set(production_items), set(context_items), set(roots), set(related))
        for relation in index['relations']:
            physical = relation['kind'] in PHYSICAL_RELATIONS
            consumers = relation.get('consumer_scene_ids', [])
            applicable = physical or not consumers or sid in consumers
            if applicable and set(relation['item_ids']) & (production_items if physical else context_items):
                related[relation['id']] = relation
                context_items.update(relation['item_ids'])
                if physical:
                    production_items.update(relation['item_ids'])
                if sid in relation.get('consumer_scene_ids', []):
                    roots.update(relation['artifact_ids'])
        roots.update(aid for aid in b['scope']['required_artifacts']
                     if b['artifacts'][aid].get('stage') == 2 and set(b['artifacts'][aid].get('item_ids', [])) & production_items)
        # Traverse local future producers for their inputs, but never demand a
        # local not-yet-produced scene/menu as its own stage-2->3 prerequisite.
        local = set(row['artifact_ids'])
        seen = set()
        def visit(aid, stack=None):
            stack = set() if stack is None else stack
            if aid in stack:
                raise ValueError('artifact dependency cycle: ' + aid)
            if aid in seen:
                return
            seen.add(aid)
            if aid not in b['artifacts']:
                raise ValueError('missing dependency artifact: ' + aid)
            a = b['artifacts'][aid]
            production_items.update(a.get('item_ids', []))
            context_items.update(a.get('item_ids', []))
            context_items.update(v.split('.', 1)[0] for v in a.get('fact_refs', []))
            referenced_facts.update(a.get('fact_refs', []))
            for parent in a.get('parents', []):
                if parent not in local:
                    roots.add(parent)
                visit(parent, stack | {aid})
        for aid in list(local | roots):
            visit(aid)
        context_items.update(production_items)
        if before == (production_items, context_items, roots, set(related)):
            break
    if not context_items <= set(index['items']):
        raise ValueError('dependency content outside indexed full scope')
    errors = []
    for iid in sorted(production_items):
        item = index['items'][iid]
        if item['status'] != 'resolved' or item['open_questions']:
            errors.append(iid + ': unresolved association: ' + '; '.join(item['open_questions']))
        if item.get('requirements_sha256') != digest(archive['items'][iid]['requirements']):
            errors.append(iid + ': physical content changed since association confirmation')
    for relation in related.values():
        if relation['status'] != 'resolved':
            errors.append(relation['id'] + ': unresolved external/content relation: ' + relation['reason'])
        values = {ref: archive['items'][ref.split('.', 1)[0]]['requirements'][ref.split('.', 1)[1]]
                  for ref in relation['fact_refs']}
        if relation.get('fact_values_sha256') != digest(values):
            errors.append(relation['id'] + ': referenced facts changed since association confirmation')
        if sid in relation.get('consumer_scene_ids', []) and set(relation['artifact_ids']) & set(row['artifact_ids']):
            errors.append(relation['id'] + ': local future producer cannot be a stage-3 prerequisite')
    sources = [r for entry in [row] + [index['items'][i] for i in sorted(production_items)] + list(related.values()) for r in entry['sources']]
    for source in sources:
        try:
            if sha(source['path']) != source['sha256']:
                errors.append('association source changed: ' + source['path'])
        except OSError:
            errors.append('association source unavailable: ' + source['path'])
    fact_refs = {iid + '.' + field for iid in production_items for field in archive['items'][iid]['requirements']}
    fact_refs.update(referenced_facts)
    fact_refs.update(ref for relation in related.values() for ref in relation['fact_refs'])
    facts = {ref: archive['items'][ref.split('.', 1)[0]]['requirements'][ref.split('.', 1)[1]] for ref in sorted(fact_refs)}
    # Empty/raw sources need current bytes too; PASS and real review are checked
    # by the existing workflow validator rather than created by this helper.
    prereqs = {aid: {k: b['artifacts'][aid].get(k) for k in ('role', 'sha256', 'rejected', 'acceptance_contract', 'parents', 'fact_refs')}
               for aid in sorted(roots)}
    base = Path(b['scene_release_index']['path']).parent.parent
    for aid in prereqs:
        review_path = b['artifacts'][aid].get('review')
        try:
            prereqs[aid]['review_sha256'] = sha(base / review_path) if review_path else None
        except OSError:
            prereqs[aid]['review_sha256'] = 'missing'
    context = {'scene_id': sid, 'scope_sha256': digest(b['scope']), 'scene_membership': row,
               'items': {i: index['items'][i] for i in sorted(production_items)},
               'relations': [related[i] for i in sorted(related)], 'facts': facts, 'prerequisites': prereqs}
    return {'scene_id': sid, 'item_ids': sorted(context_items), 'production_item_ids': sorted(production_items),
            'context_fact_refs': sorted(fact_refs), 'prerequisite_artifacts': sorted(roots),
            'relation_ids': sorted(related), 'context_sha256': digest(context), 'failures': sorted(set(errors))}

def artifact_binding(b, archive, aid):
    index = active_index(b)
    if index is None:
        return {}
    return {sid: closure(b, archive, index, sid)['context_sha256'] for sid in owners(b, index, aid)}
