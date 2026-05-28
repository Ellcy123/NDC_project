const { createApp, ref, reactive, computed, onMounted } = Vue;

createApp({
  setup() {
    // ─── state ───
    const loading = ref(true);
    const tablesLoadedCount = ref(0);
    const units = [1, 2];

    const T = reactive({
      SceneConfig: [],
      ItemStaticData: [],
      NPCStaticData: [],
      NPCLoopData: [],
      Talk: [],
      Testimony: [],
      TestimonyItem: [],
      DoubtConfig: [],
      ExposeData: [],
      ChapterConfig: [],
      LocationConfig: [],
    });

    const IDX = reactive({
      item: {}, npc: {}, talk: {}, testimony: {}, testimonyItem: {},
      doubt: {}, expose: {}, chapter: {}, scene: {}, location: {},
      npcLoopByNpcId: {},
    });

    const unitOpen = reactive({ 1: true, 2: false });
    const loopOpen = reactive({});
    const emptyScenesOpen = reactive({});  // per loop: u-l → bool
    const selected = ref(null);  // {type, id, ...}
    const history = ref([]);

    const canBack = computed(() => history.value.length > 1);

    // ─── data load ───
    async function fetchTable(name) {
      const r = await fetch(`/api/table/${name}`);
      if (!r.ok) return [];
      return await r.json();
    }

    function indexById(list, key = 'id') {
      const m = {};
      for (const x of list) m[String(x[key])] = x;
      return m;
    }

    onMounted(async () => {
      const allNames = await (await fetch('/api/tables')).json();
      tablesLoadedCount.value = allNames.length;

      const names = ['SceneConfig','ItemStaticData','NPCStaticData','NPCLoopData',
                     'Talk','Testimony','TestimonyItem','DoubtConfig','ExposeData',
                     'ChapterConfig','LocationConfig'];
      const arrs = await Promise.all(names.map(fetchTable));
      names.forEach((n, i) => { T[n] = arrs[i]; });

      IDX.item = indexById(T.ItemStaticData);
      IDX.npc = indexById(T.NPCStaticData);
      IDX.talk = indexById(T.Talk);
      IDX.testimony = indexById(T.Testimony);
      IDX.testimonyItem = indexById(T.TestimonyItem);
      IDX.doubt = indexById(T.DoubtConfig);
      IDX.expose = indexById(T.ExposeData);
      IDX.chapter = indexById(T.ChapterConfig);
      IDX.scene = indexById(T.SceneConfig, 'sceneId');
      IDX.location = indexById(T.LocationConfig);

      // NPCLoopData grouped by NPC.id
      IDX.npcLoopByNpcId = {};
      for (const lpd of T.NPCLoopData) {
        const nid = String(lpd.NPC && lpd.NPC.id || lpd.npcId || '');
        if (!nid) continue;
        (IDX.npcLoopByNpcId[nid] = IDX.npcLoopByNpcId[nid] || []).push(lpd);
      }

      loading.value = false;
    });

    // ─── helpers ───
    const localText = (val) => {
      if (Array.isArray(val)) return val[0] || val[1] || '';
      return val || '';
    };

    // ─── lookups ───
    const itemById = (id) => IDX.item[String(id)];
    const npcById = (id) => IDX.npc[String(id)];
    const talkById = (id) => IDX.talk[String(id)];
    const testimonyItemById = (id) => IDX.testimonyItem[String(id)];
    const doubtById = (id) => IDX.doubt[String(id)];
    const exposeById = (id) => IDX.expose[String(id)];
    const chapterById = (id) => IDX.chapter[String(id)];
    const sceneById = (id) => IDX.scene[String(id)];
    const locationById = (id) => IDX.location[String(id)];

    // ─── name resolvers ───
    const itemName = (id) => {
      const it = itemById(id);
      if (!it) return `(缺失 #${id})`;
      return localText(it.Name);
    };
    const npcName = (id) => {
      const n = npcById(id);
      if (!n) return `(缺失 #${id})`;
      return localText(n.Name);
    };
    const talkPreview = (id) => {
      const t = talkById(id);
      if (!t) return `(缺失 #${id})`;
      const speaker = localText(t.Speaker && t.Speaker.Name) || '?';
      const words = localText(t.Words);
      const snippet = words.length > 28 ? words.slice(0, 28) + '…' : words;
      return `${speaker}：${snippet}`;
    };
    const talkSpeakerName = (id) => {
      const t = talkById(id);
      if (!t || !t.Speaker) return '?';
      return localText(t.Speaker.Name);
    };
    const testimonyItemPreview = (id) => {
      const ti = testimonyItemById(id);
      if (!ti) return `(缺失 #${id})`;
      const s = localText(ti.testimony);
      return s.length > 30 ? s.slice(0, 30) + '…' : s;
    };

    // ─── icons / labels ───
    const itemTypeIcon = (id) => {
      const it = itemById(id);
      if (!it) return '❓';
      const t = String(it.itemType || '');
      return ({
        '0': '🎨', '1': '📷', '2': '🌿', '3': '📦', '4': '📜',
        '5': '🚪', '6': '🔧', '7': '📥', '8': '⬆️', '9': '⬇️',
      })[t] || '📦';
    };
    const itemTypeLabel = (t) => ({
      '0': '装饰', '1': '线索', '2': '环境', '3': '道具', '4': '便条',
      '5': '门', '6': '可交互道具', '7': '内嵌道具', '8': '上楼梯', '9': '下楼梯',
    })[String(t)] || `类型${t}`;
    const conditionTypeLabel = (t) => ({
      '1': '📦 道具',
      '2': '🕸 关系网',
      '3': '🕒 时间线',
      '4': '💬 证词条目',
    })[String(t)] || `类型${t}`;
    const conditionRefType = (c) => {
      const t = String(c.type);
      if (t === '1') return 'item';
      if (t === '4') return 'testimony';
      return '';
    };
    const conditionRefLabel = (c) => {
      const t = String(c.type);
      if (t === '1') return itemName(c.param);
      if (t === '4') return testimonyItemPreview(c.param);
      return `param: ${c.param}`;
    };
    const talkScriptLabel = (id) => {
      const t = talkById(id);
      if (!t || !t.script) return '';
      const s = String(t.script);
      return ({
        '1': '分支选择',
        '2': '对话结束 (end)',
        '3': '获取道具 (get)',
        '7': '进入指证 (expose)',
        '8': '切换场景 (change_scene)',
        '10': '播放视频 (play_video)',
        '11': '最终指证 (finalexpose)',
        'end': '对话结束',
        'expose': '进入指证',
        'Expose': '进入指证',
        'play_video': '播放视频',
        'finalexpose': '最终指证',
        'interrupt': '中断对话',
        'get': '获取道具',
        'unlock_map': '解锁地图',
      })[s] || `script=${s}`;
    };
    const talkBranches = (id) => {
      const t = talkById(id);
      if (!t || String(t.script) !== '1' || !Array.isArray(t.Parameters)) return [];
      return t.Parameters.map(p => ({
        text: p.ParameterStr,
        next: p.ParameterInt,
      }));
    };

    // ─── scene helpers ───
    const sceneName = (s) => {
      if (!s) return '?';
      const loc = s.location;
      if (loc && typeof loc === 'object') return localText(loc.Name) || s.note || '?';
      return s.note || '?';
    };
    const locationName = (s) => sceneName(s);
    const sceneTypeRaw = (s) => {
      const loc = s && s.location;
      if (loc && typeof loc === 'object') return loc.sceneType || '?';
      return '?';
    };
    const sceneIcon = (s) => {
      if (!s) return '📍';
      const hasItems = (s.ItemIDs || []).length > 0;
      const hasNpcs = (s.NPCInfos || []).length > 0;
      if (s.firstEnterTalk && !hasItems && !hasNpcs) return '🎬';
      if (hasNpcs) return '💬';
      if (hasItems) return '🔍';
      return '📍';
    };
    const npcId = (info) => {
      if (!info) return '';
      if (info.NPC && info.NPC.id) return String(info.NPC.id);
      return String(info.npcId || info.id || '');
    };

    // ─── chapter / loop helpers ───
    const chapterIdFor = (unit, loop) => `${unit}0${loop}`;  // 101, 102... 201, 202...
    const chapterByLoop = (unit, loop) => chapterById(chapterIdFor(unit, loop));
    const chapterTitle = (unit, loop) => {
      const c = chapterByLoop(unit, loop);
      if (!c) return '';
      return localText(c.chapterTitle);
    };
    const loopScenes = (unit, loop) => {
      const prefix = `${unit}${loop}`;
      return T.SceneConfig
        .filter(s => String(s.sceneId).startsWith(prefix))
        .slice()
        .sort((a, b) => String(a.sceneId).localeCompare(String(b.sceneId)));
    };
    const sceneHasContent = (s) => {
      if (s.firstEnterTalk) return true;
      if ((s.NPCInfos || []).length > 0) return true;
      if (displayItemIds(s).length > 0) return true;
      return false;
    };
    const loopScenesWithContent = (u, l) => loopScenes(u, l).filter(sceneHasContent);
    const loopScenesEmpty = (u, l) => loopScenes(u, l).filter(s => !sceneHasContent(s));
    const loopDoubts = (unit, loop) => {
      const c = chapterByLoop(unit, loop);
      return (c && c.doubts) || [];
    };
    const loopExposes = (unit, loop) => {
      const c = chapterByLoop(unit, loop);
      return (c && c.exposes) || [];
    };
    const npcLoopEntries = (npcId) => IDX.npcLoopByNpcId[String(npcId)] || [];

    // 过滤掉门（itemType=5）这种导航基础设施
    const HIDDEN_ITEM_TYPES = new Set(['5']);
    const displayItemIds = (s) => {
      const ids = (s && s.ItemIDs) || [];
      return ids.filter(id => {
        const it = itemById(id);
        if (!it) return true;  // 缺失的还是要显示（红色）
        return !HIDDEN_ITEM_TYPES.has(String(it.itemType));
      });
    };

    // ─── display fields ───
    const itemDisplayFields = (id) => {
      const it = itemById(id); if (!it) return {};
      const f = {};
      f['类型'] = itemTypeLabel(it.itemType);
      if (it.description) f['描述'] = localText(it.description);
      if (it.itemUseDes) f['使用说明'] = localText(it.itemUseDes);
      if (it.canAnalyzed) f['可分析'] = '是';
      if (it.canCombined) f['可合成'] = '是';
      if (it.analysedEvidence && it.analysedEvidence !== '0') {
        f['分析后→'] = `<a class="ref-chip item-inline" data-jump-item="${it.analysedEvidence}">#${it.analysedEvidence} ${itemName(it.analysedEvidence)}</a>`;
      }
      if (it.iconPath) f['图标路径'] = it.iconPath;
      return f;
    };
    const npcDisplayFields = (id) => {
      const n = npcById(id); if (!n) return {};
      const f = {};
      f['英文名'] = (Array.isArray(n.Name) ? n.Name[1] : '') || '';
      f['Role'] = ({
        '1': '死者', '2': '嫌疑人', '3': '其他', '4': '主角',
      })[String(n.role)] || `role=${n.role}`;
      f['Chapter'] = n.Chapter || '';
      return f;
    };

    // ─── validation badges ───
    const sceneBadge = (id) => {
      const s = sceneById(id);
      if (!s) return { cls: 'err', icon: '🔴' };
      // check broken item refs
      for (const itemId of s.ItemIDs || []) {
        if (!itemById(itemId)) return { cls: 'err', icon: '🔴' };
      }
      for (const info of s.NPCInfos || []) {
        if (!npcById(npcId(info))) return { cls: 'err', icon: '🔴' };
      }
      if (s.firstEnterTalk && !talkById(s.firstEnterTalk)) return { cls: 'err', icon: '🔴' };
      return { cls: 'ok', icon: '🟢' };
    };
    const talkBadge = (id) => {
      const t = talkById(id);
      if (!t) return { cls: 'err', icon: '🔴' };
      if (t.next && !talkById(t.next)) return { cls: 'err', icon: '🔴' };
      const brs = talkBranches(id);
      for (const br of brs) if (!talkById(br.next)) return { cls: 'err', icon: '🔴' };
      return { cls: 'ok', icon: '🟢' };
    };
    const doubtBadge = (id) => {
      const d = doubtById(id);
      if (!d) return { cls: 'err', icon: '🔴' };
      for (const c of d.condition || []) {
        const t = String(c.type);
        if (t === '1' && !itemById(c.param)) return { cls: 'err', icon: '🔴' };
        if (t === '4' && !testimonyItemById(c.param)) return { cls: 'err', icon: '🔴' };
      }
      return { cls: 'ok', icon: '🟢' };
    };
    const exposeBadge = (id) => {
      const e = exposeById(id);
      if (!e) return { cls: 'err', icon: '🔴' };
      if (e.testimony && e.testimony !== '0' && !testimonyItemById(e.testimony))
        return { cls: 'err', icon: '🔴' };
      for (const it of e.item || []) {
        if (!itemById(it) && !testimonyItemById(it)) return { cls: 'err', icon: '🔴' };
      }
      if (e.talkId && !talkById(e.talkId)) return { cls: 'err', icon: '🔴' };
      return { cls: 'ok', icon: '🟢' };
    };

    // ─── back-references ───
    const itemUsedIn = (itemId) => {
      const refs = [];
      const sid = String(itemId);
      // scenes
      for (const s of T.SceneConfig) {
        if ((s.ItemIDs || []).map(String).includes(sid)) {
          refs.push({ key: `scene-${s.sceneId}`, type: 'scene', id: `#${s.sceneId}`, label: sceneName(s), refType: 'scene', refId: s.sceneId });
        }
      }
      // doubt conditions
      for (const d of T.DoubtConfig) {
        for (const c of d.condition || []) {
          if (String(c.type) === '1' && String(c.param) === sid) {
            refs.push({ key: `doubt-${d.id}`, type: 'doubt', id: `#${d.id}`, label: `疑点：${d.text}`, refType: 'doubt', refId: d.id });
          }
        }
      }
      // expose items
      for (const e of T.ExposeData) {
        if ((e.item || []).map(String).includes(sid)) {
          refs.push({ key: `expose-${e.id}`, type: 'expose', id: `R${e.id}`, label: `指证回合 R${e.id}`, refType: 'expose', refId: e.id });
        }
      }
      return refs;
    };
    const itemOrTestimonyName = (id) => {
      const it = itemById(id);
      if (it) return itemName(id);
      const ti = testimonyItemById(id);
      if (ti) return testimonyItemPreview(id);
      return `(缺失 #${id})`;
    };

    // ─── navigation ───
    const isSelected = (type, id) => selected.value && selected.value.type === type && String(selected.value.id) === String(id);
    function pushSel(sel) {
      history.value.push(sel);
      if (history.value.length > 50) history.value.shift();
      selected.value = sel;
    }
    const selectLoop = (unit, loop) => pushSel({ type: 'loop', unit, loop, id: chapterIdFor(unit, loop) });
    const selectScene = (id) => pushSel({ type: 'scene', id });
    const selectItem = (id) => pushSel({ type: 'item', id });
    const selectNpc = (id) => pushSel({ type: 'npc', id });
    const selectTalk = (id) => pushSel({ type: 'talk', id });
    const selectDoubt = (id) => pushSel({ type: 'doubt', id });
    const selectExpose = (id) => pushSel({ type: 'expose', id });
    const selectTestimonyItem = (id) => pushSel({ type: 'testimonyItem', id });
    const selectByRef = (ref) => pushSel({ type: ref.refType, id: ref.refId });
    const selectByCondition = (c) => {
      const t = String(c.type);
      if (t === '1') selectItem(c.param);
      else if (t === '4') selectTestimonyItem(c.param);
    };
    function navBack() {
      if (history.value.length < 2) return;
      history.value.pop();
      selected.value = history.value[history.value.length - 1];
    }

    // ─── ui toggles ───
    function toggleUnit(u) { unitOpen[u] = !unitOpen[u]; }
    function toggleLoop(u, l) {
      const k = `${u}-${l}`;
      loopOpen[k] = !loopOpen[k];
    }
    function toggleEmptyScenes(u, l) {
      const k = `${u}-${l}`;
      emptyScenesOpen[k] = !emptyScenesOpen[k];
    }

    return {
      loading, tablesLoadedCount, units, unitOpen, loopOpen, emptyScenesOpen, selected, canBack,
      sceneHasContent, loopScenesWithContent, loopScenesEmpty, toggleEmptyScenes,
      // lookups
      itemById, npcById, talkById, testimonyItemById, doubtById, exposeById, chapterById, sceneById,
      // names
      itemName, npcName, talkPreview, talkSpeakerName, testimonyItemPreview, locationName,
      // helpers
      localText, sceneName, sceneTypeRaw, sceneIcon, npcId, itemTypeIcon, itemTypeLabel,
      conditionTypeLabel, conditionRefType, conditionRefLabel, talkScriptLabel, talkBranches,
      chapterIdFor, chapterByLoop, chapterTitle, loopScenes, loopDoubts, loopExposes,
      npcLoopEntries, displayItemIds, itemDisplayFields, npcDisplayFields, itemUsedIn, itemOrTestimonyName,
      // badges
      sceneBadge, talkBadge, doubtBadge, exposeBadge,
      // nav
      isSelected, selectLoop, selectScene, selectItem, selectNpc, selectTalk,
      selectDoubt, selectExpose, selectTestimonyItem, selectByRef, selectByCondition,
      navBack, toggleUnit, toggleLoop,
    };
  }
}).mount('#app');
