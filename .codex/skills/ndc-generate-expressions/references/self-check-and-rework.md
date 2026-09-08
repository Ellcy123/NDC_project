# Self-check and bounded rework

The manual-only repair ownership and retry rules below apply to default `USER_MANUAL` mode. For explicit PS MCP authorization, use `photoshop-background-processing.md` for the alternate ownership, trial budget and missing-capability stop. The artistic, source-preservation and Alpha gates are unchanged.

## Gate order

1. `APPROVED_ASSET_CENSUS_AND_DELTA_GATE`
2. `PORTRAIT_SOURCE_LOCK_GATE`
3. `PORTRAIT_COMPLETION_USED_FALSE_GATE`
4. `IDENTITY_CONTINUITY_GATE`
5. `VIEWPOINT_CONTINUITY_GATE`
6. `EXPRESSION_SEMANTIC_GATE`
7. `EXPRESSION_SIGNAL_COMPLETENESS_GATE`
8. `CALM_SEPARATION_GATE`
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

For new/replacement art, use `identity-and-expression-calibration.md` for the concrete face, calm-contrast, gaze and anonymous-thumbnail checks. User rejection supersedes the affected prior PASS; keep accepted siblings and bind every subsequent step to the current manifest revision.

## Key decisions

- A known portrait needing missing subject regions for the requested crop enters `WAITING_FOR_MANUAL_PORTRAIT_COMPLETION`; use `manual-portrait-source.md`. Missing, unapproved or identity-ambiguous sources return `UPSTREAM_PORTRAIT_REQUIRED`. This Skill never completes either source.
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

Persist these counters per stable character/expression and, for P1/P2, per profile in `production-record.md`. A1/A2/A3 includes the initial generation; changing prompts, filenames, handoff segments or conversations does not restart it. Manual portrait completion and waiting for a source/Alpha return spend no generation attempt. A user Alpha revision is a new inspection of returned bytes, not a Codex artistic retry. Exhaustion leaves the affected item pending with its defects; continue unrelated work without replacing accepted siblings.

No retry may introduce portrait completion, generative background removal, or profile-specific artistic generation.

## Release rule

Counts, dimensions, hashes, or a successful copy prove inventory only. Formal release needs a current evidence-registry row for every required asset and `RELEASE_STATUS: PASS`.
