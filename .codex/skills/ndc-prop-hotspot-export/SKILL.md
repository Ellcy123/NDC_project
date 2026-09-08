---
name: ndc-prop-hotspot-export
description: 从已定稿的 NDC 场景及二级菜单，通过 Photoshop MCP 逐项提取异形道具热区、容器入口和子道具图并导出 XY。用于热区修复、Alpha完整性和坐标核验；不生成道具、改写文字或重排场景。
---
# NDC 热区与坐标导出

这是第四阶段。输入是第三阶段冻结的全尺寸场景／菜单及批次记录；先读[批次协议](../ndc-prop-requirements/references/batch-contract.md)。调用全批次工作流校验 stage 4 通过后才开始；第二阶段到第三阶段的单场景放行不能代替该整批门槛。

读[热区专业细则](references/production-details.md)、[语义轮廓检查](../ndc-scene-evidence-placement/references/hotspot-semantic-review.md)及[PS操作](../ndc-scene-evidence-placement/references/photoshop-mcp-repair-and-framing.md)。

## 逐项操作

先提取缺失热区，再复检／修复已有错误热区；都使用同一套完整性与坐标门禁。只缺热区时不得转去生成式替换已经合格的场景物。遵从共用协议核对其他任务的PS占用并逐项释放。

1. 通过PS MCP打开冻结的原尺寸父图。导入需使用当前可用MCP接口；计划中的“拖入”不授权鼠标自动化。场景预览必须是定稿像素，不能含调试标记或经过缩放。菜单子图直接取独立菜单原图，再加菜单XY偏移。
2. 定义完整物体、厚度、归属阴影、真实孔隙、前景遮挡和相邻交互物。先确认宽松检查范围完整，再标独立四极和描基本轮廓；低对比不能作为删掉真实厚度的理由。
3. 按物理结构修正路径，按当前规则作有依据的2—3px外扩／已指定最终路径零再扩；剔除前景和无关台面，保留合理多岛Alpha。不用矩形或凸包连接分离物件。
4. 导出保存后检查Alpha、棋盘底、原父图叠加、整图及局部边缘。每个热区一份视觉结论，不能以批量PASS代替逐项检查。
5. PS占用、保存交接、待检目标和独立目标切换遵循共享PS协议；每张热区仍需独立技术核验与真实视觉通过，待检／失败图不能供下游或发布。可保留同一场景PS文档，记录各目标及路径以便恢复，微调只修失败部分。
6. 由最终Alpha自动算裁切左上角与尺寸，菜单子图全场景XY=菜单XY+局部裁切原点。Alpha正值RGB必须与父图对应，Alpha零处RGB清零。XY、PNG和父图哈希同步绑定。
7. 使用旧 scripts/irregular_map.py 与 evidence_delivery.py 进行已有技术验证和包装，不用它们声称完成了PS操作。不为自动授予物凭空生成点击热区。

## 返修与输出

父图若修改，回到第三阶段，撤销相关热区／坐标依赖；无关场景与未变母版保留。本阶段不打开新的图像生成预算。

输出Map、Type6、可点击子物品PNG、XYposition.txt、独立菜单XY、技术报告、逐热区审核和PS恢复件。工程Sprite Physics Shape／PolygonCollider2D接入状态独立记录：图片和坐标通过不等于运行时热区已验证。完成后交给[最终复查](../ndc-prop-delivery-review/SKILL.md)。
