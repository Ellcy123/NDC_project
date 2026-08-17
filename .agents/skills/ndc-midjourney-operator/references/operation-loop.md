# Midjourney operation loop

## Preflight

1. Parse the complete `ndc-mj-scene/v2` handoff.
2. Verify that shared requirements and every required view prompt are present.
3. Validate `scene.mode` and exact view ids: `exploration` has only `eye_level`; `non_exploration` has `frontal`, `oblique`, and `overhead_45` in that order.
4. Verify local `use` references and exclude rejected references.
5. Confirm authorization, per-view iteration budget, and whether upload confirmation is required.
6. Select and verify the handoff's declared model, default V8.1. If it is unavailable, stop rather than silently using another version. Preserve unrelated page settings.
7. Verify the aspect ratio in every view prompt and inspect the live UI for an HD or equivalent high-quality control. Enable and confirm it when available; treat HD as separate from model selection and never invent a legacy parameter when the control is absent.

## Browser execution

1. Use `browser:control-in-app-browser` and follow its current documentation.
2. Navigate to or reuse `https://www.midjourney.com/imagine`.
3. Inspect live controls; never assume coordinates, labels, or menu placement from old screenshots.
4. Resolve authentication with the user on the selected browser surface.
5. Read current upload instructions before sending local files.
6. Assign each reference only its declared role.
7. Verify both mandatory static references are assigned as Style References, verify the declared model is selected, verify the requested aspect ratio, and confirm the HD/high-quality state when the UI exposes it.
8. Process `view_prompts[]` in declared order. Submit each exact first-round prompt as one independent job; never combine views into one image.
9. Confirm every required job exists and wait for every full result grid. For `non_exploration`, do not stop after only the frontal or oblique job.

## Review and iterate

For each required view and each of its rounds:

1. Inspect all candidates at sufficient size to judge core layout and objects.
2. Apply `review-rubric.md` against the shared requirements and that view's camera contract.
3. Record one factual failure delta per rejected candidate.
4. Compare camera height with calibration landmarks and compare foreground-middle-background plus left-center-right architecture relations with that view's handoff entry.
5. Choose stop-view, variation, or repaired resubmission.
6. For a localized defect on an otherwise valid candidate, try Subtle first; inspect that result before Strong. For a repeated structural defect, repair and resubmit.
7. Deduct the round from that view's budget.
8. Stop and ask before exceeding that view's budget.

Do not change several unrelated prompt sections in one repair. Keep a brief round log so accepted clauses are not lost.

## Stop conditions

Stop one view when:

- a candidate passes hard requirements and has acceptable finish;
- that view's authorized iteration budget is exhausted;
- authentication, upload permission, or page state requires user action;
- a hard source ambiguity prevents honest review;
- the user interrupts or changes the target scene.

Declare the complete set finished only when every required view has one passing candidate. For `non_exploration`, passing frontal, oblique, and 45-degree overhead selections are all required; one attractive view cannot substitute for another.

Report what passed per view, what remains unresolved, and every exact last prompt. Do not automatically upscale, download, delete, publish, or launch extra jobs.
