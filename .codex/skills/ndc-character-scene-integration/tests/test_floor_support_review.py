from pathlib import Path
import copy,hashlib,json,sys,tempfile,unittest
from PIL import Image
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
import floor_support_review as F
import scene_staging_tools as S

class FloorSupportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        for name in ['scene','depth','current','whole','local']:
            Image.new('RGB',(100,100),'white').save(self.root/(name+'.png'))
        self.surface={'id':'floor','referenceKind':'continuous-floor-region','planeType':'floor','occupancy':{'status':'clear','evidence':'fixture'},'evidence':'independent fixed floor','contacts':[{'regions':['leftFoot','rightFoot']}],'supportPolygon':[[10,40],[90,40],[90,99],[10,99]],'geometryEvidence':{'basis':'fixed-scene-and-depth','derivedFromActorJoints':False,'method':'fixture floor polygon, separate from foot coordinates','sourceScene':self.ref('scene.png'),'depthReference':self.ref('depth.png')}}
        self.pose={'leftFoot':[30,70],'rightFoot':[60,85]}
        self.placement={'scene':str(self.root/'scene.png'),'sceneSize':[100,100],'characterName':'fixture','target':{'placementClass':'standing','standingPose':self.pose,'poseDefinition':{'poseId':'fixture'},'sceneRelations':[{'objectId':'floor','relation':'supported-by','regions':['leftFoot','rightFoot']}],'supportReviewArtifact':self.ref('current.png')}}
        self.review={'schema':'ndc-stage-visual-self-check/v1','stage_id':'fixture','reviewer':'unit-test-not-art-approval','reviewed_at':'fixture','visual_check_status':'PASS','outputs':[self.ref('current.png')],'views':[{'kind':'whole_100','path':str(self.root/'whole.png')},{'kind':'local_200_or_tiles','path':str(self.root/'local.png')}],'criteria':[{'name':n,'applicable':True,'status':'PASS','finding':'synthetic guard fixture only'} for n in F.CRITERIA]}
        self.bind()
    def tearDown(self):self.tmp.cleanup()
    def ref(self,name):
        p=self.root/name;return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    def bind(self):
        self.review.update(poseSha256=F.digest(self.pose),supportSurfaceSha256={'floor':F.digest(self.surface)},reviewedContacts=copy.deepcopy(self.pose))
        self.save_review()
    def save_review(self):
        (self.root/'review.json').write_text(json.dumps(self.review),encoding='utf-8')
        self.placement['target']['supportVisualReview']=self.ref('review.json')
    def run_check(self):
        aff={'schema':'ndc-scene-affordance/v1','sceneSize':[100,100],'zones':[],'placements':[],'supportSurfaces':[self.surface]}
        for name,obj in [('aff.json',aff),('placement.json',self.placement)]: (self.root/name).write_text(json.dumps(obj),encoding='utf-8')
        return S.validate_support_contact(self.root/'aff.json',self.root/'placement.json',self.root/'report.json',self.root/'overlay.png')
    def test_staggered_feet_accepted_without_fabricated_vertical_gap(self):
        r=self.run_check();self.assertEqual(r['status'],'pass');self.assertTrue(all(c['verticalDeltaPx'] is None for c in r['contacts']));self.assertTrue((self.root/'overlay.png').exists())
    def test_outside_floor_rejected_even_with_positive_review(self):
        self.pose['leftFoot']=[5,70];self.bind()
        with self.assertRaisesRegex(ValueError,'outside-floor-region'):self.run_check()
    def test_missing_physical_finding_rejected(self):
        self.review['criteria']=self.review['criteria'][:-1];self.save_review()
        with self.assertRaisesRegex(ValueError,'Physical support'):self.run_check()
    def test_explicit_floating_visual_failure_rejected(self):
        self.review['criteria'][0]['status']='FAIL';self.review['criteria'][0]['finding']='foot visibly floats';self.save_review()
        with self.assertRaisesRegex(ValueError,'Physical support'):self.run_check()
    def test_changed_foot_without_reinspection_rejected(self):
        self.pose['leftFoot']=[31,70]
        with self.assertRaisesRegex(ValueError,'current pose'):self.run_check()
    def test_changed_source_rejected(self):
        (self.root/'scene.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'stale evidence'):self.run_check()
    def test_changed_current_artifact_rejected(self):
        (self.root/'current.png').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'stale evidence'):self.run_check()
    def test_joint_derived_surface_rejected(self):
        self.surface['geometryEvidence']['derivedFromActorJoints']=True;self.bind()
        with self.assertRaisesRegex(ValueError,'not current joints'):self.run_check()
    def test_lying_cannot_use_floor_shortcut(self):
        self.placement['target']['placementClass']='lying';self.placement['target']['lyingPose']=self.pose
        with self.assertRaisesRegex(ValueError,'lying or seat'):self.run_check()
    def test_legacy_fixed_line_still_rejects_floating(self):
        self.surface={'id':'floor','evidence':'fixture fixed edge','occupancy':{'status':'clear','evidence':'fixture'},'contacts':[{'regions':['leftFoot','rightFoot'],'polyline':[[0,85],[100,85]],'tolerancePx':4}]}
        with self.assertRaisesRegex(ValueError,'floating'):self.run_check()
    def test_missing_local_view_rejected(self):
        self.review['views']=self.review['views'][:1];self.save_review()
        with self.assertRaisesRegex(ValueError,'whole/local'):self.run_check()
    def test_degenerate_polygon_rejected(self):
        self.surface['supportPolygon']=[[10,50],[20,50],[30,50]];self.bind()
        with self.assertRaisesRegex(ValueError,'zero area'):self.run_check()

if __name__=='__main__':unittest.main()
