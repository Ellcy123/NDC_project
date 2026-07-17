# Preview Branch Return Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent an AVG branch prompt from replaying when a selected inquiry path returns to the same menu in the preview.

**Architecture:** Add a tiny browser-global branch prompt state helper that can also be loaded by Node tests. `DialogController` creates fresh state for each playback, marks the current menu when an option is selected, and renders a hidden placeholder instead of the repeated prompt when that menu is reached again.

**Tech Stack:** Vanilla JavaScript, browser globals, Node.js built-in test runner, static HTML.

## Global Constraints

- Keep Unit3 Markdown and generated dialogue JSON unchanged.
- Show the branch prompt on first arrival.
- On a return to the same branch ID, show options directly without replaying the prompt.
- Starting a new dialogue session must show the prompt again.

---

### Task 1: Track And Suppress Repeated Branch Prompts

**Files:**
- Create: `avg_editor_v2/js/branch_prompt_state.js`
- Create: `avg_editor_v2/tests/branch_prompt_state.test.mjs`
- Modify: `avg_editor_v2/index.html:10135-10800`

**Interfaces:**
- Produces: `globalThis.BranchPromptState.create()` returning `{ returnMenuIds: Set<string> }`.
- Produces: `globalThis.BranchPromptState.markSelected(state, talkId)` to mark a menu after the player chooses an option.
- Produces: `globalThis.BranchPromptState.shouldSuppress(state, talkId, hasBranches)` returning `boolean`.
- Consumes: `DialogController._state.branchPromptState` and the current branch Talk ID.

- [ ] **Step 1: Write the failing Node test**

```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import '../js/branch_prompt_state.js';

test('suppresses a menu prompt only after an option was selected', () => {
    const state = globalThis.BranchPromptState.create();
    assert.equal(globalThis.BranchPromptState.shouldSuppress(state, '304001023', true), false);
    globalThis.BranchPromptState.markSelected(state, '304001023');
    assert.equal(globalThis.BranchPromptState.shouldSuppress(state, '304001023', true), true);
    assert.equal(globalThis.BranchPromptState.shouldSuppress(state, '304001024', false), false);
});

test('a new playback state shows the prompt again', () => {
    const first = globalThis.BranchPromptState.create();
    globalThis.BranchPromptState.markSelected(first, '304001023');
    const restarted = globalThis.BranchPromptState.create();
    assert.equal(globalThis.BranchPromptState.shouldSuppress(restarted, '304001023', true), false);
});
```

- [ ] **Step 2: Run the test and verify the missing helper fails**

Run: `node --test avg_editor_v2/tests/branch_prompt_state.test.mjs`

Expected: FAIL because `avg_editor_v2/js/branch_prompt_state.js` does not exist.

- [ ] **Step 3: Implement the state helper**

```javascript
(function (root) {
    const BranchPromptState = {
        create() {
            return { returnMenuIds: new Set() };
        },
        markSelected(state, talkId) {
            if (state && talkId != null) state.returnMenuIds.add(String(talkId));
        },
        shouldSuppress(state, talkId, hasBranches) {
            return Boolean(
                hasBranches
                && state
                && state.returnMenuIds.has(String(talkId))
            );
        },
    };
    root.BranchPromptState = BranchPromptState;
})(globalThis);
```

- [ ] **Step 4: Wire the helper into `DialogController`**

Add `<script src="/js/branch_prompt_state.js"></script>` before the main inline script. Initialize `branchPromptState: BranchPromptState.create()` in both playback entry points. In `selectBranch`, call `BranchPromptState.markSelected` with the current menu Talk ID before replacing the chain. In `_renderStream`, use `BranchPromptState.shouldSuppress`; when true, emit a hidden `.avg-line.avg-branch-return` placeholder so stream child indexes remain aligned while the branch buttons remain visible.

- [ ] **Step 5: Run focused and regression tests**

Run: `node --test avg_editor_v2/tests/branch_prompt_state.test.mjs`

Expected: 2 tests pass.

Run: `uv run python -m unittest "AVG/对话配置工作及草稿/tests/test_unit3_dialogue_pipeline.py"`

Expected: 14 tests pass.

- [ ] **Step 6: Verify the local preview assets**

Run HTTP checks against `http://127.0.0.1:9529/` and `http://127.0.0.1:9529/js/branch_prompt_state.js`.

Expected: both return HTTP 200, and Foster's generated A/B/C paths still return to menu Talk `304001023`.

- [ ] **Step 7: Commit the focused implementation**

```bash
git add avg_editor_v2/index.html avg_editor_v2/js/branch_prompt_state.js avg_editor_v2/tests/branch_prompt_state.test.mjs
git commit -m "fix: suppress repeated branch prompts in preview"
```
