"""
证据表转换工具
将 evidences.yaml 转换为 ItemStaticData.xlsx (Luban 格式)
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
    'var': ['id', 'cnName', 'enName', 'itemType', 'canCollected', 'canAnalyzed', 'canCombined',
            'combineParameter0', 'combineParameter1',
            'cnDescribe1', 'cnDescribe2', 'cnDescribe3',
            'enDescribe1', 'enDescribe2', 'enDescribe3',
            'path1', 'path2', 'path3', 'parameter'],
    'type': ['string', 'string', 'string', 'string', 'int', 'int', 'int',
             'string', 'string',
             'string', 'string', 'string',
             'string', 'string', 'string',
             'string', 'string', 'string', 'string'],
    'desc': ['物品ID', '中文名', '英文名', '物品类型', '可收集(1是0否)', '可分析(1是0否)', '可合并(1是0否)',
             '合并参数0', '合并参数1',
             '中文描述1', '中文描述2', '中文描述3',
             '英文描述1', '英文描述2', '英文描述3',
             '资源路径1', '资源路径2', '资源路径3', '事件参数'],
}


def load_yaml(path: Path) -> dict:
    """加载 YAML 文件"""
    if not path.exists():
        print(f"[WARN] 文件不存在: {path}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def convert_evidence(ev_id: str, ev_data: dict) -> dict:
    """将单个证据转换为配置表记录"""
    ev_type = ev_data.get('type', 'item')
    asset_id = ev_data.get('asset_id', '')
    analysis = ev_data.get('analysis', {})
    desc = ev_data.get('description', {})
    desc_en = ev_data.get('description_en', {})

    # 处理描述字段
    initial_desc = desc.get('initial', '') if isinstance(desc, dict) else str(desc)
    brief_desc = desc.get('brief', initial_desc) if isinstance(desc, dict) else ''
    analysis_desc = analysis.get('result_description', '') if isinstance(analysis, dict) else ''

    # 英文描述
    initial_desc_en = desc_en.get('initial', '') if isinstance(desc_en, dict) else ''
    brief_desc_en = desc_en.get('brief', '') if isinstance(desc_en, dict) else ''
    analysis_desc_en = analysis.get('result_description_en', '') if isinstance(analysis, dict) else ''

    return {
        'id': ev_id,
        'cnName': ev_data.get('name', ''),
        'enName': ev_data.get('name_en', ''),
        'itemType': ev_type,
        # 推导规则：item/clue 可收集
        'canCollected': 1 if ev_type in ['item', 'clue'] else 0,
        # 推导规则：有 analysis.required=true 可分析
        'canAnalyzed': 1 if analysis.get('required') else 0,
        'canCombined': 0,  # 默认不可合并
        'combineParameter0': '',
        'combineParameter1': '',
        'cnDescribe1': initial_desc,
        'cnDescribe2': brief_desc,
        'cnDescribe3': analysis_desc,
        'enDescribe1': initial_desc_en,
        'enDescribe2': brief_desc_en,
        'enDescribe3': analysis_desc_en,
        # 推导规则：path1 = asset_id + _big, path2 = asset_id
        'path1': f"{asset_id}_big" if asset_id else '',
        'path2': asset_id,
        'path3': '',
        'parameter': '',
    }


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
    print("证据表转换工具")
    print("=" * 50)

    # 加载所有 Unit 的证据数据
    all_records = []

    for unit_dir in sorted(PREVIEW_DATA.glob("Unit*")):
        evidences_file = unit_dir / "master" / "evidences.yaml"
        if not evidences_file.exists():
            continue

        print(f"\n📂 处理 {unit_dir.name}...")
        data = load_yaml(evidences_file)
        evidences = data.get('evidences', {})

        # 处理空列表或非字典情况
        if not evidences or not isinstance(evidences, dict):
            print(f"   ⚠️ 无证据数据或格式不正确，跳过")
            continue

        for ev_id, ev_data in sorted(evidences.items()):
            record = convert_evidence(ev_id, ev_data)
            all_records.append(record)

        print(f"   ✅ 加载 {len(evidences)} 条证据")

    # 保存 Excel
    print("\n📝 生成配置表...")
    save_excel(all_records, "ItemStaticData")

    print("\n" + "=" * 50)
    print(f"✅ 转换完成！共 {len(all_records)} 条记录")
    print("=" * 50)


if __name__ == '__main__':
    main()
