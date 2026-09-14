# Unit5 State 文件集

本目录是设计期蓝图，不是Unity运行时配置。

2026-09-14：五份State已生成并通过设计期交叉审查，结果见[交付验收](./reviews/final_validation.md)。

## 正式工作入口

- loop1_state.yaml 至 loop5_state.yaml：五轮；最后一份包含可操作分支终幕，不存在loop6。
- state_contract.yaml：本轮结构、知识累积、阶段flag与用户批准例外。
- id_registry.yaml：本轮NPC、场景、物证唯一编号；不等于已写入正式表。
- 上一级讨论结论.md、案发时间线与动线.md、风险点清单.md：设计依据与交付限制。
- reviews/：独立预检、总监准入及生成后的交叉审查。

## 来源与校验

outline_source_inventory.json保留七份来源的原始段落和SHA-256；outline_coverage_plan.json是生成前段落级计划，不是验收通过凭证。具体落点在各State的outline_coverage。

```powershell
python -m pip install -r "剧情设计/Unit5/state/requirements.txt"
python -B "剧情设计/Unit5/state/validate_unit5_state.py"
python -B -m unittest discover -s "剧情设计/Unit5/state" -p "test_*.py"
```

校验器默认只读，检查YAML重复键、章节身份、结构、ID、前置NPC、证词内联、跨轮知识、疑点唯一挂载、材料时序与终幕路由。加 `--report` 仅保存派生检查结果到 `reviews/validation_result.json`，不改State。通过不表示小游戏适配、环境指证、跨章库存或完整对白已实现。

来源变更后，仅在重新确认转译范围时运行build_source_inventory.py更新索引；它不生成或重写五份State，也不会自动把源变更写入State。必须重新核对原文变化并更新覆盖矩阵，不能单纯刷新哈希掩盖过期State。
