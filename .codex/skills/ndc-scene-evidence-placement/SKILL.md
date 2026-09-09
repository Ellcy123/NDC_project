---
name: ndc-scene-evidence-placement
description: 将已锁定 NDC 道具放入既定场景，确定承载体、原物替换、容器二级菜单及场景相关 Big/Icon，输出定稿场景和逐菜单预览。用于道具入景及菜单制作；需求盘点、独立母版、最终热区和正式打包分别交给对应阶段 Skill。
---
# NDC 场景放入与二级菜单

本 Skill 的 `scripts/`、`references/`、`assets/` 必须作为同一个完整目录随 Skill 提交，运行时从当前实际 `SKILL.md` 根相对解析。跨设备脚本入口为策划仓库的 `python -B scripts/art_pipeline/ndc_art.py run ndc-scene-evidence-placement <脚本名> -- <参数>`；不得引用维护机 `.agents`、用户名或固定盘符。Unity 根由 `NDC_ENGINE_ROOT` 推导，特殊布局用 `NDC_UNITY_EVIDENCE_ROOT`，这些本机路径不得写回 Skill。

执行前读[对话任务独立额度](../ndc-prop-requirements/references/task-budget.md)：新对话完整新额度，资产在其他对话中的历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于引用中的旧预算说明。

这是五阶段的第三阶段。批次未建立时先调用[需求整理](../ndc-prop-requirements/SKILL.md)；母版缺失时交给[母版制作](../ndc-prop-master-production/SKILL.md)。旧名称和 scripts/ 地址保持兼容，但不能再把所有阶段在本入口内重复执行。

读[共用批次协议](../ndc-prop-requirements/references/batch-contract.md)与[场景专业细则](references/production-details.md)。实际改动场景前加载[坐标修图](../ndc-coordinate-image-edit/SKILL.md)；制作Big/Icon时读[规格](references/detail-icon-production.md)；PS修正或菜单框幅调整时读[PS操作参考](references/photoshop-mcp-repair-and-framing.md)。本阶段不加载热区描边全文。

## 场景批次

开始某场景前运行workflow_state.py scene-readiness --batch <batch.json> --scene <scene_id>，按[场景放行合同](../ndc-prop-requirements/references/scene-release-contract.md)读取完整关联前置及阻塞。它只放行第二阶段到第三阶段；单个道具通过或scene_id筛选后的子集不足以放行。attempt按job和产物所属场景再次校验，不能靠改current_stage跳过；该场景制作期间前置变更会撤销相关审核。无索引旧批保持全局门槛，先追加迁移索引再按场景续跑。

1. 按锁定范围先补本阶段可执行缺失角色，再复检和修复旧问题。先看原场景是否已满足该状态；已有合格遮阳帘、窗缝或环境痕迹直接保留，只补缺失Big／热区等角色。确需替换才检查原物归属，不能因清单列了一项就生成式更换。每个场景统一规划落点、比例、支撑、动线和容器。
2. 新承载体优先依附墙边、家具端部和工作区域，不为展示信息孤立放在通道中央。先完成真实场景中的承载体，再制作依赖它的近景与菜单。保留独立合格Big，只有实际跨视图冲突才重做。
3. 场景物只需呈现本视角能看到的身份和状态，不要求把母版文字摊开、放大或转正。纸张可自然叠放；图像玩法所需可见线索仍必须保留。
4. 每个入景作业／菜单状态总计最多3次生成、每次1张，首张计入。改位置、换Skill、最终返修均不重置同一job额度。语义正确的轻微变换可先尝试一次可用MCP修正；失败后的新生成仍占这3次总额。
5. 坐标修图继续验证源图、授权区、合法裁切、接缝及最终并集外零漂移。原底图已有线条异常先比对，检测范围不适用先修检测范围，不能为通过扫描改画无关像素。
6. 每个场景完成全部道具、容器和必要状态后，收齐场景相关线索／环境Big。普通已合格Big不重复生成；环境Big保持原场景方向与有意义的语境Alpha。
7. 本批次第三阶段非Icon必需图完成后，统一制作所需Icon及其专用高分辨率来源，再进入第四阶段。实物、线索、分析结果的身份与展示方式以已通过来源为准；Icon绑定实际母版／Big，不能引用未定的候选，不依赖尚未导出的热区。先补缺Icon，再检查已有问题；已合格Icon只验证有效性并保留。

## 二级菜单

任何容器的打开态均放入二级菜单，包括已有开箱图、小保险箱和自动剧情开启；无角色、无人体部位，第一人称角度由原容器高度和空间推导。承载体、已通过母版作为参考，由Image直接生成容器和可见内容物的完整图像；不把Big后贴进容器。

自动AVG授予不新增玩家点击，保留真实触发和取得顺序。实际探索容器保留Type6→Type7→子道具链。环境叙事不塞进容器菜单规避场景可见性。

确定无框内图最终尺寸后再加精确12px白框，框后不缩放。每个菜单输出交付图、无调试层的独立场景叠加预览，并记录菜单全场景XY；不能把所有打开菜单合成一张预览代替单独检查。

## 冻结和交接

输出完整场景道具预览、逐菜单场景预览、菜单交付图、必要Big/Icon及当前审核。冻结父图路径、尺寸、哈希、菜单位置、状态和依赖图。候选图可继续独立布局试验，但不得标记冻结PASS。

按已锁定批次门槛，全部所需场景／菜单完成定稿后才进入[热区导出](../ndc-prop-hotspot-export/SKILL.md)，不再请求清单确认。阻塞时按共用协议的补缺及必要依赖例外推进，不静默缩小批次。已有完成热区可保留，父图变动仅使受影响依赖失效。

## Carrier before dependent evidence art

具体承载体审核见[场景专业细则](references/production-details.md#carrier-before-dependent-evidence-art)。独立物品母版不需要凭空发明承载体；场景相关近景必须有真实场景锚点。
