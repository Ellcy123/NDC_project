"""Synthetic geometry/evidence protocols only, never character or camera approval."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scene_scale_v2 as scale
import scene_staging_tools as tools
import production_gate as production
import character_scene_pipeline as pipeline
import visual_review_gate as visual
import test_scene_staging_tools as existing_tests


class SceneScaleV2Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup); self.root = Path(self.temp.name)
        self.old_root_override = pipeline.TEST_ROOT_OVERRIDE
        pipeline.TEST_ROOT_OVERRIDE = self.root
        self.addCleanup(setattr, pipeline, 'TEST_ROOT_OVERRIDE', self.old_root_override)
        self.scene = self.root / 'scene.png'
        Image.new('RGB', (240, 200), (40, 50, 60)).save(self.scene)
        self.depth = self.root / 'depth.png'
        Image.new('RGB', (240, 200), (90, 90, 90)).save(self.depth)
        self.basis = self.write('geometry-basis.json', {'synthetic': True, 'meaning': 'Known test geometry, not a measured room.'})
        self.snapshot = existing_tests.SceneStagingToolTests()._placement_contract(self.root, self.scene)
        self.snapshot['target']['supportPlaneId'] = 'floor'
        self.snapshot.pop('calibration')
        self.snapshot_path = self.write('A-pose-snapshot.json', self.snapshot)
        self.data = {'schema': scale.SCHEMA, 'mode': 'metric', 'scene': str(self.scene),
                     'sceneSha256': scale.sha(self.scene), 'sceneSize': [240, 200],
                     'depthReference': self.ref(self.depth), 'referencePlaneId': 'floor', 'actors': [
                         {'actorId': 'A', 'supportPlaneId': 'floor', 'placementSnapshot': self.ref(self.snapshot_path)}],
                     'supportPlanes': [{'supportPlaneId': 'floor', 'projectionScaleFromReference': 1,
                                        'evidence': self.ref(self.basis), 'footprintAnchorIds': ['f']}],
                     'anchors': []}
        for index, band in enumerate(('actor-local', 'cross-depth')):
            self.data['anchors'].append({'anchorId': 'h' + str(index), 'objectId': 'object' + str(index),
                'independenceGroup': 'group' + str(index), 'axis': 'vertical', 'role': 'height-calibration',
                'measurementLine': [[20 + 150 * index, 20], [20 + 150 * index, 120]],
                'evidence': self.ref(self.basis), 'depthBand': band, 'realWorldRangeCm': [95, 105],
                'assumedCm': 100, 'confidence': 'high', 'projectionScaleToReferencePlane': 1,
                'projectionEvidence': {'perspectiveBasisIds': ['synthetic-camera'],
                                      'sourceSupportPoint': [170, 185], 'targetSupportPoint': [110, 185]}})
        self.data['anchors'].append({'anchorId': 'f', 'objectId': 'corridor', 'independenceGroup': 'floor-width',
            'axis': 'horizontal', 'role': 'footprint-check', 'measurementLine': [[10, 190], [220, 190]],
            'usableXRange': [10, 220], 'evidence': self.ref(self.basis)})

    def write(self, name, value):
        path = self.root / name
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
        return path

    def ref(self, path):
        return {'path': str(path), 'sha256': scale.sha(path)}

    def evaluate(self):
        self.contract = self.write('scale-v2.json', self.data)
        self.report_path = self.root / 'scale-report.json'
        return tools.validate_scene_absolute_scale(self.contract, self.report_path)

    def shared_placement(self):
        self.evaluate()
        result = copy.deepcopy(self.snapshot)
        result['calibration'] = {'sceneScaleEvidence': self.ref(self.report_path), 'actorId': 'A'}
        return result

    def review(self, name, image, bounded=False):
        tile = self.root / (name + '-200.png')
        with Image.open(image) as frame:
            frame.crop((70, 10, 150, 190)).resize((160, 360), Image.Resampling.NEAREST).save(tile)
        checks = {key: 'pass' for key in visual.STAGE_CHECKS['exact-pose-whitebox']}
        if bounded: checks.update({key: 'pass' for key in scale.BOUNDED_CHECKS})
        contract = {'schema': 'ndc-stage-visual-review/v1', 'stage': 'exact-pose-whitebox',
                    'reviewAuthority': 'codex-self-check', 'decision': 'pass', 'synthetic': True,
                    'artifacts': [{'role': 'synthetic-whitebox', **self.ref(image), 'poseIds': ['a-v1'], 'snapshotIds': ['shot-1']},
                                  {'role': 'source-scene', **self.ref(self.scene)}],
                    'localTiles': [{'id': 'synthetic-local', 'bbox': [70, 10, 150, 190], **self.ref(tile)}],
                    'checks': checks, 'observations': ['SYNTHETIC_PROTOCOL_FIXTURE; no real visual approval.']}
        path = self.write(name + '-review-contract.json', contract)
        out = self.root / (name + '-review')
        visual.build_review(path, out)
        return self.ref(out / 'exact-pose-whitebox-visual-review-report.json')

    def bounded(self):
        self.data['mode'] = 'bounded'
        self.data['anchors'] = [self.data['anchors'][-1]]
        self.data['snapshots'] = [{'snapshotId': 'shot-1', 'actorPoseIds': {'A': 'a-v1'}}]
        self.data['actors'][0]['boundedRanges'] = {'heightPx': [165, 175], 'footX': [110, 110], 'footY': [185, 185]}
        complete = self.root / 'synthetic-complete.png'
        Image.new('RGB', (240, 200), (100, 90, 70)).save(complete)
        complete_review = self.review('complete', complete)
        affordance = {'schema': 'ndc-scene-affordance/v1', 'sceneSize': [240, 200],
            'zones': [{'id': 'stand-1', 'polygon': [[70, 175], [150, 175], [150, 195], [70, 195]], 'capabilities': ['stand'], 'depthClass': 'midground'}],
            'supportSurfaces': [{'id': 'floor-1', 'evidence': 'Synthetic fixed floor',
                                 'occupancy': {'status': 'clear', 'evidence': 'Synthetic empty region'},
                                 'contacts': [{'regions': ['leftFoot', 'rightFoot'], 'polyline': [[70, 185], [150, 185]], 'tolerancePx': 2}]}],
            'placements': [{'actorId': 'A', 'placementClass': 'standing', 'anchor': [110, 185], 'zoneId': 'stand-1', 'supportObjectId': 'floor-1'}]}
        affordance_path = self.write('affordance.json', affordance)
        support_report = self.write('support-report.json', tools.validate_support_contact(affordance_path, self.snapshot_path))
        card = self.root / 'synthetic-card.png'; Image.new('RGB', (100, 170), (1, 2, 3)).save(card)
        cast = {'schema': 'ndc-cast-scale/v2', 'sceneSize': [240, 200], 'horizonY': 0,
                'referenceActorId': 'A', 'maxDeviationRatio': .08, 'headScalePriority': True,
                'maxHeadDeviationRatio': .20, 'maxPairwiseHeadDeviationRatio': .20,
                'actors': [{'actorId': 'A', 'placementContract': str(self.snapshot_path),
                            'identityScaleReference': {'referenceArtifact': str(card), 'referenceFullBodyHeightPx': 170,
                               'referenceAnatomicalHeadHeightPx': 17, 'measurementMethod': 'synthetic fixture', 'confidence': 'high'}}]}
        cast_path = self.write('cast.json', cast)
        cast_report = self.write('cast-report.json', tools.validate_cast_scale(cast_path))
        ui_image = self.root / 'synthetic-ui.png'
        ui_pixels = Image.new('RGB', (240, 200), 'white'); ImageDraw.Draw(ui_pixels).rectangle((0, 0, 30, 199), fill='black'); ui_pixels.save(ui_image)
        ui = {'schema': 'ndc-ui-safety/v1', 'sceneSize': [240, 200], 'uiReferences': {'left': str(ui_image), 'right': str(ui_image)},
              'limits': {'maxHeadOcclusionRatio': 0, 'maxActionOcclusionRatio': 0},
              'actors': [{'actorId': 'A', 'uiSide': 'left', 'headBBox': self.snapshot['target']['standingPose']['headBox'],
                          'actionBBox': self.snapshot['target']['outerBBox'], 'criticalPoints': []}]}
        ui_path = self.write('ui.json', ui)
        ui_report = self.write('ui-report.json', tools.validate_ui_safety(ui_path))
        self.data['boundedEvidence'] = {
            'assumptions': [{'id': 'floor-range', 'statement': 'Synthetic bounded floor assumption, not exact camera recovery.', 'evidence': self.ref(self.basis)}],
            'isolatedActors': {'A': self.ref(complete)}, 'combinedSnapshots': {'shot-1': self.ref(complete)},
            'visualReviewReports': [complete_review],
            'supportChecks': {'A': {'affordance': self.ref(affordance_path), 'report': self.ref(support_report)}},
            'castScaleCheck': {'contract': self.ref(cast_path), 'report': self.ref(cast_report), 'dependencies': [self.ref(card)]},
            'uiCheck': {'contract': self.ref(ui_path), 'report': self.ref(ui_report), 'dependencies': [self.ref(ui_image)]},
            'sensitivityCases': []}
        for index, height in enumerate((165, 175)):
            frame = self.root / ('scenario-' + str(index) + '.png')
            image = Image.new('RGB', (240, 200), (40, 50, 60)); ImageDraw.Draw(image).rectangle((70, 185-height, 150, 185), fill=(110, 100, 90)); image.save(frame)
            self.data['boundedEvidence']['sensitivityCases'].append({'id': 'bound-' + str(index), 'assumption': 'Synthetic lower/upper outcome',
                'artifact': self.ref(frame), 'review': self.review('scenario-' + str(index), frame, True),
                'actors': {'A': {'standingEquivalentHeightPx': height, 'foot': [110, 185], 'supportPlaneId': 'floor', 'affordanceZoneId': 'stand-1'}}})

    def test_two_vertical_plus_footprint_pass_without_direction_metric(self):
        result = self.evaluate()
        self.assertEqual(result['status'], 'metric-pass')
        self.assertEqual(result['recommendedGlobalScaleFactor'], 1)

    def test_horizontal_footprint_cannot_change_height_factor(self):
        before = self.evaluate()['recommendedGlobalScaleFactor']
        self.data['anchors'][-1]['measurementLine'] = [[20, 190], [200, 190]]
        self.data['anchors'][-1]['usableXRange'] = [20, 200]
        self.assertEqual(self.evaluate()['recommendedGlobalScaleFactor'], before)

    def test_horizontal_height_still_needs_direction_transfer(self):
        other = copy.deepcopy(self.data['anchors'][0]); other.update(anchorId='extra', objectId='extra', independenceGroup='extra', axis='horizontal')
        self.data['anchors'].append(other)
        with self.assertRaisesRegex(ValueError, 'directionTransfer'): self.evaluate()
        other['projectionEvidence']['directionTransfer'] = {'method': 'Synthetic calibrated direction', 'sourceAxisPxPerCm': 1, 'verticalPxPerCm': 1, 'artifact': self.ref(self.basis)}
        self.assertEqual(self.evaluate()['status'], 'metric-pass')

    def test_horizontal_cannot_replace_second_independent_vertical(self):
        self.data['anchors'][1]['axis'] = 'horizontal'
        self.data['anchors'][1]['projectionEvidence']['directionTransfer'] = {'method': 'synthetic', 'sourceAxisPxPerCm': 1, 'verticalPxPerCm': 1, 'artifact': self.ref(self.basis)}
        with self.assertRaisesRegex(ValueError, 'two independent vertical'): self.evaluate()

    def test_current_scene_hash_and_evidence_are_required(self):
        self.evaluate(); self.scene.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'missing or stale'): self.evaluate()

    def test_footprint_and_shared_plane_cannot_be_omitted(self):
        self.data['anchors'].pop()
        with self.assertRaisesRegex(ValueError, 'footprint'): self.evaluate()

    def test_duplicate_object_not_independent(self):
        self.data['anchors'][1]['objectId'] = self.data['anchors'][0]['objectId']
        with self.assertRaisesRegex(ValueError, 'distinct objects'): self.evaluate()

    def test_footprint_outside_action_still_blocks(self):
        self.data['anchors'][-1]['usableXRange'] = [100, 200]
        with self.assertRaisesRegex(ValueError, 'action envelope'): self.evaluate()

    def test_placement_reuses_shared_registration_without_duplicate_anchors(self):
        placement = self.shared_placement()
        self.assertEqual(scale.placement_scale(placement)['heightPx'], 170)
        production.validate_placement_contract(placement, 'A')
        # The contract validator checks the formal path name only; this test never
        # creates it or writes production files.
        placement['deliveryRoot'] = str(self.root / 'formal' / 'scene')
        self.assertEqual(pipeline.validate_contract(placement), (170, 0))

    def test_changed_pose_cannot_reuse_shared_report(self):
        placement = self.shared_placement(); placement['target']['standingPose']['leftFoot'][1] -= 5
        with self.assertRaisesRegex(ValueError, 'pose/height/support changed'): scale.placement_scale(placement)

    def test_one_staging_call_reuses_checked_registry_across_actors(self):
        second = copy.deepcopy(self.snapshot)
        second['characterName'] = 'B'
        second['target']['poseDefinition']['poseId'] = 'b-v1'
        second['target']['foot'][0] += 85
        second['target']['outerBBox'] = [155, 10, 235, 190]
        pose = second['target']['standingPose']
        pose['headBox'] = [181, 15, 199, 32]
        for key, value in pose.items():
            if isinstance(value, list) and len(value) == 2: value[0] += 85
        second_path = self.write('B-pose-snapshot.json', second)
        self.data['actors'].append({'actorId': 'B', 'supportPlaneId': 'floor', 'placementSnapshot': self.ref(second_path)})
        self.data['anchors'][-1].update(measurementLine=[[10, 190], [239, 190]], usableXRange=[10, 239])
        self.evaluate()
        placements = []
        for actor_id, source in [('A', self.snapshot), ('B', second)]:
            value = copy.deepcopy(source)
            value.update(deliveryRoot=str(self.root / 'formal' / 'scene'), calibration={'sceneScaleEvidence': self.ref(self.report_path), 'actorId': actor_id})
            placements.append(self.write(actor_id + '-final-placement.json', value))
        ui = self.write('staging-ui.json', {'schema': 'ndc-ui-safety-report/v1', 'status': 'pass', 'synthetic': True})
        staging = {'scene': str(self.scene), 'sceneSize': [240, 200], 'timelineSnapshotId': 'shot-1', 'uiSide': 'left',
                   'uiSafetyReview': {'status': 'passed', 'report': str(ui), 'reportSha256': scale.sha(ui)},
                   'characters': [{'name': key, 'contract': str(path), 'layerOrder': index}
                                  for index, (key, path) in enumerate(zip(('A', 'B'), placements))], 'occlusionGraph': []}
        with patch.object(scale, 'current_report', wraps=scale.current_report) as check:
            self.assertEqual(len(pipeline.validate_staging(staging)), 2)
            self.assertEqual(check.call_count, 1)

    def test_bounded_boolean_without_current_evidence_is_rejected(self):
        self.data.update(mode='bounded', bounded=True)
        with self.assertRaisesRegex(ValueError, 'assumptions'): self.evaluate()

    def test_bounded_current_evidence_passes_without_metric_factor(self):
        self.bounded(); result = self.evaluate()
        self.assertEqual(result['status'], 'bounded-pass')
        self.assertNotIn('recommendedGlobalScaleFactor', result)
        self.assertNotIn('recommendedScaleFactor', result['actors'][0])
        self.assertEqual(scale.placement_scale(self.shared_placement())['heightRangePx'], [165, 175])

    def test_bounded_changed_placement_scenario_blocks(self):
        self.bounded(); self.data['boundedEvidence']['sensitivityCases'][1]['actors']['A']['affordanceZoneId'] = 'other'
        with self.assertRaisesRegex(ValueError, 'changes placement'): self.evaluate()

    def test_bounded_missing_head_or_complete_whitebox_blocks(self):
        self.bounded(); self.data['boundedEvidence']['isolatedActors'] = {}
        with self.assertRaisesRegex(ValueError, 'independent whitebox'): self.evaluate()

    def test_bounded_unexamined_range_blocks(self):
        self.bounded(); self.data['actors'][0]['boundedRanges']['heightPx'] = [140, 200]
        with self.assertRaisesRegex(ValueError, 'examine declared bounds'): self.evaluate()

    def test_bounded_current_local_view_change_invalidates_report(self):
        self.bounded(); self.evaluate()
        (self.root / 'scenario-1-200.png').write_bytes(b'changed')
        with self.assertRaises(ValueError): scale.current_report(self.ref(self.report_path), self.root)

    def test_bounded_missing_actual_head_report_blocks(self):
        self.bounded(); self.data['boundedEvidence']['castScaleCheck'] = {}
        with self.assertRaisesRegex(ValueError, 'hashed evidence'): self.evaluate()

    def test_bounded_actual_ui_obstruction_is_recomputed(self):
        self.bounded()
        check = self.data['boundedEvidence']['uiCheck']
        path = Path(check['contract']['path']); ui = scale.read(path)
        ui['actors'][0]['actionBBox'] = [0, 0, 20, 100]
        path.write_text(json.dumps(ui), encoding='utf-8'); check['contract'] = self.ref(path)
        with self.assertRaisesRegex(ValueError, 'current action envelope'): self.evaluate()

    def test_bounded_support_contract_change_cannot_reuse_saved_pass(self):
        self.bounded()
        check = self.data['boundedEvidence']['supportChecks']['A']
        path = Path(check['affordance']['path']); data = scale.read(path)
        data['supportSurfaces'][0]['contacts'][0]['polyline'] = [[70, 190], [150, 190]]
        path.write_text(json.dumps(data), encoding='utf-8'); check['affordance'] = self.ref(path)
        with self.assertRaisesRegex(ValueError, 'floating'): self.evaluate()

    def test_production_gate_consumes_v2_before_other_mandatory_gates(self):
        self.evaluate()
        case = {key: [] for key in ('affordanceContract', 'uiSafetyReports', 'placementContracts', 'stagingContracts', 'whiteboxEvidence', 'supportContactReports', 'castScaleReport', 'localGenerationHandoffs', 'visualReviewReports')}
        case.update(caseId='synthetic', branch='pure-narrative', sourceScene=str(self.scene), sourceSceneSha256=scale.sha(self.scene), technicalStatus='TECHNICAL_FILE_PASS', scaleDriver='standing-equivalent-multi-anchor', sceneAbsoluteScaleReport=self.ref(self.report_path))
        with self.assertRaisesRegex(ValueError, 'componentPolicyReports'):
            production.validate_case(case, 0, self.root / 'ledger.json', 'pre-generation')
        self.basis.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'missing or stale'):
            production.validate_case(case, 0, self.root / 'ledger.json', 'pre-generation')


if __name__ == '__main__':
    unittest.main(verbosity=2)
