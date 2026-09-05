# Story-driven irregular panel shapes

Panel geometry is art direction. Choose it from the event's focal relationship, motion, and intended screen placement. Every family below shapes a local or extreme-local close-up; its aspect ratio never authorizes a wider shot scale. Do not default every event to C01's shallow landscape trapezoid.

## Shape families

| Family | Typical ratio | Best for | Edge logic |
| --- | --- | --- | --- |
| Wide local-action panel | 1.6–2.8 | Two hands, cropped subject-to-prop contact, lateral prop movement, localized environment/action relation | Top and bottom edges lean with the action vector |
| Ultra-wide strip | 2.8–4.0 | Eyes, hands, headlights, letter tear, sudden reveal | Thin height compresses time and isolates one beat |
| Portrait pressure panel | 0.45–0.9 | Face, vertical hand/weapon/suitcase crop, falling limb detail, localized dominance or isolation | Side edges lean toward or away from the pressure source |
| Near-square incident | 0.9–1.4 | Evidence, prop use, compact room event, face-object relation | Mild skew keeps weight without wasting space |
| Directional trapezoid | Any appropriate ratio | Impact, interruption, panic, unstable memory | Narrow side points toward entry, impact, or escape direction |
| Mixed multi-panel sequence | Mixed | Continuous action or emotional reversal | Contrast local action/detail/reaction shapes; share border weight and visual rhythm |

## Normalized starting families

Coordinates are clockwise normalized `(x,y)` values. They are starting families, not finished designs. Move the vertices to protect the actual subject and express the specific event.

- Landscape rising right: `0.02,0.08;0.98,0.02;0.98,0.92;0.02,0.98`
- Landscape falling right: `0.02,0.02;0.98,0.08;0.98,0.98;0.02,0.92`
- Portrait leaning right: `0.05,0.02;0.94,0.08;0.99,0.96;0.12,0.99`
- Portrait leaning left: `0.06,0.08;0.95,0.02;0.88,0.99;0.01,0.94`
- Near-square pressure wedge: `0.03,0.09;0.96,0.02;0.99,0.90;0.12,0.99`
- Ultra-wide directional strip: `0.01,0.15;0.99,0.02;0.96,0.88;0.04,0.99`

Use convex polygons unless a separately approved design requires another deterministic mask. Keep vertices inside the canvas so the full black stroke remains visible.

## Design rules

1. Pick the provisional orientation before generation so the composition reserves useful negative space.
2. Finalize polygon points only after the generated raw art is accepted.
3. Keep faces, hands, weapons, evidence, badges, letters, and action joints at least three border widths inside the crop unless an intentional edge crop has been approved.
4. Aim the dominant diagonal with the action, gaze, interruption, collapse, or escape direction. Do not tilt randomly.
5. Use a restrained skew for quiet information; stronger asymmetry for impact or instability.
6. In a multi-frame event, do not make every panel the same size and direction. Pair localized action with detail or reaction while keeping every frame a local or extreme-local close-up.
7. Across an event batch, explicitly review the orientation distribution. Reject a batch that mechanically repeats one horizontal quadrilateral.
8. Default to a black miter-joined border. `18 px` worked for the 1773×887 C01 experiment; scale approximately with resolution and compare against U1 rather than treating 18 px as universal.
9. Generate magenta-mask and RGBA outputs from the same polygon. Do not redraw the image to change the frame.

## Packaging command

From either configured repository root:

```powershell
python scripts/art_pipeline/ndc_art.py run generate-ndc-emergency-art package_panel.ps1 `
  -InputPath "{JOB_PAYLOAD}/C02_frame01_raw.png" `
  -OutputDirectory "{JOB_PAYLOAD}/final" `
  -BaseName "C02_frame01" `
  -Points "0.05,0.02;0.94,0.08;0.99,0.96;0.12,0.99" `
  -BorderWidth 18
```

The script preserves the input canvas dimensions, clips the art to the polygon, draws the border programmatically, and reports alpha checks and hashes.
