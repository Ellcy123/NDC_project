---
name: pm-dashboard
description: "PM 仪表盘：扫描项目状态 → 上传 Supabase → 打开仪表盘。支持 scan/analyze/init 子命令。"
argument-hint: "[scan | analyze | init | open]"
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash, Agent, AskUserQuestion
---

# PM Dashboard Skill

项目管理仪表盘的自动化操作入口。

## 子命令

根据用户输入的参数决定执行哪个流程：

| 参数 | 动作 |
|------|------|
| (无参数) | 完整流程：scan → upload → 提示打开仪表盘 |
| `scan` | 仅扫描，更新本地 project_state.json（不上传） |
| `analyze` | spawn pm-analyst agent 做深度风险分析 |
| `init` | 重新导入种子数据（从朋友的 HTML 提取，会清空现有数据，需确认） |
| `open` | 输出仪表盘 URL 提示用户打开 |

## 执行流程

### 默认流程（无参数或 scan）

1. 运行扫描脚本：
   ```bash
   cd "D:/NDC_project/项目管理/pm-dashboard" && python scan_and_upload.py
   ```
   如果参数是 `scan`，加 `--local` 只保存本地不上传。

2. 读取扫描结果：
   ```
   D:/NDC_project/项目管理/pm-dashboard/scan_output/project_state.json
   ```

3. 向用户报告扫描摘要：
   - 各 Unit 设计文档完成度
   - 对话 JSON 数量
   - 美术资源覆盖率
   - 配置表同步状态

4. 提示用户打开仪表盘：
   ```
   打开浏览器访问仪表盘：
   D:\NDC_project\项目管理\pm-dashboard\dashboard.html
   （直接双击文件即可，数据从 Supabase 云端加载）
   ```

### analyze 流程

1. **准备数据**（两步并行）：
   ```bash
   # 扫描最新项目状态
   cd "D:/NDC_project/项目管理/pm-dashboard" && python scan_and_upload.py --local
   # 导出当前任务列表
   cd "D:/NDC_project/项目管理/pm-dashboard" && python task_sync.py
   ```
   产出：
   - `data/project_state.json`（扫描结果）
   - `data/current_tasks.json`（任务列表）

2. **spawn pm-analyst agent**：
   ```
   Agent(
     subagent_type: "pm-analyst",
     prompt: "读取以下两份数据，输出风险分析 + 任务进度更新建议：
              1. 扫描结果: D:/NDC_project/项目管理/pm-dashboard/scan_output/project_state.json
              2. 任务列表: D:/NDC_project/项目管理/pm-dashboard/scan_output/current_tasks.json
              排期文档:
              - D:/NDC_project/项目管理/策划/排期_630目标.md
              - D:/NDC_project/项目管理/程序/排期_4-6月.md
              - D:/NDC_project/项目管理/美术/0402/EPI03_排期时间线.md
              严格按 pm-analyst.md 中的输出格式，两个部分都要有：
              一、风险分析（高/中/低）
              二、任务进度更新建议（表格形式，含 task_id、当前进度、建议进度、匹配依据）"
   )
   ```

3. 将 agent 返回的分析结果呈现给用户，重点展示「任务进度更新建议」表格。

4. 使用 AskUserQuestion 询问用户：
   > "以上是 LLM 基于扫描数据的任务进度匹配建议。要批量更新这些任务的进度吗？（全部更新 / 选择性更新 / 跳过）"

5. 如果用户确认更新，将确认的更新项写入 JSON 并执行：
   ```bash
   cd "D:/NDC_project/项目管理/pm-dashboard" && python task_sync.py update scan_output/pending_updates.json
   ```

6. 询问用户是否要将新发现的风险项写入 Supabase risks 表。

### init 流程

1. 使用 AskUserQuestion 确认：
   > "init 会清空 Supabase 中现有的 tasks/milestones/risks 数据并重新导入。确定继续？"

2. 用户确认后运行：
   ```bash
   cd "D:/NDC_project/项目管理/pm-dashboard" && python seed_data.py
   ```

3. 然后自动执行一次 scan → upload。

### open 流程

直接输出：
```
仪表盘地址（双击打开）：
D:\NDC_project\项目管理\pm-dashboard\dashboard.html

在线地址（部署 GitHub Pages 后可用）：
https://<username>.github.io/ndc-dashboard/
```

## 文件结构

```
项目管理/pm-dashboard/
├── dashboard.html          # 仪表盘主页面
├── workflow.html           # 工作流文档页
├── scan_and_upload.py      # 扫描 + 上传主入口
├── seed_data.py            # CSV → Supabase 导入（init 用）
├── task_sync.py            # 任务导出 + 批量更新（analyze 用）
├── scanners/
│   ├── config.py           # 路径常量 + Supabase 凭据
│   ├── design_scanner.py   # 策划产出扫描
│   ├── dev_scanner.py      # 程序产出扫描
│   └── art_scanner.py      # 美术资源扫描
├── data/                   # 人工维护的配置数据（CSV）
│   ├── tasks_pm.csv        # 策划任务
│   ├── tasks_dev.csv       # 程序任务
│   ├── tasks_art.csv       # 美术任务
│   ├── milestones.csv      # 里程碑
│   └── risks.csv           # 风险项
└── scan_output/            # 脚本自动生成（勿手动编辑）
    ├── project_state.json  # 最新扫描结果
    ├── current_tasks.json  # 导出的任务列表（analyze 时生成）
    └── pending_updates.json # 待确认的更新（analyze 时生成）
```

## Supabase 配置

- URL: https://tyqsamueendpanbfousp.supabase.co
- 表: tasks, milestones, risks, scan_snapshots
- dashboard.html 和 scanners/config.py 中都已配置好凭据
