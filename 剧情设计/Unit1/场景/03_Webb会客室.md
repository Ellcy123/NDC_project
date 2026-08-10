# 03 Webb 会客室

**state ID**：`1003`（90xx = 场景命名空间；全 6 Loop 共用此 ID）

**位置**：1F 南侧（案发现场）
**戏剧作用**：本案所有循环的核心场景。James 厨房正下方，诡计物理基础所在。

---

## Loop 1

**状态**：出现（现场搜证）
**场景类型**：⏸️ 有限自由探索（Morrison 管控现场）
**解锁条件**：开篇 23:30 枪响后随 opening 自动进入

### 场景描述
Webb 死亡现场——Morrison 控制进入权限。Vivian 仍持枪站在原地，身上带有酒气、眼神涣散、半醉失神，对追问基本没有反应。Rosa 在场，玩家在自由探索阶段即可通过与 Rosa 对话获取其谎言证词（谎言1 + 谎言2）。玩家可以检查 Vivian 手中的小手枪（可分析硝烟），并找到 Webb 的委托协议书。

### NPC 列表
| NPC | is_liar | 关键证词 |
|---|:---:|---|
| Vivian | false | 1061001（身份：歌女）；酒后失语，追问无回应 |
| Rosa | true（Expose 对象） | 1031001（谎言1：Vivian 手里有枪）/ 1031002（谎言2：23:30 枪响只有 Vivian 在场）/ 1031003 |
| Morrison | false | 1041004（身份）；宣告 Webb 死亡 / 逮捕 Vivian / 指证后 72h 均为剧情陈述（不收集为证词） |

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 1101 | Vivian 的小手枪 | item | ✅ | 关键——L1 R1 击穿前置；可分析硝烟 |
| 1711 | 无硝烟的手枪（分析派生） | item | ❌（分析后自动）| 关键——L1 R1 击穿件；疑点 1101 condition |
| 1103 | Webb 委托协议书 | item | ✅ | 关键——换取 72h 调查期；非指证击穿件 |

---

## Loop 2

**状态**：出现（🔒 Locked — Morrison 勘验中）
**场景类型**：🔒 Locked
**解锁条件**：Morrison 现场勘验中，L3 才开放

### 场景描述
1F 南侧 Webb 会客室，仍处于 Morrison 的犯罪现场勘验控制之下。L2 全程不可进入——保护 L3 才开放的玻璃碎片 / 保险箱字条等关键证据不提前泄露。

### NPC 列表
无

### 可获取证据
无

---

## Loop 3

**状态**：出现（深度搜证）
**场景类型**：🔓 自由探索（L3 正式开放）
**解锁条件**：Morrison 勘验完成后开放

### 场景描述
Webb 死亡的案发现场，本 Loop 首次对玩家正式开放。Morrison 完成勘验后离开，Zack 可独立搜证。关键发现：没有玻璃的窗户——Zack 向窗外侧巷望去，见到垃圾袋正压在碎玻璃上。需要走出员工侧门到侧巷（08_一楼侧巷）取回玻璃碎片。会客室内还有保险箱字条、Webb+Vivian 合影（可拾取）、Webb 勒索他人的日记（扉页写 Whale—Danger，可拾取）、Rita 的照片（环境陈设）。

### NPC 列表
无（搜证阶段无 NPC 驻场）

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 1304 | 保险箱字条（密码=相遇日） | item | ✅ | 关键——疑点 1303 condition；L4 R3 击穿件；正式 L6 只显示已打开的保险箱，未再次执行密码动作 |
| 1305 | Webb 和 Vivian 的合影 | item | ✅ | 关键——疑点 1303 condition；揭示 Webb 仍记挂 Vivian |
| 1307 | Rita 的照片 | envir | ❌ | 场景道具——显示 Rita 存在感 |
| 1308 | Webb 的勒索记录日记（扉页写 Whale—Danger） | item | ✅ | 叙事证据——Whale 名字的首次物证（Webb 亲笔警觉，比 Emma opening 口述的重量更大）；不挂疑点；不可分析 |
| 1301 | 玻璃碎片（压垃圾袋下有硝烟） | item | ✅ | 关键——疑点 1301 condition；L3 R1 击穿件；须从侧巷拾取 |

---

## Loop 4

**状态**：出现（指证 Vivian 场所）
**场景类型**：⚔️ Expose（指证场所，expose.scene_id = 1003）
**解锁条件**：L4 Expose 阶段

### 场景描述
L4 指证 Vivian 的舞台。Vivian 在此坚持认罪，Zack 必须用 3 轮谎言击穿把她救出来（弹壳口径、Whale 雇人已行动、保险箱字条）。post_expose 剧情：Morrison 进入会客室后触发 turn_cutscene（看到 .45 弹壳变脸，强押 Vivian）。

### NPC 列表
| NPC | is_liar | 角色 |
|---|:---:|---|
| Vivian | true | L4 Expose 对象；自毁式认罪，三轮谎言：弹壳论 / 无人能杀 / Webb 早已忘了我 |

### 可获取证据
无（L4 在会客室不新增证据；本 Loop 指证用的证据来自其他场景：1007 酒吧一楼走廊 / 1010 Tommy 办公室 / 1002 Vivian 化妆室 + L3 继承的物证 1304 / 1401）

---

## Loop 5

**状态**：未出现
**说明**：L5 Expose 发生在蓝月亮酒吧后门 (arrest_cutscene)，不在会客室。Vivian 已被 Morrison 押走，会客室此 Loop 不再开放。

---

## Loop 6

**状态**：出现（ending_sequence Act3 + Act4 就地完成）
**场景类型**：🎬 Cutscene（forced_cutscene，封条已撤；Vivian 主导 Act3 → 退场后 Zack/Emma 在 Act4 听碎片）
**解锁条件**：Expose Morrison 完成 + Vivian 释放后，ending_sequence Act3 自动进入

### 场景描述
正式 ending 已切到 Webb 办公室（Scene 1628）。Vivian 已经打开保险箱，从深处取出唱片碎片，交给 Zack 和 Emma 去拼。正式 Talk 没有表现使用 1304 的动作，也没有执行 `get 1602`；1602 在此是剧情展示物。Vivian 说「这间屋子里的事，从今天起，就和我无关了」后退场。

Zack 和 Emma 单独留在 Webb 办公室，拼好碎片并播放。正式运行版由六个 itemShowNode 依次给出：

1. 「银月」
2. 「湖滨信托」「南区」
3. 「名单」「第一批」
4. 「Margaret Brennan 的鞋坊」
5. 「钉子」「十一月初」
6. 「不留后患」

Emma 判断这是 Whale 的计划，并追问 Margaret Brennan 是谁 → Zack 确认「那是我母亲的名字」→ Emma 惊问 → Zack 指出今天已经是 11 月 6 日 → `loop_end`。正式运行版没有离开 Webb 办公室后的车内或火场段。

### NPC 列表
| NPC | is_liar | 角色 |
|---|:---:|---|
| Vivian | false | Act3 主导：开保险箱 + 交付碎片 + 主动退场 |
| Emma | false | Act4 协助：辨认录音信息并追问 Margaret 的身份 |

### 可获取证据
| ID | 名称 | 类型 | 可拾取 | note |
|---|---|---|:---:|---|
| 1602 | "南区计划"录音盘碎片 | item | ❌ | ItemStaticData 已存在；正式 Talk 只作剧情展示，没有 `get 1602`，不能视为已入包或已跨章持有 |

### 关键道具：墙角留声机
Webb 留下的老式播放设备。Act4 在此播放碎片；表现由正式 Talk 的 itemShowNode 和 `Audio/TalkAudio003` 时间切片控制。

### 后续：正式运行版终点
听完后本 Loop 在 Zack 的「今天已经是 11 月 6 日了」处结束。旧版离开 Webb 办公室、上车与鞋坊火场方案已移入迁移归档。
