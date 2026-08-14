# Unit4 循环2 - 证据美术资产清单

> 叙事主题：Rosa 与圣心医院之争  
> 正式证据总数：11 条（含 2 条分析结果、1 条调档成果）
> ID 范围：4211-4219、4702-4703
> 数据源：`剧情设计/Unit4/state/loop2_state.yaml`、`avg_editor_v2/data/table/ItemStaticData.json`、`剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`  
> 全局规范与跨循环复用要求：见 [Unit4 证据美术资产总览](./Unit4_证据美术资产_总览.md)

---

## 证据总表

| ID | 中文名 | 类型/地点 | 小玩法关系 |
|---|---|---|---|
| 4211 | 医院配发红线注射器与十三日封签药盒 | Item；Zack 事务所，由 Rosa 交付。 | 输入/参照物 |
| 4212 | Isabel 使用后的封签药瓶 | Item；Zack 事务所，由 Rosa 交付。 | 主触发输入 |
| 4217 | Isabel 的病历本 | Item；Zack 事务所，从 Harrison 遗留材料中正式接收。 | 分析参照/编号核对 |
| 4702 | 经容量分析的回收药瓶 | 分析结果；4013 Foster 法医实验室。 | 输出 |
| 4216 | Miller 事故基金项目铭牌与康复名册 | Envir；圣心医院社会服务部／Miller 项目登记区。 | 无 |
| 4213 | 两名死者的旧药样本 | Item；4013 Foster 法医实验室，由 Foster 依法调取。 | 编号验证/剧情辅助 |
| 4218 | 验尸官办公室有限调档许可 | Key Item；4013 Foster 法医实验室，由 Foster 交付。 | 特殊对话门控 |
| 4219 | 五年七例儿童死亡病例对照表 | 调档成果；4012 社会服务部调档演出。 | 4117 更新输出 |
| 4703 | 经化验的医院冷藏库留样试剂 | 分析结果；4118 经 Foster 受控化验后取得。 | 分析输出 |
| 4214 | 圣心医院慈善项目采购与发放记录 | Item；法院会客室医院项目卷宗。 | 正式链条核对 |
| 4215 | 缺失的第十九页（副本） | Item；法院会客室，由 Mickey 交付。 | 无 |

---

## 证据详细卡片

### 4211 - 医院配发红线注射器与十三日封签药盒

- 类型/地点：Item；Zack 事务所，由 Rosa 交付。
- `Name`：`医院配发红线注射器与十三日封签药盒` / `Hospital Red-Line Syringe and Thirteen-Day Sealed Dose Box`
- `Describe`：  
  `圣心医院配发的玻璃注射器和十三日药盒。注射器红线处装有不可移动的金属止动环，活塞到达红线后无法继续抽取。药盒十三格均已按日开启，外沿保留 Rosa 的指纹确认条；这些指纹只能证明她接触过药盒，不能单独确认每格开启的具体日期。`  
  `A Sacred Heart glass syringe and thirteen-day dose box. A fixed metal stop at the red line prevents the plunger from drawing beyond the prescribed volume. All thirteen compartments have been opened, and Rosa's prints remain on the confirmation strip. The prints establish contact with the box, not the exact date each compartment was opened.`
- `ShortDescribe`：  
  `止动环限制单次抽取量，药盒十三格均已开启。`  
  `A fixed stop limits each draw, and all thirteen dose compartments have been opened.`
- 小玩法关系：`输入/参照物`。L2「十三次红线剂量核对」要求玩家持有 4211、4212、4217，并从 4212 触发容量分析。4211 提供单次红线剂量模板与十三次操作基数，不消耗；Whitfield R1 中作为剧情辅助自动展示，不进入玩家选证列表。

重点（信息表达必不可少）：

1. 玻璃注射器、红线和不可移动金属止动环必须同框；止动环是实体结构，不能只画一条红线。
2. 药盒必须恰好十三格且全部有开启痕迹，不能多格、少格或仍保持完整封闭。
3. 指纹确认条应表现为接触痕迹或取证显影，不得画成十三枚精确日期认证章。
4. 注射器、药盒的医院标记与 4212、4213、4214 使用同一 Sacred Heart 项目视觉体系。

美术参考（不影响推理）：

- 1920 年代玻璃针筒、金属活塞、黄铜/钢制止动环；避免现代塑料针管。
- 药盒为硬纸板或薄木盒，十三格以蜡纸或纸封签分隔，使用过后留下撕口与轻微药渍。
- 玩法内需提供可拖动活塞、受阻动画、十三格依次亮起和单次剂量模板资源。

---

### 4212 - Isabel 使用后的封签药瓶

- 类型/地点：Item；Zack 事务所，由 Rosa 交付。
- `Name`：`Isabel使用后的封签药瓶` / `Isabel's Used Sealed Medicine Bottle`
- `Describe`：  
  `Isabel 使用过的圣心医院药瓶。原医院封签、项目标签、批次编号和瓶体初始装量标定仍可辨，瓶中还留有部分药液。仅凭肉眼无法判断总共消耗了多少次规定剂量。`  
  `The Sacred Heart medicine bottle used for Isabel. Its original hospital seal, program label, batch number, and initial-fill calibration remain legible, and some liquid is still inside. Visual inspection alone cannot determine how many prescribed doses were consumed.`
- `ShortDescribe`：  
  `仍有剩余药液的回收瓶，保留封签、批次码和初始装量标定。`  
  `A partly filled returned bottle retaining its seal, batch code, and initial-fill calibration.`
- 小玩法关系：`主触发输入`。在 4013 Foster 法医实验室对本物执行容量分析；4211 作为必需参照，玩家完成剩余量读数、红线剂量确认和十三次核对后生成 4702。原物不消耗并接受二次封签。

重点（信息表达必不可少）：

1. 当前液面、初始装量标线、医院封签与批次码 `SHC-28-B17` 必须同时可辨。
2. 瓶封表现为“已使用但来源仍可核验”，不能画成从未开启的新瓶。
3. 与 4118 使用同款瓶型、标签和生产批号 `SHC-28-B17`；与 4212 自身分析后图保持同一瓶身划痕。4213 两瓶旧样本不得复制该批号。
4. 不在原图中写十三次吻合或无额外加量；那是 4702 的玩法结果。

美术参考（不影响推理）：

- 小型药用玻璃瓶，纸质标签因家庭保存略有卷边；液体保持普通透明/浅色，不用夸张毒性色。
- 玩法内另需量筒读数、白色衬板、Foster 二次封签和记录卡状态。

---

### 4217 - Isabel 的病历本

- 类型/地点：Item；Zack 事务所，从 Harrison 遗留材料中正式接收。
- `Name`：`Isabel的病历本` / `Isabel's Medical Record Book`
- `Describe`：
  `Isabel 在圣心医院接受十三日疗程时使用的病历本。逐日给药记录、医嘱剂量、药剂发放号和护士签注均可核对；病历只记录院方发放信息，不判断 Rosa 是否按记录完成每次注射。`
  `Isabel's Sacred Heart medical record for the thirteen-day course. Its daily administration entries, prescribed dose, medicine dispensing number, and nursing initials can be checked. The record documents what the hospital issued, not whether Rosa completed every injection exactly as written.`
- `ShortDescribe`：
  `记录十三日医嘱、逐日给药栏和 Isabel 的药剂发放号。`
  `Records the thirteen-day prescription, daily administration fields, and Isabel's dispensing number.`
- 小玩法关系：`分析参照/编号核对`。为 4702 提供十三日医嘱与给药记录背景；在 4214 中用发放号核对 4212 的生产批号和正式发放链。本物不单独证明是否存在第十四针，也不进入 Whitfield 玩家选证列表。

重点（信息表达必不可少）：

1. 1920 年代纸质病历夹内必须同时出现十三日医嘱、逐日给药栏、护士签注和独立药剂发放号。
2. 发放号与 4212 瓶签对应，但病历本身不直接写 Harrison 留样或“同批次结论”。
3. 不在病历上补写“第十四针”“家属有罪／无罪”或现代电子病历式时间戳。
4. 姓名 `ISABEL MARTINEZ` 可读；其余医学正文以能支撑给药史为限，避免用大字提前宣布死因。

美术参考（不影响推理）：

- 硬纸封皮、打字机医嘱页、护士蓝黑墨水逐日签注、药房发放联存根；边角有长期随身保存的磨损。

---

### 4702 - 经容量分析的回收药瓶

- 类型/地点：分析结果；4013 Foster 法医实验室。
- `Name`：`经容量分析的回收药瓶` / `Volume-Checked Returned Medicine Bottle`
- `Describe`：  
  `Foster 已登记原瓶和封签，测量剩余液量并完成回装与二次封签。现存药瓶的总消耗量与十三次规定红线剂量在测量容差内相符；再加入一整次红线剂量会越过容差带并侵入实际仍存区。因此，这只现存药瓶没有比十三次规定总量多消耗一整次剂量。该结果不能排除微量偏差、换瓶、补液或他人接触。`  
  `Foster logged the original bottle and seal, measured the remaining volume, then returned the liquid and applied a secondary seal. Total consumption matches thirteen prescribed red-line doses within measurement tolerance; one further full dose would cross the tolerance band into the volume still present. The bottle therefore did not consume one full dose beyond the prescribed thirteen. This does not exclude small deviations, replacement, refilling, or contact by another person.`
- `ShortDescribe`：  
  `实际消耗量与十三次红线剂量相符，第十四次完整剂量无法落入容差。`  
  `Consumption matches thirteen red-line doses; a full fourteenth dose cannot fit within tolerance.`
- 小玩法关系：`输出`。由 4212 的容量分析生成，4211 提供红线剂量模板，4217 提供医嘱疗程与给药记录；玩家完成剩余量测量、单次止动剂量确认和十三次核对后，亲手追加第十四次验证。原物不消耗。本物单独解锁 Doubt 4201，并作为 Whitfield R1 唯一可选证物。

重点（信息表达必不可少）：

1. 详情图以同一只 4212 药瓶为主体，新增 Foster 二次封签、签名和受控测量记录，不能画成全新报告瓶。
2. 分析记录清楚区分“已消耗区 / 综合容差带 / 实际仍存区”；十三份剂量末端落在容差带内。
3. 半透明第十四次剂量穿过容差带并侵入仍存区，保留铅笔划除标记。
4. 不写死毫升数；小玩法文档明确要求最终刻度由配置与美术联调校准。
5. 不包含药物毒性、批次责任或 Whitfield 主观知情结论。

美术参考（不影响推理）：

- 1920 年代法医纸质容量记录条、玻璃量筒拓片、黄铜卡槽和铅笔排线，不使用现代进度条或电子读数。
- 完成态可用带二次封签记录的法医文件夹承载，但瓶本身必须仍为视觉主体。

---

### 4216 - Miller 事故基金项目铭牌与康复名册

- 类型/地点：Envir；圣心医院社会服务部／Miller 项目登记区。
- `Name`：`Miller事故基金项目铭牌与康复名册` / `Miller Accident Fund Program Plaque and Recovery Register`
- `Describe`：  
  `社会服务部登记区陈列的 Miller 事故基金项目铭牌、历年康复名册、救助统计和家属感谢信。记录显示许多工伤家庭和儿童确实获得免费治疗并康复出院。这些材料证明项目有真实成果，不判断本轮药剂责任。`
  `The Miller Accident Fund program plaque, recovery register, aid statistics, and family thank-you letters displayed in the hospital's social-service registration area. They show that many injured workers' families and children received free care and recovered, establishing real outcomes without assigning responsibility for the medicine in this case.`
- `ShortDescribe`：  
  `名册记录多名接受免费治疗并康复出院的儿童。`  
  `The register records many children who received free care and recovered.`
- 小玩法关系：`无`。环境叙事，不进背包、不参与 Whitfield 指证。

重点（信息表达必不可少）：

1. 铭牌 `MILLER ACCIDENT FUND CHARITY PROGRAM` 清晰可读，不再写成儿童病房门牌。
2. 康复名册必须有足够多的正常出院记录，并与救助统计、家属感谢卡共同出现，不能只摆空壳牌子。
3. Miller 压印与 4114、4516 属同一体系。
4. 不夹带问题批次、死亡名单或“伪慈善”暗示。

美术参考（不影响推理）：

- 黄铜墙面铭牌、深色木框名册、社会服务登记台、手写出院日期和不同家庭的旧卡片；整体有真实使用与长期维护感。

---

### 4213 - 同配方药瓶封签组

- 类型/地点：Item；4013 Foster 法医实验室，由 Foster 从废弃样本库依法调取。
- `Name`：`同配方药瓶封签组` / `Matching-Formula Bottle Seal Set`
- `Describe`：
  `Giuseppe Rosselli 与 Bridget O'Shea 生前使用过的两只旧药瓶。原患者标签保留两人的姓名；使用者死亡后，药瓶被转入废弃样本库，并分别追加 DEATH REG. SH-24-071 与 DEATH REG. SH-24-118 吊签。两个完整编号都出现在 Harrison 纸条上。两只药瓶的残留物、封签和编号相互吻合，且与 Harrison 官方留样配方一致；但仅凭这组旧样本，不能确认它们与 Isabel 的药属于同一生产批次，也不能证明七名儿童都使用了同一配方。`
  `Two old medicine bottles used by Giuseppe Rosselli and Bridget O'Shea. Their original patient labels retain both names; after the patients died, the bottles were transferred to the discarded-sample archive and given DEATH REG. SH-24-071 and DEATH REG. SH-24-118 tags. Both complete numbers appear on Harrison's note. Their residues, seals, and numbers correspond, and their formula matches Harrison's official retained sample; these old samples alone cannot establish that they share Isabel's production batch or that all seven children received the same formula.`
- `ShortDescribe`：
  `Giuseppe／SH-24-071 与 Bridget／SH-24-118 均能在 Harrison 纸条上逐项对应；残留物、封签和编号与 Harrison 官方留样相互吻合，配方一致。`
  `Giuseppe/SH-24-071 and Bridget/SH-24-118 both match entries on Harrison's note; their residues, seals, and numbers correspond to Harrison's official retained sample, with a consistent formula.`
- 小玩法关系：`编号验证/剧情辅助`。本物使 4117 中两个编号获得“死亡编号”意义，并促成 4218 调档许可；Whitfield R2 击破后由 Zack 自动展示，不进入玩家选证列表，也不作为 4703 的生产批次输入。

重点（信息表达必不可少）：

1. Giuseppe 瓶必须同时可辨原患者姓名 `GIUSEPPE ROSSELLI` 与死后追加吊签 `DEATH REG. SH-24-071`；Bridget 瓶必须同时可辨 `BRIDGET O'SHEA` 与 `DEATH REG. SH-24-118`。姓名标签与追加吊签应有不同纸张、墨色或固定方式，表现为两个时期形成的信息层。
2. 两只瓶均归入 1924 年死亡登记，但流水号分别为 `071` 与 `118`；不得擅自改成不同年份，也不得把它们画成与 4118、4212 共享 `SHC-28-B17` 生产批号。
3. 瓶内只留少量陈旧残迹；视觉上不能暗示 Foster 已复原完整配方或原始浓度，配方一致性只来自纸面比对结果。
4. 不在瓶签上写“同配方”“同批次”或死亡原因结论；封签、编号和残留物只作为可比对的物理特征表现。

美术参考（不影响推理）：

- 两只瓶分别置于发黄蜡纸窗证物袋或木格托盘，封签旧化程度不同；旁附废弃样本登记簿局部与两个死亡编号的铅笔核对线。

---

### 4218 - 验尸官办公室有限调档许可

- 类型/地点：Key Item；4013 Foster 法医实验室，由 Foster 交付。
- `Name`：`验尸官办公室有限调档许可` / `Coroner's Limited Records Authorization`
- `Describe`：
  `验尸官办公室出具的限范围调档许可，只允许 Zack 与 Emma 在院方监督下查看 Harrison 纸条上七个指定编号对应的死亡登记和病历。许可不开放采购、批准或其他患者档案，也没有写明这些编号之间存在何种关系。`
  `A limited authorization from the coroner's office allowing Zack and Emma, under hospital supervision, to review the death registers and medical files tied to the seven numbers on Harrison's note. It does not open procurement, approval, or unrelated patient records, nor does it state how the seven numbers are connected.`
- `ShortDescribe`：
  `只允许调阅七个指定编号对应死亡登记和病历的限范围许可。`
  `A limited authorization covering only the death registers and medical files tied to seven specified numbers.`
- 小玩法关系：`特殊对话门控`。不锁定 4012 场景、基础调档员对话或环境调查；仅解锁调档员的“提交七个编号”特殊对话，许可不消耗。

重点（信息表达必不可少）：

1. 文面写明范围是七个指定医院编号对应的死亡登记与病历，并有验尸官办公室抬头、签章和日期。
2. 限制条款必须清楚排除采购卷宗、批准文件和无关患者档案。
3. 不出现 Miller 项目名称、七名儿童姓名或共同死因结论。
4. 七个编号可作为附件抄录，但版式与 4117 一致，不能额外补充解释。

美术参考（不影响推理）：

- 单页公务许可配一张窄幅编号附件，打字机正文、蓝黑签字、凸印或墨印公章；纸张保持行政文件的克制感。

---

### 4219 - 五年七例儿童死亡病例对照表

- 类型/地点：Clue；4012 社会服务部调档演出完成后，由 4117 更新生成。
- `Name`：`五年七例儿童死亡病例对照表` / `Five-Year Comparison of Seven Child Deaths`
- `Describe`：  
  `根据 Harrison 纸条和七份正式病历整理出的病例对照表。七个编号均对应儿童，七人都由 Whitfield 负责的 Miller 慈善项目经手，并在治疗期间出现相似的严重低血糖反应与器官损伤；院方均把责任归为家属误用、擅自加量或保存不当。Isabel Martinez 是时间最近的一例。表格不能单独证明七人使用了完全相同的配方或生产批次。`
  `A comparison assembled from Harrison's note and seven official medical files. Every number belongs to a child handled by Whitfield's Miller charity program; each child developed similar severe hypoglycemic reactions and organ injury during treatment, while the hospital assigned blame to family misuse, extra dosing, or poor storage. Isabel Martinez is the most recent case. The chart alone cannot prove that all seven received the exact same formula or production lot.`
- `ShortDescribe`：  
  `五年七名项目儿童出现相似症状，院方反复归责家属；Isabel 是最近一例。`
  `Seven program children show recurring symptoms and family blame over five years; Isabel is the latest case.`
- 小玩法关系：`4117 更新输出`。调档员按编号顺序摆放七份病历后生成并替换 4117 的调查状态；本物单独解锁 Doubt 4202，并作为 Whitfield R2 唯一可选证物。

重点（信息表达必不可少）：

1. 完成态必须保留 4117 七个编号的原顺序，并对应七份可数的病例索引卡。
2. 表格栏目至少呈现姓名、年龄、Miller 项目经手、治疗期症状和院方责任认定；不得增加未经病历确认的主观结论。
3. 最后一行是 `ROSA MARTINEZ / ISABEL MARTINEZ`，但不使用夸张高亮替玩家宣布阴谋。
4. 不设置药剂名称、配方、剂量或生产批次栏目；本证物不能把七名儿童锁成同一种药剂或同一生产批次。

美术参考（不影响推理）：

- 七张病历索引卡按时间铺在档案车台面，Harrison 原纸条置于左侧；完成态可加 Zack 的铅笔对照线，但不制作现代电子表格。

---

### 4703 - 经化验的医院冷藏库留样试剂

- 类型/地点：分析结果；4118 经 Foster 受控化验后取得。
- `Name`：`经化验的医院冷藏库留样试剂` / `Tested Hospital Cold-Storage Retained Sample`
- `Describe`：  
  `Foster 对医院官方冷藏留样的化验显示，有效成分浓度波动异常，并含有不应出现在合格成品中的降解杂质；按疗程连续使用可能造成严重低血糖反应与器官损伤。样本始终处于医院冷藏和封签交接控制下，结果不能由 Rosa 家庭或废弃样本库的保存环境解释。该化验不能单独确认 Isabel 药瓶与留样同批，也不能指出批准者或主观知情。`
  `Foster's tests of the hospital's official cold-storage retained sample show abnormal fluctuation in active concentration and degradation impurities that should not be present in a sound finished medicine. Repeated use over a course could cause severe hypoglycemic reactions and organ injury. Because the sample remained under hospital refrigeration and sealed chain of custody, its condition cannot be attributed to Rosa's home or the discarded-sample archive. The test alone does not establish that Isabel's bottle came from the same lot, nor identify an approver or prior knowledge.`
- `ShortDescribe`：  
  `医院规范冷藏的官方留样仍存在浓度波动、异常降解杂质与连续使用风险。`
  `The officially refrigerated hospital sample still shows concentration variation, abnormal degradation, and repeated-use risk.`
- 小玩法关系：`分析输出`。输入仅为 4118；4213 已另行完成与 Harrison 官方留样的配方比对，但不作为同批化验对照。与 4214 共同用于 Whitfield R3：4703证明医院控制下的留样本身有风险，4214再证明它与 Isabel 药瓶属于同一采购记录、同一生产批次和同一配方。

重点（信息表达必不可少）：

1. 保留 4118 原瓶身份、医院冷藏登记与交接记录，新增 Foster 二次封签、样本编号和化验结果卡。
2. 使用 1928 年可理解的颜色反应、沉淀、显微/效价对照和纸面记录，不出现现代色谱图、质谱、电子屏或精确分子图。
3. 结论用 `IRREGULAR POTENCY`、`ABNORMAL DEGRADATION` 等限度明确的英文，不写“蓄意投毒”。
4. 与 4118、4212、4214 的生产批号 `SHC-28-B17` 完全一致；4213 两瓶旧样本不得出现该批号。

美术参考（不影响推理）：

- 木质试管架、玻璃滴管、比色管、纸质结果卡和 Foster 的蓝黑签字；原药瓶置于中央受控托盘。

---

### 4214 - 圣心医院慈善项目采购与发放记录

- 类型/地点：Item；法院会客室医院项目卷宗。
- `Name`：`圣心医院慈善项目采购与发放记录` / `Sacred Heart Charity Program Procurement and Distribution Record`
- `Describe`：  
  `圣心医院慈善项目的采购、入库与发放合订记录。Isabel 病历中的药剂发放号与 Rosa 回收药瓶对应；该药瓶和 Harrison 官方冷藏留样列在同一采购记录下，生产批号均为 SHC-28-B17，配方相同。记录还显示该批药经过医院正式采购、入库，并由 Miller 慈善项目发给 Isabel。它不证明另外六名儿童使用了完全相同的配方或生产批次。`
  `A bound set of Sacred Heart charity-program procurement, intake, and distribution records. The dispensing number in Isabel's medical file matches Rosa's returned bottle; that bottle and Harrison's official cold-storage sample appear under the same procurement entry, share production lot SHC-28-B17, and use the same formula. The lot was formally purchased, received into hospital stock, and issued to Isabel through the Miller charity program. The record does not establish that the other six children received the exact same formula or production lot.`
- `ShortDescribe`：  
  `Isabel 药瓶与医院冷藏留样同属 SHC-28-B17，并由项目正式采购和发放。`
  `Isabel's bottle and the hospital retained sample share lot SHC-28-B17, formally purchased and issued by the program.`
- 小玩法关系：`正式链条核对`。与 4703 共同用于 Whitfield R3；4217 提供发放号，4212 与 4118／4703 提供同一生产批号。本物不为 4213 两瓶旧样本补写批次。

重点（信息表达必不可少）：

1. 四段核对关系清楚：`PURCHASE ORDER → HOSPITAL INTAKE → RETAINED SAMPLE / CHARITY DISPENSING`。
2. 生产批号 `SHC-28-B17` 同时对应 Harrison 官方留样和 Isabel 发放项；Isabel 发放号与 4217、4212 一致。
3. 配方栏显示两件药剂配方相同，但不得延伸覆盖另外六份历史病例。
4. 执行层副本不出现最终理事会签字原件。

美术参考（不影响推理）：

- 医院行政合订本，淡绿/米色格式纸、编号骑缝章、打字与手写核验混合；用页签帮助玩家追踪三步链条。

---

### 4215 - 缺失的第十九页（副本）

- 类型/地点：Item；法院会客室，由 Mickey 交付。
- `Name`：`缺失的第十九页（副本）` / `Missing Page Nineteen Copy`
- `Describe`：  
  `医院项目批准副本的目录将第十九页列为“理事会特别采购批准”，但装订内容从第十八页直接跳到第二十页。执行层副本没有这页，也没有签字原件。缺页只能证明一份特别采购批准页应当存在，不能据此认定批准者。`  
  `The project-approval copy lists page nineteen as “Board Special Procurement Approval,” yet the bound pages jump directly from eighteen to twenty. This execution-level copy contains neither that page nor the original signature. The gap establishes that an approval page should exist, not who signed it.`
- `ShortDescribe`：  
  `目录列有“理事会特别采购批准”，装订副本却从第18页跳到第20页。`  
  `The contents list a “Board Special Procurement Approval,” but the copy jumps from page 18 to page 20.`
- 小玩法关系：`无`。锁定伏笔，不参与 Whitfield 本轮三轮击穿。

重点（信息表达必不可少）：

1. 左侧目录行清楚显示 `PAGE 19 — BOARD SPECIAL PROCUREMENT APPROVAL`。
2. 右侧装订边缘或翻页构图必须让 `18` 后直接出现 `20`，第十九页物理缺失明确。
3. 不出现签字人剪影、Miller 姓名高亮或“Whitfield 撕走”的暗示。

美术参考（不影响推理）：

- 复印/抄写副本纸张比原件略灰，装订孔连续但第十九页被抽走；页码可用红蓝铅笔圈出。

---
