# Unit4 State Risk Closure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close Unit4 State risks 1–7 with a finalized L5 identity-lock contract, normalized State scene types, explicit field/persistence/finale mapping, and an automated repository-side validator.

**Architecture:** Keep the five State YAML files as the narrative blueprints, add one machine-readable Unit4 contract, and validate both through a Ruby/Psych command with no external dependencies. Rich scene behavior moves from custom `type` strings to `design_tags`; unsupported structures are classified as design-only or special-adapter inputs instead of being silently treated as runtime tables.

**Tech Stack:** YAML, Markdown, Ruby standard library (`Psych`, `JSON`, `OptionParser`, `Minitest`), Git.

## Global Constraints

- Do not modify Unity code, `avg_editor_v2/data/table/*.json`, `preview_new2/data/table/*.json`, or AVG Talk/Expose JSON.
- Unit4 remains `5_loops_plus_non_loop_finale`; never create `loop6_state.yaml`.
- L5 uses the approved independent identity lock and has no normal `doubts`.
- Preserve all existing narrative facts, IDs, Expose materials, knowledge boundaries, and U4/U5 cutoff.
- Use `apply_patch` for repository file edits.
- New validator code must be test-first and use only Ruby standard-library dependencies.

---

### Task 1: Write Contract Validator Tests

**Files:**
- Create: `剧情设计/Unit4/state/test_validate_state_contract.rb`

**Interfaces:**
- Consumes: future `Unit4StateContract::Validator.new(root:).validate`
- Produces: Minitest expectations for the seven risk-closure rules.

- [ ] **Step 1: Create a test harness that loads a temporary copy of Unit4 State**

The test file must use `Dir.mktmpdir`, copy `canon_manifest.json` and `剧情设计/Unit4/state`, then require `validate_state_contract.rb`.

- [ ] **Step 2: Add a failing happy-path test**

```ruby
def test_repository_state_satisfies_contract
  result = validator.validate
  assert_empty result.errors
end
```

- [ ] **Step 3: Add mutation tests for each contract rule**

Tests must mutate temporary YAML text and assert an error for:

- custom scene type;
- unclassified top-level field;
- L5 `open_questions`;
- L5 standard doubt gate;
- missing persistence declaration;
- blocking L3 investigation record;
- ending sequence chapter end before `ending_4045`.

- [ ] **Step 4: Run tests and verify RED**

Run:

```bash
ruby 剧情设计/Unit4/state/test_validate_state_contract.rb
```

Expected: failure because `validate_state_contract.rb` and `state_contract.yaml` do not exist.

### Task 2: Implement Machine Contract and Validator

**Files:**
- Create: `剧情设计/Unit4/state/state_contract.yaml`
- Create: `剧情设计/Unit4/state/validate_state_contract.rb`
- Test: `剧情设计/Unit4/state/test_validate_state_contract.rb`

**Interfaces:**
- Consumes: five `loop*_state.yaml` files and root `canon_manifest.json`.
- Produces: `Unit4StateContract::Result#errors`, CLI exit 0/1, and exact PASS output.

- [ ] **Step 1: Add the machine-readable contract**

Contract sections:

```yaml
scene_types: [cutscene, free_exploration]
field_policy: {}
persistent_inputs: []
identity_lock: {}
non_progress_records: {}
ending_sequence: {}
```

- [ ] **Step 2: Implement duplicate-key and YAML loading helpers**

Use `Psych.parse_file` to scan duplicate mapping keys before `YAML.load_file`.

- [ ] **Step 3: Implement validation methods**

Create methods:

```ruby
validate_manifest
validate_known_facts_chain
validate_scene_types
validate_field_policy
validate_identity_lock
validate_persistence
validate_non_progress_records
validate_ending_sequence
validate_duplicate_keys
```

- [ ] **Step 4: Add CLI behavior**

On success print `PASS Unit4 state contract validation`; on failure print every error and exit 1.

- [ ] **Step 5: Run tests and verify GREEN**

Run:

```bash
ruby 剧情设计/Unit4/state/test_validate_state_contract.rb
```

Expected: mutation tests fail until State files are normalized; validator unit behavior passes.

### Task 3: Normalize Scene Types and Field Policies

**Files:**
- Modify: `剧情设计/Unit4/state/loop1_state.yaml`
- Modify: `剧情设计/Unit4/state/loop2_state.yaml`
- Modify: `剧情设计/Unit4/state/loop3_state.yaml`
- Modify: `剧情设计/Unit4/state/loop4_state.yaml`
- Modify: `剧情设计/Unit4/state/loop5_state.yaml`

**Interfaces:**
- Consumes: `state_contract.yaml.scene_types` and `field_policy`.
- Produces: State files with basic `type` plus optional `design_tags`.

- [ ] **Step 1: Replace every composite scene type**

Map cutscene-like scenes to `cutscene`; map all player-controlled investigation/action scenes to `free_exploration`.

- [ ] **Step 2: Preserve rich behavior in `design_tags`**

Example:

```yaml
type: free_exploration
design_tags: [identity_lock, expose_location, story_climax]
```

- [ ] **Step 3: Run validator**

Expected: scene-type and field-policy checks pass; identity, persistence, L3 record, and ending checks may still fail.

### Task 4: Finalize Identity Lock and Persistence

**Files:**
- Modify: `剧情设计/Unit4/state/loop1_state.yaml`
- Modify: `剧情设计/Unit4/state/loop3_state.yaml`
- Modify: `剧情设计/Unit4/state/loop4_state.yaml`
- Modify: `剧情设计/Unit4/state/loop5_state.yaml`

**Interfaces:**
- Consumes: approved three-chain evidence mapping.
- Produces: fixed identity interaction/gate contract and five chapter-persistent inputs.

- [ ] **Step 1: Replace L5 `open_questions` with `interaction_contract`**

Use the approved layout, submission, parallel order, and two-stage feedback values from the design spec.

- [ ] **Step 2: Add `gate_contract`**

Set `standard_doubt_progress_required: false`, `completion_condition: all_chains_completed`, and `unlocks: expose`.

- [ ] **Step 3: Add persistence declarations at first acquisition**

Add chapter persistence to 4112, 4153001, 4315, 4416, and 4418 with exact `required_by` chain references.

- [ ] **Step 4: Run validator**

Expected: identity and persistence checks pass.

### Task 5: Resolve L3 Records and Non-Loop Finale

**Files:**
- Modify: `剧情设计/Unit4/state/loop3_state.yaml`
- Modify: `剧情设计/Unit4/state/loop5_state.yaml`
- Modify: `剧情设计/Unit4/风险点清单.md`
- Create: `剧情设计/Unit4/Unit4_State落表与特殊机制规范.md`

**Interfaces:**
- Consumes: design spec and machine contract.
- Produces: explicit investigation-log presentation and ending runtime ownership.

- [ ] **Step 1: Add presentation policy to all L3 non-progress records**

Each record gets `channel: investigation_log`, `blocking: false`, `auto_unlock: true`, `show_completion_toast: false`.

- [ ] **Step 2: Add `ending_sequence.runtime_contract`**

Set `counts_as_loop: false`, `inherit_loop: 5`, `chapter_end_after: ending_4045`, `next_unit_entry: enter_ohara_house`.

- [ ] **Step 3: Write the human-readable mapping specification**

Document scene mapping, field policy, identity-lock adapter inputs/outputs, persistence, non-progress records, and finale flow.

- [ ] **Step 4: Update the risk list**

Mark risks 1–7 as closed at State-contract level and list remaining Unity implementation handoff items without treating them as unresolved State design.

### Task 6: Full Verification and Delivery

**Files:**
- Verify all task-owned files.

**Interfaces:**
- Consumes: complete implementation.
- Produces: passing validation evidence and pushed Git commit.

- [ ] **Step 1: Run contract tests**

```bash
ruby 剧情设计/Unit4/state/test_validate_state_contract.rb
```

Expected: all tests pass.

- [ ] **Step 2: Run repository State contract validator**

```bash
ruby 剧情设计/Unit4/state/validate_state_contract.rb
```

Expected: `PASS Unit4 state contract validation`.

- [ ] **Step 3: Run syntax and whitespace checks**

```bash
ruby -e 'require "yaml"; Dir["剧情设计/Unit4/state/*.yaml"].each { |p| YAML.load_file(p) }'
git diff --check
```

Expected: both commands exit 0.

- [ ] **Step 4: Verify scope**

`git status --short` must list only the approved spec, plan, Unit4 State/contract/validator/test/mapping/risk files.

- [ ] **Step 5: Commit and push**

Commit message:

```text
feat(unit4): close state integration risks
```

Push the current branch to its configured upstream.
