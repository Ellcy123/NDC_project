---
name: generate-ndc-emergency-art
description: "Design, generate, deliver, and mount local or extreme-local close-up NDC emergency-event and flashback comic frames from narrative requirements, current player knowledge, EPI02 scene art, character cards, U1 references, and formal Talk configuration. Use when producing or configuring C01-C09突发事件图片、闪回图或动态漫画单帧/多格；choose a story-driven panel shape, generate clean borderless art with the mandatory camera and graphic-style prompt, package the accepted raw art with a programmatic black border and transparency, then—only after explicit approval—deliver formal Unity assets and mount them through the Excel-first Talk workflow."
---


## Production paths and closeout

Run `python scripts/art_pipeline/ndc_art.py paths` from either configured repository root before reading or writing production files. The Git-managed launcher resolves `{PLANNING_ROOT}`, `{ENGINE_ROOT}`, and `{WORK_ROOT}` from this machine's ignored `ndc.local.json` or `NDC_PLANNING_ROOT` / `NDC_ENGINE_ROOT` / `NDC_ART_WORK_ROOT`. These names are logical roots, not literal folders or requirements for a drive letter or repository layout. Read `{PLANNING_ROOT}/docs/美术生产工作区.md` and the dependency setup it links. Never copy another person's machine paths into shared rules.

Create the task with `python scripts/art_pipeline/ndc_art.py workspace create --name NAME --kind KIND`. `{JOB_PAYLOAD}` means the exact returned `payload` path; put candidates, revisions, QA, copied inputs, and prepared delivery there. Use `python scripts/art_pipeline/ndc_art.py run SKILL_NAME SCRIPT_NAME ...` for this skill's versioned scripts. Resolve another skill with `python scripts/art_pipeline/ndc_art.py skill SKILL_NAME`; its `references/`, `scripts/`, and `assets/` are relative to the returned `skill_root`, never a compatibility entry's directory. All project-owned helper scripts and schemas must be present in Git; do not depend on private scripts in a home folder, scratch directory, or an old machine checkout. Install third-party runtimes and libraries as documented, without committing credentials or virtual environments.

Resolve character cards through `{PLANNING_ROOT}/美术资产交付/角色/角色索引.json` and expression pairs through `{PLANNING_ROOT}/美术资产交付/角色表情/表情索引.json`; retain the selected asset hash and approval state. A card does not imply approval of a portrait, expression set, or new generated asset. Other input placeholders in examples must be replaced with the task's explicitly selected, existing inputs before execution.

After the user approves the specific finished candidate, prepare and verify the engine delivery under the shared workflow. Clean closed-job payloads only through its state-aware closeout; preserve pending review and active work. These rules replace historical output-directory defaults in this skill, while all art-quality and user-approval gates still apply. Historical case paths remain provenance, not default output destinations. Missing external references or validators remain unresolved dependencies; never silently substitute another image or claim PASS.

# Generate NDC Emergency Art

Produce one user-requested NDC emergency event from requirement extraction through review-ready transparent PNGs and, when explicitly authorized, through formal game configuration and verification. One event folder may contain one image or several sequential images. C01 is a successful experiment, not a universal composition or border template.

Use two permission stages within this one workflow:

- **Experiment/review:** generate, package, and test placement under the created job's `payload/`; do not mutate formal assets or tables.
- **Approved formal delivery:** enter only when the user explicitly asks to configure/mount the approved frame in game. Generation approval alone is not configuration approval.

## Resolve the event brief

Read [source map](references/source-map.md) and inspect only the requirement, scene, character, and U1 references relevant to the requested event.

Before generation, write a compact frame plan with:

`frame | narrative instant | current player knowledge | forbidden reveal | local subject | close-up content/action | visual hook | provisional orientation/panel family | selected references`

Treat the requirement's remarks and restrictions as hard spoiler boundaries. Do not reveal an identity, injury, culprit, evidence, motive, or causal explanation before the specified dialogue does.

Every emergency frame must be a local or extreme-local close-up. This is a runtime/display constraint, not a preference. `local subject` is the cropped focal region, such as a face, eyes, hand, shoe, evidence prop, door gap, floor trace, flame edge, or localized light/shadow. `close-up content/action` is the exact action, expression, gaze, pose, or focal relationship shown inside that crop.

Enforce one dominant focal action or contact point per frame. It must win immediately at thumbnail size and occupy most of the readable image area; faces, torsos, rooms, and secondary props provide only the minimum context needed to understand that action.

- When a face is contextual rather than the story action, show only a deliberate partial crop—such as half a face, the lower face, or an eye strip—and keep it secondary. Do not default to a complete head-and-torso portrait.
- For writing, prioritize the gripping fingers, pen tip, paper contact, and a few unreadable marks. A face may appear only as a partial contextual crop unless the expression itself is a separate narrative beat.
- For handcuffs, prioritize the wrist, cuff, locking hand, chain, and exact contact point. Keep full bodies and broad police blocking outside the frame.
- Apply the same principle to rings, doors, evidence, injuries, flames, and other actions: crop around the story-bearing contact, not around the person who performs it.
- If both a facial reaction/identity beat and an action/prop beat need equal clarity, split them into two local close-ups instead of widening one image. Do not duplicate the same beat merely to increase frame count.

When an extreme crop makes connected anatomy, hand ownership, object support, or a mechanical action unstable, use a controlled pull-back for the generation source: include the complete involved hands, connected wrists or forearms, the supporting surface, and only enough nearby context to make the action physically unambiguous. After the wider source passes anatomy, prop, support, and period review, crop it deterministically to the intended local subject. Record the crop rectangle beside the corrective prompt. Do not use cropping to hide an unresolved error; the full generated action chain must already be correct.

The final accepted emergency frame must never be a medium shot, long shot, full-body portrait, complete two-person blocking, establishing view, or panorama. A slightly wider near-local generation source is only an anatomy/mechanics stabilization technique, not the delivered composition. Express scene information through a meaningful localized detail. When context still cannot fit, split movement, reveal, reaction, consequence, or time change into separate local close-ups rather than expanding the delivered frame.

Choose the smallest frame count that communicates the event under this close-up constraint. A character does not need to appear in a scene-focused frame, but the focal scene detail must remain narratively specific and readable at the supported emergency-art footprint.

For the current Unit2 C01-C09 frame-count audit, read [Unit2 frame-count guidance](references/unit2-frame-count.md). It distinguishes explicit multi-image requirements from strong recommendations and optional detail panels; it does not override a changed requirement document or user approval.

## Design the shot and panel together

Read [panel shapes](references/panel-shapes.md). Select a provisional orientation and panel family from the event's visual verb and focal relationship, not from the previous event's output.

- Use landscape when a lateral local action, hand-to-prop relation, two cropped focal details, or a localized environment-to-character contact is the main read.
- Use portrait for a face, vertical hand/weapon/suitcase crop, falling or rising limb detail, localized dominance, or isolation.
- Use near-square when a contained prop, evidence reveal, face-object relation, or compact room incident is the main read.
- Use an ultra-wide strip for eyes, hands, a sudden reveal, or a compressed before/after beat.
- Use tilted trapezoids or asymmetrical convex panels when pressure, interruption, impact, or instability benefits from a directional edge.

A set is not acceptable if every event reuses the same shallow horizontal quadrilateral without a narrative reason. In a multi-frame event, vary local action/detail and orientation when that improves rhythm, while keeping every frame close-up and the sequence visually coherent.

## Plan the screen footprint from Talk

When the event is mounted in AVG dialogue or the task includes size/XY design, read [Talk-driven screen placement](references/talk-driven-placement.md) before choosing final image dimensions.

Use the exact formal `Talk.xlsx` mount row to determine which AVG side is active. Place the event on the opposite, inactive side whenever that side remains free during the comic's lifetime. Do not infer the side from character identity or from the draft JSON's `speakType`, and do not default to the narrow centre corridor.

Treat final PNG dimensions and XY as one design decision. Runtime comic display starts from native asset size; export the approved image at its intended footprint instead of relying on the offscreen safety scaler. For multi-image events, compose the cumulative sibling bounds so every panel avoids the active AVG and remains readable as the sequence builds.

When formal mounting is requested, also account for the comic lifetime across later Talk rows; read [formal delivery and Talk mounting](references/formal-delivery-and-talk-mounting.md) before selecting the final mount row or resizing an approved panel.

## Generate clean rectangular art

Read [art direction](references/art-direction.md). Every submitted image prompt must use one of its two opening templates, replace both bracketed fields from the frame plan, and include the shared camera/style calibration block in full. This applies to character close-ups and scene-only detail close-ups. Do not shorten, paraphrase away, or replace the mandatory calibration with a generic style summary.

Use the `imagegen` skill with the selected local reference images. Assign each reference a single role: character identity, scene geometry, prop identity, or U1 style/composition. Avoid flooding the edit with redundant references. When compositing a scene and character, bind image 1 to the background and image 2 to character identity as specified by the composite template; remove any red guide box from the result.

Before submitting each generation, save the exact prompt, ordered reference paths with their assigned roles, generation surface, and conversation/task URL when available in `<event-id>_<frame>_prompt.md` beside the experimental output. Record corrective retries separately instead of overwriting the first submission. This prompt record is required for reproducibility and must match what was actually submitted.

Generate a clean full-bleed rectangular PNG first. The image model must not draw:

- black or white panel borders;
- transparent corners or cutout shapes;
- magenta masks;
- speech bubbles, captions, UI, fake lettering, watermarks, or decorative framing.

Preserve named character identity from the approved character cards and environment continuity from the EPI02 background. The chosen local subject must be sharp; only non-subject out-of-focus areas may receive realistic shallow-depth-of-field blur. Compose for the provisional panel family and leave safe space around faces, hands, evidence, and action joints that the later polygon must not cut.

Generate one candidate. Inspect narrative correctness, identity, anatomy, hands, prop count, period details, scene continuity, read order, and spoiler boundaries. Allow one corrective retry from the same references when a clear requirement is violated; do not polish a rejected candidate.

## Accept the generated raw art

Once the generated raw PNG passes story, identity, anatomy, prop, period, scene-continuity, composition, spoiler, and mandatory-prompt checks, treat that exact raw image as the accepted art candidate. The mandatory Chinese camera/fusion block and the full English graphic-style block are the complete art-style calibration for this workflow.

Do not run a second AI cleanup or style-calibration pass, and do not redraw an accepted raw image merely to reduce texture. If the first candidate violates a hard requirement, the one allowed corrective retry must start from the original references and the full mandatory generation prompt; it is a replacement generation, not a post-generation simplification step.

## Finalize and package the panel

After raw-art acceptance, write `<event-id>_<frame>_panel_design.md` beside the raw output. Record:

- narrative reason for the chosen orientation and edge direction;
- final normalized convex polygon points in clockwise order;
- border width;
- protected subjects and safe margins;
- intended screen placement or relation to sibling frames, if known;
- the closest U1 structural reference and what is deliberately different.

Run `scripts/package_panel.ps1` with those normalized points. It creates a magenta-mask preview and an RGBA PNG with a programmatic black miter-joined border. The border is a separate production step, never a second AI generation.

Use the experimental output root:

`<job>\payload\imagegen\<event-id>\<variant>\`

Do not copy into formal game assets until the user approves the specific frame. Approved delivery may later target:

`{ENGINE_ROOT}/Assets/Resources/Art/Scene/Emergency/EPI02/<event-folder>/`

Do not treat approval of the picture as permission to write formal resources or tables. Wait until the user explicitly says to configure/mount/deliver it into the game.

## Deliver and mount an approved event

When formal configuration is explicitly requested, read and follow [formal delivery and Talk mounting](references/formal-delivery-and-talk-mounting.md). Continue the same workflow through all of these stages:

1. Reconfirm the approved RGBA frame, intended native display size, exact Talk mount row, active AVG side, XY, entry motion, and visible lifetime.
2. Perform only deterministic technical resizing or packaging on the approved art. Do not redraw it with AI during delivery.
3. Copy the final frames into the formal EPI02 emergency folder, write the matching `XYposition.txt`, and provide valid Unity Sprite metadata with unique GUIDs.
4. Use the `unity-table-edit` skill to change only the authorized Talk cells in `res/xls/Talk.xlsx`; never hand-edit generated JSON or bytes.
5. Run `res/Translate/bin/Debug/Translate.exe`, then verify the workbook row, generated `Talk.json`, runtime `Talk.bytes.txt`, resource paths, metadata, dialogue linkage, side occupancy, and output timestamps.

Mount one image per exact Talk row. Multiple files in one event folder do not automatically create a sequence, and the optional video parameter is not a second-image slot. Preserve dialogue text, `next`, speaker side, and unrelated script parameters unless the user explicitly authorizes those changes.

## Acceptance and handoff

Inspect the accepted raw image, magenta preview, and transparent result at normal size and thumbnail size. Verify:

- the intended read order survives the polygon;
- every frame is a local or extreme-local close-up, with no medium, long, full-body, establishing, or panoramic composition;
- the filled `local subject` is sharp and the shallow-depth-of-field blur affects only non-subject areas;
- scene content, character design, palette, strokes, and linework remain unchanged except for necessary character lighting, with no invented material, texture, or detail;
- character and scene grading match, using the scene grade as authority;
- the full mandatory English graphic-style block was present in the generation prompt and no removed pose, full-body, briefcase, clothing-list, or white-background instruction was reintroduced;
- faces, hands, action joints, evidence, and identity props are not clipped;
- the shape supports the event rather than imitating C01;
- the frame count follows the event's distinct beats without widening any frame beyond a local close-up;
- the exact Talk mount row and active AVG side were checked when placement is in scope;
- every visible panel stays on the inactive side across its actual runtime lifetime, including later Talk rows and side switches;
- the border is consistently black and programmatic;
- all four RGBA corner alpha values are `0`, and an interior pixel is opaque;
- output dimensions and aspect ratio match the intended orientation;
- no forbidden story information appears;
- when formal delivery is requested, the formal PNG dimensions and alpha match the approved result, `XYposition.txt` and Talk XY agree, every `.meta` imports as a Sprite with transparency and a unique GUID, and every configured resource path resolves;
- when formal delivery is requested, the Excel row, generated JSON, and runtime bytes were rebuilt and checked, while dialogue text, `next`, and `isRight` remain unchanged unless explicitly authorized.

Show the accepted image and report the requirement sources, selected visual references, frame plan, panel-design path, raw/magenta/RGBA paths, dimensions, SHA256 equality for copied generation outputs, alpha check, rejected candidates, and whether any formal game asset was changed. State explicitly that no post-generation AI simplification or style-calibration pass was used. For a configured event, additionally report the exact Talk IDs and spoken lines, frame-to-row mapping, size/XY/entry settings, formal resource folder, Excel/JSON/bytes verification, and any Translate or Unity-import warning.
