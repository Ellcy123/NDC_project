---
name: ndc-character-scene-manual-return
description: 接收用户人工修改后交回的 NDC 角色入景 PSD，并在用户确认图层、阴影、位置和比例已定稿时，仅按资产需求导出人物／阴影层和 XYposition.txt。用于角色入景人工回流；不审核、不修图、不生图，也不处理道具人工回流。
metadata:
  category: art/character/scene-manual-return
---

# 角色入景：人工回流

本 Skill 只在用户交回或指定人工修改后的角色入景 PSD 时使用。普通角色入景生产继续使用原参考／生产 Skill；道具人工回流使用独立的 [ndc-prop-manual-return](../ndc-prop-manual-return/SKILL.md)，不得套用本 Skill。

执行前读[人工回流与极简导出合同](references/return-and-export-contract.md)。若来源是节点交付包，优先使用其中每场唯一的 `performance_editable_source` PSD；新节点 PSD 的三维白模、整场 baseline 和结构质量由上游 reference 节点合同负责，本 Skill 不在用户定稿后复审。也可使用用户明确指定的其它角色入景 PSD。

## 定稿 PSD

用户明确说明图层、阴影、位置和比例已经完成，并要求导出时，用户说明即为导出依据：

1. 从当前资产需求取得角色／状态、人物层、阴影层、命名、格式和目标目录。
2. 从 PSD 原样导出这些既定层，不修改源 PSD，不移动、不缩放、不修图。
3. 读取每个导出层在原场景画布中的整数左上角 XY；文件名使用匹配的 `__XY_x<int>_y<int>`，并用 `scripts/write_xyposition.py` 写一份 `XYposition.txt`。
4. 只报告目标目录、导出文件清单和 XY 文档，随后结束。

不得运行视觉／技术审核、身份／动作／比例／位置／阴影判断、Alpha 多底检查、整场重建、hash 审计、candidate registry、manual return manifest、revision、ledger、finalizer、审阅截图、过程包或新的 PASS 判定。缺必需层或同名层无法映射时只报告精确缺项，不自行生成、修复或扩展任务。

实际调用 Photoshop MCP 时仍执行项目级最小安全前置、打开、读取图层边界、导出和关闭／释放；这只是运行安全，不是资产审核。若当前方式可直接导出，不为证明过程制造中间文件。

## 未定稿回流

用户未声明 PSD 定稿时，不假定可以导出，也不替用户审核或继续角色生产。保留原文件，说明当前还缺哪项用户决定；其它不依赖该决定的主线不受影响。
