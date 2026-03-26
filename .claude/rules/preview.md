---
paths:
  - "preview_new2/**"
---

# 预览系统规则

- 修改预览系统前必须先读 `preview_new2/DEPLOY.md`
- 预览数据 JSON 格式必须与 state_to_preview.py 的输出格式一致
- 启动方式：`python -m http.server 8080 --directory "D:\\"` 然后访问 `http://localhost:8080/NDC_project/preview_new2/index.html`
- 数据目录：`preview_new2/data/table/`
- 不要直接修改 preview_new2/data/ 下的 JSON——应通过 state_to_preview.py 从 state 文件生成
