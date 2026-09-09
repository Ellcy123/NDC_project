"""Shared scene scale evidence: metric height, separate footprint, bounded review.

This validates supplied evidence and arithmetic. It does not infer camera geometry,
inspect images, authorize generation, or upgrade historical v1 reports.
"""
from pathlib import Path
import hashlib
import json
import math
import statistics

from PIL import Image, ImageDraw

SCHEMA = 'ndc-scene-absolute-scale/v2'
REPORT = 'ndc-scene-absolute-scale-report/v2'
BOUNDED_CHECKS = {'boundedRangeJustified', 'boundedPlacementInvariant',
                  'boundedSupport', 'boundedHeadScale', 'boundedUIReadability'}


def need(ok, message):
    if not ok:
        raise ValueError('SCENE_GEOMETRY_BLOCKED: ' + message)


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(value):
    return isinstance(value, str) and bool(value.strip())


def number(value, label, positive=True):
    need(isinstance(value, (int, float)) and not isinstance(value, bool)
         and math.isfinite(value) and (value > 0 if positive else True), label + ' must be finite' + (' and positive' if positive else ''))
    return float(value)


def interval(value, label, positive=False):
    need(isinstance(value, list) and len(value) == 2, label + ' needs two bounds')
    low, high = (number(v, label, positive) for v in value)
    need(low <= high, label + ' bounds are reversed')
    return [low, high]


def ref(item, base):
    need(isinstance(item, dict) and text(item.get('path')) and text(item.get('sha256')), 'hashed evidence reference required')
    path = Path(item['path'])
    path = path if path.is_absolute() else Path(base) / path
    need(path.is_file() and sha(path).lower() == item['sha256'].lower(), 'missing or stale evidence: ' + str(path))
    return path.resolve()


def geometry(data):
    """Calibration is excluded so immutable pose snapshots cannot form a hash cycle."""
    return {key: data[key] for key in ('scene', 'sceneSize', 'characterHeightCm', 'target')}


def height(data):
    target = data['target']
    return number(target['standingEquivalentHeightPx'] if target.get('placementClass') in ('seated', 'lying')
                  else target['visibleHeightPx'], 'standing-equivalent image height')


def _line(anchor, size):
    line = anchor.get('measurementLine')
    need(isinstance(line, list) and len(line) == 2 and all(isinstance(p, list) and len(p) == 2 for p in line), 'two measured line endpoints required')
    for point in line:
        for value, bound in zip(point, size):
            need(0 <= number(value, 'measurement coordinate', False) < bound, 'measurement line outside scene')
    length = math.dist(*line)
    need(length > 0, 'zero-length measurement')
    return length


def _direction(anchor, base):
    if anchor['axis'] == 'vertical':
        return 1.0
    transfer = anchor.get('projectionEvidence', {}).get('directionTransfer')
    need(isinstance(transfer, dict) and text(transfer.get('method')), 'horizontal height anchor requires directionTransfer')
    ref(transfer.get('artifact'), base)
    return number(transfer.get('verticalPxPerCm'), 'vertical rate') / number(transfer.get('sourceAxisPxPerCm'), 'source-axis rate')


def _review(reference, base, artifacts, extra_checks=(), source_sha=None):
    # Reuse the native actual whole/local inspection gate, not an authored boolean.
    import production_gate as production
    review_path = ref(reference, base)
    report = production.validate_visual_report(reference, 'scene-scale review', Path(base) / 'scale.json')
    need(report['stage'] == 'exact-pose-whitebox', 'bounded geometry requires actual whitebox inspection')
    need(all(report['checks'].get(key) == 'pass' for key in extra_checks), 'missing/failed bounded sensitivity judgment')
    hashes = {item['sha256'].lower() for item in report['artifacts']}
    if source_sha:
        need(source_sha.lower() in hashes, 'bounded review does not bind the current scene context')
    for item in artifacts:
        ref(item, base)
        need(item['sha256'].lower() in hashes, 'current whitebox/sensitivity image is not in its visual review')
    return report


def _bounded(data, base, actors, snapshots):
    from scene_staging_tools import validate_support_contact, validate_cast_scale, validate_ui_safety
    bounded = data.get('boundedEvidence', {})
    assumptions = bounded.get('assumptions')
    need(isinstance(assumptions, list) and assumptions and all(text(a.get('id')) and text(a.get('statement')) for a in assumptions), 'explicit bounded assumptions required')
    need(len({a['id'] for a in assumptions}) == len(assumptions), 'duplicate assumption')
    for assumption in assumptions:
        ref(assumption.get('evidence'), base)
    complete = bounded.get('isolatedActors', {})
    need(set(complete) == set(actors), 'complete independent whitebox required for every actor')
    combined = bounded.get('combinedSnapshots')
    expected = data.get('snapshots')
    need(isinstance(expected, list) and expected, 'full simultaneous-cast snapshot scope required')
    expected_pairs = set()
    for snapshot in expected:
        need(text(snapshot.get('snapshotId')) and isinstance(snapshot.get('actorPoseIds'), dict) and snapshot['actorPoseIds'], 'snapshot actor-pose map required')
        for actor_id, pose_id in snapshot['actorPoseIds'].items():
            need(actor_id in actors and pose_id == actors[actor_id]['poseId'], 'snapshot differs from exact actor pose')
            expected_pairs.add((snapshot['snapshotId'], pose_id))
    need(isinstance(combined, dict) and set(combined) == {s['snapshotId'] for s in expected}, 'complete combined snapshots required')
    visual = bounded.get('visualReviewReports')
    need(isinstance(visual, list) and visual, 'actual full/local whitebox reviews required')
    reviews = [_review(item, base, [], source_sha=data['sceneSha256']) for item in visual]
    reviewed = {a['sha256'].lower() for r in reviews for a in r['artifacts']}
    pairs = {(s, pose) for r in reviews for a in r['artifacts'] for s in a.get('snapshotIds', []) for pose in a.get('poseIds', [])}
    need(expected_pairs <= pairs, 'missing reviewed whole-scene snapshot-pose coverage')
    for item in list(complete.values()) + list(combined.values()):
        ref(item, base)
        need(item['sha256'].lower() in reviewed, 'current complete/combined whitebox lacks review')

    support = bounded.get('supportChecks', {})
    need(set(support) == set(actors), 'actual support check required for every actor')
    for actor_id, item in support.items():
        affordance = ref(item.get('affordance'), base)
        saved = read(ref(item.get('report'), base))
        current = validate_support_contact(affordance, snapshots[actor_id][0])
        need(saved == current and current['status'] == 'pass' and current['poseId'] == actors[actor_id]['poseId'], 'support report differs from current snapshot/affordance')
    cast = bounded.get('castScaleCheck', {})
    cast_contract = ref(cast.get('contract'), base)
    cast_data = read(cast_contract)
    need({a['actorId'] for a in cast_data['actors']} == set(actors), 'head check lacks full cast')
    dependencies = {ref(item, base) for item in cast.get('dependencies', [])}
    for actor in cast_data['actors']:
        placement = Path(actor['placementContract'])
        placement = placement if placement.is_absolute() else cast_contract.parent / placement
        need(placement.resolve() == snapshots[actor['actorId']][0], 'head check uses another pose snapshot')
        identity = Path(actor['identityScaleReference']['referenceArtifact'])
        identity = identity if identity.is_absolute() else cast_contract.parent / identity
        need(identity.resolve() in dependencies, 'current approved-card hash missing from head check')
    current_cast = validate_cast_scale(cast_contract)
    need(read(ref(cast.get('report'), base)) == current_cast and current_cast.get('headScalePriority') is True
         and current_cast.get('maxHeadDeviationRatio', 1) <= .20 and current_cast.get('maxPairwiseHeadDeviationRatio', 1) <= .20, 'current anatomical head check required')
    ui = bounded.get('uiCheck', {})
    ui_contract = ref(ui.get('contract'), base)
    ui_data = read(ui_contract)
    need({a['actorId'] for a in ui_data['actors']} == set(actors), 'actual UI check lacks cast')
    dependencies = {ref(item, base) for item in ui.get('dependencies', [])}
    for raw in ui_data['uiReferences'].values():
        path = Path(raw); path = path if path.is_absolute() else ui_contract.parent / path
        need(path.resolve() in dependencies, 'actual UI image hash missing')
    for actor in ui_data['actors']:
        snap = snapshots[actor['actorId']][1]
        need(actor['actionBBox'] == snap['target']['outerBBox'], 'UI check does not bind current action envelope')
        pose_key = {'seated': 'seatedPose', 'lying': 'lyingPose'}.get(snap['target'].get('placementClass'), 'standingPose')
        need(actor['headBBox'] == snap['target'][pose_key]['headBox'], 'UI check does not bind current anatomical head')
    current_ui = validate_ui_safety(ui_contract)
    need(read(ref(ui.get('report'), base)) == current_ui and current_ui.get('status') == 'pass', 'actual UI report differs from current inputs')

    scenarios = bounded.get('sensitivityCases')
    need(isinstance(scenarios, list) and len(scenarios) >= 2, 'at least lower/upper sensitivity scenarios required')
    values = {key: [] for key in actors}
    scenario_hashes = set()
    for scenario in scenarios:
        need(text(scenario.get('id')) and text(scenario.get('assumption')), 'explain sensitivity assumption')
        need(set(scenario.get('actors', {})) == set(actors), 'sensitivity scenario omits an actor')
        report = _review(scenario.get('review'), base, [scenario.get('artifact')], BOUNDED_CHECKS, data['sceneSha256'])
        need({a['poseId'] for a in actors.values()} <= {pose for item in report['artifacts'] for pose in item.get('poseIds', [])}, 'sensitivity view lacks whole cast')
        scenario_hashes.add(scenario['artifact']['sha256'])
        for key, current in scenario['actors'].items():
            need(current.get('supportPlaneId') == actors[key]['supportPlaneId'] and current.get('affordanceZoneId') == snapshots[key][1]['target']['affordanceZoneId'], 'sensitivity changes placement or support; resolve geometry first')
            height_px = number(current.get('standingEquivalentHeightPx'), 'scenario height')
            foot = current.get('foot')
            need(isinstance(foot, list) and len(foot) == 2, 'scenario foot required')
            values[key].append([height_px] + [number(v, 'scenario foot', False) for v in foot])
    need(len(scenario_hashes) >= 2, 'distinct sensitivity outcomes require actual distinct inspected images')
    for key, actor in actors.items():
        declared = actor['boundedRanges']
        for index, name in enumerate(('heightPx', 'footX', 'footY')):
            bounds = interval(declared.get(name), name, index == 0)
            observed = [value[index] for value in values[key]]
            need(math.isclose(min(observed), bounds[0]) and math.isclose(max(observed), bounds[1]), 'sensitivity does not examine declared bounds: ' + key + '/' + name)
        low, high = declared['heightPx']
        need(low <= actor['standingEquivalentHeightPx'] <= high and (high-low)/actor['standingEquivalentHeightPx'] <= .20, 'height interval is unresolved or changes head/placement scale')
        for axis, name in enumerate(('footX', 'footY')):
            need(declared[name][0] <= snapshots[key][1]['target']['foot'][axis] <= declared[name][1], 'chosen support point outside bounded evidence')
    return {'assumptionIds': [a['id'] for a in assumptions], 'sensitivityCaseIds': [s['id'] for s in scenarios],
            'meaning': 'Bounded visual geometry only; no recovered metric camera, exact hidden foot or scale factor.'}


def validate(contract_path, report_path=None, preview_path=None):
    path = Path(contract_path).resolve(); base = path.parent; data = read(path)
    need(data.get('schema') == SCHEMA and data.get('mode') in ('metric', 'bounded'), 'v2 mode required')
    scene = ref({'path': data.get('scene'), 'sha256': data.get('sceneSha256')}, base)
    ref(data.get('depthReference'), base)
    with Image.open(scene) as image:
        size = image.size
    need(list(size) == data.get('sceneSize'), 'source scene size changed')
    planes = {p['supportPlaneId']: p for p in data.get('supportPlanes', [])}
    need(planes and len(planes) == len(data['supportPlanes']), 'unique shared support planes required')
    need(data.get('referencePlaneId') in planes, 'named common reference plane required')
    if data['mode'] == 'metric':
        need(planes[data['referencePlaneId']].get('projectionScaleFromReference') == 1, 'reference plane projects to itself at scale 1')
    actors, snapshots = {}, {}
    for item in data.get('actors', []):
        key = item.get('actorId'); plane = item.get('supportPlaneId')
        need(text(key) and key not in actors and plane in planes, 'unique actor and registered support plane required')
        snapshot_path = ref(item.get('placementSnapshot'), base); snap = read(snapshot_path)
        need(not snap.get('calibration', {}).get('sceneScaleEvidence'), 'pose snapshot must not depend on its future registry')
        snap_scene = Path(snap['scene']); snap_scene = snap_scene if snap_scene.is_absolute() else snapshot_path.parent / snap_scene
        need(snap_scene.resolve() == scene and snap['sceneSize'] == list(size), 'snapshot uses another source scene')
        need(snap['target'].get('supportPlaneId') == plane, 'snapshot support plane differs')
        pose = snap['target']['poseDefinition'].get('poseId'); need(text(pose), 'exact pose ID required')
        actors[key] = {'actorId': key, 'poseId': pose, 'supportPlaneId': plane,
                       'characterHeightCm': number(snap['characterHeightCm'], 'character height'),
                       'standingEquivalentHeightPx': height(snap), 'geometrySha256': digest(geometry(snap)),
                       'boundedRanges': item.get('boundedRanges')}
        snapshots[key] = (snapshot_path, snap)
    need(actors, 'full actor scope required')
    groups, objects, anchors, rates = set(), set(), {}, []
    for item in data.get('anchors', []):
        key = item.get('anchorId'); role = item.get('role')
        need(text(key) and key not in anchors and role in ('height-calibration', 'footprint-check'), 'unique anchor role required')
        need(text(item.get('objectId')) and item['objectId'] not in objects and text(item.get('independenceGroup')) and item['independenceGroup'] not in groups, 'anchors need distinct objects and independent groups')
        objects.add(item['objectId']); groups.add(item['independenceGroup'])
        need(item.get('axis') in ('vertical', 'horizontal'), 'anchor axis required')
        ref(item.get('evidence'), base)
        measured = _line(item, size)
        output = {**item, 'measuredObjectPx': measured}
        if role == 'height-calibration' and data['mode'] == 'metric':
            need(item.get('depthBand') in ('actor-local', 'cross-depth'), 'height local/cross-depth band required')
            real_range = interval(item.get('realWorldRangeCm'), 'realWorldRangeCm', True)
            assumed = number(item.get('assumedCm'), 'assumed height'); need(real_range[0] <= assumed <= real_range[1], 'assumed dimension outside evidence range')
            need(item.get('confidence') in ('medium', 'high'), 'metric anchors need usable confidence')
            projection = number(item.get('projectionScaleToReferencePlane'), 'reference-plane projection')
            evidence = item.get('projectionEvidence', {})
            need(evidence.get('perspectiveBasisIds'), 'actual projection basis required')
            if item['depthBand'] == 'cross-depth':
                need(evidence.get('sourceSupportPoint') and evidence.get('targetSupportPoint'), 'cross-depth support projection required')
            direction = _direction(item, base)
            output.update(verticalPxPerCm=measured * projection * direction / assumed, directionScaleToVertical=direction)
            rates.append(output)
        elif role == 'footprint-check':
            need(item['axis'] == 'horizontal', 'footprint anchor must describe horizontal occupation')
            lo, hi = interval(item.get('usableXRange'), 'usable horizontal occupation')
            need(0 <= lo < hi <= size[0], 'invalid footprint interval')
            endpoints = [point[0] for point in item['measurementLine']]
            need(min(endpoints) <= lo < hi <= max(endpoints), 'usable footprint exceeds the measured horizontal span')
        anchors[key] = output
    footprint = {k for k, a in anchors.items() if a['role'] == 'footprint-check'}
    need(footprint, 'independent horizontal footprint evidence required')
    for plane_id, plane in planes.items():
        ref(plane.get('evidence'), base)
        selected = plane.get('footprintAnchorIds')
        need(isinstance(selected, list) and selected and set(selected) <= footprint, 'each support plane needs footprint checks')
        for key, actor in actors.items():
            if actor['supportPlaneId'] == plane_id:
                box = snapshots[key][1]['target']['outerBBox']
                need(len(box) == 4 and all(math.isfinite(v) for v in box), 'valid action envelope required')
                for anchor_id in selected:
                    bounds = anchors[anchor_id]['usableXRange']
                    need(bounds[0] <= box[0] < box[2] <= bounds[1], 'action envelope exceeds reviewed horizontal footprint')
    report = {'schema': REPORT, 'contract': str(path), 'contractSha256': sha(path),
              'scene': str(scene), 'sceneSha256': sha(scene), 'mode': data['mode'],
              'status': data['mode'] + '-pass', 'anchors': list(anchors.values()),
              'actors': list(actors.values()), 'supportPlaneIds': list(planes), 'axisAwareProjection': True}
    if data['mode'] == 'metric':
        vertical = [a for a in rates if a['axis'] == 'vertical']
        need(len(vertical) >= 2 and {a['depthBand'] for a in vertical} == {'actor-local', 'cross-depth'}, 'metric needs two independent vertical height anchors spanning local/cross-depth')
        from scene_staging_tools import _weighted_median
        values = [a['verticalPxPerCm'] for a in rates]
        median = _weighted_median([(a['verticalPxPerCm'], 3.0 if a['confidence'] == 'high' else 2.0) for a in rates])
        limits = data.get('limits', {}); spread_limit = number(limits.get('maxAnchorSpreadRatio', .08), 'height spread tolerance')
        deviation = number(limits.get('maxGlobalDeviationRatio', .08), 'height deviation tolerance')
        need(spread_limit <= .35 and deviation <= .25, 'legacy tolerance ceilings retained')
        spread = (max(values)-min(values))/median
        need(spread <= spread_limit, 'height anchors disagree after depth projection')
        factors = []
        for actor in actors.values():
            projection = number(planes[actor['supportPlaneId']].get('projectionScaleFromReference'), 'support-plane projection')
            expected = median * projection * actor['characterHeightCm']
            factor = expected / actor['standingEquivalentHeightPx']
            need(abs(factor-1) <= deviation, 'current actor height disagrees with scene metric')
            actor.update(expectedHeightPx=expected, recommendedScaleFactor=factor)
            factors.append(factor)
        report.update(referenceVerticalPxPerCm=median, anchorSpreadRatio=spread,
                      recommendedGlobalScaleFactor=statistics.median(factors))
    else:
        report['boundedEvidence'] = _bounded(data, base, actors, snapshots)
    if report_path:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if preview_path:
        with Image.open(scene) as original:
            preview = original.convert('RGB')
        draw = ImageDraw.Draw(preview)
        for anchor in anchors.values():
            draw.line([tuple(p) for p in anchor['measurementLine']], fill='cyan' if anchor['role'] == 'height-calibration' else 'orange', width=2)
        Path(preview_path).parent.mkdir(parents=True, exist_ok=True); preview.save(preview_path)
    return report


def current_report(reference, base):
    path = ref(reference, base); report = read(path)
    need(report.get('schema') == REPORT, 'shared placement evidence must be a v2 report')
    contract = ref({'path': report.get('contract'), 'sha256': report.get('contractSha256')}, path.parent)
    current = validate(contract)
    need(digest(current) == digest(report), 'scene scale report no longer matches current evidence')
    return current


def placement_scale(data, base=None, expected_report=None):
    reference = data.get('calibration', {}).get('sceneScaleEvidence')
    need(reference, 'shared sceneScaleEvidence reference required')
    # Placement callers often receive an already-loaded object. Absolute references
    # are mandatory there; ledger callers may resolve relative refs to the file.
    if base is None:
        need(Path(reference.get('path', '')).is_absolute(), 'shared scale reference must be absolute')
        base = Path(reference['path']).parent
    if expected_report is None:
        report = current_report(reference, base)
    else:
        report = read(ref(reference, base))
        need(digest(report) == digest(expected_report), 'placement uses another scene registry')
    actor_id = data['calibration'].get('actorId')
    matches = [a for a in report['actors'] if a['actorId'] == actor_id]
    need(len(matches) == 1, 'placement actor missing from full shared registry')
    actor = matches[0]
    need(actor['geometrySha256'] == digest(geometry(data)), 'placement pose/height/support changed after shared scale review')
    need(Path(data['scene']).resolve() == Path(report['scene']).resolve(), 'placement scene differs from registry')
    return {'mode': report['mode'], 'heightPx': actor.get('expectedHeightPx', actor['standingEquivalentHeightPx']),
            'heightRangePx': actor.get('boundedRanges', {}).get('heightPx') if actor.get('boundedRanges') else None,
            'spread': report.get('anchorSpreadRatio', 0.0), 'report': report, 'actorId': actor_id}
