# Unit4 循环4 - 证据美术资产清单

> 叙事主题：Patrick 留下的另一种解释  
> 正式证据总数：11 条（含 2 条记忆观察结果）  
> ID 范围：4411-4419、4704、4709  
> 数据源：`剧情设计/Unit4/state/loop4_state.yaml`、`avg_editor_v2/data/table/ItemStaticData.json`、`剧情设计/Unit4/Unit4_大纲0723_逻辑重构版_v3.md`  
> 全局规范与跨循环复用要求：见 [Unit4 证据美术资产总览](./Unit4_证据美术资产_总览.md)

---

## 证据总表

| ID | 中文名 | 类型/地点 | 小玩法关系 |
|---|---|---|---|
| 4411 | Lakeshore 清退协警通知 | Item；Zack 事务所，由 Doris 从大衣口袋交出。 | 剧情行动输入 |
| 4412 | Lakeshore 最终收购协议 | Item；O'Hara 家桌面。 | 现实行动输入 |
| 4413 | Margaret 写给 O'Hara 的短便条 | Item；O'Hara 家，收购协议旁。 | 场景解锁输入 |
| 4414 | 临时停止执行回执 | Item/剧情结果；O'Hara 家，由 Watts 跟进送达。 | 电话交互输出 |
| 4415 | 1903 南区码头旧照片 | Item；Margaret 家 Patrick 旧物。 | 记忆观察输入 |
| 4704 | 右下牙长期缺损 | Derived Memory；查看 4415 后触发。 | 记忆观察输出/提示节点 |
| 4416 | Patrick 葬礼册与 1919 旧信封 | Item；Margaret 家 Patrick 旧物。 | 记忆观察输入 + 跨玩法输入 |
| 4709 | 1919 同时出现的两项可观察事实 | Derived Memory；查看 4416 后生成。 | 记忆观察输出 |
| 4417 | Patrick 外套口袋里的粉笔转运牌 | Clue；Margaret 家 Patrick 旧外套。 | 无 |
| 4418 | Patrick 遗物匣 | Key Item；Margaret 指证后主动交付。 | L4-L5 跨 Loop 主输入 |
| 4419 | Margaret 写给 Mickey 但未寄出的短笺 | Item；Margaret 家 Patrick 旧物中。 | 无 |

---

## 证据详细卡片

### 4411 - Lakeshore 清退协警通知

- 类型/地点：Item；Zack 事务所，由 Doris 从大衣口袋交出。
- `Name`：`Lakeshore清退协警通知` / `Lakeshore Police-Assistance Eviction Notice`
- `Describe`：  
  `Lakeshore 发出的清退协警通知。O'Hara 家被列为第一批核心拒售户，文件要求辖区警员在次日上午第三次接触时到场“维持民事秩序”，并备注住户已两次明确拒售。文件被 Morrison 放进 Doris 的大衣口袋，因此从爆炸中保留下来。`  
  `A Lakeshore notice requesting police assistance for a clearance action. The O'Hara home is listed among the first core holdouts, and precinct officers are requested to attend the third contact the next morning to “maintain civil order.” A note states that the resident has already refused twice. Morrison placed the document in Doris's coat pocket, allowing it to survive the explosion.`
- `ShortDescribe`：  
  `O'Hara 被列为核心拒售户，第三次接触将有辖区警员到场。`  
  `O'Hara is listed as a core holdout, with precinct officers assigned to the third contact.`
- 小玩法关系：`剧情行动输入`。触发前往 O'Hara 家并支持临时停止执行申请；不进入 Margaret Expose R1。

重点（信息表达必不可少）：

1. `O'HARA`、`CORE HOLDOUT`、`THIRD CONTACT`、`POLICE TO MAINTAIN CIVIL ORDER` 可读。
2. 备注明确住户已两次拒售，不得写成双方已达成搬迁协议。
3. Lakeshore 抬头与 4412、4120、4516 外卷统一。
4. 文件边缘可有大衣口袋折痕，但不应有爆炸烧损。

美术参考（不影响推理）：

- 企业打字通知配警务协助抄送栏，冷灰纸张、蓝色收文章；折成三折塞在大衣内袋。

---

### 4412 - Lakeshore 最终收购协议

- 类型/地点：Item；O'Hara 家桌面。
- `Name`：`Lakeshore最终收购协议` / `Lakeshore Final Purchase Agreement`
- `Describe`：  
  `Lakeshore 向 O'Hara 提出的最终收购协议。报价明显低于正常价值，并要求在四十八小时内签署。O'Hara 没有签名，而是在签名页亲手写下“不出售”。`  
  `Lakeshore's final purchase offer to O'Hara. The price is plainly below ordinary value and the agreement demands a signature within forty-eight hours. O'Hara did not sign; she wrote “I WILL NOT SELL” across the signature page.`
- `ShortDescribe`：  
  `低价收购协议限时四十八小时，O'Hara 在签名页写下“不出售”。`  
  `A low-price forty-eight-hour offer, marked “I WILL NOT SELL” by O'Hara.`
- 小玩法关系：`现实行动输入`。与 4411 和 O'Hara 的拒售事实用于电话申请临时停止执行；与 O'Hara 证词共同用于 Margaret Expose R1。

重点（信息表达必不可少）：

1. 抬头 `LAKESHORE — FINAL PURCHASE AGREEMENT` 和 `48 HOURS` 限期可读。
2. 报价栏明显偏低，但具体金额尚未由 canon 锁定，需在房产价值表确定后统一填写。
3. 签名栏没有 O'Hara 正式签字，只有她的大字手写 `I WILL NOT SELL`。
4. 不画成已生效协议，不盖成交或付款章。

美术参考（不影响推理）：

- 多页地产合同、奶白厚纸、企业压印；O'Hara 的拒售字迹用深色钢笔/铅笔，笔压重、横跨签名栏。

---

### 4413 - Margaret 写给 O'Hara 的短便条

- 类型/地点：Item；O'Hara 家，收购协议旁。
- `Name`：`Margaret写给O'Hara的短便条` / `Margaret's Note to O'Hara`
- `Describe`：  
  `Margaret 留给 O'Hara 的短便条：“把报价签了，先搬来我这里。别找 Zack。”便条末尾有 Margaret 的签名。`  
  `A short note from Margaret to O'Hara: “Sign the offer and come stay with me first. Don't go to Zack.” Margaret's signature appears at the bottom.`
- `ShortDescribe`：  
  `Margaret 要 O'Hara 签约搬走，并明确写着“别找 Zack”。`  
  `Margaret tells O'Hara to sign, move out, and “don't go to Zack.”`
- 小玩法关系：`场景解锁输入`。取得后解锁 Margaret 家；与 O'Hara 证词共同用于 Margaret Expose R2。

重点（信息表达必不可少）：

1. 画面英文正文固定表达三件事：签报价、先搬来、不要找 Zack。
2. Margaret 签名必须清楚，使便条来源无需靠猜。
3. 与 4419 保持同一老年女性笔迹体系，但 4413 更匆忙、更短促。

美术参考（不影响推理）：

- 从普通记事纸撕下的小条，折过一次，压在协议上；蓝黑墨水略有停顿。

---

### 4414 - 临时停止执行回执

- 类型/地点：Item/剧情结果；O'Hara 家，由 Watts 跟进送达。
- `Name`：`临时停止执行回执` / `Temporary Stay of Enforcement Receipt`
- `Describe`：  
  `值班法官签发的临时停止执行回执，有效至次日傍晚。复核完成前，警员不得协助进入房屋、搬动财物或强制带离住户；回执不能阻止合法卫生检查。`  
  `A temporary stay issued by the duty judge and valid until the following evening. Pending review, police may not assist entry into the home, removal of property, or forced removal of the resident. The stay does not bar a lawful health inspection.`
- `ShortDescribe`：  
  `暂时禁止警员协助入屋、搬物或强制带离住户，但不阻止卫生检查。`  
  `It temporarily bars police-assisted entry, property removal, or forced removal, but not a health inspection.`
- 小玩法关系：`电话交互输出`。Zack 以 4411、4412 和 O'Hara 拒售事实联系 Watts；值班法官签发后取得。本件不参与 Margaret 指证，证明保护真实生效。

重点（信息表达必不可少）：

1. `TEMPORARY STAY OF ENFORCEMENT`、生效期限和三项禁止行为可读。
2. 限定条款 `DOES NOT BAR LAWFUL HEALTH INSPECTION` 必须保留，为终幕后续留合法接口。
3. 值班法官签名、法院印章、Watts 登记/送达栏完整。
4. 不写成永久产权胜诉或全面禁止任何进入。

美术参考（不影响推理）：

- 法院快速签发的单页回执，红色临时章、蓝黑签字和送达时间栏；纸面较新，带夜间匆忙处理的墨迹。

---

### 4415 - 1903 南区码头旧照片

- 类型/地点：Item；Margaret 家 Patrick 旧物。
- `Name`：`1903南区码头旧照片` / `1903 South Side Dock Photograph`
- `Describe`：  
  `一张 1903 年南区码头旧照片。Patrick、Liam、少年 Mickey 与工人们站在货栈前。照片只记录他们当时同处工运网络，不直接说明后来清场中的折返、受伤或使命交接。`  
  `A 1903 photograph from the South Side docks. Patrick, Liam, a teenage Mickey, and other workers stand before a freight shed. The photograph records their shared labor network at the time; it does not itself establish the later rescue, injuries, or any transfer of a mission.`
- `ShortDescribe`：  
  `1903年，Patrick、Liam、少年 Mickey 与工人们在南区码头货栈前合影。`  
  `Patrick, Liam, a teenage Mickey, and dock workers pose before a South Side freight shed in 1903.`
- 小玩法关系：`记忆观察输入`。查看照片触发 Zack 对少年 Mickey 右下牙伤与长期偏右含咬习惯的童年记忆，生成 4704；原照片不消耗。

重点（信息表达必不可少）：

1. Patrick、Liam、少年 Mickey 三人可辨，但构图不能把 Mickey 单独置于“继承人”中心位。
2. 背景明确是南区码头货栈和工人群体；照片日期 `1903` 可在背面手写。
3. 少年 Mickey 的牙伤不必在正面远景中清晰到可直接比对；细节由记忆观察 4704 承担。

美术参考（不影响推理）：

- 棕褐银盐相片、厚卡托、边缘磨损和背面家族注记；工人穿着、货栈工具符合 1903 年码头环境。

---

### 4704 - 右下牙长期缺损

- 类型/地点：Derived Memory；查看 4415 后触发。
- `Name`：`右下牙长期缺损` / `Longstanding Lower-Right Tooth Damage`
- `Describe`：  
  `Zack 想起 1903 年清场后，少年 Mickey 嘴角带血，右下第一臼齿外侧牙尖缺了一块，邻近第二前臼齿向内偏移。他后来长期用右侧、约三十度斜向含咬雪茄。这个记忆只提供比较方向，不能单独证明 Morrison 的访客是谁。`  
  `Zack remembers teenage Mickey after the 1903 clearance, blood at his mouth, with the outer cusp of the lower-right first molar broken and the adjacent second premolar displaced inward. He later habitually held cigars on the right at roughly a thirty-degree angle. This memory provides a direction for comparison and cannot by itself identify Morrison's visitor.`
- `ShortDescribe`：  
  `Mickey 的旧牙伤会造成右侧、约三十度斜向的稳定含咬习惯。`  
  `Mickey's old dental injury produces a stable right-side bite at roughly thirty degrees.`
- 小玩法关系：`记忆观察输出/提示节点`。由 4415 触发；只提示玩家在 L5 比较 4315 与 4512，不占身份锁 4503 提交位，也不参加 Expose。

重点（信息表达必不可少）：

1. 作为记忆卡/观察图，不画成现代牙科 X 光或法医鉴定报告。
2. 可用少年 Mickey 嘴角伤势局部 + 简洁手绘牙位记忆示意，明确右下位置、缺损牙尖和邻牙内偏。
3. 不把 4315 烟蒂直接叠成“匹配成功”，不出现访客身份结论。

美术参考（不影响推理）：

- Zack 童年记忆使用低饱和棕灰、边缘虚化；牙位辅助线采用铅笔笔记风格。

---

### 4416 - Patrick 葬礼册与 1919 旧信封

- 类型/地点：Item；Margaret 家 Patrick 旧物。
- `Name`：`Patrick葬礼册与1919旧信封` / `Patrick Funeral Register and 1919 Envelope`
- `Describe`：  
  `Patrick 葬礼册记录着葬礼来宾和日期；Zack 记得葬礼后 Mickey 对他说“他没做完的，我会接着做。”同存的旧信封以 Donnelly & Associates 为抬头，法人代表为 Michael F. Donnelly，始于 1919 年并印有四十二层办公室地址。两件材料只把葬礼承诺与法律壳起点放在同一年，不能单凭年份证明账户控制或 Whale 身份。`  
  `Patrick's funeral register records the date and attendees; Zack remembers Mickey saying afterward, “I'll carry on what he left unfinished.” An old envelope kept with it bears the Donnelly & Associates letterhead, names Michael F. Donnelly as principal, dates from 1919, and lists a forty-second-floor office address. Together they place the funeral promise and the beginning of the legal shell in the same year, but the shared date alone proves neither account control nor the identity of Whale.`
- `ShortDescribe`：  
  `1919年，Mickey 作出葬礼承诺，Donnelly & Associates 也开始持续经营。`  
  `In 1919, Mickey made his funeral promise as Donnelly & Associates began continuous operation.`
- 小玩法关系：`记忆观察输入 + 跨玩法输入`。查看后生成 4709；本件在 L5 身份锁链 4501 与 4112、4513、4514 共同生成 4705，并提供四十二层地址。

重点（信息表达必不可少）：

1. 葬礼册日期与 1919 旧信封日期清楚落在同一年，但不能只靠构图画成“等号”。
2. 信封抬头 `DONNELLY & ASSOCIATES`、`MICHAEL F. DONNELLY`、`42ND FLOOR` 可读。
3. 葬礼册中 Mickey 作为来宾之一出现，不伪造 Patrick 的使命授权文字。
4. 信封视觉体系需与 4514、4513 的 Donnelly 文件一致。

美术参考（不影响推理）：

- 黑边葬礼登记册、旧教堂纸张和米黄商业信封并置；信封长期保存而泛黄，邮戳/日期仍可读。

---

### 4709 - 1919 同时出现的两项可观察事实

- 类型/地点：Derived Memory；查看 4416 后生成。
- `Name`：`1919同时出现的两项可观察事实` / `Two Observable Facts from 1919`
- `Describe`：  
  `Patrick 葬礼后，Mickey 说会接着做；同在 1919 年，Donnelly & Associates 以 Michael F. Donnelly 为法人代表开始持续经营。这两项事实同时出现，形成调查方向，但不能证明 1919-A 的账户归属或 Mickey 当时已经是 Whale。`  
  `After Patrick's funeral, Mickey said he would carry on the work; in the same year, Donnelly & Associates began continuous operation under Michael F. Donnelly. Their coincidence creates a direction for investigation, but does not establish ownership of 1919-A or that Mickey was already Whale.`
- `ShortDescribe`：  
  `Mickey 的葬礼承诺与 Donnelly 法律壳起点都出现在1919年。`  
  `Mickey's funeral promise and the beginning of the Donnelly legal shell both occur in 1919.`
- 小玩法关系：`记忆观察输出`。由 4416 生成，仅作怀疑方向；不参加 L5 固定身份锁，也不替代 4514 的账户授权证明。

重点（信息表达必不可少）：

1. 使用“葬礼册日期卡 + 旧信封日期卡”并列，中间只用开放式铅笔括号，不画确定等号。
2. 结果卡必须带边界提示 `SAME YEAR — CONTROL NOT YET PROVEN` 或等义简短标签。
3. 不出现 Whale 标识。

美术参考（不影响推理）：

- CASE BOARD 记忆观察卡，沿用 4416 原物缩略图和 Zack 的铅笔年份圈线。

---

### 4417 - Patrick 外套口袋里的粉笔转运牌

- 类型/地点：Clue；Margaret 家 Patrick 旧外套。
- `Name`：`Patrick外套口袋里的粉笔转运牌` / `Chalk Transfer Tag from Patrick's Coat`
- `Describe`：  
  `1919 年清场转运使用的小块硬纸牌，长期留在 Patrick 外套口袋里。牌上只写着“WEST SIDE / ONE LEFT”，没有姓名；当时闸门流程会把已确认姓名写在牌面。它证明 Patrick 听见还有一人后便折返，当时尚不知道被困者是 Mickey。`  
  `A small card used during the 1919 clearance transfer, preserved in Patrick's coat pocket. It reads only “WEST SIDE / ONE LEFT,” with no name; the gate procedure normally added a confirmed name to the tag. It shows that Patrick turned back after hearing one person remained, before knowing the trapped worker was Mickey.`
- `ShortDescribe`：  
  `牌上只有“WEST SIDE / ONE LEFT”，没有被困者姓名。`  
  `The tag reads only “WEST SIDE / ONE LEFT,” with no trapped person's name.`
- 小玩法关系：`无`。Margaret Expose R3 的单件强证据，不进入遗物匣字母锁。

重点（信息表达必不可少）：

1. 正面文字固定为两行 `WEST SIDE` / `ONE LEFT`，必须清晰且无姓名栏填写。
2. 牌面可保留空白 `NAME:` 栏或流程预留区，帮助玩家看出姓名缺失是有意义的，而不是美术漏写。
3. 使用粉笔/粗铅笔，不得改成正式印刷救援名单。

美术参考（不影响推理）：

- 从行李牌或硬纸箱边角撕下的小牌，约掌心大小，穿孔断绳、煤灰和外套口袋压痕明显。

---

### 4418 - Patrick 遗物匣

- 类型/地点：Key Item；Margaret 指证后主动交付。
- `Name`：`Patrick遗物匣` / `Patrick's Keepsake Box`
- `Describe`：  
  `Patrick 的深色橡木遗物匣。顶盖刻着“P.B.”，正面嵌有氧化的工人运动领袖徽章，长侧面刻着“FOR THE MANY WE PAY THE FEW”。匣内保存一张遇难当晚未使用的返程票。它证明 Patrick 原本有回家安排，并保存了一句后来被 Mickey 长期使用的信条；它不构成使命交接。`  
  `Patrick's dark oak keepsake box. “P.B.” is carved into the lid, an oxidized labor-organizer badge is set into the front, and the long side bears the inscription “FOR THE MANY WE PAY THE FEW.” Inside is an unused return ticket from the night he was injured. It shows that Patrick planned to go home and preserves a phrase Mickey later adopted; it does not constitute a transfer of mission.`
- `ShortDescribe`：  
  `刻有七词信条并保存未使用返程票的 Patrick 遗物匣。`  
  `Patrick's box bears a seven-word creed and contains an unused return ticket.`
- 小玩法关系：`L4-L5 跨 Loop 主输入`。L4 玩家旋转匣身、找到完整刻句并亲手选出七个首字母，记录跨 Loop 状态 `FTMWPTF`；L5 玩家拨入七位机械字母锁，打开保险柜并一次性取得 4513-4516。玩法不生成新证据 ID，4418 不消耗、不参加身份锁或 Expose。

重点（信息表达必不可少）：

1. 必须复用 U2 2107 的同一物件：约 25×18×10 cm 深色橡木匣、顶盖 `P.B.`、正面工运徽章和侧面完整刻句均不得变形或改位。
2. U4 新增可旋转物件状态和打开后的内衬/返程票状态；不能只交一张闭合平面图。
3. 完整刻句必须位于同一长侧面、同一阅读方向，清晰可选出七个词首字母。
4. 返程票标明回程/返家方向和未使用状态，但不写“为了 Mickey 折返”。
5. L4 首字母玩法另需七枚黄铜字片和旧皮革记录条；完成态清楚显示 `FTMWPTF`。
6. 不增加授权书、继承留言或 Patrick 指名 Mickey 的内容。

美术参考（不影响推理）：

- 保持 U2 既有哑光木蜡油、圆润磨损边角、黄铜搭扣和氧化徽章。
- 刻句为浅而工整的手工刻痕；选中反馈使用贴合刻痕的薄黄铜描边，不用现代霓虹光。
- 内部为旧布/皮革衬层，返程票长期压存但文字可读。

---

### 4419 - Margaret 写给 Mickey 但未寄出的短笺

- 类型/地点：Item；Margaret 家 Patrick 旧物中。
- `Name`：`Margaret写给Mickey但未寄出的短笺` / `Margaret's Unsent Note to Mickey`
- `Describe`：  
  `Margaret 写给 Mickey 却没有寄出的短笺：“葬礼那天你说你会接着做。我已经拦不住你了。那晚的完整经过，不要再对 Zack 提。”短笺确认 Margaret 主动参与维持简化版本，但不证明 Mickey 的身份。`  
  `An unsent note from Margaret to Mickey: “At the funeral you said you would carry it on. I cannot stop you now. Do not tell Zack the full account of that night again.” It confirms Margaret's active role in preserving the simplified story, but does not establish Mickey's identity.`
- `ShortDescribe`：  
  `Margaret 要 Mickey 不再向 Zack 提起1919年当晚的完整经过。`  
  `Margaret asks Mickey never again to tell Zack the full account of the night in 1919.`
- 小玩法关系：`无`。动机材料，不参加 Margaret R3、遗物匣密码或 L5 身份锁。

重点（信息表达必不可少）：

1. 三句核心内容完整可读，收件人可为 `Mickey`，但无寄出邮戳。
2. 与 4413 同一 Margaret 笔迹；本件更犹豫，有停笔、划改或未封口状态。
3. 不加入 Mickey 回信、Patrick 遗言或 Whale 相关字样。

美术参考（不影响推理）：

- 未装入信封或只折起未封的私人短笺，边缘因多年保存而脆化；放在 Patrick 旧物底层。

---

## L4-L5 字母锁玩法附属美术（不新增证据 ID）

- 4418 可旋转物件：闭合正面、刻句侧面、打开内衬三种状态。
- 七词可选区域与薄黄铜首字母描边。
- 七格旧皮革记录条与 `F/T/M/W/P/T/F` 黄铜字片。
- L5 七个并列机械字母轮、中央刻线、七个锁舌状态点和黄铜把手。
- 保险柜内部四层/四组文件轮廓：4513、4514、4515、整袋封存的 4516。
- 禁止在开柜动画中露出 4517、4518、4519，禁止用密码正确直接播放 `Mickey = Whale` 结论。

---
