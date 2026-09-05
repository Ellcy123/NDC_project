# Expression delivery receipt schema 12

Create one receipt per character and profile. Formal delivery is fail-closed.

## Required shape

```json
{
  "schema_version": 12,
  "artifact_class": "PROFILE_DELIVERY_RECEIPT",
  "character_id": "stable_character_id",
  "profile": "transparent",
  "profile_spec": {"canvas": [1164, 916], "mode": "RGBA", "background": "alpha_0"},
  "portrait_source": {
    "path": "{JOB_PAYLOAD}/approved-portrait.png",
    "sha256": "64-lowercase-hex",
    "authority": "USER_CONFIRMED_COMPLETED_PORTRAIT",
    "portrait_completion_used": false,
    "status": "PASS"
  },
  "expression_manifest": "{JOB_PAYLOAD}/expression-job.json",
  "approved_asset_census": "{JOB_PAYLOAD}/approved-expression-census.json",
  "expressions": [
    {
      "expression_id": "calm",
      "profile_asset": "{JOB_PAYLOAD}/transparent/character_calm.png",
      "profile_asset_sha256": "64-lowercase-hex",
      "native_rgba": "{JOB_PAYLOAD}/native/character_calm.png",
      "native_rgba_sha256": "64-lowercase-hex",
      "manual_alpha_return": {
        "method": "USER_RETURNED_MANUAL_BACKGROUND_PROCESSING",
        "processor_authority": "USER_MANUAL_BACKGROUND_PROCESSING",
        "handoff_edit_mode": "IN_PLACE_OVERWRITE",
        "codex_background_removal_used": false,
        "user_returned": true,
        "handoff_source": {
          "path": "{JOB_PAYLOAD}/pre-alpha/character_calm.png",
          "sha256": "64-lowercase-hex"
        },
        "returned_native": {
          "path": "{JOB_PAYLOAD}/native/character_calm.png",
          "sha256": "64-lowercase-hex"
        },
        "handoff_manifest": "{JOB_PAYLOAD}/pre-alpha/handoff-manifest.json",
        "edge_review": "{JOB_PAYLOAD}/qa/alpha-edge-review.json",
        "protected_white_status": "PASS",
        "white_fringe_status": "PASS",
        "formal_status": "PASS"
      },
      "artistic_status": "PASS",
      "identity_status": "PASS",
      "viewpoint_status": "PASS",
      "style_status": "PASS",
      "texture_status": "PASS",
      "detail_lighting_status": "PASS",
      "expression_status": "PASS",
      "profile_status": "PASS",
      "cross_profile_source_audit": "{JOB_PAYLOAD}/qa/cross-profile.json",
      "profile_guide_review": "{JOB_PAYLOAD}/qa/profile-guide.json",
      "mechanical_audit": "{JOB_PAYLOAD}/qa/mechanical.json"
    }
  ],
  "continuity_review": {
    "whole_set_checked": true,
    "identity": "PASS",
    "viewpoint": "PASS",
    "style_texture": "PASS",
    "detail_lighting": "PASS",
    "expression_separability": "PASS",
    "thumbnail_readability": "PASS",
    "geometry": "PASS"
  },
  "final_status": "FORMAL_PASS"
}
```

## Validation rules

- `schema_version=12` and `profile` is exactly `transparent` or `greenscreen`.
- Profile specification is exact: transparent `1164x916 RGBA/alpha_0` unless explicitly marked legacy `1152x900`; greenscreen `1536x1024 RGB/#00FF2B`.
- Portrait authority is `USER_CONFIRMED_COMPLETED_PORTRAIT`, current hash matches, `portrait_completion_used=false`, and status is PASS.
- Every expression has one existing RGBA native source and one existing profile asset with matching current SHA-256 values.
- Manual-Alpha return method is exactly `USER_RETURNED_MANUAL_BACKGROUND_PROCESSING`; processor authority is `USER_MANUAL_BACKGROUND_PROCESSING`, `handoff_edit_mode=IN_PLACE_OVERWRITE`, `codex_background_removal_used=false`, and `user_returned=true`.
- The pre-Alpha handoff source is recorded by its unchanged manifest row, even though the user overwrites the original handoff PNG in place. The handoff manifest, current native RGBA, and Alpha-edge review must exist. The manifest-row hash must match the pre-edit handoff hash; the current-native path/hash must equal `native_rgba`; and protected-white, white-fringe, silhouette, and formal statuses must pass.
- Every artistic and profile gate is PASS.
- Cross-profile audit proves the transparent and greenscreen outputs use the same native RGBA SHA-256.
- Continuity booleans/statuses all pass and `final_status=FORMAL_PASS` only when no blocking field remains.
