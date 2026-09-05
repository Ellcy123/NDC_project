# Linked asset identity and two-sided Alpha review

Read before approving any linked Big, Icon, Map or Type 7 child, and before accepting cutouts. These are visual decisions; the existence of a JSON record does not establish them.

## One physical identity, different presentation roles

Keep one identity dossier per item ID: approved semantic raster path/hash, physical class, material, shape, component count, holes/fasteners, distinctive marks/damage, and actual state. List all required roles and explicitly omit only inapplicable roles.

Create a process-only side-by-side view of the exact proposed Big, Icon and Map, plus the native parent/Type 7 local view when applicable. Inspect it together with the high-resolution master, then inspect each role at its runtime size and local 200%. Save `identity_review.json` with the exact role paths/hashes, master path/hash, comparison view, per-feature findings, justified presentation differences, and `PASS`, `FAIL` or `NOT_CHECKED`. This record complements, not replaces, each role's stage review. Cross-role failure blocks the package even when every role has a separate old PASS.

Different viewing angle, scene lighting, reverse/folded document face, information density, and an explicitly required open/closed or before/after state may differ. Explain the visible change from the same physical object. Do not demand front-facing readable text in a paper Map to prove identity. Do not excuse a different material, missing component, different fastener or invented damage as low-information presentation.

For example, a pale torn cardboard luggage tag with an off-centre hole and short broken cord is not a dark rigid rectangular plaque with a centre hole and long rope merely because both say the same words (Unit4 4417). A clue Big's UI photograph frame does not turn the depicted physical object into a photograph inventory item. Only a clue whose actual collectible identity is a photograph may use a photographic object as its Icon.

## Separate what must survive from what must disappear

Before Alpha editing, identify and record source-native regions for:

- `BODY_MUST_KEEP`: every visible material surface, including low-contrast glass, liquid, reflections, thin needles, rims, paper thickness and small fasteners;
- `OWN_SHADOW_KEEP`: attributable shadow needed by this role;
- `REAL_GAPS_REMOVE`: genuine holes and spaces between objects;
- `BACKGROUND_REMOVE`: external matte/background and unrelated support;
- `FOREGROUND_EXCLUDE`: actual foreground occlusion, where applicable.

The lists are semantic ownership evidence, not masks manufactured by a global colour threshold. In a continuous translucent surface, transmitted source-background colour is not automatically a hole. For a scene Map, preserve accepted-parent RGB; do not invent semi-transparency that corrupts pixel alignment. For standalone Big/Icon glass, use faithful partial Alpha only when its material continuity, markings, highlights and edges survive visually on different backgrounds. Do not classify a high-lightness connected area as background without source comparison.

Unit4 4211 has two distinct tests: the syringe barrel is continuous glass that must survive; the space above the external plunger rod between the thumb rest, barrel flange and box is real background to remove. Protecting the former never authorizes a white patch in the latter. Inspect thin needle and metal rings separately. Restoring an entire bounding rectangle is not a valid repair.

For each output, inspect native/runtime views plus complete 200% edge/material views on black, white and contrasting checkerboard, together with Alpha-only and the original source. White reveals dark/dirty fringes; black reveals white matte; checkerboard and Alpha reveal missing structure. Record findings for both `missing_target_material` and `residual_background`, including the exact regions checked. Review the actual final Icon again: a valid high-resolution cutout can fail after reduction.

If reliable semi-transparent extraction is unavailable, restart from the intact source and preserve the complete glass silhouette/material; remove separable external background without cutting through it. If the result still needs manual glass work, mark `MANUAL_ALPHA_REQUIRED` and keep it in process with a precise handoff, not in a newly approved final package. Do not repeatedly lower a colour threshold until reflective/white material disappears. Never repair missing material by painting or generating only a disguised hole fill and claiming source preservation.

## Rejection, recovery and non-substitution

For user rejection, retain the original message/date or screenshot, exact affected files/hashes, rejected features and superseded review identifiers in a process-only rejection record. Mark the current role status and release index rejected immediately; do not erase history or silently rename a rejection into PASS. Unaffected roles remain independently inspectable candidates, not automatically rejected.

On restart, read the current rejection/review index before old release records. If history is missing, seek the exact project/task records and distinguish recovered user instructions from assistant inference. Keep concrete positive/negative examples in project process evidence, not ephemeral UI state alone. When a source changes, inspect its dependent roles; never mix independently regenerated generations merely because names match.
