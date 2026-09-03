# Shadow construction

## Separate the shadow types

1. **Contact shadow:** starts exactly at shoes, seat/body contact, or support contacts. It is short and anchors the actor.
2. **Cast shadow:** projects the actor opposite the dominant light on the receiving plane.
3. **Occlusion shadow:** optional local shadow on a wall, furniture, or prop.

Do not replace all three with a generic polygon under the actor.

## Light and ground contract

Before drawing a cast shadow, record:

- which light actually reaches the actor;
- at least two scene cues supporting its direction, such as existing object shadows, window patches, lamp cones, or architectural occlusion;
- receiving plane and its vanishing directions;
- left/right shoe or support contact points;
- approved direction, length, taper, hardness, and color/alpha.

If the actor stands outside the strong directional light, use contact shadow only or request review. Do not infer a long cast shadow merely because a bright region exists elsewhere in the image.

## Deterministic construction

- Start contact shadow separately at each foot/contact.
- Project the approved actor silhouette or a simplified mass silhouette through the approved ground transform.
- Conform to floor perspective and stop/clip at real occluders or plane changes.
- For the approved NDC block style, use RGB `(0,0,0)`. Default alpha is `255`; any lower opacity must be explicitly approved from scene evidence.
- Render the approved mask with code; code must not invent light direction or arbitrary vertices.

## State variants

- Reuse the exact shadow when feet, lower body, position, and visible cast silhouette are unchanged.
- Redraw only when a changed body/prop silhouette materially affects a visible hard cast shadow.
- A shared shadow must be a named layer or identically baked pixels in both states.

Verify origin at contacts, direction, length, taper, plane conformity, opacity, and absence of floating gaps.
