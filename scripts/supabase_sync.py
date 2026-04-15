#!/usr/bin/env python3
"""
NDC Config Table Sync: Supabase ↔ Local JSON

Usage:
  python supabase_sync.py setup     # 打印 SQL 建表语句（需在 Supabase Dashboard 执行）
  python supabase_sync.py upload    # 上传本地 JSON → Supabase
  python supabase_sync.py pull      # 拉取 Supabase → 本地 JSON
  python supabase_sync.py status    # 查看 Supabase 中各表状态
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# ── Config ──────────────────────────────────────────────
SUPABASE_URL = "https://tyqsamueendpanbfousp.supabase.co"
SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR5cXNhbXVlZW5kcGFuYmZvdXNwIiwi"
    "cm9sZSI6ImFub24iLCJpYXQiOjE3NzUxOTI1NjMsImV4cCI6MjA5MDc2ODU2M30."
    "qa_EqkXHkq5ki8CYt0cJk-Se2vfj8PTVHci239YblfM"
)

DATA_DIR = Path(__file__).resolve().parent.parent / "preview_new2" / "data" / "table"

# 需要同步的配置表（与 editor.html 保持一致）
TABLES = [
    "ItemStaticData",
    "SceneConfig",
    "NPCStaticData",
    "TestimonyItem",
    "DoubtConfig",
    "ExposeData",
    "ExposeConfig",
    "Testimony",
    "ChapterConfig",
]


def get_client():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def cmd_setup():
    """打印 Supabase 建表 SQL"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  请在 Supabase SQL Editor 中执行以下 SQL：                    ║
║  https://supabase.com/dashboard/project/tyqsamueendpanbfousp/sql/new
╚══════════════════════════════════════════════════════════════╝

-- 1. 创建配置表
CREATE TABLE IF NOT EXISTS config_tables (
  name        TEXT PRIMARY KEY,
  data        JSONB NOT NULL DEFAULT '[]'::jsonb,
  updated_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_by  TEXT DEFAULT 'unknown'
);

-- 2. 自动更新时间戳
CREATE OR REPLACE FUNCTION update_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS set_config_timestamp ON config_tables;
CREATE TRIGGER set_config_timestamp
  BEFORE UPDATE ON config_tables
  FOR EACH ROW EXECUTE FUNCTION update_config_timestamp();

-- 3. 开放公共访问（与 PM Dashboard 一致）
ALTER TABLE config_tables ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow all config" ON config_tables;
CREATE POLICY "Allow all config" ON config_tables
  FOR ALL USING (true) WITH CHECK (true);

-- 完成！运行 `python supabase_sync.py upload` 上传数据。
""")


def cmd_upload():
    """上传本地 JSON → Supabase"""
    client = get_client()
    success, fail = 0, 0
    for name in TABLES:
        path = DATA_DIR / f"{name}.json"
        if not path.exists():
            print(f"  [FAIL]{name}: 文件不存在 ({path})")
            fail += 1
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            client.table("config_tables").upsert({
                "name": name,
                "data": data,
                "updated_by": "upload_script",
            }).execute()
            print(f"  [OK] {name}: {len(data)} rows uploaded")
            success += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            fail += 1
    print(f"\nDone: {success} ok, {fail} failed")


def cmd_pull():
    """拉取 Supabase → 本地 JSON"""
    client = get_client()
    result = client.table("config_tables").select("*").execute()
    if not result.data:
        print("Supabase 中没有数据。请先运行 upload。")
        return

    pulled = 0
    for row in result.data:
        name = row["name"]
        if name not in TABLES:
            continue
        path = DATA_DIR / f"{name}.json"
        data = row["data"]
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        ts = row.get("updated_at", "?")
        by = row.get("updated_by", "?")
        print(f"  [OK]{name}: {len(data)} rows → {path.name}  (by {by}, {ts})")
        pulled += 1
    print(f"\n完成: {pulled} 个表已拉取到 {DATA_DIR}")


def cmd_status():
    """查看 Supabase 中各表状态"""
    client = get_client()
    result = client.table("config_tables").select("name,updated_at,updated_by").execute()
    if not result.data:
        print("Supabase 中没有数据。")
        return
    print(f"{'表名':<20} {'行数':>6} {'更新者':<15} {'更新时间'}")
    print("─" * 70)

    # 获取完整数据来计算行数
    full = client.table("config_tables").select("*").execute()
    for row in sorted(full.data, key=lambda r: r["name"]):
        name = row["name"]
        count = len(row["data"]) if isinstance(row["data"], list) else "?"
        by = row.get("updated_by", "?")
        ts = row.get("updated_at", "?")
        if isinstance(ts, str) and len(ts) > 19:
            ts = ts[:19]
        print(f"  {name:<20} {count:>4}   {by:<15} {ts}")


# ── State YAML 同步 ─────────────────────────────────
# State 文件目录映射
STATE_DIRS = {
    "Unit1": Path(__file__).resolve().parent.parent / "剧情设计" / "unit1 重构版" / "state",
}


def cmd_upload_states():
    """上传 state YAML → Supabase (存为 JSON)"""
    import yaml
    client = get_client()
    success, fail = 0, 0
    for unit, state_dir in STATE_DIRS.items():
        if not state_dir.exists():
            print(f"  [SKIP] {unit}: directory not found ({state_dir})")
            continue
        for yaml_file in sorted(state_dir.glob("loop*_state.yaml")):
            loop_match = yaml_file.stem.replace("_state", "")  # "loop1"
            key = f"state_{unit}_{loop_match}"
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                client.table("config_tables").upsert({
                    "name": key,
                    "data": data,
                    "updated_by": "state_upload",
                }).execute()
                print(f"  [OK] {key} <- {yaml_file.name}")
                success += 1
            except Exception as e:
                print(f"  [FAIL] {key}: {e}")
                fail += 1
    print(f"\nDone: {success} ok, {fail} failed")


def cmd_pull_states():
    """拉取 Supabase state → 本地 YAML"""
    import yaml
    client = get_client()
    result = client.table("config_tables").select("*").like("name", "state_%").execute()
    if not result.data:
        print("Supabase 中没有 state 数据。请先运行 upload-states。")
        return
    for row in sorted(result.data, key=lambda r: r["name"]):
        name = row["name"]  # e.g. "state_Unit1_loop1"
        parts = name.split("_")  # ["state", "Unit1", "loop1"]
        if len(parts) < 3:
            continue
        unit, loop = parts[1], parts[2]
        if unit not in STATE_DIRS:
            print(f"  [SKIP] {name}: unknown unit {unit}")
            continue
        out_dir = STATE_DIRS[unit]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{loop}_state.yaml"
        yml = yaml.dump(
            row["data"], allow_unicode=True, default_flow_style=False,
            sort_keys=False, width=120,
        )
        out_path.write_text(yml, encoding="utf-8")
        by = row.get("updated_by", "?")
        print(f"  [OK] {name} -> {out_path.name}  (by {by})")


COMMANDS = {
    "setup": cmd_setup,
    "upload": cmd_upload,
    "pull": cmd_pull,
    "status": cmd_status,
    "upload-states": cmd_upload_states,
    "pull-states": cmd_pull_states,
}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd in COMMANDS:
        COMMANDS[cmd]()
    else:
        print(__doc__)
