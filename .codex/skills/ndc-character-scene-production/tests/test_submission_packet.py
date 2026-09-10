import base64
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_chatgpt_web_submission_packet import build

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class SubmissionPacketTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.prompt = self.root / "prompt.txt"; self.prompt.write_text("complete prompt")
        self.profile = self.root / "importance.json"; self.profile.write_text("{}")
        self.binding = self.root / "binding.json"
        self.binding.write_text(json.dumps({"status":"PASS","checks":{"rendered_prompt_sha256":digest(self.prompt)}}))
        self.importance = self.root / "importance-gate.json"
        self.importance.write_text(json.dumps({"status":"PASS","profile_sha256":digest(self.profile)}))
        inputs=[]
        for n, role in enumerate(("local-whitebox-crop","untouched-full-scene","approved-character-card"),1):
            path=self.root/f"input-{n}.png"; path.write_bytes(PNG)
            inputs.append({"role":role,"path":str(path.resolve()),"sha256":digest(path)})
        self.contract={"schema":"ndc-chatgpt-web-submission-source/v1","scene_id":"s","revision":1,"pose_ids":["a"],
            "conversation_url":"https://chatgpt.com/c/scene-s-r1","uploaded_inputs":inputs,
            "prompt":{"path":str(self.prompt.resolve()),"sha256":digest(self.prompt)},
            "prompt_binding_gate":{"path":str(self.binding.resolve()),"sha256":digest(self.binding)},
            "importance_profile":{"path":str(self.profile.resolve()),"sha256":digest(self.profile)},
            "importance_gate":{"path":str(self.importance.resolve()),"sha256":digest(self.importance)}}
        self.contract_path=self.root/"contract.json"; self.contract_path.write_text(json.dumps(self.contract))

    def test_builds_fixed_order_immutable_packet(self):
        result=build(self.contract_path,self.root/"packet")
        manifest=json.loads(Path(result["manifest"]).read_text())
        self.assertEqual(manifest["submission_order"], ["local-whitebox-crop","untouched-full-scene","approved-character-card","full-prompt"])
        self.assertEqual(len(manifest["uploaded_inputs"]),3)
        self.assertTrue(Path(result["receipt_draft"]).is_file())

    def test_stale_gate_or_nonempty_destination_fails(self):
        self.prompt.write_text("changed")
        with self.assertRaisesRegex(ValueError,"hash"):
            build(self.contract_path,self.root/"packet")
        self.contract["prompt"]["sha256"]=digest(self.prompt)
        self.contract_path.write_text(json.dumps(self.contract))
        with self.assertRaisesRegex(ValueError,"binding"):
            build(self.contract_path,self.root/"packet2")


if __name__ == "__main__":
    unittest.main()
