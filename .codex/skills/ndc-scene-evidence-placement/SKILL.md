---
name: ndc-scene-evidence-placement
description: Place collectible NDC evidence and environmental observations into approved raster scenes, enforce complete Map/Position/Big/Icon contracts by runtime item type and acquisition route, prepare Unity Type 6 to Type 7 container chains, and deterministically finalize Map, Big, 130px Icon, and 620px clue-Polaroid assets. Use when adding, replacing, auditing, or packaging clickable evidence props, clue photos, environment observations, or container contents in NDC exploration scenes.
---

# NDC Scene Evidence Placement

Turn an approved scene plus an evidence requirement into a staged, Unity-ready evidence package. Preserve the source and derive coordinates from the accepted final image. Never eyeball or manually transcribe `Position`.

## Read first

1. Read the relevant Unit evidence-art document and the matching state scene before deciding what appears in the scene.
2. Read `../ndc-coordinate-image-edit/SKILL.md` completely before any raster insertion or replacement. Its source-preservation, mask, crop, seam, and final-union checks remain mandatory.
3. Read [references/delivery-contract.md](references/delivery-contract.md) before naming or packaging assets.
4. When the request includes a Big image, Icon, or clue Polaroid, read [references/detail-icon-production.md](references/detail-icon-production.md) before generating, scaling, rotating, framing, or approving it.

If the request includes Unit/Episode identity or IDs, read `canon_manifest.json` before inferring paths or namespaces.

## Classify before editing

Resolve two separate axes before assigning a delivery class:

| `ItemStaticData.itemType` | Runtime meaning | Standard art behavior |
|---|---|---|
| `3` / `item` | A physical object or document that enters inventory. It may optionally support analysis or combination. | A world-space pickup needs Map + `Position` + ordinary Big + Icon. A dialogue, Expose, analysis, or minigame grant that is never left for the player to locate needs Big + Icon and no invented Map. |
| `1` / `clue` | A photographed or recorded scene condition. The player collects the record, not the original object; clues cannot be analyzed or combined. | A photographed scene clue needs Map + `Position` + locked `620 x 620` clue-Polaroid Big + Icon. An automatic or derived clue result with no world-space locate/click step needs its approved result Big + Icon and no invented Map. |
| `2` / `envir` | A clickable environmental observation that never enters inventory. | Always deliver a no-suffix Map + full-scene `Position` + Big, and omit Icon completely. Pure non-interactive scene dressing is background art, not an `envir` ItemStaticData row. |

`itemType` defines what the record means after interaction. The actual acquisition event defines whether an `item` or `clue` needs a world-space Map. Never infer the delivery solely from the type name or from prefilled path fields.

Then assign every requested evidence record one delivery class:

- `scene-pickup`: a visible, clickable `item` or photographed `clue` obtained by investigating the base scene. Deliver Map, `Position`, the type-appropriate Big, and Icon.
- `container-state`: a drawer, safe, locker, case, box, pocket, bin, or similar Unity secondary-menu container. Deliver a scene-exact Type 6 entrance screenshot, a separately authored Type 7 open view, independent coordinates for both, and the complete Type 6 -> Type 7 -> contained-item chain. Every contained interactive record also requires its own Map crop and full-scene `Position`, plus its itemType-appropriate Big/Icon contract. Do not treat the container pair as a substitute for the contained record's Map.
- `detail-only`: an `item` or `clue` analysis result, memory result, automatic minigame output, or handed-over evidence that is never visible or clickable as a world prop. Deliver the type-appropriate Big and Icon only; do not invent a scene coordinate. An `envir` record can never use this class. A `post_expose`, dialogue, or minigame label alone does not prove this class; inspect the actual acquisition event.
- `environment`: an ItemStaticData `envir` observation. Deliver a real no-suffix Map, full-scene `Position`, and Big; omit `iconPath` and the `*_icon.png` artifact. The Map may be an exact crop from a baked final scene or an approved conditional/State overlay, but it must be a real scene hotspot that can be placed at its recorded coordinate.
- `minigame-only`: an interaction asset that does not enter ItemStaticData. Route it to the minigame asset workflow.

Classify from the actual player acquisition event in the matching state, SceneConfig, and ItemStaticData chain—not from filenames, an existing empty `mapSpritePath`, or `pickup` alone. Create an acquisition coverage row for every requested evidence item with: `itemId`, acquisition event, delivery class, visible state, parent container IDs when applicable, Map stem, full-scene `Position`, Big stem, Icon stem or explicit omission, and source references.

Apply this hard gate before art production and again before delivery:

- Anything obtained by clicking or searching the exploration scene must have a visible scene anchor. Big and Icon alone never satisfy an exploration pickup.
- A direct `item` pickup or photographed `clue` requires a non-empty Map and `Position`, plus the type-appropriate Big and Icon.
- A pickup found after opening a Type 7 container requires its own non-empty Map and `Position` inside the displayed Type 7 view. Type 6 and Type 7 images do not replace that child Map.
- An `item` or `clue` granted automatically by dialogue, Expose, minigame completion, or analysis may omit Map only when it is never left for the player to locate or click. If the event visibly presents the record in the scene, deliver the required conditional/handover state as well.
- Every `envir` row requires non-empty `mapSpritePath`, full-scene `Position`, and `desSpritePath`. Its `iconPath` must be empty or omitted, and no environment Icon file may be staged. Missing Map/Position/Big or a configured/staged environment Icon blocks delivery.
- A locked or post-Expose cache must be classified by what the player does after it unlocks. If the player opens it and clicks the contents, it is a container exploration chain; if the game grants the contents automatically, document the visible event state and the no-Map reason.

Block the batch when any acquisition coverage row is unresolved. Do not generate Big/Icon-only placeholders to make an incomplete row look finished.

## Art authorship boundary

The evidence's semantic appearance must come from an approved high-resolution raster master: an accepted image-generation result, artist-authored raster, approved source extraction, or an approved deterministic transformation of such a master. The master must already establish the prop silhouette, perspective, material, construction, wear, lighting, and scene context.

Deterministic code may own masks, crop rectangles, coordinate extraction, compositing, perspective transforms, rotation, scale, alpha handling, locked-frame application, exact-text placement, export dimensions, overlays, hashes, and verification reports. It must not originate the evidence or scene artwork.

Production delivery is blocked when Python/Pillow, Canvas, SVG, HTML/CSS, shaders, or similar procedural drawing is used to create the prop body, paper/card surface, container, furniture, background, scene state, texture, wear, lighting, handwritten marks, or illustrative layout. These APIs remain valid for test fixtures, masks, debug overlays, borders, and deterministic transforms of approved art.

Exact titles, dates, numbers, or body text may be composited deterministically only onto an approved illustrated physical master. Code must not fabricate a whole document by drawing a blank page, table, rules, stamps, handwriting, and text. Record the semantic master path/hash and any exact-text layer path/hash in the job manifest. A visual assembled mostly from code is a mockup, not a final asset.

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
- `icon-presentation contract`: the inventory-scale silhouette, view, lighting, material identity, short left-down shadow, and readability needed at `130 x 130`. It is a separate presentation asset, not a mechanically shrunken Big. A flat front-facing paper or approved Polaroid may be deterministically re-laid out from its approved Big surface; a dimensional prop requires its own high-resolution icon master.

For an `envir` record, replace the `icon-presentation contract` with an explicit Icon-omission contract. Do not create an Icon merely because another ItemStaticData row in the same scene has one.

Never copy the detailed text requirements from the `big-detail contract` into the in-scene generation prompt. The map scene is a discovery anchor, not a readable evidence card or product shot. Unless the evidence itself is an environmental sign meant to be read in the scene, body text and exact metadata must remain unreadable at gameplay scale.

### 2. Prepare the insertion with the base skill

Use `ndc-coordinate-image-edit` to create the source-sized authorization mask, legal generation crop, job manifest, and non-destructive composed scene.

The authorization workspace must include:

- the new object;
- its physically necessary contact shadow, reflection, or occlusion;
- a generous portion of the legal support surface for natural integration and model freedom.

For a collectible scene pickup, start from a tight intent mask and expand it into the parent authoring workspace under the base skill's evidence rule: at least `3x` the proposed object bounds on both axes, at least `128 source pixels` on every unoccluded side, and preferably the whole usable tray, tabletop, drawer interior, or floor patch. After generation, derive a separate final composition mask from the actual object, shadow, and necessary support-surface patch; keep at least `64 source pixels` around every unoccluded semantic edge. The composition mask must remain inside the parent workspace but must not include unrelated model drift merely because the parent workspace allowed it. Do not include characters or protected architecture. Never rescale or crop the full scene after placement.

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
- any semantic part of the prop or its contact shadow is clipped by the parent workspace or comes within `64 source pixels` of an unoccluded final-composition hard-mask edge.
- a freestanding container fails the completeness check: its opening or rim, both unoccluded side walls, bottom or base ring, and contact shadow must remain visibly complete and separable at gameplay size. Natural occlusion is allowed only when caused by an existing scene object and recorded in the placement contract; touching a mask boundary, visually dissolving into a same-value background, or merely passing pixel-containment checks is not acceptable.

Inspect this at the full scene's expected gameplay display size, not only in a zoomed crop. Pixel containment is necessary but is not visual approval.

### 4. Prepare the standalone evidence image

Keep two outputs conceptually separate:

- Map crop: an exact rectangular crop from the accepted scene. It normally includes local scene background and is what Unity places at `Position`.
- Detail image: the standalone evidence view used by `desSpritePath`. Prefer a separately approved transparent detail render when legibility or presentation requires it. Otherwise use a clean source/crop-sized alpha mask to extract the accepted object.

The detail image may be a clearer view than the in-scene object, but identity, material, damage, labels, handedness, and state must match.

The detail image is the only default location for close-reading content. It may face the viewer and present exact text clearly; the matching map object should preserve the same identity and state without duplicating that information density.

Do not send the `2560 x 1600` three-frame guide to Unity. It is a measurement and layout workspace only. Finalize an ordinary transparent Big as exactly one selected frame: portrait `571 x 1000`, square `818 x 818`, or landscape `1000 x 571`. Finalize an Icon as `130 x 130` RGBA with all visible prop and shadow pixels inside the fixed `115 x 115` safe rectangle. A clue Polaroid remains `620 x 620`; its frame is locked and the photo is perspective-composited through the canonical window mask. The exact coordinates, commands, alpha rules, and review sizes are in [references/detail-icon-production.md](references/detail-icon-production.md).

### 5. Package deterministically

Run:

```powershell
python scripts/evidence_delivery.py package `
  --source-scene <approved-scene-before-item.png> `
  --final-scene <approved-scene-with-item.png> `
  --authorization-mask <source-sized-item-mask.png> `
  --base-verification <final_verification.json> `
  --map-padding 32 `
  --item-id <item-id> `
  --scene-id <scene-id> `
  --folder-path <EPIxx\scene-folder> `
  --map-stem <SCxxxx_item_xxxx> `
  --detail-stem <SCxxxx_item_xxxx_big> `
  --icon-stem <SCxxxx_item_xxxx_icon> `
  --detail-image <approved-transparent-detail.png> `
  --icon-image <approved-130x130-icon.png> `
  --icon-verification <icon-verification.json> `
  --z <-3> `
  --output-dir <image\edit_jobs\job\delivery>
```

Use `--cutout-mask` instead of `--detail-image` only when the standalone image must be extracted from the accepted final scene. Production packaging for `item` and `clue` requires an independently approved `130 x 130` RGBA Icon and its passing report from `evidence_art.py verify-icon` or `finalize-icon`. Every `envir` package must use `--omit-icon` and omit all Icon arguments, manifest fields, patch fields, and staged Icon files. The package command must never silently shrink a Big or detail image into an Icon. `--allow-legacy-derived-icon` exists only to rebuild an audited old package and must be explicit in its manifest.

When both the source and accepted final scene are supplied, the script derives the map rectangle and `(x, y)` from the actual changed-pixel bounds, then adds `--map-padding` (default `32`). This deliberately decouples the runtime Map crop from the much larger authorization workspace. When no source is available, it falls back to the authorization-mask bounds. `--map-rect left top right bottom` is only an audited compatibility override for pre-existing baked props. The rectangle is top-left based and half-open. It must contain every changed pixel and all clickable visual content.

### 6. Verify the delivery

Run:

```powershell
python scripts/evidence_delivery.py verify --manifest <delivery_manifest.json>
```

Delivery is blocked unless all applicable checks pass:

- every acquisition coverage row passes and every exploration-acquired item has its required Map/`Position` scene anchor;
- the job manifest identifies an approved semantic raster master, and no production artwork was procedurally originated by code;
- source and final scene dimensions/mode match;
- the base coordinate verification passes;
- pixels outside the authorization mask are byte-identical;
- all changed pixels fit inside the exported map rectangle; the larger unused portion of the authorization workspace does not have to fit inside it;
- the exported map sprite equals the accepted scene rectangle pixel-for-pixel;
- pasting the map sprite at `(x, y)` over the source reconstructs the accepted final scene;
- the standalone detail image exists and is non-empty;
- when `iconPath` is present, the staged Icon is exactly `130 x 130` RGBA, all visible pixels remain inside `[7,7,122,122)`, transparent pixels carry zero RGB, and the supplied Icon verification report matches the staged bytes;
- when `--omit-icon` is used, the patch, manifest, and artifact list all omit the Icon rather than writing an empty or invented path;
- every `envir` package has Map + `Position` + Big, uses `--omit-icon`, and contains no `iconPath`, Icon stem, Icon verification report, or `*_icon.png` file;
- asset stems and ItemStaticData paths agree;
- staged artifact hashes still match the manifest.

If any check fails, repair the job rather than editing coordinates or reports by hand.

## Environment observation workflow

Use the normal scene-coordinate workflow for every ItemStaticData `envir` record, even though it does not enter inventory:

1. Preserve or author the observation in the accepted full-resolution scene or an approved conditional/State layer.
2. Export the no-suffix Map as an exact scene-local crop and derive its full-scene `Position` from that accepted native-resolution image.
3. Produce the `desSpritePath` Big for the player's close observation. Keep its physical identity and state consistent with the Map.
4. Package with `--omit-icon`; leave `iconPath` empty or omit it, and stage no Icon file.
5. Verify Map reconstruction/alignment, non-empty Big, asset stems, coordinates, hashes, and complete Icon omission.

An object that is only visual dressing and cannot be clicked or recorded belongs in the background art and must not be added as an `envir` ItemStaticData row.

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

Block delivery if any link in `Type 6 -> Type 7 -> contained evidence Map/Position -> contained evidence Big/Icon` is missing.

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

The accepted Type 7 view is also the coordinate truth for its contained evidence. Each clickable child must be fully visible and separable at gameplay size. Do not use generic paper piles, generic cards, or an empty container as a stand-in for several distinct contained items.

U1 is the sizing reference, not a rigid global clamp. Across the audited U1 drawer/cabinet pairs:

- Type 6 screenshots range from about `60-296 px` wide and `40-160 px` high, with a median near `148 x 74 px`.
- Type 7 final images range from about `272-456 px` wide and `252-484 px` high, with a median near `410 x 356 px`.
- Start an ordinary drawer near `400 x 360 px` final size, then adjust for the container's real aspect ratio, interior contents, available scene space, and gameplay readability. Never enlarge an object merely to expose detailed writing.

### 4. Export every contained evidence Map

For every evidence ID in the Type 7 `ActionParam`:

1. Define the child's exact rectangular crop in the accepted final bordered Type 7 image. Include the whole clickable visual and enough stable local context; do not crop through the object or shadow.
2. Export that rectangle pixel-for-pixel as the child's `mapSpritePath` PNG. It may repeat pixels already visible in Type 7; this matches the established Unity overlay convention.
3. Convert the Type 7-local crop origin to the full-scene coordinate system:

```text
childX = type7X + localCropLeft
childY = type7Y + localCropTop
```

4. Write `[childX, childY, childZ]` to the child's `Position`. Never leave `mapSpritePath` or `Position` empty for a contained exploration pickup.
5. Verify that the child crop lies completely inside Type 7 and that pasting it at `(childX, childY)` aligns pixel-for-pixel with the displayed Type 7 view.

Use the same low-information rule as a base-scene Map: the child sprite identifies the item in the opened container; exact readable evidence content stays in Big.

### 5. Position Type 7 near Type 6

Type 7 remains in the full scene's top-left, Y-down coordinate system. It is not automatically centered on the screen or treated as an unpositioned UI card.

Use center anchoring as the default proposal, based on the final Type 7 dimensions including its 12-pixel border:

```text
x2 = round(x1 + width1 / 2 - width2 / 2) + nudgeX
y2 = round(y1 + height1 / 2 - height2 / 2) + nudgeY
```

Then make only the smallest justified nudge required by the opening direction, scene boundary, nearby occlusion, or the container's physical attachment. Record `x2`, `y2`, `width2`, `height2`, `nudgeX`, `nudgeY`, and the resulting center offset separately; never reuse Type 6 coordinates silently.

For reference, the audited U1 drawer/cabinet pairs have center offsets of roughly `-40 to +33 px` on X and usually `-53 to +92 px` on Y. Values outside that range are allowed only with a written scene-specific reason. Verify that the complete bordered Type 7 rectangle remains within the source scene canvas.

### 6. Add and verify the final 12-pixel white border

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

### 7. Verify and package all states and contained items

The staged container delivery must include:

- `prop_<container>1.png`, its exact crop rectangle, and its Type 6 `Position`;
- the approved borderless Type 7 source retained for recovery;
- final `prop_<container>2.png`, its independent Type 7 `Position`, center-anchor calculation, and 12-pixel border declaration;
- the Type 6 and Type 7 ItemStaticData draft rows;
- every contained interactive record's Map crop, full-scene `Position`, itemType-appropriate Big/Icon deliverables, ItemStaticData draft row, and Map-to-Type-7 alignment verification;
- the contained evidence IDs and proof that only Type 6 is bound by SceneConfig;
- reconstruction verification for Type 6 and border/placement verification for Type 7.

See [references/delivery-contract.md](references/delivery-contract.md) for the container manifest and coordinate example.

## Staging and synchronization

Default to `image/edit_jobs/<job>/delivery/`. Never overwrite the approved scene or write directly into `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE` during generation.

After visual approval, present the staged package and ItemStaticData patch. Copying assets into Unity or changing tables requires explicit user authorization. When merging `XYposition.txt`, preserve existing entries and normalize only the new line unless the user separately authorizes cleanup.

## Recovery

Every job must retain:

- the acquisition coverage ledger and classification reasons;
- the approved semantic raster master and its provenance/hash; exact-text layers are retained separately when used;
- the base coordinate-edit manifests and masks;
- the accepted full scene;
- detail source or cutout mask;
- Big, Icon, or clue-Polaroid masters, masks, selected frame/direction parameters, locked-template hashes, and finalization reports when applicable;
- `delivery_manifest.json`;
- `delivery_verification.json`;
- hashes of all staged runtime artifacts.

Resume from these artifacts. Do not reconstruct a coordinate from screenshots or memory.
