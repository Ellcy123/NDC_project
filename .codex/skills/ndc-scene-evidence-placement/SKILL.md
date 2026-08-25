---
name: ndc-scene-evidence-placement
description: Place collectible NDC evidence into an approved raster scene without coordinate drift, or prepare a Unity Type 6 to Type 7 secondary-menu container pair. Export exact scene-local crops, independently positioned open-container views, detail and icon assets, top-left pixel coordinates, ItemStaticData drafts, and machine-verifiable delivery reports. Use when adding or replacing clickable evidence props, drawers, lockers, safes, boxes, pockets, or other EVIDENCE runtime assets in NDC exploration scenes.
---

# NDC Scene Evidence Placement

Turn an approved scene plus an evidence requirement into a staged, Unity-ready evidence package. Preserve the source and derive coordinates from the accepted final image. Never eyeball or manually transcribe `Position`.

## Read first

1. Read the relevant Unit evidence-art document and the matching state scene before deciding what appears in the scene.
2. Read `../ndc-coordinate-image-edit/SKILL.md` completely before any raster insertion or replacement. Its source-preservation, mask, crop, seam, and final-union checks remain mandatory.
3. Read [references/delivery-contract.md](references/delivery-contract.md) before naming or packaging assets.

If the request includes Unit/Episode identity or IDs, read `canon_manifest.json` before inferring paths or namespaces.

## Classify before editing

Assign every requested evidence record one delivery class:

- `scene-pickup`: a visible, clickable object placed in a scene. Deliver the complete package in this skill.
- `container-state`: a drawer, safe, locker, case, box, pocket, bin, or similar Unity secondary-menu container. Deliver a scene-exact Type 6 entrance screenshot, a separately authored Type 7 open view, independent coordinates for both, and the complete Type 6 -> Type 7 -> contained-item chain. Do not treat it as one static pickup or a generic before/after edit.
- `detail-only`: a document, analysis result, memory result, or handed-over evidence that is never present as a world prop. Deliver detail/icon assets only; do not invent a scene coordinate.
- `environment`: a non-pickup environmental observation. Keep it in the background or state prop; do not create a fake collectible map sprite.
- `minigame-only`: an interaction asset that does not enter ItemStaticData. Route it to the minigame asset workflow.

Do not force all evidence records through `scene-pickup`.

## Scene-pickup workflow

### 1. Establish the contract

Record:

- Unit, Episode, Loop, Scene ID, Item ID, evidence name, and source design file.
- Approved final scene source and its exact pixel dimensions.
- `folderPath`, `mapSpritePath`, `desSpritePath`, and `iconPath` stems from the current ItemStaticData draft when available.
- Placement intent in plain language: support surface, scale, orientation, lighting, occlusion, and visibility.
- Spoiler exclusions and cross-evidence visual constraints.

Treat current table rows as naming inputs, not proof that a placeholder position or asset exists.

Before writing any generation prompt, split the evidence art requirement into two explicit information contracts:

- `map-scene contract`: only the low-information features needed to discover and identify the object class in the exploration scene—silhouette, material, broad color, approximate state, and natural placement. Its view, foreshortening, occlusion, and visible face must follow the source scene camera and support-surface perspective. A document may show only its spine, edge, thickness, folded corner, or an unreadable portion of its cover.
- `big-detail contract`: all close-reading information carried by `desSpritePath`, including exact titles, dates, numbers, body text, handwriting, damage, comparison marks, and puzzle-specific details.

Never copy the detailed text requirements from the `big-detail contract` into the in-scene generation prompt. The map scene is a discovery anchor, not a readable evidence card or product shot. Unless the evidence itself is an environmental sign meant to be read in the scene, body text and exact metadata must remain unreadable at gameplay scale.

### 2. Prepare the insertion with the base skill

Use `ndc-coordinate-image-edit` to create the source-sized authorization mask, legal generation crop, job manifest, and non-destructive composed scene.

The authorization mask must include only:

- the new object;
- its physically necessary contact shadow, reflection, or occlusion;
- the smallest background repair halo needed for natural integration.

Do not include unrelated furniture, characters, walls, or broad lighting regions. Never rescale or crop the full scene after placement.

For a `scene-pickup`, the base-skill prompt must state the `map-scene contract` and must explicitly require:

- ordinary physical scale inferred from nearby furniture and the support surface;
- orientation along the scene's existing vanishing lines, rather than toward the viewer;
- no enlargement, tilting, standing-up, or frontal presentation for legibility;
- the whole object, contact shadow, reflection, and necessary occlusion to remain inside the authorization mask;
- no readable title, date, number, signature, or body text unless the map-scene contract explicitly requires it.

### 3. Produce and approve the full scene

Generate or edit only through the prepared crop. Compose through the base skill. Run its boundary, structural, and final-union checks. The accepted full-size PNG is the coordinate truth for every derivative.

Do not derive coordinates or item crops from an AI generation canvas, preview, resized review image, or earlier candidate.

Reject the scene candidate even when pixel-containment checks pass if any of the following is visible:

- the prop reads like a close-up, evidence card, product display, or signboard;
- a document's detailed text is readable from the exploration view;
- the prop is enlarged or turned toward the camera to expose information;
- its perspective, thickness, contact, or orientation conflicts with the support surface;
- any semantic part of the prop or its contact shadow is clipped by the authorization mask.
- a freestanding container fails the completeness check: its opening or rim, both unoccluded side walls, bottom or base ring, and contact shadow must remain visibly complete and separable at gameplay size. Natural occlusion is allowed only when caused by an existing scene object and recorded in the placement contract; touching a mask boundary, visually dissolving into a same-value background, or merely passing pixel-containment checks is not acceptable.

Inspect this at the full scene's expected gameplay display size, not only in a zoomed crop. Pixel containment is necessary but is not visual approval.

### 4. Prepare the standalone evidence image

Keep two outputs conceptually separate:

- Map crop: an exact rectangular crop from the accepted scene. It normally includes local scene background and is what Unity places at `Position`.
- Detail image: the standalone evidence view used by `desSpritePath`. Prefer a separately approved transparent detail render when legibility or presentation requires it. Otherwise use a clean source/crop-sized alpha mask to extract the accepted object.

The detail image may be a clearer view than the in-scene object, but identity, material, damage, labels, handedness, and state must match.

The detail image is the only default location for close-reading content. It may face the viewer and present exact text clearly; the matching map object should preserve the same identity and state without duplicating that information density.

### 5. Package deterministically

Run:

```powershell
python scripts/evidence_delivery.py package `
  --source-scene <approved-scene-before-item.png> `
  --final-scene <approved-scene-with-item.png> `
  --authorization-mask <source-sized-item-mask.png> `
  --base-verification <final_verification.json> `
  --map-padding <small-pixel-margin> `
  --item-id <item-id> `
  --scene-id <scene-id> `
  --folder-path <EPIxx\scene-folder> `
  --map-stem <SCxxxx_item_xxxx> `
  --detail-stem <SCxxxx_item_xxxx_big> `
  --icon-stem <SCxxxx_item_xxxx_icon> `
  --detail-image <approved-transparent-detail.png> `
  --z <-3> `
  --output-dir <image\edit_jobs\job\delivery>
```

Use `--cutout-mask` instead of `--detail-image` only when the standalone image must be extracted from the accepted final scene. Supply `--icon-image` when a separately approved icon exists; otherwise the script derives a transparent square icon from the detail image.

By default the script derives the map rectangle and `(x, y)` from the source-sized authorization mask, then adds `--map-padding`. This is the preferred path. `--map-rect left top right bottom` is only an audited compatibility override for pre-existing baked props. The rectangle is top-left based and half-open. It must contain every changed pixel and all clickable visual content. A few pixels of stable local background are allowed; arbitrary large padding is not.

### 6. Verify the delivery

Run:

```powershell
python scripts/evidence_delivery.py verify --manifest <delivery_manifest.json>
```

Delivery is blocked unless all applicable checks pass:

- source and final scene dimensions/mode match;
- the base coordinate verification passes;
- pixels outside the authorization mask are byte-identical;
- all changed pixels fit inside the exported map rectangle;
- the exported map sprite equals the accepted scene rectangle pixel-for-pixel;
- pasting the map sprite at `(x, y)` over the source reconstructs the accepted final scene;
- the standalone detail image exists and is non-empty;
- asset stems and ItemStaticData paths agree;
- staged artifact hashes still match the manifest.

If any check fails, repair the job rather than editing coordinates or reports by hand.

## Coordinate contract

- Origin: full scene top-left.
- X direction: right.
- Y direction: down.
- Unit: source-scene pixels.
- `x, y`: top-left of the exported map crop.
- `width, height`: exact map crop dimensions.
- `z`: Unity sorting value supplied by configuration policy; it is not inferred from pixels.
- Unity uses the crop dimensions and center pivot to turn this top-left point into the runtime Sprite position.

The structured delivery manifest is authoritative. `XYposition.txt` is a compatibility artifact only and must use ASCII punctuation.

## Unity secondary-menu container workflow

Use this workflow for drawers, safes, lockers, cases, boxes, pockets, bins, and other containers that open into a larger in-scene secondary view.

### 1. Establish the runtime chain

Define all three levels before producing art:

1. Type 6 is the closed or normal-state entrance bound by `SceneConfig`. Its `ActionParam` is the Type 7 item ID.
2. Type 7 is the open secondary view. It is generated by Type 6 and is not directly bound by `SceneConfig`. Its `ActionParam` is the comma-separated list of contained evidence IDs.
3. Each contained evidence keeps its own map/detail/icon contract. The Type 7 view shows only enough information to locate and identify it; readable text and close-reading detail belong in its `desSpritePath` Big image.

Block delivery if any link in `Type 6 -> Type 7 -> contained evidence` is missing.

### 2. Export `prop_<container>1.png` as an exact scene screenshot

`prop_<container>1.png` is not regenerated artwork. It is a pixel-exact rectangular screenshot from the accepted final scene at its native dimensions.

- Include the complete closed or normal-state container plus only the minimum stable edge pixels needed for a reliable overlay.
- Record `x`, `y`, `z`, `width`, `height`, and the half-open crop rectangle `[x, y, x + width, y + height]` in the structured delivery manifest.
- Write the same top-left `x,y` to `XYposition.txt`; do not print coordinates into the PNG.
- Pasting `prop_<container>1.png` at `(x, y)` over the matching source scene must reproduce the accepted scene state pixel-for-pixel.
- Never estimate or manually transcribe the coordinate from a review screenshot. Derive it from the accepted native-resolution scene and authorization/crop data.

### 3. Author `prop_<container>2.png` as the open secondary view

The Type 7 image is independently authored from the physical identity of the Type 6 container. It is not a magnified crop of `prop_<container>1.png` and does not need to preserve the scene camera exactly.

- Show the opened container from a top-down or near-top-down view so the interior is legible.
- Preserve the same material, color, construction, wear, handedness, handle placement, and opening direction as the container in the scene.
- Keep the container complete and make the interior readable, but do not turn the evidence inside it into a detailed product shot. Small writing remains unreadable; exact text and puzzle metadata stay in Big images.
- Determine the borderless interior image's final pixel size before adding the required border. Do not resize after border application.

U1 is the sizing reference, not a rigid global clamp. Across the audited U1 drawer/cabinet pairs:

- Type 6 screenshots range from about `60-296 px` wide and `40-160 px` high, with a median near `148 x 74 px`.
- Type 7 final images range from about `272-456 px` wide and `252-484 px` high, with a median near `410 x 356 px`.
- Start an ordinary drawer near `400 x 360 px` final size, then adjust for the container's real aspect ratio, interior contents, available scene space, and gameplay readability. Never enlarge an object merely to expose detailed writing.

### 4. Position Type 7 near Type 6

Type 7 remains in the full scene's top-left, Y-down coordinate system. It is not automatically centered on the screen or treated as an unpositioned UI card.

Use center anchoring as the default proposal, based on the final Type 7 dimensions including its 12-pixel border:

```text
x2 = round(x1 + width1 / 2 - width2 / 2) + nudgeX
y2 = round(y1 + height1 / 2 - height2 / 2) + nudgeY
```

Then make only the smallest justified nudge required by the opening direction, scene boundary, nearby occlusion, or the container's physical attachment. Record `x2`, `y2`, `width2`, `height2`, `nudgeX`, `nudgeY`, and the resulting center offset separately; never reuse Type 6 coordinates silently.

For reference, the audited U1 drawer/cabinet pairs have center offsets of roughly `-40 to +33 px` on X and usually `-53 to +92 px` on Y. Values outside that range are allowed only with a written scene-specific reason. Verify that the complete bordered Type 7 rectangle remains within the source scene canvas.

### 5. Add and verify the final 12-pixel white border

The border is a rectangular, fully opaque white frame around the final borderless Type 7 image. It is not a silhouette stroke and not transparent padding.

After all generation, cleanup, and resizing are complete, run:

```powershell
python scripts/secondary_prop_border.py add `
  --input <approved-final-size-borderless-open-view.png> `
  --output <prop_container2.png> `
  --border 12
```

This places a `W x H` opaque input at `(12, 12)` on an opaque white canvas of `(W + 24) x (H + 24)`. Do not resize or crop the result afterward.

Verify before packaging:

```powershell
python scripts/secondary_prop_border.py verify `
  --input <approved-final-size-borderless-open-view.png> `
  --output <prop_container2.png> `
  --border 12
```

Verification must prove the final dimensions, all four exact white strips, full opacity, and pixel identity of the inner image. Repair the source or rerun border generation when it fails; do not paint over the report.

### 6. Verify and package both states

The staged container delivery must include:

- `prop_<container>1.png`, its exact crop rectangle, and its Type 6 `Position`;
- the approved borderless Type 7 source retained for recovery;
- final `prop_<container>2.png`, its independent Type 7 `Position`, center-anchor calculation, and 12-pixel border declaration;
- the Type 6 and Type 7 ItemStaticData draft rows;
- the contained evidence IDs and proof that only Type 6 is bound by SceneConfig;
- reconstruction verification for Type 6 and border/placement verification for Type 7.

See [references/delivery-contract.md](references/delivery-contract.md) for the container manifest and coordinate example.

## Staging and synchronization

Default to `image/edit_jobs/<job>/delivery/`. Never overwrite the approved scene or write directly into `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE` during generation.

After visual approval, present the staged package and ItemStaticData patch. Copying assets into Unity or changing tables requires explicit user authorization. When merging `XYposition.txt`, preserve existing entries and normalize only the new line unless the user separately authorizes cleanup.

## Recovery

Every job must retain:

- the base coordinate-edit manifests and masks;
- the accepted full scene;
- detail source or cutout mask;
- `delivery_manifest.json`;
- `delivery_verification.json`;
- hashes of all staged runtime artifacts.

Resume from these artifacts. Do not reconstruct a coordinate from screenshots or memory.
