# 场景提示词与MJ原图重叠推进

本文件中的“下游任务”均指已按 [任务派发](task-dispatch.md) 实际完成 `get_goal` / `create_goal` 启动的下游目标任务；承载对话本身不是目标启动证据。

用于已有授权的场景生产：上游任务锁定并发布场景A的提示包，下游任务制作A的原始MJ图；上游同时准备独立场景B。不等待整批提示全部完成，也不把同一场景的多个视角拆给互不知情的任务。实际派发、单个消费任务领取、租约及修订失效沿用本Skill公共核心，不另建队列。

## 放行单元及最低读取范围

一个unit是一处独立场景的一个主状态。exploration完整范围只有eye_level；non_exploration完整范围按frontal、oblique、overhead_45排列。共享空间事实、全局风格、来源和角色／玩法道具排除边界先锁定，再放行整个视角组。已经批准且不变的视角保留原文件和审核，仅制作缺失或明确要求重画的视角。

上游按[提示Skill](../../ndc-scene-to-mj-prompt/SKILL.md)读取本场景需求、既有资产查验结果、当前来源和必要视角。下游领取后只读当前packet、其中既有[完整v4交接](../../ndc-scene-to-mj-prompt/references/handoff-schema.md)、提示锁、原journal当前相关job和[MJ操作Skill](../../ndc-midjourney-operator/SKILL.md)；不重新盘点全部场景，也不加载道具、PS或视频流程。

## Packet中的场景字段

公共schema仍为ndc-art-stage-packet/v1，pipeline_kind=scene_mj，unit_id等于v4 scene.id。revision按公共核心追加；producer_task_id始终对应原journal.plan.task_id，下游任务ID不会改写母任务历史。execution_mode由总计划固定，不能在领取时切换。

payload仅映射现有文件和原job，不复制一份大场景schema：

```json
{
  "handoff_role": "scene_handoff",
  "prompt_lock_role": "prompt_lock",
  "view_jobs": {"eye_level": "scene-id|eye_level|day"},
  "style_reference_roles": {
    "city_rain": "style_city_rain",
    "character_graphic": "style_character_graphic"
  },
  "generation_authorization_role": "generation_authorization"
}
```

files按公共role/path/sha256记录完整v4 JSON、提示锁、需求／来源、两个既有静态Style Reference文件和已有出图授权证据。实际MJ界面仍选账户内保存的两张静态Style References，不能因打包有本地副本就重传或改成图像／构图参考。任一status:use参考也必须冻结在files中。一个角色对应一份明确文件。

authority.journal是原日志绝对路径；downstream_jobs恰好覆盖view_jobs中的全部视角job。提示发布本身可用upstream_jobs=[]，因为文本没有需要伪造的像素审核；若确有已接受图像上游，则公共核心核对其当前接受状态。

## 文本提示锁与原生产预算

prompt_lock使用ndc-scene-prompt-lock/v1，status=LOCKED，包含scene_id、handoff_sha256、reviewer、checked_at、完整view_ids、逐视角prompt_sha256_by_view、source_roles，以及shared_space_facts数组（每项fact、source_roles）。style_reference_sha256分别绑定city_rain和character_graphic。checks字典逐项写具体核对结论：source_lookup、exact_prompts、shared_space、global_style、view_set、empty_background、deferred_props、reference_roles。不得复制空洞“全部通过”代替来源核对。

提示锁只证明文本／来源合同已检查，不包含visual_check_status或虚构图片输出。视觉参考已有的真实全图／局部审阅照常保留；未变的批准来源复用其有效记录。纯文本移交不为自己建立图像PASS或再次审遍所有旧图。

每个原视角job的requirements绑定scene_id、view_id、master_state、shared_contract_sha256、view_contract_sha256；生成job的limits.model保持原3次含首次，历史已批准视角可沿用source_decision.mode=reuse、model=0的复用job，history及未知提交事件原样保留。scripts/scene_adapter.py的contract_hashes(handoff,lock,file_map)计算这两个合同摘要，validate_release也返回它们。共享摘要绑定公共空间／风格／来源；视角摘要只绑定该view条目。仅修改某视角时，按原art_workflow_state.py revise更新对应job的requirements；共享事实改变才更新相应所有视角。不要把整份handoff文件当作每个视角job的唯一输入，否则一个视角修改会使所有不变图返工。

所有实际生图前仍在原journal预留attempt，submission.arguments.prompt保存本次完整实际提示原文。当前合同的首轮必须精确使用v4 prompt_en；之后按缺陷修改提示，仍用同一job剩余额度。有明确需求修订时保留旧合同、旧首轮文本和次数，在原job追加revise；当前合同首轮按新锁定提示执行，不能将其称为重获3次。unknown/pending先查现有MJ job和保存文件，再原IDresolve，不能重交或另开journal。预算耗尽且无当前合格图时留候选／待处理；已通过视角不为用完次数再次生成。

## 验证与真实出图权限

validation模式只允许核对提示包、生成派发参数和下游接收验证，不打开／提交MJ，不预留真实生成attempt，不accept图片。维护Skill和合成测试不是艺术生产授权。对应generation_authorization可明确allowed=false、mode=validation，并保存来源说明。

production模式实际执行前读取已有用户授权证据：allowed=true、mode=production、source_kind=user_instruction、scope=mj_scene_generation、scene_ids覆盖本scene、instruction记录用户原意、source_roles指向真实授权来源。不能把维护指令、测试夹具或Skill文本当授权。若没有，validate_release返回can_execute=false及MJ_GENERATION_NOT_AUTHORIZED，由公共核心保留WAITING_MANUAL；这只记录原权限缺口，不增加清单审批步骤。有授权的任务继续使用该授权，不重复询问。

共享核心典型调用，脚本和参数全部解析为实际绝对路径：

```text
python pipeline.py --db <原pipeline.sqlite> publish --packet <scene-packet.json> --task <原producer-task-id>
python pipeline.py --db <原pipeline.sqlite> claim --dispatch <已绑定dispatch-id> --task <实际consumer-task-id>
python pipeline.py --db <原pipeline.sqlite> guard --task <实际consumer-task-id>
python pipeline.py --db <原pipeline.sqlite> result --result <scene-result.json> --task <实际consumer-task-id>
```

dispatch创建／复用实际任务、领取票据和未知派发恢复见公共入口。每次外部动作前guard，来源或上游revision变化时停止旧包续作，保留已用额度，领取新包后只重新检查受影响部分。

## 原图结果与接收

result.status为PASS／FAIL／WAITING_MANUAL；验证专用结果为VALIDATION_COMPLETE，不计入生产PASS。FAIL或WAITING_MANUAL的payload.unresolved列具体视角、缺陷、原次数及未知结果；候选文件可保留，不能补写全量通过。

生产PASS的payload.views按完整view顺序，每项包含view_id、原job_id、native_role、stage_review_role、texture_review_role、provenance_role；所有结果文件均放在公共核心分配的输出目录并列入result.files。每张native必须能实际解码为2:1并与原journal当前接受输出一致。既有ndc-stage-visual-self-check/v1记录必须是该接受事件的真实当前记录，继续运行原stage validator。纹理记录沿用ndc-texture-coherence/v1，额外artifact_sha256绑定本原图；workflow=midjourney-scene，coverage_scope=full_image_tiles，并运行既有texture validator。全图100%、完整原像素局部、风格与纹理检查不能由尺寸或生成完成代替。

已接受视角在别的工作目录时，将原图和原审核字节原样复制到本次分配目录；调用现有art_workflow_state.py verify-copy生成ndc-art-byte-copy/v1证据，以该行copy_proof_role列入结果。适配器继续核验原acceptance、原源字节和原审核，仅验证交付副本等同，不新增艺术PASS或attempt。源或拒收变化仍撤销复制有效性。账户／设置等旧证据如需随包交付也复制到分配目录，保留来源，不移动其他任务原文件。

每个provenance记录scene_id、view_id、native_sha256、native_dimensions=[宽,高]、native_format、download_kind=native_mj_image、真实mj_job_id、原submission_id、exact_submitted_prompt、当前合同first_round_prompt_sha256、actual_model、hd_setting=selected/unavailable、account_verified=true及account_evidence_role。保存真实账户检查证据；不把账户名、标签或HD开关当原图尺寸证明。style_reference_roles必须是city_rain=style、character_graphic=style；static_style_sha256匹配原包两静态图。

已明确标为reuse的历史原图使用download_kind=approved_native_mj_reuse，保存reuse_basis与reuse_source_evidence_role所指的真实批准来源，仍核验当前接受、原图字节、现行场景／风格与纹理及多视角空间。未在本次提交MJ，不要求也不补造旧attempt、当前账户截图或未知旧首轮文字；已有可靠历史仍保留。此例外只用于实际批准的原生MJ来源，不允许把其他生成图或裁切图冒充MJ原图。新生成视角继续执行上段全部提交检查。

provenance还写shared_space_review和实际compared_view_ids。先完成的视角可为空，后完成视角与已有接受视角及来源共同核对；最终全部视角对的比较须覆盖。遮挡可随相机变化，已知门窗连接、空间拓扑和主状态不能变化。只有实际查阅过的比较才写入，不能让第一张图声称比较尚不存在的视角。最终PASS不含未解决required view；原MJ字节直接交付，不追加PS扩图、改光或道具任务。

验证结果只需一个result.files中的validation_record。payload.validation_record_role指向它；记录check_kind=contract_only、artistic_approval=false、mj_submitted=false、scene_id、完整view_ids和handoff_sha256。validate_result返回VALIDATION_COMPLETE，不能用它替换生产审核或原图文件。

## 只读适配器与测试夹具

scripts/scene_adapter.py提供validate_release(packet,base:Path)->dict和validate_result(packet,result,base:Path)->dict；失败抛ValueError。它校验文件、文本合同、原累计预算和证据，不提交MJ，不写attempt/accept，不变更生产状态；公共核心负责派发和接收事务。

tests/test_scene_adapter.py导出make_fixture(base,scene_id,producer_task_id,mode='validation',scene_mode='exploration',history_model=0)。它构建完整v4合成合同、allowed=false证据及初始测试journal，引用既有静态图；不生成艺术图片、不写视觉PASS、不提交工具。测试内部另用明确标注的人工像素／记录夹具验证现有stage与texture脚本，不可移入真实生产目录或当作真实审核。
