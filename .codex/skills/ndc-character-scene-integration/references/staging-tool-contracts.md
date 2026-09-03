# Staging tool contracts and commands

Use the tools in `scripts/scene_staging_tools.py` before the scale/whitebox pipeline. All authored JSON is strict JSON. Runtime reports and previews belong under `D:\Codex\NDC\工作过程文件` until the user approves a final asset.

## 1. Extract the engineering timeline

```powershell
python scripts/scene_staging_tools.py extract-timeline `
  --talk-table D:\PMH\ndc\NDC\Assets\table\Talk.json `
  --npc-loop-table D:\PMH\ndc\NDC\Assets\table\NPCLoopData.json `
  --scene-config-table D:\PMH\ndc\NDC\Assets\table\SceneConfig.json `
  --scene-id 1003 `
  --start-talk-id 106005001 `
  --asset-root D:\PMH\ndc\NDC\Assets\Resources `
  --output D:\Codex\NDC\工作过程文件\scene-name\timeline-engine.json
```

Use `--scene-config-table` plus `--scene-id` to derive the initial cast automatically. Add a repeated `--initial-loop-id` only for a verified actor not represented by that scene configuration. The report records source hashes, cast before/after every node, frozen actors, enter/exit events, asset paths, and issues.

When the chain reaches a dialogue choice, the extractor records `UNRESOLVED_BRANCH` and stops instead of guessing. Rerun with a verified selection such as `--choice 106001008=106001101`; repeat `--choice` for later branches. Use `--strict` only after the initial cast and every required branch are resolved.

The extractor is tolerant of the current JSON-like Unity exports but never rewrites them.

## 2. Validate the directing timeline

```json
{
  "schema": "ndc-directing-timeline/v1",
  "timelineType": "pure-narrative",
  "snapshots": [
    {
      "id": "beat-01-initial",
      "storyBeat": {
        "objective": "keep the patient calm",
        "conflict": "the chart suggests bad news",
        "emotion": "contained worry",
        "subtext": "do not reveal the diagnosis yet",
        "actionFocus": "medical chart"
      },
      "silentFrameStatement": "The nurse hides concern while checking the chart.",
      "event": {"type": "initial"},
      "actors": [
        {
          "actorId": "nurse",
          "poseId": "room-nurse-hold-chart-v1",
          "transformId": "room-nurse-transform-v1",
          "placementId": "room-nurse-place-v1",
          "affordanceZoneId": "stand-bedside-01",
          "gazeTarget": {"type": "scene-object", "id": "chart-01"},
          "futureActorDependency": false,
          "reciprocityRequired": false,
          "performance": {
            "action": "holds and reads the chart with one thumb tightening on its edge",
            "emotion": "contained worry",
            "energy": "low but tense",
            "beatEnergy": "low",
            "silentFrameVerb": "hide",
            "ongoingOccupation": "checks the chart before the doctor enters",
            "performanceFamily": "ongoing-occupation",
            "bodyLine": "slight forward curve toward the chart",
            "weightDistribution": "70 percent on the bed-side leg",
            "facialExpression": "brow pinched, mouth held closed",
            "handBusiness": "right thumb presses the chart edge",
            "gestureMotivation": {
              "leftHand": "supports the chart weight",
              "rightHand": "holds the page edge while reading"
            },
            "namedSupport": "floor-01",
            "socialTerritory": "bedside clinical work zone",
            "costumeState": "on-duty 1928 nurse uniform, sleeves neat",
            "holdPoseValidity": "pass",
            "tenSecondHold": "pass",
            "depthHonesty": "pass"
          }
        }
      ]
    }
  ]
}
```

Run:

```powershell
python scripts/scene_staging_tools.py validate-directing-timeline timeline-directing.json
```

For later snapshots, an enter event must add exactly its `actorId`; an exit event must remove exactly its `actorId`. During uninterrupted presence, `poseId`, `transformId`, `placementId`, and `affordanceZoneId` are immutable.

## 3. Validate and render scene affordances

```json
{
  "schema": "ndc-scene-affordance/v1",
  "sceneSize": [2560, 1600],
  "zones": [
    {
      "id": "stand-bedside-01",
      "polygon": [[1160, 920], [1510, 920], [1590, 1490], [1080, 1490]],
      "capabilities": ["stand"],
      "depthClass": "midground"
    },
    {
      "id": "sit-chair-01",
      "polygon": [[1740, 820], [2040, 820], [2070, 1320], [1690, 1320]],
      "capabilities": ["sit"],
      "depthClass": "midground"
    }
  ],
  "supportSurfaces": [
    {
      "id": "floor-01",
      "evidence": "visible floor line verified against the depth/model reference",
      "occupancy": {"status": "clear", "evidence": "no loose object occupies the contacts"},
      "contacts": [
        {
          "regions": ["leftFoot", "rightFoot"],
          "polyline": [[1160, 1360], [1510, 1360]],
          "tolerancePx": 4
        }
      ]
    }
  ],
  "placements": [
    {
      "actorId": "nurse",
      "placementClass": "standing",
      "anchor": [1320, 1360],
      "zoneId": "stand-bedside-01",
      "supportObjectId": "floor-01"
    }
  ]
}
```

```powershell
python scripts/scene_staging_tools.py validate-affordance affordance.json
python scripts/scene_staging_tools.py render-affordance affordance.json affordance-review.png --base scene.png
```

Zone polygons constrain the anchor on a real support region; they do not describe the actor's vertical body envelope. After the exact placement contract exists, calculate independent scene contact evidence:

```powershell
python scripts/scene_staging_tools.py validate-support-contact affordance.json placement.json `
  --report support-contact.json `
  --preview support-contact.png
```

The preview draws scene-authored support lines in cyan. Each named contact is green when its signed vertical difference is within tolerance; floating or sinking contacts are red with the pixel gap. Codex must visually confirm that the cyan line matches the fixed scene/depth support. The production ledger requires one passing `ndc-support-contact-report/v1` per exact pose ID.

Every support surface requires `occupancy.status: clear|occupied`. An occupied surface requires the item, logical destination, reason, old-location repair mask, and destination mask. A chair, bed, door, railing, or other fixed structure never enters the scalable actor component; only the loose item and its two minimum change regions do.

## 3.1 Validate fixed-scene absolute scale

Create `ndc-scene-absolute-scale/v1` with at least three unique `independenceGroup` values. Include both `horizontal` and `vertical` axes plus `actor-local` and `cross-depth` bands. Each anchor stores `measurementLine`, `realWorldRangeCm`, `assumedCm`, `projectionScaleToActorPlane`, confidence, and projection evidence. The command recomputes the line length instead of trusting a typed pixel value.

```powershell
python scripts/scene_staging_tools.py validate-scene-absolute-scale scene-scale.json `
  --report scene-scale-report.json --preview scene-scale-overlay.png
```

The report's `recommendedGlobalScaleFactor` is a diagnosis. A value outside the declared unit tolerance fails and sends all actors back to the depth/whitebox stage. Do not apply it to extracted RGBA layers. The overlay is mandatory because a mathematically consistent report built from the wrong door base, window span, bed edge, or support point is still invalid evidence.

## 3.2 Validate same-scene cast scale

After every actor has a canonical height and final support point, create one shared scene contract:

```json
{
  "schema": "ndc-cast-scale/v2",
  "sceneSize": [2560, 1600],
  "horizonY": 620,
  "referenceActorId": "nurse",
  "maxDeviationRatio": 0.05,
  "maxHeadDeviationRatio": 0.05,
  "headScalePriority": true,
  "perspectiveEvidence": "floor-grid convergence verified against the aligned depth plane",
  "actors": [
    {
      "actorId": "nurse",
      "placementContract": "nurse-placement.json",
      "identityScaleReference": {
        "referenceArtifact": "approved-nurse-card.png",
        "referenceFullBodyHeightPx": 1180,
        "referenceAnatomicalHeadHeightPx": 154,
        "measurementMethod": "approved-card-front-view",
        "confidence": "high"
      }
    },
    {
      "actorId": "doctor",
      "placementContract": "doctor-placement.json",
      "identityScaleReference": {
        "referenceArtifact": "approved-doctor-card.png",
        "referenceFullBodyHeightPx": 1240,
        "referenceAnatomicalHeadHeightPx": 150,
        "measurementMethod": "approved-card-front-view",
        "confidence": "high"
      }
    }
  ]
}
```

```powershell
python scripts/scene_staging_tools.py validate-cast-scale cast-scale.json `
  --report cast-scale-report.json
```

The validator first derives each approved identity's anatomical head/full-body ratio, predicts the whitebox head height at its locked body scale and depth, and checks every actor plus every head-height pair. It then uses canonical height and support-point depth to check standing-equivalent body height and every body-height pair. Head checks are primary: a body-only pass is a failure. This report proves relative cast consistency only and cannot replace the preceding absolute-scale report.

## 4. Generate and rank blocking candidates automatically

The browser editor is not the main authoring path. Codex creates a blocking request and runs the deterministic candidate builder first:

```json
{
  "schema": "ndc-blocking-request/v1",
  "scene": "scene.png",
  "sceneSize": [2560, 1600],
  "actorId": "nurse",
  "placementClass": "standing",
  "standingEquivalentHeightPx": 720,
  "affordanceContract": "affordance.json",
  "zoneId": "stand-bedside-01",
  "posePresets": ["attentive-task", "guarded-hold", "reach-target"],
  "facing": "right",
  "gazePoint": [1550, 610],
  "actionTarget": [1510, 820],
  "uiSide": "left",
  "uiReferences": {"left": "D:\\PMH\\工作\\对话构图参考-左.png"},
  "performance": {
    "action": "reads the chart while concealing concern",
    "gazeTarget": {"type": "scene-object", "id": "chart-01"},
    "leftHandAction": "supports the chart",
    "rightHandAction": "thumb tightens on the chart edge",
    "supportObject": "floor-01",
    "beatEnergy": "low",
    "silentFrameVerb": "hide",
    "ongoingOccupation": "checks the chart before the doctor enters",
    "performanceFamily": "ongoing-occupation",
    "gestureMotivation": {
      "leftHand": "supports the chart weight",
      "rightHand": "holds the page edge while reading"
    },
    "namedSupport": "floor-01",
    "socialTerritory": "bedside clinical work zone",
    "tenSecondHold": "pass",
    "depthHonesty": "pass",
    "requiredProps": ["chart-01"]
  },
  "maxCandidates": 8
}
```

```powershell
python scripts/scene_staging_tools.py build-blocking-candidates blocking-request.json blocking-candidates
```

The builder derives candidate anchors inside the selected affordance polygon, synthesizes repeatable anatomical landmarks from performance presets, overlays the real UI, rejects incompatible inputs, and ranks candidates by face/hand UI safety, action-envelope obstruction, and action-target distance. It writes one JSON and preview per candidate, a contact sheet, and a report.

The score is deliberately not a final artistic verdict. Codex reviews story readability, performance naturalism, support, perspective/scale, occlusion, and entrance-path logic, edits the selected JSON if needed, and reruns all gates. Record the request hash and chosen pose ID.

Supported deterministic presets currently include `attentive-task`, `guarded-hold`, `reach-target`, `enter-walk`, `lean-observe`, `seated-engage`, and `lying-rest`; placement class still determines the anatomical model. Add new reusable presets only after a concrete scene exposes a repeatable need.

## 5. Prepare the local three-reference generation handoff

After the combined whitebox gate passes, create one handoff per actor presence:

```json
{
  "schema": "ndc-local-generation-handoff/v1",
  "actorId": "nurse",
  "poseId": "room-nurse-hold-chart-v1",
  "scene": "scene.png",
  "whiteboxComposite": "whitebox-beat-01.png",
  "characterCard": "nurse-card.png",
  "actorBBox": [1080, 450, 1510, 1420],
  "cropPaddingPx": 180,
  "generationAspectRatio": [4, 5],
  "outputMode": "contextual-local-replacement",
  "generationPrompt": "Base on Image 1 and replace only the reviewed whitebox with the approved nurse from Image 3..."
}
```

```powershell
python scripts/scene_staging_tools.py prepare-local-generation-handoff local-handoff.json local-handoff
```

Before this command, isolate the accepted actor's anatomical 3D mannequin as a process-only RGBA guide and composite it onto the untouched original-color scene at the locked registration. Visually reject any clipped silhouette, fringe, missing prop envelope, moved contact, or altered source pixels. The input called `whiteboxComposite` for new production is this original-scene-plus-isolated-3D-mannequin overlay, not the globally neutralized 3D room and never a stick/joint/programmatic-block image. The command verifies that the full scene and overlay share the original canvas, expands the padded actor region to `generationAspectRatio` using original pixels only, then writes `image-1-local-whitebox.png`, `local-clean-reference.png`, and `local-generation-handoff.json`. The report records Image 1/2/3 roles, hashes, requested/actual crop ratio, crop policy, original/local actor boxes, crop box, and Photoshop paste top-left. Choose the ratio from the action envelope and support/context needs: standing is often portrait, seated interaction may be square/wider, and lying normally needs landscape. Choose padding large enough to include named support, action target, nearby scale sanity object, relevant occluders, and local light context without turning Image 1 back into an unconstrained whole-scene redraw.

The first generated local result is an in-place contextual replacement and is not a delivery background. Compare it against Image 3 for identity/style and Image 1 for pose/scale/contact/light. Only after those checks pass may extraction use one uniform scale plus translation for mechanical registration. If generation misses a correct whitebox, regenerate; if the result matches the whitebox but still reads at the wrong scene scale, return to the depth/scale/whitebox stage. Record any allowed transform; never use nonuniform scaling, warping, or registration to fix the wrong action or wrong template.

## 6. Validate actual UI obstruction

Each snapshot first selects one applicable `uiSide` from the two mutually exclusive UI candidates. The contract below validates the selected side only; generating two reports for the same unchanged snapshot is optional diagnostic evidence and must not become a dual-side delivery gate.

## 6a. Validate conservative alpha coverage and edge RGB

After the contextual RGB and semantic/background-removal result are approved, use `scripts/conservative_matte.py` when the returned file contains a baked light-neutral checker. A manual polygon is only an authorized-region bound and is forbidden as the final alpha.

```powershell
python scripts/conservative_matte.py checker-cutout.png actor.rgba.png `
  --report actor-matte-report.json `
  --preview-prefix actor-matte
```

The tool flood-fills only border-connected neutral pixels, retains enclosed light actor pixels, expands foreground rather than eroding it, and writes black, white, and dark scene-tone previews. Its v2 report separately audits neutral RGB contamination on retained edges and returns only `TECHNICAL_FILE_PASS/FAIL`. Codex must still compare all previews with the contextual source and reject missing silhouette content or visible gray/white rims.

## 6aa. Record mandatory stage-by-stage visual review

Every generated or transformed image requires a separate `ndc-stage-visual-review/v1` contract. Run:

```powershell
python scripts/visual_review_gate.py visual-review.json visual-review-output
```

Stages are `exact-pose-whitebox`, `contextual-local-result`, `matte-extraction`, `pre-composite-registration`, and `final-full-composite`. Put the image being judged first in `artifacts`, then add the untouched scene, accepted local result, whitebox/depth reference, matte previews, or prior stage as comparison artifacts. Add `localTiles` for every actor, action, contact, edge, and overlap region. Codex must open the generated board before completing `checks`, `observations`, and `decision`.

The tool validates the evidence and renders the board; it never converts measurements into an artistic decision. A `VISUAL_REVIEW_FAIL` blocks the next step. The post-generation production ledger must reference a passing report for all five stages. Stages containing an actor in physical contact also require `environmentResponse`: visually verify the expected deformation, displacement, load, wrapping, overlap, and contact shadow in soft/supporting/movable objects. Coordinate contact without a corresponding environmental response is a failure.

For `exact-pose-whitebox`, the primary artifact is the character-preview 3D anatomical mannequin whitebox and comparison artifacts include the generated empty-scene depth image and untouched scene. The scene stays white/light gray; every simultaneous actor uses a recorded, stable, mutually distinct matte color with enough saturation and hue separation for local extraction. Stick skeletons, joint diagrams, or programmatic geometry-block mannequins are forbidden in new production and cannot be listed as review evidence. Every actor's complete anatomy must remain inspectable. If bedding, clothing, furniture, or another actor will obscure limbs in the final frame, the 3D review image must expose those limbs through a transparent/ghosted/cutaway support layer; a partial mannequin whose missing anatomy is represented only by an occluding mound cannot pass `supportContact` or `environmentResponse`.

## 6b. Validate component policy and final gaze

Run `validate-component-policy` on both the planned and final layer manifests. `structuralSceneObjectIds` may occur only in `source-occluder` layers with `sourcePolicy: exact-source-pixels` and `uniformScale: 1`. Every loose-object relocation must reference an old-location repair layer, a new-location layer, and two existing masks.

```powershell
python scripts/scene_staging_tools.py validate-component-policy component-policy.json --report component-policy-report.json
```

At final composite size, annotate each eye center, visible face-direction point, named target point, pose ID, and angular tolerance. Run:

```powershell
python scripts/scene_staging_tools.py validate-gaze-conformance gaze.json --report gaze-report.json
```

This geometric report does not infer eye direction automatically; it prevents a visually reviewed landmark annotation from disagreeing with the directing target while a stale text contract still says `pass`.

```json
{
  "schema": "ndc-ui-safety/v1",
  "scene": "scene.png",
  "sceneSize": [2560, 1600],
  "uiReferences": {
    "left": "D:\\PMH\\工作\\对话构图参考-左.png",
    "right": "D:\\PMH\\工作\\对话构图参考-右.png"
  },
  "maskThreshold": {"backgroundRgb": [255, 255, 255], "tolerance": 12},
  "limits": {"maxHeadOcclusionRatio": 0.0, "maxActionOcclusionRatio": 0.20},
  "actors": [
    {
      "actorId": "nurse",
      "uiSide": "left",
      "headBBox": [1220, 470, 1340, 620],
      "actionBBox": [1080, 450, 1510, 1420],
      "criticalPoints": [
        {"name": "rightHand", "point": [1370, 830]},
        {"name": "chart", "point": [1325, 760]}
      ]
    }
  ]
}
```

```powershell
python scripts/scene_staging_tools.py validate-ui-safety ui.json --report ui-report.json --preview ui-preview.png
```

The preview uses the real reference pixels. A conceptual two-thirds estimate is not a PASS. The obstruction mask counts only visible, non-background UI pixels: fully transparent padding is ignored regardless of its stored RGB. When adapting a 2560 px UI reference to a wider panoramic scene, expand onto a transparent canvas and preserve the source alpha; never fill the extension with opaque white or black. Open the rendered UI preview after every canvas adaptation—an opaque blank region or a preview without the scene is evidence of an invalid UI gate, not a safe layout.

## 7. Validate exploration idle/active states

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
    "reason": "the click redirects attention without changing support"
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

`assemblyMode` may be `registered-complete-state`, `registered-local-patch`, or `exact-master-canvas`. A registered complete state allows a natural whole-body action change but still requires the same runtime canvas, support contacts, transform, and placement; it never permits a horizontal body splice.

```powershell
python scripts/scene_staging_tools.py verify-exploration-states states.json idle.png active.png --output-dir state-review
```

The output contains a difference image, half-blend overlay, flicker GIF, and machine report. Codex must still visually review identity, support/shadow continuity, state readability, silhouettes, and flicker jumps.

## 11. Validate production evidence coverage

Every batch and every formal single-scene run requires a production ledger. This gate prevents a flat asset manifest, a filename convention, or a weak technical QA script from bypassing the directing and whitebox chain.

```powershell
python scripts/production_gate.py production-ledger.json --report production-ledger-report.json
```

The ledger schema is `ndc-scene-integration-production-ledger/v2` and its `stage` is `pre-generation` or `post-generation`. Each case records the source-scene hash, runtime branch, engineering/directing evidence, affordance contract, real UI reports, an independent fixed-scene absolute-scale report, cast-relative scale report, one support-contact report per exact pose ID, component-policy reports, reviewed whiteboxes, and local-generation handoffs. Post-generation additionally requires gaze-conformance, matte-v2, and formal conformance reports. Exploration cases also record the idle-master state pair and explicitly set `statesIndependentlyNormalized: false`.

Narrative entry checks must name the entry path and visible portal state. A visible closed door cannot be accepted as an entry route unless the snapshot includes an `opened-during-transition` state. `technicalStatus` is limited to `NOT_RUN`, `TECHNICAL_FILE_PASS`, or `TECHNICAL_FILE_FAIL`; the file-check layer may never emit artistic `PASS`.

The evidence gate returns `EVIDENCE_GATE_PASS`. This means the required evidence chain is present and internally named correctly; it does not replace Codex visual review or user batch approval.

## 8. Render the incremental timeline board

After each simultaneous-cast whitebox snapshot is rendered, create:

```json
{
  "schema": "ndc-timeline-board/v1",
  "sceneSize": [2560, 1600],
  "uiReferences": {
    "left": "D:\\PMH\\工作\\对话构图参考-左.png",
    "right": "D:\\PMH\\工作\\对话构图参考-右.png"
  },
  "snapshots": [
    {"id": "beat-01", "image": "whitebox-beat-01.png", "uiSide": "left", "caption": "Nurse holds chart before doctor enters"},
    {"id": "beat-02", "image": "whitebox-beat-02.png", "uiSide": "right", "caption": "Doctor enters; nurse remains frozen"}
  ]
}
```

```powershell
python scripts/scene_staging_tools.py render-timeline-board timeline-board.json timeline-board
```

Read the contact sheet in order. Each frame must pass the silent-frame statement, and no pose may anticipate a future entrant.

## 9. Visual pose/blocking editor fallback

Codex normally uses the automatic candidate builder and direct JSON edits. Open `scripts/pose_blocking_editor.html` locally only when visual inspection or a small final adjustment is faster and safer than editing coordinates. Load the selected generated candidate, fixed scene, and applicable left/right UI reference; adjust anatomical joints, head box, action box, or gaze target, then export the revised fragment.

The editor is a reproducible inspection/fine-adjustment aid, not the primary workflow and not work that should normally be delegated to the user. Its fragment must still be combined with the directing timeline, affordance, UI, scale, support, occlusion, and whitebox contracts.

## 10. Project-asset regression baseline

Inventory the current read-only NPC/background assets and actual UI shapes without treating them as blanket artistic approvals:

```powershell
python scripts/scene_staging_tools.py audit-project-assets `
  --npc-loop-table D:\PMH\ndc\NDC\Assets\table\NPCLoopData.json `
  --asset-root D:\PMH\ndc\NDC\Assets\Resources `
  --background-root D:\PMH\ndc\NDC\Assets\Resources\Art\Scene\Backgrounds `
  --ui-left D:\PMH\工作\对话构图参考-左.png `
  --ui-right D:\PMH\工作\对话构图参考-右.png `
  --output D:\Codex\NDC\工作过程文件\人物入景回归\project-baseline.json
```

The report records every configured idle/active path, coordinate, existence, canvas, alpha/corner state, hash, background inventory, and UI obstruction extent. Use `--strict` to fail missing state assets or idle/active canvas mismatches.

On a later audit, add `--baseline <previous-report.json>`. The comparison lists added, removed, and modified logical NPC/background/UI entries. A hash or dimension change is a review trigger, not an automatic failure and not visual approval.
