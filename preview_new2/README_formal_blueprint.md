# NDC Formal Blueprint

这里现在有两张图：

- `flow_blueprint.html`：剧情流程顺序图，默认应该看这个。
- `formal_blueprint.html`：细颗粒度配置关系图，主要用于查 Talk 断链、资源缺失等配置问题。

这是正式配置的只读蓝图视图，数据来自 `D:\NDC\res\xls` 生成的配置快照。

## 生成图谱

在 `D:\NDC` 下运行：

```powershell
$env:PYTHONIOENCODING='utf-8'
D:\NDC\.uv-python\cpython-3.11.14-windows-x86_64-none\python.exe tools\ndc_config_audit\export_config_snapshot.py
D:\NDC\.uv-python\cpython-3.11.14-windows-x86_64-none\python.exe tools\ndc_config_audit\export_blueprint_graph.py
```

图谱会写入：

- `D:\NDC\tools\ndc_config_audit\out\blueprint_graph.json`
- `D:\NDC_project\preview_new2\data\formal\blueprint_graph.json`

## 打开

```bat
D:\NDC_project\preview_new2\start_formal_blueprint.bat
```

或访问：

```text
http://127.0.0.1:8790/flow_blueprint.html
```

## 当前能力

- 按 Loop 过滤正式配置图谱
- 按节点类型过滤
- 搜索节点文本 / ID / meta
- 展示 Loop、Scene、Talk、NPC、Item、证词、疑点、指证、资源节点
- 展示 Talk next、branch、疑点条件、指证使用证据、场景包含物等关系
- 点击节点查看来源表、key、meta 和关联边
- 校验叠层：error / warning 节点会标红或标黄
- 支持“只看问题节点”
- 节点详情里会展示对应校验问题

当前是只读视图，不会修改正式配置。
