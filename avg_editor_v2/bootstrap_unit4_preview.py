#!/usr/bin/env python3
"""Build and merge Unit4 preview rows into avg_editor_v2 table snapshots.

The editor tables remain the preview source of truth.  This script is an
idempotent bootstrap/import helper for the first Unit4 snapshot; it does not
write Unity tables and it never touches rows outside the EPI04/4xxx scope.
"""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

import yaml


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
STATE_DIR = REPO_ROOT / "剧情设计" / "Unit4" / "state"
SCENE_DOC_DIR = REPO_ROOT / "剧情设计" / "Unit4" / "场景"
EVIDENCE_ART_DIR = REPO_ROOT / "剧情设计" / "Unit4" / "证据设计"
EXPLORE_DOC_DIR = SCENE_DOC_DIR / "探索场景"
AVG_DOC_DIR = SCENE_DOC_DIR / "AVG场景"
TABLE_DIR = HERE / "data" / "table"
EPISODE = "EPI04"

AVG_SCENE_DOCS: dict[str, list[str]] = {
    "4001": ["AVG_L1_开篇_法院东翼_封锁.md"],
    "4002": ["AVG_L1_Harrison外间办公室_指证后开柜.md"],
    "4016": ["AVG_L2_法院预审法庭_下午.md"],
    "4021": ["AVG_L3_开篇_Zack事务所_深夜来电.md"],
    "4023": ["AVG_L3_Morrison宅邸门口_指证后.md"],
    "4029": ["AVG_L3_开篇_Morrison宅邸门外_抵达.md"],
    "4031": ["AVG_L4_开篇_Zack事务所_对质与清退通知.md"],
    "4035": ["AVG_L4_衔接_OHara家后巷_井检口.md"],
    "4041": ["AVG_L5_开篇_四十二层外厅_抵达.md"],
    "4042": ["AVG_L5_高潮_Mickey办公室_坠落与救援.md"],
    "4043": [
        "AVG_L5_终幕_大楼楼梯与停车区_撤离.md",
        "AVG_L5_终幕_法院档案车内_离开.md",
    ],
    "4044": ["AVG_L5_终幕_法院档案车内_拆阅档案.md"],
    "4045": ["AVG_L5_终幕_南区街道_OHara门外.md"],
}


NPC_DEFS: dict[str, dict[str, str]] = {
    "401": {"name": "Zack Brennan", "role": "4", "file": "zack.md", "icon": "zack_brennan", "asset": "Zack"},
    "402": {"name": "Emma O'Malley", "role": "4", "file": "emma.md", "icon": "emma_o_malley", "asset": "Emma"},
    "403": {"name": "Mickey Donnelly", "role": "2", "file": "mickey.md", "icon": "mickey_donnelly", "asset": "Mickey"},
    "404": {"name": "Watts", "role": "2", "file": "watts.md", "icon": "watts", "asset": "Watts"},
    "405": {"name": "Harold Morrison", "role": "1", "file": "harold_morrison.md", "icon": "morrison", "asset": "Morrison"},
    "406": {"name": "Doris Morrison", "role": "2", "file": "doris_morrison.md", "icon": "mrsmorrison", "asset": "Doris"},
    "407": {"name": "Rosa Martinez", "role": "3", "file": "rosa.md", "icon": "rosa", "asset": "Rosa"},
    "408": {"name": "Eleanor Foster", "role": "3", "file": "foster.md", "icon": "foster", "asset": "Foster"},
    "409": {"name": "Whitfield", "role": "2", "file": "whitfield.md", "icon": "whitfield", "asset": "Whitfield"},
    "410": {"name": "Margaret Brennan", "role": "2", "file": "margaret.md", "icon": "margaret_brennan", "asset": "Margaret"},
    "411": {"name": "Mrs. O'Hara", "role": "3", "file": "ohara.md", "icon": "ohara", "asset": "OHara"},
    "412": {"name": "Pierce", "role": "3", "file": "pierce.md", "icon": "pierce", "asset": "Pierce"},
    "413": {"name": "Judge Harrison", "role": "1", "file": "harrison.md", "icon": "harrison", "asset": "Harrison"},
    "414": {"name": "Sarah", "role": "3", "file": "sarah.md", "icon": "sarah", "asset": "Sarah"},
    "415": {"name": "夜班电话接线员", "role": "3", "file": "telephone_operator.md", "icon": "telephone_operator", "asset": "Operator"},
    "416": {"name": "法院档案管理员", "role": "3", "file": "court_archivist.md", "icon": "court_archivist", "asset": "Archivist"},
    "417": {
        "name": "社会服务部调档员",
        "role": "3",
        "file": "social_service_records_clerk.md",
        "icon": "social_service_records_clerk",
        "asset": "RecordsClerk",
        "art": (
            "【Unit4 人物美术需求】社会服务部调档员\n"
            "- 中年女性，简单盘发，浅色立领衬衣搭配深色行政工作外套；不得穿医生白大褂、护士服或护士帽。\n"
            "- 场景立绘三态：柜台办公、离场、扶住木质档案车返回；角色与档案车分层制作。\n"
            "- 非重要 NPC，不要求完整行走动画；办公姿态与推车姿态配合位移即可。\n"
            "- 对话头像由头顶裁至衣领，提供日常办公、察觉病历异常两个表情状态。\n"
            "- 资源：social_service_records_clerk_small / social_service_records_clerk_big。"
        ),
    },
    "418": {
        "name": "退休法官",
        "role": "3",
        "file": "retired_judge.md",
        "icon": "retired_judge",
        "asset": "RetiredJudge",
        "art": (
            "【Unit4 人物美术需求】退休法官\n"
            "- 独立角色资产，不与书记员、法警、法院路人或其他法官共用。\n"
            "- 年长、保守、稳重，熟悉庭审程序；始终单独位于固定法官席。\n"
            "- 需要独立角色立绘与庭审发言状态。\n"
            "- 不使用 Harrison 的个人特征，避免被误认为同一人或亲属。\n"
            "- 资源：retired_judge_small / retired_judge_big。"
        ),
    },
    "419": {
        "name": "记者群像",
        "role": "3",
        "file": "reporter_crowd.md",
        "icon": "reporter_crowd",
        "asset": "ReporterCrowd",
        "art": (
            "【Unit4 人物美术需求】记者群像（记者 A / B / C）\n"
            "- 三名发言位共用一套基础单人立绘和一个 NPC 配置，不拆成三套基础角色资产。\n"
            "- A 使用带 PRESS 卡的窄檐记者帽；B 使用 1928 年式折叠皮腔新闻相机；C 使用衣领高位的垂挂式 PRESS 证章。\n"
            "- 三种配饰必须在头顶至衣领的头像裁切内可辨；不得出现现代麦克风、监听耳机、塑料证件套或电子闪光灯。\n"
            "- 场景层始终表现记者群像整体行动；右侧对话框只切换当前发言者及其单一配饰。\n"
            "- 资源：reporter_crowd_small / reporter_crowd_big，另需 A/B/C 三种配饰层。"
        ),
    },
}

SPECIAL_ASSET_DISPOSITIONS = {
    **{
        str(evidence_id): (
            "minigame",
            "CASE BOARD 小玩法专用资源，普通道具图片不适用",
        )
        for evidence_id in range(4704, 4710)
    },
    "4516": (
        "narrative_discovery",
        "剧情发现，不作为玩家可操作道具",
    ),
}

NPC_TOKEN_TO_ID = {
    "watts": "404",
    "harold": "405",
    "archivist": "416",
    "clerk": "417",
    "rosa": "407",
    "foster": "408",
    "whitfield": "409",
    "mickey": "403",
    "doris": "406",
    "operator": "415",
    "ohara": "411",
    "sarah": "414",
    "margaret": "410",
}

LOOP_TITLES = {
    1: "Harrison 的秘密调查",
    2: "十三日红线",
    3: "Harold 的最后一夜",
    4: "Patrick 留下的选择",
    5: "四十二层",
}

EXPOSE_SCENES = {1: "4002", 2: "4016", 3: "4023", 4: "4034", 5: "4042"}
EXPOSE_NPCS = {1: "404", 2: "409", 3: "406", 4: "410", 5: "403"}
EXPLORATION_ENTRY_SCENES = {1: "4002", 2: "4011", 3: "4027", 4: "4032", 5: "4042"}


def as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return "；".join(as_text(v) for v in value if as_text(v))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return str(value).strip()


def load_states() -> dict[int, dict[str, Any]]:
    states: dict[int, dict[str, Any]] = {}
    for loop in range(1, 6):
        path = STATE_DIR / f"loop{loop}_state.yaml"
        with path.open("r", encoding="utf-8") as handle:
            states[loop] = yaml.safe_load(handle)
    return states


def markdown_sections(path: Path) -> tuple[str, dict[str, list[str]]]:
    title = ""
    current = ""
    sections: dict[str, list[str]] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        if current and line:
            sections[current].append(line)
    return title, sections


def clean_markdown(value: str) -> str:
    value = value.strip().strip("|").strip()
    value = re.sub(r"[`*]+", "", value)
    value = re.sub(r"^[-*]\s+", "", value)
    value = re.sub(r"^\d+[.)]\s+", "", value)
    return re.sub(r"\s+", " ", value).strip()


def clean_art_block(value: str) -> str:
    """Keep numbered/bulleted layout while removing Markdown-only emphasis."""
    lines: list[str] = []
    for raw_line in value.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        lines.append(re.sub(r"[`*]+", "", line))
    return "\n".join(lines)


def bilingual_card_fields(body: str, field: str) -> list[tuple[str, list[str]]]:
    """Extract bilingual `Field` pairs, including named variants such as 爆炸前."""
    if field == "Name":
        matches = re.finditer(
            r"- `Name`：`([^`]*)`\s*/\s*`([^`]*)`",
            body,
        )
        return [("", [match.group(1).strip(), match.group(2).strip()]) for match in matches]
    matches = re.finditer(
        rf"- `({re.escape(field)}(?:（([^）]+)）)?)`：\s*\n"
        r"\s*`([^`]*)`\s*\n\s*`([^`]*)`",
        body,
    )
    return [
        (match.group(2) or "", [match.group(3).strip(), match.group(4).strip()])
        for match in matches
    ]


def load_evidence_art_cards(expected_ids: set[str]) -> dict[str, dict[str, Any]]:
    """Load the 56 formal evidence production cards used by the preview item table."""
    cards: dict[str, dict[str, Any]] = {}
    for path in sorted(EVIDENCE_ART_DIR.glob("Unit4_*.md")):
        text = path.read_text(encoding="utf-8")
        headings = list(re.finditer(r"(?m)^###\s+(\d{4})\s+-\s+(.+?)\s*$", text))
        for index, heading in enumerate(headings):
            evidence_id = heading.group(1)
            if evidence_id not in expected_ids:
                continue
            if evidence_id in cards:
                raise ValueError(f"duplicate evidence art card: {evidence_id}")
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            body = text[heading.start():end]
            names = bilingual_card_fields(body, "Name")
            descriptions = bilingual_card_fields(body, "Describe")
            short_descriptions = bilingual_card_fields(body, "ShortDescribe")
            must = re.search(
                r"重点（信息表达必不可少）：\s*\n(.*?)(?=\n美术参考（不影响推理）：)",
                body,
                re.S,
            )
            reference = re.search(
                r"美术参考（不影响推理）：\s*\n(.*?)(?=\n---|\n## |\Z)",
                body,
                re.S,
            )
            if len(names) != 1 or not descriptions or not short_descriptions or not must or not reference:
                raise ValueError(f"incomplete evidence art card: {evidence_id} ({path.name})")
            if any(not value for _, pair in names + descriptions + short_descriptions for value in pair):
                raise ValueError(f"empty bilingual field in evidence art card: {evidence_id}")

            description_by_variant = {variant: pair for variant, pair in descriptions}
            short_by_variant = {variant: pair for variant, pair in short_descriptions}
            if set(description_by_variant) != set(short_by_variant):
                raise ValueError(f"description state mismatch in evidence art card: {evidence_id}")
            primary_variant = "爆炸前" if "爆炸前" in description_by_variant else descriptions[0][0]
            variants = [
                {
                    "key": variant or "default",
                    "label": variant or "默认",
                    "Describe": pair,
                    "ShortDescribe": short_by_variant[variant],
                }
                for variant, pair in descriptions
            ]
            cards[evidence_id] = {
                "Name": names[0][1],
                "Describe": description_by_variant[primary_variant],
                "ShortDescribe": short_by_variant[primary_variant],
                "ArtRequirement": (
                    "【信息表达必不可少】\n"
                    f"{clean_art_block(must.group(1))}\n"
                    "【风格参考】\n"
                    f"{clean_art_block(reference.group(1))}"
                ),
                "variants": variants,
            }

    missing = sorted(expected_ids - set(cards), key=int)
    if missing:
        raise ValueError(f"missing evidence art cards: {', '.join(missing)}")
    return cards


def section_fragments(lines: list[str]) -> list[str]:
    fragments: list[str] = []
    for line in lines:
        if line.startswith("|"):
            cells = [clean_markdown(cell) for cell in line.strip("|").split("|")]
            if not cells or all(re.fullmatch(r":?-{2,}:?", cell or "-") for cell in cells):
                continue
            if cells[:2] in (["交互点", "内容"], ["阶段", "表现"], ["状态", "内容"]):
                continue
            text = "：".join(cell for cell in cells if cell)
        else:
            text = clean_markdown(line)
        if text and text not in fragments:
            fragments.append(text)
    return fragments


def section_text(sections: dict[str, list[str]], *names: str) -> str:
    parts: list[str] = []
    for name in names:
        for fragment in section_fragments(sections.get(name, [])):
            if fragment not in parts:
                parts.append(fragment)
    return "；".join(parts)


def section_info(sections: dict[str, list[str]]) -> dict[str, str]:
    info: dict[str, str] = {}
    for line in sections.get("场景信息", []):
        match = re.match(r"^-\s*([^：]+)：\s*(.+)$", line)
        if match:
            info[clean_markdown(match.group(1))] = clean_markdown(match.group(2))
    return info


def evidence_anchor_text(raw: dict[str, Any]) -> str:
    anchors = []
    for evidence in raw.get("evidence") or []:
        evidence_id = str(evidence.get("id") or "").strip()
        name = str(evidence.get("name") or "").strip()
        if evidence_id or name:
            anchors.append(" ".join(part for part in (evidence_id, name) if part))
    return "；".join(anchors) or "无独立可拾取物品"


def explore_art_requirement(scene_id: str, name: str, loop: int, raw: dict[str, Any], path: Path) -> str:
    title, sections = markdown_sections(path)
    info = section_info(sections)
    screen_fragments = section_fragments(sections.get("画面与交互", []))
    scene_reference = screen_fragments[0] if screen_fragments else as_text(raw.get("description"))
    screen_focus = "；".join(screen_fragments) or as_text(raw.get("description"))
    state_text = section_text(sections, "人物与状态", "状态与边界", "状态边界")
    phase_text = section_text(sections, "交互阶段", "运行阶段与衔接", "保险柜内容", "保险柜内部", "身份锁落点", "运行阶段与人物站位")
    art_text = section_text(sections, "美术重点")
    time_version = info.get("时段") or next(
        (token for token in ("凌晨", "清晨", "深夜", "夜晚", "下午", "白天") if token in title),
        "按剧情时段",
    )
    lines = [
        f"【探索场景底图】{name}",
        f"- 时间版本：{time_version}版；背景资源：{info.get('内部英文名', f'u4_scene_{scene_id}')}",
        f"- 资产性质：{info.get('类型', '探索')}场景底图，人物与场景分离，不合成人物",
        f"- 场景参考：{scene_reference}",
        f"- 画面重点：{screen_focus}",
        f"- Loop/状态：L{loop}" + (f"；{state_text}" if state_text else ""),
        f"- 关键道具锚点（复用底图汇总）：{evidence_anchor_text(raw)}",
    ]
    if phase_text:
        lines.append(f"- 交互与分层说明：{phase_text}")
    if art_text:
        lines.append(f"- 美术参考：{art_text}")
    return "\n".join(lines)


def avg_art_requirement(scene_id: str, name: str, loop: int, raw: dict[str, Any], paths: list[Path]) -> str:
    documents = [(*markdown_sections(path), path) for path in paths]
    infos = [section_info(sections) for _, sections, _ in documents]
    time_version = next((info.get("时段") for info in infos if info.get("时段")), "")
    if not time_version:
        combined = " ".join(
            [name]
            + [title for title, _, _ in documents]
            + [path.stem for _, _, path in documents]
            + [info.get("内部英文名", "") for info in infos]
        )
        time_version = next((token for token in ("凌晨", "清晨", "深夜", "夜晚", "下午", "白天", "dawn") if token in combined), "按剧情时段")
        if time_version == "dawn":
            time_version = "黎明"
    resource_names = [info.get("内部英文名", "") for info in infos if info.get("内部英文名")]
    resource_types = [info.get("资源形态", "完整 AVG 画面") for info in infos]
    lines = [
        f"【完整 AVG 场景图】{name}",
        f"- 时间版本：{time_version}版；背景资源：{' / '.join(resource_names) or f'u4_scene_{scene_id}'}",
        f"- 资产性质：{'；'.join(resource_types)}；人物和场景合成整图，不开放自由探索",
        f"- 场景参考：SC{scene_id} {name}",
    ]
    for index, (title, sections, _) in enumerate(documents, 1):
        visual = section_text(sections, "画面", "画面节奏", "空间布局", "必需画面")
        label = f"构图 {chr(64 + index)}" if len(documents) > 1 else "画面重点"
        if visual:
            lines.append(f"- {label}：{visual}")
        narrative = section_text(sections, "剧情作用")
        if narrative:
            lines.append(f"- 叙事作用：{narrative}")
        boundary = section_text(sections, "边界", "运行边界", "美术重点")
        if boundary:
            lines.append(f"- 排除内容与演出边界：{boundary}")
    return "\n".join(lines)


def scene_art_requirement(
    scene_id: str, name: str, loop: int, raw: dict[str, Any], is_cutscene: bool, is_ending: bool
) -> str:
    explore_matches = sorted(EXPLORE_DOC_DIR.glob(f"EXP_SC{scene_id}_*.md"))
    avg_paths = [AVG_DOC_DIR / filename for filename in AVG_SCENE_DOCS.get(scene_id, [])]
    missing = [path for path in explore_matches + avg_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing Unit4 scene art document(s): {missing}")
    if explore_matches:
        requirement = explore_art_requirement(scene_id, name, loop, raw, explore_matches[0])
        if avg_paths:
            supplement = avg_art_requirement(scene_id, name, loop, raw, avg_paths)
            supplement_lines = supplement.splitlines()[4:]
            if supplement_lines:
                requirement += "\n- AVG 高潮演出补充：" + "；".join(
                    line.removeprefix("- ") for line in supplement_lines
                )
        return requirement
    if avg_paths:
        return avg_art_requirement(scene_id, name, loop, raw, avg_paths)
    kind = "非 Loop 终幕" if is_ending else "AVG" if is_cutscene else "探索"
    raise ValueError(f"SC{scene_id} {kind}场景缺少专用美术需求文档")


def avg_character_action_requirements(
    scene_id: str, loop: int, paths: list[Path]
) -> list[dict[str, Any]]:
    """Expose same-scene AVG performance requirements without inventing extra scenes."""
    rows: list[dict[str, Any]] = []
    for path in paths:
        title, sections = markdown_sections(path)
        info = section_info(sections)
        requirement = section_text(
            sections,
            "演出顺序",
            "画面",
            "画面节奏",
            "剧情作用",
            "美术重点",
            "边界",
            "运行边界",
        )
        rows.append(
            {
                "name": title or path.stem,
                "stage": f"L{loop} / SC{scene_id} 同场景 AVG 演出层",
                "assetName": info.get("内部英文名", ""),
                "requirement": requirement,
            }
        )
    return rows


def walk_testimonies(value: Any, loop: int, out: dict[str, dict[str, Any]]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "testimony_ids" and isinstance(child, list):
                for testimony in child:
                    if isinstance(testimony, dict) and testimony.get("id") is not None:
                        tid = str(testimony["id"])
                        entry = {**testimony, "source_loop": loop}
                        previous = out.get(tid)
                        if previous and previous.get("content") != entry.get("content"):
                            raise ValueError(f"conflicting testimony definition: {tid}")
                        out[tid] = entry
            walk_testimonies(child, loop, out)
    elif isinstance(value, list):
        for child in value:
            walk_testimonies(child, loop, out)


def collect_testimonies(states: dict[int, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for loop, state in states.items():
        walk_testimonies(state, loop, result)
    return result


def collect_scene_evidence(states: dict[int, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for loop, state in states.items():
        for scene in state.get("scenes") or []:
            for evidence in scene.get("evidence") or []:
                eid = str(evidence["id"])
                result.setdefault(eid, {**evidence, "first_scene": scene["id"], "source_loop": loop})
    return result


def collect_registry(states: dict[int, dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Prefer the first/source definition and report inherited drift."""
    result: dict[str, dict[str, Any]] = {}
    risks: list[str] = []
    for loop, state in states.items():
        for evidence in state.get("evidence_registry") or []:
            eid = str(evidence["id"])
            candidate = {**evidence, "source_loop": evidence.get("source_loop", loop)}
            previous = result.get(eid)
            if previous is None:
                result[eid] = candidate
                continue
            if evidence.get("inherited"):
                if previous.get("type") != evidence.get("type"):
                    risks.append(
                        f"{eid} 继承类型 {evidence.get('type')} 与首次定义 {previous.get('type')} 不一致；预览采用首次定义。"
                    )
                if previous.get("first_scene") != evidence.get("first_scene"):
                    risks.append(
                        f"{eid} 继承来源场景 {evidence.get('first_scene')} 与首次定义 {previous.get('first_scene')} 不一致；预览采用首次定义。"
                    )
                continue
            if (previous.get("name"), previous.get("type")) != (
                evidence.get("name"), evidence.get("type")
            ):
                raise ValueError(f"conflicting evidence definition: {eid}")
    return result, risks


def analysis_links(registry: dict[str, dict[str, Any]]) -> tuple[dict[str, str], dict[str, str]]:
    source_to_result: dict[str, str] = {}
    result_to_source: dict[str, str] = {}
    for eid, evidence in registry.items():
        if not evidence.get("analysis"):
            continue
        sources = [str(value) for value in evidence.get("source") or []]
        if len(sources) == 1:
            source_to_result[sources[0]] = eid
            result_to_source[eid] = sources[0]
    return source_to_result, result_to_source


def item_type(source_type: str) -> str:
    return {"clue": "1", "envir": "2"}.get(source_type, "3")


def acquisition_label(evidence: dict[str, Any]) -> str:
    acquisition = evidence.get("acquisition")
    if isinstance(acquisition, dict):
        return str(acquisition.get("kind") or "manual")
    if acquisition:
        return str(acquisition)
    if evidence.get("analysis"):
        return "analysis"
    if evidence.get("generated_by"):
        return "special_mechanic"
    return "manual"


def scene_background_resources(art_requirement: str) -> list[str]:
    """Read the pre-agreed asset names already embedded in the scene art card."""
    marker = "背景资源："
    for line in art_requirement.splitlines():
        if marker not in line:
            continue
        raw_names = line.split(marker, 1)[1].strip()
        names = [name.strip() for name in raw_names.split(" / ") if name.strip()]
        if names:
            return names
    raise ValueError("scene art requirement has no background resource name")


def background_asset_path(resource_name: str) -> str:
    return f"Art\\Scene\\Backgrounds\\{EPISODE}\\{resource_name}"


def item_asset_token(item_type_value: str) -> str:
    return {"1": "clue", "2": "envir"}.get(item_type_value, "item")


def build_item_rows(
    registry: dict[str, dict[str, Any]],
    scene_evidence: dict[str, dict[str, Any]],
    scene_names: dict[str, str],
    scene_resources: dict[str, list[str]],
    art_cards: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    source_to_result, result_to_source = analysis_links(registry)
    rows: list[dict[str, Any]] = []
    for eid, registered in sorted(registry.items(), key=lambda pair: int(pair[0])):
        if registered.get("type") == "testimony":
            continue
        evidence = {**registered, **scene_evidence.get(eid, {})}
        source_type = str(registered.get("type") or evidence.get("type") or "item")
        first_scene = str(registered.get("first_scene") or evidence.get("first_scene") or "")
        art_card = art_cards[eid]
        name = art_card["Name"][0]
        direct_analysis_result = source_to_result.get(eid, "")
        preview_analysis = bool(evidence.get("analysis")) and not direct_analysis_result
        runtime_item_type = item_type(source_type)
        special_disposition = SPECIAL_ASSET_DISPOSITIONS.get(eid)
        resource_names = scene_resources.get(first_scene) or []
        if not special_disposition and not resource_names:
            raise ValueError(f"standard evidence has no source scene resource: {eid}")
        asset_base = (
            f"SC{first_scene}_{item_asset_token(runtime_item_type)}_{eid}"
            if not special_disposition
            else ""
        )
        row: dict[str, Any] = {
            "id": eid,
            "Name": deepcopy(art_card["Name"]),
            "itemType": runtime_item_type,
            "canAnalyzed": "true" if direct_analysis_result else "false",
            "analysedEvidence": direct_analysis_result,
            "beforeAnalysedEvidence": result_to_source.get(eid, ""),
            "canCombined": "false",
            "combineParameter": [],
            "Describe": deepcopy(art_card["Describe"]),
            "ShortDescribe": deepcopy(art_card["ShortDescribe"]),
            "location": [scene_names.get(first_scene, "非场景直接取得"), ""],
            "Chapter": EPISODE,
            "folderPath": (
                f"{EPISODE}\\{resource_names[0]}"
                if resource_names and not special_disposition
                else ""
            ),
            "desSpritePath": f"{asset_base}_big" if asset_base else "",
            "mapSpritePath": asset_base,
            "iconPath": f"{asset_base}_icon" if asset_base else "",
            "Position": [],
            "ArtRequirement": art_card["ArtRequirement"],
            "obtainMethod": acquisition_label(evidence),
            "HiddenStuff": "true",
            "sourceStateType": source_type,
            "sourceLoop": int(registered.get("source_loop") or evidence.get("source_loop") or 0),
            "sourceScene": first_scene,
            "previewStatus": "art_pending",
        }
        if special_disposition:
            row["previewAssetMode"], row["previewAssetNote"] = special_disposition
        if preview_analysis:
            row["previewAnalysisRequired"] = True
        if registered.get("persistence"):
            row["persistence"] = deepcopy(registered["persistence"])
        if registered.get("generated_by"):
            row["generatedBy"] = registered["generated_by"]
        if len(art_card["variants"]) > 1:
            row["previewEvidenceStates"] = deepcopy(art_card["variants"])
        rows.append(row)
    return rows


def build_npc_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for npc_id, info in NPC_DEFS.items():
        name = info["name"]
        icon = info["icon"]
        rows.append(
            {
                "id": npc_id,
                "Name": [name, name],
                "role": info["role"],
                "Chapter": EPISODE,
                "IconSmall": f"{icon}_small",
                "IconLarge": f"{icon}_big",
                "ArtRequirement": info.get("art") or (
                    f"【Unit4 人物预览】{name}\n"
                    f"人物事实与美术边界见 剧情设计/Unit4/人物设定/{info['file']}；"
                    f"预配置头像资源：{icon}_small / {icon}_big。"
                ),
                "previewStatus": "art_pending",
            }
        )
    return rows


def npc_info(
    loop: int,
    scene_id: str,
    key: str,
    data: dict[str, Any],
    npc_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    token = key.rsplit("_", 1)[-1].lower()
    npc_id = NPC_TOKEN_TO_ID.get(token)
    if not npc_id:
        raise ValueError(f"unmapped Unit4 scene NPC key: {key}")
    pending_talk = str(data.get("talk") or key)
    asset_token = NPC_DEFS[npc_id]["asset"]
    asset_base = f"Art\\Scene\\NPC\\{EPISODE}\\SC{scene_id}_npc_{asset_token}"
    return {
        "id": f"{npc_id}{loop}",
        "NPC": deepcopy(npc_rows[npc_id]),
        "TalkInfo": {
            "id": "",
            "videoEpisode": EPISODE,
            "videoLoop": f"loop{loop}",
            "videoScene": "",
            "pendingTalkKey": pending_talk,
            "previewStatus": "avg_pending",
        },
        "LoopTalkInfo": {
            "id": "",
            "videoEpisode": EPISODE,
            "videoLoop": f"loop{loop}",
            "videoScene": "",
            "pendingTalkKey": f"{pending_talk}_repeat",
            "previewStatus": "avg_pending_repeat_8LL_namespace",
        },
        "IsinRight": "false",
        "ResPath": f"{asset_base}1",
        "ClickResPath": f"{asset_base}2",
        "PosX": "",
        "Posy": "",
        "PosZ": "-2",
        "sourceStateKey": key,
        "previewStatus": "avg_and_art_pending",
    }


def build_scene_rows(
    states: dict[int, dict[str, Any]], npc_rows: list[dict[str, Any]]
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, str],
    dict[str, list[str]],
]:
    npc_by_id = {row["id"]: row for row in npc_rows}
    scenes: list[dict[str, Any]] = []
    npc_loops: list[dict[str, Any]] = []
    art_assets: list[dict[str, Any]] = []
    scene_names: dict[str, str] = {}
    scene_resources: dict[str, list[str]] = {}

    for loop, state in states.items():
        raw_scenes = [(scene, False) for scene in state.get("scenes") or []]
        raw_scenes.extend(
            (scene, True) for scene in (state.get("ending_sequence") or {}).get("scenes") or []
        )
        opening_scene_ids = {
            str(event.get("scene_id")) for event in (state.get("opening") or {}).get("sequence") or []
        }
        event_by_scene: dict[str, list[dict[str, Any]]] = {}
        for event in (state.get("opening") or {}).get("sequence") or []:
            event_by_scene.setdefault(str(event.get("scene_id")), []).append(event)

        for raw, is_ending in raw_scenes:
            scene_id = str(raw.get("scene_id") if is_ending else raw.get("id"))
            name = str(raw.get("scene_name") or raw.get("name") or f"Scene {scene_id}")
            scene_names[scene_id] = name
            source_type = str(raw.get("type") or "cutscene")
            is_cutscene = source_type == "cutscene"
            design_tags = list(raw.get("design_tags") or [])
            evidence_ids = [str(e["id"]) for e in raw.get("evidence") or []]
            npc_infos: list[dict[str, Any]] = []
            for key, value in (raw.get("npcs") or {}).items():
                info = npc_info(loop, scene_id, key, value, npc_by_id)
                npc_infos.append(info)
                npc_loops.append(deepcopy(info))

            opening_events = event_by_scene.get(scene_id, [])
            event_triggers = list(raw.get("event_triggers") or [])
            preview_events = []
            for event in opening_events + event_triggers:
                preview_events.append(
                    {
                        "id": str(event.get("event_id") or event.get("id") or "event"),
                        "pendingTalkKey": str(event.get("talk") or ""),
                        "forced": bool(event.get("forced", True)),
                    }
                )

            art_requirement = scene_art_requirement(
                scene_id, name, loop, raw, is_cutscene=is_cutscene, is_ending=is_ending
            )
            resource_names = scene_background_resources(art_requirement)
            scene_resources[scene_id] = resource_names
            background_paths = [background_asset_path(resource) for resource in resource_names]
            background_id = background_paths[0]
            row: dict[str, Any] = {
                "sceneId": scene_id,
                "location": {
                    "id": scene_id,
                    "Name": [name, resource_names[0]],
                    "sceneType": "3" if is_cutscene else "1",
                    "backgroundImage": background_id,
                },
                "Chapter": EPISODE,
                "loop": loop,
                "isOpen": not is_cutscene and not is_ending,
                "NPCInfos": npc_infos,
                "ItemIDs": evidence_ids,
                "note": "非 Loop 终幕" if is_ending else ("纯 AVG / 过场" if is_cutscene else "探索 / 交互"),
                "ArtRequirement": art_requirement,
                "designTags": design_tags,
                "previewSceneKind": "dialogue" if is_cutscene or is_ending else "explore",
                "previewStatus": "avg_pending" if is_cutscene or is_ending else "structure_ready_art_pending",
            }
            if len(background_paths) > 1:
                row["previewBackgroundImages"] = background_paths
            if preview_events:
                row["previewEvents"] = preview_events
            if scene_id in opening_scene_ids:
                row["isOpeningScene"] = True
            if is_ending:
                row["nonLoopFinale"] = True
                row["pendingTalkKey"] = str(raw.get("talk") or "")
                row["runtimeExit"] = deepcopy(raw.get("runtime_exit") or {})
            scenes.append(row)
            for resource_index, (resource_name, resource_path) in enumerate(
                zip(resource_names, background_paths),
                1,
            ):
                art_row: dict[str, Any] = {
                        "id": resource_path,
                        "Name": (
                            name
                            if len(resource_names) == 1
                            else f"{name} · 构图 {chr(64 + resource_index)}"
                        ),
                        "displayName": resource_name,
                        "category": "scene",
                        "sceneKind": "dialogue" if is_cutscene or is_ending else "explore",
                        "ArtRequirement": art_requirement,
                        "assetStatus": "pending",
                        "Chapter": EPISODE,
                        "events": preview_events,
                    }
                if not is_cutscene and not is_ending and AVG_SCENE_DOCS.get(scene_id):
                    art_row["characterActionRequirements"] = avg_character_action_requirements(
                        scene_id,
                        loop,
                        [AVG_DOC_DIR / filename for filename in AVG_SCENE_DOCS[scene_id]],
                    )
                art_assets.append(art_row)

    # Runtime NPCLoopData normally uses NPC+Loop as a four-digit row id.  Doris
    # appears in two different L3 scenes with distinct first-click dialogue, so
    # the editor copy needs scene-specific preview ids until runtime ownership is
    # finalized.  Keep the runtime candidate explicit for later table handoff.
    duplicate_ids: dict[str, list[dict[str, Any]]] = {}
    for row in npc_loops:
        duplicate_ids.setdefault(str(row["id"]), []).append(row)
    for runtime_id, duplicate_rows in duplicate_ids.items():
        if len(duplicate_rows) < 2:
            continue
        for index, row in enumerate(sorted(duplicate_rows, key=lambda item: item["sourceStateKey"]), 1):
            preview_id = f"{runtime_id}{index}"
            row["runtimeCandidateId"] = runtime_id
            row["id"] = preview_id
            row["previewRowId"] = preview_id
            for scene in scenes:
                for info in scene.get("NPCInfos") or []:
                    if info.get("sourceStateKey") == row["sourceStateKey"]:
                        info["runtimeCandidateId"] = runtime_id
                        info["id"] = preview_id
                        info["previewRowId"] = preview_id
    return scenes, npc_loops, art_assets, scene_names, scene_resources


def build_testimony_rows(testimonies: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for tid, testimony in sorted(testimonies.items(), key=lambda pair: int(pair[0])):
        content = str(testimony.get("content") or testimony.get("name") or f"Testimony {tid}")
        speaker = str(testimony.get("speaker") or tid[:3])
        is_timeline = tid == "4153001"
        rows.append(
            {
                "id": tid,
                "testimonyType": "1",
                "testimony": [content, content],
                "truth": ["", ""],
                "triggerType": "Timeline" if is_timeline else "None",
                "triggerParam": "415,4024,2236,2315" if is_timeline else speaker,
                "shortDesc": [content, content],
                "shortTruth": ["", ""],
                "HiddenStuff": "true",
                "Chapter": EPISODE,
                "loop": int(testimony.get("source_loop") or tid[3]),
                "ArtRequirement": "来源：Unit4 State 内联证词；AVG 制作后校对原句与 truth。",
                "pendingAcquisitionTalkKey": str(testimony.get("acquisition_talk") or ""),
                "sourceKind": str(testimony.get("kind") or "collectible"),
                "previewStatus": "avg_pending",
            }
        )
    return rows


def normalized_condition(condition: dict[str, Any]) -> dict[str, str]:
    typ = str(condition.get("type") or "")
    param = str(condition.get("param") or "")
    # Unit4 State used type=3 as a broad testimony marker.  Runtime config
    # reserves 3 for Timeline; only the switchboard record is a real timeline.
    if typ == "3" and param != "4153001":
        typ = "4"
    return {"type": typ, "param": param}


def build_doubt_rows(states: dict[int, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[int, list[dict[str, Any]]]]:
    rows: list[dict[str, Any]] = []
    by_loop: dict[int, list[dict[str, Any]]] = {}
    for loop, state in states.items():
        loop_rows: list[dict[str, Any]] = []
        for doubt in state.get("doubts") or []:
            row = {
                "id": str(doubt["id"]),
                "text": str(doubt.get("text") or ""),
                "Chapter": EPISODE,
                "isFragment": "true" if doubt.get("isFragment") else "false",
                "condition": [normalized_condition(c) for c in doubt.get("unlock_condition") or []],
            }
            rows.append(row)
            loop_rows.append(deepcopy(row))
        by_loop[loop] = loop_rows
    return rows, by_loop


def expose_rounds(expose: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(expose.get("rounds"), list):
        return list(expose["rounds"])
    total = int(expose.get("total_rounds") or 0)
    return [expose[f"round_{idx}"] for idx in range(1, total + 1)]


def build_exposes(state: dict[str, Any], loop: int) -> list[dict[str, Any]]:
    expose = state.get("expose") or {}
    pending_root = str(expose.get("target_talk") or f"L{loop}_expose")
    rows: list[dict[str, Any]] = []
    for index, round_data in enumerate(expose_rounds(expose), 1):
        lie_source = str(round_data.get("lie_source") or "0") if index == 1 else "0"
        rows.append(
            {
                "id": str(index),
                "testimony": lie_source,
                "item": [str(item["id"]) for item in round_data.get("usable_evidence") or []],
                "talkId": "",
                "pendingTalkKey": f"{pending_root}.round_{index}",
                "lie": str(round_data.get("lie") or ""),
                "result": str(round_data.get("result") or ""),
                "previewStatus": "avg_pending",
            }
        )
    return rows


def normalize_opening(state: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for event in (state.get("opening") or {}).get("sequence") or []:
        result.append(
            {
                "eventId": str(event.get("event_id") or ""),
                "sceneId": str(event.get("scene_id") or ""),
                "pendingTalkKey": str(event.get("talk") or ""),
                "runtimeExit": deepcopy(event.get("runtime_exit") or {}),
                "requiredBeats": list(event.get("required_beats") or []),
            }
        )
    return result


def normalize_identity_lock(state: dict[str, Any]) -> dict[str, Any]:
    source = (state.get("special_mechanics") or {}).get("identity_lock") or {}
    if not source:
        return {}
    chains = []
    for chain in source.get("chains") or []:
        outputs = chain.get("outputs") or ([chain["output"]] if chain.get("output") else [])
        chains.append(
            {
                "id": str(chain.get("id") or ""),
                "name": str(chain.get("name") or ""),
                "inputs": [
                    {
                        "type": str(item.get("type") or "item"),
                        "id": str(item.get("id") or ""),
                        "name": str(item.get("name") or ""),
                        "sourceLoop": int(item.get("source_loop") or 5),
                    }
                    for item in chain.get("inputs") or []
                ],
                "outputs": [
                    {"type": str(item.get("type") or "derived_conclusion"), "id": str(item.get("id") or ""), "name": str(item.get("name") or "")}
                    for item in outputs
                ],
                "proofBoundary": as_text(chain.get("proof_boundary")),
            }
        )
    return {
        "status": str(source.get("status") or ""),
        "replacesStandardDoubts": bool(source.get("replaces_standard_doubts")),
        "chains": chains,
        "completionCondition": str((source.get("gate_contract") or {}).get("completion_condition") or "all_chains_completed"),
        "unlocks": str((source.get("gate_contract") or {}).get("unlocks") or "expose"),
        "interactionContract": deepcopy(source.get("interaction_contract") or {}),
        "previewStatus": "structure_ready",
    }


def normalize_ending(state: dict[str, Any]) -> dict[str, Any]:
    ending = state.get("ending_sequence") or {}
    runtime = ending.get("runtime_contract") or {}
    return {
        "structure": str(ending.get("structure") or "non_loop_finale"),
        "countsAsLoop": bool(runtime.get("counts_as_loop", ending.get("counted_as_loop", False))),
        "inheritLoop": int(runtime.get("inherit_loop") or 5),
        "chapterEndAfter": str(runtime.get("chapter_end_after") or "ending_4045"),
        "nextUnitEntry": str(runtime.get("next_unit_entry") or "enter_ohara_house"),
        "scenes": [
            {
                "id": str(scene.get("id") or ""),
                "sceneId": str(scene.get("scene_id") or ""),
                "name": str(scene.get("scene_name") or ""),
                "pendingTalkKey": str(scene.get("talk") or ""),
                "runtimeExit": deepcopy(scene.get("runtime_exit") or {}),
            }
            for scene in ending.get("scenes") or []
        ],
        "previewStatus": "structure_ready_avg_pending",
    }


def post_expose_segments(state: dict[str, Any], loop: int) -> list[dict[str, Any]]:
    expose = state.get("expose") or {}
    post = expose.get("post_expose") or {}
    segments = [
        {
            "order": 1,
            "type": "post_expose",
            "title": f"L{loop} 指证后剧情",
            "brief": as_text(post.get("description") or post.get("player_knowledge_gained")),
            "sceneId": EXPOSE_SCENES[loop],
            "videoEpisode": EPISODE,
            "videoLoop": f"loop{loop}",
            "videoScene": "",
            "entryTalkId": "",
            "pendingTalkKey": str(post.get("talk") or ""),
            "previewStatus": "avg_pending",
        }
    ]
    if loop == 5:
        for index, scene in enumerate((state.get("ending_sequence") or {}).get("scenes") or [], 2):
            segments.append(
                {
                    "order": index,
                    "type": "non_loop_finale",
                    "title": str(scene.get("scene_name") or scene.get("id") or "终幕"),
                    "brief": as_text(scene.get("description")),
                    "sceneId": str(scene.get("scene_id") or ""),
                    "videoEpisode": EPISODE,
                    "videoLoop": "loop5",
                    "videoScene": "",
                    "entryTalkId": "",
                    "pendingTalkKey": str(scene.get("talk") or ""),
                    "previewStatus": "avg_pending",
                }
            )
    return segments


def build_chapter_rows(
    states: dict[int, dict[str, Any]],
    doubts_by_loop: dict[int, list[dict[str, Any]]],
    scene_resources: dict[str, list[str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for loop, state in states.items():
        player = state.get("player_context") or {}
        goals = player.get("goals") or {}
        opening = state.get("opening") or {}
        runtime_root = opening.get("runtime_root") or {}
        pending_init_talk = str(runtime_root.get("init_talk") or "")
        init_scene = str(runtime_root.get("init_scene") or "")
        exposes = build_exposes(state, loop)
        row: dict[str, Any] = {
            "id": f"40{loop}",
            "chapterTitle": [LOOP_TITLES[loop], LOOP_TITLES[loop]],
            "chapterBrief": [as_text(goals.get("secondary")), ""],
            "openingBrief": [as_text((opening.get("sequence") or [{}])[0].get("required_beats")), ""],
            "summaryTitle": ["本轮获得的信息", ""],
            "summaryContent": [as_text(player.get("post_expose_knowledge")), ""],
            "newDoubtTitle": ["本轮调查问题", ""],
            "newDoubtContent": [as_text(goals.get("primary")), ""],
            "chapterGoal": [as_text(goals.get("primary") or player.get("chapter_goal")), ""],
            "chapterSteps": [],
            "initTalk": "",
            "pendingInitTalkKey": pending_init_talk,
            "initScene": init_scene,
            "openingScene": init_scene,
            "explorationEntryScene": EXPLORATION_ENTRY_SCENES[loop],
            "openingSequence": normalize_opening(state),
            "doubts": deepcopy(doubts_by_loop[loop]),
            "clearDoubts": [row["id"] for row in doubts_by_loop[loop]],
            "topBg": background_asset_path(scene_resources[EXPOSE_SCENES[loop]][0]),
            "bottomBg": "",
            "exposeScene": EXPOSE_SCENES[loop],
            "exposeNpcId": EXPOSE_NPCS[loop],
            "suspectVideoPos": "",
            "suspectTalkPos": "",
            "zackTalkPos": "",
            "exposes": exposes,
            "postExposeSegments": post_expose_segments(state, loop),
            "map2Scenes": [],
            "ArtRequirement": f"【Unit4 Loop{loop} 预览】结构已配置；AVG、指证背景和正式资源待后续补齐。",
            "previewStatus": "structure_ready_avg_pending",
            "sourceState": f"剧情设计/Unit4/state/loop{loop}_state.yaml",
        }
        identity = normalize_identity_lock(state)
        if identity:
            row["specialMechanics"] = {"identityLock": identity}
        ending = normalize_ending(state)
        if ending.get("scenes"):
            row["endingSequence"] = ending
        rows.append(row)
    return rows


def build_rows() -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    states = load_states()
    testimonies = collect_testimonies(states)
    registry, risks = collect_registry(states)
    item_ids = {eid for eid, evidence in registry.items() if evidence.get("type") != "testimony"}
    art_cards = load_evidence_art_cards(item_ids)
    scene_evidence = collect_scene_evidence(states)
    npc_rows = build_npc_rows()
    scene_rows, npc_loop_rows, art_rows, scene_names, scene_resources = build_scene_rows(
        states,
        npc_rows,
    )
    item_rows = build_item_rows(
        registry,
        scene_evidence,
        scene_names,
        scene_resources,
        art_cards,
    )
    testimony_rows = build_testimony_rows(testimonies)
    doubt_rows, doubts_by_loop = build_doubt_rows(states)
    chapter_rows = build_chapter_rows(states, doubts_by_loop, scene_resources)
    return (
        {
            "ChapterConfig": chapter_rows,
            "SceneConfig": scene_rows,
            "ItemStaticData": item_rows,
            "NPCStaticData": npc_rows,
            "NPCLoopData": npc_loop_rows,
            "TestimonyItem": testimony_rows,
            "DoubtConfig": doubt_rows,
            "ArtAssetConfig": art_rows,
        },
        risks,
    )


TABLE_KEYS = {
    "ChapterConfig": "id",
    "SceneConfig": "sceneId",
    "ItemStaticData": "id",
    "NPCStaticData": "id",
    "NPCLoopData": "id",
    "TestimonyItem": "id",
    "DoubtConfig": "id",
    "ArtAssetConfig": "id",
}


def sort_key(value: dict[str, Any], key: str) -> tuple[int, Any]:
    raw = str(value.get(key, ""))
    return (0, int(raw)) if raw.isdigit() else (1, raw)


def merge_rows(existing: list[dict[str, Any]], incoming: Iterable[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    incoming_rows = list(incoming)
    incoming_ids = {str(row[key]) for row in incoming_rows}
    result = [row for row in existing if str(row.get(key, "")) not in incoming_ids]
    result.extend(deepcopy(incoming_rows))
    result.sort(key=lambda row: sort_key(row, key))
    return result


def write_tables(rows_by_table: dict[str, list[dict[str, Any]]]) -> None:
    for table_name, incoming in rows_by_table.items():
        path = TABLE_DIR / f"{table_name}.json"
        with path.open("r", encoding="utf-8") as handle:
            existing = json.load(handle)
        # This script owns the EPI04 preview slice. Remove a previous generated
        # slice first so changed preview-only ids cannot leave stale rows behind.
        key = TABLE_KEYS[table_name]
        existing = [
            row for row in existing
            if row.get("Chapter") != EPISODE
            and not str(row.get("sceneId") if key == "sceneId" else row.get(key, "")).startswith("4")
        ]
        merged = merge_rows(existing, incoming, key)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(merged, handle, ensure_ascii=False, indent=2)
            handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="merge generated EPI04 rows into editor tables")
    args = parser.parse_args(argv)
    rows_by_table, risks = build_rows()
    for table_name, rows in rows_by_table.items():
        print(f"{table_name}: {len(rows)} Unit4 rows")
    for risk in risks:
        print(f"RISK: {risk}")
    if args.write:
        write_tables(rows_by_table)
        print(f"wrote Unit4 rows to {TABLE_DIR}")
    else:
        print("dry-run only; pass --write to merge")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
