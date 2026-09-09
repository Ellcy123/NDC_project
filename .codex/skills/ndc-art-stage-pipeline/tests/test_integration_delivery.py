"""Actual synthetic pixels verify original-resolution layer/XY reconstruction."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from integration_adapter import verify_delivery
from pipeline import file_hash


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.scene=self.root/'scene.png'; Image.new('RGBA',(12,10),(20,30,40,255)).save(self.scene)
        self.layer=self.root/'actor.png'
        image=Image.new('RGBA',(4,4),(0,0,0,0)); image.paste((150,80,60,255),(1,1,3,4)); image.save(self.layer)
        self.final=self.root/'final.png'; canvas=Image.open(self.scene).convert('RGBA'); canvas.alpha_composite(image,(3,2)); canvas.save(self.final)
        ref=lambda path:{'path':str(path),'sha256':file_hash(path)}
        self.packet={'unit_id':'A','unit_scope':{'cases':[{'case_id':'day','snapshots':[{'snapshot_id':'s0','actor_pose_ids':{'a':'pose'}}]}]},'payload':{'scene_role':'scene'},'files':[{'role':'scene',**ref(self.scene)}]}
        self.manifest={'scene_id':'A','snapshots':[{'case_id':'day','snapshot_id':'s0','layers':[{**ref(self.layer),'x':3,'y':2}],'composite':ref(self.final)}]}
        self.path=self.root/'delivery.json'
        self.delivered={(str(path),file_hash(path)) for path in (self.layer,self.final)}

    def run_check(self):
        self.path.write_text(json.dumps(self.manifest),encoding='utf-8')
        return verify_delivery(self.path,self.packet,self.delivered)

    def test_exact_original_pixel_reconstruction(self):
        self.assertEqual(self.run_check()['snapshots_reconstructed'],1)

    def test_wrong_xy_cannot_pass_delivery(self):
        self.manifest['snapshots'][0]['layers'][0]['x']=4
        with self.assertRaisesRegex(ValueError,'reconstruction differs'):
            self.run_check()

    def test_omitted_snapshot_cannot_pass(self):
        self.manifest['snapshots']=[]
        with self.assertRaisesRegex(ValueError,'every required snapshot'):
            self.run_check()

    def test_report_cannot_substitute_for_layer_files(self):
        self.delivered.remove((str(self.layer),file_hash(self.layer)))
        with self.assertRaisesRegex(ValueError,'Layer missing'):
            self.run_check()


if __name__=='__main__':unittest.main()
