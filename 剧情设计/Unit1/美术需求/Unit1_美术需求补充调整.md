# Unit1 美术需求补充调整

> 版本：v1.0 / 2026-06-23
> 用途：Unit1 新增/修改道具与场景装饰的美术需求汇总

---

## 1. 《艾斯弗德先驱报》报纸（新增 · 环境叙事）

| 字段 | 内容 |
|------|------|
| 大图命名 | `SC9004_envir_ashford_herald_big` |
| 场景图命名 | `SC9004_envir_ashford_herald` |
| 放置场景 | 酒吧大堂（SC9004），Morrison 身边 |
| 出现时机 | L4 |

### 美术需求

参考版式：1928年《芝加哥论坛报》（Chicago Daily Tribune）宽幅大报

整体版式结构（从上至下）：

① 顶部耳版（左右各一个小方框，夹住报头）
- 左耳：天气预报栏，例：WEATHER — Rain likely, High 48°F
- 右耳：今日索引，例：Society P.4 / Finance P.6 / Sports P.8

② 报头（全宽通栏）
- 主报名：THE ASHFORD HERALD（黑体大型衬线字体，全宽居中）
- 副标：艾斯弗德先驱报（报名正下方，小字）
- 日期行（报头正下方横线内）：ASHFORD, FRIDAY, NOVEMBER 9, 1928 ✦ FINAL EDITION ✦ TWO CENTS

③ 头版主区（报头以下，八栏布局）

左侧主栏（跨4栏）— 头版主稿

标题（两层）：
MILLER FAMILY FOUNDATION DONATES $40,000
TO CITY HOSPITAL AND ORPHAN RELIEF

配图：西装男性半身照，黑白，面部模糊不可辨认，图说：
Charles Miller, junior member of the Miller family, was seen departing the foundation offices Thursday evening.（Miller家族年轻成员查尔斯·米勒于周四傍晚离开基金会办公室时被拍摄到。）

正文前三段（可读，仅供美术排版用，不必全放上去）：
ASHFORD, Nov. 9 — The Miller Family Charitable Foundation announced Thursday a donation of forty thousand dollars to the Ashford City Hospital and the Southside Orphan Relief Fund, in what foundation trustees described as "a commitment to the dignity and welfare of every Ashford citizen."
Charles Miller, speaking on behalf of the foundation, declined to appear in person but issued a written statement: "Our family has long believed that the strength of a city is measured not by its towers, but by how it tends to those who cannot tend to themselves."

右侧副栏（跨4栏）— 三条次要新闻叠排

次要新闻一（跨2栏）：
SACRED HEART HOSPITAL ANNOUNCES ADVANCES IN SURGICAL CARE
正文2–3行后模糊

次要新闻二（跨2栏）：
TIDEWATER REALTY CO. ACQUIRES THREE SOUTH DISTRICT PROPERTIES
正文2–3行后模糊

次要新闻三（跨4栏，横跨底部）：
WORLD'S FAIR OPENING DATE CONFIRMED; CITY PLANNING COMMITTEE RELEASES DISTRICT MAP
正文2–3行后模糊

美术参考（不影响推理）：
- 1928年美国宽幅大报（broadsheet）风格，黑白印刷，油墨略有晕染
- 四至五栏竖排布局，头版标题跨栏，内页板块标题字号明显大于正文
- 纸张泛黄，轻微折痕（曾被对折保存）
- 整体气质：《纽约时报》/《芝加哥论坛报》1920s版式，严肃大报，非小报

### 文案备注

头版主标题：
Miller家族基金会向市立医院及孤儿救助捐款4万美元

版面正文参考：
艾斯弗德，11月9日——Miller家族慈善基金会于周四宣布，向艾斯弗德市立医院及南区孤儿救助基金捐款四万美元。基金会受托人将此次捐助定性为"对每一位艾斯弗德市民之尊严与福祉的承诺"。
小Charles Miller代表基金会发言，本人未出席，而是发表了一份书面声明："我们家族长久以来坚信，一座城市的强大，衡量标准不在于它的高楼大厦，而在于它如何照料那些无力自顾的人。"

右侧副栏标题：
- 圣心医院宣布外科医疗技术取得新进展
- TideWater地产公司收购南区三处物业
- 世博会开幕日期确认；城市规划委员会发布分区地图

---

## 2. 弹壳大图（修改 · 道具 item）

| 字段 | 内容 |
|------|------|
| 大图命名 | 已有 |
| 场景图命名 | 已有 |
| 操作 | 修改现有资源 |

### 美术需求

修改内容：
1. 将弹壳刻印文字 "MILLER ARMS" 修改为 "TideWater ARMS"
2. 原拓印图（资源编号 SC9003_item_72）：玩家完成拓印动作后，系统显示的拓印纸图片需在拓印纸上附着原始弹壳轮廓（即纸张上同时可见弹壳底部圆形拓印痕迹 + "TideWater ARMS" 字样的铅笔拓印效果）

美术参考（不影响推理）：
- 弹壳材质：黄铜色，底部刻字清晰、具有金属光泽
- 拓印纸：白色薄纸，铅笔灰色拓印痕迹，有轻微手压纹
- 拓印图中弹壳轮廓与字样同步呈现，不单独裁切

---

## 3. 被撕毁的信纸（修改 · 道具 item）

| 字段 | 内容 |
|------|------|
| 大图命名 | `SC9003_item_torn_letter_big` |
| 场景图命名 | `SC9003_item_torn_letter` |
| 操作 | 原"被撕毁的合同"改为"一封被撕毁的信纸" |

### 美术需求

原道具"被撕毁的合同"修改为"一封被撕毁的信纸"，调整信息表达侧重点如下：

重点（信息表达必不可少）：
1. 信件性质：非正式合同，而是一封非常隐秘、不走明面的私信，无抬头、无正式格式
2. 保留信息（需可读）：■■■■, Proceed with the 'internal arrangement' within the establishment; remove the obstacle, and your troubles will disappear. — Whale（去执行那项"内部安排"；替我扫清障碍，你的麻烦也会一笔勾销。）
3. 收信/委托对象署名：在保留信息开头句子前出现的名字（■■■■），其内容被撕毁或被污渍覆盖，不可辨认
4. 删去原合同中的甲方"鲸鱼"署名、金额条款、正式委托条款等一切合同格式要素

美术参考（不影响推理）：
- 形态：信纸残片若干，拼合后约占原信纸的60–70%，撕裂边缘不规则
- 纸质：普通信纸，米白色，手写字迹（钢笔或铅笔均可）
- 场景背景：L3，后巷垃圾袋内 / 取出后摊铺在桌面拼合的状态即可
- 整体视觉传达：随意丢弃的废弃物，而非正式法律文书残片——脏旧感强，可有轻微水渍或折痕

---

## 4. Morrison 桌面酒杯（新增 · 场景装饰）

| 字段 | 内容 |
|------|------|
| 大图命名 | 无 |
| 场景图命名 | `SC9004_envir_morrison_whiskey_glass` |
| 放置场景 | 酒吧大堂 SC010_bg_BarLobby（SC9004） |
| 出现时机 | L3、L4 两次 Morrison 出场，酒杯始终置于其桌面 |

### 美术需求

重点（信息表达必不可少）：
1. 酒杯类型：厚底平底玻璃杯（Old Fashioned glass / rocks glass），1920s美国酒吧常见款式，杯身矮而宽，杯壁略厚
2. 酒液颜色：琥珀色至深金色（威士忌/波本），液面约在杯身三分之二处——暗示他已经喝了一些，但还没喝完
3. 杯内有两到三块冰块，边缘已开始融化，轮廓不再规整
4. 杯壁外侧有明显冷凝水珠，桌面接触处有一小圈水渍晕开的痕迹

美术参考（不影响推理）：
- 整体色调：暖琥珀色酒液 + 冰块的冷白透明，在昏暗的酒吧灯光下有轻微折射感
- 杯身无花纹，素面，但可见轻微手工吹制玻璃的不均匀感（年代质感）
