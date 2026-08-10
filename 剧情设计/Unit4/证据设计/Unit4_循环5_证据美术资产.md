# Unit4 循环5 - 证据美术资产清单

> 叙事主题：四十二层与终幕  
> 正式证据总数：13 条（含 4 条身份推理结果；收录终幕 4517-4519）  
> ID 范围：4511-4519、4705-4708  
> 数据源：`剧情设计/Unit4/state/loop5_state.yaml`、`avg_editor_v2/data/table/ItemStaticData.json`、`剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`  
> 全局规范与跨循环复用要求：见 [Unit4 证据美术资产总览](./Unit4_证据美术资产_总览.md)

---

## 证据总表

| ID | 中文名 | 类型/地点 | 小玩法关系 |
|---|---|---|---|
| 4511 | Mickey 定制钢笔 | Item；Mickey 私人办公室书桌。 | 身份锁输入 |
| 4512 | Mickey 的半支古巴雪茄 | Item；Mickey 私人烟灰缸。 | 身份锁输入 |
| 4513 | 1925 年内部接口接管记录 | Item；字母锁保险柜。 | 字母锁输出 + 身份锁输入 |
| 4514 | 1919 年的银行授权附页-Donnelly & Associates（手写签名） | Item；字母锁保险柜。 | 字母锁输出 + 双链输入 |
| 4515 | 手写功业簿 | Item；字母锁保险柜。 | 字母锁输出 + 身份锁输入 |
| 4516 | Miller 保险外卷与内封套 | Container/Item；字母锁保险柜。 | 字母锁输出 + 终幕容器 |
| 4705 | 1919-A 与 Donnelly & Associates 属于同一法律资金网络 | Derived Conclusion；L5 身份锁链 4501。 | 身份锁输出 |
| 4706 | Morrison 页结论 | Derived Conclusion；L5 身份锁链 4502。 | 身份锁输出 |
| 4707 | 书写者一致性 | Derived Conclusion；L5 身份锁链 4502。 | 身份锁输出 |
| 4708 | Mickey 就是 Morrison 死亡当晚的陌生访客 | Derived Conclusion；L5 身份锁链 4503。 | 身份锁输出 |
| 4517 | Tidewater 地基材料替换单 | Item；4516 内封套的 1912 内页。 | 终幕容器输出 |
| 4518 | Sean O'Malley 特殊处置页 | Item；4516 内封套的 1912 内页。 | 终幕容器输出 |
| 4519 | 后插入的水源维护页 | Item；4516 内封套的 1928 后插附件。 | 终幕容器输出/行动输入 |

---

## 证据详细卡片

> 当前运行真源采用 `loop5_state.yaml` 的三条并行、固定提交位身份锁。`L5_Whale身份开放推理面板_概念设计.md` 明确标为概念方向稿，未经另行批准不替代现行合同。本节按现行身份锁撰写，同时让证据图可在未来开放节点面板中复用。

### 4511 - Mickey 定制钢笔

- 类型/地点：Item；Mickey 私人办公室书桌。
- `Name`：`Mickey定制钢笔` / `Mickey's Custom Fountain Pen`
- `Describe`：  
  `一支刻有“M.F.D.”的定制钢笔。笔尖右侧有长期缺口，会在特定转折处留下稳定断墨。钢笔只能帮助确认同一书写工具与作者，不能单独证明用它写下的内容真实。`  
  `A custom fountain pen engraved “M.F.D.” A longstanding chip on the right side of the nib produces a stable ink break at particular turns of the stroke. The pen can help identify a writing instrument and author; it cannot by itself prove that the written content is true.`
- `ShortDescribe`：  
  `刻有“M.F.D.”，缺口笔尖会留下稳定断墨。`  
  `Engraved “M.F.D.,” with a chipped nib that leaves a repeatable break in the ink.`
- 小玩法关系：`身份锁输入`。当前固定链 4502 的输入之一，与 4514、4515 共同生成 4707，并支持 4706 的作者/参与视角判断；证据不消耗。笔尖放大和试写样本只在身份锁界面展开，不开放标准分析按钮，不生成新的 Item ID。

重点（信息表达必不可少）：

1. 笔帽 `M.F.D.` 清楚可读，雕刻属于私人定制而非临时刻上。
2. 笔尖右侧缺口必须在放大图中可辨，并提供一条试写断墨样本。
3. 断墨特征与 4514 签名、4515 关键转折笔画完全一致。
4. 不把钢笔画成自动打印犯罪内容的“真相钥匙”。

美术参考（不影响推理）：

- 1920 年代高档黑色硬橡胶/赛璐珞钢笔，金色笔夹与金尖，长期使用处有细微磨亮。
- 玩法附属资源包括笔尖微距、标准试写线和三份笔迹局部对照裁切。

---

### 4512 - Mickey 的半支古巴雪茄

- 类型/地点：Item；Mickey 私人烟灰缸。
- `Name`：`Mickey的半支古巴雪茄` / `Mickey's Half-Smoked Cuban Cigar`
- `Describe`：  
  `Mickey 私人烟灰缸里留下的半支古巴雪茄，来源有书桌位置、刻有“M.F.D.”的烟灰缸和 Zack 既往目击共同支持。它的品牌、直径和含咬位置与 Morrison 现场烟蒂一致；烟嘴右侧同样呈现前段内陷、后段缺少一枚完整压痕和约三十度斜向受力。`  
  `A half-smoked Cuban cigar from Mickey's private ashtray, supported as his by the desk location, the ashtray engraved “M.F.D.,” and Zack's prior observation. Its brand, diameter, and mouth position match the butt at Morrison's house; the right side also shows a collapsed forward section, one missing complete rear impression, and force at roughly thirty degrees.`
- `ShortDescribe`：  
  `有可靠私人来源，并与 Morrison 现场烟蒂共享同一复合齿痕。`  
  `Reliably sourced to Mickey and bearing the same compound bite as the cigar at Morrison's house.`
- 小玩法关系：`身份锁输入`。当前固定链 4503 与 4315 共同生成 4708；4153001 Morrison 最后通话记录只作为到访时间窗前置语境，不占提交位。4704 只提示比较方向。证据不消耗；标准化侧视裁切只在身份锁界面使用，不开放标准分析按钮。

重点（信息表达必不可少）：

1. 烟灰缸 `M.F.D.`、私人书桌位置和半支雪茄同框，所有权来源不能只靠 Zack 旁白。
2. 与 4315 同品牌卷标、直径、茄衣颜色、含咬位置和复合齿痕；至少提供标准化并排侧视裁切。
3. 齿痕四维同时匹配，不能只靠“同品牌”或“右侧咬过”完成视觉结论。
4. 单独查看 4512 时不写“杀人者”或 Whale。

美术参考（不影响推理）：

- 高档古巴雪茄，燃烧长度约剩一半；Mickey 烟灰缸为深色石材/银器，私人缩写低调刻在边缘。

---

### 4513 - 1925 年内部接口接管记录

- 类型/地点：Item；字母锁保险柜。
- `Name`：`1925年内部接口接管记录` / `1925 Internal Interface Transfer Record`
- `Describe`：  
  `一份 1925 年内部接管记录。文件说明 Donnelly & Associates 自 1919 年起持续负责 Tidewater 的合同、产权、银行重组和诉讼拖延；1925 年接管页只写内部代号“W”，同页代号说明写明“W / Whale”。职责栏为“警务协调 / 银月会联络 / 非合同障碍处理”。文件未出现接管者实名，需要与其他材料交叉核对。`  
  `A 1925 internal transfer record. It states that Donnelly & Associates had handled Tidewater contracts, title work, bank restructuring, and litigation delays since 1919. The 1925 transfer page identifies only the internal code “W,” defined on the same page as “W / Whale.” Its duties are “police coordination / Silver Moon liaison / non-contractual obstacle handling.” The transferee is not named and must be established by cross-checking other evidence.`
- `ShortDescribe`：  
  `1925年接管页记录了 W / Whale 的职责，但没有显示接管者实名。`  
  `The 1925 transfer page records W / Whale's duties without naming the transferee.`
- 小玩法关系：`字母锁输出 + 身份锁输入`。4418 字母锁玩法开柜后与 4514-4516 同次取得；当前固定链 4501 输入之一，并与 4515 用于 Mickey Expose R3。证据不消耗。

重点（信息表达必不可少）：

1. 日期 `1925`、代号 `W / WHALE` 和三项职责全部可读；接管者实名不得出现。
2. 历史栏明确 Donnelly & Associates 自 `1919` 起经营法律业务，接管 Whale 职责发生在 `1925`，不得混成同一年。
3. 文件应体现内部机密登记，不是 Mickey 自己写给 Zack 的认罪书。
4. `Miller` 上层审批可保留机构级来源，但不能在本页展开 U5 小 Charles 或水源行动。

美术参考（不影响推理）：

- 机密人事/职责转接表，深色文件夹、打字正文、代号栏红色或蓝色登记章；保留 1920 年代企业官僚质感。

---

### 4514 - 1919 年的银行授权附页-Donnelly & Associates（手写签名）

- 类型/地点：Item；字母锁保险柜。
- `Name`：`1919 年的银行授权附页-Donnelly & Associates（手写签名）` / `1919 Bank Authorization Addendum — Donnelly & Associates (Hand-Signed)`
- `Describe`：  
  `一份 1919 年银行授权附页，将“1919-A”登记为 Donnelly & Associates 的受托结算子账户。唯一授权签字人为 Michael F. Donnelly，账户用途栏引用 Harrison 存根上的圣心医院赔偿案号。附页证明账户授权与法律实体关系，不代表每笔记录内容都真实。`  
  `A 1919 bank-authorization addendum registering “1919-A” as a fiduciary settlement subaccount of Donnelly & Associates. Michael F. Donnelly is the sole authorized signer, and the account-purpose field cites the Sacred Heart compensation case numbers found on Harrison's receipt. The addendum establishes account authority and legal-entity linkage, not the truth of every transaction recorded under it.`
- `ShortDescribe`：  
  `1919-A 属于 Donnelly & Associates 受托子账户，Mickey 是唯一授权签字人。`  
  `1919-A is a Donnelly & Associates fiduciary subaccount with Mickey as sole authorized signer.`
- 小玩法关系：`字母锁输出 + 双链输入`。开柜取得；当前固定链 4501 与 4112、4416、4513 生成 4705，链 4502 与 4511、4515 生成 4707；同时单独用于 Mickey Expose R1。证据不消耗；签名裁切只在身份锁界面使用，不开放标准分析按钮。

重点（信息表达必不可少）：

1. `ACCOUNT: 1919-A`、`FIDUCIARY SETTLEMENT SUBACCOUNT`、`DONNELLY & ASSOCIATES`、`SOLE AUTHORIZED SIGNER: MICHAEL F. DONNELLY` 全部可读。
2. Sacred Heart 赔偿案号与 4112 备注一一对应；账号和案号格式必须复用。
3. Mickey 正式签名是 4515 笔迹比对的已知样本，需提供高分辨率签字裁切。
4. 签名笔画在关键转折处出现与 4511 缺口笔尖一致的断墨，但不能夸张成肉眼远景就自动得出结论。

美术参考（不影响推理）：

- 1919 年银行格式附页，奶白厚纸、压印抬头、钢笔签名和公证/银行骑缝章；与 4112 属同一账户表格体系。

---

### 4515 - 手写功业簿

- 类型/地点：Item；字母锁保险柜。
- `Name`：`手写功业簿` / `Handwritten Ledger of Deeds`
- `Describe`：  
  `同一名书写者长期私下记录的一本功业簿。“救下的人”和“被牺牲的人”被放在同一种冷静执行格式中。Morrison 页写有“会面失控；现场按自杀口径收尾；惯用手留有偏差；清场由上层另线完成”，其中包含普通律师无法从公开记录取得的参与者视角。关键转折处存在稳定断墨，但作者身份尚未确认。`  
  `A private ledger maintained over many years by one unidentified writer, placing people saved and people sacrificed in the same controlled operational format. The Morrison entry reads, “meeting lost control; scene closed under suicide narrative; handedness discrepancy remained; clearance completed on a separate upper-level line,” revealing a participant's perspective unavailable in public records. Stable ink breaks appear at key turns, but the writer's identity has not yet been established.`
- `ShortDescribe`：  
  `一名未确认书写者长期记录救援、牺牲和现场收尾。`  
  `An unidentified writer recorded rescues, sacrifices, and scene cleanup over many years.`
- 小玩法关系：`字母锁输出 + 身份锁输入`。开柜取得；当前固定链 4502 与 4511、4514 生成 4706、4707，并与 4513 用于 Mickey Expose R3。证据不消耗；翻页与笔迹裁切属于身份锁内部查看，不开放标准分析按钮。

重点（信息表达必不可少）：

1. 不是财务账本，而是按姓名/案件、结果、保留接口、代价记录的私人行动簿。
2. 至少可浏览 O'Brien、Webb、Moore、Harrison、Morrison、Rosa、Mary 七条；Morrison 行的四段核心内容必须可读。
3. Harrison 行清楚区分 `UPPER-LEVEL INDEPENDENT CLEARANCE` 与 `PIERCE — SCENE/FILES`，避免把所有行动都写成 Mickey 直接下令。
4. Rosa、Mary 行保留真实救援成果，不能把全部善行画成伪造。
5. 同一人长期笔迹一致；断墨位置可供 4511、4514 后续对照，但卡面不标注作者。
6. 不写成一页完整犯罪自白替玩家宣布 `I AM WHALE`。

美术参考（不影响推理）：

- 深色皮面私人簿册、索引页签、蓝黑墨水和多年不同深浅；版式克制、近似律师工作记录，但内容透露其私人价值算法。
- 需制作可翻阅关键页、Morrison 页大图、笔迹局部与断墨裁切。

---

### 4516 - Miller 保险外卷与内封套

- 类型/地点：Container/Item；字母锁保险柜。
- `Name`：`Miller保险外卷与内封套` / `Miller Insurance Outer File and Sealed Inner Packet`
- `Describe`：  
  `一套由外卷和防拆内封套组成的 Miller 保险档案。外卷列出南区优先处理户与执行职责：银行制造债务，Lakeshore 负责资金、估价和审批，Tidewater 接收房产，W / Whale 协调法律障碍、Pierce 警务网络和银月会。内封套仍未拆，外部目录只指向“1912 / 特殊处置与事故材料”和“1928 / 后插入执行附件”。`  
  `A Miller insurance file consisting of an outer volume and a tamper-sealed inner packet. The outer file lists priority South Side holdouts and operational roles: the bank creates debt, Lakeshore handles funds, valuation, and approval, Tidewater receives property, and W / Whale coordinates legal obstacles, Pierce's police network, and the Silver Moon Society. The inner packet remains sealed; its exterior index points only to “1912 / Special Treatment and Accident Materials” and “1928 / Later-Inserted Execution Attachments.”`
- `ShortDescribe`：  
  `外卷列出南区执行分工；防拆内封套在四十二层仍保持未拆。`  
  `The outer file lists South Side operational roles; the tamper-sealed inner packet remains unopened on the forty-second floor.`
- 小玩法关系：`字母锁输出 + 终幕容器`。开柜时与 4513-4515 同次取得，但不参加 L5 身份锁或 Expose。安全地点剪断防拆线后，1912 内页输出 4517、4518，1928 后插附件输出 4519；不合成新 ID。

重点（信息表达必不可少）：

1. 外卷与内封套轮廓、材质和可读层级明确分开；L5 只允许查看外卷与内封外观。
2. 外卷的职责分工可读，但不出现实际分赃账户。
3. 内封套使用 Miller 事故基金压印、防拆线和两项目录；与 4114、4216 的 Miller 标识同源。
4. L5 详情图和开柜动画绝不能露出 4517-4519 的正文、Sean 姓名或水源点。
5. 终幕需制作剪断防拆线、抽出 1912 内页和发现后插 1928 附件的分阶段容器状态。

美术参考（不影响推理）：

- 厚重深蓝/炭灰外卷、黄铜夹、蜡/压纹防拆封套和棉线；封套底部暗夹应能在第二次整理时被发现，但 L5 初见不抢眼。

---

### 4705 - 1919-A 与 Donnelly & Associates 属于同一法律资金网络

- 类型/地点：Derived Conclusion；L5 身份锁链 4501。
- `Name`：`1919-A与Donnelly & Associates属于同一法律资金网络` / `1919-A and Donnelly & Associates Share One Legal Financial Network`
- `Describe`：  
  `1919-A 存根、Donnelly 银行授权附页、1919 旧信封和 1925 接管记录共同证明：Mickey 先实际控制 Donnelly 的法律资金接口，后来接管“W / Whale”职责。这个结论依赖账户授权与接管记录，不是因为几个材料恰好都出现1919年。`  
  `The 1919-A receipt, Donnelly bank authorization, 1919 envelope, and 1925 transfer record together show that Mickey first controlled Donnelly's legal-financial interface and later assumed the “W / Whale” role. The conclusion rests on account authority and the transfer record, not merely on several documents sharing the year 1919.`
- `ShortDescribe`：  
  `Mickey 先控制 Donnelly 法律资金接口，后于1925年接管 W / Whale 职责。`  
  `Mickey controlled the Donnelly legal-financial interface before assuming W / Whale in 1925.`
- 小玩法关系：`身份锁输出`。固定链 4501 输入为 4112 + 4514 + 4416 + 4513；完成后生成本事实卡，不消耗输入。

重点（信息表达必不可少）：

1. 使用四张来源缩略卡和两段时间轴：`1919 — LEGAL/FINANCIAL CONTROL`、`1925 — W/WHALE TRANSFER`。
2. 账户授权线应比“同年”连线更醒目，避免视觉上鼓励只靠年份猜结论。
3. 事实卡为 CASE BOARD/身份锁 UI 结果，不画成世界内现成报告。

美术参考（不影响推理）：

- Zack 的铅笔连线、年份标签和文件局部，完成态使用克制的黄铜扣合/盖章反馈。

---

### 4706 - Morrison 页结论

- 类型/地点：Derived Conclusion；L5 身份锁链 4502。
- `Name`：`Morrison页结论` / `Conclusion from the Morrison Entry`
- `Describe`：  
  `功业簿的 Morrison 页知道会面失控、现场被按自杀口径收尾、惯用手留下偏差，以及爆炸清场由上层另一条线完成。这些内容属于杀人、现场伪装和事后修正参与者的视角，不是普通律师从公开记录能够整理出的信息。`  
  `The Morrison entry knows that the meeting lost control, the scene was closed under a suicide narrative, a handedness discrepancy remained, and the explosive clearance came through a separate upper-level line. This is the viewpoint of someone involved in the killing, staging, and subsequent correction, not information an ordinary lawyer could compile from public records.`
- `ShortDescribe`：  
  `Morrison 页包含只有会面与现场收尾参与者才知道的内部视角。`  
  `The Morrison entry contains an internal viewpoint available only to a participant in the meeting and staging.`
- 小玩法关系：`身份锁输出`。由链 4502 对 4515 的内部内容与既有 Morrison 现场事实进行复原；与 4707 同链生成，不消耗输入。

重点（信息表达必不可少）：

1. 以 4515 Morrison 页四段文字为核心，旁接 4311 右手枪位、4316 上层另线装置等已知事实缩略图。
2. 结论强调“参与者视角”，但最终实名仍需 4707/后续 Expose，不在卡面直接写 `Mickey killed Morrison`。
3. 不是世界内法医报告。

美术参考（不影响推理）：

- 深色功业簿页置中，外围为低透明现场记录，Zack 用铅笔写下 `PARTICIPANT'S KNOWLEDGE`。

---

### 4707 - 书写者一致性

- 类型/地点：Derived Conclusion；L5 身份锁链 4502。
- `Name`：`书写者一致性` / `Consistent Authorship`
- `Describe`：  
  `Mickey 功业簿与银行授权附页上正式归属于 Michael F. Donnelly 的签名笔迹一致；两者在相同转折处都出现定制钢笔缺口造成的稳定断墨。功业簿由 Mickey 长期书写。这个结论确认作者，不保证簿中每项自我评价都客观真实。`  
  `The handwriting in Mickey's ledger matches the signature formally attributed to Michael F. Donnelly on the bank authorization. Both show the same repeatable ink break at corresponding stroke turns, caused by the chipped custom pen. Mickey wrote the ledger over time. This establishes authorship, not the objective truth of every self-assessment in the book.`
- `ShortDescribe`：  
  `正式签名、功业簿笔迹和缺口钢笔断墨共同确认作者是 Mickey。`  
  `The formal signature, ledger handwriting, and chipped-pen ink breaks identify Mickey as the author.`
- 小玩法关系：`身份锁输出`。固定链 4502 输入为 4515 + 4514 + 4511；与 4706 一起完成作者与行动视角证明。

重点（信息表达必不可少）：

1. 三栏微距：4514 正式签名、4515 同字形/转折、4511 缺口笔尖试写。
2. 至少标出三处相同字形和两处稳定断墨，不能只给系统绿勾。
3. 边界标签提示 `AUTHORSHIP — CONTENT NOT AUTOMATICALLY TRUE`。
4. 结果为推理 UI 卡，不是凭空出现的笔迹鉴定公文。

美术参考（不影响推理）：

- 描图纸叠合、放大镜边框、铅笔标记与编号圆点；避免现代生物识别/百分比匹配界面。

---

### 4708 - Mickey 就是 Morrison 死亡当晚的陌生访客

- 类型/地点：Derived Conclusion；L5 身份锁链 4503。
- `Name`：`Mickey就是Morrison死亡当晚的陌生访客` / `Mickey Was Morrison's Unknown Visitor`
- `Describe`：  
  `Morrison 现场烟蒂与 Mickey 私人烟灰缸中的半支雪茄，在品牌、直径、含咬位置以及“前段内陷、后段缺少一枚完整压痕、约三十度斜向受力”的复合齿痕上全部吻合。结合 Donnelly & Associates 的来电时间窗，可以确认 Mickey 在 Morrison 死前到过现场。这个结论证明访客身份，不单靠雪茄证明开枪行为。`  
  `The cigar butt from Morrison's house and the half-smoked cigar from Mickey's private ashtray match in brand, diameter, mouth position, and the compound bite pattern: forward collapse, one missing complete rear impression, and force at roughly thirty degrees. Together with the Donnelly & Associates call window, the match establishes that Mickey visited Morrison before his death. It identifies the visitor; the cigars alone do not prove the shooting.`
- `ShortDescribe`：  
  `两支雪茄的来源与复合齿痕全部吻合，锁定 Mickey 是死前访客。`  
  `The sourced cigars and their full compound bite match identify Mickey as the pre-death visitor.`
- 小玩法关系：`身份锁输出`。固定链 4503 输入为 4315 + 4512；4153001 只提供 22:43 后的到访窗口，4704 只提供比较方向，均不占提交位。输入不消耗。

重点（信息表达必不可少）：

1. 两支雪茄并排标准化展示，四项匹配维度逐项可见，不以单一颜色或品牌替代完整比对。
2. 来源卡同时保留“湿杯垫现场”和“M.F.D. 私人烟灰缸”，防止只比外观不比所有权来源。
3. 可在边缘附 22:43 Donnelly 来电窗口，但不把接线员证词画成亲眼见到 Mickey。
4. 结论卡写“访客”，不写“仅凭雪茄确认枪手”。

美术参考（不影响推理）：

- 证物摄影式左右对照、齿痕轮廓描图和四个铅笔核对点；完成反馈保持案件板风格。

---

## 非 Loop 终幕｜Miller 内封套

### 4517 - Tidewater 地基材料替换单

- 类型/地点：Item；4516 内封套的 1912 内页。
- `Name`：`Tidewater地基材料替换单` / `Tidewater Foundation Material Substitution Order`
- `Describe`：  
  `1912 年工程材料替换单。原定承重材料在事故前被主动替换为更低等级的材料，批准与执行时间都早于事故记录。文件证明材料降级是事前决定，尚不能单独说明谁预见或希望事故发生。`  
  `A 1912 construction-material substitution order. The specified load-bearing material was deliberately replaced with a lower-grade material before the accident, with approval and execution dates preceding the incident record. It establishes a prior downgrade, not by itself who foresaw or intended the accident.`
- `ShortDescribe`：  
  `事故前，Tidewater 主动把原定承重材料替换为更低等级材料。`  
  `Before the accident, Tidewater deliberately replaced the specified load-bearing material with a lower-grade one.`
- 小玩法关系：`终幕容器输出`。安全地点剪开 4516 内封套并查看 1912 内页时取得；不参加 L5 身份锁或 Expose，不生成派生 ID。

重点（信息表达必不可少）：

1. 双栏对照 `ORIGINAL SPECIFICATION` / `AUTHORIZED SUBSTITUTE`，承重等级或质量指标明确下降。
2. 批准/执行日期早于事故日期；具体材料名称、等级和数值须经工程与年代考据后统一，不由美术自行编造。
3. Tidewater 抬头和项目编号与 4120、4516 外卷同体系。
4. 不印“制造事故”或谋杀结论。

美术参考（不影响推理）：

- 1912 年工程变更单、蓝图纸边角、铅笔承重批注和企业盖章；纸张明显比 1928 附件更旧。

---

### 4518 - Sean O'Malley 特殊处置页

- 类型/地点：Item；4516 内封套的 1912 内页。
- `Name`：`Sean O'Malley特殊处置页` / `Sean O'Malley Special-Treatment Page`
- `Describe`：  
  `1912 年的特殊处置页，要求将 Sean O'Malley 与工人队伍分开，并在事故记录完成前“处理其异议”。页面有老 Charles 的签名，但没有直接写出杀人、弃尸或伪造事故命令。它使 Sean 的死亡从普通工伤进入高度明确的谋杀疑云，完整执行链仍需后续调查。`  
  `A 1912 special-treatment page ordering that Sean O'Malley be separated from the work crew and that his objection be “handled” before the accident record was completed. The page bears the elder Charles's signature but contains no direct order to kill, dispose of a body, or falsify the accident. It turns Sean's death from an ordinary workplace accident into a strong murder suspicion, while leaving the execution chain unresolved.`
- `ShortDescribe`：  
  `事故记录完成前，Sean 被要求与工人分开并“处理其异议”。`  
  `Before the accident record was completed, Sean was to be separated from the crew and his objection “handled.”`
- 小玩法关系：`终幕容器输出`。与 4517 同在 1912 内页；不参加 L5 身份锁，U5 才处理执行人与弃尸链。

重点（信息表达必不可少）：

1. `SEAN O'MALLEY`、`SEPARATE FROM WORK CREW`、`HANDLE HIS OBJECTION BEFORE ACCIDENT RECORD IS COMPLETED` 可读。
2. 老 Charles 的正式签名可读，但正文不能出现 `KILL`、`BODY`、`DUMP` 等直接命令。
3. 与 4517 共享 1912 项目编号和旧纸张批次，显示两页属于同一事故档案。
4. 不提前画出具体杀人方法、执行人或小 Charles 越权。

美术参考（不影响推理）：

- 单页机密附件，正文少而冷，页角有 `SPECIAL HANDLING` 章；签名墨水老化、纸面有封存压痕。

---

### 4519 - 后插入的水源维护页

- 类型/地点：Item；4516 内封套的 1928 后插附件。
- `Name`：`后插入的水源维护页` / `Later-Inserted Water-System Maintenance Page`
- `Describe`：  
  `一张后来插入档案的水源维护页，纸张批次和日期格式与原计划不同。文件表面安排在四天后，对 O'Hara 私人井和两个公共水点进行“封闭、清洗、重新开放”，却没有列出污染物、执行人、小 Charles 签名或老 Charles 的正常审批。它足以提示有人追加了水源层面的危险行动，但不能让人准确预知行动会提前到当夜。`  
  `A water-system maintenance page inserted later into the file, using a different paper batch and date format from the original plan. On its face, it schedules the O'Hara private well and two public water points for “closure, cleaning, and reopening” four days later, yet names no contaminant, operator, younger Charles signature, or normal approval by the elder Charles. It indicates a dangerous water-related addition but does not allow an accurate prediction that action would be moved forward to that night.`
- `ShortDescribe`：  
  `后插页安排四天后处理 O'Hara 私井和两个公共水点，审批与执行信息异常缺失。`  
  `A later-inserted page schedules the O'Hara well and two public water points four days later, with abnormal gaps in approval and execution.`
- 小玩法关系：`终幕容器输出/行动输入`。拆开 4516 的 1928 后插附件取得；抵达南区发现中毒症状后，Zack 交给 Watts，用于封闭标记水点和组织救援。无分析或合成产物。

重点（信息表达必不可少）：

1. 三个地点可读：`O'HARA PRIVATE WELL` + 两个公共水点；与 L4 O'Hara 后巷井结构一致。
2. 表面执行日明确在发现文件的四天后，不能写成当夜日期。
3. 操作词只写 `CLOSE / CLEAN / REOPEN` 或等义行政语言，不出现毒物名称。
4. 纸张、日期格式、打字机字形与原档案明显不同，表现后插；但不得用现代荧光高亮替玩家宣布伪造。
5. 签批栏异常空缺：无小 Charles 签名，也无老 Charles 正常审批。

美术参考（不影响推理）：

- 较新的 1928 行政表格纸夹在旧档案中，裁切尺寸略有差异；附简化水点位置图和三处维护标记。
- 需要可从详情图中清楚裁出三个地点，供 Watts 后续公共卫生封锁表现复用。

---

## L5 身份锁玩法附属美术（当前正式合同）

### 固定链 4501｜法律壳与身份演变

- 输入卡：4112、4514、4416、4513。
- 输出卡：4705。
- 视觉重点：1919 账户授权与 1925 职责接管必须分成两段，不能只按同年配对。

### 固定链 4502｜功业簿作者与行动视角

- 输入卡：4515、4514、4511。
- 输出卡：4706、4707。
- 视觉重点：内容视角与作者识别是两个不同结果；先看内部知识，再用正式签名与缺口笔尖确认作者。

### 固定链 4503｜Morrison 近期访客

- 输入卡：4315、4512。
- 前置语境：4153001 Morrison 最后通话记录；不占提交位。
- 提示方向：4704；不占提交位。
- 输出卡：4708。
- 视觉重点：品牌、直径、含咬位置、复合齿痕和私人物件来源全部匹配。

### 通用交互美术

- 当前 state 为三链并行、固定槽位、玩家确认提交；错误不消耗证据、不清空已完成链。
- 输入证据缩略图必须能展开查看本文 `Describe` 与关键视觉裁切。
- 派生卡 4705-4708 使用 CASE BOARD 事实卡模板，不制作成世界内凭空出现的报告纸。
- Mickey 承认前，界面只显示“已具备对质依据”，不得出现文字等式 `MICKEY = WHALE`。
- 开放节点网概念稿若未来获批，需要另行更新 State、玩法规范和本节资源清单；当前不按该概念追加全量节点美术。

---
