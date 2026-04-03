"""
NDC PM Dashboard - 扫描 & 上传
主入口：扫描两个仓库 -> 生成 project_state -> 上传到 Supabase

用法:
  python scan_and_upload.py           # 扫描 + 上传
  python scan_and_upload.py --local   # 仅扫描，保存到本地 JSON（不上传）
  python scan_and_upload.py --auto    # 扫描 + 上传 + 自动更新有 auto_link 的任务进度
"""
import json
import sys
import os
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanners import design_scanner, dev_scanner, art_scanner
from scanners.config import SUPABASE_URL, SUPABASE_KEY

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scan_output")


def run_scan():
    """执行全部扫描"""
    print("[1/3] 扫描策划产出...")
    design = design_scanner.run()

    print("[2/3] 扫描程序产出...")
    dev = dev_scanner.run()

    print("[3/3] 扫描美术资源...")
    art = art_scanner.run(design_data=design)

    state = {
        "scan_time": datetime.now().isoformat(),
        "design": design,
        "dev": dev,
        "art": art,
    }
    return state


def save_local(state):
    """保存到本地 JSON"""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, "project_state.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"  -> 已保存到 {path}")
    return path


def upload_to_supabase(state):
    """上传扫描结果到 Supabase"""
    try:
        from supabase import create_client
    except ImportError:
        print("  [X] pip install supabase")
        return False

    print("  上传到 Supabase...")
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 插入扫描快照
    result = client.table("scan_snapshots").insert({
        "data": state,
    }).execute()

    if result.data:
        print(f"  [OK] 已上传扫描快照 (id: {result.data[0]['id']})")
        return True
    else:
        print("  [X] 上传失败")
        return False


def auto_update_tasks(state):
    """自动更新有 auto_link 的任务进度"""
    try:
        from supabase import create_client
    except ImportError:
        return

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 获取所有有 auto_link 的任务
    result = client.table("tasks").select("*").not_.is_("auto_link", "null").execute()
    if not result.data:
        print("  无 auto_link 任务需要更新")
        return

    updated = 0
    for task in result.data:
        auto_link = task["auto_link"]
        auto_progress = resolve_auto_link(state, auto_link)
        if auto_progress is None:
            continue

        # 只在自动值更高时更新（PM 手动设的值优先）
        current = task.get("progress", 0) or 0
        if auto_progress > current:
            client.table("tasks").update({
                "progress": auto_progress,
                "updated_at": datetime.now().isoformat(),
                "updated_by": "auto_scan",
            }).eq("id", task["id"]).execute()
            updated += 1
            print(f"  [UP] {task['task_id']} {task['name']}: {current}% -> {auto_progress}%")

    print(f"  [OK] 自动更新了 {updated} 个任务")


def resolve_auto_link(state, link):
    """解析 auto_link 路径，返回进度百分比 (0-100)"""
    # auto_link 格式示例:
    #   "design.dialogue.EPI01.talk_total" -> 对比目标值计算比例
    #   "art.movieclip.by_episode.epi02" -> 有/无 -> 0 或 100
    #   "design.units.Unit3.state_files:6" -> 当前值/目标值

    parts = link.split(":")
    path = parts[0]
    target = int(parts[1]) if len(parts) > 1 else None

    # 遍历路径
    value = state
    for key in path.split("."):
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
        if value is None:
            return None

    # 计算进度
    if isinstance(value, (int, float)):
        if target:
            return min(100, round(value / target * 100))
        else:
            return 100 if value > 0 else 0
    elif isinstance(value, bool):
        return 100 if value else 0
    elif isinstance(value, list):
        if target:
            return min(100, round(len(value) / target * 100))
        return 100 if len(value) > 0 else 0

    return None


def print_summary(state):
    """打印扫描摘要"""
    d = state["design"]
    dev = state["dev"]
    art = state["art"]

    print("\n" + "=" * 50)
    print("扫描摘要")
    print("=" * 50)

    # 设计
    for unit in ["Unit1", "Unit2", "Unit3", "Unit4"]:
        u = d["units"].get(unit, {})
        if not u.get("exists"):
            print(f"  {unit}: (未创建)")
            continue
        print(f"  {unit}: {u.get('characters', 0)}角色 | {u.get('scenes', 0)}场景 | "
              f"{u.get('state_files', 0)}state | {u.get('evidence_docs', 0)}证据 | "
              f"{u.get('expose_docs', 0)}指证")

    # 对话
    print()
    for epi in ["EPI01", "EPI02", "EPI03"]:
        dlg = d["dialogue"].get(epi, {})
        if not dlg.get("exists"):
            print(f"  {epi}: 无 JSON 对话")
            continue
        print(f"  {epi}: {dlg.get('talk_total', 0)} Talk + {dlg.get('expose_total', 0)} Expose JSON")

    # 程序
    print(f"\n  配置表: {dev['config_xlsx']['total']} XLSX | "
          f"{dev['table_json']['total']} JSON | "
          f"{dev['config_sync']['in_sync']} 同步 / {dev['config_sync']['out_of_sync']} 不同步")

    # 美术
    print(f"\n  美术资源: {art['total_files']} 总文件")
    print(f"    场景: {art['scene']['total']} | NPC: {art['npc']['total']} | "
          f"MovieClip: {art['movieclip']['total']} | AVG演出: {art['avg_clip']['total']} | "
          f"UI: {art['ui']['total']}")
    print(f"    覆盖率: MovieClip {art['coverage']['movieclip']} | "
          f"AVG {art['coverage']['avg_clip']} | 语音 {art['coverage']['voice']}")
    print()


def main():
    args = sys.argv[1:]
    local_only = "--local" in args
    auto_update = "--auto" in args

    print("NDC PM Dashboard 扫描器")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    # 扫描
    state = run_scan()
    print_summary(state)

    # 保存本地
    save_local(state)

    # 上传
    if not local_only:
        upload_to_supabase(state)

    # 自动更新任务
    if auto_update:
        print("\n自动更新任务进度...")
        auto_update_tasks(state)

    print("\n完成!")


if __name__ == "__main__":
    main()
