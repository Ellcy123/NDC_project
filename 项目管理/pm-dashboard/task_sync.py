"""
任务同步工具：从 Supabase 导出任务 / 批量更新任务进度
用于 pm-analyst agent 的 LLM 智能匹配流程
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from scanners.config import SUPABASE_URL, SUPABASE_KEY

try:
    from supabase import create_client
except ImportError:
    print("[FAIL] supabase: pip install supabase")
    sys.exit(1)

DATA_DIR = os.path.join(os.path.dirname(__file__), "scan_output")


def export_tasks(output_path=None):
    """导出所有任务和里程碑到本地 JSON"""
    if output_path is None:
        output_path = os.path.join(DATA_DIR, "current_tasks.json")

    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    tasks = client.table("tasks").select("*").execute().data
    milestones = client.table("milestones").select("*").execute().data

    result = {
        "exported_at": __import__("datetime").datetime.now().isoformat(),
        "tasks": tasks,
        "milestones": milestones,
        "summary": {
            "total_tasks": len(tasks),
            "total_milestones": len(milestones),
            "by_category": {},
            "by_status": {},
        }
    }

    for t in tasks:
        cat = t.get("category", "unknown")
        status = t.get("status", "unknown")
        result["summary"]["by_category"][cat] = result["summary"]["by_category"].get(cat, 0) + 1
        result["summary"]["by_status"][status] = result["summary"]["by_status"].get(status, 0) + 1

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(tasks)} tasks, {len(milestones)} milestones -> {output_path}")
    return result


def update_tasks(updates):
    """
    批量更新任务进度
    updates: list of {"task_id": "PM-003", "progress": 80, "status": "...", "note": "..."}
    """
    client = create_client(SUPABASE_URL, SUPABASE_KEY)

    ok_count = 0
    for update in updates:
        task_id = update["task_id"]
        fields = {k: v for k, v in update.items() if k != "task_id"}
        fields["updated_by"] = "LLM-analyze"

        try:
            client.table("tasks").update(fields).eq("task_id", task_id).execute()
            ok_count += 1
            print(f"  [OK] {task_id} -> progress={fields.get('progress', '?')}%")
        except Exception as e:
            print(f"  [FAIL] {task_id}: {e}")

    print(f"\n{ok_count}/{len(updates)} updated")
    return ok_count


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        # python task_sync.py update updates.json
        if len(sys.argv) > 2:
            with open(sys.argv[2], "r", encoding="utf-8") as f:
                data = json.load(f)
            update_tasks(data["updates"])
        else:
            print("Usage: python task_sync.py update <updates.json>")
    else:
        export_tasks()
