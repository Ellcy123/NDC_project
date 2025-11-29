# -*- coding: utf-8 -*-
"""
从evidences.yaml中提取note类型证词，生成Testimony表Excel
按照Testimony表配置规则.md格式
"""

import yaml
import pandas as pd
import re
from pathlib import Path

# 路径配置
EVIDENCES_FILE = Path(r"D:\NDC_project\Preview\data\master\evidences.yaml")
NPCS_FILE = Path(r"D:\NDC_project\Preview\data\master\npcs.yaml")
OUTPUT_FILE = Path(r"D:\NDC_project\story\Testimony_from_data.xlsx")

def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_speaker_from_name(name):
    """从证词名称中提取说话者名字"""
    # 例如: "Tommy时间证词" -> "Tommy"
    # "Morrison夫人时间证词" -> "Morrison夫人"
    # "Rosa关于音乐音量的证词" -> "Rosa"
    patterns = [
        r'^(.+?)时间证词',
        r'^(.+?)关于.+的证词',
        r'^(.+?)目击.*证词',
        r'^(.+?)的.+证词',
        r'^(.+?)证词',
    ]
    for pattern in patterns:
        match = re.match(pattern, name)
        if match:
            return match.group(1)
    return name

def get_npc_names():
    """获取NPC名称映射"""
    data = load_yaml(NPCS_FILE)
    npcs = data.get('npcs', {})

    name_map = {}
    for npc_id, npc_data in npcs.items():
        cn_name = npc_data.get('name_cn', '')
        en_name = npc_data.get('name', '')
        # 提取简短名称
        short_cn = cn_name.split('·')[0] if '·' in cn_name else cn_name
        name_map[short_cn] = en_name
        name_map[en_name.split()[0]] = en_name  # "Rosa Martinez" -> "Rosa" -> "Rosa Martinez"

    return name_map

def convert_notes_to_testimony():
    """
    从evidences.yaml提取note类型，转换为Testimony表格式
    """
    evidences_data = load_yaml(EVIDENCES_FILE)
    evidences = evidences_data.get('evidences', {})
    npc_names = get_npc_names()

    rows = []
    evidence_count = {}  # 记录每个说话者的证词序号

    for ev_id, ev_data in evidences.items():
        if ev_data.get('type') != 'note':
            continue

        name = ev_data.get('name', '')
        name_en = ev_data.get('name_en', '')
        description = ev_data.get('description', {})
        cn_words = description.get('initial', '')

        # 提取说话者名字
        speaker_cn = extract_speaker_from_name(name)

        # 尝试匹配英文名
        speaker_en = ''
        for cn, en in npc_names.items():
            if cn in speaker_cn or speaker_cn in cn:
                speaker_en = en
                break
        if not speaker_en:
            # 从英文证词名提取
            speaker_en = name_en.replace("'s", "").replace(" Time Testimony", "").replace(" Testimony", "").strip()
            parts = speaker_en.split()
            if parts:
                speaker_en = parts[0]

        # 计算证词序号
        if speaker_cn not in evidence_count:
            evidence_count[speaker_cn] = 0
        evidence_count[speaker_cn] += 1

        row = {
            'id': ev_id,  # 使用证据ID作为临时ID
            'speakerName': speaker_cn,
            'speakerNameEn': speaker_en,
            'cnWords': cn_words,
            'enWords': '',  # 英文内容需要后续补充
            'ifIgnore': 0,
            'ifEvidence': evidence_count[speaker_cn],
            'cnExracted': cn_words,  # 重复配置
            'enExracted': '',
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # 按照配置表规则的字段顺序
    columns_order = ['id', 'speakerName', 'speakerNameEn',
                     'cnWords', 'enWords',
                     'ifIgnore', 'ifEvidence',
                     'cnExracted', 'enExracted']
    df = df[columns_order]

    df.to_excel(OUTPUT_FILE, index=False)
    print(f"已生成: {OUTPUT_FILE}")
    print(f"  - 共 {len(rows)} 条证词数据（从evidences.yaml的note类型提取）")

    # 打印统计
    print("\n证词统计：")
    for speaker, count in evidence_count.items():
        print(f"  - {speaker}: {count}条证词")

    return df

def main():
    print("=" * 60)
    print("evidences.yaml (note类型) -> Testimony Excel 转换工具")
    print("按照Testimony表配置规则.md格式生成")
    print("=" * 60)

    convert_notes_to_testimony()

    print("\n转换完成！")

if __name__ == "__main__":
    main()
