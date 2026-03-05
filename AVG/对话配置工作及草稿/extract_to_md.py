#!/usr/bin/env python3
"""
JSON → MD 提取脚本
将 EPI02 的 Talk/Expose JSON 文件提取为 MD 草稿（仅中文）。
每个 Loop 生成一个 MD 文件。

用法: python extract_to_md.py
"""

import json
import os
from pathlib import Path
from collections import OrderedDict

# 路径配置
BASE = Path(__file__).parent.parent  # NDC_project/AVG/
TALK_DIR = BASE / "EPI02" / "Talk"
EXPOSE_DIR = BASE / "EPI02" / "Expose"
OUTPUT_DIR = Path(__file__).parent  # 对话配置工作及草稿/

# Loop 主题（可自行修改）
LOOP_THEMES = {
    1: "火灾现场 + Morrison审讯",
    2: "威胁链条与连号钞票",
    3: "Mickey登场 + 掠夺性贷款",
    4: "Rose的黄昏之爱",
    5: "Vinnie纵火认罪",
    6: "Leonard终极指证",
}

# Expose 文件对应关系
EXPOSE_FILES = {
    1: "loop1_morrison.json",
    2: "loop2_leonard.json",
    3: "loop3_moore.json",
    4: "loop4_danny.json",
    5: "loop5_vinnie.json",
    6: "loop6_leonard.json",
}


def load_json(filepath):
    """加载 JSON 文件，处理可能的格式问题"""
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    return json.loads(text)


def format_action(cn_action):
    """提取情绪/表情描述，过滤肢体动作"""
    if not cn_action or cn_action.strip() == "":
        return ""
    return f" [{cn_action}]"


def format_talk_entry(entry, is_expose=False):
    """将单条对话转为 MD 格式"""
    lines = []
    entry_id = entry.get("id", "")
    script = entry.get("script", "")
    cn_speaker = entry.get("cnSpeaker", "")
    cn_action = entry.get("cnAction", "")
    cn_words = entry.get("cnWords", "")

    # 标题行：ID + 脚本标记
    header = f"### {entry_id}"

    if script == "get":
        param_int0 = entry.get("ParameterInt0", 0)
        header += f" `get` → {param_int0}"
    elif script in ("branches", "1"):
        header += " `branches`"
    elif script == "end":
        header += " `end`"
    elif script == "change_scene":
        param_str0 = entry.get("ParameterStr0", "")
        header += f" `change_scene` → {param_str0}"
    elif script == "Lie":
        param_int0 = entry.get("ParameterInt0", 0)
        param_int1 = entry.get("ParameterInt1", 0)
        param_str0 = entry.get("ParameterStr0", "")
        header += f" `Lie` → 成功跳转 `{param_int0}` (Round {param_int1})"

    lines.append(header)

    # 说话人 + 情绪
    action_str = format_action(cn_action)
    lines.append(f"**{cn_speaker}**{action_str}")

    # 对白
    if cn_words:
        # 多行对白处理
        for word_line in cn_words.split("\n"):
            lines.append(f"> {word_line}")

    # 获取证据附加信息
    if script == "get":
        param_int0 = entry.get("ParameterInt0", 0)
        key_info = entry.get("keyInfoContent", "")
        if key_info:
            lines.append(f"> 📋 获取证据: {param_int0}「{key_info}」")
        else:
            lines.append(f"> 📋 获取证据: {param_int0}")

    # 分支选项
    if script in ("branches", "1"):
        options = []
        for i in range(3):
            ps = entry.get(f"ParameterStr{i}", "")
            pi = entry.get(f"ParameterInt{i}", 0)
            if ps and ps.strip():
                options.append((ps, pi))
        markers = ["❶", "❷", "❸"]
        for idx, (text, target) in enumerate(options):
            m = markers[idx] if idx < len(markers) else f"({idx+1})"
            lines.append(f"> - {m} {text} → `{target}`")

    # Lie 可用证据
    if script == "Lie":
        param_str0 = entry.get("ParameterStr0", "")
        if param_str0:
            lines.append(f"> 🎯 可用证据: {param_str0}")

    lines.append("")  # 空行分隔
    return "\n".join(lines)


def detect_branches(entries):
    """检测分支结构：找出所有分支入口及其目标ID"""
    branch_targets = set()
    for entry in entries:
        script = entry.get("script", "")
        if script in ("branches", "1"):
            for i in range(3):
                pi = entry.get(f"ParameterInt{i}", 0)
                if pi:
                    branch_targets.add(pi)
    return branch_targets


def compute_branch_chains(entries):
    """计算所有分支链的 ID 集合和汇合点。
    返回 (branch_chain_ids: set, convergence_ids: set)
    - branch_chain_ids: 属于任何分支链内部的 ID（不包含汇合点）
    - convergence_ids: 分支汇合点 ID
    """
    id_to_entry = {e["id"]: e for e in entries}

    # 按分支入口分组：branch_entry_id → [target1, target2, ...]
    branch_groups = {}
    for entry in entries:
        script = entry.get("script", "")
        if script in ("branches", "1"):
            targets = []
            for i in range(3):
                pi = entry.get(f"ParameterInt{i}", 0)
                if pi:
                    targets.append(pi)
            if targets:
                branch_groups[entry["id"]] = targets

    branch_target_set = set()
    for targets in branch_groups.values():
        branch_target_set.update(targets)

    # 第一遍：追踪每条分支链的完整路径
    raw_chains = {}  # branch_target → [id1, id2, ...]
    for bt in branch_target_set:
        chain = []
        current = bt
        visited = set()
        while current and current in id_to_entry:
            if current in visited:
                break
            if current != bt and current in branch_target_set:
                break
            visited.add(current)
            chain.append(current)
            e = id_to_entry[current]
            nxt = e.get("next", "")
            script = e.get("script", "")
            if nxt == "" or script in ("end", "branches", "1"):
                break
            nxt_int = int(nxt) if nxt else 0
            if nxt_int in branch_target_set:
                break
            current = nxt_int
        raw_chains[bt] = chain

    # 第二遍：对于同一分支入口的多条链，找共同后缀（= 汇合段）
    convergence_ids = set()
    branch_chain_ids = set()

    for branch_entry_id, targets in branch_groups.items():
        chains_for_group = [raw_chains.get(t, []) for t in targets if t in raw_chains]
        if len(chains_for_group) < 2:
            for c in chains_for_group:
                branch_chain_ids.update(c)
            continue

        # 找所有链共有的 ID（汇合段 = 所有链都经过的尾部）
        id_sets = [set(c) for c in chains_for_group]
        shared = id_sets[0]
        for s in id_sets[1:]:
            shared = shared & s

        # 汇合点 = shared 中最早出现的 ID（在任一链中的位置）
        if shared:
            # 用第一条链的顺序找最早的共有 ID
            first_chain = chains_for_group[0]
            conv_start = None
            for cid in first_chain:
                if cid in shared:
                    conv_start = cid
                    break
            if conv_start:
                convergence_ids.add(conv_start)
                # 所有链中，汇合点之前的 ID 才是分支链 ID
                for chain in chains_for_group:
                    for cid in chain:
                        if cid in shared:
                            break
                        branch_chain_ids.add(cid)
            else:
                for c in chains_for_group:
                    branch_chain_ids.update(c)
        else:
            for c in chains_for_group:
                branch_chain_ids.update(c)

    return branch_chain_ids, convergence_ids


def process_talk_file(filepath):
    """处理单个 Talk JSON 文件 → MD 片段"""
    entries = load_json(filepath)
    if not entries:
        return ""

    filename = os.path.basename(filepath)
    location = entries[0].get("cnLocation", "")

    lines = []
    lines.append(f"## Talk: {filename}")
    lines.append(f"> 场景：{location}")
    lines.append("")

    # 分析分支结构
    branch_chain_ids, convergence_ids = compute_branch_chains(entries)

    # 找出哪些 ID 是分支的起始 + 对应文本
    branch_sections = {}  # target_id → label
    for entry in entries:
        script = entry.get("script", "")
        if script in ("branches", "1"):
            for i in range(3):
                pi = entry.get(f"ParameterInt{i}", 0)
                ps = entry.get(f"ParameterStr{i}", "")
                if pi and ps:
                    branch_sections[pi] = ps

    markers_list = ["❶", "❷", "❸"]
    branch_keys = list(branch_sections.keys())
    in_branch = False

    for entry in entries:
        eid = entry["id"]

        # 到达汇合点 → 结束分支区域
        if eid in convergence_ids and in_branch:
            in_branch = False
            lines.append("---")
            lines.append(f"<!-- 汇合点 -->")
            lines.append("")

        # 进入（或切换到下一个）分支
        if eid in branch_sections:
            in_branch = True
            label = branch_sections[eid]
            idx = branch_keys.index(eid) if eid in branch_keys else 0
            marker = markers_list[idx % len(markers_list)]
            lines.append("---")
            lines.append(f"<!-- 分支{marker}：{label} -->")
            lines.append("")

        # 输出对话条目
        lines.append(format_talk_entry(entry))

        # 如果在分支中，且 next 指向汇合点，标注
        if in_branch and eid in branch_chain_ids:
            nxt = entry.get("next", "")
            nxt_int = int(nxt) if nxt else 0
            if nxt_int in convergence_ids:
                lines.append(f"→ 汇合至 `{nxt_int}`")
                lines.append("")

    lines.append("")
    return "\n".join(lines)


def process_expose_file(filepath):
    """处理 Expose JSON 文件 → MD 片段"""
    entries = load_json(filepath)
    if not entries:
        return ""

    filename = os.path.basename(filepath)
    location = entries[0].get("cnLocation", "")

    lines = []
    lines.append(f"## Expose: {filename}")
    lines.append(f"> 场景：{location}")
    lines.append("")

    for entry in entries:
        lines.append(format_talk_entry(entry, is_expose=True))

    lines.append("")
    return "\n".join(lines)


def generate_loop_md(loop_num):
    """生成单个 Loop 的 MD 文件"""
    theme = LOOP_THEMES.get(loop_num, "")
    lines = []
    lines.append(f"# Loop {loop_num} - {theme}")
    lines.append("")

    # Talk 文件
    talk_dir = TALK_DIR / f"loop{loop_num}"
    if talk_dir.exists():
        # 按 manifest 或文件名排序
        manifest_path = talk_dir / "_manifest.json"
        if manifest_path.exists():
            try:
                manifest = load_json(manifest_path)
                talk_files = [f for f in manifest if f != "_manifest.json"]
            except Exception:
                talk_files = sorted(
                    [f for f in os.listdir(talk_dir) if f.endswith(".json") and f != "_manifest.json"]
                )
        else:
            talk_files = sorted(
                [f for f in os.listdir(talk_dir) if f.endswith(".json") and f != "_manifest.json"]
            )

        for tf in talk_files:
            talk_path = talk_dir / tf
            if talk_path.exists():
                lines.append(process_talk_file(talk_path))

    # Expose 文件
    expose_file = EXPOSE_FILES.get(loop_num, "")
    if expose_file:
        expose_path = EXPOSE_DIR / expose_file
        if expose_path.exists():
            lines.append(process_expose_file(expose_path))

    return "\n".join(lines)


def main():
    print("=== EPI02 JSON → MD 提取 ===\n")

    for loop_num in range(1, 7):
        md_content = generate_loop_md(loop_num)
        output_path = OUTPUT_DIR / f"Loop{loop_num}_对话草稿.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 统计
        talk_dir = TALK_DIR / f"loop{loop_num}"
        talk_count = len([f for f in os.listdir(talk_dir) if f.endswith(".json") and f != "_manifest.json"]) if talk_dir.exists() else 0
        expose_file = EXPOSE_FILES.get(loop_num, "")
        has_expose = (EXPOSE_DIR / expose_file).exists() if expose_file else False

        print(f"Loop {loop_num}: {talk_count} Talk + {'1 Expose' if has_expose else '0 Expose'} → {output_path.name}")

    print(f"\n完成！文件输出到: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
