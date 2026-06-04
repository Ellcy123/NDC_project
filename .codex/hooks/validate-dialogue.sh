#!/bin/bash
# Validate dialogue files before Write/Edit
# Triggered by PreToolUse when Write|Edit is used
# Receives tool input as JSON via stdin

# Read tool input from stdin
INPUT=$(cat)

# Extract file_path from JSON input
FILE_PATH=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

# Skip if no file path or not in AVG/dialogue area
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Only validate dialogue-related files
case "$FILE_PATH" in
  *AVG*|*对话草稿*|*生成草稿*)
    ;;
  *)
    exit 0
    ;;
esac

# Skip if file doesn't exist yet (new file being created)
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

ERRORS=""

if [[ "$FILE_PATH" =~ \.json$ ]]; then
  # Check for valid JSON syntax
  if command -v python &>/dev/null; then
    python -c "import json; json.load(open(r'$FILE_PATH', encoding='utf-8'))" 2>/dev/null
    if [ $? -ne 0 ]; then
      ERRORS="${ERRORS}ERROR: Invalid JSON syntax in $FILE_PATH\n"
    fi
  fi
fi

if [[ "$FILE_PATH" =~ 对话草稿 ]] || [[ "$FILE_PATH" =~ 生成草稿 ]]; then
  # Check for duplicate dialogue IDs (9 digits after ###)
  DUPES=$(grep -oP '(?<=### )\d{9}' "$FILE_PATH" 2>/dev/null | sort | uniq -d | head -5)
  if [ -n "$DUPES" ]; then
    ERRORS="${ERRORS}ERROR: Duplicate dialogue IDs: ${DUPES}\n"
  fi
fi

if [ -n "$ERRORS" ]; then
  echo -e "$ERRORS"
  if echo -e "$ERRORS" | grep -q "^ERROR:"; then
    exit 1
  fi
fi

exit 0
