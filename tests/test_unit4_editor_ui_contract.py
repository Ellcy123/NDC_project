from __future__ import annotations

import unittest
from pathlib import Path


INDEX = Path(__file__).resolve().parents[1] / "avg_editor_v2" / "index.html"


class Unit4EditorUiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX.read_text(encoding="utf-8")

    def test_unit4_is_selectable_and_maps_to_epi04(self) -> None:
        self.assertIn('<option value="Unit4">Unit 4 - 四十二层之前</option>', self.html)
        self.assertIn("if (unit === 'Unit4') return 'EPI04';", self.html)

    def test_loop6_is_disabled_and_hidden_for_unit4(self) -> None:
        self.assertIn("unit === 'Unit4' && chip.dataset.loop === 'loop6'", self.html)
        self.assertIn("loop6Option.disabled = unit === 'Unit4'", self.html)
        self.assertIn("if (unit === 'Unit4' && loop === 'loop6')", self.html)

    def test_pending_avg_entries_do_not_use_npc_name_fallback(self) -> None:
        self.assertIn("if (!id && !videoScene && pendingTalkKey)", self.html)
        self.assertIn("AVG 待制作：${pendingTalkKey}", self.html)

    def test_identity_lock_and_finale_have_dedicated_renderers(self) -> None:
        self.assertIn("renderIdentityLockStage(loop)", self.html)
        self.assertIn("renderFinaleStage(loop)", self.html)
        self.assertIn("stage.type === 'identityLock'", self.html)
        self.assertIn("stage.type === 'nonLoopFinale'", self.html)

    def test_evidence_modal_renders_preview_evidence_states(self) -> None:
        self.assertIn("item.previewEvidenceStates", self.html)
        self.assertIn("证据阶段状态（预览增强）", self.html)
        self.assertIn("cn(state.Describe)", self.html)

    def test_exploration_entry_is_distinct_from_runtime_init_scene(self) -> None:
        self.assertIn("loop.explorationEntryScene || loop.initScene", self.html)
        self.assertIn("selected.explorationEntryScene || selected.initScene", self.html)

    def test_special_evidence_assets_are_not_reported_as_missing_standard_art(self) -> None:
        self.assertIn("item.previewAssetMode", self.html)
        self.assertIn("narrative_discovery: '剧情发现'", self.html)
        self.assertIn("不适用（${escapeHtml(assetDisposition)}）", self.html)

    def test_multi_background_scenes_are_associated_with_all_art_assets(self) -> None:
        self.assertIn("scene.previewBackgroundImages", self.html)
        self.assertIn("DataManager.sceneBackgrounds(scene).includes(assetId)", self.html)


if __name__ == "__main__":
    unittest.main()
