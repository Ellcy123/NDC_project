# NDC Big, Icon, and clue-photo production contract

Use this reference whenever a delivery includes `desSpritePath` Big art, an
`iconPath` Icon, or a photographed `clue` Big. The scene Map remains governed
by the coordinate-placement workflow and must never be rescaled.

## Governing principle

Target size is an export contract, not an AI generation size.

1. Establish one approved high-resolution identity master for the evidence.
2. Author the Big and Icon for their different presentation roles.
3. Use deterministic code for rotation, fitting, transparency, template
   composition, final dimensions, and reports.
4. Inspect the final runtime-sized PNG. A high-resolution master is not visual
   approval at gameplay size.

Do not ask an image model to produce an exact `130x130` file. Do not rely on
Unity to shrink a `256x256` source. Do not create an Icon by resizing the whole
Big canvas.

## Semantic master and code boundary

An approved semantic raster master must exist before deterministic finalization. It may be an accepted image-generation result, artist-authored raster, approved source extraction, or approved transformation of one of those sources. It must already carry the evidence's silhouette, perspective, physical construction, material, wear, lighting, and period style.

Production scripts may crop, mask, composite, rotate, resize, perspective-map, manage alpha, apply locked templates, place exact approved typography, and generate verification data. They must not use Pillow/ImageDraw, Canvas, SVG, HTML/CSS, shaders, or equivalent code to originate the final evidence body, paper/card surface, tables and rules, container, furniture, texture, wear, lighting, handwriting, background, or scene-state artwork. Those APIs remain valid for test fixtures, masks, guides, borders, and debug overlays.

For an exact-text document, first approve an illustrated high-resolution physical document master. Keep exact title/body/stamp/signature artwork as separate approved layers when needed, then composite those layers into the master. Drawing a blank page and constructing the entire document with code is a layout mockup, not final art.

Record the semantic master path and SHA-256, authoring mode, and every separately composited exact-content layer path/hash in the job manifest. Missing provenance blocks final delivery.

## Asset routing

| Art class | Big route | Icon route |
|---|---|---|
| Physical or volumetric prop | Transparent identity master, ordinary Big frame | Dedicated high-resolution Icon pose and top-side lighting |
| Paper, file, or flat printed object | Preserve approved exact content and lay it into an ordinary Big frame | Reuse the approved front texture, lay it flat, add the standard shadow deterministically |
| Photographed clue | Locked `620x620` Polaroid template | Treat the accepted Polaroid as a flat object; do not regenerate its photo or frame text |
| Analysis or derived result | Use the approved result presentation | Produce an Icon only when the delivery contract or user explicitly requires one |

`iconPath` is optional in the runtime schema. Do not invent an Icon for every
ItemStaticData row globally. When a batch contract requires an Icon, however,
the production Icon rules below are mandatory.

## Ordinary Big production

The bundled [Big layout guide](../assets/big_layout_guide_2560x1600.png) is a
`2560x1600` transparent UI positioning workspace. It is not a runtime Big.
The colored lines never appear in a final asset. Export only the selected frame
rectangle after hiding the guide.

| Frame | Guide rect `[l,t,r,b)` | Runtime size | Local safe rect | Use |
|---|---:|---:|---:|---|
| `portrait` / green | `[502,243,1073,1243)` | `571x1000` | `[58,100,513,900)` | Vertically dominant prop |
| `square` / yellow | `[378,334,1196,1152)` | `818x818` | `[82,82,736,736)` | Approximately square prop |
| `landscape` / red | `[288,458,1288,1029)` | `1000x571` | `[100,58,900,513)` | Horizontally dominant prop |

The safe rectangles implement at least ten percent clearance on every side,
rounded inward conservatively. They are maximum envelopes, not fill targets.
Do not enlarge every item until it touches the safe rectangle.

Classify the unrotated silhouette as portrait, square, or landscape. Record the
rotation direction explicitly as `+10` or `-10` degrees; positive means
counter-clockwise in image coordinates. The source requirement does not choose
one universal direction, so never hide the choice in a default.

Fit using the rotated bounds, not the original bounds. For width `w`, height
`h`, and angle `10 degrees`:

```text
rotatedWidth  = |w cos(10)| + |h sin(10)|
rotatedHeight = |w sin(10)| + |h cos(10)|
scale = min(safeWidth / rotatedWidth, safeHeight / rotatedHeight)
```

After rotation and resampling, the real antialiased alpha bounds must still be
inside the selected local safe rectangle. New production must not upscale an
undersized master just to fill the frame. Use:

```powershell
python scripts/evidence_art.py finalize-big `
  --master <approved-transparent-master.png> `
  --frame portrait|square|landscape `
  --rotation-degrees 10|-10 `
  --output <runtime-big.png> `
  --layout-preview <optional-2560x1600-review.png> `
  --report <big-verification.json>
```

The optional preview is a review artifact only. Do not copy it into runtime.

## Icon production

### Visual contract

- Final PNG: exactly `130x130`, RGBA.
- Final combined visible envelope: inside `[7,7,122,122)`, at most
  `115x115`. The envelope includes the prop and its shadow.
- Standard work canvas: `1040x1040`, with combined content inside
  `[60,60,980,980)`, at most `920x920`.
- Keep the subject visually centered. Do not center the combined subject plus
  left-down shadow, because that shifts the subject up and right.
- Use top-side lighting and a small noon-like cast shadow whose centroid lies
  left and below the subject centroid.
- Keep the subject and shadow as separate masks through finalization.
- `115x115` is a hard maximum, not a requirement to fill the box. Prefer a
  slightly smaller working envelope when Lanczos support or a soft shadow needs
  clearance.

For complex volumetric props, create a dedicated high-resolution Icon view that
preserves the Big identity but owns its own pose, light, and shadow. For flat
paper and Polaroid objects, preserve the approved front artwork and transform it
deterministically; do not send exact text through the image model again.

### Alpha-safe finalization

Use the bundled finalizer:

```powershell
python scripts/evidence_art.py finalize-icon `
  --master <1040x1040-combined-rgba.png> `
  --subject-mask <1040x1040-subject-mask.png> `
  --shadow-mask <1040x1040-shadow-mask.png> `
  --output <130x130-icon.png> `
  --report <icon-verification.json>
```

The finalizer uses one premultiplied-alpha Lanczos reduction from `1040` to
`130`, converts back to straight RGBA, zeros RGB under fully transparent
pixels, and rechecks the final alpha bounds. Do not resize the final PNG again.
Every revision must restart from the high-resolution master.

The Icon verification report belongs to the Icon artifact. Pass it to
`evidence_delivery.py package` together with `--icon-image`. A production
package must not silently derive an Icon from Big. The explicit legacy switch
exists only to reopen an older package, not to produce new art.

## Photographed clue Big

The bundled [Polaroid frame](../assets/clue_polaroid_frame_620x620.png) is the
locked runtime template. The matching
[window mask](../assets/clue_polaroid_window_mask_620x620.png) is a canonical,
versioned mask; do not rediscover the green region by thresholding each job.

1. Generate or approve a high-resolution first-person close observation of the
   clue with only the necessary surrounding context.
2. Crop for the important clue information without fabricating new readable
   facts.
3. Perspective-map the photo to the canonical window quadrilateral.
4. Composite only through the canonical mask.
5. Export exactly `620x620` RGBA. Do not resize or additionally rotate the
   frame.
6. Require every pixel outside the window mask, including the paper frame,
   stains, edge wear, and transparent exterior, to remain byte-identical to the
   locked template.

```powershell
python scripts/evidence_art.py compose-polaroid `
  --photo <approved-high-resolution-clue-photo.png> `
  --output <runtime-clue-big.png> `
  --report <polaroid-verification.json>
```

The template SHA-256 is
`8c5bd335a686e4a5ff7be1887c65cd30cfaa08646c8b2643566583a395e4a244`.
The canonical window-mask SHA-256 is
`58995e55031cc2c264e6320da683e9dd6e727ec052f80a90ad9167a12876cc04`.
Replacing it is a template revision and requires a new explicit authorization,
not an ordinary evidence job.

## Visual approval gates

Machine reports cannot prove identity, period accuracy, readable exact text,
correct top-side lighting, convincing material, or good small-size hierarchy.
Inspect:

- the ordinary Big at its native runtime dimensions;
- the full `620x620` clue Polaroid;
- the Icon at `130x130`, plus representative `100x100`, `120x120`, and
  `150x150` UI previews;
- transparent edges over both light and dark checkerboards.

Reject muddy micro-detail, unreadable silhouette, a long or wrong-direction
shadow, repeated-resize softness, colored guide residue, and any frame or
transparent-edge contamination even when the dimensional report passes.
