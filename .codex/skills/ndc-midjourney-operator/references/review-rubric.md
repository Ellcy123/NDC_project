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

Perform this category in two passes. First inspect the complete image. Then follow `style-analysis-protocol.md` and inspect every overlap-safe original-resolution tile, including edges, quiet walls/floors, deepest shadows, brightest lights, sky, and future extension seams. Check line-weight rhythm and endings, brush direction and scale, hard/soft edge hierarchy, material-specific texture, repeated texture stamps, local blur/sharpen mismatch, generated joins, and compression artifacts. Record stable traits separately from material branches, minority traits, and noise. Style cannot be marked `pass` unless both whole-image review and complete local coverage are recorded.

Use this calibrated scene baseline when comparing references and candidates:

- Stable core: compressed large shapes, deep grouped shadows, restrained charcoal/brown-gray/olive-gray bases, limited warm focal accents, controlled hard structural edges plus softer atmospheric transitions, and texture whose direction and density respond to material, distance, weather, and scale.
- Character-graphic reference branch: hard massing, edge economy, limited warm emphasis; never transfer its person, costume, skin, or composition into the empty environment.
- City-rain reference branch: rain streaks, matte weather grain, vertical depth, restrained orange illumination; do not demand its skyline, night state, or rain in unrelated scenes.
- Courthouse/interior branch when supported by the handoff: thin stable architectural lines, subdued olive/charcoal/amber grouping, hard doors/panels/moldings, soft daylight shafts, and restrained surface wear.
- Conditional only: jewel-tone saturation, broadly applied calligraphic black contours, and thick-paint language. Their absence is not a failure unless the current approved scene reference requires them.

Fail style review when texture is uniformly stamped across depth, rain or brush direction contradicts surfaces and perspective, all architecture receives the same heavy contour, distant edges are sharpened like the foreground, or local seams/duplicated patterns are visible.

<!-- NDC_TEXTURE_COHERENCE_MODULE:BEGIN -->
### B2. Texture coherence — independent fail-closed gate

Do not merge this gate into a generic style score. First freeze the approved palette/value compression, line-weight hierarchy, grouped shadows, hard-soft edge behavior, native brush language, and material treatment under `STYLE_LOCK_GATE`. Then evaluate only texture frequency, continuity, scale, and distribution under `TEXTURE_COHERENCE_GATE`.

Require all of the following:

- large shapes and grouped shadows remain readable before surface detail;
- semantic detail concentrates around the declared focal architecture, gameplay route, and permanent narrative focal areas;
- secondary structures use limited material cues and quiet planes remain quiet without losing reference-supported grain or brush language;
- material texture follows the surface, perspective, weather, lighting, and depth, with a consistent scale for that plane;
- distant areas do not acquire foreground-strength hard micro-edges;
- repeated stamps, random cracks, speckled noise, fragmented short marks, arbitrary micro-ornament, and uniform sharpening are absent.

Fail when either gate is `FAIL` or `NOT_CHECKED`. A texture-coherent image with changed art style is not a pass; a style-faithful image with broken or overfilled texture is not a pass. For a local formal file, validate the fail-closed record with `python scripts/art_pipeline/ndc_art.py tool texture`; automatic image-quality scores may screen candidates but cannot approve either artistic gate.
<!-- NDC_TEXTURE_COHERENCE_MODULE:END -->

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

- A candidate passes the hard vetoes, A–G, `STYLE_LOCK_GATE`, and `TEXTURE_COHERENCE_GATE`: select the strongest and stop that view unless refinement was requested.
- A candidate is structurally valid with a localized finish issue: try a subtle variation first.
- A candidate is partial in A, C, D, or E but otherwise strong: consider a strong variation only if it can preserve the valid base.
- All candidates repeat the same camera, structure, scale, or layer defect: repair the prompt/reference plan and resubmit.
- Results fail for unrelated reasons with no stable base: simplify to camera, architecture, permanent environment, and exclusions before restoring finish language.

Complete a scene only when every required Midjourney view passes and the Photoshop handoff is explicit. A non-exploration scene remains incomplete until all three required views pass.
