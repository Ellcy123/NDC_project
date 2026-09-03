---
name: ndc-coordinate-image-edit
description: Perform non-destructive, coordinate-locked cleanup, evidence placement, and structural repair on NDC raster art through bounded authorization regions, legal generation crops, per-job residue checks, axis-aware seam scans, deterministic bridges, and a final union-mask zero-drift audit. Use for localized removal, cleanup, replacement, material repair, evidence insertion, or grid/line alignment; do not use for whole-image generation or broad restyling.
---

# NDC Coordinate Image Edit

This is the only supported NDC local-raster repair workflow. The image model supplies appearance inside a bounded region; deterministic code owns crop legality, masks, registration, placement, seam repair, and verification.

Use [scripts/coordinate_patch.py](scripts/coordinate_patch.py) for every job. Legacy `scan-seam` and `repair-vertical-seam` commands remain only so old manifests can be inspected; do not use them for new work.

## Mandatory stage-end visual self-check gate

Every art-production stage executed by this Skill must end with an actual visual self-check before its output may be accepted, passed to a later formal stage, packaged, or released. This includes source/mask acceptance, generation, deterministic recomposition, structural repair, accepted full-scene composition, Map/Big/Icon derivation, state export, and final packaging. Inspect the current whole image at `100%` and every applicable local region at nearest-neighbor `200%` or through complete original-pixel tiles. Compare against the frozen source, authorized change, protected regions, and every applicable structure, residue, perspective, scale, contact, shadow, style, texture, edge, text, and runtime-readability requirement.

Write one current `ndc-stage-visual-self-check/v1` JSON record per executed stage. It must bind the stage ID, reviewer/date, input and output paths plus SHA-256, the inspected `whole_100` and `local_200_or_tiles` views, every applicable criterion with an explicit finding and `PASS`/`FAIL`/`NOT_CHECKED`, the overall `visual_check_status`, and the responsible rework stage when blocked. Missing record, missing visual-detection item, stale output hash, missing required view, `FAIL`, or `NOT_CHECKED` is `STAGE_VISUAL_SELF_CHECK_GATE: BLOCKED`: do not mark the stage passed, use its output downstream, or call it formal. Technical validators, dimensions, hashes, masks, boundary/seam reports, or absence of a detected error cannot write visual `PASS`.

After a block, return to the responsible stage, perform the missing inspection and required repair/regeneration, then repeat the visual self-check on the new current output. Release only after the current hash has a passing record. For every file-producing stage, run `python D:/Codex/NDC/scripts/validate-ndc-stage-visual-self-check.py --record <visual-review.json> --artifact <current-output>`; a nonzero result is a hard stop. The existing per-stage retry ceiling still applies, and exhausting it leaves a candidate rather than weakening this gate. The more detailed `visual_review.json` and terminal presence rules below remain mandatory and may satisfy this gate only when they contain the same required evidence.

## Delivery invariants

- Never overwrite the original source. Work in one unique `<system-temp>/ndc_art_jobs/<task-name>-<uuid>/` directory. Return accepted runtime art to the parent evidence workflow; do not publish crops, masks, candidates, or reports directly into the repository.
- Treat rectangles as half-open `[left, right)` and `[top, bottom)` using a recorded top-left origin unless the user explicitly supplied another origin.
- Before the first image-file modification or generation, record the source path, regions to change, and protected elements in the job manifest. When the user's confirmed task and project material reliably determine those inputs, enter production directly; do not wait for a separate `before -> after` or candidate-review confirmation. Request clarification only when a material requirement cannot be reliably determined.
- Split disjoint edits into sequential jobs. Each job uses the last accepted full-size result as its source, but final verification always compares the finished image with the original source.
- For removal and repair, keep the source-sized authorization mask bounded to the affected object or structural group. Include cast shadow, glow, loose fragments, edge residue, and required reconstruction context; exclude protected frames, architecture, and unrelated objects.
- For a newly inserted collectible evidence prop, do not trace the proposed silhouette with the parent authorization mask. Treat it as a generous authoring workspace on the legal support surface. Prefer the whole usable tray, tabletop, drawer interior, floor patch, or other placement surface. Unless a protected scene boundary prevents it, its bounding box must be at least `3x` the proposed object bounding box on both axes and leave at least `128 source pixels` on every unoccluded side. When those requirements conflict, use the larger region.
- Keep the parent authorization workspace separate from the final composition mask. After generation, build the composition mask around the actual complete object and the support-surface material that must be recomposed. It must remain a subset of the confirmed parent workspace and leave at least `64 source pixels` between every unoccluded semantic edge/shadow and its hard boundary. It may be smaller than the parent workspace so harmless model drift does not inflate the runtime Map crop, but it must never collapse back to a silhouette trace.
- Feather only inward. Every pixel outside the hard mask must remain byte-identical to that job's source.
- Prefer a `1024x1024` real-source crop whenever it contains the edit and sufficient registration context. Never resize the authorized target to make the crop legal.
- A generation crop must have edges divisible by 16, neither edge above 3840px, aspect ratio at most 3:1, and 655,360–8,294,400 total pixels. Expand into real source context to satisfy these limits.
- The returned AI patch must have exactly the same aspect ratio as the prepared crop. Reject it instead of stretching or center-cropping it.
- The final file must be PNG, match the original size and mode, and be byte-identical outside the union of all confirmed masks.
- For each defined record and production stage, make at most `3` fresh AI generation attempts without pausing for per-attempt approval. Persist every candidate under a versioned temporary path and append its result immediately to `<ndc-temp-work>/generation_attempt_log.json` with `recordId`, `stage`, `attempt`, `candidatePath`, `result`, `reasonCodes`, and a concise `reasonDetail`. Deterministic recomposition, registration, mask refinement, or a mask-authorized structural bridge using an already persisted candidate does not consume an attempt.
- Accept the first candidate that passes all machine and visual gates. If attempt `3` is rejected, make no fourth generation call: set the record/stage status to `skipped_after_3_failed_generations`, retain all three candidates until the parent batch reaches a normal terminal publish, record the three rejection reasons, and return control so the next independent record can proceed. At terminal publication the parent compacts those reasons into `production_report.json` and deletes the temporary candidates. A new set of attempts requires a new user task or an authorized scope expansion, not a separate review of the existing task.
- When three consecutive candidates at the same support location fail for the same visual reason—such as floating, absent contact/cast shadow, incompatible perspective, scale, or the same occlusion conflict—lock that location against a fourth attempt. Record the common reason, return to the frozen source, and choose another independent support surface. Do not use a container as a direct-pickup workaround: an object physically inside, held by, or protruding from a basket, drawer, box, bag, pocket, or similar container belongs to the parent evidence workflow's Type 6 -> Type 7 container chain, not a freestanding scene-prop edit.

### Non-bypassable visual-review records

Every executed stage—candidate generation, deterministic recomposition, structure repair, accepted full-scene composition, Map crop, standalone Big, Icon master/final, and requested state image—must write a process-only `visual_review.json` before its output can be accepted as an input to a later formal stage. The record must identify the stage, input/output paths and SHA-256 values, review date, whole-image `100%` view, local nearest-neighbor `200%` or greater view, inspected review-image paths, applicable criteria, and one explicit `PASS` or `FAIL` conclusion for each criterion. Technical reports, image dimensions, outside-mask equality, hashes, and the absence of a detected error cannot write visual `PASS` automatically.

For in-scene objects, review and record support contact, occlusion, contact/cast shadow direction, perspective, scale against scene anchors, lighting/value integration, material/edge integration, spatial/movement conflicts, and mask-boundary completeness. A prop that reads as floating or half-floating is `FAIL` even when every pixel-containment check succeeds. For standalone evidence, record silhouette, physical construction, texture/style consistency, exact-text legibility, Alpha/edge appearance, and runtime-frame readability as applicable.

At terminal publication, write `final_visual_record_presence_gate.json` in the process directory. It must enumerate every executed stage and every formal PNG role, verify each current output hash against a matching passing `visual_review.json`, and report `FINAL_VISUAL_RECORD_PRESENCE_GATE: PASS`. Missing records, missing required views, stale hashes, incomplete criteria, or an unresolved `FAIL` are `NOT_CHECKED`/`FAIL` and block handoff. This is an internal quality gate; it does not restore a user-by-user approval pause.

## Canonical workflow

### 1. Load the runtime and inspect the source

Call `codex_app__load_workspace_dependencies` and use its bundled Python executable. Store it in a task-specific variable such as `$ndcImagePython`.

Resolve the system temporary root and create a unique child before any raster work:

```powershell
$ndcTempNamespace = Join-Path ([System.IO.Path]::GetTempPath()) "ndc_art_jobs"
$ndcWorkRoot = Join-Path $ndcTempNamespace "<task-name>-<uuid>"
```

Verify the resolved `$ndcWorkRoot` is a strict child of `$ndcTempNamespace`. Do not use the namespace root itself as a job or cleanup target.

Open the original with `view_image`. List every edit region and divide it into independent jobs, for example:

1. desktop objects;
2. wastebasket;
3. sorting-grid interior;
4. a later deterministic seam bridge, only if a scan fails.

Do not use an earlier rejected preview as the new original.

### 2. Build bounded masks and legal crops

Create source-sized masks. One object may use one polygon; overlapping objects that require a single reconstructed surface may share one mask. Preserve real surrounding material inside the crop so the model can infer texture and registration.

For collectible evidence placement, first make a tight intent mask that records the proposed object envelope, then expand it deterministically into the broad authorization workspace. The intent mask is a planning artifact, not the final hard mask. Use `expand-mask`; the command fails rather than silently clipping the required `3x` workspace or `128px` side margins:

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" expand-mask `
  --input "$ndcWorkRoot/intent_mask.png" `
  --output "$ndcWorkRoot/authorization_mask.png" `
  --scale 3 `
  --min-margin 128 `
  --limit-rect 1024 384 2048 1408 `
  --report "$ndcWorkRoot/authorization_mask_report.json"
```

Inspect both masks over the full scene. A rectangular broad workspace is acceptable when the prompt and protected-element list keep unrelated content unchanged; it is not required to hug the object contour.

After a candidate exists, create the final composition mask from the candidate's actual object, shadow, and necessary support-surface patch. Prepare a second manifest with the same source and crop, use this composition mask, and compose from the already persisted `generated.png`; this deterministic recomposition does not authorize or require another generation. In final verification, pass the parent authorization mask as the legal union and the composition manifest as the executed job.

Prepare an AI job with an explicit legal crop:

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" prepare `
  --source "D:/NDC_project/image/source.png" `
  --edit-rect 1170 925 1860 1040 `
  --crop-rect 1008 464 2032 1488 `
  --mask "$ndcWorkRoot/masks/desktop-mask.png" `
  --feather 5 `
  --canvas-kind generation `
  --out-dir "$ndcWorkRoot/01-desktop"
```

Inspect `source_crop.png`, `hard_mask.png`, and `manifest.json` before generation. The white hard-mask area must include all removable residue while excluding every protected boundary.

If a target such as `1730x520` exceeds 3:1, expand the real-source crop, for example to `1744x592`; do not scale the target. Prefer a square crop when it comfortably fits, because square model outputs avoid aspect drift.

### 3. Generate one full crop for the confirmed job

Use built-in `image_gen` with `source_crop.png` in `referenced_image_paths`. Do not use `num_last_images_to_include` for a local crop. Ask for the edited full crop, not an isolated object.

```text
Use case: precise-object-edit
Asset type: NDC localized raster repair
Input image: the exact prepared context crop
Primary request: remove or repair only the confirmed objects/structure
Style/medium: preserve the source illustration, line weight, palette, material wear, perspective, and lighting
Hard invariants: preserve all named frames and surroundings; keep exact framing and camera; do not crop, zoom, rotate, shift, resize, add text, or add unrelated objects; return the full edited crop
```

When the job inserts an NDC evidence prop into an exploration scene, extend the prompt with a map-view contract. Do not paste the full detail-art requirement into this prompt. Use this structure:

```text
Use case: NDC in-scene evidence anchor
Primary request: add a discoverable scene prop that communicates only its object class, silhouette, material, broad color, and current state.
Map-view information budget: this is not the detail sprite. Do not expose exact titles, dates, numbers, signatures, or body text. At gameplay scale it only needs to read as a folder, ledger, envelope, pen, tool, or other named object class.
Perspective contract: infer ordinary physical scale, visible face, foreshortening, and orientation from the source camera, nearby furniture, support surface, and vanishing lines. A document may show only its edge, spine, thickness, folded corner, or an unreadable cover fragment.
Placement contract: keep the entire object, contact shadow, reflection, and required occlusion inside the authorized edit region.
Hard invariants: do not enlarge, stand up, tilt, rotate, or turn the prop toward the viewer for legibility; do not create a close-up, evidence card, product display, signboard, or readable document; return the full edited crop with unchanged framing and camera.
```

The matching `*_big` detail asset owns close-reading information. Generate it separately from the scene insertion so exact text requirements cannot force the map prop into an oversized frontal presentation.

After generation:

1. use only the returned local saved path;
2. immediately copy it into the job directory as `generated.png`;
3. verify its aspect ratio before composition;
4. never leave a project-bound result only under `$CODEX_HOME/generated_images`.

### 4. Compose and scan every object-mask boundary

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" compose `
  --manifest "$ndcWorkRoot/01-desktop/manifest.json" `
  --ai-patch "$ndcWorkRoot/01-desktop/generated.png" `
  --output "$ndcWorkRoot/01-desktop/step1.png"

& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" scan-boundary `
  --manifest "$ndcWorkRoot/01-desktop/manifest.json" `
  --ring 6
```

Accept the job only when:

- registration is credible and recorded;
- `source_unchanged`, size, and mode checks pass;
- outside-mask differing channels and maximum difference are both `0`;
- `scan-boundary` passes;
- the full image, close crop, and boundary overlay show no retained silhouette, white/black rim, glow, clipped shadow, or strange generated edge.

For in-scene evidence insertion, also reject the job when the prop is oversized relative to nearby objects, turned toward the viewer for legibility, readable like a detail card, inconsistent with the support-surface perspective, or semantically clipped by the hard mask. Run this review on the full scene at expected gameplay display size. Passing containment and boundary reports alone is not acceptance.

For every newly inserted freestanding object, inspect both the parent-authorization overlay and final-composition overlay together with the close crop and gameplay-size full scene. Reject it if any unoccluded semantic edge, tag, loose part, reflection, or shadow comes within `64 source pixels` of the composition hard-mask boundary, if either boundary reads as part of the object, or if a required base/contact shadow merges into the background so that the object appears visually incomplete. A zero outside-mask pixel diff does not waive this completeness check.

If a source-colored fragment remains because the mask was too tight, rebuild the evidence workspace from the intent mask with larger `--scale` or `--min-margin` values and recompose from the persisted generated crop when it already contains the complete object. Regenerate only if the crop itself lacks the complete object or usable replacement texture.

### 5. Scan structural lines in the original orientation

Run a structure scan wherever a paste boundary crosses a long rail, molding, cabinet line, grid divider, desk edge, or similar structure. Do not rotate the image manually.

- `--seam-axis x`: vertical paste boundary; compares horizontal lines on its left and right.
- `--seam-axis y`: horizontal paste boundary; compares vertical lines above and below it.

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" scan-structure `
  --image "$ndcWorkRoot/final-step.png" `
  --rect 2200 800 2225 900 `
  --seam-axis x `
  --seam 2210 `
  --band 6 `
  --max-drift 1 `
  --report "$ndcWorkRoot/grid-left-report.json" `
  --overlay "$ndcWorkRoot/grid-left-overlay.png"
```

The scan rectangle must cover only the structure that is supposed to continue through the edited mask. Exclude preserved outer frames, diagonal perspective edges, curves, and neighboring material seams; otherwise their legitimate slope can be misclassified as paste drift.

Delivery requires `passed: true`, no blocking unmatched edge, and `max_observed_drift <= 1`. Inspect the overlay and close crop even when the report passes.

### 6. Repair a failed line with a mask-authorized narrow bridge

Do not move the entire AI patch, blur the seam, average a wide wall area, or regenerate first. Create a new repair job from the last accepted full-size image. Its mask must be a narrow source-sized strip inside the original parent authorization mask.

Keep the bridge normally 8–12px deep. The helper refuses a deeper bridge and verifies that the repair mask is a subset of the parent mask.

```powershell
# Prepare a small deterministic job; this crop is not sent to the image model.
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" prepare `
  --source "$ndcWorkRoot/02-grid/step2.png" `
  --edit-rect 2210 800 2222 900 `
  --crop-rect 2180 780 2250 920 `
  --mask "$ndcWorkRoot/masks/grid-left-bridge-mask.png" `
  --feather 2 `
  --canvas-kind deterministic `
  --out-dir "$ndcWorkRoot/03-grid-left-bridge"

& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" repair-structure `
  --manifest "$ndcWorkRoot/03-grid-left-bridge/manifest.json" `
  --seam-axis x `
  --seam 2210 `
  --direction positive `
  --sample-band 16 `
  --anchor-width 4 `
  --max-depth 12 `
  --authorization-mask "$ndcWorkRoot/masks/grid-mask.png"

& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" compose `
  --manifest "$ndcWorkRoot/03-grid-left-bridge/manifest.json" `
  --ai-patch "$ndcWorkRoot/03-grid-left-bridge/generated.png" `
  --registration off
```

Direction meanings:

- axis `x`, positive: extend protected pixels from the left toward the right;
- axis `x`, negative: extend protected pixels from the right toward the left;
- axis `y`, positive: extend protected pixels from above downward;
- axis `y`, negative: extend protected pixels from below upward.

Re-run `scan-structure` on the repaired boundary. Keep the failed pre-repair report and passing post-repair report. If the intended structure is curved, diagonal, perspective-changing within the bridge, or semantically complex, do not use deterministic extension; request a new bounded generation instead.

### 7. Verify the chained final against the original

After all jobs and bridges, compare the final PNG with the original through the union of every confirmed parent mask:

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" verify-final `
  --source "D:/NDC_project/image/source.png" `
  --output "$ndcWorkRoot/final.png" `
  --mask "$ndcWorkRoot/masks/desktop-mask.png" `
  --mask "$ndcWorkRoot/masks/grid-mask.png" `
  --manifest "$ndcWorkRoot/01-desktop/manifest.json" `
  --manifest "$ndcWorkRoot/02-grid/manifest.json" `
  --manifest "$ndcWorkRoot/03-grid-left-bridge/manifest.json" `
  --scan-report "$ndcWorkRoot/01-desktop/boundary_report.json" `
  --scan-report "$ndcWorkRoot/02-grid/boundary_report.json" `
  --scan-report "$ndcWorkRoot/grid-left-report-after.json"
```

Pass every composed AI/deterministic job manifest in execution order and every required passing boundary/structure report. The manifest chain must begin at the original source and end at the final PNG. A report is accepted only when its recorded image hash belongs to that chain; a boundary report must also point to its exact manifest output.

Final delivery requires:

- source and output size/mode match;
- `outside_union_nonzero_channels == 0`;
- `outside_union_max_channel_difference == 0`;
- `outside_union_pixels_bit_identical == true`;
- `manifest_chain_passed == true`;
- `all_job_manifests_passed == true`;
- `all_scan_reports_passed == true`;
- every residue scan and relevant structure scan passes;
- visual inspection of the full image and close crops finds no semantic damage or odd edges.
- every executed stage and each final PNG role has a hash-matching passing visual-review record, and `FINAL_VISUAL_RECORD_PRESENCE_GATE == PASS`.

### 8. Hand off and recover

Before parent publication, inspect the full image and close crops. Return internally to the parent:

- original source and final PNG paths;
- the temporary parent masks and job manifests;
- final prompts and built-in generation mode;
- registration scale/dx/dy for each AI job;
- boundary and structure scan results;
- the temporary `final_verification.json` path and four final containment fields;
- whether the official asset was left untouched.

Recover an interrupted job with:

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" status `
  --manifest "$ndcWorkRoot/01-object/manifest.json"
```

- prepared without `generated.png`: generation has not been persisted;
- prepared with `generated.png`: compose it; do not regenerate;
- composed: inspect existing output and reports; do not repeat the job.

Do not copy masks, manifests, prompts, generated candidates, close crops, overlays, or verification JSON into the project-facing delivery. The parent evidence router publishes only accepted runtime PNGs, one scene-level `XYposition.txt`, one compact `production_report.json`, and the scene preview, then cleans the exact temporary job after verified publication. An interrupted job remains in the temporary namespace for recovery.
