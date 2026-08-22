# `ndc-mj-scene/v3` handoff schema

Return a human-readable summary followed by one YAML block using this field order. Preserve the shared requirements and every required view prompt; neither can replace the other.

```yaml
handoff_version: ndc-mj-scene/v3

scene:
  id: "optional NDC scene or asset id"
  name: "short scene name"
  purpose: "background, key art, evidence close-up, or other use"
  mode: "exploration | non_exploration"
  canvas_use: "primary_exploration | story_progression"

original_requirement: |
  Faithfully retain the user's or source document's requirement.
  Keep wording that may matter to later review.

visual_brief:
  time: "time of day or lighting condition"
  interior_exterior: "interior | exterior | mixed"
  architectural_function: "what the space is for"
  visual_facts:
    - "drawable, source-supported fact shared by every view"
  removed_nonvisual_facts:
    - "dialogue, explanation, or character action omitted or converted"

normalized_requirement:
  hard:
    - "shared core object, scene identity, or gameplay-critical fact"
  soft:
    - "shared important type, distribution, lighting, material, or period cue"
  flexible:
    - "shared harmless count, ornament, or incidental variation"
  must_not_have:
    - "shared prohibited subject or damaging failure"

layer_plan:
  base_environment_narrative:
    - "permanent content allowed in the generated background"
  interaction_closeup:
    - "evidence reserved for a separate close-up"
  scan_overlay:
    - "residue, imprint, or analysis visualization kept separate"
  collectible_layer:
    - "pick-up item kept separate"
  transient_story_layer:
    - "character, body, temporary prop, or Loop-specific object kept separate"

view_prompts:
  - id: "eye_level | frontal | oblique | overhead_45"
    label_zh: "平视搜证视角 | 正方位视角 | 侧方位/斜侧视角 | 45度俯视角"
    camera_contract:
      view_direction: "where the camera faces"
      perspective: "perspective type"
      camera_height: "exact range, source value, or justified description"
      horizon: "horizon placement"
      pitch: "eye-level, level, or approximately 45 degrees downward"
      scale_calibration:
        - "door, handrail, desk, wainscot, window sill, or stair landmark"
    scene_description:
      viewpoint_change: "none, or rotation direction/degrees plus elevation change"
      foreground: "foreground anchors in this view"
      middle_ground: "middle-ground anchors in this view"
      background: "background anchors in this view"
      lateral_layout: "left, center, and right major masses in this view"
      architecture_relations:
        - "connection, separation, overlap, route, and relative-scale rule"
      camera_calibration:
        - "observable landmark used to verify this view's camera"
    prompt_en: |
      One exact copy-ready English Midjourney paragraph for this view.
    prompt_zh: |
      A faithful Chinese counterpart for human review.

references:
  - file: "absolute local path or user-provided image label"
    role: "style | environment | composition | identity | reject"
    status: "use | reject"
    reason: "what it contributes or why it risks semantic leakage"

parameters:
  generation_aspect_ratio: "2:1"
  model: "latest"
  other: []

canvas_plan:
  final_delivery: "16:10 | horizontally_extended_exploration"
  final_size: "exact pixels if supplied; otherwise unresolved"
  post_mj_operation: "crop_or_reframe_to_16_10 | extend_horizontally | none"
  crop_safe_area: "required content that must survive a 16:10 crop, or not_applicable"
  central_safe_area: "composition that must remain intact"
  left_extension: "continuity constraints for Photoshop Firefly, or none"
  right_extension: "continuity constraints for Photoshop Firefly, or none"
  pan_readability: "how entrance, route, anchors, and interaction zones read while panning"

time_variant_plan:
  geometry_lock: true
  master_time: "day | night | other"
  requested_variants: []
  method: "Photoshop manual relighting; no MJ regeneration by default"

postprocess_handoff:
  photoshop_firefly_extension: "required | not_required"
  manual_relighting: "required | not_required"
  removable_layers: []

review_priority:
  - "core composition and per-view camera contract"
  - "core objects"
  - "scene identity and period"
  - "reference leakage"
  - "lighting and finish"

assumptions:
  - "non-blocking inference made while drafting"

operator_notes:
  iteration_budget_per_view: 3
  preferred_action: "submit-base-view-set-review-and-handoff-to-photoshop"
```

## View-set rules

- `scene.mode: exploration` requires exactly one `view_prompts` entry with `id: eye_level`.
- The exploration `camera_contract` must state an eye-level three-point-perspective composition, camera optical center `1.7–1.8 meters` above the floor, horizon at the upper third, and eye-level pitch.
- `scene.mode: non_exploration` requires exactly three entries in this order: `frontal`, `oblique`, and `overhead_45`.
- `overhead_45` means the camera looks downward at approximately 45 degrees. It does not mean a 45-degree horizontal rotation.
- Each entry is one independent Midjourney job. Never combine multiple required views into one prompt or one multi-panel image.
- Shared scene identity, architecture, core objects, lighting state, exclusions, and rendering language must not drift between non-exploration views. Only camera-dependent spatial descriptions may change.
- `scene.canvas_use: story_progression` requires `final_delivery: 16:10`, `post_mj_operation: crop_or_reframe_to_16_10`, and a post-MJ crop-safe plan.
- `scene.canvas_use: primary_exploration` requires a central safe area plus any post-MJ left/right Photoshop Firefly extension and pan-readability plans.

## Field rules

- `original_requirement` is the audit source, not decorative provenance. Do not replace it with only the prompts.
- `visual_brief` retains only shared drawable facts and records what nonvisual material was removed or translated.
- `scene.mode` comes from gameplay: use `exploration` only when the player must search, inspect, or collect props or evidence. Ordinary furniture or decoration is insufficient.
- Every `scene_description` is a per-view camera and spatial contract. Use `viewpoint_change: none` only when that entry does not convert an existing source view.
- Do not invent exact camera values except for the project-mandated exploration lock. Record other inferred ranges under `assumptions` and make them hard only when composition or readability depends on them.
- Every NDC scene handoff must add `empty environment with no visible characters` to `normalized_requirement.hard` and list `people, named characters, crowds, human figures, faces, bodies, silhouettes` under `must_not_have`. Keep those tokens out of positive `prompt_en` prose and place them only in one final dedicated `--no` parameter.
- Character names, blocking, poses, and actions may remain verbatim in `original_requirement` for provenance, but must be translated into environmental traces and must not appear as positive content in any `prompt_en` or `prompt_zh`.
- Yellow or neutral character silhouettes are scale-review overlays only. Do not put them in prompt text or references. Populate `camera_contract.scale_calibration` with architectural landmarks instead.
- Only permanent environmental storytelling belongs in `layer_plan.base_environment_narrative`. Put every collectible, disappearing object, character, body, Loop-specific prop, close-up clue, and scan visualization in its separate layer list and exclude it from the generated base prompt.
- `normalized_requirement` explains shared priority. Do not promote harmless object counts into `hard`.
- Each `prompt_en` is the exact submission text for its own view. The operator must not silently rewrite it before that view's first run.
- Each `prompt_zh` is for review and must not introduce details absent from its paired `prompt_en`.
- `references` includes rejected candidates so the operator does not accidentally upload them.
- `parameters.model` defaults to `latest` for every NDC scene. Override it only when the user explicitly requests a specific model for the current job set.
- Keep model selection out of every `prompt_en`; when `model` is `latest`, the operator uses the current latest model shown in the live Midjourney settings.
- `parameters.generation_aspect_ratio` is fixed at `2:1` for every Midjourney scene job. `16:10` and every wider exploration ratio belong only to the post-MJ canvas plan.
- Day/night variants share one geometry master by default. Use `time_variant_plan.method: Photoshop manual relighting`; do not request separate MJ generations unless the user explicitly overrides this production rule.
- `review_priority` may be reordered for a special scene.
- `iteration_budget_per_view` counts the initial generation for each view and defaults to three unless the user sets another limit.

If no reference image is supplied, use `references: []`. If the original requirement is stored in a file, include the relevant text and optionally identify the source path under `scene`; do not hand the operator only a path it may not be able to interpret.
