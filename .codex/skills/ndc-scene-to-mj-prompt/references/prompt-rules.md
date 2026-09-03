# NDC Midjourney scene prompt rules

## 1. Prompt objective

Translate an NDC scene into a readable game-background view set, not an architectural blueprint and not a prose summary. Optimize in this order:

1. Core composition and camera readability.
2. Gameplay- or story-critical objects.
3. Scene identity and period credibility.
4. Lighting, material, and approved rendering language.
5. Decorative richness.

A beautiful image that loses the core layout or key object is a failure. A correct image may vary harmless details such as the exact number of windows, frames, benches, books, or lamps.

## Required view set

Classify the scene from gameplay requirements before writing camera language:

- `exploration`: the player must search, inspect, or collect props or evidence. Output exactly one `eye_level` prompt. It must state an eye-level three-point-perspective composition, camera optical center `1.7–1.8 meters` above the floor, and the horizon at the upper third. Treat all three clauses as hard requirements.
- `non_exploration`: no searchable evidence or prop interaction is required. Output exactly three prompts: `frontal`, `oblique`, and `overhead_45`. `overhead_45` means an approximately 45-degree downward camera angle, not a 45-degree horizontal rotation.

Do not output alternative angles for an exploration scene. Do not omit any of the three required non-exploration views. A view set represents independent Midjourney jobs, never a multi-panel image.

Keep scene identity, architecture, core objects, lighting state, exclusions, and rendering language invariant across non-exploration views. Rebuild only the camera-dependent foreground-middle-background and left-center-right relationships.

## Canvas-use rule

Classify `scene.canvas_use` independently from view count:

- `story_progression`: fixed narrative/dialogue use; generate at `2:1`, then crop/reframe to the standard `16:10` delivery after MJ.
- `primary_exploration`: main in-game exploration use; generate at `2:1`, protect a central safe area, and plan any additional Photoshop Firefly Generative Fill on the left and right after MJ for mouse-panning width.

Midjourney generation ratio is always `2:1`, regardless of scene purpose. Treat `16:10` and every wider exploration ratio as post-MJ delivery decisions. If an exploration final size is absent, mark final width unresolved and hand off the extension plan. Preserve continuous walls, floor, ceiling, street, skyline, and light direction at both edges so Firefly can extend them safely.

## Character-free scene invariant

Every NDC scene image is an empty environment background. Do not place people, named characters, crowds, bodies, faces, human figures, or silhouettes in the image, even when the source scene describes character blocking or actions.

Keep character facts verbatim only in `original_requirement`. In the normalized contract and prompt, translate character activity into environmental traces:

- guarded or occupied entrance → physical barricades, rope stanchions, signage, or a visibly restricted route;
- files being moved → unattended archive carts, stacked boxes, and an open service path;
- characters waiting near a side door → a clearly visible secondary entrance and an unobstructed approach;
- recent activity → displaced furniture, open doors, lighting state, footprints, or other non-human traces supported by the source.

Always add `empty environment with no visible characters` to `hard`. Always list `people, named characters, crowds, human figures, faces, bodies, silhouettes` under `must_not_have`. Do not repeat these tokens in positive prompt prose. Put them only once at the end of `prompt_en` as `--no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes`; express the same rule as non-submitted review text in `prompt_zh`.

Do not use portrait or character references for scene content, composition, environment, or identity. A separate operator workflow may apply one only as a style reference when it explicitly guards against subject leakage; this exception never relaxes the empty-environment requirement.

Character-scale validation is separate from generation. Use architectural proxies such as door height, handrails, desks, wainscot, windows, and stair risers. A temporary neutral silhouette may be placed over a generated candidate for scale review, but it must never enter positive prompt text, an uploaded composition reference, or the final background.

## Background and layer contract

Only permanent environmental storytelling may be baked into the scene background.

- `base_environment_narrative`: permanent architecture, wear, fixed furnishings, lasting family/class/profession/incident traces; allowed in the base.
- `interaction_closeup`: close-up evidence; separate.
- `scan_overlay`: oil, residue, imprint, analysis highlight; separate.
- `collectible_layer`: every item that can be picked up; separate.
- `transient_story_layer`: characters, bodies, temporary or Loop-specific props, and anything that may disappear; separate.

Do not describe separated content positively in `prompt_en` or `prompt_zh`. Reserve a visible, source-supported placement area when later alignment matters.

## 2. Requirement precision

- Phrase `hard` requirements explicitly and early.
- Phrase `soft` requirements by type and approximate distribution, not exact count.
- Leave `flexible` details to Midjourney unless they help composition.
- Make an exact number hard only when the number itself carries gameplay, evidence, route, or narrative meaning.
- Prefer `a row of small high clerestory windows` over `exactly four to six windows` when the count is not meaningful.

## 3. Scene prompt order

Use this order for each English view paragraph:

1. Era, location, scene type, time of day.
2. Shot scale, camera height, view direction, perspective, and depth.
3. Core spatial layout from foreground to background or left to right.
4. Core objects with position, scale, and relationship.
5. Secondary architecture, furniture, and period props.
6. Lighting direction, contrast, and palette.
7. Rendering language.
8. Concise exclusions.
9. Stable parameters such as aspect ratio.

Do not bury core objects after a long style block.

Before compressing this information into view paragraphs, write a short shared visual brief and an importance-ranked scene description for each view. The brief keeps only drawable facts. Each scene description must expose its own camera and spatial graph so another reviewer can audit it without reverse-engineering the prompt.

For every architecture-led view, define:

- depth anchors: foreground, middle ground, background;
- lateral anchors: left, center, right;
- structural relations: connected to, separated from, behind, in front of, aligned with, leading toward, partially occluding, or remaining fully visible;
- relative scale and route logic for major doors, windows, walls, counters, stairs, corridors, and critical props;
- camera calibration: a wall feature or object whose visible top or edge confirms the intended height.

For every changed viewpoint, name the horizontal rotation direction and approximate angle, state any elevation change, and rebuild all depth and lateral anchors. Do not keep source-image foreground/background wording after the camera has moved unless it remains geometrically valid.

## 4. NDC scene rendering language

The stable cross-reference core is:

`stylized graphic environment illustration, compressed large-scale shape design, deep grouped shadow masses, controlled hard-soft edge hierarchy, clear structural edges on focal architecture, softer atmospheric transitions in distance, restrained charcoal, brown-gray or olive-gray base palette, limited warm amber or muted orange focal accents, matte painterly-digital surface, scale-aware grain and directional texture, stylized realism.`

Treat this as calibration vocabulary, not an unchanging boilerplate. It describes the relationship among shape, value, edge, color, and texture; it does not require every scene to share the same saturation or contour weight.

Add branch clauses only with complete-image and local-tile evidence from the approved references for the current scene:

- `vibrant jewel tones` or `rich color saturation`: only when the approved scene examples actually use broad saturated color families;
- `bold calligraphic black ink contours`: only for a clearly graphic focal-object or character-derived branch; do not impose it on rain atmosphere, distant buildings, every wall edge, or every interior molding;
- `deliberate digital brushwork` or `stylized digital thick painting`: only when visible brush direction and scale are supported locally; do not use them as synonyms for generic image texture;
- `clean planes of solid color`: useful for focal mass compression, but combine with material- and distance-specific texture where the reference shows it.

The three static references have different jobs:

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
- `prohibited_artifacts`: non-semantic micro-detail, repeated texture stamps, random cracks, speckled noise, fragmented short brush marks, decorative clutter, and uniformly sharpened edges.

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

Use `--ar 2:1` exactly once for every Midjourney scene prompt. Never replace it with `16:10` or a wider delivery ratio. Plan the `16:10` story crop or exploration extension only after MJ generation. Default the handoff to `parameters.model: "latest"` unless the user explicitly requests a specific model for the current job. Do not append a model-version parameter to the prompt text; the operator must use the current latest model in the live Midjourney settings.

For day/night variants, generate one geometry master by default. Keep camera, crop, architecture, furniture, object placement, and routes locked; hand off manual Photoshop relighting and color work instead of asking Midjourney to regenerate the alternate time.

## 5. Exclusions

Do not paste a universal negative block into every prompt beyond the mandatory character-free exclusion. Select other damaging or recurrent failure modes for the specific scene. Encode the mandatory exclusion as a dedicated Midjourney parameter, not positive prose:

`--no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes`

Additional scene-specific exclusions may include:

`modern fixtures, text, UI, fog, heavy dust, photorealism, 3D render, blurry details, messy brushwork`

Object exclusions must come from the requirement. If a reference strongly contains an unwanted subject, reject or change the reference instead of adding a longer exclusion list.

## 6. Reference roles and leakage

- Use a `style` reference for palette, line, and texture only when its subject is compatible enough not to dominate.
- Use an `environment` reference for period architecture and props.
- Use a `composition` reference for framing and spatial massing.
- Use an `identity` reference only for a uniquely identifiable non-character object meant to appear.
- Mark a reference `reject` when it introduces an unwanted person, exterior skyline, modern object, or unrelated dominant motif.

Do not label every image as a style reference. A character portrait and a city exterior used together on an empty interior can produce unwanted figures and city windows even when the text says `no people`.

## 7. Calibrated exploration-scene example

Requirement classification:

```yaml
hard:
  - 1928 courthouse evidence-search hallway in daytime
  - exactly one eye-level three-point-perspective view
  - camera height 1.7-1.8 meters
  - horizon at the upper third
  - closed double courtroom door at the far end
  - long red runner leading toward the courtroom
  - one nearest evidence table with a clear reserved placement area for a separately layered docket folder
  - no people or modern recording equipment
soft:
  - small high clerestory windows on the right
  - heavy wooden benches along both sides
  - dark wood wainscoting and Neoclassical details
flexible:
  - exact number of windows, benches, paintings, and decorative panels
```

Copy-ready `eye_level` prompt:

```text
1928 Chicago courthouse evidence-search hallway in daylight, a single eye-level three-point-perspective game-background view, camera optical center 1.7–1.8 meters above the floor, horizon at the upper third, a closed carved double courtroom door anchoring the far end, a long muted red runner leading from the foreground to that door, one nearest evidence table with a clear uncluttered placement area for a later interactive layer, one waiting-room doorway and framed Neoclassical paintings along the left wall, a row of small high clerestory windows along the right wall, heavy 1920s wooden benches arranged along both sides, deep walnut wainscoting, matte plaster and a coffered ceiling, deep focus, parallel daylight beams crossing the floor, subdued olive-gray, charcoal and walnut color grouping, limited warm amber highlights against deep grouped shadows, compressed large-scale shape design, thin stable architectural construction lines on focal doors, moldings and panels, hard geometric edges with soft daylight shafts and restrained atmospheric transitions, scale-aware fine grain and matte painterly-digital texture, stylized realism, unoccupied environment --ar 2:1 --no people, person, humans, characters, crowds, figures, faces, bodies, silhouettes, microphones, recording equipment, cables, readable text, modern fixtures
```

The window type matters; the exact count does not.

## 8. Final prompt checks

- Exactly one copy-ready English paragraph for `exploration`; exactly three for `non_exploration`.
- Exploration uses only `eye_level` and states the three-point perspective, `1.7–1.8 meters`, and upper-third horizon lock.
- Non-exploration uses exactly `frontal`, `oblique`, and `overhead_45`; the last clearly means a roughly 45-degree downward camera angle.
- No `/imagine prompt:` prefix.
- No model-version parameter.
- Handoff model defaults to `latest` unless the current user request explicitly requests a specific model.
- No unsupported image URLs in prompt text.
- No contradiction between positive and exclusion clauses.
- No character names, human actions, poses, crowds, figures, faces, bodies, or silhouettes as positive content in any prompt counterpart.
- `hard`, `must_not_have`, and every prompt counterpart enforce an empty environment with no visible characters; character tokens occur in `prompt_en` only inside the final dedicated `--no` parameter.
- Positive prompt text contains no character scale, position, action, occupation, body, or silhouette language; scale uses architecture only.
- Only permanent `base_environment_narrative` content is baked in; collectible, transient, close-up, and scan content remains separate.
- Every MJ prompt uses `--ar 2:1`; `story_progression` has a post-MJ `16:10` crop-safe plan, and `primary_exploration` has a center-safe and optional post-MJ Photoshop Firefly horizontal-extension plan.
- Day/night variants share the same geometry master and default to Photoshop manual relighting.
- No decorative detail has more emphasis than a hard object.
- Every view's scene description identifies foreground, middle ground, background, and major left-center-right anchors.
- Architecture-defining masses have explicit connection, separation, overlap, or route relationships.
- Any critical camera height is backed by an observable calibration landmark.
- Every viewpoint conversion includes direction, approximate rotation, elevation, and a rebuilt spatial graph.
- Shared scene facts do not drift between the three non-exploration prompts.
- Chinese counterpart preserves the same priorities instead of expanding the design.
- Every style-analysis-derived clause has complete-image evidence and complete overlap-safe local coverage; the analysis records image entries, deduplicated images, tile count, stable traits, branch traits, minority traits, and artifacts.
- `texture_contract` locks approved style authority, identifies focal/secondary/quiet/distant zones, and defines material-specific direction, scale, density, continuity, and prohibited artifacts.
- Every view implements the same texture contract without changing the approved palette, value structure, line hierarchy, brush language, edge hierarchy, or material treatment.
