---
name: ndc-prop-manual-return
description: 接收用户人工定稿或明确指定的 NDC 道具 PSD，按现有图层、图层效果、层级关系与画布坐标机械导出 Type6、Type7、Map、Big、Icon 和 XYposition.txt。用于道具人工回流与定稿后导出；不生图、不修图、不重做热区、不新建交付候选，也不判定正式 PASS。
metadata:
  category: art/prop/manual-return
---

# 道具：人工回流导出

本 Skill 只处理用户已经人工定稿并要求导出的道具 PSD，或用户明确指定为当前导出权威的道具图层。普通母版生成继续使用 `ndc-prop-master-production`；场景放入、热区设计和最终复查继续使用各自 Skill。本 Skill 不改变这些生产流程或额度。

开始前读[人工回流与机械导出合同](references/return-and-export-contract.md)。遇到 Type6／Type7／子 Map、同组多层 Map、Big／Icon 替换时，再读[SC4002 与 SC4003 案例归纳](references/case-studies-sc4002-sc4003.md)；案例说明决策依据，不是可直接复制的路径或坐标。

## 输入边界

用户明确表示已经手工处理完成、图层／位置／层级可直接导出时，用户指定的 PSD、活动文档、图层名和父子关系就是本分支的内容权威。只核对需求中的输出角色与机械可导出性，不重新判断构图、语义轮廓、文字、美术质量或是否应当重做。

磁盘解析前必须确认人工修改已经保存；活动 Photoshop 文档有未保存变化时，不得用旧磁盘字节冒充当前结果。若用户没有授权保存源 PSD，只从当前活动文档直接导出受支持目标，或将无法可靠取得的单项明确列为阻断；不要替用户保存或覆盖源 PSD。

如需调用 Photoshop MCP，仍先完整读取项目当前《PS MCP 操作参考手册》，记录手册哈希与能力快照，并只使用实时 `supported` 的读取／导出能力。本 Skill 不授权 Computer Use、鼠标自动化、修图、重描路径或生成式补全。

## 机械导出

1. 从当前需求列出所有必需输出，逐项绑定唯一 `output_id`、PSD 图层路径、角色、目标文件名、是否带 XY、父级输出和渲染方式。使用 `assets/prop-manual-return.template.json` 建立本次 manifest。
2. 运行 `scripts/prop_manual_return.py validate --manifest <manifest.json>`。跨设备通过仓库入口运行时使用 `python -B scripts/art_pipeline/ndc_art.py run ndc-prop-manual-return prop_manual_return.py -- <参数>`；所有路径由调用者或 `ndc_art.py paths` 提供，不在 Skill 中写机器绝对路径。
3. 从 PSD 原样导出指定层。普通 Alpha 层用 `raw_layer`；带边框、描边等已定稿图层效果的目标用 `visual_layer_with_effects`，导出其完整视觉范围；只在用户明确要求从定稿层派生 Big／Icon 时使用 `deterministic_derivative`。不得把整个文档合成裁图当作独立层，也不得混入同组兄弟层。
4. 人工回流 Big 的当前尺寸与既有最终规格不一致时，直接在本支线顺手做非生成式尺寸调整后继续导出；这是一项常规处理，不新增门禁、状态或用户确认节点。优先不缩放地补齐透明画布，其次才是保持比例的单次缩放＋透明留边，禁止拉伸；调整前后检查主体／文字完整、无裁切、无重复采样。已有明确 Profile／目标尺寸时可在 manifest 记录 `final_profile` 与 `target_size`；没有单项重复字段时沿用本批已锁定需求或同类正式规格，不因回流源尺寸错误暂停其它输出。
5. 坐标一律取导出目标在原场景画布中的实际视觉左上角。Map 与 Type6 文件 stem 末尾写 `__XY_x<int>_y<int>`；Type7 可按既有运行时命名不带 XY 后缀，但仍写入同一 `XYposition.txt`。Big／Icon 默认不写 XY。
6. 运行 `scripts/prop_manual_return.py write-xy --manifest <manifest.json> --output <XYposition.txt>`；只有 manifest 已记录当前用户允许覆盖时才加 `--replace`。每行固定为 `<stem>\t【x,y】`。
7. 运行 `scripts/prop_manual_return.py verify --manifest <manifest.json> --delivery-dir <目标目录> --xy-file <XYposition.txt>`，核对文件存在、文件名坐标、XY 文本和父子引用；已记录目标尺寸的 Big／Icon 只在回执中写 `size_matches_target`，不因此改变命令退出状态或建立尺寸门禁。若为 false，就按第 4 步直接调整并重跑普通自检。Alpha 0 下清理 RGB 可作为无视觉变化的技术规范化；Alpha 正值像素、图层效果和画布位置必须保持，Big 规格调整除外但必须保留上述前后检查。

完成后只报告源 PSD、实际导出文件、父子关系和 XY。机械导出结论使用 `MECHANICAL_EXPORT_COMPLETE`；它不等于新的视觉 PASS、有效 PASS、程序接入或整批正式发布。

## 人工回流的交付位置

人工定稿回流直接写入用户指定的场景交付目录，不再复制一份到 `交付候选`。只有覆盖唯一可恢复旧文件时才建立必要备份；备份放工作过程历史或用户指定位置，不能借备份重新建立候选状态。过程记录若需要，只保留一份精简 manifest／校验回执在 `{WORK_ROOT}`，不把它混入交付图片目录。

同名目标文件必须有当前任务的明确覆盖范围。未获覆盖授权时，保留旧文件并只阻断该项；已授权时只替换名单内文件，不碰同目录其他资产。

## 不适用

- 用户还在要求调整图层、修边、补内容或重新判断热区：回到 `ndc-scene-evidence-placement` 或 `ndc-prop-hotspot-export`。
- 需要新生成或重画母版、Big、Icon：使用 `ndc-prop-master-production`。仅把人工定稿 Big 调整到最终技术规格仍留在本 Skill。
- 需要正式视觉复核、候选转正、运行时接入或整包发布：使用 `ndc-prop-delivery-review`。
- 角色入景 PSD：使用 `ndc-character-scene-manual-return`。

缺图层、同名层映射不唯一、图层效果无法忠实导出、当前修改未保存且活动文档又不能直接导出时，只阻断相应输出并报告精确缺项；不扩大成整场返工。
