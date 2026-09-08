# Manual portrait source completion and return

Use this intake branch only when an otherwise identified portrait lacks subject regions required by the requested expression/profile crop. A cropped shoulder can be valid for the general portrait deliverable; do not retroactively reject that deliverable. This workflow intentionally relies on human completion. Do not add an automatic completion Skill, spend an A1/A2/A3 attempt, or turn PS Alpha-trial authorization into permission to fill shoulders.

## Handoff before E0/E1 acceptance

Record `WAITING_FOR_MANUAL_PORTRAIT_COMPLETION` in the job's production record, with the affected character and requested profiles. Preserve the approved source path/hash and identity authority. Give the human a concrete brief: which shoulder, chest, costume or contour is missing; the required framing/guide coverage and resolution; the approved face, viewpoint, lighting and clothing to preserve; and the file to return. Do not claim human work is finished from a changed file timestamp. Continue unrelated accepted characters while this character waits.

This handoff is source preparation, not `PRE_ALPHA_HANDOFF`. Keep a source-return record containing the original source path/hash, returned path/hash, manual completion confirmation, intended use and actual identity/structure review. Do not reuse E5 handoff IDs or fabricate `manual_alpha_return` fields. The returned portrait need not be an Alpha-processed expression set.

## Accept the manual return

After the human identifies the completed source, verify the character mapping, approved identity, applicable expression/profile framing, complete required subject regions, viewpoint, costume, light and image readability. Bind the review to the actual returned bytes. If it is still missing required regions, keep the manual waiting status and state the remaining repair; if identity/approval is unresolved, use `UPSTREAM_PORTRAIT_REQUIRED`. A hash change proves a new version, not visual acceptance.

Once accepted, refresh only the affected E0 census/mapping and E1 source lock, then continue from the first invalidated state. Freeze this source as calm; all new non-calm expressions start from it. Preserve earlier accepted work as history. Changing the source invalidates only assets actually dependent on that source, not unrelated approved historical expressions or other characters.

The legacy receipt field `portrait_completion_used=false` records that this Skill did not perform completion. It does not erase the upstream human operation: link the separate source-return provenance from the production record. The later E5/E6 manual background handoff has its own exact-file manifest, confirmation and Alpha receipt and is still required when applicable.
