# Exploration interaction-state assembly

This reference applies to exploration NPCs whose runtime `ResPath` and `ClickResPath` represent click-before and click-after states. Pure narrative actors use the entry/exit directing timeline instead; they do not receive an idle/active pair merely because more actors enter later.

## Single-master rule

The accepted idle state is always the master for runtime position, scale, identity/body proportions, support relationship, canvas, shadow registration, and Photoshop coordinates. It must read as a natural ambient hold that does not already perform to the player. The active state must visibly engage the player.

Author a `stateDeltaScope` before generation. Default to the smallest readable change: attention target, eyes/expression, head angle, upper-torso orientation, or one motivated hand action. Preserve ongoing occupation, named support, social territory, depth, and runtime transform. A whole-body delta requires a recorded interaction reason; it is not the default cure for a stiff idle pose.

Choose one assembly mode before generation:

- `registered-local-patch`: only a constrained region changes; idle pixels outside it remain the master;
- `exact-master-canvas`: a larger authored change remains on the exact master canvas/transform;
- `registered-complete-state`: a complete, coherent full-body pose may change, but it is generated and delivered as one complete state—not spliced—and is registered to the same canvas, scale, support contacts, placement, and shadow logic.

For the after state:

- generate only the allowed change region, or generate on the exact master canvas without recropping;
- reuse the same transform as the before state;
- never normalize each state by its own alpha bounding box;
- never join independently generated full bodies with a straight horizontal waist cut.

In `registered-complete-state`, natural whole-body motion is allowed when the interaction needs it. Feet, seat/bed contacts, or other declared support anchors remain registered within tolerance; alpha support-bottom drift is bounded. Do not force frozen lower-body pixels when that would make the active performance stiff or anatomically broken.

## Freeze and change contracts

For local-patch or exact-master-canvas assembly, record:

- fixed anchors: head top, neck base, left/right shoulder, waist center, elbows, prop contacts, hips, knees, feet/support contacts;
- frozen regions: all pixels that must remain identical;
- allowed change mask: the smallest region capable of the requested action;
- natural seam paths: collar, lapel, sleeve cuff, prop edge, hairline, or an existing occlusion edge.

If only the head or one arm changes, do not authorize the full torso. If the action necessarily changes the torso, register the new patch to at least three shared anchors before blending.

Facial accessories must be registered to facial landmarks from the accepted master. Never draw glasses, pupils, scars, or similar details at fixed canvas coordinates: a small pose or crop shift turns them into doubled or misplaced facial features.

For a registered complete state, record the shared canvas plus at least one support anchor, normally both feet or seat/bed contacts. Also record idle attention target, active attention target, and maximum alpha support drift.

## Machine-readable local-patch assembly gate

`verify-states` requires a `stateAssembly` object. A minimum contract is:

```json
{
  "stateAssembly": {
    "beforeIsMaster": true,
    "assemblyMode": "registered-local-patch",
    "reuseMasterTransform": true,
    "assetCanvasSize": [385, 400],
    "allowedChangeMasks": [
      {"label": "head-and-pointing-arm", "bbox": [0, 0, 200, 220]}
    ],
    "naturalSeamPaths": [
      {"label": "left-lapel", "points": [[100, 120], [112, 155], [118, 190]]}
    ],
    "facialAccessoryChanges": [
      {
        "name": "reading-glasses",
        "anchors": {
          "leftEye": [0, 0],
          "rightEye": [0, 0],
          "noseBridge": [0, 0]
        }
      }
    ],
    "occlusionStrategy": "separate-source-occluder"
  }
}
```

Zero coordinates are placeholders only. This `verify-states` contract accepts `registered-local-patch` or `exact-master-canvas`. A seam path spanning at least half the asset width while remaining essentially horizontal is rejected. `occlusionStrategy` may be `none`, `separate-source-occluder`, or `source-exact-irregular-mask`; a constant-Y alpha cut is never valid.

## Machine-readable exploration pair gate

Use `scene_staging_tools.py verify-exploration-states` for every exploration idle/active pair, including registered complete states:

```json
{
  "schema": "ndc-exploration-state-pair/v1",
  "interactionType": "exploration-click-pair",
  "assemblyMode": "registered-complete-state",
  "assetCanvasSize": [385, 400],
  "idleAttentionTarget": "scene-object",
  "activeAttentionTarget": "player",
  "reuseMasterTransform": true,
  "statesIndependentlyNormalized": false,
  "stateDeltaScope": {
    "regions": ["head", "upper-torso"],
    "wholeBodyAuthorized": false,
    "reason": "player engagement needs only an attention turn"
  },
  "supportAnchors": [
    {"name": "left-foot-contact", "idle": [142, 382], "active": [142, 382], "tolerancePx": 2},
    {"name": "right-foot-contact", "idle": [225, 382], "active": [225, 382], "tolerancePx": 2}
  ],
  "maxAlphaSupportDriftPx": 4,
  "visualReview": {
    "reviewAuthority": "codex-self-check",
    "identityContinuity": "pass",
    "supportAndShadowContinuity": "pass",
    "stateReadability": "pass",
    "edgeContinuity": "pass",
    "flicker": "pass"
  }
}
```

The validator emits a half-blend overlay, difference image, flicker GIF, changed-pixel metrics, and report. It rejects canvas, alpha-corner, support-anchor, frozen-region, alpha-bottom drift, independent normalization, or missing/failed Codex visual-review evidence. `registered-local-patch` and `exact-master-canvas` additionally require `allowedChangeMasks`; every changed pixel must stay inside them. A machine report cannot invent the visual-review values: Codex records them only after inspecting the original-size flicker and edge backgrounds.

## Continuity QA

Check more than frozen-pixel equality:

1. for patch modes, compare silhouettes for 8-16 pixels on both sides of every seam;
2. reject abrupt width changes, doubled outlines, broken lapels, disconnected sleeves, and lighting jumps;
3. compare edge direction and luminance across any seam band;
4. verify support/prop anchors do not move unless authorized;
5. verify the idle state reads as ambient and active reads as player engagement;
6. flicker between states at original size to expose placement, scale, support, shadow, or identity jumps.

A passing lower-body equality test does not prove that the transition is visually continuous.

## Alpha rule

Prefer real RGBA output. A rendered checkerboard is not transparency.

- Reject baked checkerboard delivery.
- If recovery is necessary, use a proper matte-extraction method with edge-color decontamination, then inspect hair, fingers, glasses, garment edges, and shoes on both dark and light backgrounds.
- Do not use a brightness threshold plus blurred alpha as final production matting; it leaves light matte contamination and makes the actor look pasted on.

For interaction components, keep necessary support/occlusion pixels with a minimal irregular alpha. For independent standing actors, do not include scene pixels unless physically required.
