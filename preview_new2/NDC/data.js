// NDC sample data — shape mirrors real production fields
// Exposed on window so Babel-compiled scripts can share.

const CHAPTERS = [
  { id: "EPI01", label: "EPI 01 · 码头迷雾" },
  { id: "EPI02", label: "EPI 02 · 剧院余烬" },
  { id: "EPI03", label: "EPI 03 · 金库之下" },
];

const LOOPS = [
  { id: "loop1", title: "Loop 1：初探旧码头", chapter: "EPI01", status: "in-progress" },
  { id: "loop2", title: "Loop 2：剧院幕后", chapter: "EPI01", status: "in-progress" },
  { id: "loop3", title: "Loop 3：血色协议", chapter: "EPI02", status: "draft" },
  { id: "loop4", title: "Loop 4：雨夜审讯", chapter: "EPI02", status: "draft" },
  { id: "loop5", title: "Loop 5：金库之下", chapter: "EPI03", status: "locked" },
  { id: "loop6", title: "Loop 6：黎明枪声", chapter: "EPI03", status: "locked" },
];

// Stages per loop: 开篇 / 调查场景 / 指证 / 突发 / 结尾
const STAGES = {
  loop1: [
    {
      key: "opening", label: "开篇", type: "intro",
      items: [
        { id: "s1_op", name: "Zack 的办公室", npcs: 1, evid: 2, status: "unlocked" },
      ],
    },
    {
      key: "investigate", label: "调查场景", type: "scene",
      items: [
        { id: "s1_palace", name: "Palace 剧院后台", npcs: 3, evid: 6, status: "unlocked" },
        { id: "s1_tommy", name: "Tommy 的住处", npcs: 2, evid: 4, status: "unlocked" },
        { id: "s1_dock", name: "旧码头仓库", npcs: 2, evid: 5, status: "unlocked" },
        { id: "s1_bar", name: "绿灯酒吧二楼", npcs: 4, evid: 3, status: "locked", unlockHint: "需先从 Rosa 处获得证词 1031002" },
        { id: "s1_lab", name: "法医停尸房", npcs: 1, evid: 2, status: "locked", unlockHint: "需提交证据 1104 给 Finch 警官" },
      ],
    },
    {
      key: "accuse", label: "指证", type: "accuse",
      items: [
        { id: "s1_ac", name: "指证环节 · 码头", npcs: 4, evid: 0, status: "not-open", unlockHint: "调查阶段完成 ≥ 80%" },
      ],
    },
    {
      key: "event", label: "突发事件", type: "event",
      items: [
        { id: "s1_ev", name: "码头枪声", npcs: 2, evid: 1, status: "unlocked" },
      ],
    },
    {
      key: "ending", label: "结尾", type: "ending",
      items: [
        { id: "s1_end", name: "雨中结案", npcs: 1, evid: 0, status: "not-open" },
      ],
    },
  ],
  loop2: [
    { key: "opening", label: "开篇", type: "intro",
      items: [{ id: "s2_op", name: "剧院前厅", npcs: 2, evid: 1, status: "unlocked" }] },
    { key: "investigate", label: "调查场景", type: "scene",
      items: [
        { id: "s2_stage", name: "主舞台后", npcs: 3, evid: 5, status: "unlocked" },
        { id: "s2_dress", name: "更衣室走廊", npcs: 2, evid: 4, status: "unlocked" },
      ] },
    { key: "accuse", label: "指证", type: "accuse",
      items: [{ id: "s2_ac", name: "指证环节 · 剧院", npcs: 3, evid: 0, status: "not-open" }] },
    { key: "event", label: "突发事件", type: "event",
      items: [{ id: "s2_ev", name: "幕布之下", npcs: 1, evid: 1, status: "unlocked" }] },
    { key: "ending", label: "结尾", type: "ending",
      items: [{ id: "s2_end", name: "黎明剧院", npcs: 2, evid: 0, status: "not-open" }] },
  ],
};

// Scenes with npc positions + evidence + background art status
const SCENES = {
  s1_palace: {
    id: "s1_palace",
    name: "Palace 剧院后台",
    loop: "loop1",
    bgStatus: "ok",
    bgPrompt: "1920年代歌舞剧院后台,化妆镜灯泡,红丝绒幕布一角,地面散落羽毛与香烟盒,暖黄钨丝灯",
    timeOfDay: "夜 · 雨",
    npcs: [
      { id: "npc_rosa",   name: "Rosa Vitale",   role: "歌女 / 线人",  x: 22, y: 58, artStatus: "ok",      testimonyIds: ["1031002", "1031004"] },
      { id: "npc_tommy",  name: "Tommy Delano",  role: "剧院经理",     x: 52, y: 62, artStatus: "missing", testimonyIds: ["1021001"] },
      { id: "npc_zack",   name: "Zack Brennan",  role: "侦探主角",     x: 76, y: 66, artStatus: "ok",      testimonyIds: [] },
    ],
    evidence: [
      { id: "1101", title: "带血的手帕",         type: "原始",  artStatus: "ok",      npc: "Rosa Vitale" },
      { id: "1102", title: "镀金烟盒",           type: "原始",  artStatus: "ok",      npc: "Tommy Delano" },
      { id: "1103", title: "撕碎的演出单",       type: "原始",  artStatus: "missing", npc: "—" },
      { id: "1703", title: "手帕上的血型报告",   type: "分析后", artStatus: "ok",     npc: "—", derivedFrom: "1101" },
      { id: "1704", title: "烟盒内侧刻字",       type: "分析后", artStatus: "wip",    npc: "—", derivedFrom: "1102" },
      { id: "1901", title: "演出单残片 + 烟盒",  type: "合成物", artStatus: "missing", npc: "—", derivedFrom: ["1103", "1102"] },
    ],
  },
  s1_tommy: {
    id: "s1_tommy", name: "Tommy 的住处", loop: "loop1", bgStatus: "wip",
    bgPrompt: "狭窄单间公寓,铁架床,桌上半瓶威士忌,墙上赛马海报,月光从百叶窗漏入",
    timeOfDay: "晨 · 阴",
    npcs: [
      { id: "npc_tommy", name: "Tommy Delano", role: "剧院经理", x: 48, y: 60, artStatus: "missing", testimonyIds: ["1021003"] },
      { id: "npc_landlady", name: "Mrs. Hale", role: "房东太太", x: 18, y: 55, artStatus: "missing", testimonyIds: ["1041001"] },
    ],
    evidence: [
      { id: "1201", title: "抽屉里的欠条", type: "原始", artStatus: "ok", npc: "—" },
      { id: "1202", title: "口红印信封",   type: "原始", artStatus: "ok", npc: "—" },
      { id: "1203", title: "藏在床底的枪", type: "原始", artStatus: "wip", npc: "—" },
      { id: "1705", title: "欠条上的指纹", type: "分析后", artStatus: "missing", npc: "—", derivedFrom: "1201" },
    ],
  },
  s1_dock: {
    id: "s1_dock", name: "旧码头仓库", loop: "loop1", bgStatus: "missing",
    bgPrompt: "密歇根湖畔废弃仓库,木箱堆叠,生锈铁钩,晨雾,远处汽笛",
    timeOfDay: "晨 · 雾",
    npcs: [
      { id: "npc_james", name: "James Webb",  role: "码头工头", x: 30, y: 62, artStatus: "ok",      testimonyIds: ["1051002"] },
      { id: "npc_thug",  name: "无名打手",    role: "背景NPC",   x: 70, y: 68, artStatus: "missing", testimonyIds: [] },
    ],
    evidence: [
      { id: "1301", title: "破损的货运单",   type: "原始",   artStatus: "ok",      npc: "—" },
      { id: "1302", title: "子弹壳 · .38",   type: "原始",   artStatus: "ok",      npc: "—" },
      { id: "1303", title: "沾泥的女士手套", type: "原始",   artStatus: "missing", npc: "—" },
      { id: "1706", title: "货运单拓印",     type: "分析后", artStatus: "wip",     npc: "—", derivedFrom: "1301" },
      { id: "1902", title: "手套 + 手帕比对", type: "合成物", artStatus: "missing", npc: "—", derivedFrom: ["1303", "1101"] },
    ],
  },
};

// Full dialogue scripts — 9-digit ID形如 105001005 (episode·loop·scene·line)
const DIALOGUES = {
  "105001005": {
    id: "105001005", scene: "Palace 剧院后台", loop: "Loop 1", ctx: "Zack 抵达后台,首次见到 Rosa",
    lines: [
      { who: "Zack Brennan", text: "这种时候还亮着灯,Palace 倒是舍得电费。", mood: "讥诮" },
      { who: "Rosa Vitale",  text: "电费是剧院出的,失眠是我自己的。", mood: "冷淡" },
      { who: "Zack Brennan", text: "我在找一个人。", mood: "平静" },
      { who: "Rosa Vitale",  text: "这座城里谁不在找人呢,侦探。", mood: "反问" },
    ],
  },
  "105001012": {
    id: "105001012", scene: "Palace 剧院后台", loop: "Loop 1", ctx: "Zack 展示手帕后",
    lines: [
      { who: "Zack Brennan", text: "这是你的吗?", mood: "逼问" },
      { who: "Rosa Vitale",  text: "…是。但那血不是我的。", mood: "低声" },
      { who: "Zack Brennan", text: "那是谁的?", mood: "冷" },
      { who: "Rosa Vitale",  text: "你知道的。你早就知道。", mood: "转身离开" },
    ],
  },
  "105001008": {
    id: "105001008", scene: "Palace 剧院后台", loop: "Loop 1", ctx: "Tommy 否认当晚离开",
    lines: [
      { who: "Tommy Delano", text: "我一整晚都在办公室,账本没合完。", mood: "躲闪" },
      { who: "Zack Brennan", text: "那你怎么解释后门的脚印?", mood: "压迫" },
      { who: "Tommy Delano", text: "那是…那是 Rosa 的。她出去透气。", mood: "慌乱" },
    ],
  },
  "105001020": {
    id: "105001020", scene: "Palace 剧院后台", loop: "Loop 1", ctx: "Rosa 单独与 Zack 的告解",
    lines: [
      { who: "Rosa Vitale",  text: "Tommy 不是坏人,他只是被逼急了。", mood: "辩护" },
      { who: "Zack Brennan", text: "被逼急的人也会扣扳机。", mood: "陈述" },
      { who: "Rosa Vitale",  text: "侦探,你见过清醒的扳机手吗?", mood: "苦笑" },
    ],
  },
  "105001021": {
    id: "105001021", scene: "Palace 剧院后台", loop: "Loop 1", ctx: "追问 1031004 关于欠款",
    lines: [
      { who: "Zack Brennan", text: "他欠了多少?", mood: "追问" },
      { who: "Rosa Vitale",  text: "七百二十美元。不多不少。", mood: "平静" },
      { who: "Zack Brennan", text: "这个数字,你记得真清楚。", mood: "暗讽" },
      { who: "Rosa Vitale",  text: "……", mood: "沉默" },
    ],
  },
  "105001030": {
    id: "105001030", scene: "旧码头仓库", loop: "Loop 1", ctx: "James 交出货运单",
    lines: [
      { who: "James Webb",   text: "日期被人划过。我盯着货单这么多年,头一回见到有人敢改数字。", mood: "谨慎" },
      { who: "Zack Brennan", text: "谁改的?", mood: "直接" },
      { who: "James Webb",   text: "我不知道,但不是我。你清楚规矩。", mood: "回避" },
    ],
  },
  "105001040": {
    id: "105001040", scene: "Tommy 的住处", loop: "Loop 1", ctx: "Mrs. Hale 门外低语",
    lines: [
      { who: "Mrs. Hale",    text: "他半夜才回来,靴子全是码头的泥。", mood: "压低嗓音" },
      { who: "Zack Brennan", text: "几点?", mood: "确认" },
      { who: "Mrs. Hale",    text: "两点二十,我那口钟不走慢。", mood: "笃定" },
    ],
  },
};

// Full NPC registry
const NPCS = {
  npc_zack:    { id: "npc_zack",    name: "Zack Brennan",  role: "侦探主角",    artStatus: "ok",
                 prompt: "中年男性,1920s 精致三件套西装,疲惫但警觉的神态,左眉有疤",
                 dialogueIds: ["105001005", "105001012"] },
  npc_tommy:   { id: "npc_tommy",   name: "Tommy Delano",  role: "剧院经理",    artStatus: "missing",
                 prompt: "40岁男性,发福,油头梳得一丝不苟,袖扣失色,眼神闪躲",
                 dialogueIds: ["105001008"] },
  npc_rosa:    { id: "npc_rosa",    name: "Rosa Vitale",   role: "歌女 / 线人", artStatus: "ok",
                 prompt: "28岁女性,深红丝绒晚礼服,长手套,烟嘴,讽刺的微笑",
                 dialogueIds: ["105001020", "105001021"] },
  npc_james:   { id: "npc_james",   name: "James Webb",    role: "码头工头",    artStatus: "ok",
                 prompt: "50岁男性,工装背带裤,络腮胡,左手缺一指",
                 dialogueIds: ["105001030"] },
  npc_landlady:{ id: "npc_landlady",name: "Mrs. Hale",     role: "房东太太",    artStatus: "missing",
                 prompt: "60岁女性,碎花围裙,夹鼻眼镜,手里永远攥着一串钥匙",
                 dialogueIds: ["105001040"] },
  npc_thug:    { id: "npc_thug",    name: "无名打手",      role: "背景NPC",     artStatus: "missing",
                 prompt: "壮汉,皮夹克,软呢帽压低,脸部不必精细",
                 dialogueIds: [] },
};

// Evidence detail w/ derivation graph
const EVIDENCE = {
  "1101": { id: "1101", title: "带血的手帕", type: "原始",   artStatus: "ok",
            desc: "白色亚麻手帕,一角绣 R.V.,上有干涸血迹。Rosa 案发当晚持有。",
            scene: "s1_palace", derivedTo: ["1703", "1902"] },
  "1102": { id: "1102", title: "镀金烟盒",   type: "原始",   artStatus: "ok",
            desc: "内侧刻字 '致 T.D. — 1924'。Tommy 称系家传。",
            scene: "s1_palace", derivedTo: ["1704", "1901"] },
  "1103": { id: "1103", title: "撕碎的演出单", type: "原始", artStatus: "missing",
            desc: "被撕成三片,拼合后缺一角,写有某包厢号。",
            scene: "s1_palace", derivedTo: ["1901"] },
  "1703": { id: "1703", title: "手帕上的血型报告", type: "分析后", artStatus: "ok",
            desc: "Finch 警官送检,AB 型 — 与剧院后门发现的血迹匹配。",
            scene: "s1_palace", derivedFrom: ["1101"] },
  "1704": { id: "1704", title: "烟盒内侧刻字", type: "分析后", artStatus: "wip",
            desc: "显微拓印,字迹实为后加工,原字被磨平。",
            scene: "s1_palace", derivedFrom: ["1102"] },
  "1901": { id: "1901", title: "演出单残片 + 烟盒", type: "合成物", artStatus: "missing",
            desc: "拼合后指向 Palace 14 号包厢 — Tommy 常用。",
            scene: "s1_palace", derivedFrom: ["1103", "1102"] },
};

// Testimony lookup
const TESTIMONIES = {
  "1031002": { id: "1031002", npc: "Rosa Vitale",  text: "凌晨两点,我听见后门有争执声 — 是 Tommy 的声音。" },
  "1031004": { id: "1031004", npc: "Rosa Vitale",  text: "他欠了道上的钱,不是第一次了。" },
  "1021001": { id: "1021001", npc: "Tommy Delano", text: "我当晚在 Palace,没离开过。Rosa 可以作证。" },
  "1021003": { id: "1021003", npc: "Tommy Delano", text: "那把枪不是我的。我从不碰枪。" },
  "1041001": { id: "1041001", npc: "Mrs. Hale",    text: "他半夜回来的,靴子全是码头的泥。" },
  "1051002": { id: "1051002", npc: "James Webb",   text: "那晚码头没船靠岸,工人全放假了。" },
};

// Art-needs aggregate (derived but pre-built for demo)
const ART_NEEDS = {
  scenes: [
    { id: "s1_palace", name: "Palace 剧院后台", chapter: "EPI01", loop: "Loop 1", status: "ok"      },
    { id: "s1_tommy",  name: "Tommy 的住处",    chapter: "EPI01", loop: "Loop 1", status: "wip"     },
    { id: "s1_dock",   name: "旧码头仓库",       chapter: "EPI01", loop: "Loop 1", status: "missing" },
    { id: "s2_stage",  name: "主舞台后",         chapter: "EPI01", loop: "Loop 2", status: "ok"      },
    { id: "s2_dress",  name: "更衣室走廊",       chapter: "EPI01", loop: "Loop 2", status: "wip"     },
  ],
  npcs: [
    { id: "npc_zack",    name: "Zack Brennan",  chapter: "EPI01", status: "ok"      },
    { id: "npc_rosa",    name: "Rosa Vitale",   chapter: "EPI01", status: "ok"      },
    { id: "npc_tommy",   name: "Tommy Delano",  chapter: "EPI01", status: "missing" },
    { id: "npc_james",   name: "James Webb",    chapter: "EPI01", status: "ok"      },
    { id: "npc_landlady",name: "Mrs. Hale",     chapter: "EPI01", status: "missing" },
    { id: "npc_thug",    name: "无名打手",       chapter: "EPI01", status: "missing" },
  ],
  evidence: [
    { id: "1101", title: "带血的手帕",   chapter: "EPI01", loop: "Loop 1", scene: "Palace 剧院后台", status: "ok"      },
    { id: "1102", title: "镀金烟盒",     chapter: "EPI01", loop: "Loop 1", scene: "Palace 剧院后台", status: "ok"      },
    { id: "1103", title: "撕碎的演出单", chapter: "EPI01", loop: "Loop 1", scene: "Palace 剧院后台", status: "missing" },
    { id: "1201", title: "抽屉里的欠条", chapter: "EPI01", loop: "Loop 1", scene: "Tommy 的住处",    status: "ok"      },
    { id: "1203", title: "藏在床底的枪", chapter: "EPI01", loop: "Loop 1", scene: "Tommy 的住处",    status: "wip"     },
    { id: "1302", title: "子弹壳 · .38", chapter: "EPI01", loop: "Loop 1", scene: "旧码头仓库",      status: "ok"      },
    { id: "1303", title: "沾泥的女士手套",chapter: "EPI01", loop: "Loop 1", scene: "旧码头仓库",      status: "missing" },
    { id: "1705", title: "欠条上的指纹", chapter: "EPI01", loop: "Loop 1", scene: "Tommy 的住处",    status: "missing" },
    { id: "1706", title: "货运单拓印",   chapter: "EPI01", loop: "Loop 1", scene: "旧码头仓库",      status: "wip"     },
    { id: "1901", title: "演出单+烟盒",  chapter: "EPI01", loop: "Loop 1", scene: "Palace 剧院后台", status: "missing" },
    { id: "1902", title: "手套+手帕比对",chapter: "EPI01", loop: "Loop 1", scene: "旧码头仓库",      status: "missing" },
  ],
};

// Story narrative — novel-style prose per loop.
// `body` is an array of paragraphs. Use {{#1101}} / {{@Rosa Vitale}} / {{"1031002}} inline
// to mark clickable evidence ids / npcs / testimony ids. {{^scene}} marks a scene break.
const NARRATIVE = [
  { loop: "loop1", no: "第一章", chapter: "EPI 01 · 码头迷雾", title: "初探旧码头",
    epigraph: "城市在凌晨两点睡着,只有雨不睡。——Z.B.",
    body: [
      "那晚,Palace 剧院后台的灯还亮着。{{@Rosa Vitale}} 在镜前卸妆,指尖夹着一支熄了火的烟。她说她听见了争执声,是 {{@Tommy Delano}} 的嗓音——沙哑、紧绷、像一根快断的弦。",
      "我走到更衣室门口,在地毯的褶皱里捡起一块 {{#1101}}。白亚麻,一角绣着 R.V.,血已经干了,颜色却还新。",
      "{{^scene}}",
      "{{@Tommy Delano}} 的住处在西十二街的三楼,楼梯吱呀作响像是替人数数。抽屉里藏着一张 {{#1201}},数字七百二十美元,还有一个不属于 Tommy 的名字。床底的铁盒里是一把 {{#1203}},枪管还带着机油味——这把枪最近被人擦过。",
      "Mrs. Hale 在门外压着嗓子说:“他半夜才回来,靴子全是码头的泥。”{{\"1041001}}",
      "{{^scene}}",
      "旧码头的雾像一块没洗干净的床单。{{@James Webb}} 递给我一张 {{#1301}},上面的日期被人划去重写。“那晚没船靠岸。”他说。{{\"1051002}} 但地上有一枚 {{#1302}},.38 口径——Tommy 从不碰枪的那种。",
      "在一堆麻绳和铁钩之间,我还看见一只 {{#1303}}。尺码不大,指尖沾着后台地毯的绒。",
    ],
    pins: [
      { label: "关键证据", items: ["1101", "1103", "1201", "1303"] },
      { label: "关键证词", items: ["1031002", "1041001", "1051002"] },
    ],
  },
  { loop: "loop2", no: "第二章", chapter: "EPI 01 · 码头迷雾", title: "剧院幕后",
    epigraph: "聚光灯熄灭以后,舞台上还留着一只鞋。",
    body: [
      "第二次回到 Palace,前厅的海报已经换过了。歌女换了新人,票务说 Rosa 请了病假——可我知道,她不是会请病假的那种人。",
      "主舞台后面,一段 {{#1103}} 拼不全。缺一角,刚好是包厢号的位置。{{@Tommy Delano}} 的办公室空着,抽屉里却压着另一支烟——和 {{#1102}} 是同一批货。",
      "{{^scene}}",
      "更衣室走廊的尽头有一扇门,锁是新的。Rosa 的证词 {{\"1031004}} 说:“他欠了道上的钱,不是第一次了。”这句话我反复听了三遍,每遍都像在听不同的人说。",
    ],
    pins: [
      { label: "关键证据", items: ["1103", "1102"] },
      { label: "关键证词", items: ["1031004"] },
    ],
  },
  { loop: "loop3", no: "第三章", chapter: "EPI 02 · 剧院余烬", title: "血色协议",
    epigraph: "草稿 · 待补。",
    body: [
      "[草稿] Rosa 的立场在本章反转。主线引入“协议书”道具,与 Loop1 的 {{#1703}} 形成回环。",
      "[草稿] 指证环节的分歧点在此触发,根据玩家是否已获取 {{#1901}} 有两条不同的对话走向。",
    ],
    pins: [
      { label: "待定证据", items: ["1703", "1901"] },
    ],
  },
  { loop: "loop4", no: "第四章", chapter: "EPI 02 · 剧院余烬", title: "雨夜审讯",
    epigraph: "草稿 · 待补。",
    body: [
      "[草稿] 审讯室场景,{{@Tommy Delano}} 的证词 {{\"1021003}} 与物证 {{#1203}} 出现矛盾。",
      "[草稿] 玩家需通过多轮盘问迫使 Tommy 改口,否则进入“假证词”分支。",
    ],
    pins: [
      { label: "待定证据", items: ["1203"] },
      { label: "待定证词", items: ["1021003"] },
    ],
  },
  { loop: "loop5", no: "第五章", chapter: "EPI 03 · 金库之下", title: "金库之下", epigraph: "—", body: ["[尚未撰写]"], pins: [] },
  { loop: "loop6", no: "第六章", chapter: "EPI 03 · 金库之下", title: "黎明枪声", epigraph: "—", body: ["[尚未撰写]"], pins: [] },
];

// Story timeline — key beats per loop (kept for reference / future use)
const TIMELINE = [
  { loop: "Loop 1", beats: [
    { t: "00:00", label: "尸体被发现",      kind: "event" },
    { t: "00:12", label: "Zack 抵达码头",    kind: "scene" },
    { t: "00:24", label: "首次遇见 Rosa",    kind: "npc" },
    { t: "00:38", label: "获得证据 1101",    kind: "evid" },
    { t: "00:55", label: "突发：码头枪声",   kind: "event" },
    { t: "01:10", label: "指证 · 码头",      kind: "accuse" },
  ]},
  { loop: "Loop 2", beats: [
    { t: "00:00", label: "剧院开演",         kind: "event" },
    { t: "00:15", label: "Tommy 失踪报警",   kind: "npc" },
    { t: "00:32", label: "证据 1103 出现",   kind: "evid" },
    { t: "00:48", label: "幕布之下",         kind: "event" },
    { t: "01:05", label: "黎明剧院",         kind: "scene" },
  ]},
  { loop: "Loop 3", beats: [
    { t: "00:00", label: "血色协议开场",     kind: "event" },
    { t: "00:20", label: "Rosa 的背叛",      kind: "npc" },
    { t: "00:45", label: "指证分歧点",       kind: "accuse" },
  ]},
  { loop: "Loop 4", beats: [
    { t: "00:00", label: "雨夜审讯",         kind: "event" },
    { t: "00:30", label: "假证词 1021003",    kind: "evid" },
  ]},
  { loop: "Loop 5", beats: [{ t: "—", label: "草稿中", kind: "event" }] },
  { loop: "Loop 6", beats: [{ t: "—", label: "草稿中", kind: "event" }] },
];

// Flowchart — nodes + edges (dialogue/accuse triggers)
const FLOW = {
  nodes: [
    { id: "n1", label: "开场对话\n105001005",    x: 60,  y: 80,  kind: "dialogue" },
    { id: "n2", label: "选择：盘问 / 旁观",     x: 260, y: 80,  kind: "branch"   },
    { id: "n3", label: "Rosa 证词\n1031002",     x: 460, y: 30,  kind: "testimony"},
    { id: "n4", label: "Tommy 证词\n1021001",    x: 460, y: 140, kind: "testimony"},
    { id: "n5", label: "解锁场景\nTommy 的住处",  x: 700, y: 80,  kind: "unlock"   },
    { id: "n6", label: "证据汇总检查",            x: 940, y: 80,  kind: "check"    },
    { id: "n7", label: "指证 · 码头",             x: 1160,y: 80,  kind: "accuse"   },
  ],
  edges: [
    { from: "n1", to: "n2" },
    { from: "n2", to: "n3", label: "盘问" },
    { from: "n2", to: "n4", label: "旁观" },
    { from: "n3", to: "n5" },
    { from: "n4", to: "n5" },
    { from: "n5", to: "n6" },
    { from: "n6", to: "n7", label: "证据 ≥ 4" },
  ],
};

Object.assign(window, {
  CHAPTERS, LOOPS, STAGES, SCENES, NPCS, EVIDENCE, TESTIMONIES,
  ART_NEEDS, TIMELINE, NARRATIVE, FLOW, DIALOGUES,
});
