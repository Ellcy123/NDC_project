# Case studies and failure lessons

## Status rule

No case below is currently a verified end-to-end formal success. Preserve successful components as reusable evidence, but do not describe a scene as successful while identity, whitebox, interaction-component extraction, state delivery, shadow, or final visual approval remains open.

| Case | Reusable success | Negative evidence / remaining failure | Formal status |
|---|---|---|---|
| SC2309 Danny bedroom | corrected multi-object scale, exact 100% paste-back, shared `(X,Y)`, lower-body freeze, zero-difference reconstruction | initial visual-only proxy was oversized; after-state face still failed identity review | partial technical success only |
| SC2314 Leonard office | seated support must be a character+chair+contact component; authorized-region exterior stayed unchanged | person-only extraction broke chair, lower body, and contact | component-rule success, not complete delivery proof |
| SC2211 bank lobby | position/depth decision supplied useful scale anchors | final actor slightly oversized; horizontal torso seam and unsupported shadow failed | negative production case |
| SC2212 Moore VIP parlor | physical scene overrode a nonexistent dialogue desk; sofa staging and coffee-table occlusion were correct decisions | whole scene was regenerated; seated body was normalized to a wrong outer height; no approved final component/state/shadow | negative production case |
| SC2206/SC2406 hospital | canonical heights and untouched-background reconstruction were recorded | default upright skeletons were mislabeled as whiteboxes; final poses were invented later; furniture and actor-actor occlusion were undeclared; combined staging never passed semantic review | rejected test / negative case |
| Unit2 batch 20260828 | sources, dimensions, hashes, RGBA canvases, and several placement coordinates were collected reproducibly | target-box fitting ignored recorded heights; flat skeleton/rectangle proxies were called whiteboxes; cast snapshots were not engine-derived; visible closed-door entry, unsupported stair contact, camera-facing prop presentation, alpha halos, and synthetic/no shadows survived a file-only `hardGatePass` | rejected process batch / training negative |
| SC2518 v5 performance retest | contextual seated performance and post-entry lifecycle were clearer than the rejected batch | cast-scale checked only standing-equivalent full-body height; Zack's contextual component and Mickey/Lula cutouts used incompatible scale drivers; Lula's nearer head remained too small, Mickey's head/body read too small, and the final report reused a pre-generation scale PASS without measuring final heads | rejected scale test / training negative |

## Global semantic diagnosis added after the rejected staging run

The stiff, theater-like result was not only an image-generation problem. The workflow handed image generation a technically described placement before Codex had completed directing. Reusable causes were:

- dialogue was not reduced to an objective/conflict/emotion/subtext/action-focus beat;
- a union cast was planned instead of engineering-derived entry/exit snapshots;
- initial actors were allowed to visually anticipate later entrants;
- depth/model references were treated mainly as scale and foot-position aids instead of maps of walk, stand, sit, lie, lean, reach, pass-behind, and support affordances;
- UI safety was expressed as a rough opposite-two-thirds rule instead of tested against the real left/right composition pixels;
- pose was locked too early as a generic upright skeleton, so whitebox precision merely preserved a weak performance;
- gesture, weight distribution, gaze, hand business, facial tension, costume state, and hold-pose validity were not machine-readable requirements;
- independently plausible actors were composed without first reading the fixed shot as a silent narrative frame.

Correction: extract lifecycle, direct incremental story snapshots, map affordances, generate deterministic blocking candidates, test actual UI, freeze existing actors across later entrances, and only then begin scale/depth/whitebox production. Image generation executes the chosen performance; it does not decide the scene's dramatic logic.

## Existing production NPC and background assets

Assets under the read-only Unity `Art/Scene/NPC` and `Art/Scene/Backgrounds` trees are current-project evidence for runtime canvas conventions, idle/active pairing, shadows, coordinates, silhouette density, and historically accepted scene language. They are not automatically formal success examples: audit lifecycle role, UI side, support, state meaning, and visible performance before deriving a reusable rule.

When a historical asset is used as a reference, record its exact path and the property being borrowed. Do not copy its pose or placement merely because it shipped; the new scene's story beat, affordance, and lifecycle remain authoritative.

### EPI02 performance-language evidence

The existing EPI02 NPC assets provide useful project-language evidence because their figures often read as an activity already in progress rather than a pose performed for the camera. Borrow only the named property after checking its scene and runtime role:

- SC2606: Margaret's bed-supported, downward-attention hold and Foster's work-oriented side profile show that low-energy concern can read through support, head angle, and occupied hands; an active state may redirect attention without replacing the whole social territory.
- SC2420: Danny's seated newspaper activity uses a prop and support to explain the body shape before the player interacts.
- SC2604: Morrison's crossed-arm window hold uses architectural territory and an off-player gaze; its active change is primarily attention/orientation.
- SC2515: Vinnie's seated drink and lowered head create a self-sustaining idle state; raising attention is enough to distinguish engagement.
- SC2211: deep/small actors preserve architectural scale and social zone instead of being enlarged or pushed forward for portrait readability.

These examples support a global rule: first specify ongoing occupation, named support, social territory, gaze, hand motivation, beat energy, and a ten-second hold; then select pose geometry. They do not authorize copying an EPI02 pose into another scene, and they do not prove every shipped asset is correct.

## SC2518 v8: relative scale passed while the scene still failed

The v8 room test aligned the three approved-card head ratios, but the whole cast remained too large against the door, windows, bed, and other fixed objects. This proved that cast-relative scale and fixed-scene absolute scale are independent gates. The Zack layer also included a regenerated chair and blanket, so later registration could alter a fixed structural object and destroy the original occlusion. Lula's written target named Zack while the final face looked toward the empty left/UI side, and matte reports passed despite visible neutral RGB rims.

Reusable correction: measure at least three independent fixed objects across horizontal/vertical axes and local/cross-depth bands, then rebuild all whiteboxes if the robust global factor is not near 1. Keep structural furniture in untouched source pixels; relocate loose items through separate old-location repair and new-location layers, restore exact source occluders, validate final gaze geometrically, and treat alpha coverage and RGB decontamination as separate edge gates. Assembly scripts may collect report hashes but may not author semantic `pass` values.

## Bedroom standing character

Depth and whitebox references materially improved the 170cm proxy placement. Lesson: require both before formal generation, but keep scale approval independent from their compliance.

## Office seated character

Extracting only the person failed when the generated chair did not match the source. Expanding the generation context to the full seated interaction component solved the contact, then a minimal irregular alpha prevented a large rectangular scene patch.

## Bank lobby midground test

The position decision succeeded, but three later gates failed:

- a single door/horizon estimate produced a slightly oversized 510px target;
- before and after were independently generated and independently normalized, then joined on a straight waist line, creating a visible fracture;
- a fixed semi-transparent six-point polygon was used as shadow without scene light or ground-plane evidence.

Corrections:

- require multi-anchor projected scale and dispersion checks;
- use the before state as the single master and generate only a registered local patch;
- check seam continuity, not only frozen equality;
- require a light/ground contract and separate contact from cast shadow;
- reject baked checkerboards or decontaminate mattes before delivery.

These are production gates, not scene-specific coordinates.

## VIP parlor seated calibration test

The approved scene had no desk even though the dialogue described one. The physical scene therefore won: the character was staged on the center rear sofa, with files on his lap and the coffee table retained as a foreground occluder.

The first v1 delivery was later rejected. Although the three standing-equivalent estimates clustered near 305px, the seated proxy was assigned a 340px outer height and the generated actor was then normalized to fill that height. The whitebox therefore encoded an oversized seated body instead of bending the locked 170cm ruler. User correction indicated that the seated actor needed roughly 72-74% of the delivered height while the standing-equivalent calibration remained the scale ruler.

The same delivery also exposed two deterministic artifacts: fixed-canvas glasses were drawn over the face without eye-landmark registration, and the lower body was both joined across a horizontal seam and clipped by a constant `OCCLUDER_TOP`. Technical freeze checks passed but the face and knee/leg continuity failed visual review.

The test exposed these reusable requirements:

- seated pose height is not the same measurement as the 170cm standing-equivalent scale; bend the locked anatomical ruler, keep head/body scale fixed, and treat a top hat or raised hand only as an outer extension;
- an image generator may return 3:2 even when the source is 16:10. Use a deterministic letterboxed handoff, preserve calibration bars, and restore the source canvas mechanically. The generated depth, whitebox, or full scene is still only an auxiliary/candidate and cannot replace original pixels.

The rejected v1 did not match the locked anatomical scale. The next gate is to rebuild the seated proxy from the 170cm ruler, pass Codex full-frame and local-tile structural review, then extract the character plus minimum sofa-contact pixels, reapply the original coffee table as a separate exact foreground occluder, and paste that component into the untouched 2560×1600 source.

## Hospital four-character rejected test

The delivery contained files named `whitebox`, but the human content was only a scene blockout plus red skeletons. Zack, Mickey, and Emma used the script's default upright pose even though the final actors leaned, gestured, held a key/briefcase, or wrote in a notebook. Margaret used a thin lying skeleton rather than a volumetric body capable of proving blanket, rail, and bed contact.

The test checked each character separately and composited by filename order. It had no scene staging contract, no pairwise actor occlusion graph, no exact furniture masks for every actor, and no combined-cast whitebox review. Mickey's alpha box overlapped Margaret's region, but the overlap was resolved accidentally by layer order rather than a validated physical relation. Reconstructability and unchanged background pixels passed, yet the scene remained visually invalid.

Reusable correction: generate exact-pose volumetric whiteboxes after scale calibration, review all characters together at full-frame and local-tile scale, declare every scene and actor overlap, pass the Codex structural gate, and only then generate identity art. Compare the formal composite back to both depth and whitebox; retry up to six times, then retain only the closest failed result as a clearly marked candidate for the final batch review. Technical file presence can never stand in for this semantic gate.

Zack's rejected result illustrates a directing failure before generation: the wide planted stance, open reaching hand, forward position, and defensive energy lacked a current-node cause, named ongoing occupation, or credible ten-second hold. It read as an entrant confronting an unseen event rather than a person already inhabiting a quiet hospital room. A valid alternative is not automatically one particular seated pose; Codex must first confirm the snapshot, available bed/chair support, Margaret's lifecycle presence, UI side, and whether looking toward Margaret creates an authorized current interaction. Only then may a supported bedside sit/lean become the selected family.

The latest local-generation proposal corrects a separate execution failure. Once directing and whitebox pass, generate from a crop containing the approved whitebox, use the full scene only for global lighting/context, and use the card only for identity/style. Compare before extraction, allow only uniform registration after pose/contact pass, and reapply exact source occluders. This prevents the model from re-solving the whole scene, drifting scale, or inventing furniture while retaining deterministic paste-back.

## Unit2 20260828 rejected process batch

This batch exposed a false-positive pipeline rather than a single bad drawing. Recorded character heights never became the body-scale driver: each generated actor was independently fitted to a target rectangle, allowing stature, head size, and depth to drift while numeric placement reports still looked complete. The so-called whiteboxes were flat skeletons and bounding rectangles, so they could not prove torso volume, weight transfer, chair or stair contact, prop reach, or overlap between actors. A union-like cast plan then ignored actual entry/exit state, and file checks promoted the output with `hardGatePass` even when the silent frame failed.

SC2518 made the contradiction visible: Mickey occupied the door territory while Lula was labelled as entering through the same visibly closed door. The correction is to extract the engine timeline, freeze earlier actors, validate the travel corridor, and choose a post-entry hold only after an authored door-opening transition. Existing actors must not be re-posed to acknowledge a later entrant unless the current node explicitly changes them.

SC2316 showed the performance and perspective failure: Emma presented the letter toward the camera, did not direct attention uphill toward Zack, and lacked convincing tread/riser contact in a low-angle shot. The correction is to authorize the verb first—climb, stop, or address—then lock uphill body orientation, gaze target, hand motivation, uphill/downhill foot contacts, and the letter's narrative receiver in a volumetric stair-aware proxy.

The batch also used brightness-threshold matte extraction and generic blur, leaving light/dark edge contamination, while shadows were missing or unrelated to scene light. Correction: treat alpha decontamination, contact shadow, cast shadow, and receiving plane as separate reviewed artifacts. No hash, canvas-size, or reconstruction result may be promoted beyond `TECHNICAL_FILE_PASS`; formal status requires the Codex semantic gates and post-generation conformance review.

## SC2518 v5 head-scale failure

The v5 whitebox compared canonical heights and foot-depth projection but treated the anatomical head boxes as secondary pose details. That allowed Lula's closer full-body target to pass while her head remained only slightly larger than the farther actors. In assembly, Mickey and Lula were normalized from alpha bounds while Zack arrived as a contextual chair component, so their final heads no longer shared a scale driver. A manually copied `castScaleConformance: pass` then described the placement contracts rather than the final pixels.

Correction: new production uses cast-scale v2 with `headScalePriority: true`. Measure each approved card's front-view anatomical head/full-body ratio; compare every whitebox head individually and pairwise after depth projection; only then review standing-equivalent height. After generation, author measured final head boxes and rerun the same cast report. Alpha bounds, action outer boxes, garments, props, or a locally regenerated support object may never determine actor scale. A nearer comparable adult head that is not visibly larger is an immediate whitebox/final-composite failure even when full-body ratios pass.
