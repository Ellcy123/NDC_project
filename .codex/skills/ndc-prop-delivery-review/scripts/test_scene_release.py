"""Behavioral fixtures for scene gates; fixture PASS is never production approval."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import workflow_state as w
import scene_release as s
import test_workflow_state as legacy


class SceneReleaseTests(unittest.TestCase):
    def setUp(self):
        fixture = legacy.WorkflowTests()
        fixture.setUp()
        self.addCleanup(fixture.tearDown)
        self.root, self.archive = fixture.root, fixture.archive
        self.path = self.root / 'scoped.json'
        self.b = copy.deepcopy(fixture.b)
        self.b.pop('attempt_head')
        self.b['attempt_log'] = 'scoped-attempts.jsonl'
        self.b['scope']['scene_ids'] = ['s', 't']
        self.scene_job = 'p|scene|s|closed'
        self.master_job = 'p|master||closed'
        self.b['jobs'][self.scene_job] = {'item_id':'p','kind':'scene','scene_id':'s','state':'closed'}
        self.b['artifacts']['master']['job_id'] = self.master_job
        self.b['artifacts']['master']['scene_id'] = ''  # Shared masters are not scene-tagged.
        self.b['artifacts']['scene'].update(job_id=self.scene_job, status='PENDING', frozen=False)
        self.menu_job = 'p|menu|s|open'
        self.b['jobs'][self.menu_job] = {'item_id':'p','kind':'menu','scene_id':'s','state':'open'}
        self.b['artifacts']['p_menu'] = dict(item_ids=['p'], stage=3, role='container_type7', scene_id='s',
                                           status='PENDING', rejected=False, parents=['scene','master'],
                                           fact_refs=['p.identity'], job_id=self.menu_job,
                                           acceptance_contract={'content_contract':'fixture container content'})
        self.b['artifacts']['p_menu_preview'] = dict(item_ids=['p'], stage=3, role='scene_menu_preview', scene_id='s',
                                                   status='PENDING', rejected=False, parents=['scene','p_menu'],
                                                   fact_refs=['p.identity'],
                                                   acceptance_contract={'content_contract':'fixture menu preview'})
        self.b['scope']['required_artifacts'] += ['p_menu','p_menu_preview']
        self.b['artifacts']['environment'].update(scene_id='t', status='PENDING', parents=['q_scene'])
        self.icon_job = 'p|derived||icon'
        self.b['jobs'][self.icon_job] = {'item_id':'p','kind':'derived','scene_id':'','state':'icon'}
        self.b['artifacts']['p_icon'] = dict(item_ids=['p'], stage=3, role='icon', status='PENDING',
                                           rejected=False, parents=['big'], fact_refs=['p.identity'],
                                           job_id=self.icon_job,
                                           acceptance_contract={'content_contract':'fixture icon identity'})
        self.b['scope']['required_artifacts'].append('p_icon')
        for aid, stage, role, parents in [('q_master',2,'semantic_master',[]), ('q_scene',3,'scene_preview',['q_master'])]:
            a = copy.deepcopy(self.b['artifacts']['master'])
            a.update(item_ids=['q'],stage=stage,role=role,status='PENDING',rejected=False,parents=parents,
                     fact_refs=['q.identity'],scene_id='' if stage==2 else 't',path=aid+'.png',review=aid+'_review.json')
            a.pop('job_id',None)
            (self.root/a['path']).write_bytes(('fixture '+aid).encode())
            a['sha256']=w.sha(self.root/a['path'])
            self.b['artifacts'][aid]=a
            self.b['scope']['required_artifacts'].append(aid)
            rec=copy.deepcopy(w.read(self.root/'master_review.json'))
            rec.update(stage_id=aid,role=role,outputs=[{'path':a['path'],'sha256':a['sha256']}])
            rec['workflow_binding']=w.expected_binding(self.b,self.archive,aid)
            w.write_json(self.root/a['review'],rec)
        w.write_json(self.path,self.b)
        w.initialize(self.path)
        self.b=w.read(self.path)
        self.index={'schema':s.SCHEMA,'batch_id':self.b['batch_id'],'scope_sha256':w.digest(self.b['scope']),
                    'reviewer':'fixture-only','reason':'synthetic complete association audit',
                    'items':{},'scenes':{},'relations':[]}
        for iid in ['p','q']:
            source=self.root/(iid+'_source.txt'); source.write_text('fixture content '+iid)
            self.index['items'][iid]={'status':'resolved','open_questions':[],
                                      'sources':[{'path':str(source),'sha256':w.sha(source)}]}
        self.index['scenes']={'s':{'item_ids':['p'],'artifact_ids':['scene','p_menu','p_menu_preview'],'sources':copy.deepcopy(self.index['items']['p']['sources'])},
                              't':{'item_ids':['q'],'artifact_ids':['q_scene','environment'],'sources':copy.deepcopy(self.index['items']['q']['sources'])}}
        self.index_path=self.root/'index.json'
        self.prompt=self.root/'prompt.txt'; self.prompt.write_text('fixture actual scene prompt 1')

    def install(self,revise=False):
        w.write_json(self.index_path,self.index)
        w.install_scene_index(self.path,self.index_path,'fixture migration/revision evidence',revise)
        self.b=w.read(self.path)

    def set_pass(self,aid):
        self.b=w.read(self.path)
        a=self.b['artifacts'][aid]; a.update(status='PASS',rejected=False,frozen=True)
        rec=w.read(self.root/a['review'])
        rec['workflow_binding']=w.expected_binding(self.b,self.archive,aid)
        w.write_json(self.root/a['review'],rec)
        w.write_json(self.path,self.b)

    def relation(self,kind='shared_identity',status='resolved',artifact_ids=None):
        self.index['relations']=[{'id':'p-q','kind':kind,'status':status,'item_ids':['p','q'],
                                 'artifact_ids':artifact_ids or [],'fact_refs':['q.identity'],
                                 'consumer_scene_ids':['s'] if artifact_ids else [],
                                 'sources':copy.deepcopy(self.index['items']['q']['sources']),
                                 'reason':'fixture relationship from supplied source'}]

    def test_legacy_batch_without_index_keeps_global_gate(self):
        self.assertTrue(w.validate(self.path,3,scene_id='s'))
        with self.assertRaisesRegex(ValueError,'prerequisites'):
            w.reserve_attempt(self.path,self.scene_job,self.prompt,'fixture first call')

    def test_ready_scene_proceeds_despite_unrelated_failed_master(self):
        self.install()
        self.assertEqual(w.validate(self.path,3,scene_id='s'),[])
        self.assertTrue(w.validate(self.path,3))
        self.assertEqual(w.reserve_attempt(self.path,self.scene_job,self.prompt,'fixture first call'),1)
        result=w.progress(self.path)
        self.assertEqual(result['overall']['required'],len(self.b['scope']['required_artifacts']))
        self.assertEqual(result['scenes']['s']['stage'],3)
        self.assertEqual(result['scenes']['t']['stage'],2)
        self.assertEqual(result['current_stage'],2)

    def test_stage_scalar_cannot_bypass_the_scene_gate(self):
        self.relation(); self.install()
        self.b['current_stage']=5; w.write_json(self.path,self.b)
        with self.assertRaisesRegex(ValueError,'prerequisites'):
            w.reserve_attempt(self.path,self.scene_job,self.prompt,'cannot force final stage')

    def test_shared_master_without_scene_id_is_still_checked(self):
        self.install()
        self.b['artifacts']['master']['rejected']=True; w.write_json(self.path,self.b)
        self.assertTrue(w.validate(self.path,3,scene_id='s'))

    def test_all_related_state_masters_required_but_other_scene_placement_not_required(self):
        self.relation('state_variant'); self.install()
        self.assertTrue(w.validate(self.path,3,scene_id='s'))
        self.set_pass('q_master')
        self.assertEqual(w.validate(self.path,3,scene_id='s'),[])
        self.assertEqual(w.read(self.path)['artifacts']['q_scene']['status'],'PENDING')

    def test_unknown_external_association_blocks(self):
        self.relation(status='unresolved'); self.install()
        self.assertTrue(any('unresolved' in e for e in w.validate(self.path,3,scene_id='s')))

    def test_unresolved_member_cannot_hide_behind_resolved_edge(self):
        self.relation('container_content')
        self.index['items']['q'].update(status='unresolved',open_questions=['unknown contents count'])
        self.install()
        self.assertTrue(any('unknown contents count' in e for e in w.validate(self.path,3,scene_id='s')))

    def test_container_future_local_menu_is_not_its_own_prerequisite(self):
        # The scene producer may depend on source masters, and other local
        # stage-3 producers may depend on this scene; no stage-3 output is ready.
        self.install()
        closure=s.closure(self.b,self.archive,s.active_index(self.b),'s')
        self.assertNotIn('scene',closure['prerequisite_artifacts'])
        self.assertNotIn('p_menu',closure['prerequisite_artifacts'])
        self.assertNotIn('p_menu_preview',closure['prerequisite_artifacts'])
        self.assertEqual(set(closure['prerequisite_artifacts']),{'master','big'})
        self.assertEqual(w.validate(self.path,3,scene_id='s'),[])
        with self.assertRaisesRegex(ValueError,'prerequisites'):
            w.reserve_attempt(self.path,self.menu_job,self.prompt,'actual menu still requires its scene')

    def test_depicted_external_content_is_real_prerequisite(self):
        self.relation('depicted_content',artifact_ids=['q_scene']); self.install()
        self.set_pass('q_master')
        self.assertTrue(w.validate(self.path,3,scene_id='s'))
        self.set_pass('q_scene')
        self.assertEqual(w.validate(self.path,3,scene_id='s'),[])

    def test_changed_related_fact_invalidates_existing_scene_without_image_parent_edge(self):
        self.relation('fact_reference'); self.install(); self.set_pass('q_master'); self.set_pass('scene')
        b=w.read(self.path)
        self.assertEqual(w.review_errors(self.path,b,self.archive,'scene'),[])
        self.archive['items']['q']['requirements']['identity']['value']='different related photograph subject'
        w.write_json(self.root/'content.json',self.archive)
        self.assertTrue(w.review_errors(self.path,b,self.archive,'scene'))
        self.assertFalse(w.scene_readiness(self.path,'s')['ready'])

    def test_changed_parent_bytes_revoke_gate_and_existing_scene(self):
        self.install(); self.set_pass('scene')
        (self.root/'master.png').write_bytes(b'changed master pixels')
        b=w.read(self.path)
        self.assertFalse(w.scene_readiness(self.path,'s')['ready'])
        self.assertTrue(w.review_errors(self.path,b,self.archive,'scene'))

    def test_affected_includes_associated_scene_without_direct_image_parent(self):
        self.relation('shared_identity'); self.install()
        affected=w.affected(w.read(self.path),['q_master'])
        self.assertIn('scene',affected)
        self.assertIn('q_scene',affected)
        self.assertIn('environment',affected)
        self.assertNotIn('master',affected)

    def test_unrelated_scene_does_not_get_revoked_by_affected(self):
        self.install()
        self.assertNotIn('scene',w.affected(w.read(self.path),['q_master']))

    def test_locked_date_reference_does_not_wait_for_unrelated_document_master(self):
        self.archive['items']['q']['requirements']['date']={'level':'A','value':'1928-05-03','source':'canon:q:date'}
        w.write_json(self.root/'content.json',self.archive)
        self.relation('fact_reference')
        self.index['relations'][0]['fact_refs']=['q.date']
        self.index['relations'][0]['consumer_scene_ids']=['s']
        self.b['artifacts']['scene']['fact_refs'].append('q.date')
        w.write_json(self.path,self.b)
        self.install()
        result=w.scene_readiness(self.path,'s')
        self.assertTrue(result['ready'])
        self.assertNotIn('q_master',result['prerequisite_artifacts'])
        self.assertNotIn('q',result['production_item_ids'])
        self.assertIn('q.date',result['context_fact_refs'])
        self.assertNotIn('q.identity',result['context_fact_refs'])
        self.assertEqual(w.reserve_attempt(self.path,self.scene_job,self.prompt,'reference facts already locked'),1)

    def test_depicted_approved_identity_needs_its_source_not_a_new_master(self):
        self.relation('depicted_content'); self.install()
        self.assertTrue(w.scene_readiness(self.path,'s')['ready'])
        self.assertEqual(w.read(self.path)['artifacts']['q_master']['status'],'PENDING')
        (self.root/'q_source.txt').write_text('identity source changed')
        self.assertFalse(w.scene_readiness(self.path,'s')['ready'])

    def test_unconfirmed_referenced_fact_blocks_even_without_image_prerequisite(self):
        self.relation('fact_reference',status='unresolved'); self.install()
        self.assertFalse(w.scene_readiness(self.path,'s')['ready'])

    def test_unreferenced_fact_and_master_change_do_not_revoke_semantic_consumer(self):
        self.archive['items']['q']['requirements']['date']={'level':'A','value':'1928-05-03','source':'canon:q:date'}
        w.write_json(self.root/'content.json',self.archive)
        self.relation('fact_reference'); self.index['relations'][0]['fact_refs']=['q.date']; self.install(); self.set_pass('scene')
        self.archive['items']['q']['requirements']['identity']['value']='unrelated document appearance change'
        w.write_json(self.root/'content.json',self.archive)
        (self.root/'q_master.png').write_bytes(b'unrelated master changed')
        self.assertEqual(w.review_errors(self.path,w.read(self.path),self.archive,'scene'),[])
        self.assertNotIn('scene',w.affected(w.read(self.path),['q_master']))

    def test_semantic_relation_cannot_omit_both_facts_and_artifacts(self):
        self.relation('fact_reference'); self.index['relations'][0]['fact_refs']=[]
        with self.assertRaisesRegex(ValueError,'actual facts or image prerequisites'):
            self.install()

    def test_migration_and_revision_preserve_real_attempt_count(self):
        # A master attempt is permitted in stage2 before any scene index exists.
        self.b['artifacts']['master']['status']='PENDING'; w.write_json(self.path,self.b)
        self.assertEqual(w.reserve_attempt(self.path,self.master_job,self.prompt,'master fixture 1'),1)
        self.install()
        self.index['reason']='new documented association review'; self.install(revise=True)
        b=w.read(self.path); events=w.log_events(self.path,b)
        self.assertEqual(w.effective_count(b,events,self.master_job),1)
        self.assertEqual(w.reserve_attempt(self.path,self.master_job,self.prompt,'same-pair fixture 2'),2)
        with self.assertRaisesRegex(ValueError,'already initialized'):
            w.initialize(self.path)

    def test_scene_cannot_reset_three_calls_via_index_revision_or_current_stage(self):
        self.install()
        for n in range(1,4):
            self.prompt.write_text('actual revised prompt '+str(n))
            self.assertEqual(w.reserve_attempt(self.path,self.scene_job,self.prompt,'fixture change '+str(n)),n)
        self.index['reason']='review without extra budget'; self.install(revise=True)
        with self.assertRaisesRegex(ValueError,'exhausted'):
            w.reserve_attempt(self.path,self.scene_job,self.prompt,'fourth call')

    def test_scope_shrink_and_index_pointer_removal_are_rejected(self):
        self.install(); b=w.read(self.path)
        b.pop('scene_release_index'); w.write_json(self.path,b)
        self.assertTrue(any('pointer' in e for e in w.validate(self.path,1)))
        w.write_json(self.path,self.b)
        self.b['scope']['required_artifacts'].remove('q_master'); w.write_json(self.path,self.b)
        self.assertTrue(any('scope/jobs changed' in e for e in w.validate(self.path,1)))

    def test_unrelated_source_file_failure_does_not_block_ready_scene(self):
        self.install()
        (self.root/'q_source.txt').write_text('changed unrelated source')
        self.assertEqual(w.validate(self.path,3,scene_id='s'),[])
        self.assertTrue(w.validate(self.path,3,scene_id='t'))

    def test_stage4_and_icon_global_barriers_remain(self):
        self.install(); self.set_pass('scene')
        self.assertTrue(w.validate(self.path,4))
        self.assertTrue(w.validate(self.path,4,scene_id='s'))
        self.assertEqual(w.validate(self.path,3,scene_id='s'),[])
        with self.assertRaisesRegex(ValueError,'prerequisites'):
            w.reserve_attempt(self.path,self.icon_job,self.prompt,'cannot start Icon before other scenes')

    def test_index_cannot_omit_an_actual_scene_producer(self):
        self.index['scenes']['s']['artifact_ids']=[]
        with self.assertRaisesRegex(ValueError,'omits|assign'):
            self.install()

    def test_tampered_index_snapshot_never_falls_back_to_legacy(self):
        self.install()
        Path(self.b['scene_release_index']['path']).write_text('{}')
        self.assertTrue(any('snapshot' in e for e in w.validate(self.path,3,scene_id='s')))

    def test_actual_cli_migration_readiness_attempt_and_progress(self):
        w.write_json(self.index_path,self.index)
        script=Path(w.__file__).resolve()
        def run(command,*args):
            result=subprocess.run([sys.executable,str(script),command,'--batch',str(self.path),*args],
                                  capture_output=True,text=True,encoding='utf-8',check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            return json.loads(result.stdout)
        migration=run('migrate-scene-release','--index',str(self.index_path),'--reason','actual fixture CLI migration')
        self.assertEqual(migration['counts_preserved'][self.scene_job],0)
        self.assertTrue(run('scene-readiness','--scene','s')['ready'])
        self.assertEqual(run('attempt','--job',self.scene_job,'--prompt',str(self.prompt),
                             '--reason','actual fixture CLI first call')['reserved_attempt'],1)
        self.assertEqual(run('progress')['stage_dispatch'],'per_scene')


if __name__=='__main__':
    unittest.main()
