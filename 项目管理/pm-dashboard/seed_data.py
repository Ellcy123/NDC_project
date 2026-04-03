"""
种子数据导入 - 从 CSV 配置文件读取任务/里程碑/风险，导入 Supabase
数据源在 data/ 目录下的 CSV 文件，修改数据只需编辑 CSV。

用法：
  python seed_data.py          # 清空+全量导入
  python seed_data.py --dry    # 只读取预览，不写入
"""
import csv, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scanners.config import SUPABASE_URL, SUPABASE_KEY

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def read_csv(filename):
    """读取 CSV 文件，返回 dict 列表。自动清理空值字段。"""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[WARN] {filename} not found, skipping")
        return []

    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            cleaned = {}
            for k, v in row.items():
                if v is None or v.strip() == "":
                    continue  # 跳过空值，让 Supabase 用默认值
                cleaned[k] = v.strip()
            rows.append(cleaned)
    return rows


def parse_tasks(rows):
    """处理 tasks CSV 行：转换数值类型。"""
    for row in rows:
        if "estimated_days" in row:
            row["estimated_days"] = float(row["estimated_days"])
    return rows


def parse_milestones(rows):
    """处理 milestones.csv 行：解析 depends_on JSON。"""
    for row in rows:
        if "depends_on" in row:
            try:
                row["depends_on"] = json.loads(row["depends_on"])
            except (json.JSONDecodeError, TypeError):
                row["depends_on"] = []
    return rows


def parse_risks(rows):
    """处理 risks.csv 行：无特殊转换。"""
    return rows


def main():
    dry_run = "--dry" in sys.argv

    print("=== NDC PM Dashboard seed (CSV → Supabase) ===")
    print(f"数据目录: {DATA_DIR}")
    if dry_run:
        print("[DRY RUN] 只读取预览，不写入 Supabase\n")

    # 读取 CSV（任务按工种拆分为三个文件）
    tasks_pm = parse_tasks(read_csv("tasks_pm.csv"))
    tasks_dev = parse_tasks(read_csv("tasks_dev.csv"))
    tasks_art = parse_tasks(read_csv("tasks_art.csv"))
    tasks = tasks_pm + tasks_dev + tasks_art
    milestones = parse_milestones(read_csv("milestones.csv"))
    risks = parse_risks(read_csv("risks.csv"))

    # 分类统计
    categories = {}
    for t in tasks:
        cat = t.get("category", "?")
        categories[cat] = categories.get(cat, 0) + 1

    print(f"\n任务: {len(tasks)} 条")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print(f"里程碑: {len(milestones)} 条")
    print(f"风险项: {len(risks)} 条")

    if dry_run:
        print("\n[DRY RUN] 预览完毕，未写入")
        return

    # 连接 Supabase
    from supabase import create_client
    db = create_client(SUPABASE_URL, SUPABASE_KEY)

    # 清空现有数据
    print("\n清空旧数据...")
    db.table("tasks").delete().neq("id", 0).execute()
    db.table("milestones").delete().neq("id", 0).execute()
    db.table("risks").delete().neq("id", 0).execute()

    # 批量插入（Supabase 单次最多 1000 行，我们不会超）
    print(f"插入 {len(tasks)} 任务...")
    # 分批插入，每批 50 条，避免请求过大
    batch_size = 50
    for i in range(0, len(tasks), batch_size):
        batch = tasks[i:i + batch_size]
        db.table("tasks").insert(batch).execute()

    print(f"插入 {len(milestones)} 里程碑...")
    db.table("milestones").insert(milestones).execute()

    print(f"插入 {len(risks)} 风险项...")
    db.table("risks").insert(risks).execute()

    print(f"\n[OK] {len(tasks)} tasks + {len(milestones)} milestones + {len(risks)} risks")
    print("数据源: data/tasks_pm.csv, tasks_dev.csv, tasks_art.csv, milestones.csv, risks.csv")
    print("修改数据 → 编辑对应 CSV → 重跑 python seed_data.py")


if __name__ == "__main__":
    main()
