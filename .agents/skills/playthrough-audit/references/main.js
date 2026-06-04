/**
 * NDC PLAYTHROUGH AUDIT — INTERACTIVE ENGINE
 * Copy this file verbatim into the report output directory.
 * Never regenerate it. It handles all interactivity generically.
 *
 * Engines included:
 *  - Navigation & progress bar
 *  - Scroll-triggered reveal animations
 *  - Keyboard navigation
 *  - Collapsible sections
 *  - Filter engine (severity, dimension, loop)
 *  - Tab switching
 *  - Heatmap interaction
 *  - Health score gauge animation
 *  - Sort engine (tables)
 *  - Mermaid diagram init
 *  - Difficulty chart (SVG)
 *  - Search (issue filtering)
 *  - Print/export
 */
(function () {
  'use strict';

  /* ── HELPERS ──────────────────────────────────────────────── */
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.from((ctx || document).querySelectorAll(sel)); }

  /* ── NAVIGATION & PROGRESS BAR ────────────────────────────── */
  const progressBar = $('#progress-bar');
  const navDots     = $$('.nav-dot');
  const sections    = $$('.section');

  function updateProgress() {
    if (!progressBar) return;
    var scrollTop    = window.scrollY;
    var scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
    var pct          = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
    progressBar.style.width = pct + '%';
    progressBar.setAttribute('aria-valuenow', Math.round(pct));
    updateNavDots();
  }

  function updateNavDots() {
    var scrollMid = window.scrollY + window.innerHeight / 2;
    sections.forEach(function (sec, i) {
      var dot = navDots[i];
      if (!dot) return;
      var top    = sec.offsetTop;
      var bottom = top + sec.offsetHeight;
      if (scrollMid >= top && scrollMid < bottom) {
        dot.classList.add('active');
        dot.classList.remove('visited');
      } else if (window.scrollY + window.innerHeight > top) {
        dot.classList.remove('active');
        dot.classList.add('visited');
      } else {
        dot.classList.remove('active', 'visited');
      }
    });
  }

  window.addEventListener('scroll', function () {
    requestAnimationFrame(updateProgress);
  }, { passive: true });
  updateProgress();

  navDots.forEach(function (dot) {
    dot.addEventListener('click', function () {
      var target = $('#' + dot.dataset.target);
      if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
  });

  /* ── KEYBOARD NAVIGATION ───────────────────────────────────── */
  function currentSectionIndex() {
    var scrollMid = window.scrollY + window.innerHeight / 2;
    for (var i = 0; i < sections.length; i++) {
      var top    = sections[i].offsetTop;
      var bottom = top + sections[i].offsetHeight;
      if (scrollMid >= top && scrollMid < bottom) return i;
    }
    return 0;
  }

  document.addEventListener('keydown', function (e) {
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) return;
    if (e.key === 'ArrowDown' || e.key === 'ArrowRight') {
      var next = sections[currentSectionIndex() + 1];
      if (next) { next.scrollIntoView({ behavior: 'smooth' }); e.preventDefault(); }
    }
    if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
      var prev = sections[currentSectionIndex() - 1];
      if (prev) { prev.scrollIntoView({ behavior: 'smooth' }); e.preventDefault(); }
    }
  });

  /* ── SCROLL-TRIGGERED REVEAL ───────────────────────────────── */
  var revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

  $$('.animate-in').forEach(function (el) { revealObserver.observe(el); });

  // Stagger children
  $$('.stagger-children').forEach(function (parent) {
    Array.from(parent.children).forEach(function (child, i) {
      child.style.setProperty('--stagger-index', i);
    });
  });

  /* ── COLLAPSIBLE SECTIONS ──────────────────────────────────── */
  $$('.collapsible-header').forEach(function (header) {
    header.addEventListener('click', function () {
      var body = header.nextElementSibling;
      if (!body || !body.classList.contains('collapsible-body')) return;

      if (header.classList.contains('open')) {
        header.classList.remove('open');
        body.style.maxHeight = '0';
        body.style.opacity = '0';
      } else {
        header.classList.add('open');
        body.style.maxHeight = body.scrollHeight + 'px';
        body.style.opacity = '1';
      }
    });
  });

  // Expand All / Collapse All
  window.expandAll = function (containerId) {
    var container = containerId ? $('#' + containerId) : document;
    $$('.collapsible-header', container).forEach(function (h) {
      var body = h.nextElementSibling;
      if (body && body.classList.contains('collapsible-body')) {
        h.classList.add('open');
        body.style.maxHeight = body.scrollHeight + 'px';
        body.style.opacity = '1';
      }
    });
  };

  window.collapseAll = function (containerId) {
    var container = containerId ? $('#' + containerId) : document;
    $$('.collapsible-header', container).forEach(function (h) {
      var body = h.nextElementSibling;
      if (body && body.classList.contains('collapsible-body')) {
        h.classList.remove('open');
        body.style.maxHeight = '0';
        body.style.opacity = '0';
      }
    });
  };

  /* ── FILTER ENGINE ─────────────────────────────────────────── */
  var filterState = { severity: [], dimension: [], loop: [] };

  function applyFilters() {
    var cards = $$('.issue-card');
    var visibleCount = 0;

    cards.forEach(function (card) {
      var show = true;

      // Check each filter group (AND between groups)
      ['severity', 'dimension', 'loop'].forEach(function (group) {
        if (filterState[group].length > 0) {
          var val = card.dataset[group] || '';
          // OR within a group
          if (filterState[group].indexOf(val) === -1) {
            show = false;
          }
        }
      });

      card.style.display = show ? '' : 'none';
      if (show) visibleCount++;
    });

    // Update counter
    var counter = $('.filter-count');
    if (counter) {
      counter.textContent = visibleCount + ' / ' + cards.length + ' issues';
    }
  }

  $$('.filter-chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      var group = chip.dataset.filterGroup;
      var value = chip.dataset.filterValue;
      if (!group || !value) return;

      var idx = filterState[group].indexOf(value);
      if (idx === -1) {
        filterState[group].push(value);
        chip.classList.add('active');
      } else {
        filterState[group].splice(idx, 1);
        chip.classList.remove('active');
      }
      applyFilters();
    });
  });

  window.clearFilters = function () {
    filterState = { severity: [], dimension: [], loop: [] };
    $$('.filter-chip').forEach(function (c) { c.classList.remove('active'); });
    applyFilters();
  };

  /* ── TAB SWITCHING ─────────────────────────────────────────── */
  $$('.tab-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var group = btn.dataset.tabGroup;
      var target = btn.dataset.tabTarget;
      if (!group || !target) return;

      // Deactivate all in group
      $$('.tab-btn[data-tab-group="' + group + '"]').forEach(function (b) {
        b.classList.remove('active');
      });
      $$('.tab-panel[data-tab-group="' + group + '"]').forEach(function (p) {
        p.style.display = 'none';
      });

      // Activate target
      btn.classList.add('active');
      var panel = $('#' + target);
      if (panel) panel.style.display = '';
    });
  });

  // Init: show first tab in each group
  var initedGroups = {};
  $$('.tab-btn').forEach(function (btn) {
    var group = btn.dataset.tabGroup;
    if (group && !initedGroups[group]) {
      initedGroups[group] = true;
      btn.click();
    }
  });

  /* ── HEATMAP INTERACTION ───────────────────────────────────── */
  var heatmapTooltip = document.createElement('div');
  heatmapTooltip.className = 'heatmap-tooltip';
  document.body.appendChild(heatmapTooltip);

  $$('.heatmap-cell').forEach(function (cell) {
    cell.addEventListener('mouseenter', function (e) {
      var detail = cell.dataset.detail || '';
      if (!detail) return;
      heatmapTooltip.textContent = detail;
      heatmapTooltip.style.display = 'block';
      var rect = cell.getBoundingClientRect();
      heatmapTooltip.style.left = (rect.left + rect.width / 2) + 'px';
      heatmapTooltip.style.top = (rect.top - 8) + 'px';
      heatmapTooltip.classList.add('visible');
    });

    cell.addEventListener('mouseleave', function () {
      heatmapTooltip.classList.remove('visible');
      heatmapTooltip.style.display = 'none';
    });

    // Click → scroll to related issue
    cell.addEventListener('click', function () {
      var issueId = cell.dataset.issueLink;
      if (issueId) {
        var target = $('#' + issueId);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'center' });
          target.classList.add('highlight-flash');
          setTimeout(function () { target.classList.remove('highlight-flash'); }, 2000);
        }
      }
    });
  });

  /* ── HEALTH SCORE GAUGE ANIMATION ──────────────────────────── */
  var gaugeObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;

      // Animate gauge ring
      var fill = entry.target.querySelector('.gauge-fill');
      if (fill) {
        var score = parseInt(fill.dataset.score) || 0;
        var circumference = 2 * Math.PI * 54; // r=54
        var offset = circumference - (score / 100) * circumference;
        fill.style.strokeDasharray = circumference;
        fill.style.strokeDashoffset = circumference;
        requestAnimationFrame(function () {
          fill.style.transition = 'stroke-dashoffset 1.5s cubic-bezier(0.16,1,0.3,1)';
          fill.style.strokeDashoffset = offset;
        });
      }

      // Animate score number
      var scoreEl = entry.target.querySelector('.gauge-score');
      if (scoreEl) {
        var target = parseInt(scoreEl.dataset.target) || 0;
        animateNumber(scoreEl, 0, target, 1200);
      }

      gaugeObserver.unobserve(entry.target);
    });
  }, { threshold: 0.3 });

  $$('.gauge-container').forEach(function (el) { gaugeObserver.observe(el); });

  // Animate score card numbers
  var cardObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      var numEl = entry.target.querySelector('.score-card-number');
      if (numEl) {
        var target = parseInt(numEl.dataset.target) || 0;
        animateNumber(numEl, 0, target, 800);
      }
      cardObserver.unobserve(entry.target);
    });
  }, { threshold: 0.3 });

  $$('.score-card').forEach(function (el) { cardObserver.observe(el); });

  function animateNumber(el, from, to, duration) {
    var start = performance.now();
    function update(now) {
      var progress = Math.min((now - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      el.textContent = Math.round(from + (to - from) * eased);
      if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
  }

  /* ── SORT ENGINE ───────────────────────────────────────────── */
  var severityOrder = { critical: 0, major: 1, minor: 2, suggestion: 3 };

  $$('.sortable-header').forEach(function (header) {
    header.addEventListener('click', function () {
      var table = header.closest('.audit-table');
      if (!table) return;
      var colIndex = Array.from(header.parentNode.children).indexOf(header);
      var tbody = table.querySelector('tbody');
      if (!tbody) return;

      var rows = Array.from(tbody.querySelectorAll('tr'));
      var sortType = header.dataset.sortType || 'text';
      var asc = !header.classList.contains('sort-asc');

      // Clear other sort indicators
      $$('.sortable-header', table).forEach(function (h) {
        h.classList.remove('sort-asc', 'sort-desc');
      });
      header.classList.add(asc ? 'sort-asc' : 'sort-desc');

      rows.sort(function (a, b) {
        var aVal = a.children[colIndex] ? a.children[colIndex].textContent.trim() : '';
        var bVal = b.children[colIndex] ? b.children[colIndex].textContent.trim() : '';

        if (sortType === 'severity') {
          aVal = severityOrder[aVal.toLowerCase()] !== undefined ? severityOrder[aVal.toLowerCase()] : 99;
          bVal = severityOrder[bVal.toLowerCase()] !== undefined ? severityOrder[bVal.toLowerCase()] : 99;
          return asc ? aVal - bVal : bVal - aVal;
        }
        if (sortType === 'number') {
          return asc ? parseFloat(aVal) - parseFloat(bVal) : parseFloat(bVal) - parseFloat(aVal);
        }
        return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      });

      rows.forEach(function (row) { tbody.appendChild(row); });
    });
  });

  /* ── MERMAID INIT ──────────────────────────────────────────── */
  if (window.mermaid) {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        darkMode: true,
        background: '#1C1C35',
        primaryColor: '#D4A843',
        primaryTextColor: '#E8E6E3',
        primaryBorderColor: '#3A3A55',
        lineColor: '#6B6775',
        secondaryColor: '#252545',
        tertiaryColor: '#2A2A3E',
        nodeTextColor: '#E8E6E3',
        edgeLabelBackground: '#252545',
        clusterBkg: '#1C1C35',
        clusterBorder: '#3A3A55',
        titleColor: '#D4A843'
      },
      flowchart: { useMaxWidth: true, htmlLabels: true },
      securityLevel: 'loose'
    });

    document.addEventListener('DOMContentLoaded', function () {
      $$('.mermaid-diagram').forEach(function (el, i) {
        var id = 'mermaid-graph-' + i;
        try {
          mermaid.render(id, el.textContent.trim()).then(function (result) {
            el.innerHTML = result.svg;
            el.classList.add('rendered');
          });
        } catch (err) {
          el.innerHTML = '<p style="color:#C93B3B;">Mermaid render error: ' + err.message + '</p>';
        }
      });
    });
  }

  /* ── DIFFICULTY CHART (SVG) ────────────────────────────────── */
  var chartObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      renderChart(entry.target);
      chartObserver.unobserve(entry.target);
    });
  }, { threshold: 0.2 });

  $$('.chart-container').forEach(function (el) { chartObserver.observe(el); });

  function renderChart(container) {
    var dataStr = container.dataset.values;
    if (!dataStr) return;
    var data;
    try { data = JSON.parse(dataStr); } catch (e) { return; }

    var labels = data.loops || [];
    var series = data.series || [];
    if (!labels.length || !series.length) return;

    var width = container.clientWidth || 600;
    var height = 250;
    var padding = { top: 20, right: 20, bottom: 40, left: 40 };
    var chartW = width - padding.left - padding.right;
    var chartH = height - padding.top - padding.bottom;

    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', height);

    var maxVal = 0;
    series.forEach(function (s) {
      s.values.forEach(function (v) { if (v > maxVal) maxVal = v; });
    });
    maxVal = Math.max(maxVal, 5); // minimum scale

    var colors = ['#D4A843', '#2A7B9B', '#C93B3B', '#2D8B55', '#7B6DAA'];

    // Grid lines
    for (var g = 0; g <= 5; g++) {
      var gy = padding.top + chartH - (g / 5) * chartH;
      var line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', padding.left);
      line.setAttribute('x2', padding.left + chartW);
      line.setAttribute('y1', gy);
      line.setAttribute('y2', gy);
      line.setAttribute('stroke', '#2E2E48');
      line.setAttribute('stroke-width', '1');
      svg.appendChild(line);

      var label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      label.setAttribute('x', padding.left - 8);
      label.setAttribute('y', gy + 4);
      label.setAttribute('text-anchor', 'end');
      label.setAttribute('fill', '#6B6775');
      label.setAttribute('font-size', '11');
      label.textContent = Math.round((g / 5) * maxVal);
      svg.appendChild(label);
    }

    // X axis labels
    labels.forEach(function (lbl, i) {
      var x = padding.left + (i + 0.5) * (chartW / labels.length);
      var text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', x);
      text.setAttribute('y', height - 8);
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('fill', '#9B97A0');
      text.setAttribute('font-size', '12');
      text.textContent = lbl;
      svg.appendChild(text);
    });

    // Draw lines for each series
    series.forEach(function (s, si) {
      var color = colors[si % colors.length];
      var points = [];

      s.values.forEach(function (v, vi) {
        var x = padding.left + (vi + 0.5) * (chartW / labels.length);
        var y = padding.top + chartH - (v / maxVal) * chartH;
        points.push(x + ',' + y);

        // Dot
        var circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', x);
        circle.setAttribute('cy', y);
        circle.setAttribute('r', '4');
        circle.setAttribute('fill', color);
        circle.style.opacity = '0';
        circle.style.transition = 'opacity 0.5s ' + (vi * 0.1) + 's';
        svg.appendChild(circle);
        requestAnimationFrame(function () { circle.style.opacity = '1'; });
      });

      // Line
      var polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
      polyline.setAttribute('points', points.join(' '));
      polyline.setAttribute('fill', 'none');
      polyline.setAttribute('stroke', color);
      polyline.setAttribute('stroke-width', '2');
      polyline.setAttribute('stroke-linecap', 'round');
      polyline.setAttribute('stroke-linejoin', 'round');
      var totalLen = polyline.getTotalLength ? polyline.getTotalLength() : 1000;
      polyline.style.strokeDasharray = totalLen;
      polyline.style.strokeDashoffset = totalLen;
      polyline.style.transition = 'stroke-dashoffset 1.2s cubic-bezier(0.16,1,0.3,1)';
      svg.appendChild(polyline);
      requestAnimationFrame(function () { polyline.style.strokeDashoffset = '0'; });
    });

    // Legend
    var legendY = padding.top;
    series.forEach(function (s, si) {
      var color = colors[si % colors.length];
      var g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      var rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('x', padding.left + si * 120);
      rect.setAttribute('y', legendY - 12);
      rect.setAttribute('width', '12');
      rect.setAttribute('height', '12');
      rect.setAttribute('rx', '2');
      rect.setAttribute('fill', color);
      g.appendChild(rect);
      var text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', padding.left + si * 120 + 16);
      text.setAttribute('y', legendY);
      text.setAttribute('fill', '#9B97A0');
      text.setAttribute('font-size', '11');
      text.textContent = s.name || ('Series ' + (si + 1));
      g.appendChild(text);
      svg.appendChild(g);
    });

    container.appendChild(svg);
  }

  /* ── SEARCH (Issue Filtering) ──────────────────────────────── */
  var searchInput = $('#issue-search');
  var searchTimeout = null;

  if (searchInput) {
    searchInput.addEventListener('input', function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(function () {
        var query = searchInput.value.toLowerCase().trim();
        $$('.issue-card').forEach(function (card) {
          if (!query) {
            card.style.display = '';
            $$('.search-highlight', card).forEach(function (h) {
              h.outerHTML = h.textContent;
            });
            return;
          }
          var text = card.textContent.toLowerCase();
          if (text.indexOf(query) !== -1) {
            card.style.display = '';
          } else {
            card.style.display = 'none';
          }
        });
        // Update counter
        var visible = $$('.issue-card').filter(function (c) { return c.style.display !== 'none'; }).length;
        var counter = $('.filter-count');
        if (counter) {
          counter.textContent = visible + ' / ' + $$('.issue-card').length + ' issues';
        }
      }, 300);
    });
  }

  /* ── PRINT / EXPORT ────────────────────────────────────────── */
  // The export button is in _base.html, using onclick="window.print()"
  // Print styles are handled in CSS @media print

})();
