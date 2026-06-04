#!/bin/bash
# 跨场景信息泄漏检测
# 级别: WARNING（不阻断）

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

# 路径过滤在 bash 层完成
if [ -z "$FILE_PATH" ]; then exit 0; fi
case "$FILE_PATH" in
  *对话草稿*|*生成草稿*) ;;
  *) exit 0 ;;
esac
if [ ! -f "$FILE_PATH" ]; then exit 0; fi

echo "$INPUT" | python "$CLAUDE_PROJECT_DIR/.claude/hooks/validate_info_isolation.py"
exit $?
