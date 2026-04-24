// NDC Preview — UI components
// Uses globals from data.js. React from window.

const { useState, useEffect, useRef, useMemo } = React;

/* ─── small icon set (inline SVG, 1.5 stroke, noir-ish) ─── */
const Ico = {
  search:   (p) => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>,
  lock:     (p) => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...p}><rect x="4" y="11" width="16" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/></svg>,
  npc:      (p) => <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></svg>,
  evid:     (p) => <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}><path d="M4 4h12l4 4v12H4z"/><path d="M16 4v4h4"/></svg>,
  x:        (p) => <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}><path d="m6 6 12 12M18 6 6 18"/></svg>,
  collapse: (p) => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}><path d="m15 18-6-6 6-6"/></svg>,
  expand:   (p) => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}><path d="m9 18 6-6-6-6"/></svg>,
  refresh:  (p) => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/><path d="M3 21v-5h5"/></svg>,
  export:   (p) => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}><path d="M12 3v12"/><path d="m7 8 5-5 5 5"/><path d="M5 21h14"/></svg>,
  help:     (p) => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" {...p}><circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.8.4-1 1-1 1.7v.5"/><circle cx="12" cy="17" r=".6" fill="currentColor"/></svg>,
  check:    (p) => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" {...p}><path d="m5 12 5 5 9-11"/></svg>,
  alert:    (p) => <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" {...p}><path d="M12 4 2 20h20z"/><path d="M12 10v4"/><circle cx="12" cy="17" r=".8" fill="currentColor"/></svg>,
  arrow:    (p) => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" {...p}><path d="M5 12h14M13 6l6 6-6 6"/></svg>,
};

/* ─── status badge helpers ─── */
function statusBadgeProps(status) {
  if (status === "unlocked")  return { cls: "", label: "已解锁" };
  if (status === "locked")    return { cls: "locked", label: "未解锁" };
  if (status === "not-open")  return { cls: "locked", label: "不开放" };
  return { cls: "", label: status };
}

/* ─── tween number ─── */
function TweenNumber({ value }) {
  const [v, setV] = useState(value);
  const [pulse, setPulse] = useState(false);
  useEffect(() => {
    if (value === v) return;
    setPulse(true);
    const from = v, to = value;
    const start = performance.now(), dur = 150;
    let raf;
    const step = (t) => {
      const k = Math.min(1, (t - start) / dur);
      setV(Math.round(from + (to - from) * k));
      if (k < 1) raf = requestAnimationFrame(step);
      else setTimeout(() => setPulse(false), 80);
    };
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, [value]);
  return <span className={"tween-wrap" + (pulse ? " pulse" : "")}>{v}</span>;
}

/* ─── typewriter cursor for loading states ─── */
function TypeCursor() {
  const [on, setOn] = useState(true);
  useEffect(() => {
    const id = setInterval(() => setOn((x) => !x), 500);
    return () => clearInterval(id);
  }, []);
  return <span style={{ display: "inline-block", width: "0.55em", background: on ? "var(--gold)" : "transparent", height: "0.95em", verticalAlign: "-2px", marginLeft: 2 }} />;
}

/* ─── TOP BAR ─── */
function TopBar({ chapter, setChapter, query, setQuery }) {
  return (
    <div className="topbar">
      <div className="brand">
        <div className="brand-mark">N</div>
        <div>
          <div className="brand-name">NDC Preview</div>
          <div className="brand-sub">内容工作台 · build 0.4.2</div>
        </div>
      </div>

      <div className="top-center">
        <div className="chapter-select">
          <span className="chapter-select-label">CHAPTER</span>
          <select
            value={chapter}
            onChange={(e) => setChapter(e.target.value)}
          >
            {CHAPTERS.map((c) => (
              <option key={c.id} value={c.id}>{c.label}</option>
            ))}
          </select>
          <span className="chapter-select-caret">▾</span>
        </div>

        <label className="search">
          <span className="search-ico"><Ico.search /></span>
          <input
            placeholder="全局搜索   场景 · NPC · 证据 · 对话 ID"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <span className="search-kbd">⌘ K</span>
        </label>
      </div>

      <div className="top-actions">
        <button className="icon-btn" title="刷新数据"><Ico.refresh /></button>
        <button className="icon-btn" title="导出"><Ico.export /></button>
        <button className="icon-btn" title="帮助"><Ico.help /></button>
      </div>
    </div>
  );
}

/* ─── SIDEBAR ─── */
function Sidebar({ loopId, setLoopId, chapter, sceneId, setSceneId, collapsed, setCollapsed }) {
  const [tip, setTip] = useState(null);
  const loops = LOOPS.filter((l) => l.chapter === chapter || l.status !== "locked" || true); // show all, dim locked
  const stages = STAGES[loopId] || [];
  const loop = LOOPS.find((l) => l.id === loopId);

  if (collapsed) {
    return (
      <aside className="sidebar" style={{ padding: "10px 6px" }}>
        <button className="collapse-btn" onClick={() => setCollapsed(false)} title="展开"><Ico.expand /></button>
        <div style={{ marginTop: 14, display: "flex", flexDirection: "column", gap: 6, alignItems: "center" }}>
          {LOOPS.map((l) => (
            <button
              key={l.id}
              className={"loop-chip" + (l.id === loopId ? " active" : "") + (l.status === "locked" ? " locked" : "")}
              style={{ width: 36, padding: "6px 0", textAlign: "center" }}
              onClick={() => setLoopId(l.id)}
              title={l.title}
            >L{l.id.slice(4)}</button>
          ))}
        </div>
      </aside>
    );
  }

  return (
    <aside className="sidebar">
      <div className="side-head">
        <div className="side-title">Loops</div>
        <button className="collapse-btn" onClick={() => setCollapsed(true)} title="折叠"><Ico.collapse /></button>
      </div>
      <div className="loop-row">
        {LOOPS.map((l) => (
          <button
            key={l.id}
            className={"loop-chip" + (l.id === loopId ? " active" : "") + (l.status === "locked" ? " locked" : "")}
            onClick={() => setLoopId(l.id)}
            title={l.title}
          >LOOP {l.id.slice(4)}</button>
        ))}
      </div>

      <div className="loop-title">
        <span className="kicker">Current · {chapter}</span>
        {loop ? loop.title : ""}
      </div>

      <div className="stages">
        {stages.map((stage) => (
          <div className="stage" key={stage.key}>
            <div className="stage-label">{stage.label}</div>
            {stage.items.map((it) => {
              const isLocked = it.status !== "unlocked";
              const active = sceneId === it.id;
              return (
                <div
                  key={it.id}
                  className={"scene-item" + (active ? " active" : "") + (isLocked ? " locked" : "")}
                  onClick={() => !isLocked && setSceneId(it.id)}
                  onMouseEnter={() => isLocked && it.unlockHint && setTip({ id: it.id, text: it.unlockHint })}
                  onMouseLeave={() => setTip(null)}
                  style={{ position: "relative" }}
                >
                  {isLocked && <span style={{ color: "var(--locked)" }}><Ico.lock /></span>}
                  <span className="scene-name">{it.name}</span>
                  <span className="scene-badges">
                    <span className="badge" title="NPC"><Ico.npc />&thinsp;{it.npcs}</span>
                    <span className={"badge " + (it.evid > 0 ? "gold" : "")} title="证据"><Ico.evid />&thinsp;{it.evid}</span>
                  </span>
                  {tip && tip.id === it.id && (
                    <span className="tip show">{tip.text}</span>
                  )}
                </div>
              );
            })}
          </div>
        ))}

        <div style={{ padding: "24px 14px 0", color: "var(--text-faint)", fontSize: 10.5, fontFamily: "JetBrains Mono, monospace", letterSpacing: ".08em" }}>
          <div style={{ opacity: .5 }}>{'// end of ' + loopId}</div>
          <div style={{ opacity: .3, marginTop: 4 }}>loaded<TypeCursor /></div>
        </div>
      </div>
    </aside>
  );
}

/* ─── SCENE VIEW ─── */
function SceneView({ sceneId, onPickNpc, onPickEv }) {
  const scene = SCENES[sceneId];
  const [labels, setLabels] = useState("auto"); // auto | all | off

  if (!scene) return <div style={{ padding: 40, color: "var(--text-dim)" }}>选择一个场景</div>;

  const bgMissing = scene.bgStatus !== "ok";
  const bgCls = "scene-bg" + (bgMissing ? " placeholder" : "");

  const counts = {
    npc: scene.npcs.length,
    npcMiss: scene.npcs.filter((n) => n.artStatus !== "ok").length,
    ev: scene.evidence.length,
    evMiss: scene.evidence.filter((e) => e.artStatus !== "ok").length,
  };

  return (
    <div className="scene-view">
      <div className="scene-head">
        <div className="scene-heading">
          <div className="scene-crumb">{scene.loop.toUpperCase()} · SCENE · {scene.id}</div>
          <h1>{scene.name}</h1>
          <div className="scene-sub">
            <span>时间 · <b>{scene.timeOfDay}</b></span>
            <span>NPC · <b><TweenNumber value={counts.npc} /></b>{counts.npcMiss > 0 && <span style={{ color: "var(--brick)" }}>&nbsp;({counts.npcMiss} 缺立绘)</span>}</span>
            <span>证据 · <b><TweenNumber value={counts.ev} /></b>{counts.evMiss > 0 && <span style={{ color: "var(--brick)" }}>&nbsp;({counts.evMiss} 缺美术)</span>}</span>
            <span>背景 · <b style={{ color: bgMissing ? "var(--brick)" : "var(--ok)" }}>
              {scene.bgStatus === "ok" ? "已完成" : scene.bgStatus === "wip" ? "进行中" : "缺美术"}
            </b></span>
          </div>
        </div>
      </div>

      <div className="scene-stage">
        <div className={bgCls} data-id={scene.id} />
        <div className="scene-vignette" />

        <div className="scene-corner">
          <span className="dot" />REC · {scene.id.toUpperCase()}
        </div>
        <div className="scene-corner r">
          {scene.timeOfDay} · TAKE 001
        </div>

        {scene.npcs.map((n) => (
          <div
            key={n.id}
            className={"npc-pin"}
            style={{ left: n.x + "%", top: n.y + "%" }}
            onClick={() => onPickNpc(n.id)}
          >
            <div className={"npc-figure" + (n.artStatus === "missing" ? " missing" : "")} />
            <div className="pin-ground" />
            <div className="npc-label">{n.name}</div>
          </div>
        ))}

        <div className="scene-toolbar">
          <button className={labels === "auto" ? "active" : ""} onClick={() => setLabels("auto")}>自动</button>
          <button className={labels === "all" ? "active" : ""} onClick={() => setLabels("all")}>全部</button>
          <button className={labels === "off" ? "active" : ""} onClick={() => setLabels("off")}>仅坐标</button>
        </div>
      </div>

      {bgMissing && (
        <div style={{ fontSize: 11, fontFamily: "JetBrains Mono, monospace", color: "var(--warn)", display: "flex", gap: 8, alignItems: "center" }}>
          <Ico.alert /> 场景背景待交付 — <span style={{ color: "var(--text-dim)" }}>{scene.bgPrompt}</span>
        </div>
      )}

      <div className="ev-section">
        <div className="section-head">
          <h2>证据</h2>
          <span className="count">{scene.evidence.length} 件</span>
          <span className="rule" />
          <span style={{ fontFamily: "JetBrains Mono, monospace", fontSize: 10, color: "var(--text-faint)", letterSpacing: ".1em" }}>
            原始 {scene.evidence.filter(e=>e.type==="原始").length} · 分析 {scene.evidence.filter(e=>e.type==="分析后").length} · 合成 {scene.evidence.filter(e=>e.type==="合成物").length}
          </span>
        </div>
        <div className="ev-grid">
          {scene.evidence.map((e) => (
            <div
              key={e.id}
              className={"ev-card " + (e.artStatus === "missing" ? "missing" : e.artStatus === "wip" ? "wip" : "")}
              onClick={() => onPickEv(e.id)}
            >
              <div className="ev-top">
                <span className="ev-id">#{e.id}</span>
                <span className={"ev-type " + (e.type === "分析后" ? "derived" : e.type === "合成物" ? "syn" : "")}>{e.type}</span>
              </div>
              <div className="ev-title">{e.title}</div>
              <div className="ev-foot">
                <span className={"ev-art-status " + (e.artStatus === "ok" ? "ok" : e.artStatus === "wip" ? "wip" : "miss")}>
                  <span className="dot" />
                  {e.artStatus === "ok" ? "已完成" : e.artStatus === "wip" ? "进行中" : "缺美术"}
                </span>
                <span style={{ color: "var(--text-faint)" }}>{e.npc !== "—" ? e.npc : "场景拾取"}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ─── ART OVERVIEW ─── */
function ArtView() {
  const [sub, setSub] = useState("evidence");
  const [filter, setFilter] = useState("all");
  const [collapsed, setCollapsed] = useState({});

  const rows = ART_NEEDS[sub];
  const filtered = filter === "all" ? rows : rows.filter((r) => r.status === filter);

  // group by loop/scene for evidence, by chapter otherwise
  const grouped = {};
  filtered.forEach((r) => {
    const k = sub === "evidence" ? (r.scene || r.loop || r.chapter) : (r.chapter);
    (grouped[k] ||= []).push(r);
  });

  const counts = {
    all: rows.length,
    ok: rows.filter((r) => r.status === "ok").length,
    wip: rows.filter((r) => r.status === "wip").length,
    missing: rows.filter((r) => r.status === "missing").length,
  };

  return (
    <div className="art-view">
      <div className="sub-tabs">
        <button className={"sub-tab" + (sub === "evidence" ? " active" : "")} onClick={() => setSub("evidence")}>证据 <span className="tag">{ART_NEEDS.evidence.length}</span></button>
        <button className={"sub-tab" + (sub === "npcs" ? " active" : "")} onClick={() => setSub("npcs")}>人物 <span className="tag">{ART_NEEDS.npcs.length}</span></button>
        <button className={"sub-tab" + (sub === "scenes" ? " active" : "")} onClick={() => setSub("scenes")}>场景 <span className="tag">{ART_NEEDS.scenes.length}</span></button>
      </div>

      <div className="art-filters">
        <span className="filter-label">状态</span>
        {[["all", "全部", counts.all], ["missing", "缺美术", counts.missing], ["wip", "进行中", counts.wip], ["ok", "已完成", counts.ok]].map(([k, l, c]) => (
          <button key={k} className={"pill" + (filter === k ? " on" : "")} onClick={() => setFilter(k)}>
            {l} · {c}
          </button>
        ))}
      </div>

      {Object.entries(grouped).map(([groupKey, list]) => {
        const isCol = collapsed[groupKey];
        return (
          <div key={groupKey}>
            <div className={"group-hdr" + (isCol ? " collapsed" : "")} onClick={() => setCollapsed((s) => ({ ...s, [groupKey]: !s[groupKey] }))}>
              <span className="chev">▾</span>
              <span>{groupKey}</span>
              <span className="meta">
                <span className="badge miss">{list.filter((r) => r.status === "missing").length}</span>
                <span className="badge warn">{list.filter((r) => r.status === "wip").length}</span>
                <span className="badge ok">{list.filter((r) => r.status === "ok").length}</span>
              </span>
            </div>
            {!isCol && (
              <table className="art-table">
                <thead>
                  <tr>
                    <th style={{ width: 72 }}>ID</th>
                    <th>{sub === "evidence" ? "名称" : "名称"}</th>
                    {sub === "evidence" && <th>场景</th>}
                    {sub === "scenes" && <th>Loop</th>}
                    <th style={{ width: 130 }}>状态</th>
                    <th style={{ width: 90 }}></th>
                  </tr>
                </thead>
                <tbody>
                  {list.map((r) => (
                    <tr key={r.id} className={r.status}>
                      <td><span className="mono" style={{ color: "var(--gold)" }}>#{r.id}</span></td>
                      <td>{r.title || r.name}</td>
                      {sub === "evidence" && <td style={{ color: "var(--text-dim)" }}>{r.scene}</td>}
                      {sub === "scenes" && <td style={{ color: "var(--text-dim)" }}>{r.loop}</td>}
                      <td>
                        <span className={"status-cell " + r.status}>
                          {r.status === "ok" ? <Ico.check /> : r.status === "missing" ? <Ico.alert /> : <span style={{ width: 8, height: 8, background: "var(--warn)", display: "inline-block" }} />}
                          {r.status === "ok" ? "已完成" : r.status === "wip" ? "进行中" : "缺美术"}
                        </span>
                      </td>
                      <td style={{ textAlign: "right" }}><span className="link mono" style={{ fontSize: 10 }}>打开 →</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        );
      })}
    </div>
  );
}

/* ─── STORY NARRATIVE ─── */
// Render inline markers from NARRATIVE: {{#id}} evidence · {{@name}} npc · {{"id}} testimony · {{^scene}} break
function renderParagraph(text, onPickEv, onPickNpc) {
  if (text === "{{^scene}}") return { sceneBreak: true };
  const out = [];
  const re = /\{\{([#@"^])([^}]*)\}\}/g;
  let last = 0, m, key = 0;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const [, kind, val] = m;
    if (kind === "#") {
      const ev = EVIDENCE[val];
      out.push(
        <span key={key++} className="inline-ev" onClick={() => onPickEv(val)} title={ev ? ev.title : val}>
          <span className="inline-ev-id">#{val}</span>{ev && <span className="inline-ev-name">{ev.title}</span>}
        </span>
      );
    } else if (kind === "@") {
      const npc = Object.values(NPCS).find((n) => n.name === val);
      out.push(
        <span key={key++} className="inline-npc" onClick={() => npc && onPickNpc(npc.id)}>
          {val}
        </span>
      );
    } else if (kind === '"') {
      const t = TESTIMONIES[val];
      out.push(
        <span key={key++} className="inline-testimony" title={t ? t.text : val}>
          <span className="inline-q-mark">“”</span><span className="mono inline-q-id">#{val}</span>
        </span>
      );
    }
    last = m.index + m[0].length;
  }
  if (last < text.length) out.push(text.slice(last));
  return { nodes: out };
}

function NarrativeView({ loopId, setLoopId, onPickEv, onPickNpc }) {
  const chapter = NARRATIVE.find((c) => c.loop === loopId) || NARRATIVE[0];
  const [fontScale, setFontScale] = useState(1);

  // stats
  const wordCount = chapter.body.filter((p) => p !== "{{^scene}}").join("").length;
  const evidenceRefs = new Set();
  const npcRefs = new Set();
  chapter.body.forEach((p) => {
    (p.match(/\{\{#[^}]+\}\}/g) || []).forEach((m) => evidenceRefs.add(m.slice(3, -2)));
    (p.match(/\{\{@[^}]+\}\}/g) || []).forEach((m) => npcRefs.add(m.slice(3, -2)));
  });

  return (
    <div className="narr-view">
      <aside className="narr-side">
        <div className="smallcap" style={{ marginBottom: 10, color: "var(--gold-2)" }}>章节</div>
        <div className="narr-toc">
          {NARRATIVE.map((c) => (
            <button
              key={c.loop}
              className={"narr-toc-item" + (c.loop === loopId ? " active" : "")}
              onClick={() => setLoopId(c.loop)}
            >
              <span className="narr-toc-no">{c.no}</span>
              <span className="narr-toc-title">{c.title}</span>
              <span className="narr-toc-chap mono">{c.chapter.split(" · ")[0]}</span>
            </button>
          ))}
        </div>
      </aside>

      <article className="narr-article" style={{ fontSize: 15 * fontScale }}>
        <header className="narr-head">
          <div className="narr-kicker mono">{chapter.chapter} · {chapter.no.toUpperCase()}</div>
          <h1 className="narr-title">{chapter.title}</h1>
          {chapter.epigraph && chapter.epigraph !== "—" && (
            <div className="narr-epigraph">{chapter.epigraph}</div>
          )}
          <div className="narr-rule" />
        </header>

        <div className="narr-body">
          {chapter.body.map((p, i) => {
            const r = renderParagraph(p, onPickEv, onPickNpc);
            if (r.sceneBreak) return <div key={i} className="narr-break">❦</div>;
            // drop cap on first real paragraph
            const isFirst = i === 0 || chapter.body.slice(0, i).every((q) => q === "{{^scene}}");
            return (
              <p key={i} className={"narr-p" + (isFirst ? " first" : "")}>{r.nodes}</p>
            );
          })}
        </div>

        {chapter.pins && chapter.pins.length > 0 && (
          <footer className="narr-foot">
            {chapter.pins.map((pin, i) => (
              <div key={i} className="narr-pin">
                <div className="smallcap">{pin.label}</div>
                <div className="narr-pin-items">
                  {pin.items.map((id) => {
                    if (/^\d{7}$/.test(id)) {
                      const t = TESTIMONIES[id];
                      return <span key={id} className="inline-testimony" title={t ? t.text : id}><span className="mono inline-q-id">#{id}</span></span>;
                    }
                    const ev = EVIDENCE[id];
                    return (
                      <span key={id} className="inline-ev" onClick={() => onPickEv(id)}>
                        <span className="inline-ev-id">#{id}</span>{ev && <span className="inline-ev-name">{ev.title}</span>}
                      </span>
                    );
                  })}
                </div>
              </div>
            ))}
          </footer>
        )}

        <div className="narr-end mono">— 本章终 —</div>
      </article>
    </div>
  );
}

/* ─── FLOW ─── */
function FlowView() {
  const byId = Object.fromEntries(FLOW.nodes.map((n) => [n.id, n]));
  return (
    <div className="flow-view">
      <div className="section-head" style={{ marginBottom: 14 }}>
        <h2 className="serif">流水线 · Loop 1 码头章节</h2>
        <span className="count mono">{FLOW.nodes.length} 节点 · {FLOW.edges.length} 触发</span>
        <span className="rule" />
      </div>
      <div className="flow-canvas">
        <svg className="flow-svg" width="1300" height="260">
          <defs>
            <marker id="arr" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
              <path d="M0,0 L8,4 L0,8 z" fill="var(--gold-2)" opacity=".8" />
            </marker>
          </defs>
          {FLOW.edges.map((e, i) => {
            const a = byId[e.from], b = byId[e.to];
            const mx = (a.x + b.x) / 2;
            const d = `M ${a.x + 60} ${a.y} C ${mx} ${a.y}, ${mx} ${b.y}, ${b.x - 60} ${b.y}`;
            return (
              <g key={i}>
                <path className="flow-edge" d={d} markerEnd="url(#arr)" />
                {e.label && <text className="flow-edge-label" x={mx} y={(a.y + b.y) / 2 - 6} textAnchor="middle">{e.label}</text>}
              </g>
            );
          })}
        </svg>
        {FLOW.nodes.map((n) => (
          <div key={n.id} className={"flow-node " + n.kind} style={{ left: n.x, top: n.y }}>
            <span className="kind">{n.kind}</span>
            {n.label.split("\n").map((ln, i) => (
              <div key={i} style={{ fontFamily: i > 0 ? "JetBrains Mono, monospace" : "inherit", fontSize: i > 0 ? 10 : 11, color: i > 0 ? "var(--gold)" : "var(--text)", letterSpacing: i > 0 ? ".08em" : 0 }}>{ln}</div>
            ))}
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: 14, marginTop: 14, fontSize: 10.5, color: "var(--text-dim)", fontFamily: "JetBrains Mono, monospace", letterSpacing: ".08em" }}>
        {[["dialogue","对话"], ["branch","分支"], ["testimony","证词"], ["unlock","解锁"], ["check","校验"], ["accuse","指证"]].map(([k, l]) => (
          <span key={k} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
            <span className={"flow-node " + k} style={{ position: "static", transform: "none", padding: "2px 6px", minWidth: 0, fontSize: 9 }}>{k}</span>
            {l}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ─── AVG-style dialogue player (Disco Elysium vibe) ─── */
function AvgPlayer({ dialogueIds, focusNpc }) {
  const valid = dialogueIds.filter((d) => DIALOGUES[d]);
  const [dIdx, setDIdx] = useState(0);        // which dialogue bundle
  const [lIdx, setLIdx] = useState(0);        // which line within
  const [typed, setTyped] = useState("");     // currently typed chars
  const [done, setDone]  = useState(false);   // current line fully typed
  const [history, setHistory] = useState([]); // lines already seen this dialogue

  const cur = valid[dIdx] ? DIALOGUES[valid[dIdx]] : null;
  const line = cur?.lines[lIdx];

  // typewriter
  useEffect(() => {
    if (!line) return;
    setTyped(""); setDone(false);
    const full = line.text;
    let i = 0;
    const id = setInterval(() => {
      i++;
      setTyped(full.slice(0, i));
      if (i >= full.length) { clearInterval(id); setDone(true); }
    }, 22);
    return () => clearInterval(id);
  }, [dIdx, lIdx, valid.length]);

  // reset when npc changes
  useEffect(() => {
    setDIdx(0); setLIdx(0); setHistory([]);
  }, [focusNpc]);

  if (!valid.length) {
    return <span style={{ color: "var(--text-faint)", fontStyle: "italic", fontSize: 11 }}>暂无对白</span>;
  }

  const advance = () => {
    if (!done) {
      // skip to end
      setTyped(line.text); setDone(true);
      return;
    }
    // push current to history
    setHistory((h) => [...h, { ...line, dId: cur.id }]);
    if (lIdx + 1 < cur.lines.length) {
      setLIdx((i) => i + 1);
    } else if (dIdx + 1 < valid.length) {
      setDIdx((i) => i + 1); setLIdx(0); setHistory([]);
    } else {
      // loop back? keep at end — replay button shown
    }
  };

  const reset = () => { setLIdx(0); setHistory([]); };

  const atEnd = done && lIdx + 1 >= cur.lines.length && dIdx + 1 >= valid.length;
  const isSelf = line && line.who === focusNpc;

  return (
    <div className="avg">
      <div className="avg-tabs">
        {valid.map((did, i) => (
          <button key={did}
            className={"avg-tab" + (i === dIdx ? " active" : "")}
            onClick={() => { setDIdx(i); setLIdx(0); setHistory([]); }}
          >
            <span className="mono">#{did}</span>
          </button>
        ))}
      </div>

      {cur && (
        <div className="avg-ctx mono">
          <span className="avg-ctx-scene">{cur.scene}</span>
          <span className="avg-ctx-sep">·</span>
          <span className="avg-ctx-desc">{cur.ctx}</span>
        </div>
      )}

      <div className="avg-stage" onClick={advance} tabIndex={0}
           onKeyDown={(e) => { if (e.key === " " || e.key === "Enter") { e.preventDefault(); advance(); } }}>
        {history.length > 0 && (
          <div className="avg-history">
            {history.slice(-3).map((h, i) => (
              <div key={i} className={"avg-line faded" + (h.who === focusNpc ? " self" : "")}>
                <div className="avg-who">{h.who}<span className="avg-mood">（{h.mood}）</span></div>
                <div className="avg-text">“{h.text}”</div>
              </div>
            ))}
          </div>
        )}
        {line && (
          <div key={cur.id + "-" + lIdx} className={"avg-line current" + (isSelf ? " self" : "")}>
            <div className="avg-who">
              {line.who}
              <span className="avg-mood">（{line.mood}）</span>
            </div>
            <div className="avg-text">
              “{typed}
              {!done && <span className="avg-caret">▌</span>}
              {done && "”"}
            </div>
          </div>
        )}
        <div className="avg-footer">
          <span className="avg-progress mono">
            {lIdx + 1} / {cur.lines.length}
            <span className="avg-sep">·</span>
            {dIdx + 1} / {valid.length}
          </span>
          <span className="avg-hint mono">
            {!done ? "点击跳过打字" : atEnd ? "对白结束" : "点击 / 空格 继续 ▸"}
          </span>
        </div>
      </div>

      <div className="avg-controls">
        <button className="pill" onClick={reset}>↻ 重播本段</button>
        {atEnd && <button className="pill on" onClick={() => { setDIdx(0); setLIdx(0); setHistory([]); }}>◂ 从头</button>}
      </div>
    </div>
  );
}


/* ─── DRAWER ─── */
function CopyAssetName({ name, status }) {
  const [copied, setCopied] = useState(false);
  const onCopy = () => {
    navigator.clipboard?.writeText(name).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    });
  };
  const dotColor = status === "ok" ? "var(--ok)" : status === "wip" ? "var(--warn)" : "var(--brick)";
  return (
    <button className="copy-asset" onClick={onCopy} title="点击复制文件名">
      <span className="copy-asset-dot" style={{ background: dotColor }} />
      <span className="copy-asset-name mono">{name}</span>
      <span className="copy-asset-ico">{copied ? "✓ 已复制" : "复制"}</span>
    </button>
  );
}

function Drawer({ kind, id, onClose, onPickEv }) {
  if (!id) return null;
  const isEv = kind === "evid";
  const data = isEv ? EVIDENCE[id] : NPCS[id];
  if (!data) return null;

  return (
    <>
      <div className={"drawer-backdrop open"} onClick={onClose} />
      <div className="drawer open">
        <div className="drawer-head">
          <div>
            <div className="drawer-id">{isEv ? "EVIDENCE" : "NPC"} · #{data.id.replace("npc_","").toUpperCase()}{isEv ? "" : ""}  {isEv && "#" + data.id}</div>
            <h2 className="drawer-title">{isEv ? data.title : data.name}</h2>
            {isEv ? (
              <div className="mono" style={{ fontSize: 11, color: "var(--text-dim)", letterSpacing: ".06em", marginTop: 4 }}>
                类型 · {data.type} · 场景 · {SCENES[data.scene]?.name || data.scene}
              </div>
            ) : (
              <div className="mono" style={{ fontSize: 11, color: "var(--text-dim)", letterSpacing: ".06em", marginTop: 4 }}>
                {data.role}
              </div>
            )}
          </div>
          <button className="drawer-close" onClick={onClose}><Ico.x /></button>
        </div>

        <div className="drawer-body">
          {isEv ? <EvidenceDetail ev={data} onPickEv={onPickEv} /> : <NpcDetail npc={data} />}
        </div>
      </div>
    </>
  );
}

function EvidenceDetail({ ev, onPickEv }) {
  // build columns for derivation: sources → current → targets
  const sources = (ev.derivedFrom || []).map((i) => EVIDENCE[i]).filter(Boolean);
  const targets = (ev.derivedTo   || []).map((i) => EVIDENCE[i]).filter(Boolean);

  return (
    <>
      <section>
        <div className="smallcap" style={{ marginBottom: 8 }}>描述</div>
        <p style={{ fontFamily: "Playfair Display, serif", fontSize: 14, lineHeight: 1.6, color: "var(--parch-mute)", margin: 0 }}>
          {ev.desc}
        </p>
      </section>

      <section>
        <div className="smallcap" style={{ marginBottom: 8 }}>字段</div>
        <dl className="kv">
          <dt>ID</dt><dd className="mono" style={{ color: "var(--gold)" }}>#{ev.id}</dd>
          <dt>类型</dt><dd>{ev.type}</dd>
          <dt>场景</dt><dd>{SCENES[ev.scene]?.name || "—"}</dd>
          <dt>美术</dt><dd><span className={"status-cell " + (ev.artStatus === "ok" ? "ok" : ev.artStatus === "wip" ? "wip" : "miss")}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "currentColor", display: "inline-block" }} />
            {ev.artStatus === "ok" ? "已完成" : ev.artStatus === "wip" ? "进行中" : "缺美术"}
          </span></dd>
        </dl>
      </section>

      <section>
        <div className="smallcap" style={{ marginBottom: 8 }}>派生链</div>
        <div className="deriv">
          <div className="deriv-row">
            <div className="deriv-col">
              <div className="deriv-col-head">来源</div>
              {sources.length ? sources.map((s) => (
                <div key={s.id} className={"deriv-node" + (s.artStatus === "missing" ? " miss" : "")} onClick={() => onPickEv(s.id)}>
                  <span className="nid">#{s.id}</span>
                  {s.title}
                </div>
              )) : <div style={{ fontSize: 11, color: "var(--text-faint)", fontStyle: "italic" }}>无 — 原始证据</div>}
            </div>
            <div className="deriv-arrow"><Ico.arrow /></div>
            <div className="deriv-col" style={{ alignItems: "center" }}>
              <div className="deriv-col-head">当前</div>
              <div className="deriv-node focus">
                <span className="nid">#{ev.id}</span>
                {ev.title}
              </div>
            </div>
            <div className="deriv-arrow"><Ico.arrow /></div>
            <div className="deriv-col">
              <div className="deriv-col-head">派生</div>
              {targets.length ? targets.map((t) => (
                <div key={t.id} className={"deriv-node" + (t.artStatus === "missing" ? " miss" : "")} onClick={() => onPickEv(t.id)}>
                  <span className="nid">#{t.id}</span>
                  {t.title}
                </div>
              )) : <div style={{ fontSize: 11, color: "var(--text-faint)", fontStyle: "italic" }}>无 — 终点</div>}
            </div>
          </div>
        </div>
      </section>
    </>
  );
}

function NpcDetail({ npc }) {
  return (
    <>
      <section style={{ display: "grid", gridTemplateColumns: "120px 1fr", gap: 14, alignItems: "start" }}>
        <div style={{
          width: 120, height: 160,
          background: npc.artStatus === "ok" ? "var(--coal)" : "color-mix(in srgb, var(--brick) 10%, var(--coal))",
          border: "1px solid " + (npc.artStatus === "ok" ? "var(--gold-2)" : "var(--brick)"),
          position: "relative",
        }}>
          <div style={{
            position: "absolute", inset: 3,
            background: npc.artStatus === "ok"
              ? "repeating-linear-gradient(-45deg, rgba(232,198,120,.08) 0 2px, transparent 2px 5px), linear-gradient(180deg, #2a2116, #120c07)"
              : "repeating-linear-gradient(45deg, rgba(184,64,64,.15) 0 3px, transparent 3px 7px)",
          }} />
          {npc.artStatus !== "ok" && (
            <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center", fontFamily: "Playfair Display, serif", fontSize: 48, color: "var(--brick)", opacity: .7 }}>?</div>
          )}
        </div>
        <div>
          <div className="smallcap" style={{ marginBottom: 6 }}>美术需求</div>
          <p style={{ fontFamily: "Playfair Display, serif", fontSize: 13.5, lineHeight: 1.6, color: "var(--parch-mute)", margin: 0 }}>
            {npc.prompt}
          </p>
          <div style={{ marginTop: 10 }}>
            <CopyAssetName name={`art/npc/${npc.id}_${(npc.name || "").toLowerCase().replace(/\s+/g, "_")}.png`} status={npc.artStatus} />
          </div>
        </div>
      </section>

      <section>
        <div className="smallcap" style={{ marginBottom: 8 }}>对白 · AVG 预览</div>
        <AvgPlayer dialogueIds={npc.dialogueIds} focusNpc={npc.name} />
      </section>

      <section>
        <div className="smallcap" style={{ marginBottom: 8 }}>相关证词</div>
        {Object.values(TESTIMONIES).filter((t) => t.npc === npc.name).length ? (
          <div style={{ display: "grid", gap: 12 }}>
            {Object.values(TESTIMONIES).filter((t) => t.npc === npc.name).map((t) => (
              <div key={t.id}>
                <div className="quote">"{t.text}"</div>
                <div className="quote-meta">#{t.id} · {t.npc}</div>
              </div>
            ))}
          </div>
        ) : <span style={{ color: "var(--text-faint)", fontStyle: "italic", fontSize: 11 }}>暂无证词</span>}
      </section>
    </>
  );
}

Object.assign(window, {
  TopBar, Sidebar, SceneView, ArtView, NarrativeView, FlowView, Drawer, Ico, TweenNumber,
});
