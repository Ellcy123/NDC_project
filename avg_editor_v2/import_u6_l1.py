"""Import the approved experimental L1 into shared preview tables, once.

The default/dry-run changes no project data. --write appends L1 rows, updates
only the three approved source fields on item 6208, and merges only Unit6's
manifest registration and flow cache. It never reads an experimental engine.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TABLES = HERE / "data/table"
SOURCE = ROOT / "剧情设计/试验单元/U1_五Loop试验版/L1_完整对白.md"
REPORT = HERE / "data/_table_drafts/Unit6/integration_report_l1.json"
MANIFEST = ROOT / "canon_manifest.json"
FLOW = HERE / "data/formal/unit_flow.json"
BLOCKS = (
    "entrance", "lobby_intro", "emma_connections", "emma_terms",
    "cooperation_close", "gunshot", "discovery", "rosa_intro", "rosa_repeat",
    "rosa_saw", "rosa_heard", "vivian_intro", "vivian_repeat", "vivian_shot",
    "vivian_gun", "morrison_intro", "morrison_repeat", "morrison_connection",
    "morrison_basis", "inspect_gun", "analyze_gun", "inspect_commission",
    "expose_open", "expose_lie", "expose_success", "expose_wrong",
    "negotiation", "ending",
)
ITEMS = dict(gun_raw="6101", gun_check="6208", commission="6103",
             rosa_claim="6031001", rosa_heard="6031002",
             vivian_ownership="6061001", morrison_basis="6111001")
GRANT_BLOCKS = dict(gun_raw="inspect_gun", gun_check="analyze_gun",
                    commission="inspect_commission", rosa_claim="rosa_saw",
                    rosa_heard="rosa_heard", vivian_ownership="vivian_gun",
                    morrison_basis="morrison_basis")
SPEAKERS = {"Zack": "601", "Emma": "602", "Rosa": "603", "Vivian": "606",
            "Morrison": "611", "门卫": "612"}
MENUS = {
    "emma": ("602", "lobby_intro", None, [
        ("怎么知道这里的门路？", "emma_connections"),
        ("想怎么合作？", "emma_terms")]),
    "rosa": ("603", "rosa_intro", "rosa_repeat", [
        ("究竟看见了什么？", "rosa_saw"), ("23:30 在哪里、听见什么？", "rosa_heard")]),
    "vivian": ("606", "vivian_intro", "vivian_repeat", [
        ("那声枪响和你有关吗？", "vivian_shot"), ("这把枪是你的吗？", "vivian_gun")]),
    "morrison": ("611", "morrison_intro", "morrison_repeat", [
        ("和这家酒吧是什么关系？", "morrison_connection"),
        ("目前判断的依据是什么？", "morrison_basis")]),
}
SCENES = {
    "entrance": ("6100", "1021", "蓝月亮酒吧门外"),
    "lobby": ("6101", "1029", "酒吧大堂"),
    "discovery": ("6102", "1031", "Webb 会客室·发现现场"),
    "parlor": ("6103", "1103", "Webb 会客室"),
}
LIE = "Vivian 手里这把枪刚刚开过火，Webb 就是被它打死的。"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def row_id(row, table):
    return str(row["sceneId" if table == "SceneConfig" else "id"])


def parse_source(path=SOURCE):
    blocks = {}
    current = None
    node = None
    grants = {}
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.startswith("## dialogue: "):
            current = line[len("## dialogue: "):].strip()
            require(current in BLOCKS and current not in blocks, f"Invalid/duplicate block at {line_number}: {current}")
            blocks[current] = []
            node = None
            continue
        if current is None or not line.strip():
            continue
        actor = re.fullmatch(r"\*\*(.+?)\*\*", line.strip())
        if actor:
            require(actor[1] in SPEAKERS, f"Unknown speaker at {line_number}: {actor[1]}")
            node = dict(speaker=actor[1], text="", grants=[], line=line_number)
            blocks[current].append(node)
        elif line.startswith(">"):
            require(node is not None and not node["grants"], f"Text without speaker or after @get at {line_number}")
            node["text"] += ("\n" if node["text"] else "") + line[1:].strip()
        elif line.startswith("@get "):
            key = line[5:].strip()
            require(node is not None and node["text"], f"Empty grant node at {line_number}")
            require(key in ITEMS and key not in grants, f"Unknown/duplicate @get at {line_number}: {key}")
            require(current == GRANT_BLOCKS[key] and not node["grants"], f"Wrong grant block/node: {key}")
            node["grants"].append(key)
            grants[key] = current
        else:
            raise ValueError(f"Unparsed dialogue/action line {line_number}: {line}")
    require(set(blocks) == set(BLOCKS), f"Missing blocks: {set(BLOCKS) - set(blocks)}")
    require(set(grants) == set(ITEMS), f"Missing grants: {set(ITEMS) - set(grants)}")
    require(all(nodes and all(n["text"] for n in nodes) for nodes in blocks.values()), "Empty block/node")
    return {key: blocks[key] for key in BLOCKS}


def context(key):
    if key == "entrance":
        return "entrance"
    if key in ("lobby_intro", "emma_connections", "emma_terms", "cooperation_close", "gunshot"):
        return "lobby"
    return "discovery" if key == "discovery" else "parlor"


def compile_rows(blocks, tables):
    existing_npcs = {str(row["id"]): row for row in tables["NPCStaticData"]}
    new_npcs = [dict(id=nid, Name=[name, english], role="2", Chapter="EPI06",
                     ArtRequirement="", showInRelationshipNetwork="1" if nid == "611" else "0",
                     showInTimeline="1" if nid == "611" else "0")
                for nid, name, english in [("611", "Morrison", "Morrison"), ("612", "门卫", "Doorman")]]
    npcs = {**existing_npcs, **{row["id"]: row for row in new_npcs}}
    for nid in SPEAKERS.values():
        require(nid in npcs and npcs[nid].get("Chapter") == "EPI06", f"Missing Unit6 speaker: {nid}")
    groups, talks, grant_nodes = {}, [], {}
    for group_number, key in enumerate(BLOCKS, 100):
        owner = next((v[0] for k, v in MENUS.items() if key.startswith(k + "_")), "601")
        scene = "loop1_rosa" if key in ("expose_open", "expose_lie", "expose_success") else "l1_" + key
        rows = []
        for index, node in enumerate(blocks[key], 1):
            require(index <= 999, f"Too many nodes in {key}")
            tid = f"{owner}{group_number:03d}{index:03d}"
            row = dict(id=tid, step=str(index), isRight="true" if node["speaker"] == "Zack" else "false",
                       waitTime="0", Speaker=deepcopy(npcs[SPEAKERS[node["speaker"]]]),
                       Location=[SCENES[context(key)][2], ""], Words=[node["text"], ""], cnAction="",
                       next="", script="", Parameters=[], videoEpisode="EPI06", videoLoop="loop1",
                       videoScene=scene, videoId=tid)
            if node["grants"]:
                grant = node["grants"][0]
                iid = ITEMS[grant]
                row.update(script="3", Parameters=[dict(ParameterInt=iid, ParameterStr=("TIM" if len(iid) == 7 else "EV") + iid)])
                grant_nodes[grant] = dict(talkId=tid, block=key, nodeIndex=index - 1, materialId=iid)
            if rows:
                rows[-1]["next"] = tid
            rows.append(row)
        groups[key] = rows
        talks.extend(rows)

    def first(key):
        return groups[key][0]["id"]

    def ref(key):
        return {field: groups[key][0][field] for field in ("id", "videoEpisode", "videoLoop", "videoScene")}

    menu_ids = {}
    for key, (nid, intro, repeat, topics) in MENUS.items():
        menu = deepcopy(groups[intro][-1])
        mid = nid + "810001"
        menu.update(id=mid, videoId=mid, step="810", Words=["", ""], cnAction="", script="1", next="", Parameters=[])
        for title, block in topics:
            menu["Parameters"].append(dict(ParameterStr=title, ParameterInt=first(block)))
            groups[block][-1]["next"] = mid
        if key == "emma":
            menu["Parameters"].append(dict(ParameterStr="结束交谈，去找 Webb", ParameterInt=first("cooperation_close")))
        else:
            end = deepcopy(menu)
            end.update(id=nid + "810002", videoId=nid + "810002", step="811", script="2", Parameters=[])
            menu["Parameters"].append(dict(ParameterStr="结束交谈", ParameterInt=end["id"]))
            talks.append(end)
            groups[repeat][-1]["next"] = mid
        groups[intro][-1]["next"] = mid
        talks.append(menu)
        menu_ids[key] = mid
    groups["entrance"][-1]["next"] = first("lobby_intro")
    for left, right in [("cooperation_close", "gunshot"), ("gunshot", "discovery"),
                        ("expose_open", "expose_lie"), ("expose_lie", "expose_success"),
                        ("expose_success", "negotiation"), ("negotiation", "ending")]:
        groups[left][-1]["next"] = first(right)
    groups["discovery"][-1].update(script="2", next="")
    groups["expose_lie"][-1].update(script="7", Parameters=[
        dict(ParameterStr="EV6208", ParameterInt="0"), dict(ParameterInt="1")])
    groups["expose_success"][-1]["script"] = "11"
    groups["expose_wrong"][-1]["next"] = first("expose_lie")
    groups["ending"][-1].update(script="15", next="")
    step = 0
    for key in ("expose_open", "expose_lie", "expose_success"):
        for row in groups[key]:
            step += 1
            row["step"] = str(step)

    # These two new cards use only approved facts, not old U1 narrative text.
    item_template = dict(itemType="3", canAnalyzed="false", canCombined="false", Chapter="EPI06", Loop=1,
                         folderPath="", desSpritePath="", mapSpritePath="", iconPath="", Position=["0", "0", "-3"],
                         HiddenStuff="false", ArtRequirement="", obtainMethod="manual", location=["Webb 会客室", ""])
    raw = dict(deepcopy(item_template), id="6101", Name=["Vivian 的小手枪", ""], canAnalyzed="true", analysedEvidence="6208",
               Describe=["Vivian 留在现场的 Colt 1908 型 .25 口径袖珍手枪。尚未检查是否近期击发。", ""],
               ShortDescribe=["Vivian 留在现场的 Colt 1908 型 .25 口径袖珍手枪。", ""])
    commission_text = "Webb 亲笔签署的协议，日期 1928-10-31；Zack Brennan 为遗嘱执行人，Vivian Gray 继承其全部遗产。"
    commission = dict(deepcopy(item_template), id="6103", Name=["Webb 签署的委托协议", ""],
                      Describe=[commission_text, ""], ShortDescribe=[commission_text, ""])
    testimony_cards = {
        "rosa_claim": ("Rosa 对小手枪的指认", LIE, "1"),
        "rosa_heard": ("Rosa 所述的枪声与玻璃声", "Rosa 自称 23:30 在会客室附近走廊打扫，听见一声枪响，接着听见玻璃碎声。", "1"),
        "vivian_ownership": ("Vivian 承认小手枪属于自己", "Vivian 承认现场这把小手枪属于自己。", "1"),
        "morrison_basis": ("Morrison 判断的来源", "Morrison 称自己在吧台附近听见 23:30 枪声；到场见 Webb 倒地、Vivian 持枪，Rosa 指认她。", "1"),
    }
    testimonies, full_testimonies = [], []
    for key, (title, text, kind) in testimony_cards.items():
        iid = ITEMS[key]
        card = dict(id=iid, testimonyType=kind, testimony=[text, ""], truth=["", ""], triggerType="None",
                    triggerParam=iid[:3], shortDesc=[title, ""], shortTruth=["", ""], HiddenStuff="false")
        testimonies.append(card)
        grant = grant_nodes[key]
        owner_name = next(name for name, nid in SPEAKERS.items() if nid == iid[:3])
        words = "\n".join(n["text"] for n in blocks[grant["block"]][:grant["nodeIndex"] + 1] if n["speaker"] == owner_name)
        full_testimonies.append(dict(id=grant["talkId"], npc=deepcopy(npcs[iid[:3]]), chapter="601",
                                     words=[words, ""], evidenceItem=[deepcopy(card)]))

    old_scenes = {str(s["sceneId"]): s for s in tables["SceneConfig"]}
    scenes, locations, npc_loops = [], [], []
    for key, (sid, old_id, name) in SCENES.items():
        require(old_id in old_scenes, f"Missing art source scene {old_id}")
        background = old_scenes[old_id]["location"]["backgroundImage"]
        location = dict(id=sid, Name=[name, ""], sceneType="1", backgroundImage=background)
        locations.append(location)
        scene = dict(sceneId=sid, location=deepcopy(location), loop=1, openInLoops=[1], isOpen=key == "parlor",
                     ItemIDs=["6101", "6103"] if key == "parlor" else [], NPCInfos=[], previewTalks=[],
                     note="Unit6 L1 试验预览；仅复用原场景背景，未复用旧剧情。")
        for npc_key in (["emma"] if key == "lobby" else ["rosa", "vivian", "morrison"] if key == "parlor" else []):
            nid, intro, repeat, _ = MENUS[npc_key]
            info = dict(id="61" + nid, NPC=deepcopy(npcs[nid]), TalkInfo=ref(intro),
                        LoopTalkInfo=ref(repeat) if repeat else {**ref(intro), "id": menu_ids[npc_key]},
                        IsinRight="false", ResPath="", ClickResPath="", PosX="0", Posy="0", PosZ="-2")
            scene["NPCInfos"].append(info)
            npc_loops.append(deepcopy(info))
        preview = {"entrance": [("门外接头", "entrance")],
                   "lobby": [("大堂合作交谈", "lobby_intro"), ("合作收口与枪响", "cooperation_close")],
                   "discovery": [("发现现场", "discovery")],
                   "parlor": [("查看小手枪", "inspect_gun"), ("检查小手枪", "analyze_gun"),
                              ("查看委托协议", "inspect_commission"), ("指证错误回应", "expose_wrong")]}[key]
        scene["previewTalks"] = [dict(title=title, **ref(block)) for title, block in preview]
        scenes.append(scene)
    doubts = [dict(id="6101", isFragment=False, text="Rosa 对这把枪的指认可信吗？", condition=[
        dict(type="1", param="6208"), dict(type="4", param="6031001"), dict(type="1", param="6103")])]
    exposes = [dict(id="6101", testimony="6031001", item=["6208"], talkId=first("expose_success"))]
    opening_sequence = [dict(sceneId=SCENES[scene][0], entryTalkId=first(block), title=title,
                             videoEpisode="EPI06", videoLoop="loop1", videoScene=ref(block)["videoScene"])
                        for scene, block, title in [("entrance", "entrance", "门外接头"),
                            ("lobby", "lobby_intro", "大堂前置合作交谈"),
                            ("lobby", "gunshot", "大堂枪响"),
                            ("discovery", "discovery", "枪响后发现现场")]]
    chapter = dict(id="601", chapterTitle=["枪声之后", ""], chapterBrief=["查清会客室里发生了什么。", ""],
                   chapterGoal=["核查 Rosa 对 Vivian 手中小枪的指认。", ""],
                   initTalk=first("entrance"), initScene="6103", openingScene="6100", explorationEntryScene="6103",
                   openingSequence=opening_sequence, doubts=deepcopy(doubts), clearDoubts=["6101"],
                   exposes=deepcopy(exposes), exposeNpcId="603", exposeScene="6103",
                   topBg=scenes[-1]["location"]["backgroundImage"], map2Scenes=[dict(mapId="601", sceneId="6103")],
                   summaryTitle=["这把枪近期没有开火", ""],
                   summaryContent=["检查排除了 Vivian 当时持有的小手枪近期击发。Morrison 仍要问话，并允许 Zack 继续调查 72 小时。", ""],
                   newDoubtTitle=["Webb 的生意", ""], newDoubtContent=["真正的枪击仍需调查。", ""],
                   postExposeSegments=[dict(order=1, type="talk", title="争取调查时间与 L1 收束", sceneId="6103",
                       entryTalkId=first("negotiation"), videoScene=ref("negotiation")["videoScene"], videoEpisode="EPI06", videoLoop="loop1")],
                   previewStatus="experimental_table_preview")
    additions = dict(ChapterConfig=[chapter], SceneConfig=scenes, LocationConfig=locations,
                     ItemStaticData=[raw, commission], NPCStaticData=new_npcs, NPCLoopData=npc_loops,
                     Talk=talks, Testimony=full_testimonies, TestimonyItem=testimonies, DoubtConfig=doubts, ExposeData=exposes)
    report = dict(unit="Unit6", episode="EPI06", loop="loop1", source=SOURCE.relative_to(ROOT).as_posix(),
                  sourceNodes=sum(map(len, blocks.values())), topics=8, items=ITEMS, dialogues={key: first(key) for key in BLOCKS},
                  blockTalkIds={key: [r["id"] for r in groups[key]] for key in BLOCKS}, menus=menu_ids,
                  grantNodes=grant_nodes, counts={key: len(rows) for key, rows in additions.items()},
                  addedIds={key: [row_id(row, key) for row in rows] for key, rows in additions.items()},
                  sharedItemIdException="6208 is a retained L2 prototype ID; its actual source is L1, from analysis of 6101.")
    return additions, report


def build_plan(source=SOURCE):
    require(not REPORT.exists(), "L1 is already imported. Refusing to overwrite shared tables; use a separately reviewed Words sync.")
    before = {p.stem: read(p) for p in sorted(TABLES.glob("*.json"))}
    additions, report = compile_rows(parse_source(source), before)
    merged = deepcopy(before)
    for table, rows in additions.items():
        require(isinstance(before.get(table), list), f"Missing array table: {table}")
        existing = [row_id(row, table) for row in before[table]]
        incoming = [row_id(row, table) for row in rows]
        require(len(existing) == len(set(existing)), f"Existing duplicate IDs in {table}")
        require(len(incoming) == len(set(incoming)) and not set(existing).intersection(incoming), f"ID collision in {table}")
        merged[table].extend(deepcopy(rows))
    originals = [r for r in before["ItemStaticData"] if str(r["id"]) == "6208"]
    require(len(originals) == 1 and originals[0].get("Chapter") == "EPI06", "Expected one existing EPI06 item 6208")
    old_item = deepcopy(originals[0])
    require(old_item.get("beforeAnalysedEvidence") in (None, "", "6101"), "6208 has an unexpected analysis source")
    new_item = dict(deepcopy(old_item), Loop=1, beforeAnalysedEvidence="6101", obtainMethod="auto")
    merged["ItemStaticData"] = [deepcopy(new_item) if str(r["id"]) == "6208" else r for r in merged["ItemStaticData"]]
    report["updatedRows"] = {"ItemStaticData": [dict(id="6208", before=old_item, after=new_item,
                                                    fields=["Loop", "beforeAnalysedEvidence", "obtainMethod"])]}
    report["preservedRowsSha256"] = {k: digest(v) for k, v in before.items() if isinstance(v, list)}
    report["preservedObjectsSha256"] = {k: digest(v) for k, v in before.items() if not isinstance(v, list)}
    report["sourceSha256"] = hashlib.sha256(Path(source).read_bytes()).hexdigest()

    old_manifest, old_flow = read(MANIFEST), read(FLOW)
    manifest = deepcopy(old_manifest)
    experiments = [e for e in manifest.get("experimentalUnits", []) if e.get("unit") == "Unit6"]
    require(len(experiments) == 1 and experiments[0].get("unityEpisode") == "EPI06", "Missing Unit6 experiment registration")
    experiment = experiments[0]
    require(experiment.get("presentLoops") == [2], "Unexpected already-present Unit6 loops")
    experiment["presentLoops"] = [1, 2]
    sources = experiment.setdefault("sources", {})
    # Keep the original single L2 draft path for existing consumers.
    sources.setdefault("drafts", {})["loop1"] = SOURCE.relative_to(ROOT).as_posix()
    sources["drafts"].setdefault("loop2", sources.get("draft", "剧情设计/试验单元/U1_五Loop试验版/L2_完整对白.md"))
    report["manifestBeforeSha256"] = digest(old_manifest)
    report["manifestUnit6Before"] = next(e for e in old_manifest["experimentalUnits"] if e["unit"] == "Unit6")
    report["manifestUnit6After"] = deepcopy(experiment)

    # The existing builder always writes a full payload. Stage its inputs/output
    # outside the project, then retain every existing non-Unit6 object unchanged.
    from build_unit_flow import build as build_flow
    with tempfile.TemporaryDirectory(prefix="ndc-u6-l1-dryrun-") as directory:
        stage = Path(directory)
        for name, rows in merged.items():
            write_json(stage / "table" / f"{name}.json", rows)
        write_json(stage / "canon_manifest.json", manifest)
        generated = build_flow(table_dir=str(stage / "table"), out_path=str(stage / "flow.json"),
                               manifest_path=str(stage / "canon_manifest.json"))
    flow = deepcopy(old_flow)
    old_u6 = old_flow["units"]["Unit6"]
    new_u6 = deepcopy(generated["units"]["Unit6"])
    require([l["id"] for l in new_u6["loops"]] == ["loop1", "loop2"], "Unexpected generated Unit6 loops")
    require(next(l for l in new_u6["loops"] if l["id"] == "loop2") == next(l for l in old_u6["loops"] if l["id"] == "loop2"),
            "Builder would change the existing L2 flow; refusing the merge")
    flow["units"]["Unit6"] = new_u6
    report["flowBeforeSha256"] = digest(old_flow)
    report["flowUnit6Before"] = deepcopy(old_u6)
    report["flowUnit6AfterSha256"] = digest(new_u6)
    return dict(before=before, tables=merged, additions=additions, report=report,
                manifest=manifest, flow=flow, manifestBefore=old_manifest, flowBefore=old_flow)


def apply_plan(plan):
    require(not REPORT.exists(), "L1 already imported")
    for table, value in plan["before"].items():
        require(read(TABLES / f"{table}.json") == value, f"Table changed after preflight: {table}")
    require(read(MANIFEST) == plan["manifestBefore"] and read(FLOW) == plan["flowBefore"], "Manifest/flow changed after preflight")
    targets = {TABLES / f"{table}.json": plan["tables"][table] for table in plan["additions"]}
    targets.update({MANIFEST: plan["manifest"], FLOW: plan["flow"], REPORT: plan["report"]})
    # Pre-serialize everything and roll back on a write error. Successful import
    # remains one-time; no raw, untracked overwrite path is provided.
    payloads = {path: (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8") for path, value in targets.items()}
    backups = {path: path.read_bytes() if path.exists() else None for path in targets}
    written = []
    try:
        for path, payload in payloads.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            written.append(path)
            path.write_bytes(payload)
    except Exception:
        for path in reversed(written):
            if backups[path] is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(backups[path])
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--dry-run", "--dryrun", action="store_true")
    args = parser.parse_args()
    plan = build_plan()
    if args.write:
        apply_plan(plan)
    print(json.dumps(dict(mode="written" if args.write else "dry-run", counts=plan["report"]["counts"],
                         sourceNodes=plan["report"]["sourceNodes"], topics=8,
                         updatedExistingRows={"ItemStaticData": ["6208"]}, loops=[1, 2]), ensure_ascii=False))


if __name__ == "__main__":
    main()
