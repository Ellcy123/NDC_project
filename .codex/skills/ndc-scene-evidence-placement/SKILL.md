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
| `status` | `ready`, `skipped_after_3_failed_generations`, `blocked_by_skipped_record:<itemId>`, or a concrete unresolved dependency |

Do not invoke a production child while any route or acquisition row is unresolved. A production-time `skipped_after_3_failed_generations` status is terminal for that row rather than unresolved, so it does not stop independent ready rows.

## Bounded generation retries and fail-forward

After the user confirms the concrete visual edit, a production child may make up to `3` fresh AI generation calls for the same `itemId` and production stage without asking between attempts.

1. Persist every candidate under a versioned path inside the current system-temporary job. After each rejection, append the attempt number, temporary candidate path, machine/visual reason codes, and a concise reason to `<ndc-temp-work>/generation_attempt_log.json`.
2. Accept the first candidate that passes the route-specific machine and visual gates. Deterministic recomposition, registration, mask refinement, or repair using an already persisted candidate does not count as a fresh generation attempt.
3. After the third rejected generation, stop that record. Set its acquisition-contract row to `skipped_after_3_failed_generations`, add `skipReasons`, retain rejected artifacts only until the batch reaches a normal terminal publish, and do not create a delivery package or pretend the record passed.
4. Continue automatically with the next `ready` record whose production does not depend on the skipped record. If a later row depends on it, mark that row `blocked_by_skipped_record:<itemId>` without spending generation attempts, then continue searching for the next independent ready row.
5. Do not use this fail-forward rule to bypass unresolved canon, route, ID, synchronization permission, or destructive-action questions. Those remain blockers rather than generation failures.
6. In the final report, list every skipped/blocked record ID, its three attempt reasons or dependency reason, and which record production resumed with. Do not publish temporary candidate paths that are deleted during cleanup.

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

Stage a temporary `detail-only` verification package with:

- the approved Big and required Icon plus their verification reports and source hashes;
- an internal `ItemStaticData.patch.json` containing the approved detail/icon paths while preserving the current table schema for `mapSpritePath` and `Position`; explicitly clear any stale active world path or Position using that schema's accepted empty representation rather than merely omitting the patch field. This patch is a verification input and is not copied into the project-facing delivery. A non-empty legacy placeholder may remain only when the merged row has no SceneConfig binding or staged Map artifact and the manifest proves it is runtime-inert;
- `detail_delivery_manifest.json` recording route, itemType, acquisition event, explicit Map/Position omission reason, artifact hashes, and any separate handover-state dependency;
- `detail_delivery_verification.json` proving the Big/Icon reports match the staged bytes and that no usable Map, non-empty Position, or scene artifact entered the package; record any preserved legacy placeholder path as inert rather than treating it as delivered art.

The scene packager is not used for this route. Until a dedicated detail-package checker exists, record the verification evidence explicitly and do not describe the package as machine-verified beyond the Big/Icon reports. At terminal publication, copy only the runtime Big/Icon assets and compact status report; omit `scene_preview.png` and `XYposition.txt` because this route has no world-space anchor.

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
- Never overwrite an approved source scene. Keep generation, masks, masters, per-record packages, manifests, reports, overlays, and rejected candidates inside the system-temporary job described below.
- Draft configuration and asset packages may be prepared after route approval. Copying assets into Unity or changing formal tables still requires explicit user authorization.

The existing shared implementation resources remain under this skill for compatibility:

- `scripts/evidence_delivery.py`
- `scripts/evidence_publish.py`
- `scripts/evidence_art.py`
- `scripts/secondary_prop_border.py`
- `references/delivery-contract.md`
- `references/detail-icon-production.md`
- `assets/`

Child skills load only the resources relevant to their route.

Before running any shared Python script in Codex desktop, load the bundled workspace dependencies and use the returned Python executable. Do not assume that bare `python` or `python3` has Pillow or the required image libraries.

## Temporary work and compact publication

New production must not create `image/edit_jobs/<job>` or leave process artifacts elsewhere in the repository.

1. Resolve the operating system temporary directory and create one unique child under `<system-temp>/ndc_art_jobs/<job>-<uuid>/`. Confirm the resolved job path is a strict child of that namespace before writing or cleaning it.
2. Put every route contract, crop, mask, prompt, generated candidate, semantic master, overlay, verification report, per-record delivery package, attempt log, and helper-script output in that temporary job. A per-record package may still contain `ItemStaticData.patch.json`, its own `XYposition.txt`, and detailed manifests because those are internal verification inputs, not project deliverables.
3. When all independent rows have reached a terminal state, publish the accepted scene-anchored records with `scripts/evidence_publish.py`. The project-facing directory is `image/deliveries/<batch>/<scene>/` and contains only:

```text
scene_preview.png
XYposition.txt
production_report.json
assets/
  <runtime Map, Big, and applicable Icon PNGs>
```

`XYposition.txt` is scene-level, contains one ASCII `<map-stem> x,y` line for every successful record with a runtime Position, and excludes skipped/blocked records. Do not publish `ItemStaticData.patch.json`; the configuration workflow consumes this one consolidated XY file. A batch with no world-space Position may omit `XYposition.txt` and `scene_preview.png` rather than inventing them.

Use the publisher for normal direct-scene/environment batches:

```text
<workspace-python> .codex/skills/ndc-scene-evidence-placement/scripts/evidence_publish.py \
  --work-dir <system-temp>/ndc_art_jobs/<job>-<uuid> \
  --output-dir image/deliveries/<batch>/<scene> \
  --scene-preview <accepted-combined-scene.png> \
  --manifest <passing-record-delivery-manifest.json> \
  --manifest <next-passing-record-delivery-manifest.json> \
  --status-report <terminal-batch-status.json> \
  --batch <batch> \
  --scene-id <scene-id> \
  --scene-name <scene-name> \
  --cleanup-work-dir
```

The publisher rechecks manifest/artifact hashes, refuses an existing final directory, writes one combined XY file, strips temporary paths from the compact report, and only then recursively deletes the exact temporary job. A normally completed batch with skipped records is still terminal and must be cleaned after its failure reasons are compacted into `production_report.json`. If production is interrupted, publication fails, or cleanup itself fails, retain the temporary job for recovery and report the condition; never delete first or clean a broader temp/project directory. Legacy `image/edit_jobs` folders are not migrated or deleted automatically.

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
