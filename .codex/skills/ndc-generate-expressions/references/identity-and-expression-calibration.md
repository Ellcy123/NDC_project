# Identity and expression calibration

Apply to new or user-requested replacement expressions. Keep approved expressions outside the production delta unchanged; review current technical requirements through the reuse workflow.

## Plan against the actual calm

Inspect the approved portrait before assigning signals. Record which cues already exist in calm: knitted brows, narrow eyes, compressed lips, downturned corners, or a lowered gaze. Repeating those cues is not a new expression.

Describe the intended change as an observable difference from this baseline. For near-neutral narrative states, specify complementary eye and mouth/brow changes when a single subtle cue would be ambiguous. Do not impose the same two-cue formula or a universal amplitude on every emotion. Keep the role's approved age, temperament and requested intensity.

Separate movable performance from fixed identity:

- Fixed: face length/width, forehead and hairline, eye spacing and orbital shape, nasal bridge/tip/nostril proportions, nose-to-mouth distance, mouth location/width, jaw corners and chin shape.
- Movable within the requirement: brow tension, eyelids, iris direction, lip compression and explicitly allowed small head/neck performance.

For gaze, specify the target relative to the viewer and the character's eye height (for example, viewer-right and below the eyes). Sideways, upward and downward glances are different signals. A gaze change does not authorize head rotation or a change of camera.

When an RGBA viewer exposes hidden RGB outside Alpha, inspect the source composited on a neutral background before diagnosing image corruption. A deterministic display composite or face crop of the same approved source may be supplied as supporting identity evidence; record its derivation. It does not replace the portrait authority, create a new calm, remove a background, or justify editing Alpha. Do not feed an old expression back into generation.

## Review the picture before its label

1. Compare the approved portrait and current candidate at matched display scale with original framing visible. Use the existing portrait comparison helper for the overview. If face geometry is unclear, inspect corresponding face regions at comparable displayed scale as well as native tiles; do not hide a pose or outline change with independently convenient crops.
2. Check fixed facial geometry first. Matching hairstyle, costume, age category, or drawing style is insufficient to establish the same person. Record concrete observations for face proportion, eyes, nose, nose-mouth spacing, and jaw/chin rather than a single generic identity PASS.
3. Compare performance against calm and the accepted same-character expressions at the job's thumbnail target. Judge the visible image before reading its filename or prompt. Do not call an eye/mouth change readable only because it becomes detectable on a large close-up.
4. Check the actual gaze direction, lip state, and permitted head motion independently. A recognizable person looking in the wrong direction can still fail the expression requirement.
5. Finish costume, anatomy, palette, lighting, style, texture and native-detail checks. Record actual whole/native-tile inspection and bind the result to the current output hash.

Review-only resizing does not authorize resampling or altering the native production asset. A technical validator proves record structure/hash binding, not that these visual judgments are correct. Measurements may identify drift but must not manufacture an artistic PASS or claim pixel identity for a generated image.

If an applicable requirement remains uncertain, record the failed or unresolved criterion and retain the file as a candidate. A3 is a retry ceiling, not a reason to accept the closest result.

## Targeted retry and user rejection

For each retry, preserve the failed file and record: observed defect, failed criterion, intended prompt change, unchanged constraints, and the next image's actual result. Start from the approved portrait every time. Strengthen the missing signal without silently broadening head motion, changing identity, or lowering intensity.

A user rejection supersedes earlier Codex PASS for that exact asset. Record `USER_REJECTED` with the rejected file/hash, reason, and invalidated downstream uses. Keep prior records as history; they cannot authorize current handoff, Alpha, profile or release. Preserve user-accepted siblings and regenerate only the rejected delta. A new explicit rework request may start a fresh bounded A1/A2/A3 attempt; do not reset the counter automatically after a failure.

After a replacement passes artistic review, preserve the former handoff bytes and pre-edit manifest. Check that the live file has not received an intervening user edit before replacing it. Publish a versioned manifest and an explicit pointer to the current revision; record which rows supersede rejected hashes. Resolve user-returned files against this current revision, not the oldest filename match. Keep user-returned RGBA and frozen pre-Alpha candidates separate in provenance so an image hash change caused by manual processing is not mistaken for rejection or regeneration.
