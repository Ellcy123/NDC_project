# NDC emergency-art source map

Use the user-named event requirement as the primary scope. Read only the relevant event section and linked dialogue context.

## Narrative requirements

- Authoritative Unit2 flashback/emergency-art requirement, directly organized from Feishu revision 454: `{PLANNING_ROOT}/剧情设计/Unit2/Unit2_飞书闪回需求完整整理.md`
- The authoritative document currently contains 16 events and 28 named image assets. Use its per-image facts, order, asset names, trigger semantics, and spoiler restrictions for a full Unit2 rebuild.
- Legacy compatibility redirects only; do not treat these as separate requirement sources: `{PLANNING_ROOT}/剧情设计/Unit2/Unit2_闪回需求与台本挂载点.md` and `{PLANNING_ROOT}/剧情设计/Unit2/美术需求/Unit2_AVG突发事件动态漫画.md`
- Gap/rebuild planning aid: `{PLANNING_ROOT}/剧情设计/Unit2/美术需求/Unit2_飞书突发事件缺口与Skill出图需求.md`
- Unit2 scene design notes: `{PLANNING_ROOT}/剧情设计/Unit2/场景/`
- Formal Talk source and side field: `{ENGINE_ROOT}/res/xls/Talk.xlsx` (`右侧显示` / runtime `Talk.isRight`)
- Talk side runtime implementation: `{ENGINE_ROOT}/Assets/_Project/Scripts/Talk/TalkPanel.cs` (`ApplySide`)
- Formal dialogue context is authoritative when requirement excerpts and current dialogue differ. Follow the Talk/Expose path named by the requirement.

## Visual identity and environment

- Approved character cards: `{PLANNING_ROOT}/美术资产交付/角色/角色索引.json`
- EPI02 scene backgrounds: `{ENGINE_ROOT}/Assets/Resources/Art/Scene/Backgrounds/EPI02/`
- EPI02 NPC scene art: `{ENGINE_ROOT}/Assets/Resources/Art/Scene/NPC/EPI02/`
- EPI02 evidence/prop art: `{ENGINE_ROOT}/Assets/Resources/Art/Scene/EVIDENCE/EPI02/`

Use English character names in prompts and handoff text: Rosa, Zack, Emma, Tommy, Morrison, Vivian, Jimmy, Anna, Webb, Mrs. Morrison, Whale, and the English names appearing in Unit2 requirements. A source filename may retain its existing spelling.

## U1 emergency references

Reference root: `{ENGINE_ROOT}/Assets/Resources/Art/Scene/Emergency/EPI01/`

U1 establishes that emergency assets are not a single fixed shape or size. Each folder represents one event and may contain one or several transparent images plus `XYposition.txt` placement data.

Useful structural examples:

| Need | U1 example | Size / ratio | What to study |
| --- | --- | --- | --- |
| Historical full-scene layout evidence | `BackAlley\l5_alley_headlights_01.png` | 2560×1600 / 1.60 | Placement/rhythm evidence only; do not copy its establishing composition into current emergency art |
| Ultra-wide impact/detail | `BackAlley\l5_alley_headlights_02.png` | 1220×336 / 3.63 | Narrow light/action strip |
| Portrait face pressure | `BackAlley\l5_alley_headlights_03.png` | 324×436 / 0.74 | Vertical reaction inset |
| Portrait hand/weapon | `BackAlley\l5_alley_headlights_04.png` | 368×720 / 0.51 | Tall object-action crop |
| Three-part evidence beat | `EmmaAtVIPRoom\l2_camera_drop_01..03.png` | 1.33–1.72 | Reaction → object → consequence |
| Eye strip then hand action | `L4MorrisonAgreement\l4_morrison_tear_agreement_01..02.png` | 2.98 and 2.08 | Different widths for different beats |
| Near-square evidence | `L6SafeBox\safebox.png`, `record.png` | 1.30 and 1.01 | Object-centred panels and non-polygon cutouts |
| Mixed horizontal/vertical sequence | `SHOW\c01..c05\` | 0.61–3.15 | Alternating portrait, square and strip panels |
| Compact irregular prop panel | `TommyOffice\l2_tommy_drawer_01.png` | 1.29 | Skewed near-square with accent edge |

Study U1 for panel rhythm, black-border weight, transparent corners, placement, and how a single event splits into several views. Do not copy its characters, exact polygon, color treatment, dimensions, full-body framing, or establishing views. Current emergency frames remain local or extreme-local close-ups even when a historical U1 reference is wider.

## Working and delivery roots

- Experiments: `<job>\payload\imagegen\<event-id>\<variant>\`
- Formal event art after explicit approval: `{ENGINE_ROOT}/Assets/Resources/Art/Scene/Emergency/EPI02/<event-folder>/`

Never overwrite U1 references. Do not stage experimental outputs into `Assets` merely because generation succeeded.
