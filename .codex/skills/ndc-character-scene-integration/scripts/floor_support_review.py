"""Continuous-floor coverage plus bound human visual evidence, never a height test."""
from pathlib import Path
import hashlib
import json
import math

CRITERIA = {'weightAndSoleContact', 'floorDepthAndPerspective', 'structuralClearance', 'environmentResponse'}

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()

def validate_surface(surface, size):
    if surface.get('referenceKind') != 'continuous-floor-region':
        raise ValueError('Not a continuous floor surface')
    if surface.get('planeType') != 'floor' or surface['occupancy']['status'] != 'clear':
        raise ValueError('Continuous-region mode only supports clear floor planes')
    polygon = surface.get('supportPolygon', [])
    if len(polygon) < 3:
        raise ValueError('Continuous floor requires an independently authored supportPolygon')
    for point in polygon:
        if len(point) != 2 or not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in point):
            raise ValueError('Invalid floor polygon point')
        if not (0 <= point[0] <= size[0] and 0 <= point[1] <= size[1]):
            raise ValueError('Floor polygon exceeds canvas')
    evidence = surface.get('geometryEvidence', {})
    area2 = sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(polygon, polygon[1:]+polygon[:1]))
    if abs(area2) < 1e-8:
        raise ValueError('Floor polygon has zero area')
    if evidence.get('basis') != 'fixed-scene-and-depth' or evidence.get('derivedFromActorJoints') is not False:
        raise ValueError('Floor region must come from fixed scene/depth, not current joints')
    if not str(evidence.get('method', '')).strip() or not evidence.get('sourceScene') or not evidence.get('depthReference'):
        raise ValueError('Floor geometry provenance is incomplete')
    regions = [r for c in surface.get('contacts', []) for r in c.get('regions', [])]
    if not regions or any(r not in {'leftFoot', 'rightFoot'} for r in regions) or len(regions) != len(set(regions)):
        raise ValueError('Floor region contacts must name distinct feet')

def file_ref(ref, base):
    if not isinstance(ref, dict) or not ref.get('path') or not ref.get('sha256'):
        raise ValueError('Missing hashed evidence reference')
    p = Path(ref['path'])
    if not p.is_absolute():
        p = base / p
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest().lower() != ref['sha256'].lower():
        raise ValueError('Missing or stale evidence: ' + str(p))
    return p.resolve()

def covered(point, polygon, point_in_polygon):
    # Boundary-inclusive coverage, like Shapely covers; reuse existing interior test.
    if point_in_polygon(tuple(point), polygon):
        return True
    x, y = point
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        cross = (x-a[0])*(b[1]-a[1]) - (y-a[1])*(b[0]-a[0])
        if abs(cross) < 1e-8 and min(a[0], b[0])-1e-8 <= x <= max(a[0], b[0])+1e-8 and min(a[1], b[1])-1e-8 <= y <= max(a[1], b[1])+1e-8:
            return True
    return False

def validate_contacts(surface, placement, pose, regions, placement_path, point_in_polygon):
    validate_surface(surface, placement['sceneSize'])
    if placement['target'].get('placementClass') not in {'standing', 'walking', 'leaning', 'seated'}:
        raise ValueError('Continuous floor mode cannot replace lying or seat/body support checks')
    if not regions or any(r not in {'leftFoot', 'rightFoot'} for r in regions):
        raise ValueError('Only foot contacts may use continuous-floor mode')
    base = placement_path.parent
    geo = surface['geometryEvidence']
    source = file_ref(geo['sourceScene'], base)
    scene = Path(placement['scene'])
    if not scene.is_absolute(): scene = base / scene
    if source != scene.resolve():
        raise ValueError('Floor evidence must bind the placement source scene')
    file_ref(geo['depthReference'], base)
    review_ref = placement['target'].get('supportVisualReview')
    review_path = file_ref(review_ref, base)
    review = json.loads(review_path.read_text(encoding='utf-8-sig'))
    if review.get('schema') != 'ndc-stage-visual-self-check/v1' or review.get('visual_check_status') != 'PASS' or not review.get('reviewer') or not review.get('reviewed_at'):
        raise ValueError('Continuous floor requires a current completed visual review')
    if review.get('poseSha256') != digest(pose) or review.get('supportSurfaceSha256', {}).get(surface['id']) != digest(surface):
        raise ValueError('Visual review does not bind current pose and independent surface')
    inspected = review.get('reviewedContacts', {})
    if any(inspected.get(r) != pose.get(r) for r in regions):
        raise ValueError('Visual review did not inspect the exact current foot contacts')
    art = placement['target'].get('supportReviewArtifact')
    artifact = file_ref(art, base)
    outputs = review.get('outputs', [])
    if not any(file_ref(o, review_path.parent) == artifact for o in outputs):
        raise ValueError('Support visual review is for another image')
    views = review.get('views', [])
    if not {'whole_100', 'local_200_or_tiles'} <= {v.get('kind') for v in views}:
        raise ValueError('Missing whole/local support inspection')
    for v in views:
        view = Path(v.get('path', ''))
        if not view.is_absolute(): view = review_path.parent / view
        if not view.is_file(): raise ValueError('Missing inspected view')
    criteria = {c.get('name'): c for c in review.get('criteria', [])}
    for name in CRITERIA:
        c = criteria.get(name, {})
        if c.get('applicable') is not True or c.get('status') != 'PASS' or not str(c.get('finding', '')).strip():
            raise ValueError('Physical support review incomplete or failed: ' + name)
    results = []
    for region in regions:
        point = pose.get(region)
        if not isinstance(point, list) or len(point) != 2 or not all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in point):
            raise ValueError('Invalid foot point')
        inside = covered(point, surface['supportPolygon'], point_in_polygon)
        results.append({'region':region, 'supportObjectId':surface['id'], 'point':point, 'expectedSupportY':None, 'verticalDeltaPx':None, 'tolerancePx':None, 'condition':'inside-floor-region' if inside else 'outside-floor-region', 'status':'pass' if inside else 'fail', 'referenceKind':'continuous-floor-region', 'visualReview':str(review_path), 'visualReviewSha256':review_ref['sha256'], 'evidenceBoundary':'Region coverage plus current visual review; no independently measured vertical gap is claimed'})
    return results
