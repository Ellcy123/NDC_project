"""
程序产出扫描器 - 配置表、代码、JSON 数据表
"""
import os
import glob
from datetime import datetime
from .config import UNITY_XLS, UNITY_TABLE_JSON, UNITY_SCRIPTS, PREVIEW_DIR


def scan_config_xlsx():
    """扫描 D:\\NDC\\res\\xls\\ 下的 XLSX 配置表"""
    result = {"files": {}, "total": 0}
    if not os.path.isdir(UNITY_XLS):
        return result

    for f in sorted(os.listdir(UNITY_XLS)):
        if f.endswith(".xlsx") and not f.startswith("~$"):
            full_path = os.path.join(UNITY_XLS, f)
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
            result["files"][f.replace(".xlsx", "")] = {
                "last_modified": mtime.strftime("%Y-%m-%d %H:%M"),
                "size_bytes": os.path.getsize(full_path),
            }
    result["total"] = len(result["files"])
    return result


def scan_table_json():
    """扫描 D:\\NDC\\Assets\\table\\ 下的 JSON 配置表"""
    result = {"files": {}, "total": 0}
    if not os.path.isdir(UNITY_TABLE_JSON):
        return result

    for f in sorted(os.listdir(UNITY_TABLE_JSON)):
        if f.endswith(".json") and not f.endswith(".meta"):
            full_path = os.path.join(UNITY_TABLE_JSON, f)
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
            result["files"][f.replace(".json", "")] = {
                "last_modified": mtime.strftime("%Y-%m-%d %H:%M"),
                "size_bytes": os.path.getsize(full_path),
            }
    result["total"] = len(result["files"])
    return result


def scan_config_sync():
    """对比 NDC_project preview JSON vs NDC XLSX，检查同步状态"""
    preview_table_dir = os.path.join(PREVIEW_DIR, "table")
    result = {"in_sync": 0, "out_of_sync": 0, "details": []}

    if not os.path.isdir(preview_table_dir) or not os.path.isdir(UNITY_XLS):
        return result

    preview_tables = set()
    for f in os.listdir(preview_table_dir):
        if f.endswith(".json"):
            preview_tables.add(f.replace(".json", ""))

    unity_tables = set()
    for f in os.listdir(UNITY_XLS):
        if f.endswith(".xlsx") and not f.startswith("~$"):
            unity_tables.add(f.replace(".xlsx", ""))

    common = preview_tables & unity_tables
    only_preview = preview_tables - unity_tables
    only_unity = unity_tables - preview_tables

    for table_name in sorted(common):
        preview_path = os.path.join(preview_table_dir, f"{table_name}.json")
        unity_path = os.path.join(UNITY_XLS, f"{table_name}.xlsx")
        p_mtime = os.path.getmtime(preview_path)
        u_mtime = os.path.getmtime(unity_path)

        diff_hours = (p_mtime - u_mtime) / 3600
        if abs(diff_hours) > 24:
            result["out_of_sync"] += 1
            result["details"].append({
                "table": table_name,
                "status": "out_of_sync",
                "preview_newer": diff_hours > 0,
                "diff_hours": round(abs(diff_hours), 1),
            })
        else:
            result["in_sync"] += 1

    for t in sorted(only_preview):
        result["details"].append({"table": t, "status": "only_in_preview"})
    for t in sorted(only_unity):
        result["details"].append({"table": t, "status": "only_in_unity"})

    return result


def scan_scripts():
    """扫描 Unity C# 脚本"""
    result = {"total": 0, "table_classes": 0}
    if not os.path.isdir(UNITY_SCRIPTS):
        return result

    cs_files = glob.glob(os.path.join(UNITY_SCRIPTS, "**", "*.cs"), recursive=True)
    result["total"] = len(cs_files)

    table_dir = os.path.join(UNITY_SCRIPTS, "table")
    if os.path.isdir(table_dir):
        result["table_classes"] = len(glob.glob(os.path.join(table_dir, "*.cs")))

    return result


def run():
    """执行完整程序扫描"""
    return {
        "config_xlsx": scan_config_xlsx(),
        "table_json": scan_table_json(),
        "config_sync": scan_config_sync(),
        "scripts": scan_scripts(),
    }
