---
name: feishu-docs
description: Read Feishu documents and Wiki pages from a URL or document token through the project's self-contained Feishu runtime. Use when the user asks to open, inspect, extract, or summarize content from a Feishu document.
---

# Feishu Docs

Read Feishu documents with the project-local runtime. Do not reference tools, credentials, or files under another project.

## Read a document

From the workspace root, run:

```powershell
node .codex/skills/feishu-docs/scripts/feishu_docs.mjs read "<Feishu URL or document token>"
```

The command resolves Wiki nodes to their underlying document ID, fetches all document blocks, preserves their order, and prints flattened readable text with document metadata.

To inspect metadata without fetching the body:

```powershell
node .codex/skills/feishu-docs/scripts/feishu_docs.mjs info "<Feishu URL or document token>"
```

## Local runtime

- Load credentials only from `.env.feishu.local` at the workspace root. This file must remain ignored by Git.
- Use only the vendored runtime under this skill's `runtime/` directory.
- If `runtime/node_modules` is missing, restore local production dependencies with `npm install --omit=dev --ignore-scripts` from the `runtime/` directory.
- Never print, quote, copy into output, or commit credential values.
- This skill is read-only. Do not call create, update, upload, or delete tools exposed internally by the vendored runtime.
- If authentication or permission fails, report the concise error without exposing environment values.
