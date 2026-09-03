# Profile guides and source-integrity gate

The approved portrait set is already completed upstream. This Skill checks source integrity but never adds or reconstructs a missing region.

## Source lock

At `E1_PORTRAIT_SOURCE_LOCK`, record:

- approved portrait path and SHA-256;
- user-confirmed status;
- `portrait_completion_used=false`;
- visible head/hair-or-hat, shoulders, chest/costume exit, and intended crop;
- protected light regions;
- viewpoint family and source dimensions.

If the portrait cannot support the requested expression/profile framing, return `UPSTREAM_PORTRAIT_REQUIRED`. Do not outpaint, extend, patch, or relax the guide.

## Greenscreen guide, 1536 x 1024

- hair/hat-inclusive top must not cross the guide band `y=36..39`;
- chin must not fall below `y=697..699`;
- character center axis aligns with `x=755..758`;
- subject reaches the bottom naturally;
- the complete visible silhouette remains intact.

## Transparent guide, 1164 x 916

- skull top excluding hair/hat must not cross `y=120..125`;
- chin must not fall below `y=631..636`;
- average eye line targets `y=374..377`, operational tolerance `+/-10 px`;
- cheek contours excluding ears/hair/hat stay between centers `x=419.5` and `x=722.5`;
- blue `x=566.5` is visual guidance, not a hard gate;
- subject reaches the bottom naturally and Alpha remains clean.

Use one calm-locked transform for the complete same-character, same-profile set. If an expression crosses a guide, revise one shared transform for the whole set or regenerate the expression from the portrait when its pose is wrong. Never fit each expression independently.

`prepare_profile_guide_review.py` creates evidence only. Codex must inspect the whole output and set `visual_status` and `formal_status`; automatic landmarks cannot approve a profile.
