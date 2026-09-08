# NDC 道具五阶段共用批次协议

2026-09-08 用户确认实施。五阶段为需求、母版、场景与菜单、热区、交付。各入口及本协议决定新流程；迁移的专业细则保留物理、图像和技术要求。旧文中逐步重复审核、同位换址重开额度等解释由本协议明确替代。

## 核心规则

1. 来源和权限优先：项目来源检索顺序、只读输入、PS MCP通道和逐图审核保留。PS占用、保存交接及检查调度遵循共享PS协议：同任务WAITING_REVIEW时不能开始下一资产；安全交接后其他任务可使用PS。完整真实审核FAIL后，预算耗尽或用户明确封存候选时，可记录封存并继续独立资产；失败资产的后继依赖及发布仍阻塞。工作文件放项目工作过程目录，正式图片仅进入最终交付；未授权不改Unity。
2. 一份content_archive.json维护事实，一份batch.json维护范围／依赖／进度。记录精确来源，不把档案当作覆盖剧情事实的权威。
3. A必须准确；B在生成前列明允许差异；C仅在画风范围内自由。技术、身份、结构、像素保护和用户拒收不参加百分比容错。可读文字仍禁止PS／代码后补。
4. 第二阶段到第三阶段按场景及完整关联前置放行：某场景的全部道具、同物状态、容器内容及物理关联所需母版／普通Big、真实外部父图均有效通过，照片内容和跨物品引用事实及来源已锁定，且没有未解决关联，即可制作该场景。只引用已确认身份／日期等事实时，不附加生产该引用对象其余母版的要求。无关场景的未完成图不阻塞它。只放松这一个交接门槛；第三阶段全部非Icon必需图完成后统一制作Icon，全部场景／菜单定稿冻结后统一提取热区。Icon包括其专用高分辨率来源，不在第二阶段抢先生产。环境痕迹不强行生成独立物件。具体索引和迁移见[场景放行合同](scene-release-contract.md)；无索引的旧批次保持全批次阶段2门槛。
5. 同一母版状态最多3批×2张，首批计入；每个入景／菜单作业最多3张，首张计入。必要独立Icon或场景相关Big生成沿用原三次上限，记为derived作业。合格即停止。换阶段、位置、文件名或最终复查不能清零。
6. 语义正确的轻微框幅／变换先进行一次可用PS修正。该分支不赠送新生成额度；同一缺陷不能无限PS微调，未能修正则使用剩余额度或记录人工阻塞。
7. 达上限后的最佳版本仍按实际质量分为通过或候选。关键失败下游继承候选，只可用于不受影响的布局试验；不进入正式热区／归档。已允许的B/C差异不反复报风险。
8. 每阶段只审核新增或改变的风险；每个当前产物有一份包含相关内容、风格、边缘等结论的真实视觉记录。旧审核可严格复用；禁止技术检查自动给艺术PASS。

## 执行优先级与清单授权

全量续作先补全缺失，再复检已有问题资产，最后按复检结论修复或重制。五阶段是生产依赖顺序；补缺／复检／重制是工作优先级，不能用“先复用”把整批旧图复检或已知返修提前到可执行的缺失项之前。

- 第一阶段只做足以识别缺口、防止重复生成的来源、状态、角色与既有审核索引核对；不先逐图重新视觉审完所有旧资产。缺失按交付角色记录，例如缺Map不等于Big缺失，待审和拒收也不等于缺失。
- 每阶段先处理其可执行缺失项。缺失项引用的旧母版／承载体，允许只核对该依赖；若它确有缺陷，先完成其他独立缺失项，再以明确的依赖阻塞理由修复必要前置。不得借此前置例外展开全批旧图复检。
- 按场景放行不等于逐道具抢跑：尚不可执行的缺失项记录本场景全部关联中缺哪个前置；不能仅按scene_id过滤母版，也不能用完成百分比放行。达到当前场景门槛只复检和修复必要前置；其他独立场景可以继续。Icon、第四阶段和最终交付仍用整批门槛。缺失项本轮产生的失败应在原job额度内闭环，不能把它误当作禁止处理的旧资产返修。
- 清单是执行锚点，不是用户审批关卡。已授权生产就自行核对并继续；已授权美术拟定的虚构字段记录为统一设定并传播到相关道具，不重复询问。不能从旧任务迁移“仅统计／暂停”状态来覆盖用户最新恢复生产指令，也不能忽略用户当前仍生效的暂停／仅统计。
- 多任务协作时在共享工作记录中标明负责场景、当前作业和PS占用者，优先未被其他任务开始的场景。同一场景同一角色不重复生产；PS使用前核对占用，保存、检查并释放后才交接，不关闭其他任务的文档。占用不明时先做不使用PS的独立工作。

batch可记录execution_priority（active_pass、缺失清单、依赖例外及下一步）。这是调度证据，不修改已锁定scope/jobs，不给任何失败图免检。

## 进度报告

锁定required_artifacts为图像总进度分母，只计当前依赖和审核有效的PASS；原始source_reference、提示、候选、过程遮罩和重复副本不计完成。报告“有效PASS数／必需角色总数＝百分比”，同时报各场景实际阶段、场景放行阻塞、阶段分子／分母及执行轮次。新索引下progress返回stage_dispatch=per_scene；兼容字段current_stage是最早尚未完成的实际阶段，declared_current_stage仅保留批次原声明值，均不能代替scene-readiness或attempt门槛。母版通过不等于整项或正式交付完成。

首次补缺前按角色记录缺失基线；补缺完成数只统计该基线里新增且通过的角色，旧图复用和返修不得混算。用户要求阶段进度时，在开始、每批完成、阶段切换、阻塞变化时主动报告总百分比与阶段百分比；无新增PASS就如实说明进度未增加。变更分母须有真实需求变更依据并保留前后数值，不能为提高百分比缩小范围。

## 数据字段

批次JSON相对路径以batch.json目录解析。推荐把所有绝对来源复制成可恢复输入后引用。以下是字段形状，不是现成通过记录；不要把示例的状态改成PASS而不实际审阅。

```json
{
  "schema": "ndc-prop-batch/v1",
  "batch_id": "UnitX_batch_YYYYMMDD",
  "objective": "用户当前的完整交付目标",
  "current_stage": 1,
  "next_action": "核对关键事实",
  "requirements_locked": false,
  "content_archive": "content_archive.json",
  "attempt_log": "attempts.jsonl",
  "scope": {
    "item_ids": ["item1"], "scene_ids": ["scene1"],
    "required_artifacts": ["item1.master", "scene1.final", "item1.map", "item1.big"]
  },
  "jobs": {
    "item1|master||closed": {"item_id":"item1","kind":"master","scene_id":"","state":"closed"},
    "item1|scene|scene1|closed": {"item_id":"item1","kind":"scene","scene_id":"scene1","state":"closed"}
  },
  "artifacts": {
    "item1.master": {
      "item_ids":["item1"], "stage":2, "role":"semantic_master", "status":"PENDING", "rejected":false,
      "job_id":"item1|master||closed", "parents":[], "fact_refs":["item1.identity"],
      "acceptance_contract":{"content_contract":"身份和所有A字段正确","style_identity":"既定画风结构"}
    },
    "scene1.final": {
      "item_ids":["item1"], "stage":3, "role":"scene_preview", "scene_id":"scene1",
      "status":"PENDING", "rejected":false, "frozen":false,
      "parents":["item1.master"], "fact_refs":["item1.identity"],
      "acceptance_contract":{"placement":"比例承托遮挡风格及区域外像素保护"}
    },
    "item1.map": {
      "item_ids":["item1"], "stage":4, "role":"scene_pickup_map", "status":"PENDING", "rejected":false,
      "parents":["scene1.final"], "fact_refs":["item1.identity"],
      "acceptance_contract":{"semantic_target_completeness":"完整物体和阴影","parent_overlay_semantic_alignment":"父图对应"}
    },
    "item1.big": {
      "item_ids":["item1"], "stage":2, "role":"ordinary_big", "status":"PENDING", "rejected":false,
      "parents":["item1.master"], "fact_refs":["item1.identity"],
      "acceptance_contract":{"runtime_size":"符合选定Big规格","content_contract":"关键内容保持"}
    }
  }
}
```

content_archive.json使用schema=ndc-prop-content/v1，items为编号字典；每项包含source_references数组和requirements字典。每个事实包含level(A/B/C)、value、source；B还必须有allowed_difference。事实键可为identity、age、date等，fact_refs按item.field引用。母版的事实清单必须覆盖其负责物品的全部A字段；派生图绑定实际依赖的内容，不能为了复用省略关键字段。

每项还必须有inventory：keywords非空数组、checked_roots非空数组（每行root、result=found/no_match）、found布尔值、disposition为reuse/complete_missing/repair/regenerate/new/blocked之一、reason为具体判断。命中时selected必须含path和sha256，并列明批准／拒收依据；未找到时不得选reuse。顺序以项目来源规则为准；命中后checked_roots不得继续查后续根目录另选来源。细化到实际状态／图像角色，记录found不自动获得usable=true。

artifact通过时补齐path、sha256、review；所有参考图、源图和母版按实际parents传递，原始场景可作为额外source_reference角色加入artifacts（不要求生成）。本批次所有必需图像都要进入required_artifacts，包括逐菜单scene_menu_preview和菜单container_type7；不能仅列容易完成的子集。环境Big采用environment_big，无Icon；自动授予按需要保留场景状态而不新增Map。

published_path仅在发布时填正式PNG绝对路径。acceptance_contract是检查项名称→本资产具体要求；不是自动PASS。审核记录中的criteria须覆盖这些名称及该角色原有的专用必需项。

## 工具用法

脚本位于同级 ndc-prop-delivery-review/scripts/workflow_state.py。把命令路径转换成实际绝对路径。

```text
python workflow_state.py init --batch <batch.json>
python workflow_state.py validate --batch <batch.json> --stage 2
python workflow_state.py attempt --batch <batch.json> --job "item1|master||closed" --prompt <actual_prompt.txt> --reason "首批或本次具体修正"
python workflow_state.py binding --batch <batch.json> --artifact item1.master
python workflow_state.py affected --batch <batch.json> --artifact item1.master
python workflow_state.py progress --batch <batch.json>
python workflow_state.py resolve-history --batch <batch.json> --job "item1|master||closed" --evidence <history_resolution.json>
python workflow_state.py migrate-scene-release --batch <batch.json> --index <reviewed_scene_index.json> --reason "已核对全范围场景成员及关联来源"
python workflow_state.py scene-readiness --batch <batch.json> --scene scene1
python workflow_state.py validate --batch <batch.json> --stage 3 --scene scene1
```

init锁定scope/jobs并创建只追加、哈希串联的尝试日志。attempt在每次真实生图前预留一个名额；下一批／下一次重试须修改实际提示内容，失败没有输出的预留也保守计入，不自动退额度。补写结果可以记录在各候选审核中，不修改已写的attempt事件。日志与batch头不一致时先检查崩溃写入或截断；禁止删除日志再init。

derived作业按绑定产物的生产阶段执行门槛：无场景依赖的普通派生图在阶段2，场景相关Big与所有Icon在阶段3。同一job不混绑不同生产阶段；其实际父图必须通过。第三阶段非Icon必需图先完成，再制作Icon（含专用Icon母版和确定性导出），不能从未定的线索或候选Big提前衍生。Icon不依赖第四阶段热区PNG，避免循环。已合格Icon保留字节和有效审核，仅更新生产阶段归属；不重置job/次数。progress为只读核验，不写PASS；可在batch.initial_missing_artifacts保存首次补缺基线。

resolve-history只适用于init中明确标记UNKNOWN_CONSERVATIVE_EXHAUSTION、actual_count=null且按上限占用、尚未追加真实attempt的job，只能更正一次。证据JSON须含schema=ndc-prop-history-resolution/v1、batch_id、job_id、confirmed_count（0至该job上限）、determination（new或known_historical）、reviewer、reason和sources（非空的path／sha256数组）。执行者先实际查阅这些来源，证明同一job未开始或确切历史次数，不能用文件缺失或自写结论代替来源。命令保存不可覆盖的证据快照并追加日志事件，后续按已确认次数累计；技术校验不代替历史事实判断。

stage 2校验需求已锁；有场景索引时stage 3加--scene核验完整关联前置，attempt按job和产物归属自动执行同一门槛；stage 3不加--scene仍保留全局核验。stage 4检查整批结果及全部场景／菜单已冻结；stage 5检查所有必需结果及其依赖。--scene不能用于stage 4或5放宽范围。不得缩小batch.scope/jobs来获得场景放行，不把原场景中尚待制作的菜单误列为入景前置。仅修复单一热区的任务可以在第一阶段明确限定为单资产批次，并纳入其既有场景父图；不能把一个已锁定全量任务偷换为该范围。

## 续跑、历史接入和失效传播

每轮先读objective、next_action、progress里的场景实际阶段、当前拒收和有效产物，核验对应文件；current_stage不再表示所有场景只能一起处在一个阶段。无索引旧批次仍遵循原全局顺序。按[迁移命令](scene-release-contract.md#接入与续跑)追加场景索引时保留同一batch、scope、jobs、初始历史和全部真实尝试，不再init。不反复加载全套Skill或重扫全部历史。记录integration_status以区别图片交付与程序接入。

旧任务第一次接入时，在批次内补齐范围、来源和当前通过证据。逐job区分：有来源依据的未开始新作业计0；已发生的生成按可靠记录累计；确有历史但次数无法恢复才按该job上限保守占用。仅仅没有交付文件、没有状态字段或新拆分角色没有日志，不能证明“已生成且用尽”。也不能仅凭文件缺失断言历史为0。记录检索范围、历史任务标识和判断依据；未知占用必须明确标成占用，不能报告成实际生成次数。

已有次数写入job.legacy_attempts和job.legacy_evidence，init后不直接修改。若保守占用后来有可靠历史证据，可用resolve-history追加一次审计更正，保留初始job、原日志、证据快照和本批真实调用；不重建批次或删除尝试。无可靠证据仍保持占用，继续其他独立缺失项。已通过资产只补足当前复用实际缺失的证据，不重画。

用户否定时立即令受影响artifact.rejected=true并记录理由／日期；通过新审核后才恢复。修改内容档案事实会使绑定该事实的记录失效；场景索引还绑定关联物品的事实、来源、前置审核及图像版本，因此没有直接image parents边的相关场景也会失效，后代随之失效。无关场景、事实和资产不连带撤回。修改父图同理。affected包含实际图像后代和关联前置所影响的场景产物，只给出需复核列表，不自动修改图片或伪造新审核。

## 专业边界

道具画面第一人称、无角色和人体部位，不因策划描写手持、递交、开柜就新增演员、手或倒影。原照片已经要求的人物影像按该照片内容合同处理，不据此引入场景角色。所有容器打开态（包括既有资产、自动AVG和小保险箱）都使用二级菜单；自动授予仍保留原授予语义。Type6和子道具Map沿原图像素提取；Type7直接生图后加12px边框；普通Big、环境Big、620px线索照片与130pxIcon的不同规格继续有效。
