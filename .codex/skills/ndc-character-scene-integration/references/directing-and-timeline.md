# Directing, lifecycle, and performance logic

This reference defines the semantic foundation that must exist before scale, depth, whitebox, generation, or compositing. It applies globally to fixed-camera NDC scenes; it is not hospital-room-specific.

## 1. Route the asset type first

Every request must be classified before interpreting a still frame.

### Exploration NPC

An exploration NPC is present while the player explores and has two runtime states:

- `idle`: a self-sustaining ambient pose before interaction;
- `active`: a visibly different player-engagement pose after click/dialogue start.

The two states share the same runtime placement, canvas, scale, support relationship, and scene logic. They are not two unrelated illustrations. The idle pose must not already perform directly to the player; the active pose must clearly engage the player. Use `verify-exploration-states` for registered full-state or local-patch pairs.

### Pure narrative actor

A pure narrative actor follows the dialogue/script lifecycle. The actor can enter and leave at authored nodes. A still image showing every actor who ever appears is not a valid scene plan.

Build a chronological cast timeline from `SceneConfig`, `Talk`, and `NPCLoopData` before blocking. `SceneConfig.NPCInfos` supplies the configured initial cast; script `13` spawns the `NPCLoopData` record named by `ParameterInt`; script `14` removes the NPC ID named by `ParameterInt`. A dialogue branch must be explicitly selected and recorded; never follow an arbitrary option. Treat the current engine tables as source evidence, not as editable inputs.

## 2. Timeline snapshots, not one timeless cast

For each meaningful node, store:

- cast before and after the node;
- enter, exit, or dialogue event;
- actors that must remain frozen;
- speaker and visible action focus;
- story beat and silent-frame statement;
- UI side active at that node.

An actor is assigned one pose, transform, placement, gaze logic, and costume state for each uninterrupted period of presence. A later entrant may be added, but must not silently change an actor already on screen. If an actor exits and later re-enters, a new presence generation may be authored explicitly.

This incremental rule prevents a common false interaction: an early actor looks, reaches, or reacts toward someone who has not entered yet. It also prevents a later actor from making an earlier actor's otherwise stable asset appear to jump.

## 3. Story-beat contract

Every timeline snapshot requires a concise five-part beat:

1. `objective`: what the active character wants now;
2. `conflict`: what blocks or complicates it;
3. `emotion`: the dominant visible emotional pressure;
4. `subtext`: what must be implied rather than stated;
5. `actionFocus`: the object, person, exit, or task carrying the beat.

Also write one `silentFrameStatement`: what a viewer should understand with dialogue and UI text removed. If this cannot be stated clearly, character placement and acting are not ready.

## 4. Performance contract

Every visible actor must define:

- one `silentFrameVerb` that can be read without dialogue, such as wait, guard, read, hide, leave, or intervene;
- `beatEnergy` as `still`, `low`, `medium`, or `high`;
- the `ongoingOccupation` the actor was already doing before this frozen instant;
- a `performanceFamily`: `ongoing-occupation`, `supported-hold`, `transition`, or `confrontational-action`;
- exact physical action rather than a generic standing label;
- emotional state and energy level;
- body line and weight distribution;
- facial expression only where the approved camera makes it visible; otherwise use readable head, shoulder, and body orientation;
- each hand's visible action or relaxed resting state; an unoccupied hand needs no invented task, prop, grip, or gesture;
- a `namedSupport`, including the floor plane when no furniture bears weight;
- a `socialTerritory` describing the actor's believable work, rest, family, or transit zone in the room;
- gaze target type and target ID;
- costume state appropriate to era, role, location, and immediate story state;
- `tenSecondHold=pass`: the pose remains physically and psychologically credible when held on screen;
- `depthHonesty=pass`: the actor was not enlarged or pushed toward camera merely to improve readability.

Review **story fit and bodily naturalness separately** in the existing performance review. A pose may convey the correct action yet remain stiff. Trace support through feet or furniture, pelvis, torso, shoulders, and arms; joints should form a coherent resting or acting body rather than independently satisfy coordinates. Check whether shoulders, elbows, wrists, and fingers are needlessly tense at the same time. Quiet poses, straight hanging arms, and neutral expressions can be natural. Do not prescribe asymmetry, staggered feet, tilted shoulders, contrapposto, or a large gesture to every actor as a universal cure.

Read the simultaneous cast as a whole before detailed rendering. Different roles such as explaining, listening, observing, and resting should have distinct visible attention and activity when the story calls for them; repeating lowered heads, clasped hands, and tightly held arms can create unintended ceremonial or mourning behavior. Translate the selected intent into camera-visible actions; keep narrative context in the directing contract rather than copying its labels into the image prompt. Record this judgment in the same whole-scene review, without a new report or approval step.

### Choose the performance family before choosing a pose

Use scene affordances and the current beat to enumerate plausible families, then discard incompatible ones:

- `ongoing-occupation`: reading, writing, tending, packing, watching, drinking, waiting, or another action that began before the frozen frame;
- `supported-hold`: sitting, leaning, lying, bracing, or resting against a named scene support;
- `transition`: entering, exiting, crossing, turning, or reaching a destination, only when the current node contains that transition;
- `confrontational-action`: stopping, intervening, recoiling, threatening, or urgent reaching, only when conflict and beat energy require it.

Still and low-energy beats normally use ongoing occupation, attentive rest, or supported hold. Judge gesture size against its visible purpose: a small open-hand explanation can fit a quiet conversation, while a defensive wide stance needs a physical or narrative cause. Do not add motion merely to avoid stiffness, or systematically replace motion with lowered heads, compressed shoulders, or clasped hands. Relaxed unoccupied hands and credible weight distribution may be sufficient.

### Existing actors and state deltas

In pure narrative scenes, an uninterrupted actor's performance is frozen when someone else enters. The entrant may own the transitional or confrontational gesture; existing actors do not acquire a response pose or reciprocal gaze unless the script explicitly creates a later state for them.

For exploration pairs, the active state normally changes attention, head angle, upper-torso orientation, expression, or one local hand action while preserving social territory, scale, support, and runtime transform. Escalate to a larger whole-body delta only when the interaction meaning cannot otherwise read.

### Safe interaction logic

Use one of these gaze targets:

- `scene-object`: a prop or architectural focus already present;
- `player`: only when the state explicitly engages the player;
- `actor`: only when that actor is present in the same snapshot;
- `offscreen`: a stable offscreen event or location, not a future entrant;
- `none`: unfocused or inward attention justified by the beat.

If `reciprocityRequired` is true, both actors must be present and the other actor must return the authored interaction. Incidental shared direction should not be mislabeled as reciprocal acting.

The written target is not final evidence. At the final composite size, use `validate-gaze-conformance` with eye/face geometry only where it is actually visible; for back views or closed eyes use the supported non-numeric review and readable head/body orientation, never invented eye points. Whitebox fine eye direction and expression remain deferred to formal character art under [layered-character-batches.md](layered-character-batches.md). A clearly contradictory visible direction fails even when its JSON names the intended target. A later entrant may look toward a frozen existing actor without forcing that existing actor to reciprocate.

## 5. Scene affordances are acting constraints

The depth image and model image are not only scale references. They describe where an actor can physically:

- walk and stop;
- stand with valid foot contact;
- sit, lie, or lean on a named support;
- reach an object;
- pass behind, in front of, beside, or inside a scene object;
- be partially hidden by a valid occluder;
- enter or exit the fixed frame.

Create polygonal zones with capabilities `walk`, `stand`, `sit`, `lie`, `lean`, `occluder`, or `no-go`. A placement anchor must fall inside a zone supporting its placement class, but polygon membership alone cannot prove physical support. Establish usable space and support depth from the empty scene before deriving actor scale. Seated, lying, and leaning poses require a named support object; soft surfaces must respond to the load rather than remain frozen merely because they came from the original scene.

Choose among physically valid zones by story value: objective access, tension, readable silhouette, depth separation, entrance path, UI safety, and hold-pose credibility. Do not choose a location merely because it has empty pixels.

## 6. Actual UI references replace the two-thirds shortcut

Use `D:\PMH\工作\对话构图参考-左.png` and `D:\PMH\工作\对话构图参考-右.png` as pixel references when available. Derive obstruction from their non-background pixels and check each snapshot's actual UI side.

The two references are mutually exclusive candidates, not simultaneous requirements. After the current cast, story focus, entrances, action envelope, and composition balance are known, Codex selects the lower-cost side, records one `uiSide` for that snapshot, and validates that side only. A later snapshot may select the opposite side when its cast distribution changes. Do not shrink a correctly scaled actor merely to make both UI candidates pass.

The former "opposite two-thirds" rule is only a rough early guess and cannot pass the UI gate. Validate:

- zero UI obstruction over the anatomical face/head box unless explicitly approved;
- zero obstruction over declared critical hand, prop, or interaction points;
- action-envelope obstruction below the contract threshold;
- readable direction of movement and gaze after the UI overlay is visible.

## 7. Candidate blocking and freeze order

For a narrative timeline:

1. block the earliest snapshot with all initially present actors;
2. read the whole low-cost scene preview for story fit, naturalness, affordance, applicable UI, coarse direction, pose, and support before polishing individual actors;
3. freeze accepted actors' pose, transform, placement, and zone IDs;
4. add the next entrant without changing frozen actors;
5. remove exiting actors at their authored nodes;
6. render all meaningful snapshots into a contact sheet;
7. read the sequence silently and reject anticipatory or accidental interactions;
8. use that blocking decision to complete reliable support/depth calibration and structural assets per presence; a provisional preview is not a final scale or support approval.

Do not merge snapshot whiteboxes into one all-cast image when those actors never coexist. A combined whitebox is required for each simultaneous cast snapshot, not for the union of the entire scene timeline.

## 8. Semantic stop conditions

Do not proceed to character generation when any of these is true:

- asset type is unknown;
- timeline is incomplete, cyclic, or has unresolved enter/exit issues;
- a pose depends on a future actor;
- a later entrant changes an existing actor's invariant state;
- the silent-frame statement is unclear;
- a placement lacks the required affordance or support;
- the actual UI reference blocks a face or critical action landmark;
- an exploration idle/active pair lacks a clear interaction-state distinction;
- a pose reads as a neutral mannequin, generic stage line, or theatrical front-facing lineup.
- a gesture's size, direction, or tension contradicts the beat or has no readable purpose;
- the body is stiff despite a semantically correct action, the support is unnamed, or the pose fails a ten-second hold; naturally resting hands are valid;
- the actor was moved toward camera or enlarged merely to make the character easier to read.
- the visible final-size gaze or head/body direction contradicts the named current-snapshot target; do not invent measurements for invisible eyes.

Technical correctness cannot override these semantic failures.
