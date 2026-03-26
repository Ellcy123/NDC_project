#!/bin/bash
# Pre-compact hook - save session state before context compression
# Triggered by PreCompact

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-D:/NDC_project}"
SESSION_DIR="$PROJECT_DIR/production/session-state"
SESSION_FILE="$SESSION_DIR/active.md"

# Ensure directory exists
mkdir -p "$SESSION_DIR"

# Write timestamp
echo "# Active Session" > "$SESSION_FILE"
echo "" >> "$SESSION_FILE"
echo "Last updated: $(date '+%Y-%m-%d %H:%M:%S')" >> "$SESSION_FILE"
echo "" >> "$SESSION_FILE"

# Record recently modified files
echo "## Recently Modified Files" >> "$SESSION_FILE"
cd "$PROJECT_DIR" && git diff --name-only HEAD 2>/dev/null | head -20 >> "$SESSION_FILE"
echo "" >> "$SESSION_FILE"

# Record unstaged changes
UNSTAGED=$(cd "$PROJECT_DIR" && git diff --stat 2>/dev/null)
if [ -n "$UNSTAGED" ]; then
  echo "## Unstaged Changes" >> "$SESSION_FILE"
  echo "$UNSTAGED" >> "$SESSION_FILE"
fi

exit 0
