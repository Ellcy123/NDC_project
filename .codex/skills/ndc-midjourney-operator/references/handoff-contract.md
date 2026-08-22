# Accepted NDC scene handoff

Accept `handoff_version: ndc-mj-scene/v3` with these required payloads:

```yaml
handoff_version: ndc-mj-scene/v3
scene:
  id: "optional"
  name: "scene name"
  purpose: "scene background"
  mode: "exploration | non_exploration"
  canvas_use: "primary_exploration | story_progression"
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
layer_plan:
  base_environment_narrative: []
  interaction_closeup: []
  scan_overlay: []
  collectible_layer: []
  transient_story_layer: []
view_prompts:
  - id: "eye_level | frontal | oblique | overhead_45"
    label_zh: ""
    camera_contract:
      view_direction: ""
      perspective: ""
      camera_height: ""
      horizon: ""
      pitch: ""
      scale_calibration: []
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
  generation_aspect_ratio: "2:1"
  model: "latest"
  other: []
canvas_plan:
  final_delivery: "story_frame | horizontal_pan_scene"
  final_size: "known dimensions or unresolved pending UI/delivery spec"
  post_mj_operation: "crop_or_reframe_to_16_10 | extend_horizontally | none"
  crop_safe_area: "required content that must survive the post-MJ crop, or not_applicable"
  central_safe_area: ""
  left_extension: "none | Photoshop Firefly extension brief"
  right_extension: "none | Photoshop Firefly extension brief"
  pan_readability: "not_applicable | required"
time_variant_plan:
  geometry_lock: true
  master_time: "the one Midjourney generation lighting state"
  variants: []
  method: "Photoshop manual relighting"
postprocess_handoff:
  photoshop_firefly: []
  photoshop_relighting: []
  removable_layers: []
review_priority: []
assumptions: []
operator_notes:
  iteration_budget_per_view: 3
  preferred_action: "submit-required-view-set-review-and-report-photoshop-handoff"
```

## Validation

- Reject a packet that has prompts but no requirements, or requirements without the complete required view set.
- `scene.mode: exploration` requires exactly one `eye_level` entry. Require eye-level three-point perspective, an optical center about `1.7–1.8 m` above the floor, and a horizon near the upper third.
- `scene.mode: non_exploration` requires `frontal`, `oblique`, and `overhead_45` in that order. The overhead view must look downward about 45 degrees.
- Reject any prompt that requests multiple views, a contact sheet, split panels, or a collage in one image.
- Require `visual_brief`, `camera_contract`, `scene_description`, `layer_plan`, `canvas_plan`, and `time_variant_plan`.
- Treat each `prompt_en` as exact for that view's first submission.
- Do not submit `ndc-mj-scene/v1` or `v2` directly. Migrate it through `ndc-scene-to-mj-prompt`.
- The generated base must be character-free. Reject positive prompt language for people, characters, bodies, corpses, occupations, poses, silhouettes, or character actions. Allow these tokens only in one dedicated final `--no` parameter.
- Calibrate human scale with architectural facts such as door height, handrail height, desk height, window-sill height, and stair proportions. A temporary neutral silhouette may be overlaid only after generation for review; do not upload it, prompt it, or retain it in the asset.
- Only permanent environmental narrative may be baked into the base. Keep interaction close-ups, scan overlays, collectibles, plot items that may disappear, characters, bodies, and Loop-specific changes in removable layers or separate assets.
- Every Midjourney scene job uses fixed `generation_aspect_ratio: 2:1`; scene use cannot override it.
- `story_progression` requires a post-MJ crop/reframe to `16:10` with all required content inside the crop-safe area.
- `primary_exploration` requires a stable central safe area and any post-MJ left/right Photoshop Firefly extension briefs for a pannable final canvas. If delivery width is unknown, report it as unresolved without changing the MJ ratio.
- Generate one geometry master for day/night variants. Do not send separate same-space day/night jobs by default; hand off manual Photoshop relighting while locking composition and spatial structure.
- Shared scene identity, architecture, core permanent objects, lighting state, exclusions, and rendering language must not drift across required Midjourney views.
- Do not reinterpret `soft` or `flexible` counts as hard.
- Do not upload `status: reject` references. If a `use` reference lacks a role, stop and classify it.
- Default `parameters.model` to `latest`. Select and verify the current latest model in the live UI; never add a fixed model-version parameter unless the current user explicitly requests one.
- Count each view's initial grid as round 1 for that view.

Extra source paths or notes do not replace the required fields.
