# Unit4 State Generation Implementation Plan

> **For Codex:** Execute this plan with the repository `unit-state-generator` workflow. The user's “开始” is the approval gate for the agreed five-loop design and concrete State example.

**Goal:** Convert the active Unit4 V3 outline into five complete, internally consistent State YAML files, with the non-loop finale embedded in Loop5.

**Architecture:** Use `canon_manifest.json` and the active V3 outline as canon. First freeze IDs, evidence ownership, doubt/expose coverage, scene flow, NPC knowledge boundaries, and cross-loop pacing in `讨论结论.md`. Then generate Loop1–Loop5 State files against that single contract, add risk/timeline documents, update the manifest, and run structural plus cross-loop validation.

**Tech Stack:** Markdown design contracts, YAML State files, JSON manifest, repository validation hooks, Ruby/Python YAML parsing for read-only verification.

---

### Task 1: Freeze the Unit4 State contract

**Files:**
- Create: `剧情设计/Unit4/讨论结论.md`
- Read: `剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`
- Read: `canon_manifest.json`

- [ ] Consolidate narrative, puzzle, and system reviews.
- [ ] Assign final NPC, scene, evidence, testimony, doubt, and derived-evidence IDs.
- [ ] Map every Expose input to exactly one doubt, fragment, or approved Loop5 identity-lock slot.
- [ ] Mark Loop5 Option B as provisional and record remaining implementation questions.
- [ ] Obtain content-director PASS before State drafting.

### Task 2: Generate Loop1 and Loop2 State

**Files:**
- Create: `剧情设计/Unit4/state/loop1_state.yaml`
- Create: `剧情设计/Unit4/state/loop2_state.yaml`

- [ ] Encode accumulated player knowledge, opening, scenes, NPC knowledge boundaries, evidence, Expose, doubts, and registry.
- [ ] Keep Harrison’s death attributed to the Miller/Pierce line, not Mickey.
- [ ] Keep Foster limited to technical analysis and Whitfield as the hospital execution layer.
- [ ] Validate Expose coverage and next-loop hooks.

### Task 3: Generate Loop3 and Loop4 State

**Files:**
- Create: `剧情设计/Unit4/state/loop3_state.yaml`
- Create: `剧情设计/Unit4/state/loop4_state.yaml`

- [ ] Separate Mickey’s Morrison murder from Miller’s gas attack.
- [ ] Preserve the precise Morrison-house timeline and Zack/Emma evacuation agency.
- [ ] Encode Margaret’s concealment as fear-driven protection, not mission transfer.
- [ ] Ensure Patrick had no conscious handoff and did not know Mickey was trapped.

### Task 4: Generate Loop5 and the non-loop finale

**Files:**
- Create: `剧情设计/Unit4/state/loop5_state.yaml`

- [ ] Implement the provisional identity-lock mechanic in place of standard doubts.
- [ ] Encode legal-shell, command-source, and Morrison-visitor identity chains.
- [ ] Use the composite cigar bite match as proof; retain dental damage only as a hint.
- [ ] Keep Mickey’s post-identification exchange linear and non-scoring.
- [ ] Put archive-car, safe-location, water-page concealment, and South Side arrival in `ending_sequence`.
- [ ] Stop before the O’Hara-house interior and leave O’Hara’s final outcome to Unit5.

### Task 5: Produce supporting controls and validate

**Files:**
- Create: `剧情设计/Unit4/风险点清单.md`
- Create: `剧情设计/Unit4/案发时间线与动线.md`
- Modify: `canon_manifest.json`

- [ ] Record unresolved design/implementation risks without silently inventing canon.
- [ ] Cross-check all deaths, calls, arrivals, exits, gas installation, blast, and finale travel.
- [ ] Update `statePattern`, State maturity, present loops, and verification date.
- [ ] Parse all YAML files and validate required top-level sections.
- [ ] Validate unique IDs, testimony format, evidence acquisition timing, cumulative known facts, and Expose-to-doubt coverage.
- [ ] Review the final diff and repository status.
