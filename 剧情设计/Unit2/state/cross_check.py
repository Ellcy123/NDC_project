import re, os, argparse, datetime

os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# ===========================
# CONSTANTS
# ===========================

NPC_NAME_MAP = {
    'morrison': '莫里森', 'ohara': '欧哈拉', 'tony': '托尼',
    'vinnie': '维尼', 'moore': '穆尔', 'leonard': '伦纳德',
    'danny': '丹尼', 'rose': '罗丝', 'emma': '艾玛', 'mickey': '米奇',
    'margaret': '玛格丽特', 'foster': '福斯特',
}

# 对话草稿文件搜索路径（优先级从高到低）
DIALOGUE_DRAFT_PATHS = [
    'AVG/0304/对话草稿/Loop{loop_num}',           # 单文件目录（每个NPC一个文件）
    'AVG/对话配置工作及草稿/生成草稿',              # 合并草稿
    'AVG/对话配置工作及草稿',                       # 旧版草稿
]

ALL_CHECKS = list('ABCDEFGHIJ')
STATE_CHECKS = list('ABCD')
DIALOGUE_CHECKS = list('EFGHIJ')

CHECK_NAMES = {
    'A': 'Scene Evidence IDs',
    'B': 'Testimony IDs',
    'C': 'Expose Evidence',
    'D': 'Doubt Conditions',
    'E': 'Dialogue ID Format',
    'F': 'Duplicate IDs',
    'G': 'Blind Spots Leaks',
    'H': 'Branch Convergence',
    'I': 'Get Spacing',
    'J': 'Evidence ID Range',
}

# ===========================
# CLI ARGUMENTS
# ===========================

parser = argparse.ArgumentParser(description='NDC Project Cross-Check Validator')
parser.add_argument('--loop', type=int, help='Only check specific loop (1-6)')
parser.add_argument('--check', type=str, help='Only run specific checks (comma-separated, e.g. A,B,G)')
parser.add_argument('--dialogue', action='store_true', help='Include dialogue draft checks (E-J)')
parser.add_argument('--verbose', action='store_true', help='Show detailed output including passing checks')
parser.add_argument('--update-status', action='store_true', help='Auto-update validation_status in state files')
args = parser.parse_args()

if args.loop:
    loop_range = [args.loop]
else:
    loop_range = list(range(1, 7))

if args.check:
    enabled_checks = [c.strip().upper() for c in args.check.split(',')]
else:
    enabled_checks = ALL_CHECKS if args.dialogue else STATE_CHECKS

def check_enabled(letter):
    return letter in enabled_checks

# ===========================
# LOAD DATA TABLES (regex)
# ===========================

def extract_items(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    items = {}
    id_pattern = re.compile(r'"id"\s*:\s*"(\d+)"')
    name_pattern = re.compile(r'"Name"\s*:\s*\["([^"]*)"')
    blocks = content.split('{')
    for block in blocks[1:]:
        id_match = id_pattern.search(block)
        name_match = name_pattern.search(block)
        if id_match:
            iid = id_match.group(1)
            name = name_match.group(1) if name_match else 'UNKNOWN'
            items[iid] = name
    return items

def extract_testimony_items(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    items = {}
    id_pattern = re.compile(r'"id"\s*:\s*"(\d+)"')
    testimony_pattern = re.compile(r'"testimony"\s*:\s*\["([^"]*)"')
    blocks = content.split('{')
    for block in blocks[1:]:
        id_match = id_pattern.search(block)
        test_match = testimony_pattern.search(block)
        if id_match:
            tid = id_match.group(1)
            text = test_match.group(1) if test_match else 'UNKNOWN'
            items[tid] = text
    return items

items = extract_items('preview_new2/data/table/ItemStaticData.json')
testimony_items = extract_testimony_items('preview_new2/data/table/TestimonyItem.json')

print(f'Loaded ItemStaticData: {len(items)} items')
print(f'Loaded TestimonyItem: {len(testimony_items)} items')
print()

# ===========================
# LOAD STATE FILES (regex)
# ===========================

def get_indent(line):
    """Return number of leading spaces in the line."""
    return len(line) - len(line.lstrip())

def extract_from_state(filepath):
    """Extract evidence IDs, testimony IDs, expose evidence, and doubt conditions from state YAML using regex."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {
        'scene_evidence': [],       # (scene_context, id, name)
        'testimony_ids': [],        # (npc_context, id)
        'expose_evidence': [],      # (round_context, id, name)
        'doubt_conditions': [],     # (doubt_id, doubt_text, condition_string)
    }

    lines = content.split('\n')
    current_scene = ''
    current_section = ''  # 'scenes', 'expose', 'doubts', 'opening', 'other'
    current_npc = ''
    current_round = ''
    in_evidence_block = False
    evidence_block_indent = 0
    in_usable_evidence = False
    usable_evidence_indent = 0
    current_doubt_id = ''
    current_doubt_text = ''

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        indent = get_indent(line)

        # Track top-level sections (indent 0)
        if indent == 0:
            if stripped.startswith('scenes:'):
                current_section = 'scenes'
                in_evidence_block = False
                in_usable_evidence = False
            elif stripped.startswith('expose:'):
                current_section = 'expose'
                in_evidence_block = False
                in_usable_evidence = False
            elif stripped.startswith('doubts:'):
                current_section = 'doubts'
                in_evidence_block = False
                in_usable_evidence = False
            elif stripped.startswith('opening:'):
                current_section = 'opening'
                in_evidence_block = False
                in_usable_evidence = False
            elif re.match(r'\w+:', stripped):
                current_section = 'other'
                in_evidence_block = False
                in_usable_evidence = False
            continue

        # --- SCENES SECTION ---
        if current_section == 'scenes':
            m = re.match(r'(\s*)evidence:', line)
            if m:
                in_evidence_block = True
                evidence_block_indent = get_indent(line)
                continue

            if in_evidence_block and indent <= evidence_block_indent:
                in_evidence_block = False

            m = re.match(r'\s*-\s*id:\s*(\d+)', line)
            if m and not in_evidence_block:
                scene_id = m.group(1)
                for j in range(i+1, min(i+5, len(lines))):
                    nm = re.match(r'\s*name:\s*"(.+)"', lines[j])
                    if nm:
                        current_scene = nm.group(1)
                        break
                continue

            m = re.match(r'\s*name:\s*"(.+)"', line)
            if m and not in_evidence_block:
                current_scene = m.group(1)
                continue

            if in_evidence_block:
                m = re.match(r'\s*-\s*id:\s*(\d+)', line)
                if m:
                    ev_id = m.group(1)
                    ev_name = ''
                    for j in range(i+1, min(i+5, len(lines))):
                        lj = lines[j].strip()
                        if not lj or lj.startswith('#'):
                            continue
                        nm = re.match(r'\s*name:\s*"(.+)"', lines[j])
                        if nm:
                            ev_name = nm.group(1)
                            break
                        if re.match(r'\s*-\s*id:', lines[j]):
                            break
                    result['scene_evidence'].append((current_scene, ev_id, ev_name))
                    continue

            m = re.match(r'\s+(\w+_\w+):', line)
            if m and not in_evidence_block and not line.strip().startswith('#'):
                candidate = m.group(1)
                if candidate not in ['lie_source', 'usable_evidence', 'unlock_condition']:
                    current_npc = candidate

            m = re.match(r'\s*-\s*(\d{7})\b', line)
            if m:
                tid = m.group(1)
                result['testimony_ids'].append((f'{current_scene} > {current_npc}', tid))
                continue

        # --- EXPOSE SECTION ---
        if current_section == 'expose':
            m = re.match(r'\s*(round_\d+):', line)
            if m:
                current_round = m.group(1)
                in_usable_evidence = False
                continue

            m = re.match(r'\s{2}target:', line)
            if m:
                continue

            m = re.match(r'\s{2}(\w+):$', line)
            if m:
                current_npc = m.group(1)
                continue

            if 'usable_evidence:' in stripped:
                in_usable_evidence = True
                usable_evidence_indent = get_indent(line)
                continue

            if in_usable_evidence:
                if indent <= usable_evidence_indent and not stripped.startswith('-') and not stripped.startswith('name:'):
                    m2 = re.match(r'\s*\w+:', stripped)
                    if m2 and 'name:' not in stripped:
                        in_usable_evidence = False

                if in_usable_evidence:
                    m = re.match(r'\s*-\s*id:\s*(\S+)', line)
                    if m:
                        ev_id = m.group(1)
                        ev_name = ''
                        for j in range(i+1, min(i+5, len(lines))):
                            lj = lines[j].strip()
                            if not lj or lj.startswith('#'):
                                continue
                            nm = re.match(r'\s*name:\s*"(.+)"', lines[j])
                            if nm:
                                ev_name = nm.group(1)
                                break
                            if re.match(r'\s*-\s*id:', lines[j]):
                                break
                        result['expose_evidence'].append((current_round, ev_id, ev_name))
                        continue

            m = re.match(r'\s*-\s*(\d{7})\b', line)
            if m and not in_usable_evidence:
                tid = m.group(1)
                result['testimony_ids'].append((f'expose > {current_npc}', tid))
                continue

        # --- DOUBTS SECTION ---
        if current_section == 'doubts':
            m = re.match(r'\s*-\s*id:\s*(\d+)', line)
            if m:
                current_doubt_id = m.group(1)
                continue

            m = re.match(r'\s*text:\s*"(.+)"', line)
            if m:
                current_doubt_text = m.group(1)[:80]
                continue

            m = re.match(r'\s*unlock_condition:\s*"(.+)"', line)
            if m:
                result['doubt_conditions'].append((current_doubt_id, current_doubt_text, m.group(1)))
                continue

    return result


# ===========================
# LOAD BLIND SPOTS (for CHECK G)
# ===========================

def load_blind_spots(filepath):
    """Extract blind_spots per NPC from npc_knowledge_pools.yaml using regex."""
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    result = {}
    current_npc = None
    in_blind_spots = False
    blind_spots_indent = 0

    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        indent = get_indent(line)

        # Top-level NPC key (indent 0, single word followed by colon)
        if indent == 0 and re.match(r'^(\w+):$', stripped):
            current_npc = stripped[:-1]
            in_blind_spots = False
            if current_npc not in result:
                result[current_npc] = []
            continue

        if current_npc:
            # blind_spots: keyword
            if stripped == 'blind_spots:':
                in_blind_spots = True
                blind_spots_indent = indent
                continue

            # Another keyword at same or higher level ends blind_spots
            if in_blind_spots and indent <= blind_spots_indent and not stripped.startswith('-'):
                in_blind_spots = False

            if in_blind_spots and stripped.startswith('- '):
                result[current_npc].append(stripped[2:])

    return result


def extract_keywords_from_blind_spot(text):
    """Extract distinguishing keywords from a blind_spot string.
    Focuses on: numbers, percentages, specific names (not too common), locations."""
    keywords = []

    # Numbers and percentages (e.g., "12%", "600", "289%", "3000")
    keywords.extend(re.findall(r'\d+%', text))
    keywords.extend(re.findall(r'\b\d{3,}\b', text))  # 3+ digit numbers

    # Chinese location/specific terms (2+ chars, excluding very common words)
    common_words = {'的', '了', '是', '在', '和', '与', '有', '不', '也', '就', '都', '这',
                    '那', '她', '他', '它', '们', '个', '来', '去', '到', '从', '对', '把',
                    '被', '让', '给', '用', '因为', '但是', '所以', '如果', '而且', '虽然',
                    '已经', '可以', '应该', '自己', '知道', '什么', '怎么', '没有', '不是',
                    '还是', '其实', '但', '或', '又', '也', '还', '却', '于', '很', '太',
                    '真', '最', '能', '会', '要', '想', '说', '看', '做', '叫', '过',
                    '死', '人', '事', '关系', '具体', '细节', '存在', '角色', '情况',
                    '完整', '过程', '原因', '结果'}

    # Extract quoted content or parenthesized content as high-value keywords
    quoted = re.findall(r'[「」""]([^「」""]+)[「」""]', text)
    keywords.extend(quoted)
    paren = re.findall(r'（([^）]+)）', text)
    for p in paren:
        # Split parenthesized content by common delimiters
        parts = re.split(r'[、，,]', p)
        keywords.extend([part.strip() for part in parts if len(part.strip()) >= 2])

    # Specific Chinese terms (location, identity, etc.) - extract 2-4 char segments
    # that aren't common words
    chinese_terms = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
    for term in chinese_terms:
        if term not in common_words and len(term) >= 2:
            keywords.append(term)

    # English proper nouns (capitalized words, 3+ chars)
    english_names = re.findall(r'\b[A-Z][a-z]{2,}\b', text)
    # Filter out very common names that would cause too many false positives
    # Keep names that are specific to the blind_spot context
    keywords.extend(english_names)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for kw in keywords:
        if kw not in seen and len(kw) >= 2:
            seen.add(kw)
            unique.append(kw)
    return unique


# ===========================
# DIALOGUE DRAFT LOADING
# ===========================

def find_dialogue_files(loop_num):
    """Find dialogue draft files for a given loop. Returns list of (filepath, filename) tuples."""
    files = []

    # Priority 1: Individual NPC files in AVG/0304/对话草稿/Loop{N}/
    dir1 = f'AVG/0304/对话草稿/Loop{loop_num}'
    if os.path.isdir(dir1):
        for fname in sorted(os.listdir(dir1)):
            if fname.endswith('.md'):
                files.append((os.path.join(dir1, fname), fname))

    # Priority 2: Combined draft in 生成草稿/
    combined = f'AVG/对话配置工作及草稿/生成草稿/Loop{loop_num}_生成草稿.md'
    if os.path.exists(combined) and not files:
        files.append((combined, os.path.basename(combined)))

    # Priority 3: Old draft location
    old = f'AVG/对话配置工作及草稿/Loop{loop_num}_对话草稿.md'
    if os.path.exists(old) and not files:
        files.append((old, os.path.basename(old)))

    return files


def load_dialogue_content(loop_num):
    """Load all dialogue content for a loop. Returns (combined_text, list_of_files)."""
    files = find_dialogue_files(loop_num)
    if not files:
        return None, []

    combined = ''
    for fpath, fname in files:
        with open(fpath, 'r', encoding='utf-8') as f:
            combined += f'\n\n<!-- FILE: {fname} -->\n\n' + f.read()

    return combined, files


def extract_dialogue_ids(content):
    """Extract all dialogue IDs from ### headers. Returns list of (id_str, line_num)."""
    ids = []
    for i, line in enumerate(content.split('\n'), 1):
        m = re.match(r'^### (\d+)', line)
        if m:
            ids.append((m.group(1), i))
    return ids


def extract_npc_lines(content):
    """Extract dialogue lines grouped by NPC Chinese name.
    Returns dict: {npc_cn_name: [(line_num, line_text), ...]}"""
    result = {}
    lines = content.split('\n')
    current_speaker = None

    for i, line in enumerate(lines, 1):
        # Speaker line: **NPC中文名** or **扎克·布伦南**
        m = re.match(r'^\*\*(.+?)\*\*', line)
        if m:
            current_speaker = m.group(1).split('[')[0].strip()  # Remove emotion tag
            continue

        # Dialogue line (starts with >)
        if line.strip().startswith('>') and current_speaker:
            text = line.strip()[1:].strip()
            if text and not text.startswith('📋') and not text.startswith('-'):
                if current_speaker not in result:
                    result[current_speaker] = []
                result[current_speaker].append((i, text))

    return result


# ===========================
# VALIDATION STATUS UPDATE
# ===========================

def update_validation_status(filepath, result_str):
    """Update the cross_check field in a state file's validation_status section."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    today = datetime.date.today().isoformat()
    new_value = f'{today} {result_str}'

    # Try to update existing cross_check field
    pattern = r'(  cross_check:\s*)"[^"]*"'
    if re.search(pattern, content):
        content = re.sub(pattern, rf'\1"{new_value}"', content)
    else:
        # Append validation_status section if missing
        vs_block = f'''
# ═══════════════════════════════════════
# 验证状态
# ═══════════════════════════════════════

validation_status:
  cross_check: "{new_value}"
  structure_completeness: "PENDING"
  evidence_coverage: "PENDING"
  npc_entries: "PENDING"
  goal_alignment: "PENDING"
  info_pacing: "PENDING"
  connoisseur: "PENDING"
  expose: "PENDING"
'''
        content = content.rstrip() + '\n' + vs_block

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


# ===========================
# RUN CHECKS
# ===========================

# Load blind spots once (for CHECK G)
blind_spots_data = {}
if check_enabled('G'):
    blind_spots_data = load_blind_spots('AVG/对话配置工作及草稿/前置配置/npc_knowledge_pools.yaml')

all_discrepancies = []
all_warnings = []
summary = {}  # {check_letter: (error_count, warning_count)}
for c in ALL_CHECKS:
    summary[c] = (0, 0)

# Track all IDs across loops for cross-loop duplicate detection (CHECK F)
global_id_registry = {}  # {id_str: (loop_num, filename, line_num)}

for loop_num in loop_range:
    fpath = f'AVG/0304/state/loop{loop_num}_state.yaml'
    if not os.path.exists(fpath):
        print(f'=== LOOP {loop_num}: state file not found, skipping ===')
        continue

    data = extract_from_state(fpath)
    discrepancies = []
    warnings = []

    # ─── STATE CHECKS (A-D) ───

    # CHECK A: Scene evidence IDs must exist in ItemStaticData
    if check_enabled('A'):
        for scene, ev_id, ev_name in data['scene_evidence']:
            if ev_id not in items:
                discrepancies.append(('A', f'scenes > "{scene}" > evidence', ev_id, ev_name,
                                      f'ID {ev_id} NOT FOUND in ItemStaticData'))
            elif ev_name and items[ev_id] != ev_name:
                discrepancies.append(('A', f'scenes > "{scene}" > evidence', ev_id, ev_name,
                                      f'NAME MISMATCH: state="{ev_name}" vs ItemStaticData="{items[ev_id]}"'))

    # CHECK B: Testimony IDs must exist in TestimonyItem
    if check_enabled('B'):
        for context, tid in data['testimony_ids']:
            if tid not in testimony_items:
                discrepancies.append(('B', f'{context} > testimony_ids', tid, '',
                                      f'Testimony ID {tid} NOT FOUND in TestimonyItem'))

    # CHECK C: Expose usable_evidence must exist in ItemStaticData
    if check_enabled('C'):
        for rnd, ev_id, ev_name in data['expose_evidence']:
            if ev_id.startswith('OBS'):
                continue
            if ev_id not in items:
                if ev_id in testimony_items:
                    discrepancies.append(('C', f'expose > {rnd} > usable_evidence', ev_id, ev_name,
                                          f'ID {ev_id} is a TestimonyItem, NOT in ItemStaticData (testimony text: "{testimony_items[ev_id][:60]}...")'))
                else:
                    discrepancies.append(('C', f'expose > {rnd} > usable_evidence', ev_id, ev_name,
                                          f'ID {ev_id} NOT FOUND in ItemStaticData or TestimonyItem'))
            elif ev_name and items[ev_id] != ev_name:
                discrepancies.append(('C', f'expose > {rnd} > usable_evidence', ev_id, ev_name,
                                      f'NAME MISMATCH: state="{ev_name}" vs ItemStaticData="{items[ev_id]}"'))

    # CHECK D: Doubt unlock_condition item/testimony references
    if check_enabled('D'):
        for doubt_id, doubt_text, condition in data['doubt_conditions']:
            item_refs = re.findall(r'item:(\d+)', condition)
            for iref in item_refs:
                if iref not in items:
                    discrepancies.append(('D', f'doubts > id={doubt_id} ("{doubt_text}")', iref, '',
                                          f'item:{iref} NOT FOUND in ItemStaticData'))
            test_refs = re.findall(r'testimony:(\d+)', condition)
            for tref in test_refs:
                if tref not in testimony_items:
                    discrepancies.append(('D', f'doubts > id={doubt_id} ("{doubt_text}")', tref, '',
                                          f'testimony:{tref} NOT FOUND in TestimonyItem'))

    # ─── DIALOGUE CHECKS (E-J) ───

    dialogue_content, dialogue_files = None, []
    if any(check_enabled(c) for c in DIALOGUE_CHECKS):
        dialogue_content, dialogue_files = load_dialogue_content(loop_num)
        if dialogue_content is None:
            if args.verbose:
                print(f'  [INFO] Loop {loop_num}: No dialogue draft files found, skipping checks E-J')

    if dialogue_content:
        dialogue_ids = extract_dialogue_ids(dialogue_content)

        # CHECK E: Dialogue ID format validation
        if check_enabled('E'):
            for id_str, line_num in dialogue_ids:
                if len(id_str) == 9:
                    # Talk ID: first digit should match loop number (for EPI02, loop digit in position 3)
                    # Format: {20}{loop}{scene}{sequence} — but actual format varies
                    # Just validate it's 9 digits
                    pass  # 9 digits is valid for Talk
                elif len(id_str) == 6:
                    pass  # 6 digits could be valid for some expose formats
                else:
                    discrepancies.append(('E', f'line {line_num}', id_str, '',
                                          f'ID length {len(id_str)} (expected 9 for Talk)'))

        # CHECK F: Duplicate ID detection
        if check_enabled('F'):
            loop_ids = {}  # {id_str: line_num} within this loop
            for id_str, line_num in dialogue_ids:
                if id_str in loop_ids:
                    discrepancies.append(('F', f'line {line_num}', id_str, '',
                                          f'DUPLICATE within Loop {loop_num} (first at line {loop_ids[id_str]})'))
                else:
                    loop_ids[id_str] = line_num

                # Cross-loop duplicate check
                if id_str in global_id_registry:
                    prev_loop, prev_file, prev_line = global_id_registry[id_str]
                    discrepancies.append(('F', f'line {line_num}', id_str, '',
                                          f'DUPLICATE across loops (also in Loop {prev_loop} line {prev_line})'))
                else:
                    fname = dialogue_files[0][1] if dialogue_files else ''
                    global_id_registry[id_str] = (loop_num, fname, line_num)

        # CHECK G: Blind spots keyword leak detection
        if check_enabled('G') and blind_spots_data:
            npc_lines = extract_npc_lines(dialogue_content)
            for npc_key, blind_spots_list in blind_spots_data.items():
                cn_name = NPC_NAME_MAP.get(npc_key, '')
                if not cn_name:
                    continue

                # Find NPC's dialogue lines (match by partial name)
                npc_dialogue = []
                for speaker, lines_list in npc_lines.items():
                    if cn_name in speaker:
                        npc_dialogue.extend(lines_list)

                if not npc_dialogue:
                    continue

                for bs in blind_spots_list:
                    keywords = extract_keywords_from_blind_spot(bs)
                    for kw in keywords:
                        for line_num, line_text in npc_dialogue:
                            if kw in line_text:
                                warnings.append(('G', f'{cn_name} line {line_num}', kw, '',
                                                 f'Keyword "{kw}" from blind_spot: "{bs[:60]}..."'))

        # CHECK H: Branch convergence
        if check_enabled('H'):
            lines = dialogue_content.split('\n')
            # Find all branch jump targets
            branch_targets = []  # (line_num, target_id)
            merge_points = []    # (line_num, target_id)

            for i, line in enumerate(lines, 1):
                # Branch option: > - ❶ ... → `{ID}`
                m = re.search(r'→\s*`(\d+)`', line)
                if m:
                    branch_targets.append((i, m.group(1)))

                # Merge point: → 汇合至 `{ID}`
                m = re.search(r'汇合至\s*`(\d+)`', line)
                if m:
                    merge_points.append((i, m.group(1)))

            # All IDs present in the file
            all_ids_set = set(id_str for id_str, _ in dialogue_ids)

            # Check branch targets exist
            for line_num, target_id in branch_targets:
                if target_id not in all_ids_set:
                    discrepancies.append(('H', f'line {line_num}', target_id, '',
                                          f'Branch target ID {target_id} NOT FOUND in dialogue'))

            # Check merge points exist
            for line_num, target_id in merge_points:
                if target_id not in all_ids_set:
                    discrepancies.append(('H', f'line {line_num}', target_id, '',
                                          f'Merge point ID {target_id} NOT FOUND in dialogue'))

        # CHECK I: Get spacing
        if check_enabled('I'):
            lines = dialogue_content.split('\n')
            # Track gets per Talk section
            current_talk = ''
            get_positions = []  # (line_num, evidence_id)
            dialogue_line_count = 0

            for i, line in enumerate(lines, 1):
                # New Talk section
                m = re.match(r'^## Talk:', line)
                if m:
                    # Check previous talk's gets
                    if len(get_positions) >= 2:
                        for j in range(1, len(get_positions)):
                            prev_line, prev_id = get_positions[j-1]
                            curr_line, curr_id = get_positions[j]
                            # Count ### headers between the two gets (dialogue lines)
                            between = 0
                            for k in range(prev_line, curr_line):
                                if k <= len(lines) and re.match(r'^### \d+', lines[k-1]):
                                    between += 1
                            between -= 1  # Exclude the get line itself
                            if between < 3:
                                discrepancies.append(('I', f'{current_talk}', f'{prev_id}→{curr_id}', '',
                                                      f'Only {between} dialogue lines between gets (minimum 3)'))

                    current_talk = line.strip()
                    get_positions = []
                    continue

                # Expose section also resets
                m = re.match(r'^## Expose:', line)
                if m:
                    # Final check for previous talk
                    if len(get_positions) >= 2:
                        for j in range(1, len(get_positions)):
                            prev_line, prev_id = get_positions[j-1]
                            curr_line, curr_id = get_positions[j]
                            between = 0
                            for k in range(prev_line, curr_line):
                                if k <= len(lines) and re.match(r'^### \d+', lines[k-1]):
                                    between += 1
                            between -= 1
                            if between < 3:
                                discrepancies.append(('I', f'{current_talk}', f'{prev_id}→{curr_id}', '',
                                                      f'Only {between} dialogue lines between gets (minimum 3)'))
                    current_talk = line.strip()
                    get_positions = []
                    continue

                # Get marker
                m = re.match(r'^### (\d+)\s+`get`', line)
                if m:
                    get_positions.append((i, m.group(1)))

            # Final check for last talk section
            if len(get_positions) >= 2:
                for j in range(1, len(get_positions)):
                    prev_line, prev_id = get_positions[j-1]
                    curr_line, curr_id = get_positions[j]
                    between = 0
                    for k in range(prev_line, curr_line):
                        if k <= len(lines) and re.match(r'^### \d+', lines[k-1]):
                            between += 1
                    between -= 1
                    if between < 3:
                        discrepancies.append(('I', f'{current_talk}', f'{prev_id}→{curr_id}', '',
                                              f'Only {between} dialogue lines between gets (minimum 3)'))

        # CHECK J: Evidence ID range validation
        if check_enabled('J'):
            for scene, ev_id, ev_name in data['scene_evidence']:
                if len(ev_id) == 4 and ev_id.startswith('2'):
                    # EPI02 evidence: 2{loop}{xx} format
                    ev_loop_digit = int(ev_id[1])
                    if ev_loop_digit > loop_num:
                        discrepancies.append(('J', f'scenes > "{scene}" > evidence', ev_id, ev_name,
                                              f'Evidence from Loop {ev_loop_digit} used in Loop {loop_num} (future loop)'))

    # ─── OUTPUT ───

    # Count per-check
    for check_letter, _, _, _, _ in discrepancies:
        err, warn = summary[check_letter]
        summary[check_letter] = (err + 1, warn)
    for check_letter, _, _, _, _ in warnings:
        err, warn = summary[check_letter]
        summary[check_letter] = (err, warn + 1)

    has_issues = discrepancies or warnings
    if has_issues:
        print(f'=== LOOP {loop_num} DISCREPANCIES ({len(discrepancies)} errors, {len(warnings)} warnings) ===')
        for check, location, eid, state_name, issue in discrepancies:
            print(f'  [{check}] {location}')
            if state_name:
                print(f'      ID: {eid}  |  State Name: "{state_name}"')
            else:
                print(f'      ID: {eid}')
            print(f'      Issue: {issue}')
            print()
        for check, location, eid, state_name, issue in warnings:
            print(f'  [{check}] WARNING: {location}')
            print(f'      {issue}')
            print()
    else:
        print(f'=== LOOP {loop_num}: ALL CLEAR ===')
    print()

    all_discrepancies.extend([(loop_num, d) for d in discrepancies])
    all_warnings.extend([(loop_num, w) for w in warnings])

    # Update validation_status if requested
    if args.update_status:
        error_count = len(discrepancies)
        if error_count == 0:
            update_validation_status(fpath, 'PASS')
        else:
            update_validation_status(fpath, f'FAIL: {error_count} issues')
        if args.verbose:
            print(f'  [INFO] Updated validation_status in {fpath}')

# ===========================
# SUMMARY
# ===========================

total_errors = len(all_discrepancies)
total_warnings = len(all_warnings)

print('========================================')
print('VALIDATION SUMMARY')
print('========================================')
for c in enabled_checks:
    err, warn = summary[c]
    name = CHECK_NAMES.get(c, c)
    status = 'PASS'
    parts = []
    if err > 0:
        parts.append(f'{err} errors')
    if warn > 0:
        parts.append(f'{warn} warnings')
    if parts:
        status = ', '.join(parts)
    print(f'  Check {c} ({name:.<25s}) {status}')
print('========================================')
print(f'TOTAL: {total_errors} errors, {total_warnings} warnings')
print('========================================')
