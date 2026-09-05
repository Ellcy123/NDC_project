---
name: ndc-multichar-avg-production
description: Design and produce NDC static AVG scenes containing two or more simultaneous characters, from story-grounded left/right blocking and variable-N colored whiteboxes through one-actor contextual generation, Photoshop extraction, coordinate-locked compositing, and final layered PSD/PNG review. Use for 多人AVG、多人过场图、多人静态剧情图、逐人抠图贴回场景；not for character design, expression sheets, dynamic comics, or empty-background generation.
---


## Production paths and closeout

Run `python scripts/art_pipeline/ndc_art.py paths` from either configured repository root before reading or writing production files. The Git-managed launcher resolves `{PLANNING_ROOT}`, `{ENGINE_ROOT}`, and `{WORK_ROOT}` from this machine's ignored `ndc.local.json` or `NDC_PLANNING_ROOT` / `NDC_ENGINE_ROOT` / `NDC_ART_WORK_ROOT`. These names are logical roots, not literal folders or requirements for a drive letter or repository layout. Read `{PLANNING_ROOT}/docs/美术生产工作区.md` and the dependency setup it links. Never copy another person's machine paths into shared rules.

Create the task with `python scripts/art_pipeline/ndc_art.py workspace create --name NAME --kind KIND`. `{JOB_PAYLOAD}` means the exact returned `payload` path; put candidates, revisions, QA, copied inputs, and prepared delivery there. Use `python scripts/art_pipeline/ndc_art.py run SKILL_NAME SCRIPT_NAME ...` for this skill's versioned scripts. Resolve another skill with `python scripts/art_pipeline/ndc_art.py skill SKILL_NAME`; its `references/`, `scripts/`, and `assets/` are relative to the returned `skill_root`, never a compatibility entry's directory. All project-owned helper scripts and schemas must be present in Git; do not depend on private scripts in a home folder, scratch directory, or an old machine checkout. Install third-party runtimes and libraries as documented, without committing credentials or virtual environments.

Resolve character cards through `{PLANNING_ROOT}/美术资产交付/角色/角色索引.json` and expression pairs through `{PLANNING_ROOT}/美术资产交付/角色表情/表情索引.json`; retain the selected asset hash and approval state. A card does not imply approval of a portrait, expression set, or new generated asset. Other input placeholders in examples must be replaced with the task's explicitly selected, existing inputs before execution.

After the user approves the specific finished candidate, prepare and verify the engine delivery under the shared workflow. Clean closed-job payloads only through its state-aware closeout; preserve pending review and active work. These rules replace historical output-directory defaults in this skill, while all art-quality and user-approval gates still apply. Historical case paths remain provenance, not default output destinations. Missing external references or validators remain unresolved dependencies; never silently substitute another image or claim PASS.

# NDC Multi-character AVG Production

Produce a static multi-character AVG image on an already approved fixed NDC background. Keep the original scene pixels authoritative and deliver a reconstructable layered PSD plus a flattened PNG.

This is a specialized production workflow built on `../ndc-character-scene-integration/`. Reuse that skill's deterministic tools and detailed prompt modules, but do not rely on inheritance alone: the multi-character hard gates below are mandatory within this skill and its `ndc-multichar-avg-plan/v2` contract.

## Essential invariants

- Resolve the current Unit/Episode through `canon_manifest.json`; do not infer chapter identity from folder names.
- Determine whether the AVG already exists before producing anything. Audit or repair an existing completed scene only when the user requests it.
- Start from a fixed approved background. Do not use this skill to generate or redesign an empty scene.
- Select one readable dramatic snapshot from the actual dialogue/state. Write the silent-frame statement before blocking.
- Cluster the cast primarily on the left half or the right half. Do not distribute characters evenly across the full width like a stage lineup.
- Treat the current simultaneous cast as `N`. A combined whitebox contains exactly those `N` actors, and each actor has one matching isolated whitebox.
- Assign `N` clearly distinct matte colors to `N` actors. Colors are local segmentation labels only: never bind blue to Zack, amber to Leonard, or any color to a permanent identity. Preserve the chosen mapping only through the current scene/snapshot handoffs.
- When `N >= 3`, at least one actor must be clearly back-facing or three-quarter-back. That actor is normally a foreground half-body presence with feet outside the frame.
- Prefer standing poses. A seated pose needs a current-node dramatic and physical-support justification.
- Generate one actor at a time. Never ask the image model to generate the simultaneous cast as one fused image.
- Do not design limb contact between actors. A prop belongs to one actor at the frozen snapshot and is held close to that actor; avoid the unstable instant of hand-to-hand transfer.
- Whitebox approval locks pose, occupied volume, depth, gaze, support, and placement. Later Photoshop work may use one uniform scale plus translation per actor; never warp anatomy or use a universal scale percentage.
- The generated contextual scene is reference-only. Only an approved extracted actor/loose prop/shadow component may enter the final PSD. The untouched source background supplies every final background pixel.
- Photoshop Select Subject is an initial mask, not a final matte. Inspect and manually repair hair, glasses, fingers, props, foliage overlaps, and rail gaps.
- Do not write into Unity or replace a formal runtime asset unless the user explicitly authorizes that separate delivery step.

## Internal hard gates

These rules apply even if the parent skill is unavailable or not loaded:

- Timeline: derive the exact simultaneous cast from the active dialogue/state branch. Record one frozen `timelineSnapshotId` and whether each actor is already present or enters at that snapshot. A character who speaks later is not automatically a later entrant.
- Actual UI: locate the real left/right dialogue-UI image or engine-derived mask. `uiSide` is only a routing label; it is never proof of safety. Record the UI file, hash, canvas placement, mirror state, machine report, and overlay. No face, identity-critical head area, motivated hand, owned prop, or action focus may be hidden.
- Canonical height: read every actor's integer height in centimeters from the current character canon and record the source file. Never infer relative height from the generated result.
- Identity scale: measure the approved character card's full-body and anatomical-head pixel heights and record body-build/head-to-body notes. Head-size relationships take priority over shoulder bulk, clothing silhouette, or apparent muscularity.
- Absolute scene scale: validate the cast against at least three independent fixed-object groups. The set must cover horizontal and vertical measurements, at least two depth bands, and both actor-local and cross-depth evidence. Record assumptions and confidence; do not size the whole cast by eye.
- Cast-relative scale: project canonical heights from each actor's support point/depth, then compare standing-equivalent height and anatomical head height pairwise. Perspective may make a shorter foreground actor larger on canvas, but the report must explain it.
- Exact performance and pose: record the silent-frame verb, beat energy, ongoing occupation, performance family, action, emotion, facial expression, body line, weight distribution, both-hand motivations, named support, social territory, action focus, subtext, costume state, prop continuity, depth honesty, head box, neck, shoulders, elbows, hands, hip center, knees, feet, outer action box, support point, facing, gaze, and a pose that can be held for ten seconds.
- Support and affordance: name the floor/chair/desk/rail or off-frame support and validate contact. A cropped foreground actor still needs an intentional off-frame support model; do not lower the body until it looks crouched merely to hide the feet.
- Occlusion: record every actor pair as no-overlap or an explicit front/back relationship, plus any exact-source scene occluders. Do not improvise layer order during Photoshop assembly.
- Artifact linkage: the combined and isolated whiteboxes must use the source-scene canvas, the same actor pose/transform, and recorded hashes. Regenerate affected isolated whiteboxes when blocking changes.
- Visual review: before approval, inspect the whole frame at 100% and every head, hand, prop, support, edge, and overlap region at 200%; save a report and review images. A JSON validator pass never substitutes for this visual inspection.

Do not advance to `whitebox-approved` unless timeline, actual UI, absolute scene scale, cast-relative scale, support, occlusion, artifact-linkage, and whitebox visual-review gates all pass. Do not advance to `final` unless gaze, identity, lighting, matte, registration, background preservation, and final visual review all pass.

## Workflow

1. Read [references/workflow.md](references/workflow.md) and resolve the source scene, dialogue beat, current cast, prop ownership, and existing-asset status.
2. Present one concrete text blocking example before creating or changing production files, following the repository confirmation rule.
3. After confirmation, author the v2 cast plan described in [references/contracts.md](references/contracts.md). Complete timeline, canonical-height, character-card scale, real-UI, scene-scale, cast-scale, affordance, pose-landmark, and occlusion records as described in [references/workflow.md](references/workflow.md). Run `scripts/validate_avg_cast_plan.py` at every declared stage.
4. Produce and visually review the combined anatomical mannequin whitebox plus `N` isolated whiteboxes. Run every `whitebox-approved` gate and ask for whitebox approval before formal actor generation.
5. For each actor, run the existing `prepare-local-generation-handoff` tool and read `../ndc-character-scene-integration/references/prompt-modules.md`. Attach references in its required order: local isolated whitebox crop, untouched full scene, approved character card.
6. Generate each actor separately. Reject identity, costume, gaze, pose, scale, light, or texture drift before extraction. Retry only the failed actor.
7. Read [references/photoshop-and-qa.md](references/photoshop-and-qa.md), then extract, manually refine, register, shadow, layer, and export through actual Photoshop.
8. Inspect the whole composite at 100% and every actor/action region at 200%. Validate the final plan, leave the layered PSD open when useful, and deliver links to the PSD, PNG, and review record.

## Confirmation modes

- Default: confirm the text blocking example, then confirm the combined whitebox. Continue actor-by-actor unless the user asks for a batch.
- Stepwise: pause after every actor candidate and every requested Photoshop adjustment.
- Batch: after the combined whitebox is approved, generate, extract, and composite all actors sequentially without intermediate approval. Still reject and regenerate failed actors internally; do not propagate a known failure into the final PSD.

User approval never converts a known technical or semantic failure into a pass. If the user changes the blocking, regenerate the combined and affected isolated whiteboxes before changing final actors.
