# Approved-expression reuse and delta production

## Authority

User-confirmed expression files are immutable approved assets. They outrank a new generic prompt, a regenerated lookalike, later cross-character geometry averages, and a newly introduced audit heuristic. Never regenerate, recolor, recompose, rename in place, or silently omit an approved expression merely because it appears again in a later unit's requirements.

Historical approval proves provenance, not current delivery compliance. Preserve the original bytes and SHA-256, but run the complete current-task delivery gates before formal reuse. A legacy file with any current gate `FAIL` or `NOT_CHECKED` cannot enter the formal package. If the active task explicitly requires final delivery under the current standard, route that failed requirement to `REPLACE_REQUIRED_CURRENT_SPEC_FAILURE`; keep the historical file untouched as evidence and produce the replacement in the working directory.

One user-controlled exception exists for old same-character, same-name, previously approved expressions: when the user explicitly says their expression amplitude does not require remake, record `LEGACY_APPROVED_EXPRESSION_AMPLITUDE`. Only `expression_signal`, `calm_separation`, `pairwise_separability`, and `thumbnail_readability` may then use `WAIVED_BY_USER_LEGACY_AMPLITUDE`. Keep the actual review evidence and never rewrite the waiver as `PASS`. Identity, viewpoint, style, profile geometry, bust completeness, detail, lighting, texture, color, background/Alpha, cross-profile version continuity, and every other gate still require current `PASS`. New or replaced assets can never use this waiver.

When an old approved pair must be recomposed or technically repaired for current canvas, Alpha, mode, or exact-green requirements, route it as `NORMALIZED_CURRENT_PAIR`, not byte-identical reuse and not new generation. Preserve and hash each profile's normalization source, bind both rows to one current cross-profile pair-version evidence file and hash, require `normalization_provenance=PASS`, and rerun every current delivery gate. The legacy amplitude waiver remains available only when `legacy_approved_source=true`; all non-amplitude defects still require repair or replacement.

## Mandatory census before generation

At E0, do not limit discovery to the current Unit or to already-known role folders. For every Unit3-or-later expression request, first resolve and inventory the two user-designated read-only historical libraries at their current locations, in this order: `{HISTORICAL_EXPRESSION_U1_ROOT}`, then `{HISTORICAL_EXPRESSION_U2_ROOT}`. Original source identities were `D:\PMH\工作\人设\001第一章\头像\表情` and `D:\PMH\工作\人设\002第二章\Unit2表情`; these paths are provenance only, never cross-machine defaults. Record the selected roots, source provenance and availability. Do this before creating a generation queue or expanding discovery to another archive root; missing libraries must be reported, not silently replaced or treated as empty. If neither library supplies a matching candidate, continue with any other user-authorized historical root as needed. Discovery must match the same character through reviewed role aliases, then match exact expression IDs or explicitly declared semantic aliases, and classify the profile from the path. A same-named expression belonging to another character is reference-only and can never be reused; a merely similar emotion is not a reusable match.

The discovery report is candidate evidence, not reuse approval. For every discovered role/profile directory, build the exact file-level census with `scripts/build_approved_expression_census.py`, review provenance and ambiguity, and freeze the approved source path and SHA-256. Exact names may be routed after this review; aliases or semantically equivalent names require an explicit reviewed mapping and may not be guessed. If discovery finds more than one candidate for the same character/expression/profile, route `BLOCKED_NAME_AMBIGUITY` until the authoritative historical asset is resolved.

Each requirement receives exactly one production action:

- `REUSE_APPROVED_AS_IS`: all requested profile files already exist and are user-confirmed;
- `GENERATE_NEW`: no approved file exists in any requested profile;
- `PARTIAL_PROFILE_GAP`: only some requested profiles exist; stop for a profile-specific decision rather than regenerating all profiles;
- `REPLACE_ONLY_BY_USER_REQUEST`: an approved file exists but the user explicitly requested replacement;
- `BLOCKED_NAME_AMBIGUITY`: multiple files or aliases cannot be resolved safely.
- `REPLACE_REQUIRED_CURRENT_SPEC_FAILURE`: a same-character historical asset exists but fails at least one current delivery gate and the current task authorizes current-standard finalization.

The generation queue contains only non-calm `GENERATE_NEW`, explicit `REPLACE_ONLY_BY_USER_REQUEST`, plus `REPLACE_REQUIRED_CURRENT_SPEC_FAILURE` items authorized by the active final-delivery task. When the user confirms `calm = approved portrait`, missing same-profile calm routes to `DERIVE_CALM_FROM_APPROVED_PORTRAIT`: copy the unchanged portrait into the non-final `PRE_ALPHA_HANDOFF`, wait for the user to manually process that exact file in place and confirm completion, and only then perform profile composition. Codex never removes its background or repairs its Alpha. Calm is never completed, regenerated, or treated as an expression-generation job. A requirement list is not a generation list.

Historical discovery must be completed before an Image 2 call. If a candidate was generated before the archive search finishes, retain it only as working history; it cannot displace a user-approved reusable asset or enter delivery unless the census proves the historical candidate is not reusable.

## Full-library preservation

Maintain three separate lists:

1. complete approved library, including assets not requested by the current unit;
2. current-unit requirements and their reuse mapping;
3. true production delta.

Do not show only the current generated subset as though it were the character's complete library. A merged review index may reference or copy approved existing assets plus new assets, but it must retain provenance and hashes. Out-of-scope approved assets remain listed as preserved and are never deleted.

## Mixed transparent specifications

A character may legitimately have approved transparent assets in both legacy `1152x900` and current `1164x916` sizes. Reuse each approved file as-is. Do not resize the legacy library merely to make the folder uniform.

For a new transparent expression, choose the requested current specification. When that exact specification has at least two approved same-character assets, derive a `character_profile_baseline` from those files. This exact-spec, same-character baseline outranks a calm asset in another size and all cross-character historical ranges. If no same-character exact-spec baseline exists, use the normal calm-anchor route.

## Zack Brennan rule learned from the Unit 3 test

Zack has a unique approved three-quarter view and mixed transparent history. Analyze him independently:

- preserve his original yaw, viewing side, face foreshortening, asymmetric shoulder logic, and off-center balance;
- greenscreen uses the approved Zack greenscreen set and calm file as its role-specific baseline;
- current-size transparent generation uses approved Zack `1164x916` assets as the baseline set rather than a front-facing cross-character average or a `1152x900` calm file;
- existing Zack expressions are reused exactly; only missing expression/profile deltas enter generation;
- no generic front-view center or face-proportion target may override this baseline.
