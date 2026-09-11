"""Adapter wiring and rejection tests; fixtures do not prove visual approval."""
import copy
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import pipeline as p
import integration_adapter as adapter
from dispatch_plan import build_dispatch_plan
from reference_task_plan import build_reference_task_plan, reserve_reference, bind_reference

PROJECT = Path(__file__).resolve().parents[4]
SKILLS_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_STATE = SKILLS_ROOT / 'ndc-generate-characters/scripts/art_workflow_state.py'


class NativeContractStub:
    """Deliberately not a visual/production validator; positive wiring only."""
    @staticmethod
    def resolve_path(raw, base):
        path = Path(raw)
        return path.resolve() if path.is_absolute() else (Path(base).parent / path).resolve()
    @classmethod
    def validate_file_ref(cls, ref, label, base):
        path = cls.resolve_path(ref['path'], base)
        p.need(p.file_hash(path) == ref['sha256'], 'stale native ref')
        return path, p.read(path)
    @staticmethod
    def validate_ledger(path):
        return {'status':'EVIDENCE_GATE_PASS', 'fixture_stub':True}


class IntegrationAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.refs = []
        self.scope = {'cases':[{'case_id':'A-day','snapshots':[{'snapshot_id':'s0','actor_pose_ids':{'nurse':'nurse-pose','patient':'patient-pose'}}]}]}
        self.add('scene', {'explicit_synthetic_source':True})
        self.add('scope', {'scene_id':'A','scope':self.scope,'status':'LOCKED','requirement_basis':'Synthetic contract fixture only','validation_only':True})
        self.add('depth', {'explicit_synthetic_reference':True})
        self.add('identity', {'explicit_synthetic_reference':True})
        staging = self.add('staging', {'timelineSnapshotId':'s0','combinedWhiteboxReview':{'poseIds':{'nurse':'nurse-pose','patient':'patient-pose'}}})
        scene = next(r for r in self.refs if r['role']=='scene')
        self.add('pre', {'schema':'ndc-scene-integration-production-ledger/v2','stage':'pre-generation','processRoot':str(self.root),'cases':[{'caseId':'A-day','sourceScene':scene['path'],'sourceSceneSha256':scene['sha256'],'stagingContracts':[staging]}]})
        self.add('prompts', {'scene_id':'A','poses':{pose:{'prompt':'Synthetic contract only','reference_roles':['scene','identity','depth'],'checked_by':'test fixture','findings':'Not an art review'} for pose in ('nurse-pose','patient-pose')}})
        self.add('authorization', {'allowed':False,'source_kind':'user_instruction','scene_ids':['A'],'scope':'character_scene_production','instruction':'Fixture only, no real generation'})
        self.add('history', {'production_id':'original-production','basis':'Synthetic imported counts','source_roles':['scene'],'jobs':{'actor-job':{'model':2,'ps':1}}})
        history = next(r for r in self.refs if r['role']=='history')
        plan = {'schema':'ndc-art-production-plan/v1','task_id':'upstream','production_id':'original-production','jobs':[{'job_id':'actor-job','asset_key':'A|formal','requirements':{'scene_id':'A','production_id':'original-production','phase':'formal','pose_ids':['nurse-pose','patient-pose']},'source_decision':{'mode':'derive','evidence':'Explicit fixture history'},'required_criteria':['native-post-generation'],'output_roles':['final-composite'],'limits':{'model':6,'ps':3},'history':{'model':2,'ps':1},'history_evidence':[history]}]}
        (self.root/'plan.json').write_text(json.dumps(plan), encoding='utf-8')
        api = runpy.run_path(str(WORKFLOW_STATE))
        api['initialize'](self.root/'plan.json', self.root/'journal.jsonl')
        self.packet = {'schema':p.SCHEMA,'pipeline_kind':'character_scene','project_root':str(PROJECT),'execution_mode':'validation','unit_id':'A','revision':1,'model_policy':p.INTEGRATION_MODELS,'producer_task_id':'upstream','unit_scope':self.scope,'authority':{'journal':str(self.root/'journal.jsonl'),'upstream_jobs':[],'downstream_jobs':['actor-job']},'files':self.refs,'payload':{'production_id':'original-production','scene_role':'scene','scope_role':'scope','pre_ledger_role':'pre','depth_roles':['depth'],'identity_roles':['identity'],'prompt_bundle_role':'prompts','history_role':'history','budget_jobs':{'actor-job':['nurse-pose','patient-pose']},'authorization_role':'authorization'}}
        self.stub = patch.object(adapter, 'native_gate', return_value=NativeContractStub)
        self.stub.start(); self.addCleanup(self.stub.stop)

    def add(self, role, data):
        path = self.root/(role+'.json')
        path.write_text(json.dumps(data), encoding='utf-8')
        ref = {'role':role,'path':str(path),'sha256':p.file_hash(path)}
        self.refs.append(ref)
        return ref

    def edit(self, role, fn):
        ref = next(r for r in self.refs if r['role']==role)
        data = p.read(ref['path']); fn(data)
        Path(ref['path']).write_text(json.dumps(data), encoding='utf-8')
        ref['sha256'] = p.file_hash(ref['path'])

    def test_whole_scene_wiring_keeps_original_imported_counts(self):
        before = Path(self.packet['authority']['journal']).read_bytes()
        result = adapter.validate_release(self.packet, self.root)
        self.assertEqual(result['budgets']['actor-job'], {'model_used':0,'ps_used':0,'unknown':[]})
        self.assertTrue(result['validation_only']); self.assertFalse(result['can_execute'])
        self.assertEqual(Path(self.packet['authority']['journal']).read_bytes(), before)
        self.assertEqual(result['importance_mode'], 'legacy_conservative_h0_h1')

    def test_new_scope_requires_current_tiered_importance_profile(self):
        gate = adapter.importance_gate()
        profile = {'schema':'ndc-visual-importance/v1','domain':'character_scene','scene_id':'A','revision':1,
                   'classification_basis':['Synthetic runtime composition'],
                   'hard_gates':{name:{'applicable':True,'reason':'Synthetic required contract'} for name in gate.HARD_GATES},
                   'regions':[{'id':'actor','owner':'actor:nurse','tier':'H1','tolerance_ratio':0.1,
                               'criteria':['identity silhouette'],'views':['whole_runtime','whole_100'],
                               'reason':'Synthetic narrative focus','dependsOn':[]}]}
        profile_ref=self.add('importance_profile',profile)
        gate_ref=self.add('importance_gate',{'status':'PASS','profile_sha256':profile_ref['sha256']})
        self.edit('scope',lambda d:d.update(importance_policy_version='ndc-visual-importance/v1'))
        self.packet['payload'].update(importance_profile_role='importance_profile',importance_gate_role='importance_gate')
        result=adapter.validate_release(self.packet,self.root)
        self.assertEqual(result['importance_mode'],'tiered_h0_h1_h2_h3')
        Path(gate_ref['path']).write_text(json.dumps({'status':'PASS','profile_sha256':'0'*64}))
        gate_ref['sha256']=p.file_hash(gate_ref['path'])
        with self.assertRaisesRegex(ValueError,'stale'):
            adapter.validate_release(self.packet,self.root)

    def test_native_gate_is_actually_called_and_weak_fixture_cannot_pass_it(self):
        self.stub.stop()
        with self.assertRaises(ValueError):
            adapter.validate_release(self.packet, self.root)

    def test_omitted_cast_is_not_a_ready_whole_scene(self):
        self.edit('staging', lambda d:d['combinedWhiteboxReview']['poseIds'].pop('patient'))
        staging = next(r for r in self.refs if r['role']=='staging')
        self.edit('pre', lambda d:d['cases'][0].update(stagingContracts=[staging]))
        with self.assertRaisesRegex(ValueError, 'Complete cast'):
            adapter.validate_release(self.packet, self.root)

    def test_omitted_case_is_rejected(self):
        self.edit('pre', lambda d:d.update(cases=[]))
        with self.assertRaisesRegex(ValueError, 'whole-scene cases'):
            adapter.validate_release(self.packet, self.root)

    def test_no_authorization_cannot_become_production_ready(self):
        self.packet['execution_mode']='production'
        self.assertFalse(adapter.validate_release(self.packet,self.root)['can_execute'])

    def test_existing_finite_exception_keeps_scope_and_effective_cap(self):
        grant={'source_kind':'user_instruction','instruction':'Synthetic explicit extra allowance','grant_id':'one-time-grant','source_roles':['scene'],'production_id':'original-production','scene_id':'A','job_id':'actor-job','phase':'formal','base_limits':{'model':6,'ps':3},'additional_limits':{'model':2,'ps':1}}
        self.add('extra', grant)
        self.packet['payload']['budget_exception_roles']={'actor-job':'extra'}
        refs={r['role']:r for r in self.refs}
        adapter.validate_job_limits({'limits':{'model':8,'ps':4}},'actor-job',self.packet,refs)
        with self.assertRaisesRegex(ValueError,'Effective cap'):
            adapter.validate_job_limits({'limits':{'model':10,'ps':5}},'actor-job',self.packet,refs)
        with self.assertRaisesRegex(ValueError,'another production'):
            self.edit('extra',lambda d:d.update(scene_id='B'))
            adapter.validate_job_limits({'limits':{'model':8,'ps':4}},'actor-job',self.packet,refs)

    def test_unbacked_increase_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'original scoped user exception'):
            adapter.validate_job_limits({'limits':{'model':8,'ps':4}},'actor-job',self.packet,{r['role']:r for r in self.refs})

    def test_history_cannot_be_zeroed_at_handoff(self):
        self.edit('history', lambda d:d['jobs'].update({'actor-job':{'model':0,'ps':0}}))
        with self.assertRaisesRegex(ValueError, 'Imported history'):
            adapter.validate_release(self.packet, self.root)

    def test_scope_cannot_be_silently_changed(self):
        self.packet['unit_scope'] = {'cases':[{'case_id':'A-day','snapshots':[{'snapshot_id':'s0','actor_pose_ids':{'nurse':'nurse-pose'}}]}]}
        with self.assertRaisesRegex(ValueError, 'Original requirement scope'):
            adapter.validate_release(self.packet, self.root)

    def test_wrong_model_policy_rejected(self):
        self.packet['model_policy'] = {'production':{'model':'gpt-5.6-terra','thinking':'high'}}
        with self.assertRaisesRegex(ValueError, 'Fixed Astra'):
            adapter.validate_release(self.packet, self.root)

    def test_failure_returns_to_responsible_reference_stage(self):
        result = adapter.validate_result(self.packet,{'status':'FAIL','payload':{'reason':'Wrong contact in reference','return_stage':'reference'}},self.root)
        self.assertEqual(result['return_stage'],'reference')

    def test_result_binding_changes_on_rejection_not_cost_append(self):
        _, jobs = p.workflow(self.packet)
        job = jobs['actor-job']; first=adapter.job_binding(job)
        job['attempts']['new']={'result':'produced'}
        self.assertEqual(adapter.job_binding(job), first)
        job['revision'] += 1
        self.assertNotEqual(adapter.job_binding(job), first)


class ModelDispatchTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.context={'controller_task_id':'controller','project':{'projectId':'actual-project-fixture','isGitRepository':False},'explicit_new_task_authorized':True,'art_execution_authorized':True,'authorization_note':'Explicit user pipeline choice; test performs no real app call.'}
        self.reservation={'dispatch_id':'d1','pipeline_id':'p1','action':'create','status':'RESERVED','target_thread_id':None,'unit_id':'A','revision':1,'execution_mode':'production','downstream_skill':'ndc-character-scene-production','model_policy':p.INTEGRATION_MODELS,'database_path':str(self.root/'pipeline.sqlite'),'packet_path':str(self.root/'packet.json'),'packet_sha256':'a'*64,'work_directory':str(self.root/'output')}

    def test_new_terra_task_has_actual_model_and_effort_arguments(self):
        result=build_dispatch_plan(self.reservation,self.context)
        args=result['tool_call']['arguments']
        self.assertEqual((args['model'],args['thinking']),('gpt-5.6-terra','xhigh'))
        self.assertEqual(result['effect_scope']['character_scene_generation_backend'],'chatgpt_web_browser')
        self.assertFalse(result['effect_scope']['codex_image_generation'])
        self.assertEqual(result['effect_scope']['photoshop_backend'],'native_mcp_single_operator')
        self.assertFalse(result['effect_scope']['photoshop_requires_shared_queue'])
        self.assertTrue(result['effect_scope']['formal_delivery_requires_native_post_gate'])
        self.assertTrue(result['effect_scope']['formal_delivery'])
        self.assertIn('网页版 ChatGPT',args['prompt'])
        self.assertIn('外置 Chrome、Edge',args['prompt'])
        self.assertIn('禁止调用 Codex ImageGen',args['prompt'])

    def test_reused_terra_task_has_same_explicit_model_policy(self):
        self.reservation.update(action='send',target_thread_id='terra-worker')
        args=build_dispatch_plan(self.reservation,self.context)['tool_call']['arguments']
        self.assertEqual((args['model'],args['thinking'],args['threadId']),('gpt-5.6-terra','xhigh','terra-worker'))

    def test_astra_bootstrap_has_medium_effort(self):
        args=build_reference_task_plan(self.context,str(self.root/'request.md'))['tool_call']['arguments']
        self.assertEqual((args['model'],args['thinking']),('gpt-6-astra','medium'))

    def test_wrong_fixed_policy_does_not_dispatch(self):
        self.reservation['model_policy']=copy.deepcopy(p.INTEGRATION_MODELS)
        self.reservation['model_policy']['production']['thinking']='max'
        with self.assertRaises(ValueError):
            build_dispatch_plan(self.reservation,self.context)

    def test_existing_reference_authorization_is_enough_to_resume(self):
        self.context.update(explicit_new_task_authorized=False, existing_task_dispatch_authorized=True, existing_reference_task_id='existing-astra')
        args=build_reference_task_plan(self.context,str(self.root/'request.md'))['tool_call']['arguments']
        self.assertEqual((args['threadId'],args['model'],args['thinking']),('existing-astra','gpt-6-astra','medium'))
        self.context.pop('existing_reference_task_id')
        with self.assertRaises(ValueError):
            build_reference_task_plan(self.context,str(self.root/'request.md'))

    def test_changed_request_cannot_bind_as_the_original_dispatch(self):
        request=self.root/'request.md'; request.write_text('Original scope')
        reserve_reference(build_reference_task_plan(self.context,str(request)),request)
        request.write_text('Different scope')
        with self.assertRaisesRegex(ValueError,'Request changed'):
            bind_reference(request,{'threadId':'real-astra'})

    def test_reference_bootstrap_unknown_cannot_create_twice(self):
        request=self.root/'request.md'; request.write_text('Explicit fixture request')
        plan=build_reference_task_plan(self.context,str(request))
        self.assertEqual(reserve_reference(plan,request)['status'],'SUBMITTING')
        self.assertEqual(bind_reference(request,{'clientThreadId':'setup-only'})['status'],'SETUP_PENDING')
        with self.assertRaises(FileExistsError):
            reserve_reference(plan,request)
        self.assertEqual(bind_reference(request,{'threadId':'real-astra'})['thread_id'],'real-astra')
        self.assertEqual(bind_reference(request,{'clientThreadId':'late-setup'})['status'],'BOUND')
        with self.assertRaises(ValueError):
            bind_reference(request,{'threadId':'another-task'})


if __name__=='__main__':
    unittest.main()
