# Preview Branch Return Design

## Goal

In the AVG preview, show a branch menu's prompt line on first arrival. After a
player selects a topic and that path returns to the same branch node, show the
options directly without replaying the prompt line.

## Current Problem

The prompt text and branch options share one Talk node. Returning through
`next` correctly reaches that node, but the preview renders it as an ordinary
dialogue line again. This makes prompts such as Foster's opening question
repeat after every topic.

## Chosen Behavior

The preview controller tracks branch Talk IDs whose prompt has already been
shown during the current dialogue session.

- First arrival: render the prompt line and its options.
- Return to the same branch ID: suppress only the repeated prompt line and
  render the options beneath the path's final line.
- Starting a new dialogue session clears the tracked IDs.
- Dialogue JSON and source Markdown remain unchanged.

## Alternatives Rejected

- Split prompt and options into separate Talk nodes: changes generated IDs and
  dialogue structure for a preview-only behavior issue.
- Hide every branch node's text: closer to Unity's direct-branch handling, but
  removes the useful prompt on first preview playback.

## Verification

- A branch prompt appears once when the dialogue first reaches the menu.
- Selecting A returns to the same options without repeating the prompt.
- Selecting B after A behaves the same way.
- Starting the dialogue again shows the prompt once again.
- Existing variable-length branch options and branch target traversal continue
  to pass the Unit3 dialogue pipeline tests.
