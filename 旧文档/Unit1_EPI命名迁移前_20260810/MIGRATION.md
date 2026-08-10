# Unit1 EPI 命名迁移归档（2026-08-10）

本目录保存 Unit1 从双命名空间迁移到正式命名空间前的可追溯快照。

## 迁移结论

- 正式章节：Unit1 / EPI01。
- 当前业务 ID：1xxx；对话、证词等长 ID 同样以 1 开头。
- 原 Unit9 / EPI09 / 9xxx 只作为本归档中的历史来源，不再是当前数据源。
- 原 EPI08 与 Unit8 对话草稿已删除；如需恢复，使用 Git 历史。

## 归档内容

- `AVG/EPI01_旧正式版/`：迁移前项目内的旧 EPI01（Jimmy 旧剧情），不是当前台本。
- `AVG/EPI09_9xxx作者版/`：迁移前的 Unit9 / EPI09 作者 JSON。
- `对话草稿/Unit9_9xxx/`：迁移前的六个 Loop MD 草稿。
- `未进入当前运行版/`：曾设计但未出现在 Unity 正式 Talk 的结尾飞车、鞋坊大火分镜与语音资源。
- `一次性迁移脚本/`：只服务旧 Unit8 / Unit9 命名空间的一次性脚本，已退出当前工作流。
- `旧审查与预览备份/`：旧 Unit9 一致性报告与 Unit8 预览表备份，已从活跃目录移出。
- `旧美术需求备份/`：仍引用 EPI09 / 9xxx 资源占位的旧版美术清单，已从当前 Unit1 美术需求移出。

## 当前真源

1. Unity 正式运行表：`D:\NDC\Assets\table\Talk.json`、`SceneConfig.json`、`ExposeData.json`、`ItemStaticData.json`、`TestimonyItem.json`。
2. 项目内正式 AVG：`AVG/EPI01/`，由 Unity Talk 正式表按 Loop/Scene 可重复生成。
3. AI 完整台本：`AVG/对话配置工作及草稿/Unit1/`。
4. 当前策划 State：`剧情设计/Unit1/state/`，已迁移为 1xxx。

同号的 EPI09 原稿只在台词与说话人均一致时补充动作说明；不一致项见
`AVG/对话配置工作及草稿/Unit1/Unit1_EPI09来源差异清单.json`。
