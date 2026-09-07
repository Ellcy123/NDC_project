# `ndc-mj-scene/v4` handoff contract

Use the following shared contract. Values are descriptive examples, not ready-to-submit scene facts. Version 4 replaces v3's mandatory postproduction and per-prop layer planning with an MJ endpoint and default prop deferral.

```yaml
handoff_version: ndc-mj-scene/v4
workflow_end_stage: mj_image_delivery
scene:
  id: "scene or asset id"
  name: "scene name"
  mode: "exploration | non_exploration"
  canvas_use: "primary_exploration | story_progression"
original_requirement: |
  Relevant source text and current user corrections, with source paths.
visual_brief:
  time: "requested master time/state"
  interior_exterior: "interior | exterior | mixed"
  architectural_function: "room or place function"
  visual_facts: ["source-supported architecture, main furniture, broad surface state"]
  removed_nonvisual_facts: ["character actions or nonvisual story"]
prop_policy:
  mode: defer_gameplay_props
  ambient_dressing: sparse_period_appropriate_noninteractive
  retained_spatial_masses: ["architecture, structural fixture or room-defining major furniture"]
  deferred_from_source: ["source-defined gameplay or environmental-narrative props omitted from MJ; no location planning required"]
  explicit_mj_exceptions: []
normalized_requirement:
  hard: ["empty environment with no visible characters", "scene and camera obligations"]
  soft: ["period material and lighting"]
  flexible: ["harmless architectural detail", "sparse ordinary period ambient dressing"]
  must_not_have: ["people, named characters, crowds, human figures, faces, bodies, silhouettes", "scene-specific structural failures"]
texture_contract:
  style_authority_locked: true
  approved_style_authority: ["inspected reference or current user instruction"]
  immutable_style_traits: ["palette, line hierarchy, grouped shadows, brush and edge language"]
  focal_detail_zones: ["current scene's required focal structures"]
  secondary_detail_zones: ["supporting structure"]
  quiet_zones: ["source-appropriate broad supporting planes"]
  distant_zones: ["receding value groups"]
  material_texture_rules: ["material direction, scale, density, continuity and depth response"]
  prohibited_artifacts: ["nonsemantic microdetail, repeated stamps and fragmented noise"]
  style_changing_cleanup_language_forbidden: true
view_prompts:
  - id: eye_level
    label_zh: "平视搜证视角"
    camera_contract:
      position: "camera location derived from the current scene requirement"
      view_direction: "viewing direction and visible spatial relationships for this view"
      perspective: "three-point perspective for exploration"
      camera_height: "1.7–1.8 meters for exploration"
      horizon: "upper third for exploration"
      pitch: "eye-level; approximately 45-degree downward only for overhead_45"
      scale_calibration: ["visible architectural landmarks"]
    scene_description:
      viewpoint_change: "none or source-view rotation/elevation"
      foreground: "source-appropriate near elements for this view"
      middle_ground: "main masses and spatial relationships for this view"
      background: "source-appropriate distant elements for this view"
      lateral_layout: "left, center and right main masses"
      architecture_relations: ["connection, route, occlusion and relative scale"]
      camera_calibration: ["observable camera evidence"]
    prompt_en: "Exact English submission, --ar 2:1 once and final character --no parameter"
    prompt_zh: "Faithful Chinese review counterpart, including exclusions"
references:
  - file: "absolute local file"
    role: "style | environment | composition | identity | reject"
    status: "use | reject"
    reason: "role and semantic leakage boundary"
parameters:
  generation_aspect_ratio: "2:1"
  model: latest
  quality: hd_if_available
  other: []
framing_context:
  central_readability: "the current scene's required focal elements and spatial relationships remain readable"
  known_later_display_constraint: null
  edge_continuity: "coherent broad planes, without forced prop zones"
master_state: "the one requested time/state; no automatic alternate MJ geometry"
delivery_contract:
  artifact: native_mj_image
  preserve_original_pixels: true
  record_actual_dimensions: true
  include: ["selected native file", "exact prompt and settings", "job identity", "candidate review", "visual and texture records"]
review_priority: [camera_and_layout, architecture_and_routes, empty_background, style_and_texture, editing_convenience]
assumptions: []
operator_notes:
  iteration_budget_per_view: 3
  preferred_action: submit_review_iterate_deliver_native_mj
```

## Required interpretation

- `exploration` is based on gameplay and requires only `eye_level`. `non_exploration` requires `frontal`, `oblique`, `overhead_45` in that order, each an independent job. The YAML above shows only the exploration example.
- First-round English text is exact; Chinese text must not introduce extra objects. Keep people only in the final single `--no` parameter. Keep model selection out of prompt text; always `--ar 2:1` once.
- `deferred_from_source` preserves omitted facts only; it is not a to-do list, prompt content, negative inventory or required placement map. Missing deferred objects cannot fail the grid. The original requirement may mention them without granting MJ inclusion.
- Both mandatory saved static references remain Style References. Additional references preserve their declared roles. Do not add deferred-prop identity images.
- Final game width, 16:10 crop, horizontal extension, alternate lighting and prop implementation do not block this MJ delivery. `framing_context` carries only already-known composition constraints, without requesting follow-up operations.
- No required `layer_plan`, `canvas_plan`, `time_variant_plan` or `postprocess_handoff` in v4. For older handoffs, preserve sources and valid camera/style clauses, defer game-defined props except current user-explicit MJ inclusions, retain optional sparse ordinary ambient dressing, replace those fields, and record migration before submission. Do not silently reinterpret an old exact prompt.
- Actual native dimensions and file checksums must be measured after download. HD selected in the UI is not proof of delivered dimensions or readable detail.
- Delivery means MJ source output available for user editing; it does not claim a finished Unity background. Unresolved hard failures remain work-process candidates after the finite budget.
