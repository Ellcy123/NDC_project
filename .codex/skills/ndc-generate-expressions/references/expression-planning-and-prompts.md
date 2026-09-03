# Expression planning and generation prompts

## Planning

Inventory reusable approved expressions before generation. Calm is the approved portrait and never enters the generation queue. Every non-calm requirement records:

- `expression_id` and display name;
- `basic_emotion`, `micro_expression`, `narrative_state`, or `action_state`;
- brow, eyelid/gaze, mouth, and supporting performance signals;
- `intensity_target`, signature cues, calm contrast, forbidden confusions, and thumbnail target;
- small permitted shoulder, torso, head/neck, gaze, and garment response;
- `viewpoint_change=false` unless separately approved.

Default basic emotions and narrative states to `2_readable`. Never lower intensity to rescue a weak candidate.

## Reference order

1. Image 1: user-confirmed completed portrait; sole identity, viewpoint, calm, and generation source.
2. Optional approved character card: costume/style verification only.
3. Optional same-source face evidence: identity verification only when a retry needs it.

Never use another expression as a source. Never use a generated transparent or greenscreen output as a source.

## Generation prompt

```text
Use Image 1 as the immutable character, identity, viewpoint, costume, lighting, palette, style, texture, and body-proportion authority. Generate one new expression from this exact portrait on a clean, uniform light-neutral background.

Target expression: 【display_name】.
Brow signal: 【brow_signal】.
Eyelid and gaze signal: 【eye_signal】.
Mouth signal: 【mouth_signal】.
Intensity target: 【intensity_target】.
Required signature cues: 【numbered_signature_cues】.
Contrast against calm: 【contrast_against_calm】.
Forbidden confusions: 【forbidden_confusions】.
Thumbnail readability: 【thumbnail_readability_target】.
Allowed small performance delta: 【performance_delta】.

Preserve the exact person-specific facial geometry, approved camera/viewpoint family and viewing side, age, hair, costume construction, body type, lower-bust structure, lighting direction and occlusion shadows, palette, line hierarchy, brush language, material treatment, and stable texture density. Change only the planned expression and recorded small performance delta.

Do not redesign, beautify, de-age, rotate to another viewpoint, move the camera, change costume, add a prop unless explicitly authorized, add text, add scenery, generate transparency, generate a green background, remove the background, complete or extend any body region, sharpen globally, or add unsupported micro-detail.
```

Image generation produces an artistic candidate only. The user later handles background processing manually by editing the non-final handoff file in place; Codex only reviews the resulting Alpha and edge RGB.

## Retry discipline

Allow at most A1 initial, A2 targeted, and A3 final. Each retry begins from the approved portrait and changes only the failed variable. After A3, keep the closest file as `CANDIDATE_ONLY`; do not weaken gates.
