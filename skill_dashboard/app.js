(function () {
  "use strict";

  const catalog = window.SKILL_CATALOG;

  if (!catalog || !Array.isArray(catalog.skills)) {
    document.body.innerHTML = "<p style='padding:24px'>Skill 数据加载失败，请确认 skills-data.js 与网页位于同一目录。</p>";
    return;
  }

  const colors = {
    "数字人与语音": "#e6a373",
    "场景出图": "#83b7d0",
    "角色与表情": "#c49ad4",
    "道具出图": "#a4ba80",
    "视频与分镜": "#aa98dc",
    "剧情与推理": "#d7a95a",
    "对白与台本": "#cf8790",
    "配置生产": "#75b69d",
    "测试与审计": "#7fc1bf",
    "设计IDE与可视化": "#9baed9",
    "开发与项目": "#aeb5b8",
    "AI辅助": "#c79bda"
  };

  const state = {
    query: "",
    category: "all",
    project: "all",
    sort: "rating-desc"
  };

  const elements = {
    searchInput: document.getElementById("searchInput"),
    categoryFilters: document.getElementById("categoryFilters"),
    projectFilters: document.getElementById("projectFilters"),
    sortSelect: document.getElementById("sortSelect"),
    skillGrid: document.getElementById("skillGrid"),
    resultCount: document.getElementById("resultCount"),
    emptyState: document.getElementById("emptyState"),
    resetButton: document.getElementById("resetButton"),
    emptyResetButton: document.getElementById("emptyResetButton"),
    copyVisibleButton: document.getElementById("copyVisibleButton"),
    toast: document.getElementById("toast")
  };

  const normalize = (value) => String(value || "").toLocaleLowerCase("zh-CN").replace(/\s+/g, " ").trim();

  function getCategories() {
    const counts = new Map();
    catalog.skills.forEach((skill) => counts.set(skill.category, (counts.get(skill.category) || 0) + 1));
    return Array.from(counts.entries());
  }

  function setupHeader() {
    document.getElementById("skillCount").textContent = catalog.skills.length;
    document.getElementById("categoryCount").textContent = getCategories().length;
    document.getElementById("projectCount").textContent = new Set(catalog.skills.map((skill) => skill.project)).size;
    document.getElementById("scanRules").textContent = catalog.scanRules;
    document.getElementById("generatedAt").textContent = catalog.generatedAt;
  }

  function setupCategoryFilters() {
    const allButton = createFilterChip("all", "全部", catalog.skills.length, "#d8a84e");
    allButton.classList.add("is-active");
    elements.categoryFilters.appendChild(allButton);

    getCategories().forEach(([category, count]) => {
      elements.categoryFilters.appendChild(createFilterChip(category, category, count, colors[category]));
    });
  }

  function createFilterChip(value, label, count, color) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "filter-chip";
    button.dataset.category = value;
    button.style.setProperty("--chip-color", color);
    button.innerHTML = `<span>${escapeHtml(label)}</span><span class="chip-count">${count}</span>`;
    return button;
  }

  function filteredSkills() {
    const query = normalize(state.query);
    const result = catalog.skills.filter((skill) => {
      const matchesCategory = state.category === "all" || skill.category === state.category;
      const matchesProject = state.project === "all" || skill.project === state.project;
      const searchText = normalize([
        skill.name,
        skill.category,
        skill.project,
        skill.kind,
        skill.purpose,
        skill.inputs.join(" "),
        skill.path
      ].join(" "));
      return matchesCategory && matchesProject && (!query || searchText.includes(query));
    });

    result.sort((a, b) => {
      if (state.sort === "modified-desc") return b.modified.localeCompare(a.modified) || b.rating - a.rating;
      if (state.sort === "name-asc") return a.name.localeCompare(b.name, "en");
      if (state.sort === "category-asc") return a.category.localeCompare(b.category, "zh-CN") || b.rating - a.rating;
      return b.rating - a.rating || b.modified.localeCompare(a.modified);
    });

    return result;
  }

  function render() {
    const skills = filteredSkills();
    elements.skillGrid.textContent = "";
    const fragment = document.createDocumentFragment();
    skills.forEach((skill) => fragment.appendChild(createCard(skill)));
    elements.skillGrid.appendChild(fragment);
    elements.resultCount.textContent = skills.length;
    elements.emptyState.hidden = skills.length !== 0;
    elements.skillGrid.hidden = skills.length === 0;
    elements.copyVisibleButton.disabled = skills.length === 0;
  }

  function createCard(skill) {
    const article = document.createElement("article");
    article.className = "skill-card";
    article.style.setProperty("--category-color", colors[skill.category] || "#d8a84e");

    const inputs = skill.inputs.map((input) => `<li>${escapeHtml(input)}</li>`).join("");
    const hasRating = Number.isFinite(skill.rating);
    const ratingWidth = `${hasRating ? Math.min(100, Math.max(0, skill.rating / 5 * 100)) : 0}%`;
    const ratingLabel = hasRating ? skill.rating.toFixed(1) : "未评分";
    const shortProject = skill.project === "planning" ? "策划仓库" : "工程仓库";
    const locator = `${skill.project}:${skill.path}`;

    article.innerHTML = `
      <div class="card-meta">
        <span class="category-badge">${escapeHtml(skill.category)}</span>
        <span class="kind-badge">${escapeHtml(skill.kind)}</span>
      </div>
      <button class="skill-name-button" type="button" data-copy-name="${escapeAttribute(skill.name)}" aria-label="复制 Skill 名称 ${escapeAttribute(skill.name)}">
        <span class="skill-name">${escapeHtml(skill.name)}</span>
        <span class="copy-glyph" aria-hidden="true">⧉</span>
      </button>
      <p class="purpose">${escapeHtml(skill.purpose)}</p>
      <div class="input-block">
        <span class="input-title">需要输入</span>
        <ul class="input-list">${inputs}</ul>
      </div>
      <div class="card-spacer"></div>
      <div class="rating-row" title="${escapeAttribute(skill.ratingNote)}">
        <span class="rating-stars" style="--rating-width:${ratingWidth}" aria-label="${hasRating ? `评分 ${skill.rating} / 5` : "未评分"}"></span>
        <span class="rating-number">${ratingLabel}</span>
      </div>
      <p class="rating-note">${escapeHtml(skill.ratingNote)}</p>
      <div class="card-footer">
        <button class="source-button" type="button" data-copy-path="${escapeAttribute(locator)}" title="复制仓库与相对路径：${escapeAttribute(locator)}">
          <span aria-hidden="true">⌘</span>
          <span>${escapeHtml(shortProject)} · 复制定位</span>
        </button>
        <span class="modified">更新 ${escapeHtml(skill.modified)}</span>
      </div>`;
    return article;
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function escapeAttribute(value) {
    return escapeHtml(value).replace(/`/g, "&#096;");
  }

  async function copyText(text, message) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        textarea.remove();
      }
      showToast(message);
    } catch (error) {
      showToast("复制失败，请手动选择文字");
    }
  }

  let toastTimer;
  function showToast(message) {
    clearTimeout(toastTimer);
    elements.toast.textContent = message;
    elements.toast.classList.add("is-visible");
    toastTimer = setTimeout(() => elements.toast.classList.remove("is-visible"), 1800);
  }

  function updateCategoryButtons() {
    elements.categoryFilters.querySelectorAll("[data-category]").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.category === state.category);
    });
  }

  function updateProjectButtons() {
    elements.projectFilters.querySelectorAll("[data-project]").forEach((button) => {
      button.classList.toggle("is-active", button.dataset.project === state.project);
    });
  }

  function resetFilters() {
    state.query = "";
    state.category = "all";
    state.project = "all";
    state.sort = "rating-desc";
    elements.searchInput.value = "";
    elements.sortSelect.value = state.sort;
    updateCategoryButtons();
    updateProjectButtons();
    render();
  }

  elements.searchInput.addEventListener("input", (event) => {
    state.query = event.target.value;
    render();
  });

  elements.categoryFilters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-category]");
    if (!button) return;
    state.category = button.dataset.category;
    updateCategoryButtons();
    render();
  });

  elements.projectFilters.addEventListener("click", (event) => {
    const button = event.target.closest("[data-project]");
    if (!button) return;
    state.project = button.dataset.project;
    updateProjectButtons();
    render();
  });

  elements.sortSelect.addEventListener("change", (event) => {
    state.sort = event.target.value;
    render();
  });

  elements.skillGrid.addEventListener("click", (event) => {
    const nameButton = event.target.closest("[data-copy-name]");
    if (nameButton) {
      copyText(nameButton.dataset.copyName, `已复制：${nameButton.dataset.copyName}`);
      return;
    }
    const pathButton = event.target.closest("[data-copy-path]");
    if (pathButton) copyText(pathButton.dataset.copyPath, "已复制仓库与相对路径");
  });

  elements.copyVisibleButton.addEventListener("click", () => {
    const names = filteredSkills().map((skill) => skill.name).join("\n");
    copyText(names, `已复制 ${filteredSkills().length} 个 Skill 名称`);
  });

  elements.resetButton.addEventListener("click", resetFilters);
  elements.emptyResetButton.addEventListener("click", resetFilters);

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault();
      elements.searchInput.focus();
    }
    if (event.key === "Escape" && document.activeElement === elements.searchInput) {
      elements.searchInput.value = "";
      state.query = "";
      render();
      elements.searchInput.blur();
    }
  });

  setupHeader();
  setupCategoryFilters();
  render();
})();
