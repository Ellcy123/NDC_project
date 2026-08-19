# Classification and edit contract

## Core distinction

Classify an object by its role in the scene and workflow, not by its physical type.

- Environmental infrastructure establishes how the place functions and normally remains.
- Environmental storytelling establishes what kind of place or moment this is and remains only when the current scene requirement needs it.
- Content props carry evidence, text, identity, interaction payload, or later placement and normally leave the clean plate.

## Classification matrix

### KEEP_STRUCTURE

- Walls, floor, ceiling, doors, windows, molding, columns, stairs, room dividers
- Built-in cabinetry, counters, shelving, plumbing, radiators, fixed wiring
- Large furniture that defines navigation or gameplay layout
- Existing openings, drawer/cabinet shells, and their source-specified open/closed state

### KEEP_ENVIRONMENT

- Lamps and practical fixtures
- Wall or desk telephones and other period infrastructure
- Curtains, blinds, rugs, clocks, mirrors without portraits, plain frames
- Sinks, stoves, heaters, ordinary cookware required to read the room's function
- Tables, chairs, beds, daybeds, folded cots, desks, cabinets, coat hooks
- A restrained amount of scene-defining ordinary life: moving boxes during a move, shoe-repair tools in a cobbler's home, filing furniture in an archive
- Natural wear, dust, stains, creases, surface scratches, and non-symbolic material detail

### REMOVE_CONTENT

- Evidence and all objects intended for a later evidence-placement pass
- Letters, photographs, albums, books, ledgers, forms, newspapers, loose files, notes, cards
- Readable posters, signs, labels, signatures, logos, seals, badges, portraits, names, numbers
- Weapons, blood, suspicious traces, marked containers, unique tokens, clue-specific clothing contents
- Decorative objects not needed for scene identity, especially when they compete with planned interaction points
- Repeated or excessive small objects that make every surface look searchable

### REVIEW

- A movable object that may be either ordinary life or a planned interaction target
- A container whose existence is necessary but whose contents may be evidence
- A picture frame that may be a neutral decoration or a clue-bearing portrait
- A garment that defines ordinary occupancy but may contain a clue
- Boxes, parcels, wastebaskets, or piles whose quantity affects narrative state

Resolve `REVIEW` from the current scene requirement. If still ambiguous, preserve the shell and remove readable or clue-bearing contents.

## Container rule

Prefer `keep container, remove payload`:

- Keep the dresser and slightly open drawer; remove the album or photograph inside.
- Keep the half-open moving carton when the move is scene-defining; remove the funeral booklet, letter, or marked object inside.
- Keep the coat on a wall hook when it establishes occupancy; remove the token or evidence from its pocket.
- Keep the letter rack as furniture; remove the unique unsent note and readable envelopes.

## Visual invariants

Treat the following as hard locks unless the user explicitly authorizes change:

1. Pixel dimensions and aspect ratio
2. Crop, camera position, camera height, lens feel, and perspective
3. Architecture, large furniture, walkable routes, and object scale
4. Key-light direction, window light, practical-light state, intensity, penumbra, and cast shadows
5. Reflections, specular highlights, ambient occlusion, and bounced-light color
6. Palette, color grade, contrast, saturation, line weight, brush texture, and stylization
7. Period identity, surface age, dust, wear, and material roughness

## Position language

Name removals precisely:

- Use `left foreground wall`, `center desk surface`, `rear-right window sill`, or `second drawer from top`.
- Identify the object by color, size, and neighboring landmark.
- When several objects overlap, state which silhouette must remain.
- Do not say only `remove clutter`; enumerate the intended removals.

## Failure handling

- Local inpainting defect: repair the single named patch on the accepted result.
- Missing retained object: return to the original image and repeat with that object explicitly locked.
- Global relighting, recoloring, or restyling: discard the result and retry from the original with fewer removal targets.
- Large number of removals: split the work into spatial passes while reusing the original image whenever a pass drifts globally.

## Example: newly occupied apartment

Keep the wall telephone, lamps, narrow table, stove, sink, beds, curtain, collapsed cot, cabinets, and a restrained number of moving boxes. Keep the box and drawer states. Remove the album, old photograph, funeral booklet, letters, clue token, unsent note, readable leaflets, and unnecessary tabletop decoration. Reconstruct only the exposed drawer interior, box interior, tabletop, or wall surface while preserving the original window light and furniture shadows.
