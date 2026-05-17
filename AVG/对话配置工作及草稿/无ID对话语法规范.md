# 无ID对话草稿语法规范 v0.2

适用范围：Unit10 起的对话 MD 草稿（Talk + Expose）。Unit9 及更早草稿沿用旧的九位 ID 格式，不回溯。

核心变化：**MD 草稿不再手写 9 位对话 ID**。节点靠角色发言块自然分隔；分支、证据/证词提取、Expose 谎言一律用行首 `@` 指令书写——脚本可确定解析、可校验。9 位 ID 由后置预处理器 `assign_ids.py` 按出现顺序统一补（该脚本待 ID 体系定稿后实现，本规范先定语法）。

设计原则：**语法以写手书写自然、人读顺畅、机器确定解析为第一优先**。`sync_to_json.py` / 预处理器适配本语法，不让脚本现状限制语法表达力。

---

## 1. 节点边界（替代 `### 数字ID`）

一个**角色发言块** = 一个对话节点：

```markdown
**扎克·布伦南** [动作描述]
> 台词第一句
> 台词第二句
```

- 触发节点的是 `**角色名**` 行；其下连续 `>` 行属于同一节点
- 节点之间用空行分隔
- `**角色名**` 后可跟 `[动作/情绪描述]`，可省略
- 单节点内可写多句 `>`；拆句、单句 ≤35 字的处理交给后置工序，写手专注内容与节奏
- 纯画面/转场/NPC 静默反应：用 `<!-- -->` 注释，**不**写成发言块（不成为节点）
- 承载 `@get` / `@branch` / `@lie` 等机制的发言块必须保留（机制锚点）

## 2. section 头（保留不变，sync 靠它分文件）

```markdown
## §N. Scene {scene_id} — {人类可读描述}
## Talk: {npc}_{conv}.json
## Expose: Loop{N}_{npc}.json
```

section 头与对话 ID 无关，照旧书写。

## 3. 分支指令

| 指令 | 语义 |
|------|------|
| `@branch <分支名>` | 分支组开始。其紧邻上一个发言块即"选项触发句" |
| `@opt "<选项文本>" -> <标签> # <信息维度>` | 一个玩家选项，跳到某 `@path` |
| `@path <标签>` | 一条分支路径开始 |
| `@goto <标签>` | 当前路径在此跳到目标标签（通常是汇合点） |
| `@label <标签>` | 定义一个跳转目标 |

- `<标签>` 用语义化英文/拼音小写名（如 `gun_owner`、`merge`），不用数字
- 信息维度取值：身份/关系、时间线、事件/线索、情绪/态度、背景/环境（见 `.claude/rules/dialogue.md`）
- 每个分支组 `@opt` ≥ 2；每条 `@path` 必须以 `@goto` 收束（禁止永久分叉）

样例：

```markdown
**扎克·布伦南** [声音压低，只够两个人听见]
> 我有几句话得问清楚。
@branch 追问方向
@opt "你有没有开过这把枪？" -> gun_fired   # 事件/线索
@opt "你需要坐下来吗？"     -> sit_down    # 情绪/态度
@opt "这把枪——是你的吗？"  -> gun_owner   # 身份/关系

@path gun_fired
**薇薇安·罗斯** [眼神像在看他后面]
> 我……不知道。
@goto merge

@path sit_down
**薇薇安·罗斯** [停了很久]
> 我不知道我在哪……
@goto merge

@path gun_owner
**薇薇安·罗斯**
> 是……
@get 证词 1030001 "Vivian：蓝月亮酒吧的歌女" #identity
@goto merge

@label merge
**扎克·布伦南** [把话题收回]
> 好，我们从头说。
```

## 4. 证据/证词提取指令 `@get`

```markdown
**扎克·布伦南** [盯着枪]
> 这把枪——是你的吗？
@get 证词 1030001 "Vivian：蓝月亮酒吧的歌女" #identity
```

- 格式：`@get {证词|证据} {ID} "{摘要}" #{keyInfoType}`
- 挂在紧邻的上一个发言块上
- ID 是 state / 配置表里的**真实数据**：证词 7 位、证据 4 位，写手必须照抄，不可省略或编造
- `keyInfoType` 取值：identity / timeline / statement（见 `.claude/rules/dialogue.md`）
- 两次 `@get` 之间至少间隔 3-5 个普通节点

## 5. Expose 指证指令

| 指令 | 语义 |
|------|------|
| `@round <N>` | 第 N 轮指证开始 |
| `@lie anchor=<testimony_id>` | 本轮谎言锚；anchor 引用 Talk 中已可收集的证词 ID。其后发言块是谎言台词 |
| `@evidence "<证据名>" -> <标签> #correct` | 能击穿本轮谎言的正确证据 |
| `@evidence "<证据名>" -> <标签> #trap "<陷阱理由>"` | 陷阱证据，必须写明"看似相关但不构成反驳"的理由 |
| `@label` / `@goto` | 同分支语法，用于退守对白与轮次衔接 |

- 每轮至少一个 `#correct` 证据
- 第 1 轮 `@lie anchor` 必须对应 Talk 中已收集的证词（Expose 第一谎言规则）
- 后续轮谎言是嫌疑人被逼出的新谎言（止损式），由嫌疑人主动说出，不是 Zack 喂话
- `#trap` 必须带理由（落实三大原则"陷阱有逻辑"）

样例：

```markdown
## Expose: Loop1_morrison.json

@round 1
@lie anchor=1010001
**莫里森** [翻记事本]
> 死者……应该就是 Margaret 本人。
@evidence "死者无婚戒"     -> r1_break #correct
@evidence "首饰盒空置"     -> r1_break #correct
@evidence "现场无金属残留" -> r1_break #trap "只证未焚烧，不证伪身份"

@label r1_break
**莫里森** [脸色变了]
> ……尸检还没出，我只是按惯例推断。
@goto round2

@round 2
@lie anchor=null
**莫里森**
> 那也不能说明死的不是她。
...
```

## 6. 预处理器 `assign_ids.py` 职责（待实现，本节定契约）

输入：本规范格式的无 ID MD。输出：`sync_to_json.py` 可直接消费的标准 MD（含补好的 9 位 ID + `### ID \`branches\`` / `### ID \`get\`` / `### ID \`Lie\`` 等）。

- 按发言块出现顺序连续分配 9 位对话 ID（ID 编码方案由 Unit10 ID 体系定稿后注入，本规范不固化具体值）
- `@path X` 首节点 ID = 对应 `@opt ... -> X` 的跳转目标
- `@goto Y` → 本路径末节点 next 指向 `@label Y`（或 `@path Y`）首节点
- `@get` → 翻译为 `### ID \`get\` → {配置ID}` + keyInfo 注释
- `@lie` / `@evidence` → 翻译为 Expose 的 Lie 节点 + 出示证据选项

### 强制校验（FAIL 即拦截，不产出）

1. `@opt` 指向的标签无对应 `@path` → FAIL
2. 存在未被任何 `@opt` 指向的 `@path`（孤儿分支）→ FAIL
3. 某条 `@path` 未以 `@goto` 收束（永久分叉）→ FAIL
4. `@goto` 目标未定义（无对应 `@label` / `@path`）→ FAIL
5. 同名 `@label` / `@path` 重复定义 → FAIL
6. 一组 `@branch` 的 `@opt` 数 < 2 → FAIL
7. `@get` ID 位数不符（证词≠7 位 / 证据≠4 位）→ FAIL
8. `@get` / `@lie anchor` 引用的 ID 在配置表查无 → FAIL
9. 某 `@round` 无 `#correct` 证据（谎言击不穿）→ FAIL

### 警告（WARNING，不拦截）

- `@opt` 缺 `# 信息维度` 注释
- `@evidence #trap` 缺陷阱理由
- 两次 `@get` 间隔 < 3 节点

## 7. 速查

```
节点      **角色名** [动作] + 下方 > 台词行
画面      <!-- 注释 -->（不成节点）
分支      @branch 名 / @opt "文本" -> 标签 #维度 / @path 标签 / @goto 标签 / @label 标签
提取      @get 证词|证据 ID "摘要" #keyInfoType
指证      @round N / @lie anchor=ID / @evidence "名" -> 标签 #correct|#trap "理由"
不写      任何 9 位对话 ID（后置预处理器补）
保留      ## §N. Scene / ## Talk: / ## Expose: section 头
```
