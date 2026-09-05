# Coordinate-bearing hotspot semantic review

Read this before creating or accepting any exploration Map, Type 6 container entrance, or clickable child inside Type 7. This gate decides what the player is being told can be clicked; pixel provenance alone cannot answer that question.

## One target, one record

Write one passing `ndc-stage-visual-self-check/v1` record for exactly one coordinate-bearing PNG. Do not group several Maps or Type 6 sprites into one PASS record. Set `role` to a clear hotspot role such as `scene_pickup_map`, `container_type6`, or `container_child_map` so the validator applies this gate.

The record must contain these view kinds in addition to the normal whole/local views:

- `alpha_only`: white target Alpha on black, at native scale or nearest-neighbor enlargement.
- `checkerboard`: the exported RGBA over a high-contrast checkerboard; inspect every visible plane and edge.
- `parent_overlay`: the Alpha boundary over the untinted accepted parent. Do not use an opaque color wash that hides source details.

Viewing a transparent PNG only against the app's black background is insufficient. Black may be a real dark object, transparent negative space, or missing Alpha; the three views above must disambiguate it.

## Semantic inventory before tracing

Write `target_identity` and enumerate every intended `target_components` before drawing Alpha. For a compound clue, list each complete physical object separately—for example, `funeral register`, `1919 envelope`, and `supporting document`. For planar objects, include every visible face, thickness edge, curled edge, and attributable shadow.

First establish a loose inspection selection and pass the whole/local pre-extrema coverage gate for the complete body-plus-shadow union. Only then mark the top, bottom, left, and right semantic extrema independently on the accepted parent. Then inspect the base contour and final expanded/excluded contour against that inventory. A crop may be technically inside the parent while still missing a page corner, photo edge, drawer face, or visible thickness plane.

Do not use a bounding rectangle or convex hull to join separate target objects when it captures the box, album page, tabletop, cabinet, or other background between them. Use concave paths or multiple Alpha islands. Multi-island Alpha is valid; unrelated bridge pixels are not.

## Transparent negative-space audit

Every internal or between-island transparent region must be classified:

- intentional physical separation between distinct target objects;
- a genuine hole/opening in the target;
- foreground occlusion removed from the target;
- failure caused by an incomplete mask.

Only the first three may pass, and each must be described in `transparent_negative_spaces` with `location`, `physical_reason`, and `intentionally_transparent: true`. A large unexplained black/transparent notch through a paper, photograph, tag, drawer face, or other continuous surface is a missing-target failure.

## Adjacent interactive-unit isolation

For Type 6 and any hotspot beside another plausible interactive object, set `adjacent_interactables_present: true` and list each neighbor in `excluded_adjacent_interactables`.

Examples:

- an upper drawer beside or directly above another drawer;
- two cabinet doors sharing a stile;
- a box touching another box in a stack;
- a photograph mounted on an album page;
- a letter beside other independently collectible papers.

The parent overlay must show every listed neighbor as Alpha 0. A target drawer includes its own front, handle, bounding seams, visible thickness/opening plane when applicable, and attributable shadow. It excludes the neighboring drawer's face, handle, interior seam area, and cabinet body. If the Type 7 shows the top drawer opening, the Type 6 may not select a lower drawer merely because both fit in one crop.

## Required passing criteria

All of the following criteria must be present, applicable, and PASS:

- `semantic_target_completeness`
- `transparent_negative_space_justification`
- `unrelated_parent_pixel_exclusion`
- `adjacent_interactable_exclusion`
- `click_mislead_risk`
- `parent_overlay_semantic_alignment`

The passing record also needs:

```json
{
  "hotspot_visual_context": {
    "target_identity": "complete physical target",
    "target_components": ["named component"],
    "semantic_extrema_confirmed": true,
    "complete_visible_planes_confirmed": true,
    "missing_target_pixels": false,
    "unrelated_parent_pixels": false,
    "click_mislead_risk": "none",
    "alpha_only_reviewed": true,
    "checkerboard_reviewed": true,
    "parent_overlay_reviewed": true,
    "transparent_negative_spaces": [],
    "adjacent_interactables_present": false,
    "excluded_adjacent_interactables": [],
    "adjacent_interactables_alpha_zero": false
  }
}
```

When adjacent interactables are present, `excluded_adjacent_interactables` must be non-empty and `adjacent_interactables_alpha_zero` must be `true`.

## Pass boundary

Reject and return to mask authoring when any of these is visible:

- any missing portion of a continuous target surface;
- an unexplained transparent hole or notch;
- container/page/table/cabinet pixels used to connect separate target objects;
- another drawer, door, box, pocket, or collectible partly inside Alpha;
- an edge that would make a player reasonably believe a neighboring object also opens;
- a visual conclusion based only on hashes, coordinates, parent-pixel equality, or the absence of an obvious seam.

After correction, regenerate all dependent coordinates, hashes, manifests, formal copies, and `XYposition.txt` entries. The rejected PASS record stays in history and must not cover the new bytes.
