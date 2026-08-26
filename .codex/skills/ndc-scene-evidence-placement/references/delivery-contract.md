# NDC evidence delivery contract

Use this contract for scene-local clickable evidence packages. It records the conventions observed in `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE` and the current Unity loading code.

## Runtime asset roles

| Output | ItemStaticData field | Meaning |
|---|---|---|
| `<map-stem>.png` | `mapSpritePath` | Exact scene-local crop placed back over the scene. It may include local background and contact shadow. It is not assumed to be transparent. |
| `<detail-stem>.png` | `desSpritePath` | Standalone evidence/detail view. Ordinary transparent Bigs use one final frame only: `571 x 1000`, `818 x 818`, or `1000 x 571`; clue Polaroids stay `620 x 620`. |
| `<icon-stem>.png` | `iconPath` | Optional runtime item selection/inventory Icon. When present, it is `130 x 130` RGBA with all prop and shadow pixels inside the fixed `115 x 115` safe rectangle. |
| `prop_<container>1.png` | Type 6 `mapSpritePath` | Pixel-exact closed/normal-state screenshot from the accepted scene. Only this entrance state is bound by `SceneConfig`. |
| `prop_<container>2.png` | Type 7 `mapSpritePath` | Independently authored top-down or near-top-down open-container view, positioned near Type 6 and finished with a 12-pixel opaque white rectangular border. |
| delivery folder | `folderPath` | Path below `Art/Scene/EVIDENCE`, normally `EPIxx\<scene-folder>`. |
| `x, y, z` | `Position` | Map-crop top-left pixel coordinate plus Unity sorting value. |

## Acquisition coverage contract

Every evidence-art batch starts with a coverage ledger. This is required even when existing ItemStaticData rows already contain Big/Icon paths, because those paths do not prove that an exploration pickup is present in the scene.

| Actual acquisition event | Required visible/runtime coverage |
|---|---|
| Click item in base exploration scene | Item Map + full-scene `Position` + Big + configured Icon |
| Open Type 6/Type 7 container, then click item | Type 6 Map/Position + Type 7 Map/Position + child item Map/full-scene `Position` + child Big + configured Icon |
| Click environmental observation that does not enter inventory | Visible background/state prop plus a real scene hotspot/Map contract; do not deliver Big/Icon as its only presence |
| Automatic dialogue or Expose grant | Big + configured Icon; add a conditional/handover state when the item is visibly presented in the scene |
| Automatic minigame or analysis result | Big + configured Icon when configured; no Map only when there is no world-space locate/click step |
| Unlock cache, then player searches it | Route by the post-unlock interaction; use the full container chain when contents remain clickable |

The ledger must cite the matching state and runtime rows. Empty or placeholder `mapSpritePath`/`Position` values are failures, not evidence that an item is `detail-only`.

Current Sprite import convention is single Sprite, center pivot, 100 pixels per unit. `SceneMgr.ConvertMapPosToWorldPos` reads `Position` as a top-left, Y-down map coordinate and uses the map Sprite rectangle to calculate the center.

## Required staged files

```text
delivery/
  scene_with_item.png
  <map-stem>.png
  <detail-stem>.png
  <icon-stem>.png
  XYposition.txt
  ItemStaticData.patch.json
  position_overlay.png
  delivery_manifest.json
  delivery_verification.json
```

The staged package does not include Unity `.meta` files. Unity creates or preserves those during the approved synchronization step. `<icon-stem>.png` is required when `iconPath` is present; it is omitted completely when the contract deliberately uses no Icon. A production Icon package also retains its matching `*_verification.json` report as a recovery input.

For a `container-state`, stage this pair-oriented package instead:

```text
delivery/
  prop_<container>1.png
  prop_<container>2_inner.png
  prop_<container>2.png
  <contained-map-stem>.png
  <contained-detail-stem>.png
  <contained-icon-stem>.png              # when iconPath is configured
  <contained-icon-verification>.json     # when iconPath is configured
  XYposition.txt
  ItemStaticData.patch.json
  container_position_overlay.png
  container_delivery_manifest.json
  container_delivery_verification.json
```

Repeat the contained-item files for every child ID. `prop_<container>2_inner.png` is a recovery and verification source. Do not copy it into the Unity EVIDENCE runtime folder.

## Delivery manifest core

```json
{
  "version": 2,
  "coordinateSystem": {
    "origin": "top-left",
    "xAxis": "right",
    "yAxis": "down",
    "unit": "pixel",
    "sceneWidth": 3348,
    "sceneHeight": 1600
  },
  "item": {
    "id": "4317",
    "sceneId": "4025",
    "folderPath": "EPI04\\u4_exp_court_dispatch_night"
  },
  "mapCrop": {
    "x": 1248,
    "y": 736,
    "width": 164,
    "height": 96,
    "rect": [1248, 736, 1412, 832]
  },
  "unityDraft": {
    "mapSpritePath": "SC4025_item_4317",
    "desSpritePath": "SC4025_item_4317_big",
    "iconPath": "SC4025_item_4317_icon",
    "Position": ["1248", "736", "-3"]
  }
}
```

Numbers above illustrate the schema only. Actual coordinates must be derived from the accepted full-resolution scene.

## Secondary-menu container manifest

Use a separate manifest for a Type 6 to Type 7 container pair. This example uses the audited U1 `1843 -> 1844 -> 1409` drawer chain to make the contained-item coordinate relationship concrete:

```json
{
  "version": 1,
  "deliveryClass": "container-state",
  "coordinateSystem": {
    "origin": "top-left",
    "xAxis": "right",
    "yAxis": "down",
    "unit": "pixel",
    "sceneWidth": 3348,
    "sceneHeight": 1600
  },
  "runtimeChain": {
    "closedItemId": "1843",
    "closedItemType": "6",
    "closedActionParam": "1844",
    "openItemId": "1844",
    "openItemType": "7",
    "openActionParam": "1409",
    "containedItemIds": ["1409"],
    "sceneConfigBinds": ["1843"]
  },
  "closedState": {
    "image": "prop_Bottom drawer of the low cabinet_1.png",
    "x": 806,
    "y": 1193,
    "z": -1,
    "width": 160,
    "height": 120,
    "rect": [806, 1193, 966, 1313],
    "source": "accepted-native-resolution-scene"
  },
  "openState": {
    "innerImage": "prop_Bottom drawer of the low cabinet_2_inner.png",
    "image": "prop_Bottom drawer of the low cabinet_2.png",
    "x": 709,
    "y": 1029,
    "z": -1,
    "width": 392,
    "height": 392,
    "anchor": {
      "strategy": "closed-center",
      "nudgeX": 19,
      "nudgeY": -28,
      "centerOffsetX": 19,
      "centerOffsetY": -28
    },
    "border": {
      "kind": "rectangular",
      "pixels": 12,
      "rgba": [255, 255, 255, 255],
      "appliedAfterFinalResize": true
    }
  },
  "containedItems": [
    {
      "itemId": "1409",
      "mapSpritePath": "SC9002_item_07",
      "localCropRect": [122, 98, 290, 250],
      "Position": ["831", "1127", "-1"],
      "desSpritePath": "SC9002_item_07_big",
      "iconPath": "SC9002_item_07_icon",
      "alignmentRule": "child Position = openState Position + local crop origin"
    }
  ]
}
```

The U1 numbers document an existing runtime example; do not copy them into another scene. Here `831 = 709 + 122` and `1127 = 1029 + 98`, proving that the contained item's Map has its own full-scene `Position`. Derive every new pair and child coordinate from its accepted full-resolution imagery.

For center anchoring, calculate the unnudged Type 7 top-left from final bordered dimensions:

```text
x2 = round(x1 + width1 / 2 - width2 / 2) + nudgeX
y2 = round(y1 + height1 / 2 - height2 / 2) + nudgeY
```

The manifest records the final result and the nudge. `nudgeX` and `nudgeY` are also the Type 7 center offset relative to Type 6 when the formula is used exactly.

## Compatibility text

Write one ASCII line per staged item:

```text
SC4025_item_4317 1248,736
```

For a container pair, write both states on separate lines:

```text
prop_Low cabinet drawer_1 1551,680
prop_Low cabinet drawer_2 1436,560
```

The structured manifest is the source of truth. Do not emit full-width commas or decorative brackets in new output.

## Naming rules

- Reuse stems already present in the Unit ItemStaticData draft when available.
- File extensions remain `.png`; ItemStaticData path fields omit the extension.
- A map, detail, and icon trio for one item must share the same base stem.
- A secondary-menu pair uses the established `prop_<container>1` and `prop_<container>2` naming convention unless an approved runtime stem already exists.
- Do not rename an approved runtime asset during packaging merely to improve style.
- Use one evidence folder per scene or existing scene-folder convention.

## Alpha rules

- Map crop: preserve the accepted scene mode and exact pixels. RGB is valid.
- Detail: an ordinary physical Big is RGBA and is exported once from a high-resolution semantic master to exactly one final frame. The `2560 x 1600` guide is never a runtime file. A clue Polaroid is exactly `620 x 620`; its locked template is never scaled or rotated.
- Icon: exactly `130 x 130` RGBA. Every visible prop and shadow pixel must remain inside `[7,7,122,122)`, so the alpha bounding box is no larger than `115 x 115`; this is a ceiling, not a fill target. Fully transparent pixels must have RGB zero. Use a `1040 x 1040` master with content inside `[60,60,980,980)` and perform one premultiplied-alpha LANCZOS downsample. Never silently derive an Icon from Big during production packaging.
- Type 6 container screenshot: preserve the exact accepted scene pixels and mode.
- Type 7 borderless source: require an opaque RGB or RGBA image at final inner dimensions.
- Type 7 runtime image: export RGBA with a fully opaque `RGBA(255,255,255,255)` rectangular border exactly 12 pixels wide on all four sides. The final dimensions are the inner dimensions plus 24 pixels on each axis. Do not resize after adding the border.

## Scene reconstruction invariant

For a normal scene pickup, let `S` be the approved source scene, `F` the accepted scene with item, `C` the map crop, and `(x, y)` its coordinate. Delivery requires:

1. `S` and `F` have identical size and mode.
2. All `S != F` pixels are inside the approved authorization mask.
3. Every changed pixel is inside `C`'s rectangle. Unchanged portions of the larger authorization workspace may remain outside it.
4. `C == F.crop(rect)` pixel-for-pixel.
5. Pasting `C` onto `S` at `(x, y)` produces `F` pixel-for-pixel.

For new placement jobs with both `S` and `F`, derive `rect` from the actual changed-pixel bounding box plus at least `32px` of stable local background. Fall back to the authorization-mask bounding box only when `S` is unavailable. Manual `--map-rect` input is reserved for audited legacy/baked-prop extraction.

This proves that Unity can reconstruct the accepted scene state from the background plus runtime item Sprite.

## When reconstruction is intentionally impossible

Type 6 must still satisfy the normal scene reconstruction invariant because it is an exact scene screenshot. Type 7 is an independently authored open view and is not expected to reconstruct the closed scene. Instead, verify that:

1. Its material and structure match Type 6.
2. Its final bordered rectangle remains inside the source scene canvas at its recorded top-left position.
3. Its center is anchored near Type 6, or the manifest explains the scene-specific nudge.
4. Its final dimensions equal the borderless source dimensions plus 24 pixels on both axes.
5. All four border strips are exactly 12 pixels of opaque white.
6. Its interior equals the approved borderless source pixel-for-pixel.
7. The Type 6 -> Type 7 -> contained-item configuration chain is complete, and only Type 6 is bound by `SceneConfig`.
8. Every contained exploration item has a non-empty `mapSpritePath` and full-scene `Position`; its local crop lies inside Type 7 and aligns pixel-for-pixel at that position.

## Art authorship and provenance

The runtime image's semantic content must originate in an approved raster master, not in procedural drawing code. The delivery manifest records the semantic master path and SHA-256 plus any separately approved exact-text layer path and SHA-256.

Code may transform and verify approved art. It may crop, mask, composite, rotate, resize, perspective-map, handle alpha, add the locked Polaroid frame or Type 7 border, write debug overlays, and calculate coordinates. It may also place exact approved text over an already illustrated physical master.

Code must not draw the final prop body, blank document, ruled table, card stack, container, furniture, texture, wear, lighting, handwriting, scene background, or condition-state composition. Test fixtures and non-runtime debug graphics are exempt. A code-drawn mockup cannot be promoted to `final_assets` merely because its dimensions and paths pass.

Other overlapping props, animated objects, or multi-layer occlusion setups that cannot be represented by these contracts must describe their required layer/state composition and block ordinary scene-pickup delivery. Do not weaken an invariant silently.

## Big, Icon, and clue-Polaroid production contract

The exact frame coordinates, safe rectangles, explicit `+10/-10` rotation rule, `1040 -> 130` Icon pipeline, canonical `620 x 620` Polaroid mask, deterministic commands, and visual review checklist are defined in [detail-icon-production.md](detail-icon-production.md). Treat that reference and `scripts/evidence_art.py` as the executable art-size contract.
