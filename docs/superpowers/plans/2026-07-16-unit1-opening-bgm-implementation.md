# Unit1 Opening BGM Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure the six Unit1 loop opening scenes with the correct indoor, outdoor, or city-overlook BGM and prevent the hardcoded summary track from overriding those choices.

**Architecture:** `SceneConfig.backgroundMusic` remains the source of truth for the selected opening track. `AudioMgr` resolves the `Gen_BGM_SummaryTalk*` family under `LoopBgmRoot` while preserving the legacy `Audio/BGM` root for other configured scene tracks. `ChapterMgr` passes the known `initScene` ID to `AudioMgr`, which falls back to `Gen_BGM_SummaryTalk` when the scene has no configured BGM.

**Tech Stack:** Unity C#, generated table classes, Excel source tables, NDC `Translate.exe` table builder.

## Global Constraints

- Configure only Unit1 opening Scene IDs `1021` through `1026`.
- Store BGM filenames without `.wav` in `SceneConfig.backgroundMusic`.
- Do not edit dialogue, testimony, audio, video, or unrelated generated table files.
- Preserve all pre-existing working-tree changes from other windows.

---

### Task 1: Scene-aware summary BGM fallback

**Files:**
- Modify: `D:/NDC/Assets/_Project/Scripts/Manager/AudioMgr.cs`
- Modify: `D:/NDC/Assets/_Project/Scripts/Manager/ChapterMgr.cs`

**Interfaces:**
- Consumes: `ChapterConfig.initScene`, `SceneConfig.backgroundMusic`, `LoopBgmRoot`, `PathMgr.BGMPrePath`.
- Produces: `AudioMgr.PlaySummaryTalkBGM(int sceneId)`.

- [ ] **Step 1: Record the current failing behavior**

Run:

```powershell
rg -n "PlaySummaryTalkBGM\(|PlaySummaryTalkBGMIfRequested" Assets/_Project/Scripts/Manager/AudioMgr.cs Assets/_Project/Scripts/Manager/ChapterMgr.cs
```

Expected before implementation: `PlaySummaryTalkBGM()` accepts no scene ID and always starts the default `SummaryTalk` constant.

- [ ] **Step 2: Implement scene-aware path resolution in AudioMgr**

Add a resolver that sends summary-talk variants to `LoopBgmRoot` and preserves the legacy root for every other filename. Use it in both ordinary scene entry and the summary-talk request. Replace the no-argument method with a scene-aware overload:

```csharp
public void PlaySummaryTalkBGM(int sceneId)
{
    var data = TableConfig.GetTableByKey<SceneConfig>(TableEnum.SceneConfig, sceneId);
    string resourcePath = ResolveSceneBgmPath(data?.backgroundMusic) ?? SummaryTalk;
    PlayStoryBGM(resourcePath);
}
```

- [ ] **Step 3: Pass initScene from ChapterMgr**

Change the helper signature and both call sites:

```csharp
static void PlaySummaryTalkBGMIfRequested(bool shouldPlay, int sceneId)
{
    if (!shouldPlay) return;
    if (AudioMgr.Instance == null) return;

    AudioMgr.Instance.PlaySummaryTalkBGM(sceneId);
}
```

Both initial-dialogue paths call it with `config.initScene`.

- [ ] **Step 4: Verify source behavior**

Run the same `rg` command from Step 1.

Expected after implementation: all calls use an `int sceneId`, and no no-argument `PlaySummaryTalkBGM()` call remains.

### Task 2: Configure six Unit1 opening scenes

**Files:**
- Modify: `D:/NDC/res/xls/SceneConfig.xlsx`
- Generate: `D:/NDC/Assets/table/SceneConfig.json`
- Generate: `D:/NDC/Assets/Resources/table/SceneConfig.bytes.txt`

**Interfaces:**
- Consumes: Scene IDs and BGM mapping from the approved design.
- Produces: runtime `SceneConfig.backgroundMusic` values.

- [ ] **Step 1: Verify all six backgroundMusic cells are initially empty**

Inspect rows `1021` through `1026` in the `SceneConfig` worksheet and assert the third column is empty.

- [ ] **Step 2: Write the approved mapping**

```text
1021 = Gen_BGM_SummaryTalk_Outdoor
1022 = Gen_BGM_SummaryTalk_Outdoor
1023 = Gen_BGM_SummaryTalk_Room
1024 = Gen_BGM_SummaryTalk_Room
1025 = Gen_BGM_SummaryTalk_Outdoor
1026 = Gen_BGM_SummaryTalk
```

- [ ] **Step 3: Rebuild formal tables**

Run:

```powershell
Set-Location D:/NDC/res
./Translate/bin/Debug/Translate.exe
```

Expected: `SceneConfig.json` and `SceneConfig.bytes.txt` are regenerated. The known integration-DLL temporary-resource error may remain after table output and does not invalidate successfully generated table files.

- [ ] **Step 4: Remove unrelated generated diffs**

Compare the post-build worktree with the pre-build worktree. Restore only generator-created changes in unrelated table/code outputs; preserve every pre-existing user modification.

### Task 3: End-to-end verification

**Files:**
- Verify all files from Tasks 1 and 2.

**Interfaces:**
- Consumes: implemented code and generated tables.
- Produces: evidence that configuration and fallback behavior are complete.

- [ ] **Step 1: Verify the six Excel and JSON values**

Assert the mapping in Task 2 matches both `SceneConfig.xlsx` and `SceneConfig.json` exactly.

- [ ] **Step 2: Verify resources exist**

Assert these files exist under `Assets/Resources/Audio/buttonSFX/UI625audio/bgm/`:

```text
Gen_BGM_SummaryTalk.wav
Gen_BGM_SummaryTalk_Outdoor.wav
Gen_BGM_SummaryTalk_Room.wav
```

- [ ] **Step 3: Verify scope**

Run `git diff --check` and inspect `git diff --name-only`. Expected task-owned files are the two C# files and the three SceneConfig layers only; all unrelated audio/video changes remain untouched.
