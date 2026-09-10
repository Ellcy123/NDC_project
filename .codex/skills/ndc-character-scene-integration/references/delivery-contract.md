# Delivery contract and QA

Use [production-cadence.md](production-cadence.md) for milestone boundaries, shared budgets and valid review reuse. Whiteboxes allow [up to three generations and three Photoshop MCP repairs](whitebox-photoshop-fallback.md), with PS available from the first useful candidate under [PS-first repair](ps-first-repair.md). Formal context, revision and model extraction share the actor/interaction model budget. Do not create a fresh budget at packaging or manufacture attempts to fit an old checker.

## Required asset and evidence coverage

The list below is coverage, not 23 separate production or review stages per actor. Shared scene evidence is created once and referenced by the relevant actors. Formal folders contain passed image/layer assets; reports, prompts, manifests and rejected history stay in the work folder. Consolidate final source/hash/XY data once after pixel freeze.

The user-facing delivery root must be named with the source scene basename, without the extension, for example `SC2212_bg_LakeshoreTrust_VIPParlor`. Put character/version folders inside it when needed. Do not use a generic `delivery` folder as the user-facing delivery root. The placement contract must store this absolute path as `deliveryRoot`; `validate-contract` rejects a basename mismatch, paths outside `D:\Codex\NDC`, and formal delivery roots inside `工作过程文件`.

1. source scene identity, original dimensions, and hash;
2. Codex-reviewed exact-pose proxy evidence;
3. aligned depth reference containing that exact pose;
4. engine-derived lifecycle report, directing timeline, scene-affordance map, actual-UI report, automatic blocking candidates/report, and incremental timeline board;
5. isolated exact-pose volumetric whitebox for every actor presence;
6. one combined-cast whitebox per simultaneous-cast snapshot, with scene occluders and character order visible;
7. Codex whitebox/depth review record, full-frame and local-tile coverage evidence, artifact hashes, pose IDs, snapshot staging contracts, and pairwise occlusion graphs;
8. exploration idle/active RGBA assets, or narrative presence assets keyed to lifecycle where applicable;
9. shadow strategy: baked, shared, reused, or redrawn;
10. original-resolution state/snapshot previews;
11. Photoshop top-left `(X,Y)` and asset dimensions for each state;
12. machine-readable placement/delivery contract;
13. final-vs-timeline-vs-depth-vs-whitebox comparison report, prompts, reference-role manifest, rejected attempts, and QA report;
14. local-generation handoff report containing Image 1/2/3 roles, crop/original boxes, source hashes, and clean local reference;
15. identity/style comparison against the approved card and pose/contact comparison against the approved whitebox;
16. actual extraction and registration provenance, composed uniform transform if used, and current revalidated pose/scale/contact evidence; permitted PS correction follows the cadence reference and explicit user locks;
17. exact source-scene occluder masks with internal holes preserved, and any minimum changed actor-object interaction component;
18. `xyposition-Unit<chapter>.md` entry;
19. when the actual model/repair budget is exhausted or a specific capability/time stop remains, a marked work candidate with unresolved failures and true counts, never in the formal root;
20. a pre-generation and post-generation `ndc-scene-integration-production-ledger/v2`, plus their `production_gate.py` reports. The ledger must hash every referenced artifact and use only `NOT_RUN`, `TECHNICAL_FILE_PASS`, or `TECHNICAL_FILE_FAIL` for file-check status.
21. a fixed-scene absolute-scale report and overlay, independent from cast-relative head/body scale;
22. planned/final component-policy reports, with paired masks for every relocated loose prop and fixed structures excluded from scalable layers;
23. final gaze-conformance and matte-v2 reports, including black, white, and dark scene-tone edge previews.

## Technical gates

- Use the original scene as the only background pixel source.
- Keep all generation references separate from delivery pixels.
- Generate against the deterministic local whitebox crop; use the full scene only as global context and the character card only as identity/style authority.
- Work and extract at original scene resolution; never enlarge a preview into a formal asset.
- RGBA must have real alpha, transparent corners, and no light/dark matte fringe.
- Reconstruct each preview by pasting the asset at 100% scale at its recorded `(X,Y)`.
- Pixels outside the authorized alpha/bbox must equal the source exactly.
- Required frozen regions must be byte-identical.
- Verify seam continuity separately from freeze equality.
- For local-patch states, require one accepted master, exact transform reuse, bounded change masks, natural seam paths, landmark-anchored facial accessories, and a non-horizontal occlusion strategy. For registered complete exploration states, require exact canvas/transform reuse plus support-anchor and alpha-bottom registration.
- Verify physical scale against at least three independent fixed-object groups spanning horizontal/vertical dimensions and actor-local/cross-depth bands before whitebox approval and again after final composition. Cast-relative head/body scale cannot replace this absolute gate.
- Reject a default upright skeleton or empty-scene blockout presented as a human whitebox. It must share the approved pose ID, head scale, landmarks, position, and contacts.
- Require Codex full-frame and complete local-tile review of isolated/combined whiteboxes and the aligned depth reference before generation. Hashes prove artifact identity only; they do not grant semantic PASS.
- Use the shared scene-scale register for v2 scale evidence; distinguish vertical height calibration from horizontal footprint checks. Metric evidence requires two independent vertical references and a separate footprint check; a horizontal dimension contributes to height only with a valid direction transfer. Do not count dimensions of one object as independent objects. Bounded evidence must pass the measured range, sensitivity, support, whole-whitebox and UI checks specified in the staging contracts; it must not claim an exact camera or a metric recommended scale. Existing v1 contracts remain subject to their original recomputation checks and must not be relabeled v2 without the required evidence.
- For seated characters, verify that the anatomical seated span is lower than the same-depth standing equivalent and that head size matches the approved master within tolerance. Hats and action extensions do not change body scale.
- Check the applicable real left/right UI reference using nontransparent actor, prop, support, and shadow pixels. The two-thirds shortcut cannot pass delivery. For every three-plus-cast snapshot, the multicast actors, bound UI contract actors and UI report actors must be the same unique actor-ID set; status alone or a report that silently omits one on-screen actor cannot pass.
- New or revised lying placements use cast-scale v3. Ground lying declares a ground plane; elevated lying binds the unchanged support contact to the fixed scene/current pose plus independent support-plane, projected-ground or same-depth-reference, and whole/local visual evidence. Do not repurpose the bed contact as floor depth or edit horizon/tolerance to pass. Unchanged accepted historical reuse does not require a retroactive rerun.
- In multi-character scenes, composite all actors who coexist in each timeline snapshot and test opaque overlap; do not build a union cast from different times.
- Require a declared pairwise relation for every overlapping character pair and exact scene-occluder masks where a character passes behind furniture. Independent checks cannot substitute for combined-cast review.
- After character generation, run the same full-frame plus complete local-tile comparison against both the aligned depth reference and combined whitebox. `validate-final-conformance` must pass before formal packaging.
- Preserve the high-resolution source, compose any permitted support-anchored uniform transforms, update affected pose/scale/contact evidence, then apply final resampling once. Reject alpha-box fitting, nonuniform scale, warp, limb/joint edits, or registration concealing wrong performance.
- Reapply occluders from exact untouched-scene pixels and preserve openings; rectangular or straight-line concealment cannot substitute for the source mask.
- Never place a fixed chair, bed, door, railing, or other structural object in a generated/scalable actor component. Loose-object relocation uses a minimum source-repair mask plus a minimum destination layer; unchanged structural occluders remain exact source pixels at scale 1.
- Before identity generation require a current passing pre-generation ledger; rerun when its inputs change. Run post-generation validation on the finished current layers. Reuse unchanged valid reports instead of regenerating them for every command. `EVIDENCE_GATE_PASS` proves structural coverage only, not artistic or delivery approval.
- A visibly closed portal cannot be used as an on-screen entrance. Either document an opening transition and choose a post-entry hold after it closes, use a genuinely off-screen route, or select another snapshot. The final still must not falsely depict entry through a closed door.

## Visual gates

- apparent scale and depth read naturally beside at least two scene objects;
- the silent frame communicates the authored beat, and performance is natural rather than a front-facing stage pose;
- silent-frame verb, energy, activity, support, social territory and sustainable posture agree with the beat; hands may naturally rest, and low energy does not excuse stiff shoulders, arms or ritual-like cast similarity;
- every actor placement is compatible with the declared affordance and lifecycle snapshot;
- complete outer rectangle contains hair, hands, props, garments, and shoes;
- feet/seat/support contacts are plausible;
- final pose and volume match the current reviewed placement/whitebox: head-ratio individual/pairwise deviation within 20%; valid fixed-line support contacts retain 4px tolerance and major joints 3% of standing-equivalent height. Continuous floors use their region-plus-physical-review branch and cannot claim a measured floating gap from region coverage;
- hidden feet/body are verified using the same complete layer/transform as final occlusion; head-neck-shoulder support and loaded pillow/bedding response are visibly continuous, not just within a support polygon;
- character-character and character-scene occlusion match the approved combined whitebox and graph;
- identity and style match the approved card and scene;
- final eye/face direction agrees geometrically with the named current-snapshot target;
- alpha coverage is complete and retained edge RGB contains no visible neutral background contamination on black, white, or scene-tone previews;
- before/after transition has no torso, clothing, edge, or lighting fracture;
- contact/cast shadow matches the local light and receiving plane.

Do not erase a character with a straight horizontal alpha cut to simulate foreground furniture. Deliver the complete actor plus a separate pixel-accurate foreground occluder when layering permits; otherwise use an irregular mask traced from the exact source object and document the hidden region.

Do not report formal completion when visual gates fail. Follow the shared counts and time/repair routing in the cadence reference. Preserve unresolved candidates under `工作过程文件`; do not force a legacy exact-six handoff schema to describe a different actual stop. Copy-bound reviews retain original observation provenance plus destination hash checks; packaging cannot revive a user-rejected asset. Archive passed assets within the authorized task without another routine approval hold.

Never write a bare `PASS` or `hardGatePass` from canvas, alpha, hash, bbox, or reconstruction checks. Report `TECHNICAL_FILE_PASS` for those checks and record the separate Codex semantic reviews for performance, scale, support, occlusion, UI, identity, light, and edge quality.
