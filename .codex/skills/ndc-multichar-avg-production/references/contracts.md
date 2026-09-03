# Cast-plan contract v2

Use one JSON plan per frozen simultaneous-cast snapshot. New work must use:

```json
"schema": "ndc-multichar-avg-plan/v2"
```

Validate after every stage change:

```powershell
python scripts/validate_avg_cast_plan.py <plan.json>
```

The validator is a hard gate, not a visual judge. A user must still approve the combined whitebox, and the operator must still inspect generated actors and Photoshop mattes.

## Stages

- `blocking`: the active timeline snapshot, exact simultaneous cast, source/UI identities, canonical heights, card scale references, performances, pose landmarks, support, all pairwise occlusion decisions, and intended artifact paths are declared. Timeline must already pass; later review artifacts may be `PENDING`.
- `whitebox-approved`: the combined and isolated whiteboxes exist on the source canvas; UI, absolute scene scale, cast-relative scale, support, artifact linkage, and 100%/200% visual review all have `PASS` records.
- `final`: contextual candidates, cutouts, per-actor registration, layered PSD/PNG, gaze, background preservation, identity/light/matte checks, and final 100%/200% review all pass.

Legacy `ndc-multichar-avg-plan/v1` files are not valid for new production. Migrate them before formal actor generation.

## Review artifact shape

Every review object uses auditable paths rather than a bare status string:

```json
{
  "report": "D:/path/review.json",
  "reportSha256": "64-lowercase-hex-characters",
  "preview": "D:/path/review-overlay.png",
  "status": "PASS"
}
```

At `blocking`, reviews that depend on an unfinished whitebox use `status: "PENDING"`; their intended `report` and `preview` paths must still be declared. At `whitebox-approved` and `final`, required review files must exist, hashes must match, and status must be `PASS`.

## V2 structure example

Coordinates use the untouched source-scene canvas. The actor array below shows one complete actor template; repeat it for every simultaneous actor and record all pairwise occlusion entries. Values illustrate the structure only; measure every real scene independently.

```json
{
  "schema": "ndc-multichar-avg-plan/v2",
  "stage": "whitebox-approved",
  "sceneId": "SCxxxx",
  "sceneKind": "static-multichar-avg",
  "sourceScene": "D:/path/fixed-background.png",
  "sourceSceneSha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "sceneSize": [2560, 1600],
  "castClusterSide": "right",
  "uiSide": "left",
  "uiReference": "D:/path/left_BG.png",
  "uiReferenceSha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "uiPlacement": {
    "canvasSize": [2560, 1600],
    "topLeft": [0, 0],
    "mirrorX": false
  },
  "timelineReview": {
    "snapshotId": "loop3-node-205009006",
    "report": "D:/path/timeline-report.json",
    "reportSha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
    "status": "PASS"
  },
  "uiSafetyReview": {
    "report": "D:/path/ui-safety-report.json",
    "reportSha256": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
    "preview": "D:/path/ui-safety-overlay.png",
    "status": "PASS",
    "protectedRegions": ["headBox", "leftHand", "rightHand", "ownedProp", "actionFocus"],
    "maxHeadOverlapRatio": 0.0,
    "maxCriticalOverlapRatio": 0.0
  },
  "silentFrameStatement": "One investigator controls the foreground while his partner closes the suspect's legal escape.",
  "combinedWhitebox": "D:/path/combined-whitebox.png",
  "combinedWhiteboxSha256": "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "actorContacts": [],
  "sceneAbsoluteScaleReview": {
    "contract": "D:/path/scene-absolute-scale.json",
    "report": "D:/path/scene-absolute-scale-report.json",
    "reportSha256": "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
    "preview": "D:/path/scene-absolute-scale-overlay.png",
    "status": "PASS",
    "projectionModel": "single-horizon floor-plane projection",
    "horizonY": 515,
    "anchorGroups": [
      {
        "id": "sofa",
        "scope": "cross-depth",
        "depthBand": "near",
        "measuredAxes": ["horizontal", "vertical"],
        "confidence": "medium",
        "measurementLines": [
          {"axis": "horizontal", "start": [670, 1120], "end": [1320, 1120], "realWorldRangeCm": [180, 230], "assumption": "three-seat club sofa"},
          {"axis": "vertical", "start": [670, 880], "end": [670, 1120], "realWorldRangeCm": [75, 100], "assumption": "floor-to-back height"}
        ]
      },
      {
        "id": "bookcase-bay",
        "scope": "actor-local",
        "depthBand": "mid",
        "measuredAxes": ["horizontal", "vertical"],
        "confidence": "high",
        "measurementLines": [
          {"axis": "horizontal", "start": [1960, 730], "end": [2240, 730], "realWorldRangeCm": [75, 105], "assumption": "single cabinet bay"},
          {"axis": "vertical", "start": [1960, 530], "end": [1960, 1320], "realWorldRangeCm": [210, 260], "assumption": "floor-standing bookcase"}
        ]
      },
      {
        "id": "window-column",
        "scope": "cross-depth",
        "depthBand": "far",
        "measuredAxes": ["vertical"],
        "confidence": "medium",
        "measurementLines": [
          {"axis": "vertical", "start": [1450, 410], "end": [1450, 1180], "realWorldRangeCm": [220, 300], "assumption": "architectural floor-to-lintel span"}
        ]
      }
    ]
  },
  "castScaleReview": {
    "contract": "D:/path/cast-scale.json",
    "report": "D:/path/cast-scale-report.json",
    "reportSha256": "1111111111111111111111111111111111111111111111111111111111111111",
    "status": "PASS",
    "headScalePriority": true,
    "maxDeviationRatio": 0.03,
    "maxHeadDeviationRatio": 0.05
  },
  "whiteboxVisualReview": {
    "report": "D:/path/whitebox-visual-review.json",
    "reportSha256": "2222222222222222222222222222222222222222222222222222222222222222",
    "preview": "D:/path/whitebox-review-board.png",
    "status": "PASS",
    "wholeFrameZoomPercent": 100,
    "localZoomPercent": 200
  },
  "occlusionGraph": {
    "pairwise": [
      {"actors": ["201", "205"], "relation": "no-overlap"},
      {"actors": ["201", "player"], "relation": "second-in-front"},
      {"actors": ["205", "player"], "relation": "second-in-front"}
    ],
    "sceneOccluders": [
      {"id": "foreground-table-edge", "source": "sourceScene", "aboveActors": ["player"]}
    ]
  },
  "outputPsd": "D:/path/final.psd",
  "outputPng": "D:/path/final.png",
  "actors": [
    {
      "actorId": "205",
      "name": "Mickey Donnelly",
      "presenceAtSnapshot": "already-present",
      "characterCard": "D:/path/mickey-card.png",
      "characterCardSha256": "3333333333333333333333333333333333333333333333333333333333333333",
      "canonicalHeightCm": 183,
      "canonicalHeightSource": "D:/path/mickey.md",
      "canonicalHeightSourceSha256": "4444444444444444444444444444444444444444444444444444444444444444",
      "identityScaleReference": {
        "referenceFullBodyHeightPx": 1420,
        "referenceAnatomicalHeadHeightPx": 175,
        "bodyBuild": "lean, controlled, tailored silhouette",
        "headToBodyNotes": "Preserve the approved card's narrow shoulder-to-head relationship."
      },
      "whiteboxColor": "#8F55C7",
      "isolatedWhitebox": "D:/path/mickey-isolated.png",
      "isolatedWhiteboxSha256": "5555555555555555555555555555555555555555555555555555555555555555",
      "whiteboxCanvasSize": [2560, 1600],
      "depthClass": "midground",
      "framing": "full-body",
      "backFacing": false,
      "feetVisible": true,
      "poseFamily": "standing-legal-pressure",
      "seatedJustification": "",
      "facing": "screen-right",
      "gazeTarget": "201",
      "support": "scene:floor-mid-right",
      "supportPoint": [1780, 1390],
      "anchor": "feet-bottom-center",
      "standingEquivalentHeightPx": 882,
      "poseLandmarks": {
        "headBox": [1710, 508, 1830, 650],
        "neck": [1770, 666],
        "leftShoulder": [1705, 700],
        "rightShoulder": [1835, 700],
        "leftElbow": [1680, 900],
        "rightElbow": [1860, 890],
        "leftHand": [1710, 990],
        "rightHand": [1835, 980],
        "hipCenter": [1770, 1030],
        "leftKnee": [1735, 1210],
        "rightKnee": [1805, 1210],
        "leftFoot": [1735, 1390],
        "rightFoot": [1810, 1390],
        "outerBBox": [1656, 508, 1903, 1390]
      },
      "performance": {
        "silentFrameVerb": "contains",
        "beatEnergy": "controlled pressure",
        "ongoingOccupation": "holds his place beside Zack during the negotiation",
        "performanceFamily": "restrained legal pressure",
        "action": "holds position as legal pressure",
        "emotion": "controlled resolve",
        "facialExpression": "quietly alert, jaw set",
        "bodyLine": "upright with restrained forward intent",
        "weightDistribution": "balanced with weight slightly forward",
        "leftHandMotivation": "kept close and ready, not reaching",
        "rightHandMotivation": "rests near jacket front, not exchanging an object",
        "namedSupport": "scene:floor-mid-right",
        "socialTerritory": "shares the investigators' side without merging silhouettes",
        "actionFocus": "Moore and the deed envelope",
        "subtext": "his presence makes refusal legally dangerous",
        "costumeState": "approved three-piece suit, intact and buttoned consistently",
        "propContinuity": "holds no prop at this snapshot",
        "depthHonesty": "midground scale follows the floor support projection",
        "tenSecondHold": true
      },
      "supportContactReview": {
        "report": "D:/path/mickey-support-report.json",
        "reportSha256": "6666666666666666666666666666666666666666666666666666666666666666",
        "preview": "D:/path/mickey-support-overlay.png",
        "status": "PASS"
      },
      "prop": null
    }
  ]
}
```

Repeat the complete actor object for every simultaneous actor. Within one snapshot, every actor needs a unique `#RRGGBB` whitebox color. Colors are temporary scene labels and never permanent character identities.

## Absolute-scale requirements

`sceneAbsoluteScaleReview.anchorGroups` must contain at least three unique groups. Across the complete set:

- both `horizontal` and `vertical` must occur in `measuredAxes`;
- at least two `depthBand` values must occur;
- at least one group must use `scope: actor-local`;
- at least one group must use `scope: cross-depth`;
- every group must state `confidence` as `low`, `medium`, or `high`.
- every `measuredAxes` entry must have a matching `measurementLines` entry with exact endpoints, a plausible centimeter range, and a written assumption;
- the review must record a finite `horizonY` and a named `projectionModel`.

Use the parent deterministic tool rather than judging only by eye:

```powershell
python ../ndc-character-scene-integration/scripts/scene_staging_tools.py `
  validate-scene-absolute-scale <contract.json> --report <report.json> --preview <overlay.png>
```

## Cast-scale requirements

Every actor requires a canonical integer height, source file, approved-card measurements, support point, standing-equivalent pixel height, and exact head box. Run:

```powershell
python ../ndc-character-scene-integration/scripts/scene_staging_tools.py `
  validate-cast-scale <contract.json> --report <report.json>
```

`headScalePriority` must be `true`. `maxDeviationRatio` may not exceed `0.03`, and `maxHeadDeviationRatio` may not exceed `0.05`. Do not use a universal scale percentage. A large foreground figure may be correct when perspective supports it; the canonical-height projection and pairwise report decide.

## UI requirements

`uiReference` must be the real UI image or an engine-derived mask source, not a remembered percentage of the screen. `uiPlacement` records the target canvas, top-left placement, and whether the engine mirrors the asset. `uiSafetyReview` must protect `headBox`, both motivated hands, owned props, and the action focus with zero critical overlap. Run:

```powershell
python ../ndc-character-scene-integration/scripts/scene_staging_tools.py `
  validate-ui-safety <contract.json> --report <report.json> --preview <overlay.png>
```

The overlay must be reviewed on the same canvas as the combined whitebox. A selected side passes only when faces, identity-critical head regions, motivated hands, owned props, and the action focus remain readable.

## Final-stage additions

At `final`, every actor also requires:

```json
{
  "contextualCandidate": "D:/path/actor-context.png",
  "rawCutout": "D:/path/actor-cutout.png",
  "finalLayerName": "30_Mickey_EdgeClean",
  "registration": {
    "uniformScalePercent": 98.5,
    "translateX": 12.0,
    "translateY": -4.0,
    "anchor": "feet-bottom-center"
  },
  "edgeReview": "PASS",
  "identityReview": "PASS",
  "lightingReview": "PASS"
}
```

The plan also requires `outputPsdSha256`, `outputPngSha256`, and three PASS review artifacts named `finalGazeReview`, `backgroundPreservationReview`, and `finalVisualReview`. `finalVisualReview` records `wholeFrameZoomPercent: 100` and `localZoomPercent: 200`.

Registration permits exactly one uniform scale plus translation per actor. If this cannot match the approved head box, support anchor, and action envelope, reject that actor candidate instead of warping it.
