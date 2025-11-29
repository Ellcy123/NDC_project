# -*- coding: utf-8 -*-
"""
从Preview/data目录的yaml文件生成配置表Excel
按照配置表规则文档格式生成：
- npcs.yaml -> NPCStaticData.xlsx
- evidences.yaml -> ItemStaticData.xlsx
- scenes.yaml -> SceneConfig.xlsx
"""

import yaml
import pandas as pd
from pathlib import Path

# 路径配置
DATA_DIR = Path(r"D:\NDC_project\Preview\data\master")
OUTPUT_DIR = Path(r"D:\NDC_project\story")

def load_yaml(file_path):
    """加载YAML文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def convert_npcs():
    """
    转换NPC数据到配置表格式
    按照NPC表配置规则.md的字段：
    id, cnName, enName, role, path1, path2, path3,
    TestimonyCount, cnTestimony, enTestimony,
    cnDescribe, enDescribe, ifExpose, cnNewDescribe, enNewDescribe
    """
    data = load_yaml(DATA_DIR / "npcs.yaml")
    npcs = data.get('npcs', {})

    rows = []
    for npc_id, npc_data in npcs.items():
        # 提取info中的描述信息，用 / 分隔
        info = npc_data.get('info', {})
        cn_describe_list = [npc_data.get('description', '')]

        # 按循环顺序收集info
        for loop_key in ['loop1', 'loop2', 'loop3', 'loop4', 'loop5', 'loop6']:
            if loop_key in info:
                loop_info = info[loop_key]
                if isinstance(loop_info, list):
                    cn_describe_list.extend(loop_info)

        cn_describe = '/'.join(cn_describe_list) if cn_describe_list else ''

        row = {
            'id': npc_id,
            'cnName': npc_data.get('name_cn', ''),
            'enName': npc_data.get('name', ''),
            'role': npc_data.get('role', ''),
            'path1': '',
            'path2': '',
            'path3': '',
            'TestimonyCount': 0,
            'cnTestimony': '',
            'enTestimony': '',
            'cnDescribe': cn_describe,
            'enDescribe': '',  # 需要后续补充英文
            'ifExpose': '',
            'cnNewDescribe': '',
            'enNewDescribe': '',
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # 按照配置表规则的字段顺序
    columns_order = ['id', 'cnName', 'enName', 'role', 'path1', 'path2', 'path3',
                     'TestimonyCount', 'cnTestimony', 'enTestimony',
                     'cnDescribe', 'enDescribe', 'ifExpose', 'cnNewDescribe', 'enNewDescribe']
    df = df[columns_order]

    output_path = OUTPUT_DIR / "NPCStaticData_updated.xlsx"
    df.to_excel(output_path, index=False)
    print(f"已生成: {output_path}")
    print(f"  - 共 {len(rows)} 条NPC数据")
    return df

def convert_evidences():
    """
    转换证据数据到配置表格式（ItemStaticData）
    按照Item表配置规则.md的字段：
    id, cnName, enName, itemType, canCollected, canAnalyzed, canCombined,
    combineParameter0, combineParameter1,
    cnDescribe1, cnDescribe2, cnDescribe3,
    enDescribe1, enDescribe2, enDescribe3,
    path1, path2, path3, parameter
    """
    data = load_yaml(DATA_DIR / "evidences.yaml")
    evidences = data.get('evidences', {})

    rows = []
    for ev_id, ev_data in evidences.items():
        # 物品类型
        ev_type = ev_data.get('type', 'item')

        # 是否可收集（envir类型不可收集）
        can_collected = ev_type != 'envir'

        # 分析相关
        analysis = ev_data.get('analysis', {})
        can_analyzed = analysis.get('required', False)

        # 描述
        description = ev_data.get('description', {})
        cn_describe1 = description.get('initial', '')
        cn_describe2 = analysis.get('result_description', '') if can_analyzed else ''

        row = {
            'id': ev_id,
            'cnName': ev_data.get('name', ''),
            'enName': ev_data.get('name_en', ''),
            'itemType': ev_type,
            'canCollected': can_collected,
            'canAnalyzed': can_analyzed,
            'canCombined': False,
            'combineParameter0': '',
            'combineParameter1': '',
            'cnDescribe1': cn_describe1,
            'cnDescribe2': cn_describe2,
            'cnDescribe3': '',
            'enDescribe1': '',  # 需要后续补充英文
            'enDescribe2': '',
            'enDescribe3': '',
            'path1': ev_data.get('asset_id', ''),
            'path2': '',
            'path3': '',
            'parameter': '',
        }
        rows.append(row)

    df = pd.DataFrame(rows)

    # 按照配置表规则的字段顺序
    columns_order = ['id', 'cnName', 'enName', 'itemType',
                     'canCollected', 'canAnalyzed', 'canCombined',
                     'combineParameter0', 'combineParameter1',
                     'cnDescribe1', 'cnDescribe2', 'cnDescribe3',
                     'enDescribe1', 'enDescribe2', 'enDescribe3',
                     'path1', 'path2', 'path3', 'parameter']
    df = df[columns_order]

    output_path = OUTPUT_DIR / "ItemStaticData_new.xlsx"
    df.to_excel(output_path, index=False)
    print(f"已生成: {output_path}")
    print(f"  - 共 {len(rows)} 条物品数据")
    return df

def convert_scenes():
    """
    转换场景数据到配置表格式（SceneConfig）
    按照Scene表配置规则.md的字段：
    sceneId, sectionId, sceneName, sceneNameEn, chapterId, sceneType,
    backgroundImage, backgroundMusic, ambientSound, unlockCondition, npcsPresent, 备注

    注意：scenes.yaml中的ID是基础场景ID（SC1001），
    需要为每个循环生成对应的场景配置（SC1101, SC1201等）
    """
    data = load_yaml(DATA_DIR / "scenes.yaml")
    scenes = data.get('scenes', {})

    rows = []

    # 为每个基础场景生成6个循环的配置
    for base_scene_id, scene_data in scenes.items():
        # 从SC1001格式中提取章节和场景序号
        # SC1001 -> 章节=1, 场景序号=001 -> 简化为01
        chapter = base_scene_id[2]  # '1'
        scene_num = base_scene_id[3:5]  # '01' (取前两位)

        # 生成6个循环的场景配置
        for loop in range(1, 7):
            scene_id = f"SC{chapter}{loop}{scene_num}"
            section_id = f"SEC{loop:02d}"

            row = {
                'sceneId': scene_id,
                'sectionId': section_id,
                'sceneName': scene_data.get('name', ''),
                'sceneNameEn': scene_data.get('name_en', ''),
                'chapterId': f"CH{int(chapter):03d}",
                'sceneType': 'crime',  # 默认为搜证场景，需后续调整
                'backgroundImage': f"Art/Scenes/{scene_data.get('asset_id', '')}.png",
                'backgroundMusic': '',
                'ambientSound': '',
                'unlockCondition': '',
                'npcsPresent': '',
                '备注': scene_data.get('description', ''),
            }
            rows.append(row)

    df = pd.DataFrame(rows)

    # 按照配置表规则的字段顺序
    columns_order = ['sceneId', 'sectionId', 'sceneName', 'sceneNameEn', 'chapterId',
                     'sceneType', 'backgroundImage', 'backgroundMusic', 'ambientSound',
                     'unlockCondition', 'npcsPresent', '备注']
    df = df[columns_order]

    # 按sceneId排序
    df = df.sort_values('sceneId').reset_index(drop=True)

    output_path = OUTPUT_DIR / "SceneConfig_new.xlsx"
    df.to_excel(output_path, index=False)
    print(f"已生成: {output_path}")
    print(f"  - 共 {len(rows)} 条场景数据（{len(scenes)}个基础场景 x 6循环）")
    return df

def main():
    print("=" * 60)
    print("Preview数据 -> 配置表Excel 转换工具")
    print("按照配置表规则文档格式生成")
    print("=" * 60)

    # 确保输出目录存在
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 转换各表
    print("\n[1/3] 转换NPC数据（按NPC表配置规则.md）...")
    npc_df = convert_npcs()

    print("\n[2/3] 转换物品/证据数据（按Item表配置规则.md）...")
    item_df = convert_evidences()

    print("\n[3/3] 转换场景数据（按Scene表配置规则.md）...")
    scene_df = convert_scenes()

    print("\n" + "=" * 60)
    print("转换完成！")
    print(f"输出目录: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
