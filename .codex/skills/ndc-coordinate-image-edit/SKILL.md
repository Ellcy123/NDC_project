---
name: ndc-coordinate-image-edit
description: Perform non-destructive, coordinate-locked cleanup and structural repair on NDC raster art through small authorization masks, legal generation crops, per-job residue checks, axis-aware seam scans, narrow deterministic bridges, and a final union-mask zero-drift audit. Use for localized removal, cleanup, replacement, material repair, or grid/line alignment; do not use for whole-image generation or broad restyling.
---

# NDC Coordinate Image Edit

This is the only supported NDC local-raster repair workflow. The image model supplies appearance inside a bounded region; deterministic code owns crop legality, masks, registration, placement, seam repair, and verification.

Use [scripts/coordinate_patch.py](scripts/coordinate_patch.py) for every job. Legacy `scan-seam` and `repair-vertical-seam` commands remain only so old manifests can be inspected; do not use them for new work.

## Delivery invariants

- Never overwrite the original source. Work in `image/edit_jobs/<task-name>/` and deliver a versioned PNG.
- Treat rectangles as half-open `[left, right)` and `[top, bottom)` using a recorded top-left origin unless the user explicitly supplied another origin.
- Before the first image-file modification or generation, show a real `before -> after` example with the source path, regions to change, and protected elements; wait for explicit confirmation unless that exact edit was already confirmed in the current task.
- Split disjoint edits into sequential jobs. Each job uses the last accepted full-size result as its source, but final verification always compares the finished image with the original source.
- Use a small source-sized authorization mask for each object or tightly related structural group. Include the object's cast shadow, glow, loose fragment, and edge residue; exclude preserved frames, table edges, architecture, and unrelated pixels.
- Feather only inward. Every pixel outside the hard mask must remain byte-identical to that job's source.
- Prefer a `1024x1024` real-source crop whenever it contains the edit and sufficient registration context. Never resize the authorized target to make the crop legal.
- A generation crop must have edges divisible by 16, neither edge above 3840px, aspect ratio at most 3:1, and 655,360–8,294,400 total pixels. Expand into real source context to satisfy these limits.
- The returned AI patch must have exactly the same aspect ratio as the prepared crop. Reject it instead of stretching or center-cropping it.
- The final file must be PNG, match the original size and mode, and be byte-identical outside the union of all confirmed masks.
- A failed or visually rejected generation does not authorize another call. Ask before regenerating. Deterministic recomposition or a mask-narrow structural bridge using the already persisted patch does not require regeneration.

## Canonical workflow

### 1. Load the runtime and inspect the source

Call `codex_app__load_workspace_dependencies` and use its bundled Python executable. Store it in a task-specific variable such as `$ndcImagePython`.

Open the original with `view_image`. List every edit region and divide it into independent jobs, for example:

1. desktop objects;
2. wastebasket;
3. sorting-grid interior;
4. a later deterministic seam bridge, only if a scan fails.

Do not use an earlier rejected preview as the new original.

### 2. Build the smallest masks and legal crops

Create source-sized masks. One object may use one polygon; overlapping objects that require a single reconstructed surface may share one mask. Preserve a strip of real surrounding material inside the crop so the model can infer texture and registration.

Prepare an AI job with an explicit legal crop:

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" prepare `
  --source "D:/NDC_project/image/source.png" `
  --edit-rect 1170 925 1860 1040 `
  --crop-rect 1008 464 2032 1488 `
  --mask "D:/NDC_project/image/edit_jobs/task/masks/desktop-mask.png" `
  --feather 5 `
  --canvas-kind generation `
  --out-dir "D:/NDC_project/image/edit_jobs/task/01-desktop"
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

After generation:

1. use only the returned local saved path;
2. immediately copy it into the job directory as `generated.png`;
3. verify its aspect ratio before composition;
4. never leave a project-bound result only under `$CODEX_HOME/generated_images`.

### 4. Compose and scan every object-mask boundary

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" compose `
  --manifest "D:/NDC_project/image/edit_jobs/task/01-desktop/manifest.json" `
  --ai-patch "D:/NDC_project/image/edit_jobs/task/01-desktop/generated.png" `
  --output "D:/NDC_project/image/edit_jobs/task/01-desktop/step1.png"

& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" scan-boundary `
  --manifest "D:/NDC_project/image/edit_jobs/task/01-desktop/manifest.json" `
  --ring 6
```

Accept the job only when:

- registration is credible and recorded;
- `source_unchanged`, size, and mode checks pass;
- outside-mask differing channels and maximum difference are both `0`;
- `scan-boundary` passes;
- the full image, close crop, and boundary overlay show no retained silhouette, white/black rim, glow, clipped shadow, or strange generated edge.

If a small source-colored fragment remains because the mask was too tight, expand only that object's mask within the already confirmed edit rectangle and recompose from the persisted generated crop. Regenerate only if the crop lacks usable replacement texture.

### 5. Scan structural lines in the original orientation

Run a structure scan wherever a paste boundary crosses a long rail, molding, cabinet line, grid divider, desk edge, or similar structure. Do not rotate the image manually.

- `--seam-axis x`: vertical paste boundary; compares horizontal lines on its left and right.
- `--seam-axis y`: horizontal paste boundary; compares vertical lines above and below it.

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" scan-structure `
  --image "D:/NDC_project/image/edit_jobs/task/final-step.png" `
  --rect 2200 800 2225 900 `
  --seam-axis x `
  --seam 2210 `
  --band 6 `
  --max-drift 1 `
  --report "D:/NDC_project/image/edit_jobs/task/grid-left-report.json" `
  --overlay "D:/NDC_project/image/edit_jobs/task/grid-left-overlay.png"
```

The scan rectangle must cover only the structure that is supposed to continue through the edited mask. Exclude preserved outer frames, diagonal perspective edges, curves, and neighboring material seams; otherwise their legitimate slope can be misclassified as paste drift.

Delivery requires `passed: true`, no blocking unmatched edge, and `max_observed_drift <= 1`. Inspect the overlay and close crop even when the report passes.

### 6. Repair a failed line with a mask-authorized narrow bridge

Do not move the entire AI patch, blur the seam, average a wide wall area, or regenerate first. Create a new repair job from the last accepted full-size image. Its mask must be a narrow source-sized strip inside the original parent authorization mask.

Keep the bridge normally 8–12px deep. The helper refuses a deeper bridge and verifies that the repair mask is a subset of the parent mask.

```powershell
# Prepare a small deterministic job; this crop is not sent to the image model.
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" prepare `
  --source "D:/NDC_project/image/edit_jobs/task/02-grid/step2.png" `
  --edit-rect 2210 800 2222 900 `
  --crop-rect 2180 780 2250 920 `
  --mask "D:/NDC_project/image/edit_jobs/task/masks/grid-left-bridge-mask.png" `
  --feather 2 `
  --canvas-kind deterministic `
  --out-dir "D:/NDC_project/image/edit_jobs/task/03-grid-left-bridge"

& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" repair-structure `
  --manifest "D:/NDC_project/image/edit_jobs/task/03-grid-left-bridge/manifest.json" `
  --seam-axis x `
  --seam 2210 `
  --direction positive `
  --sample-band 16 `
  --anchor-width 4 `
  --max-depth 12 `
  --authorization-mask "D:/NDC_project/image/edit_jobs/task/masks/grid-mask.png"

& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" compose `
  --manifest "D:/NDC_project/image/edit_jobs/task/03-grid-left-bridge/manifest.json" `
  --ai-patch "D:/NDC_project/image/edit_jobs/task/03-grid-left-bridge/generated.png" `
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
  --output "D:/NDC_project/image/edit_jobs/task/final.png" `
  --mask "D:/NDC_project/image/edit_jobs/task/masks/desktop-mask.png" `
  --mask "D:/NDC_project/image/edit_jobs/task/masks/grid-mask.png" `
  --manifest "D:/NDC_project/image/edit_jobs/task/01-desktop/manifest.json" `
  --manifest "D:/NDC_project/image/edit_jobs/task/02-grid/manifest.json" `
  --manifest "D:/NDC_project/image/edit_jobs/task/03-grid-left-bridge/manifest.json" `
  --scan-report "D:/NDC_project/image/edit_jobs/task/01-desktop/boundary_report.json" `
  --scan-report "D:/NDC_project/image/edit_jobs/task/02-grid/boundary_report.json" `
  --scan-report "D:/NDC_project/image/edit_jobs/task/grid-left-report-after.json"
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

### 8. Deliver and recover

Show the full image and close crops. Report:

- original source and final PNG paths;
- all parent masks and job manifests;
- final prompts and built-in generation mode;
- registration scale/dx/dy for each AI job;
- boundary and structure scan results;
- `final_verification.json` path and four final containment fields;
- whether the official asset was left untouched.

Recover an interrupted job with:

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" status `
  --manifest "D:/NDC_project/image/edit_jobs/task/01-object/manifest.json"
```

- prepared without `generated.png`: generation has not been persisted;
- prepared with `generated.png`: compose it; do not regenerate;
- composed: inspect existing output and reports; do not repeat the job.
