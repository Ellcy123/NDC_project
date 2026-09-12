---
name: ndc-art-stage-pipeline
description: 在已授权的NDC批次中，让UI肖像母图与双规格裁切、独立场景提示词与MJ原图生产、人物入景整场参考与正式资产生产跨任务重叠推进。负责冻结交接、唯一领取、复用下游目标任务、结果回收和人工节点暂停；不设计资产，不增加出图权限；额度按真实对话任务独立计算。
metadata:
  category: art/workflow/stage-handoff
---

# NDC 分阶段重叠推进

## Photoshop MCP 强制前置

本 Skill 或其实际下游在第一次调用 Photoshop MCP 前，必须完整读取当前环境的《PS MCP 操作参考手册》：维护工作区从项目根解析 `PS_MCP_操作参考手册.md`，工程镜像从仓库根解析 `production/art_pipeline/PS_MCP_操作参考手册.md`。在作业记录中保存实际手册路径、版本、SHA-256 和当前会话能力快照；两处均不存在或哈希不一致时不得以历史记忆继续操作。手册负责通用效率、抠图、Alpha、路径、单引擎、超时回退和视觉/技术验收；本 Skill 继续负责阶段权限、额度、交接和内容门禁。实时目录只允许执行 supported 能力，手册本身不增加操作授权。

本 Skill 自带的 `scripts/`、`references/` 等支持文件一律从当前实际 `SKILL.md` 目录相对解析并随 Skill 提交。跨设备执行从策划仓库根使用 `python -B scripts/art_pipeline/ndc_art.py run ndc-art-stage-pipeline <脚本名> -- <参数>`；不得依赖维护机 `.agents` 路径、用户名或固定盘符。缺少支持文件视为部署失败，不回退搜索其他电脑路径。

重叠任务必须运行在持续目标模式（2026-09-09 用户明确要求）。新建和复用派发都须携带明确的目标创建授权与完整阶段目标；目标任务先 `get_goal`，无未完成目标时实际 `create_goal`，已有同批目标则接续，且回传一次真实状态。`create_thread` 成功、提示词含“目标”或一轮对话结束均不能证明目标已启用/完成。不得依靠上游常驻监管维持生产。具体启动与核验见[任务派发](references/task-dispatch.md)。

人物入景以确定并交接整场白模为上游完成边界；下游 Terra/xhigh 全权负责正式生产。每个 scene/revision 使用一个**逻辑场景工作区**，不强制独占物理 OS 窗口；一次真实 canary 后，不同生成单元可在专用 ChatGPT 对话中并发，但每次仍重传三份独立引用和完整提示词。READY/revision、WIP、人体覆盖、时间盒与最低产出统一遵循[效率与状态合同](../ndc-character-scene-integration/references/efficiency-and-state-contract.md)。上游交接后继续其他场景，不轮询生产；下游完成当前场景后只调用一次 `claim-next`，无 READY 单元即结束本轮，等待新 READY 事件唤醒。

执行前读[对话任务独立额度](references/task-budget.md)：新对话完整新额度，其他对话的资产历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于旧预算说明。

适用于用户要求边准备边生产、阶段交接后开任务同步推进，或续作这些已启用流水的批次。一个角色或一个完整独立场景达到交接条件就发布；上游继续其他单位，下游执行已发布单位，不按全批完成百分比放行。

- UI：原 `ndc-generate-ui-portraits` 的 U0/U1 由上游负责，U2/U3 双规格裁切及成对审核由下游负责。[UI交接](references/ui-pipeline.md)规定身份、人工补肩、母图和历史规格复用边界。
- 场景：原 `ndc-scene-to-mj-prompt` 负责一个场景的完整 v4 提示包；`ndc-midjourney-operator` 接手该场景全部必需视角。[场景交接](references/scene-pipeline.md)规定共享空间事实、精确提示、出图授权及原生交付门槛。

实际启用前读 [发布与接续协议](references/pipeline-protocol.md)；派发时再读 [任务派发](references/task-dispatch.md)。维护Skill、准备提示词或验证机制本身不授权新艺术生成。只有用户已明确授权创建下游承载对话时才调用 `create_thread`（人物入景此分工已有本轮明确授权），已有授权不逐包重复询问；承载对话随后必须真实 `get_goal` / `create_goal` 成为下游目标任务，已绑定的同批目标任务优先复用。明确已有出图授权后，MJ 才能实际提交。

每个流水批次默认一个上游协调任务、一个下游阶段目标任务。同场景多视角共同归这个下游；人物入景也按完整场景交接，使用 [入景专属协议](references/integration-pipeline.md)：Astra/medium产出所有参考，Terra/xhigh统一编排所有同场角色并在受支持的内置或外置浏览器中通过网页版 ChatGPT 生成正式像素；不能按角色拆分 Codex 任务，但必须允许同一场景窗口内多个已登记 ChatGPT 对话并发生成不同角色，或同一角色的不同姿势。默认先把同场角色生成完再统一提取；有记录的真实等待／阻塞或其它具体调度理由时，可错峰处理已就绪角色，但完整总清单及未就绪项必须保留，不能删除缺项来提高完成率或把局部工作冒充整场完成。

人物入景下游建立逻辑场景工作区交接记录时，以 `assets/integration-scene-window-handoff.template.json` 为字段模板；模板只提供字段、健康／canary、WIP、状态与去重政策，不替代冻结 packet、实际浏览器句柄、对话 URL、production Skill 的状态管理脚本或真实回执。

1. 从完整生产计划和原始累计日志建立 `pipeline.sqlite`。单位绑定稳定身份、原journal及上下游job，不创建第二套尝试预算。
2. 每当一个单位完成其专门上游检查，立即生成并 `publish` 不可变版本交接包；不等待其他单位。仅绑定相关job及其来源，不能哈希整个不断追加的journal使无关进展触发返工。
3. 活动协调者立即 `reserve-dispatch`，准备具体工具参数，先 `dispatch-sent` 再执行一次 create/send。收到真实任务ID后 `bind-dispatch`。应用回执未知或只有setup ID时先核实，不能重发创建。
4. 下游取得唯一 `claim` 后，按原Skill生产；每个有成本或写入的安全段前 `guard`，仍通过原journal登记attempt及结果。跨任务保留资产语义ID和原journal，按实际下游对话ID自动独立计数，旧资产历史不扣减新任务额度；PS若实际使用，通过原生 MCP；本机同一时刻仅由一个任务操作，保存检查点并核对无在途命令后才交棒。
5. 用 `result` 回收实际文件、审核或明确失败／人工停止记录。下游只调用一次 `claim-next`；没有 READY 单位时结束当前轮，由上游在新 READY revision 发布后唤醒同一任务。不得 heartbeat 轮询无变化状态。

人工补肩、来源身份选择、用户明确保留的确认节点或既有出图授权缺口只停止相关分支。人工返回须接入真实来源和原日志、重核相关条件再恢复；不得由流水脚本自动补肩、替用户批准或把等待算作模型重试。

输入发生实质变化时追加新版本并停止旧版本后继。旧任务的在途或未知操作先核实，旧结果留在隔离目录；不能因超时自动把同一资产交给第二位执行者。最终完成仍要完整单位范围及各自原有技术、视觉、身份、纹理和交付门槛都通过。

本Skill由活动Codex任务在生产边界驱动，支持真实阶段重叠；不是会话结束后的无人值守调度服务。报告须区分生产PASS、合成协议验证、真实生成和实测耗时，不能用测试夹具证明艺术质量或承诺提速百分比。当前任务明确选为交付目标的图片（包括明确用于交付的参考图）须按共享[效率与状态合同](../ndc-character-scene-integration/references/efficiency-and-state-contract.md)登记到 `{DELIVERY_ROOT}` 的 `交付候选` 隔离层；审计和制作进度先读取候选清单，但候选覆盖、复核结果和正式就绪必须分列，候选不得触发工程同步。
