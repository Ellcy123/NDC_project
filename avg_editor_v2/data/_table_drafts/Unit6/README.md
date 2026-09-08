# 五 Loop 试验版：统一配置接入

2026-09-07：按用户确认，试验版使用原 avg_editor_v2 网页和统一配置表，不再跳转独立试玩页。

本地入口：

- L1：http://localhost:9529/index.html?unit=Unit6&loop=loop1
- L2：http://localhost:9529/index.html?unit=Unit6&loop=loop2

Unit6 / EPI06 / 6xxx 是试验命名空间，登记在 canon_manifest.json 的 experimentalUnits；不计为第六个正式章节，不自动同步 Unity。当前接入 L1、L2，L3—L5 尚未接入。

## 当前数据源

- data/table/ChapterConfig.json：601 为 L1，602 为 L2，分别挂载开场、场景入口、疑点、指证和收束。
- 同目录 SceneConfig、LocationConfig、NPCStaticData、NPCLoopData、MapConfig：L1 的门外／大堂／发现现场背景，以及一处会客室调查地点；L2 的六处调查地点及独立人物引用。6200 是 L2 开场背景引用。
- 同目录 ItemStaticData、Testimony、TestimonyItem、DoubtConfig、ExposeData：物品与口供分表，分析前后双向关联，指证材料全部进入当前疑点。
- 同目录 Talk.json：L1 包含28个对白段、217句台词，另有4个菜单与3个退出节点，共224条。Emma 在枪响前的大堂有两题，Rosa／Vivian／Morrison 在会客室各两题，共8个主题，另加退出。L2 保持239个对白节点、12个菜单／退出节点和2个前情材料初始化节点，共253条；六名可交谈 NPC，共13主题，另加退出。
- data/formal/unit_flow.json：由原 build_unit_flow.py 从上述表派生，仍为统一流程图缓存。

后续配置修改直接改统一表；import_u6_l1.py 与 import_u6_l2.py 只用于各轮的一次性接入，拒绝重新覆盖已接入的数据。experiments/u1-five-loop 的旧 manifest、engine 和 app 不参与原网页加载。

对白润色以 `剧情设计/试验单元/U1_五Loop试验版/L2_完整对白.md` 为源；使用 `sync_u6_l2_words.py` 先预检，再加 `--write` 回写本地统一表。此流程仅更新本试验的中文台词、英文发言名与人物显示名，并清除动作文字；校验原有节点身份、跳转及取证位置，其他 Unit 不受影响。

L1 对白源为 `剧情设计/试验单元/U1_五Loop试验版/L1_完整对白.md`；同目录的 `L1_制作合同.md` 记录本轮因果、知识边界与取证位置。首次导入前检查 MD；后续改字需另做受限文本同步，不能重新运行导入来覆盖既有表。

## L1 单次指证

| 疑点 | 触发材料 | 指证用 |
|---|---|---|
| 6101 Rosa 对这把枪的指认可信吗？ | 6208 枪检、6031001 Rosa 的原始指认、6103 委托协议 | 6208 为唯一出示物；6031001 为被攻击证词；协议仅作推进前置，保证后续交涉已有来源 |

原枪6101在会客室取得，分析后替换为6208。6208是此前 L2 单轮预览已经分配的试验 ID，继续复用同一检查结果；本次仅将 Loop 改为1、beforeAnalysedEvidence 指向6101、obtainMethod 改为 auto。不能因62字头把其来源判成 L2，也不增加重复结果卡。6032001保留为 L2 的回顾摘要，L1 原始指认是6031001。

正确提交只排除这把枪近期击发，不替 Vivian 排除所有嫌疑。指证后接既有委托协议的交涉与72小时调查期限，不再提交第二件证据；只有收尾最后一句结束 Loop。跳过 Emma 的两个可选主题，仍会经过固定合作收口、枪响和发现现场。

## L2 两轮指证

| 疑点 | 触发材料 | 指证用 |
|---|---|---|
| 6201 两本账的说法 | 6201 留存账、6202 公账、6052002 两账相等口供 | 两账为出示材料；6052002 为首轮被攻击证词 |
| 6202 经手的催款事务 | 6203 八月存根、6052001 签发职责 | 6203 为第二轮出示材料；6052001 只作来源确认 |

两轮答案对应 ChapterConfig.exposes 与 ExposeData 的相同行。不能用拒收另一张逻辑有效的证据维护唯一答案，现有对白／材料的维度区分沿用已审方案。

## 预览与工程的边界

原网页是配置预览：可播放对白、查看完整材料、显示分析产物、查看疑点依赖和指证答案。它没有自动库存、条件题解锁或选证失败重试；本次没有增加替代玩法引擎。

SceneConfig.previewTalks 是预览增强字段：引用同一 Talk 表的开场、取物、分析和错误回应，使用原对白抽屉播放；不能原样当作 Unity 新字段同步。

L1 的 ChapterConfig.openingSequence 只用于网页按背景定位四段开场，字段为 sceneId、entryTalkId、title、videoEpisode、videoLoop、videoScene。实际对白从 initTalk 顺序进入大堂菜单，菜单退出才继续枪响与发现现场；四张定位卡不替代这条对白链。

TalkBranchUnlockConfig.json 保留工程真实 ScriptableObject 的 rules 结构。Emma 第三题的 target Talk ID，要求6204原照片或6701分析照片任一，matchMode=0。原网页展示此条件，不执行库存门控；工程需用这份配置更新 FrontendConfigs 中的 asset，不能声称复制JSON即可生效。所有 TalkParam 仍只有原来的文本及跳转字段。

原 U1 至 U5 的既有表行、AVG、台本未改动；integration_report.json 保存 L2 导入前旧行的校验摘要与新增ID清单，integration_report_l1.json 保存 L1 新增行、6208唯一例外的改前／改后值，以及既有表、Manifest、流程缓存的保全摘要。L1 接入保留原 L2 对白、菜单与流程。

test_u6_l1.py 检查完整对白回写、8个主题回流、单次指证、取证时序、引用和旧数据保全；test_u6_l1_preview.cjs 检查四段开场、跳过 Emma 可选主题、NPC菜单、分析入口、指证至收尾及切回 L2／原 U1。原有 test_u6_tables.py 与 test_u6_preview.cjs 继续检查 L2。

此前 Sites 独立试玩地址不是本次统一配置入口；当前交付入口为以上原网页本地地址。
