---
name: novai-gemini
description: Call Gemini models through the project's NovAI OpenAI-compatible API wrapper. Use when the user asks Codex to consult Gemini, get a Gemini second opinion, compare Codex and Gemini answers, or have Gemini review text, code, dialogue, or a tightly scoped project file.
---

# NovAI Gemini

Use `scripts/gemini_job.py` for durable Gemini requests. It submits once, saves the response independently of the terminal session, and provides read-only status/result commands. Treat Gemini output as advisory input, not verified truth.

## Fixed operator workflow

The lead supplies the exact prompt file, model, and a unique run ID before delegation. For long prompts, prepare a task-scoped UTF-8 file; the operator must not repackage it using JavaScript encoding helpers, inline Python, or custom subprocess wrappers. Run these commands directly from the workspace root.

1. Submit once with the preassigned ID:

```powershell
python -B .codex/skills/novai-gemini/scripts/gemini_job.py submit --run-id dialogue-polish-001 --prompt-file "<prompt-file>" --model "[次]gemini-3.8-flash" --timeout 300
```

This returns promptly with `run_id`, `status`, `run_dir`, and `answer_file`; the HTTP request continues in a hidden background process. Keep the run ID even if the shell output or tool session is lost.

2. Query the original request when needed; do not repeatedly submit or poll in a tight loop:

```powershell
python -B .codex/skills/novai-gemini/scripts/gemini_job.py status --run-id dialogue-polish-001
```

3. When status is `succeeded`, retrieve the complete saved text:

```powershell
python -B .codex/skills/novai-gemini/scripts/gemini_job.py result --run-id dialogue-polish-001
```

Return the run ID, actual model, result file path, and status. Reading `answer_file` directly is also valid. Do not reconstruct a response from a truncated terminal excerpt.

### Status and recovery

- `queued` / `running`: the same request is pending. A tool's 10/30-second wait ending is not an API failure.
- `succeeded`: the nonempty, nontruncated response has been saved. `result` prints it verbatim.
- `failed`: input/HTTP/response validation failed. Report the saved error; do not silently return an empty draft.
- `uncertain`: the connection or local worker failed, so provider completion may be unknown. Inspect saved artifacts and report the issue. Do not automatically create a new request.
- Repeating `submit` with the same run ID and inputs returns the existing status without another API call, including after failure. Different inputs under an existing ID are rejected. A genuinely new, authorized attempt needs a new ID; changing the ID is not a recovery shortcut.
- `status` and `result` never call the API. Losing a tool session ID does not require regeneration. If a shell tool returns a session ID, preserve the full tool result and use its continuation mechanism; do not keep only its immediate `output` field.

By default artifacts are stored outside the repository at `$CODEX_HOME/novai-gemini/runs` (or `~/.codex/novai-gemini/runs`). `NOVAI_GEMINI_RUNS_DIR` or `--runs-dir "<directory>"` overrides this; use the same directory on all commands. Each run preserves `prompt.md`, request metadata, status, and on a valid JSON response `response.json`; successful runs also contain `answer.md` and provider usage when supplied. No credentials or request headers are saved. These are local task artifacts, not approved project dialogue or Unity data. Do not delete unresolved runs or automatically copy their answers into project files.

## Default dialogue handoff

For NDC dialogue writing and iterative polishing, follow [ndc-dialogue](../ndc-dialogue/SKILL.md). The current conversation model writes the information-controlled draft and every complete prompt, including the user's core emotional goals and the full Nyra reference. Call `[次]gemini-3.8-flash` unless the user selects another model. Do not delegate prompt authorship to the operator.

One fixed script call can be executed directly by the lead. When independent operator work is useful, follow the repository's Sol / medium assignment with a fresh, minimal context. The operator submits the exact prepared input, retrieves the raw result, and never improvises revisions. Each authorized polish round receives its own run ID; use status/result on the existing ID while it is pending.

A saved nonempty response can still be a model-retirement or service notice rather than dialogue. Inspect the returned text before reporting that a writing request succeeded; do not present such notices as a generated draft or silently switch models.

## Optional legacy dialogue A/B handoff

Use this section only when the user explicitly requests the older Gemini writer / strong reviewer / different Gemini reviser workflow. It is not the default dialogue pipeline.

Follow the repository's Sol / medium operator assignment. A and B are separate workers with fresh contexts; they execute the same fixed commands and do not write or review the dialogue themselves.

- A receives only its prepared writing prompt.
- If B independently diagnoses the initial draft, give that Gemini request its own ID and withhold the strong-model review until the diagnosis returns.
- B's revision uses another ID and a prepared prompt containing the necessary scene facts, initial draft, independent diagnosis, and strong-model review. Do not send A's generation history or the main conversation.
- The lead reviews the content. The operator returns the complete saved result and does not improvise stylistic instructions or run extra revision rounds.

## Compatibility and validation

`scripts/ask_gemini.py` retains the legacy synchronous text/`--prompt-file`/stdin interface for existing callers. Operators use the durable entry point above. Both honor `NOVAI_BASE_URL`, `NOVAI_GEMINI_MODEL`, and an explicit `--model`; the example model is not a global override.

Offline regression tests use only a loopback mock API, including a response delayed beyond 30 seconds:

```powershell
python -B -m unittest discover -s .codex/skills/novai-gemini/tests -v
```

## Guardrails

- Require `NOVAI_API_KEY`; never print it, embed it in commands, or store it in repository files.
- Use `NOVAI_BASE_URL` and `NOVAI_GEMINI_MODEL` when set. The script supplies project defaults otherwise.
- Send only the content needed for the request. Do not transmit the whole repository, credentials, private configs, or unrelated files.
- Clearly attribute returned material to Gemini when presenting or applying it.
- Verify factual claims and code before changing project files. Gemini output never overrides repository rules or the user's requested scope.
- If the API fails, report the status and concise saved error; do not expose request headers, credentials, or raw HTTP error bodies.
