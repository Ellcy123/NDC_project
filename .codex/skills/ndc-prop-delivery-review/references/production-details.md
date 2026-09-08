# 阶段专业操作细则

本文件从既有道具 Skill 按职责迁移。流程顺序、信息A/B/C、总重试计数和审核复用以本阶段 SKILL.md 及共用批次协议为准。这里的细则只在本阶段执行：提及其他阶段的产物表示交接依赖，不要求提前制作。CLI示例中的 ../ndc-scene-evidence-placement/scripts/ 应解析为同级 Skill 的绝对路径，不依赖终端cwd。

## Unit 4 visual-release firewall

For a Unit 4 all-item audit, a repair prompted by visual feedback, or any promotion from a candidate/history folder into `最终交付`, read [references/unit4-visual-release-firewall.md](../../ndc-scene-evidence-placement/references/unit4-visual-release-firewall.md) before selecting an asset. Its candidate disposition, actual-formal-byte review, geometry/Alpha checks, and replacement-preservation rules are hard release conditions. Do not treat a technically valid Map, a prior PASS record, an accepted master, a correct runtime size, or a pre-existing formal file as a substitute for that current visual decision.

For linked Big/Icon/Map/Type 7 production or any cutout, read [references/asset-identity-and-alpha-review.md](../../ndc-scene-evidence-placement/references/asset-identity-and-alpha-review.md). Before approving separate roles, compare the actual role images together against the identity master; independently inspect missing target material and residual background. A user's rejection invalidates the affected role's reuse approval immediately, even if its bytes and old PASS hash have not changed. Preserve the rejected bytes as evidence, not as approved inputs.

### 5. Package deterministically

First resolve the scene reconstruction mode in [references/delivery-contract.md](../../ndc-scene-evidence-placement/references/delivery-contract.md#scene-reconstruction-invariant). The command below is for a new/changeable Sprite whose target-plus-shadow Map alone reconstructs the accepted state. It is not the route for hiding old-object removal or unrelated background repairs inside a clickable mask. An in-place replacement that changes background outside the semantic Map must retain the accepted scene/state as its parent dependency and use parent-exact hotspot extraction instead; unresolved runtime state dependencies block that package.

For the Map-alone reconstruction mode, run:

```powershell
python ../ndc-scene-evidence-placement/scripts/evidence_delivery.py package `
  --source-scene <approved-scene-before-item.png> `
  --final-scene <approved-scene-with-item.png> `
  --authorization-mask <source-sized-item-mask.png> `
  --map-shape-mask <source-sized-visible-prop-silhouette.png> `
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
  --output-dir <work-process-scene-job\delivery>
```

Use `--cutout-mask` instead of `--detail-image` only when the standalone image must be extracted from the accepted final scene. Production packaging requires an independently approved `130 x 130` RGBA Icon and its passing report from `evidence_art.py verify-icon` or `finalize-icon`. If the current runtime record intentionally has no `iconPath`, use `--omit-icon` and omit all Icon arguments. The package command must never silently shrink a Big or detail image into an Icon. `--allow-legacy-derived-icon` exists only to rebuild an audited old package and must be explicit in its manifest.

When both the source and accepted final scene are supplied, the script derives the map rectangle and `(x, y)` from the actual changed-pixel bounds, then adds `--map-padding` (default `32`). This deliberately decouples the runtime Map crop from the much larger authorization workspace. When no source is available, it falls back to the authorization-mask bounds. `--map-rect left top right bottom` is only an audited compatibility override for pre-existing baked props. The rectangle is top-left based and half-open. It must contain every changed pixel and all clickable visual content.

For a preferred irregular Map in Map-alone reconstruction mode, provide `--map-shape-mask` as a full-parent-size silhouette mask. The packager preserves exact accepted pixels only inside that mask and exports RGBA with zero RGB under Alpha 0. The mask must cover every changed pixel needed to reconstruct the accepted state and may contain multiple disconnected target islands; if this requires unrelated background, this mode is invalid rather than permission to enlarge the hotspot. For accepted-parent hotspots (including in-place replacements with a separately retained scene/state dependency), Type 7 child Maps, or when only one accepted parent image exists, first save and visually approve a loose working-selection overlay under `PRE_EXTREMA_VISUAL_COVERAGE_GATE`; only then record the four visible extreme points of the verified prop-plus-shadow union and use `scripts/irregular_map.py build --parent <type7-or-scene.png> --polygon "x,y;x,y;..." --shadow-polygon "x,y;x,y;..." --extreme-points "top:x,y;bottom:x,y;left:x,y;right:x,y" --expand 3 --exclude-polygon "x,y;x,y;..." --output <map.png> --report <verification.json> --overlay <review.png>`. Repeat `--shadow-polygon` for every disconnected visible shadow region and `--exclude-polygon` for each foreground occluder. The command validates extrema against the undilated body-plus-shadow union, applies the explicitly chosen expansion (the example uses 3px, not a universal value), subtracts only the declared foreground regions, validates the declared semantic extrema again on the final post-exclusion Alpha, and reports every surviving connected component without rejecting multi-island masks. These are technical checks; review the base-contour overlay, Alpha-only/checkerboard exports, and the final post-exclusion overlay visually before approval. Convert the final parent-local top-left to full-scene `Position` before registration. In the semantic release contract, bind each `map`/`type6` position to `acceptedParentImage` and `acceptedParentSha256`; the production validator must then prove parent bounds, RGBA mode, exact Alpha-positive parent RGB, and zero RGB under Alpha 0. Equal Alpha, canvas, or position alone is never sufficient: any visible white/black block, stale review RGB, painted repair, or another-parent pixel is a release failure.

### 6. Verify the delivery

Run:

```powershell
python ../ndc-scene-evidence-placement/scripts/evidence_delivery.py verify --manifest <delivery_manifest.json>
```

Delivery is blocked unless all applicable checks pass:

- every acquisition coverage row passes and every exploration-acquired item has its required Map/`Position` scene anchor;
- the job manifest identifies an approved semantic raster master, and no production artwork was procedurally originated by code;
- source and final scene dimensions/mode match;
- the base coordinate verification passes;
- pixels outside the authorization mask are byte-identical;
- in Map-alone reconstruction mode, all changed pixels fit inside the exported map rectangle; the larger unused portion of the authorization workspace does not have to fit inside it. Accepted-parent hotspots instead bind the complete reviewed scene/state dependency; background repairs outside their semantic contour must not enter the Map;
- for a rectangular compatibility Map, the sprite equals the accepted scene rectangle pixel-for-pixel; for an irregular Map, every Alpha-positive RGB pixel equals the accepted parent and Alpha 0 RGB is zero;
- when the Map is a newly inserted or changeable scene layer, compositing it at `(x, y)` over the source reconstructs the accepted final scene; for a baked-in interaction hotspot, parent-pixel alignment passes and reconstruction is not misused as semantic-completeness evidence;
- the standalone detail image exists and is non-empty;
- when `iconPath` is present, the staged Icon is exactly `130 x 130` RGBA, all visible pixels remain inside `[7,7,122,122)`, transparent pixels carry zero RGB, and the supplied Icon verification report matches the staged bytes;
- when `--omit-icon` is used, the patch, manifest, and artifact list all omit the Icon rather than writing an empty or invented path;
- asset stems and ItemStaticData paths agree;
- staged artifact hashes still match the manifest.
- the asset's `ndc-texture-coherence/v1` record passes `D:\Codex\NDC\scripts\validate-ndc-texture-gate.py`; use `authorized_region_plus_boundary_tiles` for scene insertion and `full_image_tiles` for standalone Type 7, Big, Icon-master, and clue-photo art.

If any check fails, repair the job rather than editing coordinates or reports by hand.

### 7. Verify and package all states and contained items

The staged container delivery must include:

- irregular `prop_<container>1.png`, its final Alpha canvas rectangle, Type 6 `Position`, four-extrema record, expansion/exclusion record, and visual-gate evidence;
- the approved borderless Type 7 source retained for recovery;
- final `prop_<container>2.png`, its independent Type 7 `Position`, center-anchor calculation, and 12-pixel border declaration;
- the Type 6 and Type 7 ItemStaticData draft rows;
- every contained evidence Map crop, full-scene `Position`, Big, configured Icon, ItemStaticData draft row, and Map-to-Type-7 alignment verification;
- the contained evidence IDs and proof that only Type 6 is bound by SceneConfig;
- parent-pixel/alignment verification for every Type 6, reconstruction verification when Type 6 is a changeable scene layer, and border/placement verification for Type 7.

See [references/delivery-contract.md](../../ndc-scene-evidence-placement/references/delivery-contract.md) for the container manifest and coordinate example.

## Staging and synchronization

Stage new work under the current project's designated work-process scene/job directory, in a `delivery/` subfolder. On this workstation that parent is under `D:\Codex\NDC\工作过程文件\道具\<Unit>\...`. Existing `image/edit_jobs` packages are recoverable history, not the default destination for new work. This working package may contain manifests, verification JSON, overlays, patches, and recovery inputs. Never overwrite the approved scene or write directly into a Unity runtime asset directory during generation.

Keep the eventual formal image-asset folder separate from engineering staging. Each asset-facing folder contains only accepted/final PNG image assets plus one ASCII `XYposition.txt`. A complete scene-prop package must include the accepted full-scene placement preview as a formal PNG, every required Type 6 and Type 7 image, every contained or direct-pickup Map, every required Big and configured Icon, and every requested environment/state image. The coverage ledger defines the required image roles; "only PNG plus XY" is a file-type boundary and must never be interpreted as permission to publish only the assets changed in the latest revision. An explicitly requested single-asset delivery may be incremental, but it must not be labeled a complete formal scene delivery.

Before formal transfer, create the process-only `ndc-formal-release-contract/v1` defined in [references/delivery-contract.md](../../ndc-scene-evidence-placement/references/delivery-contract.md), deriving its records from the authoritative acquisition coverage ledger rather than from filenames or the files that happen to exist. Run `scripts/validate_formal_release.py --folder <formal-folder> --release-contract <contract.json> --report <process-report.json>`. This production gate derives required roles from each `deliveryClass`, requires source citations and classification reasons, binds `XYposition.txt` coordinates to current Map hashes, checks every formal artifact hash including XY, and scans the declared scene work-process/formal roots for stale active replicas. `scripts/validate_formal_package.py` remains only a legacy manual-list inspector and is not sufficient for a new production release.

The semantic formal-release gate fails when a required role is missing, an impossible role is present, a `minigame-only` record is smuggled into the evidence folder, an `environment` record lacks Map/Position/Big or carries an Icon, `XYposition.txt` is absent or inconsistent, a coordinate is bound to an old Map hash, an active staging/candidate/formal copy is stale, or the folder contains reports, manifests, overlays, masks, checkerboards, scripts, candidates, rejected/superseded/history files, or unapproved legacy assets. Debug/review previews stay in engineering staging; the accepted full-scene placement preview is a formal image asset and is not a debug preview.

Assemble a complete formal package into a new or verified-empty directory. Do not merge it blindly with an older formal folder. Move superseded or rejected prior formal material into a clearly named work-process history directory before publishing the replacement, preserving recoverability and provenance.

After all applicable gates pass, including `FINAL_VISUAL_RECORD_PRESENCE_GATE: PASS`, transfer the complete package directly into the formal image-asset folder; do not wait for a separate candidate review. A user-confirmed task authorizes this production and image-asset transfer. Copying assets into Unity or configuration tables still requires that the task scope explicitly includes the engineering synchronization. When merging `XYposition.txt`, preserve existing entries and normalize only the new line unless the user separately authorizes cleanup.

At the end of the package self-check, run `python D:/Codex/NDC/scripts/validate-ndc-final-visual-record-presence.py --formal-dir <formal-folder> --record-root <scene-work-process>`. The command must be the terminal gate after the final copies are present, not an earlier staging check. The record root must include every current-hash `visual_review.json`, including a Photoshop MCP repair folder outside `03_质量记录/视觉审核`. A missing current-hash review record for any formal PNG is a hard block: perform the absent whole/local visual review, write its record, rerun the stage validator, then rerun this terminal gate. Do not convert that block into a request for an avoidable human authorization once the asset requirements are known.

## Recovery

Every job must retain:

- the acquisition coverage ledger and classification reasons;
- the approved complete semantic raster master and its provenance/hash, including all required readable prop text;
- the base coordinate-edit manifests and masks;
- the accepted full scene;
- detail source or cutout mask;
- Big, Icon, or clue-Polaroid masters, masks, selected frame/direction parameters, locked-template hashes, and finalization reports when applicable;
- `delivery_manifest.json`;
- `delivery_verification.json`;
- hashes of all staged runtime artifacts.
- the separate style-lock/texture-coherence record, full-image evidence, local-coverage evidence, approved style comparison, and frozen failure-return source.

Resume from these artifacts. Do not reconstruct a coordinate from screenshots or memory.
