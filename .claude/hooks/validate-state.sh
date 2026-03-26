#!/bin/bash
# Validate state YAML files before Write/Edit
# Triggered by PreToolUse when Write|Edit is used
# Receives tool input as JSON via stdin

# Read tool input from stdin
INPUT=$(cat)

# Extract file_path from JSON input
FILE_PATH=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

# Skip if no file path
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Only validate state YAML files
case "$FILE_PATH" in
  *state*.yaml|*state*.yml|*前置配置*.yaml)
    ;;
  *)
    exit 0
    ;;
esac

# Skip if file doesn't exist yet
if [ ! -f "$FILE_PATH" ]; then
  exit 0
fi

ERRORS=""

# Check YAML syntax
if command -v python &>/dev/null; then
  RESULT=$(python -c "
import yaml, sys
try:
    with open(r'$FILE_PATH', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if data is None:
        print('WARNING: Empty YAML file')
except yaml.YAMLError as e:
    print(f'ERROR: Invalid YAML syntax: {e}')
    sys.exit(1)
" 2>&1)
  if [ $? -ne 0 ]; then
    ERRORS="${ERRORS}${RESULT}\n"
  elif [ -n "$RESULT" ]; then
    echo "$RESULT"
  fi
fi

# Check for required fields in loop state files
if [[ "$FILE_PATH" =~ loop[0-9]+_state ]]; then
  if command -v python &>/dev/null; then
    python -c "
import yaml
with open(r'$FILE_PATH', encoding='utf-8') as f:
    data = yaml.safe_load(f)
if data:
    missing = [f for f in ['player_context', 'scenes'] if f not in data]
    if missing:
        print(f'WARNING: Missing top-level fields: {missing}')
" 2>/dev/null
  fi
fi

if [ -n "$ERRORS" ]; then
  echo -e "$ERRORS"
  if echo -e "$ERRORS" | grep -q "^ERROR:"; then
    exit 1
  fi
fi

exit 0
