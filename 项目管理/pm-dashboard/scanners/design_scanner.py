"""
策划产出扫描器 - 扫描设计文档、对话、预览数据
"""
import os
import glob
from datetime import datetime
from .config import DESIGN_DIR, AVG_DIR, PREVIEW_DIR, UNITS, UNIT_TO_EPI, LOOPS


def count_files(directory, pattern="*", recursive=False):
    """计数目录下匹配的文件数（排除目录和隐藏文件）"""
    if not os.path.isdir(directory):
        return 0
    if recursive:
        files = glob.glob(os.path.join(directory, "**", pattern), recursive=True)
    else:
        files = glob.glob(os.path.join(directory, pattern))
    return len([f for f in files if os.path.isfile(f) and not os.path.basename(f).startswith(".")])


def count_md(directory):
    return count_files(directory, "*.md")


def count_yaml(directory):
    return count_files(directory, "*.yaml")


def count_json(directory):
    return count_files(directory, "*.json")


def scan_unit(unit_name):
    """扫描单个 Unit 的设计产出"""
    unit_dir = os.path.join(DESIGN_DIR, unit_name)
    if not os.path.isdir(unit_dir):
        return {"exists": False}

    result = {
        "exists": True,
        "characters": count_md(os.path.join(unit_dir, "人物设定")),
        "scenes": count_md(os.path.join(unit_dir, "场景")),
        "state_files": count_yaml(os.path.join(unit_dir, "state")),
        "evidence_docs": count_md(os.path.join(unit_dir, "证据设计")),
        "expose_docs": count_md(os.path.join(unit_dir, "循环指证设计")),
        "plot_docs": count_md(os.path.join(unit_dir, "剧情")),
    }

    # Unit3 特有内容
    minigame_dir = os.path.join(unit_dir, "小玩法")
    if os.path.isdir(minigame_dir):
        result["minigames"] = count_md(minigame_dir)

    connoisseur_dir = os.path.join(unit_dir, "鉴赏力")
    if os.path.isdir(connoisseur_dir):
        result["connoisseur"] = count_md(connoisseur_dir)

    sudden_dir = os.path.join(unit_dir, "突发事件")
    if os.path.isdir(sudden_dir):
        result["sudden_events"] = count_md(sudden_dir)

    return result


def scan_dialogue_json(epi_name):
    """扫描 AVG 对话 JSON 文件"""
    epi_dir = os.path.join(AVG_DIR, epi_name)
    if not os.path.isdir(epi_dir):
        return {"exists": False, "talk": {}, "expose": {}}

    result = {"exists": True, "talk": {}, "expose": {}}

    # Talk JSON per loop
    talk_dir = os.path.join(epi_dir, "Talk")
    if os.path.isdir(talk_dir):
        for loop in LOOPS:
            loop_dir = os.path.join(talk_dir, loop)
            if os.path.isdir(loop_dir):
                # 排除 _manifest.json 和 .backup 目录
                json_files = [
                    f for f in glob.glob(os.path.join(loop_dir, "*.json"))
                    if os.path.isfile(f) and not os.path.basename(f).startswith("_")
                ]
                result["talk"][loop] = len(json_files)

    # Expose JSON
    expose_dir = os.path.join(epi_dir, "Expose")
    if os.path.isdir(expose_dir):
        json_files = [
            f for f in glob.glob(os.path.join(expose_dir, "*.json"))
            if os.path.isfile(f) and not os.path.basename(f).startswith("_")
        ]
        result["expose"]["total"] = len(json_files)
        # 按 loop 分组
        for f in json_files:
            name = os.path.basename(f)
            for loop in LOOPS:
                loop_num = loop.replace("loop", "")
                if name.startswith(f"loop{loop_num}_"):
                    result["expose"].setdefault(loop, 0)
                    result["expose"][loop] += 1

    result["talk_total"] = sum(result["talk"].values())
    result["expose_total"] = result["expose"].get("total", 0)
    return result


def scan_dialogue_drafts():
    """扫描对话草稿 MD 文件"""
    drafts_dir = os.path.join(AVG_DIR, "对话配置工作及草稿")
    result = {"loops_with_drafts": []}

    # 检查生成草稿
    gen_dir = os.path.join(drafts_dir, "生成草稿")
    if os.path.isdir(gen_dir):
        for loop_num in range(1, 7):
            draft = os.path.join(gen_dir, f"Loop{loop_num}_生成草稿.md")
            if os.path.isfile(draft) and os.path.getsize(draft) > 100:
                result["loops_with_drafts"].append(loop_num)

    # 检查 0304 目录（Unit3 草稿）
    unit3_drafts = os.path.join(AVG_DIR, "0304", "对话草稿")
    if os.path.isdir(unit3_drafts):
        result["unit3_draft_loops"] = []
        for loop_num in range(1, 7):
            loop_dir = os.path.join(unit3_drafts, f"Loop{loop_num}")
            if os.path.isdir(loop_dir) and count_md(loop_dir) > 0:
                result["unit3_draft_loops"].append(loop_num)
        result["unit3_draft_files"] = count_md(unit3_drafts) + sum(
            count_md(os.path.join(unit3_drafts, f"Loop{i}")) for i in range(1, 7)
        )

    return result


def scan_preview_data():
    """扫描预览系统数据完整性"""
    result = {}
    for unit in UNITS:
        unit_dir = os.path.join(PREVIEW_DIR, unit)
        if not os.path.isdir(unit_dir):
            result[unit] = {"exists": False, "loops": 0, "extras": []}
            continue

        loops = sum(1 for i in range(1, 7)
                    if os.path.isfile(os.path.join(unit_dir, f"loop{i}.yaml")))
        extras = [f for f in os.listdir(unit_dir)
                  if not f.startswith("loop") and os.path.isfile(os.path.join(unit_dir, f))]
        result[unit] = {"exists": True, "loops": loops, "extras": extras}

    # Table JSON
    table_dir = os.path.join(PREVIEW_DIR, "table")
    if os.path.isdir(table_dir):
        result["table_files"] = count_json(table_dir)
    else:
        result["table_files"] = 0

    return result


def scan_config_tables():
    """扫描 preview_new2/data/table 下的配置表"""
    table_dir = os.path.join(PREVIEW_DIR, "table")
    result = {}
    if not os.path.isdir(table_dir):
        return result

    for f in sorted(os.listdir(table_dir)):
        if f.endswith(".json"):
            full_path = os.path.join(table_dir, f)
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
            size = os.path.getsize(full_path)
            result[f.replace(".json", "")] = {
                "last_modified": mtime.strftime("%Y-%m-%d %H:%M"),
                "size_bytes": size,
            }
    return result


def run():
    """执行完整策划扫描"""
    result = {"units": {}, "dialogue": {}, "drafts": {}, "preview": {}, "config_tables": {}}

    # 扫描各 Unit 设计文档
    for unit in UNITS:
        result["units"][unit] = scan_unit(unit)

    # 也检查 Unit4
    result["units"]["Unit4"] = scan_unit("Unit4")

    # 扫描对话 JSON
    for epi in ["EPI01", "EPI02", "EPI03"]:
        result["dialogue"][epi] = scan_dialogue_json(epi)

    # 扫描草稿
    result["drafts"] = scan_dialogue_drafts()

    # 扫描预览数据
    result["preview"] = scan_preview_data()

    # 扫描配置表
    result["config_tables"] = scan_config_tables()

    return result
