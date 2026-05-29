---
name: config-edit
description: "改 NDC 编辑器配置表（avg_editor_v2/data/table）。用自然语言说要改什么，skill 负责：定位到对的表/字段、连带处理互相影响的关联表、改前阐述理解给用户确认、改后基线对比自校验。触发：用户说'改配置/改表/把X改成Y/这个证据(场景/NPC/疑点/指证/底图/美术需求/突发事件)改一下'等。即使改动很小也走完整流程。不改 Unity / 不改对白(Talk 走 AVG 管线)。"
argument-hint: "[自然语言描述要改什么，如：把 2204 威胁便条英文改成文档版]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit, Bash, AskUserQuestion
---

# config-edit — 配置表安全改动流程

帮用户改 `D:\NDC_project\avg_editor_v2\data\table\*.json`。核心承诺：**改得对、关联表一起改、改前讲清楚、改后自校验、不许改坏**。

**开工前必读**：
- [config-rules.md](config-rules.md)（数据源、外键关系图、ID 编码、可改字段白名单、设计期新表、语义规则）
- [pitfalls.md](pitfalls.md)（实战踩坑：comic 坐标换算、全屏图vs叠图、证据获得时机、地图状态链、旧残留引用，以及下游 Talk/Unity 交接提醒）

## 边界
- 只改 `avg_editor_v2/data/table`。绝不碰 Unity(`D:\NDC\Assets\table`)、`res/xls`、`preview_new2`。
- 不改对白：`Talk` 由 AVG 管线（sync_to_json）维护，本 skill 不动 Talk 文本；只在关联检查里提示"这句被某 Talk 引用"。
- 改动无论多小，五段流程一段不少。

## 流程（5 段）

### Phase 0 · 理解 + 定位（内部）
1. 把自然语言解析成：**哪张表 / 哪条(主键) / 哪个字段 / 旧值 → 新值**。
2. 读 config-rules.md，用外键关系图判定**连带影响**：这条改动牵连哪些别的表的哪些字段。
3. 查可改字段白名单；超出白名单或触及外键（如改 id、改 ExposeData/DoubtConfig.condition）→ 标记为"高风险"，Phase 1 里重点说明。
4. 跑语义规则核对（Item vs Testimony、疑点归属 Loop、时间线文本、底图 sceneKind 唯一性等）。

> 定位不确定（多条匹配、指代不清）→ 用 AskUserQuestion 问清，**不猜**。

### Phase 1 · 阐述理解（必须输出给用户，等确认）
固定格式：
```
【理解】要改 <表>.<字段>，pk=<主键>
        旧：<旧值>
        新：<新值>
【关联影响】<A表.字段> 需同步为 <…>；<B表.字段> 受影响 <…>
            （或：无关联表受影响）
【语义校验】符合/违反 <哪条规则>
【风险】<是否触及外键/改主键/高风险；如无写"低，纯文案">
是否执行？
```
等用户"对/可以/执行"。用户纠正 → 调整后重新阐述，直到确认。

### Phase 2 · 落地
1. **基线**：`cd .claude/skills/config-edit && python validate.py --save .ce_baseline.json`
2. **备份**：对每个要改的表 `copy {表}.json {表}.json.bak.{时间戳}`。
3. **改主字段 + 所有关联表**：用 Edit 精确改 JSON（保持缩进/编码 utf-8）。关联表的同步改动一并做掉，不留半套。
4. 游戏数据字段改完，提醒用户：此改动仅在编辑器生效；如要进游戏，需另走 Unity 同步（不在本 skill）。

### Phase 3 · 自校验（硬闸门）
```
python validate.py --compare .ce_baseline.json
```
- 退出码 0、无"新增 ERROR" → 通过。
- 出现"新增 ERROR"（本次改动引入了断链/破坏）→ **回滚**（用 .bak 还原），向用户报告哪条断了，不留半成品。
- 历史欠债不阻断；若顺手修复了既有断链，脚本会报告。

### Phase 4 · 收尾
- 给最终 diff 摘要（改了哪些表哪些条）。
- 删基线文件 `.ce_baseline.json` 和（确认无误后）多余 `.bak`（或保留备份，按用户偏好）。
- 涉及前端展示字段（sceneKind/events/loop/isOpen/ArtRequirement）的，提示用户刷新编辑器页面查看。

## 批量改动
多条同类改动（如一次补 14 个英文名）：Phase 1 用清单一次性阐述全部条目→确认→Phase 2 批量改（可写一次性 py 脚本，带备份）→Phase 3 一次校验。不要一条条问。

## 关键纪律
- LLM 不凭记忆编字段值；改前读对应表确认现状。
- 改 id / 外键字段 = 高风险，Phase 1 必须显式列出所有被引用处。
- 校验是闸门不是建议：不过（新增 ERROR）就回滚。
- 拿不准就问，别猜（呼应项目"修改前先举例确认"原则）。
