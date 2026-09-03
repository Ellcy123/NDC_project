---
name: ndc-generate-characters
description: Generate, plan, route, audit, and critique NDC stylized characters through either the full Midjourney workflow for important new characters or the ChatGPT Image 2 fast path for minor new characters and existing-character state variants. Use when the user mentions NDC or 摩登迷城 character design, asks for role or character prompts, wants MJ candidate review or refinement routing, needs a new full-body or narrative state based on an existing character card, or needs NDC character cards, conditional portraits, or animation-only black-white-red assets. Route profile-controlled bust-expression libraries to the separate ndc-generate-expressions skill.
---

# NDC Generate Characters

## Operating mode

Treat this skill as a standalone character-production skill. Do not merge its rules into a scene skill.

## Mandatory stage-end visual self-check gate

Every art-production stage executed by this Skill must end with an actual visual self-check before its output may be accepted, passed to a later formal stage, packaged, or released. This includes reference/selection acceptance, MJ candidate and refinement stages, identity lock, general-style conversion, card/portrait/black-white-red generation, constrained edits, module acceptance, composition, normalization, derivation, and final packaging. Inspect the current whole image at `100%` and every applicable local region at nearest-neighbor `200%` or through complete original-pixel tiles. Compare against the current identity/style authority and every applicable brief, anatomy, view, design, expression, structure, layout, palette, texture, edge, Alpha, and runtime-readability requirement.

Write one current `ndc-stage-visual-self-check/v1` JSON record per executed stage. It must bind the stage ID, reviewer/date, input and output paths plus SHA-256, the inspected `whole_100` and `local_200_or_tiles` views, every applicable criterion with an explicit finding and `PASS`/`FAIL`/`NOT_CHECKED`, the overall `visual_check_status`, and the responsible rework stage when blocked. Missing record, missing visual-detection item, stale output hash, missing required view, `FAIL`, or `NOT_CHECKED` is `STAGE_VISUAL_SELF_CHECK_GATE: BLOCKED`: do not advance the production state, use the output downstream, or call it formal. Technical validators, dimensions, hashes, prompt locks, or absence of a detected error cannot write visual `PASS`.

After a block, return to the earliest responsible stage, perform the missing inspection and required repair/regeneration, then repeat the visual self-check on the new current output. Release only after the current hash has a passing record. For every file-producing stage, run `python D:/Codex/NDC/scripts/validate-ndc-stage-visual-self-check.py --record <visual-review.json> --artifact <current-output>`; a nonzero result is a hard stop. Existing route-specific retry ceilings still apply, and exhausting one leaves a candidate rather than weakening this gate.

Treat user-supplied prompt text and the user's explicit image selection as the highest artistic authority. A user prompt remains active until the user explicitly retires or replaces it. Do not rewrite it to force an inferred personality expression, story prop, or other brief-derived visual cue. When a locked downstream prompt requires a neutral or expressionless character, that neutral result is correct even when the prose brief describes the character as kind-looking, cheerful, threatening, or otherwise expressive.

An explicit user selection freezes that artistic candidate and ends the artistic search loop for the selected asset. Continue only with required non-generative technical normalization, packaging, and evidence recording unless the user explicitly requests an artistic change. Do not reopen Midjourney identity design merely because a selected downstream card or portrait omits a temporary expression or a deferrable story prop. Read `references/cases/alley-killer-2026-08-28.md` when diagnosing this specific overcorrection pattern.

Default to preparing copy-ready prompts, reference order, parameter constraints, review decisions, and refinement checklists for the user to execute manually. Do not call image-generation or image-editing tools merely because the task concerns NDC characters. Only execute images in Codex when the user explicitly asks for Codex execution, batch processing, automatic file management, or engineering integration.

Read `references/character-rules.md` before planning or judging any character task. Read `references/prompt-library.md` when producing prompts. Read `references/evidence-and-gaps.md` when deriving a new preference, evaluating a borderline case, or explaining the confidence of a recommendation.

Read `references/style-self-check.md` before judging or delivering generated assets. Its file paths and hard gates are mandatory for NDC output QA. Read `references/modular-character-card.md` only when the user explicitly requests a 4K character card or when the user explicitly requests assembly from separately generated views.

<!-- NDC_TEXTURE_COHERENCE_MODULE:BEGIN -->
Read the style-locked texture-control section in `references/prompt-library.md` before writing any non-immutable character prompt, and apply the separate `STYLE_LOCK_GATE` plus `TEXTURE_COHERENCE_GATE` in `references/style-self-check.md` to every generated character image. Texture control may reduce only non-semantic micro-detail and broken frequency distribution; it may not change identity, approved style references, palette/value compression, line hierarchy, grouped shadows, edge behavior, brush language, material treatment, costume construction, or approved identity-bearing detail.

The default one-pass character-card prompt and portrait prompt remain byte-for-byte immutable. Do not append the texture module, negative wording, or any other text to those two submissions. Control their failure through post-generation gates and restart from the approved source/reference chain. A preventive prompt revision requires a separately approved locked version and new hash evidence.
<!-- NDC_TEXTURE_COHERENCE_MODULE:END -->

Read `references/execution-gates.md` before any Codex-executed generation, edit, assembly, formal audit, or delivery. It defines the mandatory reference manifest, stage receipts, evidence fields, and the distinction between an exploratory candidate chain and a fail-closed formal delivery. These rules apply regardless of the reasoning model. A model may not replace a missing measurement or comparison with an unsupported statement that an asset "looks acceptable."

Read `references/post-generation-normalization.md` before producing or technically finishing any portrait or character card. Portrait generation and the default non-4K character-card branch use immutable master prompts. Artistic generation is approved before background removal, proportional scaling, placement, or edge cleanup; non-portrait structural completion, when required, also occurs only after that approval. Portraits never add a missing-shoulder completion stage. Only an explicit user request for `4K` activates the modular 3840×2160 character-card route.

Read `references/style-analysis-protocol.md` whenever the task asks for style analysis, style self-check, comparison with style references, or formal style approval. A complete-image review is only the first pass. Use `scripts/make_style_review_tiles.py` to cover every source pixel with overlapping original-resolution tiles, inspect every tile for line, brush, texture, edge, material, and micro-detail behavior, then return those observations to the whole image. Do not call a 4K/8K reference fully analyzed from its downscaled overview alone. A formal style pass requires both `whole_image_checked: true` and `local_tile_coverage_complete: true`.

Use the bundled files in `assets/` in the exact roles stated below. Do not substitute visually similar references without user approval.

## Formal delivery and exploratory candidate rule

For every formal asset, use only `PASS`, `FAIL`, or `NOT_CHECKED` for each required gate. `NOT_CHECKED` is not a pass. Any upstream `FAIL` or `NOT_CHECKED` blocks formal assembly and formal delivery.

### Non-skippable production state and recovery guardrail

For every important-new-character formal branch, maintain one explicit current state. Use only the following forward order, and record the state in the active stage receipt before invoking the next artistic tool:

`BRIEF_LOCKED -> MJ_CANDIDATE -> USER_SELECTED -> [REPAIR_CANDIDATE ->] IDENTITY_LOCKED -> GENERAL_STYLE_CANDIDATE -> GENERAL_STYLE_LOCKED -> CARD_CANDIDATE -> CARD_ART_PASS -> PORTRAIT_CANDIDATE -> PORTRAIT_ART_PASS -> TECHNICAL_PASS -> FORMAL_PASS`

The portrait branch may replace `PORTRAIT_CANDIDATE -> PORTRAIT_ART_PASS` with `PORTRAIT_SKIPPED` only when the selected route does not require a portrait. A failed MJ search uses the separate mandatory edge `MJ_CANDIDATE -> FALLBACK_SELECTED -> REPAIR_CANDIDATE -> IDENTITY_LOCKED`; it may not jump directly from `FALLBACK_SELECTED` to `IDENTITY_LOCKED`. Minor-character and existing-state fast paths must record their own route-specific source/candidate states, but the same no-skip, failure, prompt-lock, and formal-language rules below still apply.

- `USER_SELECTED` freezes the exact user-selected pixels as the artistic authority, but it does not automatically prove technical or formal delivery gates. Skip the optional `REPAIR_CANDIDATE` state only when no artistic repair is requested or required.
- `FALLBACK_SELECTED` is never an identity lock. It may move only into `REPAIR_CANDIDATE` and must independently pass every identity-lock gate afterward.
- A generation result starts as `*_CANDIDATE`, even when its prompt, tool metadata, filename, or user request contains the words “formal”, “final”, or “delivery”. File existence and visual plausibility never advance the state by themselves.
- A failed or `NOT_CHECKED` state has no forward edge. Return to the earliest responsible stage, preserve the failed evidence, and do not start downstream art as if the upstream source had passed.
- Before every image-generation or image-editing call, write a one-line checkpoint containing `current_state`, `source_authority`, `allowed_next_state`, `prompt_lock_status`, and `upstream_blockers`. If `prompt_lock_status` is required and is not `PASS`, or any `upstream_blockers` remain, the call is forbidden except for an explicitly labeled exploratory candidate chain.

Browser, connector, page, login-session, download, or inspection failure is an execution failure, not permission to change the production route. Recover the same page/job, use a user-supplied download of that exact candidate with recorded provenance, or stop at `NOT_CHECKED`. Do not replace an important-character MJ identity stage with a fresh Image 2 design merely to keep work moving. A tool substitution is allowed only when this skill already defines that route for the character class, or the user explicitly authorizes the route change after being told what identity/style authority would change.

When the user explicitly selects an image, immediately save or update the reference manifest and selection receipt before any further artistic call. Record the selected file path, originating job/candidate when known, user-selection evidence, hash, dimensions, and frozen identity/costume/palette/style invariants. Do not generate an alternative identity after that point unless the user explicitly rejects or replaces the selection.

Treat every “change only X” request as a constrained-edit branch:

1. Freeze the selected source and define an explicit edit region or mask before generation.
2. The model output is only an `EDIT_CANDIDATE`; never use the whole regenerated frame directly as the new identity lock.
3. Composite the edited region onto the frozen source while restoring the original source pixels outside the approved mask. If the available tool cannot provide a trustworthy mask or deterministic outside-mask preservation, stop with `NOT_CHECKED` or deliver a clearly labeled candidate for user review.
4. Verify pixel identity outside the mask when deterministic comparison is possible, and always perform a whole-image visual comparison for face, body, pose, garment construction, palette, accessories, shoes, lighting, background, crop, and canvas.
5. Any unrequested drift returns to the constrained-edit stage. Do not describe the result as “only X changed” without this evidence.

For the immutable default character-card and portrait prompts, the prompt-lock check is a hard pre-call gate rather than retrospective documentation. Export and verify the snapshot with `scripts/verify_locked_prompt.py`, save `PROMPT_LOCK_PASS` plus its SHA-256 in the stage receipt, and submit exactly that snapshot with the required reference order. Never make a freeform card or portrait first and attempt to validate or replace its prompt afterward.

After an image returns, describe it only as a candidate pending review. The terms `正式`, `最终`, `交付图`, `approved`, `accepted`, `FORMAL_PASS`, or equivalent may be used only after the asset's applicable artistic, identity, structure, style, texture, technical, provenance, delivery-receipt, and texture-record gates all pass. If the user asks whether a shown candidate is the delivery image, answer from the recorded state and gate evidence rather than from the image's general appearance.

When the user explicitly requests a complete workflow, exploratory set, or downstream candidate despite an upstream failure, continue only as an exploratory candidate chain. Preserve the actual failed result and the failure evidence; label every downstream file and receipt `CANDIDATE_ONLY`; record all `upstream_blockers`; and never describe a candidate as approved, accepted, or formally delivered. A failed or unreviewed source may be used only as a declared candidate-identity source for that exploratory chain, never as a formal `identity_source` or an approval source. Formal assets must resume from an approved same-character source.

For important-character Midjourney candidate selection, use the mandatory `123` principle in `references/character-rules.md`: a fixed prompt version is one group; Batch 1 is its initial four-image grid, Batch 2 is one `Vary Subtle` grid from the nearest Batch-1 candidate when Batch 1 has no pass, and Batch 3 is one `Vary Strong` grid from the nearest candidate across Batches 1–2 when Batch 2 has no pass. Revise the prompt from Batch-1 evidence only after Batch 3 has no pass, then start the next group. Run at most three groups. After the third group, select the closest candidate across all generated images as `FALLBACK_SELECTED`, record its defects, and move it only into a declared repair/candidate chain. It is not an identity lock or formal asset until a later refined result independently passes its gates. This replacement applies only to MJ candidate selection; technical-normalization retry safeguards remain unchanged.

Before generation, print or save the exact reference-role manifest required by `references/execution-gates.md`. Identity sources, style-only sources, landed peer comparisons, and rejected examples must be separate lists. A source may not silently change roles. In particular, a peer portrait may prove portrait style but never another character's identity, and a rejected image may demonstrate a defect but may not become an approved identity source.

Every formal pass must include evidence, not only a conclusion:

- actual pixel dimensions and ratio;
- source provenance and any crop or scale factor;
- subject bounding boxes or placement measurements required by that asset type;
- exact comparison paths and the role of each comparison;
- whole-image review status;
- original-pixel local-coverage status for style review;
- unresolved differences and the stage to which a failure returns.
- separate `STYLE_LOCK_GATE` and `TEXTURE_COHERENCE_GATE` statuses plus a validated `ndc-texture-coherence/v1` record for the formal candidate.

If the evidence cannot be obtained, stop with `NOT_CHECKED` and report the missing evidence. Never lower the delivery standard to keep the workflow moving.

## Required inputs

Obtain or identify:

1. The character brief or existing character image.
2. The requested stage: full body, optional head, MJ refinement, general-style full body, character card, conditional portrait, animation-only black-white-red card, or full workflow.
3. Role-specific visible constraints: age, gender, ethnicity when specified, profession, class, hairstyle, upper garment, lower garment, shoes, and required accessories. Separately label each expression, mood cue, and portable story prop as `HARD_NOW` only when the active user prompt or an explicit user instruction requires it in the current stage; otherwise label it `DEFER_TO_IMAGE2` or `DOWNSTREAM_STATE_ONLY`. Do not automatically translate personality prose into a mandatory facial expression.
4. The production route: important new character, minor new character, or state variant of an existing character.
5. For an existing-character state variant, the current approved general-style character card. Do not proceed from text alone when that card exists.

If the brief lacks a material identity or costume decision, retain a visible placeholder such as `【角色描述】` instead of inventing plot facts.

## Workflow

### 0. Choose the production route

- Use the full Midjourney workflow for important new characters that need a reusable design master.
- For a minor new character, skip Midjourney and generate directly with ChatGPT Image 2. Use `assets/general-fullbody-style-reference.png` as the style reference and reuse the same general-style wording used by the full-body conversion and character-card stages. Its standard deliverable is the general-style character card only; do not generate a portrait merely to complete a set.
- For an additional state of an existing character, skip Midjourney and use the current approved general-style character card as the primary identity and design reference. Generate the requested state from that card; do not recreate the character from text.
- Route by narrative importance, reuse frequency, identity risk, and production cost. Do not force the full workflow merely because the request concerns a character.
- The black-white-red card is not part of the standard workflow. Trigger it only when the user or project requirement explicitly says that the character is entering animation production.

### 1. Convert the brief into visual design

Extract only visible design conclusions. Separate face, hair, upper garment, lower garment, shoes, accessories, body type, posture, and period/profession cues. Do not turn abstract personality words directly into unsupported costume elements or a mandatory expression. Preserve the user's prompt wording verbatim and maintain a separate deferral list for expressions and portable story props that may be repaired later with Image 2.

### 2. Prepare the Midjourney full-body generation

Use the current Midjourney default model. Never add `--v`, `--V 8.1`, or another model-version flag.

Open or reuse the Alpha Imagine page at `https://alpha.midjourney.com/imagine`. Do not identify the Alpha site from the upper-left logo or a screenshot and do not substitute the non-Alpha `www.midjourney.com` page.

The two core MJ style references are already saved in the Midjourney account. Click `Images` in the upper-right of the Imagine page, select the matching two saved images from the panel below, and assign both to `Use style`. Do not upload the local copies during normal operation. Use the bundled assets only to visually identify the correct saved images:

- `assets/mj-style-reference-1.png`
- `assets/mj-style-reference-2.jpg`

Use 1:2. Require a complete head-to-toe character, natural standing pose, shoulder-height/eye-level camera, and a minimal pure-white background. Keep both reference files and the aspect ratio fixed while changing the character-description variable.

### 2.1 Apply the MJ `123` candidate-selection loop

Apply the same loop to the full-body grid and to every optional MJ head-material grid. A pass means the current stage's applicable hard gates are met, not merely that an image is the least flawed. Expression and portable story props are excluded from MJ hard gates unless the active user prompt or an explicit instruction marks them `HARD_NOW`. Do not revise the prompt before completing the current group's `Subtle` then `Strong` route. At every decision, save the group number, batch number, job URL/ID, selected source candidate, variation action, review result, and—when starting a new group—the exact prompt delta derived from its Batch-1 evidence. The detailed sequence, maximum budget, and `FALLBACK_SELECTED` handling are defined in `references/character-rules.md` and the stage-receipt requirements in `references/execution-gates.md`.

### 3. Apply the head-quality gate

After selecting a viable full body, inspect the head at useful zoom.

- Treat facial legibility as a hard gate, not a preference. Both eyes, the brow/eye spacing, the nose bridge and tip, the mouth or mustache shape, the jaw/cheek contour, and the hairline must be simultaneously readable at useful zoom. Dramatic chiaroscuro is allowed only when it sculpts these landmarks rather than erasing them.
- If the head is clear, structurally reasonable, identity-distinctive, and fits the role description, skip separate head generation.
- If the head is too small, blurred, malformed, cropped, generic, insufficiently descriptive, or has a large shadow mass that hides an eye or other identity landmarks, do not pass the gate. Generate separate head material with the same two MJ style references and 9:16, or explicitly route the face through local repair before identity lock.

Do not require the separate head to look like the face in the full-body image. Midjourney text generation cannot reliably reproduce the same person. Judge the head by role-description fit, structural quality, hairstyle silhouette, age, period, and usability as refinement material. Do not fail it for lacking an inferred smile, menace, kindness, or other temporary expression unless that expression is explicitly required in the current MJ prompt.

Never confuse the MJ head material with the later general-style portrait deliverable.

### 4. Plan MJ-stage refinement and lock identity

Use the full-body image as the source of body type, pose, outfit layers, shoes, accessories, color scheme, and silhouette. When a separate head is stronger, use it as a replacement or redraw reference without demanding raw-image facial consistency.

Route defects explicitly:

- Regenerate full body for major body, pose, costume, role, or style failure.
- Generate or regenerate head material for an otherwise good full body with an unusable head.
- Refine locally for background debris, fake text/signatures, unwanted objects, silhouette joins, hands, feet, shoes, clothing borders, and excessive fragmented details.
- Treat local repeated marks, broken texture continuity, or isolated decorative micro-detail as a bounded repair from the frozen approved source. Treat whole-image micro-detail inflation as a regeneration from the original stage authority; never chain from the failed candidate or use sharpening, texture overlays, AI upscaling, or repeated resizing as a texture fix.
- Defer a missing portable story prop or non-identity expression to Image 2 unless the active user prompt explicitly makes it a current-stage hard requirement. Their absence alone must not restart MJ concept generation.
- Treat a hand hidden behind the back as a pose defect. Prefer an otherwise comparable candidate with both arms and hands visible. Accept the hidden-hand candidate only when its body type, head-to-body proportion, face, or role fit is materially stronger; in that case, repair the pose with Image 2 before producing the character card.
- Accept directly when the full body and head are already clear and usable.

Do not declare identity lock while the face is still ambiguous. If the raw full-body face fails the legibility gate, combine the chosen body with approved head material or locally repair/re-light the face until the resulting MJ-stage refined full body has a readable, distinctive face.

Treat that refined full body as the first identity lock. Preserve an identity-anchor crop of its final face when the full-body scale is too small for reliable comparison. The crop must come from the same locked image or the exact face composited into it; an unrelated raw MJ head is not a valid downstream identity anchor. Downstream identity consistency begins here, not between the two raw MJ generations.

### 5. Produce downstream assets

Use `assets/general-fullbody-style-reference.png` only as the target style reference when converting the locked MJ-stage full body. Reference order for identity-sensitive conversion is: locked MJ full body first, its same-source face identity-anchor crop second when needed, and the general full-body style reference last. Explicitly treat the first two as identity/design sources and the last as style-only.

The conversion must preserve person-specific facial geometry, not merely demographic labels. Compare face shape and forehead, eye/brow spacing, nose silhouette, mouth/mustache shape, jaw/cheek contour, ears, hairline, and asymmetries between the MJ identity lock and the converted full body. If the conversion invents a cleaner or more generic face, changes apparent age, or retains only broad traits such as “older man with side-parted hair and mustache,” reject it and return to the conversion stage.

Before creating the character card, make sure the locked general-style full body shows both arms naturally lowered and both hands completely visible. A hand may not remain behind the back or hidden by the torso. Preserve the selected character's body type, head-to-body ratio, face, clothing, accessories, and palette while correcting only the arm/hand pose.

Then produce only the assets required by the selected route:

1. General-style character card, 16:9, for every role that needs an independent character asset.
2. General-style portrait, 4:5, only for important, recurring, UI-present, or explicit close-up roles. Minor roles do not receive a portrait by default. Use `assets/general-portrait-style-reference.png` only as the portrait style reference.
3. Black-white-red character card, 16:9, only for an explicitly animation-bound role. Use `assets/black-white-red-style-reference.jpg` only as the target style reference. Preserve the rules below for that conditional branch even though it is excluded from standard production.

Separate artistic generation from technical normalization. First judge the native candidate's identity, design, required views, anatomy, and target style. If those pass, freeze the approved pixels and repair delivery-only properties through the ordered operations in `references/post-generation-normalization.md`: background removal when required, proportional scaling and placement, then exact-canvas and edge checks. Tightly bounded canvas extension or missing-edge completion remains available only for non-portrait assets whose required structure would otherwise be incomplete. A native candidate with the wrong delivery dimensions or ratio is not automatically an artistic failure; the normalized final file must meet the exact ratio, dimensions, bounding-box caps, and background requirement before delivery.

For expression review, follow the active asset prompt rather than the prose character brief. The locked general character-card and portrait prompts require neutral/expressionless presentation; a missing benevolent smile is therefore not a card or portrait failure. A smile in an earlier concept image does not need to persist downstream. Likewise, a story prop omitted from the MJ concept image is a recorded Image 2 repair item, not an MJ candidate rejection, unless the user explicitly says that the prop is identity-defining and non-deferrable.

For a general-style character card without an explicit `4K` request, use the locked one-pass character-card prompt in `references/prompt-library.md` as the default production route. Submit that prompt verbatim with the recorded reference order; do not paraphrase, expand, translate, add negative prompts, or inject delivery-size instructions. Preserve the native artistic result, then normalize delivery-only properties after the identity and style pass.

Only when the user explicitly requests `4K` for the character card, use the modular workflow in `references/modular-character-card.md`: generate and approve each required view as an independent high-resolution image, preserve every approved module, then use `scripts/compose_character_card.py` for deterministic assembly on an exact 3840×2160 white canvas. Do not ask an image model to redraw approved modules during final assembly. Record the explicit 4K trigger in the stage receipt; absence of that trigger forbids automatic routing to modular generation.

Require three complete and consistently scaled full-body modules: front, strict left side, and back. Normalize their trimmed subjects to one shared height so head tops and heel baselines match exactly, then visually verify shoulder, waist, knee, and coat/garment construction lines. Do not preserve unequal source-pixel sizes or bottom-align them with an unused blank strip above. Each approved full-body module must also retain enough native head detail to verify that view's facial geometry, hair mass, hairline and ears; preserve a same-pixel head crop as the downstream identity anchor before generating a separate head view. A head panel may directly use that unscaled approved crop when it is natively detailed enough, or use it as the locked input for a clarity-only supplement. A supplement must not redesign identity, hair, age, costume or view; record its provenance and reject it if those invariants drift. Every full-body view is a prop-free design reference: both hands must be empty and naturally lowered, and no portable prop may touch, overlap, hang from, or be carried by any character body. Require three neutral head views: front, strict right side, and back, each sourced through that approved full-body head-anchor route. Require one worn-shoe close-up showing the character's lower trouser legs, ankles, and both feet wearing the approved shoes, plus zero to three approved, identity-relevant accessory, portable-prop, or construction details. Reject missing required angles, inconsistent module identity or design, misaligned view scale, unexplained layout voids, meaningless fabric crops used as filler, any non-empty hand, any prop attached to or overlapping a full-body view, or any head supplement that changes the approved full-body identity.

Treat clothing-fold language, edge hierarchy, material response, and ink rhythm as formal delivery gates, not optional polish. NDC general-style garments use a small number of decisive angular fold wedges at load points, hard structural turns, broad quiet dark masses, and short controlled tonal bridges inside larger planes. Reject long continuously blended or airbrushed cloth, rounded melted folds, decorative micro-wrinkles, or generic glossy 3D shading. Ink weight is selective rather than uniformly heavy: focal silhouette turns, occlusions, and load-bearing corners may be bold; long garment edges are medium or fine and tapered; internal folds may be finer, broken, or carried by adjacent value blocks. Require visible swell, taper, breaks, and decisive endings, but do not force every edge to the same comic-outline weight. Hair remains grouped into large directional masses with a few broad ribbon-like marks and no individual-strand rendering. Treat finish by material: cloth and most skin planes stay matte, while approved polished leather, metal, jewelry, and badges may use compact sharp highlights. When the user supplies a hue-adjusted approved composite, treat it as the color authority: style repair may change fold edges and ink treatment only, while preserving its hue, palette, identity, design, and all already approved modules.

For an explicitly triggered black-white-red card, keep black, white, and red unmistakably dominant. Do not restore normal or general-style skin color. Skin may carry only a barely perceptible near-grayscale warm gray-brown or muted sepia bias, substantially less saturated than the general-style card. Use that faint hue only within skin planes while retaining the graphic black-white structure. Avoid both extremes: broad pure-white skin highlights and visibly brown/orange natural skin.

Keep red as a small, spatially purposeful signal accent: favor an asymmetric shadow-side rim, local separation light, or an identity-bearing tie, emblem, eye, or accessory. Reject an automatic full red outline around every edge, large red background blocks, red page borders, broad red floor shapes, or large red garment panels unless the approved source character explicitly requires them or the user explicitly selects the minimalist poster branch. Preserve low-contrast internal facets inside near-black garments instead of flattening them into featureless silhouettes.

Use the general-style character card as the identity source for the portrait and black-white-red card. Do not use the raw MJ head as the official portrait identity source.

For portraits, treat the portrait-style reference as style-only. The portrait branch may use faceted values and short directional dry-brush marks to carry form, so an extremely heavy outer contour is not a universal pass condition. Keep hard structural turns and controlled short tonal bridges, reject smooth airbrushing, and reject horizontal extension bands, duplicated background strips, or cutout seams as generation artifacts. If the reference subject changes the character's sex, age, face, hairstyle, or costume identity, reject that result immediately and retry with the approved character card as the only image reference while reproducing the portrait style in text.

A formal portrait must begin with a newly rendered portrait candidate made from the locked portrait prompt. A crop or enlargement of a character-card panel cannot replace that artistic generation. After the newly rendered candidate passes identity and portrait-style review, background removal, proportional scaling, canvas placement, and non-generative edge cleanup are permitted technical-normalization steps; they do not invalidate the portrait's newly rendered provenance as long as the face, hair, costume design, lighting, and interior rendering remain frozen. Record every operation. When transparency is required, inspect the entire visible silhouette on black, white, and saturated red backgrounds; a transparent corner alone is not evidence of a clean cutout.

Do not add a shoulder-completion stage to portrait production. A shoulder cropped or truncated by the native portrait frame is acceptable by itself and does not block delivery. Preserve the approved portrait composition and continue only with the required ratio, background, placement, and visible-edge checks; do not outpaint or generate missing shoulder content merely to make both shoulders complete.

For existing-character state variants, keep the approved general-style character card as the identity source. Change only the requested state, expression, action, damage, prop, costume difference, or scene condition. Preserve unrequested facial, body, costume, palette, and style features.

### Expression-skill handoff

Do not produce a reusable bust-expression library inside this skill. When the request needs multiple portrait expressions, a profile-specific calm anchor, greenscreen expression assets, transparent expression assets, or green/transparent expression delivery together, finish the required approved portrait/identity work here and hand the job to `ndc-generate-expressions`.

The handoff must include the approved portrait path and status, portrait receipt when available, approved character card and same-source face anchor when available, frozen identity/costume/style invariants, and any known crop or missing-bust-region risks. Portrait delivery itself does not complete a missing shoulder. If a downstream expression profile requires a larger bust region, the expression skill may perform its own bounded completion of missing head/shoulder/chest edges, but it may not approve or redesign an upstream identity.

A one-off full-body narrative state remains in this character skill. A bust portrait expression set belongs to `ndc-generate-expressions`. Do not satisfy the latter by reusing this skill's generic existing-character state route.

## Review order

For MJ full-body candidates, review in this order:

1. Complete body, usable pose, and stable anatomy.
   Prefer two naturally lowered arms with visible hands; a hand behind the back is a repairable but meaningful pose penalty. In a strict orthographic side view, the far hand may overlap naturally, but the arm may not be posed behind the back.
2. Role, age, period, profession, and costume match.
3. NDC style formed by both MJ references.
4. Body proportion, silhouette, garment layers, shoes, and required accessories.
5. Head-quality gate.
6. Repairable local defects.

For downstream assets, first verify identity, layout/content, anatomy, and target style on the native artistic candidate. Use the matching self-check library as a group rather than choosing one convenient example. Freeze a passing candidate, perform only the required technical normalization, then verify exact final ratio, dimensions, subject/head placement, bounding boxes, alpha edges, and provenance. Do not retroactively reject a character because the two raw MJ faces differ.

Run the mechanical inspection script on the normalized final candidate after subjective artistic approval:

```text
python scripts/audit_character_delivery.py --asset-type card --input <card.png> --output-dir <qa-dir> --expected-size 3840x2160
python scripts/audit_character_delivery.py --asset-type portrait --input <portrait.png> --output-dir <qa-dir> --expected-size 1280x1600
```

The script's `mechanical_status` is only a prerequisite. Its `formal_status` intentionally remains `NOT_CHECKED` until identity, structure, style, provenance, and edge review receipts are complete. Never reinterpret a mechanical pass as a formal pass.

Before using the words `FORMAL_PASS` or delivering a formal asset, save a JSON receipt following `references/execution-gates.md` and run:

```text
python scripts/validate_delivery_receipt.py --receipt <delivery-receipt.json>
```

Only `RECEIPT_VALID: FORMAL_PASS` permits formal delivery. `RECEIPT_VALID: BLOCKED` is a valid diagnostic outcome but not a deliverable pass. `RECEIPT_INVALID` means the evidence structure is incomplete and must never be summarized as passed.

Also validate the asset's independent style-lock/texture record:

```text
python D:/Codex/NDC/scripts/validate-ndc-texture-gate.py --record <texture-gate-record.json>
```

Only `TEXTURE_GATE_VALID: FORMAL_PASS` together with the existing receipt pass permits formal delivery. The validator checks recorded evidence and fail-closed status; it never replaces Codex visual review.

For every style judgment, follow the full-image plus complete-local-coverage protocol. Sampling only the face, hands, folds, or another preferred region is insufficient; semantic crops may supplement but never replace the overlap-safe grid. Report stable group-wide traits separately from branch traits, minority tendencies, and artifacts.

Never mark an identity-sensitive asset as passed from category resemblance alone. “Same age, same hairstyle, same mustache, same coat” is insufficient if the person-specific eye, nose, mouth, cheek/jaw, ear, or hairline geometry has drifted.

## Output contract

When preparing a full workflow, return these sections in order:

1. `角色纯视觉设定`
2. `MJ 全身提示词` with Chinese and English versions
3. `MJ 参数与参考图清单`
4. `头部质量闸门`
5. `MJ 头部提示词` only when the gate fails, or mark it as skipped
6. `MJ 素材精修任务单`
7. `MJ 身份锁与同源面部锚点`
8. `通用风格全身转绘提示词`
9. `通用风格角色卡模块提示词与拼版清单`
10. `通用风格肖像提示词` only when the portrait branch is required; otherwise mark it as skipped with the route reason
11. `黑白红风格角色卡提示词` only when animation production explicitly triggers it; otherwise mark it as retained but not generated
12. `比例、身份、结构与风格自检`
13. `验收与返工路由`

For the Image 2 fast path, return instead:

1. `生产路由与理由`
2. `参考图顺序`
3. `Image 2 可复制提示词`
4. `身份与风格锁定项`
5. `验收与返工路由`

Put each user-copyable prompt in its own fenced block. Keep operator notes outside prompt blocks. State the reference-image order immediately before each prompt.

When critiquing supplied images, report each issue as:

`问题 | 严重度 | 是否重生 | 推荐处理阶段/工具 | 理由`

Distinguish user-confirmed rules from case-derived judgments whenever a new conclusion is involved.
