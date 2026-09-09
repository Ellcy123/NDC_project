# End-to-end workflow

## 1. Discover and route

1. Read `canon_manifest.json` for the active Unit/Episode identity.
2. Locate the dialogue/state node, SceneConfig/ArtAsset entry, approved background, current AVG asset, and every approved character card.
3. Classify the request:
   - missing multi-character AVG: run full production;
   - completed AVG: audit only unless the user requests a variant or repair;
   - missing background: stop and route to the scene-background workflow;
   - dynamic multi-panel event: route to the dynamic-comic workflow.
4. Keep Unity and runtime tables read-only unless a later explicit delivery request authorizes changes.

## 2. Direct the frozen story beat

Extract from the actual dialogue/state:

- current cast and any entrances/exits;
- objective and conflict;
- emotional state and subtext;
- action focus and prop ownership;
- speaker/focus character;
- gaze graph;
- one silent-frame statement describing what a viewer understands without text.

Choose a pose family that can credibly be held for ten seconds. Do not freeze a transitional hand-to-hand exchange, a mid-step limb tangle, or a generic upright lineup.

Before blocking, save the active-branch timeline result and choose one `timelineSnapshotId`. For each actor record `presenceAtSnapshot` as `already-present` or `enters-now`. Dialogue order is not entrance order: a person who first speaks later may already be standing in the room. The simultaneous cast must match the chosen snapshot exactly.

## 3. Choose composition side

Choose either a left-half or right-half cast cluster after the dramatic relationship is understood. Locate the actual dialogue-UI image used by the scene or derive its mask from the engine prefab. Record its path, SHA-256, top-left placement, and whether the engine mirrors it for the selected side. `uiSide` states which UI variant is active; it is not a substitute for the source asset or overlap report.

Use depth and asymmetry to create a readable relationship:

- triangle, wedge, enclosure, blocked exit, dominant foreground, or separated witness;
- unequal depth and head sizes where the scene supports them;
- clear negative space on the lower-cost UI side;
- no face, critical hand, or prop hidden by the selected UI.

Run the parent tool's `validate-ui-safety` route against the real UI before approving a whitebox. Save both the JSON report and visible overlay. Review actor and UI geometry on the original source canvas; a hand-made rectangle is acceptable only when it was derived from the true asset bounds and recorded as such.

## 4. Apply multi-character blocking rules

- The current snapshot has `N` simultaneous actors; `N` is not fixed.
- For `N >= 3`, include at least one clear back/three-quarter-back foreground actor, normally half-body with feet outside the frame.
- A two-person scene does not require a back-facing actor.
- Prefer standing actors. Record why a seated actor is necessary and name the chair/bed/support.
- Keep every actor's limbs and props independent. Projection overlap may be used only when silhouettes, faces, and actions remain readable; physical contact is not allowed by default.
- Assign every gaze to another actor, an owned prop, or a named scene landmark.
- A prop is held by one owner close to that actor. Avoid a passing/receiving pose.

## 5. Create and approve whiteboxes

### 5.1 Lock identity and absolute scale first

Before drawing final mannequins:

1. Read each actor's canonical integer height from the current character document and record the source path and hash.
2. Measure the approved character card's full-body pixel height and anatomical-head pixel height. Record body-build notes so a lean actor is not replaced by a generic broad-shouldered mannequin.
3. Select at least three independent fixed-object groups in the untouched scene. Together they must include horizontal and vertical measurement lines, at least two depth bands, and both actor-local and cross-depth evidence. For every line record both canvas endpoints, the plausible real-world centimeter range, the assumption, and confidence. Record the horizon/projection model used to compare depth bands.
4. Run `validate-scene-absolute-scale`; do not proceed if it recommends a global size correction outside the accepted tolerance.
5. Project each actor's canonical height from the named support point and depth. Record standing-equivalent pixel height, anatomical head box, and the approved card reference, then run `validate-cast-scale` with `headScalePriority: true`.

Absolute scene scale answers “is the whole cast too large for the room?” Cast-relative scale answers “are these particular people the correct sizes relative to one another?” Both must pass.

### 5.2 Record exact anatomy, support, and occlusion

For every actor, record the silent-frame verb, beat energy, ongoing occupation, performance family, action, emotion, facial expression, body line, weight distribution, both-hand motivations, named support, social territory, action focus, subtext, costume state, prop continuity, depth honesty, head box, neck, shoulders, elbows, hands, hip center, knees, feet, outer action box, support point, facing, gaze target, and whether the pose can be held for ten seconds. Off-frame landmarks are still recorded on the shared coordinate system.

Name and validate the support or affordance. A back-facing half-body actor normally stands on an off-frame floor; hide the feet by foreground framing and depth, not by compressing or crouching the mannequin.

Record every unordered actor pair in the occlusion graph, including pairs with no overlap. Also record any rail, plant, counter, doorway, or furniture that must later be restored from exact source pixels above an actor layer.

### 5.3 Build linked whiteboxes

Create one combined character-preview whitebox and one isolated whitebox per actor:

- preserve the fixed camera and recognizable scene topology;
- use realistic 3D anatomical mannequins rather than sticks, rectangles, or silhouettes;
- allocate one distinct medium-saturation color per actor;
- treat the color as a local segmentation label only;
- keep pose, joints, head box, occupied volume, support, depth, and transform identical between combined and isolated versions;
- show the complete anatomy in the isolated whitebox even when the combined view is partially occluded;
- preserve a stable actor-color mapping across the current scene handoffs.

The combined and isolated files must equal the source-scene canvas size. Record the source, combined, and isolated SHA-256 values. Each isolated actor must match the combined actor's color, exact landmarks, support point, occupied volume, and transform; it is not a fresh pose generation.

Review head sizes first, then full height, perspective, support, gaze, action, contact, UI, and dramatic readability. Save a 100% whole-frame inspection plus 200% local crops for every head, hand/prop, support, and overlap region. Only after the timeline, UI, absolute-scale, cast-scale, support, occlusion, artifact-linkage, and visual-review reports pass may the plan move to `whitebox-approved` and receive user approval.

## 6. Prepare one local handoff per actor

Use the general integration tool:

```powershell
python ../ndc-character-scene-integration/scripts/scene_staging_tools.py `
  prepare-local-generation-handoff <actor-handoff-request.json> <output-dir>
```

The scene and isolated whitebox must share the same calibration canvas. Correct size/path errors instead of bypassing the gate.

Attach references in this exact order:

1. local crop containing only the approved actor whitebox;
2. untouched full scene;
3. approved full character card.

The local crop controls pose, occupied volume, position, depth, support, and action envelope. The full scene controls light, palette, perspective, and color grade. The card controls identity, body type, costume, accessories, and line language.

When the source is 16:10 and the generator returns 3:2, use the calibrated-bar procedure from the general integration prompt module. Never silently stretch the scene.

## 7. Generate actors sequentially

Generate exactly one actor per result, even in batch mode. State both hands, gaze target, support, prop ownership, framing, and prohibited contact. Include the complete NDC style and texture module rather than a loose phrase such as “match noir style.”

Reject before Photoshop when any of these fail:

- recognizable identity or costume;
- whitebox pose/volume/position;
- gaze target or facing;
- prop owner and non-handoff action;
- scene-derived light/color grade;
- line weight, black masses, hair language, or texture density;
- extra people or generated fixed objects.

Retry only the failed actor from the frozen handoff. Do not chain from a failed contextual result.

## 8. Extract and register in Photoshop

Follow [photoshop-and-qa.md](photoshop-and-qa.md). Each actor receives:

- contextual candidate;
- raw transparent cutout/PSD;
- hidden unmodified registered backup;
- visible edge-clean layer;
- one recorded uniform scale and translation;
- separate contact/cast shadow where required.

Full-body actors register from named foot/support landmarks. Cropped foreground actors register from head size plus approved frame-edge/bottom anchors. Never apply a universal 90% rule.

## 9. Assemble and inspect

Recommended layer order from top to bottom:

1. foreground actors and required foreground occluders;
2. midground actors;
3. per-actor contact/cast shadows directly beneath their owners;
4. exact-source scene occluders;
5. untouched original background.

Inspect:

- full frame at 100%;
- each face/hair/glasses region at 200%;
- each hand/prop/contact region at 200%;
- actor-to-actor spacing and occlusion;
- head-size ratios and absolute scene scale;
- UI side and negative space;
- edge color, shadows, lighting, style, and texture coherence.

Save final gaze, background-preservation, and visual-review reports. Background preservation means all pixels not covered by approved actor, loose-prop, shadow, or exact-source occluder layers remain identical to the hashed source scene.

Do not label a final result passed because the PSD/PNG exists. Record semantic and technical results separately.

## 10. Deliver

Deliver at minimum:

- layered PSD on the original scene canvas;
- flattened PNG on the original scene canvas;
- cast plan and registration log;
- approved combined and isolated whiteboxes;
- contextual candidates and raw cutouts;
- 100% full-frame and 200% local review images.

Do not copy to Unity until explicitly asked.
