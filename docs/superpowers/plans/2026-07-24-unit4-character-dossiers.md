# Unit4 Character Dossiers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the obsolete Unit4 character material with fourteen current dossiers aligned to the active V3 outline, then remove duplicate drafts and publish the verified result.

**Architecture:** `剧情设计/Unit4/人物设定/` becomes the Unit4-scoped source for thirteen present-day characters plus one historical core character. Every dossier uses the same compact structure: emotional summary, dramatic function, inner conflict, relationships, Unit4 progression, knowledge boundary, voice/behavior, and continuity locks.

**Tech Stack:** Markdown, Git, repository validation scripts.

## Global Constraints

- Canon identity and active outline come from `canon_manifest.json`.
- Unit4 facts come from `剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`; archived or backup outlines are not canon.
- Emotional interpretation must not invent facts or reveal Unit5 information to the player during Unit4.
- Patrick's priority is: working-class collective interest, individual workers' lives, then himself.
- Patrick returned because one worker remained trapped; he did not know it was Mickey, did not retrieve bills or documents, and made no succession handoff.
- Zack became idealistic when leaving legal practice, was forced into realism before Unit1, and is gradually recalled toward idealism by Emma and the cases.
- Mickey did not order or participate in Harrison's murder; Miller's committee acted through Pierce.
- Mickey killed Morrison and staged the shooting; the gas device belongs to a separate Miller clean-up line.
- User requested removal of old Unit4 character drafts; Git history is the recovery path.

---

### Task 1: Establish the Unit4 dossier set

**Files:**
- Create: `剧情设计/Unit4/人物设定/zack.md`
- Create: `剧情设计/Unit4/人物设定/emma.md`
- Create: `剧情设计/Unit4/人物设定/margaret.md`
- Create: `剧情设计/Unit4/人物设定/ohara.md`
- Create: `剧情设计/Unit4/人物设定/patrick.md`

**Interfaces:**
- Consumes: active Unit4 V3 outline and current cross-Unit protagonist history.
- Produces: the protagonist/family/community side of the Unit4 emotional model.

- [ ] Write each dossier with a roughly 500-Chinese-character emotional summary followed by implementation-facing sections.
- [ ] Lock Zack's timeline as idealistic lawyer-to-detective, reality-forced before Unit1, then gradually recalled toward idealism.
- [ ] Lock Patrick's class-solidarity hierarchy and delete all bill/document retrieval motivation.
- [ ] Keep O'Hara's final state and Emma's Unit5 confrontation outside Unit4 knowledge.

### Task 2: Replace the legal and police character material

**Files:**
- Create: `剧情设计/Unit4/人物设定/harrison.md`
- Create: `剧情设计/Unit4/人物设定/watts.md`
- Create: `剧情设计/Unit4/人物设定/thomas_morrison.md`
- Create: `剧情设计/Unit4/人物设定/doris_morrison.md`
- Create: `剧情设计/Unit4/人物设定/pierce.md`
- Delete: `剧情设计/Unit4/人物设定/mrs_morrison.md`
- Delete: `剧情设计/Unit4/人物设定/mrs_morrison_v3.md`

**Interfaces:**
- Consumes: V3 Harrison and Morrison causality/timelines.
- Produces: separate emotional and factual boundaries for the two Morrisons and the procedural suppression chain.

- [ ] Write Harrison as a guilty man beginning to accept consequences, not a redeemed innocent.
- [ ] Write Watts's loyalty as guarding the door until he understands that loyalty requires releasing the facts.
- [ ] Standardize Thomas Morrison's name and preserve the transactional, incomplete nature of his late turn.
- [ ] Keep Doris's motive as protecting the household boundary, not serving the organization.
- [ ] Keep Pierce responsible for Harrison's clean-up and Morrison procedural suppression, not Morrison's shooting or gas installation.

### Task 3: Replace the hospital, victim, and antagonist material

**Files:**
- Modify: `剧情设计/Unit4/人物设定/mickey.md`
- Modify: `剧情设计/Unit4/人物设定/foster.md`
- Create: `剧情设计/Unit4/人物设定/rosa.md`
- Create: `剧情设计/Unit4/人物设定/whitfield.md`
- Delete: `剧情设计/Unit4/人物设定/mickey_v3.md`

**Interfaces:**
- Consumes: V3 hospital case, Mickey identity lock, current Unit5 Foster boundary.
- Produces: the emotional counterargument that real help does not grant authority to allocate sacrifice.

- [ ] Rebuild Mickey around “rescued → misread as chosen → real results → claimed decision authority → loss of interpretive certainty.”
- [ ] Rebuild Foster around precise omission while keeping the Sean truth in the design-layer boundary until Unit5.
- [ ] Write Rosa's refusal to sign away responsibility for Isabel's death without turning her into a Miller investigator.
- [ ] Write Whitfield's institutional self-exoneration without inventing private trauma or upper-level knowledge.

### Task 4: Review the complete set

**Files:**
- Review: `剧情设计/Unit4/人物设定/*.md`
- Review: `剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`
- Review: `canon_manifest.json`

**Interfaces:**
- Consumes: all fourteen dossiers.
- Produces: a corrected, contradiction-free dossier set.

- [ ] Verify the roster is thirteen Unit4 present-day characters plus Patrick as a historical core character.
- [ ] Search for obsolete six-Loop structure, bill retrieval, old cigar chain, old Morrison name, and premature Unit5 revelations.
- [ ] Cross-check every responsibility statement against the V3 timeline.
- [ ] Run content-director review and apply all blocking corrections.

### Task 5: Verify, commit, and push

**Files:**
- Verify: all task-scoped modifications already present in the working tree.

**Interfaces:**
- Consumes: reviewed Markdown and prior approved Unit4 readiness changes.
- Produces: one intentional commit pushed to the current branch.

- [ ] Run `git diff --check`.
- [ ] Run `python3 scripts/validate_canon_manifest.py`.
- [ ] Run `python3 -m unittest tests.test_canon_manifest`.
- [ ] Inspect `git diff --stat`, file roster, and obsolete-term searches.
- [ ] Commit the complete approved Unit4 V3 readiness and character-dossier work.
- [ ] Push the current branch to `origin`.
