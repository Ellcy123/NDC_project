# NDC 角色资产：生成后技术整备

## 目的

把“人物与画风生成”同“尺寸、比例、透明、占比和边缘交付”分开。模型只负责一次生成稳定的角色资产；技术规格不得反向污染或改写已锁定的生成提示词。

用户明确选定原生艺术图时，该选择即为本资产的艺术冻结点。不得因为模型推断的笑容、气质或可后补道具没有出现而返回 MJ 或重新生成下游资产；只进行用户要求或交付规格确实需要的非生成式处理。背景透明化属于艺术候选确定后的末端技术步骤，不得提前写入或改写生成提示词，也不得用透明底要求否定尚未做技术整备的原生艺术图。

## 一、生成提示词锁

### 肖像

- 唯一主提示词为 `prompt-library.md` 的“7. 通用风格肖像”代码块。
- 图 1 固定为同角色当前批准的通用风格角色卡；图 2 固定为 `assets/general-portrait-style-reference.png`，且只控制画风。
- 调用生图工具时逐字提交主提示词。禁止改写、摘要、翻译、扩写、补充透明背景、肩部范围、负面词、尺寸修复词或角色专属描述。
- 角色的具体脸、发型、发色、服装与配色只由图 1 提供，不在主提示词中二次描述。

### 普通角色卡

- 用户没有明确写出 `4K` 时，唯一主提示词为 `prompt-library.md` 的“6.2 默认整卡生成”代码块。
- 默认一次生成整张角色卡，以身份和画风稳定为优先；不得自动拆模块，不得把“正式交付”理解为默认 4K。
- 调用生图工具时逐字提交主提示词，只替换提示词明确保留的角色变量；禁止追加分辨率、透明、抠图、包围框、扩图、补全或技术验收文字。

### 明确 4K 角色卡

- 只有用户明确要求 `4K` 时才读取 `modular-character-card.md`，生成高像素模块并确定性拼成 3840×2160。
- “高清”“正式”“最终”“可用”不能自动解释成 4K；不确定时仍走普通整卡生成。

每次生成前保存以下提示词锁记录：

```yaml
prompt_lock:
  source_path: <prompt-library.md absolute path>
  source_section: <6.2 or 7>
  submitted_prompt_path: <verbatim prompt snapshot>
  exact_text_match: PASS|FAIL
  reference_1: <approved same-character identity path>
  reference_2: <style-only path>
  explicit_4k_requested: true|false
```

`exact_text_match: FAIL` 时不得调用生成工具。

从任一已配置仓库根目录运行；先以 `ndc_art.py paths` 返回的策划根替换 `{PLANNING_ROOT}`，导出目标使用本任务的项目外 `payload` 路径。使用脚本直接导出并复核，不要手工重写主提示词：

```text
python scripts/art_pipeline/ndc_art.py run ndc-generate-characters verify_locked_prompt.py --prompt-library "{PLANNING_ROOT}/.codex/skills/ndc-generate-characters/references/prompt-library.md" --prompt-id portrait --export <portrait-prompt.txt>
python scripts/art_pipeline/ndc_art.py run ndc-generate-characters verify_locked_prompt.py --prompt-library "{PLANNING_ROOT}/.codex/skills/ndc-generate-characters/references/prompt-library.md" --prompt-id portrait --verify <portrait-prompt.txt>
python scripts/art_pipeline/ndc_art.py run ndc-generate-characters verify_locked_prompt.py --prompt-library "{PLANNING_ROOT}/.codex/skills/ndc-generate-characters/references/prompt-library.md" --prompt-id character-card-default --export <card-prompt.txt>
python scripts/art_pipeline/ndc_art.py run ndc-generate-characters verify_locked_prompt.py --prompt-library "{PLANNING_ROOT}/.codex/skills/ndc-generate-characters/references/prompt-library.md" --prompt-id character-card-default --verify <card-prompt.txt>
```

只有输出 `PROMPT_LOCK_PASS` 的快照才允许提交给生成工具；工具调用中的提示词必须直接来自该快照。

## 二、两阶段验收

### A. 艺术候选

先检查：

1. 是否为同一角色，而非同类人物；
2. 发型、发色、年龄、体型、服装层级和配色是否继承批准角色卡；
3. 肖像是否符合固定肖像提示词；角色卡是否具备当前批准的全身、头部和细节结构；
4. 是否符合对应自检库的整图与原像素局部画风。

这一阶段不因原生输出尺寸、比例、背景不透明、人物占比或外缘裁切而要求重生。只有人物身份、画风或主体结构错误才返回生成阶段。肖像肩膀被原生画框截断不属于结构失败。

艺术候选通过后保存原图并冻结。后续技术整备不得改动脸、头发内部、服装内部、配色、明暗风格、笔触或已经完整的人体结构。

### B. 技术整备

按实际需要依序执行，未需要的步骤记为 `SKIPPED_NOT_NEEDED`：

1. `抠图`：在艺术候选已确定并冻结后，若该资产交付要求透明，才移除暖白或其他生成背景并生成真实 RGBA；保留完整轮廓，不把浅发、帽檐、耳朵、肩线或深色衣物误删。锁定提示词中的暖象牙色/纸张质感底属于生成阶段的风格环境，不改变“最后再透明化”的顺序；不得为了提前获得透明底改写主提示词或重生人物。
2. `扩图/补全`：仅用于角色卡、全身图或其他非肖像资产在必需结构被原边界截断时补齐缺失外缘。编辑区域限制在缺失边缘及必要接缝；脸、发型主体和完整衣物区域冻结。肖像不执行缺肩补全；原生构图中的截肩可直接保留，不得仅为补齐肩膀调用扩图或局部生成。
3. `等比例缩放`：只做等比例缩放，禁止非等比例拉伸。优先缩小或原尺寸放置；需要放大时记录倍率并检查插值损伤。
4. `画布定位`：将人物放入目标画布，按批准历史数据设置人物与头部位置。新资产人物包围框及人物占比不得超过对应历史样本最大值；需要例外时，必须先记录头部占比和位置，并证明轮廓上限变化确由头部构图规律导致，再交用户确认。
5. `边缘清理`：检查白边、浅色光晕、锯齿、断发、透明孔洞、重复扩展带和接缝。肖像原生画框造成的截肩不是边缘缺陷。
6. `最终机械检查`：读取实际像素；角色卡为 16:9，肖像为 4:5。对透明交付资产在黑、白、饱和红底上检查完整轮廓；暖白边、纸张色晕、锯齿或透明孔洞失败时只返回抠图/边缘清理，不返回艺术生成。

技术整备不能修复人物身份或画风。若抠图或扩图改变脸、发型、服装设计、色相、笔触或高反差结构，返回该技术步骤，不得重新生成整张资产。

## 三、返工路由

| 问题 | 返回阶段 |
|---|---|
| 身份、发型、发色、服装或画风错误 | 原提示词生成；提示词本身保持不变 |
| 普通角色卡缺失关键视图且无法局部修复 | 原提示词整卡重生 |
| 角色卡、全身图等非肖像资产仅缺必需外缘结构或画布空间 | 局部扩图/补全 |
| 肖像原生构图缺肩或截肩 | 不返工、不补全；继续比例、背景、画布定位与可见边缘检查 |
| 背景、白边、光晕或透明孔洞错误 | 抠图与边缘清理 |
| 画布比例、尺寸、人物占比或位置错误 | 等比例缩放与画布定位 |
| 明确 4K 角色卡的单一模块错误 | 只返工失败模块 |
| 技术操作改变身份或画风 | 回退该技术操作，恢复冻结艺术候选 |

同一技术问题连续两次失败时停止自动重试，保留艺术候选和失败版本，报告具体差异；不得通过改写主提示词逃避技术问题。
