---
name: ndc-scene-evidence-placement
description: Place collectible NDC evidence into approved raster scenes, enforce a complete scene anchor for every exploration-acquired item, prepare Unity Type 6 to Type 7 container chains, and deterministically finalize Map, Big, 130px Icon, and 620px clue-Polaroid assets. Use when adding, replacing, auditing, or packaging clickable evidence props and container contents in NDC exploration scenes.
---

# NDC Scene Evidence Placement

Turn an approved scene plus an evidence requirement into a staged, Unity-ready evidence package. Preserve the source and derive coordinates from the accepted final image. Never eyeball or manually transcribe `Position`.

## Unit 4 visual-release firewall

For a Unit 4 all-item audit, a repair prompted by visual feedback, or any promotion from a candidate/history folder into `最终交付`, read [references/unit4-visual-release-firewall.md](references/unit4-visual-release-firewall.md) before selecting an asset. Its candidate disposition, actual-formal-byte review, geometry/Alpha checks, and replacement-preservation rules are hard release conditions. Do not treat a technically valid Map, a prior PASS record, an accepted master, a correct runtime size, or a pre-existing formal file as a substitute for that current visual decision.

For linked Big/Icon/Map/Type 7 production or any cutout, read [references/asset-identity-and-alpha-review.md](references/asset-identity-and-alpha-review.md). Before approving separate roles, compare the actual role images together against the identity master; independently inspect missing target material and residual background. A user's rejection invalidates the affected role's reuse approval immediately, even if its bytes and old PASS hash have not changed. Preserve the rejected bytes as evidence, not as approved inputs.

## Mandatory stage-end visual self-check gate

Every art-production stage executed by this Skill must end with an actual visual self-check before its output may be accepted, passed to a later formal stage, packaged, synchronized, or released. This includes semantic-master acceptance, scene insertion, accepted full-scene composition, Type 6/Type 7 work, Map contour/export, Big, Icon master/final, clue Polaroid, requested event/state images, deterministic transforms, placement previews, and final packaging. Inspect the current whole image at `100%` and every applicable local region at nearest-neighbor `200%` or through complete original-pixel tiles. Compare against the accepted source and every applicable acquisition, physical construction, support/contact, occlusion, shadow, perspective, scale, movement, light, style, texture, text, Alpha, edge, coordinate, and runtime-readability requirement.

Write one current `ndc-stage-visual-self-check/v1` JSON record per executed stage. It must bind the stage ID, reviewer/date, input and output paths plus SHA-256, the inspected `whole_100` and `local_200_or_tiles` views, every applicable criterion with an explicit finding and `PASS`/`FAIL`/`NOT_CHECKED`, the overall `visual_check_status`, and the responsible rework stage when blocked. Missing record, missing visual-detection item, stale output hash, missing required view, `FAIL`, or `NOT_CHECKED` is `STAGE_VISUAL_SELF_CHECK_GATE: BLOCKED`: do not use the output downstream, package/synchronize it, or call it formal. Technical validators, coordinates, dimensions, hashes, masks, Alpha/border reports, or absence of a detected error cannot write visual `PASS`.

After a block, return to the responsible stage, perform the missing inspection and required repair/regeneration, then repeat the visual self-check on the new current output. Release only after the current hash has a passing record. For every file-producing stage, run `python D:/Codex/NDC/scripts/validate-ndc-stage-visual-self-check.py --record <visual-review.json> --artifact <current-output>`; a nonzero result is a hard stop. Existing generation-attempt ceilings still apply, and exhausting one leaves a candidate rather than weakening this gate. The more detailed review and terminal presence rules below remain mandatory and may satisfy this gate only when they contain the same required evidence.

Existing files are candidates, not presumed-approved inputs: inspect and choose them before any new generation, but never promote them merely because their manifest, dimensions, Alpha arithmetic, coordinate check, Icon check, prior PASS, or formal-release validator is green.

For every candidate that would contribute a scene Map, complete the visual candidate gate before copying it to a formal folder or writing a release contract: (1) compare the full native-resolution source scene at 100% against the candidate Map; (2) inspect the Map on checkerboard and Alpha-only at nearest-neighbour 200%; (3) inspect a tinted and an untinted parent overlay at 200%; and (4) explicitly name target physical planes, attributable shadow, every excluded adjacent evidence item, and every excluded background plane. Candidate fails if Alpha includes area merely because it is dark, low-contrast, contiguous, inside an authorization mask, or inside a changed-pixel rectangle. A complete object image does not validate its own scene Map. In particular, paper/documents must not acquire desk fronts, desktop surface, broad environmental shadows, or neighboring paper; folders must not acquire desk/background strips, loose unrelated dark patches, or neighboring evidence; multipart clues must not acquire each other's component silhouettes. Mark `FAIL`/`NOT_CHECKED`, preserve process history, and re-author the contour if any such inclusion is visible. Never create PASS by packaging, copying, renaming, or mechanically revalidating a rejected Alpha.

For every coordinate-bearing Map or Type 6 hotspot, one passing record may bind exactly one PNG. It must also include Alpha-only, checkerboard, and untinted parent-overlay views plus the semantic hotspot fields in [references/hotspot-semantic-review.md](references/hotspot-semantic-review.md). A shared batch PASS, a sprite viewed only on black, or parent-RGB equality cannot approve a hotspot. Missing target planes, unexplained transparent holes, unrelated parent pixels, and any neighboring clickable container included in Alpha are visual failures even when the technical crop is pixel-perfect.

When Photoshop is used, follow [references/photoshop-mcp-repair-and-framing.md](references/photoshop-mcp-repair-and-framing.md). Photoshop operations default to the bridged Photoshop MCP; do not substitute mouse/keyboard control unless the user explicitly authorizes that fallback for the current task. Photoshop work is strictly serial: finish, verify, visually pass, and current-hash validate one image before opening, switching to, modifying, or accepting the next image.

### Existing Big correction priority

When an existing ordinary Big or clue Big is being corrected, classify the failure before generating anything. If the current semantic master already has the correct prop identity, required content and exact readable text, material/style, lighting premise, and perspective, but fails only frame choice, size, safe-range occupancy, rotation, transparent margin, minor crop, or a small non-semantic cleanup, **use Photoshop MCP first**. Work from a recoverable duplicate; perform the smallest supported move, uniform scale, rotation, crop/reframe, or transparency cleanup; preserve every semantic pixel; then deterministically apply the locked runtime frame/template and rerun the Big visual/technical gates. Do not regenerate an otherwise correct Big merely to solve a layout defect.

For environment Bigs, never use decorative tilt or a generic rectangular/soft-window fade. Isolate the named environmental observation and its required physical context with a content-led irregular Alpha; keep its original scene orientation. For physical-prop Icons, export the transparent physical object or approved component group, not a clue-Polaroid/photo frame. When deriving any Map from a composited scene, keep the approved Alpha scope but sample every Alpha-positive RGB pixel from the final accepted parent scene at the released XY coordinate; zero RGB where Alpha is zero before formal validation.

Run a current Photoshop capability preflight before this correction. If the paired host cannot open or place the approved local master because file access/whitelisting is unavailable, record `PS_MCP_LOCAL_FILE_ACCESS_BLOCKED`, preserve the input and the intended edit, complete unrelated work, and retry after access is restored. Never silently replace this with Computer Use or mouse/keyboard automation. A deterministic `evidence_art.py finalize-big` or `compose-polaroid` export remains permitted after the semantic master is accepted; it owns only rotation, fit, transparency-safe resampling, locked framing/template composition, dimensions, and reports.

Escalate to an image-model rebuild only when visual review proves a semantic defect: wrong prop/content/style/period treatment, missing or wrong exact information, broken construction, or an undersized/invalid master that cannot be re-framed without prohibited upscaling or semantic loss. Record the failure class, the MCP capability/path result, all retained predecessor hashes, and why re-generation—not Photoshop framing—was necessary. A rebuilt semantic master restarts the normal Big/Polaroid whole-100%, local-200%, safe-range/template, texture, and current-hash review gates.

### Readable prop text: generation-only semantic rule

Photoshop MCP must never create, insert, replace, delete, typeset, restyle, paint, or composite readable prop text. This prohibition also applies to deterministic/Pillow/Canvas/SVG text overlays, text corrections, OCR replacements, or "exact-text" layers after a raster master is generated. Photoshop remains the first choice only for a semantically complete Big whose readable text is already correct and whose defect is strictly presentational.

When any required title, date, number, ledger entry, signature, stamp wording, or body text is missing, wrong, garbled, incomplete, or insufficiently readable, classify it as a semantic failure and return to the image-generation stage. Retain the failed source and review record, then generate a new complete raster candidate with its final required text authored in that result; do not repair the candidate by overlaying text. Runtime sizing, alpha cleanup, masks, locked frames, coordinate crops, and Icon derivatives may transform only that accepted complete raster.

### Multi-part prop hierarchy after semantic lock

When an accepted evidence master contains two or more distinct physical components (for example papers, cards, photographs, folders, tags, or a document plus its clipboard), do not default to an evenly aligned, upright row. After all required content and readable text have passed, assess whether a restrained staggered composition would better establish physical hierarchy: a rear component may sit slightly offset, components may have distinct small rotations, and a foreground component may partially overlap another.

Use only a non-semantic transform of the accepted complete raster components. Photoshop MCP is the preferred route: on a recoverable duplicate, make a tight independent selection for each physical component, use the exposed **selection-to-new-layer / layer-via-cut** operation to cut that component into its own layer, then move, scale, or rotate the resulting layers. Do not require a separate split-document/re-place workflow when a per-component selection-and-cut route is exposed. Keep source shadows with their component; a uniform new layer-effect shadow is optional rather than a prerequisite. If the current capability catalogue does not expose the required selection-to-layer operation, record `PS_MCP_SELECTION_TO_LAYER_UNAVAILABLE`, retain the unchanged master and intended transform parameters, and use a documented alpha-safe deterministic transform; never describe that fallback as a Photoshop edit and never substitute mouse/keyboard automation. Never retype or change readable text during this recomposition. Validate every required wording and detail on the pre-composition complete master; after that gate has passed, the final staggered Big may deliberately obscure portions of text or a rear component to establish a natural overlap hierarchy. The final layout need not keep every detail fully readable, but it must retain the identity of every component, the intended front/back relationship, attributable shadows, transparent gaps, and the selected Big safe range. Reject only a layout that wholly conceals a required component, creates a false merged object, clips a component, or makes the underlying source relationship implausible. Include whole, local, and guide-overlay views in the current-hash visual review.

### Type 7 source-anchor, viewpoint, and direct-composition lock

For every `container_type7*` stage, the record must also contain a `type7_visual_context` object with: the real container identity; a written derivation of the visible environment from the frozen original-scene anchor; `height_class` (`low`, `mid`, or `high`); `observation_direction` (`downward`, `level`, or `upward`); a first-person viewpoint rationale; the literal method `direct_image_generation`; and `child_fully_contained: true`. A passing Type 7 record must bind a hash-checked `original_scene_visual_anchor`, a `source_anchor_side_by_side` image, and applicable passing criteria named `mandatory_direct_image_container_rule`, `source_anchor_visual_comparison`, `container_height_and_observation_direction`, `visual_self_check`, plus a child/container identity-and-full-visibility criterion. `validate-ndc-stage-visual-self-check.py` enforces these fields; missing evidence blocks the stage.

The mandatory production order is: **approved Big first → actual whole/local visual PASS → Image directly generates the opened container, its child, and the derived environment together → optional borderless-interior Photoshop MCP reframe when only irrelevant environment is excessive → Type 7 whole/local/source-anchor comparison PASS → add the 12px frame → derive the child Map**. Never paste, warp, or deterministically composite the Big into a container after generation. A permitted reframe may only uniformly enlarge/reposition/crop the already direct-generated borderless composition and must follow the Photoshop reference; it never includes the white frame. The image prompt for every opened-container or contained-item state must literally include: `第一人称视角、打开XX、近距离观察XX内、特写场景`. Replace `XX` with the actual container and add the source-derived environment, physical support, full containment, and prohibition on exposed corners.

Choose viewing angle from the container's real source height, not from a default top-down template. A low coffee table, trash bin, wastebasket, floor box, or floor drawer requires a standing-player downward view. A mid-height drawer, wardrobe pocket, or desk organizer uses only the amount of downward/level view that the real height supports. A high shelf, upper cabinet, or high-hung container may require eye-level or upward observation. State this derivation in both the prompt and review record; if a candidate's camera contradicts the actual height, reject it even when the contents are readable.

The source/Type 7 comparison is a visual derivation, not a parameter or furniture-count check. Inspect side by side whether the source predicts the Type 7's actual furniture geometry, materials, adjacency, depth, lighting direction/value, and camera height. A generic desk, drawer, tabletop, or room with a similar object count fails. For a transformable near-success placement, use the Photoshop-MCP rescue order first: one supported low-cost correction, then at most one fresh generation at that location, then freeze/reroute if it still fails. Other same-cause failures retain the generic three-attempt ceiling. Never reveal one corner of an item to bypass the problem.

## Read first

1. Read the relevant Unit evidence-art document and the matching state scene before deciding what appears in the scene.
2. Read the coordinate-edit Skill completely before any raster insertion or replacement. Prefer `../ndc-coordinate-image-edit/SKILL.md`; when that sibling source is not installed in `.agents`, read the maintained NDC mirror at `D:\Codex\NDC\NDC_project\.codex\skills\ndc-coordinate-image-edit\SKILL.md`. Its source-preservation, mask, crop, seam, and final-union checks remain mandatory.
3. Read [references/delivery-contract.md](references/delivery-contract.md) before naming or packaging assets.
4. When the request includes a Big image, Icon, or clue Polaroid, read [references/detail-icon-production.md](references/detail-icon-production.md) before generating, scaling, rotating, framing, or approving it.
5. Before drawing, accepting, or revising any Map/Type 6 Alpha, read [references/hotspot-semantic-review.md](references/hotspot-semantic-review.md).
6. Before any Photoshop placement repair, Type 7 reframe, or Photoshop-authored hotspot path, read [references/photoshop-mcp-repair-and-framing.md](references/photoshop-mcp-repair-and-framing.md).

If the request includes Unit/Episode identity or IDs, read `canon_manifest.json` before inferring paths or namespaces.

## Scene source and output routing

Before selecting an NDC scene source, read and obey the current project's source-search precedence and stop conditions. Keep machine-specific root ordering in project rules, not in this Skill. Match the exact scene ID, chapter, state, and approval lineage; do not silently select a draft, process export, thumbnail, or similarly named scene when the governing source policy identifies an approved source. Record roots checked, exact source path, and SHA-256. If conflicting candidates within the permitted source cannot be resolved from current project records, block source selection instead of guessing.

Treat `D:\PMH\工作` and `D:\PMH\ndc` as read/copy-only inputs. Copy required material into `D:\Codex\NDC\工作过程文件\道具\<Unit>\...` before authoring, and place confirmed deliverables only under `D:\Codex\NDC\最终交付\道具\<Unit>\...`. On this workstation, every scene-level work and delivery directory must include a clear Chinese scene/status name, optionally followed by a stable English alias after `__`, for example `SC4002_哈里森外间办公室_白天__Harrison_outer_office_day`. Runtime image stems and `XYposition.txt` entries must still match the configured engineering names exactly; never append Chinese to a runtime filename merely to satisfy the directory-naming rule.

## Preflight inventory and reuse lineage

### Candidate-first routing

Before selecting a scene source, repairing, or generating any item, inventory all four recoverable scopes for the scene ID, configured runtime stem, item ID, and clear Chinese/English aliases:

1. current formal delivery under `D:\Codex\NDC\最终交付\道具`;
2. accepted semantic masters, staged candidates, and prior technical/visual records under `D:\Codex\NDC\工作过程文件\道具`;
3. recoverable historical, withdrawn, or superseded packages; and
4. user-approved source or delivery assets from the declared read-only project roots.

For every requested item, record the source path and SHA-256, candidate status, applicable visual/technical evidence, delivery-class scope, and exactly one disposition: `reuse current formal PASS`, `promote revalidated candidate`, `targeted non-semantic repair`, `regenerate after recorded candidate rejection`, `new`, or `blocked awaiting source/manual work`. A candidate outside the current formal directory is not absent merely because it is in process history. Re-run the current hash-bound technical and visual gates before promotion; do not regenerate a usable candidate simply because a new generation is easier.

Use this routing order: preserve or promote a passing candidate first; use Photoshop MCP first for a strictly non-semantic frame, size, placement, rotation, Alpha-margin, or minor-cleanup fault; regenerate only when the surviving candidates fail a documented semantic/style/construction/text gate, cannot be safely reframed, or no usable source exists. When Photoshop lacks the required automated operation, retain the source and its intended edit, complete unrelated work, and route to `blocked awaiting source/manual work` rather than silently weakening the candidate's gate.

Evaluate asset and scene scopes separately. A scene Map, hotspot, or Type 6/Type 7 chain failure cannot by itself invalidate an independently user-approved Big/Icon/semantic master. Keep that asset as a recoverable candidate with an explicit scope/status while repairing the scene chain. Do not move, withdraw, or overwrite an approved asset merely because a broader scene package fails; replace it only after that same asset has a recorded current-hash failure or an explicit user-requested revision. Conversely, never label an asset-level reuse as a complete scene delivery until its required scene chain passes.

Do not generate a duplicate merely because a similarly named file is easy to overlook. A prior formal asset may be regenerated only when its current visual record is failed/rejected or when the user explicitly requests a revision; move superseded formal material into recoverable work-process history only after the replacement itself has passed the same asset-level gates.

For a request to reuse a prior-Unit physical prop, locate the actual source PNG/Sprite in the read-only project roots before generating. Copy the source bytes, record source and destination SHA-256, and use that copy as the closed Big/Icon when the requirement is exact reuse. A prose specification, filename stem, or remembered appearance is not an image source: when the authoritative pixels cannot be found after the declared search roots and version history are checked, block that exact-reuse state instead of generating a lookalike and calling it reused.

## Classify before editing

Assign every requested evidence record one delivery class:

- `scene-pickup`: a visible, clickable object obtained by investigating the base scene and resting entirely on an independent support surface. Deliver Map, `Position`, Big, and every configured Icon. A paper, tag, or object partly pushed into a container is never a `scene-pickup` workaround.
- `container-state`: a drawer, safe, locker, case, box, pocket, bin, basket, bag, or similar Unity secondary-menu container. Deliver a scene-exact irregular RGBA Type 6 entrance Map whose Alpha follows the visible closed/normal container and attributable shadow, a separately authored rectangular Type 7 open view, independent coordinates for both, and the complete Type 6 -> Type 7 -> contained-item chain. Every contained exploration pickup also requires its own Map crop and full-scene `Position`, plus Big and every configured Icon. Do not treat the container pair as a substitute for the contained item's Map. A rectangular Type 6 crop is legacy compatibility only and requires a recorded runtime limitation. This remains mandatory even when the current camera can see inside the container; do not reveal a corner or label of the child in the base scene to avoid the chain.
- `detail-only`: an analysis result, memory result, automatic minigame output, or handed-over evidence that is never visible or clickable as a world prop. Deliver detail/icon assets only; do not invent a scene coordinate. A `post_expose`, dialogue, or minigame label alone does not prove this class; inspect the actual acquisition event.
- `environment`: a non-pickup environmental observation. It must remain visibly represented in the background or a state prop. If the player clicks it to discover or record information, deliver its real scene Map/`Position` plus a Big that presents the observed information; omit Icon. Its Big uses the two-mode, content-led irregular Alpha workflow in [references/detail-icon-production.md](references/detail-icon-production.md), not the ordinary prop's fully opaque rectangular crop by default. Do not infer this class from an `environment` filename when the authoritative event is actually `minigame-only`.
- `minigame-only`: an interaction asset that does not enter ItemStaticData. Route it to the minigame asset workflow.

Classify from the actual player acquisition event in the matching state, SceneConfig, and ItemStaticData chain—not from filenames, an existing empty `mapSpritePath`, or `pickup` alone. Create an acquisition coverage row for every requested evidence item with: `itemId`, acquisition event, delivery class, visible state, parent container IDs when applicable, Map stem, full-scene `Position`, Big stem, Icon stem or explicit omission, and source references.

Apply this hard gate before art production and again before delivery:

- Anything obtained by clicking or searching the exploration scene must have a visible scene anchor. Big and Icon alone never satisfy an exploration pickup.
- A direct scene pickup requires a non-empty Map and `Position`.
- A pickup found after opening a Type 7 container requires its own non-empty Map and `Position` inside the displayed Type 7 view. Type 6 and Type 7 images do not replace that child Map.
- An item granted automatically by dialogue, Expose, minigame completion, or analysis may omit Map only when it is never left for the player to locate or click. If the event visibly presents the item in the scene, deliver the required conditional/handover state as well.
- A locked or post-Expose cache must be classified by what the player does after it unlocks. If the player opens it and clicks the contents, it is a container exploration chain; if the game grants the contents automatically, document the visible event state and the no-Map reason.

Block the batch when any acquisition coverage row is unresolved. Do not generate Big/Icon-only placeholders to make an incomplete row look finished.

## Container visibility and physical placement gate

Apply this gate before choosing `scene-pickup` versus `container-state`, again before generation, and once more at expected gameplay display size after compositing.

- Prefer solid-walled or otherwise non-openwork trash cans, wastebaskets, bins, and similar ordinary containers. Use an open mesh or perforated design only when an approved design, established scene fact, or gameplay requirement actually calls for it; convenience in showing the contents is not sufficient.
- Preserve the scene's walkable route. Do not place a prop in a doorway, principal aisle, required path between furniture, or another space the player or staged characters must traverse.
- Treat every item physically inside or held by a container as `container-state`, whether or not the current camera can see into it. Do not tilt the container, lower its rim, enlarge the item, or make contents protrude merely to expose a direct pickup. Keep the closed or normal Type 6 container as the base-scene anchor and reveal the child only in the Type 7 view, where it receives its own Map and `Position`.
- Never route environmental storytelling through a Type 7 secondary menu. An `environment` record must remain legible through the base background or a genuine scene state. If the fixed camera cannot plausibly show it, revise the in-scene placement or narrative presentation rather than hiding it as a container child.
- Require real support contact. The prop must sit on the floor, shelf, desk, or other support surface with compatible perspective, occlusion, and contact shadow; floating and partially floating placement both fail.
- Derive scale from comparable real-world objects, furniture anchors, and scene depth. A prop that reads materially oversized at gameplay scale fails even when its mask, crop, and coordinates are technically valid.
- When a candidate is semantically correct and only slightly wrong in position, scale, rotation, or capability-correctable perspective, classify it as `near_success_transformable` and follow the Photoshop-MCP rescue order: correct once at low cost, visually verify; if blocked or still failing, regenerate once from the frozen source; if that fresh attempt also fails and returns here, freeze the location and use another support or a genuine Type 6 -> Type 7 chain. For candidates that never meet this near-success definition, three consecutive same-cause failures still forbid a fourth attempt at that location. Record the candidates and failure reason; never simulate a container by showing a child edge in the base scene.

Any failure above rejects the candidate and returns the responsible art stage to the frozen source, except for the explicitly bounded `near_success_transformable` Photoshop-MCP branch. Do not mask, cover, relabel, or arbitrarily shrink a failed composite to hide a structural or semantic error. Record the walkable-space judgment, interior-visibility judgment, support/contact evidence, scale anchors, exact Photoshop transform when used, and any direct-pickup-to-container reroute in the placement contract and acquisition coverage ledger.

## Art authorship boundary

The evidence's semantic appearance must come from an approved high-resolution raster master: an accepted image-generation result, artist-authored raster, approved source extraction, or an approved deterministic transformation of such a master. The master must already establish the prop silhouette, perspective, material, construction, wear, lighting, and scene context.

Deterministic code may own masks, crop rectangles, coordinate extraction, compositing of already-approved non-text art, perspective transforms, rotation, scale, alpha handling, locked-frame application, export dimensions, overlays, hashes, and verification reports. It must not originate the evidence or scene artwork, or create/change readable prop text.

Production delivery is blocked when Python/Pillow, Canvas, SVG, HTML/CSS, shaders, or similar procedural drawing is used to create the prop body, paper/card surface, container, furniture, background, scene state, texture, wear, lighting, handwritten marks, or illustrative layout. These APIs remain valid for test fixtures, masks, debug overlays, borders, and deterministic transforms of approved art.

Required titles, dates, numbers, and body text must be authored inside the accepted image-generation or artist-authored raster master. Code must not fabricate or complete readable document text, whether on a physical master or a blank page/table. Record the complete semantic master path/hash and the visual proof that its required wording is present. A visual assembled or text-completed with code is a mockup, not a final asset.

For a Type 7 container state, the deterministic allowance above never permits compositing a separately generated Big, photograph, card, or other child into an opened container. Once the Big has passed its own visual gate, use it only as an Image reference; Image must generate the complete opened container, fully supported child, perspective, local light, and source-derived environment in one result. Deterministic work may still derive Maps, masks, coordinates, Alpha and runtime crops from that accepted result. When only excessive irrelevant environment prevents readability, Photoshop MCP may uniformly enlarge/reposition/crop the complete direct-generated borderless interior before the final frame, as defined in the Photoshop reference; this is framing, not child compositing.

### Paper and file information-density rule

For paper, letter, note, file, receipt, card, dossier, envelope, or similar document evidence, **excluding photographs**, treat scene-visible and container-view imagery as discovery/physical-state views. The base-scene Map and Type 7 may show a reverse, fold, edge, partly obscured state, or generalized paper/file silhouette with no readable body text, title, date, or signature. This is not a repair defect when the document remains physically identifiable and locatable. The picked-up Big is the mandatory detail carrier for the exact readable information. Do not add, enlarge, sharpen, or expose in-scene writing merely to prove the Big contract. Photographs remain subject to their own identity/content and visible-photo review rules.

For a photo-related prop, first generate and visually verify the standalone photo's required content. If that photo contains a person, then before its Big or Type 7 can pass, run a second direct Image style-transfer stage against the approved full-body character-style reference supplied for that role. Preserve the approved photo's character design, action, palette, and background; change only the character rendering to the supplied character general style. Do not add people, props, correspondence, or narrative claims. Record both the original-photo and style-reference hashes and inspect the style-transferred result whole and locally before it is used in a container view.

### Mandatory visual-review evidence and release lock

After every executed visual production step, save a process-only `visual_review.json` before accepting its output into the next formal step. This includes semantic masters, each scene insertion candidate and accepted composition, Map contour/export, Big, Icon master and final Icon, requested event/state image, placement preview, and any deterministic transform that changes an exported PNG. Each record must name the stage, input/output paths and SHA-256 values, whole-image `100%` and local `>=200%` review views, review-image paths, applicable per-item findings, and explicit `PASS`/`FAIL` conclusions. Hashes, dimensions, masks, Alpha checks, texture scripts, or successful delivery verification are technical evidence only and must not create a visual `PASS`.

For freestanding scene props, the applicable findings must explicitly cover support contact, occlusion, contact/cast shadow, perspective, real-world scale, light direction/value, material/edge integration, movement conflicts, and composition-mask completeness. A prop that appears floating or half-floating is `FAIL`; absence of an artifact seam is not a substitute. For standalone assets, check physical construction, silhouette, style/texture, text legibility, Alpha edge and runtime-size readability as applicable.

Before formal transfer, create `final_visual_record_presence_gate.json` in the work-process package. It must enumerate every executed stage, every required formal PNG, and `XYposition.txt`; verify every current hash against its passing review or release-contract record; bind every coordinate-bearing Map hash to its current `x,y` and the SHA-256 of its accepted full native parent; and end in `FINAL_VISUAL_RECORD_PRESENCE_GATE: PASS`. A missing, stale, incomplete, or failed record is `NOT_CHECKED`/`FAIL` and blocks formal transfer. This is a Codex self-inspection record, not a restored wait-for-user-review workflow.

<!-- NDC_TEXTURE_COHERENCE_MODULE:BEGIN -->
Every generated semantic master, in-scene Map object, Type 7 open view, Big, Icon master, and clue-photo master must preserve its approved NDC style authority and pass a separate texture-coherence review. Control only non-semantic micro-detail density, continuity, scale, and distribution. Do not simplify, smooth, sharpen, modernize, photorealize, or otherwise restyle the evidence or scene. Preserve identity-bearing wear, exact approved marks, material construction, line language, palette/value compression, and lighting; reject repeated texture stamps, random cracks/speckle, fragmented marks, uniformly sharp micro-edges, and detail that exceeds the asset's runtime role.
<!-- NDC_TEXTURE_COHERENCE_MODULE:END -->

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

Never copy the detailed text requirements from the `big-detail contract` into the in-scene generation prompt. The map scene is a discovery anchor, not a readable evidence card or product shot. Unless the evidence itself is an environmental sign meant to be read in the scene, body text and exact metadata must remain unreadable at gameplay scale.

### 2. Prepare the insertion with the base skill

Before inventing a new placement, inspect the approved full scene for an existing object of the same physical class. Prefer a bounded **Image in-place replacement** when that object already has suitable scale, support, perspective, and depth and is not another evidence item, required story object, or interactive unit. Record the old object's identity, ownership check, native location, and why it is replaceable. Supply the approved scene, target identity master, and NDC style constraints; instruct Image to replace only that object while matching the source camera, support, lighting, and low-information map-scene contract. This is semantic image editing, not a Photoshop text-addition operation.

The authorization region must cover the old object, new object, and necessary old/new shadow, reflection, and occlusion footprint. Inspect for old-object remnants, duplicated props, changed neighboring evidence, false support, and drift outside the authorized region. Do not enlarge the clickable Map to include cleanup background: retain the accepted replacement scene/state separately and derive the Map only from the new target plus its attributable shadow. If removal changes background outside the Map, document the accepted parent/state dependency; do not falsely claim that the Map alone reconstructs the original scene. If no safe same-class replacement exists, use a valid independent support or the real container workflow. Replacement does not bypass acquisition classification, physics, or the cross-role identity gate.

Use `ndc-coordinate-image-edit` to create the source-sized authorization mask, legal generation crop, job manifest, and non-destructive composed scene.

The authorization workspace must include:

- the new object;
- its physically necessary contact shadow, reflection, or occlusion;
- a generous portion of the legal support surface for natural integration and model freedom.

For a collectible scene pickup, start from a tight intent mask and expand it into the parent authoring workspace under the base skill's evidence rule: at least `3x` the proposed object bounds on both axes, at least `128 source pixels` on every unoccluded side, and preferably the whole usable tray, tabletop, drawer interior, or floor patch. After generation, derive a separate final composition mask from the actual object, shadow, and necessary support-surface patch; keep at least `64 source pixels` around every unoccluded semantic edge. The composition mask must remain inside the parent workspace but must not include unrelated model drift merely because the parent workspace allowed it. Do not include characters or protected architecture. Never rescale or crop the full scene after placement.

For a `scene-pickup`, the base-skill prompt must state the `map-scene contract` and must explicitly require:

- ordinary physical scale inferred from nearby furniture and the support surface;
- orientation along the scene's existing vanishing lines, rather than toward the viewer;
- placement outside doorways, principal aisles, and other required movement routes;
- full physical contact with the support surface, including a consistent contact shadow and any necessary occlusion;
- a solid-walled or non-openwork ordinary container unless an approved design or gameplay requirement explicitly calls for open mesh or perforation;
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
- the prop blocks a doorway, principal aisle, furniture-to-furniture passage, or another required movement route;
- the prop is floating or partially floating, or its support contact and contact shadow do not prove a stable resting surface;
- the prop is materially oversized relative to comparable real-world objects, furniture anchors, or scene depth;
- the camera should not reveal the interior of a container, but the candidate tilts, opens, lowers, or protrudes the contained item to expose it instead of using the Type 6 -> Type 7 container chain;
- an ordinary trash can, wastebasket, bin, or similar container is rendered as open mesh or another openwork design without an approved or gameplay-specific reason;
- environmental storytelling is moved into a Type 7 secondary menu instead of remaining in the base scene or a genuine scene state;
- any semantic part of the prop or its contact shadow is clipped by the parent workspace or comes within `64 source pixels` of an unoccluded final-composition hard-mask edge.
- a freestanding container fails the completeness check: its opening or rim, both unoccluded side walls, bottom or base ring, and contact shadow must remain visibly complete and separable at gameplay size. Natural occlusion is allowed only when caused by an existing scene object and recorded in the placement contract; touching a mask boundary, visually dissolving into a same-value background, or merely passing pixel-containment checks is not acceptable.
- either `STYLE_LOCK_GATE` or `TEXTURE_COHERENCE_GATE` is `FAIL` or `NOT_CHECKED`; a readable object class does not excuse style drift, fragmented material texture, repeated marks, random micro-detail, or an in-scene object rendered with Big/Icon information density.

Inspect this at the full scene's expected gameplay display size, not only in a zoomed crop. Pixel containment is necessary but is not visual approval.

For every freestanding prop or Type 6 container, run a separate `SHADOW_COVERAGE_GATE` before hotspot extrema are registered. Start from the accepted full native scene, not an inherited object crop; inspect the untinted parent at whole-image `100%` and local nearest-neighbor `200%` or greater. Record three independent masks: `BODY_MUST_COVER`, every visible attributable contact/cast-shadow region as `SHADOW_MUST_COVER`, and each foreground object as `FOREGROUND_MUST_EXCLUDE`. The final semantic target is `(BODY_MUST_COVER union SHADOW_MUST_COVER) minus FOREGROUND_MUST_EXCLUDE`. A foreground object removes only the pixels it actually covers: if the target shadow remains visible on the far side, keep that continuation even when it becomes a disconnected Alpha island. The loose selection, four-extrema rectangle, base contour, and final post-exclusion Alpha must cover every visible must-cover region. Parent-pixel equality, non-empty Alpha, and internally consistent bounds cannot pass this visual gate when the visible shadow is clipped.

### 4. Prepare the standalone evidence image

Keep two outputs conceptually separate:

- Map Sprite: a rectangular PNG canvas whose preferred clickable content is an irregular RGBA silhouette. This rule applies equally to direct pickups, environmental hotspots, Type 6 scene-container entrances, and clickable children inside Type 7. Treat the target and its own visible contact/cast shadow as one selection union. The final Alpha may contain multiple disconnected islands when a foreground occluder splits the object or its shadow; never keep only the largest connected component, require artificial connectivity, or delete a visible far-side continuation. For obliquely viewed paper, receipts, books, folders, and other planar objects with visible thickness, the target union includes the top face, every visible side/edge-thickness plane, curled or lifted edge, lower edge, and attributable shadow; never segment only the high-contrast top face because adjacent target planes resemble the supporting pile. First create a deliberately loose source-resolution working selection around the complete multi-island union; this selection is an inspection range, not the final hotspot. Run `PRE_EXTREMA_VISUAL_COVERAGE_GATE` against the accepted full native parent at whole-image `100%` and local nearest-neighbor `200%` or greater: every visible target plane, low-contrast edge, and full attributable shadow must sit inside the working selection with visible breathing room and must not touch or cross its boundary. `FAIL` or `NOT_CHECKED` blocks all extrema work. Only after this gate passes, independently mark the visible semantic union's topmost, bottommost, leftmost, and rightmost points, construct the tight outer rectangle, and trace separate body/shadow base contours inside it. Never derive the rectangle only from an inherited object crop or an unverified single polygon. Visually review the base-contour overlay and require it to contain all four extreme points before expansion. Base-contour completeness has priority over expansion: expand the passed complete base union by a visually chosen `2` or `3` Photoshop pixels. A `5px` expansion is an asset-specific trial only, requiring untinted parent/edge comparison; it is never the global default. Inspect the added pixels in the untinted parent and side/edge views; the margin may include necessary antialiasing, low-contrast thickness, or shadow softness, but it may not justify an incomplete base contour or retain unrelated background/support pixels. Then subtract every foreground object or container edge that occludes the target from the expanded mask. Foreground exclusion overrides the chosen margin only where that foreground object actually covers the target; preserve any visible target or shadow that continues beyond it. Recompute the final Alpha canvas from all surviving islands and require every declared semantic extreme point to remain selected after exclusion; if an extreme was actually hidden, correct the semantic extrema instead of retaining a pre-exclusion point. Visually review the untinted parent, final parent overlay, checkerboard export, Alpha-only export, four edge crops, and a trusted-reference missing-pixel comparison when available. Preserve accepted parent pixels inside Alpha, write zero RGB under Alpha 0, and set `Position` to the final post-exclusion union's top-left. Exclude unrelated background, container rims, supporting piles, and foreground objects occluding the target unless they are necessary to identify or physically select it. A user- or artist-authored native-pixel RGBA reference may be used directly for that same asset after coordinate, parent-RGB, Alpha, transparent-RGB, and occlusion verification; one reference does not waive visual gates for other assets. A full rectangular exact crop is a documented compatibility fallback, not the default hotspot. Alpha bounds, hashes, polygon bounds, connected-component counts, and self-consistent masks are technical evidence only; they cannot set a visual gate to `PASS`.
- Map acceptance also requires the anti-omission and neighbor-isolation procedure in [references/hotspot-semantic-review.md](references/hotspot-semantic-review.md). Never bridge separate documents with a bounding hull that selects the container between them, and never interpret black display background as proof that an internal transparent region is intentional.
- Detail image: the standalone evidence view used by `desSpritePath`. Prefer a separately approved transparent detail render when legibility or presentation requires it. Otherwise use a clean source/crop-sized alpha mask to extract the accepted object.

When an approved RGBA reference has the correct final hotspot Alpha but its RGB came from a review export or no longer equals the accepted scene, use it only as an Alpha authority. Run `scripts/irregular_map.py rebuild-reference --parent <accepted-full-scene.png> --reference <reviewed-final-alpha.png> --output <map.png> --report <verification.json>`. The command must find one confident same-scale translation, crop from all surviving Alpha islands, take every Alpha-positive RGB pixel from the accepted full native parent, and zero RGB below Alpha 0. The reference Alpha must already represent the visually approved complete base, recorded asset-specific expansion, and post-expansion foreground exclusions; do not expand it a second time. A low-confidence or ambiguous registration blocks production. The technical report deliberately leaves visual approval to the required parent overlay, Alpha-only, checkerboard, edge-view, and stage visual-review gates.

The detail image may be a clearer view than the in-scene object, but identity, material, damage, labels, handedness, and state must match.

The detail image is the only default location for close-reading content. It may face the viewer and present exact text clearly; the matching map object should preserve the same identity and state without duplicating that information density.

Do not send the `2560 x 1600` three-frame guide to Unity. It is a measurement and layout workspace only. Finalize an ordinary transparent Big as exactly one selected frame: portrait `571 x 1000`, square `818 x 818`, or landscape `1000 x 571`. An `environment` Big instead follows the content-led irregular environmental-observation profile in [references/detail-icon-production.md](references/detail-icon-production.md), uses no post-production rotation/tilt, and may use an ordinary frame only when its runtime contract explicitly assigns one. Finalize an Icon as `130 x 130` RGBA with all visible prop and shadow pixels inside the fixed `115 x 115` safe rectangle. A clue Polaroid remains `620 x 620`; its frame is locked and the photo is perspective-composited through the canonical window mask. The exact coordinates, commands, alpha rules, and review sizes are in [references/detail-icon-production.md](references/detail-icon-production.md).

### 5. Package deterministically

Run:

```powershell
python scripts/evidence_delivery.py package `
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
  --output-dir <image\edit_jobs\job\delivery>
```

Use `--cutout-mask` instead of `--detail-image` only when the standalone image must be extracted from the accepted final scene. Production packaging requires an independently approved `130 x 130` RGBA Icon and its passing report from `evidence_art.py verify-icon` or `finalize-icon`. If the current runtime record intentionally has no `iconPath`, use `--omit-icon` and omit all Icon arguments. The package command must never silently shrink a Big or detail image into an Icon. `--allow-legacy-derived-icon` exists only to rebuild an audited old package and must be explicit in its manifest.

When both the source and accepted final scene are supplied, the script derives the map rectangle and `(x, y)` from the actual changed-pixel bounds, then adds `--map-padding` (default `32`). This deliberately decouples the runtime Map crop from the much larger authorization workspace. When no source is available, it falls back to the authorization-mask bounds. `--map-rect left top right bottom` is only an audited compatibility override for pre-existing baked props. The rectangle is top-left based and half-open. It must contain every changed pixel and all clickable visual content.

For a preferred irregular Map, provide `--map-shape-mask` as a full-parent-size silhouette mask. The packager preserves exact accepted pixels only inside that mask and exports RGBA with zero RGB under Alpha 0. The mask must cover every changed pixel needed to reconstruct the accepted state and may contain multiple disconnected target islands. For Type 7 child Maps, or when only one accepted parent image exists, first save and visually approve a loose working-selection overlay under `PRE_EXTREMA_VISUAL_COVERAGE_GATE`; only then record the four visible extreme points of the verified prop-plus-shadow union and use `scripts/irregular_map.py build --parent <type7-or-scene.png> --polygon "x,y;x,y;..." --shadow-polygon "x,y;x,y;..." --extreme-points "top:x,y;bottom:x,y;left:x,y;right:x,y" --expand 3 --exclude-polygon "x,y;x,y;..." --output <map.png> --report <verification.json> --overlay <review.png>`. Repeat `--shadow-polygon` for every disconnected visible shadow region and `--exclude-polygon` for each foreground occluder. The command validates extrema against the undilated body-plus-shadow union, applies the explicitly chosen expansion (the example uses 3px, not a universal value), subtracts only the declared foreground regions, validates the declared semantic extrema again on the final post-exclusion Alpha, and reports every surviving connected component without rejecting multi-island masks. These are technical checks; review the base-contour overlay, Alpha-only/checkerboard exports, and the final post-exclusion overlay visually before approval. Convert the final parent-local top-left to full-scene `Position` before registration. In the semantic release contract, bind each `map`/`type6` position to `acceptedParentImage` and `acceptedParentSha256`; the production validator must then prove parent bounds, RGBA mode, exact Alpha-positive parent RGB, and zero RGB under Alpha 0. Equal Alpha, canvas, or position alone is never sufficient: any visible white/black block, stale review RGB, painted repair, or another-parent pixel is a release failure.

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
- for a rectangular compatibility Map, the sprite equals the accepted scene rectangle pixel-for-pixel; for an irregular Map, every Alpha-positive RGB pixel equals the accepted parent and Alpha 0 RGB is zero;
- when the Map is a newly inserted or changeable scene layer, compositing it at `(x, y)` over the source reconstructs the accepted final scene; for a baked-in interaction hotspot, parent-pixel alignment passes and reconstruction is not misused as semantic-completeness evidence;
- the standalone detail image exists and is non-empty;
- when `iconPath` is present, the staged Icon is exactly `130 x 130` RGBA, all visible pixels remain inside `[7,7,122,122)`, transparent pixels carry zero RGB, and the supplied Icon verification report matches the staged bytes;
- when `--omit-icon` is used, the patch, manifest, and artifact list all omit the Icon rather than writing an empty or invented path;
- asset stems and ItemStaticData paths agree;
- staged artifact hashes still match the manifest.
- the asset's `ndc-texture-coherence/v1` record passes `D:\Codex\NDC\scripts\validate-ndc-texture-gate.py`; use `authorized_region_plus_boundary_tiles` for scene insertion and `full_image_tiles` for standalone Type 7, Big, Icon-master, and clue-photo art.

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

Treat a coordinate-bearing Map and its `Position` as one atomic release unit. Any change to the Map Alpha, crop canvas, padding, foreground exclusion, or top-left rectangle invalidates the old manifest entry, every non-history staging/candidate copy, the formal copy, and every matching `XYposition.txt` line. Recompute `x,y` from the new final Alpha canvas; update Map bytes, manifest, release contract, and XY together; then hash-bind the coordinate to that exact Map. Before release, scan the scene's work-process and formal roots for every non-history `XYposition.txt` containing the stem. Every such active package must carry the same current Map hash and coordinate. A stale `formal_stage`, candidate folder, or parallel formal package blocks release; only paths explicitly marked history/rejected/superseded are exempt.

## Unity secondary-menu container workflow

Use this workflow for drawers, safes, lockers, cases, boxes, pockets, bins, and other containers that open into a larger in-scene secondary view.

### 1. Establish the runtime chain

Define all three levels before producing art:

1. Type 6 is the closed or normal-state entrance bound by `SceneConfig`. Its `ActionParam` is the Type 7 item ID.
2. Type 7 is the open secondary view. It is generated by Type 6 and is not directly bound by `SceneConfig`. Its `ActionParam` is the comma-separated list of contained evidence IDs.
3. Each contained evidence keeps its own map/detail/icon contract. The Type 7 view shows only enough information to locate and identify it; readable text and close-reading detail belong in its `desSpritePath` Big image.

Block delivery if any link in `Type 6 -> Type 7 -> contained evidence Map/Position -> contained evidence Big/Icon` is missing.

### 2. Export `prop_<container>1.png` as an irregular scene-container entrance Map

`prop_<container>1.png` is not regenerated artwork. Extract it from the accepted final scene at native resolution, but make its Alpha follow the visible closed/normal Type 6 container plus its attributable contact/cast shadow. Apply the same loose-selection, `PRE_EXTREMA_VISUAL_COVERAGE_GATE`, independent four-extrema, base-contour, asset-specific expansion, foreground-exclusion, and final visual-review sequence used by every other Map.

When Photoshop supplies the contour, use the semantic-path and user/artist-path authority rules in [references/photoshop-mcp-repair-and-framing.md](references/photoshop-mcp-repair-and-framing.md). Structure, material continuity, and actionable-unit ownership outrank local contrast; a user-identified final path must not be silently simplified or expanded.

- For a freestanding container, include the complete visible rim/opening, unoccluded side walls, base/contact area, and attributable shadow. For a container built into furniture, select the complete actionable structural unit—such as the drawer front, seams, and handle—not the whole cabinet or surrounding wall.
- When two drawers, doors, lids, pockets, bins, or other actionable containers touch or share a seam, first use the accepted Type 7 identity to name the exact target unit. List every adjacent interactive unit and prove it is Alpha 0 in the parent overlay. A hotspot that includes any visible face, handle, seam interior, or attributable area of the neighboring unit fails because it advertises a second interaction.
- Exclude unrelated floor, wall, desk, cabinet body outside the actionable unit, nearby furniture, characters, and every separable foreground occluder. Do not restore hidden portions behind them, but retain any visible container or attributable shadow that continues beyond the occluder as a separate Alpha island.
- Preserve accepted scene RGB wherever Alpha is positive, write zero RGB under Alpha 0, and record the final post-exclusion `x`, `y`, `z`, `width`, `height`, and half-open canvas rectangle in the structured manifest.
- Write the same top-left `x,y` to `XYposition.txt`; do not print coordinates into the PNG.
- When Type 6 is a newly inserted or changeable scene layer, alpha-compositing it at `(x, y)` over its frozen source must reproduce the accepted scene state. For a baked-in container used only as a hotspot, verify native parent-pixel alignment instead; overlaying identical pixels is not evidence that its semantic contour is complete.
- Never estimate or manually transcribe the coordinate from a review screenshot. Derive it from the accepted native-resolution scene and the final Alpha canvas.
- A pixel-exact rectangular Type 6 screenshot is allowed only for an audited legacy/runtime limitation and must be labeled as a compatibility fallback, not as the default hotspot.

### 3. Author `prop_<container>2.png` as the open secondary view

The Type 7 image is independently authored from the physical identity of the Type 6 container. It is not a magnified crop of `prop_<container>1.png`, but it is a first-person, source-derived close inspection of that actual place: retain the visual environment and camera-height consequences predicted by the frozen original scene anchor.

- Use the actual container height to select downward, level, or upward viewing; do not impose a top-down view merely to make the interior legible. Low coffee-table/trash-bin/floor-container views are standing-player downward views, while high containers can be eye-level or upward.
- Preserve the same material, color, construction, wear, handedness, handle placement, opening direction, and immediate environmental anchors as the container in the scene.
- Use one direct Image composition for the opened container and every visible child. The child must be fully supported and identifiable inside it; never paste the Big into the view or leave only a corner exposed. If the view is otherwise correct but irrelevant environment occupies too much area, reframe only the complete borderless interior through Photoshop MCP; never transform the white frame.
- Keep the container complete and make the interior readable, but do not turn the evidence inside it into a detailed product shot. Small writing remains unreadable; exact text and puzzle metadata stay in Big images.
- Apply the paper-and-file information-density rule above to document children: a Type 7 may legitimately show a reverse, fold, partly obscured state, or overview with no readable writing. Retain physical identity and let the approved Big carry exact readable information.
- Determine and visually approve the borderless interior image's final pixel size and framing before adding the required border. When reframing is necessary, preserve container identity, every required child, physical support, and enough local environment to prove source derivation. Do not resize after border application.

The accepted Type 7 view is also the coordinate truth for its contained evidence. Each clickable child must be fully visible and separable at gameplay size. Do not use generic paper piles, generic cards, or an empty container as a stand-in for several distinct contained items.

U1 is the sizing reference, not a rigid global clamp. Across the audited U1 drawer/cabinet pairs:

- Historical Type 6 source crops range from about `60-296 px` wide and `40-160 px` high, with a median near `148 x 74 px`; use these only as scale context, not as permission to retain rectangular runtime hotspots.
- Type 7 final images range from about `272-456 px` wide and `252-484 px` high, with a median near `410 x 356 px`.
- Start an ordinary drawer near `400 x 360 px` final size, then adjust for the container's real aspect ratio, interior contents, available scene space, and gameplay readability. Never enlarge an object merely to expose detailed writing.

### 4. Export every contained evidence Map

For every evidence ID in the Type 7 `ActionParam`:

1. On the accepted final bordered Type 7 image, treat the child and its own visible contact/cast shadow as one union. Create a loose source-resolution working selection around the entire union; it is not the final hotspot.
2. Run `PRE_EXTREMA_VISUAL_COVERAGE_GATE` at whole-image `100%` and local nearest-neighbor `200%` or greater. Require the complete child, low-contrast edges, and its full attributable shadow to remain inside the working selection with breathing room. If any target pixel touches or crosses the boundary, enlarge or correct the working selection and repeat the gate. Do not mark extrema while the gate is `FAIL` or `NOT_CHECKED`.
3. From the visually verified complete union, independently mark the topmost, bottommost, leftmost, and rightmost pixels and build the tight outer rectangle.
4. Trace the union's currently visible base contour inside that rectangle using the Photoshop semantic-path workflow when applicable. The base contour must select all four declared extreme points. Exclude the container rim, surrounding pile, and objects above the target whenever separable. Use a concave union or multiple islands for compound evidence and preserve physically real negative spaces; never replace it with a convex hull or bounding rectangle. Never invent pixels behind an occluder. Visually review the base-contour overlay before expansion. If the user/artist explicitly marks the native Photoshop path as the final contour, do not apply a second expansion.
5. After the complete body-plus-shadow base contour passes, expand it outward by the reviewed `2` or `3` Photoshop pixels (`5px` only for a justified asset-specific trial) unless a user/artist explicitly identified the current native path as the already-final contour. Never expand that final authored path a second time. Then subtract every foreground object or container edge that sits in front of the child; do not let expansion reintroduce an occluder, but retain every visible continuation beyond that occluder even when it becomes a disconnected Alpha island. Export the post-exclusion union extent as an RGBA canvas with accepted Type 7 pixels inside the final contour and transparent zero-RGB pixels outside it. Visually review the untinted parent overlay, Alpha-only view, checkerboard view, and transparent export together. A rectangular exact crop is allowed only as a documented compatibility fallback.
6. Convert the Type 7-local crop origin to the full-scene coordinate system:

```text
childX = type7X + localCropLeft
childY = type7Y + localCropTop
```

7. Write `[childX, childY, childZ]` to the child's `Position`. Never leave `mapSpritePath` or `Position` empty for a contained exploration pickup.
8. Verify that the pre-extrema coverage gate has visual evidence, the undilated body-plus-shadow base union contains all four declared semantic extreme points, the final contour applies the recorded asset-specific expansion to that base (or zero additional expansion for an authored final path), every declared extreme remains selected after foreground subtraction, all visible disconnected target islands survive, foreground exclusions remain absent, the expanded child canvas lies completely inside Type 7, every Alpha-positive RGB pixel equals the parent Type 7 pixel at that coordinate, all Alpha-zero pixels have RGB zero, and Unity generates/uses the Sprite Physics Shape through `PolygonCollider2D`. Visual transparency, a self-consistent polygon bound, or keeping only the largest connected component does not prove the hotspot is complete.

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

- irregular `prop_<container>1.png`, its final Alpha canvas rectangle, Type 6 `Position`, four-extrema record, expansion/exclusion record, and visual-gate evidence;
- the approved borderless Type 7 source retained for recovery;
- final `prop_<container>2.png`, its independent Type 7 `Position`, center-anchor calculation, and 12-pixel border declaration;
- the Type 6 and Type 7 ItemStaticData draft rows;
- every contained evidence Map crop, full-scene `Position`, Big, configured Icon, ItemStaticData draft row, and Map-to-Type-7 alignment verification;
- the contained evidence IDs and proof that only Type 6 is bound by SceneConfig;
- parent-pixel/alignment verification for every Type 6, reconstruction verification when Type 6 is a changeable scene layer, and border/placement verification for Type 7.

See [references/delivery-contract.md](references/delivery-contract.md) for the container manifest and coordinate example.

## Staging and synchronization

Default engineering staging to `image/edit_jobs/<job>/delivery/`. This working package may contain manifests, verification JSON, overlays, patches, and recovery inputs. Never overwrite the approved scene or write directly into `D:\NDC\Assets\Resources\Art\Scene\EVIDENCE` during generation.

Keep the eventual formal image-asset folder separate from engineering staging. Each asset-facing folder contains only accepted/final PNG image assets plus one ASCII `XYposition.txt`. A complete scene-prop package must include the accepted full-scene placement preview as a formal PNG, every required Type 6 and Type 7 image, every contained or direct-pickup Map, every required Big and configured Icon, and every requested environment/state image. The coverage ledger defines the required image roles; "only PNG plus XY" is a file-type boundary and must never be interpreted as permission to publish only the assets changed in the latest revision. An explicitly requested single-asset delivery may be incremental, but it must not be labeled a complete formal scene delivery.

Before formal transfer, create the process-only `ndc-formal-release-contract/v1` defined in [references/delivery-contract.md](references/delivery-contract.md), deriving its records from the authoritative acquisition coverage ledger rather than from filenames or the files that happen to exist. Run `scripts/validate_formal_release.py --folder <formal-folder> --release-contract <contract.json> --report <process-report.json>`. This production gate derives required roles from each `deliveryClass`, requires source citations and classification reasons, binds `XYposition.txt` coordinates to current Map hashes, checks every formal artifact hash including XY, and scans the declared scene work-process/formal roots for stale active replicas. `scripts/validate_formal_package.py` remains only a legacy manual-list inspector and is not sufficient for a new production release.

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
