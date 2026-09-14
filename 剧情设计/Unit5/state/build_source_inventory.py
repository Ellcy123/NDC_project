"""Create a lossless paragraph-level source inventory for Unit5 State review."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
UNIT = ROOT / '剧情设计' / 'Unit5'
SOURCES = ['Unit5_大纲.md', 'Unit5_小Charles正确路线_终局线性流程.md',
           'Unit5_误指坏结局.md', '小玩法设计/L3_庄园双面剖面图_两阶段复原.md',
           '小玩法设计/L5_门厅照片墙_年份还原.md',
           '小玩法设计/终局A_夹层隐藏试听室_五步推理.md',
           '小玩法设计/终局B_飞行机械馆防火隔断_风险操作.md']

def build():
    result = {'schema_version': 1, 'unit': 'Unit5', 'sources': [], 'blocks': []}
    for idx, name in enumerate(SOURCES, 1):
        path = UNIT / name
        lines = path.read_text(encoding='utf-8-sig').splitlines()
        result['sources'].append({'path': path.relative_to(ROOT).as_posix(),
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'line_count': len(lines)})
        headings, block, start = [], [], 0
        def flush():
            if block:
                result['blocks'].append({'source_id': f'S{idx}-{start:04d}',
                    'source': path.relative_to(ROOT).as_posix(), 'line': start,
                    'anchor': ' / '.join(headings), 'source_text': '\n'.join(block)})
                block.clear()
        for number, line in enumerate(lines, 1):
            match = re.match(r'^(#{1,6}) (.*)', line)
            if match:
                flush()
                level = len(match[1])
                headings[:] = headings[:level-1] + [match[2]]
            elif not line.strip():
                flush()
            else:
                if not block:
                    start = number
                block.append(line)
        flush()
    return result

def coverage_plan(inventory):
    # Planned carriers follow the source's own stage boundaries, not NPC proximity.
    ranges = [(118, 205, 1, 'opening.sequence'), (245, 261, 1, 'opening.sequence'),
        (261, 336, 1, 'scenes'), (336, 361, 1, 'expose'), (361, 378, 1, 'expose.post_expose'),
        (384, 394, 2, 'opening.sequence'), (394, 433, 2, 'scenes'),
        (433, 457, 2, 'expose'), (457, 485, 2, 'expose.post_expose'),
        (493, 497, 3, 'opening.sequence'), (497, 525, 3, 'scenes'),
        (525, 535, 3, 'special_mechanics.section_stage1'),
        (535, 545, 3, 'special_mechanics.section_stage2'),
        (545, 555, 3, 'scenes.event_triggers'), (555, 565, 3, 'scenes'),
        (565, 590, 3, 'expose'), (590, 630, 3, 'expose.post_expose'),
        (636, 654, 4, 'opening.sequence'), (654, 704, 4, 'scenes'),
        (704, 747, 4, 'expose'), (747, 786, 4, 'expose.post_expose'),
        (792, 813, 5, 'opening.sequence'), (813, 880, 5, 'scenes'),
        (880, 952, 5, 'expose'), (952, 982, 5, 'expose.post_expose'),
        (982, 1008, 5, 'ending_sequence')]
    plans = []
    for block in inventory['blocks']:
        source_index = int(block['source_id'].split('-')[0][1:])
        loop, carrier = None, 'source_constraints'
        if source_index == 1:
            for start, end, n, target in ranges:
                if start <= block['line'] < end:
                    loop, carrier = n, target
                    break
            if 167 <= block['line'] < 175:
                loop, carrier = None, 'source_constraints.backstage_truth_not_performed'
        elif source_index in (2, 3):
            loop, carrier = 5, 'ending_sequence'
        elif source_index == 4:
            loop, carrier = 3, 'special_mechanics'
        else:
            loop = 5
            carrier = 'special_mechanics' if source_index == 5 else 'ending_sequence.special_mechanics'
        plans.append({**block, 'loop': loop, 'planned_carrier': carrier,
            'mapping': 'exact', 'deviation': 'none',
            'dialogue_required': loop is not None and bool(re.search(r'^\s*-?\s*(?:角色｜.+（可对话）|👤\s*NPC)', block['source_text'], re.M)),
            'testimony_required': '⚪' in block['source_text'] and source_index == 1 and loop is not None and carrier != 'expose',
            'testimony_reference_only': '⚪' in block['source_text'] and source_index == 1 and carrier == 'expose',
            'testimony_recheck': '⚪' in block['source_text'] and 'L1 已取得' in block['source_text'],
            'review_note': '段落级计划；生成者必须细分内联证言/证据与事件落点，约束不另演。'})
    return {'unit': 'Unit5', 'status': 'planned_not_generation_pass', 'rows': plans}

if __name__ == '__main__':
    target = Path(__file__).with_name('outline_source_inventory.json')
    inventory = build()
    target.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    target.with_name('outline_coverage_plan.json').write_text(
        json.dumps(coverage_plan(inventory), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(target)
