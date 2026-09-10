---
name: ndc-generate-expressions
description: Plan, generate, audit, and package NDC bust-expression sets from user-confirmed completed portraits. Use for expression requirements, manual RGBA handoff and return, explicitly authorized Photoshop MCP cutout trials, paired transparent and exact-green delivery profiles, and expression-set QA. Do not use to complete portraits, redesign characters, create full-body states, or place characters into scenes.
---

# NDC Generate Expressions

## Photoshop MCP 强制前置

仅在本 Skill 进入用户明确授权的 Photoshop MCP 模式时，第一次实际调用前必须完整读取当前环境的《PS MCP 操作参考手册》：维护工作区从项目根解析 `PS_MCP_操作参考手册.md`，工程镜像从仓库根解析 `production/art_pipeline/PS_MCP_操作参考手册.md`。在当前表情作业记录中保存实际手册路径、版本、SHA-256 和当前会话能力快照；两处均不存在或哈希不一致时不得以历史记忆继续操作。手册负责通用效率、抠图、Alpha、软硬边路径、单引擎、超时回退和视觉/技术验收；本 Skill 的人工默认模式、授权边界、双交付规格和表情门禁继续优先。实时目录只允许执行 supported 能力，手册本身不增加操作授权。

执行前读[对话任务独立额度](references/task-budget.md)：新对话完整新额度，其他对话的资产历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于旧预算说明。

实际使用原生 Photoshop MCP 前，确认 Bridge 已连接及所需命令可用，并协调本机同一时刻只有一个任务操作 Photoshop；不再调用排队或租约接口。同任务当前图须保存、完成技术及真实视觉检查并核对当前hash；未审完不得推进下一张。PASS可推进相应依赖；FAIL缺陷已记录且预算耗尽或用户要求封存时，保留候选和累计次数，仅继续独立资产；安全保存可恢复文件和固定审阅快照后，可安全交棒给其他独立任务。释放不是PASS，不解除原图及依赖的阻断、不重置预算；命令在途或结果未知时不得自行交棒。纯准备、生图等待和离线审阅不长期占用桥接，未授权的PS操作不会因连接可用而获得授权。

## Operating boundary

Background processing has two modes. Default `USER_MANUAL` follows the E5 handoff / E6 user-return path below. When the user explicitly authorizes Photoshop MCP cutout or fringe work, use `USER_AUTHORIZED_PHOTOSHOP_MCP` and read [references/photoshop-background-processing.md](references/photoshop-background-processing.md) first. That mode replaces the manual-only stop and no-Codex-Alpha-repair clauses throughout this Skill and its references, but does not waive source integrity, serial per-image review, artistic rejection, Alpha gates, or truthful provenance. Existing manual-only receipt tooling must not be fed fabricated manual-processing fields; PS trials stay non-final until the actual processor is supported end to end.

This Skill begins from a user-confirmed portrait suitable for the requested expression/profile crop. General portraits may legitimately crop the shoulders. If the requested use needs missing shoulder/chest or other subject regions, enter `WAITING_FOR_MANUAL_PORTRAIT_COMPLETION` and follow [references/manual-portrait-source.md](references/manual-portrait-source.md). This is a deliberate human handoff before E0/E1, separate from E5/E6 background processing; it consumes no image-generation attempt. Missing, unapproved or identity-ambiguous sources remain `UPSTREAM_PORTRAIT_REQUIRED`. This Skill never outpaints or reconstructs missing anatomy, and PS cutout authorization does not authorize portrait completion.

## Production record and resume point

Use [references/production-record.md](references/production-record.md) and `scripts/art_workflow_state.py` for persistent jobs, actual attempts and current evidence. Keep E0–E4 artistic production, E5/E6 manual handoff/return, and E7–E10 profile export as resumable parts of this Skill; resume at the first affected state. Reuse a review only when source and output hashes, requirements, inspection scope and approval/rejection history still match. Copying unchanged accepted bytes carries that evidence forward with a copy record. A changed portrait invalidates its dependent expressions; a changed native RGBA invalidates both derived profiles; one profile transform change invalidates only that profile and affected pair/set comparisons. Preserve passed siblings and historical records.

## Mandatory stage-end visual self-check gate

Every art-production stage executed by this Skill must end with an actual visual self-check before its output may be accepted, passed to a later formal stage, handed off, packaged, or released. This includes portrait-source acceptance, reuse acceptance, expression generation, artistic/color review, pre-Alpha handoff acceptance, returned-RGBA ingest, Alpha-edge review, profile composition, profile/set audit, normalization, and final packaging. Inspect the current whole image at `100%` and every applicable local region at nearest-neighbor `200%` or through complete original-pixel tiles. Compare against the approved portrait authority and every applicable identity, viewpoint, expression, anatomy, costume, lighting, color, style, texture, edge, Alpha, profile, placement, continuity, and runtime-readability requirement.

Write one current `ndc-stage-visual-self-check/v1` JSON record per executed stage. It must bind the stage ID, reviewer/date, input and output paths plus SHA-256, the inspected `whole_100` and `local_200_or_tiles` views, every applicable criterion with an explicit finding and `PASS`/`FAIL`/`NOT_CHECKED`, the overall `visual_check_status`, and the responsible rework stage when blocked. Missing record, missing visual-detection item, stale output hash, missing required view, `FAIL`, or `NOT_CHECKED` is `STAGE_VISUAL_SELF_CHECK_GATE: BLOCKED`: do not advance state, hand off the file, use it downstream, or call it formal. Technical validators, dimensions, hashes, Alpha/profile reports, or absence of a detected error cannot write visual `PASS`.

After a block, return to the responsible stage allowed by this Skill's authorship boundary, perform the missing inspection and authorized rework/regeneration, then repeat the visual self-check on the new current output. Release only after the current hash has a passing record. For every file-producing stage, run `python -B scripts/art_pipeline/ndc_art.py tool stage -- --record <visual-review.json> --artifact <current-output>` from the planning repository root; a nonzero result is a hard stop. Existing retry ceilings and the ban on Codex background/Alpha repair remain unchanged; when the responsible repair belongs to the user, stop at the required rework status instead of weakening this gate.

The user-approved portrait is the identity, viewpoint, costume, lighting, style, texture, and calm-expression authority. Never regenerate calm. Every non-calm expression is generated directly from that portrait, never from another expression or a failed candidate.

Default to prompt and manifest preparation. Execute image generation only after the user explicitly authorizes Codex execution. A request to update this Skill, inspect portraits, or plan requirements is not authorization to start generation.

For Unit3, treat the image files in `D:\PMH\工作\人设\003第三章\头像` as the user-confirmed completed portrait set. This directory is read-only. Copy required inputs into `D:\Codex\NDC\工作过程文件\角色表情\Unit3` before production; never modify PMH files.

## Required reading

<!-- ART_DETAIL_CONTROL_V2:BEGIN -->
For new or explicitly replaced expressions, also apply [art-detail-control](../art-detail-control/SKILL.md) during expression planning, actual prompt/reference assembly, and artistic review. Use its character/expression branch: preserve the approved portrait's identity, expression signals, lighting topology, native brush language and stable texture; reject added random pores, repeated marks, decorative folds or fragmented small highlights. Do not impose outdoor haze, universal smoothing or a new rendering style. Calm/reuse bypasses creative redesign; missing portrait regions remain upstream work. Integrate region-specific findings into the existing artistic/style/texture evidence without changing receipt schemas or treating text review as visual PASS. Existing prompt locks, generation authorization, retry limits and manual/PS processing boundaries continue to apply.
<!-- ART_DETAIL_CONTROL_V2:END -->

Read only the references needed for the current stage:

1. [references/workflow.md](references/workflow.md) for the complete state machine.
2. [references/expression-planning-and-prompts.md](references/expression-planning-and-prompts.md) before requirement planning or generation.
3. [references/manual-background-handoff-and-return.md](references/manual-background-handoff-and-return.md) before making the non-final handoff or accepting user-returned RGBA files.
4. [references/delivery-profiles.md](references/delivery-profiles.md) before composing either delivery format.
5. [references/profile-guides-and-source-integrity.md](references/profile-guides-and-source-integrity.md) before approving profile placement.
6. [references/self-check-and-rework.md](references/self-check-and-rework.md) before review, retry, or delivery.
7. [references/receipt-schema.md](references/receipt-schema.md) before formal packaging.
8. Read the remaining focused references only when their named concern applies: reuse, viewpoint, style fallback, readability, source detail/lighting, or semantic color.
9. Read [references/identity-and-expression-calibration.md](references/identity-and-expression-calibration.md) before planning or reviewing new/replacement expressions, and when processing a user rejection. It defines facial-geometry checks, actual calm contrast, and rejection supersession without reopening unrelated approved assets.

## Non-negotiable invariants

- `PORTRAIT_COMPLETION_USED=false` means this Skill performed no completion. A manually completed source may enter after acceptance; preserve its truthful upstream manual provenance separately. There is no automatic completion stage, completion prompt, completion mask, outpaint retry, or anatomical repair route in this Skill.
- Calm is the approved portrait. It is copied unchanged into the non-final handoff and is never regenerated.
- Generate each non-calm expression directly from the same approved portrait on a plain, uniform light background suitable for the user's manual background processing.
- In default `USER_MANUAL` mode, Codex does not process the background or Alpha. Explicitly authorized PS work uses only the bounded MCP route above; `remove_expression_background.py`, global light-pixel removal, and generative Alpha repair remain prohibited.
- After every requested expression passes artistic review, stop and deliver a `PRE_ALPHA_HANDOFF` package under `工作过程文件`. It is explicitly non-final and must not be copied to `最终交付`. The user edits those exact handoff PNG files in place; do not create or require a separate return folder.
- Resume only after the user confirms that the in-place handoff files have been manually background-processed as native RGBA. If their Alpha or edge RGB fails review, return `USER_ALPHA_REWORK_REQUIRED`; do not repair the background or white fringe inside this Skill.
- Never remove light pixels globally. White shirts, collars, eye whites, hair highlights, jewelry, pale linework, and other intentional light design are protected subject content.
- A transparent cutout is not approved until `ALPHA_EDGE_GATE=PASS`: inspect the whole silhouette and critical hair/shoulder/costume edges on white, mid-gray, dark gray, black, and exact `#00FF2B` at native 100% and nearest 200%. Any white halo, matte contamination, remote island, hole, erosion, jagged edge, or missing subject region is `FAIL`.
- In authorized PS mode, first test 1px selection contraction in native pixels. If white fringe remains without subject-detail loss, increase contraction by 1px to a maximum total of 2px relative to the original selection. If fringe remains at 2px, use localized selection and deletion; never continue global shrinking. Reject lost hair, costume edges, or protected light details at either step.
- Freeze exactly one edge-passing native RGBA foreground per `character + expression`. Both delivery profiles must use that exact file and SHA-256.
- Transparent and greenscreen are separate delivery profiles with separate canvases, transforms, guides, audits, and pass results. They share artistic foreground pixels, not geometry.
- Transparent delivery is `1164x916 RGBA/Alpha 0`, except an explicitly requested Unit1 legacy `1152x900` branch. Greenscreen delivery is `1536x1024 RGB` with exact `#00FF2B` background.
- Profile composition may uniformly downscale once and translate. It may not upscale, stretch, rotate, crop protected subject pixels, redraw the subject, or perform profile-specific generation.
- Preserve identity, approved viewpoint family, costume, lighting topology, palette, style, and stable texture. Every non-calm expression must also pass semantic accuracy, calm separation, thumbnail readability, and pairwise set separability.
- A file exists only as a candidate until every required artistic, Alpha-edge, profile, continuity, and receipt gate passes.

## Inputs

Identify:

1. Stable character ID, display name, approved portrait path, and portrait SHA-256.
2. Expression requirements and any approved reusable expression assets.
3. For each expression: class, brow signal, eye/gaze signal, mouth signal, intensity, signature cues, contrast against calm, forbidden confusions, and permitted small performance delta.
4. Requested profiles. Unit3 defaults to both.
5. Approved portrait viewpoint lock and protected light regions.
6. Execution mode. Stop before generation until the user explicitly says to begin.

## State-machine summary

1. `E0_INTAKE_AND_CENSUS`: map portraits to roles, normalize requirements, inventory reusable assets, and freeze the true production delta.
2. `E1_PORTRAIT_SOURCE_LOCK`: verify approval, identity, source integrity, viewpoint, detail budget, requested crop and `PORTRAIT_COMPLETION_USED=false`. A pending manual portrait return resumes through the affected E0 mapping and E1 source acceptance; it never skips directly to expression generation.
3. `E2_EXPRESSION_PLANNING`: freeze expression signals, intensity, performance bounds, prompts, and retry budgets.
4. `E3_EXPRESSION_GENERATION`: generate each non-calm state independently from the approved portrait. Calm bypasses generation.
5. `E4_ARTISTIC_REVIEW_AND_COLOR`: pass expression, identity, style, texture, detail, lighting, viewpoint, and semantic-color gates before technical extraction.
6. `E5_PRE_ALPHA_HANDOFF`: package the artistically accepted calm and non-calm native images, hashes, manifest, and clear `NON_FINAL` status for the user's in-place manual background processing, then stop.
7. `E6_USER_RETURNED_RGBA_INGEST`: after the user confirms that those exact handoff files were edited in place, verify their pre-edit manifest mapping and unchanged subject content, build multi-background previews, and pass `ALPHA_EDGE_GATE` without modifying Alpha.
8. `E7_DUAL_PROFILE_COMPOSITION`: use the same frozen user-returned RGBA foreground to compose transparent and exact-green outputs independently.
9. `E8_PROFILE_AUDIT`: validate canvas, mode, background/Alpha, guide placement, no-upscale/single-resample history, and cross-profile source identity.
10. `E9_SET_CONTINUITY`: review each same-profile set for identity, geometry, detail, lighting, expression readability, and pairwise separability.
11. `E10_FORMAL_RECEIPT_AND_RELEASE`: validate schema-12 manual receipts or schema-13 explicit Photoshop receipts and publish only a complete `RELEASE_STATUS: PASS` package.

## Mechanical tools

Use scripts as evidence and deterministic processors, never as artistic approvers:

```text
python scripts/prepare_alpha_edge_review.py --input <native-rgba.png> --output-dir <alpha-edge-qa-dir>
python scripts/compose_profile_asset.py --input <edge-pass-native-rgba.png> --profile transparent --scale <scale-at-or-below-1> --offset-x <x> --offset-y <y> --output <transparent.png> --audit <transparent-composition.json>
python scripts/compose_profile_asset.py --input <edge-pass-native-rgba.png> --profile greenscreen --scale <scale-at-or-below-1> --offset-x <x> --offset-y <y> --output <greenscreen.png> --audit <greenscreen-composition.json>
python scripts/audit_cross_profile_source_consistency.py --greenscreen-audit <greenscreen-composition.json> --transparent-audit <transparent-composition.json> --expression-id <id> --output <cross-profile-source-audit.json>
python scripts/prepare_profile_guide_review.py --profile transparent --input <transparent.png> --landmarks <reviewed-landmarks.json> --output-dir <guide-qa-dir>
python scripts/prepare_profile_guide_review.py --profile greenscreen --input <greenscreen.png> --landmarks <reviewed-landmarks.json> --output-dir <guide-qa-dir>
python scripts/audit_expression_asset.py --profile transparent --input <transparent.png> --anchor <transparent-calm.png> --state-class <class> --output-dir <qa-dir>
python scripts/audit_expression_asset.py --profile greenscreen --input <greenscreen.png> --anchor <greenscreen-calm.png> --state-class <class> --output-dir <qa-dir>
python scripts/audit_expression_set.py --manifest <expression-job.json> --profile <profile> --input-dir <profile-dir> --output-dir <set-qa-dir>
python scripts/validate_expression_receipt.py --receipt <expression-delivery-receipt.json>
python scripts/audit_expression_delivery_release.py --registry <release-evidence-registry.json> --output <release-audit.json>
```

`prepare_alpha_edge_review.py` is review-only in this workflow. It creates white, gray, black, and exact-green previews plus an Alpha visualization from the user-returned RGBA file. Codex must inspect them and write the PASS/FAIL review record; it must not change the user's Alpha or edge RGB.

## Formal output contract

The first delivery is a non-final `PRE_ALPHA_HANDOFF` package under `工作过程文件`. It contains the artistically accepted native images and hashes, clearly marks background processing as pending user action, and contains no transparent/green delivery claim. The user edits those PNGs in their original handoff directory and keeps the filenames and canvas unchanged; the manifest retains the pre-edit hashes as provenance.

Before copying anything to `最终交付` after the user confirms the in-place edits, every required `character + expression` must have:

- one frozen, edge-passing user-returned native RGBA foreground;
- one transparent profile asset;
- one greenscreen profile asset;
- a cross-profile audit proving both came from the same RGBA SHA-256;
- current artistic, Alpha-edge, profile, set-continuity, and receipt evidence.

Return concise sections covering current state, portrait/requirement mapping, production delta, generation decisions, non-final handoff inventory or user-returned Alpha review, both profile inventories when applicable, set review, and formal release status. Never describe a generation as started until the user explicitly authorizes it, and never describe the pre-Alpha handoff as final delivery.
