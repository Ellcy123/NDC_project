---
name: runninghub-h3-ref2va-audio
description: Operate the RunningHub MiniMax H3 two-pass audio-reference AI application (webapp 2087127180013817858). Use when Codex needs to generate H3 reference-to-video from up to three images and two audio references, bind voice timbre/rhythm/effects to subjects, create dialogue or lip-sync prompts, inspect or override all published nodes, control both render stages, submit/query tasks, and download the final MP4.
---

# runninghub-h3-ref2va-audio compatibility entry

本目录仅为入口，规则主实现维护在工程仓库。在本仓库根目录运行下列命令；本机仓库位置由忽略提交的 `ndc.local.json` 或环境变量配置。

```text
python scripts/art_pipeline/ndc_art.py skill runninghub-h3-ref2va-audio
```

读取返回的主 `SKILL.md`。所有 `references/`、`scripts/`、`assets/` 相对路径以返回的 `skill_root` 为基准；运行脚本用 `python scripts/art_pipeline/ndc_art.py run runninghub-h3-ref2va-audio SCRIPT_NAME ...`。不要在本入口维护第二份实现，也不要硬编码另一台电脑的盘符。

先运行 `python scripts/art_pipeline/ndc_art.py paths` 解析策划、工程和项目外工作区，并读取返回策划根下的 `docs/美术生产工作区.md`。角色卡和表情索引读取策划库，归档状态不代表成品已获批准。
