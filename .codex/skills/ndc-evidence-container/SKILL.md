---
name: ndc-evidence-container
description: Execute an already-routed NDC secondary-menu container chain from a closed Type 6 entrance through an independent Type 7 interior view to individually clickable item or clue children. This is an internal subskill for the main evidence router; do not use it for direct scene pickups, environmental observations, or automatic multi-item grants.
---

# NDC secondary-menu container execution

Build and verify one complete `Type 6 -> Type 7 -> clickable children` chain. This skill executes a route that `$ndc-scene-evidence-placement` has already approved; it does not decide whether an ambiguous interaction should be a container.

## Admission gate

Accept the job only when the route contract says all of the following:

- the resolved parent route is `container-click`;
- the player clicks a closed or normal-state container in the base exploration scene;
- the click opens a separate interior image;
- the player then clicks each collectible child in that interior view;
- every child is an `item` or `clue` that receives its own Map, full-scene `Position`, Big, and Icon.

Typical containers include a cabinet / 柜子, drawer / 抽屉, safe / 保险箱, locker or deposit locker / 寄存柜, case, chest, lidded box, or another object whose contents are hidden until it opens.

Return the job to the main router without producing or configuring assets when any of these is true:

- no independent open/interior image appears after the first click;
- the visible object is already a direct pickup in the base scene;
- a child is an `envir` observation;
- the requested behavior is to open the container and atomically grant several items without individual child clicks;
- the route, runtime IDs, child list, or accepted source scene is missing or ambiguous.

Do not approximate an unsupported route by placing hidden contents in the base scene, binding the Type 7 row directly, converting an `envir` row into a collectible, or silently changing an automatic grant into individual clicks.

## Required route contract

Before art or configuration work, require:

- accepted native-resolution base scene, scene ID, canvas size, and coordinate system;
- Type 6 ID, approved asset stem, closed-state crop target, and intended `SceneConfig` binding;
- `hotspotMode: secondary-menu-region` for the Type 6 entrance, with the exact coherent container/opening region the player may click;
- one Type 7 ID, approved asset stem, and an approved or authorable independent interior view;
- ordered child IDs, each child's confirmed `itemType` (`item` or `clue`), approved stems, intended visible form in Type 7, and `hotspotMode: object-alpha`;
- approved `z1`, `z2`, and every `childZ`, each cited to the current configuration policy or an approved existing row rather than inferred from pixels;
- staging destination and source references from State and current configuration.

Never invent IDs, reorder children, infer a missing child from prose, or copy coordinates from a screenshot. If a field is missing, report the missing field to the main router and stop.

## Runtime chain invariants

Define the chain before producing art:

1. The closed or normal entrance row has `itemType: 6`.
2. Type 6 `ActionParam` contains exactly one value: the Type 7 item ID.
3. The open-view row has `itemType: 7`.
4. Type 7 `ActionParam` is the ASCII-comma-separated list of all and only the individually clickable child IDs, in the approved order.
5. `SceneConfig` binds only the Type 6 entrance. It must not independently bind Type 7 or any contained child.
6. Every child has a non-empty `mapSpritePath`, full-scene `Position`, `desSpritePath`, and `iconPath`, with matching Map, Big, and Icon files.
7. Type 6 and Type 7 coordinates are derived and recorded independently. Never reuse one state's coordinates as the other state's coordinates without a separate calculation and a documented scene-specific reason.
8. Only the Type 6 entrance may use a coherent region hotspot. Each Type 7 child uses its own RGBA object-alpha Map; its collider may not include the container interior, neighboring children, or empty space between disconnected parts.

An `envir` row is never legal as a contained child because it does not enter inventory and belongs to the base-scene observation route.

## Shared contract and tools

Read the container-specific sections of the existing [evidence delivery contract](../ndc-scene-evidence-placement/references/delivery-contract.md) before execution: Runtime asset roles, Required staged files, Secondary-menu container manifest, Compatibility text, Alpha rules, and When reconstruction is intentionally impossible. That file remains the schema source of truth; do not copy or fork it into this skill.

Use the existing [secondary_prop_border.py](../ndc-scene-evidence-placement/scripts/secondary_prop_border.py) for the final Type 7 border. Do not move, duplicate, or replace the shared script. Use `$ndc-evidence-detail-art` for each child's Big and Icon after its route and `itemType` are fixed.

For compatibility with existing staged packages, the manifest may continue to record `deliveryClass: container-state`; this is the delivery-schema name for the parent route `container-click`, not a second routing decision.

## Execution workflow

### 1. Export the Type 6 entrance

Export `prop_<container>1.png` as a pixel-exact rectangle from the accepted native-resolution base scene.

- Include the complete closed or normal-state container and only enough stable edge pixels for a reliable overlay.
- Record `x1`, `y1`, `z1`, width, height, and half-open crop rectangle.
- Derive `Position` from the crop's top-left pixel in the full-scene, top-left-origin, Y-down coordinate system.
- Pasting the crop at `(x1, y1)` over the matching source scene must reproduce the accepted closed state pixel-for-pixel.
- Do not regenerate Type 6 art, estimate coordinates, or transcribe values from a preview.
- This is the sole standard case where an opaque/coherent region hotspot is allowed. The region must still be limited to the actual container or opening surface; do not expand it to the whole table, wall, or surrounding furniture group.

### 2. Author the independent Type 7 view

Author `prop_<container>2_inner.png` as an opaque open-container view, normally top-down or near-top-down.

- Preserve the Type 6 container's material, color, construction, wear, handedness, handle placement, and opening direction.
- Keep the full container and its interior legible. Every child must be visibly distinct, fully contained, and separable at gameplay size.
- Keep Map-level information low: the player can locate and identify a child, but exact text, dates, serial numbers, and puzzle detail remain in its Big.
- Do not use a magnified Type 6 crop, an empty interior, or generic paper/card piles as a substitute for the approved child list.
- Finish generation, cleanup, and final sizing before adding the border. Never resize or crop the bordered result.

### 3. Add and verify the locked Type 7 border

Add a rectangular, fully opaque white border exactly `12 px` wide on all four sides. It is not a silhouette stroke or transparent padding. The runtime image must be exactly `24 px` wider and taller than the approved inner image, and the inner pixels must remain identical.

From the repository root, run:

```text
<workspace-python> .codex/skills/ndc-scene-evidence-placement/scripts/secondary_prop_border.py add \
  --input <approved-final-size-prop_container2_inner.png> \
  --output <prop_container2.png> \
  --border 12

<workspace-python> .codex/skills/ndc-scene-evidence-placement/scripts/secondary_prop_border.py verify \
  --input <approved-final-size-prop_container2_inner.png> \
  --output <prop_container2.png> \
  --border 12
```

Border verification must pass. Repair the inner source or regenerate the bordered output when it fails; never paint over the result or waive the report.

### 4. Derive the independent Type 7 position

Propose a full-scene Type 7 top-left from the final bordered dimensions:

```text
x2 = round(x1 + width1 / 2 - width2 / 2) + nudgeX
y2 = round(y1 + height1 / 2 - height2 / 2) + nudgeY
```

Use only the smallest justified nudge for opening direction, scene bounds, physical attachment, or nearby occlusion. Record `x2`, `y2`, `z2`, final bordered width and height, `nudgeX`, `nudgeY`, and center offset. Verify the complete Type 7 rectangle remains inside the base-scene canvas.

Identical Type 6 and Type 7 numeric coordinates are acceptable only if they result from separate calculations and the manifest states why; numerical equality is not permission to copy the values.

### 5. Export every child object-alpha Map and calculate its Position

For every ID in Type 7 `ActionParam`:

1. Create one local RGBA layer for the child in the accepted final bordered Type 7 image. Its alpha contains only that child object/condition; stable interior background and neighboring children remain transparent.
2. Derive a half-open local crop rectangle from the child's nonzero-alpha bounds plus small transparent padding, then export that RGBA crop as the child's no-suffix Map PNG.
3. Convert its local origin to the full-scene coordinate system:

```text
childX = x2 + localCropLeft
childY = y2 + localCropTop
```

4. Write `[childX, childY, childZ]` to the child's `Position`.
5. Verify the crop is completely inside Type 7 and alpha-composites back pixel-for-pixel at the recorded local and full-scene positions.
6. Produce the child's type-appropriate Big and `130 x 130` Icon through `$ndc-evidence-detail-art`; a Type 7 image never substitutes for either asset.

Generate `hotspot_overlay.png` from every child Map alpha at the current Unity `0.5` threshold. Disconnected parts of one record may remain disconnected. Reject the child when its hotspot includes the container panel, drawer bottom, another child, or an opaque rectangular bridge. In a multi-child view, threshold all child alphas and prove pairwise hotspot intersection is zero.

Do not leave a child's Map or `Position` empty, and do not use Type 7's top-left directly as every child's position.

### 6. Draft configuration and stage the package

Stage, without synchronizing to Unity:

- `prop_<container>1.png` and its exact crop/Position record;
- retained `prop_<container>2_inner.png` recovery source;
- final bordered `prop_<container>2.png` and its independently derived Position;
- Type 6 and Type 7 ItemStaticData draft rows;
- every child Map, Position, Big, Icon, ItemStaticData draft row, and verification artifact;
- `XYposition.txt` with separate ASCII lines for Type 6 and Type 7;
- `container_delivery_manifest.json`, configuration-chain proof, coordinate overlay, and `container_delivery_verification.json`.

The manifest is the source of truth. Keep Type 6, Type 7, and every child as separate records; do not flatten the chain into a single pickup.

The shared script verifies only the Type 7 border; there is currently no single machine checker for the entire container manifest and runtime chain. `container_delivery_verification.json` must distinguish machine checks from manual structural checks and cite the artifact or configuration evidence for every PASS. Never describe the whole chain as machine-verified solely because the border report passes.

## Delivery gate

Report `PASS` only when all checks below pass:

- Type 6 is an exact accepted-scene crop and reconstructs its scene state pixel-for-pixel.
- Only Type 6 is bound by `SceneConfig`.
- Type 6 `ActionParam` resolves to exactly the one Type 7 ID.
- Type 7 `ActionParam` resolves to exactly the approved clickable child list.
- Type 6 and Type 7 each have separately derived full-scene coordinates.
- Type 7 remains inside the scene canvas, has the exact opaque `12 px` white border, and passes shared-script verification.
- Every child is an `item` or `clue` and has a Map, full-scene `Position`, Big, Icon, and pixel-alignment proof.
- Type 6 is the only coherent region hotspot; every child hotspot follows that child's reviewed alpha shape and has zero overlap with sibling hotspots.
- No `envir` child or automatic multi-item grant has entered the package.
- All staged files, configuration rows, IDs, paths, coordinate records, and hashes agree with the manifest.

If any check fails, return `BLOCKED` with the failed link in `Type 6 -> Type 7 -> child Map/Position -> child Big/Icon`. Never present a partial chain as Unity-ready and never synchronize files as part of this subskill.
