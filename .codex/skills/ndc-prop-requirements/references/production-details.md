# 阶段专业操作细则

本文件从既有道具 Skill 按职责迁移。流程顺序、信息A/B/C、总重试计数和审核复用以本阶段 SKILL.md 及共用批次协议为准。这里的细则只在本阶段执行：提及其他阶段的产物表示交接依赖，不要求提前制作。CLI示例中的 ../ndc-scene-evidence-placement/scripts/ 应解析为同级 Skill 的绝对路径，不依赖终端cwd。

## Scene source and output routing

Before selecting an NDC scene source, read and obey the current project's source-search precedence and stop conditions. Keep machine-specific root ordering in project rules, not in this Skill. Match the exact scene ID, chapter, state, and approval lineage; do not silently select a draft, process export, thumbnail, or similarly named scene when the governing source policy identifies an approved source. Record roots checked, exact source path, and SHA-256. If conflicting candidates within the permitted source cannot be resolved from current project records, block source selection instead of guessing.

Resolve current sources through `ndc_art.py paths`: approved planning inputs come from registered paths under `{PLANNING_ROOT}`, runtime sources from read-only `{ENGINE_ROOT}`, and all new authoring material from a dedicated `{WORK_ROOT}/jobs/<任务>/payload/道具/<Unit>/...` directory. Any user-authorized legacy archive is read/copy-only and its actual path belongs only in the device-local configuration or task provenance, never in reusable Skill instructions. Confirmed user-facing deliverables go under `{DELIVERY_ROOT}/道具/<Unit>/...`; engineering synchronization remains a separately authorized copy from those passed assets. Every scene-level work and delivery directory must include a clear Chinese scene/status name, optionally followed by a stable English alias after `__`, for example `SC4002_哈里森外间办公室_白天__Harrison_outer_office_day`. Runtime image stems and `XYposition.txt` entries must still match the configured engineering names exactly; never append Chinese to a runtime filename merely to satisfy the directory-naming rule.

## Preflight inventory and reuse lineage

### Candidate-first routing

For a full-batch continuation, this is per-item method selection, not the batch execution order. First index existing roles and recorded acceptance/rejection to identify gaps. Fill executable missing roles before a general re-audit or rework of old art. Revalidate only a missing role's necessary source/dependency at that point; follow the shared contract for a dependency blocked by old defects.

Before repairing or generating any item, inventory the recoverable scopes below for the scene ID, configured runtime stem, item ID, and clear Chinese/English aliases. These are evidence categories, not a source-search order: first obey the current project's source-search precedence and stop conditions. Do not search a prohibited later source root to replace a hit in an earlier authoritative root. Process/history records may still be inspected to recover approval, rejection, and derivation evidence; finding them does not change the selected source authority.

1. current formal delivery under `{DELIVERY_ROOT}/道具`;
2. accepted semantic masters, staged candidates, and prior technical/visual records in the applicable managed jobs under `{WORK_ROOT}`;
3. recoverable historical, withdrawn, or superseded packages; and
4. user-approved source or delivery assets from the declared read-only project roots.

For every requested item, record the source path and SHA-256, candidate status, applicable visual/technical evidence, delivery-class scope, and exactly one disposition: `reuse current formal PASS`, `promote revalidated candidate`, `targeted non-semantic repair`, `regenerate after recorded candidate rejection`, `new`, or `blocked awaiting source/manual work`. A candidate outside the current formal directory is not absent merely because it is in process history. Validate current technical evidence and strict review reuse (unchanged facts, parents, scope and no rejection) before promotion; do not regenerate a usable candidate simply because a new generation is easier.

Use this routing order: preserve or promote a passing candidate first; when the prop itself has correct identity, structure, required components/state and required readable information, use Photoshop MCP once for every non-prop defect, including people/body parts, background, supporting surface, scene residue, exterior framing, size, placement, rotation, Alpha-margin and cleanup. If that actual isolation output fails visual review, mark it `PROCESS_SOURCE_NOT_CANDIDATE`; it neither counts toward coverage/progress nor feeds downstream work. Do not retry Alpha thresholds on the same failed source: regenerate an independent prop with a truly empty or natively transparent background. When Photoshop lacks the required automated operation, retain the source and capability result; one permitted deterministic mask, crop, coordinate transform or Alpha cleanup may isolate existing pixels without changing the prop, and its visual failure triggers the same empty-background regeneration. A documented prop-semantic/style/construction/text gate failure also returns directly to generation. Never silently weaken the prop-semantic gate.

Evaluate asset and scene scopes separately. A scene Map, hotspot, or Type 6/Type 7 chain failure cannot by itself invalidate an independently user-approved Big/Icon/semantic master. Keep that asset as a recoverable candidate with an explicit scope/status while repairing the scene chain. Do not move, withdraw, or overwrite an approved asset merely because a broader scene package fails; replace it only after that same asset has a recorded current-hash failure or an explicit user-requested revision. Conversely, never label an asset-level reuse as a complete scene delivery until its required scene chain passes.

Do not generate a duplicate merely because a similarly named file is easy to overlook. A prior formal asset may be regenerated only when its current visual record is failed/rejected or when the user explicitly requests a revision; move superseded formal material into recoverable work-process history only after the replacement itself has passed the same asset-level gates.

For a request to reuse a prior-Unit physical prop, locate the actual source PNG/Sprite in the read-only project roots before generating. Copy the source bytes, record source and destination SHA-256, and use that copy as the closed Big/Icon when the requirement is exact reuse. A prose specification, filename stem, or remembered appearance is not an image source: when the authoritative pixels cannot be found after the declared search roots and version history are checked, block that exact-reuse state instead of generating a lookalike and calling it reused.

## Classify before editing

Assign every requested evidence record one delivery class:

- `scene-pickup`: a visible, clickable object obtained by investigating the base scene and resting entirely on an independent support surface. Deliver Map, `Position`, Big, and every configured Icon. A paper, tag, or object partly pushed into a container is never a `scene-pickup` workaround.
- `container-state`: a drawer, safe, locker, case, box, pocket, bin, basket, bag, or similar Unity secondary-menu container. Deliver a scene-exact irregular RGBA Type 6 entrance Map whose Alpha follows the visible closed/normal container and attributable shadow, a separately authored rectangular Type 7 open view, independent coordinates for both, and the complete Type 6 -> Type 7 -> contained-item chain. Every contained exploration pickup also requires its own Map crop and full-scene `Position`, plus Big and every configured Icon. Do not treat the container pair as a substitute for the contained item's Map. A rectangular Type 6 crop is legacy compatibility only and requires a recorded runtime limitation. This remains mandatory even when the current camera can see inside the container; do not reveal a corner or label of the child in the base scene to avoid the chain.
- `detail-only`: an analysis result, memory result, automatic minigame output, or handed-over evidence that is never visible or clickable as a world prop. Deliver detail/icon assets only; do not invent a scene coordinate. A `post_expose`, dialogue, or minigame label alone does not prove this class; inspect the actual acquisition event.
- `environment`: a non-pickup environmental observation. It must remain visibly represented in the background or a state prop. If the player clicks it to discover or record information, deliver its real scene Map/`Position` plus a Big that presents the observed information; omit Icon. Its Big uses the two-mode, content-led irregular Alpha workflow in [references/detail-icon-production.md](../../ndc-scene-evidence-placement/references/detail-icon-production.md), not the ordinary prop's fully opaque rectangular crop by default. Do not infer this class from an `environment` filename when the authoritative event is actually `minigame-only`.
- `minigame-only`: an interaction asset that does not enter ItemStaticData. If included in the user's image-delivery scope, record its actual page/state/component requirements in this batch, produce independent images in stage 2 and scene-dependent images in stage 3, and package separately from evidence records. Do not defer it to an unspecified or unavailable "minigame workflow", invent Map/Icon roles, or silently omit it from total coverage.

Classify from the actual player acquisition event in the matching state, SceneConfig, and ItemStaticData chain—not from filenames, an existing empty `mapSpritePath`, or `pickup` alone. Create an acquisition coverage row for every requested evidence item with: `itemId`, acquisition event, delivery class, visible state, parent container IDs when applicable, Map stem, full-scene `Position`, Big stem, Icon stem or explicit omission, and source references.

Apply this hard gate before art production and again before delivery:

- Anything obtained by clicking or searching the exploration scene must have a visible scene anchor. Big and Icon alone never satisfy an exploration pickup.
- A direct scene pickup requires a non-empty Map and `Position`.
- A pickup found after opening a Type 7 container requires its own non-empty Map and `Position` inside the displayed Type 7 view. Type 6 and Type 7 images do not replace that child Map.
- An item granted automatically by dialogue, Expose, minigame completion, or analysis may omit Map only when it is never left for the player to locate or click. If the event visibly presents the item in the scene, deliver the required conditional/handover state as well.
- A locked or post-Expose cache must be classified by what the player does after it unlocks. If the player opens it and clicks the contents, it is a container exploration chain; if the game grants the contents automatically, document the visible event state and the no-Map reason.

An unresolved acquisition coverage row blocks that item's dependent production/release and the claim of complete batch delivery, not unrelated resolved items. Record the missing fact and affected dependencies, continue all independently executable work, then revisit blocked rows. Preserve independently approved roles without labeling an incomplete item complete. Do not generate Big/Icon-only placeholders to make an unresolved row look finished.

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
