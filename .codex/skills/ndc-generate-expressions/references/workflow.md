# Expression production state machine

Record one state receipt with `PASS`, `FAIL`, or `NOT_CHECKED`. A later state cannot erase an earlier failure.

## E0_INTAKE_AND_CENSUS

Map each requirement to one user-confirmed portrait, inventory existing approved expressions, normalize aliases, and route each requested state as `REUSE_APPROVED_AS_IS`, `GENERATE_NEW`, `REPLACE_ONLY_BY_USER_REQUEST`, or `BLOCKED_NAME_AMBIGUITY`. For Unit3-or-later requests, inspect the designated Unit1 and Unit2 expression libraries before any generation planning; see `approved-reuse-and-delta-production.md`. Calm routes to `DERIVE_CALM_FROM_APPROVED_PORTRAIT` when no exact profile calm exists. Freeze the complete library and true production delta.

For Unit3, census every file in `D:\PMH\工作\人设\003第三章\头像`; do not infer additional portraits from character-card folders. PMH remains read-only.

## E1_PORTRAIT_SOURCE_LOCK

Verify approval, identity, costume, style, viewpoint, detail budget, source dimensions, protected light regions, and intended crop. Record `PORTRAIT_COMPLETION_USED=false`.

This Skill has no completion or anatomical-repair route. If the portrait is missing, unapproved, identity-ambiguous, or unsuitable for the requested profiles, return `UPSTREAM_PORTRAIT_REQUIRED` and stop that role.

Freeze calm as the approved portrait. Calm is copied unchanged into the non-final pre-Alpha handoff and is never regenerated.

## E2_EXPRESSION_PLANNING

For every state, define expression class, brow/eye/mouth signals, intensity, signature cues, calm contrast, forbidden confusions, thumbnail target, and small permitted performance delta. Generate prompts only for the unresolved non-calm delta. Every retry starts from the approved portrait.

## E3_EXPRESSION_GENERATION

Generate each non-calm expression independently from the same approved portrait on a uniform light-neutral working background. Preserve identity, viewpoint family, costume, body type, lighting topology, palette, style, and stable texture. Never generate transparent or green delivery outputs directly, never generate calm, and never use one expression as another expression's source.

## E4_ARTISTIC_REVIEW_AND_COLOR

Before the pre-Alpha handoff, pass:

- expression meaning, signature cues, calm separation, and target intensity;
- identity, viewpoint, pose limits, costume, and lower-bust structure;
- style lock, texture coherence, source detail, and lighting topology;
- portrait-versus-candidate comparison;
- semantic material color review and non-generative Photoshop correction when needed.

An artistic failure returns to E3. Technical masking cannot repair an artistic failure.

## E5_PRE_ALPHA_HANDOFF

Read `manual-background-handoff-and-return.md`. Copy the artistically accepted calm and every requested non-calm source without background or Alpha processing. Package them under `工作过程文件` with a manifest, current hashes, dimensions, modes, source mapping, and `PRE_ALPHA_HANDOFF` / `NON_FINAL` status. Do not copy this package to `最终交付`.

Stop until the user manually background-processes these exact files in place and confirms completion. Do not create or require a separate return folder.

## E6_USER_RETURNED_RGBA_INGEST

Map every in-place edited file to its exact pre-edit row in the handoff manifest. Verify that the user performed the background processing, the canvas was not rescaled or cropped, and the protected subject content remains intact. Its image hash is expected to differ from the pre-edit hash; the unmodified manifest row, not a second image copy, preserves that provenance. Codex must not use Photoshop, `remove_expression_background.py`, another extraction script, or an Image model to repair Alpha or white fringe.

Run `prepare_alpha_edge_review.py` for review evidence only. Inspect white, mid-gray, dark gray, black, and exact-green previews at native 100% and nearest 200%. A failure returns `USER_ALPHA_REWORK_REQUIRED` and stops; it does not open an internal repair loop.

Freeze one current user-returned native RGBA file and SHA-256 per expression. Any later change to Alpha or RGB invalidates downstream profile evidence.

## E7_DUAL_PROFILE_COMPOSITION

From the same frozen RGBA foreground, compose:

- transparent `1164x916 RGBA/Alpha 0` unless an explicit Unit1 legacy request selects `1152x900`;
- greenscreen `1536x1024 RGB/#00FF2B`.

Each profile uses its own calm transform, guide, geometry, and audit. Require `0 < scale <= 1`, one resample, no protected-pixel clipping, and a cross-profile audit proving the same native RGBA SHA-256.

## E8_PROFILE_AUDIT

For each asset/profile, validate canvas, mode, background/Alpha, guide landmarks, bottom contact, no-upscale/single-resample history, and current hashes. Mechanical PASS never substitutes for the Codex guide or Alpha-edge review.

## E9_SET_CONTINUITY

Audit transparent and greenscreen sets separately. Pass identity, viewpoint, costume, geometry, detail, lighting, texture, expression signal, calm separation, thumbnail readability, and anonymous pairwise separability. Rework only the failing generated state from the approved portrait.

## E10_FORMAL_RECEIPT_AND_RELEASE

Create schema-12 profile receipts. Stage the complete package under `工作过程文件`, enumerate every required `character + expression + profile`, and run `audit_expression_delivery_release.py`. Copy to `最终交付` only after `RELEASE_STATUS: PASS`.
