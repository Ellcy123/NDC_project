#!/usr/bin/env python3
"""
table_md_to_json.py
===================

把 LLM 写的临时 MD 草稿（preview_new2/data/_table_drafts/Unit{N}/Loop{N}.md）
解析成 preview_new2/data/table/*.json 的条目，按 ID 段增量合并。

由 /state-to-table skill 在 Phase 2/3 调用。本脚本不做业务推断——所有字段
推断规则在 SKILL.md 手册里，由 LLM 写 MD 时落实。

用法:
  python preview_new2/table_md_to_json.py Unit3                 # 实际写入
  python preview_new2/table_md_to_json.py Unit3 --dry-run       # 预览
  python preview_new2/table_md_to_json.py Unit3 --tables ItemStaticData,DoubtConfig

退出码:
  0  成功（含 dry-run）
  1  解析错误 / 校验失败 / 写入失败

写入策略:
  - 按 ID 段过滤现有表条目，本 Unit 段重写、其他 Unit 段原样保留
  - 同 ID 条目按 MD 为准
  - SceneConfig.NPCInfos 内联中，TalkInfo / LoopTalkInfo 字段如 MD 写空对象
    → 保留表中原值（避免覆盖 sync_to_json 写的 Talk）
  - 写完后 json.load 自校验
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ============================================================
# 路径配置
# ============================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TABLE_DIR = SCRIPT_DIR / "data" / "table"
DRAFT_ROOT = SCRIPT_DIR / "data" / "_table_drafts"

# 处理范围（与 SKILL.md 一致）
TABLES_FULL_WRITE = [
    "ItemStaticData",
    "NPCStaticData",
    "SceneConfig",
    "DoubtConfig",
    "TestimonyItem",
    "Testimony",
]
TABLES_PARTIAL_WRITE = ["ChapterConfig"]
ALL_TABLES = TABLES_FULL_WRITE + TABLES_PARTIAL_WRITE

# 各表的 ID → Unit 段提取函数
def unit_of(tbl: str, id_str: str) -> int | None:
    """从条目 ID 推出所属 Unit。返回 None 表示该表不按 Unit 切（如 NPC 跨 Unit 共享）。"""
    if not id_str:
        return None
    s = str(id_str)
    if tbl in ("ItemStaticData", "DoubtConfig", "SceneConfig"):
        # 4 位 {unit}{loop}{xx} 或 {unit}7{xx}
        return int(s[0]) if s and s[0].isdigit() else None
    if tbl == "NPCStaticData":
        # 3 位 {unit}{xx}
        return int(s[0]) if s and s[0].isdigit() else None
    if tbl in ("TestimonyItem", "Testimony"):
        # 7 位 {unit}{npc(2)}{loop}{seq(3)}（Unit8/Unit9 新格式）
        # 或 9 位 {npc(3)}{loop(3)}{seq(3)}（Unit1 旧格式，首字符=unit）
        # 两种格式首字符都是 unit（Unit1 testimony 如 1031001 首字符 1，Unit9 如 9031001 首字符 9）
        return int(s[0]) if s and s[0].isdigit() else None
    if tbl == "ChapterConfig":
        # 3 位 {unit}{0}{loop}（如 101-106）
        return int(s[0]) if s and s[0].isdigit() else None
    return None


# 部分写入表的"保留原值"字段
PARTIAL_PRESERVE_FIELDS = {
    "ChapterConfig": {
        "initTalk",
        "exposeNpcId",
        "exposes",
        "suspectVideoPos",
        "suspectTalkPos",
        "zackTalkPos",
    },
}


# ============================================================
# MD 解析
# ============================================================

# 待补充值：翻译为空字符串
PLACEHOLDER_PATTERN = re.compile(r"^待补充($|（.*$)")


def is_placeholder(value: str) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    return bool(PLACEHOLDER_PATTERN.match(s))


@dataclass
class Entry:
    table: str
    id: str
    fields: dict[str, Any] = field(default_factory=dict)
    skip_fields: list[str] = field(default_factory=list)
    source_loop: int | None = None  # for diagnostics


def parse_md_value(raw: str) -> Any:
    """解析单行字段值。识别 bool / int 字面量 / 数组 / 字符串 / 待补充。"""
    raw = raw.strip()
    if is_placeholder(raw):
        return ""
    # 数组字面量
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        # 简单 split（不支持嵌套）
        parts = [p.strip().strip('"').strip("'") for p in inner.split(",")]
        return parts
    # 字符串去引号
    if (raw.startswith('"') and raw.endswith('"')) or (
        raw.startswith("'") and raw.endswith("'")
    ):
        return raw[1:-1]
    return raw


def parse_loop_md(md_path: Path) -> list[Entry]:
    """解析一个 Loop MD，返回 Entry 列表。

    格式约定（详见 SKILL.md）：
      ## TableName
      ### {id} - {description}
      - field: value
      - field: |
          multiline
          continued
      - field:
        - {key: val, key: val}
        - subitem
    """
    entries: list[Entry] = []
    current_table: str | None = None
    current_entry: Entry | None = None

    # 当前正在累积的多行字段
    multiline_field: str | None = None
    multiline_lines: list[str] = []
    multiline_indent: int | None = None

    # 当前正在累积的列表/嵌套字段
    nested_field: str | None = None
    nested_items: list[Any] = []
    nested_indent: int | None = None

    # 提取 source_loop 用
    loop_match = re.search(r"Loop(\d+)", md_path.stem)
    source_loop = int(loop_match.group(1)) if loop_match else None

    def flush_multiline():
        nonlocal multiline_field, multiline_lines, multiline_indent
        if multiline_field is None or current_entry is None:
            multiline_field = None
            multiline_lines = []
            multiline_indent = None
            return
        text = "\n".join(line.rstrip() for line in multiline_lines).strip()
        # 多行字符串通常是中文长描述，按 [zh, en] 数组存（保持与现有表一致）
        # 但若字段名是 words / Describe / ShortDescribe / testimony，按数组装
        if multiline_field in ("words", "Describe", "ShortDescribe", "testimony"):
            current_entry.fields[multiline_field] = [text]
        else:
            current_entry.fields[multiline_field] = text
        multiline_field = None
        multiline_lines = []
        multiline_indent = None

    def flush_nested():
        nonlocal nested_field, nested_items, nested_indent
        if nested_field is None or current_entry is None:
            nested_field = None
            nested_items = []
            nested_indent = None
            return
        current_entry.fields[nested_field] = nested_items
        nested_field = None
        nested_items = []
        nested_indent = None

    def flush_entry():
        nonlocal current_entry
        flush_multiline()
        flush_nested()
        if current_entry is not None:
            entries.append(current_entry)
        current_entry = None

    text = md_path.read_text(encoding="utf-8")
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()

        # 多行字符串累积
        if multiline_field is not None:
            if not stripped or line.startswith(" " * (multiline_indent or 4)):
                # 仍在多行块内
                if line.startswith(" " * (multiline_indent or 4)):
                    multiline_lines.append(line[(multiline_indent or 4):])
                else:
                    multiline_lines.append("")
                continue
            # 多行块结束
            flush_multiline()

        # 嵌套块累积（- key: value 缩进列表）
        if nested_field is not None:
            indent_match = re.match(r"^( *)", line)
            indent = len(indent_match.group(1)) if indent_match else 0
            if stripped and indent >= (nested_indent or 2):
                # 处理嵌套列表项
                m = re.match(r"^\s*-\s*(.*)$", line)
                if m:
                    item_body = m.group(1).strip()
                    # {key: val, key: val} 单行字典
                    if item_body.startswith("{") and item_body.endswith("}"):
                        try:
                            # 用宽松解析：把 key: val 转成 "key": "val"
                            parsed = parse_inline_dict(item_body)
                            nested_items.append(parsed)
                            continue
                        except Exception:
                            pass
                    # key: value 单字段（开始一个新子对象）
                    kv = re.match(r"^([\w_]+)\s*:\s*(.*)$", item_body)
                    if kv:
                        nested_items.append({kv.group(1): parse_md_value(kv.group(2))})
                        continue
                    # 纯 scalar 项
                    nested_items.append(parse_md_value(item_body))
                    continue
                # 后续 "  key: value" 行属于上一个嵌套子对象
                kv2 = re.match(r"^\s+([\w_]+)\s*:\s*(.*)$", line)
                if kv2 and nested_items and isinstance(nested_items[-1], dict):
                    nested_items[-1][kv2.group(1)] = parse_md_value(kv2.group(2))
                    continue
                continue
            else:
                flush_nested()

        if not stripped:
            continue

        # 表名
        if stripped.startswith("## "):
            flush_entry()
            tbl_name = stripped[3:].strip()
            # 去掉括号备注 "ChapterConfig (部分写入)"
            tbl_name = re.split(r"\s*[\(（]", tbl_name)[0].strip()
            if tbl_name in ALL_TABLES:
                current_table = tbl_name
            else:
                current_table = None  # 跳过未知表
            continue

        # 跳过一级标题
        if stripped.startswith("# "):
            continue

        # 条目
        if stripped.startswith("### "):
            flush_entry()
            if current_table is None:
                continue
            head = stripped[4:].strip()
            # "{id} - {中文名} / {英文名}" 或 "{id} - {desc}" 或 "{id}"
            parts = re.split(r"\s*[-–]\s*", head, maxsplit=1)
            id_part = parts[0].strip()
            desc_part = parts[1].strip() if len(parts) > 1 else ""
            if id_part == "待补充":
                continue
            current_entry = Entry(
                table=current_table, id=id_part, source_loop=source_loop
            )
            # 从描述拆 Name / sceneName（含 " / " 分隔符）
            if desc_part:
                name_parts = [p.strip() for p in re.split(r"\s+/\s+", desc_part)]
                if current_table in ("ItemStaticData", "NPCStaticData") and len(name_parts) >= 2:
                    current_entry.fields["Name"] = name_parts[:2]
                elif current_table == "SceneConfig" and len(name_parts) >= 2:
                    current_entry.fields["sceneName"] = name_parts[0]
                    current_entry.fields["sceneNameEn"] = name_parts[1]
            continue

        # 字段
        if current_entry is None:
            continue

        m = re.match(r"^- ([\w_]+)\s*:\s*(.*)$", line.lstrip())
        if not m:
            continue
        key = m.group(1)
        value_part = m.group(2).rstrip()

        # 多行字符串触发
        if value_part == "|":
            multiline_field = key
            multiline_lines = []
            multiline_indent = 4  # 默认 4 空格缩进
            continue

        # 嵌套结构触发（值为空，下面跟缩进列表）
        if value_part == "":
            nested_field = key
            nested_items = []
            nested_indent = 2  # "  - " 风格
            continue

        # _skip_fields 特殊处理
        if key == "_skip_fields":
            arr = parse_md_value(value_part)
            if isinstance(arr, list):
                current_entry.skip_fields = arr
            continue

        current_entry.fields[key] = parse_md_value(value_part)

    flush_entry()
    return entries


def parse_inline_dict(s: str) -> dict[str, Any]:
    """解析 `{key: val, key: val}` 形式。值不带引号也行。"""
    s = s.strip().lstrip("{").rstrip("}").strip()
    if not s:
        return {}
    out: dict[str, Any] = {}
    # 简单按逗号分（不支持嵌套）
    for kv in s.split(","):
        kv = kv.strip()
        if ":" not in kv:
            continue
        k, v = kv.split(":", 1)
        out[k.strip()] = parse_md_value(v.strip())
    return out


# ============================================================
# 字段后处理 / 引用展开
# ============================================================

ENTRY_INDEX: dict[tuple[str, str], Entry] = {}


def build_entry_index(entries: list[Entry]):
    ENTRY_INDEX.clear()
    for e in entries:
        ENTRY_INDEX[(e.table, str(e.id))] = e


def find_entry(table: str, eid: str) -> Entry | None:
    return ENTRY_INDEX.get((table, str(eid)))


def expand_npc_ref(npc_id: str, existing_npc_table: list[dict]) -> dict:
    """把 npc_ref 展开成内联完整 NPCStaticData 对象。优先用本次 MD 的 entry，否则查现表。"""
    e = find_entry("NPCStaticData", str(npc_id))
    if e:
        return entry_to_json(e)
    for n in existing_npc_table:
        if str(n.get("id")) == str(npc_id):
            return n
    # 找不到 → 占位
    return {"id": str(npc_id)}


def expand_doubt_refs(refs: list, existing_doubt_table: list[dict]) -> list[dict]:
    out = []
    for ref in refs:
        eid = str(ref)
        e = find_entry("DoubtConfig", eid)
        if e:
            out.append(entry_to_json(e))
            continue
        for d in existing_doubt_table:
            if str(d.get("id")) == eid:
                out.append(d)
                break
    return out


def expand_testimony_item_refs(refs: list, existing_ti_table: list[dict]) -> list[dict]:
    out = []
    for ref in refs:
        eid = str(ref)
        e = find_entry("TestimonyItem", eid)
        if e:
            out.append(entry_to_json(e))
            continue
        for t in existing_ti_table:
            if str(t.get("id")) == eid:
                out.append(t)
                break
    return out


def normalize_value(v: Any) -> Any:
    """JSON 写入前标准化：
    - 数字字段统一字符串化
    - 待补充 → 空字符串
    """
    if isinstance(v, list):
        return [normalize_value(x) for x in v]
    if isinstance(v, dict):
        return {k: normalize_value(x) for k, x in v.items()}
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if v is None:
        return ""
    if isinstance(v, str) and is_placeholder(v):
        return ""
    return v


def entry_to_json(entry: Entry, context_tables: dict[str, list] | None = None) -> dict:
    """把 Entry 翻译成 JSON 条目（不含与现表的合并）。"""
    ctx = context_tables or {}
    id_key = "sceneId" if entry.table == "SceneConfig" else "id"
    out: dict[str, Any] = {id_key: str(entry.id)}
    fields = dict(entry.fields)

    # 处理引用展开
    if entry.table == "Testimony":
        if "npc_ref" in fields:
            npc_ref = fields.pop("npc_ref")
            out["npc"] = expand_npc_ref(str(npc_ref), ctx.get("NPCStaticData", []))
        if "evidenceItem_refs" in fields:
            refs = fields.pop("evidenceItem_refs")
            if isinstance(refs, str):
                refs = [refs]
            out["evidenceItem"] = expand_testimony_item_refs(
                refs, ctx.get("TestimonyItem", [])
            )

    if entry.table == "ChapterConfig":
        if "doubts_ref" in fields:
            refs = fields.pop("doubts_ref")
            if isinstance(refs, str):
                refs = [refs]
            out["doubts"] = expand_doubt_refs(refs, ctx.get("DoubtConfig", []))

    if entry.table == "SceneConfig":
        # NPCInfos: list of {npc_ref, instance_id, ResPath, ClickResPath, PosX, Posy, PosZ}
        if "NPCInfos" in fields:
            raw = fields.pop("NPCInfos")
            npc_infos = []
            if isinstance(raw, list):
                # 把 list of {fragmentary dict} 合并成 NPCInfo 对象
                # 解析约定：单个 NPCInfo 子对象由多行 dict 项合并而成
                # 实际 MD 风格是 `- npc_ref: 301` 后跟若干缩进字段
                # parse_loop_md 把它们装在同一个 dict 里了（见 nested 累积逻辑）
                for item in raw:
                    if not isinstance(item, dict):
                        continue
                    npc_id = item.get("npc_ref")
                    inst_id = item.get("instance_id")
                    npc_obj = expand_npc_ref(
                        str(npc_id), ctx.get("NPCStaticData", [])
                    ) if npc_id else {}
                    info = {
                        "id": str(inst_id) if inst_id else "",
                        "NPC": npc_obj,
                        "TalkInfo": {},
                        "LoopTalkInfo": {},
                        "ResPath": str(item.get("ResPath", "")),
                        "ClickResPath": str(item.get("ClickResPath", "")),
                        "PosX": str(item.get("PosX", "")),
                        "Posy": str(item.get("Posy", "")),
                        "PosZ": str(item.get("PosZ", "")),
                    }
                    npc_infos.append(info)
            out["NPCInfos"] = npc_infos

        # ItemIDs 数组转字符串
        if "ItemIDs" in fields:
            raw = fields.pop("ItemIDs")
            if isinstance(raw, list):
                out["ItemIDs"] = [str(x) for x in raw]
            elif isinstance(raw, str):
                out["ItemIDs"] = []

    # 复制其他字段
    for k, v in fields.items():
        out[k] = normalize_value(v)

    return out


# ============================================================
# 合并写入
# ============================================================


def load_existing_table(table: str) -> list[dict]:
    path = TABLE_DIR / f"{table}.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def merge_partial_preserve(
    table: str, new_entry: dict, existing_entry: dict | None
) -> dict:
    """部分写入表：保留 existing 中跳过字段的值。"""
    preserve = PARTIAL_PRESERVE_FIELDS.get(table, set())
    if not existing_entry:
        # 新增 → 跳过字段留空
        for f in preserve:
            new_entry.setdefault(f, "" if "Bg" in f or "Talk" in f or "Npc" in f else [])
        return new_entry
    out = dict(existing_entry)
    for k, v in new_entry.items():
        out[k] = v
    return out


def merge_scene_npcinfos(new_scene: dict, existing_scene: dict | None) -> dict:
    """SceneConfig.NPCInfos：保留现有条目里的 TalkInfo / LoopTalkInfo（避免覆盖 sync_to_json 写的）。"""
    if not existing_scene:
        return new_scene
    new_infos = new_scene.get("NPCInfos", [])
    old_infos = existing_scene.get("NPCInfos", [])
    if not new_infos or not old_infos:
        return new_scene
    old_by_id = {str(o.get("id")): o for o in old_infos if isinstance(o, dict)}
    merged = []
    for ni in new_infos:
        if not isinstance(ni, dict):
            merged.append(ni)
            continue
        oid = str(ni.get("id", ""))
        old = old_by_id.get(oid)
        if old:
            # 保留 TalkInfo / LoopTalkInfo（如果新条目里是空对象）
            for talk_field in ("TalkInfo", "LoopTalkInfo"):
                if not ni.get(talk_field) and old.get(talk_field):
                    ni[talk_field] = old[talk_field]
        merged.append(ni)
    new_scene["NPCInfos"] = merged
    return new_scene


def merge_table(
    table: str, unit: int, new_entries_json: list[dict]
) -> tuple[list[dict], dict]:
    """合并单表。返回 (新表内容, diff 摘要)。"""
    existing = load_existing_table(table)
    existing_by_id = {str(e.get("id") or e.get("sceneId") or e.get("chapterId")): e for e in existing}

    diff = {"added": [], "updated": [], "unchanged": [], "preserved_other_units": 0}

    # 收集本 Unit 段已存在的 ID（用于"删除"判断，但本 skill 不做主动删，用户手动）
    new_by_id = {str(e.get("id") or e.get("sceneId") or e.get("chapterId")): e for e in new_entries_json}

    # 输出表：先放非本 Unit 的旧条目，再放本 Unit 的新条目
    final = []
    seen = set()
    for e in existing:
        eid = str(e.get("id") or e.get("sceneId") or e.get("chapterId"))
        e_unit = unit_of(table, eid)
        if e_unit == unit:
            # 本 Unit 段：等下用新条目替换
            continue
        if e_unit is None and eid in new_by_id:
            # 表无 Unit 维度（如跨 Unit NPC）：MD 里指定的算更新
            continue
        final.append(e)
        seen.add(eid)
        if e_unit != unit:
            diff["preserved_other_units"] += 1

    for ne in new_entries_json:
        nid = str(ne.get("id") or ne.get("sceneId") or ne.get("chapterId"))
        old = existing_by_id.get(nid)

        # 应用部分写入合并
        if table in TABLES_PARTIAL_WRITE:
            ne = merge_partial_preserve(table, ne, old)

        # SceneConfig 特殊：保留旧 TalkInfo
        if table == "SceneConfig":
            ne = merge_scene_npcinfos(ne, old)

        if old is None:
            diff["added"].append(nid)
        elif json.dumps(old, sort_keys=True, ensure_ascii=False) == json.dumps(
            ne, sort_keys=True, ensure_ascii=False
        ):
            diff["unchanged"].append(nid)
        else:
            diff["updated"].append(nid)
        final.append(ne)

    # 按 ID 升序排序
    def sort_key(e):
        try:
            return (0, int(e.get("id") or e.get("sceneId") or e.get("chapterId") or 0))
        except (TypeError, ValueError):
            return (1, str(e.get("id") or e.get("sceneId") or e.get("chapterId") or ""))

    final.sort(key=sort_key)
    return final, diff


# ============================================================
# 主流程
# ============================================================


def parse_unit_drafts(unit: int) -> list[Entry]:
    draft_dir = DRAFT_ROOT / f"Unit{unit}"
    if not draft_dir.exists():
        print(f"[ERR] 草稿目录不存在: {draft_dir}", file=sys.stderr)
        sys.exit(1)
    md_files = sorted(draft_dir.glob("Loop*.md"))
    if not md_files:
        print(f"[ERR] {draft_dir} 下没有 Loop*.md", file=sys.stderr)
        sys.exit(1)
    all_entries: list[Entry] = []
    for md in md_files:
        print(f"[parse] {md.relative_to(PROJECT_ROOT)}")
        try:
            entries = parse_loop_md(md)
        except Exception as e:
            print(f"[ERR] 解析失败 {md}: {e}", file=sys.stderr)
            sys.exit(1)
        all_entries.extend(entries)
    return all_entries


def group_by_table(entries: list[Entry]) -> dict[str, list[Entry]]:
    out: dict[str, list[Entry]] = {t: [] for t in ALL_TABLES}
    for e in entries:
        if e.table not in out:
            out[e.table] = []
        out[e.table].append(e)
    return out


def build_context(entries_by_table: dict[str, list[Entry]]) -> dict[str, list[dict]]:
    """加载现有所有表，给引用展开用。"""
    ctx = {}
    for t in ALL_TABLES:
        ctx[t] = load_existing_table(t)
    return ctx


def main():
    ap = argparse.ArgumentParser(description="MD 草稿 → preview table JSON 合并")
    ap.add_argument("unit", help="Unit 编号，如 Unit3 或 3")
    ap.add_argument("--dry-run", action="store_true", help="只输出计划，不写文件")
    ap.add_argument("--tables", help="逗号分隔，限定只处理指定表")
    args = ap.parse_args()

    # 解析 Unit
    unit_str = args.unit.replace("Unit", "").strip()
    try:
        unit = int(unit_str)
    except ValueError:
        print(f"[ERR] 无法解析 Unit 编号: {args.unit}", file=sys.stderr)
        sys.exit(1)

    target_tables = ALL_TABLES
    if args.tables:
        target_tables = [t.strip() for t in args.tables.split(",") if t.strip()]
        unknown = [t for t in target_tables if t not in ALL_TABLES]
        if unknown:
            print(f"[ERR] 未知表: {unknown}。允许: {ALL_TABLES}", file=sys.stderr)
            sys.exit(1)

    # 解析全部 Loop MD
    entries = parse_unit_drafts(unit)
    build_entry_index(entries)
    by_table = group_by_table(entries)
    ctx = build_context(by_table)

    # 转换 + 合并
    overall_diff = {}
    new_tables = {}
    for tbl in target_tables:
        entries_in_tbl = by_table.get(tbl, [])
        if not entries_in_tbl:
            print(f"[skip] {tbl}: MD 中无条目")
            continue
        new_json = [entry_to_json(e, ctx) for e in entries_in_tbl]
        merged, diff = merge_table(tbl, unit, new_json)
        new_tables[tbl] = merged
        overall_diff[tbl] = diff
        print(
            f"[plan] {tbl}: +{len(diff['added'])} 新增 / "
            f"~{len(diff['updated'])} 更新 / "
            f"={len(diff['unchanged'])} 不变 / "
            f"keep {diff['preserved_other_units']} 其他Unit条目"
        )

    if args.dry_run:
        print("\n=== DRY-RUN：未写入任何文件 ===")
        for tbl, diff in overall_diff.items():
            if diff["added"]:
                print(f"  {tbl} 新增 IDs: {diff['added'][:20]}{'...' if len(diff['added']) > 20 else ''}")
            if diff["updated"]:
                print(f"  {tbl} 更新 IDs: {diff['updated'][:20]}{'...' if len(diff['updated']) > 20 else ''}")
        sys.exit(0)

    # 实际写入 + 自校验
    for tbl, content in new_tables.items():
        path = TABLE_DIR / f"{tbl}.json"
        tmp_path = path.with_suffix(".json.tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
        # 自校验
        try:
            with tmp_path.open("r", encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            print(f"[ERR] 校验失败 {path}: {e}", file=sys.stderr)
            tmp_path.unlink(missing_ok=True)
            sys.exit(1)
        # 原子替换
        tmp_path.replace(path)
        print(f"[write] {path.relative_to(PROJECT_ROOT)} ({len(content)} 条)")

    print("\n=== 写入完成 ===")
    for tbl, diff in overall_diff.items():
        print(
            f"  {tbl}: +{len(diff['added'])} ~{len(diff['updated'])} ={len(diff['unchanged'])}"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
