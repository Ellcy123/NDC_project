# Whole-subject color diagnostics (not a formal correction route)

Image-generation candidates may preserve identity and drawing structure while drifting in luminance, saturation, or hue. Prompt wording and another generative edit cannot prove restoration. The legacy whole-subject CIELAB tool in this file may quantify broad drift, but it is no longer permitted to produce formally corrected expression assets because changed shoulder/garment area can distort aggregate statistics. Formal work uses [semantic-palette-and-photoshop-color.md](semantic-palette-and-photoshop-color.md).

## What is frozen

For each character, freeze exactly one color anchor from the user-approved portrait before expression generation continues:

- absolute approved-portrait path and SHA-256;
- source dimensions, mode, embedded ICC presence, and sRGB-normalization decision;
- the Codex-reviewed E2 subject-mask path;
- foreground-only CIELAB D65 statistics;
- 101-point percentile curves and 256-bin histograms for `L`, `a`, and `b`;
- chroma distribution and circular mean hue for chromatic pixels;
- protected-black, protected-neutral, protected-white, and alpha rules.

This anchor is diagnostic evidence only. It does not replace the semantic material palette card and does not authorize an `apply` output for delivery.

## Mask gate

Formal anchor capture always requires an explicit Codex-reviewed subject mask from the approved portrait or accepted candidate. Do not trust embedded Alpha merely because it exists. Reject a mask that includes detached fragments, baked background, extraction debris, or unrelated pixels.

The source mask must sample only approved subject pixels. It must retain representative skin, hair, costume, linework, and approved pale design. Record any excluded region.

For an expression candidate, use its reviewed foreground Alpha or a reviewed mask. Never infer the subject from color similarity during calibration. Background pixels, exact green, and Alpha 0 pixels are neither sampled nor recolored.

## Diagnostic timing and source discipline

1. Capture the character color anchor after the E2 mask is approved and before further expression generation.
2. Complete and artistically pass the current character's full native expression set.
3. Use whole-subject statistics only to flag likely broad drift and to help prioritize semantic material review.
4. Never promote the legacy `apply` result to formal output.
5. Never compare from another expression, a previous corrected result, the calm delivery asset, or another character as a global target.
6. Split only semantic-color-passing native candidates into independent `transparent` and `greenscreen` normalization branches.

This ordering makes both delivery profiles inherit the same corrected interior pixels without merging their canvas, geometry, background, or audit rules.

## Legacy deterministic method

`scripts/calibrate_expression_color.py` remains available for diagnostic capture and historical audit reproduction. Its correction output is candidate evidence only.

The script:

- normalizes embedded ICC input to sRGB when present and otherwise records the sRGB assumption;
- converts masked subject pixels to CIELAB D65;
- detects weak global channel drift using percentile-distribution distance;
- applies a bounded robust affine correction only to channels outside the deadband;
- caps change to `8 L*` and `6 a*/b*` by default;
- leaves spot black unchanged, preserves neutral-white design, and prevents hue injection into neutral grays;
- keeps Alpha byte-for-byte unchanged;
- produces a JSON audit with before/after distributions, improvement, hashes, parameters, and explicit `NOT_CHECKED` visual/formal states.

The script cannot understand semantic materials. A larger dark jacket, completed shoulders, or changed shirt visibility may move the whole-subject histogram while the face is unchanged, or may hide a visibly wrong face behind an improved global score. Use reviewed semantic masks and Photoshop for correction.

## Commands

Capture once per approved character portrait:

```text
python scripts/calibrate_expression_color.py capture --reference <approved-portrait.png> --mask <E2-reviewed-source-mask.png> --output <character-color-anchor.json>
```

Legacy diagnostic apply, never formal delivery:

```text
python scripts/calibrate_expression_color.py apply --anchor <character-color-anchor.json> --input <expression-native-rgba.png> --output <expression-color-calibrated.png> --audit <expression-color-audit.json>
```

Do not overwrite the raw artistic candidate. Legacy decisions remain diagnostic and cannot set formal color `PASS`.

## Diagnostic review limits

Even a mechanical improvement may be visually wrong. Compare raw and diagnostic output only to identify which semantic materials need review. Formal pass criteria live in the semantic palette/Photoshop reference.

- skin is not gray, red, yellow, or overbright relative to the portrait;
- hair and costume retain their approved hue family, saturation restraint, and value hierarchy;
- spot-black masses and ink contours remain black rather than lifted or tinted;
- approved white/near-white clothing, eye whites, jewelry, and highlights remain neutral and structurally intact;
- the requested expression has not been weakened by shadow/highlight compression;
- no clipping, posterization, hue inversion, or new edge halo is visible;
- the whole role set is mutually consistent.

Do not set formal color status from this report.

Historical improvement thresholds remain useful only for comparing old audit runs; they do not determine current acceptance.

## Failure routing

- Dirty or incomplete source mask: return to E2 and repair/review the mask; do not change color thresholds.
- Mechanical regression or required correction beyond caps: keep the raw candidate, mark `FAIL`, and inspect whether the drift is local or the identity/rendering already failed E5.
- Any visible material drift: use the semantic palette and reviewed Photoshop mask route; do not globally strengthen the transform.
- Black/white protection failure, clipping, or expression readability loss: discard the calibrated output and retry from the raw artistic pass with narrower parameters.
- Many candidates drift the same way: retain the semantic palette package, diagnose the shared generation cause, then correct only the affected material/tone bands from each raw candidate.
- Color cannot be restored without repainting structure: return to E4. Calibration cannot excuse identity, style, lighting, or rendering failure.
