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

Production scripts may crop, mask, composite already-approved non-text art, rotate, resize, perspective-map, manage alpha, apply locked templates, and generate verification data. They must not use Pillow/ImageDraw, Canvas, SVG, HTML/CSS, shaders, Photoshop text, or equivalent code/tools to originate or correct readable prop typography. They must not originate the final evidence body, paper/card surface, tables and rules, container, furniture, texture, wear, lighting, handwriting, background, or scene-state artwork. Those APIs remain valid for test fixtures, masks, guides, borders, and debug overlays.

For a document whose readable wording matters, approve only a high-resolution complete raster master in which the final title/body/stamp/signature wording is already authored. If any required wording is missing, wrong, garbled, incomplete, or not readable at the relevant review scale, reject that candidate and return to image generation; do not add a separate text layer in Photoshop or code. Drawing a blank page and constructing or completing the document with code is a layout mockup, not final art.

Candidate-first selection is an economy rule, not a quality waiver. Before retaining a scene-visible candidate, inspect it inside the native-resolution parent scene at whole-frame 100% and local nearest-neighbour 200%. Compare scale against immediate physical anchors: it must not block movement or read materially oversized at depth. For a candidate Map, inspect Alpha-only, checkerboard, and tinted/untinted parent overlays. Reject it if the silhouette contains desk, floor, wall, background, a generic cast-dark area, an adjacent collectible, a container part, or any other non-target region, even if visible RGB matches the parent and technical checks pass. A candidate Big, Icon, Map, scene insertion, and runtime release are separately accepted; pass of one never approves another.

Record the complete semantic master path and SHA-256, authoring mode, and the visual review of every required readable content element in the job manifest. Missing provenance blocks final delivery.

## Asset routing

| Art class | Big route | Icon route |
|---|---|---|
| Physical or volumetric prop | Transparent identity master, ordinary Big frame | Dedicated high-resolution Icon pose and top-side lighting |
| Paper, file, or flat printed object | Preserve approved exact content and lay it into an ordinary Big frame | Reuse the approved front texture, lay it flat, add the standard shadow deterministically |
| Photographed clue | Locked `620x620` Polaroid template | Depicted physical object/group, not the UI frame; use a photo object only when the collectible itself is a photograph |
| Analysis or derived result | Use the approved result presentation | Produce an Icon only when the delivery contract or user explicitly requires one |
| Environmental observation | Content-led irregular environmental Big; select a hard silhouette assembly or a soft contextual window below | No Icon unless the runtime contract explicitly overrides the normal environment omission |

`iconPath` is optional in the runtime schema. Do not invent an Icon for every
ItemStaticData row globally. When a batch contract requires an Icon, however,
the production Icon rules below are mandatory.

## Environmental-observation Big production

An `environment` Big is not an ordinary isolated-prop card. Its Alpha must be
driven by the smallest visual unit that still communicates the environmental
story, rather than by a fully opaque rectangular crop. The PNG canvas remains
rectangular for runtime transport, but the visible Alpha inside it must follow
the selected narrative unit. Do not put an environmental observation into the
ordinary portrait/square/landscape guide merely because its source crop began
as a rectangle. The accepted canvas dimensions, visible bounds, selected mode,
and why each retained context fragment is necessary are part of the delivery
record. **Do not apply a presentation rotation or tilt to an environmental
Big.** Keep the source scene's real camera perspective and any object geometry
that naturally appears within it, but use `post_transform_rotation_degrees: 0`
for the final observation; no `+10`/`-10` ordinary-Big treatment applies.

Choose one of these two modes before making an Alpha selection:

1. **Hard silhouette assembly** — use when the story is carried by a
   separable object or a physically coherent group: for example a shrine,
   statue-and-flowers arrangement, crate, framed object with its paired clue,
   or another compound still life. Trace the union of every story-bearing
   component, necessary shared support, and attributable cast/contact shadow.
   Preserve real negative spaces between components as Alpha 0. Edges are
   physical/antialiased rather than a soft rectangular fade. Never discard a
   secondary component merely to make the outline simpler. When a day/night or
   other lighting pair depicts the same physical assembly, reuse the exact
   Alpha geometry and change only the accepted state pixels; hash-bind the
   shared mask and review both states together.

2. **Soft contextual window** — use when the story would be incomplete without
   its immediate environmental substrate: for example damaged plaster at a
   room corner, a collage on a wall, a framed portrait plus the nearby object
   that gives it meaning, or a set of drawings attached to a surface. Keep the
   narrative center fully readable and retain only the immediately necessary
   wall, frame, ledge, adjacent paper, or room geometry. Taper outward through
   a deliberately shaped, feathered Alpha transition; it must remove
   non-narrative rectangular corners and must not read as a hard opaque screen
   capture. The fade follows the observation's visual flow, not a uniform
   vignette. Do not feather away a required construction edge, readable clue,
   or material transition.

Use the hard assembly mode for a physical object/group even if its source has a
dark background; use the soft contextual window only when that retained
background itself is part of the observed information. Neither mode permits a
generic fully opaque rectangular scene crop. A visible rectangular frame,
poster board, photograph border, crate, or wall seam may remain inside the
selection when it belongs to the story; the *outer Alpha* still follows the
chosen narrative unit.

### Environmental Big workflow and gate

1. From the accepted scene/state, write a short `environmental_focus` note
   naming the center, indispensable secondary elements, retained context, and
   rejected non-context pixels. Select the mode before opening Photoshop.
2. Run the current Photoshop MCP capability preflight. On a recoverable
   duplicate, create the Alpha only through supported Photoshop operations;
   retain the complete semantic RGB within every Alpha-positive pixel. Do not
   paint, add, repair, or restyle readable text. If the necessary Alpha/mask
   operation is unavailable, record `PS_MCP_ENVIRONMENT_ALPHA_UNAVAILABLE`,
   preserve the candidate, finish unrelated deliverables, and leave this asset
   blocked for manual Alpha work rather than publishing a rectangular fallback.
   Reframe by crop, move, or uniform scale only; do not globally rotate or
   tilt the observation to make it look like a collectible card.

   If the current Photoshop MCP catalogue lacks the required non-semantic
   transform (for example, a de-rotation of an inherited tilted environment
   Big), record `PS_MCP_ENVIRONMENT_TRANSFORM_UNAVAILABLE`. A single,
   report-bound deterministic fallback is then allowed on the approved RGBA
   duplicate only: `scripts/reframe_environment_big.py` rotates in
   premultiplied Alpha, crops to the actual Alpha bounds plus declared
   transparent padding, and zeros RGB below Alpha 0. It may also apply one
   recorded source crop, uniform scale, and a named edge-only contextual taper
   when the approved focus requires it; do not use a four-sided uniform
   vignette as a substitute for an authored environmental selection. Preserve
   the original and identify this as a deterministic fallback—not a Photoshop
   edit. The final observation still records
   `post_transform_rotation_degrees: 0` and must pass the complete visual gate
   before use.
3. Review the result on both light and dark checkerboards at runtime scale and
   at local 200%: the focus must read immediately; hard assemblies must keep
   every component/support/shadow and their negative spaces; soft windows must
   retain enough environmental derivation while avoiding a rectangular
   screenshot edge. Verify Alpha 0 has zero RGB. Inspect day/night state masks
   in registration when applicable.
   Generate those non-delivery review views with:

   ```powershell
   python scripts/render_environment_big_review.py `
     --input <environment-big.png> `
     --output-dir <process-only-review-directory> `
     --focus-box <left,top,right,bottom>
   ```

   The helper composites only checkerboard review images and reports Alpha
   residue; it never modifies the Big or makes a visual-pass decision.
4. Record the approved source hash, mode, `environmental_focus`, canvas and
   Alpha bounds, `post_transform_rotation_degrees: 0`, required context,
   discarded context, checkerboard views, whole/local visual findings, and the
   final hash. Ordinary `verify-big`
   frame/safe-rectangle checks apply only when the active runtime contract
   explicitly assigns an ordinary Big frame; otherwise do not falsely reject an
   approved environmental-observation Big for not being `571x1000`,
   `818x818`, or `1000x571`.

The environmental Big retains the source's scene state and lighting. It must
not be converted into a clean product render, a Polaroid, or a Type 7 view.
For an environment record, its real scene Map/Position and this Big remain
separate requirements; the irregular Big Alpha never replaces the clickable
scene hotspot.

## Ordinary Big production

### Repair before rebuild

For a previously authored Big, determine whether the failure is semantic or only presentational before asking an image model for another asset. A correct prop identity, content/exact text, style, material, light, and perspective with an incorrect size, safe range, rotation, crop, transparent margin, or other minor non-semantic defect is a Photoshop-MCP correction case first. Preserve the original, edit a duplicate serially through the exposed Photoshop MCP commands, then use `finalize-big` only to own the exact runtime frame and verification report.

If the paired Photoshop MCP host cannot open/place the approved local source because its file access or whitelist is unavailable, write `PS_MCP_LOCAL_FILE_ACCESS_BLOCKED`, retain the source unchanged, finish unrelated work, and retry after access is restored. Do not use mouse/keyboard automation as a substitute and do not regenerate solely because that capability is temporarily absent. Rebuild only when visual inspection proves wrong style/content/identity/exact text or when the available source cannot meet the selected frame without prohibited upscaling or semantic loss. Keep every superseded master and record the MCP result, failure classification, and source hashes.

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
paper and actual collectible photograph objects (not physical props merely shown in a clue Big frame), preserve the approved complete front artwork and
transform it deterministically for the Icon only. If the Big/master itself lacks
required readable text, regenerate the complete master first; do not add that
text at the Icon stage.

For an evidence group made of multiple distinct physical pieces, first validate
all required wording on the complete pre-composition master, then establish the
approved Big composition. Prefer a restrained staggered hierarchy over a
perfectly upright, evenly spaced row when physically plausible: a rear sheet
may be offset and a foreground sheet may overlap it. The final Big is allowed
to hide parts of previously reviewed text or a rear component; it does not need
to preserve full close-reading access after the composition step. It must still
retain each component's identity and avoid clipping or false mergers. Derive
the Icon from that accepted composition; do not independently rearrange or
obscure text-bearing pieces at the Icon stage.

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

The observation photo must be opaque before framing. The finalizer replicates
only source-edge samples into a sampling guard band, without changing the photo
mapping, so the raster window mask cannot expose transparent transform fill.
Require zero non-opaque pixels inside the canonical window as well as unchanged
pixels outside it; a matching frame alone does not prove a complete photo window.

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

<!-- NDC_TEXTURE_COHERENCE_MODULE:BEGIN -->

Run `STYLE_LOCK_GATE` and `TEXTURE_COHERENCE_GATE` independently on the approved high-resolution master and every runtime-sized result. Preserve the approved prop identity, material construction, wear, palette/value compression, line/brush language, lighting, and exact content. Texture control may change only non-semantic density and continuity; it may not erase approved wear or convert the art into a smoother, flatter, sharper, more photoreal, or more generic treatment.

At Big size, semantic evidence detail may be readable but background and material microtexture must remain subordinate to the evidence. At Icon size, silhouette, material class, and one or two identity cues outrank surface microdetail; the dedicated Icon master must not inherit the Big's full text/texture frequency. At Map/gameplay size, detailed text and close-reading texture are forbidden by the map-scene information budget.

Reject repeated texture stamps, random cracks or speckle, fragmented short marks, uniform sharpening, edge halos, decorative wear unsupported by the identity master, or detail density that collapses the runtime silhouette. Save and validate an `ndc-texture-coherence/v1` record with `D:\Codex\NDC\scripts\validate-ndc-texture-gate.py`. Automatic sharpness or image-quality metrics are screening evidence only.
<!-- NDC_TEXTURE_COHERENCE_MODULE:END -->
