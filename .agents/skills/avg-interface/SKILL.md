---
name: avg-interface
description: "AVG 游戏交互界面设计：为 NDC 预览系统设计和构建 HTML 交互页面，包括流水线播放、对话预览、证据展示、场景切换等 AVG 游戏专用 UI。"
argument-hint: "[功能描述，如 '流水线播放器', '证据图鉴页', '指证模拟器'; 可选 '--unit=1 --loop=3' 指定数据范围]"
user-invocable: true
---

# AVG Interface — AVG 游戏交互界面设计

为 NDC 1920s 侦探推理游戏的预览系统 (`preview_new2/`) 设计和构建高品质 HTML 交互页面。

---

## 适用场景

| 用户请求 | 本 skill 处理 |
|---------|-------------|
| 新建预览页面（流水线、图鉴、模拟器等） | 从零构建完整 HTML 页面 |
| 优化现有预览页面的交互/视觉 | 读取现有代码后增量修改 |
| 添加新功能模块到 index.html | 在现有架构内扩展 |
| 设计 AVG 对话 / 场景切换 / 证据展示的 UI | 输出可用的前端组件代码 |

---

## Phase 0: 需求理解与数据盘点

### 0.1 解析用户参数

从用户输入中提取：
- **功能目标**：要构建什么（流水线播放器、证据图鉴、指证模拟器等）
- **数据范围**：`--unit=N --loop=M`，默认全 Unit 全 Loop
- **是新页面还是改现有页面**

### 0.2 确认数据源

NDC 预览系统的所有数据都在 `preview_new2/data/` 下，两类：

**Loop 配置（YAML）**：
```
preview_new2/data/Unit{1-3}/loop{1-6}.yaml   → 循环结构（阶段、场景列表、指证配置）
preview_new2/data/Unit{1-3}/story_overview.yaml → 叙事概览
preview_new2/data/Unit{1-3}/locations.yaml    → 场景层级（Unit2/3）
```

**配置表（JSON）**：
```
preview_new2/data/table/
├── SceneConfig.json       → 场景定义（背景图、NPC 位置、道具 ID）
├── ItemStaticData.json    → 证据/道具（名称、描述、类型、美术路径）
├── NPCStaticData.json     → NPC 基础信息（姓名、头像、角色）
├── NPCLoopData.json       → NPC 每循环变体（对话入口 ID）
├── Talk.json              → 对话链（9 位 ID, next 字段串链, Speaker, Words[cn,en]）
├── ExposeTalk.json        → 指证对话（speakType, script 含 "Lie" 标记）
├── ExposeConfig.json      → 指证配置（场景→NPC→可用证据映射）
├── ExposeData.json        → 指证数据（证词+证据→击破对话）
├── Testimony.json         → 证词原文（evidenceItem 子项）
├── TestimonyItem.json     → 证词摘要片段
├── DoubtConfig.json       → 疑点解锁条件（type=1物品/3证词 + param=ID）
├── GameFlowConfig.json    → 章节配置
├── DayTimeConfig.json     → 时段显示
├── Event.json             → 事件系统
├── Task.json / TaskConfig.json → 任务系统
└── TimeLineEvent.json     → 时间线事件
```

### 0.3 读取必要数据

根据功能需求，只读取相关的数据文件。不要全量加载所有 19 个 JSON。

**始终需要的**：
- `SceneConfig.json` — 场景基础
- `ItemStaticData.json` — 证据道具
- `NPCStaticData.json` — NPC 信息

**按需加载**：
- 涉及对话播放 → `Talk.json` + `NPCLoopData.json`
- 涉及指证 → `ExposeConfig.json` + `ExposeData.json` + `ExposeTalk.json`
- 涉及证词 → `Testimony.json` + `TestimonyItem.json`
- 涉及疑点 → `DoubtConfig.json`

---

## Phase 1: 设计思考

在写代码之前，明确以下设计决策：

### 1.1 美学方向

NDC 预览系统有统一的视觉语言，**必须遵守**：

```css
:root {
    --primary: #0a0a0a;        /* 深黑背景 */
    --secondary: #1a1a1a;      /* 次级背景 */
    --card: #2a1515;           /* 卡片：暗红棕 */
    --accent: #b84040;         /* 强调色：深红 */
    --highlight: #e8c678;      /* 高亮：金色 */
    --text-primary: #ffffff;
    --text-secondary: #cccccc;
    --text-muted: #888888;
    --success: #4a7c59;        /* 成功：暗绿 */
    --warning: #c41e3a;        /* 警告：深红 */
    --border: #333;
}
```

**风格关键词**：1920s 芝加哥黑色电影、昏暗酒吧灯光、打字机质感、烟雾缭绕。

**字体**：`'Segoe UI', sans-serif`（与现有系统一致）。

**禁忌**：
- 不使用明亮色调、彩色渐变、圆角过度的"AI slop"风格
- 不使用 Inter、Roboto 等泛用字体
- 不使用紫色渐变、大面积白色背景

### 1.2 交互模式

AVG 游戏特有的交互模式，按需选用：

| 模式 | 说明 | 关键实现 |
|------|------|---------|
| **对话播放** | 逐句显示，打字机效果，点击/自动推进 | `next` 字段链式读取，typewriter CSS animation |
| **场景切换** | 过场文字 + 背景渐变 | CSS transition + 地点名称 overlay |
| **证据拾取** | 弹出卡片 + 点击收集 | modal/toast 动画，状态追踪 |
| **疑点解锁** | 条件满足后弹出 | 运行时状态机检查 DoubtConfig |
| **指证对局** | 出示证据 → 击破谎言 | ExposeData 回合制逻辑 |
| **分支选择** | 多选项按钮 | branch-btn 样式，Parameters 字段 |

### 1.3 技术约束

- **单文件 HTML**：每个功能做成独立 `.html`，放在 `preview_new2/` 目录下
- **无构建工具**：纯 HTML + CSS + vanilla JS，不用 React/Vue/npm
- **数据通过 fetch 加载**：复用 `Config.paths` 路径逻辑（自动区分 local/deploy）
- **js-yaml 依赖**：YAML 解析用 `preview_new2/js-yaml.min.js`
- **复用现有工具函数**：`stripPrefix()`, `cn()`, `escapeHtml()`, `fixJson()` 等已在 index.html 中定义，新页面需自带或内联

---

## Phase 2: 架构设计

### 2.1 页面结构模板

新页面必须遵循的骨架：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NDC [功能名]</title>
    <script>
    // js-yaml: 根据环境选择路径
    (function(){
        var h = location.hostname;
        var isLocal = (h === 'localhost' || h === '127.0.0.1' || location.protocol === 'file:');
        var src = isLocal ? '/NDC_project/preview_new2/js-yaml.min.js' : '/preview_new2/js-yaml.min.js';
        document.write('<scr'+'ipt src="'+src+'"><\/scr'+'ipt>');
    })();
    </script>
    <style>
        /* CSS Variables — 与主系统保持一致 */
        :root { /* ... 同上 ... */ }
        /* 页面专用样式 */
    </style>
</head>
<body>
    <!-- Header: 标题 + 控件 -->
    <!-- Main: 主内容区 -->
    <!-- Modals/Overlays: 弹窗层 -->

    <script>
    // ===== Config（路径自适应）=====
    const Config = { /* 同 index.html 的 Config 对象 */ };

    // ===== DataLoader =====
    const DataLoader = { /* 含 fixJson、loadJSON、loadYAML */ };

    // ===== 业务逻辑 =====
    // ...
    </script>
</body>
</html>
```

### 2.2 必须内联的公用代码

每个新页面必须自带以下工具（因为是独立 HTML，无法 import）：

```javascript
// 路径配置（自动区分 local / deploy）
const Config = {
    get mode() {
        const h = location.hostname;
        return (h === 'localhost' || h === '127.0.0.1' || location.protocol === 'file:') ? 'local' : 'deploy';
    },
    get paths() {
        if (this.mode === 'deploy') {
            return {
                tableData: '/preview_new2/data/table',
                loopConfig: '/preview_new2/data',
                assets: '/Assets/Resources',
                avgData: '/AVG'
            };
        }
        return {
            tableData: '/NDC_project/preview_new2/data/table',
            loopConfig: '/NDC_project/preview_new2/data',
            assets: '/NDC/Assets/Resources',
            avgData: '/NDC_project/AVG'
        };
    },
    getAssetUrl(configPath) {
        if (!configPath) return '';
        return `${this.paths.assets}/${configPath.replace(/\\/g, '/')}.png`;
    }
};

// JSON 修复器（处理游戏导出的非标准 JSON）
function fixJson(text) { /* 完整状态机，从 index.html 复制 */ }

// 通用工具
function cn(field) { return Array.isArray(field) ? (field[0] || '') : (field || ''); }
function stripPrefix(id) { /* ... */ }
function escapeHtml(str) { /* ... */ }
```

### 2.3 资源路径规则

```
背景图:  Config.getAssetUrl(scene.backgroundImage)
NPC头像: Config.getAssetUrl(npc.IconLarge)  或  IconSmall
道具图:  Config.getAssetUrl(item.desSpritePath)
```

---

## Phase 3: 实现

### 3.1 编码规则

1. **单文件完整可运行**：打开即用，不依赖外部 CSS/JS（js-yaml 除外）
2. **所有 CSS 写在 `<style>` 标签内**，所有 JS 写在 `<script>` 标签内
3. **数据加载用 async/await**，加 loading 状态提示
4. **错误处理**：fetch 失败显示用户友好的错误信息，不静默吞掉
5. **响应式**：至少支持 1280px+ 屏幕宽度（主要在桌面使用）
6. **中文界面**：所有 UI 文本用中文
7. **复用 CSS 变量**：颜色、间距等全部用 `:root` 变量

### 3.2 AVG 专用组件参考

以下是常用 AVG UI 组件的实现要点：

#### 对话框（Dialog Box）
```css
.dialog-box {
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    width: 92%; max-width: 820px;
    background: rgba(20, 10, 10, 0.95);
    border: 2px solid var(--accent);
    border-radius: 8px;
    padding: 1rem 1.25rem;
    display: flex; gap: 1rem;
    z-index: 10;
}
/* 含：dlg-avatar(80x110px), dlg-speaker(金色), dlg-text, dlg-controls */
```

#### 场景容器（Scene Container）
```css
.scene-container {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: #000;
    min-height: 320px;
}
/* 背景图 + NPC 绝对定位叠加 + 对话框底部叠加 */
```

#### 证据卡片（Evidence Card）
```css
.evidence-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 0.75rem;
    cursor: pointer;
    transition: all 0.15s;
}
/* hover 时 border-color 变 accent，translateY(-1px) */
```

#### 过场遮罩（Transition Overlay）
```css
.transition-overlay {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.95);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 100;
    animation: fadeIn 0.5s ease;
}
.transition-text {
    color: var(--highlight);
    font-size: 1.5rem;
    text-align: center;
    animation: typeIn 1s steps(20, end);
}
```

### 3.3 数据 ID 编码速查

在实现逻辑时需要理解的 ID 规则：

| ID 类型 | 位数 | 格式 | 示例 |
|--------|------|------|------|
| 证据/道具 | 4位 | `{chapter}{loop}{seq}` | 1101 = EPI01 loop1 第01号 |
| 对话 | 9位 | `{loop}{scene}{sequence}` | 105001005 = L1 scene05 第005句 |
| 证词 | 7位 | `{loop}{npc}{sequence}` | 1031002 = L1 NPC03 第002条 |
| 疑点 | 4位 | `{loop}{seq}` | 1101 = L1 第01个疑点 |
| 场景 | 2-4位 | SceneConfig 的 sceneId | "010" = 酒吧大堂 |
| NPC | 3位 | NPCStaticData 的 id | 101=Zack, 102=Emma, 103=Rosa |

### 3.4 对话链解析逻辑

Talk.json 中对话通过 `next` 字段形成链表：

```javascript
// 从起始 ID 读取整段对话
function getDialogueChain(startId, talksMap) {
    const chain = [];
    let current = talksMap.get(String(startId));
    const visited = new Set();
    while (current && !visited.has(current.id)) {
        visited.add(current.id);
        chain.push(current);
        if (!current.next) break;
        current = talksMap.get(String(current.next));
    }
    return chain;
}
```

分支对话：当 `Parameters` 包含 `BranchOption` 时，显示选项按钮。

### 3.5 Loop 流程结构

每个 Loop 的标准流程（从 loop YAML 获取）：

```
1. opening     → opening_talks 中的对话自动播放
2. free_phase  → 按场景 ID 列表依次访问
   每个场景:
   a. 场景过场（地点名称）
   b. 场景内 NPC 对话（从 NPCLoopData 查 TalkInfo/LoopTalkInfo）
   c. 场景内证据获取（从 SceneConfig 的 ItemIDs 查 ItemStaticData）
   d. 疑点检查（DoubtConfig 条件是否满足）
3. expose      → 指证对局（ExposeData 回合制）
```

---

## Phase 4: 测试与部署

### 4.1 本地测试

```bash
# 从 D:\ 根目录启动服务器
python -m http.server 8080 --directory "D:\\"
# 访问新页面
# http://localhost:8080/NDC_project/preview_new2/[新页面].html
```

### 4.2 部署兼容性

- 确保 `Config.paths` 的 local/deploy 双模式都正确
- 如果新页面需要被 index.html 入口链接到，在 index.html header 区域添加导航按钮
- 新的 HTML 文件放在 `preview_new2/` 根目录（与 index.html 同级）

### 4.3 数据刷新

- 预览数据不手动编辑，通过 `state_to_preview.py` 从 state 文件生成
- 页面代码中 fetch 加 `?t=${Date.now()}` 防缓存

---

## Phase 5: 交付确认

完成后向用户确认：
1. 页面文件路径
2. 本地访问 URL
3. 功能演示（关键交互点）
4. 是否需要在 index.html 添加导航入口

---

## 设计参考：现有页面清单

| 页面 | 文件 | 功能 |
|------|------|------|
| 主预览 | `index.html` | 场景浏览、证据表、对话预览、美术需求 |
| 故事流程图 | `story_flow.html` | 节点编辑器，剧情结构可视化 |
| State 可视化 | `state_visualizer.html` | state YAML 内容展示 |
| 故事编辑器 | `story_editor.html` | story_overview 编辑 |
| 编辑器 | `editor.html` | 通用编辑 |

新页面应与这些页面在视觉和交互质量上保持一致或超越。
