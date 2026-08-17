# Accepted NDC scene handoff

Accept `handoff_version: ndc-mj-scene/v2` with these required payloads:

```yaml
handoff_version: ndc-mj-scene/v2
scene:
  id: "optional"
  name: "scene name"
  purpose: "background or other use"
  mode: "exploration | non_exploration"
original_requirement: |
  The source requirement to audit.
visual_brief:
  time: ""
  interior_exterior: ""
  architectural_function: ""
  visual_facts: []
  removed_nonvisual_facts: []
normalized_requirement:
  hard: []
  soft: []
  flexible: []
  must_not_have: []
view_prompts:
  - id: "eye_level | frontal | oblique | overhead_45"
    label_zh: ""
    camera_contract:
      view_direction: ""
      perspective: ""
      camera_height: ""
      horizon: ""
      pitch: ""
    scene_description:
      viewpoint_change: "none"
      foreground: ""
      middle_ground: ""
      background: ""
      lateral_layout: ""
      architecture_relations: []
      camera_calibration: []
    prompt_en: |
      Exact first-round Midjourney prompt for this view.
    prompt_zh: |
      Chinese review counterpart for this view.
references:
  - file: "absolute local path or image label"
    role: "style | environment | composition | identity | reject"
    status: "use | reject"
    reason: "contribution or leakage risk"
parameters:
  aspect_ratio: "2:1"
  model: "8.1"
  other: []
review_priority: []
assumptions: []
operator_notes:
  iteration_budget_per_view: 3
  preferred_action: "submit-required-view-set-and-review"
```

## Validation

- Reject a packet that has prompts but no requirements: it cannot support reliable image review.
- Reject a packet that has requirements but no complete `view_prompts` set: it is not submission-ready.
- `scene.mode: exploration` requires exactly one entry with `id: eye_level`.
- The exploration camera contract and prompt must explicitly require an eye-level three-point-perspective composition aligned with a standing eye line, camera height `1.7–1.8 meters`, and horizon at the upper third.
- `scene.mode: non_exploration` requires exactly three entries in this order: `frontal`, `oblique`, and `overhead_45`.
- The `overhead_45` entry must describe an approximately 45-degree downward camera angle, not merely a 45-degree horizontal rotation.
- Reject any entry that asks for more than one view, a contact sheet, split panels, or a collage in one image.
- Treat each `prompt_en` as exact for that view's first submission.
- Treat `original_requirement` as the shared factual audit source and `normalized_requirement` as the shared priority map.
- Require `visual_brief`, `camera_contract`, and `scene_description`; use the latter two as the explicit per-view camera and spatial audit contract.
- Do not submit `ndc-mj-scene/v1` directly. Migrate it through `ndc-scene-to-mj-prompt` so scene mode and required view count are explicit.
- Shared scene identity, architecture, core objects, lighting state, exclusions, and rendering language must not drift between non-exploration views. Camera-dependent layout wording may change.
- Do not reinterpret `soft` or `flexible` counts as hard.
- Do not upload `status: reject` references.
- If a `use` reference has no role, stop and classify it before upload.
- Default `parameters.model` to `8.1`. Accept another version only when the current user request explicitly overrides it.
- Select the declared model in the live UI and verify it before every required job set. If unavailable, stop instead of silently falling back.
- Do not duplicate model selection with a `--v` parameter in any `prompt_en`.
- Count each view's initial grid as round 1 for that view.

The packet may contain extra source paths or notes, but they do not replace the required text fields.
