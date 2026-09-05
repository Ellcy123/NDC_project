# NDC AVG keyed-layer packaging

## Source conventions

- Requirements: `{PLANNING_ROOT}/`; task files: `<job>/payload/`
- Character cards: `{PLANNING_ROOT}/美术资产交付/角色/角色索引.json`
- Scene backgrounds: `{ENGINE_ROOT}/Assets/Resources/Art/Scene/Backgrounds/`
- U1 static AVG rendering references: `{ENGINE_ROOT}/Assets/Resources/Art/avg_clip/EPI01/static/`
- Test/edit jobs: the created job's `payload/`
- Transparent-character packager: `{PLANNING_ROOT}/.codex/skills/ndc-free-exploration-character-art/scripts/package_sprites.py`

Resolve maintained references from `{PLANNING_ROOT}/canon_manifest.json` and the character registry. Existing engine assets are read-only inputs until the user approves a delivery.

## Coordinate rules

- Origin is source-image top-left; X increases right and Y increases down.
- Rectangles are half-open: `[left, right)` and `[top, bottom)`.
- Record actual source dimensions; NDC backgrounds are not all `2560x1600`.
- Keep the source scene at native size and never overwrite it.
- A scene-context plate is a pose, scale, light, and interaction master only. Never paste its generated environment into the final.
- A packaged actor canvas position is its top-left in full-scene pixels; distinguish it from the visible subject bounding box.
- Choose and record the immutable source crop before the scene-master call. Every later actor coordinate must trace back to that crop; keyed-source canvas coordinates are never scene coordinates.
- Prefer a scene master with exactly the source-crop dimensions. A different-size master is valid only when it contains the complete crop with the same aspect ratio and no crop, padding, rotation, or reframing.
- Map master landmarks into crop space separately on X and Y. Never measure from an app thumbnail, screenshot, or other resized preview.
- Package and transform every person independently. Multi-person keyed sources and interaction-group Alpha are prohibited.
- Preserve ensemble relationships through the frozen per-character boxes, foot/contact points, gaze targets, cross-layer contact landmarks, prop ownership, and occlusion order from the completed all-character plan.
- Derive every actor's visible height from the canonical profile height and recorded floor perspective. Packaging may preserve or restore that uniform scale; it may not make an observer, rear layer, or secondary character smaller merely to fit.
- Record the selected TalkPanel side in render space and map its safe rectangle into source coordinates before choosing any actor canvas. For a one-to-one `2560x1600` display, the left rectangle is `[0,0) -> [913,1600)` and the right rectangle is `[1647,0) -> [2560,1600)`.
- Every baked Alpha union and independent actor preview must have zero intersection with the mapped TalkPanel rectangle.

## Frozen crop-relative placement contract

Before any keyed-source generation, record:

```text
source_size:          (source_width, source_height)
source_crop:          (crop_x, crop_y, crop_width, crop_height)
master_size:          (master_width, master_height)
master_box:           (left, top, right, bottom)
normalized_box:       (left/master_width, top/master_height,
                       right/master_width, bottom/master_height)
crop_box:             mapped box in source-crop pixels
head/contact/body:    master-space and crop-space landmarks
source_anchor_check:  underfoot/support contact plus two nearby non-collinear anchors
```

Map each point rather than guessing a height:

```text
crop_point_x = master_point_x * crop_width  / master_width
crop_point_y = master_point_y * crop_height / master_height
full_point_x = crop_x + crop_point_x
full_point_y = crop_y + crop_point_y
```

The local source-anchor check is mandatory because an image model can redraw geometry inside an otherwise same-shaped canvas. If the master invents or shifts the underfoot floor, support object, doorway, tile intersection, bed rail, or another local anchor, reject it before green generation. A global `master_width -> crop_width` ratio cannot repair local perspective drift.

Generate the keyed source only after this contract is frozen. Prefer the same aspect ratio and request the actor in the same normalized box, but still measure the extracted Alpha afterward. Uniformly scale and translate that Alpha to the `crop_box` and contact landmarks. Do not use the centered keyed subject, green-canvas padding, or green-canvas dimensions as placement authority. If one uniform transform cannot match the box, contacts, and body axis, regenerate the keyed pose/camera angle.

## Crop and single-character chroma package

Create a deterministic crop:

```powershell
& $ndcImagePython scripts/art_pipeline/ndc_art.py run ndc-free-exploration-character-art package_sprites.py crop `
  --scene $source `
  --rect 768,64,1536,1536 `
  --output "$job/source_crop.png"
```

Package one keyed character on a transparent canvas. Choose `visible-height`, `foot`, and `position` from that character's accepted scene master and physical-anchor contract, not from example values:

```powershell
& $ndcImagePython scripts/art_pipeline/ndc_art.py run ndc-free-exploration-character-art package_sprites.py package `
  --state key_dialogue="$job/leonard_green.png" `
  --scene $source `
  --output-dir "$job/output" `
  --prefix SC2292_leonard `
  --canvas 720x1280 `
  --visible-height 812 `
  --foot 360,1212 `
  --position 768,64 `
  --shadow none
```

Repeat packaging separately for each planned person. A shared prop belongs to one named character layer; other actors preserve contact through their independently frozen landmarks.

Use `--key magenta` when green touches any subject silhouette or prop. A packager pass does not replace visual inspection of enclosed gaps, fine hair, fingers, shoes, or green/magenta spill on dark and light QA backgrounds.

## Final Alpha bake

Use this skill's `scripts/composite_rgba_layers.py` to create the authoritative full-scene plate. Repeat `--layer` in back-to-front order:

```powershell
& $ndcImagePython scripts/art_pipeline/ndc_art.py run ndc-avg-character-scene-art composite_rgba_layers.py `
  --scene $source `
  --layer leonard "$job/output/SC2292_leonard_key_dialogue.png" 768 64 `
  --layer zack "$job/output/SC2292_zack_key_dialogue.png" 768 64 `
  --output "$job/SC2292_avg_KeyDialogue_v1.png" `
  --union-mask "$job/final_union_alpha.png" `
  --report "$job/final_alpha_verification.json"
```

Delivery requires:

- output size and mode equal the source;
- `changed_pixels_outside_union == 0`;
- `outside_union_max_channel_difference == 0`;
- `outside_union_pixels_bit_identical == true`;
- visual QA finds no clipped anatomy, missing shared prop, key spill, scene fragment, floating feet, or implausible layer order.
- measured head-to-foot pixels satisfy the recorded canonical-height/depth contract;
- an actual left/right TalkPanel overlay preview confirms the selected side remains empty of characters and action props;
- the final plate depicts the selected stable key-dialogue still and excludes beats assigned to突发事件/cutaway production;
- every accepted actor came from its own single-person scene master and keyed source;
- the delivered character-to-physical-anchor pixel ratio matches the recorded real-world ratio after the declared depth adjustment.

Use `scripts/verify_avg_safe_zone.py` with the full-size union mask for deterministic UI containment. The script mirrors the production `left_BG.png` when `--side right` is selected, emits the UI-overlay preview when requested, and fails unless `actor_alpha_pixels_inside_safe_rect` is zero. Pass `--safe-rect` whenever the source-to-`2560x1600` runtime mapping is not one-to-one.

## Rejected diagnostic lesson

The 2026-08-24 U2 diagnostic exposed a prohibited recovery path:

- source scene: `2560x1600`;
- scene context crop: `1536x1536` at `(768,64)`;
- scene masters or keyed sources returned at `1254x1254` while later keyed characters were independently centered;
- the final packaging guessed `visible-height` and foot positions instead of freezing and mapping the scene-master actor boxes before green generation;
- Alpha extraction, source-pixel containment, and TalkPanel checks passed, but scene-relative size and placement still failed visually.

The lesson is that clean Alpha is not coordinate registration. Complete the physical-anchor and all-character blocking plan first, preserve each person's crop-relative actor box, validate local source geometry, and make every single-person keyed Alpha conform to its frozen box. Do not cite this diagnostic as a validated scale example.

## Optional scene-pixel repair

Use `ndc-coordinate-image-edit` only for a separately confirmed cleanup or material/structure repair. Keep its authorization mask and verification chain separate from the generated actor Alpha workflow. Never use a broad coordinate mask as a substitute for keyed extraction of a newly generated person.
