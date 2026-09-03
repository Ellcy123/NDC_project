# Self-check and bounded rework

## Gate order

1. `APPROVED_ASSET_CENSUS_AND_DELTA_GATE`
2. `PORTRAIT_SOURCE_LOCK_GATE`
3. `PORTRAIT_COMPLETION_USED_FALSE_GATE`
4. `EXPRESSION_SEMANTIC_GATE`
5. `EXPRESSION_SIGNAL_COMPLETENESS_GATE`
6. `CALM_SEPARATION_GATE`
7. `IDENTITY_CONTINUITY_GATE`
8. `VIEWPOINT_CONTINUITY_GATE`
9. `STYLE_LOCK_GATE`
10. `TEXTURE_COHERENCE_GATE`
11. `SOURCE_DETAIL_PRESERVATION_GATE`
12. `LIGHTING_TOPOLOGY_GATE`
13. `SEMANTIC_COLOR_GATE`
14. `PRE_ALPHA_HANDOFF_COMPLETENESS_GATE`
15. `USER_RETURNED_RGBA_INGEST_GATE`
16. `ALPHA_EDGE_GATE`
17. `NO_UPSCALE_SINGLE_RESAMPLE_GATE`
18. `CROSS_PROFILE_NATIVE_SOURCE_GATE`
19. `PROFILE_GUIDE_GATE`
20. `BACKGROUND_ALPHA_GATE`
21. `PAIRWISE_EXPRESSION_SEPARABILITY_GATE`
22. `THUMBNAIL_READABILITY_GATE`
23. `SET_CONTINUITY_GATE`
24. `RECEIPT_GATE`

Stop at the first failure and return to its owner state.

## Key decisions

- An incomplete or unusable portrait returns `UPSTREAM_PORTRAIT_REQUIRED`. This Skill never repairs it.
- Wrong expression, identity, viewpoint, costume, lighting, style, texture, or detail returns to generation from the approved portrait.
- Color-only drift may use reviewed semantic Photoshop masks; never use an Image model for color correction.
- After artistic review, Codex makes an unchanged non-final pre-Alpha handoff and stops. It never removes the background or white fringe.
- Missing, ambiguous, renamed, resized, cropped, or artistically altered in-place handoff edits are `USER_ALPHA_RETURN_INVALID`.
- An in-place Alpha or edge failure is `USER_ALPHA_REWORK_REQUIRED`. Codex preserves the candidate and asks the user to revise it in place, without Photoshop, scripts, or Image-model repair.
- A white halo, gray matte, colored fringe, hole, remote island, or protected-white erosion blocks both profile branches.
- Profile canvas, placement, or background failure returns only to same-profile composition from the unchanged edge-passing RGBA.
- Cross-profile native hash mismatch returns to the shared RGBA freeze point.
- Readability failure regenerates only the failing state from the approved portrait.

## Retry budgets

- artistic generation: A1, A2 targeted, A3 final;
- pre-Alpha handoff: H1 complete package, H2 inventory-only correction when a file or manifest row is missing;
- user-edited Alpha: no Codex repair retry; each user-confirmed in-place revision starts a new review attempt;
- profile composition: P1 initial, P2 measured correction.

No retry may introduce portrait completion, generative background removal, or profile-specific artistic generation.

## Release rule

Counts, dimensions, hashes, or a successful copy prove inventory only. Formal release needs a current evidence-registry row for every required asset and `RELEASE_STATUS: PASS`.
