# Formal delivery and Talk mounting

Use this reference only after the user explicitly asks to put approved emergency art into the game. Read `talk-driven-placement.md` first; it owns the active-side mapping, coordinate system, size semantics, and cumulative layout rules. This file owns the formal resource and Talk-table delivery path.

## Authorization boundary

- Approval of a generated image authorizes review and packaging, not formal file or table changes.
- Enter this phase only for an explicit instruction such as “配置进游戏”, “正式挂载”, or “放进正式资源”.
- Confirm which approved raw candidate is being delivered. Do not silently substitute a later retry, redraw, cleanup, or other edited output.
- Scope edits to the named event, frames, and Talk rows. Preserve unrelated user changes in the working tree and workbooks.

## Choose mount rows and sequence behavior

Use `{ENGINE_ROOT}/res/xls/Talk.xlsx` as the authoritative source. Trace the full reachable dialogue chain around the requirement's mount point rather than matching a sentence fragment in isolation.

- Mount one comic image on one exact Talk row.
- The ordinary comic parameter format is:

  `imagePath|text|x,y|enterLevel|enterDelay`

- `imagePath` is relative to `Assets/Resources`, without a file extension, for example `Art/Scene/Emergency/EPI02/C02/C02_01`.
- `ParameterInt` selects the optional comic-text corner: `0` top-left, `1` top-right, `2` bottom-left, `3` bottom-right. It is harmless when `text` is empty, but still preserve the intentional value.
- A second parameter string is an optional video path. Never use it as a second-image slot.
- The ordinary comic auto-hide behavior is based on actual player advances, not simply the number of rows in the spreadsheet. Adjacent comic rows can overlap for one dialogue beat; placing a non-comic row between them makes the earlier image begin exiting as the later one appears.
- Select rows for narrative timing first. Do not mount an image early merely to create overlap if that would reveal the beat before the dialogue earns it.
- Do not change comic persistence code or dialogue structure unless the user explicitly requests that separate behavior change.

For a multi-image event, record a table before editing:

`frame | exact Talk ID | spoken line | narrative beat | native size | XY | enterLevel | enterDelay | visible-with | active AVG side`

## Final size and XY

- Treat the approved RGBA image's native pixel dimensions as its runtime display footprint.
- A deterministic resize after approval is allowed when it is required to implement the approved layout; it is a technical delivery transform, not a second AI generation.
- Preserve alpha, black border sharpness, and protected subjects. Inspect the resized PNG at native size and thumbnail size.
- Record each top-left XY in both the event's `XYposition.txt` and the exact Talk parameter.
- Review the union of every frame that is simultaneously visible across the real Talk lifetime. Keep it clear of the active AVG lane and dialogue UI.

## Deliver formal resources

Use this destination family:

`{ENGINE_ROOT}/Assets/Resources/Art/Scene/Emergency/EPI02/<event-folder>/`

1. Inspect the destination before writing. Do not overwrite an existing different asset without explicit approval.
2. Copy the approved final RGBA frames with stable names such as `<event-id>_01.png`, `<event-id>_02.png`.
3. Compare SHA256 values when a file is copied without resizing. If resized, report both source and delivered hashes and dimensions.
4. Write `XYposition.txt` with one explicit filename-to-XY entry per delivered frame.
5. Ensure every PNG `.meta` imports as a Unity Sprite with `textureType: 8`, `spriteMode: 1`, and `alphaIsTransparency: 1`.
6. Ensure the folder, PNGs, and `XYposition.txt` have valid metadata and unique GUIDs. Do not reuse a GUID copied from a U1 reference.
7. Do not rely on Unity's default texture import settings for a runtime comic asset.

## Edit Talk through the Excel-first workflow

Use the `unity-table-edit` skill and follow the project Excel-first rules.

1. Inspect repository status and the current workbook/generated-output timestamps before editing. Do not discard unrelated changes.
2. Back up the current workbook in the event's experiment/delivery folder.
3. Build and inspect a temporary candidate workbook where practical. Compare cell values against the current workbook and require only the intended Talk-cell differences.
4. Write the comic script command and its first parameter on the authorized rows only. Preserve spoken text, `next`, `isRight`, and unrelated commands/parameters unless explicitly authorized.
5. If the workbook is locked, do not kill an unrelated Excel or translation process. Wait for the user's task to finish or clean up only a process that this workflow demonstrably started.
6. If the source workbook changes while preparing the candidate, rebuild from the latest workbook rather than overwriting the newer version.
7. Run the translator from the repository root context:

   `Push-Location "{ENGINE_ROOT}/res"; .\Translate\bin\Debug\Translate.exe; Pop-Location`

The translator may rewrite multiple generated table files. Do not revert or stage unrelated generated changes on the user's behalf.

## Validate the result

Treat the configuration as delivered only after all applicable checks pass:

- The exact Excel rows contain the intended comic script and only the expected parameter changes.
- Generated `Assets/table/Talk.json` contains the same Talk IDs, comic script enum, one image parameter, exact resource path, XY, entry level, and delay.
- Dialogue text, `next`, and `isRight` are unchanged unless the user authorized changes.
- The full reachable dialogue chain remains valid and the active side across the comic lifetime matches the placement plan.
- `Assets/Resources/table/Talk.bytes.txt` exists, is non-empty, and was regenerated after the workbook edit.
- Every configured resource path resolves to a delivered PNG; PNG dimensions, alpha corners, `.meta` Sprite settings, and GUID uniqueness pass.
- `XYposition.txt`, delivered native sizes, and Talk parameter XY agree with the approved layout.

`Translate.exe` can emit a downstream integration-DLL/path warning after table data has already been generated. Never hide that warning. Count table delivery as successful only when the JSON and bytes outputs actually regenerated and passed the checks above, and report the warning separately.

If Unity is available, allow it to import the assets and inspect the Sprite settings. Run Play Mode only when requested or when it is already part of the agreed acceptance check. Otherwise report that verification was static and recommend an in-game visual pass.

## Handoff

Report:

- exact Talk IDs, spoken lines, and frame-to-row mapping;
- delivered filenames, native sizes, XY, entry level/delay, and simultaneous-visible groups;
- formal resource path and `XYposition.txt` path;
- workbook, generated JSON, and runtime bytes validation;
- asset/meta/GUID validation and whether Unity/Play Mode was used;
- all warnings, especially translator integration warnings;
- the complete list of formal files changed.
