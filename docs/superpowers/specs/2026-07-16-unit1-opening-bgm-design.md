# Unit1 Opening BGM Design

## Goal

Assign the three opening-summary BGM variants to the six Unit1 loop opening scenes according to their actual setting, while preventing the existing hardcoded summary BGM call from overriding scene-specific choices.

## Audio Resources

- `Gen_BGM_SummaryTalk_Room`: indoor opening conversations.
- `Gen_BGM_SummaryTalk_Outdoor`: ordinary outdoor opening conversations.
- `Gen_BGM_SummaryTalk`: the special Zack and Emma city-overlook conversation.

All three resources are under `Assets/Resources/Audio/buttonSFX/UI625audio/bgm/`. `SceneConfig.backgroundMusic` stores only the resource filename without `.wav`.

## Scene Mapping

| Loop | Scene ID | Setting | BGM |
|---|---:|---|---|
| L1 | 1021 | Blue Moon entrance street | `Gen_BGM_SummaryTalk_Outdoor` |
| L2 | 1022 | Street corner | `Gen_BGM_SummaryTalk_Outdoor` |
| L3 | 1023 | Cabaret first-floor corridor | `Gen_BGM_SummaryTalk_Room` |
| L4 | 1024 | Bar lobby | `Gen_BGM_SummaryTalk_Room` |
| L5 | 1025 | Blue Moon entrance street at night | `Gen_BGM_SummaryTalk_Outdoor` |
| L6 | 1026 | Zack and Emma at the city overlook | `Gen_BGM_SummaryTalk` |

The special city-overlook category takes precedence over the generic indoor/outdoor distinction.

## Runtime Behavior

Entering a scene already calls `AudioMgr.PlayBGMBySceneId`, which gives `SceneConfig.backgroundMusic` first priority. However, after a loop-ending transition, `ChapterMgr.PlaySummaryTalkBGMIfRequested` currently starts `Gen_BGM_SummaryTalk` again immediately before the next loop's initial dialogue.

Change the summary-talk request handling so it uses the current opening scene's configured `backgroundMusic`. Summary-talk variants resolve under `Audio/buttonSFX/UI625audio/bgm`; existing scene BGM names continue to resolve under the legacy `Audio/BGM` root. If the scene has no configured BGM, fall back to `Gen_BGM_SummaryTalk`.

This preserves existing behavior for unconfigured future scenes while allowing the Room and Outdoor variants to work. Replaying the same configured track is harmless because `AudioMgr.PlayBGMByPath` already deduplicates identical BGM requests.

## Data Workflow

1. Update only the six rows in `res/xls/SceneConfig.xlsx`.
2. Rebuild `Assets/table/SceneConfig.json` and `Assets/Resources/table/SceneConfig.bytes.txt` through `Translate.exe`.
3. Keep unrelated generated tables and pre-existing working-tree changes out of the commit.

## Verification

- Confirm all six Scene IDs contain the expected filename in Excel and generated JSON.
- Confirm the two Room scenes, three Outdoor scenes, and one city-overlook scene load the intended resource.
- Confirm loop transitions no longer overwrite Room/Outdoor with the default track.
- Confirm a scene without `backgroundMusic` still falls back safely, and all configured summary-talk resources exist.
