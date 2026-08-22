# Midjourney operation loop

## Preflight

1. Parse the complete `ndc-mj-scene/v3` handoff. Migrate `v1` or `v2` through `ndc-scene-to-mj-prompt` before submission.
2. Verify shared requirements, every required view prompt, the layer plan, canvas use, and time-variant plan.
3. Validate view ids: `exploration` has only `eye_level`; `non_exploration` has `frontal`, `oblique`, and `overhead_45` in that order.
4. Reject any positive prompt or upload reference that contains or requests a person, character, body, corpse, role, pose, silhouette, collectible, or other mutable subject. Character tokens may appear only in one dedicated final `--no` parameter. Use architectural scale facts instead.
5. Verify local `use` references and exclude rejected references.
6. Confirm authorization, per-view iteration budget, and whether upload confirmation is required.
7. Select and verify the declared model. When it is `latest`, choose the current latest model in the live UI; do not add a fixed model-version parameter.
8. Verify fixed `--ar 2:1` in every MJ prompt. For story scenes, verify a post-MJ `16:10` crop-safe plan. For exploration scenes, verify a stable central safe area plus any post-MJ left/right Photoshop Firefly extension briefs.
9. If day/night variants are requested, submit only the declared geometry master lighting state. Preserve the other variants for Photoshop manual relighting.
10. Inspect the live UI for an HD or equivalent high-quality control. Enable it when available; do not invent a legacy parameter when absent.

## Browser execution

1. Use `browser:control-in-app-browser` and follow its current documentation.
2. Navigate directly to or reuse `https://alpha.midjourney.com/imagine`; do not identify Alpha by the upper-left logo and do not substitute the non-Alpha site.
3. Inspect live controls; never assume coordinates, labels, or menu placement from old screenshots.
4. Resolve authentication with the user on the selected browser surface.
5. Click `Images` in the upper-right, then select the two corresponding static style references already saved in the Midjourney account from the panel below. Assign both to Style Reference and do not re-upload their bundled local copies.
6. Read current upload instructions only when additional handoff `status: use` local files must be sent. Assign every reference only its declared role and verify that it cannot leak characters or mutable props.
7. Verify required style references, the declared model, requested generation ratio, and HD/high-quality state when exposed.
8. Process `view_prompts[]` in declared order. Submit each exact first-round prompt as one independent job; never combine views.
9. Confirm every required job exists and wait for every full result grid.

## Review and iterate

For each view and round:

1. Inspect all candidates at sufficient size to judge geometry, permanent environment, and forbidden content.
2. Apply `review-rubric.md` against the shared requirements and that view's contracts.
3. Reject characters, bodies, collectibles, disappearing props, Loop-specific elements, interaction close-ups, and scan overlays before aesthetic comparison.
4. Record one factual failure delta per rejected candidate.
5. Compare scale against declared architectural landmarks. If useful, ask for a temporary post-generation neutral silhouette overlay outside Midjourney; never use it as a prompt or reference.
6. For exploration canvases, check the stable central safe area and whether both edges can be extended without breaking route or perspective continuity.
7. Choose stop-view, subtle variation, strong variation, or repaired resubmission. Repair repeated structural defects instead of consuming rounds on variations.
8. Deduct the round from that view's budget and stop for approval before exceeding it.

Change one related prompt section per repair. Keep a short round log so accepted clauses are preserved.

## Stop conditions and Photoshop handoff

Stop one view when it passes hard requirements and has acceptable finish, the authorized budget is exhausted, page state needs user action, source ambiguity blocks review, or the user changes the target.

Declare the Midjourney set complete only when every required view has a passing, character-free base. Then report:

- the selected candidate and exact last prompt per view;
- any unresolved requirement;
- `story_frame` or `horizontal_pan_scene` canvas use;
- left/right Photoshop Firefly extension instructions, if any;
- day/night manual relighting variants while locking geometry;
- all collectibles, transient story items, interaction assets, scan overlays, characters, and bodies that must remain removable layers.

Do not operate Photoshop, automatically upscale, download, delete, publish, or launch extra jobs unless the user separately authorizes that work.
