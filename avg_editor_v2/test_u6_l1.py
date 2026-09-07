"""Check the real L1 draft/plan before import, or its shared rows after import.

Runs against production configuration and the approved MD; creates no fixtures
and never writes shared tables. python -B avg_editor_v2/test_u6_l1.py
"""
from copy import deepcopy
import json
from pathlib import Path
import re
import unittest

import import_u6_l1 as importer


class TrialL1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.blocks = importer.parse_source()
        cls.persisted = importer.REPORT.exists()
        if cls.persisted:
            cls.report = importer.read(importer.REPORT)
            cls.tables = {p.stem: importer.read(p) for p in importer.TABLES.glob("*.json")}
            cls.manifest = importer.read(importer.MANIFEST)
            cls.flow = importer.read(importer.FLOW)
        else:
            plan = importer.build_plan()
            cls.report, cls.tables = plan["report"], plan["tables"]
            cls.manifest, cls.flow = plan["manifest"], plan["flow"]
        cls.new = {name: [r for r in cls.tables[name] if importer.row_id(r, name) in ids]
                   for name, ids in cls.report["addedIds"].items()}
        cls.talks = {str(r["id"]): r for r in cls.new["Talk"]}
        cls.all_talks = {str(r["id"]): r for r in cls.tables["Talk"]}
        cls.chapter = cls.new["ChapterConfig"][0]

    def test_preflight_writes_no_project_data_and_repeat_is_refused(self):
        def snapshot():
            paths = set(importer.TABLES.glob("*.json")) | {importer.MANIFEST, importer.FLOW, importer.REPORT}
            return {str(path): path.read_bytes() if path.exists() else None for path in paths}
        before = snapshot()
        if self.persisted:
            with self.assertRaisesRegex(ValueError, "already imported"):
                importer.build_plan()
        else:
            importer.build_plan()
        self.assertEqual(snapshot(), before)

    def test_existing_rows_and_l2_are_preserved(self):
        for table, expected_hash in self.report["preservedRowsSha256"].items():
            rows = deepcopy(self.tables[table])
            if table not in self.report["addedIds"] and table not in self.report["updatedRows"]:
                self.assertEqual(importer.digest(rows), expected_hash, table)
                continue
            ids = [importer.row_id(r, table) for r in rows]
            self.assertEqual(len(ids), len(set(ids)), table)
            added = set(self.report["addedIds"].get(table, []))
            rows = [r for r in rows if importer.row_id(r, table) not in added]
            updates = {r["id"]: r for r in self.report["updatedRows"].get(table, [])}
            for index, row in enumerate(rows):
                rid = importer.row_id(row, table)
                if rid in updates:
                    self.assertEqual(row, updates[rid]["after"])
                    rows[index] = updates[rid]["before"]
            self.assertEqual(importer.digest(rows), expected_hash, table)
        for table, expected_hash in self.report["preservedObjectsSha256"].items():
            self.assertEqual(importer.digest(self.tables[table]), expected_hash, table)
        self.assertEqual(set(self.report["updatedRows"]), {"ItemStaticData"})
        self.assertEqual(len(self.report["updatedRows"]["ItemStaticData"]), 1)
        update = self.report["updatedRows"]["ItemStaticData"][0]
        self.assertEqual(update["id"], "6208")
        restored = dict(update["after"])
        for field in update["fields"]:
            if field in update["before"]:
                restored[field] = update["before"][field]
            else:
                restored.pop(field, None)
        self.assertEqual(restored, update["before"])

    def test_md_words_speakers_and_grant_locations(self):
        self.assertEqual(set(self.blocks), set(importer.BLOCKS))
        self.assertEqual(self.report["sourceNodes"], sum(map(len, self.blocks.values())))
        self.assertEqual(len(self.talks), self.report["sourceNodes"] + 7)
        actual_grants = {}
        for key, nodes in self.blocks.items():
            tids = self.report["blockTalkIds"][key]
            self.assertEqual(len(nodes), len(tids), key)
            for index, (node, tid) in enumerate(zip(nodes, tids)):
                talk = self.talks[tid]
                self.assertEqual(talk["Words"][0], node["text"], tid)
                self.assertEqual(talk["Speaker"]["id"], importer.SPEAKERS[node["speaker"]], tid)
                self.assertFalse(talk.get("cnAction"), tid)
                if node["grants"]:
                    grant = node["grants"][0]
                    self.assertEqual(talk["script"], "3", tid)
                    self.assertEqual(talk["Parameters"][0]["ParameterInt"], importer.ITEMS[grant])
                    self.assertEqual(self.report["grantNodes"][grant]["nodeIndex"], index)
                    actual_grants[grant] = tid
                else:
                    self.assertNotEqual(talk["script"], "3", tid)
        self.assertEqual(set(actual_grants), set(importer.ITEMS))
        self.assertEqual(sum(t["script"] == "3" for t in self.talks.values()), 7)

    def test_graph_and_free_topic_order(self):
        for tid, talk in self.talks.items():
            self.assertRegex(tid, r"^6\d{8}$")
            self.assertEqual(talk["videoEpisode"], "EPI06")
            self.assertEqual(talk["videoLoop"], "loop1")
            if talk.get("next"):
                self.assertIn(talk["next"], self.talks, tid)
        menus = self.report["menus"]
        self.assertEqual(len(menus), 4)
        self.assertEqual(sum(len(self.talks[tid]["Parameters"]) - 1 for tid in menus.values()), 8)
        for key, (_, intro, repeat, topics) in importer.MENUS.items():
            menu = self.talks[menus[key]]
            self.assertEqual(menu["script"], "1")
            self.assertEqual(len(menu["Parameters"]), 3)
            self.assertEqual(self.talks[self.report["blockTalkIds"][intro][-1]]["next"], menu["id"])
            if repeat:
                self.assertEqual(self.talks[self.report["blockTalkIds"][repeat][-1]]["next"], menu["id"])
            for parameter, (_, block) in zip(menu["Parameters"], topics):
                self.assertEqual(parameter["ParameterInt"], self.report["dialogues"][block])
                self.assertEqual(self.talks[self.report["blockTalkIds"][block][-1]]["next"], menu["id"])
            exit_id = menu["Parameters"][-1]["ParameterInt"]
            if key == "emma":
                self.assertEqual(exit_id, self.report["dialogues"]["cooperation_close"])
            else:
                self.assertEqual(self.talks[exit_id]["script"], "2")
                self.assertFalse(self.talks[exit_id]["next"])
        for left, right in [("entrance", "lobby_intro"), ("cooperation_close", "gunshot"),
                            ("gunshot", "discovery"), ("expose_open", "expose_lie"),
                            ("expose_lie", "expose_success"), ("expose_success", "negotiation"),
                            ("negotiation", "ending"), ("expose_wrong", "expose_lie")]:
            self.assertEqual(self.talks[self.report["blockTalkIds"][left][-1]]["next"], self.report["dialogues"][right])
        self.assertEqual(self.talks[self.report["blockTalkIds"]["discovery"][-1]]["script"], "2")
        for key in ("cooperation_close", "gunshot", "discovery"):
            self.assertTrue(all(self.talks[t]["script"] != "1" for t in self.report["blockTalkIds"][key]))
        roots = [self.chapter["initTalk"], self.report["dialogues"]["expose_open"]]
        for scene in self.new["SceneConfig"]:
            roots.extend(ref["id"] for ref in scene["previewTalks"])
            roots.extend(n[k]["id"] for n in scene["NPCInfos"] for k in ("TalkInfo", "LoopTalkInfo"))
        seen, todo = set(), roots[:]
        while todo:
            tid = todo.pop()
            if tid in seen:
                continue
            seen.add(tid)
            talk = self.talks[tid]
            if talk.get("next"):
                todo.append(talk["next"])
            if talk["script"] == "1":
                todo.extend(p["ParameterInt"] for p in talk["Parameters"])
        self.assertEqual(seen, set(self.talks))

    def test_one_expose_and_pre_expose_sources(self):
        self.assertEqual(self.chapter["exposes"], self.new["ExposeData"])
        self.assertEqual(self.chapter["doubts"], self.new["DoubtConfig"])
        self.assertEqual(len(self.chapter["exposes"]), 1)
        expose = self.chapter["exposes"][0]
        self.assertEqual((expose["testimony"], expose["item"]), ("6031001", ["6208"]))
        self.assertEqual(self.chapter["clearDoubts"], ["6101"])
        self.assertEqual({(c["type"], c["param"]) for c in self.chapter["doubts"][0]["condition"]},
                         {("1", "6208"), ("4", "6031001"), ("1", "6103")})
        self.assertEqual(sum(t["script"] == "7" for t in self.talks.values()), 1)
        self.assertEqual(sum(t["script"] == "15" for t in self.talks.values()), 1)
        self.assertEqual(self.talks[self.report["blockTalkIds"]["ending"][-1]]["script"], "15")
        self.assertEqual(self.talks[self.report["blockTalkIds"]["expose_success"][-1]]["script"], "11")
        for key in ("expose_open", "expose_lie", "expose_success", "expose_wrong", "negotiation", "ending"):
            self.assertTrue(all(self.talks[tid]["script"] != "3" for tid in self.report["blockTalkIds"][key]))
        compact = lambda s: re.sub(r"\s+", "", s)
        granted_claim = self.talks[self.report["grantNodes"]["rosa_claim"]["talkId"]]["Words"][0]
        self.assertIn(compact(importer.LIE), compact(granted_claim))
        self.assertIn(compact(importer.LIE), compact("".join(n["text"] for n in self.blocks["expose_lie"])))
        cards = {r["id"]: r for r in self.tables["ItemStaticData"]}
        self.assertEqual(cards["6101"]["analysedEvidence"], "6208")
        self.assertEqual(cards["6208"]["beforeAnalysedEvidence"], "6101")
        self.assertEqual(cards["6208"]["Loop"], 1)
        self.assertEqual(cards["6208"]["obtainMethod"], "auto")
        self.assertEqual(self.all_talks["601000001"]["Parameters"][0]["ParameterInt"], "6208")
        self.assertEqual(self.all_talks["601000002"]["Parameters"][0]["ParameterInt"], "6032001")

    def test_scene_and_table_references(self):
        scenes = {s["sceneId"]: s for s in self.new["SceneConfig"]}
        self.assertEqual({sid for sid, s in scenes.items() if s["isOpen"]}, {"6103"})
        self.assertEqual({n["NPC"]["id"] for n in scenes["6103"]["NPCInfos"]}, {"603", "606", "611"})
        self.assertEqual([n["NPC"]["id"] for n in scenes["6101"]["NPCInfos"]], ["602"])
        self.assertEqual(scenes["6103"]["ItemIDs"], ["6101", "6103"])
        locations = {r["id"]: r for r in self.new["LocationConfig"]}
        npc_loops = {r["id"]: r for r in self.new["NPCLoopData"]}
        npcs = {r["id"]: r for r in self.tables["NPCStaticData"]}
        for scene in scenes.values():
            self.assertEqual(scene["location"], locations[scene["location"]["id"]])
            for npc in scene["NPCInfos"]:
                self.assertEqual(npc, npc_loops[npc["id"]])
                self.assertEqual(npc["NPC"], npcs[npc["NPC"]["id"]])
            refs = scene["previewTalks"] + [n[k] for n in scene["NPCInfos"] for k in ("TalkInfo", "LoopTalkInfo")]
            for ref in refs:
                talk = self.talks[ref["id"]]
                for field in ("videoEpisode", "videoLoop", "videoScene"):
                    self.assertEqual(ref[field], talk[field])
        for row in self.new["Testimony"]:
            self.assertIn(row["id"], self.talks)
            self.assertEqual(row["chapter"], "601")
            self.assertEqual(row["evidenceItem"][0]["id"], self.talks[row["id"]]["Parameters"][0]["ParameterInt"])
        for key in ("initScene", "openingScene", "explorationEntryScene", "exposeScene"):
            self.assertIn(self.chapter[key], scenes)
        for entry in self.chapter["openingSequence"]:
            self.assertIn(entry["sceneId"], scenes)
            self.assertIn(entry["entryTalkId"], self.talks)

    def test_canon_and_only_unit6_flow_merge(self):
        manifest = deepcopy(self.manifest)
        exp = next(e for e in manifest["experimentalUnits"] if e["unit"] == "Unit6")
        self.assertEqual(exp, self.report["manifestUnit6After"])
        self.assertEqual(exp["presentLoops"], [1, 2])
        self.assertEqual(exp["sources"]["draft"], self.report["manifestUnit6Before"]["sources"]["draft"])
        manifest["experimentalUnits"] = [self.report["manifestUnit6Before"] if e["unit"] == "Unit6" else e for e in manifest["experimentalUnits"]]
        self.assertEqual(importer.digest(manifest), self.report["manifestBeforeSha256"])
        flow = deepcopy(self.flow)
        u6 = flow["units"]["Unit6"]
        self.assertEqual(importer.digest(u6), self.report["flowUnit6AfterSha256"])
        self.assertEqual([l["id"] for l in u6["loops"]], ["loop1", "loop2"])
        self.assertEqual(u6["loops"][1], self.report["flowUnit6Before"]["loops"][0])
        dependency = next(c for c in u6["loops"][0]["doubts"][0]["conditions"] if c["param"] == "6208")
        self.assertEqual(dependency["sourceLoop"], "loop1")
        self.assertEqual(dependency["status"], "current")
        flow["units"]["Unit6"] = self.report["flowUnit6Before"]
        self.assertEqual(importer.digest(flow), self.report["flowBeforeSha256"])


if __name__ == "__main__":
    unittest.main()
