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

    # NPC ID 到角色编号的映射
    # 注意：角色编号用于生成 talk_id，格式 NNXXYYY
    NPC_NUMBER_MAP = {
        'NPC101': 1,   # 查克 (Zack Brennan) - 主角
        'NPC102': 2,   # 艾玛 (Emma O'Malley)
        'NPC103': 3,   # 罗莎 (Rosa Martinez)
        'NPC104': 4,   # 莫里森警探 (Detective Morrison)
        'NPC105': 5,   # 汤米 (Tommy)
        'NPC106': 6,   # 薇薇安 (Vivian)
        'NPC107': 7,   # 韦伯 (Webb)
        'NPC108': 8,   # 安娜 (Anna Webb)
        'NPC109': 9,   # 吉米 (Jimmy)
        'NPC110': 10,  # 莫里森夫人 (Mrs. Morrison)
        'NPC111': 11,  # Anna (Jimmy's wife)
    }

    def __init__(self):
        self.npcs = {}
        self.scenes = {}
        self.evidences = {}
        self.loops = {}
        self.dialogs = {}
        # 记录每个NPC在每个循环的段落计数器
        self.npc_segment_counter = {}

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

    # ==================== ID 生成辅助方法 ====================

    def _get_npc_number(self, npc_id: str) -> int:
        """将 NPC ID 转换为角色编号 (NPC101 -> 1)"""
        return self.NPC_NUMBER_MAP.get(npc_id, 0)

    def _get_dialog_npc(self, dialog_data: dict, dialog_name: str) -> str:
        """获取对话文件的主 NPC ID"""
        if not dialog_data:
            return ''

        # 1. npc_dialog 类型：使用 npc 字段
        if dialog_data.get('npc'):
            return dialog_data['npc']

        # 2. accusation 类型：使用 target 字段
        if dialog_data.get('target'):
            return dialog_data['target']

        # 3. opening/ending 类型：从对话内容找出现最多的 NPC
        npc_counts = {}
        for section_key, section in dialog_data.items():
            if not isinstance(section, dict) or 'lines' not in section:
                continue
            for line in section.get('lines', []):
                speaker = line.get('speaker', '')
                if speaker.startswith('NPC') and speaker != 'NPC101':  # 排除主角
                    npc_counts[speaker] = npc_counts.get(speaker, 0) + 1

        if npc_counts:
            return max(npc_counts, key=npc_counts.get)

        return ''

    def _get_next_segment(self, loop_num: str, npc_id: str) -> int:
        """获取指定 NPC 的全局下一个段落号（跨循环累加）"""
        # 使用 NPC ID 作为 key，不包含 loop_num，这样段落号跨循环递增
        if npc_id not in self.npc_segment_counter:
            self.npc_segment_counter[npc_id] = 0
        self.npc_segment_counter[npc_id] += 1
        return self.npc_segment_counter[npc_id]

    def _sort_dialog_files(self, loop_dialogs: dict) -> List[tuple]:
        """按处理顺序排序对话文件: opening -> npc_dialogs(字母序) -> accusation -> ending"""
        sorted_files = []

        # 1. opening 优先
        if 'opening' in loop_dialogs:
            sorted_files.append(('opening', loop_dialogs['opening']))

        # 2. npc_dialog 文件（按文件名字母序）
        npc_files = []
        for name, data in loop_dialogs.items():
            if name in ['opening', 'accusation', 'ending', 'schema_dialogs']:
                continue
            if data and data.get('type') == 'npc_dialog':
                npc_files.append((name, data))
            elif data and data.get('npc'):  # 有 npc 字段的也算
                npc_files.append((name, data))
            elif name not in ['opening', 'accusation', 'ending'] and data:
                # 其他文件也按 npc_dialog 处理
                npc_files.append((name, data))

        # 按文件名字母序排序
        npc_files.sort(key=lambda x: x[0])
        sorted_files.extend(npc_files)

        # 3. accusation
        if 'accusation' in loop_dialogs:
            sorted_files.append(('accusation', loop_dialogs['accusation']))

        # 4. ending 最后
        if 'ending' in loop_dialogs:
            sorted_files.append(('ending', loop_dialogs['ending']))

        return sorted_files

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
                'canCollected': 1 if ev.get('type') in ['item', 'clue', 'note'] else 0,
                'canAnalyzed': 1 if 'analysis' in ev else 0,
                'canCombined': 0,  # 待补充
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
        """转换对话表（完整19个字段）- 支持自动ID生成和branches分支"""
        records = []
        npcs_data = self.npcs.get('npcs', {})

        # 重置段落计数器
        self.npc_segment_counter = {}

        # ID 分配日志
        id_allocation_log = []

        # ===== 第一遍：收集每个 section 的第一句 ID =====
        section_first_ids = {}  # key: "dialog_name/section_key" -> first_id

        for loop_num, loop_dialogs in sorted(self.dialogs.items()):
            sorted_dialogs = self._sort_dialog_files(loop_dialogs)

            for dialog_name, dialog_data in sorted_dialogs:
                if not dialog_data:
                    continue

                main_npc = self._get_dialog_npc(dialog_data, dialog_name)
                npc_number = self._get_npc_number(main_npc)

                if npc_number == 0:
                    continue

                for section_key, section in dialog_data.items():
                    if not isinstance(section, dict) or 'lines' not in section:
                        continue

                    segment = self._get_next_segment(loop_num, main_npc)

                    # 找到第一句非 player_choice 的对话
                    for line in section.get('lines', []):
                        if line.get('speaker') != 'player_choice':
                            first_id = int(f"{npc_number}{str(segment).zfill(3)}001")
                            section_first_ids[f"{dialog_name}/{section_key}"] = first_id
                            break

        # 重置段落计数器（第二遍重新计算）
        self.npc_segment_counter = {}

        # ===== 第二遍：生成记录，处理 branches =====
        for loop_num, loop_dialogs in sorted(self.dialogs.items()):
            sorted_dialogs = self._sort_dialog_files(loop_dialogs)

            for dialog_name, dialog_data in sorted_dialogs:
                if not dialog_data:
                    continue

                main_npc = self._get_dialog_npc(dialog_data, dialog_name)
                npc_number = self._get_npc_number(main_npc)

                if npc_number == 0:
                    print(f"  [WARN] 无法确定NPC: loop{loop_num}/{dialog_name}.yaml")
                    continue

                for section_key, section in dialog_data.items():
                    if not isinstance(section, dict) or 'lines' not in section:
                        continue

                    segment = self._get_next_segment(loop_num, main_npc)
                    sentence_num = 1

                    id_allocation_log.append({
                        'loop': loop_num,
                        'file': dialog_name,
                        'section': section_key,
                        'npc': main_npc,
                        'segment': segment,
                        'id_prefix': f"{npc_number}{str(segment).zfill(3)}"
                    })

                    lines = section.get('lines', [])
                    for i, line in enumerate(lines):
                        speaker_id = line.get('speaker', '')

                        # 处理 player_choice：生成 branches
                        if speaker_id == 'player_choice':
                            options = line.get('options', [])
                            if not options or len(records) == 0:
                                continue

                            # 获取前一句记录，添加 branches 属性
                            prev_record = records[-1]

                            # 收集选项信息
                            option_texts = []
                            option_reply_ids = []
                            target_section_ids = []

                            for opt_idx, opt in enumerate(options[:3]):  # 最多3个选项
                                option_texts.append(opt.get('text', ''))
                                next_section = opt.get('next_section', '')
                                target_key = f"{dialog_name}/{next_section}"
                                target_id = section_first_ids.get(target_key, 0)
                                target_section_ids.append(str(target_id))

                                # 生成主角复述选项的对话 ID
                                reply_id = int(f"{npc_number}{str(segment).zfill(3)}{str(sentence_num).zfill(3)}")
                                option_reply_ids.append(reply_id)
                                sentence_num += 1

                            # 设置前一句的 branches 参数
                            prev_record['script'] = 'branches'
                            prev_record['next'] = '/'.join(target_section_ids)

                            if len(option_texts) > 0:
                                prev_record['ParameterStr0'] = option_texts[0]
                                prev_record['ParameterInt0'] = option_reply_ids[0]
                            if len(option_texts) > 1:
                                prev_record['ParameterStr1'] = option_texts[1]
                                prev_record['ParameterInt1'] = option_reply_ids[1]
                            if len(option_texts) > 2:
                                prev_record['ParameterStr2'] = option_texts[2]
                                prev_record['ParameterInt2'] = option_reply_ids[2]

                            # 生成主角复述选项的对话行
                            zack_info = npcs_data.get('NPC101', {})
                            for opt_idx, opt in enumerate(options[:3]):
                                reply_id = option_reply_ids[opt_idx]
                                target_key = f"{dialog_name}/{opt.get('next_section', '')}"
                                target_id = section_first_ids.get(target_key, 0)

                                reply_record = {
                                    'id': reply_id,
                                    'step': sentence_num - len(options) + opt_idx,
                                    'speakType': 2,
                                    'waitTime': 0,
                                    'IdSpeaker': 'NPC101',
                                    'cnSpeaker': zack_info.get('name_cn', '查克'),
                                    'enSpeaker': zack_info.get('name', 'Zack'),
                                    'cnWords': opt.get('text', ''),
                                    'enWords': opt.get('text_en', opt.get('text', '')),
                                    'next': str(target_id),
                                    'script': '',
                                    'ParameterStr0': '',
                                    'ParameterStr1': '',
                                    'ParameterStr2': '',
                                    'ParameterInt0': 0,
                                    'ParameterInt1': 0,
                                    'ParameterInt2': 0,
                                    'imagePath': '',
                                    'voicePath': '',
                                }
                                records.append(reply_record)

                            continue

                        # 普通对话处理
                        speaker_info = npcs_data.get(speaker_id, {})

                        if speaker_id == 'narration':
                            speak_type = 1
                        elif speaker_id:
                            speak_type = 2
                        else:
                            speak_type = 3

                        if line.get('talk_id'):
                            talk_id = line['talk_id']
                        else:
                            talk_id = int(f"{npc_number}{str(segment).zfill(3)}{str(sentence_num).zfill(3)}")

                        record = {
                            'id': talk_id,
                            'step': sentence_num,
                            'speakType': speak_type,
                            'waitTime': line.get('wait_time', 0),
                            'IdSpeaker': speaker_id if speaker_id != 'narration' else '',
                            'cnSpeaker': speaker_info.get('name_cn', '旁白' if speaker_id == 'narration' else ''),
                            'enSpeaker': speaker_info.get('name', 'Narration' if speaker_id == 'narration' else ''),
                            'cnWords': line.get('text', ''),
                            'enWords': line.get('text_en', line.get('text', '')),
                            'next': '',
                            'script': line.get('script', ''),
                            'ParameterStr0': line.get('ParameterStr0', ''),
                            'ParameterStr1': line.get('ParameterStr1', ''),
                            'ParameterStr2': line.get('ParameterStr2', ''),
                            'ParameterInt0': line.get('ParameterInt0', 0),
                            'ParameterInt1': line.get('ParameterInt1', 0),
                            'ParameterInt2': line.get('ParameterInt2', 0),
                            'imagePath': '',
                            'voicePath': '',
                        }
                        records.append(record)
                        sentence_num += 1

        # 打印 ID 分配日志
        if id_allocation_log:
            print("\n  📋 Talk ID 分配 (每个 section 一个段落):")
            for log in id_allocation_log:
                print(f"     loop{log['loop']}/{log['file']}.yaml/{log['section']} → {log['npc']} 段落{log['segment']} (ID前缀: {log['id_prefix']})")

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

    def save_talk_excel_colored(self, data: List[dict], filename: str, meta: dict):
        """保存Talk表为带颜色的Excel格式"""
        if not data:
            print(f"  [WARN] {filename}: 无数据，跳过")
            return None

        from openpyxl import Workbook
        from openpyxl.styles import PatternFill

        # 定义颜色
        LIGHT_BLUE = PatternFill(start_color="DCE6F1", end_color="DCE6F1", fill_type="solid")
        LIGHT_YELLOW = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
        DARK_GRAY = PatternFill(start_color="808080", end_color="808080", fill_type="solid")

        wb = Workbook()
        ws = wb.active

        # 第1行：##var + 字段名
        ws.append(['##var'] + meta['var'])
        # 第2行：##type + 类型定义
        ws.append(['##type'] + meta['type'])
        # 第3行：## + 字段描述
        ws.append(['##'] + meta['desc'])

        # 解析ID获取NPC编号和段落号
        def parse_talk_id(talk_id):
            """从 talk_id 解析 NPC编号和段落号"""
            id_str = str(talk_id)
            if len(id_str) == 7:
                # 格式: NNXXYYY (如 2001001)
                npc_num = int(id_str[0])
                segment = int(id_str[1:4])
            elif len(id_str) == 8:
                # 格式: NNXXXYYY (如 10001001)
                npc_num = int(id_str[0:2])
                segment = int(id_str[2:5])
            else:
                npc_num = 0
                segment = 0
            return npc_num, segment

        # 第4行起：数据（带颜色）
        current_row = 4
        prev_npc_num = None
        col_count = len(meta['var']) + 1  # +1 for first empty column

        for record in data:
            talk_id = record.get('id', 0)
            npc_num, segment = parse_talk_id(talk_id)

            # 检查是否需要插入 NPC 分隔行
            if prev_npc_num is not None and npc_num != prev_npc_num:
                # 插入空行作为分隔
                ws.append([''] * col_count)
                # 给分隔行上色（深灰）
                for col in range(1, col_count + 1):
                    ws.cell(row=current_row, column=col).fill = DARK_GRAY
                current_row += 1

            # 写入数据行
            row = [''] + [record.get(field, '') for field in meta['var']]
            ws.append(row)

            # 根据段落号奇偶决定颜色
            fill_color = LIGHT_BLUE if segment % 2 == 1 else LIGHT_YELLOW
            for col in range(1, col_count + 1):
                ws.cell(row=current_row, column=col).fill = fill_color

            prev_npc_num = npc_num
            current_row += 1

        # 保存
        path = STORY_OUTPUT / f"{filename}.xlsx"
        wb.save(path)

        print(f"  [OK] {path.name}: {len(data)} 条记录 (带颜色)")
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
            # Talk表使用带颜色的保存方法
            if name == 'Talk':
                self.save_talk_excel_colored(data, name, config['meta'])
            else:
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
