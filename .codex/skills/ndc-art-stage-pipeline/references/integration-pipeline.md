# Astra参考 → Terra编排网页版ChatGPT正式入景

## 阶段责任边界（2026-09-09 用户最新要求）

上游把整个场景及所有必需角色/状态的白模确定、冻结并成功交接后，完成该场景参考职责，立即推进下一独立场景；全部参考交接后结束本轮。下游全权负责正式角色生成、与白模的位置及比例对齐、头身比/动作核验、完整母层、遮挡、提取合成、自检、返修和交付。下游默认优先生成、回收、审核并冻结同一场景全部必需角色／状态，再统一进行提取、去背景、Alpha、注册与合成；这是减少切换和返工的优先顺序，不是强制阻断。网页生成、回收或浏览器传输真实等待／受阻，或有其它可记录的具体调度理由时，可先处理已经就绪角色的合规提取和独立下游工作。上游不持续监控、轮询等待、逐角色审查生产结果或代做生产修复。结果由下游自行写入原流水并接续下一 READY 场景；结果登记是下游职责，不要求上游常驻回收。

沿正确白模修正正式角色的尺度、落点或动作属于生产工作；仅白模方案本身存在影响核心关系的错误时，由下游附差异证据主动回传 reference。收到明确返修请求才重开受影响参考，其他已交接场景不重复审核。上游保留交接前白模核心检查与可追溯包，下游保留正式生成前和交付前的真实检查，不能把已移交的生产自检重新变为上游监控任务。本节优先于公共协议中容易被理解为上游必须持续等待/回收的表述。

白模顺序：初次生成时包括隐藏部位的完整人体，保留未裁剪母层；随后按真实遮挡关系裁剪派生层或制作蒙版，审核裁剪后的场景参考。正常裁剪不算缺失，不要求补回场景中本应被遮住的像素；小瑕疵容错不取消初始完整生成。正式角色同样先生成完整母层再应用遮挡。

白模交接按[白模放行与正式完整性](../../ndc-character-scene-integration/references/whitebox-acceptance.md)：小型遮挡/缺失不影响位置、比例、头身比、动作和演绎时可放行，完整场景包指角色及状态范围齐全。下游不因这些已记录细节退回参考，须在正式生图补全并实查完整角色；原native检查保留真实核心判断与当前文件绑定。

本项目用户已明确指定此分工与自动任务交接，适用于其已授权的入景生产需求，不逐场重复询问任务创建。维护Skill不恢复暂停资产，也不凭空新增生产批次。UI/MJ原流程保持原模型；不要修改全局Codex模型或恢复旧模型路由系统。

## 模型与启动

参考和正式生产任务均须按[目标启动协议](task-dispatch.md)实际启用持续目标。参考目标止于全批完整场景参考交接，生产目标覆盖全批最终图层、接触层、原尺寸 XY、预览和可重建清单及实际自检；不将前者扩成常驻生产监控。旧普通任务优先原任务补建目标，不另建重复生产任务。

固定配置：参考兼协调任务 `gpt-6-astra / medium`；正式生产编排任务 `gpt-5.6-terra / xhigh`。“极高”对应 `xhigh`，不是max或ultra。每条流水一个参考协调任务、一个可复用生产任务。这里的 Terra 是第二阶段任务执行者，不是正式像素生成后端；正式像素固定由该任务操控受支持的内置 `iab` 或外置 Chrome/Edge，通过网页版 ChatGPT 生成。

当前已是Astra/medium的生产任务直接担任协调者；否则将实际需求保存到原过程目录，使用 `scripts/reference_task_plan.py --context <实际上下文.json> --request <需求绝对路径> --out <工具参数.json>` 生成参考任务的create/send参数。上下文字段沿用 [任务派发](task-dispatch.md)，`existing_reference_task_id`只在实际存在该参考任务时填写。预览参数后，原命令加 `--reserve` 原子创建需求文件旁的reference-dispatch.json并返回SUBMITTING，成功一次后才实际调用应用工具。重复reserve拒绝；原命令以 `--response <实际回执.json>` 绑定真实ID。只有clientThreadId时保留SETUP_PENDING，未知结果核实原任务，不删除标记或改需求文件名重建。工具参数已经含Astra/medium，Skill文本不能自行切换正在运行的回合。

参考任务获得真实ID后以自身作为 `controller_task_id` 和各场景 `producer_task_id` 初始化流水。新开 Git worktree 仍通过策划仓库公共入口解析当前主 Skill，并共享过程数据库绝对路径；不能复制数据库、回退到旧提交中的 Skill，或引用维护机 `.agents/skills` 路径。

派发生产使用公共reserve → dispatch_plan → dispatch-sent → 实际create/send → bind链。任务参数均明确 `model: gpt-5.6-terra`、`thinking: xhigh`，新建与唤醒一致。只把实际工具回执作为创建/续作证据；若可读运行配置显示不符则停止依赖操作并纠正目标任务配置，不能把提示词写了模型名当作切换成功。这里只指定生产编排任务模型；正式图像必须按 [网页版 ChatGPT 生图合同](../../ndc-character-scene-production/references/chatgpt-web-generation.md) 在受支持的可见浏览器中提交、下载和留存回执，禁止调用 Codex 图片生成工具、`imagegen`、图片 API、其它站点或其它生图后端。

## 完整场景计划

公共计划 `pipeline_kind: character_scene`，增加固定的 `model_policy`：

```json
{"reference":{"model":"gpt-6-astra","thinking":"medium"},"production":{"model":"gpt-5.6-terra","thinking":"xhigh"}}
```

每个unit是一个独立场景，`scope`在init时冻结当前需求的全部case和同时出场快照。例如：

```json
{"cases":[{"case_id":"sceneA-day","snapshots":[{"snapshot_id":"beat-01","actor_pose_ids":{"nurse":"nurse-stand-v1","patient":"patient-lie-v1"}}]}]}
```

使用原时间线和已确认需求填写完整范围；不能从一个已做好的删减ledger反推“全部需求”。探索点击前后、连续在场和其他必需状态不能漏掉。每个case的staging快照、演员→pose绑定必须与此范围一致。

正式生图按远近批次执行。正常路径中，每个网页结果回收后完成提取前视觉审核、保存原始下载与来源回执并冻结 SHA-256，然后继续本场剩余 `actor_pose_id`；冻结 scope 的全部必需角色／状态均有审核通过的生成结果或合法复用源后，再统一处理提取和合成。用整场生成进度清单逐项绑定 scene/revision、完整 scope、actor/pose、生成或复用来源、原始文件、网页回执、视觉结论、SHA-256 和当前状态，以便调度与防漏；清单是进度事实，不是提取硬门禁。

若网页生成、回收或浏览器传输处于真实等待／受阻，或存在其它有证据的具体调度理由，为避免空转可让已经就绪的角色提前进入 Remove Background、Select Subject、Alpha／蒙版、注册或其它不依赖缺项的工作。须在清单中记录例外原因、开始时间、已就绪／未就绪项、执行范围及恢复顺序；未就绪项继续保持待办，局部产物不得使整场完成或最终验收提前通过。旧任务已有部分提取结果正常保留和续用；不同完整场景仍可独立推进。参考白模与生图输入准备不受本调度原则限制。

authority.journal为原成本记录，upstream_jobs留空（上游通过原native ledger验收）；downstream_jobs包含所有本次formal actor/interaction job。已有标准journal直接续用。只有历史从未采用机器日志时，才以原生产ID和母任务ID建立一次标准日志，把真实已用数及原记录引用写入每个job.history/history_evidence；零次也须有实际新生产/该阶段未执行依据，不补造历史attempt或视觉PASS。模型6次、PS有限轮次按原节奏保留；明确授权的独立测试与旧测试只保留来源关系，不相互扣数。参考白模原3次生成与3轮PS记录继续保留在原记录中，不转成formal零次的新额度。

第二阶段每次 `attempt` 的实际提交快照须使用新记录 `tool: chatgpt_web_browser`、`operation: generate_image`，并保存 `browser: iab|chrome|edge`、ChatGPT conversation URL、submission manifest、提示词/重要度配置哈希及按序三引用的路径/哈希；历史 `chatgpt_web_iab` 记录继续兼容审计。网页收到消息即计一次 model attempt；pending/unknown 只回原对话核实，不能借切换浏览器重发或切换 Codex 生图。下载原图和 `ndc-chatgpt-web-generation-receipt/v2` 留在不可覆盖的提交包目录，回执路径作为 resolve evidence；网页预览与截图不作为生产源。

正式job的requirements含scene_id、production_id、phase:"formal"、pose_ids；limits通常为model:6和原ps限额（不大于3）。多角色调用对每个受影响job登记同一提交标识；全场工具调用按该标识去重，不把各角色计数相加成实际调用总数。未知结果先核实。

旧任务已有明确的一次有界额外授权时一并承接，不再次索要同一授权。payload.budget_exception_roles以原job ID映射授权文件role；文件须有source_kind:user_instruction、instruction、grant_id、source_roles，以及相同production_id、scene_id、job_id、phase:formal，base_limits和additional_limits（model、ps均为有限非负整数）。原journal的有效limits必须恰好等于base+additional；历史已用数照常继承，不能在每次交接时重加额度，也不能把某一角色或白模阶段的授权推广到全场正式角色。首次从旧人工日志导入时一次记录已授权的有效上限；已有机器journal的不可变上限不得靠改文件或重建journal绕过，需沿原记录支持的授权修订路径核实后再推进。

## 场景包

公共packet继续使用不可变文件引用；发布时core从plan注入unit_scope和model_policy，拒绝悄悄改动。payload字段：

| 字段 | 内容 |
|---|---|
| production_id | 原生产或用户明确独立测试ID |
| scene_role、scope_role | 原场景；LOCKED需求范围JSON，含scene_id、scope、requirement_basis |
| pre_ledger_role | 原 `ndc-scene-integration-production-ledger/v2` 的完整pre-generation ledger |
| depth_roles、identity_roles | 实际景深图及批准角色身份引用角色列表 |
| prompt_bundle_role | 实际已组装生图输入记录，含scene_id和poses映射；每pose含prompt、reference_roles、checked_by、findings |
| importance_profile_role、importance_gate_role | `ndc-visual-importance/v1` 与 `IMPORTANCE_TOLERANCE_GATE: PASS`，绑定本 scene/revision；新交接必需，旧包缺失时按全部 H0/H1 保守处理且不得使用 20%/30% 容差 |
| history_role | 原记录导入索引，含production_id、basis、source_roles、jobs；jobs的原history数值须与journal一致 |
| budget_jobs | 原formal job → 覆盖的pose ID数组，联合覆盖全部pose |
| authorization_role | 用户已有生产授权索引，含allowed、source_kind:user_instruction、scene_ids、scope:character_scene_production、instruction |

所有JSON索引都引用真实依据，不因填写字段而产生批准。原native production_gate在publish、claim、guard、result时重新运行，包含完整人物母层、联合白模、支撑/尺度/UI及真实白模视觉记录；旧PASS报告不得直接替代重验。成本journal只记录次数和变更，不再要求复制一套generic视觉accept。正式结果仍通过原post-generation ledger。

## 正式结果和参考返修

PASS结果的payload包括post_ledger_role、delivery_manifest_role、job_bindings。job_bindings按当前原jobs逐项调用 `integration_adapter.job_binding(job)`，拒收/要求变更后旧结果失效。返回files包括分配目录中的真实最终合成、native ledger、原图层/XY/重建清单及必要证据；post ledger的完整case/快照/pose范围和原场景仍须一致。沿用既有全部交付验证，不能把清单存在当重建成功。

delivery_manifest_role所指JSON的格式如下；快照必须完整覆盖冻结scope，layers按实际叠放顺序列出所有人物、影子及必要遮挡层。每个文件同时列入结果files，路径为分配输出目录内的绝对路径，sha256为实际文件哈希。脚本从原场景以原尺寸、整数XY、不缩放地逐层重建，并逐像素对比已审核合成；此技术通过不能代替native视觉审核。

```json
{"scene_id":"A","snapshots":[{"case_id":"A-day","snapshot_id":"s0","layers":[{"path":"D:/Codex/NDC/工作过程文件/example/actor.png","sha256":"实际SHA256","x":10,"y":20}],"composite":{"path":"D:/Codex/NDC/工作过程文件/example/final.png","sha256":"实际SHA256"}}]}
```

参考缺陷回传 `FAIL`，payload填reason、return_stage:reference；生成/提取缺陷为production，人工节点为manual。Astra从实际结果和差异判断影响范围，只有旧生产领取结束、在途命令已核实后才能修改该场景参考并发布下一连续revision。其他场景照常推进。Terra不得一边继续旧方案一边让Astra改它的白模。

同一人物身份/原场景或跨场景共同前置未冻结时不视为独立。固定只读身份源可共享；不同scene的工作PSD、输出和记录分开。上游按整场交接，下游整场接续；不能以任务重叠为由把同场角色A正式生成与角色B白模推导拆开。

测试用validation模式必须在scope记录明确validation_only:true；仅核对真实合同或明确的测试夹具，结果VALIDATION_COMPLETE，回执check_kind:contract_only、artistic_approval:false、generated:false并绑定pre_ledger_sha256和scope_sha256。测试既不填生产PASS，也不提交新图片。
