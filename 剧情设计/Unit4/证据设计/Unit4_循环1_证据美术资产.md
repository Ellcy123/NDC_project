# Unit4 循环1 - 证据美术资产清单

> 叙事主题：Harrison 的死亡疑云  
> 正式证据总数：12 条（含 1 条分析结果）  
> ID 范围：4111-4121、4701  
> 数据源：`剧情设计/Unit4/state/loop1_state.yaml`、`avg_editor_v2/data/table/ItemStaticData.json`、`剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`  
> 全局规范与跨循环复用要求：见 [Unit4 证据美术资产总览](./Unit4_证据美术资产_总览.md)

---

## 证据总表

| ID | 中文名 | 类型/地点 | 小玩法关系 |
|---|---|---|---|
| 4111 | Harrison公开日程与夜间出入对照 | Clue；法院档案室核对台。 | 输出 |
| 4112 | 1919-A 入账存根 | Item；Harrison 外间办公室普通费用抽屉。 | 跨玩法输入 |
| 4113 | 未完成的辞职信草稿 | Item；Harrison 外间办公室打字机废纸篮。 | 无 |
| 4114 | 圣心医院资助档案卷宗 | Item；法院档案室，由档案管理员交付。 | 无 |
| 4115 | Harrison 两个月调阅索引 | Item；法院档案室调阅台账。 | 输入 + 后续分析输入 |
| 4701 | 调阅索引中的本人赔偿裁定 | 分析结果；由 4115 在法院档案室整理得到。 | 输出 |
| 4116 | Mary / Helen 案改判往来信 | Item；法院档案室 Harrison 调阅文件。 | 无 |
| 4117 | Harrison 留下的编号纸条 | Item；Harrison 未完成的自首证物箱。 | 跨 Loop 调档输入 |
| 4118 | 医院冷藏库留样试剂 | Item；Harrison 未完成的自首证物箱。 | 分析输入 |
| 4119 | Harrison 亲笔资金流向图 | Item；Harrison 未完成的自首证物箱。 | 无 |
| 4120 | 南区综合商业开发计划摘要 | Item；Harrison 未完成的自首证物箱。 | 无 |
| 4121 | 1912 事故家庭索引 | Item；附在 4120 末页。 | 无 |

---

## 证据详细卡片

### 4111 - Harrison公开日程与夜间出入对照

- 类型/地点：Clue；法院档案室核对台。
- `Name`：`Harrison公开日程与夜间出入对照` / `Harrison Public Schedule and After-Hours Access Cross-Check`
- `Describe`：  
  `公开日程没有安排这些夜间工作。将闭馆后访问记录与调阅流水逐项核对后，可以确认 Harrison 在统计范围内共有十七次闭馆后调阅；人工抽查的三次分别落在 Mary / Helen 改判案、Frank Kowalski 贷款案和圣心医院儿童死亡赔偿案。原始记录没有说明这些旧裁定由谁签署。`  
  `Harrison's public schedule lists no such night work. Cross-checking the after-hours access log against the file ledger confirms seventeen after-hours reviews in the recorded period. The three manually verified entries concern the Mary/Helen appeal, Frank Kowalski's loan case, and the Sacred Heart child-death compensation cases. The source records do not identify who signed the old rulings.`
- `ShortDescribe`：  
  `十七次闭馆后调阅集中在医院、贷款和旧赔偿案，公开日程没有对应安排。`  
  `Seventeen after-hours file reviews focus on hospital, loan, and old compensation cases, with no matching public schedule.`
- 小玩法关系：`输出`。L1「Harrison 夜间调阅检索」以 4115 正式证据和 4122、4123 两张玩法附属页面为输入；玩家完成三轮时间窗匹配后生成 4111。4115 保留，4122、4123 不进入背包或正式 Item 表。

重点（信息表达必不可少）：

1. 详情图是三栏纸面核对结果：`PUBLIC SCHEDULE`、`AFTER-HOURS ACCESS LOG`、`FILE REVIEW LEDGER`。
2. 三条人工核对线必须分别落到 Mary / Helen、Frank Kowalski、Sacred Heart Children 三类卷宗；最终汇总数字 `17 AFTER-HOURS REVIEWS` 清晰可读。
3. 不出现“由 Harrison 签署”或“自查”字样，避免提前泄露 4701。
4. 4122、4123、4115 的纸张版式必须与玩法界面使用同一套资源。

美术参考（不影响推理）：

- 1920 年代法院档案核对台，奶白表格纸、打字机栏头、铅笔圈选和细线连接。
- 三份纸张可用黄铜夹和页签固定；完成态以克制的连续盖章和最终统计框收束。

---

### 4112 - 1919-A 入账存根

- 类型/地点：Item；Harrison 外间办公室普通费用抽屉。
- `Name`：`1919-A入账存根` / `1919-A Deposit Receipt`
- `Describe`：  
  `一张长期夹在普通收入凭据中的入账存根。付款方只写作“1919-A”，备注栏连续引用圣心医院赔偿案号，款项进入 Harrison 的私人账户。纸张保存多年，没有被刻意销毁的痕迹。`  
  `A deposit receipt kept for years among ordinary income records. The payer is listed only as “1919-A”; the memo field cites Sacred Heart compensation case numbers, and the money was credited to Harrison's personal account. The receipt shows no sign of an attempt to destroy it.`
- `ShortDescribe`：  
  `付款方记作“1919-A”，款项进入 Harrison 私人账户。`  
  `A deposit from “1919-A” was credited to Harrison's personal account.`
- 小玩法关系：`跨玩法输入`。L5 身份锁链 4501 的输入之一，与 4416、4513、4514 共同生成 4705；不参与 L1 指证。

重点（信息表达必不可少）：

1. `PAYOR: 1919-A`、Harrison 私人账户栏和 Sacred Heart 赔偿案号备注必须同时可读。
2. 不出现 Donnelly & Associates、Mickey、Whale 或账户实际控制人。
3. 与 4514 使用同一套 `1919-A` 账户编号排版和银行表格体系，方便 L5 视觉对照。

美术参考（不影响推理）：

- 1919 年银行入账凭据，小尺寸米黄纸，蓝黑油墨，左侧有归档孔和多次折叠痕。
- 混在普通费用凭据中的状态：边缘磨损、角落有旧夹痕，但关键信息仍清楚。

---

### 4113 - 未完成的辞职信草稿

- 类型/地点：Item；Harrison 外间办公室打字机废纸篮。
- `Name`：`未完成的辞职信草稿` / `Unfinished Resignation Draft`
- `Describe`：  
  `一份日期为 11 月 27 日、尚未签署和递交的辞职信草稿。正文开始清点 Harrison 参与过的裁定与收款，并写道：“我们不能一面要求他人承认罪行，一面继续否认自己的部分。”末段停在准备公开相关材料的表述上。`  
  `An unsigned, unsubmitted resignation draft dated November 27. Harrison begins listing rulings and payments in which he took part and writes, “We cannot demand that others confess while continuing to deny our own part.” The final paragraph breaks off as he states his intention to make the relevant records public.`
- `ShortDescribe`：  
  `11月27日的未签辞职稿开始清点 Harrison 自己的责任，并准备公开材料。`  
  `The unsigned November 27 draft begins accounting for Harrison's own responsibility and plans to disclose records.`
- 小玩法关系：`无`。与 4116 共同用于 Watts Expose R3。

重点（信息表达必不可少）：

1. 日期 `November 27, 1928` 可读；签名栏明确为空。
2. 两句核心英文必须可读：`We cannot demand that others confess while continuing to deny our own part.`、`I intend to make these records public...`。
3. 末段在句中停下，保留未完成打字和纸张从打字机上匆忙抽出的状态。
4. 不写成完整英雄遗书，不出现凶手或命令源。

美术参考（不影响推理）：

- Underwood 打字机字体，字距略不均；纸角有揉皱后重新展平的折痕。
- 废纸篮背景只露一角，正文保持可读。

---

### 4114 - 圣心医院资助档案卷宗

- 类型/地点：Item；法院档案室，由档案管理员交付。
- `Name`：`圣心医院资助档案卷宗` / `Sacred Heart Hospital Funding File`
- `Describe`：  
  `圣心医院慈善项目的资助档案。资助机构排名中 Miller 位列第一，医院项目对接负责人为 Whitfield；封套右上角盖有 Miller 事故基金印章。卷宗只能证明资助与对接关系，不能证明具体药剂批次由谁批准。`  
  `A funding file for Sacred Heart Hospital's charity program. Miller ranks first among the sponsoring institutions, Whitfield is listed as the hospital liaison, and the folder bears the Miller Accident Fund seal. The file establishes funding and liaison roles, not who approved a particular drug batch.`
- `ShortDescribe`：  
  `Miller 是圣心医院首位资助方，Whitfield 是项目对接负责人。`  
  `Miller is Sacred Heart's leading sponsor, with Whitfield listed as program liaison.`
- 小玩法关系：`无`。只提供 L2 调查方向，不参与 L1 R2。

重点（信息表达必不可少）：

1. 抬头 `SACRED HEART HOSPITAL — CHARITY PROGRAM FUNDING` 可读。
2. 排名第一行显示 `MILLER ACCIDENT FUND`；联络栏显示 `PROGRAM LIAISON: WHITFIELD`。
3. 右上 Miller 印章与 4216、4516 的 Miller 体系标识一致。
4. 不出现第十九页、问题批次或上层批准者。

美术参考（不影响推理）：

- 深灰蓝法院档案封套，内页为打字机清单；Miller 印章采用压印加深蓝油墨。
- 文件保存良好、带法院编号页签，区别于私人草稿。

---

### 4115 - Harrison 两个月调阅索引

- 类型/地点：Item；法院档案室调阅台账。
- `Name`：`Harrison两个月调阅索引` / `Harrison Two-Month File Review Index`
- `Describe`：  
  `法院档案室两个月的完整调阅流水，保留档号、调出与归还时间及手续栏。Harrison 的调阅集中在圣心医院儿童死亡、南区地产和旧赔偿案件；原表只记录程序事实，没有解释旧裁定由谁签署。`  
  `The archive's complete two-month file-review ledger, preserving case numbers, checkout and return times, and procedural entries. Harrison's reviews cluster around Sacred Heart child deaths, South Side property cases, and old compensation claims. The source ledger records procedure only and does not identify who signed the rulings.`
- `ShortDescribe`：  
  `两个月调阅流水集中在医院、南区地产和旧赔偿档案。`  
  `The two-month ledger clusters around hospital, South Side property, and old compensation files.`
- 小玩法关系：`输入 + 后续分析输入`。作为 L1 夜间调阅检索输入之一，与 4122、4123 生成 4111；玩法后原物保留。之后单独整理案号与旧案目录，生成 4701。

重点（信息表达必不可少）：

1. 长表必须包含 `CASE NO.`、`CHECKED OUT`、`RETURNED`、`CLERK` 等程序栏。
2. 医院、地产、赔偿三类档号通过页签或案名缩写可辨，但签署人栏不存在或未展开。
3. 与 4111 小玩法中的第三栏完全复用同一页面资源。
4. 不能在原图上圈出 Harrison 本人签署的裁定；该信息只出现在 4701。

美术参考（不影响推理）：

- 大开本法院流水簿，灰白纸、淡蓝格线、黑色打字和多名书记员的蓝黑签字。
- 页面信息密集但三类档号可通过小页签定位。

---

### 4701 - 调阅索引中的本人赔偿裁定

- 类型/地点：分析结果；由 4115 在法院档案室整理得到。
- `Name`：`调阅索引中的本人赔偿裁定` / `Harrison-Signed Rulings in the Review Index`
- `Describe`：  
  `将调阅索引中的旧案号与法院裁定目录对照后，发现 Harrison 反复调阅的赔偿旧案中包含多份由他本人签署的裁定。这个结果只证明他把自己的旧裁定纳入调查，不能证明他已经完成自首。`  
  `Comparing the old case numbers in the review index with the court's ruling directory shows that several compensation cases repeatedly reviewed by Harrison were rulings he had signed himself. This establishes that he included his own decisions in the review, not that he completed a confession.`
- `ShortDescribe`：  
  `Harrison 重查的赔偿旧案中，有多份由他本人签署。`  
  `Several compensation rulings Harrison reviewed again bear his own signature.`
- 小玩法关系：`输出`。4115 的二阶段案号整理结果；不属于 4111 夜间检索的自动结论，用于 Watts R2。

重点（信息表达必不可少）：

1. 使用 4115 的局部复印/拓片与法院裁定目录并排，至少三组案号一致。
2. 对应裁定签字栏清楚显示同一 `Harrison` 签名或法官署名章。
3. 画面只建立“调阅案号 = 本人旧裁定”，不出现“自首完成”或责任结论。

美术参考（不影响推理）：

- 以档案管理员的铅笔圈线、案号索引卡和薄描图纸叠合表现人工整理。
- 分析图保留 4115 原纸材质，不制作现代数据报告。

---

### 4116 - Mary / Helen 案改判往来信

- 类型/地点：Item；法院档案室 Harrison 调阅文件。
- `Name`：`Mary / Helen案改判往来信` / `Mary and Helen Appeal Correspondence`
- `Describe`：  
  `Harrison 连续三次要求对 Mary / Helen 案作无罪改判，三次均被法院内部驳回或退回。最末一封附有第三次提交回执，日期在 Harrison 死前三天。`  
  `Three successive letters show Harrison requesting a not-guilty ruling in the Mary/Helen case; each request was rejected or returned by the court. The final letter carries a third-submission receipt dated three days before Harrison's death.`
- `ShortDescribe`：  
  `Harrison 连续三次推动无罪改判，最后一次提交发生在死前三天。`  
  `Harrison pressed for a not-guilty ruling three times, most recently three days before his death.`
- 小玩法关系：`无`。与 4113 共同用于 Watts R3。

重点（信息表达必不可少）：

1. 三封往来信以同一案件号串联，分别带 `REJECTED`、`RETURNED`、第三次 `RECEIVED` 回执。
2. `REQUEST FOR NOT-GUILTY RULING` 或同义核心措辞可读。
3. 第三次回执日期与 Harrison 死亡相隔三天；具体月日如与最终时间线冲突，以时间线为准。
4. 不把法院驳回者写成尚未确认的具体人物。

美术参考（不影响推理）：

- 三封不同日期的法院公函叠放，页角编号 1/3、2/3、3/3；红色处理章与蓝黑签收章区分。

---

### 4117 - Harrison 留下的编号纸条

- 类型/地点：Item；Harrison 未完成的自首证物箱。
- `Name`：`Harrison留下的编号纸条` / `Harrison's Numbered Note`
- `Describe`：  
  `Harrison 手写的一张折叠纸条，依次记有 SH-24-071、SH-24-118、SH-25-044、SH-26-093、SH-27-031、SH-27-126、SH-28-052`
  `A folded handwritten note from Harrison listing SH-24-071, SH-24-118, SH-25-044, SH-26-093, SH-27-031, SH-27-126, and SH-28-052. `
- `ShortDescribe`：  
  `七个用途不明的编号。`
  `Seven unexplained hospital numbers arranged by year.`
- 小玩法关系：`跨 Loop 调档输入`。L2 中先由 4213 让其中两个编号获得“死亡编号”意义，再凭 4218 解锁调档演出；七份病例展示完成后由 4117 更新生成 4219「五年七例儿童死亡病例对照表」。4117 本身不参与 Whitfield 指证。

重点（信息表达必不可少）：

1. 纸条必须逐字出现 `SH-24-071`、`SH-24-118`、`SH-25-044`、`SH-26-093`、`SH-27-031`、`SH-27-126`、`SH-28-052`，按年份先后纵向排列，不得改成占位符或随机流水号。
2. 七个编号使用同一医院编号格式，但不能出现姓名、年龄、病种或责任认定。
3. 不出现 `DEATH`、`CHILD`、`MILLER`、药剂批号、五年七例等提前解释用途的文字。
4. Harrison 笔迹与 4113、4116、4119 保持一致；纸条有反复折叠和随手核对留下的轻微铅笔勾记。

美术参考（不影响推理）：

- 小幅法院便笺或裁开的档案纸，蓝黑墨水手写；视觉重点是七个编号，而不是表格结构。

---

### 4118 - 医院冷藏库留样试剂

- 类型/地点：Item；Harrison 未完成的自首证物箱。
- `Name`：`医院冷藏库留样试剂` / `Hospital Cold-Storage Retained Sample`
- `Describe`：  
  `Harrison 通过正式手续从圣心医院冷藏库调取的一支官方留样。药瓶置于带独立碎冰槽和镀锌金属内胆的上锁木质保冷箱内，样本格另贴医院纸封；交接单逐次记录装箱时间、箱内温度与经手人，直至 Foster 接收。补冰无需开启样本格，药瓶也没有进入任何受助家庭。仅凭外观无法判断药液成分或是否足以致病。`
  `An official retained sample obtained by Harrison from Sacred Heart Hospital's cold store through formal procedure. The bottle traveled in a locked wooden cold box with a galvanized lining and separate crushed-ice compartment; the sample compartment carried its own hospital paper seal, while each handoff recorded time, interior temperature, and custodian. Ice could be replenished without opening the sample compartment, and the bottle never entered a recipient household. Appearance alone cannot establish its composition or medical risk.`
- `ShortDescribe`：  
  `封签、生产批号和冷藏交接记录完整的医院官方留样。`
  `An official hospital sample with intact seal, production lot, and cold-storage chain.`
- 小玩法关系：`分析输入`。由 Foster 完成受控化验后更新为 4703；L2 取得 4214 后，才能确认本物与 4212 属于同一采购记录、同一生产批次和同一配方。当前没有独立操作型小玩法文档，按剧情分析交付处理。

重点（信息表达必不可少）：

1. 医院标记、瓶颈封签、生产批号、冷藏登记卡、木质保冷箱纸封和逐次交接签名全部可读。
2. 药液外观保持普通，不用异常颜色提前宣布有毒。
3. 与 4212 使用同款瓶型、标签版式和生产批号 `SHC-28-B17`；4213 两瓶旧样本不得出现该批号或同批封签。
4. 冷藏与交接记录必须明确本物始终处于医院控制下，但不在图上写“排除家庭保存”这一后续推理结论。

美术参考（不影响推理）：

- 小型棕色或透明药用玻璃瓶，软木/橡胶塞外覆纸质封签，1920 年代医院药房标签。
- 放在带法院调取封签的上锁木质保冷箱中；箱体采用镀锌金属内胆与独立碎冰槽，附医院冷藏库出库卡和逐次签收条，不使用泡沫箱、凝胶冰袋或电子温度记录器。
- Harrison办公室场景只需出现封闭保冷箱；内胆、碎冰槽、封签、温度与交接记录均由本证物特写承载，不要求环境底图可读。

---

### 4119 - Harrison 亲笔资金流向图

- 类型/地点：Item；Harrison 未完成的自首证物箱。
- `Name`：`Harrison亲笔资金流向图` / `Harrison's Handwritten Fund-Flow Diagram`
- `Describe`：  
  `Harrison 手绘的资金流向图：圣心医院控股集团专项拨款账户，经匿名中转账户“1919-A”，进入 Harrison 私人账户。他只复原了资金方向，尚未查到 1919-A 的开户实体、授权签字人或实际控制者。`  
  `Harrison's handwritten fund-flow diagram traces Sacred Heart holding-group appropriations through the anonymous intermediary account “1919-A” into Harrison's personal account. He recovered the direction of the money, but not the account's registered entity, authorized signer, or actual controller.`
- `ShortDescribe`：  
  `专项拨款经“1919-A”中转后进入 Harrison 私人账户。`  
  `Program funds passed through “1919-A” before reaching Harrison's personal account.`
- 小玩法关系：`无`。提供资金方向背景，不作为 L5 身份锁固定输入。

重点（信息表达必不可少）：

1. 三段箭头清楚：`SACRED HEART APPROPRIATIONS → 1919-A → HARRISON PERSONAL ACCOUNT`。
2. `1919-A` 只显示匿名代号，旁边保留 Harrison 写下的问号或 `ENTITY? / SIGNER?`。
3. Harrison 的笔迹与 4113 批注保持一致，但不要与 Mickey 的 4514/4515 笔迹混淆。

美术参考（不影响推理）：

- 法律便笺纸、蓝黑钢笔、反复修改的箭头与圈线；像工作中的调查图，不是印刷完成的流程图。

---

### 4120 - 南区综合商业开发计划摘要

- 类型/地点：Item；Harrison 未完成的自首证物箱。
- `Name`：`南区综合商业开发计划摘要` / `South Side Commercial Redevelopment Summary`
- `Describe`：  
  `一份南区综合商业开发摘要，写明通过银行债务、司法裁定和地产接收逐步清空目标地块。文件出现 Tidewater 与 Lakeshore，但当前摘要没有把具体清退任务指向 O'Hara，也没有列出 Whale。`  
  `A summary of the South Side commercial redevelopment plan, outlining the use of bank debt, court rulings, and property transfer to clear target parcels. Tidewater and Lakeshore appear in the document, but this summary neither singles out O'Hara nor names Whale.`
- `ShortDescribe`：  
  `南区地块将通过债务、裁定和地产接收被逐步清空。`  
  `South Side parcels are to be cleared through debt, court rulings, and property transfer.`
- 小玩法关系：`无`。为 L4 清退线和 L5 外卷提供前置信息。

重点（信息表达必不可少）：

1. 流程栏清楚显示 `DEBT → JUDGMENT → PROPERTY ACQUISITION`。
2. `TIDEWATER`、`LAKESHORE` 两个机构名可读。
3. 地图或地块表只显示南区范围和编号，不突出 O'Hara 地址。
4. 不出现 Whale、Mickey、Sean 或水源维护。

美术参考（不影响推理）：

- 1920 年代地产项目摘要，折叠蓝图小图 + 打字说明页，企业印刷感冷静规整。

---

### 4121 - 1912 事故家庭索引

- 类型/地点：Item；附在 4120 末页。
- `Name`：`1912事故家庭索引` / `1912 Accident Family Index`
- `Describe`：  
  `附在开发计划末页的家庭索引。1912 年事故赔偿编号后来又出现在“南区居民援助计划”的贷款、违约和房产接收记录中。当前索引只建立编号复用与受害家庭方向，不包含 Sean O'Malley 的特殊处置页。`  
  `A family index attached to the redevelopment summary. Compensation numbers from the 1912 accident later reappear in South Side Resident Aid records for loans, defaults, and property transfers. The index establishes reused identifiers and affected families, but does not contain Sean O'Malley's special-treatment page.`
- `ShortDescribe`：  
  `1912事故赔偿编号后来被复用于南区贷款、违约和房产接收记录。`  
  `1912 accident compensation numbers were later reused in South Side loan, default, and property records.`
- 小玩法关系：`无`。为终幕 4517、4518 的 1912 材料提供前置编号认知。

重点（信息表达必不可少）：

1. 左栏为 `1912 ACCIDENT COMPENSATION NO.`，右侧能看到同编号在贷款、违约、接收栏重复出现。
2. 只显示家庭编号与姓氏摘要，不出现 Sean 的单独处置命令。
3. 编号体系需与 4517、4518 同源，待配置定码后全章统一。

美术参考（不影响推理）：

- 作为 4120 的附页，纸张、装订孔和企业抬头一致；部分编号被 Harrison 用铅笔连线。

---

## L1 小玩法附属美术（不计入 56 条证据）

### 4122 - Harrison 公开日程

- 用途：L1 夜间调阅检索输入，只记录公开庭审、会议与公务。
- 美术：法官周程表/预约簿；日期和公开公务可读，夜间栏保持空白。
- 禁区：不显示案名、夜间调阅或 Harrison 自查结论。
- 配置归属：玩法附属页面，不进入 state 的正式证据清单、ItemStaticData 或玩家背包。

### 4123 - 档案室闭馆后访问记录

- 用途：L1 夜间调阅检索输入，玩家在多人签入签出记录中定位 Harrison 的访问窗。
- 美术：多人姓名、进入时间、离开时间三栏；Harrison 行不预先高亮。
- 禁区：不把其画成只有 Harrison 一人的记录，也不提前显示该时段调阅的案名。
- 配置归属：玩法附属页面，不进入 state 的正式证据清单、ItemStaticData 或玩家背包。

---
