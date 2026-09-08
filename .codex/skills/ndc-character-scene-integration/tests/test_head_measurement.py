from pathlib import Path
import sys,json,tempfile,unittest,copy,math
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'scripts'))
from head_measurement import anatomical_head_height
from scene_staging_tools import validate_cast_scale
from character_scene_pipeline import validate_exact_pose, POSE_POINT_FIELDS

def pose(crown=(10,10),chin=(110,10),box=(0,0,120,20)):
 return {'headBox':list(box),'headAxis':{'crown':list(crown),'chin':list(chin),'measurementEvidence':'synthetic rotation regression fixture','projectionReview':'same in-plane head, no perspective change'}}

class HeadAxisTests(unittest.TestCase):
 def test_rotation_invariance(self):
  self.assertEqual(anatomical_head_height(pose()),100)
  self.assertEqual(anatomical_head_height(pose((10,10),(10,110),(0,0,20,120))),100)
  self.assertAlmostEqual(anatomical_head_height(pose((10,10),(70,90),(0,0,100,100))),100)
 def test_legacy_vertical_unchanged(self):
  self.assertEqual(anatomical_head_height({'headBox':[0,0,120,20]}),20)
 def test_invalid_endpoints(self):
  for axis in [pose((10,10),(10,10)),pose((10,10),(130,10)),pose((float('nan'),10)),pose((float('inf'),10))]:
   with self.subTest(axis=axis),self.assertRaises(ValueError):anatomical_head_height(axis)
 def test_missing_review_is_rejected(self):
  for field in ['measurementEvidence','projectionReview']:
   data=pose();del data['headAxis'][field]
   with self.subTest(field=field),self.assertRaises(ValueError):anatomical_head_height(data)
 def test_box_validation(self):
  for box in [[0,0,0,20],[0,0,120,float('nan')],[0,0,120]]:
   with self.subTest(box=box),self.assertRaises(ValueError):anatomical_head_height({'headBox':box})

class CastIntegrationTests(unittest.TestCase):
 def test_exact_pose_uses_same_rotated_measurement(self):
  exact=pose();exact.update({name:[100,100] for name in POSE_POINT_FIELDS});exact['supportObject']='bed'
  definition={key:'test' for key in ['poseId','action','facing','gazeTarget','leftHandAction','rightHandAction']};definition['requiredProps']=[]
  target={'lyingPose':exact,'poseDefinition':definition,'sceneRelations':[{'objectId':'bed','relation':'supported-by','regions':['leftFoot'],'reason':'test'}]}
  self.assertIs(validate_exact_pose(target,'lying',(0,0,900,800),800),exact)
  exact.pop('headAxis')
  with self.assertRaisesRegex(ValueError,'implausible'):
   validate_exact_pose(target,'lying',(0,0,900,800),800)
 def fixture(self,folder,axis=True,length=100):
  card=folder/'synthetic-reference.txt';card.write_text('TEST FIXTURE ONLY',encoding='utf-8')
  contract={'schema':'ndc-cast-scale/v2','sceneSize':[2560,1600],'horizonY':0,'referenceActorId':'A','maxDeviationRatio':0.05,'maxHeadDeviationRatio':0.05,'headScalePriority':True,'actors':[]}
  for name in ['A','B']:
   exact=pose((10,10),(10+length,10),(0,0,200,20)) if name=='B' else pose((10,10),(10,110),(0,0,20,120))
   if not axis:exact.pop('headAxis')
   placement={'sceneSize':[2560,1600],'characterName':name,'characterHeightCm':180,'target':{'foot':[500,1000],'placementClass':'lying','standingEquivalentHeightPx':800,'poseDefinition':{'poseId':name},'lyingPose':exact}}
   path=folder/(name+'.json');path.write_text(json.dumps(placement),encoding='utf-8')
   contract['actors'].append({'actorId':name,'placementContract':str(path),'identityScaleReference':{'referenceArtifact':str(card),'referenceFullBodyHeightPx':800,'referenceAnatomicalHeadHeightPx':100,'measurementMethod':'synthetic','confidence':'high'}})
  path=folder/'cast.json';path.write_text(json.dumps(contract),encoding='utf-8')
  return path
 def test_rotated_same_head_passes(self):
  with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
   report=validate_cast_scale(self.fixture(Path(temp)))
   self.assertEqual(report['status'],'pass')
   self.assertEqual(report['actors'][1]['screenVerticalHeadExtentPx'],20)
   self.assertEqual(report['actors'][1]['measuredHeadHeightPx'],100)
 def test_old_vertical_behavior_still_exposes_rotation_failure(self):
  with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
   report_path=Path(temp)/'report.json'
   with self.assertRaisesRegex(ValueError,'CAST_SCALE_FAILED'):
    validate_cast_scale(self.fixture(Path(temp),axis=False),report_path)
   report=json.loads(report_path.read_text(encoding='utf-8'))
   self.assertEqual(report['status'],'fail')
 def test_genuinely_oversized_head_still_fails(self):
  with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
   report_path=Path(temp)/'report.json'
   with self.assertRaisesRegex(ValueError,'CAST_SCALE_FAILED'):
    validate_cast_scale(self.fixture(Path(temp),length=140),report_path)
   report=json.loads(report_path.read_text(encoding='utf-8'))
   self.assertEqual(report['status'],'fail')
   self.assertEqual(report['actors'][1]['headStatus'],'fail')

 def test_user_twenty_percent_head_tolerance_accepts_eighteen_percent(self):
  with tempfile.TemporaryDirectory() as temp:
   path=self.fixture(Path(temp),length=118)
   data=json.loads(path.read_text());data.update(maxHeadDeviationRatio=.20,maxPairwiseHeadDeviationRatio=.20);path.write_text(json.dumps(data))
   self.assertEqual(validate_cast_scale(path)['status'],'pass')
 def test_user_tolerance_does_not_allow_twenty_five_percent(self):
  with tempfile.TemporaryDirectory() as temp:
   path=self.fixture(Path(temp),length=125)
   data=json.loads(path.read_text());data.update(maxHeadDeviationRatio=.20,maxPairwiseHeadDeviationRatio=.20);path.write_text(json.dumps(data))
   with self.assertRaisesRegex(ValueError,'CAST_SCALE_FAILED'):validate_cast_scale(path)
 def test_pair_tolerance_is_not_automatically_doubled_to_forty_percent(self):
  with tempfile.TemporaryDirectory() as temp:
   path=self.fixture(Path(temp),length=100)
   data=json.loads(path.read_text());data['maxHeadDeviationRatio']=.20;path.write_text(json.dumps(data))
   self.assertEqual(validate_cast_scale(path)['maxPairwiseHeadDeviationRatio'],.20)

if __name__=='__main__':unittest.main(verbosity=2)
