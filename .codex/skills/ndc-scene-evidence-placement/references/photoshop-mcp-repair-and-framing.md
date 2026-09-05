# Photoshop MCP repair, framing, and semantic-path workflow

Use this reference whenever Photoshop is involved in evidence placement, Type 6/child Map tracing, or Type 7 reframing.

## Execution boundary and serial gate

- Photoshop operations default to the bridged Photoshop MCP. Do not substitute Computer Use, mouse control, keyboard automation, or screen-coordinate clicking unless the user explicitly authorizes that fallback for the current task.
- Run an MCP capability preflight before editing. Use only commands exposed by the connected Photoshop host. Translation, uniform/non-uniform scale, and rotation may be used when available. Skew, perspective, warp, content-aware operations, or other features may be used only when the MCP capability catalogue exposes them; an unsupported operation is not permission to fall back to mouse control.
- Photoshop MCP is prohibited from creating, inserting, replacing, deleting, typesetting, restyling, painting, or compositing readable prop text. Required titles, dates, numbers, stamps, signatures, ledger entries, and body text must already be present in the accepted image-generation or artist-authored raster master. Missing, wrong, garbled, incomplete, or unreadable text is a semantic failure that returns to image generation; it is never a Photoshop text-repair task.
- For an accepted multi-part Big, prefer a recoverable single-document workflow: make one selection per physical component, cut it to a new layer with the exposed selection-to-new-layer/layer-via-cut command, then transform those layers independently. This is sufficient; do not require a separate multi-document split-and-replace operation. Preserve each component's existing shadow where present. Adding a standardized layer-effect shadow is optional and must never block the composition. When the live catalogue lacks the selection-to-layer command, record `PS_MCP_SELECTION_TO_LAYER_UNAVAILABLE`, retain the master and transform plan, and use the authorized alpha-safe deterministic fallback instead of pretending a Photoshop transform occurred.
- Treat a paired host with `bridge.connected: false` as unavailable: pairing, an installed Photoshop executable, a launched Photoshop process, and local-file whitelisting do not prove that a command can run. Record the host result as `PS_MCP_BRIDGE_DISCONNECTED`, preserve a copied input plus the intended command sequence in a resumable job manifest, complete only unrelated work, then rerun the full capability preflight after the bridge reconnects. Do not issue edit commands or promote a final asset while this condition remains.
- Process one image at a time. Finish the current image, save its new bytes, run technical verification, complete the required whole/local visual self-check, validate the current-hash record, and obtain `PASS` before opening, switching to, modifying, or accepting the next image. Batch-editing several Photoshop documents before the first one passes is forbidden.
- Keep every rejected or superseded version in a clearly marked history directory. Never overwrite the only recoverable prior version.

## Near-success placement rescue order

A candidate is `near_success_transformable` only when its identity, required content, material/style, lighting premise, and support relationship are already correct, while the remaining defect is limited to small position, scale, rotation, or correctable perspective differences. Missing components, wrong identity, wrong state, impossible lighting, broken structure, severe occlusion, or a false support surface are not near-success cases.

Use this order:

1. Preserve the frozen accepted scene and the current candidate. In Photoshop MCP, try the smallest supported transform that can correct the defect: move, scale, rotate, or a capability-confirmed perspective/skew correction. Transform the prop together with its attributable contact/cast shadow and any linked edge treatment; do not transform unrelated scene pixels.
2. Recheck physical scale, perspective, support contact, occlusion, shadow direction/softness, scene lighting, walkable space, and whole-frame coherence. If both technical and visual gates pass, accept the corrected candidate and do not regenerate.
3. If Photoshop cannot perform the required operation through MCP, or the corrected candidate still fails, return to the frozen source and allow exactly one fresh generation attempt at that support location.
4. If that fresh attempt also fails and the workflow reaches this branch again, freeze the location and first seek a different valid independent support. Only when no suitable independent support exists and the acquisition design supports it, identify a genuine source-supported container and route the item through a complete Type 6 -> Type 7 -> contained-item chain. Never expose a corner, enlarge a child above the rim, or use a fake container merely to avoid the chain.

This branch is an earlier stop for a near-success candidate and supersedes the generic three-attempt allowance at that same location. The generic ceiling still applies to other generation failures that were never transformable near-success cases.

Record the defect classification, supported MCP commands, exact transform values, linked layers, before/after hashes, and why the candidate passed or returned to generation/container routing. If perspective/warp is required but unavailable through MCP, record `unsupported_by_current_photoshop_mcp` and continue to the next authorized branch; do not use mouse control silently.

## Type 7 borderless-interior reframing

Use this only when the Type 7 viewpoint, container identity, contained evidence, perspective, light, and source-derived environment are already correct, but irrelevant surrounding environment occupies too much of the secondary view.

1. Start from the approved borderless Type 7 interior. If only a bordered runtime image exists, recover the exact inner rectangle by removing the 12-pixel frame without resampling. Never include the white frame in a transform.
2. In Photoshop MCP, uniformly enlarge and reposition the complete interior composition, then crop/reframe around the actual opened container and its child. Preserve enough local environment to retain scene identity and physical support.
3. Do not distort the container, change camera height, crop away a required container wall/hinge/handle, clip any contained item or its attributable shadow, invent hidden pixels, or magnify a low-resolution source until texture/readability becomes false.
4. Complete whole-image, local-200%, and source-anchor comparison on the final borderless interior. Record scale, translation, crop rectangle, output size, and the reason the removed environment was irrelevant.
5. Only after the borderless interior passes, add the exact opaque 12-pixel white frame. Do not resize, crop, transform, or reframe the bordered result.

Reframing does not change the direct-generation requirement: the opened container, child, light, and environment must still originate together in one accepted Image result. Photoshop may adjust framing; it may not paste a separately generated Big or child into the container.

## Semantic path workflow for Type 6 and child Maps

Before tracing, list the target identity, all physical components, all visible planes/thickness/shadow, intentional negative spaces, foreground occluders, and every adjacent interactable. Judge ownership from structure and material continuity, not from contrast alone.

- Trace the complete physical target boundary. Light/shadow changes, printed content, faces in a photograph, texture changes, and low-contrast edges are not object boundaries by themselves.
- A Type 6 built into furniture includes the complete actionable unit: its front plane, handle, attributable seams/edges, visible thickness, and contact shadow. Neighboring drawers, doors, lace, cabinet faces, or handles remain Alpha zero even when they touch the target.
- A photograph Map includes the complete physical photograph paper and all of its visible corners/edges. Do not crop away people or content near one side merely because the image content is dark or visually dense; do not include the album binding or carrier page.
- A compound evidence item may need a concave union or multiple Alpha islands. Preserve real gaps between components as intentional transparent negative space. Do not replace the semantic shape with a bounding rectangle or convex hull, and do not include underlying container papers to bridge a gap.
- Foreground occlusion subtracts only truly covering pixels. Keep visible target continuation beyond an occluder; never reconstruct hidden parts.

When the user or an artist draws a same-document, same-scale Photoshop Pen path and explicitly identifies it as the correct/final hotspot, treat that native path as the authoritative final semantic contour for that asset. Read and record its path name and geometry through Photoshop MCP, derive Alpha and the tight crop/Position from it, and render Alpha-only, checkerboard, local-200%, and untinted parent-overlay views. Do not simplify, retrace, convexify, or add any further expansion unless the author explicitly says the path is only a pre-expansion base contour. Technical parent-pixel verification is still required, but it cannot replace the visual comparison to the authored path.

Each hotspot remains a separate review unit. Never approve several Map/Type 6 outputs from one shared visual record, and never begin the next Photoshop image before the current path-derived output has passed.
