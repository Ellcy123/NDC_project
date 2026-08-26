# Unit2 飞书突发事件缺口与 Skill 出图需求

> 结论版本：2026-08-26  
> 对比基线：提交 `52506103c8d96b1280c416d6e79e253023e2018b` 与飞书“闪回需求”最终工作表  
> 本文用途：作为 `generate-ndc-emergency-art` Skill 的下一批出图任务书  
> 当前范围：只生成和审查实验候选，不覆盖正式美术、不修改 Talk、不修改 Excel/JSON/bytes

## 1. 结论

飞书最终工作表共有 **16 个事件、28 个目标资产**。

上次提交已经完成并接受了 C01—C09 九组旧编号事件，共 **16 张 Skill 近景化候选**。按剧情语义对齐飞书最终版后：

- **真正缺失：7 个事件、9 张图。**
- **已覆盖：9 个事件、16 张图。**
- **另有 3 张飞书数量差异，不列入本轮缺口：**C01 少 1 张、C06 少 2 张。这三张已被当前 Skill 按“最小有效帧数 + 近景硬约束”压缩进现有画面。
- Loop6 的 P06（旧编号 C08）虽然飞书原案包含上吊远景，但上次提交已用“遗书手部 + 空床余波”两张非血腥局部画面完成同一叙事，不需要重出。

本轮应生成以下资产：

1. `evt_l1_office_telegram_01`
2. `evt_l2_overhear_danny_leonard_01`
3. `evt_l4_danny_bathroom_ring_01`
4. `evt_l4_lula_window_waiver_01`
5. `evt_l4_lula_window_waiver_postexpose_01`
6. `evt_l5_lula_strongbox_01`
7. `evt_l5_foster_call_01`
8. `evt_l5_foster_call_02`
9. `evt_l6_edith_suitcase_leave_01`

## 2. 对比依据

### 2.1 飞书最终需求

- 飞书 Wiki：`Bu4Kwx3mOiDcegkZ08Ica8sznQk`
- 工作表：`uw3NAU`
- 工作表名称：闪回需求
- 本地完整整理：`D:\NDC_project\剧情设计\Unit2\Unit2_飞书闪回需求完整整理.md`
- 读取时工作表修订号：454

### 2.2 上次提交

- Commit：`52506103c8d96b1280c416d6e79e253023e2018b`
- 提交说明：`feat(u2): add emergency art and refine art workflows`
- 提交时间：2026-08-26 09:36:51 +08:00
- 接受候选目录：`D:\NDC\NDC_project\test_output\imagegen\C01` 至 `C09`
- 首批主计划：`D:\NDC\NDC_project\test_output\imagegen\U2_C01-C05_突发事件生成计划.md`
- 后批主计划：`D:\NDC\NDC_project\test_output\imagegen\U2_C06-C09_突发事件生成计划.md`
- C01—C05 审查记录：`D:\NDC\NDC_project\test_output\imagegen\U2_C01-C05_突发事件审查记录.md`

本次覆盖判断以两份“突发事件生成计划”里的帧计划、执行记录和合格结论为主，不逐张重新审图。图片目录只用于确认计划所指的候选确实随提交存在。

### 2.3 本轮执行 Skill

- Skill：`D:\NDC\.codex\skills\generate-ndc-emergency-art\SKILL.md`
- Unit2 帧数指导：`D:\NDC\.codex\skills\generate-ndc-emergency-art\references\unit2-frame-count.md`
- 口径：局部或极局部特写、最小有效帧数、玩家当前已知信息、禁止提前剧透、干净矩形原图、通过后程序化封装黑边透明面板。

## 3. 统计口径

本文同时保留两种统计，避免把“飞书写了几张”与“当前 Skill 实际需要几张”混为一谈。

### 3.1 资产数量口径

严格按飞书每个资产名计数。飞书总量是 28 张；上次接受 16 张；两者表面相差 12 张。

### 3.2 剧情语义口径

按“玩家在这一刻必须看懂什么”计数。12 张表面差额中：

- 9 张属于完全没有生成过的新事件资产，是本轮真实缺口。
- 3 张属于 C01、C06 的拆镜差异，核心信息已经被合并到现有合格近景中。

本轮以剧情语义口径为准，不为了凑满 28 张而重新制造违反 Skill 的中景、全景或想象性画面。

## 4. 16 个飞书事件覆盖矩阵

| 飞书编号 | Loop | 飞书事件 | 飞书数量 | 上次接受 | 状态 | 本轮处理 |
| --- | --- | --- | ---: | ---: | --- | --- |
| C01 | Loop1 | 白布下的身份疑云 | 2 | 1 | 已覆盖，Skill 压缩 | 不生成 |
| P01 | Loop1 | 电报：Margaret 还活着 | 1 | 0 | **缺失** | 生成 1 张 |
| C02 | Loop2 | Mickey 街边救下 Margaret | 2 | 2 | 已覆盖 | 不生成 |
| C03 | Loop2 | 催债人威胁 O’Hara | 1 | 1 | 已覆盖 | 不生成 |
| P02 | Loop2 | 偷听 Danny 与 Leonard 谈房产证 | 1 | 0 | **缺失** | 生成 1 张 |
| C04 | Loop4 | Lula 与 Frank 地下室相伴五年 | 2 | 2 | 已覆盖 | 不生成 |
| P03 | Loop4 | Danny 困在厕所，Zack 已找到婚戒 | 1 | 0 | **缺失** | 生成 1 张 |
| P04 | Loop4 | Lula 隔窗放弃继承 | 2 | 0 | **缺失** | 生成 2 张 |
| C05 | Loop4 | Danny 坦白火场目击 | 3 | 3 | 已覆盖，使用 C05-02R 替换拒收稿 | 不生成 |
| P05 | Loop5 | Lula 带来铁盒 | 1 | 0 | **缺失** | 生成 1 张 |
| C07 | Loop5 | 火里的两个孩子 | 2 | 2 | 已覆盖 | 不生成 |
| P07 | Loop6 | Edith 提箱离开 | 1 | 0 | **缺失** | 生成 1 张 |
| P06（旧 C08） | Loop6 | Vinnie 用遗书遮盖真相 | 2 | 2 | 已覆盖，安全近景替代 | 不生成 |
| C09 | Loop6 | 三人留给 Frank 的纪念物 | 2 | 2 | 已覆盖 | 不生成 |
| C06 | Loop5 | Frank 信中的未来计划 | 3 | 1 | 已覆盖，Skill 压缩 | 不生成 |
| P06 | Loop5 | Foster 电话推翻死因 | 2 | 0 | **缺失** | 生成 2 张 |

合计：飞书 16 个事件 / 28 张；上次已接受 9 个事件 / 16 张；本轮待做 7 个事件 / 9 张；3 张为有意压缩差异。

## 5. 不列入缺口的三类差异

### 5.1 C01：飞书 2 张，上次 1 张

飞书原案把 Morrison、Zack 与白布现场拆为两张，其中包含较大范围人物关系。当前 Skill 的硬规则要求局部或极局部特写，上次接受的 C01-01 已通过白布边缘、不可辨认轮廓和烧毁地面完成“来晚了、身份仍不确定”的核心信息。

结论：Morrison 与 Zack 的反应继续由 AVG 对话承担，不为凑数新增人物中景。

### 5.2 C06：飞书 3 张，上次 1 张

飞书原案拆成“Frank 写信”“信中未来生活”“白天公园想象”三张。上次接受的 C06-01 已把 Frank 写信的手、`F & L 1923` 戒指、红玫瑰和疲惫局部面容放入同一关系框，表达求婚计划和没能实现的未来。

结论：不新增公园想象全景，也不复刻完整信件。除非后续明确要求放宽 Skill 的近景规则，否则 C06 视为已覆盖。

### 5.3 Loop6 P06（旧 C08）：远景死亡画面已安全替代

飞书图①资产是 `evt_l6_vinnie_suicide_note_02`，原描述为拘留室上吊结果；图②资产是 `evt_l6_vinnie_suicide_note_01`，描述为写遗书。

上次接受画面映射如下：

| 飞书资产 | 上次接受画面 | 语义 |
| --- | --- | --- |
| `evt_l6_vinnie_suicide_note_02` | C08-02 空床余波 | 用空床压痕、栏影和皱纸表达死亡后的缺席，不出现尸体、绳索和血 |
| `evt_l6_vinnie_suicide_note_01` | C08-01 手与遗书 | Vinnie 捏皱信纸、指节发白，表达主动把真相压回遗书 |

结论：这是符合 Skill 和非血腥表达的正式候选方向，不重做上吊远景。

## 6. 本轮统一生成合同

以下规则适用于全部 9 张候选。

### 6.1 叙事与构图

1. 只做局部或极局部特写，不做中景、全景、全身、建立镜头或多人整齐站位。
2. 每张只承载一个主要叙事瞬间；背景只提供地点色阶和少量结构，不承担完整空间介绍。
3. 主体脸、手、证物、动作接触点必须清楚；只允许非主体进入浅景深虚化。
4. 参考当前 Skill 的 ARRI 35MM、F1.2—F1.8 和完整统一风格模板执行，不在本文冻结一份可能过时的模板副本。
5. 先按干净矩形构图生成原图，不在生成阶段加入漫画黑边、透明角、红框、UI、字幕、水印或说明文字。
6. 纸面可以有符合年代的打字/手写质感，但画面叙事不得依赖模型准确生成大段文字。

### 6.2 信息边界

1. 每张只表现触发对白当刻玩家已经知道的事实。
2. 不提前确认 Leonard 的罪行、银行保护对象、Vinnie 顶罪动机、Mickey 的信息来源或后续证据链。
3. 不增加原需求没有的凶器、枪、血、尸体细节、暴力动作、现代设备或额外人物。
4. 角色英文名、身份、服装和年龄以角色卡/场景 NPC 为准，不用中文名生成角色标识。

### 6.3 生成与重试

1. 每张先出 1 个原始候选，逐张人工审查。
2. 只有出现硬性错误时允许从原始参考重新进行 1 次针对性修正；硬性错误包括人物身份错、完整人物入镜、证物错、剧透、暴力程度错和构图不是局部特写。
3. 原图通过后直接进入程序化面板包装，不调用额外 AI 简化或二次风格清理。
4. 多边形面板形状只在原图通过后确定；本文给出的长宽比仅用于约束生成构图。

### 6.4 实验输出目录

建议统一使用：

`D:\NDC\NDC_project\test_output\imagegen\<工作编号>\local_closeup_v1\`

每张至少保留：

- `<工作编号>-<帧号>_raw.png`
- `<工作编号>-<帧号>_panel_design.md`
- `<工作编号>-<帧号>_panel_rgba.png`
- `<工作编号>-<帧号>_magenta_mask.png`
- 原图与面板缩略图

## 7. 缺口任务总表

| 工作编号 | Loop | 事件 | 帧数 | 正式目标资产 | 难度 |
| --- | --- | --- | ---: | --- | --- |
| P01-L1 | Loop1 | 事务所电报 | 1 | `evt_l1_office_telegram_01` | 低 |
| P02-L2 | Loop2 | 银行偶然偷听 | 1 | `evt_l2_overhear_danny_leonard_01` | 中 |
| P03-L4 | Loop4 | 厕所门后的 Danny 与婚戒 | 1 | `evt_l4_danny_bathroom_ring_01` | 低 |
| P04-L4 | Loop4 | 隔窗放弃继承 | 2 | `evt_l4_lula_window_waiver_01`、`evt_l4_lula_window_waiver_postexpose_01` | 中高 |
| P05-L5 | Loop5 | Lula 带来铁盒 | 1 | `evt_l5_lula_strongbox_01` | 中 |
| P06-L5 | Loop5 | Foster 尸检反转 | 2 | `evt_l5_foster_call_01`、`evt_l5_foster_call_02` | 高 |
| P07-L6 | Loop6 | Edith 提箱离开 | 1 | `evt_l6_edith_suitcase_leave_01` | 中 |

## 8. P01-L1：事务所电报

### 8.1 任务信息

- 正式目标资产：`evt_l1_office_telegram_01`
- 实验目录：`D:\NDC\NDC_project\test_output\imagegen\P01_L1_telegram\local_closeup_v1\`
- 场景：Zack 事务所，深夜
- 图片触发对白：Zack：“等等。桌上多了什么东西。”
- 图片后关键信息：电报把行动目标指向圣心医院三楼，并确认 Margaret 还活着。
- 当前玩家知识：白布下的焦尸不是 Margaret，但 Zack 与 Emma 尚不知道她在哪里。

### 8.2 参考图

| 参考 | 路径 | 仅负责 |
| --- | --- | --- |
| 场景 | `D:\NDC\Assets\Resources\Art\Scene\Backgrounds\EPI02\SC2105_bg_ZackDetectiveOffice_Night.png` | 事务所桌面结构、夜间桌灯色阶 |
| Zack | `D:\NDC\NDC_project\Art\角色卡\zack.png` | 手、袖口、局部面容和身份 |
| Emma | `D:\NDC\NDC_project\Art\角色卡\emma.png` | 手、袖口、局部目光和身份 |

没有权威电报证物图。电报按 1920 年代纸张、折痕和打字格式生成，不能依赖大段可读文字完成叙事。

### 8.3 帧计划

| frame | narrative instant | current player knowledge | forbidden reveal | local subject | close-up content/action | visual hook | provisional orientation/panel family | selected references |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01-01 | Zack 刚拆开桌上突然出现的电报，Emma 同时凑近看到 | 焦尸不是 Margaret；两人仍在寻找她 | 不解释 Mickey 如何得知下落；不展示 Margaret 当前状态；不做医院画面 | 电报、Zack 拆信的手、Emma 同时压住纸角的手/目光 | 桌灯下电报位于中心，Zack 两手拉开折纸；Emma 从另一侧以手指、袖口和一小段震惊目光进入同一近焦层 | 两双手同时落在电报两侧，形成“他们同时看见”的瞬间 | 横向近方形证据/反应框，约 1.25—1.55 | 事务所背景、Zack、Emma |

### 8.4 生成语义

- 局部主体：桌灯下刚被拆开的电报、Zack 的手、Emma 同时触及纸角的手和局部目光。
- 动作重点：不是静物电报，而是两人同时发现信息的动作关系。
- 光线：事务所冷暗环境 + 暖色桌灯，只照亮纸面、手和局部眼神。
- 纸面：可保留短促打字行、医院抬头或电报格式感；不要生成需要玩家逐字阅读的完整正文。
- 禁止：完整双人半身、事务所全景、第三人、医院场面、Mickey 身影、夸张拥抱或庆祝。

### 8.5 验收

- [ ] 电报是第一视觉中心。
- [ ] Zack 与 Emma 的局部动作明确说明两人同时看见。
- [ ] 能读到“突如其来的希望”，但画面本身不解释信息来源。
- [ ] 不依赖错误或乱码长文本。
- [ ] 不出现完整人物或大范围事务所。

## 9. P02-L2：银行偶然偷听

### 9.1 任务信息

- 正式目标资产：`evt_l2_overhear_danny_leonard_01`
- 实验目录：`D:\NDC\NDC_project\test_output\imagegen\P02_L2_overhear\local_closeup_v1\`
- 场景：湖滨信托银行大厅
- 图片触发对白：Leonard：“不过……Danny，他有没有给你留过什么其他的东西？”
- 当前玩家知识：Danny 正急着处理 Frank 的房产证；Leonard 以银行手续为由拖延。
- 叙事目标：让玩家感觉自己撞见了一段不该听见的私下谈话，而不是参加正式问话。

### 9.2 参考图

| 参考 | 路径 | 仅负责 |
| --- | --- | --- |
| 场景 | `D:\NDC\Assets\Resources\Art\Scene\Backgrounds\EPI02\SC2211_bg_LakeshoreTrust_Lobby.png` | 大理石、黄铜、银行冷亮色阶 |
| Danny | `D:\NDC\NDC_project\Art\角色卡\Danny.png` | 粗壮手型、衣袖、警觉局部表情 |
| Leonard | `D:\NDC\NDC_project\Art\角色卡\Leonard Ross.png` | 手、袖口、职业化局部面容 |
| 房产证 | `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE\EPI02\LakeshoreTrust_ArchiveRoom\SC2313_item_07_big.png` | Frank 房产证明的纸张、文件夹和证物身份 |

### 9.3 帧计划

| frame | narrative instant | current player knowledge | forbidden reveal | local subject | close-up content/action | visual hook | provisional orientation/panel family | selected references |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P02-01 | Leonard 追问“其他东西”，Danny 察觉 Zack 靠近并准备抽走文件离开 | 房产证手续被拖延；Danny 缺钱 | 不揭示“其他东西”是什么；不确认 Leonard 的犯罪；不出现银行保护计划 | 房产证文件夹、Danny 抽回文件的手、Leonard 按住桌面的手、Zack 靠近的边缘信号 | 文件夹和两人的手处于清晰焦面；Danny 的肩/眼神在一侧突然转开；远端黄铜或玻璃反射中只出现 Zack 接近的模糊轮廓 | 文件夹从两手之间被猛然抽走，谈话在被撞见时中断 | 超宽文件/手部动作条，约 2.4—3.0 | 银行大厅、Danny、Leonard、房产证 |

### 9.4 生成语义

- 局部主体：房产证文件夹与两双手之间突然断开的私下交涉。
- Leonard：画面主动作仍是低声追问；职业面具只通过整齐袖口、收回手势和半张迅速恢复平静的面容表达。
- Danny：必须有“被发现后撤离”的动作起点，不要画成从容完成业务。
- Zack：只作为玻璃/黄铜反射、画面边缘衣袖或焦外靠近轮廓，不进入完整三人构图。
- 禁止：正式三方会谈、握手成交、钞票、钥匙特写、检举材料、铁盒、枪或完整大厅全景。

### 9.5 验收

- [ ] 第一眼读到私下文件交涉，第二眼发现有人接近。
- [ ] Danny 的动作是中断并撤离，不是正常离柜。
- [ ] Leonard 的职业化切换存在，但不演成明显反派表情。
- [ ] 玩家仍不知道“其他东西”的答案。
- [ ] 画面不是三人中景。

## 10. P03-L4：厕所门后的 Danny 与婚戒

### 10.1 任务信息

- 正式目标资产：`evt_l4_danny_bathroom_ring_01`
- 实验目录：`D:\NDC\NDC_project\test_output\imagegen\P03_L4_ring\local_closeup_v1\`
- 场景：Frank 家次卧与相邻厕所
- 图片触发对白：Danny：“喂！外头是谁？！我听见动静了！”
- 当前玩家知识：Zack 已在 Danny 床垫下找到 Margaret 的婚戒；Danny 被困在厕所。
- 叙事目标：同一画面完成“证物已到手”和“Danny 无法阻止”的权力倒置。

### 10.2 参考图

| 参考 | 路径 | 仅负责 |
| --- | --- | --- |
| 次卧 | `D:\NDC\Assets\Resources\Art\Scene\Backgrounds\EPI02\SC2409_bg_FrankHome_DannyGuestRoom_Night.png` | 黄昏/夜间次卧色阶与门口关系 |
| 厕所 | `D:\NDC\Assets\Resources\Art\Scene\Backgrounds\EPI02\SC2420_bg_FrankHome_Bathroom.png` | 旧厕所门、潮湿材质和年代感 |
| Zack | `D:\NDC\NDC_project\Art\角色卡\zack.png` | 持证物的手、袖口 |
| 婚戒 | `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE\EPI02\FrankHome_DannyGuestRoom\SC2409_item_05_big.png` | 单枚旧金婚戒、磨损、`P & M 1901` 刻字 |

### 10.3 帧计划

| frame | narrative instant | current player knowledge | forbidden reveal | local subject | close-up content/action | visual hook | provisional orientation/panel family | selected references |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P03-01 | Danny 在关着的厕所门后叫喊，Zack 在门外举起刚找到的婚戒 | 戒指藏在 Danny 房间；Danny 无法进入现场 | 不回演 Danny 如何拿到戒指；不解释火场真相；不把 Danny 画在次卧 | Zack 指间的婚戒、可读内圈刻字、后方关门与震动/门把信号 | 戒指和手处于极近焦面，`P & M 1901` 或对应磨损内圈可辨；后方厕所门和抖动门把焦外但可识别，门下窄光说明有人在内 | 金色戒指的稳定高光对比门把徒劳晃动 | 近方形证物/空间关系框，约 1.0—1.25 | 次卧、厕所、Zack、婚戒证物 |

### 10.4 生成语义

- 局部主体：Zack 已控制的婚戒，不是 Danny 的狼狈状态。
- Danny 不入镜；他的存在只通过关门、门把、门下光和对白成立。
- 戒指必须是一枚简约旧金圈，不能变成宝石戒指，不能误用 `F & L 1923` 求婚戒指。
- 喜剧只来自“声音很凶但门打不开”的反差，不能出现马桶、夸张姿势或厕所笑料特写。

### 10.5 验收

- [ ] 婚戒是唯一证物中心，数量和形制正确。
- [ ] `P & M 1901` 可辨或至少不出现错误刻字。
- [ ] Danny 不出现在次卧画面内。
- [ ] 关门关系足以说明 Danny 被困。
- [ ] 权力倒置强于喜剧效果。

## 11. P04-L4：隔窗放弃继承

### 11.1 任务信息

- 正式目标资产：`evt_l4_lula_window_waiver_01`、`evt_l4_lula_window_waiver_postexpose_01`
- 实验目录：`D:\NDC\NDC_project\test_output\imagegen\P04_L4_waiver\local_closeup_v1\`
- 场景：Frank 家旧厕所
- 图①触发对白：Lula：“Danny。”
- 图②触发对白：Danny：“不！我的房子！”
- 当前玩家知识：Danny 指控 Lula 图谋 Frank 的财产；Lula 准备当场放弃继承。
- 叙事目标：图①用法律文件击穿指控，图②用 Danny 的崩溃显示他同时失去遗产和最后一个替罪对象。

### 11.2 参考图

| 参考 | 路径 | 仅负责 |
| --- | --- | --- |
| 厕所 | `D:\NDC\Assets\Resources\Art\Scene\Backgrounds\EPI02\SC2420_bg_FrankHome_Bathroom.png` | 潮湿旧墙、小窗材质、冷暗色阶 |
| Lula | `D:\NDC\NDC_project\Art\角色卡\Lula Washington.png` | 手、袖口、平静局部目光 |
| Danny | `D:\NDC\NDC_project\Art\角色卡\Danny.png` | 狼狈局部面容、手和衣袖 |
| Zack | `D:\NDC\NDC_project\Art\角色卡\zack.png` | 图②必要时只提供一只稳定压住文件的手/袖口 |
| Mickey | `D:\NDC\NDC_project\Art\角色卡\miky.png` | 图②必要时只提供文件见证关系的手/袖口 |

没有现成放弃继承声明证物图。文件按 1920 年代律师声明格式生成，标题/签名区短文本可以存在，但不能依赖长文准确性。

### 11.3 帧计划

| frame | narrative instant | current player knowledge | forbidden reveal | local subject | close-up content/action | visual hook | provisional orientation/panel family | selected references |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P04-01 | Lula 从约 30×40cm 小窗把放弃继承声明递入，Danny 仰头看见 | Lula 否认贪图财产，并愿以法律文件证明 | 不揭示后续凶手或银行计划；不演成 Lula 愤怒报复 | 小窗、Lula 递入文件的手、Danny 接近文件却迟疑的手/局部眼神 | 窗框占据画面边界并明确狭小尺度；Lula 的手与声明从逆光外部进入，Danny 的上仰局部面容在室内阴影里 | 一张平整文件穿过极小窗口，切开 Danny 的强硬姿态 | 竖向窗框/文件关系框，约 0.70—0.88 | 厕所、Lula、Danny |
| P04-02 | 签字完成后，文件仍停在同一窗边，Danny 突然失控喊“我的房子” | 放弃声明已经生效；财产不归 Lula、Danny 或银行 | 不做追逐、拉扯或多人全景；不让 Lula 情绪失控 | 带签名的声明、同一窗框、Danny 抓向文件却停住的手和崩溃局部面容 | 保持图①窗框方向、纸张方向、Lula 袖口和光线连续；签名区/律师印记在前景，Danny 的嘴和眼睛进入同一近焦层；Zack/Mickey 最多用稳定的手或肩缘构成压力 | 文件上的签名/印记与 Danny 抓空的手形成“已经失去”的冲突 | 近方形偏竖连续反应框，约 0.82—1.02 | 同上，可加入 Zack/Mickey 局部 |

### 11.4 连续性要求

1. 两张必须使用同一窗框尺寸、同一开合方向、同一内外光向和同一纸张方向。
2. 图① Lula 的动作是平静递入/签署，图②依旧平静；情绪升级只发生在 Danny。
3. 飞书要求四人位置连续，但 Skill 不允许四人中景。执行时用 Lula、Danny 的局部作为主关系，Zack/Mickey 只以手、肩缘或文件见证动作保留位置，不展示四人完整站位。
4. 图②不是新的场景，而是图①数秒后的同一连续事件。

### 11.5 生成语义

- 图①局部主体：从狭小窗框递入的放弃继承声明与 Lula 稳定的手。
- 图②局部主体：已签署文件、Danny 抓空/停住的手和崩溃局部面容。
- 小窗必须确实读作约 30×40cm，不可扩大成普通窗户或门洞。
- 不出现完整厕所底图、完整马桶、四人站位、肢体拉扯或夸张喜剧。

### 11.6 验收

- [ ] 两张一眼可认作同一地点、同一窗框、连续数秒。
- [ ] 图①第一视觉中心是声明，Lula 冷静。
- [ ] 图②第一视觉中心是签字已完成与 Danny 失控。
- [ ] Danny 从强硬到恐慌的变化明确。
- [ ] 不通过全景满足“四人位置”，只保留必要局部关系。
- [ ] 正式挂载前复核飞书对白中“由 Frank……律师证明”一句的角色归属；该疑点不影响本轮出图。

## 12. P05-L5：Lula 带来铁盒

### 12.1 任务信息

- 正式目标资产：`evt_l5_lula_strongbox_01`
- 实验目录：`D:\NDC\NDC_project\test_output\imagegen\P05_L5_strongbox\local_closeup_v1\`
- 场景：Frank 家主屋，夜晚
- 图片触发对白：Lula：“不过，他给了我一个铁盒。”
- 当前玩家知识：Zack 与 Mickey 正在寻找 Frank 的检举材料；Lula 不知道材料具体是什么，但保管着 Frank 留下的铁盒。
- 叙事目标：同一画面让公共证据与私人感情两条线同时出现，但不进入 C06 的信件回忆。

### 12.2 参考图

| 参考 | 路径 | 仅负责 |
| --- | --- | --- |
| 场景 | `D:\NDC\Assets\Resources\Art\Scene\Backgrounds\EPI02\SC2518_bg_FrankHome_MainRoom_Night.png` | 主屋夜间光线、旧家具材质 |
| Lula | `D:\NDC\NDC_project\Art\角色卡\Lula Washington.png` | 捧信封的手、衣袖和克制情绪 |
| Mickey | `D:\NDC\NDC_project\Art\角色卡\miky.png` | 翻看材料的手、袖口和局部阅读关系 |
| 检举材料 | `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE\EPI02\FrankHome_MainRoom\SC2518_item_2502_big.png` | 成套卷宗、麻线、`A Statement Against Moore Bank` 标题和旧纸材质 |
| 私人情书 | `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE\EPI02\FrankHome_MainRoom\SC2518_item_2503_big.png` | Frank 笔迹与旧信纸；本帧只用于确认信件身份，不展示正文 |

没有独立的 Unit2 铁盒权威图。U1 safe-box 只能参考突发事件物件框的阅读节奏，不能复制其容器造型。本事件外层容器必须是飞书所述旧铁盒；不能擅自替换成 ItemStaticData 对未来公文包过场描述的棕色皮公文包。

### 12.3 帧计划

| frame | narrative instant | current player knowledge | forbidden reveal | local subject | close-up content/action | visual hook | provisional orientation/panel family | selected references |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P05-01 | 旧铁盒刚打开，Mickey 伸手查看检举材料，Lula 从另一侧捧起密封信封 | Frank 留下了重要东西；检举材料尚待确认 | 不展开信件正文、求婚计划或 C06 回忆；不揭示 Leonard/银行完整罪证链 | 打开的铁盒、成套卷宗、密封信封、两组不同动作的手 | 铁盒形成容器边界；卷宗标题和麻线在一侧，密封信封在另一侧；Mickey 的手压住卷宗，Lula 双手更轻地捧住信封 | 同一盒内“公共证据/私人情感”被两双手分开 | 横向物件关系框，约 1.65—2.10 | 主屋、Lula、Mickey、2502、2503 |

### 12.4 生成语义

- 局部主体：打开的旧铁盒内部，不是人物群像。
- 检举材料：必须是一叠有重量的正式卷宗，顶层可识别 `A Statement Against Moore Bank`，不能画成普通账本或单张纸。
- 私人信件：本帧应使用密封信封或只露出折叠信纸边缘，不展示 `My dearest Lula`、正文和署名。
- Mickey 与 Lula 的区别通过两双手的动作表达：Mickey 查证材料，Lula 小心捧起私人信件。
- 禁止：Frank 写信回忆、戒指、红玫瑰、完整信件正文、完整三人站位、棕色公文包替代铁盒。

### 12.5 验收

- [ ] 铁盒、检举材料和私人信件三者清楚区分。
- [ ] Mickey 与材料、Lula 与信件形成明确动作关系。
- [ ] 检举材料沿用正式证物的标题、装订和旧纸形制。
- [ ] 信件没有提前展开 C06 内容。
- [ ] 画面不是普通物品陈列，存在“刚打开、两条线同时被发现”的动作。

## 13. P06-L5：Foster 尸检反转

### 13.1 任务信息

- 正式目标资产：`evt_l5_foster_call_01`、`evt_l5_foster_call_02`
- 实验目录：`D:\NDC\NDC_project\test_output\imagegen\P06_L5_foster\local_closeup_v1\`
- 对白现场：鞋坊外电话亭
- 图①画面：圣心医院的工作室/值班工作台
- 图②画面：回看 Vinnie 被警员押走
- 图①触发对白：Foster：“我的尸检报告显示，Frank 并不是因为火灾被烧死的。”
- 图②触发对白：Foster：“他很可能是和某人博弈后，被钝器打击致死。”
- 当前玩家知识：Vinnie 已经认罪并去警局自首，Zack 与 Emma 以为案件即将结束。
- 叙事目标：图①用客观报告推翻“烧死”，图②让玩家重新审视 Vinnie 的认罪，但不能确认他在顶罪。

### 13.2 参考图

| 参考 | 路径 | 仅负责 |
| --- | --- | --- |
| Foster | `D:\NDC\Assets\Resources\Art\Scene\NPC\EPI02\SC2606_npc_Foster1.png`、`SC2606_npc_Foster2.png` | Foster 身份、年龄、脸和服装；只截取局部 |
| 医院色阶 | `D:\NDC\Assets\Resources\Art\Scene\Backgrounds\EPI02\SC2621_bg_SacredHeartHospital.png` | 圣心医院墙面、木地板、油灯/暖光与冷绿色阶；不复制病床构图 |
| Vinnie | `D:\NDC\NDC_project\Art\角色卡\Vinnie Moretti.png` | 脸型、发型、服装、帮派人物身份 |

当前没有权威“尸检工作室”背景，也没有正式尸检报告证物图。因此图①应生成 1920 年代医院值班工作台的局部：木桌、黑色电话、打字报告、台灯/油灯。不得把 `SC2621` 的病床直接搬入画面，也不得发明现代法医实验室设备。

### 13.3 帧计划

| frame | narrative instant | current player knowledge | forbidden reveal | local subject | close-up content/action | visual hook | provisional orientation/panel family | selected references |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P06-01 | Foster 一手夹住电话听筒，一手展开并指向尸检结论 | Vinnie 已认罪；众人以为 Frank 死于火灾 | 不展示尸体、伤口、血；不暗示 Leonard 或银行；不确认凶器 | 尸检报告、Foster 指向结论的手、电话听筒和严肃局部面容 | 报告占画面中心，Foster 手指停在两条短结论附近；听筒压在肩/手边，半张脸保持克制；木桌与旧式台灯只作环境 | 纸面结论把电话线另一端的“结案”突然切断 | 近方形报告/人物关系框，约 1.0—1.25 | Foster NPC、医院色阶 |
| P06-02 | 在“钝器打击”说出口时回看 Vinnie 被押走，他低头且只有若有若无的平静异常 | 尸检已推翻火灾死因；Vinnie 的认罪出现矛盾 | 不确认顶罪动机；不出现 Leonard、银行标志、枪、凶器；不做得意笑容 | Vinnie 低垂局部面容、被控制的手/袖口、警员衣袖边缘 | 竖向近景只保留 Vinnie 眼睛、嘴角和一段被押住的肩/腕；嘴角接近中性，眼神平静但不正视镜头；警员只以手和制服边缘存在 | 平静微表情与被押状态之间的不协调 | 竖向人物压力框，约 0.68—0.84 | Vinnie 角色卡；警员只作匿名局部 |

### 13.4 图①生成语义

- 局部主体：尸检报告上的结论与 Foster 指向纸面的手。
- 报告可以出现少量打字行、解剖报告版式和两条短划线/圈记；不能依赖长段准确文字。
- 若生成可读短句，含义只能是“非火灾致死”和“钝器伤”，不得写出凶器、凶手或推测对象。
- 电话必须是 1920 年代样式，纸张、灯具和桌面符合年代。
- Foster 的表情严肃克制，不能惊恐、兴奋或阴谋化。

### 13.5 图②生成语义

- 局部主体：Vinnie 低头被押走时的眼睛、嘴角和被控制的局部动作。
- “极轻上扬”必须接近中性；只让玩家产生回看疑问，不能读成嘲笑、得意或阴谋成功。
- 不正面对镜头，不做英雄化逆光，不表现牺牲感。
- 不需要警局/街道全景；警员只保留手、袖口、肩缘或手铐链的一小段。

### 13.6 验收

- [ ] 图①报告是第一视觉中心，电话关系清楚。
- [ ] 图①不出现尸体、血、现代设备或具体凶器。
- [ ] 图②能识别 Vinnie，但不是完整人物或逮捕全景。
- [ ] 图②微表情足够轻，不能得意、挑衅或阴谋化。
- [ ] 两张只制造“案件没有结束”的疑问，不揭示 Leonard 或银行。
- [ ] 图①和图②形成“客观事实反转 → 回看旧画面”的明确顺序。

## 14. P07-L6：Edith 提箱离开

### 14.1 任务信息

- 正式目标资产：`evt_l6_edith_suitcase_leave_01`
- 实验目录：`D:\NDC\NDC_project\test_output\imagegen\P07_L6_edith\local_closeup_v1\`
- 场景：Leonard 住宅
- 图片触发对白：Leonard：“Edith……你拿着箱子做什么？你回去！”
- 当前玩家知识：Leonard 的说辞正在崩塌，Edith 已在楼上听见质问，并知道他处理过沾血的西服。
- 叙事目标：Edith 的冷静离开成为压垮 Leonard 心理防线的情感打击。

### 14.2 参考图

| 参考 | 路径 | 仅负责 |
| --- | --- | --- |
| 场景 | `D:\NDC\Assets\Resources\Art\Scene\Backgrounds\EPI02\SC2617_bg_LeonardResidence.png` | 样板间式整洁、公寓材质和光线 |
| Edith | `D:\NDC\NDC_project\Art\角色卡\Edith Ross.png` | 手、服装、冷静失望的局部面容 |
| Edith 场景 NPC | `D:\NDC\Assets\Resources\Art\Scene\NPC\EPI02\SC2617_npc_Edith1.png`、`SC2617_npc_Edith2.png` | 场景内服装与色阶校准 |
| Leonard | `D:\NDC\NDC_project\Art\角色卡\Leonard Ross.png` | 伸手、衣袖和恐慌局部面容 |
| Leonard 场景 NPC | `D:\NDC\Assets\Resources\Art\Scene\NPC\EPI02\SC2611_npc_Leonard1.png`、`SC2611_npc_Leonard2.png` | 场景版本服装参考；不得照搬不匹配的站位 |

没有权威手提箱证物图。手提箱应为 1920 年代硬壳皮箱或皮革旅行箱，尺寸和磨损足以表达短期离家，不做现代拉杆箱。

### 14.3 帧计划

| frame | narrative instant | current player knowledge | forbidden reveal | local subject | close-up content/action | visual hook | provisional orientation/panel family | selected references |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P07-01 | Edith 平静握住箱柄向门外转身，Leonard 慌乱伸手却不敢碰她 | Leonard 的体面已经动摇；Edith 准备离开 | 不表现追逐、扭打、强行拉扯；不提前给出 Leonard 完整认罪结果 | Edith 稳定握箱柄的手、箱体边缘、Leonard 悬停的手和恐慌局部面容 | 箱柄与 Edith 的手处于第一焦点；Leonard 的手从后方伸来却停在几厘米外，半张慌乱面容处于次近焦层；公寓只保留整洁门框/家具边缘 | 一只稳定向外的手与一只不敢触碰的手形成控制权逆转 | 横向手/箱/反应关系框，约 1.55—1.95 | Leonard 住宅、Edith、Leonard |

### 14.4 生成语义

- Edith：动作小、稳定、已经作出决定；情绪是冷静和失望，不是哭喊或愤怒爆发。
- Leonard：恐慌通过悬停的手、失去控制的局部眼神和张口欲阻止表达，不做跪地、追逐或抓扯。
- 手提箱：必须清楚表达“准备离开”，但不要占满画面成为商品图。
- 场景：只保留整洁门框或样板间家具边缘，不能展示复式公寓全景。
- 禁止：现代拉杆箱、肢体冲突、完整双人站位、Edith 回头争吵、Leonard 已经伏法的结果。

### 14.5 验收

- [ ] 第一眼读到 Edith 已经带箱离开。
- [ ] Edith 冷静，Leonard 恐慌，情绪方向不能颠倒。
- [ ] Leonard 的手没有抓住 Edith。
- [ ] 不做追逐、拉扯或双人中景。
- [ ] 手提箱年代正确，场景仍能识别为 Leonard 住宅。

## 15. 推荐执行顺序

建议按以下顺序逐张生成和审查：

1. **P01-01 电报**：先校准“纸面证物 + 双人局部反应”，风险最低。
2. **P03-01 婚戒**：用现成权威证物校准刻字、证物形制和空间关系。
3. **P05-01 铁盒**：校准多道具但单一叙事中心的物件关系框。
4. **P02-01 银行偷听**：处理多人只以局部出现和“被撞见”的复杂动作。
5. **P04-01、P04-02 放弃继承**：连续生成并锁定窗框、纸张、袖口和光向。
6. **P07-01 Edith 离开**：处理双人情绪反差但避免拉扯。
7. **P06-01、P06-02 Foster 反转**：最后处理报告文字可靠性和 Vinnie 极轻微表情，两张均为高风险项。

每一阶段通过后再进入下一阶段。P04 与 P06 必须按同一事件连续审查，不能只接受其中一张便进入正式交付。

## 16. 每张交付物与正式资产映射

| 工作帧 | 实验原图 | 正式目标资产名 |
| --- | --- | --- |
| P01-01 | `P01-01_raw.png` | `evt_l1_office_telegram_01` |
| P02-01 | `P02-01_raw.png` | `evt_l2_overhear_danny_leonard_01` |
| P03-01 | `P03-01_raw.png` | `evt_l4_danny_bathroom_ring_01` |
| P04-01 | `P04-01_raw.png` | `evt_l4_lula_window_waiver_01` |
| P04-02 | `P04-02_raw.png` | `evt_l4_lula_window_waiver_postexpose_01` |
| P05-01 | `P05-01_raw.png` | `evt_l5_lula_strongbox_01` |
| P06-01 | `P06-01_raw.png` | `evt_l5_foster_call_01` |
| P06-02 | `P06-02_raw.png` | `evt_l5_foster_call_02` |
| P07-01 | `P07-01_raw.png` | `evt_l6_edith_suitcase_leave_01` |

正式资产名在实验阶段只作为映射，不提前写入 `Assets/Resources/Art/Scene/Emergency/EPI02`。

## 17. 批次验收清单

### 17.1 数量与命名

- [ ] 共 7 个事件、9 张原始候选。
- [ ] 9 个正式目标资产名与飞书最终工作表逐字一致。
- [ ] P06-L5 与 Loop6 的 P06 不混用目录、文件或编号。
- [ ] Loop6 遗书事件继续沿用上次 C08 的两张安全近景，不重出。

### 17.2 叙事

- [ ] 每张都能对应一条明确触发对白。
- [ ] 每张只表达当刻玩家已知信息。
- [ ] P01 不解释 Mickey；P02 不回答“其他东西”；P05 不展开情书；P06 不确认顶罪和保护对象。
- [ ] P04 两张、P06 两张分别形成清楚的连续/反转关系。

### 17.3 美术

- [ ] 9 张全部是局部或极局部特写。
- [ ] 角色身份与参考图一致，主体手、脸、证物和接触点清楚。
- [ ] 没有完整人物、多人整齐站位、建立镜头、全景或伪裁切近景。
- [ ] 道具年代正确：电报、电话、报告、声明、铁盒、皮箱均不现代化。
- [ ] 证物正确：P03 只能是 `P & M 1901`；P05 检举材料沿用正式证物形制。

### 17.4 安全与技术

- [ ] 不出现尸体、血腥、上吊、绳索、枪、凶器或新增暴力细节。
- [ ] 原图无黑边、透明角、红框、字幕、UI、水印和说明文字。
- [ ] 原图通过后再制作 panel design、黑边透明面板和洋红蒙版。
- [ ] 四角 alpha=0，中心主体 alpha=255；面板不裁断关键证物、手或脸。
- [ ] 原图通过后不追加 AI 简化流程；只有硬性违规允许一次针对性重试。

## 18. 本轮边界与后续步骤

本需求文档只授权“生成实验候选并审查”。以下动作不在本轮范围内：

- 覆盖或新增正式 Emergency 美术资源。
- 修改 Talk、SceneConfig 或其他正式配置。
- 修改 `res/xls/*.xlsx`、生成 JSON 或 bytes。
- 决定最终面板坐标、左右站位、Talk 挂载行和清除节点。

9 张候选全部通过并获得逐张批准后，再单独执行正式交付和 Talk 挂载流程；届时必须继续遵守 Excel-first 和可回退要求。
