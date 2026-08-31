# Image generation prompts

Built-in ImageGen was used for both generated semantic masters.

## Type 7 open locker master

Reference inputs: the approved SC4026 scene and the pixel-exact closed 214 locker crop.

Prompt intent: create one independently authored, near-front open 1920s station locker matching the source material, construction and lighting; show one tied kraft-paper packet on the lower shelf; keep all evidence text unreadable; omit people, UI and borders.

Targeted correction: the first candidate opened toward the wrong side. The accepted revision preserves the scene reference's physical hardware by placing hinges on the right jamb, swinging the door to the left, keeping the lock on the free left edge, and rendering `214` upright exactly once.

## 4320 blank evidence master

Reference input: the accepted Type 7 open-locker view.

Prompt intent: create the same tied kraft-paper packet as a transparent standalone evidence object, partly opened with a clean blank main sheet for deterministic exact-text compositing; preserve period paper, cotton string and NDC painted-noir style; omit all generated writing, shadows, UI and background.

## Background extraction correction

Reference input: the accepted blank evidence master.

Prompt intent: replace only the baked checkerboard with genuine transparent alpha while preserving the packet, pages, string, material, lighting, framing and blank page exactly.
