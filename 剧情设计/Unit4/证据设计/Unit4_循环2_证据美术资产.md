# Unit4 循环2 - 证据美术资产清单

> 叙事主题：Rosa 与圣心医院之争  
> 正式证据总数：8 条（含 2 条分析结果）  
> ID 范围：4211-4216、4702-4703  
> 数据源：`剧情设计/Unit4/state/loop2_state.yaml`、`avg_editor_v2/data/table/ItemStaticData.json`、`剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`  
> 全局规范与跨循环复用要求：见 [Unit4 证据美术资产总览](./Unit4_证据美术资产_总览.md)

---

## 证据总表

| ID | 中文名 | 类型/地点 | 小玩法关系 |
|---|---|---|---|
| 4211 | 医院配发红线注射器与十三日封签药盒 | Item；Zack 事务所，由 Rosa 交付。 | 输入/参照物 |
| 4212 | Isabel 使用后的封签药瓶 | Item；Zack 事务所，由 Rosa 交付。 | 主触发输入 |
| 4702 | 经容量分析的回收药瓶 | 分析结果；4013 Foster 法医实验室。 | 输出 |
| 4216 | Miller 事故基金病房铭牌与康复名册 | Envir；圣心医院 Miller 事故基金病房。 | 无 |
| 4213 | 同批次药瓶封签组 | Item；4013 Foster 法医实验室，由 Foster 依法调取。 | 无独立操作 |
| 4703 | 经化验的问题批次药剂 | 分析结果；4118 经 Foster 受控对照试验后取得。 | 分析输出 |
| 4214 | 圣心医院采购与发放记录 | Item；法院会客室医院项目卷宗。 | 无独立操作 |
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
- 小玩法关系：`输入/参照物`。L2「十三次红线剂量核对」要求玩家持有 4211、4212，并从 4212 触发容量分析。4211 提供单次红线剂量模板与十三次操作基数，不消耗；与 4702 共同用于 Whitfield R1。

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
3. 与 4118、4213 使用同款瓶型、标签、批次码位置；与 4212 自身分析后图保持同一瓶身划痕。
4. 不在原图中写十三次吻合或无额外加量；那是 4702 的玩法结果。

美术参考（不影响推理）：

- 小型药用玻璃瓶，纸质标签因家庭保存略有卷边；液体保持普通透明/浅色，不用夸张毒性色。
- 玩法内另需量筒读数、白色衬板、Foster 二次封签和记录卡状态。

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
- 小玩法关系：`输出`。由 4211 + 4212 的「十三次红线剂量核对」生成；三步为测量剩余量、确认单次止动剂量、核对十三次并亲手追加第十四次验证。原物不消耗。与 4211 共同解锁 Doubt 4201。

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

### 4216 - Miller 事故基金病房铭牌与康复名册

- 类型/地点：Envir；圣心医院 Miller 事故基金病房。
- `Name`：`Miller事故基金病房铭牌与康复名册` / `Miller Accident Fund Ward Plaque and Recovery Register`
- `Describe`：  
  `病房门口的 Miller 事故基金铭牌和历年康复名册。名册、家属感谢卡与护士记录显示，许多工伤家庭和儿童确实在这里获得免费治疗并康复出院。这些材料证明项目有真实成果，不判断本轮药剂责任。`  
  `The Miller Accident Fund ward plaque and its recovery register. The register, family thank-you cards, and nursing notes show that many injured workers' families and children received free treatment here and recovered. These materials establish real outcomes without assigning responsibility for the suspect medicine.`
- `ShortDescribe`：  
  `名册记录多名接受免费治疗并康复出院的儿童。`  
  `The register records many children who received free care and recovered.`
- 小玩法关系：`无`。环境叙事，不进背包、不参与 Whitfield 指证。

重点（信息表达必不可少）：

1. 铭牌 `MILLER ACCIDENT FUND CHILDREN'S WARD` 清晰可读。
2. 康复名册必须有足够多的正常出院记录和家属感谢卡，不能只摆空壳牌子。
3. Miller 压印与 4114、4516 属同一体系。
4. 不夹带问题批次、死亡名单或“伪慈善”暗示。

美术参考（不影响推理）：

- 黄铜墙面铭牌、深色木框名册、护士手写出院日期和不同家庭的旧卡片；整体有真实使用与长期维护感。

---

### 4213 - 同批次药瓶封签组

- 类型/地点：Item；4013 Foster 法医实验室，由 Foster 依法调取。
- `Name`：`同批次药瓶封签组` / `Matching-Batch Bottle Seal Set`
- `Describe`：  
  `另外两名死亡儿童留下的空药瓶封签组。两只空瓶的瓶颈封签和批次标记，与 Rosa 的回收瓶及 Harrison 留下的样本一致。它证明异常不只围绕 Isabel 一瓶出现，但不能单独说明药剂成分。`  
  `A set of empty medicine bottles retained from two other deceased children. Their neck seals and batch marks match Rosa's returned bottle and Harrison's preserved sample. This shows that Isabel's bottle is not the only case tied to the batch, but does not by itself establish the medicine's composition.`
- `ShortDescribe`：  
  `另外两只死亡病例空瓶与 Rosa 药瓶、Harrison 样本具有相同批次封签。`  
  `Two other fatal-case bottles carry the same batch seals as Rosa's bottle and Harrison's sample.`
- 小玩法关系：`无独立操作`。作为 Whitfield R2 证据，与 4117 共同使用；视觉上承担四瓶批次比对。若后续实现批次比对动画，4213 是主对照组，4118、4212 为外部参照，不生成新 ID。

重点（信息表达必不可少）：

1. 两只空瓶必须分别带独立病例标签，但共享同一批次码 `SHC-28-B17` 与封签版式。
2. 对照构图中允许带出 4118、4212 的标签局部，四件批次码位置必须完全一致。
3. 瓶内为空或只留干涸残迹，不能与仍有药液的 4212 混淆。
4. 不在封签上写“有毒”或死亡原因结论。

美术参考（不影响推理）：

- 两只瓶分别置于蜡纸窗证物袋或木格托盘，附法医调取标签；封签旧化程度因保存年份不同略有差异。

---

### 4703 - 经化验的问题批次药剂

- 类型/地点：分析结果；4118 经 Foster 受控对照试验后取得。
- `Name`：`经化验的问题批次药剂` / `Tested Suspect-Batch Medicine`
- `Describe`：  
  `Foster 的加急对照试验显示，同批样本的有效成分效价波动异常，并出现不应存在于合格成品中的降解迹象。连续使用可能造成严重低血糖反应与器官损伤；单支家庭保存不当不足以解释多支同批样本的一致异常。该结果不能指出谁批准或调换了药剂。`  
  `Foster's expedited comparative tests show abnormal variation in active strength and degradation signs that should not appear in a sound finished product. Repeated use could cause severe hypoglycemic reactions and organ damage; poor storage in one home cannot explain consistent abnormalities across several bottles from the same batch. The result does not identify who approved or altered the medicine.`
- `ShortDescribe`：  
  `同批样本效价波动并出现异常降解，单户保存不当不足以解释。`  
  `Same-batch samples vary in strength and show abnormal degradation not explained by one household's storage.`
- 小玩法关系：`分析输出`。输入为 4118，Foster 以 4213 同批封签组/样本作支持对照；当前没有独立可操作小玩法文档，按受控实验与对话交付。与 4214 共同用于 Whitfield R3。

重点（信息表达必不可少）：

1. 保留 4118 原瓶身份，新增法医封签、样本编号和多支同批对照记录。
2. 使用 1928 年可理解的颜色反应、沉淀、显微/效价对照和纸面记录，不出现现代色谱图、质谱、电子屏或精确分子图。
3. 结论用 `IRREGULAR POTENCY`、`ABNORMAL DEGRADATION` 等限度明确的英文，不写“蓄意投毒”。
4. 与 4118、4212、4213、4214 的批次码 `SHC-28-B17` 完全一致。

美术参考（不影响推理）：

- 木质试管架、玻璃滴管、比色管、纸质结果卡和 Foster 的蓝黑签字；原药瓶置于中央受控托盘。

---

### 4214 - 圣心医院采购与发放记录

- 类型/地点：Item；法院会客室医院项目卷宗。
- `Name`：`圣心医院采购与发放记录` / `Sacred Heart Procurement and Distribution Record`
- `Describe`：  
  `圣心医院慈善项目的采购、入库与发放合订记录。同一问题批次编号依次出现在正式采购单、医院入库号和发放清单上，发放对象集中于底层移民儿童项目。记录证明药剂进入了医院正式链条，不是护士私领或家庭转手。`  
  `A bound set of Sacred Heart charity-program procurement, intake, and distribution records. The same suspect batch appears on the official purchase order, hospital intake entry, and recipient list, which is concentrated in the low-income immigrant children's program. The record establishes formal hospital distribution rather than private removal by a nurse or transfer between families.`
- `ShortDescribe`：  
  `同一问题批次贯穿正式采购、医院入库和慈善项目发放记录。`  
  `The same suspect batch runs through official purchase, hospital intake, and charity-program distribution.`
- 小玩法关系：`无独立操作`。与 4703 共同用于 Whitfield R3；为 4213 的批次标签提供正式记录对照。

重点（信息表达必不可少）：

1. 三页或三栏连续关系清楚：`PURCHASE ORDER → HOSPITAL INTAKE → CHARITY DISTRIBUTION`。
2. 批次码 `SHC-28-B17` 在三处重复且位置醒目；与实物瓶签一致。
3. 发放对象栏目显示儿童慈善项目，但不要罗列过多个人隐私正文。
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
