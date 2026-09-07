window.SKILL_CATALOG = {
  "generatedAt": "2026-09-05 · 美术入口与跨机器路径整理",
  "scanRules": "静态美术 Skill 列策划库主入口，H3 视频 Skill 列工程库主入口；其他同名目录仅为兼容入口。道具主流程由美术同学维护，三个旧子接口待同步。图片和视频过程文件在项目外，用户确认后交付工程。已删除的 Skill 不列入入口。",
  "skills": [
    {
      "name": "runninghub-h3-greenscreen-avatar",
      "category": "数字人与语音",
      "project": "engine",
      "kind": "数字人制作",
      "purpose": "工程侧维护：按正式对白、语音与策划角色参考生成并检查 H3 绿幕数字人。",
      "inputs": [
        "Talk ID、角色名与中英文台词",
        "Unit / Loop / 场景及前后对白语境",
        "同角色参考图 1–3 张",
        "对白 Audio 1 与静音 Audio 2",
        "可选情绪、动作和批量目标"
      ],
      "rating": 4.9,
      "ratingNote": "输入门槛、付费重试上限、机器质检和交付边界都非常完整。",
      "modified": "2026-09-05",
      "path": ".codex/skills/runninghub-h3-greenscreen-avatar/SKILL.md",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "runninghub-h3-ref2va-audio",
      "category": "数字人与语音",
      "project": "engine",
      "kind": "H3 双音频",
      "purpose": "调用指定的 H3 双阶段音频参考应用；输出目录必须显式指定。",
      "inputs": [
        "最多 3 张角色参考图",
        "Reference Audio 1 与 Audio 2",
        "H3 视频提示词",
        "时长、画幅与可选种子",
        "可选节点覆盖参数"
      ],
      "rating": 4.5,
      "ratingNote": "底层调用、节点检查和下载流程清楚，但对上层剧情语境的处理依赖其他 Skill。",
      "modified": "2026-09-05",
      "path": ".codex/skills/runninghub-h3-ref2va-audio/SKILL.md",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-h3-avatar-delivery",
      "category": "数字人与语音",
      "project": "engine",
      "kind": "H3 后处理",
      "purpose": "对用户已选定的 H3 候选做确定性后处理，在当前任务中准备交付包。",
      "inputs": [
        "已批准的 Talk ID",
        "明确批准的原生候选 MP4",
        "delivery_handoff.json 与 QA 报告",
        "允许执行的裁剪、增益或绿幕处理范围",
        "正式目标与 ready 相对路径"
      ],
      "rating": 4.8,
      "ratingNote": "审批边界、哈希验证、尺寸和绿幕规范严密，交付风险控制优秀。",
      "modified": "2026-09-05",
      "path": ".codex/skills/ndc-h3-avatar-delivery/SKILL.md",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "generate-config",
      "category": "数字人与语音",
      "project": "engine",
      "kind": "配置生成",
      "purpose": "为 AVG 对话生成语音配置，补齐 voice 参数、表演 action_prompt 和绿幕表情参考图选择。",
      "inputs": [
        "AVG 对话 JSON 或 Talk ID 范围",
        "角色音色预设",
        "对白前后剧情语境",
        "表情图目录或角色素材",
        "目标 voice config 输出位置"
      ],
      "rating": 4.3,
      "ratingNote": "覆盖语音与表演配置的完整链路，规则丰富，但维护时间相对较早。",
      "modified": "2026-07-07 12:43",
      "path": ".codex/skills/generate-config/SKILL.md"
    },
    {
      "name": "ndc-scene-to-mj-prompt",
      "category": "场景出图",
      "project": "planning",
      "kind": "提示词设计",
      "purpose": "按 v3 无人物场景流程生成 MJ 提示词与生产交接包。",
      "inputs": [
        "场景名称、用途与探索类型",
        "剧情语境和必须保留的物件",
        "认可的风格样例",
        "本地参考图及各自用途",
        "探索场景单视角或非探索三视角要求"
      ],
      "rating": 4.7,
      "ratingNote": "需求拆解、视角规则和交接格式清晰，适合作为出图上游真源。",
      "modified": "2026-09-05",
      "path": ".codex/skills/ndc-scene-to-mj-prompt/SKILL.md",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-midjourney-operator",
      "category": "场景出图",
      "project": "planning",
      "kind": "MJ 执行",
      "purpose": "执行 v3 场景交接包，并按需求审核候选和规划后处理。",
      "inputs": [
        "ndc-mj-scene/v2 结构化交接包",
        "共用参考图与用途说明",
        "各视角完整提示词",
        "构图和核心物件验收标准",
        "允许的迭代轮次"
      ],
      "rating": 4.7,
      "ratingNote": "从提交到审核、Vary 和停止条件都有明确流程，生产可控性高。",
      "modified": "2026-09-05",
      "path": ".codex/skills/ndc-midjourney-operator/SKILL.md",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-coordinate-image-edit",
      "category": "场景出图",
      "project": "planning",
      "kind": "局部修图",
      "purpose": "在授权区域内进行像素坐标锁定的修图、合成与边界校验。",
      "inputs": [
        "源图片绝对路径",
        "坐标原点与允许修改的矩形区域",
        "可选非矩形硬遮罩",
        "需要移除、替换或修复的具体内容",
        "必须保持不变的边界、材质和周边元素"
      ],
      "rating": 4.8,
      "ratingNote": "非破坏式状态机、单次生成授权、遮罩外零差异验证和恢复流程都很严密。",
      "modified": "2026-09-05",
      "path": ".codex/skills/ndc-coordinate-image-edit/SKILL.md",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "episode-story-extractor",
      "category": "剧情与推理",
      "project": "planning",
      "kind": "内容设计",
      "purpose": "从剧情策划的原始故事中提炼全局关键事件、核心立意和 3–5 个情感共鸣点，为章节大纲提供稳定方向。",
      "inputs": [
        "章节编号（如 Unit 3）",
        "剧情策划的原始故事文档",
        "可选的前后章节主线背景"
      ],
      "rating": 3.7,
      "ratingNote": "职责和输出模板明确，但属于较早期的单阶段设计工具，自动校验较少。",
      "modified": "2026-06-05 11:44",
      "path": ".agents/skills/episode-story-extractor/SKILL.md"
    },
    {
      "name": "episode-outline-generator",
      "category": "剧情与推理",
      "project": "planning",
      "kind": "内容设计",
      "purpose": "把章节核心事件、立意和情感点扩展为六个 Loop 的调查目标、搜证方向、指证对象和玩家体验曲线。",
      "inputs": [
        "章节编号",
        "故事提炼器输出的三大核心要素",
        "原始故事文档",
        "可选角色与前后章约束"
      ],
      "rating": 3.7,
      "ratingNote": "六循环输出结构完整，但证据、State 与运行时映射需要下游 Skill 继续收敛。",
      "modified": "2026-06-05 11:44",
      "path": ".agents/skills/episode-outline-generator/SKILL.md"
    },
    {
      "name": "narrative-guide",
      "category": "剧情与推理",
      "project": "planning",
      "kind": "设计引导",
      "purpose": "以叙事理论逐步诊断剧情框架、角色弧光、主题和情绪节奏，帮助策划找到可执行的修正方向。",
      "inputs": [
        "当前剧情框架或故事片段",
        "希望解决的叙事问题",
        "目标玩家体验",
        "不可改变的既定事实"
      ],
      "rating": 4.2,
      "ratingNote": "适合讨论和诊断，理论框架清楚；落地仍需其他生产 Skill。",
      "modified": "2026-08-10 13:21",
      "path": ".agents/skills/narrative-guide/SKILL.md"
    },
    {
      "name": "team-design",
      "category": "剧情与推理",
      "project": "planning",
      "kind": "团队编排",
      "purpose": "编排设计师、多名审查员和内容总监，完成单场景或单 NPC 等中等规模内容设计。",
      "inputs": [
        "单场景或单 NPC 目标",
        "章节与 Loop 背景",
        "角色档案、State 和现有内容",
        "期望产出与不可变约束"
      ],
      "rating": 4.2,
      "ratingNote": "角色分工明晰，适合中型任务；流程依赖多 Agent 环境和用户确认。",
      "modified": "2026-06-05 11:44",
      "path": ".agents/skills/team-design/SKILL.md"
    },
    {
      "name": "team-expose",
      "category": "剧情与推理",
      "project": "planning",
      "kind": "团队编排",
      "purpose": "端到端设计一场完整指证：独立谜题方案、State 写入、Expose 对话、并行审查和内容总监汇总。",
      "inputs": [
        "Unit / Loop 与目标 NPC",
        "章节现有指证与证据设计",
        "当前 State 文件",
        "人物档案和对白语境"
      ],
      "rating": 4.4,
      "ratingNote": "双方案和多审查结构扎实，输入输出链清楚；规则版本相对较早。",
      "modified": "2026-06-05 11:44",
      "path": ".agents/skills/team-expose/SKILL.md"
    },
    {
      "name": "team-loop",
      "category": "剧情与推理",
      "project": "planning",
      "kind": "团队编排",
      "purpose": "编排整个 Loop 的证据、指证、State、对白与全面审查，是单 Loop 最大规模的端到端设计流程。",
      "inputs": [
        "Unit 与 Loop 标识",
        "章节设计文档",
        "已有证据和 State",
        "NPC 档案与知识边界",
        "本 Loop 的调查目标"
      ],
      "rating": 4.5,
      "ratingNote": "端到端覆盖广、审查维度完整，适合大任务；执行成本与确认节点较多。",
      "modified": "2026-06-05 11:44",
      "path": ".agents/skills/team-loop/SKILL.md"
    },
    {
      "name": "avg-dialogue",
      "category": "对白与台本",
      "project": "engine",
      "kind": "对白工作流",
      "purpose": "约束 AVG 对话的两阶段生产：先修改 Markdown 草稿，用户明确确认后再把 Words 安全同步到 JSON。",
      "inputs": [
        "Unit / EPI 与 Loop",
        "目标 NPC、场景或 Talk ID",
        "真实设计文档和现有对白",
        "拟修改的中英文台词",
        "Phase 2 明确写入授权"
      ],
      "rating": 4.5,
      "ratingNote": "真源、阶段和知识边界清楚，能有效避免直接污染正式 JSON。",
      "modified": "2026-08-10 15:47",
      "path": ".codex/skills/avg-dialogue/SKILL.md"
    },
    {
      "name": "dialog-branch-editor",
      "category": "对白与台本",
      "project": "engine",
      "kind": "对白编辑",
      "purpose": "跨文件定位上下文，为已有 Talk 链添加或修改选项、分支响应与汇合节点。",
      "inputs": [
        "NPC、AVG 文件或入口 Talk ID",
        "新增或修改的选项文字",
        "每个选项的响应对白",
        "分支汇合点或后续目标",
        "必须保留的现有节点"
      ],
      "rating": 4.2,
      "ratingNote": "分支结构示例和 ID 处理细致，范围清楚；仍需依赖正式对白规则复核。",
      "modified": "2026-08-10 15:47",
      "path": ".codex/skills/dialog-branch-editor/SKILL.md"
    },
    {
      "name": "dialog-branch-restructure",
      "category": "对白与台本",
      "project": "engine",
      "kind": "对白编辑",
      "purpose": "重构 Talk 分支架构，收敛为可回选、单路径推进和唯一结局，同时保持既有信息与跳转正确。",
      "inputs": [
        "现有 Talk 文件或入口 ID",
        "当前分支图与问题描述",
        "期望的单路径或唯一结局",
        "必须保留的对白和事件",
        "目标汇合节点"
      ],
      "rating": 4.2,
      "ratingNote": "对分支拓扑的处理专门而实用，适合结构性调整。",
      "modified": "2026-08-10 15:47",
      "path": ".codex/skills/dialog-branch-restructure/SKILL.md"
    },
    {
      "name": "talk-edit-by-chat",
      "category": "对白与台本",
      "project": "engine",
      "kind": "正式表编辑",
      "purpose": "让策划用聊天、截图或文字批量修改 Talk 表对白，集中确认后只打表一次，并严格限制为 Talk。",
      "inputs": [
        "Talk ID、截图或可定位的原文",
        "改后的中英文对白",
        "可选的多段批量修改清单",
        "最终统一执行确认"
      ],
      "rating": 4.5,
      "ratingNote": "定位、批量缓存、单次打表和表范围隔离设计成熟。",
      "modified": "2026-08-10 15:47",
      "path": ".codex/skills/talk-edit-by-chat/SKILL.md"
    },
    {
      "name": "dialogue-id-reorder",
      "category": "对白与台本",
      "project": "planning",
      "kind": "台本整理",
      "purpose": "逐 Loop、逐文件重排混乱的对话 ID，连续化编号、拆分长句，并同步修正分支和审查问题。",
      "inputs": [
        "Unit 与 Loop",
        "需要整理的完整台本 MD",
        "目标 ID 段或编号规则",
        "拆句与分支保留要求"
      ],
      "rating": 4.5,
      "ratingNote": "专门处理高风险 ID 迁移，步骤和审查约束较完整。",
      "modified": "2026-08-10 13:21",
      "path": ".agents/skills/dialogue-id-reorder/SKILL.md"
    },
    {
      "name": "dialogue-md-to-json",
      "category": "对白与台本",
      "project": "planning",
      "kind": "安全同步",
      "purpose": "把 Unit1 EPI01 六个完整台本中的中英文 Words 回写到本地 AVG JSON，并验证 1690 个正式 ID、场景和跳转不变。",
      "inputs": [
        "Unit1 六个完整台本 MD",
        "本地 AVG/EPI01 正式结构",
        "只读检查或 --write 模式",
        "写入前的用户明确确认"
      ],
      "rating": 4.9,
      "ratingNote": "写入面极窄，结构不变量和正式 ID 数量都有确定性验证。",
      "modified": "2026-08-10 13:12",
      "path": ".agents/skills/dialogue-md-to-json/SKILL.md"
    },
    {
      "name": "team-dialogue",
      "category": "对白与台本",
      "project": "planning",
      "kind": "团队编排",
      "purpose": "从 Manifest 大纲、定稿 State 和既有成稿建立连续性合同，按连续场景包撰写并审查 Talk、Opening、Expose 与过场。",
      "inputs": [
        "Unit / Loop 或连续场景包",
        "Manifest 指向的有效大纲",
        "定稿 State",
        "既有成稿、角色档案和全局连续性资料",
        "本轮对白目标与边界"
      ],
      "rating": 4.9,
      "ratingNote": "规则、连续性、声纹、接缝审查和内容总监闸门非常完整。",
      "modified": "2026-08-10 13:12",
      "path": ".agents/skills/team-dialogue/SKILL.md"
    },
    {
      "name": "config-props",
      "category": "配置生产",
      "project": "engine",
      "kind": "正式表配置",
      "purpose": "配置成对出现的可交互道具：外层 Type 6 交互物与内嵌 Type 7 道具，并保持引用关系正确。",
      "inputs": [
        "Unit / Scene",
        "外层交互物 ID 与表现",
        "内嵌道具 ID 与内容",
        "点击、获得或切换行为",
        "关联资源与文本"
      ],
      "rating": 3.8,
      "ratingNote": "领域专一、规则实用，但覆盖面较窄且更新时间较早。",
      "modified": "2026-07-07 12:43",
      "path": ".codex/skills/config-props/SKILL.md"
    },
    {
      "name": "unity-table-edit",
      "category": "配置生产",
      "project": "engine",
      "kind": "正式表编辑",
      "purpose": "以 Excel 为真源安全修改 Unity 正式配置表，再生成 JSON 与 runtime bytes，并校验三层产物一致。",
      "inputs": [
        "目标工作簿、Sheet、记录 ID 和字段",
        "新值及策划依据",
        "相关联表和运行时影响",
        "明确的正式表写入授权"
      ],
      "rating": 4.8,
      "ratingNote": "Excel-first、生成链和验证边界非常严密，是正式表修改的可靠入口。",
      "modified": "2026-08-10 20:10",
      "path": ".codex/skills/unity-table-edit/SKILL.md"
    },
    {
      "name": "config-edit",
      "category": "配置生产",
      "project": "planning",
      "kind": "预览表编辑",
      "purpose": "用自然语言安全修改 avg_editor_v2 的设计期配置副本，定位正确表和字段并联动处理关联数据。",
      "inputs": [
        "Unit、Loop 或目标对象",
        "证据、场景、NPC、疑点等 ID",
        "要改成什么及原因",
        "关联影响和不可变约束",
        "修改前确认"
      ],
      "rating": 4.7,
      "ratingNote": "定位、关联影响、改前确认和基线自校验都很完整，且与 Unity 正式表严格隔离。",
      "modified": "2026-07-02 19:38",
      "path": ".agents/skills/config-edit/SKILL.md"
    },
    {
      "name": "unit-state-generator",
      "category": "配置生产",
      "project": "planning",
      "kind": "State 架构",
      "purpose": "依据 canon_manifest 中登记的有效大纲，生成、重建或审计一个 Unit 的六个 State 文件及跨 Loop 交接。",
      "inputs": [
        "Unit 编号",
        "canon_manifest 中的活动大纲",
        "章节设计与角色资料",
        "现有 State（重建或审计时）",
        "Unity 映射与不可变约束"
      ],
      "rating": 4.9,
      "ratingNote": "真源选择、六 Loop 一致性、开场和运行时映射校验都覆盖得很深入。",
      "modified": "2026-08-10 13:21",
      "path": ".agents/skills/unit-state-generator/SKILL.md"
    },
    {
      "name": "ndc-config-test",
      "category": "测试与审计",
      "project": "engine",
      "kind": "只读测试",
      "purpose": "结合静态审计和 Unity CLI 证据测试配置，区分表可加载、结构正确与玩家真实可通关，并给出最小修复建议。",
      "inputs": [
        "Unit 与可选 Loop",
        "测试层级：静态 / EditMode / PlayMode",
        "可选自由探索 hub Talk ID",
        "正式配置与对应需求文档",
        "报告输出位置"
      ],
      "rating": 4.8,
      "ratingNote": "证据等级、FAIL/GAP/UNVERIFIED 和最小修复推导都有严格定义，且不越权改表。",
      "modified": "2026-08-21 14:55",
      "path": ".agents/skills/ndc-config-test/SKILL.md"
    },
    {
      "name": "ndc-config-review",
      "category": "测试与审计",
      "project": "engine",
      "kind": "体验验收",
      "purpose": "从叙事语义、玩家知识、证据因果、自由探索、指证、场景可达性和美术缺口等维度验收已完成配置。",
      "inputs": [
        "已完成配置的 Unit / Loop 范围",
        "Unity/AVG 正式表与设计依据",
        "相关对白、State 和美术资源",
        "希望重点复查的问题或玩家路径"
      ],
      "rating": 4.7,
      "ratingNote": "审查维度非常全面，能覆盖配置能跑但体验不成立的问题。",
      "modified": "2026-08-13 19:26",
      "path": ".agents/skills/ndc-config-review/SKILL.md"
    },
    {
      "name": "episode-consistency-audit",
      "category": "测试与审计",
      "project": "planning",
      "kind": "全集审计",
      "purpose": "对一个 Unit 的全部 Loop 做事实抽取与七维并行审计，把对白、State 和角色档案三向对账并生成 HTML 报告。",
      "inputs": [
        "Unit 标识",
        "canon_manifest 与有效章节文档",
        "六个 Loop 的对白和 State",
        "角色档案与配置资料",
        "报告输出目录"
      ],
      "rating": 4.8,
      "ratingNote": "跨 Loop、跨视角与多源事实校验完整，适合高准确率终审。",
      "modified": "2026-08-10 12:55",
      "path": ".agents/skills/episode-consistency-audit/SKILL.md"
    },
    {
      "name": "playthrough-audit",
      "category": "测试与审计",
      "project": "planning",
      "kind": "体验审计",
      "purpose": "模拟普通玩家完整游玩一个 Unit，分析信息获取、证据链、推理难度和风险点，产出交互式 HTML 报告。",
      "inputs": [
        "Unit 标识",
        "该 Unit 的 State、对白与配置表",
        "角色档案和章节设计",
        "可选的审计重点或 Loop 范围"
      ],
      "rating": 4.8,
      "ratingNote": "玩家模拟、事实复核、风险明细和可视化报告形成完整闭环。",
      "modified": "2026-08-03 10:48",
      "path": ".agents/skills/playthrough-audit/SKILL.md"
    },
    {
      "name": "avg-editor",
      "category": "设计IDE与可视化",
      "project": "planning",
      "kind": "设计规范",
      "purpose": "定义 NDC 网页配置编辑器的产品和架构：以场景为主轴，提供可视化、可编辑的游戏中间态并减少 Unity 验收成本。",
      "inputs": [
        "编辑器产品或架构问题",
        "配置表 schema 与数据流",
        "场景、Talk、证据和疑点的展示需求",
        "网页编辑与同步到 Unity 的边界"
      ],
      "rating": 4,
      "ratingNote": "作为权威设计稿内容非常完整，但明确不是可直接调用的执行 Skill。",
      "modified": "2026-08-10 13:53",
      "path": ".agents/skills/avg-editor/SKILL.md"
    },
    {
      "name": "miro",
      "category": "设计IDE与可视化",
      "project": "planning",
      "kind": "可视化工具",
      "purpose": "把缩进文本或 Markdown 大纲批量导入 Miro Mind Map，也能列出节点和清理残留内容。",
      "inputs": [
        "Miro board URL 或 board ID",
        "缩进文本或 Markdown 大纲",
        "操作类型：导入 / 列出 / 清理",
        "可选布局与目标父节点"
      ],
      "rating": 4.2,
      "ratingNote": "解决 NDC 推理内容无法直接通过 Miro AI 的实际问题，批量操作流程清楚。",
      "modified": "2026-08-10 13:14",
      "path": ".agents/skills/miro/SKILL.md"
    },
    {
      "name": "animation-rules",
      "category": "开发与项目",
      "project": "engine",
      "kind": "代码规范",
      "purpose": "统一 Unity UI 与特效动画的 DOTween 写法，包括缓动字段、Sequence 时间轴、中断保护和 Inspector 分组。",
      "inputs": [
        "要实现或修改的动画需求",
        "目标 C# 文件、面板或节点",
        "时长、位置、缩放和缓动期望",
        "现有动画代码与中断场景"
      ],
      "rating": 4,
      "ratingNote": "示例和反例十分丰富，适合作为自动规则；不负责独立执行修改。",
      "modified": "2026-07-07 12:43",
      "path": ".codex/skills/animation-rules/SKILL.md"
    },
    {
      "name": "coding-standards",
      "category": "开发与项目",
      "project": "engine",
      "kind": "代码规范",
      "purpose": "为 NDC Unity 工程提供 C# 编码规范、现有框架复用要求和常见实现禁区。",
      "inputs": [
        "Unity C# 开发任务",
        "目标脚本或模块",
        "期望功能",
        "可参照的现有项目实现"
      ],
      "rating": 4,
      "ratingNote": "项目约束和代码示例详细，能减少风格漂移；本身属于自动参考规则。",
      "modified": "2026-07-07 12:43",
      "path": ".codex/skills/coding-standards/SKILL.md"
    },
    {
      "name": "git-branch-manager",
      "category": "开发与项目",
      "project": "engine",
      "kind": "项目工具",
      "purpose": "管理 NDC 的 main 与 planning 双分支策略，处理状态检查、分支切换、提交和推送。",
      "inputs": [
        "目标动作：状态 / 切换 / 提交 / 推送",
        "目标分支",
        "提交范围与提交说明",
        "是否允许推送远端"
      ],
      "rating": 3.8,
      "ratingNote": "规则简单实用，但覆盖的是较传统且有限的双分支工作流。",
      "modified": "2026-07-07 12:43",
      "path": ".codex/skills/git-branch-manager/SKILL.md"
    },
    {
      "name": "daily-summary",
      "category": "开发与项目",
      "project": "planning",
      "kind": "项目记录",
      "purpose": "回顾指定日期的工作记录，提取任务、成果、问题与待办，并生成结构化的每日总结文档。",
      "inputs": [
        "总结日期（必需，默认今天但需要确认）",
        "可选总结范围或主题",
        "详细程度：simple / standard / detailed"
      ],
      "rating": 3.4,
      "ratingNote": "模板完整、输入直观，但无标准 frontmatter，且依赖可访问的历史对话。",
      "modified": "2026-06-05 11:44",
      "path": ".agents/skills/daily-summary/SKILL.md"
    },
    {
      "name": "pm-dashboard",
      "category": "开发与项目",
      "project": "planning",
      "kind": "项目工具",
      "purpose": "扫描项目状态、分析 PM 风险、上传 Supabase 并打开项目管理仪表盘。",
      "inputs": [
        "子命令：scan / analyze / init / open",
        "项目根目录",
        "分析范围或任务列表",
        "上传时所需的 Supabase 配置"
      ],
      "rating": 3.8,
      "ratingNote": "扫描到展示链路清楚，但依赖外部 Supabase 状态和旧版配置。",
      "modified": "2026-06-05 11:44",
      "path": ".agents/skills/pm-dashboard/SKILL.md"
    },
    {
      "name": "novai-gemini",
      "category": "AI辅助",
      "project": "engine",
      "kind": "模型调用",
      "purpose": "通过项目的 NovAI 接口调用 Gemini，对文本、代码、对白或小范围项目文件提供第二意见。",
      "inputs": [
        "要咨询或审查的 Prompt",
        "可选 Gemini 模型名",
        "可选 prompt 文件路径",
        "需要读取的单个项目文件或紧凑上下文"
      ],
      "rating": 4.2,
      "ratingNote": "调用方式简单、边界明确，适合复核；效果取决于外部模型和 API 状态。",
      "modified": "2026-08-10 15:47",
      "path": ".codex/skills/novai-gemini/SKILL.md"
    },
    {
      "name": "generate-ndc-emergency-art",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "场景出图",
      "kind": "突发事件",
      "purpose": "按剧情事件要求制作突发事件与闪回所需画面。",
      "project": "planning",
      "path": ".codex/skills/generate-ndc-emergency-art/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-avg-character-scene-art",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "场景出图",
      "kind": "AVG 人物层",
      "purpose": "制作固定机位 AVG 人物透明层、场景合成和工程所需分层包。",
      "project": "planning",
      "path": ".codex/skills/ndc-avg-character-scene-art/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-character-scene-integration",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "场景出图",
      "kind": "人物入景",
      "purpose": "依据实际台词、站位和对话框遮挡，把已确定角色放入固定场景。",
      "project": "planning",
      "path": ".codex/skills/ndc-character-scene-integration/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-evidence-container",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "道具出图",
      "kind": "旧接口待同步",
      "purpose": "旧容器子流程；接口与发布合同待美术同学同步，暂不独立执行。",
      "project": "planning",
      "path": ".codex/skills/ndc-evidence-container/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "protected_colleague_work_in_progress"
    },
    {
      "name": "ndc-evidence-detail-art",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "道具出图",
      "kind": "旧接口待同步",
      "purpose": "旧细节子流程；文字处理规则与新版冲突，暂不独立执行。",
      "project": "planning",
      "path": ".codex/skills/ndc-evidence-detail-art/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "protected_colleague_work_in_progress"
    },
    {
      "name": "ndc-evidence-scene-placement",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "道具出图",
      "kind": "旧接口待同步",
      "purpose": "旧场景子流程；与新版主流程的打包参数不兼容，暂不独立执行。",
      "project": "planning",
      "path": ".codex/skills/ndc-evidence-scene-placement/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "protected_colleague_work_in_progress"
    },
    {
      "name": "ndc-free-exploration-character-art",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "场景出图",
      "kind": "探索人物层",
      "purpose": "制作探索场景人物两态和按角色轮廓打包的透明素材。",
      "project": "planning",
      "path": ".codex/skills/ndc-free-exploration-character-art/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-generate-characters",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "角色与表情",
      "kind": "角色设计",
      "purpose": "制作角色卡和所需肖像；已有角色按明确版本锁定身份。",
      "project": "planning",
      "path": ".codex/skills/ndc-generate-characters/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-generate-expressions",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "角色与表情",
      "kind": "表情制作",
      "purpose": "从已确认肖像制作可复用表情套图和透明/绿幕素材。",
      "project": "planning",
      "path": ".codex/skills/ndc-generate-expressions/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-multichar-avg-production",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "场景出图",
      "kind": "多人编排",
      "purpose": "用站位白盒编排两人及以上 AVG 场景，再逐角色制作与验收。",
      "project": "planning",
      "path": ".codex/skills/ndc-multichar-avg-production/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "centralized"
    },
    {
      "name": "ndc-scene-evidence-placement",
      "inputs": [
        "明确的制作需求及已指定素材",
        "项目外任务的 payload 路径",
        "具体 Skill 要求的台词、源图或交接包"
      ],
      "rating": null,
      "ratingNote": "未评分：本次仅核对入口与维护状态。",
      "category": "道具出图",
      "kind": "美术同学维护",
      "purpose": "道具制作主入口：场景点击图、容器、Big/Icon 与完整交付检查。机器路径按公共工作区规则。",
      "project": "planning",
      "path": ".codex/skills/ndc-scene-evidence-placement/SKILL.md",
      "modified": "2026-09-05",
      "maintenanceStatus": "protected_colleague_work_in_progress"
    }
  ]
};
