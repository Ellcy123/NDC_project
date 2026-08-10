"""
全局 Jimmy → James 重命名脚本。

设定：昵称 = James，全名 = James O'Sullivan，"Jimmy 是爱称"对照说明全部删除。

用法：
    python scripts/rename_jimmy_to_james.py            # dry-run，只报告
    python scripts/rename_jimmy_to_james.py --apply    # 真的写入

排除：
    - Unit8（旧版/前身）
    - .backup_* / _backup_pre_unit8 / __pycache__ / 归档 / .pre_migration
    - 旧文档 / 参考资料 / Audio/（mp3 文件名保留）
    - 文件名本身不改（jimmy_001.json 保持原名）
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # d:\NDC_project

INCLUDE_DIRS = [
    "剧情设计/Unit9",
    "AVG/对话配置工作及草稿/Unit9",
    "AVG/EPI08",
    "preview_new2/data/table",
    "preview_new2",  # 含 state_to_preview_*.py
    "scripts",
    "AVG/对话配置工作及草稿",  # 含 sync_to_json.py
]

EXCLUDE_SUBSTRINGS = [
    ".backup_",
    "_backup_pre_unit8",
    "__pycache__",
    "旧文档",
    "参考资料",
    "Audio/",
    "/Unit8/",
    "\\Unit8\\",
    ".pre_migration",
    "归档",
    "rename_jimmy_to_james.py",  # 不改自己（避免覆盖 Phase 1 patterns）
    # 排除 Unit1 专用脚本（NPC ID/显示名都该保留 Jimmy）
    "state_to_preview_unit1.py",
    # 排除 sync_to_json.py（EPI01 NPC map 必须保留 jimmy，EPI08 段会手动改）
    "sync_to_json.py",
    # 排除非 Unit9 的 preview 数据目录（避免误改 Unit1-Unit7 历史数据）
    "preview_new2/data/Unit1/",
    "preview_new2\\data\\Unit1\\",
    "preview_new2/data/Unit2/",
    "preview_new2\\data\\Unit2\\",
    "preview_new2/data/Unit3/",
    "preview_new2\\data\\Unit3\\",
    "preview_new2/data/Unit4/",
    "preview_new2\\data\\Unit4\\",
    "preview_new2/data/Unit5/",
    "preview_new2\\data\\Unit5\\",
    "preview_new2/data/Unit6/",
    "preview_new2\\data\\Unit6\\",
    "preview_new2/data/Unit7/",
    "preview_new2\\data\\Unit7\\",
]

EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".py"}

# Phase 1: 先清理"Jimmy 是 James 的爱称"类对照短语
# 顺序很重要，长 pattern 在前
PRE_REPLACEMENTS = [
    ("Jimmy / James O'Sullivan", "James O'Sullivan"),
    ("Jimmy／James O'Sullivan", "James O'Sullivan"),
    ("（Jimmy 是 James 的爱称）", ""),
    ("(Jimmy 是 James 的爱称)", ""),
    ("（Jimmy 是 James 的英文爱称）", ""),
    ("(Jimmy 是 James 的英文爱称)", ""),
    ("（Jimmy 是爱称）", ""),
    ("(Jimmy 是爱称)", ""),
    ("Jimmy 是 James 的爱称。", ""),
    ("Jimmy 是 James 的爱称", ""),
    ("——Jimmy 是爱称。", "。"),
    ("——Jimmy 是爱称", ""),
    ("，Jimmy 是爱称。", "。"),
    ("，Jimmy 是爱称", ""),
    ("Jimmy 是爱称。", ""),
    ("Jimmy 是爱称", ""),
    ("Jimmy（James 的爱称）", "James"),
    ("Jimmy (James 的爱称)", "James"),
    ("Jimmy（James）", "James"),
    ("Jimmy(James)", "James"),
]

# Phase 2: 兜底替换（大小写都要 + 中文）
MAIN_REPLACEMENTS = [
    ("Jimmy", "James"),
    ("jimmy", "james"),  # NPC ID / Unity 资源名 / 文件路径引用 / state target 等
    # 中文：吉米·奥沙利文 → 詹姆斯·奥沙利文（先长后短，避免吉米先吃掉）
    ("吉米·奥沙利文", "詹姆斯·奥沙利文"),
    ("吉米", "詹姆斯"),
]


def should_skip(path: Path) -> bool:
    s = str(path).replace("\\", "/")
    return any(sub.replace("\\", "/") in s for sub in EXCLUDE_SUBSTRINGS)


def process(dry_run: bool = True):
    changes = []  # list[(path, jimmy_count_before, total_replacements)]
    pre_hits_global = {}  # pattern -> count
    for inc in INCLUDE_DIRS:
        base = ROOT / inc
        if not base.exists():
            print(f"  WARN: 跳过不存在的目录 {inc}")
            continue
        for f in base.rglob("*"):
            if not f.is_file():
                continue
            if f.suffix not in EXTENSIONS:
                continue
            if should_skip(f):
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue
            if "Jimmy" not in text and "jimmy" not in text and "吉米" not in text:
                continue
            jimmy_before = text.count("Jimmy") + text.count("jimmy") + text.count("吉米")
            new_text = text
            for old, new in PRE_REPLACEMENTS:
                if old in new_text:
                    pre_hits_global[old] = pre_hits_global.get(old, 0) + new_text.count(old)
                    new_text = new_text.replace(old, new)
            for old, new in MAIN_REPLACEMENTS:
                new_text = new_text.replace(old, new)
            jimmy_after = new_text.count("Jimmy") + new_text.count("jimmy") + new_text.count("吉米")
            if new_text != text:
                changes.append((str(f.relative_to(ROOT)), jimmy_before, jimmy_after))
                if not dry_run:
                    f.write_text(new_text, encoding="utf-8")
    return changes, pre_hits_global


def rename_files(dry_run: bool = True):
    """重命名文件名包含 jimmy/Jimmy 的文件。"""
    renames = []
    for inc in INCLUDE_DIRS:
        base = ROOT / inc
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if not f.is_file():
                continue
            if should_skip(f):
                continue
            name = f.name
            if "jimmy" not in name.lower():
                continue
            new_name = name.replace("Jimmy", "James").replace("jimmy", "james")
            if new_name == name:
                continue
            new_path = f.parent / new_name
            renames.append((str(f.relative_to(ROOT)), str(new_path.relative_to(ROOT))))
            if not dry_run:
                if new_path.exists():
                    print(f"  ⚠️ 跳过：目标已存在 {new_path}")
                    continue
                f.rename(new_path)
    return renames


def main():
    dry_run = "--apply" not in sys.argv
    print(f"{'[DRY-RUN]' if dry_run else '[APPLY]'} 扫描路径根：{ROOT}")
    print()
    changes, pre_hits = process(dry_run=dry_run)
    total_before = sum(b for _, b, _ in changes)
    total_after = sum(a for _, _, a in changes)
    print(f"=== 影响文件数：{len(changes)} ===")
    print(f"=== 替换前 Jimmy 总数：{total_before}, 替换后剩余：{total_after} ===")
    print()
    if pre_hits:
        print("--- Phase 1 清理对照短语命中 ---")
        for pat, cnt in sorted(pre_hits.items(), key=lambda x: -x[1]):
            print(f"  {cnt:4d}  {pat!r}")
        print()
    print("--- 文件改动明细（按 Jimmy 数倒序）---")
    for path, before, after in sorted(changes, key=lambda x: -x[1]):
        leftover = f" [⚠️ 残留 {after}]" if after else ""
        print(f"  {before:4d} → {after:4d}{leftover}  {path}")
    if total_after:
        print()
        print("⚠️ 有残留 Jimmy——可能在 PRE_REPLACEMENTS 里没覆盖到的格式，请人工 grep 确认")
    print()
    renames = rename_files(dry_run=dry_run)
    print(f"=== 文件重命名数：{len(renames)} ===")
    for old, new in renames:
        print(f"  {old}\n    → {new}")


if __name__ == "__main__":
    main()
