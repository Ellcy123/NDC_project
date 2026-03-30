#!/bin/bash
# Zack 结论性语言检测
# 级别: WARNING（不阻断）

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path',''))" 2>/dev/null)

# 路径过滤在 bash 层完成——不匹配时不启动 Python 主脚本
if [ -z "$FILE_PATH" ]; then exit 0; fi
case "$FILE_PATH" in
  *对话草稿*|*生成草稿*) ;;
  *) exit 0 ;;
esac
if [ ! -f "$FILE_PATH" ]; then exit 0; fi

# 只有匹配的文件才启动 Python 完整检查
echo "$INPUT" | python "$CLAUDE_PROJECT_DIR/.claude/hooks/validate_no_spoiler.py"
exit $?
