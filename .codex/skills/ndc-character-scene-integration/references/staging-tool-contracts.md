# Staging tool contracts and commands

For repairable whitebox defects, follow [PS-first repair](ps-first-repair.md) and [whitebox repair](whitebox-photoshop-fallback.md) from the first useful candidate. PS MCP repair may precede acceptance, including process-only separation of complete mannequin components. After repair, rerun the same current-pose scale, support, UI, visual and production gates described here; no filename or PS export grants readiness. Record up to three complete PS repair/review rounds separately from model calls; do not consume all three model attempts merely to enter PS.

Use the tools in `scripts/scene_staging_tools.py` within the relevant workflow milestone. All authored JSON is strict JSON. Runtime reports and diagnostic previews stay under `D:/Codex/NDC/工作过程文件`. Within an authorized task, assets that pass all current visual and technical gates can be archived formally without an additional routine user-approval wait.

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

New work uses `ndc-scene-absolute-scale/v2` as one shared scene register. Height calibration and horizontal footprint checks are separate. Existing v1 contracts remain readable through a compatibility validator; an old report is never relabelled as a v2 PASS. When its source scene and contract hash are still current, v1 is rechecked with vertical anchors only for height and any horizontal measurement as a footprint diagnostic. Missing v2 fields or `directionTransfer` alone never requires a new whitebox or a fabricated evidence file.

```powershell
python scripts/scene_staging_tools.py validate-scene-absolute-scale scene-scale.json `
  --report scene-scale-report.json --preview scene-scale-overlay.png
```

The same command selects the validator from `schema`; the v2 implementation is [scene_scale_v2.py](../scripts/scene_scale_v2.py). It returns `ndc-scene-absolute-scale-report/v2`, with `metric-pass` or `bounded-pass`. Invalid evidence raises `SCENE_GEOMETRY_BLOCKED`; it does not write a passing report.

### Shared v2 fields

All file references are `{path, sha256}` and must resolve to current files. Prefer absolute paths. Required fields are:

| Field | Content |
|---|---|
| `schema`, `mode` | `ndc-scene-absolute-scale/v2`; `metric` or `bounded` |
| `scene`, `sceneSha256`, `sceneSize` | Actual source path, current hash and original canvas size |
| `depthReference` | Current scene-authored depth/support evidence image; not inferred from current actor joints |
| `referencePlaneId` | The named common plane used by the shared height anchors |
| `supportPlanes` | Unique `supportPlaneId`, current geometry `evidence` reference and `footprintAnchorIds`; metric additionally has `projectionScaleFromReference`, with the reference plane exactly 1 |
| `actors` | Full planned actor/pose units: unique `actorId`, `supportPlaneId`, `placementSnapshot` reference; bounded also supplies `boundedRanges` |
| `anchors` | Unique `anchorId`, distinct `objectId` and `independenceGroup`, `axis`, explicit `role`, actual `measurementLine` endpoints and current `evidence` reference |

An immutable `placementSnapshot` contains the actual scene, sceneSize, characterHeightCm and complete target/pose/foot/head/action envelope, including `target.supportPlaneId`. It has no `calibration.sceneScaleEvidence` reference: native support and head checks use this independent snapshot, avoiding a registry↔placement hash cycle. Final placement adds `calibration: {sceneScaleEvidence: <current report ref>, actorId: <registered unit>}` and retains exactly that geometry. A changed pose, foot, support, height or source invalidates the binding. Metadata-only delivery fields remain separate.

For one character with several poses, keep one full-scene case and shared report. Use distinct registered pose-unit IDs such as `Emma__sit_v1` and `Emma__stand_v2`, each bound to its own `placementSnapshot` and native `poseId`; keep `placement.characterName` as the original character name. Each snapshot's `actorPoseIds` lists only the units actually present at that time. Do not split these units into fresh scene cases or budgets: map them back to the original character/interaction cost unit and retain its cumulative attempts. Bounded sensitivity covers every registered pose unit; mutually exclusive poses may use an inspected multi-frame timeline comparison and must never be described as simultaneous characters. A changed snapshot requires new current evidence, not a renamed historical PASS.

### Metric mode: height-calibration and footprint-check

Use at least **two independent vertical** `role: height-calibration` anchors, one `actor-local` and one `cross-depth`, each of medium/high confidence, plus at least one independent horizontal `role: footprint-check`. Heights store `realWorldRangeCm`, `assumedCm`, `projectionScaleToReferencePlane`, `projectionEvidence.perspectiveBasisIds`, and source/target support points for cross-depth transfer. Furniture facts are recorded once; additional actors reuse the shared plane rate. A new support plane adds a justified projection and local footprint, not another copy of the furniture measurements.

The validator recomputes line lengths and takes the confidence-weighted median of **height-only** `lineLength × projectionScaleToReferencePlane × directionScaleToVertical / assumedCm`. Each actor's expected image height is that rate × its support-plane projection × canonical height. `limits.maxAnchorSpreadRatio` and `maxGlobalDeviationRatio` default to 0.08; the prior ceilings 0.35/0.25 remain. Head/cast and support checks remain separate.

Footprint anchors have `axis: horizontal`, `role: footprint-check`, and `usableXRange: [left,right]` contained within the measured horizontal span. Every actor action envelope must stay inside its plane's referenced footprint. This checks projected occupation width; it does not measure vertical human height or prove foot contact. The original support/UI/occlusion checks still apply.

Depth projection does not convert a horizontal world direction into a vertical height ruler. An **additional** horizontal `height-calibration` anchor still requires `projectionEvidence.directionTransfer`; it cannot replace either of the two vertical anchors:

```json
{
  "method": "Describe the calibrated camera or independently established metric reference, its direction and assumptions",
  "sourceAxisPxPerCm": 0.5,
  "verticalPxPerCm": 1.0,
  "artifact": {"path": "actual-metric-evidence.json", "sha256": "actual-current-sha256"}
}
```

The rates refer to the same support depth and measurement extent; the numbers illustrate a synthetic conversion, not a scene default. Document the actual camera/reference calculation and inspect its source-bound overlay. A ground-plane homography alone does not establish vertical height. Without direction evidence use a footprint anchor; if metric prerequisites are unavailable, evaluate the bounded branch without inventing a conversion.

Historical v1 retains its original report schema but not its incorrect cross-axis vote. The compatibility validator requires at least two independent vertical anchors spanning actor-local and cross-depth, and uses only `lineLength × projectionScaleToActorPlane × characterHeightCm / assumedCm` for its legacy height factor. A horizontal v1 anchor remains a separately identified footprint diagnostic; an existing `directionTransfer` is hash-checked for audit but cannot change the height factor, while a missing one is not a blocker. The production ledger binds the v1 contract to the same current source scene, then relies on current placement, cast/head, support, UI and whole-scene reviews for current whitebox geometry. Upgrade to v2 only when current work genuinely needs the shared register; migrate existing measurements deterministically and never regenerate a whitebox solely to fill schema fields.

The metric report's `recommendedGlobalScaleFactor` is diagnostic. A value outside tolerance fails; once the support basis is sound, correct affected actors from original complete layers under PS-first and update affected evidence. Inspect the source overlay: a consistent calculation from the wrong door base or support point is still invalid geometry.

### Bounded mode: real evidence before continuation

Bounded mode keeps the source/depth/plane/actor/footprint fields above but does not require imaginary metric height anchors or exact projection factors. First inspect provisional complete whiteboxes; then freeze the chosen pose snapshot and complete the following `boundedEvidence`. These are references to existing checks and actual sensitivity inspection, not additional model attempts or a second artistic approval system:

- `assumptions`: nonempty unique `{id, statement, evidence}` records identifying observed facts, inferred regions and remaining assumptions.
- Each actor's `boundedRanges`: `heightPx: [low,high]`, `footX: [low,high]`, `footY: [low,high]`. The current reviewed snapshot must lie inside. A height range wider than 20% of that reviewed height is unresolved and blocked.
- Top-level `snapshots`: all `{snapshotId, actorPoseIds: {actorId: poseId}}`. `boundedEvidence.isolatedActors` maps every actor to its complete whitebox reference; `combinedSnapshots` maps every snapshot to its actual whole-scene image. `visualReviewReports` use current native `exact-pose-whitebox` reports with full pose/snapshot coverage, source-scene binding and whole/local inspection.
- `supportChecks`: every actor maps to `{affordance, report}` references. The validator reruns native support against its immutable pose snapshot and requires the saved report to match the current result.
- `castScaleCheck: {contract, report, dependencies}`: rerun the native full-cast v2 head-priority check on those snapshots; hash all actual identity-card dependency images. Head and pairwise tolerances remain at most 0.20. Its horizon/depth model remains a declared bounded assumption, not evidence of exact camera recovery.
- `uiCheck: {contract, report, dependencies}`: rerun the actual UI-mask check, bind the current action and anatomical head boxes and hash the referenced real UI images. The saved report must match the current result.
- `sensitivityCases`: at least two actual `{id, assumption, artifact, review, actors}` outcomes. Each actors map contains the full cast with `standingEquivalentHeightPx`, `foot`, `supportPlaneId`, `affordanceZoneId`. Their minima/maxima must cover every declared bound. Distinct outcomes need distinct inspected images; do not make duplicate screenshots or re-author an old PASS to represent a second test.
- Sensitivity reviews use the same native full/local whitebox schema with additional actual judgments `boundedRangeJustified`, `boundedPlacementInvariant`, `boundedSupport`, `boundedHeadScale`, `boundedUIReadability`. Every applicable check must be `pass`; the full current cast and scene must be bound to the reviewed images. A changed support plane/usable zone is rejected mechanically; uncertainty that changes placement, contact, head relationships or UI must be rejected by the actual inspection too.

`bounded-pass` outputs only ranges and the chosen reviewed pixel geometry. It contains no recommended metric scale factor and cannot claim an exact hidden foot or calibrated horizon. A boolean, explanatory text alone, a missing report or a stale underlying image cannot pass. This mode does not replace final whole-scene visual acceptance or increase any model/PS budget.

### Production consumption

`production_gate.validate_ledger` keeps its original outer `EVIDENCE_GATE_PASS` result. For v2 it reruns the source-bound register once, compares the stored report to the recomputed result, verifies every placement references that same register and exact actor scope, and continues all original support, cast, whitebox, visual, timeline and post-generation gates. It does not return early on `metric-pass` or `bounded-pass`. One staging command likewise reuses a validated shared register within that command, while a later invocation checks current sources again.

## 3.2 Validate same-scene cast scale

After every actor has a canonical height and final support point, create one shared scene contract:

```json
{
  "schema": "ndc-cast-scale/v2",
  "sceneSize": [2560, 1600],
  "horizonY": 620,
  "referenceActorId": "nurse",
  "maxDeviationRatio": 0.05,
  "maxHeadDeviationRatio": 0.20,
  "maxPairwiseHeadDeviationRatio": 0.20,
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

### Elevated lying depth: cast-scale v3

`target.foot` remains the authored physical support/contact anchor for historical compatibility. It is not automatically a ground-depth point when `placementClass` is `lying`. Every new or revised scene containing a lying actor uses `ndc-cast-scale/v3`; all actor entries explicitly add `depthProjection`:

```json
{"mode": "ground-support-point"}
```

This mode is valid for a lying actor only when the placement explicitly records `target.supportPlaneClass: "ground"`. For a bed, sofa, stretcher, examination table or other elevated support, use:

```json
{
  "mode": "elevated-support-projection",
  "contract": {"path": "patient-depth.json", "sha256": "<current hash>"}
}
```

The referenced contract is fail-closed:

```json
{
  "schema": "ndc-elevated-support-projection/v1",
  "scene": {"path": "scene.png", "sha256": "<current hash>"},
  "sceneSize": [2560, 1600],
  "actorId": "patient",
  "poseId": "patient-lying-r3",
  "placementContract": {"path": "patient-placement.json", "sha256": "<current hash>"},
  "supportPlane": {
    "supportPlaneId": "bed-mattress",
    "supportObjectId": "bed-01",
    "supportPoint": [1660, 1015],
    "evidence": {"path": "bed-plane-evidence.png", "sha256": "<current hash>"}
  },
  "depthProjection": {
    "mode": "projected-ground-plane",
    "projectedGroundPoint": [1660, 1288],
    "perspectiveBasisIds": ["floor-grid-01", "bed-leg-drop-01"],
    "evidence": {"path": "bed-ground-projection.png", "sha256": "<current hash>"}
  },
  "wholeArtifact": {"path": "whole-lying-whitebox.png", "sha256": "<current hash>"},
  "localArtifact": {"path": "local-lying-whitebox.png", "sha256": "<current hash>"},
  "visualReviewReport": {"path": "exact-pose-whitebox-visual-review-report.json", "sha256": "<current hash>"}
}
```

`depthProjection.mode` may instead be `same-depth-reference` with a nonempty `referenceActorId`. That reference must resolve directly to a current cast actor whose depth comes from a ground support point or projected-ground point; reference chains and cycles fail. The exact-pose review must include both distinct whole/local artifacts for the current `poseId`, plus explicit passing checks `elevatedSupportPlane`, `projectedGroundDepth`, and `wholeLocalConsistency`. The support plane must match `target.supportPlaneId`, its object must appear in an exact `supported-by` scene relation, and the current placement/scene hashes must still match.

The v3 report preserves `supportPoint` and separately emits `depthPoint`/`depthSource`; body and pairwise perspective math uses only `depthPoint`. Never alter `target.foot`, `horizonY`, the identity reference or tolerances just to force a pass. Existing unchanged accepted reuse may retain its historical v2 report; any lying geometry revision enters v3.

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

The first generated local result is contextual replacement, not a delivery background. Compare Image 3 identity/style and Image 1 pose/scale/contact/light before extraction. Follow [production-cadence.md](production-cadence.md) for pixel-preserving extraction, coherent same-image operations and bounded support-anchored uniform corrections. A wrong action/anatomy or uncertain geometry returns to its responsible stage; a suitable layer with a verified placement correction may be transformed in PS, with affected whitebox/placement/contact evidence updated and revalidated. Respect explicit user locks; never use alpha-box fitting, nonuniform scaling or warping to conceal an incorrect pose.

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

## Review version and coverage binding

Before inspection, freeze the current artifact and actual local-view SHA-256 values. View the original whole image at 100% and applicable local views at 200%/original-pixel coverage, then submit findings for those exact versions. The generated comparison board is navigation only: its resized panels do not prove original-resolution review.

Each visual-review contract artifact now requires the fixed `sha256` actually inspected. Put the current reviewed output first in `artifacts`; source scene/card references follow with their own hashes. Scope belongs to actually reviewed target images, not to identity/source references. A binding fragment is:

```json
{
  "artifacts": [
    {"role": "reviewed-composite", "path": "frame.png", "sha256": "<inspected-sha256>", "poseIds": ["actor-a-p1", "actor-b-p1"], "snapshotIds": ["snapshot-1"]},
    {"role": "source-scene", "path": "scene.png", "sha256": "<source-sha256>"}
  ],
  "localTiles": [
    {"id": "body-contact", "bbox": [100, 100, 400, 500], "path": "body-contact-200.png", "sha256": "<inspected-tile-sha256>"}
  ]
}
```

The example box is illustrative, not a scene placement. A local view must cover its declared box and have at least twice that box's pixel dimensions. Preserve the actual inspected tile path/hash; do not declare a tiny board panel as a 200% view. PASS without required local evidence is rejected. The report preserves bindings so the production gate can re-read current images and local views. A changed image or local view invalidates the old conclusion instead of automatically receiving a new hash. A valid explicit visual failure still saves its report but exits nonzero.

Expected pose coverage comes from each placement's `target.poseDefinition.poseId`. Expected snapshot membership comes from staging `timelineSnapshotId`, `characters[*].name`, and `combinedWhiteboxReview.poseIds` mapping each character name to that pose. The required stages must cover the planned poses; whitebox and final composite additionally cover snapshot/pose pairs. A combined view may cover several people or snapshots only if they were actually inspected. This adds scope to existing observations, not a new per-person file or extra review pass.

These checks verify coverage of the authored plan, not completeness of the original story interpretation. Local view dimensions/hashes do not prove that a person actually inspected them. Handoff scene/card hashes are rechecked, while legacy `sourceHashes.whiteboxComposite` has no original full-image path; preserve the existing reviewed full-whitebox/crop mapping rather than falsely compare that hash with cropped Image 1. An optional `sourceReviewRecord` hash binds that record file; it does not replace running the applicable existing stage self-check validator on the current artifact.

Pose/snapshot IDs alone are insufficient: this run's `whiteboxEvidence.isolatedActors` and `combinedSnapshots` image hashes must occur in the exact-pose-whitebox review, and the final contract's `finalComposite` with fixed `finalCompositeSha256` must occur in final-full-composite review. A retained old image/report cannot cover a new different-byte image merely because its pose ID stayed the same. Byte-identical copies at another path may reuse the original genuine observation.

For unchanged real review, preserve observation provenance. Optional `inspectionId`, `reviewedAt` and a hash-bound `sourceReviewRecord` identify a shared inspection or inherited record; never generate a new inspection timestamp merely by rerunning a script. An old report lacking bindings is not automatically accepted: derive them only from existing actual reviewed versions/coverage. If that evidence is absent or user-rejected, inspect the affected current output instead of assigning today's hashes to old PASS.

### Existing non-generative extraction

Do not repeat a successful extraction to satisfy a report schema. The production ledger's `matteReports` may reference this read-only audit wrapper:

```json
{
  "schema": "ndc-matte-readiness-audit/v1",
  "source": {"path": "context.png", "sha256": "<source-sha256>"},
  "output": {"path": "existing-rgba.png", "sha256": "<output-sha256>"},
  "extractionReport": {"path": "actual-extraction-report.json", "sha256": "<report-sha256>"},
  "expectedCanvas": [2560, 1600],
  "visualReviewReport": {"path": "matte-extraction-visual-review-report.json", "sha256": "<visual-report-sha256>"}
}
```

Use the actual declared output canvas, not the example dimensions for every crop. The gate verifies referenced bytes, real RGBA/canvas/nonempty foreground/four transparent corners and a passing matte review containing that exact output. Edge integrity, retained design pixels and residual background still need the existing actual matte visual checks. The wrapper does not infer artistic PASS and does not run extraction again. Preserve the original algorithm report (including a valid green-screen route) rather than rename its schema/status.

## 11. Validate production evidence coverage

Every batch and every formal single-scene run requires a production ledger. This gate prevents a flat asset manifest, a filename convention, or a weak technical QA script from bypassing the directing and whitebox chain.

```powershell
python scripts/production_gate.py production-ledger.json --report production-ledger-report.json
```

The ledger schema is `ndc-scene-integration-production-ledger/v2` and its `stage` is `pre-generation` or `post-generation`. Each case records the source-scene hash, runtime branch, engineering/directing evidence, affordance contract, real UI reports, an independent fixed-scene absolute-scale report, cast-relative scale report, one support-contact report per exact pose ID, component-policy reports, reviewed whiteboxes, and local-generation handoffs. Post-generation additionally requires gaze-conformance, matte-v2, and formal conformance reports. Exploration cases also record the idle-master state pair and explicitly set `statesIndependentlyNormalized: false`.

Narrative entry checks must name the entry path and visible portal state. A visible closed door cannot be accepted as an entry route unless the snapshot includes an `opened-during-transition` state. `technicalStatus` is limited to `NOT_RUN`, `TECHNICAL_FILE_PASS`, or `TECHNICAL_FILE_FAIL`; the file-check layer may never emit artistic `PASS`.

The evidence gate returns `EVIDENCE_GATE_PASS` for structural evidence coverage only. It does not replace Codex's actual visual review and never overrides user rejection. Formal packaging within the authorized task does not need another routine batch-approval stop.

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


## Tilted / lying anatomical head measurement

The spatial headBox remains the actual image-space bounding rectangle for UI, occlusion and containment. Its screen-vertical extent is not anatomical head length after in-plane rotation. Optionally add headAxis to the exact standingPose, seatedPose or lyingPose:

    "headAxis": {
      "crown": [1690, 785],
      "chin": [1599, 774],
      "measurementEvidence": "Current image hash and inspected local view; crown and chin identified on anatomy, excluding hair volume and neck.",
      "projectionReview": "Compare compatible projected anatomical axes; explain visible yaw/pitch and any unresolved foreshortening."
    }

Coordinates above illustrate schema only, not approved SC2206 measurements. Both finite, distinct endpoints must lie inside the real headBox. The validator uses their Euclidean image-space distance and separately reports screenVerticalHeadExtentPx, headMeasurementMethod and the axis evidence. Without headAxis, legacy vertical-box behavior is preserved. Sitting/lying scaleAudit head-height fields use the same selected anatomical measurement. No tolerance or identity scale reference is relaxed.

This fixes in-plane rotation only. It cannot reconstruct hidden skull/chin locations or remove out-of-plane foreshortening. When endpoints or reference comparability cannot be established from current approved images, record uncertainty and return to pose/reference review; do not invent a length to pass. Visual review and all existing scale gates remain mandatory.
# Continuous clear floor support extension

See [continuous-floor-support.md](continuous-floor-support.md) for `referenceKind: continuous-floor-region`, provenance, current review/pose/surface bindings and null pixel-gap reporting. The default fixed-line schema and tolerance are unchanged. This extension is specific to foot contacts on continuous clear floors; it cannot replace a seat, bed or body support line.
