"""Importance-tier review view tests; synthetic files do not grant visual approval."""
import copy
from pathlib import Path
import tempfile
import unittest

import stage_visual_check as s
import workflow_state as w


class ImportanceViewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.output=self.root/'output.png'; self.output.write_bytes(b'synthetic')
        self.runtime=self.root/'runtime.png'; self.runtime.write_bytes(b'runtime')
        self.whole=self.root/'whole.png'; self.whole.write_bytes(b'whole')
        self.base={'schema':s.SCHEMA,'stage_id':'x','role':'ordinary_big','reviewer':'fixture',
                   'reviewed_at':'2026-09-10T00:00:00+08:00','inputs':[],
                   'outputs':[{'path':str(self.output),'sha256':s.sha256(self.output)}],
                   'criteria':[{'name':'content','applicable':True,'status':'PASS','finding':'synthetic'}],
                   'visual_check_status':'PASS','rework_stage':None}

    def check(self,data):
        path=self.root/'review.json'; w.write_json(path,data); return s.validate_record(path,[])

    def test_h2_does_not_require_local_200(self):
        data=copy.deepcopy(self.base); data.update(importance_tier='H2',tolerance_ratio=0.2,
            views=[{'kind':'whole_runtime','path':str(self.runtime)},{'kind':'whole_100','path':str(self.whole)}])
        self.assertEqual(self.check(data),[])

    def test_h3_needs_basis_but_only_runtime_view(self):
        data=copy.deepcopy(self.base); data.update(importance_tier='H3',tolerance_ratio=0.3,
            low_salience_basis='tiny non-semantic runtime region',views=[{'kind':'whole_runtime','path':str(self.runtime)}])
        self.assertEqual(self.check(data),[])
        data.pop('low_salience_basis')
        self.assertTrue(any('low_salience_basis' in e for e in self.check(data)))

    def test_h1_can_require_local_view(self):
        data=copy.deepcopy(self.base); data.update(importance_tier='H1',tolerance_ratio=0.1,local_200_required=True,
            views=[{'kind':'whole_runtime','path':str(self.runtime)},{'kind':'whole_100','path':str(self.whole)}])
        self.assertTrue(any('local_200' in e for e in self.check(data)))


if __name__=='__main__':
    unittest.main()
