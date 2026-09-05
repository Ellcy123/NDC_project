"""Build only this experimental unit. Does not import or write formal AVG tables."""
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / '剧情设计/试验单元/U1_五Loop试验版/L2_完整对白.md'

def compile_dialogue():
    manifest = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
    result, key, current = {}, None, None
    for number, line in enumerate(SOURCE.read_text(encoding='utf-8').splitlines(), 1):
        header = re.fullmatch(r'## dialogue: ([a-z0-9_]+)', line.strip())
        if header:
            key = header.group(1)
            if key in result:
                raise ValueError(f'Duplicate section: {key}')
            result[key], current = [], None
            continue
        if not key:
            continue
        actor = re.fullmatch(r'\*\*(.+?)\*\*(?:\s*\[(.*?)\])?', line.strip())
        if actor:
            current = {'speaker': actor.group(1), 'action': actor.group(2) or '', 'text': '', 'grants': []}
            result[key].append(current)
        elif line.startswith('>'):
            if current is None:
                raise ValueError(f'Unbound text at {number}')
            current['text'] += ('\n' if current['text'] else '') + line[1:].strip()
        elif line.startswith('@get '):
            item = line[5:].strip()
            if current is None or item not in manifest['items']:
                raise ValueError(f'Invalid grant at {number}: {item}')
            current['grants'].append(item)
        elif line.startswith('@'):
            raise ValueError(f'Unsupported experimental directive at {number}: {line}')
    required = {manifest['opening'], manifest['expose']['opening'], manifest['expose']['ending'], 'photo_analyze'}
    for scene in manifest['scenes']:
        if scene.get('entry'): required.add(scene['entry'])
        required.update(o['dialogue'] for o in scene['objects'])
    for npc in manifest['npcs'].values():
        required.update([npc['intro'], npc['repeat']])
        required.update(t['id'] for t in npc['topics'])
        assert len(npc['topics']) <= 3
    for step in manifest['expose']['rounds']:
        required.update([step['lie'], step['success'], step['wrong']])
    if required != set(result):
        raise ValueError(f'Section mismatch: missing={required-set(result)}, extra={set(result)-required}')
    for section, nodes in result.items():
        if not nodes or any(not node['text'] for node in nodes):
            raise ValueError('Empty dialogue node: '+section)
    expected = {'tommy_management':'signature_statement','tommy_income':'accounts_claim','tommy_night':'tommy_night_statement','james_wages':'james_pay_statement','james_night':'james_night_statement','camera_find':'photo_raw','photo_analyze':'photo_amounts','inspect_public':'public_ledger','inspect_private':'private_ledger','inspect_letter':'demand_letter','inspect_vip':'vip_photo','inspect_wage':'pay_stub'}
    for section,nodes in result.items():
        actual = [g for n in nodes for g in n['grants']]
        if actual != ([expected[section]] if section in expected else []):
            raise ValueError(f'Grant mismatch: {section}: {actual}')
    (HERE / 'dialogue.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    report = {'sections':len(result),'nodes':sum(map(len,result.values())),'topics':sum(len(n['topics']) for n in manifest['npcs'].values()),'source':str(SOURCE.relative_to(ROOT))}
    (HERE / 'build_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=True))

if __name__ == '__main__':
    compile_dialogue()
