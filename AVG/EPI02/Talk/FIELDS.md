# Talk JSON 字段说明

## 当前预览精简版（保留字段）

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | number | 是 | 对话 ID（9位数字），对话链跳转标识 |
| cnSpeaker | string | 是 | 说话人中文名 |
| cnWords | string | 是 | 中文对白文本 |
| next | string | 条件 | 下一句 ID，末尾/分支行可省略 |
| script | string | 条件 | `"branches"` 分支 / `"get"` 获取证据 / `"end"` 结束 |
| ParameterStr0 | string | 条件 | 分支选项1文字 |
| ParameterStr1 | string | 条件 | 分支选项2文字 |
| ParameterStr2 | string | 条件 | 分支选项3文字 |
| ParameterInt0 | number | 条件 | 分支跳转目标 ID / 获取证据 ID |
| ParameterInt1 | number | 条件 | 分支跳转目标 ID |
| ParameterInt2 | number | 条件 | 分支跳转目标 ID |

> 条件字段：值为空字符串或 0 时省略不写。

## 完整版字段（游戏运行时需要，预览已省略）

| 字段 | 说明 | 省略原因 |
|------|------|---------|
| step | 文件内步骤序号 | 可从顺序推断 |
| speakType | 说话类型（1=主角, 2=NPC） | 预览不区分 |
| waitTime | 等待时间（ms） | 预览不需要 |
| IdSpeaker | 说话人 NPC ID（如 NPC201） | 有 cnSpeaker 即可 |
| enSpeaker | 英文说话人名 | 预览只看中文 |
| enWords | 英文对白 | 预览只看中文 |
| cnAction | 中文动作描述 | 预览不需要 |
| enAction | 英文动作描述 | 预览不需要 |
| keyInfoType | 信息分类（timeline/statement/identity） | 预览不需要 |
| keyInfoContent | 关键信息摘要 | 预览不需要 |
| videoEpisode | 章节标识（EPI02） | 由加载路径推断 |
| videoLoop | 循环标识（loop1-6） | 由加载路径推断 |
| videoScene | 场景文件名 | 由加载时文件名注入 |
| videoId | 视频资源 ID | 预览不需要 |
| cnLocation | 中文场景位置 | 预览不需要 |
| enLocation | 英文场景位置 | 预览不需要 |
