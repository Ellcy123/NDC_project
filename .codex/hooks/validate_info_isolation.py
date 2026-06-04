"""
检测对话草稿中是否引用了同 Loop 平行场景的证据（违反"信息严密性"原则）
级别: WARNING（宁可漏报不误报）
"""
import json, re, os, sys, glob

# 读取 stdin JSON
try:
    stdin_data = json.loads(sys.stdin.buffer.read().decode('utf-8'))
except Exception:
    sys.exit(0)

file_path = stdin_data.get('file_path', '')
if not file_path:
    sys.exit(0)

# 只检查对话草稿和生成草稿
if not any(kw in file_path for kw in ['对话草稿', '生成草稿']):
    sys.exit(0)

if not os.path.exists(file_path):
    sys.exit(0)

# 项目根目录 = hook文件所在目录的上两级
project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 1. 从文件名提取 Loop 编号
basename = os.path.basename(file_path)
loop_match = re.search(r'[Ll]oop(\d)', basename)
if not loop_match:
    sys.exit(0)
loop_num = loop_match.group(1)

# 2. 搜索对应的 state 文件
state_candidates = glob.glob(os.path.join(project_dir, '**', f'loop{loop_num}_state.yaml'), recursive=True)
if not state_candidates:
    sys.exit(0)

# 优先使用 AVG/前置配置/ 下的
state_path = state_candidates[0]
for c in state_candidates:
    if '前置配置' in c:
        state_path = c
        break

# 3. 解析 state 文件
try:
    import yaml
    with open(state_path, encoding='utf-8') as f:
        state = yaml.safe_load(f)
except Exception:
    sys.exit(0)

if not state or 'scenes' not in state:
    sys.exit(0)

# 构建映射: talk_name → scene_id, scene_id → set(evidence_ids)
talk_to_scene = {}
scene_evidence = {}

# opening 场景
opening = state.get('opening', {})
if opening and isinstance(opening, dict):
    opening_scene = str(opening.get('scene_id', ''))
    if opening_scene:
        scene_evidence[opening_scene] = set()
        talk = opening.get('talk', '')
        if talk:
            talk_to_scene[talk] = opening_scene
        for key, val in opening.items():
            if isinstance(val, dict) and 'talk' in val:
                talk_to_scene[val['talk']] = opening_scene

for scene in state['scenes']:
    sid = str(scene.get('id', ''))
    if not sid:
        continue

    ev_ids = set()

    # 直接证据列表
    for ev in scene.get('evidence', []):
        if isinstance(ev, dict):
            ev_ids.add(str(ev.get('id', '')))

    # body_search 中的证据
    bs = scene.get('body_search', {})
    if bs and isinstance(bs, dict):
        for ev in bs.get('evidence', []):
            if isinstance(ev, dict):
                ev_ids.add(str(ev.get('id', '')))

    # NPC talk 映射
    npcs = scene.get('npcs', {})
    if isinstance(npcs, dict):
        for npc_key, npc_data in npcs.items():
            if isinstance(npc_data, dict):
                talk = npc_data.get('talk', '')
                if talk:
                    talk_to_scene[talk] = sid

    scene_evidence[sid] = ev_ids

# 收集本 loop 所有证据 ID
all_loop_evidence = set()
for ev_set in scene_evidence.values():
    all_loop_evidence.update(ev_set)

# 4. 解析对话草稿
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 按 ## Talk: 分段
sections = re.split(r'^## Talk:\s*', content, flags=re.MULTILINE)

warnings = []

for section in sections[1:]:
    # 提取 talk 名称
    first_line = section.split('\n')[0].strip()
    talk_match = re.match(r'(\w+)\.json', first_line)
    if not talk_match:
        continue
    talk_name = talk_match.group(1)

    current_scene = talk_to_scene.get(talk_name)
    if not current_scene:
        continue

    # 提取 `get` → XXXX 的证据 ID（4位数字）
    get_ids = re.findall(r'`get`\s*[→\->]+\s*(\d{4})', section)
    if not get_ids:
        continue

    current_evidence = scene_evidence.get(current_scene, set())
    for eid in get_ids:
        if eid in current_evidence:
            continue  # 属于当前场景
        if eid not in all_loop_evidence:
            continue  # 不属于本 loop（前序 loop 的证据）
        # 属于本 loop 的其他场景 → 疑似跨场景泄漏
        source_scene = None
        for s_id, s_ev in scene_evidence.items():
            if eid in s_ev:
                source_scene = s_id
                break
        warnings.append(
            f'  Talk [{talk_name}] (场景{current_scene}) 引用了证据 {eid}，'
            f'但该证据属于场景 {source_scene or "未知"}'
        )

if warnings:
    print('WARNING [信息隔离] 检测到可能的跨场景证据引用:')
    for w in warnings:
        print(w)

# 永远 exit 0（WARNING 不阻断）
sys.exit(0)
