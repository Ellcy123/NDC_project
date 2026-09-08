"""Synthetic contracts only. make_fixture never submits or accepts art."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import scene_adapter as adapter


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    return path


def file_ref(role, path):
    return {'role': role, 'path': str(path.resolve()), 'sha256': adapter.sha(path)}


def make_fixture(base, scene_id='synthetic_scene', producer_task_id='synthetic_scene_producer',
                 mode='validation', scene_mode='exploration', history_model=0, reuse_views=()):
    """Return a releasable fixture packet with no attempt or artistic PASS events."""
    base = Path(base).resolve()
    base.mkdir(parents=True, exist_ok=True)
    source = base / 'synthetic-source.txt'
    source.write_text('SYNTHETIC CONTRACT TEST ONLY: a period room, a north doorway and a west window. No art approval or MJ authority.', encoding='utf-8')
    source_ref = file_ref('source_spec', source)
    asset_dir = Path(adapter.__file__).resolve().parents[2] / 'ndc-midjourney-operator/assets'
    styles = {'city_rain': file_ref('style_city_rain', asset_dir / 'ndc-static-style-city-rain.jpg'),
              'character_graphic': file_ref('style_character_graphic', asset_dir / 'ndc-static-style-character-graphic.png')}
    views = []
    for name in adapter.VIEWS[scene_mode]:
        camera = {'position': 'source-supported camera position', 'view_direction': name,
                  'perspective': 'three-point perspective' if scene_mode == 'exploration' else 'source-supported perspective',
                  'camera_height': '1.7–1.8 meters' if scene_mode == 'exploration' else 'source-supported height',
                  'horizon': 'upper third' if scene_mode == 'exploration' else 'source-supported horizon',
                  'pitch': '45 degrees downward' if name == 'overhead_45' else 'eye-level',
                  'scale_calibration': ['door height']}
        description = {'viewpoint_change': name, 'foreground': 'quiet floor', 'middle_ground': 'room-defining masses',
                       'background': 'source doorway', 'lateral_layout': 'window on west wall',
                       'architecture_relations': ['north doorway and west window remain connected by the same wall layout'],
                       'camera_calibration': ['door height visible']}
        views.append({'id': name, 'label_zh': '测试视角', 'camera_contract': camera, 'scene_description': description,
                      'prompt_en': 'Period room, '+name+' view, north doorway, west window, compressed matte shapes --ar 2:1 --no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes',
                      'prompt_zh': '测试用时期房间，北侧门、西侧窗；无可见人物；禁止作为艺术批准。'})
    handoff = {'handoff_version': 'ndc-mj-scene/v4', 'workflow_end_stage': 'mj_image_delivery',
               'scene': {'id': scene_id, 'name': 'Synthetic contract room', 'mode': scene_mode, 'canvas_use': 'story_progression'},
               'original_requirement': 'Synthetic contract only; see synthetic-source.txt.',
               'visual_brief': {'time': 'day', 'interior_exterior': 'interior', 'architectural_function': 'period room',
                                'visual_facts': ['north doorway', 'west window'], 'removed_nonvisual_facts': []},
               'prop_policy': {'mode': 'defer_gameplay_props', 'ambient_dressing': 'sparse_period_appropriate_noninteractive',
                               'retained_spatial_masses': ['walls'], 'deferred_from_source': [], 'explicit_mj_exceptions': []},
               'normalized_requirement': {'hard': ['empty environment with no visible characters', 'source room topology'],
                                          'soft': ['period material'], 'flexible': ['subordinate ambient dressing'],
                                          'must_not_have': ['people, named characters, crowds, human figures, faces, bodies, silhouettes']},
               'texture_contract': {'style_authority_locked': True, 'approved_style_authority': ['the two existing static references'],
                                    'immutable_style_traits': ['compressed shapes'], 'focal_detail_zones': ['door'],
                                    'secondary_detail_zones': ['window'], 'quiet_zones': ['wall'], 'distant_zones': ['room depth'],
                                    'material_texture_rules': ['scale-aware matte texture'], 'prohibited_artifacts': ['nonsemantic noise'],
                                    'style_changing_cleanup_language_forbidden': True},
               'view_prompts': views, 'references': [], 'parameters': {'generation_aspect_ratio': '2:1', 'model': 'latest', 'quality': 'hd_if_available', 'other': []},
               'framing_context': {'central_readability': 'door and window', 'known_later_display_constraint': None, 'edge_continuity': 'quiet wall'},
               'master_state': 'day', 'delivery_contract': {'artifact': 'native_mj_image', 'preserve_original_pixels': True,
                                                         'record_actual_dimensions': True, 'include': ['native file and current review evidence']},
               'review_priority': ['camera_and_layout', 'architecture_and_routes', 'empty_background', 'style_and_texture', 'editing_convenience'],
               'assumptions': [], 'operator_notes': {'iteration_budget_per_view': 3, 'preferred_action': 'submit_review_iterate_deliver_native_mj'}}
    hpath = write(base / 'scene-handoff.json', handoff)
    lock = {'schema': 'ndc-scene-prompt-lock/v1', 'status': 'LOCKED', 'scene_id': scene_id,
            'handoff_sha256': adapter.sha(hpath), 'reviewer': 'synthetic-contract-fixture-only', 'checked_at': '2026-09-08T00:00:00Z',
            'view_ids': [v['id'] for v in views], 'prompt_sha256_by_view': {v['id']: adapter.text_sha(v['prompt_en']) for v in views},
            'checks': {name: 'Synthetic contract shape checked; no artistic approval.' for name in adapter.LOCK_CHECKS},
            'shared_space_facts': [{'fact': 'north doorway and west window keep source identities and connections', 'source_roles': ['source_spec']}],
            'source_roles': ['source_spec'], 'style_reference_sha256': {key: value['sha256'] for key, value in styles.items()}}
    lpath = write(base / 'prompt-lock.json', lock)
    # This is a test fixture, deliberately not an actual image-generation grant.
    auth = {'allowed': False, 'mode': 'validation', 'source_kind': 'user_instruction', 'scene_ids': [scene_id],
            'scope': 'mj_scene_generation', 'instruction': 'Synthetic validation only; do not submit MJ.', 'source_roles': ['source_spec']}
    apath = write(base / 'generation-authorization.json', auth)
    files = [source_ref, *styles.values(), file_ref('scene_handoff', hpath), file_ref('prompt_lock', lpath), file_ref('generation_authorization', apath)]
    packet = {'schema': 'ndc-art-stage-packet/v1', 'pipeline_kind': 'scene_mj', 'unit_id': scene_id, 'revision': 1,
              'producer_task_id': producer_task_id, 'execution_mode': mode, 'files': files,
              'payload': {'handoff_role': 'scene_handoff', 'prompt_lock_role': 'prompt_lock',
                          'style_reference_roles': {key: value['role'] for key, value in styles.items()},
                          'generation_authorization_role': 'generation_authorization',
                          'view_jobs': {v['id']: scene_id+'|'+v['id']+'|day' for v in views}},
              'authority': {'journal': str(base/'production-journal.jsonl'), 'upstream_jobs': [],
                            'downstream_jobs': [scene_id+'|'+v['id']+'|day' for v in views]}}
    shared, view_hashes = adapter.contract_hashes(handoff, lock, adapter.file_map(files, base))
    jobs = []
    for name, key in packet['payload']['view_jobs'].items():
        job = {'job_id': key, 'asset_key': 'scene:'+key, 'source_decision': {'mode': 'generate', 'evidence': 'synthetic inventory only'},
               'requirements': {'scene_id': scene_id, 'view_id': name, 'master_state': 'day',
                                'shared_contract_sha256': shared, 'view_contract_sha256': view_hashes[name]},
               'inputs': [source_ref, *styles.values()], 'depends_on': [], 'limits': {'model': 3}, 'history': {'model': history_model},
               'required_criteria': ['camera_and_layout', 'architecture_and_routes', 'empty_background', 'style_lock', 'texture_coherence'],
               'output_roles': ['native_mj_image']}
        if history_model:
            job['history_evidence'] = [source_ref]
        if name in reuse_views:
            job['source_decision']['mode'] = 'reuse'
            job['limits']['model'] = 0
        jobs.append(job)
    plan = write(base/'production-plan.json', {'schema': 'ndc-art-production-plan/v1', 'task_id': producer_task_id, 'jobs': jobs})
    adapter.workflow().initialize(plan, Path(packet['authority']['journal']))
    write(base/'packet.json', packet)
    return packet


class SceneAdapterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.packet = make_fixture(self.base)

    def refresh(self, role, data):
        row = next(r for r in self.packet['files'] if r['role'] == role)
        write(Path(row['path']), data)
        row['sha256'] = adapter.sha(row['path'])

    def production_result(self, packet=None, base=None):
        """Private test-only evidence, using real validators on artificial pixels."""
        packet, base = packet or self.packet, base or self.base
        packet['execution_mode'] = 'production'
        auth_row=next(r for r in packet['files'] if r['role']=='generation_authorization')
        auth=adapter.read(auth_row['path']); auth.update(allowed=True,mode='production',instruction='SYNTHETIC TEST GRANT ONLY; no actual tool submission')
        write(Path(auth_row['path']),auth); auth_row['sha256']=adapter.sha(auth_row['path'])
        api=adapter.workflow(); journal=Path(packet['authority']['journal'])
        handoff=adapter.read(next(r['path'] for r in packet['files'] if r['role']=='scene_handoff'))
        texture_script=adapter.project_validator('validate-ndc-texture-gate.py')
        spec=importlib.util.spec_from_file_location('fixture_texture_protocol',texture_script); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        files=[file_ref('account_evidence',base/'synthetic-source.txt')]; output_views=[]
        for index, view in enumerate(handoff['view_prompts']):
            name=view['id']; key=packet['payload']['view_jobs'][name]
            header,events,_=api.load(journal); reuse=api.state(header,events)[key]['source_decision']['mode']=='reuse'
            native=base/(name+'_artificial_test.png'); Image.new('RGB',(20,10),(30,40,50)).save(native)
            sid='SYNTHETIC_NOT_AN_MJ_SUBMISSION_'+name
            if not reuse:
                api.mutate(journal,key,'attempt',{'kind':'model','submission_id':sid,'submission':{'tool':'synthetic_no_tool_called','operation':'fixture_only','arguments':{'prompt':view['prompt_en']}}})
                api.mutate(journal,key,'resolve',{'submission_id':sid,'result':'produced','evidence':'Artificial test pixels; no MJ call occurred'})
            outputs=write(base/(name+'_outputs.json'),[file_ref('native_mj_image',native)])
            request=base/(name+'_request.json'); api.prepare_review(journal,key,outputs,request)
            frozen=adapter.read(request)
            stage=base/(name+'_stage.json')
            record={'schema':'ndc-stage-visual-self-check/v1','stage_id':'SYNTHETIC_TEST_'+name,'role':'native_mj_image',
                    'reviewer':'TEST FIXTURE ONLY, never production approval','reviewed_at':'2026-09-08T00:00:00Z',
                    'inputs':frozen['context']['inputs'],'outputs':frozen['outputs'],
                    'views':[dict(file_ref('test_whole',native),kind='whole_100'),dict(file_ref('test_local',native),kind='local_200_or_tiles')],
                    'criteria':[{'name':c,'applicable':True,'status':'PASS','finding':'Synthetic validator fixture only'} for c in frozen['context']['required_criteria']],
                    'visual_check_status':'PASS','rework_stage':None,'workflow_context_sha256':frozen['context_sha256']}
            write(stage,record)
            api.mutate(journal,key,'accept',{'request':str(request),'records':[str(stage)],'validator':str(adapter.project_validator('validate-ndc-stage-visual-self-check.py'))})
            texture=base/(name+'_texture.json')
            data={'schema_version':'ndc-texture-coherence/v1','asset_id':'SYNTHETIC_'+name,'workflow':'midjourney-scene',
                  'artifact_sha256':adapter.sha(native),'source_authority':{'reference':'synthetic-source.txt','role':'test_fixture'},
                  'review':{'reviewer':'TEST FIXTURE ONLY','whole_image_checked':True,'local_coverage_complete':True,'coverage_scope':'full_image_tiles'},
                  'style_lock_checks':{c:'PASS' for c in module.STYLE_CHECKS},'texture_coherence_checks':{c:'PASS' for c in module.TEXTURE_CHECKS},
                  'evidence':{'whole_image':[str(native)],'local_coverage':[str(native)],'style_comparison':['synthetic test only']},
                  'failure_return_source':'synthetic test','formal_status':'PASS'}
            write(texture,data)
            provenance=base/(name+'_provenance.json')
            data={'scene_id':packet['unit_id'],'view_id':name,'native_sha256':adapter.sha(native),'native_dimensions':[20,10],
                  'native_format':'PNG','download_kind':'native_mj_image','mj_job_id':'SYNTHETIC_NO_REAL_JOB','account_verified':True,
                  'account_evidence_role':'account_evidence','actual_model':'SYNTHETIC_NOT_A_MODEL','hd_setting':'selected',
                  'style_reference_roles':{'city_rain':'style','character_graphic':'style'},
                  'static_style_sha256':{k:next(r['sha256'] for r in packet['files'] if r['role']==role) for k,role in packet['payload']['style_reference_roles'].items()},
                  'first_round_prompt_sha256':adapter.text_sha(view['prompt_en']),'submission_id':sid,'exact_submitted_prompt':view['prompt_en'],
                  'shared_space_review':'SYNTHETIC contract comparison only','compared_view_ids':[v['id'] for v in handoff['view_prompts'][:index]]}
            if reuse:
                data.update(download_kind='approved_native_mj_reuse',reuse_basis='SYNTHETIC approved native-source fixture',reuse_source_evidence_role='account_evidence')
                for field in ('submission_id','mj_job_id','account_verified','account_evidence_role','actual_model','hd_setting',
                              'style_reference_roles','static_style_sha256','first_round_prompt_sha256','exact_submitted_prompt'):
                    data.pop(field,None)
            write(provenance,data)
            roles={'native_role':'native_'+name,'stage_review_role':'stage_'+name,'texture_review_role':'texture_'+name,'provenance_role':'provenance_'+name}
            files += [file_ref(roles[field],p) for field,p in [('native_role',native),('stage_review_role',stage),('texture_review_role',texture),('provenance_role',provenance)]]
            output_views.append(dict(view_id=name,job_id=key,**roles))
        return {'status':'PASS','files':files,'payload':{'views':output_views,'unresolved':[]}}

    def test_validation_release_is_not_mj_authorization(self):
        result = adapter.validate_release(self.packet, self.base)
        self.assertFalse(result['can_execute'])
        self.assertTrue(result['validation_only'])
        header, events, _ = adapter.workflow().load(self.packet['authority']['journal'])
        self.assertEqual(events, [])

    def test_full_three_views_can_release_as_one_unit(self):
        packet = make_fixture(self.base/'other', scene_mode='non_exploration')
        self.assertEqual(adapter.validate_release(packet, self.base)['view_ids'], ['frontal','oblique','overhead_45'])

    def test_partial_nonexploration_view_set_is_rejected(self):
        packet = make_fixture(self.base/'other', scene_mode='non_exploration')
        row = next(r for r in packet['files'] if r['role'] == 'scene_handoff')
        handoff = adapter.read(row['path']); handoff['view_prompts'].pop(); write(Path(row['path']), handoff); row['sha256'] = adapter.sha(row['path'])
        with self.assertRaisesRegex(ValueError, 'full ordered view set'):
            adapter.validate_release(packet, self.base)

    def test_changed_prompt_is_rejected_before_journal_use(self):
        data = adapter.read(self.base/'scene-handoff.json'); data['view_prompts'][0]['prompt_en'] = data['view_prompts'][0]['prompt_en'].replace('Period room','Changed room')
        self.refresh('scene_handoff', data)
        with self.assertRaisesRegex(ValueError, 'stale scene/handoff'):
            adapter.validate_release(self.packet, self.base)

    def test_wrong_aspect_character_leakage_and_model_flag_rejected(self):
        initial = adapter.read(self.base/'scene-handoff.json')
        for bad in ['--ar 16:10', '--ar 2:1 --v 7', '--ar 2:1 --ar 2:1']:
            data = copy.deepcopy(initial); data['view_prompts'][0]['prompt_en'] = initial['view_prompts'][0]['prompt_en'].replace('--ar 2:1', bad)
            self.refresh('scene_handoff', data)
            with self.assertRaises(ValueError): adapter.validate_release(self.packet, self.base)
        data = copy.deepcopy(initial); data['view_prompts'][0]['prompt_en'] = 'A person, '+data['view_prompts'][0]['prompt_en']; self.refresh('scene_handoff', data)
        with self.assertRaisesRegex(ValueError, 'positive scene prompt'): adapter.validate_release(self.packet, self.base)

    def test_source_change_revokes_release(self):
        (self.base/'synthetic-source.txt').write_text('changed source')
        with self.assertRaisesRegex(ValueError, 'file missing or changed'): adapter.validate_release(self.packet, self.base)

    def test_one_static_reference_cannot_be_dropped(self):
        self.packet['payload']['style_reference_roles'].pop('character_graphic')
        with self.assertRaisesRegex(ValueError, 'both static'): adapter.validate_release(self.packet, self.base)

    def test_foreign_journal_task_is_rejected(self):
        self.packet['producer_task_id'] = 'unrelated-task'
        with self.assertRaisesRegex(ValueError, 'another producer task'): adapter.validate_release(self.packet, self.base)

    def test_missing_original_generation_grant_waits_in_production(self):
        self.packet['execution_mode'] = 'production'
        result = adapter.validate_release(self.packet, self.base)
        self.assertFalse(result['can_execute'])
        self.assertEqual(result['stop_reason'], 'MJ_GENERATION_NOT_AUTHORIZED')

    def test_history_budget_is_preserved_and_validator_is_read_only(self):
        packet = make_fixture(self.base/'old', history_model=3)
        journal = Path(packet['authority']['journal']); before = journal.read_bytes()
        self.assertEqual(adapter.validate_release(packet,self.base)['view_budgets']['eye_level']['used'],3)
        self.assertEqual(before, journal.read_bytes())

    def test_unknown_submission_is_preserved(self):
        api = adapter.workflow(); journal = Path(self.packet['authority']['journal']); key = next(iter(self.packet['payload']['view_jobs'].values()))
        api.mutate(journal,key,'attempt',{'kind':'model','submission_id':'synthetic-unknown',
                   'submission':{'tool':'synthetic_no_tool_called','operation':'fixture','arguments':{'prompt':'fixture'}}})
        api.mutate(journal,key,'resolve',{'submission_id':'synthetic-unknown','result':'unknown','evidence':'synthetic unknown outcome'})
        result = adapter.validate_release(self.packet,self.base)
        self.assertEqual(result['view_budgets']['eye_level']['used'],1)
        self.assertEqual(result['view_budgets']['eye_level']['unresolved_submissions'],['synthetic-unknown'])

    def test_text_lock_must_not_claim_visual_pass(self):
        lock = adapter.read(self.base/'prompt-lock.json'); lock['visual_check_status'] = 'PASS'; self.refresh('prompt_lock',lock)
        with self.assertRaisesRegex(ValueError,'manufacture artistic PASS'): adapter.validate_release(self.packet,self.base)

    def test_view_revision_changes_only_its_contract_hash(self):
        packet = make_fixture(self.base/'multi',scene_mode='non_exploration')
        files = adapter.file_map(packet['files'],self.base); h = adapter.read(files['scene_handoff']['path']); lock = adapter.read(files['prompt_lock']['path'])
        shared, views = adapter.contract_hashes(h,lock,files)
        h['view_prompts'][1]['scene_description']['foreground'] = 'modified oblique foreground'
        new_shared, new_views = adapter.contract_hashes(h,lock,files)
        self.assertEqual(shared,new_shared); self.assertEqual(views['frontal'],new_views['frontal']); self.assertNotEqual(views['oblique'],new_views['oblique'])

    def test_shared_room_change_changes_shared_digest(self):
        files=adapter.file_map(self.packet['files'],self.base); h=adapter.read(files['scene_handoff']['path']); lock=adapter.read(files['prompt_lock']['path'])
        before=adapter.contract_hashes(h,lock,files)[0]; lock['shared_space_facts'][0]['fact']='door moved to another wall'
        self.assertNotEqual(before,adapter.contract_hashes(h,lock,files)[0])

    def test_validation_complete_is_not_an_art_result(self):
        data={'check_kind':'contract_only','artistic_approval':False,'mj_submitted':False,'scene_id':self.packet['unit_id'],
              'view_ids':['eye_level'],'handoff_sha256':adapter.sha(self.base/'scene-handoff.json')}
        path=write(self.base/'validation-receipt.json',data)
        result={'status':'VALIDATION_COMPLETE','files':[file_ref('validation_record',path)],'payload':{'validation_record_role':'validation_record'}}
        self.assertEqual(adapter.validate_result(self.packet,result,self.base)['status'],'VALIDATION_COMPLETE')
        result['status']='PASS'
        with self.assertRaisesRegex(ValueError,'cannot return production PASS'): adapter.validate_result(self.packet,result,self.base)

    def test_unresolved_result_cannot_be_empty(self):
        with self.assertRaisesRegex(ValueError,'concrete unresolved'): adapter.validate_result(self.packet,{'status':'WAITING_MANUAL','files':[],'payload':{}},self.base)
        result=adapter.validate_result(self.packet,{'status':'WAITING_MANUAL','files':[],'payload':{'unresolved':['existing submission outcome unknown']}},self.base)
        self.assertFalse(result['artistic_approval'])

    def test_native_result_uses_real_current_journal_and_existing_validators(self):
        result=self.production_result()
        self.assertEqual(adapter.validate_result(self.packet,result,self.base)['status'],'PASS')

    def test_thumbnail_or_wrong_aspect_cannot_pass(self):
        result=self.production_result(); row=next(r for r in result['files'] if r['role']=='native_eye_level')
        Image.new('RGB',(16,10)).save(row['path']); row['sha256']=adapter.sha(row['path'])
        with self.assertRaisesRegex(ValueError,'decode at 2:1'): adapter.validate_result(self.packet,result,self.base)

    def test_stale_texture_binding_blocks_result(self):
        result=self.production_result(); row=next(r for r in result['files'] if r['role']=='texture_eye_level')
        data=adapter.read(row['path']); data['artifact_sha256']='0'*64; write(Path(row['path']),data); row['sha256']=adapter.sha(row['path'])
        with self.assertRaisesRegex(ValueError,'texture review does not bind'): adapter.validate_result(self.packet,result,self.base)

    def test_unchecked_texture_is_rejected_by_existing_texture_validator(self):
        result=self.production_result(); row=next(r for r in result['files'] if r['role']=='texture_eye_level')
        data=adapter.read(row['path']); data['review']['local_coverage_complete']=False; data['formal_status']='BLOCKED'; write(Path(row['path']),data); row['sha256']=adapter.sha(row['path'])
        with self.assertRaisesRegex(ValueError,'validate-ndc-texture-gate.py'): adapter.validate_result(self.packet,result,self.base)

    def test_forged_submitted_prompt_does_not_match_original_attempt(self):
        result=self.production_result(); row=next(r for r in result['files'] if r['role']=='provenance_eye_level')
        data=adapter.read(row['path']); data['exact_submitted_prompt']='different prompt'; write(Path(row['path']),data); row['sha256']=adapter.sha(row['path'])
        with self.assertRaisesRegex(ValueError,'differs from the original journal'): adapter.validate_result(self.packet,result,self.base)

    def test_incomplete_cross_view_spatial_comparison_blocks_full_scene_pass(self):
        base=self.base/'multi'; packet=make_fixture(base,scene_mode='non_exploration'); result=self.production_result(packet,base)
        self.assertEqual(adapter.validate_result(packet,result,base)['status'],'PASS')
        row=next(r for r in result['files'] if r['role']=='provenance_overhead_45')
        data=adapter.read(row['path']); data['compared_view_ids']=[]; write(Path(row['path']),data); row['sha256']=adapter.sha(row['path'])
        with self.assertRaisesRegex(ValueError,'cross-view spatial comparison is incomplete'): adapter.validate_result(packet,result,base)

    def test_existing_accepted_native_copy_reuses_current_review_without_reapproval(self):
        result=self.production_result(); job=self.packet['payload']['view_jobs']['eye_level']
        native_row=next(r for r in result['files'] if r['role']=='native_eye_level'); stage_row=next(r for r in result['files'] if r['role']=='stage_eye_level')
        target=self.base/'assigned-output'; target.mkdir()
        copy_path=target/'unchanged-native.png'; copy_path.write_bytes(Path(native_row['path']).read_bytes())
        stage_copy=target/'unchanged-stage.json'; stage_copy.write_bytes(Path(stage_row['path']).read_bytes())
        native_row['path']=str(copy_path); stage_row['path']=str(stage_copy)
        copies=write(target/'copies.json',[file_ref('native_mj_image',copy_path)])
        proof=target/'copy-proof.json'; api=adapter.workflow(); journal=Path(self.packet['authority']['journal']); before=journal.read_bytes()
        api.verify_copy(journal,job,copies,proof)
        result['files'].append(file_ref('copy_proof',proof)); result['payload']['views'][0]['copy_proof_role']='copy_proof'
        self.assertEqual(adapter.validate_result(self.packet,result,self.base)['status'],'PASS')
        self.assertEqual(before,journal.read_bytes())
        api.mutate(journal,job,'reject',{'reason':'synthetic source rejection'})
        with self.assertRaisesRegex(ValueError,'no accepted current artifact'): adapter.validate_result(self.packet,result,self.base)

    def test_mixed_existing_and_new_views_does_not_forge_old_generation(self):
        base=self.base/'mixed'; packet=make_fixture(base,scene_mode='non_exploration',reuse_views=('frontal',))
        result=self.production_result(packet,base)
        self.assertEqual(adapter.validate_result(packet,result,base)['status'],'PASS')
        api=adapter.workflow(); header,events,_=api.load(packet['authority']['journal']); key=packet['payload']['view_jobs']['frontal']
        self.assertEqual(api.state(header,events)[key]['attempts'],{})
        self.assertEqual(api.state(header,events)[key]['limits']['model'],0)


if __name__ == '__main__':
    unittest.main()
