# MJ scene review rubric

Review against current user corrections, source-supported architecture and the v4 contract, in this order. Record pass/partial/fail and the visible reason for each candidate; do not equate completion or aesthetic appeal with correctness.

| Priority | What to inspect | Failure or selection consequence |
|---|---|---|
| Camera and layout | Current handoff's camera position, view direction, depth, perspective and observable height/horizon cues | Failure of a hard camera or layout requirement in the current contract vetoes the candidate. |
| Architecture and routes | Source-supported spatial connections, structures, main masses, scale, required routes and silhouette separation | Added, missing or changed geometry fails when it contradicts the current contract's hard requirements. |
| Empty background | No visible people, faces, silhouettes or subject leakage; no baked user-excluded interactive content | Figure leakage fails. Missing deferred props never fails; ordinary incidental clutter is judged by its actual composition/editing impact. |
| Scene and state | Current scene's period, identity, requested lighting and source-supported material/surface state | Do not invent a different scene state or insert story-specific props to explain it. |
| Framing | Main masses readable; known display safe area if provided; coherent edges | Unknown game width or undone postproduction is not a failure. |
| Style lock | Approved palette/value compression, line hierarchy, grouped shadows, hard/soft edges, native brush language and materials | Cleaner but restyled results fail. |
| Texture coherence | Quiet planes, focal hierarchy, directional continuous material marks, depth-aware scale; no repeated stamps, seams or fragmented noise | Separate from style lock; both must pass. |
| Editing convenience | Separable forms, uncluttered routes/supporting surfaces, coherent light and readable floor/wall transitions | Rank hard-passing candidates; do not demand prop locations or sterile vector surfaces. |

A grid overview is sufficient for coarse hard-veto rejection and shortlisting only. Record unexamined fine criteria as NOT_CHECKED, not PASS; rejected candidates are retained history and do not need full local inspection. A shortlisted candidate is not yet formally approved. A shortlisted native file needs full-image review and complete original-pixel overlapping tile coverage before final style approval. Record `whole_image_checked`, `local_tile_coverage_complete`, tile count and concrete observations of linework, material direction/scale, edges, blur/sharpen mismatch and generation defects. Use architectural landmarks for scale; a prompt height label is not visual evidence of an exact measurement.

Keep `STYLE_LOCK_GATE` and `TEXTURE_COHERENCE_GATE` separate. Record each actual executed visual stage and validate current-file evidence. Hashes and dimensions prove technical properties only. Native MJ delivery is complete when all required views pass and their original files/provenance are available; retouching is outside this gate.


Across required views, compare source-supported architectural landmarks, connections and current scene state with accepted views during shortlisting, not only after every view has finished. Hide or reveal elements according to camera; do not accept inconsistent room topology. Source facts remain authoritative over generated views. For unchanged local-file selection/copy/publication, reuse a passing inspection only under [production-record.md](production-record.md); shared style/texture findings can point to one set of inspected original-pixel views.
