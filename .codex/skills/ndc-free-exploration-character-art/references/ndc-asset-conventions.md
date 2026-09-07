# NDC transparent character asset conventions

## Source locations

- Active narrative and character profiles: `{PLANNING_ROOT}/剧情设计/Unit*/人物设定/` (exclude archived/backup/deprecated trees)
- Requirements: `{PLANNING_ROOT}/`; task documents: `<job>/payload/`
- Character cards: `{PLANNING_ROOT}/美术资产交付/角色/角色索引.json`
- Scene backgrounds: `{ENGINE_ROOT}/Assets/Resources/Art/Scene/Backgrounds/`
- U1 free-exploration references: `{ENGINE_ROOT}/Assets/Resources/Art/Scene/NPC/EPI01/`
- U2 free-exploration references: `{ENGINE_ROOT}/Assets/Resources/Art/Scene/NPC/EPI02/`

Resolve paths from the active workspace instead of assuming another `_project` directory exists.

For canonical height, `{PLANNING_ROOT}` is intentionally the first authority when it exists. Writing one missing art-unification height field into the active character profile is part of the character-scale workflow and is not a formal Unity table edit. Never put the new authority only in `旧文档`, `_archive`, `backup`, `备份`, or `废弃`.

## State pairing

Existing NDC free-exploration NPCs normally use:

- `ResPath`: idle sprite, commonly filename suffix `1`;
- `ClickResPath`: click/selected sprite, commonly filename suffix `2`;
- `ShadowPath`: optional separate shadow.

The two state sprites should use the same transparent canvas. Keep visible scale, feet, and body center stable so the state swap does not jump.

Use U1 references to learn rendering density, silhouette clarity, lighting integration, state difference, and transparent padding. Do not copy their identity, costume, or unrelated pose.

For AVG-layer mode, do not assume `ResPath`/`ClickResPath` or a two-state pair. The required state set comes from dialogue staging, such as `enter`, `intervene`, `talk`, `action`, or `exit`. Every delivered state for the same controlled character should share a compatible transparent canvas and coordinate contract unless the staging explicitly moves the character to a new position. Record the first/last visible dialogue node and replacement behavior for each state.

## Coordinate semantics

NDC scene coordinates use a top-left origin with Y increasing downward. Runtime placement calls `SceneMgr.ConvertMapPosToWorldPos(mapPos, sprite.rect)`, so the configured `PosX/Posy` describes the top-left of the sprite canvas before Unity converts it to the sprite center.

Important consequences:

- record the actual source-background dimensions;
- do not assume every scene is `2560x1440`;
- distinguish the visible subject bounding box from the transparent sprite canvas;
- keep all switchable character-state and shadow canvases identical when practical;
- derive final `PosX/Posy` only after packaging/cropping the sprite canvas.

Backgrounds in the project include sizes such as `2560x1600`, `2996x1600`, and `3328x1600`. Use the current image's real dimensions.

## Formal-scope boundary

This skill stages and verifies art only. It must not:

- overwrite files under `Assets/Resources/Art/Scene/NPC/` during a test;
- edit `res/xls/*.xlsx`;
- hand-edit generated JSON or runtime bytes;
- create or change `SceneConfig`, NPC loop rows, resource paths, Unity `.meta`, or import settings.

When the user later requests formal mounting, treat that as a separate authorized task and use the project's `unity-table-edit` workflow. Excel remains the source of truth.
