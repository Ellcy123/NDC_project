# Unit4 V3 State Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Freeze Unit4 V3 as the active outline, resolve the confirmed pre-State decisions, adapt the State workflow to five Loops, and produce new Mickey and Doris character dossiers for review without deleting the old dossiers.

**Architecture:** `canon_manifest.json` remains the chapter identity and source registry. The V3 outline becomes the narrative authority, while the State generator reads `expectedLoops` and represents the non-Loop finale as the final Loop's `ending_sequence`. New character dossiers are written as side-by-side review drafts; canonical character files remain untouched until separate user approval.

**Tech Stack:** Markdown, JSON, YAML-oriented process documentation, repository validation scripts.

## Global Constraints

- Unit4 uses EPI04 and the reserved 4xxx namespace.
- Unit4 contains five Loops plus a non-Loop finale.
- L5 uses a provisional standalone identity-lock mechanic and may omit standard doubts.
- The standalone mechanic's UI and submission details remain open for later discussion.
- Harrison's death is a Miller upper-layer action; Mickey did not order or participate in the killing.
- Morrison's shooting and the Miller gas explosion are separate action lines.
- Existing `mickey.md` and `mrs_morrison.md` must not be deleted or overwritten in this pass.

---

### Task 1: Freeze the V3 outline decisions

**Files:**
- Modify: `剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`
- Modify: `canon_manifest.json`

**Interfaces:**
- Consumes: User-approved decisions from the 2026-07-24 review.
- Produces: A single active outline source for all later State work.

- [ ] Update the L5 identity-lock rules so the standalone mechanic gates Expose and may replace standard doubts.
- [ ] Add the designer-level Harrison responsibility and Morrison-night timeline.
- [ ] Retire the obsolete “法人卷宗” name.
- [ ] Define Mickey's stable composite cigar bite mark.
- [ ] Normalize character and evidence naming.
- [ ] Point Unit4's Canon outline source to V3.
- [ ] Validate `canon_manifest.json` with `python3 scripts/validate_canon_manifest.py`.

### Task 2: Generalize the State generator

**Files:**
- Modify: `.agents/skills/unit-state-generator/SKILL.md`

**Interfaces:**
- Consumes: `chapters[].maturity.state.expectedLoops` and `chapters[].maturity.structure` from `canon_manifest.json`.
- Produces: A workflow that generates the manifest-declared number of Loop State files and places a non-Loop finale in the last file's `ending_sequence`.

- [ ] Run a baseline pressure scenario against the current skill and record its failure.
- [ ] Replace hard-coded six-Loop wording with Manifest-driven Loop counts.
- [ ] Replace the missing `STATE_FIELDS.md` dependency with existing State files plus current system documents as the schema authority.
- [ ] Re-run the pressure scenario and verify Unit4 yields five files and an L5 `ending_sequence`.

### Task 3: Produce review-only character dossiers

**Files:**
- Create: `剧情设计/Unit4/人物设定/mickey_v3.md`
- Create: `剧情设计/Unit4/人物设定/mrs_morrison_v3.md`

**Interfaces:**
- Consumes: Unit4 V3 outline and the frozen designer-level timeline.
- Produces: Review drafts that can later replace the canonical dossiers after explicit user approval.

- [ ] Rewrite Mickey's dossier around the “saved versus chosen” misreading, real aid, Miller/Whale role, special bite mark, L1-L5 actions, and fixed voluntary release.
- [ ] Rewrite Doris's dossier around her exact L3 movements, limited knowledge, protective lie, expose behavior, and post-expose handoff.
- [ ] Add prominent review-status notes stating that the old canonical dossiers remain active until replacement approval.

### Task 4: Verify consistency

**Files:**
- Verify all files modified or created by Tasks 1-3.

**Interfaces:**
- Consumes: Completed drafts and process updates.
- Produces: Evidence that the new material is internally consistent and old dossiers remain present.

- [ ] Search for obsolete spellings and retired V2 assumptions in the V3 outline and new dossiers.
- [ ] Confirm the Canon source path exists and declares five expected Loops.
- [ ] Confirm the generator no longer requires six files or the missing State schema.
- [ ] Run JSON validation and repository Canon tests.
- [ ] Confirm `mickey.md` and `mrs_morrison.md` remain unchanged and present.
