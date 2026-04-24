// NDC Preview — app root + tweaks

const { useState, useEffect } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "standard",
  "grainOpacity": 0.06,
  "showVignette": true,
  "density": "regular",
  "brickHue": 0
}/*EDITMODE-END*/;

const TABS = [
  { id: "scene",    label: "场景视图" },
  { id: "art",      label: "美术需求总览" },
  { id: "timeline", label: "故事概览" },
];

function App() {
  const [t, setTweak] = useTweaks(TWEAK_DEFAULTS);
  const [chapter, setChapter] = useState("EPI01");
  const [loopId, setLoopId] = useState("loop1");
  const [sceneId, setSceneId] = useState("s1_palace");
  const [tab, setTab] = useState("scene");
  const [q, setQ] = useState("");
  const [collapsed, setCollapsed] = useState(false);

  // drawer
  const [drawer, setDrawer] = useState(null); // { kind: 'evid'|'npc', id }

  // derive chapter → first loop if needed when chapter changes
  useEffect(() => {
    const firstLoop = LOOPS.find((l) => l.chapter === chapter);
    if (firstLoop && !LOOPS.find((l) => l.id === loopId && l.chapter === chapter)) {
      setLoopId(firstLoop.id);
    }
  }, [chapter]);

  // reset sceneId when loop changes
  useEffect(() => {
    const stages = STAGES[loopId] || [];
    const first = stages.flatMap((s) => s.items).find((i) => i.status === "unlocked" && SCENES[i.id]);
    if (first) setSceneId(first.id);
  }, [loopId]);

  useEffect(() => {
    document.body.dataset.theme = t.theme === "standard" ? "" : t.theme;
    document.documentElement.style.setProperty("--grain-opacity", t.grainOpacity);
    document.documentElement.style.setProperty("--brick-hue-shift", (t.brickHue || 0) + "deg");
  }, [t.theme, t.grainOpacity, t.brickHue]);

  // Esc closes drawer
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape") setDrawer(null); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div className={"app" + (collapsed ? " sidebar-collapsed" : "")} data-screen-label="NDC Preview">
      <TopBar chapter={chapter} setChapter={setChapter} query={q} setQuery={setQ} />

      <Sidebar
        chapter={chapter}
        loopId={loopId} setLoopId={setLoopId}
        sceneId={sceneId} setSceneId={setSceneId}
        collapsed={collapsed} setCollapsed={setCollapsed}
      />

      <div className="main">
        <div className="tabs">
          {TABS.map((tb, i) => (
            <button
              key={tb.id}
              className={"tab" + (tab === tb.id ? " active" : "")}
              onClick={() => setTab(tb.id)}
            >
              <span className="mono-idx">0{i + 1}</span>{tb.label}
            </button>
          ))}
          <span className="tab-meta">
            {chapter} · {LOOPS.find((l) => l.id === loopId)?.title || ""} · 最后更新 04·24 16:20
          </span>
        </div>

        <div className="view" key={tab}>
          {tab === "scene"    && <SceneView sceneId={sceneId}
                                   onPickNpc={(id) => setDrawer({ kind: "npc",  id })}
                                   onPickEv={(id)  => setDrawer({ kind: "evid", id })} />}
          {tab === "art"      && <ArtView />}
          {tab === "timeline" && <NarrativeView loopId={loopId} setLoopId={setLoopId}
                                   onPickNpc={(id) => setDrawer({ kind: "npc",  id })}
                                   onPickEv={(id)  => setDrawer({ kind: "evid", id })} />}

        </div>

        <Drawer
          kind={drawer?.kind}
          id={drawer?.id}
          onClose={() => setDrawer(null)}
          onPickEv={(id) => setDrawer({ kind: "evid", id })}
        />
      </div>

      {t.showVignette && <div className="vignette" />}
      <div className="grain" style={{ opacity: t.grainOpacity }} />

      <TweaksPanel>
        <TweakSection label="配色方向" />
        <TweakRadio
          label="质感"
          value={t.theme}
          options={[
            { value: "standard", label: "标准 · 煤黑+暗红+金黄" },
            { value: "darker",   label: "更暗更低饱和" },
            { value: "warm",     label: "偏暖 · 旧地图" },
          ]}
          onChange={(v) => setTweak("theme", v)}
        />
        <TweakSection label="纹理" />
        <TweakSlider label="纸张颗粒" value={t.grainOpacity} min={0} max={0.18} step={0.01}
                     onChange={(v) => setTweak("grainOpacity", v)} />
        <TweakToggle label="镜头晕影" value={t.showVignette}
                     onChange={(v) => setTweak("showVignette", v)} />
      </TweaksPanel>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
