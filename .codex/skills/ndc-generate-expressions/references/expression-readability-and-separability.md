# Expression readability and set separability

## Why this gate exists

Identity, viewpoint, style, color, and profile geometry may all pass while the delivered expressions still read as the same neutral face. A changed pixel distribution, rerendered texture, or technically present eyebrow movement does not prove that the state is readable. Formal delivery therefore requires semantic amplitude and pairwise separability evidence in addition to continuity.

## Intensity scale

Use exactly one target per expression:

- `0_neutral`: calm anchor only.
- `1_micro`: intentionally restrained; readable in the matched face comparison and carried by at least two independent facial regions. Use only when the requirement itself calls for a micro-expression.
- `2_readable`: default for basic emotions and narrative states; recognizable at delivery thumbnail scale and carried by at least three independent regions, including at least two facial regions.
- `3_strong`: emphatic narrative or basic emotion; immediately readable without theatrical distortion or identity change.

Do not lower an intensity target to make a weak candidate pass. When the user's feedback says expressions are too similar, affected non-calm states default to at least `2_readable` unless the user explicitly preserves a micro-expression.

## Required planning fields

Every expression manifest entry must record:

```json
{
  "intensity_target": "2_readable",
  "signature_cues": [
    {"region": "brows", "signal": "inner brows clearly draw down and inward"},
    {"region": "eyes", "signal": "upper eyelids lower and gaze hardens"},
    {"region": "mouth", "signal": "lips compress with one corner pulled down"},
    {"region": "jaw_shoulders", "signal": "jaw tightens and shoulders square slightly"}
  ],
  "contrast_against_calm": "must exceed the character's existing stern neutral baseline",
  "forbidden_confusions": ["calm", "recollecting_observer"],
  "thumbnail_readability_target": "recognizable_at_256px_subject_height"
}
```

`signature_cues` are observable changes, not emotion synonyms. Use distinct regions. Valid facial regions include `brows`, `upper_eyelids`, `lower_eyelids`, `gaze`, `cheeks`, `nose_nasolabial`, `mouth`, and `jaw_chin`. Supporting regions may include `head_neck`, `shoulders`, `upper_torso`, and `garment_response`.

For characters whose design hides expression muscles, redistribute the signals instead of weakening the target:

- heavy eye shadow or masks require clearer eyelid aperture, gaze, cheek, mouth, jaw, or posture changes;
- glasses require readable brow silhouette, eyelid tension through the lenses, head/chin relationship, and mouth/jaw support;
- moustaches or beards require the mouth-corner and upper-lip change to move the facial-hair silhouette visibly;
- a stern calm baseline requires anger or disapproval to exceed that baseline rather than merely reproduce it.

## Prompt discipline

Separate invariant language from expression amplitude.

- Keep identity, skull, facial-feature placement, age, costume, camera/view family, lighting, and style locked.
- Do not apply `slight`, `subtle`, `faint`, `tiny`, or `restrained` to every facial signal. These words may describe small body performance deltas, but the face must meet its intensity target.
- State the signature cues positively and require the result to be distinguishable from calm at delivery scale.
- Use the completed neutral master as the default generation image. Keep the approved original portrait as comparison authority. Add a secondary portrait image during generation only when an identity failure justifies it, and state that its neutral expression must not be inherited.
- Never solve weak expression amplitude by changing the camera, view family, identity, costume, or profile composition.

## Required visual gates

### `EXPRESSION_SIGNAL_COMPLETENESS_GATE`

- Every planned signature cue is visibly present in the intended direction.
- `1_micro` has at least two independent facial regions.
- `2_readable` and `3_strong` have at least three independent regions, including at least two facial regions.
- Surface-texture rerendering and lighting noise do not count as cues.

### `CALM_SEPARATION_GATE`

- Compare calm and candidate at matched scale without relying on filenames.
- The candidate must remain distinguishable after both are reduced to delivery thumbnail scale.
- A stern, sad, or guarded calm baseline is treated as the zero point; the candidate must exceed or oppose it according to `contrast_against_calm`.

### `PAIRWISE_EXPRESSION_SEPARABILITY_GATE`

- Review the complete same-character, same-profile set in anonymous randomized order.
- Each non-calm state must be distinguishable from its `forbidden_confusions` and nearest visual neighbor.
- Record every confusion pair. A non-empty confusion list is `FAIL` for `2_readable` and `3_strong`.
- Approved reused assets participate in the review but remain immutable; rework only the failing generated delta unless the user explicitly requests replacement.

### `THUMBNAIL_READABILITY_GATE`

- Inspect the complete asset at the intended dialogue presentation scale, defaulting to `256px` subject height when the game UI size is not available.
- Do not substitute a face-only zoom for this gate. A face crop is supplementary evidence for the muscle signals.
- `2_readable` and `3_strong` must be recognizable from the complete thumbnail. `1_micro` may require the face comparison but must still differ visibly from calm.

## Evidence tool

Run:

```text
python scripts/art_pipeline/ndc_art.py run ndc-generate-expressions prepare_expression_readability_review.py --manifest <expression-job.json> --input-dir <same-profile-delivery-dir> --profile transparent --output-dir <qa-dir>
```

The tool creates:

- an anonymous full-asset thumbnail sheet;
- calm-versus-candidate head comparison rows;
- a schema-1 review JSON containing current asset hashes, planning completeness, anonymous-code mapping, and fail-closed manual fields.

The tool never assigns artistic PASS. Codex/Terra must inspect both sheets, fill the manual review for the exact assets, and set `formal_status=PASS` only when all four gates pass.

If any planning field or required cue count is invalid, the tool still writes diagnostic evidence but exits non-zero with `PLANNING_STATUS: FAIL`. Terra must return to E0 instead of continuing generation or receipt packaging.

Raw pixel-difference percentages, SSIM, and mechanical geometry metrics may locate changes but cannot pass expression readability. Image-model rerendering can change many pixels without producing a different expression.

## Rework routing

When identity, style, viewpoint, geometry, and color remain correct but any readability gate fails:

1. Return only the failing expression to E4.
2. Start again from the unchanged completed neutral master, never from the weak candidate.
3. Preserve every passing invariant and increase only the missing signature cues or target intensity.
4. Remove conflicting low-amplitude wording from the facial instructions; keep body deltas bounded.
5. Regenerate at most within the existing A1/A2/A3 budget.
6. Repeat portrait comparison, readability review, color review, and both profile normalizations for the replacement.

Do not rebuild a passing calm anchor, master, palette package, or shared profile transform merely because expression amplitude failed.
