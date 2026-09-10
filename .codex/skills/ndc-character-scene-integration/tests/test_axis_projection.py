from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scene_staging_tools as tools
import production_gate


class AxisProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.metric = self.root / 'metric.json'
        self.metric.write_text('{"fixture":"horizontal projection is foreshortened by one half"}', encoding='utf-8')
        self.contract = {
            'schema': 'ndc-scene-absolute-scale/v1', 'scene': 'unused.png',
            'sceneSize': [400, 300],
            'actors': [{'actorId': 'A', 'characterHeightCm': 170, 'standingEquivalentHeightPx': 170}],
            'limits': {'maxGlobalDeviationRatio': .05, 'maxAnchorSpreadRatio': .08, 'minimumIndependentAnchors': 3},
            'anchors': [],
        }
        for index, (axis, line) in enumerate([
            ('vertical', [[20, 20], [20, 120]]),
            ('vertical', [[200, 20], [200, 120]]),
            ('horizontal', [[50, 150], [100, 150]]),
        ]):
            self.contract['anchors'].append({
                'anchorId': f'anchor{index}', 'objectId': f'object{index}',
                'independenceGroup': f'group{index}', 'actorId': 'A',
                'axis': axis, 'depthBand': 'actor-local' if index == 0 else 'cross-depth',
                'realWorldRangeCm': [95, 105], 'assumedCm': 100,
                'measurementLine': line, 'projectionScaleToActorPlane': 1,
                'confidence': 'high',
                'projectionEvidence': {'perspectiveBasisIds': ['synthetic-camera'],
                    'sourceSupportPoint': [150, 200], 'targetSupportPoint': [200, 200]},
            })
        self.horizontal = self.contract['anchors'][2]
        self.transfer = {'method': 'Synthetic metric fixture: horizontal foreshortening at equal depth',
            'sourceAxisPxPerCm': .5, 'verticalPxPerCm': 1,
            'artifact': {'path': self.metric.name, 'sha256': tools.sha256(self.metric)}}
        self.horizontal['projectionEvidence']['directionTransfer'] = self.transfer

    def evaluate(self):
        path = self.root / 'scale.json'
        path.write_text(json.dumps(self.contract), encoding='utf-8')
        return tools.validate_scene_absolute_scale(path)

    def test_foreshortened_width_needs_separate_direction_conversion(self):
        report = self.evaluate()
        self.assertEqual(report['status'], 'pass')
        self.assertTrue(report['axisAwareProjection'])
        self.assertEqual(report['anchors'][2]['expectedActorHeightPx'], 170)
        self.assertEqual(report['anchors'][2]['directionScaleToVertical'], 2)
        self.transfer['verticalPxPerCm'] = .5
        with self.assertRaises(ValueError):
            self.evaluate()

    def test_depth_multiplier_cannot_stand_in_for_direction_evidence(self):
        del self.horizontal['projectionEvidence']['directionTransfer']
        self.horizontal['projectionScaleToActorPlane'] = 2
        with self.assertRaisesRegex(ValueError, 'requires directionTransfer'):
            self.evaluate()

    def test_changed_metric_evidence_invalidates_previous_inputs(self):
        self.evaluate()
        self.metric.write_text('{"fixture":"changed"}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'missing or stale'):
            self.evaluate()

    def test_nonfinite_or_nonpositive_direction_rates_are_rejected(self):
        for value in (0, -1, float('nan'), float('inf')):
            with self.subTest(value=value):
                self.transfer['sourceAxisPxPerCm'] = value
                with self.assertRaisesRegex(ValueError, 'finite and positive'):
                    self.evaluate()

    def case_with_report(self, report):
        scene = self.root / 'scene.bin'
        scene.write_bytes(b'unchanged scene fixture')
        report_path = self.root / 'report.json'
        report_path.write_text(json.dumps(report), encoding='utf-8')
        case = {key: [] for key in ('affordanceContract', 'uiSafetyReports', 'placementContracts',
            'stagingContracts', 'whiteboxEvidence', 'supportContactReports', 'castScaleReport',
            'localGenerationHandoffs', 'visualReviewReports')}
        case.update(caseId='fixture', branch='pure-narrative', sourceScene=str(scene),
            sourceSceneSha256=tools.sha256(scene), technicalStatus='TECHNICAL_FILE_PASS',
            scaleDriver='standing-equivalent-multi-anchor',
            sceneAbsoluteScaleReport={'path': str(report_path), 'sha256': tools.sha256(report_path)})
        return case

    def test_ledger_rejects_old_arithmetic_only_pass(self):
        report = self.evaluate()
        del report['axisAwareProjection']
        with self.assertRaisesRegex(ValueError, 'current axis-aware'):
            production_gate.validate_case(self.case_with_report(report), 0, self.root / 'ledger.json', 'pre-generation')

    def test_ledger_rechecks_metric_artifact_behind_unchanged_report(self):
        report = self.evaluate()
        case = self.case_with_report(report)
        # The valid scale check progresses to the next, intentionally absent gate.
        with self.assertRaisesRegex(ValueError, 'componentPolicyReports'):
            production_gate.validate_case(case, 0, self.root / 'ledger.json', 'pre-generation')
        self.metric.write_text('{"fixture":"changed later"}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'missing or stale'):
            production_gate.validate_case(case, 0, self.root / 'ledger.json', 'pre-generation')


if __name__ == '__main__':
    unittest.main()
