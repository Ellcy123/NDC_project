#!/usr/bin/env python3
"""
build_report.py — 把 .audit/{Unit}/ 下的审计结果聚合成 HTML 报告。

用法:
    python build_report.py <Unit号>

例如:
    python build_report.py Unit9

读取:
    .audit/{Unit}/verified.jsonl
    .audit/{Unit}/needs_human.jsonl
    .audit/{Unit}/dismissed.jsonl
    .audit/{Unit}/facts/*.json (用于展开违规上下文)
    .audit/{Unit}/scope.json

输出:
    audit-reports/{Unit}_consistency_{YYYYMMDD}/index.html
    audit-reports/{Unit}_consistency_{YYYYMMDD}/styles.css
"""
from __future__ import annotations

import datetime
import html
import json
import shutil
import sys
from pathlib import Path

DIM_NAMES = {
    "A": "A 人物档案",
    "B": "B 称谓",
    "C": "C 时间线",
    "D": "D 物证",
    "E": "E 年代用语",
    "F": "F 声纹",
    "G": "G 多视角",
    "X": "X 对话兜底",
}
DIM_PRIORITY = ["C", "G", "A", "B", "D", "F", "E", "X"]
SEV_RANK = {"P0": 0, "P1": 1, "P2": 2, "needs_human": 3, "unverified": 1}
SEV_NAMES = {
    "P0": "P0 严重",
    "P1": "P1 中度",
    "P2": "P2 轻微",
    "needs_human": "待定",
    "unverified": "未复核",
}


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as exc:
            print(f"  ⚠️  跳过格式错误行 in {path.name}: {exc}", file=sys.stderr)
    return out


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"  ⚠️  跳过格式错误 JSON {path.name}: {exc}", file=sys.stderr)
        return {}


def derive_dim(issue: dict) -> str:
    dim = issue.get("_dim") or issue.get("dim")
    if dim and dim in DIM_NAMES:
        return dim
    src = str(issue.get("_source_file", ""))
    for k in DIM_NAMES:
        if f"/{k}-" in src or f"\\{k}-" in src:
            return k
    return "X"


def derive_loop(issue: dict) -> str:
    loop = issue.get("loop")
    if loop and isinstance(loop, str) and loop.startswith("L"):
        return loop
    if loop and isinstance(loop, int):
        return f"L{loop}"
    lid = str(issue.get("line_id", ""))
    if lid and lid[0].isdigit():
        return f"L{lid[0]}"
    return "?"


def derive_sev(issue: dict, status: str = "verified") -> str:
    if status == "needs_human":
        return "needs_human"
    sev = issue.get("severity", "P2")
    if sev not in SEV_RANK:
        return "P2"
    return sev


def render_issue_card(issue: dict, status: str = "verified") -> str:
    dim = derive_dim(issue)
    sev = derive_sev(issue, status)
    loop = derive_loop(issue)

    speaker = issue.get("speaker") or issue.get("npc") or ""
    file_path = issue.get("file", "")
    line_id = issue.get("line_id", "")
    type_str = issue.get("type", "")
    text_excerpt = issue.get("text") or issue.get("claim_in_dialogue") or ""
    suggestion = issue.get("suggestion", "")
    verdict_reason = issue.get("verdict_reason", "") or issue.get("dismissal_reason", "")

    fact_excerpt = issue.get("fact_in_table") or issue.get("rule_violated") or issue.get("expected_voice") or issue.get("expected_form") or ""
    if isinstance(fact_excerpt, (dict, list)):
        fact_excerpt = json.dumps(fact_excerpt, ensure_ascii=False)

    speaker_html = f'<div class="speaker"><strong>{html.escape(str(speaker))}</strong></div>' if speaker else ""
    text_html = f'<div class="claim">{html.escape(str(text_excerpt))}</div>' if text_excerpt else ""
    fact_html = f'<div class="fact">违反: {html.escape(str(fact_excerpt))}</div>' if fact_excerpt else ""
    suggestion_html = f'<div class="suggestion">{html.escape(str(suggestion))}</div>' if suggestion else ""
    verdict_html = f'<div class="verdict-reason">复核备注: {html.escape(str(verdict_reason))}</div>' if verdict_reason else ""

    raw_json = html.escape(json.dumps(issue, ensure_ascii=False, indent=2))

    file_loc = f"{file_path}#{line_id}" if line_id else file_path

    return f'''<article class="issue" data-sev="{sev}" data-dim="{dim}" data-loop="{loop}">
  <header>
    <span class="badge sev-{sev}">{html.escape(SEV_NAMES.get(sev, sev))}</span>
    <span class="badge dim">{html.escape(DIM_NAMES.get(dim, dim))}</span>
    <span class="badge loop">{html.escape(loop)}</span>
    <span class="file">{html.escape(file_loc)}</span>
  </header>
  <div class="type-line">类型: <span class="type">{html.escape(str(type_str))}</span></div>
  {speaker_html}
  {text_html}
  {fact_html}
  {suggestion_html}
  {verdict_html}
  <details class="raw-toggle"><summary>原始 JSON</summary><pre class="raw">{raw_json}</pre></details>
</article>'''


def sort_key(item):
    issue, status = item
    sev = derive_sev(issue, status)
    dim = derive_dim(issue)
    loop = derive_loop(issue)
    return (
        SEV_RANK.get(sev, 99),
        DIM_PRIORITY.index(dim) if dim in DIM_PRIORITY else 99,
        loop,
    )


def gather_meta_conflicts(facts: dict) -> list[dict]:
    """Walk fact tables looking for _conflict markers."""
    conflicts = []
    for table_name, content in facts.items():
        def walk(obj, path):
            if isinstance(obj, dict):
                if "_conflict" in obj:
                    conflicts.append({
                        "_dim": "META",
                        "table": table_name,
                        "path": " / ".join(str(p) for p in path),
                        "type": "fact_table_conflict",
                        "severity": "P1",
                        "details": obj["_conflict"],
                    })
                for k, v in obj.items():
                    if k != "_conflict":
                        walk(v, path + [k])
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    walk(v, path + [i])
        walk(content, [])
    return conflicts


def render_meta_card(meta: dict) -> str:
    details = meta.get("details", "")
    if isinstance(details, (dict, list)):
        details = json.dumps(details, ensure_ascii=False)
    return f'''<article class="issue" data-sev="P1" data-dim="X" data-loop="?">
  <header>
    <span class="badge sev-P1">事实表冲突</span>
    <span class="file">{html.escape(meta.get("table", ""))} :: {html.escape(meta.get("path", ""))}</span>
  </header>
  <div class="claim">{html.escape(str(details))}</div>
</article>'''


def main():
    if len(sys.argv) < 2:
        print("用法: python build_report.py <Unit号>", file=sys.stderr)
        sys.exit(1)

    unit = sys.argv[1]
    audit_dir = Path(f".audit/{unit}")
    if not audit_dir.exists():
        print(f"❌ 找不到审计目录: {audit_dir}", file=sys.stderr)
        sys.exit(1)

    today = datetime.date.today().strftime("%Y%m%d")
    report_dir = Path(f"audit-reports/{unit}_consistency_{today}")
    report_dir.mkdir(parents=True, exist_ok=True)

    verified = load_jsonl(audit_dir / "verified.jsonl")
    needs_human = load_jsonl(audit_dir / "needs_human.jsonl")
    dismissed = load_jsonl(audit_dir / "dismissed.jsonl")

    # 加载事实表
    facts = {}
    facts_dir = audit_dir / "facts"
    if facts_dir.exists():
        for f in facts_dir.glob("*.json"):
            facts[f.stem] = load_json(f)

    # 找 meta 冲突
    meta_conflicts = gather_meta_conflicts(facts)

    # 主 issue 列表（verified + needs_human）
    main_items = [(i, "verified") for i in verified] + [(i, "needs_human") for i in needs_human]
    main_items.sort(key=sort_key)
    main_cards = "\n".join(render_issue_card(i, s) for i, s in main_items)

    # 已驳回
    dismissed_cards = "\n".join(render_issue_card(i, "dismissed") for i in dismissed)

    # 事实表冲突
    meta_cards = "\n".join(render_meta_card(m) for m in meta_conflicts)

    # 摘要
    scope = load_json(audit_dir / "scope.json")
    summary_items = []
    summary_items.append(f'<span><span class="k">扫描时间:</span><span class="v">{datetime.datetime.now():%Y-%m-%d %H:%M}</span></span>')
    if scope:
        summary_items.append(f'<span><span class="k">EPI:</span><span class="v">{scope.get("epi", "?")}</span></span>')
        summary_items.append(f'<span><span class="k">对话文件:</span><span class="v">{len(scope.get("dialogue_files", []))}</span></span>')
    p0 = sum(1 for i in verified if derive_sev(i) == "P0")
    p1 = sum(1 for i in verified if derive_sev(i) == "P1")
    p2 = sum(1 for i in verified if derive_sev(i) == "P2")
    summary_items.append(f'<span><span class="k">P0:</span><span class="v">{p0}</span></span>')
    summary_items.append(f'<span><span class="k">P1:</span><span class="v">{p1}</span></span>')
    summary_items.append(f'<span><span class="k">P2:</span><span class="v">{p2}</span></span>')
    summary_items.append(f'<span><span class="k">待定:</span><span class="v">{len(needs_human)}</span></span>')
    summary_items.append(f'<span><span class="k">已驳回:</span><span class="v">{len(dismissed)}</span></span>')
    summary_items.append(f'<span><span class="k">事实表:</span><span class="v">{", ".join(facts.keys()) or "(空)"}</span></span>')
    summary_html = "\n  ".join(summary_items)

    # 渲染
    template_path = Path(__file__).parent / "_base.html"
    template = template_path.read_text(encoding="utf-8")
    final = (template
        .replace("{{UNIT}}", html.escape(unit))
        .replace("{{SUMMARY}}", summary_html)
        .replace("{{ISSUES}}", main_cards or '<p style="color:#888">没有 issue。</p>')
        .replace("{{DISMISSED}}", dismissed_cards or '<p style="color:#888">无</p>')
        .replace("{{META_CONFLICTS}}", meta_cards or '<p style="color:#888">无</p>')
        .replace("{{DISMISSED_COUNT}}", str(len(dismissed)))
        .replace("{{META_COUNT}}", str(len(meta_conflicts)))
        .replace("{{TIMESTAMP}}", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    (report_dir / "index.html").write_text(final, encoding="utf-8")

    # 复制 styles.css
    src_css = Path(__file__).parent / "styles.css"
    if src_css.exists():
        shutil.copy(src_css, report_dir / "styles.css")

    print(f"✅ 报告已生成: {report_dir / 'index.html'}")
    print(f"   verified={len(verified)} needs_human={len(needs_human)} dismissed={len(dismissed)} meta_conflicts={len(meta_conflicts)}")


if __name__ == "__main__":
    main()
