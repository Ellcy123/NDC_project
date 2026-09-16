# 信息模型与来源

## 真源顺序

先读取当前项目规则和 `ndc_art.py paths`。针对一个已建立五阶段批次的章节，默认取证顺序为：

1. 当前活动范围修订、`content_archive.json`、`batch.json` 与场景放行索引；
2. 当前 SceneConfig、ItemStaticData 和对应剧情／玩法原文；
3. 当前批准资产索引、交付候选索引、审核绑定与节点清单；
4. 旧 archive、旧表、历史资产和人工说明，只用于来源追溯、差异解释或恢复候选。

来源顺序不是“最后修改时间优先”。同一事实发生冲突时，按项目规则确定权威；无法确定就把该事实标为 `unresolved`，记录互相冲突的来源和影响的产物，不选择看起来更合理的一项。

每个来源记录：

- `source_id`：本清单内唯一稳定编号；
- `kind`：content archive、batch、route table、scene config、item static data、story design、asset index 或 other；
- `path` 与 `sha256`；
- `authority`：`current`、`historical` 或 `supplemental`；
- `note`：该来源支持哪些判断，不把整份文件泛化为所有事实依据。

## 完整范围

文档范围同时记录：

- 章节与 revision；
- 全部 Item ID、场景 ID、附属小游戏／案件板／演出项；
- 活动生产范围哈希；
- 排除项及原因；
- 当前需求全集与活动执行子集的差异。

“不给美术制作”“不进 ItemStaticData”“仅历史保存”不是删除理由。它们必须留在排除／附属表，防止下一章复用时重新误算为普通道具。

## 每个道具记录

每项至少包含：

- 身份：Item ID、名称、场景、状态、取得事件；
- 两条分类轴：`semantic_class` 与 `acquisition_route`；
- 内容合同：A 类硬事实、B 类允许差异、C 类美术自由；
- 产物矩阵：角色、规格、是否必需、当前状态、人工动作、来源；
- 现有资产：精确路径、SHA-256、审核状态和证据；
- 依赖：父物、容器、同物状态、照片内容、共享事实、场景父图；
- 人工任务：输入、操作、产物、验收、阻塞、回流；
- 未决问题与影响范围。

## 状态不可混用

以下层级必须分列：

- `MISSING`：必需角色没有当前文件；
- `CANDIDATE`：已选目标，尚未完成有效复核；
- `PROVISIONAL`：可供人工判断，但存在已知缺陷或不确定性；
- `EFFECTIVE_PASS`：当前字节、事实、父图、合同和审核绑定仍有效；
- `REJECTED`：当前版本已有失败结论；
- `UNKNOWN`：尚未完成所需核对。

文件存在、技术检查通过、候选登记或节点可浏览均不能自动写成 `EFFECTIVE_PASS`。历史件只进入来源与人工对比说明，不抵扣当前需求。
