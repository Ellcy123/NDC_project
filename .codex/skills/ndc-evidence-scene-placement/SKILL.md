---
name: ndc-evidence-scene-placement
description: Place direct-pickup items, photographed clues, and clickable environmental observations in an approved NDC base exploration scene, then derive exact Map crops and Unity Positions from the accepted native-resolution image. Use only after the parent evidence router has explicitly selected the base-scene route; do not use for secondary-menu containers, detail-only grants, or minigame assets.
---

# NDC Evidence Scene Placement

This is an explicit-only execution sub-skill. It owns the base-scene visual anchor, coordinate-safe scene edit when one is needed, exact Map crop, full-scene `Position`, and scene-package verification. It does not decide the acquisition route and does not author container interiors.

## Required parent route contract

Start only when `$ndc-scene-evidence-placement` has supplied a resolved route contract containing:

- Unit, Episode, Loop, Scene ID, Item ID, evidence name, and source design/state references;
- route: `direct-scene` or `environment`;
- `itemType`: `3/item`, `1/clue`, or `2/envir`;
- the exact player acquisition/observation event;
- `anchorMode`: `visible-record` or `observation-anchor`;
- `hotspotMode: object-alpha` and the exact object/condition silhouette that may be clicked;
- approved base-scene PNG and native pixel dimensions;
- visible clickable anchor and its state before interaction;
- acquired record identity and state after interaction;
- explicit confirmation that clicking does not open a separate interior or secondary view;
- approved naming stems, folder path, and required `z` value cited to current configuration policy or an approved existing row;
- the Map information budget and spoiler exclusions;
- Big/Icon handoff status or the sibling detail-art task that will produce them.

Do not infer missing routing facts from the noun, filename, empty table fields, or an old `pickup` label. If the contract is absent, incomplete, or contradicts the source state/config, stop before art production and return the unresolved row to the parent router.

## Hard routing gate

This sub-skill accepts only interaction resolved on the base exploration scene:

- `direct-scene`: the player clicks the visible record itself and immediately obtains an `item` or records a photographed `clue`;
- `environment`: the player clicks a visible scene condition and opens an `envir` observation that never enters inventory.

Immediately return to the parent router without generating or modifying art when:

- the click opens an independent interior, enlarged open state, drawer view, cabinet view, safe view, or any other secondary image;
- the target is physically hidden behind a closed cabinet door, drawer front, lid, lockbox, or similar closure and must be revealed before it can be clicked;
- the player must click a container and then click a contained child;
- the acquisition is automatic, dialogue-granted, Expose-granted, analysis/combine-derived, or minigame-only;
- the proposed hotspot is a table, shelf, floor patch, drawer front, or other region rather than the visible record itself;
- the player interaction, visible state, or clickable anchor is unclear.

A region hotspot belongs only to the Type 6 entrance of a real secondary-menu container and is outside this sub-skill. Do not expose a hidden evidence object's Big-only title, date, number, signature, body text, or puzzle conclusion merely to make furniture clickable. If the record is hidden, return it to the parent router for a visible-record redesign or a `container-click` chain.

Identity checks depend on `anchorMode`:

- `visible-record`: Map, Big, and Icon represent the same physical record and must preserve identity and state.
- `observation-anchor`: Map and observation Big represent the same environmental condition at different information scales.

## Runtime delivery contracts

| Runtime type | This sub-skill owns | Required detail-art handoff | Forbidden |
|---|---|---|---|
| `item` | Exact scene Map and full-scene `Position` | Ordinary transparent Big plus independently approved `130 x 130` Icon | Big/Icon-only delivery for a scene search; readable Big detail in the Map |
| `clue` | Exact photographed-condition Map and full-scene `Position` | Locked `620 x 620` clue-Polaroid Big plus independently approved `130 x 130` Icon | Treating a clue as a loose inventory object; substituting Big for the scene anchor |
| `envir` | Exact no-suffix Map and full-scene `Position` | Observation Big only | Any Icon stem, `iconPath`, Icon report, or `*_icon.png` artifact |

The route defines whether a world-space Map is needed; `itemType` defines the detail contract after interaction. Every accepted record in this sub-skill requires a non-empty Map, `Position`, and Big. `item` and `clue` additionally require an Icon before final delivery; `envir` must omit it completely.

## Read only what the job needs

1. Read the relevant Unit evidence-art requirement and matching state scene. If Unit/Episode or ID identity is involved, read `canon_manifest.json` first.
2. Before any raster insertion, replacement, or cleanup, read [`../ndc-coordinate-image-edit/SKILL.md`](../ndc-coordinate-image-edit/SKILL.md) completely and follow it as the sole coordinate-locked edit workflow.
3. Before naming or packaging, read the shared [delivery contract](../ndc-scene-evidence-placement/references/delivery-contract.md).

Actual Big/Icon authorship and its detailed production contract belong to `$ndc-evidence-detail-art`. This skill consumes that child's approved artifacts and verification reports rather than reloading or reinterpreting its art rules.

Shared scripts and references remain under `../ndc-scene-evidence-placement/`; do not copy, move, or fork them into this skill.

## Workflow

### 1. Freeze the base-scene and information contracts

Record the approved PNG path, dimensions, mode, and hash. Separate:

- `Map contract`: only the object class, silhouette, material, broad color, physical state, natural placement, and discoverable scene anchor;
- `Big contract`: exact close-reading content such as titles, dates, numbers, handwriting, damage, comparison marks, or puzzle detail;
- `Icon contract`: inventory-scale presentation for `item`/`clue`, or an explicit omission for `envir`.

The Map is a discovery surface, not an evidence card. At expected gameplay size it must be findable without becoming a close-up or revealing the Big's answer. An environmental sign may remain readable only when reading that sign in the scene is the approved observation itself.

### 2. Lock scene-first Map authorship

Every accepted Map from this sub-skill ends as a per-record RGBA scene layer with transparent pixels outside that record's clickable visual. Choose between only these two Map-authoring cases:

1. `Existing anchor`: when the approved scene already contains the correct clickable object or condition, extract a source-sized semantic RGBA overlay from that scene at identical pixels. Do not redraw it merely to manufacture a delta.
2. `New or repaired anchor`: use the mandatory scene-first sequence in the next section. The object must first exist in an accepted coordinate-locked scene result; only afterward may its RGBA Map be extracted.

For a new or repaired direct-scene Map, it is forbidden to generate a standalone transparent prop or a chroma-green prop first and then paste it into the scene as the Map source. Native-alpha and green-screen generation remain available to the sibling detail-art workflow for Big/Icon production, but they do not establish scene placement, Map pixels, hotspot alpha, or `Position`.

If extraction needs cleanup, remove background from the object as it appears in the accepted scene result. Do not replace it with a separately generated cleaner object. The final alpha must still belong to the same scene-placed pixels that established the coordinates.

### 3. Use existing-anchor extraction or scene-first coordinate-locked insertion

If the approved scene already contains the correct clickable anchor, preserve it. Build a source-sized semantic mask around only the complete clickable object/condition and extract an RGBA overlay at the identical pixels. Do not include stable local background in its alpha and do not redraw the scene just to manufacture changed pixels.

If the anchor must be added or repaired, use `ndc-coordinate-image-edit` and follow this order:

1. Never overwrite the approved source. Obtain the image-edit-specific `before -> after` confirmation required by that skill before the first raster mutation or generation.
2. Draw a tight rectangular placement box on the approved native-resolution scene around the intended object envelope on its real support plane. This rectangle controls where the model places the object; it is not a Map crop, composition mask, or hotspot.
3. Expand the placement box into the broader parent authorization workspace required by the coordinate-edit skill. Prepare a legal full scene crop with enough unchanged context for perspective, scale, lighting, support-surface geometry, and shadows.
4. Ask the image model to edit and return the complete scene crop, not an isolated object, green-screen prop, close-up, inventory card, or transparent asset. The object must appear directly inside the placement box at ordinary physical scale.
5. Compose the generated crop back into the full scene at the locked coordinates. Approve the native-resolution scene result for framing, scale, perspective, contact, lighting, information budget, and boundary integrity before any Map extraction.
6. From that accepted full-scene result, semantically extract only the actual clickable object or condition into a source-sized RGBA layer. Derive a fresh composition mask from this extracted layer; never reuse the placement rectangle or broad authorization mask as object alpha.
7. When the broad generated crop introduces unrelated drift, rebuild the delivery scene from the untouched approved source plus the extracted scene-derived layer at the same coordinates. This cleanup is permitted because the object still originates from the accepted in-scene generation; a separately generated replacement object is not permitted.
8. Run boundary, relevant structural-line, and final union-mask verification on the delivery scene. The final scene must preserve the source dimensions and mode and keep every pixel outside the final extracted-layer authorization byte-identical.

Keep detailed text unreadable in the base-scene view. Orient the object with the support surface and vanishing lines. The placement box may be larger than the final object, but the final hotspot may not borrow that extra area.

The accepted full-size final PNG—not a generated crop, preview, resized review image, or rejected candidate—is the sole coordinate truth.

### 4. Approve the anchor and hotspot at gameplay size

Reject the candidate even when pixel checks pass if:

- the anchor looks like a product shot, evidence card, floating UI, or close-up;
- the prop is enlarged, stood up, rotated, or turned toward the viewer for legibility;
- Big-only text or metadata is readable too early;
- perspective, thickness, contact shadow, reflection, or occlusion conflicts with the scene;
- any object part or required shadow is clipped or visually dissolves at the edit boundary;
- the hotspot cannot be understood as something the player could reasonably click;
- the Unity hotspot proxy includes unrelated table, floor, wall, shelf, another record, or empty space between separate objects;
- the visual implies opening a container or entering another view, contradicting the parent route.

Inspect both a close crop and the full scene at expected gameplay display size. Also inspect `hotspot_overlay.png`, generated from the Map alpha at Unity's current `0.5` physics-shape threshold. A compound record such as “two glasses” may produce two disconnected hotspot islands; do not bridge them with a clickable rectangle. A tiny record may include its own visible ash, damage, spill, or contact area when that is part of the record, but may not borrow a nearby glass, coaster, table patch, or sibling evidence merely to enlarge the click target.

For a scene-first insertion, explicitly compare three different shapes: the rectangular placement box, the broad generation authorization workspace, and the final extracted object alpha. Only the last one may define the direct-scene hotspot. A necessary soft contact shadow may remain a visual contribution below the `0.5` physics threshold or in a separately verified non-clickable scene delta, but the support surface must remain non-clickable.

### 5. Derive the transparent Map and `Position`

Use this coordinate contract:

- origin: full-scene top-left;
- X increases right; Y increases down;
- unit: native source-scene pixels;
- `x, y`: top-left of the exact Map rectangle;
- `width, height`: exact Map crop dimensions;
- `z`: supplied by configuration policy, never inferred from pixels;
- rectangles are half-open `[left, right)` and `[top, bottom)`.

Export one RGBA Map layer per record. Its RGB/alpha must render the accepted object state, its transparent exterior must own no scene pixels, and its alpha-derived physics shape must represent only that record's hotspot.

- For a newly inserted/repaired anchor, retain the source-sized RGBA layer extracted from the accepted full-scene generation result and let the shared packager derive the Map rectangle from its nonzero-alpha bounds plus transparent padding.
- For a scene-integrated or unchanged anchor, provide an audited source-sized RGBA semantic layer at the exact full-scene coordinates.
- The full RGB accepted scene is a visual and zero-drift review artifact. It is not the runtime click Sprite.
- Never hand-transcribe `Position` from a screenshot or preview.

Prove that alpha-compositing the Map at `(x, y)` over its matching reconstruction base produces the accepted per-record delivery scene state pixel-for-pixel. Record the scene-first provenance chain—placement rectangle, generated scene crop, accepted full-scene result, extracted source-sized layer, Map rectangle, and final `Position`—in the staged manifest. For a multi-record scene, also prove that composing all sibling Map layers in the approved order produces the accepted combined scene and that sibling hotspot masks do not overlap.

### 6. Join the detail-art handoff

Before packaging, require the itemType-specific approved files from the parent orchestration:

- `item`: ordinary Big and independently produced `130 x 130` RGBA Icon with passing Icon report;
- `clue`: locked `620 x 620` clue-Polaroid Big and independently produced `130 x 130` RGBA Icon with passing Icon report;
- `envir`: observation Big and explicit Icon omission.

For `visible-record` and `observation-anchor`, check that Map and Big preserve the same physical identity, material, handedness, damage, and state. The Big may face the player and reveal detail; the Map may not. Do not mechanically shrink Big into Icon, and do not create a placeholder detail asset inside this skill.

### 7. Package with the shared deterministic tool

From the repository root, use:

```text
<workspace-python> .codex/skills/ndc-scene-evidence-placement/scripts/evidence_delivery.py package \
  --source-scene <approved-scene-before-anchor.png> \
  --final-scene <accepted-native-resolution-final.png> \
  --authorization-mask <source-sized-edit-or-anchor-mask.png> \
  --base-verification <coordinate-final-verification.json> \
  --map-layer <source-sized-per-record-rgba-layer.png> \
  --map-padding 4 \
  --hotspot-target <exact-clickable-object-or-condition> \
  --item-id <item-id> \
  --scene-id <scene-id> \
  --folder-path <EPIxx\scene-folder> \
  --map-stem <SCxxxx_item_xxxx> \
  --detail-stem <SCxxxx_item_xxxx_big> \
  --icon-stem <SCxxxx_item_xxxx_icon> \
  --detail-image <approved-detail.png> \
  --icon-image <approved-130x130-icon.png> \
  --icon-verification <icon-verification.json> \
  --z <approved-z> \
  --output-dir <ndc-temp-work>/packages/<item-id>
```

For an unchanged existing anchor, `--base-verification` is not required, but the source-sized RGBA overlay and semantic authorization mask remain required. For `envir`, replace all Icon arguments with `--omit-icon`. Do not leave an empty Icon artifact or field. `--allow-opaque-region-map` is legacy/container compatibility only and is forbidden for this direct-scene sub-skill.

Then run:

```text
<workspace-python> .codex/skills/ndc-scene-evidence-placement/scripts/evidence_delivery.py verify \
  --manifest <ndc-temp-work>/packages/<item-id>/delivery_manifest.json>
```

Never use `--allow-legacy-derived-icon` for new production work.

### 8. Block or release delivery

Delivery passes only when:

- the parent route contract still matches the actual player interaction;
- the native source/final dimensions and mode match;
- changed-scene coordinate verification passes and every pixel outside the authorized union is byte-identical;
- a newly generated anchor has a complete scene-first provenance chain and no isolated-prop-first Map source;
- Map crop, dimensions, manifest `Position`, and asset stem agree;
- Map is RGBA; alpha-compositing it over the matching reconstruction base passes pixel-for-pixel;
- the generated hotspot overlay matches the intended object and excludes support surfaces, sibling records, and empty bridges between disconnected objects;
- sibling hotspot intersection is zero unless an approved runtime priority rule is documented;
- Map reveals no unapproved Big-only information;
- Big exists and is non-empty and matches the Map identity/state for `visible-record` and `observation-anchor`;
- `item`/`clue` has a passing independent Icon; `envir` has no Icon anywhere;
- staged hashes still match the manifest;
- no unresolved route, visual-anchor, or container ambiguity remains.

Repair the source job or return the row to the parent router when a check fails. Never patch coordinates, manifests, reports, or runtime paths by hand to force a pass.

## Temporary staging and handoff

Stage the detailed per-record package under `<system-temp>/ndc_art_jobs/<job>-<uuid>/packages/<item-id>/`. Do not overwrite the approved scene, write process files into the repository, or write directly to Unity. Copying assets to Unity or changing live tables requires separate explicit authorization.

Return to the parent orchestration:

- route contract and source citations;
- accepted native-resolution scene path/hash;
- anchor/edit masks and coordinate verification when applicable;
- exact Map rectangle and `[x, y, z]` Position;
- hotspot mode, alpha threshold, hotspot overlay, and sibling-overlap result;
- Map, Big, and Icon paths, or explicit `envir` Icon omission;
- delivery manifest and verification report;
- any blocked row with the precise routing reason.

This handoff is internal and temporary. After all sibling records reach a terminal state, the parent router uses the shared compact publisher to copy only accepted runtime Map/Big/Icon PNGs into `image/deliveries/<batch>/<scene>/assets/`, write one scene-level `XYposition.txt`, one `scene_preview.png`, and one compact `production_report.json`. Per-record manifests, patches, XY files, overlays, masks, reports, masters, and generated candidates remain temporary and are deleted only after the final publication hashes pass.
