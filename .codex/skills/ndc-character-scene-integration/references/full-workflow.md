# Full workflow

白模顺序：初次生成时包括隐藏部位的完整人体，保留未裁剪母层；随后按真实遮挡关系裁剪派生层或制作蒙版，审核裁剪后的场景参考。正常裁剪不算缺失，不要求补回场景中本应被遮住的像素；小瑕疵容错不取消初始完整生成。正式角色同样先生成完整母层再应用遮挡。

白模阶段以 [白模放行与正式完整性](whitebox-acceptance.md) 为准：位置、比例、头身比、动作和演绎可准确判断时，小型遮挡、局部缺失和细节可放行，不为此强制补全、PS返修或再生成。下文完整母层要求在正式生产仍适用；白模只须提供足以判断核心目标的独立及联合参考。

Execution cadence and reuse are defined in [production-cadence.md](production-cadence.md). The sections below are decisions within four milestones, not separate rounds of tool discovery, image generation or duplicate review.

Keep one owner for each complete scene at each phase: Astra/medium owns references, then Terra/xhigh owns formal production after the full scene packet passes. Read [phase handoff](../../ndc-art-stage-pipeline/references/integration-pipeline.md); different released scenes may overlap. Layered actor batches do not authorize cross-task or cross-stage actor pipelines within that scene. For actual PS operations read the [global queue](../../ndc-photoshop-queue/SKILL.md); independent-scene non-PS overlap follows the cadence reference.

## 1. Whole-scene rehearsal

Read the original scene, approved identity cards/profiles, current requirements and engineering evidence once; record paths/hashes and reuse unchanged findings. Use `scene_staging_tools.py extract-timeline` for SceneConfig, Talk and NPCLoopData. Resolve exploration idle/active versus pure-narrative, configured versus required cast, dialogue branch and entrances/exits without changing engineering tables.

Read [directing-and-timeline.md](directing-and-timeline.md). Choose the visible beat and differentiated actor activities before pose coordinates: who explains, listens, observes or rests. Quiet actors can have naturally relaxed hands; no invented prop is required. Check narrative meaning and natural body mechanics separately. Preserve uninterrupted actor states and never aim at future entrants. A closed door is not proof of an entrance.

Interpret the fixed scene as walkable/support/occupied/occluding space. Resolve floor depth and furniture footprint before selecting scale. Support points must come from scene evidence, not a line reverse-engineered from the chosen feet. Consult [continuous-floor-support.md](continuous-floor-support.md): continuous-region coverage does not measure floating or sinking, and hidden support needs an unobstructed complete-layer review plus final occluded read.

Use available candidates for the first full-shot preview; otherwise use the first anatomical whitebox assembly. Mark provisional outputs as such. Judge the silent scene and overall naturalism before polish. Select one actual dialogue UI side by narrative and visibility cost; test its real mask, with faces and critical hands/props unobstructed. Do not shrink actors just to satisfy both mutually exclusive masks.

## 2. Layered production

### Support, scale and natural pose

Read [placement-decision-chain.md](placement-decision-chain.md). Establish source-authoritative floor/support locations, then target depth, then scale. Create/reuse the shared scene-scale v2 register. Height calibration uses independent vertical evidence across local and cross-depth bands; horizontal furniture normally checks footprint and clearance, without contributing to the height factor. Horizontal-to-height conversion still needs real direction-transfer evidence. Where camera metric information is insufficient, bounded mode must retain measured versus assumed ranges, support/hidden-foot intervals and sensitivity evidence with current whitebox/head/support/UI reviews. If plausible assumptions materially change placement or readability, block geometry instead of manufacturing precision. Placements reference this same source/hash and their support-plane projection; do not re-enter the same furniture estimates per actor.

Run cast-scale v2 head-first against approved-card anatomical head/body references. Use 20% individual and 20% pairwise head-ratio deviation under the user's 80% consistency requirement. Retain canonical height and fixed-scene body-scale checks. For a tilted/lying head, use the reviewed crown-to-chin anatomical axis; do not enlarge it to compensate for screen rotation or pretend the axis solves unseen foreshortening.

Author a viable complete pose with head, neck, shoulders, elbows, hands, hips, knees, feet, action target and support. Coordinates record the selected pose; they do not force a rigid silhouette or demand all limbs visibly separate. Preserve actual user-locked coordinates unless authorized to revise. Check weight through feet/pelvis/torso and appropriate shoulder/arm relaxation. A hand's natural rest is a valid motivation.

### Anatomical whiteboxes and contact

Follow [layered-character-batches.md](layered-character-batches.md): far-to-near batches may contain several separable complete actors. Generate/reuse an independently reviewed empty-scene depth image and anatomical 3D whiteboxes with stable distinct matte colors. No stick/joint/block figures or technical ruler as generation authority. Produce each complete master and the combined snapshot from those same layers/transforms; do not extract the only actor copy from an already occluded cast.

Inspect hidden anatomy and support with foreground occluders temporarily hidden or bedding ghosted/cut away, then restore the final source-pixel occluders. At whitebox stage, inspect enough of the lying body axis and support to judge position, scale and performance; minor hidden or missing regions follow whitebox-acceptance.md. Formal masters still require the entire head-to-feet body. Whitebox hard review covers structure, body scale, support and visible action silhouette; tiny eye/expression details transfer to formal review.

Run support validation. Fixed bed/seat/step lines keep their numeric tolerance; continuous floors use independent region plus actual physical review. Lying support additionally requires bed polygon, head/pillow region, foot-end region and a valid complete body axis. Coordinate coverage alone cannot approve contact. Head, neck and shoulders must be comfortably borne by the pillow; bedding/cushions need corresponding load, indentation, rise/wrap and contact shadows.

Keep a complete human master and minimum soft-response layer. Treat them as a coupled interaction when adjusting; do not freeze an unloaded pillow merely to preserve the scene. Fixed frames/rails/architecture remain original 1:1 pixels. For actual loose-object relocation, require old-location repair and destination masks. Run component-policy validation, including the final overlay plan.

Review independent and combined images for scene scale, natural acting, support, soft response, actual UI and cast/scene overlap. For whitebox defects first use [ps-first-repair.md](ps-first-repair.md), with whitebox-specific reacceptance in [whitebox-photoshop-fallback.md](whitebox-photoshop-fallback.md): at most three model attempts and three coherent PS repair/review rounds where supported. PS can start after the first useful candidate. Maintain counts and valid lower layers. Only current accepted whiteboxes, depth and required reports may pass the pre-generation production ledger.

### Actual generation handoff

Use the accepted isolated anatomical layer on the untouched original-color scene, not a globally neutralized room. `prepare-local-generation-handoff` records a 1:1 original-pixel crop expanded to a supported generation ratio, the requested/returned ratio, source hashes and Photoshop coordinates:
1. Image 1 is the local original-scene crop with the approved mannequin; it controls pose, volume, location and contact.
2. Image 2 is the untouched full scene for camera, perspective, light and palette.
3. Image 3 is the approved character card for identity, body type, costume and illustration language, not pose.

Use [prompt-modules.md](prompt-modules.md) and the visual-description helper on the actual assembled input. Keep visible language consistent with view and action, and explicitly distinguish fixed structure from responding soft material. Inspect the input references/crop; a correct draft cannot certify a later conflicting prompt. Unsupported or returned-ratio mismatch stops mapping; use an actually supported ratio rather than stretching/cropping to conceal mismatch.

Default first output is contextual local replacement. If it has local defects, apply the PS-first repair decision before requesting another model output; process-only component extraction is allowed to make a bounded repair concrete, but does not approve the contextual image. Preserve context for contacts and lighting; only actors and authorized minimum soft responses become replacement pixels. Do not regenerate fixed furniture into an actor layer. Review the contextual result against identity/style authority and the approved pose/scene before extraction.

### Extraction and registration

Use verified extraction that preserves accepted RGB; do not require a second generative pass when genuine alpha or a supported non-generative selection/mask route already works. Keep the original complete contextual canvas and its scene-crop mapping. A model removal fallback consumes the actor/interaction's shared model budget and must be inspected for redesign or scale drift.

No tight hand polygon or inward erosion may clip anatomy to hide contamination. Validate coverage and straight-RGB edge quality on black, white and scene-tone backgrounds. Where `conservative_matte.py` is relevant, keep its raw report and localized material findings; white hair/collars/highlights are not automatically background.

Map the complete local canvas back to the declared original crop, then preview on the original scene. An anatomically and semantically valid component may receive a verified support-anchored uniform scale/translation under the cadence policy. Update its affected placement/whitebox and coupled soft responses, then recheck scene/cast scale, support, naturalism, UI and occlusion. Do not fit an alpha box, warp anatomy, silently relax a locked coordinate, or independently rescale fixed structure. Bounded re-extraction, donor-pixel and occlusion repairs follow ps-first-repair.md. A wrong pose or wrong geometric premise returns to design/geometry rather than repeated cosmetic transforms.

Same-image technical steps can share one coherent operation ending in save, technical check and whole/local visual review before this task advances to its next image. A safe saved checkpoint and frozen review snapshots permit suspension for other independent queued tasks without accepting the unfinished image or its dependents; follow the shared queue for release and recovery. Retain actual extraction and registration artifacts/views for the legacy ledger scopes; do not fabricate a discarded stage. Preserve the high-resolution source and compose transforms before final resampling.

## 3. Whole-scene acceptance

Assemble the actual layers: unchanged background, source repair patches where authorized, actors, minimum soft responses, exact-source irregular occluders with holes/rails preserved, and reviewed contact/cast shadows. Use [shadow-construction.md](shadow-construction.md) when needed. Different timeline casts require their own snapshots; do not combine actors who never coexist.

At gameplay size, read narrative relationship and natural body language before zooming. Review full scene at 100% and applicable local regions at 200%/original pixels. Distinguish:
- narrative correctness from stiffness or ritual-like shared posture;
- head/body identity ratio from scene-relative size and true support;
- footprint/region membership from physical contact and structural clearance;
- a head in a pillow polygon from an actually supported head/neck/shoulder chain;
- valid alpha/hash from preserved identity, contour, material and light.

Use existing visual checks/findings for these observations; no extra report family is required. Final gaze checks apply to actually visible evidence; do not invent an eye vector through a back-facing head or treat closed eyes as looking at a target. Check gross orientation structurally and carry the reason where numeric gaze is inapplicable.

Validate final absolute/cast scale, applicable support, component policy, actual UI, gaze, edges, texture/style and final conformance on current outputs. Reuse unchanged valid evidence according to cadence, with complete current coverage. One actor's repair invalidates its interactions and affected combined views, not all independent passed assets. If the image still looks wrong, it fails even when technical reports agree.

## 4. Package and report once

For exploration pairs use `verify-exploration-states`; local patches also follow [state-variant-assembly.md](state-variant-assembly.md). Preserve intended social territory/support and shared runtime transform. Verify actual visible state differences and frozen pixels, not only file names.

Run the post-generation ledger with the five real review scopes and current final reports. `EVIDENCE_GATE_PASS` means structural evidence coverage, not artistic acceptance. File-only outcomes use `TECHNICAL_FILE_PASS/FAIL`.

Follow [delivery-contract.md](delivery-contract.md). Freeze accepted images, generate one source/XY/layer/hash manifest and reconstruct at 100% on the original scene. Verify zero drift outside authorized alpha and fixed regions. Copy only passed assets to the scene-named formal folder; keep prompts, evidence and candidates under work files. Copy bindings may reuse actual unchanged review, never invent a new review timestamp.

The cadence reference owns attempt counts, finite repair/time checkpoints and candidate handling. Budget exhaustion, a capability stop or a user pause does not require pretending that six attempts happened. Report completed assets and unresolved candidates accurately without another routine approval hold. User rejection or a visible failure always overrides prior self-check PASS.
