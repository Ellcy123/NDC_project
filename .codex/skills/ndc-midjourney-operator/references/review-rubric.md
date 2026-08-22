# NDC scene image review rubric

## Decision principle

Apply background purity and hard requirement fidelity before aesthetic ranking. A beautiful image that contains a character, mutable prop, or wrong spatial structure still fails as a formal base asset.

## Preflight hard vetoes

Fail the candidate when any of these is true:

- a person, character, body, corpse, or figure appears in the scene;
- a collectible, pickup, plot item that may disappear, Loop-specific change, interaction close-up, or scan overlay is baked into the base;
- the camera or large spatial structure contradicts the required scene;
- a forbidden modern or wrong-period dominant subject changes scene identity.

Legacy comparison images containing people or bodies are evidence of past exploration only; they do not override this rule.

## Review order

### A. Camera and composition — one-vote veto

Check viewpoint, perspective, camera height, horizon, foreground/middle/background, left/center/right anchors, and the relations among scene-defining masses. Do not accept the textual camera label at face value.

- `exploration`: review only `eye_level`. Require a visible eye-level three-point-perspective reading, optical center about `1.7–1.8 m` above the floor, and horizon near the upper third.
- `non_exploration`: review `frontal`, `oblique`, and `overhead_45` as independent jobs. One view cannot substitute for another.

Judge scale from architecture: an ordinary door near 2 m, handrail about 0.9–1.0 m, desk about 0.72–0.76 m, plus plausible window sills, wainscoting, and stair risers. A temporary neutral silhouette may be placed over the image after generation only to review scale. It must never become a Midjourney reference, prompt subject, or final-layer element.

Fail when major doors, routes, walls, counters, stages, or other defining masses merge, move to the wrong wall, or lose the intended route. Do not fail for harmless furniture rearrangement.

### B. Style consistency

Check light direction, contrast, palette, line treatment, material readability, period atmosphere, and consistency with approved examples. Use style to rank candidates only after hard vetoes and camera pass.

### C. Broad spatial structure

Check scene function, navigability, foreground/middle/background separation, architectural hierarchy, and game-background readability. For an exploration scene, the central safe area must stay compositionally stable and the left/right edges must be plausible continuation seams for Photoshop expansion.

### D. Scene-description fidelity

Check all permanent environment and narrative facts for presence, recognizable type, usable scale, intended relation, and visibility. Exact decorative counts remain flexible unless they affect gameplay or narrative logic.

### E. Background and layer compliance

Only permanent environmental narrative may remain in the base. Verify that every collectible, temporary clue, changing prop, character, body, interaction asset, and scan element is absent and represented in the removable-layer handoff instead.

### F. Period and reference leakage

Check architecture, furniture, technology, materials, and signage. Look for subjects inherited from references rather than requirements, including faces, people, city silhouettes, signature props, or copied compositions. Repair the reference plan before stacking more negative wording.

### G. Canvas and time-variant readiness

- First confirm that the submitted MJ job and result use the fixed `2:1` generation ratio.
- `story_progression`: preview the post-MJ `16:10` crop and confirm it retains all required content.
- `primary_exploration`: confirm a stable central frame and extendable left/right edges; any wider final ratio is decided after MJ.
- For day/night, approve one geometry master and report Photoshop manual relighting. Reject structural drift caused by separately generating the same space at another time of day.

## Candidate status

- `pass`: all hard requirements pass and finish is acceptable.
- `mj-pass-postprocess`: the character-free geometry master passes; only planned Photoshop extension, relighting, or removable-layer assembly remains.
- `partial`: useful foundation with a localized, repairable defect.
- `fail`: violates a hard requirement or requires structural regeneration.

## Grid action

- A candidate passes the hard vetoes and A–G: select the strongest and stop that view unless refinement was requested.
- A candidate is structurally valid with a localized finish issue: try a subtle variation first.
- A candidate is partial in A, C, D, or E but otherwise strong: consider a strong variation only if it can preserve the valid base.
- All candidates repeat the same camera, structure, scale, or layer defect: repair the prompt/reference plan and resubmit.
- Results fail for unrelated reasons with no stable base: simplify to camera, architecture, permanent environment, and exclusions before restoring finish language.

Complete a scene only when every required Midjourney view passes and the Photoshop handoff is explicit. A non-exploration scene remains incomplete until all three required views pass.
