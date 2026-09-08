# 阶段专业操作细则

本文件从既有道具 Skill 按职责迁移。流程顺序、信息A/B/C、总重试计数和审核复用以本阶段 SKILL.md 及共用批次协议为准。这里的细则只在本阶段执行：提及其他阶段的产物表示交接依赖，不要求提前制作。CLI示例中的 ../ndc-scene-evidence-placement/scripts/ 应解析为同级 Skill 的绝对路径，不依赖终端cwd。

## Every open-container state belongs to the secondary menu

Any container's open state must be presented in the secondary menu (the Type 7 presentation contract), never as an opened base-scene prop, full-scene event state, or an ordinary Big used to bypass the menu. This also applies to dialogue/AVG grants and scripted opening, inspection or handover: narrative choreography does not create an exception. Retain the accepted closed/normal scene carrier and show its opened interior through the first-person, character-free secondary-menu view. Preserve a normal opening-free ambient carrier where appropriate; do not confuse a permanently open surface such as a trolley shelf with a newly authored container-opening state.

Keep acquisition semantics distinct from presentation: an existing AVG grant may trigger the secondary menu without inventing a new exploration click, reward or acquisition order. For an actual exploration container, retain the Type 6 entrance → Type 7 interior → child item chain. Record the real trigger and required integration work. Reassess every existing open-container image against this rule; preserve history and independently sound closed-state assets, but a former scene-state PASS cannot authorize reuse as an open scene image. A secondary-menu conversion must pass its own viewpoint, size, direct-generation, frame, identity and child-coverage gates; renaming a distant scene crop does not accomplish that conversion.

## Carrier before dependent evidence art

When evidence depends on a scene carrier or support (such as an archive trolley, desk, shelf, drawer, or case), establish that actual carrier in the approved scene **before generating dependent evidence placement, observation/Big, or Type 7 art**. First inspect the scene and provenance for an existing accepted carrier; reuse it when present. If it is missing, produce and approve its scene placement first. A generic carrier invented in a close-up is not a scene anchor, and a promise to add it later does not pass this prerequisite.

Record `carrier_scene_anchor`: scene ID, accepted full-scene path/hash, native carrier region, physical identity/construction, scale and support/contact, attributable shadow, lighting, access/movement clearance, and current whole/local visual-review evidence. Then derive the evidence states and near view from that carrier. Preserve the actual scene's geometry and camera-height consequences; do not force a carrier into an unsuitable location just to match a previously invented close-up. Evidence without a scene-dependent carrier follows its own acquisition contract and does not need an invented one.

This is a production dependency, not a blanket rejection of existing art. When correcting a reversed sequence, reassess each role separately: retain an independently accepted or user-retained Big/Icon and complete evidence master if their content, identity, construction, style and technical gates still pass. Record the missing scene carrier and cross-view verification as separate unfinished work. After the carrier passes in-scene review, compare the retained roles against it and remake only a role with a demonstrated incompatibility. Do not regenerate a sound Big merely because the carrier was produced late, and do not equate retaining that Big with completing the scene package.

### Fit new carriers into the existing layout

Treat newly added carriers, trolleys, bins and comparable support objects as part of the existing room arrangement. By default, park them alongside a wall, the side/end of existing furniture, or another credible workstation edge. Avoid isolated placement that divides the open floor, splits the reception area, or introduces a new circulation obstacle merely to make the object visible. Judge adjacency, actual use/retrieval access and spatial continuity before camera visibility, lighting or pixel containment; naturally justified foreground occlusion is acceptable.

An explicit placement in narrative/design copy is a requirement to evaluate, not automatic proof that the location works. Reassess it against the approved scene and choose a reasonable compromise that preserves the required action and evidence identity while fitting the layout. Record the tradeoff; do not invent unseen entrances or silently change indispensable story/interaction facts. Depart from the adjacency preference only for a justified special requirement whose placement remains physically and compositionally credible. A conditional carrier stays in its required event state rather than becoming permanent background dressing.

### Type 7 source-anchor, viewpoint, and direct-composition lock

For every `container_type7*` stage, the record must also contain a `type7_visual_context` object with: the real container identity; a written derivation of the visible environment from the frozen original-scene anchor; `height_class` (`low`, `mid`, or `high`); `observation_direction` (`downward`, `level`, or `upward`); a first-person viewpoint rationale; the literal method `direct_image_generation`; and `child_fully_contained: true`. A passing Type 7 record must bind a hash-checked `original_scene_visual_anchor`, a `source_anchor_side_by_side` image, and applicable passing criteria named `mandatory_direct_image_container_rule`, `source_anchor_visual_comparison`, `container_height_and_observation_direction`, `visual_self_check`, plus a child/container identity-and-full-visibility criterion. `validate-ndc-stage-visual-self-check.py` enforces these fields; missing evidence blocks the stage.

The mandatory production order is: **accepted in-scene carrier anchor → approved or revalidated existing Big → actual whole/local visual PASS → Image directly generates the opened container, its child, and the derived environment together → optional borderless-interior Photoshop MCP reframe when only irrelevant environment is excessive → Type 7 whole/local/source-anchor comparison PASS → add the 12px frame → derive the child Map**. The Big-first dependency is relative to Type 7, not permission to invent a container in a Big before establishing its scene identity. Never paste, warp, or deterministically composite the Big into a container after generation. A permitted reframe may only uniformly enlarge/reposition/crop the already direct-generated borderless composition and must follow the Photoshop reference; it never includes the white frame. The image prompt for every opened-container or contained-item state must literally include: `第一人称视角、打开XX、近距离观察XX内、特写场景`. Replace `XX` with the actual container and add the source-derived environment, physical support, full containment, and prohibition on exposed corners.

Choose viewing angle from the container's real source height, not from a default top-down template. A low coffee table, trash bin, wastebasket, floor box, or floor drawer requires a standing-player downward view. A mid-height drawer, wardrobe pocket, or desk organizer uses only the amount of downward/level view that the real height supports. A high shelf, upper cabinet, or high-hung container may require eye-level or upward observation. State this derivation in both the prompt and review record; if a candidate's camera contradicts the actual height, reject it even when the contents are readable.

The source/Type 7 comparison is a visual derivation, not a parameter or furniture-count check. Inspect side by side whether the source predicts the Type 7's actual furniture geometry, materials, adjacency, depth, lighting direction/value, and camera height. A generic desk, drawer, tabletop, or room with a similar object count fails. For transformable near-success placement use one supported low-cost correction first. Further generation consumes the remaining shared scene/menu job budget; total three including the first, with no reset for location changes or review stages. Never reveal one corner of an item to bypass the problem.

## Container visibility and physical placement gate

Apply this gate before choosing `scene-pickup` versus `container-state`, again before generation, and once more at expected gameplay display size after compositing.

- Prefer solid-walled or otherwise non-openwork trash cans, wastebaskets, bins, and similar ordinary containers. Use an open mesh or perforated design only when an approved design, established scene fact, or gameplay requirement actually calls for it; convenience in showing the contents is not sufficient.
- Preserve the scene's walkable route. Do not place a prop in a doorway, principal aisle, required path between furniture, or another space the player or staged characters must traverse.
- Treat every item physically inside or held by a container as `container-state`, whether or not the current camera can see into it. Do not tilt the container, lower its rim, enlarge the item, or make contents protrude merely to expose a direct pickup. Keep the closed or normal Type 6 container as the base-scene anchor and reveal the child only in the Type 7 view, where it receives its own Map and `Position`.
- Never route environmental storytelling through a Type 7 secondary menu. An `environment` record must remain legible through the base background or a genuine scene state. If the fixed camera cannot plausibly show it, revise the in-scene placement or narrative presentation rather than hiding it as a container child.
- Require real support contact. The prop must sit on the floor, shelf, desk, or other support surface with compatible perspective, occlusion, and contact shadow; floating and partially floating placement both fail.
- Derive scale from comparable real-world objects, furniture anchors, and scene depth. A prop that reads materially oversized at gameplay scale fails even when its mask, crop, and coordinates are technically valid.
- When a candidate is semantically correct and only slightly wrong in position, scale, rotation, or capability-correctable perspective, classify it as `near_success_transformable` and follow the Photoshop-MCP rescue order: correct once at low cost and visually verify. If blocked or still failing, use only a remaining attempt from the same scene/menu job (three total including the first); a different support is not a new budget. Exhaustion preserves a candidate and returns the blocker. Acquisition rerouting still requires the real design to support it. Record the candidates and failure reason; never simulate a container by showing a child edge in the base scene.

Any failure above rejects the candidate and returns the responsible art stage to the frozen source, except for the explicitly bounded `near_success_transformable` Photoshop-MCP branch. Do not mask, cover, relabel, or arbitrarily shrink a failed composite to hide a structural or semantic error. Record the walkable-space judgment, interior-visibility judgment, support/contact evidence, scale anchors, exact Photoshop transform when used, and any direct-pickup-to-container reroute in the placement contract and acquisition coverage ledger.

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

### 1. Establish the runtime chain

Define all three levels before producing art:

1. Type 6 is the closed or normal-state entrance bound by `SceneConfig`. Its `ActionParam` is the Type 7 item ID.
2. Type 7 is the open secondary view. It is generated by Type 6 and is not directly bound by `SceneConfig`. Its `ActionParam` is the comma-separated list of contained evidence IDs.
3. Each contained evidence keeps its own map/detail/icon contract. The Type 7 view shows only enough information to locate and identify it; readable text and close-reading detail belong in its `desSpritePath` Big image.

Block delivery if any link in `Type 6 -> Type 7 -> contained evidence Map/Position -> contained evidence Big/Icon` is missing.

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
python ../ndc-scene-evidence-placement/scripts/secondary_prop_border.py add `
  --input <approved-final-size-borderless-open-view.png> `
  --output <prop_container2.png> `
  --border 12
```

This places a `W x H` opaque input at `(12, 12)` on an opaque white canvas of `(W + 24) x (H + 24)`. Do not resize or crop the result afterward.

Verify before packaging:

```powershell
python ../ndc-scene-evidence-placement/scripts/secondary_prop_border.py verify `
  --input <approved-final-size-borderless-open-view.png> `
  --output <prop_container2.png> `
  --border 12
```

Verification must prove the final dimensions, all four exact white strips, full opacity, and pixel identity of the inner image. Repair the source or rerun border generation when it fails; do not paint over the report.
