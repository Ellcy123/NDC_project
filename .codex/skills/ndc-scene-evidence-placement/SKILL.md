---
name: ndc-scene-evidence-placement
description: Route and orchestrate NDC evidence-art production from the player's actual acquisition event, then invoke the dedicated scene-placement, Type 6 to Type 7 container, or detail-art child skill. Use for creating, replacing, auditing, or packaging NDC evidence props, clues, environmental observations, cabinet or drawer contents, Bigs, Icons, and scene Map assets. Do not use for Testimony or minigame-only interface art.
---

# NDC Scene Evidence Placement Router

Treat “出道具” as a runtime delivery problem, not as a request for one standalone picture. Decide how the player obtains every requested record before producing art, assigning IDs, drafting configuration, or calculating coordinates.

This is the only automatically selected entry skill for NDC evidence-art work. It owns route selection, child-skill orchestration, coverage checks, and final completeness review. Detailed production rules live in the child skills and are loaded only after the route is fixed.

## Read before routing

1. Read the relevant Unit evidence-art requirement and the matching current state scene. Do not use an archived design as current canon.
2. Read `docs/游戏系统/核心玩法/搜证与物品系统.md` when the request depends on item type, collection, analysis, or combination behavior.
3. Inspect the matching current `SceneConfig` and `ItemStaticData` rows as runtime evidence and naming inputs. Empty or placeholder fields do not establish an acquisition route.
4. If the request includes Unit, Episode, Loop, or ID identity, read `canon_manifest.json` before inferring paths or namespaces.

If the current state, scene design, and runtime rows disagree, record the disagreement and stop before art production. Never choose the cheapest route merely because its configuration already exists.

## Build the acquisition contract first

Create one coverage row for every requested record:

| Field | Required content |
|---|---|
| `itemId` | Current approved ItemStaticData ID, or `unassigned` |
| `itemType` | `3/item`, `1/clue`, `2/envir`, `not-applicable`, or `unresolved` |
| `acquisitionEvent` | What the player clicks, opens, photographs, receives, analyzes, or combines |
| `route` | One route from the table below, or `unresolved` while required facts are missing |
| `anchorMode` | `visible-record`, `observation-anchor`, `container-entrance`, `none`, or `unresolved`; legacy `search-hotspot` must be redesigned before production |
| `visibleAnchor` | What is actually visible and clickable before acquisition |
| `hotspotMode` | `object-alpha`, `secondary-menu-region`, `none`, or `unresolved` |
| `hotspotTarget` | The exact object silhouette or approved Type 6 secondary-menu entrance region that Unity may click |
| `acquiredRecord` | The item, clue record, or observation detail delivered after interaction |
| `containerChain` | Type 6, Type 7, and child IDs when applicable |
| `zPolicy` | Approved scene-sorting values and their current configuration source, or `not-applicable` |
| `deliverables` | Required Map, Position, Big, Icon, container states, or explicit omissions |
| `sources` | Current state, scene design, and table rows supporting the decision |
| `status` | `ready` or a concrete unresolved dependency |

Do not invoke a production child while any row is unresolved.

## Route by player action

The acquisition route decides scene coverage. The ItemStaticData type decides the detail presentation. Resolve both axes; neither replaces the other.

### `direct-scene`

Use when the player clicks or photographs a visible anchor in the base exploration scene and no separate opened interior view appears.

This route requires a visible item, clue, or environmental condition that the player clicks directly. Set `anchorMode: visible-record` for items/clues and `anchorMode: observation-anchor` for environmental conditions. Set `hotspotMode: object-alpha`; the hotspot is the visible record itself, never the surrounding table, floor, wall, drawer front, or other support surface.

When a direct-scene anchor must be newly added or visually repaired, its Map authoring is scene-first: choose a placement rectangle on the approved base scene, generate the object inside a complete coordinate-locked scene crop, compose and approve that crop in the full scene, and only then extract the actual object from the accepted scene result. Derive the no-suffix Map, `Position`, and hotspot from that post-generation object alpha. The placement rectangle and its broader authorization workspace are generation controls only and must never become the hotspot. Do not generate an isolated transparent or green-screen prop first and then paste it into the scene as the source of a direct-scene Map.

A furniture/search region that grants a hidden record immediately without opening a secondary view is not valid for new production. Either make the acquired record visibly clickable or redesign the interaction as a real `container-click` chain. Keep legacy `search-hotspot` rows unresolved until the design explicitly chooses one of those routes.

Invoke, in order:

1. `$ndc-evidence-scene-placement` at `../ndc-evidence-scene-placement/SKILL.md` through acceptance of the Map and Position.
2. `$ndc-evidence-detail-art` at `../ndc-evidence-detail-art/SKILL.md` for the type-appropriate Big and Icon.
3. Return the approved detail-art handoff to `$ndc-evidence-scene-placement` for final packaging and scene-package verification.

### `container-click`

Use when all three statements are true:

1. The player first clicks a closed or normal-state container.
2. A distinct opened interior view appears.
3. The player then clicks one or more contained records individually.

Cabinets, cupboards, drawers, safes, lockers, filing cabinets, cases, chests, lidded boxes, and comparable closed storage whose contents are not already exposed must trigger the container decision gate below. Assign `container-click` with `anchorMode: container-entrance` only when the current design establishes the separate interior view and subsequent child click. While either fact is missing, keep both `route` and `anchorMode` `unresolved`. Assign `direct-scene` only when the current design explicitly says there is no secondary view and the first click grants the record directly.

Set `hotspotMode: secondary-menu-region` only for the Type 6 entrance. That region may cover the coherent container, drawer, cabinet door, or approved opening surface. Every individually clickable Type 7 child still uses `hotspotMode: object-alpha` and is clickable only on that child object.

Invoke, in order:

1. `$ndc-evidence-container` at `../ndc-evidence-container/SKILL.md` through acceptance of Type 6, Type 7, and every child Map/Position.
2. `$ndc-evidence-detail-art` once for each contained record that needs a Big or Icon.
3. Return every approved detail-art handoff to `$ndc-evidence-container` for complete-chain packaging and verification.

The current child workflow covers individually clickable contents only. If the request instead requires opening a container to grant multiple records automatically, do not reinterpret it as `container-click` or `direct-scene`; report that the route is outside the current skill and stop.

### `environment`

Use only for ItemStaticData `envir` records that the player clicks to inspect but never collects.

Invoke, in order:

1. `$ndc-evidence-scene-placement` through acceptance of Map and Position.
2. `$ndc-evidence-detail-art` for Big production with an explicit Icon omission.
3. Return the approved Big and Icon-omission handoff to `$ndc-evidence-scene-placement` for final packaging and verification.

Pure non-interactive dressing belongs in the background and must not become an `envir` row.

### `detail-only`

Use when an `item` or `clue` becomes owned without a world-space locate/click step, including:

- dialogue, Expose, AVG, handover, or scripted-event grants;
- analysis, combination, comparison, memory, identity-lock, or reasoning results;
- a formal ItemStaticData result granted by minigame completion.

Invoke only `$ndc-evidence-detail-art`. Do not invent a Map or Position. If a handover or event visibly presents the record in the scene, record the separate conditional or performance-state requirement without turning it into a collectible Map.

Stage a `detail-only` delivery with:

- the approved Big and required Icon plus their verification reports and source hashes;
- `ItemStaticData.patch.json` containing the approved detail/icon paths while preserving the current table schema for `mapSpritePath` and `Position`; explicitly clear any stale active world path or Position using that schema's accepted empty representation rather than merely omitting the patch field. A non-empty legacy placeholder may remain only when the merged row has no SceneConfig binding or staged Map artifact and the manifest proves it is runtime-inert;
- `detail_delivery_manifest.json` recording route, itemType, acquisition event, explicit Map/Position omission reason, artifact hashes, and any separate handover-state dependency;
- `detail_delivery_verification.json` proving the Big/Icon reports match the staged bytes and that no usable Map, non-empty Position, or scene artifact entered the package; record any preserved legacy placeholder path as inert rather than treating it as delivered art.

The scene packager is not used for this route. Until a dedicated detail-package checker exists, record the verification evidence explicitly and do not describe the package as machine-verified beyond the Big/Icon reports.

### `minigame-only`

Use for lock faces, puzzle boards, draggable parts, intermediate screens, or other gameplay assets that never become ItemStaticData records. Route them to the relevant minigame asset workflow and stop this skill.

### Excluded: Testimony

NPC-spoken information belongs to the Testimony system. Do not create ItemStaticData art for it.

## Normalize legacy route names

Current design documents may still use older delivery labels. Normalize them in the acquisition contract before invoking a child:

- `scene-pickup` means parent route `direct-scene`;
- `container-state / 逐件点击` means parent route `container-click`;
- `detail-only`, `environment`, and `minigame-only` retain their names.

These aliases do not override the actual player event. A legacy label that conflicts with the current state or scene design remains `unresolved` until the conflict is settled.

## Container decision gate

Before choosing `direct-scene` for any cabinet, cupboard, drawer, safe, locker, case, chest, box, pocket, bin, or similar storage, answer:

1. Is the target content already exposed in the base scene?
2. Does clicking the storage produce a distinct opened or enlarged interior view?
3. After opening, does the player still need to click the contained record?

If answers 2 and 3 are yes, `container-click` with `anchorMode: container-entrance` is mandatory. If the documents do not answer these questions, set both `route` and `anchorMode` to `unresolved`, stop, and ask; never silently fall back to `direct-scene`.

## Detail contract by ItemStaticData type

After the acquisition route is fixed:

| Type | Meaning | Detail output |
|---|---|---|
| `3` / `item` | Physical object or document entering inventory | Ordinary Big + Icon |
| `1` / `clue` | Photographed or recorded scene condition | Locked `620 x 620` clue-Polaroid Big + Icon |
| `2` / `envir` | Inspectable environment record, never collected | Big only; Icon forbidden |

Analysis and combination capability do not determine the acquisition route. A tool-assisted item removed from a scene remains scene-acquired; a newly generated analysis or combination result is `detail-only`.

## Shared non-negotiable contracts

- The approved native-resolution final image is the coordinate truth. Never estimate Position from a preview, resized image, screenshot, or memory.
- Unity refreshes each `PolygonCollider2D` from the Map Sprite physics shape. For every direct-scene record and every Type 7 child, deliver a per-record RGBA Map whose alpha describes that record's object-shaped hotspot. Do not use an opaque scene crop as a direct-item Map.
- Region hotspots are permitted only for a Type 6 secondary-menu entrance. A table, shelf, floor patch, or other support surface must not become a region hotspot for a directly acquired record.
- For a newly generated direct-scene anchor, the accepted full-scene placement must exist before the per-record Map is extracted. An independently generated isolated prop may support Big/Icon work, but it is not valid provenance for the scene Map or its coordinates.
- A scene Map is a low-information discovery anchor. Exact text, dates, numbers, handwriting, damage comparisons, and puzzle-specific detail belong in Big unless the environment itself must be read in scene.
- Production artwork must originate in an approved high-resolution raster master. Deterministic code may transform and verify approved art but must not procedurally invent the final prop, document, furniture, texture, wear, lighting, or scene artwork.
- Never overwrite an approved source scene. Stage work under `image/edit_jobs/<job>/delivery/`.
- Draft configuration and asset packages may be prepared after route approval. Copying assets into Unity or changing formal tables still requires explicit user authorization.

The existing shared implementation resources remain under this skill for compatibility:

- `scripts/evidence_delivery.py`
- `scripts/evidence_art.py`
- `scripts/secondary_prop_border.py`
- `references/delivery-contract.md`
- `references/detail-icon-production.md`
- `assets/`

Child skills load only the resources relevant to their route.

Before running any shared Python script in Codex desktop, load the bundled workspace dependencies and use the returned Python executable. Do not assume that bare `python` or `python3` has Pillow or the required image libraries.

## Final orchestration gate

Before presenting a staged delivery, verify:

- every requested record has a resolved acquisition row and source citations;
- the invoked child skills match the accepted route;
- every exploration interaction has its required visible anchor, Map, and Position;
- every direct-scene Map and every Type 7 child Map has a reviewed object-alpha hotspot overlay, with no unrelated support surface included;
- every newly generated direct-scene Map records scene-first provenance: placement rectangle, accepted coordinate-locked scene result, post-generation extraction layer, and alpha-derived Map rectangle;
- only a Type 6 secondary-menu entrance uses a region hotspot, and sibling record hotspots do not overlap unless an approved interaction-priority rule is recorded;
- every `container-click` chain contains Type 6, Type 7, and every individually clickable child;
- only Type 6 is bound by SceneConfig in a container chain;
- every required Big and Icon exists, and every `envir` Icon is absent;
- every `detail-only` row has no usable Map asset or non-empty Position, even when the table schema preserves an empty or legacy placeholder field;
- shared verification scripts and artifact-hash checks pass where applicable;
- unresolved routes, missing IDs, visual approvals, and synchronization permissions remain explicitly blocked rather than guessed.

Resume from staged manifests and approved masters. Do not reconstruct route decisions, coordinates, or asset provenance from memory.
