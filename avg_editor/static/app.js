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
      ArtAssetConfig: [],
    });

    const IDX = reactive({
      item: {}, npc: {}, talk: {}, testimony: {}, testimonyItem: {},
      doubt: {}, expose: {}, chapter: {}, scene: {}, location: {},
      asset: {},
      npcLoopByNpcId: {},
      scenesByAssetId: {},
    });

    const unitOpen = reactive({ 1: true, 2: false });
    const loopOpen = reactive({});
    const unmarkedScenesOpen = reactive({});  // per loop: u-l → bool

    // 美术需求总览筛选状态
    const artFilter = reactive({ q: '', onlyEmpty: false });

    // 编辑状态
    const editMode = ref(false);
    const draft = reactive({});
    const saveStatus = ref('');  // 'saving' / 'saved' / 'error' / ''

    // 每种 type 对应（表名 + 主键 + 可编辑字段）
    const EDITABLE_MAP = {
      scene: {
        table: 'SceneConfig', pk: 'sceneId',
        fields: ['ArtRequirement', 'openInLoops', 'sceneCategory', 'note'],
      },
      npc: {
        table: 'NPCStaticData', pk: 'id',
        fields: ['ArtRequirement', 'Name', 'role', 'Chapter'],
      },
      item: {
        table: 'ItemStaticData', pk: 'id',
        fields: ['ArtRequirement', 'Name', 'itemType', 'description', 'itemUseDes',
                 'canAnalyzed', 'canCombined', 'iconPath', 'folderPath', 'ActionParam'],
      },
      doubt: {
        table: 'DoubtConfig', pk: 'id',
        fields: ['text', 'isFragment'],
      },
      testimonyItem: {
        table: 'TestimonyItem', pk: 'id',
        fields: ['testimony', 'truth', 'shortDesc', 'shortTruth',
                 'testimonyType', 'triggerType', 'triggerParam'],
      },
      artAsset: {
        table: 'ArtAssetConfig', pk: 'id',
        fields: ['ArtRequirement', 'displayName'],
      },
    };
    const isEditableType = (type) => !!EDITABLE_MAP[type];

    // 双语字段（值是 [zh, en] 数组）
    // 注意：DoubtConfig.text 是字符串不是数组，不在此列
    const BILINGUAL_FIELDS = new Set([
      'Name', 'description', 'words', 'testimony', 'truth',
      'shortDesc', 'shortTruth', 'chapterTitle', 'chapterBrief', 'chapterGoal',
      'summaryTitle', 'summaryContent', 'newDoubtTitle', 'newDoubtContent', 'itemUseDes',
    ]);
    // 布尔字段
    const BOOL_FIELDS = new Set(['canAnalyzed', 'canCombined', 'isFragment']);

    // 枚举选项（给下拉框用）
    const ITEM_TYPE_OPTIONS = [
      { value: '0', label: '🎨 装饰' },
      { value: '1', label: '📷 线索' },
      { value: '2', label: '🌿 环境' },
      { value: '3', label: '📦 道具' },
      { value: '4', label: '📜 便条' },
      { value: '5', label: '🚪 门' },
      { value: '6', label: '🔧 可交互道具' },
      { value: '7', label: '📥 内嵌道具' },
      { value: '8', label: '⬆️ 上楼梯' },
      { value: '9', label: '⬇️ 下楼梯' },
    ];
    const ROLE_OPTIONS = [
      { value: '1', label: '死者' },
      { value: '2', label: '嫌疑人' },
      { value: '3', label: '其他' },
      { value: '4', label: '主角' },
    ];
    const TESTIMONY_TYPE_OPTIONS = [
      { value: '1', label: '🗣 自述' },
      { value: '2', label: '👂 见闻' },
    ];
    const TRIGGER_TYPE_OPTIONS = [
      { value: 'None', label: '无条件' },
      { value: 'Timeline', label: '🕒 时间线' },
      { value: 'RelationNetwork', label: '🕸 关系网' },
    ];
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
                     'ChapterConfig','LocationConfig','ArtAssetConfig'];
      const arrs = await Promise.all(names.map(fetchTable));
      names.forEach((n, i) => { T[n] = arrs[i] || []; });

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
      IDX.asset = indexById(T.ArtAssetConfig);

      // NPCLoopData grouped by NPC.id
      IDX.npcLoopByNpcId = {};
      for (const lpd of T.NPCLoopData) {
        const nid = String(lpd.NPC && lpd.NPC.id || lpd.npcId || '');
        if (!nid) continue;
        (IDX.npcLoopByNpcId[nid] = IDX.npcLoopByNpcId[nid] || []).push(lpd);
      }

      // 场景 → 资源 反查
      IDX.scenesByAssetId = {};
      for (const s of T.SceneConfig) {
        const loc = s.location;
        if (loc && typeof loc === 'object') {
          const img = loc.backgroundImage;
          if (img) {
            (IDX.scenesByAssetId[img] = IDX.scenesByAssetId[img] || []).push(s);
          }
        }
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
    const assetById = (id) => IDX.asset[String(id)];
    const sceneAssetId = (s) => {
      if (!s) return null;
      const loc = s.location;
      if (loc && typeof loc === 'object') return loc.backgroundImage || null;
      return null;
    };
    const scenesUsingAsset = (assetId) => IDX.scenesByAssetId[String(assetId)] || [];
    const filteredAssets = computed(() => {
      const q = (artFilter.q || '').toLowerCase().trim();
      let list = T.ArtAssetConfig.slice();
      if (q) {
        list = list.filter(a => {
          return assetFilename(a).toLowerCase().includes(q)
              || (a.displayName || '').toLowerCase().includes(q)
              || (a.ArtRequirement || '').toLowerCase().includes(q);
        });
      }
      if (artFilter.onlyEmpty) {
        list = list.filter(a => !a.ArtRequirement);
      }
      return list;
    });
    const assetStats = computed(() => {
      const total = T.ArtAssetConfig.length;
      const filled = T.ArtAssetConfig.filter(a => !!a.ArtRequirement).length;
      return { total, filled, empty: total - filled };
    });
    const assetFilename = (asset) => {
      if (!asset || !asset.id) return '';
      const path = String(asset.id).replace(/\\/g, '/');
      const parts = path.split('/');
      return parts[parts.length - 1];
    };
    const copyText = (text, ev) => {
      if (ev) ev.stopPropagation();
      if (!text) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
      } else {
        fallbackCopy(text);
      }
      if (ev && ev.currentTarget) {
        const el = ev.currentTarget;
        const old = el.textContent;
        el.textContent = '✓';
        setTimeout(() => { el.textContent = old; }, 800);
      }
    };
    function fallbackCopy(text) {
      const ta = document.createElement('textarea');
      ta.value = text;
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand('copy'); } catch (e) {}
      document.body.removeChild(ta);
    }

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
    const testimonyTypeLabel = (t) => ({
      '1': '🗣 自述',
      '2': '👂 见闻',
    })[String(t)] || `testimonyType=${t}`;
    const triggerTypeLabel = (t) => ({
      '0': '无条件',
      'None': '无条件',
      '1': '🕒 时间线',
      'Timeline': '🕒 时间线',
      '2': '🕸 关系网',
      'RelationNetwork': '🕸 关系网',
    })[String(t)] || `triggerType=${t}`;
    const formatTime = (s) => {
      const n = parseInt(s, 10);
      if (isNaN(n)) return s;
      const hr = Math.floor(n / 100);
      const min = n % 100;
      return `${String(hr).padStart(2, '0')}:${String(min).padStart(2, '0')}`;
    };
    const triggerParamDisplay = (ti) => {
      const tp = ti.triggerParam || '';
      if (!tp) return '';
      const t = String(ti.triggerType);
      const parts = tp.split(',').map(s => s.trim());
      const isNone = (t === '0' || t === 'None');
      const isTime = (t === '1' || t === 'Timeline');
      const isRel  = (t === '2' || t === 'RelationNetwork');
      if (isNone && parts.length >= 1) {
        return `来源: ${npcName(parts[0])}`;
      }
      if (isTime && parts.length >= 4) {
        const scene = sceneById(parts[1]);
        const sn = scene ? sceneName(scene) : `场景 #${parts[1]}`;
        return `${npcName(parts[0])} @ ${sn} ${formatTime(parts[2])}-${formatTime(parts[3])}`;
      }
      if (isRel) {
        return parts.map(p => npcName(p)).join(' × ');
      }
      return `参数: ${tp}`;
    };
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
    // 从起始 Talk ID 遍历对话链 → [{talk, branches}]
    const buildDialogueChain = (startId, maxLen = 60) => {
      const chain = [];
      const visited = new Set();
      let currentId = String(startId);
      while (currentId && !visited.has(currentId) && chain.length < maxLen) {
        visited.add(currentId);
        const talk = talkById(currentId);
        if (!talk) {
          chain.push({ talk: null, missingId: currentId });
          break;
        }
        const node = { talk, branches: null };
        const sc = String(talk.script || '');
        if ((sc === '1' || sc === 'branches') && Array.isArray(talk.Parameters)) {
          const brs = talk.Parameters.filter(p => p.ParameterStr && p.ParameterInt);
          if (brs.length > 0) {
            node.branches = brs.map(p => ({ text: p.ParameterStr, targetId: String(p.ParameterInt) }));
            chain.push(node);
            break;
          }
        }
        chain.push(node);
        if (!talk.next) break;
        const nextStr = String(talk.next);
        if (nextStr.includes('/')) {
          const params = talk.Parameters || [];
          const branchIds = nextStr.split('/');
          node.branches = branchIds.map((bid, i) => ({
            text: params[i]?.ParameterStr || `选项 ${i + 1}`,
            targetId: bid.trim(),
          }));
          break;
        }
        currentId = nextStr;
      }
      return chain;
    };

    // 说话人分类（决定颜色）
    const speakerKind = (npcIdVal) => {
      const sid = String(npcIdVal || '');
      if (sid === '101') return 'protagonist'; // Zack
      if (sid === '102') return 'partner';     // Emma
      const npc = npcById(sid);
      const role = npc ? String(npc.role) : '';
      if (role === '1') return 'victim';
      if (role === '2') return 'suspect';
      if (role === '3') return 'other';
      if (role === '4') return 'self';
      return 'unknown';
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
    const sceneTypeLabelFull = (s) => {
      // C# enum 目前只定义 dialogue=1，实测数据里还有 "3"。先做能命名的命名
      const t = String(sceneTypeRaw(s));
      const map = { '1': '对话场景 (dialogue)', '3': '未命名类型 3' };
      return map[t] || `类型 ${t}`;
    };
    const sceneCategoryIcon = {
      0: '📍', 1: '🎬', 2: '🔍', 3: '⚔️',
    };
    const sceneCategoryLabel = {
      0: '未分类', 1: '对话场景', 2: '探索场景', 3: '指证场景',
    };
    const sceneCategoryClass = {
      0: 'cat-none', 1: 'cat-dialogue', 2: 'cat-explore', 3: 'cat-expose',
    };
    const sceneCategory = (s) => s ? Number(s.sceneCategory || 0) : 0;
    const sceneIcon = (s) => sceneCategoryIcon[sceneCategory(s)] || '📍';
    const sceneNpcNames = (s) => {
      if (!s || !s.NPCInfos) return [];
      const names = [];
      for (const info of s.NPCInfos) {
        const n = npcName(npcId(info));
        if (n && !n.startsWith('(缺失')) names.push(n);
      }
      return names;
    };
    const npcId = (info) => {
      if (!info) return '';
      if (info.NPC && info.NPC.id) return String(info.NPC.id);
      return String(info.npcId || info.id || '');
    };
    // TestimonyItem id 编码：{NPC:3位}{loop:1位}{seq:3位}
    const testimonyItemNpcId = (id) => {
      const s = String(id || '');
      if (s.length !== 7) return null;
      return s.substring(0, 3);
    };
    const testimonyItemLoop = (id) => {
      const s = String(id || '');
      if (s.length !== 7) return null;
      return Number(s.substring(3, 4));
    };
    // 反查：TestimonyItem 属于哪条 Testimony
    const testimonyContaining = (tiId) => {
      const sid = String(tiId);
      for (const t of T.Testimony) {
        for (const ei of (t.evidenceItem || [])) {
          if (String(ei.id) === sid) return t;
        }
      }
      return null;
    };

    // firstEnterTalk 在 SceneConfig 里可能是字符串 ID，也可能是整个内联 Talk 对象
    const firstEnterTalkId = (s) => {
      if (!s) return null;
      const v = s.firstEnterTalk;
      if (!v) return null;
      if (typeof v === 'object') return String(v.id || '');
      return String(v);
    };

    // ─── chapter / loop helpers ───
    const chapterIdFor = (unit, loop) => `${unit}0${loop}`;  // 101, 102... 201, 202...
    const chapterByLoop = (unit, loop) => chapterById(chapterIdFor(unit, loop));
    const chapterTitle = (unit, loop) => {
      const c = chapterByLoop(unit, loop);
      if (!c) return '';
      return localText(c.chapterTitle);
    };
    // 场景属于某 Loop = openInLoops 含该 Loop
    const loopScenes = (unit, loop) => {
      return T.SceneConfig
        .filter(s => (s.openInLoops || []).map(Number).includes(Number(loop)))
        .slice()
        .sort((a, b) => String(a.sceneId).localeCompare(String(b.sceneId)));
    };
    // 仍属于该 Loop 但 openInLoops 没标的（sceneId 前缀匹配，疑似归属）
    const loopScenesUnmarked = (unit, loop) => {
      const prefix = `${unit}${loop}`;
      return T.SceneConfig
        .filter(s => String(s.sceneId).startsWith(prefix))
        .filter(s => !(s.openInLoops || []).map(Number).includes(Number(loop)))
        .slice()
        .sort((a, b) => String(a.sceneId).localeCompare(String(b.sceneId)));
    };
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
      const fetId = firstEnterTalkId(s);
      if (fetId && !talkById(fetId)) return { cls: 'err', icon: '🔴' };
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
      if (editMode.value && isDirty.value) {
        if (!confirm('当前有未保存改动，确定离开？')) return;
      }
      exitEdit();
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
    const selectAsset = (id) => pushSel({ type: 'artAsset', id });
    const selectAssetList = () => pushSel({ type: 'assetList', id: '_list' });
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
      exitEdit();
    }

    function toggleDraftLoop(l) {
      const arr = draft.openInLoops || (draft.openInLoops = []);
      const i = arr.indexOf(l);
      if (i >= 0) arr.splice(i, 1);
      else { arr.push(l); arr.sort((a, b) => a - b); }
    }

    // 当前选中实体
    function currentEntity() {
      if (!selected.value) return null;
      const cfg = EDITABLE_MAP[selected.value.type];
      if (!cfg) return null;
      const lookup = {
        scene: sceneById, npc: npcById, item: itemById,
        doubt: doubtById, testimonyItem: testimonyItemById,
        artAsset: assetById,
      };
      const fn = lookup[selected.value.type];
      return fn ? fn(selected.value.id) : null;
    }

    function enterEdit() {
      const e = currentEntity();
      if (!e) return;
      const cfg = EDITABLE_MAP[selected.value.type];
      for (const k of Object.keys(draft)) delete draft[k];
      for (const f of cfg.fields) {
        const v = e[f];
        if (BILINGUAL_FIELDS.has(f)) {
          const arr = Array.isArray(v) ? v : [];
          draft[f] = [arr[0] || '', arr[1] || ''];
        } else if (BOOL_FIELDS.has(f)) {
          draft[f] = (v === true || v === 'true' || v === 1 || v === '1');
        } else if (Array.isArray(v)) {
          draft[f] = [...v];
        } else if (v && typeof v === 'object') {
          draft[f] = JSON.parse(JSON.stringify(v));
        } else if (v !== undefined && v !== null) {
          draft[f] = v;
        } else if (f === 'openInLoops') {
          draft[f] = [];
        } else if (f === 'sceneCategory') {
          draft[f] = 0;
        } else {
          draft[f] = '';
        }
      }
      editMode.value = true;
      saveStatus.value = '';
    }

    function exitEdit() {
      editMode.value = false;
      for (const k of Object.keys(draft)) delete draft[k];
      saveStatus.value = '';
    }

    const isDirty = computed(() => {
      if (!editMode.value) return false;
      const e = currentEntity();
      if (!e) return false;
      const cfg = EDITABLE_MAP[selected.value.type];
      for (const f of cfg.fields) {
        const a = JSON.stringify(e[f] ?? null);
        const b = JSON.stringify(draft[f] ?? null);
        if (a !== b) return true;
      }
      return false;
    });

    async function saveEdit() {
      if (!isDirty.value) { exitEdit(); return; }
      const cfg = EDITABLE_MAP[selected.value.type];
      const e = currentEntity();
      if (!e) return;
      const changes = {};
      for (const f of cfg.fields) {
        const a = JSON.stringify(e[f] ?? null);
        const b = JSON.stringify(draft[f] ?? null);
        if (a !== b) changes[f] = draft[f];
      }
      saveStatus.value = 'saving';
      try {
        const r = await fetch('/api/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ table: cfg.table, id: selected.value.id, changes }),
        });
        const j = await r.json();
        if (!r.ok || j.error) throw new Error(j.error || 'save failed');
        // 写本地缓存
        for (const f of Object.keys(changes)) e[f] = changes[f];
        saveStatus.value = 'saved';
        setTimeout(() => { if (saveStatus.value === 'saved') exitEdit(); }, 800);
      } catch (err) {
        console.error(err);
        saveStatus.value = 'error';
        alert(`保存失败: ${err.message}`);
      }
    }

    // 切换选中条目时退出编辑模式
    function selectAndExit(fn) {
      return (...args) => { exitEdit(); fn(...args); };
    }

    // ─── ui toggles ───
    function toggleUnit(u) { unitOpen[u] = !unitOpen[u]; }
    function toggleLoop(u, l) {
      const k = `${u}-${l}`;
      loopOpen[k] = !loopOpen[k];
    }
    function toggleUnmarkedScenes(u, l) {
      const k = `${u}-${l}`;
      unmarkedScenesOpen[k] = !unmarkedScenesOpen[k];
    }

    return {
      T,
      loading, tablesLoadedCount, units, unitOpen, loopOpen, unmarkedScenesOpen, selected, canBack,
      toggleUnmarkedScenes, loopScenesUnmarked,
      // lookups
      itemById, npcById, talkById, testimonyItemById, doubtById, exposeById, chapterById, sceneById,
      // names
      itemName, npcName, talkPreview, talkSpeakerName, testimonyItemPreview, locationName,
      // helpers
      localText, sceneName, sceneTypeRaw, sceneTypeLabelFull, sceneIcon, sceneCategory, sceneCategoryIcon, sceneCategoryLabel, sceneCategoryClass, sceneNpcNames, npcId, firstEnterTalkId, itemTypeIcon, itemTypeLabel,
      conditionTypeLabel, conditionRefType, conditionRefLabel, talkScriptLabel, talkBranches,
      buildDialogueChain, speakerKind,
      testimonyTypeLabel, triggerTypeLabel, triggerParamDisplay,
      testimonyItemNpcId, testimonyItemLoop, testimonyContaining,
      chapterIdFor, chapterByLoop, chapterTitle, loopScenes, loopDoubts, loopExposes,
      npcLoopEntries, displayItemIds, itemDisplayFields, npcDisplayFields, itemUsedIn, itemOrTestimonyName,
      // badges
      sceneBadge, talkBadge, doubtBadge, exposeBadge,
      // nav
      isSelected, selectLoop, selectScene, selectItem, selectNpc, selectTalk,
      selectDoubt, selectExpose, selectTestimonyItem, selectAsset, selectAssetList, selectByRef, selectByCondition,
      // asset helpers
      assetById, sceneAssetId, scenesUsingAsset, assetFilename, copyText,
      artFilter, filteredAssets, assetStats, assetFilename, copyText,
      navBack, toggleUnit, toggleLoop,
      // 编辑
      editMode, draft, saveStatus, isDirty, isEditableType,
      enterEdit, exitEdit, saveEdit, toggleDraftLoop,
      ITEM_TYPE_OPTIONS, ROLE_OPTIONS, TESTIMONY_TYPE_OPTIONS, TRIGGER_TYPE_OPTIONS,
    };
  }
}).mount('#app');
