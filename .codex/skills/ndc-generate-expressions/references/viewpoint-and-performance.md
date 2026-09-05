# Viewpoint lock and expression performance

## Core distinction

Expression production must separate **camera/viewpoint continuity** from **performance continuity**.

The approved portrait fixes the camera/viewpoint family for the entire expression set. It does not freeze the character into a rigid mannequin pose. A readable performance may use small, expression-motivated motion in the shoulders, neck, head tilt, gaze, upper torso, and clothing response while the image still reads as the same portrait viewpoint.

## Absolute viewpoint lock

Freeze from the user-approved original portrait:

- `view_family`: `front`, `three_quarter_left`, `three_quarter_right`, `profile_left`, or `profile_right`;
- visible side and foreshortening pattern of the face;
- base head-yaw family and nose/cheek/ear perspective;
- camera height, projection, lens impression, and image-plane orientation;
- base bust facing direction and crop logic;
- approved-portrait absolute path and SHA-256.

No expression-generation retry, character card, style fallback, background-removal operation, or profile normalization may change these items. A subtle head tilt or gaze change may occur without crossing into another view family. A three-quarter portrait must remain the same three-quarter side; it cannot be rebuilt as front-facing merely to match a generic guide.

If a different viewpoint is narratively required, record a separate user-approved `viewpoint_exception`. `pose_exception` alone never authorizes a camera/viewpoint change.

## Allowed performance deltas

For `basic_emotion`, `micro_expression`, and `narrative_state`, allow only small, motivated deltas that reinforce the requested expression:

- slight shoulder lift, drop, rotation, contraction, or asymmetry;
- slight torso lean, recoil, settling, guarded closure, or opening;
- slight neck or head tilt that preserves the same yaw/view family;
- subtle gaze adjustment consistent with the expression;
- passive clothing response such as lapel tension, collar displacement, wrinkle compression, or fold relaxation caused by the body motion.

These changes must remain subordinate to the expression and preserve identity, body type, costume design, garment materials, hairstyle, lighting language, and approved view family. Do not add a new prop, replace clothing, invent an action, rotate the body into a new facing direction, or change the camera.

For `action_state`, larger body/action deltas still require `pose_exception=true` and exact narrative evidence. The camera/viewpoint remains locked unless the user separately approves `viewpoint_exception=true`.

## Manifest record

Record one viewpoint lock per character and one performance plan per expression:

```json
{
  "viewpoint_lock": {
    "approved_portrait": "{JOB_PAYLOAD}/user-approved-portrait.png",
    "approved_portrait_sha256": "64-lowercase-hex",
    "view_family": "three_quarter_right",
    "viewing_side": "subject turned toward camera-right",
    "camera_height": "eye-level",
    "projection": "portrait-normal",
    "status": "PASS"
  },
  "performance_delta": {
    "shoulders": "slight inward contraction",
    "upper_torso": "subtle guarded lean",
    "head_neck": "minor downward tilt; yaw family unchanged",
    "gaze": "slightly lowered while remaining readable",
    "garment_response": "small lapel compression from shoulder movement",
    "viewpoint_change": false
  }
}
```

Use `none` when a region should remain neutral. Do not write generic blanket values for a whole batch; every state must reflect its actual performance need.

## Review gate

Compare approved portrait, completed neutral master, and native candidate at matched scale. Set `VIEWPOINT_CONTINUITY_GATE=PASS` only when:

- the approved portrait remains the authority and is not replaced by the master;
- view family, viewing side, facial foreshortening, camera height, and projection agree;
- any head/neck/shoulder/torso/clothing changes are small, motivated, and recorded;
- no performance delta disguises missing anatomy or a crop boundary;
- profile normalization only scales and translates the complete candidate and does not alter its view.

Record `viewpoint_status`, `performance_delta_status`, and reviewer evidence per expression. A mechanical head box, centered face, or character-card front view cannot pass this gate.
