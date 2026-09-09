"""Prepare the explicitly requested Astra/medium reference task; no app call."""
import argparse
import json
import hashlib
import os
from pathlib import Path
from dispatch_plan import absolute, text, INTEGRATION_MODELS, DispatchPlanError, goal_bootstrap
from pipeline import unwrap_response


def bootstrap_path(request_path):
    request = Path(request_path).resolve()
    return request.with_name(request.name + '.reference-dispatch.json')


def reserve_reference(plan, request_path):
    request = Path(request_path).resolve()
    body = {'status':'SUBMITTING','request':str(request),'request_sha256':hashlib.sha256(request.read_bytes()).hexdigest(),'tool_call':plan['tool_call']}
    marker = bootstrap_path(request)
    with marker.open('x', encoding='utf-8') as handle:
        json.dump(body, handle, ensure_ascii=False, indent=2)
        handle.flush(); os.fsync(handle.fileno())
    return {'status':'SUBMITTING','marker':str(marker),'tool_call':plan['tool_call']}


def bind_reference(request_path, response):
    marker = bootstrap_path(request_path)
    lock = marker.with_name(marker.name + '.lock')
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    try:
        data = json.loads(marker.read_text(encoding='utf-8'))
        if hashlib.sha256(Path(request_path).read_bytes()).hexdigest() != data['request_sha256']:
            raise DispatchPlanError('Request changed after dispatch; reconcile the original task before revising the request')
        actual = unwrap_response(response)
        target = actual.get('threadId')
        if data['status'] == 'BOUND':
            if target and target != data['thread_id']:
                raise DispatchPlanError('A different task cannot replace the bound reference task')
            return data
        expected = data['tool_call']['arguments'].get('threadId')
        if target and expected and target != expected:
            raise DispatchPlanError('Response does not belong to the requested existing task')
        data.update(status='BOUND' if target else ('SETUP_PENDING' if actual.get('clientThreadId') else 'UNKNOWN'), actual_response=response)
        if target:
            data['thread_id'] = target
        temp = marker.with_name(marker.name + '.new')
        temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        os.replace(temp, marker)
        return data
    finally:
        os.close(fd); lock.unlink()


def build_reference_task_plan(context, request_path):
    request_path = absolute(request_path, 'request_path')
    note = text(context.get('authorization_note'), 'authorization_note')
    target = context.get('existing_reference_task_id')
    allowed = context.get('explicit_new_task_authorized') is True or (bool(target) and context.get('existing_task_dispatch_authorized') is True)
    if not allowed:
        raise DispatchPlanError('Use the existing explicit authorization to create or resume the reference task')
    prompt = ('按用户已授权的当前需求运行 ndc-character-scene-reference，模型 Astra，中级智能。'
              '先读取此实际需求文件及其中原生产ID、历史来源和全部场景范围：' + request_path + '\n'
              '你是参考阶段兼协调任务。每个完整独立场景的所有景深、单人完整白模、联合快照和实际生图输入通过后，'
              '立即按 ndc-art-stage-pipeline 的 character_scene 交接，创建或复用唯一 Terra/xhigh 生产任务；你继续其他场景参考。'
              '不要另开参考协调层，不改生产ID或重开次数，不自动恢复用户暂停的资产工作。'
              '具体资产生产范围和权限以需求原文为准；若仅维护/验证Skill，不调用生图或PS。\n授权依据：' + note)
    prompt = goal_bootstrap('完成需求文件 ' + request_path + ' 中全部已授权人物入景场景的完整参考，核实身份来源和原次数，确定全部角色/状态的位置、比例、动作、演绎与遮挡，完成整场白模及实际UI检查，逐整场冻结交给唯一正式生产任务；交接后继续其他场景，不持续监控或代做下游生产。') + '\n\n' + prompt
    if target:
        call = {'name':'mcp__codex_app__send_message_to_thread', 'arguments':{'threadId':text(target, 'existing_reference_task_id'), 'prompt':prompt}}
    else:
        project = context['project']
        if not isinstance(project.get('isGitRepository'), bool):
            raise DispatchPlanError('Use actual list_projects metadata')
        environment = 'worktree' if project['isGitRepository'] else 'local'
        if context.get('use_saved_project_directly') is True:
            text(context.get('saved_project_request_note'), 'saved_project_request_note')
            environment = 'local'
        call = {'name':'mcp__codex_app__create_thread', 'arguments':{'title':'NDC 人物入景参考与协调', 'prompt':prompt, 'target':{'type':'project','projectId':text(project.get('projectId'), 'projectId'),'environment':{'type':environment}}}}
    call['arguments'].update(INTEGRATION_MODELS['reference'])
    return {'effect':'PARAMETERS_ONLY_NO_APP_CALL', 'tool_call':call, 'before_call':'Persist the request and a SUBMITTING bootstrap marker once; an existing marker must be reconciled instead of repeating create/send.', 'after_call':'Save actual response and reference threadId. A clientThreadId remains SETUP_PENDING. This task becomes pipeline controller; use its real ID for init.', 'model_policy':INTEGRATION_MODELS}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--context', required=True)
    parser.add_argument('--request', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--reserve', action='store_true', help='Atomically mark this request SUBMITTING before the single real app call')
    parser.add_argument('--response', help='Bind an actual app response to the original bootstrap; never resend')
    args = parser.parse_args()
    if args.response:
        result = bind_reference(args.request, json.loads(Path(args.response).read_text(encoding='utf-8-sig')))
    else:
        result = build_reference_task_plan(json.loads(Path(args.context).read_text(encoding='utf-8-sig')), args.request)
        if args.reserve:
            result = reserve_reference(result, args.request)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'status':'PARAMETERS_PREPARED','out':args.out}, ensure_ascii=False))
