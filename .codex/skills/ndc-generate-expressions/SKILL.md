---
name: ndc-generate-expressions
description: Plan, generate, hand off, resume, audit, normalize, and package NDC bust-expression sets from user-confirmed completed portraits. Use for NDC or 摩登迷城 expression requirements, non-final pre-Alpha handoff, ingestion of user-returned manually processed RGBA files, paired transparent and exact-green delivery profiles, and expression-set QA. Do not use to complete missing portrait regions, remove backgrounds for the user, redesign a character, create full-body states, or place characters into scenes.
---

# NDC Generate Expressions

## Operating boundary

This Skill begins from a user-confirmed, already completed portrait. It never outpaints, extends, reconstructs, or generates missing hair, hat, shoulder, chest, costume, or body regions. If an input portrait is missing, unapproved, identity-ambiguous, or not ready for the requested delivery crop, return `UPSTREAM_PORTRAIT_REQUIRED`; do not repair it inside this Skill.

## Mandatory stage-end visual self-check gate

Every art-production stage executed by this Skill must end with an actual visual self-check before its output may be accepted, passed to a later formal stage, handed off, packaged, or released. This includes portrait-source acceptance, reuse acceptance, expression generation, artistic/color review, pre-Alpha handoff acceptance, returned-RGBA ingest, Alpha-edge review, profile composition, profile/set audit, normalization, and final packaging. Inspect the current whole image at `100%` and every applicable local region at nearest-neighbor `200%` or through complete original-pixel tiles. Compare against the approved portrait authority and every applicable identity, viewpoint, expression, anatomy, costume, lighting, color, style, texture, edge, Alpha, profile, placement, continuity, and runtime-readability requirement.

Write one current `ndc-stage-visual-self-check/v1` JSON record per executed stage. It must bind the stage ID, reviewer/date, input and output paths plus SHA-256, the inspected `whole_100` and `local_200_or_tiles` views, every applicable criterion with an explicit finding and `PASS`/`FAIL`/`NOT_CHECKED`, the overall `visual_check_status`, and the responsible rework stage when blocked. Missing record, missing visual-detection item, stale output hash, missing required view, `FAIL`, or `NOT_CHECKED` is `STAGE_VISUAL_SELF_CHECK_GATE: BLOCKED`: do not advance state, hand off the file, use it downstream, or call it formal. Technical validators, dimensions, hashes, Alpha/profile reports, or absence of a detected error cannot write visual `PASS`.

After a block, return to the responsible stage allowed by this Skill's authorship boundary, perform the missing inspection and authorized rework/regeneration, then repeat the visual self-check on the new current output. Release only after the current hash has a passing record. For every file-producing stage, run `python D:/Codex/NDC/scripts/validate-ndc-stage-visual-self-check.py --record <visual-review.json> --artifact <current-output>`; a nonzero result is a hard stop. Existing retry ceilings and the ban on Codex background/Alpha repair remain unchanged; when the responsible repair belongs to the user, stop at the required rework status instead of weakening this gate.

The user-approved portrait is the identity, viewpoint, costume, lighting, style, texture, and calm-expression authority. Never regenerate calm. Every non-calm expression is generated directly from that portrait, never from another expression or a failed candidate.

Default to prompt and manifest preparation. Execute image generation only after the user explicitly authorizes Codex execution. A request to update this Skill, inspect portraits, or plan requirements is not authorization to start generation.

For Unit3, treat the image files in `D:\PMH\工作\人设\003第三章\头像` as the user-confirmed completed portrait set. This directory is read-only. Copy required inputs into `D:\Codex\NDC\工作过程文件\角色表情\Unit3` before production; never modify PMH files.

## Required reading

Read only the references needed for the current stage:

1. [references/workflow.md](references/workflow.md) for the complete state machine.
2. [references/expression-planning-and-prompts.md](references/expression-planning-and-prompts.md) before requirement planning or generation.
3. [references/manual-background-handoff-and-return.md](references/manual-background-handoff-and-return.md) before making the non-final handoff or accepting user-returned RGBA files.
4. [references/delivery-profiles.md](references/delivery-profiles.md) before composing either delivery format.
5. [references/profile-guides-and-source-integrity.md](references/profile-guides-and-source-integrity.md) before approving profile placement.
6. [references/self-check-and-rework.md](references/self-check-and-rework.md) before review, retry, or delivery.
7. [references/receipt-schema.md](references/receipt-schema.md) before formal packaging.
8. Read the remaining focused references only when their named concern applies: reuse, viewpoint, style fallback, readability, source detail/lighting, or semantic color.

## Non-negotiable invariants

- `PORTRAIT_COMPLETION_USED=false` for every job. There is no completion stage, completion prompt, completion mask, outpaint retry, or anatomical repair route in this Skill.
- Calm is the approved portrait. It is copied unchanged into the non-final handoff and is never regenerated.
- Generate each non-calm expression directly from the same approved portrait on a plain, uniform light background suitable for the user's manual background processing.
- Codex never removes the background, creates a cutout, removes white fringe, paints an Alpha mask, or uses Photoshop for this stage. Do not run `remove_expression_background.py` or any other automatic, deterministic, generative, or Photoshop background-removal route.
- After every requested expression passes artistic review, stop and deliver a `PRE_ALPHA_HANDOFF` package under `工作过程文件`. It is explicitly non-final and must not be copied to `最终交付`. The user edits those exact handoff PNG files in place; do not create or require a separate return folder.
- Resume only after the user confirms that the in-place handoff files have been manually background-processed as native RGBA. If their Alpha or edge RGB fails review, return `USER_ALPHA_REWORK_REQUIRED`; do not repair the background or white fringe inside this Skill.
- Never remove light pixels globally. White shirts, collars, eye whites, hair highlights, jewelry, pale linework, and other intentional light design are protected subject content.
- A transparent cutout is not approved until `ALPHA_EDGE_GATE=PASS`: inspect the whole silhouette and critical hair/shoulder/costume edges on white, mid-gray, dark gray, black, and exact `#00FF2B` at native 100% and nearest 200%. Any white halo, matte contamination, remote island, hole, erosion, jagged edge, or missing subject region is `FAIL`.
- Do not hide a failed edge with inward erosion. Repair only the Alpha/matte calculation or use a reviewed manual non-generative mask from the unchanged generated candidate.
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
2. `E1_PORTRAIT_SOURCE_LOCK`: verify approval, identity, source integrity, viewpoint, detail budget, and `PORTRAIT_COMPLETION_USED=false`. Incomplete inputs block; they are never repaired here.
3. `E2_EXPRESSION_PLANNING`: freeze expression signals, intensity, performance bounds, prompts, and retry budgets.
4. `E3_EXPRESSION_GENERATION`: generate each non-calm state independently from the approved portrait. Calm bypasses generation.
5. `E4_ARTISTIC_REVIEW_AND_COLOR`: pass expression, identity, style, texture, detail, lighting, viewpoint, and semantic-color gates before technical extraction.
6. `E5_PRE_ALPHA_HANDOFF`: package the artistically accepted calm and non-calm native images, hashes, manifest, and clear `NON_FINAL` status for the user's in-place manual background processing, then stop.
7. `E6_USER_RETURNED_RGBA_INGEST`: after the user confirms that those exact handoff files were edited in place, verify their pre-edit manifest mapping and unchanged subject content, build multi-background previews, and pass `ALPHA_EDGE_GATE` without modifying Alpha.
8. `E7_DUAL_PROFILE_COMPOSITION`: use the same frozen user-returned RGBA foreground to compose transparent and exact-green outputs independently.
9. `E8_PROFILE_AUDIT`: validate canvas, mode, background/Alpha, guide placement, no-upscale/single-resample history, and cross-profile source identity.
10. `E9_SET_CONTINUITY`: review each same-profile set for identity, geometry, detail, lighting, expression readability, and pairwise separability.
11. `E10_FORMAL_RECEIPT_AND_RELEASE`: validate schema-12 receipts and publish only a complete `RELEASE_STATUS: PASS` package.

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
