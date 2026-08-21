---
name: ndc-coordinate-image-edit
description: Perform non-destructive, coordinate-locked edits on NDC raster art when only a bounded region may change and the source size, placement, and all pixels outside an approved mask must remain unchanged. Use for localized cleanup, removal, replacement, material changes, or structural repair; do not use for whole-image generation or broad restyling.
---

# NDC Coordinate Image Edit

Use the image model for appearance only. Use deterministic local code for crop geometry, registration, masking, compositing, and verification.

## Non-negotiable invariants

- Never overwrite the source image. Create a sibling result or a job-specific output directory.
- Treat rectangles as half-open: `[left, right)` and `[top, bottom)`.
- Record whether coordinates use a top-left or bottom-left origin; never infer silently when the user supplied coordinates.
- The AI-generated image never determines final size or final placement.
- Plan the generation crop against the target model's legal canvas constraints before generation. Never send an illegal crop and repair its aspect ratio by stretching or center-cropping the returned image.
- Paste only through the approved hard mask. Feathering may occur inward, but alpha must be zero outside the hard mask.
- The final image must match the source dimensions and mode, preserve source alpha when present, and be byte-identical outside the hard mask.
- Save the composed result as PNG. Lossy JPEG/WebP output cannot satisfy byte-identical outside-mask verification.
- Before the first generation or image-file modification, show a concrete `before -> after` example based on the real target and wait for explicit confirmation, unless the user already confirmed that exact edit in the current task.
- A failed or visually rejected generation does not authorize another generation. Ask before retrying.

## Use the bundled state machine

The helper is [scripts/coordinate_patch.py](scripts/coordinate_patch.py). Each edit gets its own job directory and `manifest.json`.

Before running it, call `codex_app__load_workspace_dependencies` and use the returned bundled Python executable, which includes Pillow and NumPy. Store that exact path in a task-specific PowerShell variable such as `$ndcImagePython`; do not assume the system `python` has these packages.

### 1. Inspect and define the contract

1. Read the source with `view_image` before editing.
2. Identify the smallest edit rectangle that contains every pixel allowed to change.
3. Add enough unchanged context for the model and registration, then expand the crop outward to the smallest legal generation canvas. For `gpt-image-2`, the crop width and height must both be multiples of 16, neither edge may exceed 3840 px, the long-edge-to-short-edge ratio must not exceed 3:1, and total pixels must be between 655,360 and 8,294,400. Prefer extending the crop into real source pixels; shift the crop within the source bounds when necessary. Use synthetic padding only when the source cannot supply a legal canvas, record the exact padding and target-to-canvas mapping, and never resize the authorized target region.
4. If the user supplied a screenshot rather than coordinates, visually match it once, export one proposed crop, and verify it. Do not enter open-ended template-matching or FFT design loops.
5. State the source path, coordinate origin, edit rectangle, context crop, preserved elements, and intended change in the confirmation example.

Example: a `1730x520` target is wider than 3:1 and is not a legal `gpt-image-2` canvas. When source bounds permit, expand it with real surrounding pixels to `1744x592` instead: both edges are multiples of 16, the aspect ratio is about 2.95:1, and the target itself remains unscaled.

Prepare a job:

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" prepare `
  --source "D:/NDC_project/image/source.png" `
  --edit-rect 120 240 520 460 `
  --origin top-left `
  --padding 96 `
  --out-dir "D:/NDC_project/image/edit_jobs/source-local-fix"
```

Use `--crop-rect LEFT TOP RIGHT BOTTOM` when the context crop is already known. Use `--mask path/to/mask.png` for a non-rectangular authorization mask; the mask must be source-sized or crop-sized and must not authorize pixels outside `--edit-rect`.

Inspect `source_crop.png`, `hard_mask.png`, and `manifest.json` before generation.

### 2. Generate exactly one confirmed patch

- Use the built-in `image_gen` tool by default and pass `source_crop.png` through `referenced_image_paths`. Do not use `num_last_images_to_include` when the crop has a local path.
- When the generation surface exposes an output `size`, request the exact legal crop dimensions. If it does not expose `size`, explicitly request the crop's aspect ratio and framing, then validate the returned canvas before composition.
- State that the input is the exact edit crop, list the requested change, repeat every invariant, and require the same framing and camera.
- Ask the model to return the full edited crop, not an isolated object.
- Make one generation call per confirmed iteration.
- Image generation can take minutes. Announce the call, allow the long-running tool window, and wait for its completion instead of launching competing recovery work.
- When the tool completes, use only its local `savedPath`. Never print, copy into prose, re-serialize, or inspect its Base64 payload.
- Immediately copy the selected generated file into the job directory as `generated.png`. Do not leave a project asset only under `$CODEX_HOME/generated_images`.
- Reject a returned patch whose aspect ratio differs from the prepared crop. Do not stretch it or center-crop it into compliance. A proportionally larger or smaller patch may be uniformly resampled only when its aspect ratio matches the prepared crop and the coordinate mapping remains exact; record that normalization in the manifest.
- Do not write or redesign post-processing code after generation returns.

Prompt skeleton:

```text
Use case: precise-object-edit
Asset type: NDC localized raster repair
Input image: the exact context crop from the source image
Primary request: <one bounded edit>
Style/medium: preserve the source illustration, line weight, palette, wear, perspective, and lighting
Hard invariants: change only <approved interior>; preserve <named boundaries and surroundings>; keep the exact canvas framing; do not crop, zoom, rotate, shift, resize, add text, or add unrelated objects; output the edited full crop
```

### 3. Compose through code

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" compose `
  --manifest "D:/NDC_project/image/edit_jobs/source-local-fix/manifest.json" `
  --ai-patch "D:/NDC_project/image/edit_jobs/source-local-fix/generated.png"
```

The helper normalizes the generated canvas, estimates small scale/translation drift from protected context, applies only the inward-feathered authorization mask, saves a non-destructive result, and verifies source integrity.

It reloads the saved PNG before reporting success, so verification covers the actual file on disk rather than only the in-memory composite.

Use `--registration off` only when visual inspection proves the generated crop already aligns and automatic registration makes it worse. Record that choice in the manifest.

### 4. Verify visually and numerically

Completion requires all of the following:

- `verification.source_unchanged` is `true`.
- `verification.final_size_matches_source` is `true`.
- `verification.outside_mask_nonzero_channels` is `0`.
- `verification.outside_mask_max_channel_difference` is `0`.
- The generated content is visually correct inside the mask, without black registration edges or clipped structure.
- The original boundary, perspective, lighting, and seams remain credible.

Inspect both the full result and a close crop. A zero outside-mask diff proves containment, not artistic correctness.

### 5. Deliver and recover

Show the close-up and full result. Report the result path, manifest path, final prompt, generation mode, registration values, and four verification fields.

If a task is interrupted after generation, recover from the job directory rather than from full conversation history:

```powershell
& $ndcImagePython ".codex/skills/ndc-coordinate-image-edit/scripts/coordinate_patch.py" status `
  --manifest "D:/NDC_project/image/edit_jobs/source-local-fix/manifest.json"
```

- `prepared` plus no `generated.png`: generation has not been persisted.
- `prepared` plus `generated.png`: run `compose`; do not regenerate.
- `composed`: inspect and deliver the existing result.
- Do not fork a large image-generation history as a recovery mechanism. A fresh task, when the user explicitly creates one, needs only the manifest and local file paths.
