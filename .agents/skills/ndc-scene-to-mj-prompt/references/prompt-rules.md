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

- `exploration`: the player must search, inspect, or collect props or evidence. Output exactly one `eye_level` prompt. It must state an eye-level three-point-perspective composition aligned with a standing eye line, camera height `1.7–1.8 meters`, and the horizon at the upper third. Treat all four clauses as hard requirements.
- `non_exploration`: no searchable evidence or prop interaction is required. Output exactly three prompts: `frontal`, `oblique`, and `overhead_45`. `overhead_45` means an approximately 45-degree downward camera angle, not a 45-degree horizontal rotation.

Do not output alternative angles for an exploration scene. Do not omit any of the three required non-exploration views. A view set represents independent Midjourney jobs, never a multi-panel image.

Keep scene identity, architecture, core objects, lighting state, exclusions, and rendering language invariant across non-exploration views. Rebuild only the camera-dependent foreground-middle-background and left-center-right relationships.

## Character-free scene invariant

Every NDC scene image is an empty environment background. Do not place people, named characters, crowds, bodies, faces, human figures, or silhouettes in the image, even when the source scene describes character blocking or actions.

Keep character facts verbatim only in `original_requirement`. In the normalized contract and prompt, translate character activity into environmental traces:

- guarded or occupied entrance → physical barricades, rope stanchions, signage, or a visibly restricted route;
- files being moved → unattended archive carts, stacked boxes, and an open service path;
- characters waiting near a side door → a clearly visible secondary entrance and an unobstructed approach;
- recent activity → displaced furniture, open doors, lighting state, footprints, or other non-human traces supported by the source.

Always add `empty environment with no visible characters` to `hard`. Always list `people, named characters, crowds, human figures, faces, bodies, silhouettes` under `must_not_have` and express the same exclusion concisely in both prompt counterparts.

Do not use portrait or character references for scene content, composition, environment, or identity. A separate operator workflow may apply one only as a style reference when it explicitly guards against subject leakage; this exception never relaxes the empty-environment requirement.

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

Use this as a calibration vocabulary, not an unchanging boilerplate:

`Technicolor graphic style, full color, vibrant jewel tones, rich color saturation, bold calligraphic black ink contours with varied line weight, stylized digital thick painting, deliberate digital brushwork, clean planes of solid color, matte digital texture, high-contrast chiaroscuro, deep graphic shadows, warm practical amber light, stylized realism.`

Select only the clauses supported by the user's approved examples. Shorten the style block when it competes with scene content. Avoid contradictory combinations such as demanding full jewel-tone saturation while also demanding a desaturated monochrome result.

Useful camera language includes:

- the exact exploration lock: `eye-level three-point perspective aligned with a standing eye line, camera height 1.7–1.8 meters, horizon at the upper third`;
- `eye-level perspective` or a source-supported concrete camera height for non-exploration views;
- `strict centered one-point perspective` for axial corridors;
- `two-point perspective` for room corners and oblique exteriors;
- `predominantly frontal view` for the non-exploration frontal variant;
- `approximately 45-degree downward view` for the non-exploration overhead variant;
- `horizon near the upper third` when a slightly elevated game-background view is needed;
- `deep focus` when gameplay objects across the scene must remain readable.

Use a focal-length feel when lens distortion changes the architecture: around `35–40mm` is a useful starting point for a readable corridor or room, but it is not universal. Choose shallow, medium-deep, or deep focus according to scene readability; do not paste `shallow depth of field` into a game background when it would blur a hard object.

Validate a critical camera height through visible architecture. For example, if the camera must sit above waist-high wainscoting, the image should reveal the expected top surface or edge relationship; if that surface disappears, the camera may be too low even when the prompt says `eye-level`.

Use `--ar 2:1` as the default for an NDC scene background only when no other aspect ratio is specified. Default the handoff to `parameters.model: "8.1"` unless the user explicitly requests another version for the current job. Do not append `--v 8.1` or another model-version parameter to the prompt text; the operator must select the declared version in the live Midjourney settings.

## 5. Exclusions

Do not paste a universal negative block into every prompt beyond the mandatory character-free exclusion. Select other damaging or recurrent failure modes for the specific scene. The mandatory exclusion is:

`no people, named characters, crowds, human figures, faces, bodies, or silhouettes`

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
  - one searchable sealed docket folder on the nearest evidence table
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
1928 Chicago courthouse evidence-search hallway in daylight, a single eye-level three-point-perspective game-background view aligned with a standing eye line, camera height 1.7–1.8 meters, horizon at the upper third, a closed carved double courtroom door anchoring the far end, a long muted red runner leading from the foreground to that door, one sealed docket folder clearly readable as a searchable object on the nearest evidence table, one waiting-room doorway and framed Neoclassical paintings along the left wall, a row of small high clerestory windows along the right wall, heavy 1920s wooden benches arranged along both sides, deep walnut wainscoting, matte plaster and a coffered ceiling, deep focus, parallel daylight beams crossing the floor, warm amber highlights against deep graphic shadows, Technicolor graphic illustration, expressive black ink contours, clean solid color planes, matte digital texture, stylized realism, no people, microphones, recording equipment, cables, readable text, or modern fixtures --ar 2:1
```

The window type matters; the exact count does not.

## 8. Final prompt checks

- Exactly one copy-ready English paragraph for `exploration`; exactly three for `non_exploration`.
- Exploration uses only `eye_level` and states the three-point perspective, `1.7–1.8 meters`, and upper-third horizon lock.
- Non-exploration uses exactly `frontal`, `oblique`, and `overhead_45`; the last clearly means a roughly 45-degree downward camera angle.
- No `/imagine prompt:` prefix.
- No model-version parameter.
- Handoff model defaults to `8.1` unless the current user request explicitly overrides it.
- No unsupported image URLs in prompt text.
- No contradiction between positive and exclusion clauses.
- No character names, human actions, poses, crowds, figures, faces, bodies, or silhouettes as positive content in any prompt counterpart.
- `hard`, `must_not_have`, and every `prompt_en` and `prompt_zh` enforce an empty environment with no visible characters.
- No decorative detail has more emphasis than a hard object.
- Every view's scene description identifies foreground, middle ground, background, and major left-center-right anchors.
- Architecture-defining masses have explicit connection, separation, overlap, or route relationships.
- Any critical camera height is backed by an observable calibration landmark.
- Every viewpoint conversion includes direction, approximate rotation, elevation, and a rebuilt spatial graph.
- Shared scene facts do not drift between the three non-exploration prompts.
- Chinese counterpart preserves the same priorities instead of expanding the design.
