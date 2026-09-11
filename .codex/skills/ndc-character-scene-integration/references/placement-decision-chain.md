# Placement and scale decision chain

Whitebox position/proportion repair follows [whitebox-photoshop-fallback.md](whitebox-photoshop-fallback.md): use actual anatomical mannequin components in Photoshop MCP as soon as a bounded repair is feasible, for up to three repair/review rounds; do not wait to exhaust three generated attempts. Recalibrate and reaccept the repaired whitebox before using it. For whitebox or formal art, Photoshop MCP may correct a separable actor's uniform scale or translation around a confirmed support point when anatomy, orientation, and action are already valid. Update the existing transform, scale, contact, interaction, and composite checks together; never deform anatomy or conceal an incorrect pose by resizing it to an outer rectangle.

Keep user-explicit coordinate, scale, and pose locks unless their change is authorized; distinguish them from provisional coordinates authored by Codex. The checks below are compatibility scopes inside the milestones in [production-cadence.md](production-cadence.md), not separate full reviews after every micro-operation.

## Position order

Run this decision only after runtime branch, engineering lifecycle, story beat, performance contract, scene-affordance map, and actual UI mask exist. For a scene with one visible character, evaluate depth class inside the position decision:

1. midground;
2. foreground;
3. far/background.

Use a lower-priority depth only when higher-priority positions fail physical space, state expression, orientation, occlusion, UI, or scale readability. For multiple characters, prioritize readable staging and depth separation over the single-character order.

Within each depth class, evaluate in this order:

1. derive the current timeline snapshot and silent-frame statement;
2. establish the actual usable support space and actor depth from the empty scene, then select affordance zones capable of the required standing, sitting, lying, walking, or leaning action;
3. find a location that expresses objective, conflict, emotion, subtext, and action focus;
4. confirm story fit and bodily naturalness independently, and that the performance does not depend on a future entrant;
5. if unavailable, choose a narratively equivalent action within a physically valid zone;
6. keep total character occlusion at or below 60%, with face and required hands/props readable;
7. obey furniture, architecture, support, reach, and entrance/exit orientation;
8. compare the real left/right UI candidates, select the one side with the lower story and visibility cost for this snapshot, record it, and validate the candidate against that applicable reference at pixel level; do not require both mutually exclusive sides to pass;
9. calibrate scale and complete outer rectangle.

Record rejected candidates, automatic score components, and reasons. Generate deterministic candidates from the selected zone before manual coordinate editing. Do not label a broad rectangle "midground" and then select its foreground edge without rechecking apparent depth.

The former opposite-two-thirds rule is a rough ideation heuristic only. It cannot pass UI safety because the real UI references have shaped silhouettes and local intrusions. Use `validate-ui-safety` with the actual left/right assets for every meaningful snapshot. For three-plus-cast work, every actual snapshot actor must appear exactly once in both the bound UI contract and its report; multicast validation rejects missing, unknown and duplicate actor IDs.

## Measured perspective before numerical scale

Before assigning hidden foot points or a scalar horizon, follow the evidence and sensitivity procedure in [continuous-floor-support.md](continuous-floor-support.md). Group visible scene lines by world direction; many lines in one direction improve one vanishing-point estimate but do not supply a whole horizon. Keep inferred support ranges separate from measured contacts.

## Multi-anchor scale calibration

The 170cm proxy is a ruler, not an identity, pose, or composition reference. Never place a large generic human in the requested scene as a visual subject, never send the proxy as the character reference for image generation, and never infer scale from the proxy image itself. The scene anchors create the ruler scale; the ruler only visualizes that result. For multi-character blocking, prefer a named outer rectangle with `target.proxyStyle: skeleton`; keep any solid silhouette preview as a separate technical artifact.

- Register one `ndc-scene-absolute-scale/v2` for the scene. In metric mode, use at least two independent vertical `height-calibration` anchors spanning `actor-local` and `cross-depth`, plus a separate independent horizontal `footprint-check`. Both height anchors need medium/high confidence. Two dimensions of one sofa remain one object/group. A horizontal footprint checks occupied width and does not enter the height median.
- Useful anchors include full doors, door handles, counter tops, desk tops, chair seats/backs, beds, stair risers, and people already approved in the same camera.
- Several estimates derived from the same provisional vanishing point, ground plane, or assumed furniture dimensions are correlated evidence, even if they use different object IDs. Agreement between them establishes arithmetic consistency, not reliable physical scale. State the shared assumptions and uncertainty in the existing calibration evidence; compare against actual scene topology, local support depth, and the whole composition. A visibly implausible actor does not pass because those estimates agree. Revisit the uncertain basis rather than tune numbers to make the validator pass.
- Record each object's stable `objectId`, `independenceGroup`, `depthBand`, measured dimension, plausible real-world range, chosen real-world value, raw image measurement, measurement projected to the actor plane, plane/depth relation, projection method, projected standing-height estimate, and confidence. A cross-depth anchor also records source/target support points and the perspective-basis IDs used for projection. A prose source label alone is insufficient evidence. The validator recomputes `projectedMeasurementPxAtTarget × characterHeightCm ÷ assumedCm`; the recorded `value` must agree within the declared tolerance.
- Run `validate-scene-absolute-scale` for the shared register. `metric-pass` recomputes measurement lines and the height-only median, then projects the shared reference-plane rate to each registered support plane. It diagnoses affected actor scale; it does not automatically rescale approved layers. `bounded-pass` instead requires actual complete/combined whitebox, support, head and UI checks plus inspected sensitivity outcomes, and outputs ranges without a metric correction factor. A relative cast pass cannot override blocked scene geometry.
- Project anchors to the target foot point through justified scene geometry; do not compare raw pixel height across unrelated depths. Depth transfer and direction transfer are separate: a horizontal cabinet width cannot become a vertical human-height ruler by a depth ratio alone. Use a calibrated camera or an independently established metric reference for the direction conversion; otherwise keep that width as a footprint check outside the height estimator. The absolute-scale contract requires explicit evidence-bound direction conversion for horizontal anchors that contribute to height; see staging-tool-contracts.md. A ground-plane homography alone does not establish off-plane standing height.
- In metric v2, combine height anchors only after reference-plane and any necessary direction projection. Keep the original deviation/spread ceilings; new tasks normally use 0.08 for each. Legacy per-actor calibrations still use `median-after-depth-projection` and their cross-depth checks. A stylized scene with inconsistent furniture is reason to revisit the evidence, not tune the numbers into agreement.
- Validate both height and action outer width. Hair, hands, elbows, garments, props, and shoes must stay inside the approved action envelope with safety margin.

For a seated character, do not paste the standing proxy over a chair and do not replace it with an arbitrary head-and-torso block. First calibrate `standingEquivalentHeightPx` from the 170cm ruler. Lock that scale, then bend the same anatomical ruler at the hips and knees. Keep the approved character's head-to-body ratio and body-segment lengths unchanged; sitting changes joint angles and vertical extent, not identity scale.

Record an anatomical head box that excludes hats and hair extensions, shoulders, hip/seat contact, knees, both feet, support surface, and action outer rectangle. The bare-head anatomical seated span from crown to the lowest body contact must be lower than `standingEquivalentHeightPx` at the same depth. Hats, raised hands, props, or forward-projected feet are recorded as outer extensions; they may enlarge `visibleHeightPx`, but they never authorize scaling up the body. `outerBBox` and `visibleHeightPx` are results of the locked pose, not targets that the generated actor is resized to fill.

The seated contract must include a `scaleAudit` containing `anatomicalTopY`, `anatomicalBottomY`, `standingHeadHeightPx`, `seatedHeadHeightPx`, `bodyScaleDriver: standingEquivalentHeightPx`, and structured `outerExtensions` with labels, boxes, and reasons. The two head heights must agree within the declared tolerance, 20% for new NDC tasks under the user rule of 2026-09-08. The anatomical head and all seated joints must stay inside the approved outer box; the target foot anchor must equal the midpoint/lowest contact derived from both feet. The seat contact and both feet must agree with the furniture and ground plane before depth/whitebox generation. Record any foreground furniture in `target.occluderPolygons`; the deterministic preview restores those source pixels after drawing the proxy so the visible occlusion is evaluated instead of guessed.

New placements reference the shared scene report through `calibration.sceneScaleEvidence: {path, sha256}` and their stable `calibration.actorId`. The register already holds the independent estimates; do not recopy the same furniture into every actor. `target.supportPlaneId` and the complete pose/height snapshot must agree with the register. A new support plane needs its own justified projection and footprint, not another copy of all the height anchors. Historical placements without this reference retain their original two-anchor checks.

For bounded geometry, first use provisional whole-scene candidates for diagnosis, within the original whitebox budget. Freeze the actual reviewed pose snapshot independently of its future scale report, then review the lower/upper assumptions. Only after current full/local whitebox, support, head and UI evidence passes can the register emit `bounded-pass`; the earlier preview is never generation readiness. A range that changes the support plane, usable position, head relationship or UI readability is blocked. See [staging-tool-contracts.md](staging-tool-contracts.md) for the exact scene-scale v2 and elevated-lying cast-scale v3 interfaces.

For a lying character, use the same principle with `placementClass: lying`. Calibrate `standingEquivalentHeightPx` at the bed/support depth, lock the anatomical head height, then rotate and bend the same body along the bed perspective. A lying outer box is normally much shorter and wider than a standing box. Its height can never be used to rescale the person. Record the anatomical head box, shoulders, elbows, hands, hip, knees, both feet, body axis, support object, and a support `contactPoint`. The head height in the lying pose must match the same-depth standing master within the declared tolerance, 20% for new NDC tasks under the user rule of 2026-09-08. The affordance support surface must also define its full support polygon, a head/pillow region, and a foot-end region. A single contact point or several torso contacts cannot prove that the feet are on the bed or that the body is oriented head-to-foot correctly.

Treat the back of the head, neck, shoulders, pillow, and adjacent bedding as one contact relationship. Establish where the head is carried and how the neck and shoulders rest before generating or repairing the minimum interaction region. The pillow should compress or wrap where the load calls for it, with coherent contact darkening and bedding response; a shadow alone cannot repair an unsupported neck. Preserve an independent complete actor master and a separate soft-surface response component, but review them together after any relevant transform. Fixed bed frames and rails stay at source pixels, scale, and coordinates. Original pillow pixels may be reused only if they already express the required load; source origin is not a reason to freeze an unloaded pillow.

For every pose, compare the head box against the approved identity-scale reference and the other actors at their projected depths before reviewing the whole outer rectangle. For non-standing poses, also compare it against the same-depth standing ruler. If the head shrinks because the character sits or lies down, or a nearer actor's head becomes smaller than a farther comparable adult without identity evidence, reject the placement even when the outer box looks tidy.

## Exact pose requirement for every placement class

Every placement class must contain an explicit pose definition before actor depth alignment or whitebox creation. Record a stable `poseId`, action, facing, gaze target, both hand actions or resting states, required props, support object, and the complete anatomical landmark set: head box, neck, both shoulders, elbows, hands, hips, knees, and feet. Standing is not exempt. Empty-scene support/depth evidence is established first and must not be reverse-fitted to these joints.

The renderer must use those landmarks. It may not synthesize a default symmetrical upright pose from only `foot` and `visibleHeightPx`. If the intended action is leaning, reaching, holding, turning, sitting, or lying, the proxy and whitebox must already show that exact action.

## Depth and whitebox gate

Depth and whitebox are mandatory after exact-pose proxy approval, but their roles differ:

- Infer empty-scene ground/support geometry independently from the actor.
- Encode stand/sit affordance polygons as anchor/support regions rather than full-body rectangles. Encode support contact polylines from the empty scene/depth/model before the actor joints exist.
- Run `validate-support-contact` after pose authoring. Fixed support lines calculate signed vertical delta; negative beyond tolerance is floating, positive beyond tolerance is sinking. Continuous ground follows [continuous-floor-support.md](continuous-floor-support.md): region coverage has no unique expected support Y and cannot measure floating. For lying poses, require `lyingSupportEnvelope.status: pass` plus visible anatomical and soft-surface contact. Inspect the overlay because a mathematically consistent but visually misplaced support line or polygon is still invalid.
- A seated actor normally has at least two support objects: pelvis-to-seat and feet-to-floor. Do not attach hip and feet to one generic chair ID merely to pass a support check.
- Before assigning a seated support, audit whether the seat is physically occupied. Loose objects require a bounded clearance plan and logical destination. Use one minimum old-location repair patch and one minimum destination layer for the moved item. Never include the fixed chair/bed structure itself in a generated or scalable actor component; exact fixed source occluders remain at scale 1. A cushion or bedding response uses its separate bounded interaction layer.
- Validate seated kinematics from pelvis through knees to feet. Record primary support foot, signed foot stagger, stance-width/shoulder-width range, torso facing, and orientation rationale. Reject a declared three-quarter turn whose feet remain implausibly wide and symmetrical.
- Overlay the approved exact-pose proxy on the aligned depth reference without changing landmarks, anchor, or outer box.
- Render a solid neutral volumetric human whitebox from the same pose contract. It deliberately repeats the locked pose/scale to embody final occupied volume and contacts; it is not a new scale estimate.
- Produce an isolated whitebox per actor presence plus one combined-cast whitebox for each simultaneous-cast snapshot with declared actor order and scene occluders.
- Inspect the same complete actor layer with and without the final occluders, using exactly the same transform. First verify feet, legs, pelvis, and support; then verify the visible upper body against furniture and the whole scene. Hidden lower anatomy is not permission to guess a larger scale or accept a floating silhouette. Reuse these views within the existing review rather than creating a separate evidence workflow.
- Reject changes to camera, topology, support orientation, pose ID, head size, landmarks, contacts, layer order, or occlusion.
- A stick skeleton, generic upright mannequin, empty room blockout, outer rectangle, or file merely named `whitebox` is not a human whitebox.
- Codex reviews the rendered depth and whitebox artifacts at full-frame and complete local-tile scale. Store artifact hashes, pose IDs, the comparison report, and all required check results; no generated character may use a pending or failed structural review. Do not stop for per-character user approval.

Generated depth/whitebox pixels are never final scene pixels.

## Multi-character occlusion gate

Create one scene staging contract for every simultaneous-cast timeline snapshot. Give each present character a unique back-to-front `layerOrder`. For each pair of overlapping action boxes, record `front`, `back`, physical reason, allowed overlap region, maximum rear-character occlusion, and rear landmarks that must stay visible. Any unrecorded intersection fails. Never create an all-scene union contract for actors who do not coexist.

During one uninterrupted period of presence, an actor keeps the same `poseId`, transform, placement, and `affordanceZoneId`. A later entrant is added around those frozen contracts and cannot make existing actors turn, react, move, or change costume. Actor-to-actor gaze targets must be present in the same snapshot; required reciprocal acting must be declared and complete.

Record each character's relation to scene objects as `supported-by`, `touching`, `in-front-of`, `behind`, or `inside`. Relations may be regional: a character can be behind a bed rail but in front of a mattress. Use exact masks/polygons; a single whole-character z-order is insufficient.

The snapshot combined whitebox must show these relations before generation. After generation, review the same simultaneous cast again; independent per-character approval cannot pass the snapshot.

## Placement contract minimum

For new shared v2 placement, retain the full scene/target/pose fields below, add `target.supportPlaneId`, and replace the legacy `calibration` body with:

```json
{"sceneScaleEvidence":{"path":"absolute/current-scene-scale-report.json","sha256":"current SHA-256"},"actorId":"stable-actor-pose-unit"}
```

Use absolute source/report paths. The register binds an immutable pose snapshot containing `scene`, `sceneSize`, `characterHeightCm` and the complete `target`; that snapshot must not reference the report that will later depend on it. Final placement may add delivery metadata and the calibration reference, but must preserve the bound geometry. This avoids a circular hash dependency and keeps scene facts in one place.

The expanded per-actor calibration example below is the **historical v1 form**, still readable without silently upgrading an old PASS:

```json
{
  "scene": "absolute/path/to/scene.png",
  "deliveryRoot": "absolute/output/path/scene-basename",
  "proxy": "absolute/path/to/170cm-proxy.png",
  "sceneSize": [2560, 1600],
  "characterHeightCm": 175,
  "target": {
    "placementClass": "standing",
    "depthClass": "midground",
    "affordanceZoneId": "stand-zone-01",
    "foot": [0, 0],
    "visibleHeightPx": 0,
    "outerBBox": [0, 0, 0, 0]
  },
  "calibration": {
    "aggregationMethod": "median-after-depth-projection",
    "maxSpreadRatio": 0.08,
    "maxCrossDepthMedianDeltaRatio": 0.08,
    "derivedValueToleranceRatio": 0.03,
    "projectedHeightEstimatesPx": [
      {
        "objectId": "door-01",
        "independenceGroup": "architecture-door-01",
        "dimension": "height",
        "realWorldRangeCm": [195, 215],
        "assumedCm": 205,
        "imageMeasurementPx": 0,
        "projectedMeasurementPxAtTarget": 0,
        "projectionMethod": "ground-plane projection to target foot point",
        "planeRelation": "same wall bay, projected to actor depth",
        "depthBand": "cross-depth",
        "projectionEvidence": {
          "sourceSupportPoint": [0, 0],
          "targetSupportPoint": [0, 0],
          "perspectiveBasisIds": ["floor-vanishing-grid-01"]
        },
        "value": 0,
        "confidence": "medium"
      },
      {
        "objectId": "counter-01",
        "independenceGroup": "furniture-counter-01",
        "dimension": "height",
        "realWorldRangeCm": [85, 100],
        "assumedCm": 92,
        "imageMeasurementPx": 0,
        "projectedMeasurementPxAtTarget": 0,
        "projectionMethod": "ground-plane projection to target foot point",
        "planeRelation": "foreground of actor, depth corrected",
        "depthBand": "actor-local",
        "value": 0,
        "confidence": "medium"
      }
    ]
  }
}
```

Zeroes are placeholders and must never reach production.

Every target also requires:

```json
"poseDefinition": {
  "poseId": "scene-character-state-v1",
  "action": "exact narrative action",
  "facing": "camera-relative orientation",
  "gazeTarget": "specific target",
  "leftHandAction": "exact action",
  "rightHandAction": "exact action",
  "requiredProps": []
},
"standingPose": {
  "headBox": [0, 0, 0, 0],
  "neck": [0, 0],
  "leftShoulder": [0, 0],
  "rightShoulder": [0, 0],
  "leftElbow": [0, 0],
  "rightElbow": [0, 0],
  "leftHand": [0, 0],
  "rightHand": [0, 0],
  "leftHip": [0, 0],
  "rightHip": [0, 0],
  "leftKnee": [0, 0],
  "rightKnee": [0, 0],
  "leftFoot": [0, 0],
  "rightFoot": [0, 0],
  "supportObject": "floor or named support"
},
"sceneRelations": [
  {
    "objectId": "floor-01",
    "relation": "supported-by",
    "regions": ["leftFoot", "rightFoot"],
    "reason": "both shoes contact the actor ground plane"
  }
]
```

For seated and lying classes, use `seatedPose` or `lyingPose` instead of `standingPose`, but keep the same complete landmark set and add the class-specific seat/bed fields described below.

For a multi-character scene, add a scene staging contract:

```json
{
  "scene": "absolute/path/to/scene.png",
  "sceneSize": [2560, 1600],
  "timelineSnapshotId": "beat-02-after-entry",
  "uiSide": "left",
  "uiSafetyReview": {
    "status": "passed",
    "report": "absolute/path/ui-safety-report.json",
    "reportSha256": "fill after validation"
  },
  "characters": [
    {"name": "Rear Actor", "contract": "absolute/path/rear.contract.json", "layerOrder": 10},
    {"name": "Front Actor", "contract": "absolute/path/front.contract.json", "layerOrder": 20}
  ],
  "occlusionGraph": [
    {
      "front": "Front Actor",
      "back": "Rear Actor",
      "reason": "front actor stands closer on the approved ground plane",
      "allowedOverlapBBox": [0, 0, 0, 0],
      "maxBackOcclusionRatio": 0.60,
      "requiredVisibleLandmarks": ["headBox", "leftHand"]
    }
  ],
  "combinedWhiteboxReview": {
    "status": "passed",
    "reviewAuthority": "codex-self-check",
    "artifact": "absolute/path/combined-whitebox.png",
    "artifactSha256": "fill after render",
    "depthReference": "absolute/path/aligned-depth-reference.png",
    "depthReferenceSha256": "fill after render",
    "poseIds": {"Rear Actor": "pose-id", "Front Actor": "pose-id"},
    "wholeImageChecked": true,
    "localTileCoverageComplete": true,
    "comparisonReport": "absolute/path/whitebox-depth-comparison.md",
    "checks": {
      "timelineConformance": "pass",
      "storyBeatConformance": "pass",
      "performanceConformance": "pass",
      "affordanceConformance": "pass",
      "scaleConformance": "pass",
      "poseConformance": "pass",
      "supportContactConformance": "pass",
      "sceneOcclusionConformance": "pass",
      "castOcclusionConformance": "pass",
      "uiSafeAreaConformance": "pass"
    }
  }
}
```

`combinedWhiteboxReview.status` may be set to `passed` only after Codex actually inspects the whole image and every local tile against the placement, depth, pose, support-contact report/overlay, and occlusion contracts. `supportContactConformance` is copied from the deterministic report, never typed as an unsupported assertion. Hashes establish artifact identity but do not substitute for visual review. A failed review is corrected and rerun automatically without interrupting the user.

After formal character generation and combined composition, add:

```json
"formalConformanceReview": {
  "status": "passed",
  "reviewAuthority": "codex-self-check",
  "attempt": 1,
  "finalComposite": "absolute/path/final-composite.png",
  "finalCompositeSha256": "fill after composition",
  "combinedWhitebox": "absolute/path/combined-whitebox.png",
  "combinedWhiteboxSha256": "fill after render",
  "depthReference": "absolute/path/aligned-depth-reference.png",
  "depthReferenceSha256": "fill after render",
  "wholeImageChecked": true,
  "localTileCoverageComplete": true,
  "comparisonReport": "absolute/path/final-vs-depth-whitebox.md",
  "checks": {
    "timelineConformance": "pass",
    "storyBeatConformance": "pass",
    "performanceConformance": "pass",
    "affordanceConformance": "pass",
    "scaleConformance": "pass",
    "poseConformance": "pass",
    "jointPlacementConformance": "pass",
    "supportContactConformance": "pass",
    "actionEnvelopeConformance": "pass",
    "sceneOcclusionConformance": "pass",
    "castOcclusionConformance": "pass",
    "uiSafeAreaConformance": "pass",
    "identityConformance": "pass",
    "costumeStateConformance": "pass",
    "styleConformance": "pass",
    "shadowConformance": "pass",
    "backgroundPreservationConformance": "pass"
  }
}
```

If attempt 6 still fails, do not fabricate PASS. Add a `candidateHandoff` record with `attemptCount: 6`, the selected artifact/hash, comparison report, unresolved `failedChecks`, selection reason, and a `candidateRoot` in a dedicated child of configured `{WORK_ROOT}`. The best-available candidate is shown only in the final batch review and never enters a formal planning or engine target.

For `placementClass: seated`, also provide:

```json
"seatedPose": {
  "headBox": [0, 0, 0, 0],
  "neck": [0, 0],
  "leftShoulder": [0, 0],
  "rightShoulder": [0, 0],
  "leftElbow": [0, 0],
  "rightElbow": [0, 0],
  "leftHand": [0, 0],
  "rightHand": [0, 0],
  "leftHip": [0, 0],
  "rightHip": [0, 0],
  "hipSeat": [0, 0],
  "leftKnee": [0, 0],
  "rightKnee": [0, 0],
  "leftFoot": [0, 0],
  "rightFoot": [0, 0],
  "supportObject": "scene object name"
},
"scaleAudit": {
  "anatomicalTopY": 0,
  "anatomicalBottomY": 0,
  "standingHeadHeightPx": 0,
  "seatedHeadHeightPx": 0,
  "headToleranceRatio": 0.20,
  "bodyScaleDriver": "standingEquivalentHeightPx",
  "outerExtensions": [
    {
      "label": "hat",
      "bbox": [0, 0, 0, 0],
      "reason": "approved character headwear outside anatomical head box"
    }
  ]
}
```

Also add `target.standingEquivalentHeightPx`. `calibration.projectedHeightEstimatesPx` must estimate this standing-equivalent height at the same depth; `target.visibleHeightPx` must equal the seated `outerBBox` height within two pixels. The anatomical seated span must remain below the standing-equivalent height, while each structured `outerExtensions` box explains only extra hat, prop, hand, or garment pixels. `outerBBox` or an alpha bounding box may never be recorded as the body scale driver. Use `target.poseToStandingRatioRange` when the default 0.55–1.20 range needs a documented exception; do not change the range merely to pass a failed composition.

For `placementClass: lying`, use the same `standingEquivalentHeightPx` and `scaleAudit.bodyScaleDriver`, but provide `lyingHeadHeightPx`, `contactPoint`, and:

```json
"lyingPose": {
  "headBox": [0, 0, 0, 0],
  "neck": [0, 0],
  "leftShoulder": [0, 0],
  "rightShoulder": [0, 0],
  "leftElbow": [0, 0],
  "rightElbow": [0, 0],
  "leftHand": [0, 0],
  "rightHand": [0, 0],
  "leftHip": [0, 0],
  "rightHip": [0, 0],
  "hip": [0, 0],
  "leftKnee": [0, 0],
  "rightKnee": [0, 0],
  "leftFoot": [0, 0],
  "rightFoot": [0, 0],
  "bodyAxis": [[0, 0], [0, 0]],
  "supportObject": "scene bed or support name"
}
```

For lying poses, `target.visibleHeightPx` is the outer box's vertical span, normally 22–70% of the standing-equivalent height. This range is only a pose sanity check; it never drives body scale.
