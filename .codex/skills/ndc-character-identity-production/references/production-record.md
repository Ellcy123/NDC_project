# 生产接续、对话任务预算和有效审核引用

先读[对话任务独立额度](task-budget.md)，2026-09-09新规则优先。

版本：ndc-art-production/v1，2026-09-08。适用于本 Skill 实际生产、人工交接和多阶段派生；简单提示词讨论不创建台账。道具已有 `ndc-prop-batch/v1` 时继续使用原道具日志，不再建立第二套计数。角色入景也继续使用自身台账。

## 一份任务记录，按真实依赖分工作项

在当前项目过程目录保留 `production-plan.json` 和追加式 `production-journal.jsonl`。计划是执行锚点，执行者核实后直接推进；不是用户逐项批准表。先识别用途和资产ID，再按当前项目来源规则检索；先记录存在性与适用性，不扩成整批旧图返修。资产库地址与机器检索顺序不写进此协议。

一个job代表一个可独立验收的产物/原生母版/输出规格，`asset_key` 包含稳定身份、用途和状态/视图。`job_id` 不以临时文件名或尝试轮次命名。不同需求确实存在上游依赖时才填 `depends_on`。例如母图→big、母图→small；两个规格互不依赖。共同母图变化使两个规格失效，只改big裁切不使small失效。

审核输入包含实际身份源、风格源、场景、规格等必要文件的路径/哈希；剧情或任务事实放入 `requirements`。不可把“正面”“左侧面”“UI头像”三个用途都算成找到同一资产。纯历史复用不补造旧生成、旧母图或旧审核：只对本次身份、来源、可读性、规格及复制的实际核对留下记录。

计划格式如下。示例是一个技术状态模板，坐标/身份/额度由当前任务填写；`limits` 必须遵守主Skill已有预算。不得照抄示例去批准资产。

```json
{
  "schema": "ndc-art-production-plan/v1",
  "task_id": "current-art-task",
  "jobs": [{
    "job_id": "actor-ui-master",
    "asset_key": "character:actor-id:ui-master:neutral",
    "source_decision": {"mode": "generate", "evidence": "本次实际查验结果与缺项"},
    "requirements": {"identity_id": "actor-id", "purpose": "ui-master", "state": "neutral"},
    "inputs": [{"role": "approved_identity", "path": "identity.png", "sha256": "实际SHA-256"}],
    "depends_on": [],
    "limits": {"model": 3},
    "history": {},
    "required_criteria": ["identity", "style", "composition"],
    "output_roles": ["ui_master"]
  }]
}
```

`source_decision.mode` 为 `reuse/derive/generate/manual_input/repair`；`limits` 可含 `model/ps/technical`，零表示该种操作不可执行。人工来源接收使用manual_input，不能启动自动补画。初始化前的资产历史填入 `history`，非零时提供带path/sha256的 `history_evidence`；默认只追溯，不扣减当前对话。只有 `history_task_id` 明确等于当前真实对话 ID 的次数才计入当前额度。共享原日志按对话分别计数，新对话完整新额度，无须额外询问。

```text
python -B scripts/art_workflow_state.py init --plan <production-plan.json> --journal <production-journal.jsonl>
python -B scripts/art_workflow_state.py status --journal <production-journal.jsonl>
```

初始化拒绝覆盖旧日志；同一任务目录用 `.ndc-art-task-registry.json` 绑定task_id与权威日志，换日志文件名不能清零。跨目录搬迁须连同原日志/注册和证据保留，脚本不声称在全磁盘检测另起任务。同一计划拒绝重复语义asset_key和依赖环。日志每条记录连上前一条哈希。仅短时锁定记录写入；锁冲突不删除其他写入者的锁。不把这个文件锁当成Photoshop文档锁。

## 先登记实际提交，再操作工具

按主Skill冻结额度，含首次，跨阶段/回退/落点/区域共用原工作项额度；一个模型调用返回多候选如何计数，依主Skill既有规定。开始前把实际tool、operation及arguments保存为提交JSON；提示词必须是最终原文，参考路径/次序和相应来源哈希一并留在arguments中。PS按一轮完整修复计划计数，单条图层命令不单算一轮。不要把凭据写入提交快照。

```text
python -B scripts/art_workflow_state.py attempt --journal <journal> --job <id> --kind model --submission-id <稳定本次提交ID> --submission <实际提交.json>
python -B scripts/art_workflow_state.py resolve --journal <journal> --job <id> --submission-id <同ID> --result produced --evidence <实际jobID及保存结果的说明>
```

`produced` 只表示产生了候选/完成了这一处理轮次，不表示视觉通过。`unknown` 表示提交可能成功但结果不明，仍占额度并阻断重复提交；先查服务端job和已保存文件，再用同ID补记结果。只有确证没有生成/没有执行时才能填 `no_output`，释放该次艺术额度并累计工具错误。不得将差图标成no_output。连续无结果错误默认两次后先修复能力连接；实际恢复并有证据时用 `recover-tool --reason ...`，历史事件和总次数仍保留。主Skill已有更严格断联规则时继续遵守。

通用风格全身使用网页版 ChatGPT 时，`submission` 直接引用不可覆盖角色提交包的 manifest，新提交固定记录 `tool: chatgpt_web_browser`、`operation: generate_image`、`browser: iab|chrome|edge`、专用对话 URL、character/revision、mode/branch、全部上传项及提示词哈希；历史 `chatgpt_web_iab` 记录继续兼容审计。网页已收到消息即算真实 attempt；pending/unknown 必须先回原对话核实，不能刷新后重发或换生图后端。`resolve` 的网页来源证据必须包含 `CHATGPT_WEB_CHARACTER_GENERATION_GATE: PASS` 回执路径，但该门禁不代替艺术验收。

达到额度后保留候选和失败原因，继续可独立执行的其他项。不要为凑满数字追加无意义操作，也不把候选标成正式。新对话自动拥有完整新额度，保留旧任务来源关系即可，不要求用户答复；同一对话不通过 `revise` 修改额度。

## 人工交接与接续

`wait --journal ... --job ... --reason WAITING_FOR_MANUAL_PORTRAIT_COMPLETION` 标记明确的人工肖像补全交接。人工接手是预期步骤，不算工具故障或模型重试；同组其他独立准备可继续。

人工返回后先按主Skill检查身份、完整范围、适用裁切和文件质量，再保存前/后来源与说明；用 `revise --changes <changes.json>` 接入新的inputs并失效相关下游，然后 `resume --reason <实际接收检查说明>` 继续。必要的当前来源审核仍执行，不能仅凭resume生成通过状态。

肖像肩胸补全与表情生产后的背景/Alpha手工处理是两种不同交接，保持各自责任状态及回执，不把一份返回文件自动当成另一阶段完成。禁止把人工完成历史写成Codex补全过程；表情旧回执中的 `PORTRAIT_COMPLETION_USED=false` 继续表示该Skill未执行补全。

人工会原地覆盖的文件必须是工作交接副本，不能同时充当已接受父job的不可变输出。表情示例：永久保留E4已通过原生艺术源；E5交接PNG复制到原定人工处理目录并保存交接前哈希清单；E6的manual_input job依赖不可变E4源，输入为人工回传PNG及交接清单，不依赖E5可变副本的旧PASS。原目录回传方式不变。肩部适配同理保留原肖像，对工作副本接收新输入，避免人工完成后旧父hash过期让后续无法恢复。

## 冻结检查上下文，再引用真实审核

接受候选前准备输出引用JSON数组（每项包含role、path、sha256），其role必须精确覆盖计划中的output_roles：

```text
python -B scripts/art_workflow_state.py prepare-review --journal <journal> --job <id> --outputs <outputs.json> --out <new-review-request.json>
```

该命令只冻结当前需求、来源、父依赖、输出及检查范围，返回 `REVIEW_REQUIRED`。准备并实际查看主Skill要求的全图与原像素/200%局部；在原有 `ndc-stage-visual-self-check/v1` 记录中填写实际观察和结论，并添加 `workflow_context_sha256`，值来自本次请求。views引用带实际sha256。记录所覆盖输出的role放在outputs项目中或单输出记录的顶层role；inputs覆盖当前来源和父产物。

这只是原有阶段自检的上下文绑定扩展，不改表情、UI或其他专门receipt schema。不要复制旧PASS并自动换成新上下文哈希。来源、要求、父依赖或拒收事件变化后必须真实复核受影响项。没有执行的创作环节不造记录，快速淘汰候选保留拒收原因，未检查项不写PASS。

```text
python -B scripts/art_workflow_state.py accept --journal <journal> --job <id> --request <new-review-request.json> --record <真实阶段记录.json> --stage-validator <项目原有阶段视觉验证器.py>
```

多个输出可以传多次 `--record`。此命令调用现有阶段验证器、检查每个输出和适用项、回读实际源/输出/视图哈希，并核对当时冻结的要求及父依赖。主Skill专门的身份、纹理、坐标、Alpha、构图和最终交付验证器仍须执行；通用日志不是它们的替代。脚本不看图，不生成艺术PASS，也不作用户批准。

同一图的连续技术操作可组成一个有明确输入/输出、已覆盖全部新增风险的处理阶段。同任务须完成当前图保存、技术/真实视觉检查并核对当前hash，未审完不能推进下一张或批量补审。PASS可推进相应依赖；FAIL已明确缺陷且预算耗尽或用户指示封存时，保留候选、失败记录和原次数，仅继续独立资产，失败后代仍阻断。本机 Photoshop 同一时刻仅由一个任务操作：安全保存可恢复文件和固定审阅快照、无在途或结果未知命令后，可挂起释放给其他独立任务；原图未通过状态、依赖阻断及累计预算保留。恢复时重新核对当前文档、源版本及hash，不接着偶然的活动文档操作。不能合并跨越必要身份确认或不可逆依赖的操作；已经查看的同一全图/局部材料由风格、细节、纹理检查共享。

## 拒收、修改、原样复制和完成检查

- 用户否定某产物时立即 `reject --reason <具体否定>`，它及依赖项失效，事件保留。不能继续沿用同字节旧图的PASS。
- 已有job修改要求或输入时用 `revise --changes <JSON>`；仅允许requirements/inputs变化，不改变身份键、依赖和额度。需要真正新增任务范围时另写带旧记录来源的扩围计划，原日志保留。
- 重复accept同一请求/记录、revise写回未变内容均不追加新的失效事件。重新引用等价父审核不会使不变子产物重做；父要求、输入、输出或拒收revision改变时仍递归失效。
- 只复制不变字节时，先检查原job的当前证据，再调用 `verify-copy --journal ... --job ... --copies <role/path/sha256数组.json> --out <新复制核验.json>`；它只证明复制与当前已审核来源一致，不重审身份或风格。最终包装引用原审核与复制核验；以后转交前重新运行，不把旧复制报告当成永不过期的批准。
- `check --journal ...` 要求本计划每个声明输出具有当前有效的审核绑定，缺项/拒收/源变更返回非零。发布明确子集时可重复传 `--job <id>` 只核对该范围及其依赖；返回仍列出其他未完成项和 `whole_plan_current:false`，不能把子集通过说成全批次完成。
- 废弃尝试保留失败记录，不进入当前接受依赖链的“全部PASS”条件。旧图、人工作业、候选和正式图分开说明，不删除失败历史来让检查通过。

生产时只维护这份短记录和实际必要证据；稳定后一次整理交付清单。时间记录把工具等待、PS处理、真实审阅、报告整理与人工等待分开，不承诺统一提速百分比。仅在用户已启用重叠推进且具体生产范围已有授权时，按 [阶段交接](../../ndc-art-stage-pipeline/SKILL.md) 将单角色UI母图→裁切整备、完整独立场景提示→MJ交给一个可复用下游目标任务；首个合格单位即可派发，上游继续独立单位。创建或复用承载对话后，下游必须先真实调用 `get_goal`，无未完成目标时调用 `create_goal` 建立覆盖完整已授权阶段批次的持续目标；已有同批目标则接续，不能只把“目标”写进提示词或把 `create_thread` 成功当作目标已启用。新建承载任务仍须已有明确授权，传递原journal/job及剩余次数，不拆同场角色或绕过人工节点；没有READY时结束当前回合，之后由活动协调任务唤醒同一目标任务，不后台生图或新增人工审批。其他流程不因此自动开生产任务；Photoshop 改用原生 MCP，同一时刻仅由一个任务操作，不启动旧 PS broker 或 watchdog。
