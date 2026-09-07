# NDC MJ prompt rules

## Generation scope

The scene chain ends at native MJ image delivery. Generate every scene at `--ar 2:1`. Do not append model-version flags. The operator selects `latest` in the live UI and enables HD when exposed.

Exploration requires exactly one `eye_level` view with eye-level three-point perspective, optical center 1.7–1.8 meters above the floor and upper-third horizon. Non-exploration requires three independent views in order: `frontal`, `oblique`, `overhead_45` (45 degrees downward). Preserve scene facts and master light state across views. Do not create collages.

## Reduce source facts before writing

Current user corrections override source requirements and historical prompts. Retain source-supported architecture, circulation, structural fixtures, scene-defining major masses, material and surface conditions, light and period cues. Default to `defer_gameplay_props`: specified props, collectibles, clues and game-defined environmental-narrative objects stay outside MJ prompts even when permanent. A few period-appropriate ordinary ambient objects may be added freely as non-interactive set dressing; they remain low-priority, cannot stand in for deferred evidence, and must not change the layout or crowd the scene. Do not require their future positions or invent prop-friendly surfaces. User-explicit MJ inclusions are recorded exceptions.

Character names, bodies, poses and actions remain only in source provenance. Do not convert omitted actions into extra objects. Add the empty-background constraint to the hard contract; in English submission text put character tokens only in one final `--no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes` parameter.

## Camera-first composition

Write: camera position/direction → scene identity/period → foreground-middle-background and left-center-right major masses → light → approved style/texture → parameters. Favor a concise paragraph, not an inventory. Do not let style adjectives outweigh spatial instructions.

Derive camera position, view direction and visible spatial relationships from the current scene requirement. Define relationships among the required main masses, preserve continuous supporting surfaces and separate silhouettes so later manual editing remains practical. Quiet surfaces still retain approved brush texture. No arbitrary empty evidence patches are required.

An exact furniture count is hard only when the source or current user makes it spatially essential. Use architectural scale proxies. Mark unsupported furniture placement as an assumption. For changed viewpoints, reconstruct depth relationships instead of carrying old foreground labels forward.

## 4. NDC scene rendering language

The stable cross-reference core is:

`stylized graphic environment illustration, compressed large-scale shape design, deep grouped shadow masses, controlled hard-soft edge hierarchy, clear structural edges on focal architecture, softer atmospheric transitions in distance, restrained charcoal, brown-gray or olive-gray base palette, limited warm amber or muted orange focal accents, matte painterly-digital surface, scale-aware grain and directional texture, stylized realism.`

Treat this as calibration vocabulary, not an unchanging boilerplate. It describes the relationship among shape, value, edge, color, and texture; it does not require every scene to share the same saturation or contour weight.

Add branch clauses only with complete-image and local-tile evidence from the approved references for the current scene:

- `vibrant jewel tones` or `rich color saturation`: only when the approved scene examples actually use broad saturated color families;
- `bold calligraphic black ink contours`: only for a clearly graphic focal-object or character-derived branch; do not impose it on rain atmosphere, distant buildings, every wall edge, or every interior molding;
- `deliberate digital brushwork` or `stylized digital thick painting`: only when visible brush direction and scale are supported locally; do not use them as synonyms for generic image texture;
- `clean planes of solid color`: useful for focal mass compression, but combine with material- and distance-specific texture where the reference shows it.

The two mandatory static Style References and the optional courthouse calibration example have different jobs:

- `ndc-static-style-character-graphic.png` controls graphic compression, hard shape massing, edge economy, and limited warm emphasis only. It must not contribute people, costume shapes, skin treatment, or character composition to a scene.
- `ndc-static-style-city-rain.jpg` controls rain atmosphere, matte weather texture, vertical depth, charcoal/brown-gray grouping, and restrained orange light. It does not define interior architectural linework.
- `approved-courthouse-scene-style.png` calibrates readable interior architecture, thin stable construction lines, subdued olive/charcoal/amber color grouping, hard geometry with soft daylight shafts, and restrained material detail.

Select only supported clauses. Shorten the style block when it competes with scene content. Avoid contradictory combinations such as demanding full jewel-tone saturation while also demanding a desaturated monochrome result.

Support must come from both complete-image review and complete local-tile coverage under `style-analysis-protocol.md`. Do not add brushwork, texture, edge, grain, or material claims from a reduced overview alone. Record whether a clause is a stable cross-reference trait, a scene/material branch, a minority option, or an artifact before promoting it into executable prompt language.

<!-- NDC_TEXTURE_COHERENCE_MODULE:BEGIN -->
### Style-locked texture-coherence control

Texture coherence is a rendering discipline, not a new style. Preserve the approved scene palette, value compression, line hierarchy, grouped shadows, hard-soft edge behavior, native brush language, material treatment, and every supported branch clause. Never use `simplify the art style`, `minimalist illustration`, `flat vector style`, `smooth clean surfaces`, `remove brush texture`, or a similar global cleanup instruction.

Build one `texture_contract` before drafting view prompts:

- `focal_detail_zones`: gameplay-critical architecture, routes, and permanent narrative focal areas where semantic detail must remain readable;
- `secondary_detail_zones`: supporting structures that need silhouette, major turns, and limited material cues;
- `quiet_zones`: broad walls, floors, ceilings, shadow masses, sky, or other planes that retain only reference-supported matte grain or directional brush behavior;
- `distant_zones`: large value groups and atmospheric transitions without newly invented hard micro-edges;
- `material_texture_rules`: direction, scale, density, and continuity by material, distance, weather, and perspective;
- `prohibited_artifacts`: non-semantic micro-detail, repeated texture stamps, random cracks, speckled noise, fragmented short brush marks, composition-obstructing clutter, and uniformly sharpened edges. Sparse ordinary ambient dressing is allowed; it is not a texture artifact merely because it adds detail.

Use this control language after the approved rendering-language clauses and before exclusions:

`preserve the approved NDC rendering language exactly, organize the scene through compressed large-scale shapes and grouped shadow masses, material texture remains directional, continuous, scale-aware and subordinate to object structure, perspective, distance and lighting, concentrate semantic detail around the declared focal architecture and gameplay areas, keep secondary surfaces restrained and quiet planes visually quiet while retaining the approved native brush language, broad distant value groups with no newly invented hard micro-edges`

Do not paste a universal texture-negative parameter into every Midjourney prompt. Add a targeted exclusion only after a real batch shows one recurrent damaging artifact. Texture control must never delete supported weather grain, wear, dry brush, impasto, paper grain, architectural linework, or identity-bearing detail merely because it increases local frequency.
<!-- NDC_TEXTURE_COHERENCE_MODULE:END -->

Useful camera language includes:

- the exact exploration lock: `eye-level three-point perspective, camera optical center 1.7–1.8 meters above the floor, horizon at the upper third`;
- `eye-level perspective` or a source-supported concrete camera height for non-exploration views;
- `two-point perspective` for room corners and oblique exteriors;
- `predominantly frontal view` for the non-exploration frontal variant;
- `approximately 45-degree downward view` for the non-exploration overhead variant;
- `horizon near the upper third` when a slightly elevated game-background view is needed;
- `deep focus` when gameplay objects across the scene must remain readable.

Use a focal-length feel when lens distortion changes the architecture: around `35–40mm` is a useful starting point for a readable corridor or room, but it is not universal. Choose a focus treatment that keeps all hard objects and gameplay routes readable.

Validate a critical camera height through visible architecture. For example, if the camera must sit above waist-high wainscoting, the image should reveal the expected top surface or edge relationship; if that surface disappears, the camera may be too low even when the prompt says `eye-level`.

Use `--ar 2:1` exactly once for every Midjourney scene prompt. Never replace it with `16:10` or a wider delivery ratio. A known downstream crop is framing context only; the workflow ends with the native MJ image. Default the handoff to `parameters.model: "latest"` unless the user explicitly requests a specific model for the current job. Do not append a model-version parameter to the prompt text; the operator must use the current latest model in the live Midjourney settings.

For day/night variants, generate one geometry master by default. Submit only the requested master state. Other time variants and their production methods are outside this delivery unless explicitly requested.

## 5. Exclusions

Do not paste a universal negative block into every prompt beyond the mandatory character-free exclusion. Select other damaging or recurrent failure modes for the specific scene. Encode the mandatory exclusion as a dedicated Midjourney parameter, not positive prose:

`--no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes`

Additional scene-specific exclusions may include:

`modern fixtures, text, UI, fog, heavy dust, photorealism, 3D render, blurry details, messy brushwork`

Object exclusions must come from the requirement. If a reference strongly contains an unwanted subject, reject or change the reference instead of adding a longer exclusion list.

## 6. Reference roles and leakage

- Use a `style` reference for palette, line, and texture only when its subject is compatible enough not to dominate.
- Use an `environment` reference for period architecture and material vocabulary; exclude deferred prop content.
- Use a `composition` reference for framing and spatial massing.
- Use an `identity` reference only for an intended architectural or room-defining element, or a current user-explicit MJ inclusion; never attach deferred gameplay-prop identity references.
- Mark a reference `reject` when it introduces an unwanted person, exterior skyline, modern object, or unrelated dominant motif.

Do not label every image as a style reference. A character portrait and a city exterior used together on an empty interior can produce unwanted figures and city windows even when the text says `no people`.

## Submission check

- Required views and current user camera are explicit; first submission matches the exact handoff prompt.
- No game-defined deferred props in positive text or reference roles; sparse non-interactive ambient details are permitted; missing props cannot fail the MJ image.
- No postprocess_handoff, operational canvas_plan, layer placement map or required relighting phase.
- Known downstream crop/pan constraints are optional framing context; missing final game size is not a blocker.
- Native file, actual dimensions, exact prompt, job identity and visual/texture review form the MJ delivery package.
