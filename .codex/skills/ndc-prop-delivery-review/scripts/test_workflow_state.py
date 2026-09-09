from pathlib import Path
import copy
import json
import tempfile
import unittest

import workflow_state as w

class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.path = self.root / 'batch.json'
        self.job = 'p|master||closed'
        self.archive = {'schema':'ndc-prop-content/v1', 'items':{
            'p': {'source_references':['canon:p'], 'requirements':{
                'identity':{'level':'A','value':'paper','source':'canon:p'},
                'age':{'level':'A','value':10,'source':'canon:p:age'}}},
            'q': {'source_references':['canon:q'], 'requirements':{
                'identity':{'level':'A','value':'wall stain','source':'canon:q'}}}}}
        w.write_json(self.root / 'content.json', self.archive)
        for iid, item in self.archive['items'].items():
            item['inventory'] = {'keywords':[iid], 'checked_roots':[{'root':'test source','result':'no_match'}],
                                 'found':False,'disposition':'new','reason':'synthetic fixture has no source art'}
        w.write_json(self.root / 'content.json', self.archive)
        self.b = {'schema':w.SCHEMA,'batch_id':'test','objective':'test complete prop delivery',
                  'current_stage':1,'next_action':'create master','requirements_locked':True,
                  'content_archive':'content.json','attempt_log':'attempts.jsonl',
                  'scope':{'item_ids':['p','q'],'scene_ids':['s'],'required_artifacts':['master','scene','big','environment']},
                  'jobs':{self.job:{'item_id':'p','kind':'master','scene_id':'','state':'closed'}},
                  'artifacts':{}}
        for aid, stage, role, parents, item in [
            ('master',2,'semantic_master',[],'p'),('scene',3,'scene_preview',['master'],'p'),
            ('big',2,'ordinary_big',['master'],'p'),('environment',3,'environment_big',[],'q')]:
            output = self.root / (aid + '.png')
            output.write_bytes(('fixture pixels ' + aid).encode())
            whole = self.root / (aid + '_whole.png'); whole.write_bytes(b'whole')
            local = self.root / (aid + '_local.png'); local.write_bytes(b'local')
            a = {'item_ids':[item],'stage':stage,'role':role,'status':'PASS','rejected':False,
                 'parents':parents,'fact_refs':[item+'.'+f for f in self.archive['items'][item]['requirements']],
                 'acceptance_contract':{'content_contract':'all key facts and physical identity'},
                 'path':output.name,'sha256':w.sha(output),'review':aid+'_review.json',
                 'scene_id':'s','frozen':True}
            self.b['artifacts'][aid] = a
            rec = {'schema':'ndc-stage-visual-self-check/v1','stage_id':aid,'role':role,
                   'reviewer':'fixture-only','reviewed_at':'2026-09-08T00:00:00+08:00',
                   'inputs':[], 'outputs':[{'path':output.name,'sha256':w.sha(output)}],
                   'views':[{'kind':'whole_100','path':whole.name},{'kind':'local_200_or_tiles','path':local.name}],
                   'criteria':[{'name':'content_contract','applicable':True,'status':'PASS','finding':'test fixture only'}],
                   'visual_check_status':'PASS', 'rework_stage':None}
            w.write_json(self.root / a['review'], rec)
        for aid in self.b['artifacts']:
            rp = self.root / self.b['artifacts'][aid]['review']
            rec = w.read(rp); rec['workflow_binding'] = w.expected_binding(self.b, self.archive, aid)
            w.write_json(rp, rec)
        w.write_json(self.path, self.b)
        w.initialize(self.path)
        self.b = w.read(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        w.write_json(self.path, self.b)

    def test_valid_batch_and_unchanged_copy_reuses_review(self):
        self.assertEqual(w.validate(self.path, 5), [])
        formal = self.root/'formal'; formal.mkdir()
        a = self.b['artifacts']['big']; target = formal/'big.png'
        target.write_bytes((self.root/a['path']).read_bytes())
        a['published_path'] = str(target); self.save()
        self.assertEqual(w.formal_errors(self.path, formal), [])

    def test_inventory_required_before_generation(self):
        self.archive['items']['p'].pop('inventory'); w.write_json(self.root/'content.json',self.archive)
        self.assertTrue(any('inventory' in e for e in w.validate(self.path,2)))
        prompt=self.root/'prompt.txt'; prompt.write_text('new')
        with self.assertRaisesRegex(ValueError,'prerequisites'):
            w.reserve_attempt(self.path,self.job,prompt,'first')

    def test_hit_stops_later_source_search(self):
        inv=self.archive['items']['p']['inventory']
        inv.update(found=True, disposition='reuse', selected={'path':'test.png','sha256':'x'})
        inv['checked_roots']=[{'root':'first','result':'found'},{'root':'later','result':'found'}]
        w.write_json(self.root/'content.json',self.archive)
        self.assertTrue(any('later root' in e for e in w.validate(self.path,2)))

    def test_rejected_same_hash_never_reuses(self):
        self.b['artifacts']['master']['rejected']=True; self.save()
        errors=w.validate(self.path,5)
        self.assertTrue(any('rejected' in e for e in errors))

    def test_changed_fact_invalidates_only_dependents(self):
        self.archive['items']['p']['requirements']['age']['value']=8
        w.write_json(self.root/'content.json', self.archive)
        self.assertTrue(w.review_errors(self.path,self.b,self.archive,'big'))
        self.assertEqual(w.review_errors(self.path,self.b,self.archive,'environment'),[])

    def test_parent_change_invalidates_child(self):
        (self.root/'master.png').write_bytes(b'new')
        self.assertTrue(any('changed' in e for e in w.review_errors(self.path,self.b,self.archive,'big')))

    def test_changed_requirements_same_bytes_invalidates(self):
        self.b['artifacts']['big']['acceptance_contract']['content_contract']='different approved rule'
        self.save()
        self.assertTrue(w.validate(self.path,5))

    def test_incomplete_batch_blocks_hotspots(self):
        self.b['artifacts']['scene']['status']='PENDING'; self.save()
        self.assertTrue(w.validate(self.path,4))

    def test_unfrozen_scene_blocks_hotspots(self):
        self.b['artifacts']['scene']['frozen']=False; self.save()
        self.assertTrue(any('not frozen' in e for e in w.validate(self.path,4)))

    def test_scope_cannot_shrink(self):
        self.b['scope']['required_artifacts'].remove('environment'); self.save()
        self.assertTrue(any('scope/jobs changed' in e for e in w.validate(self.path,1)))

    def test_six_master_calls_then_stop_even_after_stage_change(self):
        for n in range(1,7):
            prompt=self.root/'prompt.txt'; prompt.write_text('round '+str((n+1)//2))
            self.assertEqual(w.reserve_attempt(self.path,self.job,prompt,'specific revision'),n)
        self.b=w.read(self.path); self.b['current_stage']=5; self.save()
        with self.assertRaisesRegex(ValueError,'exhausted'):
            w.reserve_attempt(self.path,self.job,prompt,'final review retry')

    def test_identical_prompt_rejected_on_new_round(self):
        prompt=self.root/'prompt.txt'; prompt.write_text('same prompt')
        w.reserve_attempt(self.path,self.job,prompt,'first')
        w.reserve_attempt(self.path,self.job,prompt,'second of same pair')
        with self.assertRaisesRegex(ValueError,'revised'):
            w.reserve_attempt(self.path,self.job,prompt,'retry')

    def test_log_truncation_is_detected(self):
        prompt=self.root/'prompt.txt'; prompt.write_text('first')
        w.reserve_attempt(self.path,self.job,prompt,'first')
        log=self.root/'attempts.jsonl'; log.write_text(log.read_text().splitlines()[0]+'\n')
        self.assertTrue(any('head mismatch' in e for e in w.validate(self.path,1)))

    def test_scene_attempt_three_is_total_limit(self):
        new=self.root/'scene_batch.json'; b=copy.deepcopy(self.b)
        key='p|scene|s|closed'; b.pop('attempt_head'); b['attempt_log']='scene_attempts.jsonl'
        b['jobs']={key:{'item_id':'p','kind':'scene','scene_id':'s','state':'closed'}}
        w.write_json(new,b); w.initialize(new)
        for n in range(1,4):
            prompt=self.root/'prompt.txt'; prompt.write_text('specific revision '+str(n))
            self.assertEqual(w.reserve_attempt(new,key,prompt,'specific error '+str(n)),n)
        with self.assertRaisesRegex(ValueError,'exhausted'):
            w.reserve_attempt(new,key,prompt,'new location')

    def test_attempt_retains_exact_prompt_snapshot(self):
        prompt=self.root/'prompt.txt'; prompt.write_text('first prompt')
        w.reserve_attempt(self.path,self.job,prompt,'first')
        prompt.write_text('later changed prompt')
        e=w.log_events(self.path,w.load_batch(self.path))[-1]
        self.assertEqual(Path(e['prompt_path']).read_text(),'first prompt')

    def test_menu_requires_own_scene_preview(self):
        self.b['artifacts']['environment'].update(role='container_type7',scene_id='s')
        self.save()
        self.assertTrue(any('individual scene menu preview' in e for e in w.validate(self.path,4)))

    def test_partial_review_does_not_cover_full_requirement(self):
        rp=self.root/self.b['artifacts']['big']['review']; record=w.read(rp)
        record['criteria'][0]['name']='dimensions_only'; w.write_json(rp,record)
        self.assertTrue(any('missing required' in e for e in w.validate(self.path,5)))

    def test_missing_review_view_is_blocked(self):
        (self.root/'big_local.png').unlink()
        self.assertTrue(w.validate(self.path,5))

    def test_dependency_cycle_is_blocked(self):
        self.b['artifacts']['master']['parents']=['big']; self.save()
        self.assertTrue(any('cycle' in e for e in w.validate(self.path,5)))

    def test_nonapproved_extra_formal_png_is_blocked(self):
        formal=self.root/'formal'; formal.mkdir(); (formal/'unknown.png').write_bytes(b'x')
        self.assertTrue(w.formal_errors(self.path,formal))

    def test_affected_does_not_invalidate_independent_item(self):
        self.assertEqual(w.affected(self.b,['master']),['big','master','scene'])

    def test_missing_A_fact_is_blocked_even_if_binding_rewritten(self):
        a=self.b['artifacts']['master']; a['fact_refs']=['p.identity']; self.save()
        rp=self.root/a['review']; record=w.read(rp)
        record['workflow_binding']=w.expected_binding(self.b,self.archive,'master'); w.write_json(rp,record)
        self.assertTrue(any('omits A' in e for e in w.validate(self.path,5)))

    def test_legacy_budget_import_cannot_be_reset(self):
        new=self.root/'legacy.json'; b=copy.deepcopy(self.b)
        b.pop('attempt_head'); b['attempt_log']='legacy.jsonl'
        b['jobs'][self.job].update(legacy_attempts=6,legacy_evidence='same conversation log reference', legacy_task_id=w.current_task_id())
        w.write_json(new,b); w.initialize(new)
        prompt=self.root/'prompt.txt'; prompt.write_text('new')
        with self.assertRaisesRegex(ValueError,'exhausted'):
            w.reserve_attempt(new,self.job,prompt,'resume')
        b=w.read(new); b['jobs'][self.job]['legacy_attempts']=0; w.write_json(new,b)
        self.assertTrue(w.validate(new,1))

    def derived_batch(self, role='ordinary_big', stage=2):
        path = self.root/'derived.json'
        b = copy.deepcopy(self.b)
        b.pop('attempt_head'); b['attempt_log']='derived.jsonl'
        key='p|derived||presentation'
        b['jobs']={key:{'item_id':'p','kind':'derived','scene_id':'','state':'presentation'}}
        b['artifacts']['big'].update(job_id=key, status='PENDING', role=role, stage=stage)
        w.write_json(path,b); w.initialize(path)
        prompt=self.root/'derived_prompt.txt'; prompt.write_text('complete derived art')
        return path, key, prompt

    def test_stage2_derivative_does_not_require_itself_to_pass(self):
        path,key,prompt=self.derived_batch()
        self.assertEqual(w.reserve_attempt(path,key,prompt,'missing ordinary presentation'),1)

    def test_derived_requires_accepted_parent(self):
        path,key,prompt=self.derived_batch()
        b=w.read(path); b['artifacts']['master']['rejected']=True; w.write_json(path,b)
        with self.assertRaisesRegex(ValueError,'prerequisites'):
            w.reserve_attempt(path,key,prompt,'missing presentation')

    def test_icon_waits_for_stage3_scene_and_big_sources(self):
        path,key,prompt=self.derived_batch('icon',3)
        b=w.read(path); b['artifacts']['scene']['status']='PENDING'; w.write_json(path,b)
        with self.assertRaisesRegex(ValueError,'prerequisites'):
            w.reserve_attempt(path,key,prompt,'missing Icon')
        b['artifacts']['scene']['status']='PASS'; w.write_json(path,b)
        self.assertEqual(w.reserve_attempt(path,key,prompt,'sources now complete'),1)

    def test_icon_cannot_be_scheduled_in_stage2(self):
        path,key,prompt=self.derived_batch('icon',2)
        self.assertTrue(any('Icon producer stage' in e for e in w.validate(path,2)))
        with self.assertRaisesRegex(ValueError,'stage 3'):
            w.reserve_attempt(path,key,prompt,'premature Icon')

    def history_fixture(self):
        path=self.root/'unknown.json'; b=copy.deepcopy(self.b)
        b.pop('attempt_head'); b['attempt_log']='unknown.jsonl'
        b['jobs'][self.job].update(legacy_attempts=6,legacy_task_id=w.current_task_id(),legacy_evidence={
            'status':'UNKNOWN_CONSERVATIVE_EXHAUSTION','actual_count':None})
        w.write_json(path,b); w.initialize(path)
        source=self.root/'prior-task.txt'; source.write_text('Synthetic prior-task count: two.')
        evidence=self.root/'resolution.json'
        w.write_json(evidence,{'schema':'ndc-prop-history-resolution/v1','batch_id':'test',
            'job_id':self.job,'confirmed_count':2,'determination':'known_historical',
            'reviewer':'test fixture','reason':'synthetic recovered count',
            'sources':[{'path':source.name,'sha256':w.sha(source)}]})
        return path,evidence

    def test_unknown_hold_resolution_is_append_only_and_keeps_real_limit(self):
        path,evidence=self.history_fixture()
        original=(self.root/'unknown.jsonl').read_bytes()
        self.assertEqual(w.resolve_history(path,self.job,evidence),2)
        self.assertTrue((self.root/'unknown.jsonl').read_bytes().startswith(original))
        self.assertEqual(w.read(path)['jobs'][self.job]['legacy_attempts'],6)
        for n in range(3,7):
            prompt=self.root/'retry.txt'; prompt.write_text('revised pair '+str((n+1)//2))
            self.assertEqual(w.reserve_attempt(path,self.job,prompt,'specific fix'),n)
        with self.assertRaisesRegex(ValueError,'exhausted'):
            w.reserve_attempt(path,self.job,prompt,'extra')
        self.assertEqual(w.validate(path,2),[])
        with self.assertRaisesRegex(ValueError,'already resolved'):
            w.resolve_history(path,self.job,evidence)

    def test_history_resolution_rejects_missing_or_tampered_source(self):
        path,evidence=self.history_fixture()
        (self.root/'prior-task.txt').write_text('changed')
        with self.assertRaisesRegex(ValueError,'source bytes changed'):
            w.resolve_history(path,self.job,evidence)

    def test_history_resolution_sources_remain_bound_after_append(self):
        path,evidence=self.history_fixture()
        w.resolve_history(path,self.job,evidence)
        (self.root/'prior-task.txt').write_text('changed')
        self.assertTrue(any('source bytes changed' in e for e in w.validate(path,2)))

    def test_known_history_cannot_use_resolution_to_refund_calls(self):
        _,evidence=self.history_fixture()
        with self.assertRaisesRegex(ValueError,'explicit unknown'):
            w.resolve_history(self.path,self.job,evidence)

    def test_progress_excludes_candidates_invalid_reviews_and_extra_sources(self):
        self.b['initial_missing_artifacts']=['big']
        self.b['artifacts']['big']['status']='PENDING'
        self.b['artifacts']['extra']=copy.deepcopy(self.b['artifacts']['environment'])
        self.save()
        before=self.path.read_bytes()
        result=w.progress(self.path)
        self.assertEqual(result['overall'],{'passed':3,'required':4,'percent':75.0})
        self.assertEqual(result['missing_fill'],{'passed':0,'required':1,'percent':0.0})
        self.assertEqual(self.path.read_bytes(),before)
        (self.root/'master.png').write_bytes(b'changed')
        self.assertEqual(w.progress(self.path)['overall']['passed'],1)

if __name__ == '__main__':
    unittest.main()
