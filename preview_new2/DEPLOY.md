# 预览网站部署规则

## 部署平台

- **Vercel**（静态站点托管）
- 项目名：`ndc-preview`
- 线上地址：https://ndc-preview.vercel.app

## 部署命令

```bash
cd D:/NDC_project && vercel deploy --prod
```

首次部署需要 `vercel login`。后续部署直接执行上述命令即可。

## 部署根目录

Vercel 从 `D:\NDC_project\` 整个仓库根目录部署，通过 `vercel.json` 配置 rewrite：

```json
{
  "rewrites": [
    { "source": "/", "destination": "/preview_new2/index.html" }
  ]
}
```

即访问 `/` 自动加载 `preview_new2/index.html`。

## 路径体系（本地 vs 线上）

`preview_new2/index.html` 中的 `Config` 对象自动检测环境并切换路径：

| 资源 | 本地路径（`localhost`） | 线上路径（Vercel） |
|------|----------------------|-------------------|
| 数据表 | `/NDC_project/preview_new2/data/table` | `/preview_new2/data/table` |
| 循环配置 | `/NDC_project/preview_new2/data` | `/preview_new2/data` |
| 美术资源 | `/NDC/Assets/Resources` | `/Assets/Resources`（不存在，线上无美术） |
| AVG 对话 | `/NDC_project/AVG` | `/AVG` |

**js-yaml 库**也做了同样的环境检测（`index.html` 顶部 `<script>` 块）：
- 本地：`/NDC_project/Preview/js-yaml.min.js`
- 线上：`/Preview/js-yaml.min.js`

## Manifest 文件

线上环境无法做目录列举（`directory listing`），对话文件的发现依赖 `_manifest.json`：

| 目录 | Manifest |
|------|----------|
| `AVG/EPI02/Talk/loop{1-6}/` | `_manifest.json`（列出该目录下所有 .json） |
| `AVG/EPI02/Expose/` | `_manifest.json` |
| `AVG/EPI01/Talk/loop{1-6}/` | `_manifest.json` |
| `AVG/EPI01/Expose/` | `_manifest.json` |

新增或删除对话 JSON 文件后，必须同步更新对应目录的 `_manifest.json`。

## 何时需要重新部署

以下文件修改后需要执行 `vercel deploy --prod`：

- `preview_new2/index.html`（预览页面本身）
- `preview_new2/data/table/*.json`（ItemStaticData, SceneConfig, Talk, ExposeData 等）
- `preview_new2/data/Unit{1,2,3}/*.yaml`（loop 配置、locations、talk_summary）
- `AVG/EPI*/Talk/**/*.json` 或 `AVG/EPI*/Expose/**/*.json`（对话数据）
- `AVG/EPI*/Talk/**/_manifest.json` 或 `AVG/EPI*/Expose/_manifest.json`
- `vercel.json`（路由规则）

仅修改 MD 草稿、设计文档、state.yaml 等不影响线上预览的文件时**不需要**重新部署。
