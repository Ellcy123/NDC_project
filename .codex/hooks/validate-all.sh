#!/bin/bash
# 统一验证入口：一次 Python 调用完成所有 5 项检查
# 替代原来的 5 个独立 hook（避免 5 次 Python 启动开销）
python "$CLAUDE_PROJECT_DIR/.claude/hooks/validate_dispatcher.py"
exit $?
