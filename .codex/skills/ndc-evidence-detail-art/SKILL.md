---
name: ndc-evidence-detail-art
description: Produce NDC evidence Big, inventory Icon, and locked clue-Polaroid art from a route and itemType contract already classified by the parent evidence skill. Use only as an explicit sub-skill; do not use it to decide acquisition routes, place scene Maps, or build Type 6/Type 7 containers.
---

# NDC Evidence Detail Art

Produce the close-view and inventory assets for one already-classified evidence record. This skill owns Big, Icon, clue-Polaroid finalization, and their verification reports. It does not decide how the player acquires the record.

## Caller contract

Require the parent skill to provide, at minimum:

- `itemId`, evidence name, Unit/Episode/Loop, and source design references;
- the resolved acquisition `route` and `itemType` (`3/item`, `1/clue`, or `2/envir`);
- the approved `desSpritePath` stem and either the approved `iconPath` stem or an explicit Icon-omission flag;
- the Big-detail contract: physical identity, state, material, damage, exact readable facts, and spoiler exclusions;
- the Icon-presentation contract for `item` and `clue`, or an explicit omission contract for `envir`;
- `anchorMode`, the acquired-record identity, and the matching Map or container-child reference when one exists.

Treat `route` as an input fact and carry it into the handoff. Do not reopen State, SceneConfig, or ItemStaticData to reclassify it. If the contract is missing, contradictory, or still marked unresolved, return it to the parent skill without generating placeholder art.

This skill never creates or edits Map sprites, scene coordinates, scene images, Type 6/Type 7 art, configuration rows, or Unity files. For a world-space pickup, those remain the caller's responsibility. `detail-only` means only that no Map is expected; its `item` or `clue` detail contract still applies.

## Read before production

Read [the existing detail and Icon production contract](../ndc-scene-evidence-placement/references/detail-icon-production.md) completely before generating, composing, resizing, or approving an asset. Reuse these existing resources in place; do not copy, rename, or replace them:

- [Big layout guide](../ndc-scene-evidence-placement/assets/big_layout_guide_2560x1600.png)
- [locked 620px Polaroid frame](../ndc-scene-evidence-placement/assets/clue_polaroid_frame_620x620.png)
- [canonical Polaroid window mask](../ndc-scene-evidence-placement/assets/clue_polaroid_window_mask_620x620.png)
- [deterministic finalizer and verifier](../ndc-scene-evidence-placement/scripts/evidence_art.py)

The parent `ndc-scene-evidence-placement` skill owns final cross-route delivery packaging and completeness review.

## Route by itemType without reclassification

| Supplied contract | Big output | Icon output |
|---|---|---|
| `itemType=3/item`, including `detail-only` | One ordinary transparent Big | Required `130x130` RGBA Icon |
| `itemType=1/clue`, including `detail-only` | Locked `620x620` Polaroid Big | Required `130x130` RGBA Icon made from the accepted Polaroid identity |
| `itemType=2/envir` | Approved observation Big consistent with its Map identity/state | Forbidden: omit `iconPath`, Icon master, report, and `*_icon.png` |

An `envir` contract cannot be `detail-only`. Do not invent an Icon because neighboring ItemStaticData rows have one. Do not silently waive a required `item` or `clue` Icon.

## Information split and identity lock

The Map is a low-information discovery anchor. Keep exact titles, dates, numbers, body text, handwriting, damage comparisons, and puzzle-specific details in Big unless the parent contract explicitly identifies an environmental sign that must be readable in the scene. Never push Big-detail requirements back into Map art to make the clue easier to notice.

Big and Icon must preserve the acquired record's object identity, material, construction, handedness, damage, labels, and visible state. For `visible-record`, a matching Map must remain recognizable as that same evidence. For `search-hotspot`, the Map intentionally represents the furniture/search anchor instead; verify the acquisition-contract link and do not force visual identity between the anchor and hidden record. A container-child Map must remain recognizable as the same evidence shown in Big and Icon.

## Semantic master and code boundary

Start from one approved high-resolution semantic raster master: an accepted image-generation result, artist-authored raster, approved source extraction, or an approved deterministic transformation of one. It must already establish silhouette, perspective, construction, material, wear, lighting, period style, and evidence identity.

Deterministic code may crop, mask, composite, rotate, fit, resize, perspective-map, manage alpha, apply locked templates, place separately approved exact-text layers, and generate reports. It must not originate the prop body, paper surface, tables, texture, wear, lighting, handwriting, background, or illustrative layout. For exact-text documents, first approve the illustrated physical document master, then composite approved title/body/stamp/signature layers. Record every master and content layer path plus SHA-256.

## Ordinary Big

The `2560x1600` guide is a positioning workspace, never a runtime asset. Export exactly one final frame after hiding the guide:

| Frame | Runtime size | Local safe rect `[l,t,r,b)` | Use |
|---|---:|---:|---|
| `portrait` | `571x1000` | `[58,100,513,900)` | Vertically dominant evidence |
| `square` | `818x818` | `[82,82,736,736)` | Approximately square evidence |
| `landscape` | `1000x571` | `[100,58,900,513)` | Horizontally dominant evidence |

Classify the unrotated silhouette, choose and record `+10` or `-10` degrees explicitly, and fit from the rotated antialiased alpha bounds. Safe rectangles are maximum envelopes, not fill targets. Do not upscale an undersized master merely to fill a frame.

Finalize with the existing tool:

```text
<workspace-python> .codex/skills/ndc-scene-evidence-placement/scripts/evidence_art.py finalize-big \
  --master <approved-transparent-master.png> \
  --frame portrait|square|landscape \
  --rotation-degrees 10|-10 \
  --output <runtime-big.png> \
  --layout-preview <optional-review-only.png> \
  --report <big-verification.json>
```

Never stage the layout preview as runtime art.

## Clue Polaroid Big

Use the locked frame and canonical mask through the existing finalizer. Approve a high-resolution first-person close observation, crop only to emphasize facts already authorized by the contract, perspective-map it through the canonical window, and export exactly `620x620` RGBA. Do not resize or rotate the completed frame.

```text
<workspace-python> .codex/skills/ndc-scene-evidence-placement/scripts/evidence_art.py compose-polaroid \
  --photo <approved-high-resolution-clue-photo.png> \
  --output <runtime-clue-big.png> \
  --report <polaroid-verification.json>
```

Every pixel outside the window mask must remain byte-identical to the locked template. The tool enforces the current approved template and mask hashes; replacing either resource requires separate explicit authorization.

## Icon

Icon is an independently authored presentation asset, not the whole Big canvas shrunk to `130x130`.

- Work at `1040x1040` RGBA with the combined subject and shadow inside `[60,60,980,980)`, at most `920x920`.
- Preserve separate subject and shadow masks.
- Keep the subject visually centered; use top-side lighting and a short noon-like shadow whose centroid lies left and below the subject.
- For a dimensional prop, approve a dedicated high-resolution Icon pose that preserves Big identity.
- For flat paper or an accepted Polaroid, reuse its approved front artwork and transform it deterministically; never regenerate exact text.
- Finalize once to exactly `130x130` RGBA. All visible subject and shadow pixels must remain inside `[7,7,122,122)`, at most `115x115`; fully transparent pixels must carry zero RGB.
- Restart every revision from the high-resolution master. Never resize a finalized Icon again.

```text
<workspace-python> .codex/skills/ndc-scene-evidence-placement/scripts/evidence_art.py finalize-icon \
  --master <1040x1040-combined-rgba.png> \
  --subject-mask <1040x1040-subject-mask.png> \
  --shadow-mask <1040x1040-shadow-mask.png> \
  --output <130x130-icon.png> \
  --report <icon-verification.json>
```

## Approval and handoff gate

Do not hand an asset back to the parent until all applicable checks pass:

- the semantic master and any exact-content layers have recorded provenance and hashes;
- the ordinary Big finalization report passes, and the native-size image has no guide residue, clipped alpha, or unreadable required detail;
- the clue report proves `620x620` RGBA output, a changed photo window, and byte-identical locked frame/exterior;
- the Icon report proves exact size, safe bounds, correct transparency, and the supplied subject/shadow relationship;
- the Icon is inspected at `130x130` and representative `100x100`, `120x120`, and `150x150` previews, with transparent edges checked over light and dark backgrounds;
- Big and Icon share the acquired-record identity and state; a Map also shares that identity for `visible-record` or container-child work, while a `search-hotspot` Map instead matches its separate visible-anchor contract;
- `envir` handoff contains a non-empty Big and an explicit Icon omission, with no Icon stem, file, or report.

Reject muddy micro-detail, an unreadable silhouette, wrong-direction or overlong shadow, repeated-resize softness, frame contamination, fabricated facts, or identity drift even when machine reports pass.

Return the approved Big and, when applicable, Icon; their masters and masks; selected frame/rotation; verification reports; source hashes; supplied route/itemType; and explicit Icon presence or omission. The parent skill then combines these outputs with Map/Position or container deliverables and performs final packaging.
