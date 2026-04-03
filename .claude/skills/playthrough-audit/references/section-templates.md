# HTML Section Templates — 报告 Section 结构规范

生成 HTML section 时参考本文档。每个 section 只包含 `<section>` 标签，不含 `<html>/<head>/<body>/<style>/<script>`。

---

## 通用规则

1. 每个 section 用 `<section class="section" id="section-N">` 包裹
2. 内容在 `<div class="section-content">` 内
3. 用 `animate-in` class 做滚动显示，用 `stagger-children` 做级联
4. Mermaid 代码放 `<div class="mermaid-diagram">` 内（main.js 自动渲染）
5. 中文内容为主，标题可中英双语
6. 所有动态数据用 `DATA_PLACEHOLDER` 格式标注

---

## Section 01: Executive Summary

```html
<section class="section" id="section-1">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">01</span>
      <h2 class="section-title">Executive Summary</h2>
      <p class="section-subtitle">审计概览与健康度评分</p>
    </div>

    <!-- Health Gauge -->
    <div class="gauge-container animate-in">
      <svg class="gauge-ring" viewBox="0 0 120 120">
        <circle class="gauge-bg" cx="60" cy="60" r="54" />
        <circle class="gauge-fill" cx="60" cy="60" r="54"
                data-score="OVERALL_SCORE" />
      </svg>
      <div class="gauge-score" data-target="OVERALL_SCORE">0</div>
      <div class="gauge-label">Overall Health</div>
    </div>

    <!-- Severity Cards -->
    <div class="score-cards stagger-children">
      <div class="score-card severity-critical animate-in">
        <div class="score-card-number" data-target="CRITICAL_COUNT">0</div>
        <div class="score-card-label">Critical</div>
      </div>
      <div class="score-card severity-major animate-in">
        <div class="score-card-number" data-target="MAJOR_COUNT">0</div>
        <div class="score-card-label">Major</div>
      </div>
      <div class="score-card severity-minor animate-in">
        <div class="score-card-number" data-target="MINOR_COUNT">0</div>
        <div class="score-card-label">Minor</div>
      </div>
      <div class="score-card severity-suggestion animate-in">
        <div class="score-card-number" data-target="SUGGESTION_COUNT">0</div>
        <div class="score-card-label">Suggestion</div>
      </div>
    </div>

    <!-- Scope Info -->
    <div class="callout callout-info animate-in">
      <span class="callout-icon">SCOPE_ICON</span>
      <div>
        <span class="callout-title">审计范围</span>
        <p class="callout-content">SCOPE_DESCRIPTION</p>
      </div>
    </div>

    <!-- Dimension Scores (mini cards) -->
    <h3 class="screen-heading animate-in">维度评分</h3>
    <div class="score-cards stagger-children" style="grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));">
      <!-- Repeat for each of 7 dimensions -->
      <div class="score-card animate-in" style="border-color: var(--color-accent);">
        <div class="score-card-number" data-target="DIM_SCORE">0</div>
        <div class="score-card-label">DIM_NAME</div>
      </div>
    </div>
  </div>
</section>
```

---

## Section 02: Evidence Chain

```html
<section class="section" id="section-2">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">02</span>
      <h2 class="section-title">Evidence Chain</h2>
      <p class="section-subtitle">证据链路完整性分析</p>
    </div>

    <!-- Stats -->
    <div class="score-cards stagger-children" style="grid-template-columns: repeat(3, 1fr);">
      <div class="score-card animate-in" style="border-color: var(--color-accent);">
        <div class="score-card-number" data-target="TOTAL_EVIDENCE">0</div>
        <div class="score-card-label">Total Evidence</div>
      </div>
      <div class="score-card animate-in" style="border-color: var(--color-pass);">
        <div class="score-card-number" data-target="COMPLETE_CHAINS">0</div>
        <div class="score-card-label">Complete Chains</div>
      </div>
      <div class="score-card animate-in" style="border-color: var(--color-fail);">
        <div class="score-card-number" data-target="BROKEN_CHAINS">0</div>
        <div class="score-card-label">Broken Chains</div>
      </div>
    </div>

    <!-- Mermaid Diagram -->
    <div class="mermaid-container animate-in">
      <div class="mermaid-diagram">
        MERMAID_EVIDENCE_CHAIN_CODE
      </div>
    </div>

    <!-- Broken Chain Issues -->
    <h3 class="screen-heading animate-in">链路问题</h3>
    <!-- Repeat issue-card for each broken chain -->
    <div class="issue-card issue-SEVERITY animate-in">
      <div class="collapsible-header">
        <div class="issue-meta">
          <span class="severity-badge badge-SEVERITY">SEVERITY</span>
          <span class="issue-meta-tag">EVIDENCE_ID</span>
          <span>ISSUE_TITLE</span>
        </div>
      </div>
      <div class="collapsible-body">
        <p>ISSUE_DESCRIPTION</p>
        <p><strong>修复建议：</strong>FIX_SUGGESTION</p>
      </div>
    </div>
  </div>
</section>
```

---

## Section 03: Player Journey

```html
<section class="section" id="section-3">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">03</span>
      <h2 class="section-title">Player Journey</h2>
      <p class="section-subtitle">玩家体验时间线与风险点</p>
    </div>

    <!-- Timeline per Loop -->
    <div class="timeline animate-in">
      <!-- Repeat for each Loop -->
      <div class="timeline-loop-header">Loop N — LOOP_THEME</div>

      <!-- Normal info acquisition -->
      <div class="timeline-item">
        <div class="timeline-marker info"></div>
        <div class="timeline-content">
          <h4>SCENE / NPC</h4>
          <p>WHAT_PLAYER_LEARNS</p>
        </div>
      </div>

      <!-- Risk point (red) -->
      <div class="timeline-item">
        <div class="timeline-marker risk"></div>
        <div class="timeline-content">
          <h4>RISK_TITLE</h4>
          <p>RISK_DESCRIPTION</p>
          <span class="severity-badge badge-SEVERITY">SEVERITY</span>
        </div>
      </div>

      <!-- Aha moment (gold) -->
      <div class="timeline-item">
        <div class="timeline-marker aha"></div>
        <div class="timeline-content">
          <h4>AHA_TITLE</h4>
          <p>AHA_DESCRIPTION</p>
        </div>
      </div>
    </div>
  </div>
</section>
```

---

## Section 04: Character Network

```html
<section class="section" id="section-4">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">04</span>
      <h2 class="section-title">Character Network</h2>
      <p class="section-subtitle">人物关系网络与一致性审计</p>
    </div>

    <!-- Mermaid Relationship Graph -->
    <div class="mermaid-container animate-in">
      <div class="mermaid-diagram">
        MERMAID_CHARACTER_GRAPH_CODE
      </div>
    </div>

    <!-- Character Cards -->
    <!-- Repeat for each NPC -->
    <div class="character-card animate-in">
      <div class="collapsible-header character-header">
        <div class="character-avatar">NPC_INITIAL</div>
        <div>
          <div class="character-name">NPC_NAME</div>
          <div class="character-role">NPC_ROLE</div>
        </div>
        <span class="severity-badge badge-WORST_SEVERITY">ISSUE_COUNT issues</span>
      </div>
      <div class="collapsible-body">
        <!-- Mini status grid: Loop x Dimension -->
        <table class="audit-table">
          <thead>
            <tr>
              <th>维度</th><th>L1</th><th>L2</th><th>L3</th><th>L4</th><th>L5</th><th>L6</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>知识边界</td>
              <td class="cell-RESULT">STATUS</td>
              <!-- repeat per loop -->
            </tr>
            <!-- repeat per dimension -->
          </tbody>
        </table>
        <!-- Issue details for this NPC -->
        <div class="issue-card issue-SEVERITY" style="margin-top: var(--space-4);">
          <p>ISSUE_DESCRIPTION</p>
        </div>
      </div>
    </div>
  </div>
</section>
```

---

## Section 05: Difficulty Curve

```html
<section class="section" id="section-5">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">05</span>
      <h2 class="section-title">Difficulty Curve</h2>
      <p class="section-subtitle">难度曲线与信息密度分析</p>
    </div>

    <!-- Chart (rendered by main.js) -->
    <div class="chart-container animate-in" data-values='CHART_JSON_DATA'>
      <!-- SVG rendered here by main.js -->
    </div>

    <!-- Info density violations -->
    <h3 class="screen-heading animate-in">信息密度违规</h3>
    <table class="audit-table animate-in">
      <thead>
        <tr>
          <th class="sortable-header" data-sort-type="text">Loop</th>
          <th class="sortable-header" data-sort-type="text">位置</th>
          <th class="sortable-header" data-sort-type="number">信息点数</th>
          <th>违规描述</th>
          <th class="sortable-header" data-sort-type="severity">严重度</th>
        </tr>
      </thead>
      <tbody>
        <!-- Repeat rows -->
        <tr>
          <td>LOOP</td>
          <td>LOCATION</td>
          <td>COUNT</td>
          <td>DESCRIPTION</td>
          <td><span class="severity-badge badge-SEVERITY">SEVERITY</span></td>
        </tr>
      </tbody>
    </table>

    <!-- Frustration risk points -->
    <h3 class="screen-heading animate-in">挫败感风险点</h3>
    <!-- issue-card list -->
  </div>
</section>
```

`CHART_JSON_DATA` 格式：
```json
{
  "loops": ["L1", "L2", "L3", "L4", "L5", "L6"],
  "series": [
    {"name": "推理步数", "values": [2, 3, 4, 5, 4, 6]},
    {"name": "信息密度", "values": [3, 4, 5, 4, 3, 5]},
    {"name": "谜题难度", "values": [2, 3, 4, 5, 4, 5]},
    {"name": "综合难度", "values": [2, 3, 4, 5, 4, 5]}
  ]
}
```

---

## Section 06: Dialogue Heatmap

```html
<section class="section" id="section-6">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">06</span>
      <h2 class="section-title">Dialogue Quality</h2>
      <p class="section-subtitle">对话质量热力图（12 维度 × Loop）</p>
    </div>

    <!-- Heatmap -->
    <div class="heatmap-container animate-in">
      <div class="heatmap-grid" style="grid-template-columns: 180px repeat(LOOP_COUNT, 1fr);">
        <!-- Header row -->
        <div class="heatmap-label-y"></div>
        <div class="heatmap-label-x">L1</div>
        <div class="heatmap-label-x">L2</div>
        <!-- ... -->

        <!-- Data rows (one per dimension) -->
        <div class="heatmap-label-y">1. 知识边界</div>
        <div class="heatmap-cell" data-level="pass" data-detail="DETAIL_TEXT"
             data-issue-link="issue-ID">PASS</div>
        <div class="heatmap-cell" data-level="fail" data-detail="DETAIL_TEXT"
             data-issue-link="issue-ID">FAIL</div>
        <!-- repeat cells -->

        <!-- repeat rows for all 12 dimensions -->
      </div>
    </div>

    <!-- Cross-loop patterns -->
    <h3 class="screen-heading animate-in">跨 Loop 模式问题</h3>
    <!-- issue-card list for pattern issues -->
  </div>
</section>
```

---

## Section 07: Timeline Audit

```html
<section class="section" id="section-7">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">07</span>
      <h2 class="section-title">Timeline Audit</h2>
      <p class="section-subtitle">时序一致性与信息泄露检测</p>
    </div>

    <!-- Tabs for different audit sub-categories -->
    <div class="tab-group">
      <button class="tab-btn active" data-tab-group="timeline" data-tab-target="tab-leaks">信息泄露</button>
      <button class="tab-btn" data-tab-group="timeline" data-tab-target="tab-facts">Facts 流转</button>
      <button class="tab-btn" data-tab-group="timeline" data-tab-target="tab-attrs">属性一致</button>
      <button class="tab-btn" data-tab-group="timeline" data-tab-target="tab-truth">单层真相</button>
    </div>

    <!-- Tab panels (each with an audit-table) -->
    <div class="tab-panel" id="tab-leaks" data-tab-group="timeline">
      <table class="audit-table">
        <thead>
          <tr>
            <th class="sortable-header" data-sort-type="text">Loop</th>
            <th>泄露内容</th>
            <th>出处</th>
            <th class="sortable-header" data-sort-type="text">应属 Loop</th>
            <th class="sortable-header" data-sort-type="severity">严重度</th>
          </tr>
        </thead>
        <tbody>
          <!-- rows -->
        </tbody>
      </table>
    </div>

    <!-- repeat for other tabs -->
  </div>
</section>
```

---

## Section 08: Narrative Assessment

```html
<section class="section" id="section-8">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">08</span>
      <h2 class="section-title">Narrative Assessment</h2>
      <p class="section-subtitle">叙事连贯性与情绪弧线评估</p>
    </div>

    <!-- Emotion arc: tabs per Loop -->
    <div class="tab-group">
      <!-- one tab per loop -->
      <button class="tab-btn" data-tab-group="emotion" data-tab-target="emotion-L1">L1</button>
      <!-- ... -->
    </div>

    <div class="tab-panel" id="emotion-L1" data-tab-group="emotion">
      <div class="callout callout-accent">
        <span class="callout-icon">EMOTION_ICON</span>
        <div>
          <span class="callout-title">设计情绪弧：DESIGNED_ARC</span>
          <p class="callout-content">实际传达：ACTUAL_ARC</p>
          <p class="callout-content">匹配度：MATCH_SCORE / 5</p>
        </div>
      </div>
    </div>

    <!-- Foreshadowing table -->
    <h3 class="screen-heading animate-in">伏笔回收率</h3>
    <table class="audit-table animate-in">
      <thead>
        <tr><th>伏笔</th><th>埋设</th><th>回收</th><th>状态</th><th>质量</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>FORESHADOW_DESC</td>
          <td>PLANTED_LOOP</td>
          <td>RECOVERED_LOOP</td>
          <td class="cell-RESULT">STATUS</td>
          <td>QUALITY</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>
```

---

## Section 09: Issue Detail

```html
<section class="section" id="section-9">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">09</span>
      <h2 class="section-title">Issue Detail</h2>
      <p class="section-subtitle">完整问题明细（可筛选 / 排序 / 搜索）</p>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar animate-in">
      <div class="filter-group">
        <span class="filter-group-label">Severity</span>
        <button class="filter-chip" data-filter-group="severity" data-filter-value="critical">Critical</button>
        <button class="filter-chip" data-filter-group="severity" data-filter-value="major">Major</button>
        <button class="filter-chip" data-filter-group="severity" data-filter-value="minor">Minor</button>
        <button class="filter-chip" data-filter-group="severity" data-filter-value="suggestion">Suggestion</button>
      </div>
      <div class="filter-group">
        <span class="filter-group-label">Dimension</span>
        <button class="filter-chip" data-filter-group="dimension" data-filter-value="player">Player</button>
        <button class="filter-chip" data-filter-group="dimension" data-filter-value="evidence">Evidence</button>
        <button class="filter-chip" data-filter-group="dimension" data-filter-value="character">Character</button>
        <button class="filter-chip" data-filter-group="dimension" data-filter-value="dialogue">Dialogue</button>
        <button class="filter-chip" data-filter-group="dimension" data-filter-value="timeline">Timeline</button>
        <button class="filter-chip" data-filter-group="dimension" data-filter-value="difficulty">Difficulty</button>
        <button class="filter-chip" data-filter-group="dimension" data-filter-value="narrative">Narrative</button>
      </div>
      <div class="filter-group">
        <span class="filter-group-label">Loop</span>
        <button class="filter-chip" data-filter-group="loop" data-filter-value="L1">L1</button>
        <button class="filter-chip" data-filter-group="loop" data-filter-value="L2">L2</button>
        <button class="filter-chip" data-filter-group="loop" data-filter-value="L3">L3</button>
        <button class="filter-chip" data-filter-group="loop" data-filter-value="L4">L4</button>
        <button class="filter-chip" data-filter-group="loop" data-filter-value="L5">L5</button>
        <button class="filter-chip" data-filter-group="loop" data-filter-value="L6">L6</button>
      </div>
      <input type="text" id="issue-search" placeholder="Search issues...">
      <button class="filter-clear" onclick="clearFilters()">Clear</button>
      <span class="filter-count">TOTAL / TOTAL issues</span>
    </div>

    <!-- Expand/Collapse controls -->
    <div style="margin-bottom: var(--space-4); display: flex; gap: var(--space-2);">
      <button class="btn" onclick="expandAll('issue-list')">Expand All</button>
      <button class="btn" onclick="collapseAll('issue-list')">Collapse All</button>
    </div>

    <!-- Issue Cards -->
    <div id="issue-list">
      <!-- Repeat for each issue -->
      <div class="issue-card issue-SEVERITY"
           id="issue-ISSUE_ID"
           data-severity="SEVERITY"
           data-dimension="DIMENSION"
           data-loop="LOOP">
        <div class="collapsible-header">
          <div class="issue-meta">
            <span class="severity-badge badge-SEVERITY">SEVERITY</span>
            <span class="issue-meta-tag">LOOP</span>
            <span class="issue-meta-tag">DIMENSION</span>
            <span style="flex:1;">ISSUE_TITLE</span>
          </div>
        </div>
        <div class="collapsible-body">
          <p><strong>问题描述：</strong>ISSUE_DESCRIPTION</p>
          <p><strong>影响范围：</strong>AFFECTED_SCOPE</p>
          <p><strong>文件位置：</strong><code>FILE_LOCATION</code></p>
          <p><strong>修复建议：</strong>FIX_SUGGESTION</p>
          <p><strong>修复难度：</strong><span class="effort-badge effort-LEVEL">EFFORT_LEVEL</span>
             <strong style="margin-left: var(--space-4);">影响度：</strong><span class="impact-badge impact-LEVEL">IMPACT_LEVEL</span></p>
        </div>
      </div>
    </div>
  </div>
</section>
```

---

## Section 10: Fix Priorities

```html
<section class="section" id="section-10">
  <div class="section-content">
    <div class="section-header">
      <span class="section-number">10</span>
      <h2 class="section-title">Fix Priorities</h2>
      <p class="section-subtitle">修复优先级路线图</p>
    </div>

    <!-- Priority Group 1 -->
    <div class="priority-group animate-in">
      <div class="priority-group-title">P1 — 立即修复</div>
      <!-- Repeat items -->
      <div class="priority-item priority-1">
        <div class="priority-num">1</div>
        <div class="priority-info">
          <div class="priority-title">ISSUE_TITLE</div>
          <div class="priority-desc">ISSUE_SUMMARY</div>
          <div style="margin-top: var(--space-2);">
            <span class="severity-badge badge-SEVERITY">SEVERITY</span>
            <span class="effort-badge effort-LEVEL">EFFORT</span>
            <span class="impact-badge impact-LEVEL">IMPACT</span>
            <span class="issue-meta-tag">LOOPS</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Priority Group 2 -->
    <div class="priority-group animate-in">
      <div class="priority-group-title">P2 — 近期修复</div>
      <!-- items with priority-2 class -->
    </div>

    <!-- Priority Group 3 -->
    <div class="priority-group animate-in">
      <div class="priority-group-title">P3 — 有空就改</div>
      <!-- items with priority-3 class -->
    </div>
  </div>
</section>
```
