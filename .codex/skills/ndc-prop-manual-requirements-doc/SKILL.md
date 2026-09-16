---
name: ndc-prop-manual-requirements-doc
description: 将 NDC 某章节的全量道具、照片线索、环境叙事物和附属交互需求整理为可供人工直接执行的详细清单与 DOCX，并保留来源、取得路线、产物角色、缺口、依赖和验收边界。用于“人工处理清单”“道具需求完整文档”“其他章节复用同类文档”；不生图、不修图、不修改批次状态，也不把候选或节点资产判为正式 PASS。
---
# NDC 道具人工需求文档

本 Skill 把分散的策划、剧情、配置、现有资产和批次记录转成两份同步产物：机器可核验的 `ndc-prop-manual-requirements/v1` JSON，以及人工可逐项执行的详细 DOCX。清单覆盖完整章节范围，不只列当前缺失或已完成内容。

先读同级 [道具需求整理 Skill](../ndc-prop-requirements/SKILL.md) 的范围、来源和取得方式规则；本 Skill 不替代其 `content_archive.json`、`batch.json` 或活动范围，只把已核实事实组织成人工文档。开始整理时读[信息模型与来源](references/information-model.md)和[分类与产物规则](references/classification-and-artifact-rules.md)。准备文档时再读[文档结构与写作](references/document-structure-and-writing.md)；生成 DOCX、渲染及交付前读[执行与质量门禁](references/workflow-and-quality-gates.md)。

## 范围与路径

1. 运行项目 `ndc_art.py paths`，取得 `{PLANNING_ROOT}`、`{ENGINE_ROOT}`、`{WORK_ROOT}`、`{DELIVERY_ROOT}`。不得把本 Skill 文件中的占位符当成字面路径，也不得猜固定盘符、用户名或相邻 checkout。
2. 策划与游戏工程根只读；抽取表、标准化 JSON、Markdown、渲染页和审核记录进入 `{WORK_ROOT}/道具/<Unit>/需求文档_<revision>/`。
3. 只有完成内容核对和 DOCX 逐页视觉检查的文档，才复制到 `{DELIVERY_ROOT}/道具/<Unit>/需求文档/`。内部 JSON、审计报告和页面 PNG 不进入最终交付，除非用户明确要求。

## 工作步骤

1. **锁定完整范围。** 以章节、Loop、场景、Item、小游戏／案件板附属项为全集，记录当前活动范围修订及 SHA-256。被排除项仍列在“范围外与历史保留”章节并写明原因，不从文档中消失。
2. **建立来源快照。** 优先读已锁 `content_archive.json` 与 `batch.json`，再读当前 SceneConfig、ItemStaticData、剧情／玩法原文、已批准资产索引和必要的历史纠偏。每项结论绑定 `source_id`、路径、SHA-256 和权威状态；旧表、旧 archive 或文件名只能作为差异证据，不能覆盖当前来源。
3. **分开两条分类轴。** `semantic_class` 决定普通 Big、照片线索 `clue_big 620×620`、环境 Big 或小游戏专用表现；`acquisition_route` 决定 Map/XY、直接拾取四态、Type 6/7、菜单与演出状态。不得因 NPC 交付而把照片线索降成普通 Big，也不得因道具看起来像旧照片而自动升成照片线索。
4. **推导完整产物矩阵。** 每个 item/state/scene/role 都写 `REQUIRED` 或带具体理由的 `NOT_APPLICABLE`；现有文件只是 `current_status`，不能改变需求。直接拾取、容器、环境观察、detail-only 与 minigame-only 逐类应用[分类规则](references/classification-and-artifact-rules.md)。
5. **把缺口转成人工任务。** 对 `manual_action != NONE` 的角色建立任务，包含输入文件、操作说明、输出、尺寸／命名、视觉与技术验收、依赖、阻塞原因和返回位置。一个笼统的“需人工处理”不是任务；一个角色缺口也不能用另一个角色的现有文件抵扣。
6. **保留状态边界。** 物理存在、历史件、候选、provisional、单项 PASS、有效 PASS、节点可审和整章正式交付分列。文档只报告当前证据，不写入 batch、不转正资产、不把人工节点批准解释为正式发布。
7. **先校验 JSON，再写 DOCX。** 从 `assets/manual-requirements.template.json` 初始化，填完后运行 `scripts/manual_requirements.py validate`；零错误后生成 Markdown 审阅摘要。DOCX 按[文档结构](references/document-structure-and-writing.md)制作，并使用 `assets/document-profile.zh-CN.json` 的字段和视觉配置。
8. **渲染并逐页复核。** 通过可用的 `documents` Skill 运行其当前 `render_docx.py`，以原尺寸检查每一页的表格溢出、缺字、断行、孤行、空白页、重复表头和页脚。任何修改后重新渲染全部页面；最终只交付通过复核的 DOCX。

## 命令

从本 Skill 根执行；解释器使用当前工作区依赖返回的 Python：

```text
python scripts/manual_requirements.py init --chapter-id UnitX --title "章节名称" --revision YYYY-MM-DD --output <工作目录>/manual_requirements.json
python scripts/manual_requirements.py validate --input <工作目录>/manual_requirements.json --report <工作目录>/validation_report.json
python scripts/manual_requirements.py summary --input <工作目录>/manual_requirements.json --output <工作目录>/人工需求审阅摘要.md
python -m unittest discover -s tests -p "test_*.py"
```

`init` 只建立待填清单，不代表通过。`validate` 的成功只证明结构与跨字段规则成立，不能替代来源阅读、视觉判断或 DOCX 页面检查。

## 完成条件

- 章节全集、排除项、场景和 Item 数量可相互对账；每个 item 都有当前来源。
- 资产性质与取得路线分别统计，所有照片线索、环境叙事物、普通道具和附属玩法均可枚举。
- 每个 `REQUIRED` 角色都有当前状态；所有需人工角色都有可执行任务，所有阻塞都有影响范围和恢复条件。
- 机器 JSON 校验零错误；DOCX 内容与 JSON 计数一致；每页渲染审阅通过。
- 文档明确标注“需求清单／人工交接，不等于资产正式 PASS”，且不修改生产状态或游戏工程。
