# NDC Project - 侦探解谜游戏

## 美术制作入口

- [角色卡索引与人物目录](美术资产交付/角色/README.md)：按人物/色版/版本查找唯一参考，不从旧文件夹猜图。
- [美术工作区和收尾规则](docs/美术生产工作区.md)：静态美术 Skill 在策划库，H3 视频 Skill 在工程库；两类过程文件统一放本机配置的项目外工作区，用户确认后交付，结束时清理临时大文件。
- [Skill 看板](skill_dashboard/index.html)：统一主入口与用途。
- [跨机器配置与依赖](production/art_pipeline/dependencies.md)：两库共用仓库内入口；自有脚本随 Git，机器路径另存被忽略的 `ndc.local.json`。

## 项目说明

这是一款原创侦探解谜游戏的开发项目，玩家将扮演侦探 Zack Brennan，在1920年代芝加哥的酒吧中调查一系列神秘事件。

**游戏类型：** 叙事推理 / 时间循环解谜

**核心玩法：**
- 与NPC对话收集线索
- 搜集证据揭露谎言
- 通过指证系统击破嫌疑人
- 多轮循环逐步接近真相

## 内容声明

⚠️ **本项目所有内容均为虚构创作**

- 所有角色、场景、案件、对话均为原创虚构内容
- 仅供游戏娱乐和创意展示目的
- 如与现实人物或事件有任何相似，纯属巧合

## Canon 章节映射

项目当前以 Unit1–Unit5 为正式章节身份。Unit1 已统一为 EPI01 / 1xxx；Unit9 / EPI09 / 9xxx 仅作为迁移前历史归档。Unit10 是 Unit2 的策划标题来源别名。完整的 Episode、ID 命名空间、内容来源、完成度及历史版本以 [`canon_manifest.json`](canon_manifest.json) 为准，当前数据不做运行时自动 ID 转换。

Unit1 的运行时真源是 `D:\NDC\Assets\table\`；项目内 `AVG/EPI01/` 与
`AVG/对话配置工作及草稿/Unit1/` 是从正式表验证生成的 JSON 镜像和 AI 可读完整台本。
`avg_editor_v2/data/table/` 是预览 / 编辑副本，不覆盖 Unity 正式表的真源地位。

## Preview 预览工具

`avg_editor_v2/` 文件夹包含剧情预览 + 配置编辑网页工具，用于：

- **团队内部协作** - 策划、编剧、美术等成员查看剧情流程
- **内容审校** - 检查对话、证据、NPC信息的一致性
- **进度同步** - 让团队成员了解当前剧情开发状态

🔗 在线预览：https://ndc-preview.vercel.app

---

*This is a fictional detective game project. All content is original creative work for entertainment purposes only.*
