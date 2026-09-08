# `ndc-mj-scene/v4` handoff contract

Read the [canonical v4 handoff contract](../../ndc-scene-to-mj-prompt/references/handoff-schema.md). This path remains a compatibility entry for existing callers; the schema is maintained once in the prompt Skill. That Skill is already required for prompt preparation and the shared original-pixel tile helper. If unavailable, restore the declared dependency before accepting a handoff; do not invent or maintain a second schema.

The v4 payload remains compatible. Scene inventory, job continuation and evidence bindings use this Skill's [production record](production-record.md), not unversioned extra mandatory handoff fields.
