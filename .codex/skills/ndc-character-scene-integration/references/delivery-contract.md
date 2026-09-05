# Delivery contract and QA

## Required outputs per character

The user-facing delivery root must be named with the source scene basename, without the extension, for example `SC2212_bg_LakeshoreTrust_VIPParlor`. Put character/version folders inside it when needed. Do not use a generic `delivery` folder as the user-facing delivery root. The placement contract must store this absolute path as `deliveryRoot`; `validate-contract` rejects a basename mismatch, paths outside the configured work root's `<job>/payload/`, and prepared-delivery roots inside `工作过程文件` or `candidates`.

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
16. extraction and registration record, including the single uniform scale and translation if used, plus proof that pose/contact passed before registration;
17. exact source-scene occluder masks with internal holes preserved, and any minimum changed actor-object interaction component;
18. `xyposition-Unit<chapter>.md` entry;
19. when six attempts fail, a separately marked best-available candidate package under `工作过程文件`, never in the formal delivery root.
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
- Reject scale contracts that count two dimensions of one object as two independent anchors or omit the object's real-world range, chosen value, raw/projected image measurements, plane relation, and projection method. Recompute each anchor's 170cm result instead of trusting a handwritten projected height.
- For seated characters, verify that the anatomical seated span is lower than the same-depth standing equivalent and that head size matches the approved master within tolerance. Hats and action extensions do not change body scale.
- Check the applicable real left/right UI reference using nontransparent actor, prop, support, and shadow pixels. The two-thirds shortcut cannot pass delivery.
- In multi-character scenes, composite all actors who coexist in each timeline snapshot and test opaque overlap; do not build a union cast from different times.
- Require a declared pairwise relation for every overlapping character pair and exact scene-occluder masks where a character passes behind furniture. Independent checks cannot substitute for combined-cast review.
- After character generation, run the same full-frame plus complete local-tile comparison against both the aligned depth reference and combined whitebox. `validate-final-conformance` must pass before formal packaging.
- Permit at most one uniform scale plus translation after pose/contact approval. Reject nonuniform scale, warp, limb/joint edits, or registration that conceals the wrong performance.
- Reapply occluders from exact untouched-scene pixels and preserve openings; rectangular or straight-line concealment cannot substitute for the source mask.
- Never place a fixed chair, bed, door, railing, or other structural object in a generated/scalable actor component. Loose-object relocation uses a minimum source-repair mask plus a minimum destination layer; unchanged structural occluders remain exact source pixels at scale 1.
- Before any image-generation call, run `production_gate.py` on the pre-generation ledger. After extraction and final conformance, run it again on the post-generation ledger. `EVIDENCE_GATE_PASS` means required evidence exists and agrees structurally; it is not an artistic, narrative, or delivery approval.
- A visibly closed portal cannot be used as an on-screen entrance. Either document an opening transition and choose a post-entry hold after it closes, use a genuinely off-screen route, or select another snapshot. The final still must not falsely depict entry through a closed door.

## Visual gates

- apparent scale and depth read naturally beside at least two scene objects;
- the silent frame communicates the authored beat, and performance is natural rather than a front-facing stage pose;
- silent-frame verb, beat energy, ongoing occupation, named support, social territory, both hand motivations, and ten-second hold all agree with the current lifecycle node;
- every actor placement is compatible with the declared affordance and lifecycle snapshot;
- complete outer rectangle contains hair, hands, props, garments, and shoes;
- feet/seat/support contacts are plausible;
- final pose and volume match the Codex-reviewed whitebox: head height within 5%, support contacts within 4px, and major joints within 3% of standing-equivalent height;
- character-character and character-scene occlusion match the approved combined whitebox and graph;
- identity and style match the approved card and scene;
- final eye/face direction agrees geometrically with the named current-snapshot target;
- alpha coverage is complete and retained edge RGB contains no visible neutral background contamination on black, white, or scene-tone previews;
- before/after transition has no torso, clothing, edge, or lighting fracture;
- contact/cast shadow matches the local light and receiving plane.

Do not erase a character with a straight horizontal alpha cut to simulate foreground furniture. Deliver the complete actor plus a separate pixel-accurate foreground occluder when layering permits; otherwise use an irregular mask traced from the exact source object and document the hidden region.

Do not report formal completion when technical gates pass but visual gates fail. Retry the failed branch up to six times without interrupting the user. After six failures, select the closest result, list every unresolved gate, keep it under `工作过程文件`, and include it only as a candidate in the final batch review.

Never write a bare `PASS` or `hardGatePass` from canvas, alpha, hash, bbox, or reconstruction checks. Report `TECHNICAL_FILE_PASS` for those checks and record the separate Codex semantic reviews for performance, scale, support, occlusion, UI, identity, light, and edge quality.
