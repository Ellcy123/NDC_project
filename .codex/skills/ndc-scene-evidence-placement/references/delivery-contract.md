# NDC evidence delivery contract

Use this contract for scene-local clickable evidence packages. It records the conventions observed in `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE` and the current Unity loading code.

## Runtime asset roles

| Output | ItemStaticData field | Meaning |
|---|---|---|
| `<map-stem>.png` | `mapSpritePath` | Preferred: tight RGBA canvas whose Alpha follows the target prop's visible contour and drives its Sprite Physics Shape. Legacy compatibility: exact rectangular scene crop. |
| `<detail-stem>.png` | `desSpritePath` | Standalone evidence/detail view. Ordinary transparent Bigs use one final frame only: `571 x 1000`, `818 x 818`, or `1000 x 571`; clue Polaroids stay `620 x 620`. |
| `<icon-stem>.png` | `iconPath` | Optional runtime item selection/inventory Icon. When present, it is `130 x 130` RGBA with all prop and shadow pixels inside the fixed `115 x 115` safe rectangle. |
| `prop_<container>1.png` | Type 6 `mapSpritePath` | Preferred: scene-exact irregular RGBA Map following the visible closed/normal container plus attributable shadow. Only this entrance state is bound by `SceneConfig`; rectangular crops are compatibility fallbacks only. |
| `prop_<container>2.png` | Type 7 `mapSpritePath` | Direct-generated first-person open-container view whose observation angle follows the real container height, positioned near Type 6 and finished with a 12-pixel opaque white rectangular border. |
| delivery folder | `folderPath` | Path below `Art/Scene/EVIDENCE`, normally `EPIxx\<scene-folder>`. |
| `x, y, z` | `Position` | Map-crop top-left pixel coordinate plus Unity sorting value. |

## Acquisition coverage contract

Every evidence-art batch starts with a coverage ledger. This is required even when existing ItemStaticData rows already contain Big/Icon paths, because those paths do not prove that an exploration pickup is present in the scene.

| Actual acquisition event | Required visible/runtime coverage |
|---|---|
| Click item in base exploration scene | Item Map + full-scene `Position` + Big + configured Icon |
| Open Type 6/Type 7 container, then click item | Type 6 Map/Position + Type 7 Map/Position + child item Map/full-scene `Position` + child Big + configured Icon |
| Click environmental observation that does not enter inventory | Visible background/state prop + real scene Map/`Position` + Big; omit Icon |
| Automatic dialogue or Expose grant | Big + configured Icon; add a conditional/handover state when the item is visibly presented in the scene |
| Automatic minigame or analysis result | Big + configured Icon when configured; no Map only when there is no world-space locate/click step |
| Unlock cache, then player searches it | Route by the post-unlock interaction; use the full container chain when contents remain clickable |

The ledger must cite the matching state and runtime rows. Empty or placeholder `mapSpritePath`/`Position` values are failures, not evidence that an item is `detail-only`.

Current Sprite import convention is single Sprite, center pivot, 100 pixels per unit. `SceneMgr.ConvertMapPosToWorldPos` reads `Position` as a top-left, Y-down map coordinate and uses the map Sprite rectangle to calculate the center.

## Engineering working-stage files

The following is the full verification/recovery package kept under the work-process or engineering staging directory. It is not the user-facing formal image-asset folder.

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

The engineering staged package does not include Unity `.meta` files. Unity creates or preserves those during the approved synchronization step. `<icon-stem>.png` is required when `iconPath` is present; it is omitted completely when the contract deliberately uses no Icon. A production Icon package also retains its matching `*_verification.json` report as a recovery input in this engineering package.

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

## Formal image-asset folders

After all applicable gates pass, build the formal image-asset folder containing only accepted/final PNG image assets and one ASCII `XYposition.txt`. For a complete scene-prop or container-chain delivery, its required shape is:

```text
<scene-id>_道具放入预览图.png
prop_<container>1.png
prop_<container>2.png
<contained-or-direct-map-stem>.png
<contained-or-direct-detail-stem>.png
<contained-or-direct-icon-stem>.png        # when iconPath is configured
<additional-accepted-environment-or-state-image>.png
XYposition.txt
```

Repeat container and item rows for every acquisition-coverage entry. Omit a role only when the contract explicitly proves it does not apply. The scene placement preview is the accepted full scene with the delivered props/states represented; it is not a position overlay or checkerboard review image.

Transfer the complete formal image-asset folder directly after all applicable gates pass, including a process-package `final_visual_record_presence_gate.json` that enumerates every executed production stage and every required formal PNG, hash-matches each to a passing per-stage visual-review record, and reports `FINAL_VISUAL_RECORD_PRESENCE_GATE: PASS`. Do not wait for a separate user-review approval. Missing, stale, incomplete, or failed visual-review evidence blocks transfer even when technical verification passes. Keep `ItemStaticData.patch.json`, manifests, verification reports, position/hotspot overlays, masks, scripts, debug previews, rejected versions, superseded versions, and recovery-only sources in the engineering/work-process package. Do not narrow a complete formal package to the images changed in the latest revision. Do not merge a replacement package with a prior formal directory unless every pre-existing file is independently verified for the new package.

Validate a new production folder with `scripts/validate_formal_release.py --folder <formal-folder> --release-contract <process-contract.json>`. The legacy `validate_formal_package.py` manual file-list check cannot establish delivery-class correctness, Map-to-coordinate hash binding, or active-replica consistency and is not a production gate.

### Semantic formal-release contract

Keep this contract in the work-process package, never in the formal image folder:

```json
{
  "version": 1,
  "kind": "ndc-formal-release-contract",
  "scenePreview": "SC4002_道具放入预览图.png",
  "additionalStateImages": [],
  "records": [
    {
      "recordId": "4112",
      "deliveryClass": "scene-pickup",
      "classificationReason": "Player clicks the item in the base exploration scene",
      "sourceReferences": [
        "剧情设计/Unit4/state/loop1_state.yaml",
        "ItemStaticData:4112"
      ],
      "iconPolicy": "required",
      "assets": {
        "map": "SC4002_item_4112.png",
        "big": "SC4002_item_4112_big.png",
        "icon": "SC4002_item_4112_icon.png"
      },
      "positions": [
        {
          "role": "map",
          "stem": "SC4002_item_4112",
          "x": 604,
          "y": 550,
          "assetSha256": "<64-lowercase-hex>",
          "acceptedParentImage": "<accepted-full-native-parent.png>",
          "acceptedParentSha256": "<64-lowercase-hex>"
        }
      ]
    }
  ],
  "artifactSha256": {
    "SC4002_道具放入预览图.png": "<64-lowercase-hex>",
    "SC4002_item_4112.png": "<64-lowercase-hex>",
    "SC4002_item_4112_big.png": "<64-lowercase-hex>",
    "SC4002_item_4112_icon.png": "<64-lowercase-hex>",
    "XYposition.txt": "<64-lowercase-hex>"
  },
  "replicaScanRoots": [
    "<scene-work-process-root>",
    "<scene-formal-parent-root>"
  ]
}
```

The contract is the executable acquisition coverage ledger for release:

- `scene-pickup`: require `map`, `big`, Map `Position`, and `icon` when `iconPolicy` is `required`.
- `environment`: require `map`, Map `Position`, and `big`; `iconPolicy` must be `omit`, and an Icon is forbidden.
- `detail-only`: require `big`, configured Icon, and no Map/Position.
- `minigame-only`: require empty evidence `assets` and `positions`; route its gameplay art outside this evidence formal folder.
- `container-state`: require `type6` and `type7`, independent positions for both, explicit `containerGrantMode`, and every child as a nested classified record.

Every record must include `classificationReason` and authoritative `sourceReferences`. `artifactSha256` must cover exactly every formal PNG plus `XYposition.txt`. Every coordinate entry repeats the current Map SHA-256 so a crop/Alpha/canvas revision automatically invalidates its old coordinate. Every `map` and `type6` coordinate also binds `acceptedParentImage` and `acceptedParentSha256`; the production validator must load that exact parent and prove that all Alpha-positive RGB matches it at `x,y`, all Alpha-zero RGB is zero, the sprite is RGBA, and its canvas lies within the parent. Matching Alpha or matching dimensions cannot excuse visible RGB drift, white/black fill blocks, painted repairs, stale review RGB, or another-parent pixels. `replicaScanRoots` must cover the scene's work-process and formal roots. The validator ignores only path segments explicitly marked history, legacy, rejected, or superseded; any other staging, candidate, or formal copy containing the same stem is active and must match both Map hash and `x,y`.

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

A Map PNG and its coordinate are one atomic record. Any Alpha, crop, padding, exclusion, or canvas change invalidates the old `Position`, release-contract hash binding, formal PNG, and every non-history `XYposition.txt` copy. Recompute the top-left from the new final Alpha canvas and update all active staging/candidate/formal packages together. Before release, scan every declared scene work-process and formal root; a matching stem with an old coordinate, missing sibling Map, or different Map hash is a hard failure. Clearly marked history/rejected/superseded paths remain recoverable and are excluded from active-replica enforcement.

## Naming rules

- Reuse stems already present in the Unit ItemStaticData draft when available.
- File extensions remain `.png`; ItemStaticData path fields omit the extension.
- A map, detail, and icon trio for one item must share the same base stem.
- A secondary-menu pair uses the established `prop_<container>1` and `prop_<container>2` naming convention unless an approved runtime stem already exists.
- Do not rename an approved runtime asset during packaging merely to improve style.
- Use one evidence folder per scene or existing scene-folder convention.

## Map silhouette and hotspot rules

- A PNG canvas is rectangular, but the preferred visible and clickable region is not. Trace the target prop's current visible outer contour and let Sprite Physics Shape plus `PolygonCollider2D` carry that outline into runtime interaction.
- Detect the selected prop together with every visible region of its own contact/cast shadow. Start from the accepted full native parent, not an inherited object crop. Maintain independent `BODY_MUST_COVER`, repeatable `SHADOW_MUST_COVER`, and repeatable `FOREGROUND_MUST_EXCLUDE` masks. For oblique paper, receipts, books, folders, and similar planar objects, the body includes the top face, every visible side/edge-thickness plane, curled or lifted edge, lower edge, and attributable shadow; similarity to supporting paper is not a reason to keep only the high-contrast top face. Before locating any extrema, build a deliberately loose source-resolution working selection around the entire body-plus-shadow union. This is an inspection range, not the final hotspot. Run `PRE_EXTREMA_VISUAL_COVERAGE_GATE` on the accepted parent at whole-image `100%` and local nearest-neighbor `200%` or greater. The complete body, all visible planes, low-contrast edges, and full attributable shadow must remain inside the working selection with visible breathing room and must not touch or cross its boundary. Save the reviewed overlay. `FAIL` or `NOT_CHECKED` blocks extrema registration.
- The semantic target may consist of multiple disconnected Alpha islands. A foreground occluder removes only the pixels it actually covers; preserve visible target or shadow that reappears beyond it. Never keep only the largest connected component, require artificial connectivity, or discard a far-side shadow continuation because an intervening chair leg, rim, or other object splits it.
- Only after the pre-extrema gate passes, independently register the visible semantic union's `top`, `bottom`, `left`, and `right` extreme points. Record whether each point belongs to the body, contact shadow, or cast shadow, and build the tight outer rectangle from all islands. A rectangle derived only from an inherited crop, the body, the largest component, or one proposed polygon is not valid evidence of completeness.
- The undilated body-plus-shadow union and the final post-exclusion Alpha must both select all four registered semantic extreme points. If subtraction removes one, the point was not actually visible and must be corrected before export. Missing any one point fails the Map even if its own Alpha bounds, hashes, and parent-pixel checks pass.
- Visually review the undilated base-contour overlay and validate the four points against that union, then expand it outward by a visually selected `2` or `3` Photoshop pixels. Use `5px` only as an asset-specific trial with untinted parent/edge evidence, not a global default. The base must already be complete; expansion is a safety margin for antialiasing, low-contrast thickness, and shadow softness, not permission to repair an incomplete contour or retain unrelated background/support pixels.
- After expansion, subtract every foreground object, container rim, or other layer that visibly sits in front of the target. Foreground exclusion has priority over the chosen margin only on the pixels it covers. Record and verify these negative regions separately, then recompute the final crop from all surviving Alpha islands.
- Visually review the final post-exclusion contour in an untinted parent-image overlay, Alpha-only image, checkerboard export, and transparent export. Approval requires the complete prop and every attributable shadow island to remain selected while every separable foreground occluder remains excluded. Alpha bounds, hashes, polygon bounds, connected-component counts, and internally consistent masks are technical evidence only and cannot set a visual gate to `PASS`.
- Include the selected prop plus every visually attributable contact/cast-shadow region, including visible continuation beyond an occluder. Exclude ordinary background, container rims, supporting piles, and unrelated objects above or across the prop whenever they can be separated without inventing hidden pixels.
- Never reconstruct or paint occluded portions merely to obtain a closed silhouette. Follow the actually visible boundary.
- Use a full rectangular crop only for an audited legacy asset or a proven runtime/import limitation. A Type 6 entrance follows the same irregular rule unless that exception is explicitly recorded.
- If a user- or artist-approved same-scale RGBA reference has the correct final Alpha but its visible RGB is not byte-identical to the accepted parent, do not copy its RGB and do not reject its reviewed contour solely for that mismatch. Use `irregular_map.py rebuild-reference` to register the reference uniquely against the accepted full native parent, reuse only its already-expanded/post-exclusion Alpha, rebuild all visible RGB from the parent, zero transparent RGB, and recompute the tight canvas and `Position`. Do not apply any second expansion to an authored final Alpha. An ambiguous or low-confidence translation blocks production, and the command's technical pass cannot substitute for the full visual gates.

## Alpha rules

- Map Sprite: preferred output is RGBA. Alpha-positive RGB must equal the accepted parent image at the registered coordinate; Alpha 0 RGB must be zero. Legacy rectangular Maps preserve the accepted scene mode and exact pixels.
- Detail: an ordinary physical Big is RGBA and is exported once from a high-resolution semantic master to exactly one final frame. The `2560 x 1600` guide is never a runtime file. A clue Polaroid is exactly `620 x 620`; its locked template is never scaled or rotated.
- Icon: exactly `130 x 130` RGBA. Every visible prop and shadow pixel must remain inside `[7,7,122,122)`, so the alpha bounding box is no larger than `115 x 115`; this is a ceiling, not a fill target. Fully transparent pixels must have RGB zero. Use a `1040 x 1040` master with content inside `[60,60,980,980)` and perform one premultiplied-alpha LANCZOS downsample. Never silently derive an Icon from Big during production packaging.
- Type 6 container entrance: export RGBA; Alpha-positive RGB must equal the accepted scene at its recorded top-left, Alpha 0 RGB must be zero, and the final Alpha must follow the complete visible actionable container unit plus attributable shadow after foreground exclusions.
- Type 7 borderless source: require an opaque RGB or RGBA image at final inner dimensions.
- Type 7 runtime image: export RGBA with a fully opaque `RGBA(255,255,255,255)` rectangular border exactly 12 pixels wide on all four sides. The final dimensions are the inner dimensions plus 24 pixels on each axis. Do not resize after adding the border.

## Scene reconstruction invariant

For a normal scene pickup, let `S` be the approved source scene, `F` the accepted scene with item, `C` the map crop, and `(x, y)` its coordinate. Delivery requires:

1. `S` and `F` have identical size and mode.
2. All `S != F` pixels are inside the approved authorization mask.
3. Every changed pixel is inside `C`'s rectangle. Unchanged portions of the larger authorization workspace may remain outside it.
4. For a rectangular Map, `C == F.crop(rect)` pixel-for-pixel. For an irregular Map, every Alpha-positive RGB pixel in `C` equals the corresponding pixel in `F`, Alpha 0 RGB is zero, and the contour includes every changed pixel required by the accepted state.
5. Pasting the rectangular Map or alpha-compositing the irregular Map onto `S` at `(x, y)` produces `F` pixel-for-pixel.

For new placement jobs with both `S` and `F`, derive `rect` from the actual changed-pixel bounding box plus at least `32px` of stable local background. Fall back to the authorization-mask bounding box only when `S` is unavailable. Manual `--map-rect` input is reserved for audited legacy/baked-prop extraction.

This proves that Unity can reconstruct the accepted scene state from the background plus runtime item Sprite.

## When reconstruction is intentionally impossible

When Type 6 is a newly inserted or changeable scene layer, it must satisfy the normal reconstruction invariant through irregular alpha compositing. When the container is already baked into the background and Type 6 is only its interaction hotspot, verify scene-exact parent-pixel alignment, Alpha rules, four-extrema coverage, expansion/exclusion evidence, and semantic contour completeness; compositing identical pixels over the same background is not a completeness test. Type 7 is an independently authored open view and is not expected to reconstruct the closed scene. Instead, verify that:

1. Its material and structure match Type 6.
2. Its final bordered rectangle remains inside the source scene canvas at its recorded top-left position.
3. Its center is anchored near Type 6, or the manifest explains the scene-specific nudge.
4. Its final dimensions equal the borderless source dimensions plus 24 pixels on both axes.
5. All four border strips are exactly 12 pixels of opaque white.
6. Its interior equals the approved borderless source pixel-for-pixel.
7. The Type 6 -> Type 7 -> contained-item configuration chain is complete, and only Type 6 is bound by `SceneConfig`.
8. Every contained exploration item has a non-empty `mapSpritePath` and full-scene `Position`; its local canvas lies inside Type 7, its Alpha-positive pixels align pixel-for-pixel at that position, and its Sprite Physics Shape excludes transparent and unrelated occluding content.

## Art authorship and provenance

The runtime image's semantic content, including every required readable prop title, date, number, ledger entry, stamp wording, signature wording, and body text, must originate in one approved complete raster master, not in procedural drawing code. The delivery manifest records that complete semantic master path and SHA-256 plus its text-legibility visual proof.

Code may transform and verify approved art. It may crop, mask, composite already-approved non-text art, rotate, resize, perspective-map, handle alpha, add the locked Polaroid frame or Type 7 border, write debug overlays, and calculate coordinates. It must not place, correct, redraw, or composite readable prop text over a master.

Code must not draw the final prop body, blank document, ruled table, card stack, container, furniture, texture, wear, lighting, handwriting, scene background, or condition-state composition. Test fixtures and non-runtime debug graphics are exempt. A code-drawn mockup cannot be promoted to `final_assets` merely because its dimensions and paths pass.

Other overlapping props, animated objects, or multi-layer occlusion setups that cannot be represented by these contracts must describe their required layer/state composition and block ordinary scene-pickup delivery. Do not weaken an invariant silently.

## Big, Icon, and clue-Polaroid production contract

The exact frame coordinates, safe rectangles, explicit `+10/-10` rotation rule, `1040 -> 130` Icon pipeline, canonical `620 x 620` Polaroid mask, deterministic commands, and visual review checklist are defined in [detail-icon-production.md](detail-icon-production.md). Treat that reference and `scripts/evidence_art.py` as the executable art-size contract.
