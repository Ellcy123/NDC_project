# NDC evidence delivery contract

Use this contract for scene-local clickable evidence packages. It records the conventions observed in `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE` and the current Unity loading code.

## Runtime asset roles

| Output | ItemStaticData field | Meaning |
|---|---|---|
| `<map-stem>.png` | `mapSpritePath` | Exact scene-local crop placed back over the scene. It may include local background and contact shadow. It is not assumed to be transparent. |
| `<detail-stem>.png` | `desSpritePath` | Standalone evidence/detail view. Prefer RGBA transparency when the object can be isolated. |
| `<icon-stem>.png` | `iconPath` | Item selection and inventory icon. |
| `prop_<container>1.png` | Type 6 `mapSpritePath` | Pixel-exact closed/normal-state screenshot from the accepted scene. Only this entrance state is bound by `SceneConfig`. |
| `prop_<container>2.png` | Type 7 `mapSpritePath` | Independently authored top-down or near-top-down open-container view, positioned near Type 6 and finished with a 12-pixel opaque white rectangular border. |
| delivery folder | `folderPath` | Path below `Art/Scene/EVIDENCE`, normally `EPIxx\<scene-folder>`. |
| `x, y, z` | `Position` | Map-crop top-left pixel coordinate plus Unity sorting value. |

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

The staged package does not include Unity `.meta` files. Unity creates or preserves those during the approved synchronization step.

For a `container-state`, stage this pair-oriented package instead:

```text
delivery/
  prop_<container>1.png
  prop_<container>2_inner.png
  prop_<container>2.png
  XYposition.txt
  ItemStaticData.patch.json
  container_position_overlay.png
  container_delivery_manifest.json
  container_delivery_verification.json
```

`prop_<container>2_inner.png` is a recovery and verification source. Do not copy it into the Unity EVIDENCE runtime folder.

## Delivery manifest core

```json
{
  "version": 1,
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

Use a separate manifest for a Type 6 to Type 7 container pair. This example uses an audited U1 drawer pair to make the coordinate relationship concrete:

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
    "closedItemId": "1831",
    "closedItemType": "6",
    "closedActionParam": "1832",
    "openItemId": "1832",
    "openItemType": "7",
    "openActionParam": "1304",
    "containedItemIds": ["1304"],
    "sceneConfigBinds": ["1831"]
  },
  "closedState": {
    "image": "prop_Low cabinet drawer_1.png",
    "x": 1551,
    "y": 680,
    "z": -1,
    "width": 156,
    "height": 68,
    "rect": [1551, 680, 1707, 748],
    "source": "accepted-native-resolution-scene"
  },
  "openState": {
    "innerImage": "prop_Low cabinet drawer_2_inner.png",
    "image": "prop_Low cabinet drawer_2.png",
    "x": 1436,
    "y": 560,
    "z": -1,
    "width": 452,
    "height": 360,
    "anchor": {
      "strategy": "closed-center",
      "nudgeX": 33,
      "nudgeY": 26,
      "centerOffsetX": 33,
      "centerOffsetY": 26
    },
    "border": {
      "kind": "rectangular",
      "pixels": 12,
      "rgba": [255, 255, 255, 255],
      "appliedAfterFinalResize": true
    }
  }
}
```

The U1 numbers document an existing runtime example; do not copy them into another scene. Derive every new pair from its accepted full-resolution scene and record both positions independently.

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
- Detail: RGBA is preferred for physical objects; an opaque document page or full-frame photographic evidence may remain RGB/RGBA without forced alpha removal.
- Icon: export RGBA. Derived icons preserve the detail image aspect ratio and do not crop content.
- Type 6 container screenshot: preserve the exact accepted scene pixels and mode.
- Type 7 borderless source: require an opaque RGB or RGBA image at final inner dimensions.
- Type 7 runtime image: export RGBA with a fully opaque `RGBA(255,255,255,255)` rectangular border exactly 12 pixels wide on all four sides. The final dimensions are the inner dimensions plus 24 pixels on each axis. Do not resize after adding the border.

## Scene reconstruction invariant

For a normal scene pickup, let `S` be the approved source scene, `F` the accepted scene with item, `C` the map crop, and `(x, y)` its coordinate. Delivery requires:

1. `S` and `F` have identical size and mode.
2. All `S != F` pixels are inside the approved authorization mask.
3. The authorization mask is inside `C`'s rectangle.
4. `C == F.crop(rect)` pixel-for-pixel.
5. Pasting `C` onto `S` at `(x, y)` produces `F` pixel-for-pixel.

For new placement jobs, derive `rect` from the source-sized authorization-mask bounding box plus a small explicit padding value. Manual `--map-rect` input is reserved for audited legacy/baked-prop extraction.

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

Other overlapping props, animated objects, or multi-layer occlusion setups that cannot be represented by these contracts must describe their required layer/state composition and block ordinary scene-pickup delivery. Do not weaken an invariant silently.
