# Canon Manifest 最终审查修复报告

## 修复范围

- `canonicalUnit=UnitN` 现在要求 `playerChapter=N` 且 `unityEpisode=EPI{N:02d}`；坏类型仍返回字段化错误，不会向外泄漏类型异常。
- `chapters[].aliases` 现在校验对象结构、非空 `name` / `role`、章内与跨章唯一性，以及不得遮蔽 canonical Unit。
- `flowAliases[].name` 现在必须声明在其 `target` 章节的 `aliases` 中。
- 仓库测试精确锁定 Unit1/Unit2 的 aliases，Unit3-5 必须为空。
- `maturity.state` / `maturity.avg` 为 `reserved` 或 `absent` 时，`presentLoops` 必须为空。

## TDD 证据

解释器均为 `C:\Users\Ellcy\.local\bin\python3.11.exe`。

### 1. Canonical identity 关系

RED：

```powershell
& 'C:\Users\Ellcy\.local\bin\python3.11.exe' -m unittest tests.test_canon_manifest.CanonManifestValidationTests.test_player_chapter_must_match_canonical_unit_number tests.test_canon_manifest.CanonManifestValidationTests.test_unity_episode_must_match_canonical_unit_number -v
```

结果：`Ran 2 tests`，`FAILED (failures=2)`；两项均因验证器返回空错误列表而失败。

GREEN：同一命令，结果 `Ran 2 tests`，`OK`。

### 2. Chapter aliases 与 flow 归属

RED：

```powershell
& 'C:\Users\Ellcy\.local\bin\python3.11.exe' -m unittest tests.test_canon_manifest.CanonManifestValidationTests.test_chapter_alias_items_must_be_objects tests.test_canon_manifest.CanonManifestValidationTests.test_chapter_alias_fields_must_be_non_empty_strings tests.test_canon_manifest.CanonManifestValidationTests.test_chapter_alias_names_must_be_unique_within_chapter tests.test_canon_manifest.CanonManifestValidationTests.test_chapter_alias_names_must_be_unique_across_chapters tests.test_canon_manifest.CanonManifestValidationTests.test_chapter_alias_names_cannot_shadow_canonical_units tests.test_canon_manifest.CanonManifestValidationTests.test_flow_alias_name_must_be_declared_by_target_chapter -v
```

结果：`Ran 6 tests`，`FAILED (failures=21)`；21 个失败含 `name` / `role` 坏值子用例，均因缺少对应校验而失败。

GREEN：在同一命令后加入仓库锁定测试 `tests.test_canon_manifest.CanonManifestValidationTests.test_repository_manifest_has_exact_chapter_aliases`，结果 `Ran 7 tests`，`OK`。

### 3. reserved / absent presentLoops

RED：

```powershell
& 'C:\Users\Ellcy\.local\bin\python3.11.exe' -m unittest tests.test_canon_manifest.CanonManifestValidationTests.test_reserved_loop_components_require_empty_present_loops tests.test_canon_manifest.CanonManifestValidationTests.test_absent_loop_components_require_empty_present_loops -v
```

结果：`Ran 2 tests`，`FAILED (failures=4)`；四个 state/avg 子用例均因验证器返回空错误列表而失败。

GREEN：同一命令，结果 `Ran 2 tests`，`OK`。

## 最终验证

```powershell
& 'C:\Users\Ellcy\.local\bin\python3.11.exe' -m unittest tests.test_canon_manifest -v
```

结果：`Ran 36 tests in 0.606s`，`OK`。

```powershell
& 'C:\Users\Ellcy\.local\bin\python3.11.exe' scripts/validate_canon_manifest.py canon_manifest.json --repo-root .
```

结果：`Canon manifest OK: 5 chapters`。

## 自查与文件边界

- `git diff --check -- scripts/validate_canon_manifest.py tests/test_canon_manifest.py` 返回 0；只有 Git 的 LF/CRLF 提示，无空白错误。
- 实现采用 guarded parsing；非法 JSON 类型只产生字段错误，不参与关系计算。
- 重复 alias 使用全章节登记表，flow alias 使用目标章节登记集合，未通过名字猜测归属。
- 未修改 `canon_manifest.json`、builder、docs、AVG、state、table 或 formal output。
- 本次提交只暂存：
  - `scripts/validate_canon_manifest.py`
  - `tests/test_canon_manifest.py`
  - `.superpowers/sdd/final-fix-report.md`
