#!/bin/bash
# 证据 ID 冲突检测
# 级别: ERROR（硬拦截）

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

# 路径过滤在 bash 层完成
if [ -z "$FILE_PATH" ]; then exit 0; fi
case "$FILE_PATH" in
  *ItemStaticData*|*证据设计*|*证据美术*) ;;
  *) exit 0 ;;
esac

echo "$INPUT" | python "$CLAUDE_PROJECT_DIR/.claude/hooks/validate_evidence_id.py"
exit $?
