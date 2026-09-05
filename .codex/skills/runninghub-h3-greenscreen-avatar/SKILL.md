---
name: runninghub-h3-greenscreen-avatar
description: Generate and machine-review context-grounded, camera-locked green-screen talking-character candidates with the RunningHub MiniMax H3 two-pass audio-reference workflow. Use calm/expression/calm by default or gated expression/expression/expression when the Talk path and Audio 1 show that matching emotion is already active at frame 1. Use exact game dialogue with Audio 1 voice conditioning, verified Talk context, the official I2VA three-field prompt structure, performance-adaptive delivery, a fixed camera and subject distance, diagnostic audio QA, machine-guided failure-specific prompt repair between attempts, and at most three paid attempts. Use for 绿幕数字人、数字人口播、AVG角色说话视频、游戏原始语音口型、固定机位胸像、批量生成、失败重出、绿幕/构图/音频审查、expression-transfer generation, troubleshooting, inspection, or downloading H3 avatar output. Produce native machine-pass candidates for user review; do not perform delivery post-processing or ready staging.
---

# runninghub-h3-greenscreen-avatar compatibility entry

本目录仅为入口，规则主实现维护在工程仓库。在本仓库根目录运行下列命令；本机仓库位置由忽略提交的 `ndc.local.json` 或环境变量配置。

```text
python scripts/art_pipeline/ndc_art.py skill runninghub-h3-greenscreen-avatar
```

读取返回的主 `SKILL.md`。所有 `references/`、`scripts/`、`assets/` 相对路径以返回的 `skill_root` 为基准；运行脚本用 `python scripts/art_pipeline/ndc_art.py run runninghub-h3-greenscreen-avatar SCRIPT_NAME ...`。不要在本入口维护第二份实现，也不要硬编码另一台电脑的盘符。

先运行 `python scripts/art_pipeline/ndc_art.py paths` 解析策划、工程和项目外工作区，并读取返回策划根下的 `docs/美术生产工作区.md`。角色卡和表情索引读取策划库，归档状态不代表成品已获批准。
