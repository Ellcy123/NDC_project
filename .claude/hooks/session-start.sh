#!/bin/bash
# Session start hook - show recent context
# Triggered by SessionStart

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-D:/NDC_project}"

echo "=== NDC Project Session ==="
echo ""

# Show recent git commits
echo "Recent commits:"
cd "$PROJECT_DIR" && git log --oneline -3 2>/dev/null
echo ""

# Show active session state if exists
SESSION_FILE="$PROJECT_DIR/production/session-state/active.md"
if [ -f "$SESSION_FILE" ]; then
  echo "Active session state:"
  cat "$SESSION_FILE"
  echo ""
fi

exit 0
