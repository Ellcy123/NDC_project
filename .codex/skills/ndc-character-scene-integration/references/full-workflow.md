# Full character-to-scene workflow and gates

This sequence is mandatory and global to fixed-camera NDC scenes. A later artifact cannot retroactively pass an earlier gate. Codex executes the gates autonomously and does not stop for per-character user approval.

## 0. Runtime branch and input completeness

Classify the asset as `exploration-click-pair` or `pure-narrative`. Read the dialogue, scene configuration, engineering tables, approved background/depth/model references, NPC assets, character profiles/cards, canonical integer heights, states, props, and player-POV rules. Missing branch, height, card, state, or scene timing means `SKIP_SCENE_MISSING_DATA`.

## 1. Engineering lifecycle extraction

For pure narrative scenes, run `extract-timeline` from the current `Talk.json` and `NPCLoopData.json`. Supply every actor present before the start node. Resolve missing nodes, cycles, duplicate enters, exits of absent actors, and missing resources. Record source hashes. Do not edit production tables or guess an unresolved cast.

For exploration NPCs, confirm `ResPath`, `ClickResPath`, shadow path, runtime transform, and whether idle/active resources are distinct.

## 2. Story and directing timeline

For each meaningful snapshot, author objective, conflict, emotion, subtext, action focus, and a silent-frame statement. Record event type, current cast, speaker, UI side, and frozen actors. Run `validate-directing-timeline`.

Block the earliest snapshot first. An uninterrupted actor keeps the same pose, transform, placement, and affordance zone when later actors enter. An actor cannot look, reach, or react toward a future entrant.

## 3. Scene affordance interpretation

Use the fixed background, depth image, and model image to mark ground, support furniture, walkable paths, standing/sitting/lying/leaning zones, reach targets, entry/exit routes, and occluders. A stand/sit zone is an anchor/support region on the ground or furniture, never a vertical full-character rectangle. Author each support contact polyline and an occupancy state from the empty scene/depth/model before placing joints. If a support is occupied by loose cloth, props, papers, bedding, or another object, define whether it is retained, removed, or relocated and name the logical destination. Fixed structural furniture is never part of a generated/scalable actor component. A relocation uses a minimum source-repair mask at the old location and a destination mask for the moved loose object; unchanged furniture occluders come from exact source pixels at scale 1. Run `validate-affordance`, render the map, and run `validate-component-policy` on the planned layer manifest. Choose positions by physical support and narrative value, not empty pixel availability.

For every `enter` event, record a portal and unobstructed entry path around all frozen actors and their supports. If the visible portal is closed, either include and validate the door-opening transition or stage the actor in the first physically reachable post-entry hold; never show a closed door and call a person pasted beside it an entering performance.

## 4. Actual dialogue-UI safety

Treat left and right UI references as alternative placements for a snapshot. After preliminary cast blocking, choose the side with the lower narrative, face, hand, prop, and action-envelope obstruction cost; write that single side into the directing/staging snapshot and validate only its real mask. Re-evaluate when the cast distribution changes, but never shrink a correct actor scale solely to make both mutually exclusive UI sides pass.

Use the real left/right dialogue composition references as masks. Validate each snapshot with `validate-ui-safety`. Faces and declared critical hands/props must be unobstructed; action-envelope overlap stays under the explicit threshold. The opposite-two-thirds shortcut is not a final gate.

## 5. Automated performance blocking

For every visible actor, define silent-frame verb, beat energy, ongoing occupation, performance family, action, emotion, body line, weight distribution, facial expression, motivated purpose for both hands, named support, social territory, facing, gaze, costume state, ten-second hold validity, props, depth honesty, and action target. Start from what the actor was already doing in that room; do not start from a pose preset.

Enumerate ongoing-occupation, supported-hold, transition, and confrontational-action candidates from the current scene affordances. Retain only families authorized by the current beat and lifecycle node. Run `build-blocking-candidates` to generate deterministic joint/box contracts from the approved affordance zone, standing-equivalent scale, retained pose presets, action target, gaze, and actual UI. Review its ranked contact sheet and machine scores. Codex selects or edits JSON and reruns; the browser editor is only a precision fallback. Reject generic upright, symmetrical, camera-facing theater-line poses and low-energy wide-stance/open-hand gestures without a concrete cause.

## 6. Incremental sequence review

Render every meaningful simultaneous-cast snapshot with `render-timeline-board`. Read the contact sheet silently and verify the narrative statement, entrance order, hold-pose continuity, UI readability, and absence of anticipatory or accidental interactions. Freeze accepted existing actors before adding the next entrant.

## 7. Fixed-scene absolute scale, then cast-relative scale

Use at least three independent fixed-scene objects. The set must include horizontal and vertical dimensions and two depth bands: at least one actor-local anchor and at least one cross-depth anchor. Suitable evidence includes doors, window bays/sills, beds, cabinets, chair seats/backs, or other stable architecture/furniture; multiple dimensions of one object remain one independence group. Record the exact image measurement line, real-world range, confidence, perspective basis, source support point, target support point, and projection scale. Run `validate-scene-absolute-scale` and inspect its overlay. If anchor factors disagree beyond tolerance, stop and repair geometry or assumptions. If they agree that the entire cast is too large or small, rebuild every actor whitebox around feet, pelvis, and named support contacts; never resize extracted actors to rescue this gate. The 170cm proxy only visualizes this result.

Only after fixed-scene absolute scale passes, create one shared cast-scale v2 contract for each simultaneous snapshot. Measure each approved-card anatomical head/full-body ratio, project it to the actor support depth, and check actor-by-actor and pair-by-pair head scale before body height. Cast-relative PASS proves internal agreement only and cannot override failed absolute scene scale. Missing height, identity-scale reference, anatomical head measurement, or support depth blocks the gate rather than being silently normalized.

## 8. Exact pose contract

Merge the selected automated blocking fragment into the placement contract. Lock pose ID, action, facing, gaze, both hand actions, props, anatomical head box, neck, shoulders, elbows, hands, hips, knees, feet, support/prop contacts, action outer box, safety margin, support object, affordance zone, and scene occluders. Standing characters require explicit joints; a default upright skeleton is not an action pose.

## 9. Exact-pose 3D mannequin review

Keep locked joints and coordinates in the contract, but do not render a stick skeleton or programmatic block proxy. Review the character-preview 3D anatomical mannequin whitebox at gameplay size with head scale first: check each head against its approved-card ratio and compare every visible pair after depth projection. Only after that passes review story readability, performance naturalism, full-body height, location, pose, contacts, action width, orientation, actual UI, and proposed occlusion. If rejected, edit the contract and regenerate the 3D mannequin whitebox; do not correct it later by resizing the final actor.

## 10. Independent empty-scene depth

Infer horizon, vanishing directions, floor/support planes, furniture volumes, and occluders from the empty approved scene. Generate the fixed-camera depth image, then pair it with the character-preview 3D anatomical mannequin whitebox generated from the same locked placements.

## 11. Character-preview 3D mannequin whitebox

Generate a realistic 3D anatomical mannequin at the final generation position, scale, and pose. Keep the scene white/light gray, but assign each simultaneous actor a stable, distinct, medium-saturation matte material color that separates cleanly from the scene and every other actor; record and reuse that mapping. Produce one isolated whitebox per actor presence and one combined-cast whitebox per simultaneous-cast snapshot. Never combine actors who do not coexist in the lifecycle. Show head scale, shoulder width, torso/pelvis volume, limb thickness, bends, hand direction, prop envelope, support contacts, and occlusion. Reapply scene occluders in the intended layer relationship. New production forbids stick skeletons, joint diagrams, and programmatic geometry-block mannequins entirely.

Before accepting any whitebox, run `validate-support-contact` against the scene-authored contact polylines. Review its overlay to confirm the cyan support lines themselves coincide with the fixed scene/depth support, then require every named contact to remain within tolerance. Red vertical gaps identify floating or sinking and block generation. For lying actors, author `supportPolygon`, `headRegionPolygon`, and `footRegionPolygon` on the support surface. The head center must occupy the head/pillow region, both feet the foot-end region, every anatomical point and body-axis endpoint the support polygon, and the body-axis endpoints must stay near the authored head and feet. A handwritten `supportContactConformance: pass` is not evidence. Covered anatomy remains mandatory whitebox evidence: use a transparent/ghosted blanket, cutaway support layer, or equivalent view so the full mannequin from head through pelvis, knees, legs, and both feet can be inspected against the bed length and foot-end region. Never replace the hidden lower body with only a blanket mound. Separately inspect `environmentResponse`: contact with bedding, upholstery, clothing, cushions, movable props, or another body must produce the expected indentation, rise, wrap, displacement, load, overlap, and contact shadow. For a covered lying actor, the bedding silhouette must describe the hidden torso and legs continuously through the foot-end region; a visible head with a flat or empty blanket is a logic failure even if contact coordinates pass.

For a seated pose, validate the whole movement chain: pelvis is fixed by the seat, each foot is fixed by the floor, knee positions connect those anchors, and foot width/stagger must support the declared torso turn and forward/back lean. Symmetrical wide feet tend to force a frontal stage pose. Record a primary support foot and a small motivated stagger, then keep shoulder line, head turn, gaze, and hand action explicit; feet influence orientation but do not decide it alone.

## 12. Multi-character staging and occlusion graph

For every pair overlapping in the same snapshot, record front character, rear character, allowed overlap region/reason, maximum rear occlusion, and rear face/hand/prop landmarks that must stay visible. For every character, record support/touch/front/behind relations with scene objects. The snapshot combined whitebox must agree; undeclared intersections fail.

## 13. Codex pre-generation semantic and structural gate

Inspect the directing timeline, affordance map, actual-UI previews, automatic blocking report, incremental contact sheet, original-scene proxy, depth proxy, isolated whiteboxes, snapshot combined whiteboxes, per-actor scale table, cast-scale/pairwise-height report, and pairwise occlusion tables together. Codex must review whole images and every local tile, record hashes, pose IDs, comparison reports, and pass/fail results for story readability, performance, lifecycle continuity, affordance, UI, individual and cast-relative scale, pose, contacts, scene occlusion, and cast occlusion. Status becomes `READY_FOR_CHARACTER_GENERATION` only after semantic checks and `validate-whitebox-gate` pass. This is an autonomous gate, not a user waiting point.

Create an `ndc-scene-integration-production-ledger/v2` and run `scripts/production_gate.py` at `pre-generation`. It must reference the actual absolute-scale, cast-scale, support-contact, component-policy, UI, whitebox, and lifecycle reports and hashes. A custom batch or assembly script cannot declare readiness from RGBA mode, canvas size, alpha presence, target-box fit, file counts, or hard-coded `pass` strings.

## 14. Character or interaction-component generation

Create an `ndc-local-generation-handoff/v1` contract and run `prepare-local-generation-handoff`. Choose a generation aspect ratio from the approved action envelope plus required support, occluder, and light context. The tool expands the crop on original scene pixels to that ratio; it never scales the crop. Its three model inputs are fixed:

1. Image 1: a deterministic local crop of the untouched original-color scene with only the accepted actor's isolated anatomical 3D mannequin composited at the locked coordinates; include enough support, nearby object, occluder, and light context;
2. Image 2: the untouched full scene, used only for camera, perspective, full-scene light, palette, and context;
3. Image 3: the approved character card, used only for identity, body type, costume, palette, fixed accessories, brushwork, and line language.

Before cropping, semantically isolate the actor mannequin from the accepted combined 3D whitebox and place it over the untouched original scene using the locked registration. The isolated guide must retain the complete mannequin and authorized prop envelope without room pixels, fringe, or clipped limbs; it is reviewed as a process image and is never a delivery asset. Do not use the globally neutralized whitebox room as Image 1 because it discards the original scene's material, value, and lighting evidence. The first-pass `outputMode` is `contextual-local-replacement`. The prompt directs an in-place replacement of the 3D mannequin in Image 1, not a transparent person-only output and not a redesign of the scene. The Codex-reviewed whitebox controls pose, scale, position, occupied volume, contacts, and overlap only after both scale gates pass. Nearby fixed objects remain regression evidence: a contradictory final read returns to absolute scale. Preserve the character card's design, remove the mannequin, and generate the actor plus authorized loose props with enough support context to solve contact. Never regenerate or extract unchanged structural furniture into the scalable component.

## 15. Codex post-generation conformance

First compare the local generated character against Image 3 for identity/style and against Image 1 for pose, joint logic, occupied volume, scale, and contacts. A generated actor that misses an approved whitebox returns to generation and cannot be repaired by registration. If the actor matches the whitebox but the composite scale still reads incorrectly, the whitebox/depth calibration failed and must be rebuilt before another generation attempt.

Every raster-producing or raster-transforming step has its own visual stop gate. Use `scripts/visual_review_gate.py` to create a comparison board, open that board, inspect the whole frame and all local tiles, and record explicit findings before continuing. Required stages are exact-pose whitebox, contextual local result, matte extraction, pre-composite registration, and final full composite. Numeric contracts and technical scripts are diagnostic evidence only; they cannot visually approve an image.

After pose and contact pass, extract the character or authorized interaction component. A single documented uniform scale plus translation may align the extracted alpha to the approved anatomical landmarks and original Photoshop coordinates; an alpha/outer box never drives scale. This registration is mechanical normalization only: no anisotropic scaling, warping, limb movement, joint correction, or changed support contact. Compare the registered full composite with its directing snapshot, reviewed whitebox, and aligned depth reference. Inspect the gameplay-size full frame head-first, then every character/action/overlap region as local tiles. Rerun cast-scale v2 using measured final head boxes: each head height tolerance is 5%, pairwise head-ratio tolerance is 10%, support contact tolerance is 4px, and major-joint tolerance is 3% of standing-equivalent height. A passing full-body or alpha-box fit cannot override a failed final head ratio. Also check story readability, performance, actor-scene occlusion, actor-actor occlusion, actual UI, identity, style, costume state, shadow, and untouched-background preservation. Record the transform and report, then run `validate-final-conformance`.

Preserve the accepted contextual result's crop registration. First scale the complete generated local canvas back to the original no-resize `cropBBox`, then use that mapping to preview the extracted component on the untouched scene. Compare the preview with the accepted local result, near and far fixed furniture, head sizes, and the simultaneous cast. A compositor must not crop alpha and apply a new arbitrary visible height after this point. If the visually accepted contextual result and the reviewed whitebox disagree, stop, update the absolute-scale/whitebox evidence, and revalidate it before compositing.

Never use a tight hand-authored polygon as the final alpha. It may only bound the authorized change/protection region. Produce the final matte in a separate background-removal step from the approved contextual RGB. If the model bakes a neutral checker into RGB, run `conservative_matte.py`. Its v2 report separates silhouette coverage from edge RGB contamination, preserves enclosed light content such as shirts and paper, and expands retained foreground rather than eroding it. Compare black, white, and dark scene-tone previews with the contextual master. A correct alpha with gray/white straight-RGB contamination still fails; neither missing content nor retained background may be concealed by inward feathering.

Annotate final-size eye center, face-direction point, named target point, and angular tolerance, then run `validate-gaze-conformance`. The final image fails when its gaze disagrees with the directing target even if the text contract is correct. Existing actors still do not need to reciprocate a later entrant unless the timeline explicitly requires it.

## 16. Snapshot cast composition

For each simultaneous-cast snapshot, assemble actors, loose-prop source repairs, relocated props, exact-source occluders, contact shadows, and cast shadows. Extract occluders from the untouched source at exact coordinates and preserve internal holes, rails, gaps, and irregular edges. A character using a chair or bed does not authorize that fixed structure to enter the actor layer. Run `validate-component-policy` against the final layer manifest, then check actor-actor overlap, actor-scene overlap, opaque patches, face/hand readability, support contacts, and actual UI. Do not create a union-cast composite for actors who never coexist.

## 17. States, extraction, and delivery

For exploration NPCs, validate the registered idle/active pair with `verify-exploration-states`; local-patch assembly may additionally use `verify-states`. The active delta normally changes attention/expression/head/upper torso or a local hand action while keeping social territory and support fixed. Extract original-resolution RGBA assets with minimum irregular environment masks. Record Photoshop `(X,Y)`, size, any uniform registration transform, layer order, occluder masks, shadow strategy, lifecycle presence, and Unit ledger. Reconstruct on the untouched source with zero changes outside authorized alpha. Deliver timeline, affordance, UI, blocking, proxy, depth, whitebox, local-generation handoff, identity/style comparison, state, and occlusion evidence with the assets.

Run production ledger v2 again at `post-generation` before formal packaging. It requires final gaze-conformance, component-policy, and matte-v2 reports in addition to final conformance. The technical file layer may say only `TECHNICAL_FILE_PASS` or `TECHNICAL_FILE_FAIL`; unqualified `PASS` belongs exclusively to the complete semantic, structural, visual, and delivery gate.

## 18. Retry and batch-review policy

Do not interrupt the user during normal production. A branch may make up to six valid attempts, each with a recorded failed variable and a deliberate correction. A result that passes all gates enters the formal scene-named package. If six attempts still fail, select the closest attempt by failed-gate count and severity, record the unresolved failures, validate it with `validate-candidate-handoff`, and keep it under `工作过程文件` as `best-available candidate`. Continue the remaining batch and present all formal outputs and candidates together for one final user approval. Never place a candidate in `最终交付`.

## Completion status

`PASS` requires semantic and technical gates. Exact reconstruction, hashes, canvas size, or valid alpha cannot compensate for a wrong lifecycle, unreadable story beat, stiff performance, invalid affordance, actual-UI conflict, unreviewed/mismatched whitebox, incorrect physical placement, or incorrect occlusion. User approval happens once at the completed batch level; it is not a substitute for Codex self-check and does not turn a known failed candidate into formal delivery.
