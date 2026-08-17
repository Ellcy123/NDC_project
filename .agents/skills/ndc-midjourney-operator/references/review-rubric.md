# NDC scene image review rubric

## Decision principle

Judge requirement fidelity and aesthetic quality separately. Hard fidelity controls pass/fail; aesthetics choose among otherwise valid candidates.

## Review categories

### A. Core composition and camera

Check:

- scene type and major viewpoint;
- foreground, middle ground, and background relationship;
- direction and perspective;
- major doors, paths, walls, counters, stage, or other scene-defining masses;
- whether the scene remains readable as a game background.
- camera height and horizon against observable architectural landmarks;
- focal-length distortion and depth-of-field readability when the handoff specifies them;
- foreground, middle ground, background and left, center, right anchors;
- connection, separation, overlap, route, visibility, and relative scale among architecture-defining masses.

Apply the scene-mode rule before aesthetic judgment:

- `exploration`: audit only the required `eye_level` job. Fail a candidate if it does not visibly read as an eye-level three-point-perspective composition aligned with a standing eye line, camera height `1.7–1.8 meters`, and horizon at the upper third.
- `non_exploration`: audit `frontal`, `oblique`, and `overhead_45` as three independent jobs. The frontal view must remain predominantly straight-on, the oblique view must expose the declared side and spatial relations, and the overhead view must look downward at approximately 45 degrees. One view cannot substitute for another.

Do not accept a textual camera label at face value. Use visible geometry: expected top surfaces or edges of wainscoting, desks, counters, window sills, rails, and stair landings should agree with the intended height. Verify that major doors or routes intended to remain separate are not merged, occluded, or moved onto the wrong wall.

Fail when the camera or large layout changes the intended scene. Do not fail for harmless furniture rearrangement.

### B. Core objects

Check every gameplay-, evidence-, interaction-, or narrative-critical object for:

- presence;
- recognizable type;
- usable scale;
- intended location or relationship;
- visibility and separation from the background.

An attractive image missing a core object fails. A deformed but recognizable core object is usually `partial` and may suit a variation.

### C. Scene identity and period

Check architecture, furniture, technology, materials, signage, and clothing if present. Flag modern or wrong-period elements that change the scene's identity. Do not demand museum-level precision from minor decoration unless the source requires it.

### D. Required and forbidden subjects

Check whether characters, crowds, bodies, vehicles, text, modern devices, weather, or other explicitly required or forbidden subjects are present. A forbidden dominant subject is a hard failure.

### E. Reference leakage

Look for subjects inherited from references rather than requirements:

- faces or people from portraits;
- skyline, towers, or exterior windows from city references;
- unwanted signature props;
- copied composition that conflicts with the scene.

Repair the reference plan before piling on negative words.

### F. Lighting and graphic finish

Check light direction, contrast, palette, line treatment, material readability, and consistency with approved examples. Use this category to rank valid images unless lighting obscures a core object or breaks a hard narrative condition.

### G. Soft and flexible details

Allow variation in non-critical counts, ornament, minor prop placement, decorative patterns, and incidental clutter. For example, accept any convincing row of small high clerestory windows when their exact number has no gameplay meaning.

## Candidate status

- `pass`: satisfies the category with no meaningful correction.
- `partial`: useful foundation with a localized or tolerable defect.
- `fail`: violates a hard requirement or requires structural regeneration.

## Grid action

- One or more candidates in the current view pass A–E: select the strongest using F and stop that view, unless the user requested refinement.
- A candidate passes A–E but has a local F/G issue: use a subtle variation first; inspect it before escalating to a strong variation on the same base.
- A candidate is partial in A or B but otherwise strong: consider a strong variation.
- All candidates fail the same camera, depth-layer, architecture-relation, or other A–E condition: repair the prompt or reference plan and resubmit instead of relying on repeated variations.
- Results fail for different reasons with no stable base: simplify the prompt to composition and core objects before adding finish back.

After reviewing all required jobs, declare the set complete only when every required view has one passing candidate. A non-exploration scene is incomplete until `frontal`, `oblique`, and `overhead_45` each pass.
