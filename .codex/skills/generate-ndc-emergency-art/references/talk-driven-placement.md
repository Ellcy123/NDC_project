# Talk-driven screen placement

Use this reference when an emergency frame is mounted in AVG dialogue or when the user asks for final image dimensions, XY, `XYposition.txt`, or an in-game layout experiment.

## Determine the active AVG side

1. Locate the exact mount Talk ID in the authoritative workbook: `{ENGINE_ROOT}/res/xls/Talk.xlsx`.
2. Read the `右侧显示` value for the row that actually spawns the comic. Do not substitute the draft JSON's `speakType`.
3. Apply the runtime mapping from `TalkPanel.ApplySide`:

| `右侧显示` / `Talk.isRight` | Active AVG | Preferred event side |
| --- | --- | --- |
| `false` | Left | Right |
| `true` | Right | Left |

If the requirement says "after this line", inspect both that line and the row on which the comic command will be mounted. If a multi-panel comic persists across later Talk rows, inspect the entire visible interval. A later side switch can turn an initially empty lane into a collision; in that case adjust the panel group, end the earlier panel before the switch, or choose another approved presentation.

Use the narrow centre corridor only as a fallback when both sides are simultaneously occupied or the event deliberately needs a central interruption. It is not the default placement.

## Coordinate and size semantics

- `XYposition.txt` stores the frame's intended top-left location in the current scene image's pixel coordinate system.
- The normal TalkPanel/comic layer uses a 2560 × 1600 visible design area, with left and right AVG containers approximately 913 px wide in the current prefab.
- Scene sprites may be wider than 2560. Do not copy a numeric X from another scene blindly; check the current hall sprite dimensions and validate the intended screen-side result in Unity or the actual placement path.
- Comic art begins at its native PNG footprint. Export the final transparent PNG at the intended size; do not depend on `FitToVisibleRect` to turn an oversized generation into the final layout.
- U1 sizes are structural evidence, not mandatory templates. Emergency inserts must stay in compact local-close-up families: face, eyes, hand, prop, pressure crop, strip, or contained localized action panel.

## Prefer focused, cumulative layouts

For an ordinary single-frame event, use a local or extreme-local close-up on the inactive side. Avoid filling the entire free half merely because space exists, and never widen the content into a medium, long, full-body, establishing, or panoramic shot.

For multi-image events:

- assign one narrative beat to each image;
- mix local focal subjects, action details, reactions, and consequences instead of repeating the same framing; every sibling remains a local or extreme-local close-up;
- give each sibling an explicit native size and top-left XY;
- review the union of all panels that remain visible, not each frame in isolation;
- allow overlap only when it is intentional and does not cover the visual hook of an earlier frame;
- keep all cumulative bounds clear of the active AVG lane and important dialogue UI.

Record the Talk ID(s), `右侧显示` evidence, active side, chosen opposite side, native dimensions, XY, and cumulative bounds in the layout experiment. Do not write formal `XYposition.txt` or Talk configuration unless the user explicitly requests delivery.
