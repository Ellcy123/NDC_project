---
name: ndc-prop-delivery-review
description: 复查并归档 NDC 道具图片包，核验内容覆盖、跨状态身份、热区坐标、有效审核及有限返修，汇总风险和工程接入待办。用于道具最终验收、候选转正及交付复核；不把技术通过当视觉批准。
---
# NDC 道具最终复查与交付

这是第五阶段。读[批次协议](../ndc-prop-requirements/references/batch-contract.md)、[审核与复用](references/review-contract.md)及[交付细则](references/production-details.md)。命名、角色和目录仍遵从[交付合同](../ndc-scene-evidence-placement/references/delivery-contract.md)。

## 完整复查

全量生产时，本阶段在可执行缺失交付补全后进行整体复检，问题返回责任阶段有限修复；不得把本入口提前当作补缺前的全量审核任务。用户当前仅要求统计／复检时按该范围执行，不自动生图。进度按共用协议同时报告完整总角色、各场景实际阶段与补缺基线，正式交付另计；某场景获准入景不代表整批Icon／热区或正式交付已放行。

1. 从锁定需求推导必需交付，不能从现有文件反推需求已齐全。分别报告母版、场景、热区、正式整项及阻塞数量。
2. A类事实全部通过；B类按原先明确允许的差异判断；C类不追求像素一致。风险表列尚未核实或超出允许范围的差异。关键错误与技术错误不能被平均分数抵消。
3. 同组比较Big/Icon/Map/菜单及必要状态，判断身份、组件和状态关系；真实角度、光线与合理遮挡可变。读取当前拒收，用户否定立即使相关复用失效。
4. 核对实际待交付字节及完整链。已有审核满足图像／父图／内容／要求／范围均未变化且无拒收时复用记录；同哈希不足以放行。最终整包联组复查仍执行。
5. 关键问题返回责任阶段，保留原job和累计次数。额度用尽只能保留候选并汇总人工待处理；不得因最终审核再次启动三轮生成。
6. 每个正式PNG必须绑定通过的真实视觉记录。复用记录只证明旧观察仍适用，脚本不得生成新的艺术PASS。详情图通过不代表热区通过。
7. 图片范围和程序接入分开：交付图片及可供接入的坐标／说明，不擅自修改Unity，不将程序未绑定错误计为缺PNG。用户明确要求运行时完成时仍需单独验证。

## 校验和归档

新五阶段批次必须依次执行以下命令，路径从Skill目录解析为绝对路径，不依赖终端cwd：

- `python scripts/workflow_state.py validate --batch <batch.json> --stage 5`：全批次交接、内容版本、依赖、生成额度与审核有效性。
- `python ../ndc-scene-evidence-placement/scripts/validate_formal_release.py --folder <formal> --release-contract <contract> --batch <batch.json>`：原图像角色、XY、父图与旧副本检查，并核验批次。
- `python scripts/final_visual_check.py --formal-dir <formal> --record-root <process> --batch <batch.json>`：最终复制后核对每个正式文件有有效逐图审核绑定。

正式目录仅接受通过的PNG与一份XYposition.txt。报告、候选、PSD、遮罩和历史放在工作过程目录。替换包先完整验证，保存旧版本后发布；不混入旧目录的未知文件。通过适用门槛即归档，不等待重复人工确认。每个artifact可记录published_path以支持最终副本核对，但它必须与已审核字节一致。

## 可复用工具

scripts/workflow_state.py 管理批次门槛、追加尝试日志和审核复用判定；scripts/scene_release.py计算有证据的场景关联前置闭包。可选索引、无重置迁移与续作命令见[场景放行合同](../ndc-prop-requirements/references/scene-release-contract.md)。
scripts/stage_visual_check.py、scripts/final_visual_check.py 是移入本Skill的共用审核实现；项目根旧命令保留兼容入口。
旧evidence_art、evidence_delivery、irregular_map、secondary_prop_border和validate_formal_release仍保留在原Skill脚本地址。不要搬动脚本破坏历史作业。
