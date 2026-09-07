# 出图视觉记录验证器合同

这三个本地验证器按当前 skill 合同重建，并非找回或恢复原先 `D:/Codex/NDC/scripts/` 下的脚本。验证器只检查既有人工 / Codex 视觉记录、必需证据和当前文件 SHA-256；不会看图作艺术判断，不会填写视觉 PASS，也不会修改真实美术或批准记录。

依据为各出图 skill 的 `ndc-stage-visual-self-check/v1` 条款、`ndc-generate-characters/references/style-self-check.md` 的八项纹理检查和 `style-analysis-protocol.md` 的完整局部覆盖，以及 `ndc-scene-evidence-placement/SKILL.md` 的 Type 7 源场景 / 高度 / 视角 / 直接生成规则。本次检查的 `image/` 与 `production/` 下未检出这两个新 schema 的现有 JSON 实例；下面将这些已有语义固定为本地支持的字段结构，不能据此声称兼容未知外部脚本的全部旧格式。

## 命令和返回值

从策划仓库根运行，依赖 Python 3.10+ 与 Pillow：

```text
python scripts/art_pipeline/validate_stage_visual_self_check.py --record <review.json> --artifact <当前文件>
python scripts/art_pipeline/validate_texture_gate.py --record <texture-review.json>
python scripts/art_pipeline/validate_final_visual_record_presence.py --formal-dir <正式目录> --record-root <完整工作过程目录> [--report <新的过程报告.json>]
```

通过返回 0；缺记录、字段、文件、当前哈希、必需检查或检查不是明确 PASS 时返回 1。解析错误也阻断。stage 与 texture 不写文件；terminal 默认只向标准输出返回报告，只有显式传入 `--report` 才新建过程报告，不覆盖既有报告，不允许写入正式目录。报告不是视觉批准记录。

## 共用字段

- 文件引用为 `{"path":"文件路径","sha256":"64位SHA-256"}`。相对路径以该记录所在目录为基准；引用必须仍存在且与当前字节一致。
- 检查项为 `{"status":"PASS","finding":"实际看图后写出的具体发现"}`。只接受大小写精确的 PASS；FAIL、NOT_CHECKED、空发现、布尔值与笼统总分均不能通过。
- `reviewer` 为实际审查者；`reviewed_at` 为 ISO 日期或时间。脚本不替审查者补写。
- JSON 重复键拒绝接受，避免后一条 PASS 覆盖前一条 FAIL。

## Stage 记录

支持 `schema: ndc-stage-visual-self-check/v1`，必需字段为：

| 字段 | 内容 |
|---|---|
| `stage_id` | 本次实际阶段标识 |
| `reviewer` / `reviewed_at` | 审查者及日期 |
| `inputs` | 非空文件引用数组，冻结本次视觉输入 |
| `output` | 单个文件引用；每份记录仅为一个实际输出作结论 |
| `visual_check_status` | 明确 PASS |
| `required_criteria` | 本阶段所有适用检查项名称，非空、不重复 |
| `criteria` | 名称到检查项对象的映射，每项都有 PASS 与具体 finding |
| `views` | 下述整图与局部检查证据 |

`--artifact` 可以是 `output` 的正式目录副本，但字节必须完全相同；原 `output` 与所有源记录仍须可读且 hash 有效。图片输出必须自身被整图和局部查看，不能只查看输入后批准输出。JSON/Markdown 等非图片交接产物可以使用已冻结视觉输入作为查看源，同时绑定交接输出的当前 hash。

阻断记录应按 skill 写出负责返工的阶段；本地验证器直接拒绝这种记录，不会通过填入返工字段使它变成 PASS。脚本会核查所有已列的 criteria，不允许在 required 清单外藏一项 FAIL。通用阶段的适用检查完整性由该阶段的现行 skill 与审查者负责；脚本不会凭阶段名字推测无限种业务检查。Type 7 另有下述不可省略项目。

## 整图与局部 views

`views.whole_100` 必须同时包含文件引用字段、检查项字段、`scale_percent: 100`，以及 `source` 文件引用。整图证据图不得小于源图，源图必须是本记录 hash 绑定的被审输出或视觉输入。

`views.local_200_or_tiles` 包含检查项字段和同一 `source` 文件引用，并选择以下一种方式：

1. `mode: nearest_neighbor_200`：`scale_percent` 不小于 200，`resampling: nearest`；`images` 为非空数组，每项包含文件引用、PASS/finding 和源像素 `bbox: [left, top, right, bottom]`。检查图必须达到记录中的放大尺寸。此模式支持普通 stage，不能代替 texture 的完整原像素分块。
2. `mode: complete_original_pixel_tiles`：`source_size: [width,height]` 必须等于实际源图，`local_tile_coverage_complete: true`，`tiles` 为非空数组，每块包含文件引用、PASS/finding 与源像素 bbox，尺寸不得小于源裁切范围。验证器计算矩形并集，确认没有遗漏待检范围。

完整 tiles 还需声明 `coverage_mode`：

- `full_image_tiles`：覆盖源图所有像素，适用独立 Type 7、Big、Icon 母图、线索照片等。
- `authorized_region_plus_boundary_tiles`：`required_regions` 列出包含 bbox、role 与 finding 的全部适用区域；至少各有 `authorized_region` 与 `boundary` 一项，tiles 必须完整覆盖它们，适用于场景插入与角色局部合成。区域本身是否穷尽授权范围和边界仍须原授权合同及实际视觉审查确认。

坐标为左上原点、右/下不包含的整数矩形，必须位于实际源图内。记录中的视图缩放、采样方式和已查看声明仍是审查者的证据责任；脚本验证文件与几何，不声称证明屏幕上真的进行了观察或图片内容艺术正确。

## Type 7 额外项目

所有以 `container_type7` 开头的 `stage_id` 还必须有：

- `type7_visual_context.real_container_identity`：真实容器；`environment_derivation`：从源场景推导当前可见环境的文字；`first_person_viewpoint_rationale`：第一人称视点依据。
- `height_class` 为 low / mid / high；`observation_direction` 为 downward / level / upward。low 必须 downward；中高位置与具体镜头是否合理由源图并排检查判定。
- `type7_visual_context.method: direct_image_generation` 与 `child_fully_contained: true`。
- 顶层 `original_scene_visual_anchor`、`source_anchor_side_by_side` 两个 hash 绑定的图片引用。
- required_criteria 与 criteria 均包含 `mandatory_direct_image_container_rule`、`source_anchor_visual_comparison`、`container_height_and_observation_direction`、`visual_self_check`，以及本地序列化名称 `child_container_identity_and_full_visibility`。最后一项对应 skill 中的子件/容器身份与完整可见检查，不是额外的生成要求。

技术验证不能证明 direct generation 声明、真实支撑关系或子件在画面中的完整容纳；必须由实际看图者对照源锚记录 finding。未满足字段与视觉证据时不通过。

## Texture 记录

支持 `schema: ndc-texture-coherence/v1`。包含 `reviewer`、`reviewed_at`、单个 `artifact` 文件引用、`formal_status: FORMAL_PASS`、`whole_image_checked: true`、`local_tile_coverage_complete: true`，以及绑定 artifact 的 views。局部模式必须为 complete_original_pixel_tiles。

`STYLE_LOCK_GATE` 为含 PASS/finding 的对象，另含非空 `references` 文件引用数组和 `frozen_invariants` 字符串数组，分别保存实际风格来源与冻结的提示词/身份/色阶/线条/暗部/笔触/材质等适用约束。

`TEXTURE_COHERENCE_GATE` 为含 PASS/finding 的对象，另含 required_criteria 和 criteria；以下八项均不能省略：

```text
large_shape_readability
focal_detail_hierarchy
quiet_plane_control
material_texture_continuity
texture_scale_consistency
depth_aware_detail_density
repeated_pattern_artifacts_absent
nonsemantic_microdetail_absent
```

STYLE_LOCK 与 TEXTURE 两项必须独立通过。完整图片/分块审查其他必需项目仍按所属 skill 执行。

## Terminal 记录存在性

递归枚举正式目录内每一张 PNG；递归扫描 record-root 内 JSON；逐张取正式文件当前 SHA-256，只接受上述 stage schema 的单个 output 明确绑定且整份记录校验通过的审查。无效旧 schema 和格式异常会列出原因。缺任意正式 PNG 的有效记录即 BLOCKED；含糊 batch PASS、只记录文件名、输出数组无逐项结论或另一文件的 hash 都不能代替。相同当前 hash 存在未解决的失败/无效审查时也阻断，不以另一个 PASS 掩盖。

一份单输出审查可以覆盖该图的字节相同正式副本；这不意味着它可为同目录中其他内容的图作批量批准。record-root 必须包含实际 Photoshop 修复过程目录等记录来源。

此命令只完成“每张当前正式 PNG 的视觉审查记录存在性”，不会从已有文件反推本应执行的全部阶段或缺失角色。完整阶段链、采集覆盖、语义 release、纹理门禁仍必须独立执行；不能把本命令当成完整场景交付证明。

## 旧格式及验证

`ndc-stage-visual-review/v1` 与 `ndc-stage-visual-review-report/v1` 的旧脚本输出不能自动视为这里的 PASS：它们通常缺少 reviewer/date、逐项 finding、整图和完整局部视图证据。这里明确拒绝并说明，不补造记录、不重新计算旧图片 hash 来冒充旧审查，也不把机械检验报告映射成视觉批准。

最小回归检查：

```text
python -B -m unittest discover -s scripts/art_pipeline/tests -p test_visual_record_gates.py -v
```

所有测试图与模拟记录都只在临时目录中建立并自动清理。检查覆盖合法记录与正式副本、当前 hash 变化、漏视图/必需检查/发现、NOT_CHECKED/FAIL、逐 PNG 记录缺失、矛盾当前记录、Type 7 源锚/视角/方法/容纳、纹理分块缺口和命令返回值。这些模拟记录不是任何生产美术的批准。
