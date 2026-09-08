"""Validate trial table integration and preservation of all pre-existing rows."""
from pathlib import Path
import json
import hashlib
import unittest

HERE=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))

class TrialTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=read(HERE/'data/_table_drafts/Unit6/integration_report.json')
        l1_report=HERE/'data/_table_drafts/Unit6/integration_report_l1.json'
        cls.l1=read(l1_report) if l1_report.exists() else None
        cls.tables={k:read(HERE/'data/table'/f'{k}.json') for k in cls.r['addedIds']}
        cls.new={k:[x for x in rows if str(x.get('id',x.get('sceneId'))) in cls.r['addedIds'][k]] for k,rows in cls.tables.items()}
        cls.talk={x['id']:x for x in cls.new['Talk']}

    def test_preserved_rows_and_unique_ids(self):
        for name,rows in self.tables.items():
            keys=[str(x.get('id',x.get('sceneId'))) for x in rows]
            self.assertEqual(len(keys),len(set(keys)),name)
            added=set(self.r['addedIds'][name])
            if self.l1:added.update(self.l1['addedIds'].get(name,[]))
            old=[x for x in rows if str(x.get('id',x.get('sceneId'))) not in added]
            digest=hashlib.sha256(json.dumps(old,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
            self.assertEqual(digest,self.r['preservedRowsSha256'][name],name)

    def test_talk_graph_and_menus(self):
        for row in self.talk.values():
            self.assertEqual(row['videoEpisode'],'EPI06')
            self.assertEqual(row['videoLoop'],'loop2')
            if row.get('next'): self.assertIn(row['next'],self.talk)
            if row['script']=='1':
                self.assertLessEqual(len(row['Parameters']),4)
                for p in row['Parameters']: self.assertIn(p['ParameterInt'],self.talk)
        menus=[self.talk[x] for x in self.r['menus'].values()]
        self.assertEqual(sum(len(t['Parameters'])-1 for t in menus),13)
        self.assertEqual(sum(bool(t['Words'][0]) for t in self.talk.values()),239)
        for scene in self.new['SceneConfig']:
            for ref in scene['previewTalks']+[r[k] for r in scene['NPCInfos'] for k in ('TalkInfo','LoopTalkInfo')]:
                self.assertEqual(self.talk[ref['id']]['videoScene'],ref['videoScene'])

    def test_evidence_prerequisites_and_analysis(self):
        chapter=self.new['ChapterConfig'][0]
        self.assertEqual(chapter['exposes'],self.new['ExposeData'])
        self.assertEqual(chapter['doubts'],self.new['DoubtConfig'])
        conditions={(x['type'],x['param']) for d in chapter['doubts'] for x in d['condition']}
        for e in chapter['exposes']:
            self.assertIn(e['talkId'],self.talk)
            for item in e['item']: self.assertIn(('1',item),conditions)
        ids=self.r['items']; self.assertEqual([e['item'] for e in chapter['exposes']],[[ids['private_ledger'],ids['public_ledger']],[ids['demand_letter']]])
        self.assertIn(('4',ids['signature_statement']),conditions)
        self.assertIn(('4',ids['accounts_claim']),conditions)
        items={r['id']:r for r in self.new['ItemStaticData']}
        self.assertEqual(items[ids['photo_raw']]['analysedEvidence'],ids['photo_amounts'])
        self.assertEqual(items[ids['photo_amounts']]['beforeAnalysedEvidence'],ids['photo_raw'])
        grants=[t['Parameters'][0]['ParameterInt'] for t in self.talk.values() if t['script']=='3']
        self.assertEqual(set(grants),set(ids.values()))

    def test_flow_and_canon(self):
        m=read(HERE.parent/'canon_manifest.json')
        self.assertNotIn('Unit6',m['policy']['canonicalUnits'])
        self.assertEqual(next(x for x in m['chapters'] if x['canonicalUnit']=='Unit1')['unityEpisode'],'EPI01')
        flow=read(HERE/'data/formal/unit_flow.json')['units']['Unit6']
        self.assertEqual([x['id'] for x in flow['loops']],['loop1','loop2'] if self.l1 else ['loop2'])
        self.assertEqual(flow['chapter'],'EPI06')

if __name__=='__main__': unittest.main()
