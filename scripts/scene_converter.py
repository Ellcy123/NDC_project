"""
场景表转换工具
将 scenes.yaml + loop配置 转换为 SceneConfig.xlsx (Luban 格式)
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
    'var': ['sceneId', 'sceneName', 'sceneNameEn', 'sceneType',
            'backgroundImage', 'backgroundMusic', 'ambientSound',
            'unlockCondition', 'npcsPresent', 'note'],
    'type': ['string', 'string', 'string', 'string',
             'string', 'string', 'string',
             'string', 'string', 'string'],
    'desc': ['场景ID', '中文名', '英文名', '场景类型',
             '背景图片', '背景音乐', '环境音效',
             '解锁条件', '场景NPC', '备注'],
}


def load_yaml(path: Path) -> dict:
    """加载 YAML 文件"""
    if not path.exists():
        print(f"[WARN] 文件不存在: {path}")
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def convert_scene_id(base_id: str, loop_num: int) -> str:
    """将基础场景ID转换为循环场景ID
    SC1001 + loop1 → SC1101
    SC1017 + loop2 → SC1217
    """
    if not base_id or len(base_id) < 6:
        return base_id

    chapter = base_id[2]  # '1'
    # 取后两位作为场景序号
    scene_num = base_id[-2:]  # '01' from SC1001, '17' from SC1017

    return f"SC{chapter}{loop_num}{scene_num}"


def get_scene_type(loop_type: str) -> str:
    """转换场景类型"""
    type_map = {
        'search': 'search',
        'npc': 'dialogue',
        'locked': 'lock',
    }
    return type_map.get(loop_type, '')


def extract_scenes_from_loop(loop_data: dict, loop_num: int, npcs_data: dict) -> list:
    """从单个循环配置中提取所有场景"""
    scenes = []  # [(scene_id, type, npc, note), ...]

    # 1. 开篇场景 opening.scenes
    opening = loop_data.get('opening', {})
    for scene_entry in opening.get('scenes', []):
        scene_id = scene_entry.get('scene_id', '')
        dialog_file = scene_entry.get('dialog_file', '')
        note = f"opening: {dialog_file}" if dialog_file else "opening"
        scenes.append((scene_id, 'dialogue', '', note))

    # 2. 自由探索场景 free_phase.scenes
    free_phase = loop_data.get('free_phase', {})
    for scene_entry in free_phase.get('scenes', []):
        scene_id = scene_entry.get('scene', '')
        scene_type = scene_entry.get('type', '')
        npc_id = scene_entry.get('npc', '')

        # 构建备注
        if scene_type == 'search':
            evidences = scene_entry.get('evidences', [])
            ev_ids = [ev.get('id', '') for ev in evidences if isinstance(ev, dict)]
            note = f"free_phase: 搜索 {','.join(ev_ids)}" if ev_ids else "free_phase: 搜索"
        elif scene_type == 'npc':
            # 获取NPC名称
            npc_name = ''
            if npc_id and npc_id in npcs_data:
                npc_name = npcs_data[npc_id].get('name_cn', npcs_data[npc_id].get('name', ''))
            note = f"free_phase: 与{npc_name}对话" if npc_name else f"free_phase: 与{npc_id}对话"
        elif scene_type == 'locked':
            note = scene_entry.get('note', 'free_phase: 本循环不可进入')
        else:
            note = scene_entry.get('note', 'free_phase')

        scenes.append((scene_id, get_scene_type(scene_type), npc_id, note))

    # 3. 指证场景 expose.scene
    expose = loop_data.get('expose', {})
    if expose.get('scene'):
        scene_id = expose.get('scene')
        target = expose.get('target', '')
        target_name = expose.get('target_name', target)
        note = f"expose: 指证{target_name}"
        scenes.append((scene_id, 'dialogue', target, note))

    # 4. 结尾场景 ending.scene
    ending = loop_data.get('ending', {})
    if ending.get('scene'):
        scene_id = ending.get('scene')
        transition_to = ending.get('transition_to', '')
        note = f"ending: 过渡到{transition_to}" if transition_to else "ending"
        scenes.append((scene_id, 'dialogue', '', note))

    return scenes


def process_unit(unit_dir: Path) -> list:
    """处理单个Unit的所有场景"""
    records = []

    # 加载基础场景数据
    scenes_file = unit_dir / "master" / "scenes.yaml"
    scenes_data = load_yaml(scenes_file).get('scenes', {})
    if not scenes_data:
        print(f"   [WARN] 无场景数据: {scenes_file}")
        return []

    # 加载NPC数据（用于获取NPC名称）
    npcs_file = unit_dir / "master" / "npcs.yaml"
    npcs_data = load_yaml(npcs_file).get('npcs', {})

    # 遍历所有循环配置
    loops_dir = unit_dir / "loops"
    if not loops_dir.exists():
        print(f"   [WARN] 无loops目录: {loops_dir}")
        return []

    for loop_file in sorted(loops_dir.glob("loop*.yaml")):
        loop_data = load_yaml(loop_file)
        loop_num = loop_data.get('loop_number', 0)

        if not loop_num:
            # 尝试从文件名提取
            try:
                loop_num = int(loop_file.stem.replace('loop', ''))
            except:
                continue

        print(f"   📂 处理 {loop_file.name} (循环{loop_num})...")

        # 提取该循环的所有场景
        loop_scenes = extract_scenes_from_loop(loop_data, loop_num, npcs_data)

        # 跟踪场景出现次数（用于处理重复）
        scene_count = {}

        for base_id, scene_type, npc_id, note in loop_scenes:
            if not base_id:
                continue

            # 转换场景ID
            new_id = convert_scene_id(base_id, loop_num)

            # 处理重复场景
            if new_id in scene_count:
                scene_count[new_id] += 1
                suffix_idx = scene_count[new_id] - 1
                suffix = chr(ord('A') + suffix_idx - 1)  # _A, _B, _C...
                new_id = f"{new_id}_{suffix}"
            else:
                scene_count[new_id] = 1

            # 从基础场景获取信息
            base_scene = scenes_data.get(base_id, {})
            if not base_scene:
                print(f"      [WARN] 未找到基础场景: {base_id}")
                continue

            record = {
                'sceneId': new_id,
                'sceneName': base_scene.get('name', ''),
                'sceneNameEn': base_scene.get('name_en', ''),
                'sceneType': scene_type,
                'backgroundImage': base_scene.get('asset_id', ''),
                'backgroundMusic': '',
                'ambientSound': '',
                'unlockCondition': '',
                'npcsPresent': npc_id,
                'note': note,
            }
            records.append(record)

        print(f"      ✅ 提取 {len(loop_scenes)} 个场景")

    return records


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
    print("场景表转换工具")
    print("=" * 50)

    all_records = []

    for unit_dir in sorted(PREVIEW_DATA.glob("Unit*")):
        print(f"\n📂 处理 {unit_dir.name}...")

        records = process_unit(unit_dir)
        all_records.extend(records)

        print(f"   ✅ 共 {len(records)} 条场景记录")

    # 保存 Excel
    print("\n📝 生成配置表...")
    save_excel(all_records, "SceneConfig")

    print("\n" + "=" * 50)
    print(f"✅ 转换完成！共 {len(all_records)} 条记录")
    print("=" * 50)


if __name__ == '__main__':
    main()
