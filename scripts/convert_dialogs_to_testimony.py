# -*- coding: utf-8 -*-
"""
从Preview/data/Unit1/dialogs目录的对话文件生成Testimony表Excel
按照Testimony表配置规则.md和Talk表配置规则.md格式
"""

import yaml
import pandas as pd
from pathlib import Path

# 路径配置
DIALOGS_DIR = Path(r"D:\NDC_project\Preview\data\Unit1\dialogs")
NPCS_FILE = Path(r"D:\NDC_project\Preview\data\master\npcs.yaml")
OUTPUT_FILE = Path(r"D:\NDC_project\story\Testimony_from_dialogs.xlsx")

# 角色编号映射（根据Talk表配置规则）
SPEAKER_NUM = {
    'NPC101': 1,  # Zack Brennan
    'NPC102': 2,  # Emma O'Malley
    'NPC103': 3,  # Rosa Martinez
    'NPC104': 4,  # Morrison
    'NPC105': 5,  # Tommy
    'NPC106': 6,  # Vivian Rose
    'NPC107': 7,  # Jimmy
    'NPC108': 8,  # Anna
    'NPC109': 9,  # Webb
    'NPC110': 10, # Mrs. Morrison
}

def load_yaml(file_path):
    """加载YAML文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"    [警告] YAML解析错误: {file_path.name} - {e}")
        return None

def get_npc_names():
    """获取NPC名称映射"""
    data = load_yaml(NPCS_FILE)
    npcs = data.get('npcs', {})

    name_map = {}
    for npc_id, npc_data in npcs.items():
        name_map[npc_id] = {
            'cn': npc_data.get('name_cn', '').split('·')[0],  # 取短名
            'en': npc_data.get('name', '')
        }
    return name_map

def parse_dialog_file(file_path, npc_names, dialog_segment_counter):
    """
    解析单个对话文件，返回证词列表

    Args:
        file_path: 对话文件路径
        npc_names: NPC名称映射
        dialog_segment_counter: 对话段落计数器（按角色）

    Returns:
        rows: 证词行列表
    """
    data = load_yaml(file_path)
    if not data:
        return []

    loop = data.get('loop', 1)
    npc = data.get('npc', '')

    rows = []
    line_counter = {}  # 每个角色在当前文件中的句子计数

    # 遍历所有section
    for section_key, section_data in data.items():
        if not isinstance(section_data, dict) or 'lines' not in section_data:
            continue

        lines = section_data.get('lines', [])
        for line in lines:
            speaker = line.get('speaker', '')
            text = line.get('text', '')
            emotion = line.get('emotion', '')

            if not speaker or not text:
                continue

            # 获取角色编号
            speaker_num = SPEAKER_NUM.get(speaker, 99)

            # 获取对话段落号
            if speaker not in dialog_segment_counter:
                dialog_segment_counter[speaker] = 1
            segment = dialog_segment_counter[speaker]

            # 获取句子序号
            if speaker not in line_counter:
                line_counter[speaker] = 0
            line_counter[speaker] += 1
            sentence = line_counter[speaker]

            # 生成Talk表ID: NNXXYYY
            talk_id = int(f"{speaker_num}{segment:03d}{sentence:03d}")

            # 获取说话者名称
            names = npc_names.get(speaker, {'cn': speaker, 'en': speaker})
            speaker_cn = names['cn']
            speaker_en = names['en']

            row = {
                'id': talk_id,
                'speakerName': speaker_cn,
                'speakerNameEn': speaker_en,
                'cnWords': text,
                'enWords': '',  # 需要后续补充英文
                'ifIgnore': 0,
                'ifEvidence': 0,  # 默认不是证据，需要后续标记
                'cnExracted': '',
                'enExracted': '',
                '_loop': loop,
                '_file': file_path.name,
            }
            rows.append(row)

    return rows

def convert_dialogs_to_testimony():
    """从对话文件生成Testimony表"""
    npc_names = get_npc_names()

    all_rows = []
    dialog_segment_counter = {}  # 全局对话段落计数器

    # 按循环顺序处理对话文件
    for loop_num in range(1, 7):
        loop_dir = DIALOGS_DIR / f"loop{loop_num}"
        if not loop_dir.exists():
            continue

        print(f"处理 loop{loop_num}...")

        # 获取该循环的所有对话文件
        for yaml_file in sorted(loop_dir.glob("*.yaml")):
            print(f"  - {yaml_file.name}")

            # 更新段落计数器（每个文件是一个新的对话段落）
            data = load_yaml(yaml_file)
            if data and 'npc' in data:
                main_npc = data['npc']
                if main_npc not in dialog_segment_counter:
                    dialog_segment_counter[main_npc] = 0
                dialog_segment_counter[main_npc] += 1

            rows = parse_dialog_file(yaml_file, npc_names, dialog_segment_counter)
            all_rows.extend(rows)

    df = pd.DataFrame(all_rows)

    # 按照配置表规则的字段顺序（去除调试字段）
    columns_order = ['id', 'speakerName', 'speakerNameEn',
                     'cnWords', 'enWords',
                     'ifIgnore', 'ifEvidence',
                     'cnExracted', 'enExracted']
    df_output = df[columns_order]

    df_output.to_excel(OUTPUT_FILE, index=False)
    print(f"\n已生成: {OUTPUT_FILE}")
    print(f"  - 共 {len(all_rows)} 条证词数据")

    # 统计
    print("\n按循环统计：")
    for loop in range(1, 7):
        count = len(df[df['_loop'] == loop])
        if count > 0:
            print(f"  - 循环{loop}: {count}条")

    return df

def main():
    print("=" * 60)
    print("Preview/dialogs -> Testimony Excel 转换工具")
    print("按照Testimony表配置规则.md格式生成")
    print("=" * 60)
    print()

    convert_dialogs_to_testimony()

    print("\n转换完成！")

if __name__ == "__main__":
    main()
