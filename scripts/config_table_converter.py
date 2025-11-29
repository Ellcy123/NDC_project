"""
配表小助手 - 数据转换脚本
将 Preview/data 数据转换为 Luban 配置表格式
"""
import sys
import io
# 修复Windows终端编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import yaml
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import shutil
from datetime import datetime

# 路径配置
PREVIEW_DATA = Path(r"D:\NDC_project\Preview\data")
STORY_OUTPUT = Path(r"D:\NDC_project\story")
UNITY_OUTPUT = Path(r"D:\NDC\Config\Datas\story")

# 确保yaml输出中文不转义
yaml.add_representer(str, lambda dumper, data: dumper.represent_scalar('tag:yaml.org,2002:str', data))


class ConfigTableConverter:
    """配置表转换器"""

    def __init__(self):
        self.npcs = {}
        self.scenes = {}
        self.evidences = {}
        self.loops = {}
        self.dialogs = {}

    def load_all_data(self):
        """加载所有数据"""
        print("📖 加载数据...")

        # 加载主数据
        self.npcs = self._load_yaml(PREVIEW_DATA / "master" / "npcs.yaml")
        self.scenes = self._load_yaml(PREVIEW_DATA / "master" / "scenes.yaml")
        self.evidences = self._load_yaml(PREVIEW_DATA / "master" / "evidences.yaml")

        # 加载循环数据
        loops_dir = PREVIEW_DATA / "Unit1" / "loops"
        if loops_dir.exists():
            for f in loops_dir.glob("loop*.yaml"):
                loop_num = f.stem.replace("loop", "")
                self.loops[loop_num] = self._load_yaml(f)

        # 加载对话数据
        dialogs_dir = PREVIEW_DATA / "Unit1" / "dialogs"
        if dialogs_dir.exists():
            for loop_dir in dialogs_dir.iterdir():
                if loop_dir.is_dir() and loop_dir.name.startswith("loop"):
                    loop_num = loop_dir.name.replace("loop", "")
                    self.dialogs[loop_num] = {}
                    for f in loop_dir.glob("*.yaml"):
                        self.dialogs[loop_num][f.stem] = self._load_yaml(f)

        print(f"  ✅ NPCs: {len(self.npcs.get('npcs', {}))}")
        print(f"  ✅ Scenes: {len(self.scenes.get('scenes', {}))}")
        print(f"  ✅ Evidences: {len(self.evidences.get('evidences', {}))}")
        print(f"  ✅ Loops: {len(self.loops)}")
        print(f"  ✅ Dialog files: {sum(len(d) for d in self.dialogs.values())}")

    def _load_yaml(self, path: Path) -> dict:
        """加载yaml文件"""
        if not path.exists():
            print(f"  [WARN] 文件不存在: {path}")
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"  [ERROR] 加载失败 {path.name}: {e}")
            return {}

    # ==================== 转换方法 ====================

    def convert_npc(self) -> List[dict]:
        """转换NPC表（完整15个字段）"""
        records = []
        npcs_data = self.npcs.get('npcs', {})

        for npc_id, npc in npcs_data.items():
            # 收集所有描述信息
            descriptions_cn = [npc.get('description', '')]
            descriptions_en = [npc.get('description_en', npc.get('description', ''))]

            # 添加各循环的info
            info = npc.get('info', {})
            for loop_key in sorted(info.keys()):
                loop_info = info[loop_key]
                if isinstance(loop_info, list):
                    descriptions_cn.extend(loop_info)

            record = {
                'id': npc_id,
                'cnName': npc.get('name_cn', ''),
                'enName': npc.get('name', ''),
                'role': npc.get('role', ''),
                'path1': '',  # 待补充
                'path2': '',  # 待补充
                'path3': '',  # 待补充
                'TestimonyCount': '',  # 待补充
                'cnTestimony': '',  # 待补充
                'enTestimony': '',  # 待补充
                'cnDescribe': '/'.join(filter(None, descriptions_cn)),
                'enDescribe': '/'.join(filter(None, descriptions_en)),
                'ifExpose': '',  # 待补充
                'cnNewDescribe': '',  # 待补充
                'enNewDescribe': '',  # 待补充
            }
            records.append(record)

        return records

    def convert_scene(self) -> List[dict]:
        """转换场景表（完整12个字段）"""
        records = []
        scenes_data = self.scenes.get('scenes', {})

        for scene_id, scene in scenes_data.items():
            record = {
                'sceneId': scene_id,
                'sectionId': '',  # 待补充
                'sceneName': scene.get('name', ''),
                'sceneNameEn': scene.get('name_en', ''),
                'chapterId': '',  # 待补充
                'sceneType': 'dialogue',  # 默认类型
                'backgroundImage': f"Art/Scenes/{scene.get('asset_id', '')}.png",
                'backgroundMusic': '',  # 待补充
                'ambientSound': '',  # 待补充
                'unlockCondition': '',  # 待补充
                'npcsPresent': '',  # 待补充
                '备注': scene.get('description', ''),
            }
            records.append(record)

        return records

    def convert_item(self) -> List[dict]:
        """转换物品表（完整19个字段）"""
        records = []
        evidences_data = self.evidences.get('evidences', {})

        for ev_id, ev in evidences_data.items():
            desc = ev.get('description', {})
            initial_desc = desc.get('initial', '') if isinstance(desc, dict) else str(desc)
            analysis = ev.get('analysis', {})
            analysis_desc = analysis.get('result_description', '') if isinstance(analysis, dict) else ''

            record = {
                'id': ev_id,
                'cnName': ev.get('name', ''),
                'enName': ev.get('name_en', ''),
                'itemType': ev.get('type', 'item'),
                'canCollected': ev.get('type') in ['item', 'clue', 'note'],
                'canAnalyzed': 'analysis' in ev,
                'canCombined': False,  # 待补充
                'combineParameter0': '',  # 待补充
                'combineParameter1': '',  # 待补充
                'cnDescribe1': initial_desc,
                'cnDescribe2': analysis_desc,
                'cnDescribe3': '',  # 待补充
                'enDescribe1': ev.get('description_en', initial_desc),
                'enDescribe2': '',  # 待补充
                'enDescribe3': '',  # 待补充
                'path1': '',  # 待补充
                'path2': '',  # 待补充
                'path3': '',  # 待补充
                'parameter': '',  # 待补充
            }
            records.append(record)

        return records

    def convert_talk(self) -> List[dict]:
        """转换对话表（完整19个字段）"""
        records = []
        talk_id_counter = {}
        npcs_data = self.npcs.get('npcs', {})

        for loop_num, loop_dialogs in sorted(self.dialogs.items()):
            for dialog_name, dialog_data in loop_dialogs.items():
                if not dialog_data:
                    continue

                # 生成基础ID: 章节(1位) + 循环(2位) + 文件序号(2位) + 行序号(2位)
                base_id = int(f"1{loop_num.zfill(2)}00")

                # 遍历对话段落
                step = 1
                for section_key, section in dialog_data.items():
                    if not isinstance(section, dict) or 'lines' not in section:
                        continue

                    for line in section['lines']:
                        speaker_id = line.get('speaker', '')
                        speaker_info = npcs_data.get(speaker_id, {})

                        record = {
                            'id': base_id + step,
                            'step': step,
                            'speakType': 2,  # 默认对话类型
                            'waitTime': 0,
                            'IdSpeaker': speaker_id,
                            'cnSpeaker': speaker_info.get('name_cn', ''),
                            'enSpeaker': speaker_info.get('name', ''),
                            'cnWords': line.get('text', ''),
                            'enWords': line.get('text_en', line.get('text', '')),
                            'next': '',  # 待补充
                            'script': '',  # 待补充
                            'ParameterStr0': '',  # 待补充
                            'ParameterStr1': '',  # 待补充
                            'ParameterStr2': '',  # 待补充
                            'ParameterInt0': '',  # 待补充
                            'ParameterInt1': '',  # 待补充
                            'ParameterInt2': '',  # 待补充
                            'imagePath': '',  # 待补充
                            'voicePath': '',  # 待补充
                        }
                        records.append(record)
                        step += 1

        return records

    def convert_testimony(self) -> List[dict]:
        """转换证词表（完整9个字段）"""
        records = []
        npcs_data = self.npcs.get('npcs', {})

        for loop_num, loop_dialogs in sorted(self.dialogs.items()):
            # 主要从 accusation.yaml 提取证词
            accusation = loop_dialogs.get('accusation', {})
            if not accusation:
                continue

            base_id = int(f"3{loop_num.zfill(2)}1001")
            step = 1

            for section_key, section in accusation.items():
                if not isinstance(section, dict) or 'lines' not in section:
                    continue

                for line in section['lines']:
                    speaker_id = line.get('speaker', '')
                    speaker_info = npcs_data.get(speaker_id, {})

                    record = {
                        'id': base_id + step - 1,
                        'speakerName': speaker_info.get('name_cn', ''),
                        'speakerNameEn': speaker_info.get('name', ''),
                        'cnWords': line.get('text', ''),
                        'enWords': line.get('text_en', line.get('text', '')),
                        'ifIgnore': 0,  # 默认显示
                        'ifEvidence': 0,  # 默认非证词
                        'cnExracted': '',  # 待补充
                        'enExracted': '',  # 待补充
                    }
                    records.append(record)
                    step += 1

        return records

    # ==================== 输出方法 ====================

    def save_yaml(self, data: List[dict], filename: str, meta: dict):
        """保存为yaml格式"""
        output = {
            '_meta': meta,
            'data': data
        }

        path = STORY_OUTPUT / f"{filename}.yaml"
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(output, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

        print(f"  📄 {path.name}: {len(data)} 条记录")
        return path

    def save_excel(self, data: List[dict], filename: str, meta: dict):
        """保存为Excel格式（带Luban表头）"""
        if not data:
            print(f"  [WARN] {filename}: 无数据，跳过")
            return None

        # 使用 openpyxl 直接创建带表头的 Excel
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active

        # 第1行：##var + 字段名
        ws.append(['##var'] + meta['var'])
        # 第2行：##type + 类型定义
        ws.append(['##type'] + meta['type'])
        # 第3行：## + 字段描述
        ws.append(['##'] + meta['desc'])

        # 第4行起：数据（第一列留空，与表头对齐）
        for record in data:
            row = [''] + [record.get(field, '') for field in meta['var']]
            ws.append(row)

        # 保存
        path = STORY_OUTPUT / f"{filename}.xlsx"
        wb.save(path)

        print(f"  [OK] {path.name}: {len(data)} 条记录")
        return path

    def copy_to_unity(self):
        """复制Excel到Unity目录"""
        print("\n📦 复制到Unity目录...")

        if not UNITY_OUTPUT.exists():
            print(f"  ⚠️ Unity目录不存在: {UNITY_OUTPUT}")
            return

        for xlsx in STORY_OUTPUT.glob("*.xlsx"):
            target = UNITY_OUTPUT / xlsx.name
            shutil.copy2(xlsx, target)
            print(f"  ✅ {xlsx.name} -> {target}")

    # ==================== 主流程 ====================

    def run(self, tables: List[str] = None):
        """执行转换"""
        print("=" * 50)
        print("🚀 配表小助手 - 开始转换")
        print("=" * 50)

        # 加载数据
        self.load_all_data()

        # 定义表配置（严格按照规则文档的完整字段）
        table_configs = {
            'NPCStaticData': {
                'converter': self.convert_npc,
                'meta': {
                    'var': ['id', 'cnName', 'enName', 'role', 'path1', 'path2', 'path3',
                            'TestimonyCount', 'cnTestimony', 'enTestimony',
                            'cnDescribe', 'enDescribe', 'ifExpose', 'cnNewDescribe', 'enNewDescribe'],
                    'type': ['string', 'string', 'string', 'string', 'string', 'string', 'string',
                             'int', 'string', 'string',
                             'string', 'string', 'string', 'string', 'string'],
                    'desc': ['NPC ID', '中文名', '英文名', '角色类型', '资源路径1', '资源路径2', '资源路径3',
                             '证词数量', '中文证词', '英文证词',
                             '中文描述', '英文描述', '可指证编号', '指证后中文描述', '指证后英文描述'],
                }
            },
            'SceneConfig': {
                'converter': self.convert_scene,
                'meta': {
                    'var': ['sceneId', 'sectionId', 'sceneName', 'sceneNameEn', 'chapterId',
                            'sceneType', 'backgroundImage', 'backgroundMusic', 'ambientSound',
                            'unlockCondition', 'npcsPresent', '备注'],
                    'type': ['string', 'string', 'string', 'string', 'string',
                             'string', 'string', 'string', 'string',
                             'string', 'string', 'string'],
                    'desc': ['场景ID', '小节ID', '中文场景名', '英文场景名', '章节ID',
                             '场景类型', '背景图路径', '背景音乐', '环境音效',
                             '解锁条件', '场景NPC', '备注'],
                }
            },
            'ItemStaticData': {
                'converter': self.convert_item,
                'meta': {
                    'var': ['id', 'cnName', 'enName', 'itemType', 'canCollected', 'canAnalyzed', 'canCombined',
                            'combineParameter0', 'combineParameter1',
                            'cnDescribe1', 'cnDescribe2', 'cnDescribe3',
                            'enDescribe1', 'enDescribe2', 'enDescribe3',
                            'path1', 'path2', 'path3', 'parameter'],
                    'type': ['string', 'string', 'string', 'string', 'bool', 'bool', 'bool',
                             'string', 'string',
                             'string', 'string', 'string',
                             'string', 'string', 'string',
                             'string', 'string', 'string', 'string'],
                    'desc': ['物品ID', '中文名', '英文名', '物品类型', '可收集', '可分析', '可合并',
                             '合并参数0', '合并参数1',
                             '中文描述1', '中文描述2', '中文描述3',
                             '英文描述1', '英文描述2', '英文描述3',
                             '资源路径1', '资源路径2', '资源路径3', '事件参数'],
                }
            },
            'Talk': {
                'converter': self.convert_talk,
                'meta': {
                    'var': ['id', 'step', 'speakType', 'waitTime', 'IdSpeaker', 'cnSpeaker', 'enSpeaker',
                            'cnWords', 'enWords', 'next', 'script',
                            'ParameterStr0', 'ParameterStr1', 'ParameterStr2',
                            'ParameterInt0', 'ParameterInt1', 'ParameterInt2',
                            'imagePath', 'voicePath'],
                    'type': ['int', 'int', 'int', 'float', 'string', 'string', 'string',
                             'string', 'string', 'string', 'string',
                             'string', 'string', 'string',
                             'int', 'int', 'int',
                             'string', 'string'],
                    'desc': ['对话ID', '步骤', '对话类型', '等待时间', '说话人ID', '中文名', '英文名',
                             '中文台词', '英文台词', '下一句ID', '脚本类型',
                             '字符串参数0', '字符串参数1', '字符串参数2',
                             '整数参数0', '整数参数1', '整数参数2',
                             '头像路径', '语音路径'],
                }
            },
            'Testimony': {
                'converter': self.convert_testimony,
                'meta': {
                    'var': ['id', 'speakerName', 'speakerNameEn', 'cnWords', 'enWords',
                            'ifIgnore', 'ifEvidence', 'cnExracted', 'enExracted'],
                    'type': ['int', 'string', 'string', 'string', 'string',
                             'int', 'int', 'string', 'string'],
                    'desc': ['证词ID', '说话人中文名', '说话人英文名', '中文内容', '英文内容',
                             '是否隐藏', '证词序号', '中文提取', '英文提取'],
                }
            },
        }

        # 确定要处理的表
        if tables:
            table_configs = {k: v for k, v in table_configs.items() if k in tables}

        # 执行转换
        print("\n📝 生成配置表...")
        results = {}

        for name, config in table_configs.items():
            data = config['converter']()
            self.save_yaml(data, name, config['meta'])
            self.save_excel(data, name, config['meta'])
            results[name] = len(data)

        # 复制到Unity
        self.copy_to_unity()

        # 输出统计
        print("\n" + "=" * 50)
        print("✅ 转换完成！")
        print("=" * 50)
        print("\n📊 统计:")
        for name, count in results.items():
            print(f"  {name}: {count} 条")

        return results


if __name__ == '__main__':
    import sys

    converter = ConfigTableConverter()

    # 支持命令行参数指定表
    if len(sys.argv) > 1:
        tables = sys.argv[1:]
        converter.run(tables)
    else:
        converter.run()
