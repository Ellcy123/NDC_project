# Unit4 State v3 候选重生成实施计划

## 目标

以 `canon_manifest.json` 登记的 Unit4 v3 大纲为最高事实源，升级 State 合同与校验器，并在不覆盖现行 State 的前提下生成五份可审查候选文件。

## 范围

1. `state_contract.yaml` 升级为 v2：
   - 锁定 Manifest 与 v3 大纲。
   - 定义唯一根 Opening、连续事件序列和控制权恢复规则。
   - 分类 `outline_coverage` 与 `narrative_continuity`。
2. `validate_state_contract.rb` 与测试：
   - 保留现有证据、身份锁、跨 Loop 持久化及结局边界校验。
   - 新增 Opening、覆盖矩阵、连续性和无来源新增校验。
3. 生成 `state_candidate_v3/loop1_state.yaml` 至 `loop5_state.yaml`：
   - 保留现有证据、疑点、证词和 Expose 核心链。
   - 重构五个 Opening。
   - 修正强制事件归属、控制权与跨场交接。
   - 删除 L5 夜班门房体系。
4. 修正与 v3 明确冲突的 Unit4 支撑文档。
5. 输出候选与现行 State 差异报告。

## 执行顺序

1. 补合同与失败测试。
2. 生成五份候选 State。
3. 静态校验 YAML、ID、覆盖矩阵和连续性。
4. 检查 Ruby 校验环境；若本机仍无 Ruby，记录未执行原因并用等价静态检查补足。
5. 交付差异报告；不自动替换正式 State。

