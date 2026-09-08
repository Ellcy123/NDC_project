# PS-first repair from existing content

Use for whitebox or formal-image omissions, contamination, registration and local assembly defects before another generation. Start with the closest useful source, including an earlier candidate's correct component. Preserve source layers; a globally failed candidate may supply a locally suitable patch after inspection, but its old failure never becomes a whole-image PASS.

## Choose the smallest useful repair

In the existing work record, identify the defect, its source rather than just its visible symptom, available donor pixels, target region, verified operation and acceptance check. This is a short routing decision, not another approval or mandatory report. Prefer existing-pixel repair where it can preserve correct structure and save total work. Skip directly to pose/geometry redesign when the premise is wrong; do not force every image through every repair type.

| Situation | First useful operation | Required limit |
| --- | --- | --- |
| RGB checkerboard, background residue, stray pixels or included neighbour | Re-select the real silhouette and extract the retained pixels to an independent layer | Do not regenerate merely to obtain alpha; distinguish white clothing, dark linework and self-shadow from background |
| Excess transparent margins or oversized working fragment | Adjust the working selection/crop or preview | Keep original-resolution delivery registration and XY; do not trim required anatomy or crop the fixed scene to hide defects |
| Complete, suitable actor at wrong size/location/overall tilt | Establish support/depth, then transform from the original layer | Preserve explicit user locks; use documented support anchors and recheck interactions; do not repeatedly resample or fit an alpha rectangle |
| A limb should be behind bedding/furniture | Correct layer order or foreground contour; add compatible existing occluder pixels if needed | First check that the body itself rests correctly; retain complete anatomy in the master |
| Small hole, omitted edge or seam | Check for a selection omission; re-extract, or add a compatible donor patch | Match material, light direction, perspective and resolution; smoothing an edge cannot correct structure |
| Old pillow/object rim survives replacement | Correct replacement coverage and restore available exact-source background outside the intended replacement | Distinguish old-object pixels from protected architecture; source pixels cannot reveal background that was never visible |
| One candidate has a better local component | Extract that component and register it with the retained master | Verify identity/anatomy and disclose mixed provenance; do not mistake a patched visible fragment for a complete independent actor |
| Minor edge/opacity mismatch | Use a bounded independent layer and verified local controls | No whole-image blur to conceal errors; no assumed brush, mask-paint or adjustment-layer capability |

Missing visible anatomy or a wrong face may still be repaired with a compatible same-character source. If none exists, generate only the necessary component/interaction when viable within the remaining allowance. Major identity, pose, camera or style failures can justify regenerating the affected unit; keep correct other actors and the fixed scene. Defect area alone is not the decision: a tiny wrong face can be critical, while a large checkerboard can be a straightforward extraction job.

## Coupled soft-material repairs

Inspect the actual complete body together with the bed/seat before extracting a new soft response. A generated context may quietly move the human; its attractive contact does not prove that the retained master fits.

- For a neck/shoulder gap, first reuse a known compatible support patch from the same complete-body arrangement, below the actor and above the replaced soft surface. Keep one coherent pillow volume and contact edge.
- Keep usable pillow/bedding surface where the final actor will cover it. Do not bake a different generated body's hole into the final support layer. When another body's pixels overlap the needed surface, inspect a compatible donor or re-extraction route rather than copying those body pixels as bedding.
- For exposed toes/legs, check bed-plane position and body angle first. If the body is sound, rebuild the foreground blanket contour with matching existing folds/volume. Do not delete the feet or raise a blanket indefinitely to hide a floating body.
- For an old pillow rim, separate uncovered old soft material, protected bed/wall structure and misregistered background brought in by the new patch. Refine each region independently. Feathering cannot align rails, invent an unseen background or make two conflicting pillow volumes become one.

Keep full actor, minimum support response and foreground occlusion separately editable. Check the same complete actor with and without occlusion, then the actual scene. Use the same transform for both views; recheck head/neck/shoulder bearing, pelvis/feet support, cloth volume, shadows and fixed structure after relevant changes.

## Capability and time

Use the shared PS queue and current host/catalog/schema checks. Verified selection/path → new layer → Apply Image → transform operations can implement donor-pixel assembly even if clone stamp or content-aware fill is absent. Re-extracting a retained region and hiding its source provides reversible removal without assuming an erase command. Apply Image scope and layer visibility must be verified on the actual document.

Distinguish Photoshop's general features from current MCP support and from operations already tested in this task. A manual dialog, mask-density control or unsupported warp does not authorize automated painting/retouching. If the proposed fix needs an unavailable operation, consider the verified alternatives above before declaring that defect blocked; do not change to UI automation.

Choose a bounded coherent repair, grouping related small fixes on one image. A saved and reviewed repair state counts once; commands, crop previews and manifest writes are not new attempts. Keep separate model and PS counters under production-cadence.md, with PS allowed before model exhaustion. Compare PS preparation/queue/operation/review cost against generation preparation/wait/extraction/registration/review cost. If the repair does not reduce the diagnosed defects or creates a growing chain of incompatible patches, return to the last useful source and change the method instead of endlessly patching.

At the image milestone, save PSD/PNG, release safely through the queue and inspect the fixed whole/local snapshots. Record current hashes and actual findings. Patch feasibility, tool availability and final artistic PASS are different claims. Failed results and unused allowance stay explicit; successful local work does not pass the whole scene or reset counts.
