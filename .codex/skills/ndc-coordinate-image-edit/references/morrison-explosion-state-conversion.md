# Morrison explosion aftermath: reference-locked state conversion

Read this reference only for Mode B: an established scene keeps its camera and spatial identity while a connected event changes a large portion of its visible state.

## Evidence and limits

User-approved comparison, 2026-08-24:

- before: `D:\PMH\工作\场景\004第四章\定稿\u4_exp_morrison_service_night_preblast.png`
  - 3164 × 1600 RGB
  - SHA-256 `B5889FCCBE31109AAD078762A8D53108B5506DD534A8AD4D79A9D38C634534FB`
- delivered aftermath: `D:\PMH\工作\场景\004第四章\定稿\u4_exp_morrison_service_night_preblast_BOOM.png`
  - 3164 × 1600 RGB
  - SHA-256 `82655CE4A75CE0D676E90E29AD6E1063A90660C3E2CA62EF4B7F80165E09C427`
- user-provided ChatGPT process record: `https://chatgpt.com/share/6a8bc223-58bc-83ea-b285-b4b29ed692a0`

The share record shows two large semantic edit passes: a kitchen region with the blast source offscreen to the right, followed by the service-passage region with its central access hatch treated as the source. The supplied delivery image is the authoritative result. The exact manual finishing operations between the generated regions and that delivery were not recorded, so do not invent a specific Photoshop procedure.

Direct pixel comparison confirms this is not a small-patch cleanup: about 75.4% of pixels differ by more than 10 channel levels, about 30.4% differ by more than 30, and mean luminance changes from about 32.97 to 16.40. The successful lock is therefore **camera, composition, room topology, landmark identity, and damage causality**, not broad byte identity.

## What the result preserves

- the original 3164 × 1600 canvas and near-2:1 framing;
- the same viewpoint, vanishing structure, wall/floor division, and walkable route;
- the left cabinet and cooking run, rear sink/window zone, central doorway, right meter/valve niche, second window, and right baseboard as recognizable landmarks;
- period, line language, matte painted surface, and large hard-edged value masses.

These are protection classes. They may be scorched, broken, darkened, or partially occluded, but they must remain spatially identifiable unless the user explicitly authorizes their destruction.

## What the result changes coherently

- the ceiling lamp is off and the former warm pool of light is removed;
- both windows are broken and admit cold exterior shafts that help unify the two edited regions;
- cabinets, doors, wall skin, floorboards, and trim are damaged as one pressure-wave event rather than as unrelated dirty patches;
- destruction grows stronger toward the right-side source: lifted floorboards, larger wall loss, deeper soot, and denser debris;
- residual orange embers remain subordinate to the cold darkness and trace combustible wood seams without becoming open flames;
- debris uses broad, readable wood and plaster masses instead of uniform micro-fragments or high-frequency noise.

## Prompt anatomy that produced the useful base

Build the edit request in this order:

1. **Identity lock:** preserve current composition, ratio, and art style.
2. **Event and elapsed state:** identify the room as having undergone an indoor gas explosion and specify whether this is immediate aftermath or later ruins.
3. **Source location:** name an onscreen source or an offscreen direction.
4. **Damage recipients:** explicitly name windows/glass, cabinet or door fronts, floorboards, walls/trim, and any critical utility hardware.
5. **Directional severity:** say that damage intensifies toward the source; do not distribute equal damage everywhere.
6. **Global lighting transition:** switch off the interior practical light and define any exterior light that now enters through destroyed openings.
7. **Residual activity:** keep only weak ember light in damaged wood if required; avoid a fireball or broad active flames unless the story calls for them.
8. **Texture-density controls:** avoid fine fragmented texture, random speckles, and stacked material detail; require hard-edged, broad-brush simplification.
9. **Unchanged-content clause:** keep everything not named unchanged at the level of scene identity and placement.
10. **Style lock:** append the user-approved current style text. The historical prompt in this case is evidence, not a universal style source; do not silently carry obsolete or scene-specific terms into later jobs.

Case prompt body, preserved as evidence:

```text
保留当前构图、比例和美术风格，修改图片：【将图1改为经历了一场室内燃气爆炸后的场景，爆炸源在右侧画面之外；窗户、玻璃完全破碎；柜子柜门大多数遭受强烈损毁；地板被爆炸掀起损毁，越靠近爆炸源的地板损毁越强烈；室内灯关闭；部分木制结构残留微弱火光；避免细碎纹理；避免杂点；避免出现材质过于堆砌细节，保持硬边缘大笔触概括化】没说要修改的内容都保持不变。参考以下风格提示词保持风格统一：【用户当次批准的常驻风格提示词】
```

For the second semantic region, the same structure was retained while changing the source clause to the central access hatch and replacing cabinet damage with door damage.

## Recommended workflow

### 1. Write a spatial-state contract

Before generation, record:

- fixed camera/canvas;
- protected landmark graph;
- event source and direction;
- near/middle/far severity bands;
- global light transition;
- material-specific debris and forbidden additions.

This contract must be derived from the actual before image. Do not describe a generic ruined kitchen and hope it matches later.

### 2. Choose a coherent base-edit scale

Prefer a full-frame reference edit when the model can preserve the source aspect ratio and landmarks. If the input/output limits make that unreliable, split the image into the smallest number of **large semantic regions** that each contain complete architectural relationships. Two overlapping regions were effective in this case: the cooking/window zone and the doorway/service-niche zone.

Context regions may overlap for continuity. Do not divide along the edge of one cabinet, doorway, window, or light beam. Do not create many small object crops before the whole scene has a convincing shared state.

### 3. Generate the base state before local repair

Each region prompt must repeat the same identity lock, elapsed state, damage direction, lighting logic, texture-density controls, and style lock. Change only the local source and named damage recipients. Review the regions together, not as isolated attractive crops.

Reject the base when:

- the room no longer reads as the same location;
- damage has no source gradient;
- one region uses a different exposure, brush scale, soot direction, or debris language;
- destruction reads as old decay rather than the requested event state;
- the result preserves furniture so completely that the stated blast severity is implausible;
- the model fills the scene with tiny noisy fragments.

### 4. Reconstruct the exact delivery canvas

Generation may return a different pixel size even when the ratio is preserved. Restore the original canvas deterministically and keep a record of every scale, crop, translation, overlap, and blend. Never independently stretch width and height. If aspect ratios differ materially, reject the candidate instead of hiding the mismatch.

When two large regions are used, align them by several protected landmarks and long perspective lines, not by one edge. Resolve overlap in a broad, naturally changing surface such as soot falloff or shadow; never leave a straight exposure seam. Recheck the full image after each integration.

### 5. Use coordinate repair only for finishing

After the whole-frame state works, return to Mode A for:

- exact seam cleanup;
- restoring a critical meter, valve, frame, or cabinet line;
- removing duplicated debris or accidental objects;
- repairing local line weight, edge halos, or perspective drift;
- protecting pixels outside the final small correction masks.

Do not attempt to build the primary explosion by accumulating these small repairs.

## Mode B acceptance gate

Deliver only when all of the following pass:

- exact original canvas size and mode;
- same camera, room topology, and principal landmark positions;
- readable source direction and severity gradient;
- one shared elapsed state, exposure system, soot/debris direction, and brush scale;
- material damage appropriate to wood, plaster/tile, glass, and metal;
- no straight crop boundary, rectangular brightness island, duplicated object, or local style island;
- no people, text, modern objects, or other unrequested narrative additions;
- normal-size whole-frame review passes before any pixel-containment report is cited.

For Mode B, do not report `outside_union_pixels_bit_identical` as the primary success metric. Report the protection-map and spatial-identity audit first, then the exact-canvas reconstruction record, then any Mode A containment checks used for finishing.
