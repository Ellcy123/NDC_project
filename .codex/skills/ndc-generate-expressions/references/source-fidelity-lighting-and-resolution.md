# Source fidelity, lighting topology, and resolution

The approved portrait is the source authority and calm. This Skill does not create a completed master or synthesize missing geometry.

## Native-detail budget

Before generation, record portrait dimensions and face/head pixel height against the largest delivery demand. Generated native candidates and user-returned edge-passing RGBA sources must support delivery with `0 < scale <= 1.0`. DPI metadata, sharpening, AI upscaling, texture overlays, or repeated resizing cannot create approved detail.

## Source-detail gate

Compare approved portrait, raw generated candidate, user-returned edge-passing RGBA, and final profile output at whole-image scale, native 100%, and nearest 200%. Check face/eyes, hair or hat, costume, and identity-critical details. Stable regions must retain the approved line, brush, texture, and material language.

The user's manual background processing may change only Alpha and partial-Alpha matte-contaminated RGB. Codex performs review only and must not repair the returned Alpha. Opaque subject-interior pixels must remain byte-identical to the accepted artistic candidate unless a separately documented semantic color correction occurred before the `PRE_ALPHA_HANDOFF`.

## Lighting topology

Preserve key-light direction and stable cast/occlusion shadows. For hats, keep the underside of the brim and forehead/eye-socket region in the same continuous shadow family. Reject new fill light, rim light, glow, or a bright strip below the brim.

Lighting or detail failure returns to generation from the approved portrait. Do not repair it with global darkening, sharpening, or profile composition.
