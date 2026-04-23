"""
NPC表转换工具
将 npcs.yaml 转换为 NPCStaticData.xlsx (Luban 格式)
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import yaml
from pathlib import Path
from openpyxl import Workbook

# 路径配置
PREVIEW_DATA = Path(r"D:\NDC_project\Preview\data")
OUTPUT_DIR = Path(r"D:\NDC_project\story")

# 表头配置（Luban 格式）
COLUMNS = {
    'var': ['id', 'cnName', 'enName', 'role', 'path1', 'path2', 'path3',
            'TestimonyCount', 'cnTestimony', 'enTestimony',
            'cnDescribe', 'enDescribe', 'infoCount',
            'info1', 'info2', 'info3', 'info4', 'info5', 'info6',
            'ifExposeInfo1', 'cnNewInfo1', 'enNewInfo1',
            'ifExposeInfo2', 'cnNewInfo2', 'enNewInfo2',
            'npcPosX', 'npcPosY', 'npcRelation', 'npcRelationParaCn', 'npcRelationParaEn'],
    'type': ['string', 'string', 'string', 'string', 'string', 'string', 'string',
             'int', 'string', 'string',
             'string', 'string', 'int',
             'string', 'string', 'string', 'string', 'string', 'string',
             'int', 'string', 'string',
             'int', 'string', 'string',
             'float', 'float', 'string', 'string', 'string'],
    'desc': ['NPC ID', '中文名', '英文名', '角色类型', '资源路径1', '资源路径2', '资源路径3',
             '证词数量', '中文证词', '英文证词',
             '中文描述', '英文描述', '信息数量',
             '人物信息1', '人物信息2', '人物信息3', '人物信息4', '人物信息5', '人物信息6',
             '指证info编号1', '指证后中文1', '指证后英文1',
             '指证info编号2', '指证后中文2', '指证后英文2',
             '关系图X坐标', '关系图Y坐标', '关联NPC', '关系描述(中)', '关系描述(英)'],
}


def load_yaml(path: Path) -> dict:
    """加载 YAML 文件"""
    if not path.exists():
        print(f"[WARN] 文件不存在: {path}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def load_testimonies(unit_dir: Path) -> dict:
    """从 evidences.yaml 加载证词（type: note）"""
    evidences_file = unit_dir / "master" / "evidences.yaml"
    if not evidences_file.exists():
        return {}

    data = load_yaml(evidences_file)
    evidences = data.get('evidences', {})

    # 处理 evidences 为列表或空的情况
    if not evidences or isinstance(evidences, list):
        return {}

    # 按 NPC 名称关键词分类证词
    npc_keywords = {
        'NPC103': ['Rosa'],
        'NPC104': ['Morrison'],
        'NPC105': ['Tommy'],
        'NPC106': ['Vivian'],
        'NPC107': ['James'],
        'NPC108': ['Anna'],
        'NPC110': ['Mrs. Morrison', 'Morrison夫人'],
    }

    testimonies = {}  # {npc_id: [(cn_text, en_text), ...]}

    for ev_id, ev_data in evidences.items():
        if ev_data.get('type') != 'note':
            continue

        name = ev_data.get('name', '')
        desc = ev_data.get('description', {})
        cn_text = desc.get('initial', '') if isinstance(desc, dict) else str(desc)

        desc_en = ev_data.get('description_en', {})
        en_text = desc_en.get('initial', '') if isinstance(desc_en, dict) else ''

        # 根据证据名称匹配 NPC
        for npc_id, keywords in npc_keywords.items():
            for keyword in keywords:
                if keyword in name:
                    if npc_id not in testimonies:
                        testimonies[npc_id] = []
                    testimonies[npc_id].append((cn_text, en_text))
                    break

    return testimonies


def convert_npc(npc_id: str, npc_data: dict, testimonies: dict) -> dict:
    """将单个 NPC 转换为配置表记录"""
    name = npc_data.get('name', '')
    info_list = npc_data.get('info', [])

    # 处理 info 字段
    info_records = {}
    expose_info = []  # [(id, text, expose_truth, text_en, expose_truth_en), ...]

    for item in info_list:
        if isinstance(item, dict):
            idx = item.get('id', 0)
            text = item.get('text', '')
            text_en = item.get('text_en', '')
            info_records[idx] = f"{text}/{text_en}"

            # 检查是否有指证真相
            if 'expose_truth' in item:
                expose_info.append((
                    idx,
                    item.get('text', ''),
                    item.get('expose_truth', ''),
                    item.get('text_en', ''),
                    item.get('expose_truth_en', '')
                ))

    # 处理证词
    npc_testimonies = testimonies.get(npc_id, [])
    cn_testimonies = [t[0] for t in npc_testimonies]
    en_testimonies = [t[1] for t in npc_testimonies]

    record = {
        'id': npc_id,
        'cnName': npc_data.get('name_cn', ''),
        'enName': name,
        'role': npc_data.get('role', ''),
        # path1 = 英文名_big, path2 = 英文名
        'path1': f"{name}_big" if name else '',
        'path2': name,
        'path3': '',
        # 证词
        'TestimonyCount': len(npc_testimonies),
        'cnTestimony': '/'.join(cn_testimonies),
        'enTestimony': '/'.join(en_testimonies),
        # 描述
        'cnDescribe': npc_data.get('description', ''),
        'enDescribe': npc_data.get('description_en', ''),
        # info 数量
        'infoCount': len(info_list),
        # info 1-6
        'info1': info_records.get(1, ''),
        'info2': info_records.get(2, ''),
        'info3': info_records.get(3, ''),
        'info4': info_records.get(4, ''),
        'info5': info_records.get(5, ''),
        'info6': info_records.get(6, ''),
        # 指证字段
        'ifExposeInfo1': expose_info[0][0] if len(expose_info) > 0 else '',
        'cnNewInfo1': f"{expose_info[0][1]}/{expose_info[0][2]}" if len(expose_info) > 0 else '',
        'enNewInfo1': f"{expose_info[0][3]}/{expose_info[0][4]}" if len(expose_info) > 0 else '',
        'ifExposeInfo2': expose_info[1][0] if len(expose_info) > 1 else '',
        'cnNewInfo2': f"{expose_info[1][1]}/{expose_info[1][2]}" if len(expose_info) > 1 else '',
        'enNewInfo2': f"{expose_info[1][3]}/{expose_info[1][4]}" if len(expose_info) > 1 else '',
        # 关系图
        'npcPosX': npc_data.get('npcPosX', ''),
        'npcPosY': npc_data.get('npcPosY', ''),
        'npcRelation': npc_data.get('npcRelation', ''),
        'npcRelationParaCn': npc_data.get('npcRelationParaCn', ''),
        'npcRelationParaEn': npc_data.get('npcRelationParaEn', ''),
    }

    return record


def save_excel(records: list, filename: str):
    """保存为 Luban 格式 Excel"""
    if not records:
        print(f"[WARN] {filename}: 无数据，跳过")
        return None

    wb = Workbook()
    ws = wb.active

    # 第1行：##var + 字段名
    ws.append(['##var'] + COLUMNS['var'])
    # 第2行：##type + 类型定义
    ws.append(['##type'] + COLUMNS['type'])
    # 第3行：## + 字段描述
    ws.append(['##'] + COLUMNS['desc'])

    # 第4行起：数据（第一列留空）
    for record in records:
        row = [''] + [record.get(field, '') for field in COLUMNS['var']]
        ws.append(row)

    # 保存
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{filename}.xlsx"
    wb.save(path)

    print(f"[OK] {path.name}: {len(records)} 条记录")
    return path


def main():
    print("=" * 50)
    print("NPC表转换工具")
    print("=" * 50)

    # 加载所有 Unit 的 NPC 数据
    all_records = []

    for unit_dir in sorted(PREVIEW_DATA.glob("Unit*")):
        npcs_file = unit_dir / "master" / "npcs.yaml"
        if not npcs_file.exists():
            continue

        print(f"\n📂 处理 {unit_dir.name}...")

        # 加载 NPC 数据
        data = load_yaml(npcs_file)
        npcs = data.get('npcs', {})

        if not npcs or not isinstance(npcs, dict):
            print(f"   ⚠️ 无NPC数据或格式不正确，跳过")
            continue

        # 加载证词数据
        testimonies = load_testimonies(unit_dir)
        print(f"   📝 加载 {sum(len(v) for v in testimonies.values())} 条证词")

        # 转换 NPC
        for npc_id, npc_data in sorted(npcs.items()):
            record = convert_npc(npc_id, npc_data, testimonies)
            all_records.append(record)

        print(f"   ✅ 加载 {len(npcs)} 个NPC")

    # 保存 Excel
    print("\n📝 生成配置表...")
    save_excel(all_records, "NPCStaticData")

    print("\n" + "=" * 50)
    print(f"✅ 转换完成！共 {len(all_records)} 条记录")
    print("=" * 50)


if __name__ == '__main__':
    main()
