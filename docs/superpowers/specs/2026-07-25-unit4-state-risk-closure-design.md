# Unit4 State 风险收口设计

> 日期：2026-07-25
> 状态：用户已批准 B 方案
> 范围：NDC_project 仓库侧 State、落表契约与自动校验
> 不在范围：Unity 运行时代码、正式配置表 JSON 写入、L5 最终美术与交互实现

## 一、目标

关闭 Unit4 State 风险清单中的前七项，使五份 State 同时满足：

1. L5 身份锁不再保留玩法层待定项。
2. L5 明确绕过普通疑点进度，以三链完成作为 Expose 唯一门槛。
3. 场景 `type` 使用稳定、可映射的 State 基础类型。
4. 所有扩展顶层字段都有机器可读的落表分类。
5. L5 所需跨 Loop 材料具有章节级持久化契约。
6. L3 非进度调查结论有明确的玩家展示与非阻塞规则。
7. 非 Loop 终幕明确归属 L5，并只在最后节点触发结章。

## 二、方案选择

采用契约驱动方案：

- 五份 State 继续作为剧情与关卡蓝图。
- 新增 `state_contract.yaml`，作为 Unit4 State 扩展字段、持久化和特殊机制的机器可读真源。
- 新增 Ruby/Psych 校验器与 Minitest 测试，不引入第三方依赖。
- 不直接修改 `avg_editor_v2/data/table/*.json`，避免在玩法尚未进入 Unity 实现时制造孤立运行时字段。

不采用：

- 只改文字而不校验：无法阻止后续回归。
- 直接扩展 `avg_editor_v2/fill_from_state.py`：该脚本目前是 Unit2 专用并会写表，超出本次范围。

## 三、场景类型契约

### 3.1 基础类型

Unit4 `scenes[].type` 只允许：

- `cutscene`
- `free_exploration`

指证归属由顶层 `expose.location` 和表关联推导，不使用复合自造枚举。

### 3.2 设计标签

复杂功能保留在 `design_tags`。以下十项是 Unit4 当前契约词表，不是示例枚举：

- `opening`
- `transition`
- `analysis`
- `crisis`
- `aftermath`
- `action_result`
- `expose_location`
- `locked`
- `identity_lock`
- `story_climax`

示例：

```yaml
- id: 4042
  type: free_exploration
  design_tags:
    - identity_lock
    - expose_location
    - story_climax
```

`design_tags` 为设计期字段，不直接写入正式 SceneConfig。

## 四、L5 身份锁契约

### 4.1 布局与提交

- 三条证明链同时开放。
- 每条链显示固定材料槽。
- 玩家填满当前链后主动点击“验证”。
- 已完成链固定显示派生结论，不允许回退或被错误提交重置。

### 4.2 失败反馈

- 错误提交不消耗证据。
- 错误提交不清除已完成链。
- 第一次错误只提示逻辑维度不成立。
- 同一链连续第二次错误提示缺少的信息维度。
- 提示不得直接点名正确证据 ID。

### 4.3 Expose 门槛

```yaml
gate_contract:
  standard_doubt_progress_required: false
  completion_condition: all_chains_completed
  unlocks: expose
```

L5 必须满足：

- 不存在顶层 `doubts`。
- `special_mechanics.identity_lock.replaces_standard_doubts: true`。
- 三条链完成后才允许触发 `mickey_returns` 与 Expose。

## 五、字段分类与落表政策

`state_contract.yaml.field_policy` 使用四种分类：

| 分类 | 含义 |
|---|---|
| `runtime_source` | 可转换为现有正式配置表字段 |
| `design_only` | 只供策划、审查和编辑器表现使用 |
| `special_adapter` | 需要专门适配器；不得由通用转换器猜测 |
| `structural` | State 文件结构字段，不直接对应单张配置表 |

Unit4 顶层字段归属：

| 字段 | 分类 | 目标 |
|---|---|---|
| `player_context` | design_only | 不落正式表 |
| `opening` | structural | 转换时提供初始流程信息 |
| `scenes` | runtime_source | SceneConfig / LocationConfig / NPC / Item 关联 |
| `expose` | runtime_source | ChapterConfig / ExposeData |
| `doubts` | runtime_source | ChapterConfig / DoubtConfig |
| `evidence_registry` | runtime_source | ItemStaticData / TestimonyItem 来源 |
| `testimony_registry` | runtime_source | TestimonyItem |
| `doubt_progress` | design_only | 由 doubts 数量推导，不直接落表 |
| `cross_loop_evidence` | design_only | 持久化审查输入 |
| `non_progress_investigation_records` | design_only | 调查记录表现 |
| `special_mechanics` | special_adapter | L5 身份锁专用 |
| `ending_sequence` | special_adapter | L5 后非 Loop 终幕 |
| `meta` | design_only | Unit/Loop 元数据 |

未登记的顶层字段视为校验错误。

## 六、跨 Loop 持久化

必须保持到 L5 的输入：

| ID | 类型 | 首现 | 用途 |
|---|---|---|---|
| 4112 | item | L1 | 法律壳链 |
| 4153001 | testimony | L3 | Morrison 访客时间窗口 |
| 4315 | item | L3 | Morrison 现场雪茄 |
| 4416 | item | L4 | 1919 法律壳起点 |
| 4418 | key_item | L4 | L5 保险柜密码 |

每项在首现 State 中加入：

```yaml
persistence:
  scope: chapter
  reset_policy: retain_across_loops
  required_by:
    - identity_lock.chain_4501
```

校验器必须确认：

- ID 在声明的首现 Loop 存在。
- 持久化范围为 `chapter`。
- 重置策略为 `retain_across_loops`。
- L5 身份锁引用的 ID 与契约一致。

## 七、L3 非进度调查记录

四条记录保持在 `non_progress_investigation_records`，每条新增：

```yaml
presentation:
  channel: investigation_log
  blocking: false
  auto_unlock: true
  show_completion_toast: false
```

规则：

- 输入满足后自动写入调查记录页。
- 不增加疑点进度分母。
- 不阻塞 Doris Expose。
- 不显示“疑点完成”提示。

## 八、非 Loop 终幕

`loop5_state.yaml.ending_sequence.runtime_contract` 固定为：

```yaml
runtime_contract:
  counts_as_loop: false
  inherit_loop: 5
  chapter_end_after: ending_4045
  next_unit_entry: enter_ohara_house
```

校验器确认：

- Manifest `expectedLoops` 仍为 5。
- 不存在 `loop6_state.yaml`。
- `ending_4043`、`ending_4044` 不触发结章。
- `ending_4045` 最终画面仍是 O'Hara 家门外。
- U5 首个允许动作是进入 O'Hara 家。

## 九、自动校验器

新增：

- `剧情设计/Unit4/state/state_contract.yaml`
- `剧情设计/Unit4/state/validate_state_contract.rb`
- `剧情设计/Unit4/state/test_validate_state_contract.rb`

校验器使用 Ruby 标准库：

- `Psych`：YAML 解析与重复键扫描。
- `JSON`：Manifest 解析。
- `OptionParser`：命令行参数。

命令：

```bash
ruby 剧情设计/Unit4/state/validate_state_contract.rb
ruby 剧情设计/Unit4/state/test_validate_state_contract.rb
```

成功输出必须包含：

```text
PASS Unit4 state contract validation
```

## 十、验收标准

1. 五份 State YAML 均可解析且无重复键。
2. `known_facts` 链仍精确累计。
3. 所有 `scenes[].type` 属于基础类型集合。
4. 所有顶层字段均在契约中分类。
5. L5 身份锁没有 `open_questions`。
6. 身份锁三链覆盖全部 L5 Expose 材料。
7. 五项跨 Loop 材料全部具备章节持久化声明。
8. L3 四条非进度记录全部明确非阻塞。
9. 非 Loop 终幕仅在 `ending_4045` 后结章。
10. 不修改 Unity、正式表 JSON 或 AVG Talk。
