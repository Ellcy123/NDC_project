"""
统一入口：从 stdin 读取一次 JSON，根据 file_path 路由到对应的检查逻辑。
避免多个 hook 各自启动 python 提取路径的重复开销。

用法: 被 validate-all.sh 调用，stdin 接收 PreToolUse JSON
退出码: 0=通过（含WARNING）, 1=ERROR阻断

重要: PreToolUse 在工具执行之前触发，所以：
  - Write 操作: 文件可能还不存在，要检查的内容在 stdin_data['content']
  - Edit 操作: 文件存在但还是旧内容，新内容在 stdin_data['new_string']
"""
import json, re, os, sys


def get_content_to_check(stdin_data, file_path):
    """获取需要检查的文本内容。
    优先使用 stdin 中即将写入的内容（Write 的 content 或 Edit 的 new_string），
    其次才读磁盘上的旧文件。
    返回 (full_text, is_new_file)
    """
    content = stdin_data.get('content', '')      # Write 操作的完整内容
    new_string = stdin_data.get('new_string', '')  # Edit 操作的新片段

    if content:
        # Write 操作：content 就是即将写入的完整文件
        return content, True
    elif new_string and os.path.exists(file_path):
        # Edit 操作：读旧文件，模拟替换后的完整内容
        old_string = stdin_data.get('old_string', '')
        try:
            with open(file_path, encoding='utf-8') as f:
                old_content = f.read()
            # 模拟 Edit 的效果
            return old_content.replace(old_string, new_string, 1), False
        except Exception:
            return new_string, False
    elif os.path.exists(file_path):
        # 兜底：直接读旧文件
        try:
            with open(file_path, encoding='utf-8') as f:
                return f.read(), False
        except Exception:
            return '', False
    return '', True


def main():
    # 1. 读取 stdin JSON（一次性）
    try:
        raw = sys.stdin.buffer.read().decode('utf-8')
        stdin_data = json.loads(raw)
    except Exception:
        return 0

    file_path = stdin_data.get('file_path', '')
    if not file_path:
        return 0

    results = []  # (level, message)

    # 2. 路由检查
    is_dialogue = any(kw in file_path for kw in ['对话草稿', '生成草稿'])
    is_avg = 'AVG' in file_path or is_dialogue
    is_state = ('state' in file_path and file_path.endswith(('.yaml', '.yml'))) or '前置配置' in file_path
    is_evidence = any(kw in file_path for kw in ['ItemStaticData', '证据设计', '证据美术'])
    is_json = file_path.endswith('.json')

    # 获取即将写入的内容（Write 的 content 或 Edit 后的完整文件）
    check_text, is_new = get_content_to_check(stdin_data, file_path)

    # ── 检查 1: 对话格式（重复ID / JSON语法） ──
    if is_avg and check_text:
        if is_json:
            try:
                json.loads(check_text)
            except json.JSONDecodeError as e:
                results.append(('ERROR', f'Invalid JSON syntax: {e}'))

        if is_dialogue:
            ids = re.findall(r'(?<=### )\d{9}', check_text)
            seen = set()
            dupes = []
            for id_ in ids:
                if id_ in seen and id_ not in dupes:
                    dupes.append(id_)
                seen.add(id_)
            if dupes:
                results.append(('ERROR', f'Duplicate dialogue IDs: {dupes[:5]}'))

    # ── 检查 2: State YAML 格式 ──
    if is_state and check_text:
        try:
            import yaml
            data = yaml.safe_load(check_text)
            if data is None:
                results.append(('WARNING', f'Empty YAML file: {file_path}'))
            elif re.search(r'loop\d+_state', file_path):
                missing = [field for field in ['player_context', 'scenes'] if field not in data]
                if missing:
                    results.append(('WARNING', f'Missing top-level fields: {missing}'))
        except Exception as e:
            if 'yaml' in str(type(e).__module__):
                results.append(('ERROR', f'Invalid YAML syntax: {e}'))

    # ── 检查 3: Zack 结论性语言（悬疑感原则） ──
    if is_dialogue and check_text:
        lines = check_text.splitlines(keepends=True)

        spoiler_phrases = [
            r'所以这说明', r'由此可见', r'这证明了', r'这意味着',
            r'换句话说', r'也就是说', r'真相是', r'答案很明显',
            r'不难看出', r'可以确定', r'一切都指向', r'显而易见',
            r'这就解释了', r'事实上就是', r'毫无疑问', r'很明显就是',
            r'肯定是.*的', r'必定是', r'说白了就是',
        ]
        pattern = '|'.join(spoiler_phrases)

        spoilers = []
        for i, line in enumerate(lines):
            if re.match(r'\*\*扎克', line):
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].startswith('>'):
                        dialogue = lines[j][1:].strip()
                        m = re.search(pattern, dialogue)
                        if m:
                            preview = dialogue[:60] + ('...' if len(dialogue) > 60 else '')
                            spoilers.append(f'  L{j+1}: "{preview}" (触发词: {m.group()})')
                    elif lines[j].strip() and not lines[j].startswith('>'):
                        break

        if spoilers:
            msg = 'Zack台词中检测到结论性语言:\n' + '\n'.join(spoilers)
            results.append(('WARNING', msg))

    # ── 检查 4: 跨场景信息泄漏（信息隔离原则） ──
    if is_dialogue and check_text:
        try:
            import yaml, glob

            basename = os.path.basename(file_path)
            loop_match = re.search(r'[Ll]oop(\d)', basename)
            if loop_match:
                loop_num = loop_match.group(1)
                project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

                state_candidates = glob.glob(
                    os.path.join(project_dir, '**', f'loop{loop_num}_state.yaml'),
                    recursive=True
                )
                state_path = None
                for c in state_candidates:
                    if '前置配置' in c:
                        state_path = c
                        break
                if not state_path and state_candidates:
                    state_path = state_candidates[0]

                if state_path:
                    with open(state_path, encoding='utf-8') as f:
                        state = yaml.safe_load(f)

                    if state and 'scenes' in state:
                        talk_to_scene = {}
                        scene_evidence = {}

                        # opening
                        opening = state.get('opening', {})
                        if opening and isinstance(opening, dict):
                            osid = str(opening.get('scene_id', ''))
                            if osid:
                                scene_evidence[osid] = set()
                                talk = opening.get('talk', '')
                                if talk:
                                    talk_to_scene[talk] = osid
                                for k, v in opening.items():
                                    if isinstance(v, dict) and 'talk' in v:
                                        talk_to_scene[v['talk']] = osid

                        for scene in state['scenes']:
                            sid = str(scene.get('id', ''))
                            if not sid:
                                continue
                            ev_ids = set()
                            for ev in scene.get('evidence', []):
                                if isinstance(ev, dict):
                                    ev_ids.add(str(ev.get('id', '')))
                            bs = scene.get('body_search', {})
                            if bs and isinstance(bs, dict):
                                for ev in bs.get('evidence', []):
                                    if isinstance(ev, dict):
                                        ev_ids.add(str(ev.get('id', '')))
                            npcs = scene.get('npcs', {})
                            if isinstance(npcs, dict):
                                for nk, nd in npcs.items():
                                    if isinstance(nd, dict) and 'talk' in nd:
                                        talk_to_scene[nd['talk']] = sid
                            scene_evidence[sid] = ev_ids

                        all_loop_ev = set()
                        for s in scene_evidence.values():
                            all_loop_ev.update(s)

                        # 用 check_text（即将写入的内容）而非磁盘文件
                        sections = re.split(r'^## Talk:\s*', check_text, flags=re.MULTILINE)
                        iso_warnings = []
                        for section in sections[1:]:
                            fl = section.split('\n')[0].strip()
                            tm = re.match(r'(\w+)\.json', fl)
                            if not tm:
                                continue
                            talk_name = tm.group(1)
                            cur_scene = talk_to_scene.get(talk_name)
                            if not cur_scene:
                                continue
                            get_ids = re.findall(r'`get`\s*[→\->]+\s*(\d{4})', section)
                            cur_ev = scene_evidence.get(cur_scene, set())
                            for eid in get_ids:
                                if eid not in cur_ev and eid in all_loop_ev:
                                    src = next((s for s, e in scene_evidence.items() if eid in e), '未知')
                                    iso_warnings.append(
                                        f'  Talk [{talk_name}] (场景{cur_scene}) '
                                        f'引用了证据 {eid}，但属于场景 {src}'
                                    )

                        if iso_warnings:
                            msg = '检测到可能的跨场景证据引用:\n' + '\n'.join(iso_warnings)
                            results.append(('WARNING', msg))
        except Exception:
            pass

    # ── 检查 5: 证据 ID 冲突（信息严密性原则） ──
    if is_evidence and os.path.basename(file_path) != 'ItemStaticData.json':
        try:
            project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            item_json = os.path.join(project_dir, 'preview_new2', 'data', 'table', 'ItemStaticData.json')

            if os.path.exists(item_json):
                with open(item_json, encoding='utf-8') as f:
                    items = json.load(f)
                existing_ids = {str(item['id']) for item in items if 'id' in item}

                def extract_ids(text):
                    pats = [
                        r'证据编号[：:]\s*(\d{4})',
                        r'\|\s*(\d{4})\s*\|',
                        r"(?:^|\s)id[：:\s]+[\"']?(\d{4})[\"']?",
                        r'-\s*id:\s*(\d{4})',
                    ]
                    ids = set()
                    for p in pats:
                        ids.update(re.findall(p, text, re.MULTILINE))
                    return ids

                new_string = stdin_data.get('new_string', '')
                old_string = stdin_data.get('old_string', '')
                content = stdin_data.get('content', '')

                new_ids = set()
                if new_string:
                    # Edit: 只检查新增的 ID
                    new_ids = extract_ids(new_string) - extract_ids(old_string)
                elif content:
                    # Write: 对比新内容与已有文件
                    new_ids = extract_ids(content)
                    if os.path.exists(file_path):
                        with open(file_path, encoding='utf-8') as f:
                            new_ids -= extract_ids(f.read())

                conflicts = new_ids & existing_ids
                if conflicts:
                    results.append((
                        'ERROR',
                        f'证据 ID 冲突！新增的以下 ID 已存在于 ItemStaticData: {sorted(conflicts)}\n'
                        f'  请分配新的 ID（参考编码规则: EPI01=1xxx, EPI02=2xxx, EPI03=3xxx）'
                    ))
        except Exception:
            pass

    # 3. 输出结果
    has_error = False
    for level, msg in results:
        if level == 'ERROR':
            print(f'ERROR: {msg}')
            has_error = True
        else:
            print(f'WARNING [{level_tag(msg)}] {msg}')

    return 1 if has_error else 0


def level_tag(msg):
    if '结论性语言' in msg or 'Zack' in msg:
        return '悬疑感'
    if '跨场景' in msg:
        return '信息隔离'
    return '校验'


if __name__ == '__main__':
    sys.exit(main())
