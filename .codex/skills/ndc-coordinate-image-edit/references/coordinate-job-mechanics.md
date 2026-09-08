# Coordinate job mechanics

Use the current Skill's stable job, remaining generation budget and project process directory throughout these commands. Numeric coordinates below are command examples, never scene defaults; derive every real rectangle/mask from the current source. Ordinary local repair reads this file; evidence-specific authoring rules are conditional in [prop-adapter.md](prop-adapter.md).

### 1. Load the runtime and inspect the source

Call `codex_app__load_workspace_dependencies` and use its bundled Python executable. Store it in a task-specific variable such as `$ndcImagePython`.

Resolve the active project root and its work-process directory, then create a unique recoverable child before any raster work. Resolve `$ndcAssetProcessRoot` to the current asset category and chapter beneath that directory (for example `场景/Unit<n>/<task>` for scene work), inheriting the parent task's classification; do not create an unclassified asset folder directly under `工作过程文件`. Set `$ndcCoordinateScript` to the absolute installed path of this Skill's `scripts/coordinate_patch.py` and `$ndcSource` to the verified source image:

```powershell
$ndcProcessRoot = Join-Path $ndcProjectRoot "工作过程文件"
$ndcWorkRoot = Join-Path $ndcAssetProcessRoot "坐标修图/<task-name>-<uuid>"
```

Verify the resolved `$ndcWorkRoot` is a strict child of `$ndcProcessRoot`. Resume its existing production record and manifests after interruption; do not create a new job/budget merely to continue. Keep candidates and review history after publication. This workflow does not authorize cleanup of other directories.

Open the original with `view_image`. List every edit region and divide it into independent jobs, for example:

1. desktop objects;
2. wastebasket;
3. sorting-grid interior;
4. a later deterministic seam bridge, only if a scan fails.

Do not use an earlier rejected preview as the new original.

### 2. Build bounded masks and legal crops

Create source-sized masks. One object may use one polygon; overlapping objects that require a single reconstructed surface may share one mask. Preserve real surrounding material inside the crop so the model can infer texture and registration.

For inserted evidence, first apply the broad authorization workspace and separate composition-mask rules in [prop-adapter.md](prop-adapter.md). Ordinary removal/repair uses a bounded object or structural mask.

Prepare an AI job with an explicit legal crop:

```powershell
& $ndcImagePython $ndcCoordinateScript prepare `
  --source "$ndcSource" `
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

Reserve the next actual generation in the existing production job before submission; a child crop does not receive a new budget. Use built-in `image_gen` with `source_crop.png` in `referenced_image_paths`. Do not use `num_last_images_to_include` for a local crop. Ask for the edited full crop, not an isolated object.

```text
Use case: precise-object-edit
Asset type: NDC localized raster repair
Input image: the exact prepared context crop
Primary request: remove or repair only the confirmed objects/structure
Style/medium: preserve the source illustration, line weight, palette, material wear, perspective, and lighting
Hard invariants: preserve all named frames and surroundings; keep exact framing and camera; do not crop, zoom, rotate, shift, resize, add text, or add unrelated objects; return the full edited crop
```

For evidence insertion, use the map-view input contract in [prop-adapter.md](prop-adapter.md), not a detail-sprite prompt.

After generation:

1. use only the returned local saved path;
2. immediately copy it into the job directory as `generated.png`;
3. verify its aspect ratio before composition;
4. never leave a project-bound result only under `$CODEX_HOME/generated_images`.

### 4. Compose and scan every object-mask boundary

```powershell
& $ndcImagePython $ndcCoordinateScript compose `
  --manifest "$ndcWorkRoot/01-desktop/manifest.json" `
  --ai-patch "$ndcWorkRoot/01-desktop/generated.png" `
  --output "$ndcWorkRoot/01-desktop/step1.png"

& $ndcImagePython $ndcCoordinateScript scan-boundary `
  --manifest "$ndcWorkRoot/01-desktop/manifest.json" `
  --ring 6
```

Accept the job only when:

- registration is credible and recorded;
- `source_unchanged`, size, and mode checks pass;
- outside-mask differing channels and maximum difference are both `0`;
- `scan-boundary` passes;
- for an RGB or RGBA scene insert with source-identical surroundings, `scan-boundary` may use its exact unchanged-context proof: current source/output/mask hashes, an actually changed inner RGB region, final RGB equal to the registered patch, two unchanged inner boundary rings plus all remaining crop context, and zero changes outside the crop. The complete source Alpha plane must remain byte-identical; when the registered patch carries Alpha, that entire plane must also equal the final crop. An RGB patch supplies no replacement Alpha. Do not flatten or discard existing transparency to obtain a pass. This is exact pixel evidence for a boundary with no generated-delta samples; do not lower sampling thresholds or add background changes to satisfy the scanner. It does not replace any visual or final union-mask gate;
- the full image, close crop, and boundary overlay show no retained silhouette, white/black rim, glow, clipped shadow, or strange generated edge.

For evidence insertion, also apply the gameplay-scale and semantic-completeness checks in [prop-adapter.md](prop-adapter.md).

### 5. Scan structural lines in the original orientation

Run a structure scan wherever a paste boundary crosses a long rail, molding, cabinet line, grid divider, desk edge, or similar structure. Do not rotate the image manually.

- `--seam-axis x`: vertical paste boundary; compares horizontal lines on its left and right.
- `--seam-axis y`: horizontal paste boundary; compares vertical lines above and below it.

```powershell
& $ndcImagePython $ndcCoordinateScript scan-structure `
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
& $ndcImagePython $ndcCoordinateScript prepare `
  --source "$ndcWorkRoot/02-grid/step2.png" `
  --edit-rect 2210 800 2222 900 `
  --crop-rect 2180 780 2250 920 `
  --mask "$ndcWorkRoot/masks/grid-left-bridge-mask.png" `
  --feather 2 `
  --canvas-kind deterministic `
  --out-dir "$ndcWorkRoot/03-grid-left-bridge"

& $ndcImagePython $ndcCoordinateScript repair-structure `
  --manifest "$ndcWorkRoot/03-grid-left-bridge/manifest.json" `
  --seam-axis x `
  --seam 2210 `
  --direction positive `
  --sample-band 16 `
  --anchor-width 4 `
  --max-depth 12 `
  --authorization-mask "$ndcWorkRoot/masks/grid-mask.png"

& $ndcImagePython $ndcCoordinateScript compose `
  --manifest "$ndcWorkRoot/03-grid-left-bridge/manifest.json" `
  --ai-patch "$ndcWorkRoot/03-grid-left-bridge/generated.png" `
  --registration off
```

Direction meanings:

- axis `x`, positive: extend protected pixels from the left toward the right;
- axis `x`, negative: extend protected pixels from the right toward the left;
- axis `y`, positive: extend protected pixels from above downward;
- axis `y`, negative: extend protected pixels from below upward.

Re-run `scan-structure` on the repaired boundary. Keep the failed pre-repair report and passing post-repair report. If the intended structure is curved, diagonal, perspective-changing within the bridge, or semantically complex, do not use deterministic extension; use a new bounded generation only when the same parent job has remaining budget. Otherwise retain the unresolved defect without a new call.

### 7. Verify the chained final against the original

After all jobs and bridges, compare the final PNG with the original through the union of every confirmed parent mask:

```powershell
& $ndcImagePython $ndcCoordinateScript verify-final `
  --source "$ndcSource" `
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
- every current accepted dependency and requested final output has a matching passing review under the production-record protocol; historical rejected/superseded candidates stay archived and cannot be accepted inputs. For a parent workflow requiring the legacy final-presence JSON, validate only that accepted chain and its actual output roles.

### 8. Hand off and recover

Before handoff, inspect the current full image and affected close crops (reuse valid evidence for byte-preserving publication). Return to the caller:

- original source and final PNG paths;
- the recorded parent masks and job manifests;
- final prompts and built-in generation mode;
- registration scale/dx/dy for each AI job;
- boundary and structure scan results;
- the process `final_verification.json` path and four final containment fields;
- whether the official asset was left untouched.

Recover an interrupted job with:

```powershell
& $ndcImagePython $ndcCoordinateScript status `
  --manifest "$ndcWorkRoot/01-object/manifest.json"
```

- prepared without `generated.png`: no result is persisted here; this does not prove no generation occurred. Reconcile the production reservation and returned/local result before submitting again;
- prepared with `generated.png`: compose it; do not regenerate;
- composed: inspect existing output and reports; do not repeat the job.

Keep masks, manifests, prompts, candidates, close crops, overlays and verification JSON in the project work-process directory, including after publication. Return only the caller's requested accepted PNGs to its formal delivery path. A standalone cleanup has no implicit Map/Big/Icon, XYposition, evidence report or parent-batch requirement. Interrupted jobs resume from this retained directory. Never delete failed candidates or reviews as a publication side effect.
