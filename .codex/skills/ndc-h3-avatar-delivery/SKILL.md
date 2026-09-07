---
name: ndc-h3-avatar-delivery
description: Deterministically post-process and stage explicitly user-approved NDC MiniMax H3 green-screen avatar candidates. Use after the user approves a specific Talk ID and candidate video and asks to 放进去、加入 ready、处理绿幕、统一 #00FF2B、调整音量、裁剪已批准的首尾、转成 1280×848、更新替换清单、核对任务费用或验证哈希. Normalize only edge-connected green background, convert 1536×1024 to 1272×848 plus 4 px side padding, verify the delivery, copy only into the replacement staging ready tree, and update Markdown/CSV records. Never generate or retry videos and never modify formal game assets without a separate explicit request.
---

# ndc-h3-avatar-delivery compatibility entry

本目录仅为入口，规则主实现维护在工程仓库。在本仓库根目录运行下列命令；本机仓库位置由忽略提交的 `ndc.local.json` 或环境变量配置。

```text
python scripts/art_pipeline/ndc_art.py skill ndc-h3-avatar-delivery
```

读取返回的主 `SKILL.md`。所有 `references/`、`scripts/`、`assets/` 相对路径以返回的 `skill_root` 为基准；运行脚本用 `python scripts/art_pipeline/ndc_art.py run ndc-h3-avatar-delivery SCRIPT_NAME ...`。不要在本入口维护第二份实现，也不要硬编码另一台电脑的盘符。

先运行 `python scripts/art_pipeline/ndc_art.py paths` 解析策划、工程和项目外工作区，并读取返回策划根下的 `docs/美术生产工作区.md`。角色卡和表情索引读取策划库，归档状态不代表成品已获批准。
