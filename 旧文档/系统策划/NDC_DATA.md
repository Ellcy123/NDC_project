# NDC_Datas

文件包含 12 个工作表

---

## Important

*此工作表为空*

---

## Chapter

| SectionrID   | SubChapterName   | ChapterID   | ChapterName   | OpeningCutscene   | EndingCutscene   | DataExposure   | Prerequisites   |
|:-------------|:-----------------|:------------|:--------------|:------------------|:-----------------|:---------------|:----------------|
| 子章节ID        | 子章节名称            | 主章节ID       | 主章节名称         | 开场动画              | 结束动画             | 对应指证           | 前置条件            |
| string       | string           | string      | string        | string            | string           | string         | array           |
| SEC01        | Rosa的谎言          | CH001       | 蓝月亮歌舞厅谋杀案     | CS001_Opening     | nan              | DAT002         | nan             |
| SEC02        | 嫁祸案件             | CH001       | 蓝月亮歌舞厅谋杀案     | nan               | nan              | nan            | nan             |

---

## Scene

| SceneID   | SceneName     | SceneChapter   | NULL            | SceneType   | BackgroundImage         | NPCIDs                  | AmbientSound   | BGMFile   | UnlockText   |
|:----------|:--------------|:---------------|:----------------|:------------|:------------------------|:------------------------|:---------------|:----------|:-------------|
| 场景ID      | 场景名称          | 场景隶属章节         | 备注              | 场景类型        | 背景图片                    | NPC列表                   | 环境音效           | 背景音乐      | 未解锁提示        |
| string    | string        | string         | nan             | enum        | string                  | array                   | string         | string    | string       |
| SC101     | Webb会客室       | SEC01          | 故事开篇场景WEBB死亡现场  | dialogue    | webb_meetingroom.jpg    | WEBB，MORRISON，ZACK      | nan            | nan       | nan          |
| SC102     | 歌舞厅外的街道       | SEC01          | 与EMMA对话场景       | dialogue    | outside.jpg             | EMMA,ZACK               | nan            | nan       | nan          |
| SC103     | Rosa的储藏室      | SEC01          | 搜证              | crime       | storeroom.jpg           | nan                     | nan            | nan       | nan          |
| SC104     | 歌舞厅一楼走廊       | SEC01          | 迷晕ZACK案发现场      | crime       | 1F_corridor.jpg         | nan                     | nan            | nan       | nan          |
| SC105     | TOMMY的办公室     | SEC01          | 跟TOMMY对话场景      | dialogue    | tommy_office.jpg        | TOMMY                   | nan            | nan       | nan          |
| SC106     | 酒吧大堂          | SEC01          | 跟ROSA对话场景       | dialogue    | hall.jpg                | ROSA                    | nan            | nan       | nan          |
| SC107     | Vivian的化妆室    | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC108     | Jimmy的厨房      | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC109     | Webb办公室       | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC110     | Jimmy的家中卧室    | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC111     | Jimmy的家中客厅    | SEC01          |                 | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC112     | 歌舞厅二楼走廊       | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC113     | Morrison家中客厅  | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC114     | Morrison的家中书房 | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC115     | Morrison警局    | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC116     | 厨房通道          | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC117     | 酒吧歌舞厅         | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | 这里还不能进入      |
| SC118     | Morrion家中外景   | SEC01          | nan             | noentry     | nan                     | nan                     | nan            | nan       | nan          |
| SC119     | Webb会客室-2     | SEC01          | WEBB死亡现场-Emma出场 | dialogue    | webb_meetingroom_02.jpg | WEBB，MORRISON，EMMA，ZACK | nan            | nan       | nan          |

---

## Role

| NPCID   | NPCName      | Type        | RoleIcon   | Portrait         | BgDescription      | UnlockCondition   | SelectedState   | Marked   | DialogueContent   | ExposeMessage        |
|:--------|:-------------|:------------|:-----------|:-----------------|:-------------------|:------------------|:----------------|:---------|:------------------|:---------------------|
| NPCID编号 | NPC姓名        | 用户角色        | 头像图片       | 头像               | 背景简述               | 解锁条件              | 选中状态            | 标记       | 对话内容              | 指正内容                 |
| string  | string       | enum        | string     | string           | string             | string            | int             | int      | string            | string               |
| NPC001  | Webb         | victim      | nan        | nan              | 蓝月亮歌舞厅老板，涉嫌洗钱      | nan               | 1               | 1        | D011,D006         | DAT001               |
| NPC002  | Rosa         | suspect     | nan        | note_rosa        | 50岁的清洁工            | nan               | 0               | 1        | D001,D003         | DAT002,DAT003,DAT004 |
| NPC003  | Tommy        | suspect     | nan        | note_tommy       | 45岁的酒吧经理           | EVE001            | 1               | 0        | D004,D005         | DAT006,DAT007,DAT008 |
| NPC004  | Morrison     | suspect     | nan        | note_morrison    | 芝加哥警局的警探，负责处理这起谋杀案 | EVE002            | 1               | 1        | D007,D008         | DAT009               |
| NPC005  | Anna         | suspect     | nan        | note_anna        | 我是Anna             | nan               | nan             | nan      | nan               | nan                  |
| NPC006  | Jimmy        | suspect     | nan        | note_jimmy       | 我是Jimmy            | nan               | nan             | nan      | nan               | nan                  |
| NPC007  | Mrs.Morrison | suspect     | nan        | note_mrsmorrison | 我是Mrs.Morrison     | nan               | nan             | nan      | nan               | nan                  |
| NPC008  | Vivian       | suspect     | nan        | note_vivan       | nan                | nan               | nan             | nan      | nan               | nan                  |
| NPC009  | Zack         | protagonist | nan        | note_vivan       | 我是主人公              | EVE003            | nan             | nan      | nan               | nan                  |
| NPC010  | Emma         | protagonist | nan        | note_vivan       | 我是记者               | nan               | nan             | nan      | nan               | nan                  |

---

## Investgate_Expose_Message

| DataID   | ChapterID   | NPCID   | NPCName   | NPCType   | NPCData                             | EvidenceID               | IfExpose   | ExposedData   |
|:---------|:------------|:--------|:----------|:----------|:------------------------------------|:-------------------------|:-----------|:--------------|
| 信息ID     | 章节ID        | NPC ID  | NPC姓名     | NPC类型     | NPC信息                               | 对应指证道具 IDs（每个阶段可能对应三个道具） | 是否用于指证     | 指证后信息         |
| string   | string      | string  | string    | enum      | string                              | array                    | bool       | string        |
| DAT001   | CH001       | NPC001  | Webb      | VICTIM    | nan                                 | nan                      | False      | nan           |
| DAT002   | CH001       | NPC002  | Rosa      | SUSPECT   | 当天晚上我被TOMMY经理安排了工作                  | nan                      | False      | nan           |
| DAT003   | CH001       | NPC002  | Rosa      | SUSPECT   | 于是我一直在地下室酒窖清理，整理酒瓶和架子               | EV001,EV003,EV004        | True       | aaaa          |
| DAT004   | CH001       | NPC002  | Rosa      | SUSPECT   | 我没有听到任何的脚步声                         | nan                      | False      | nan           |
| DAT006   | CH001       | NPC003  | Tommy     | SUSPECT   | 案发当晚大概11点多，我看到一个警察从侧门异常进入，直接往后台办公室走 | nan                      | False      | nan           |
| DAT007   | CH001       | NPC003  | Tommy     | SUSPECT   | 我听到后台有重物拖拽的声音                       | nan                      | False      | nan           |
| DAT008   | CH001       | NPC003  | Tommy     | SUSPECT   | 按工作安排，Rosa当晚应该在后台走廊清洁               | nan                      | False      | nan           |
| DAT009   | CH001       | NPC004  | Morrison  | SUSPECT   | 我得到报案后立刻赶往现场，发现死亡的WEBB和持枪的ZACK      | nan                      | False      | nan           |

---

## Evidence

| EvidenceID   | EvidenceName   | EvidenceType   | RelatedSceneID   | SectionId   | Icon               | DetailImage        | Description                                                             | RelatedNPCIDs   | AnalysisRequired   | AnalysisResult                         | CombinatableFrom   | TriggerEvent    | DisplayAfterGot   |
|:-------------|:---------------|:---------------|:-----------------|:------------|:-------------------|:-------------------|:------------------------------------------------------------------------|:----------------|:-------------------|:---------------------------------------|:-------------------|:----------------|:------------------|
| 证据编号         | 证据名称           | 证据类型           | 相关场景             | 所属子章节       | 图标                 | 详细图片               | 描述                                                                      | 相关NPC           | 需要分析               | 分析后描述                                  | 组合来源对象             | 触发事件            | 场景搜证后显示图标（探索场景）   |
| string       | string         | string         | string           | string      | string             | string             | string                                                                  | string          | string             | string                                 | string             | int             | string            |
| EV001        | 工作记录卡          | item           | SC103            | SEC01       | nan                | nan                | "Rosa Martinez - 11月15日夜班：后台走廊清洁 23:00-01:00"                           | NPC002          | 0                  | nan                                    | nan                | nan             | clear             |
| EV002        | 空氯仿瓶           | item           | SC104            | SEC01       | nan                | nan                | 芝加哥总医院麻醉科标签，瓶口有残留气味                                                     | NPC002          | 0                  | nan                                    | nan                | nan             | clear             |
| EV003        | 毛巾             | item           | SC103            | SEC01       | nan                | nan                | 白色毛巾                                                                    | NPC002          | 1                  | 一条白色毛巾，散发着刺鼻的甜腻气味，毛巾上有明显的使用痕迹          | nan                | nan             | clear             |
| EV004        | 地板拖拽痕迹         | clue           | SC104            | SEC01       | nan                | nan                | 地毯拖拽痕迹，从走廊尽头到Webb办公室                                                    | NPC002          | 1                  | 痕迹宽度约为肩宽，深度表明被拖拽物体重量至少150磅，绝非普通清洁工具能造成 | nan                | nan             | clear             |
| EV005        | TOMMY的证词       | note           | SC105            | SEC01       | nan                | nan                | 11点多有人影从侧门进来                                                            | NPC003          | 0                  | nan                                    | nan                | nan             | clear             |
| EV006        | TOMMY的证词       | note           | SC105            | SEC01       | nan                | nan                | 听到后台有重物拖拽的声音                                                            | NPC003          | 0                  | nan                                    | nan                | nan             | clear             |
| EV007        | 医疗账单           | environment    | SC103            | SEC01       | medicalrecords.png | medicalrecords.png | 一张芝加哥总医院的账单显示"患者：Miguel Martinez，哮喘治疗费用：50美元/月"，账单底部盖着红色印章"逾期未付-已停止治疗"。 | NPC002          | 0                  | nan                                    | nan                | EV007_Collected | clear             |
| EV008        | 随便配的合并线索1      | item           | SC103            | SEC01       | nan                | nan                | 随便配的合并线索1                                                               | NPC002          | 0                  | nan                                    | nan                | nan             | clear             |
| EV009        | 随便配的合并线索2      | item           | SC103            | SEC01       | nan                | nan                | 随便配的合并线索2                                                               | NPC002          | 0                  | nan                                    | nan                | nan             | clear             |
| EV010        | 合并后的线索         | item           | SC103            | SEC01       | nan                | nan                | 合并后的线索                                                                  | NPC002          | 0                  | nan                                    | EV008,EV009        | nan             | nan               |

---

##  Dialog

| DialogueID   | SceneID   | NPC      | DialogueType   | Icon   | CharacterPortrait   | FrontContent   | NPCTalk   | Content                                                           | Options        | IsEnd   | VoiceFile   | ExtractHighlight   | NextContent   | TriggerEvent   |
|:-------------|:----------|:---------|:---------------|:-------|:--------------------|:---------------|:----------|:------------------------------------------------------------------|:---------------|:--------|:------------|:-------------------|:--------------|:---------------|
| 对话ID         | 场景ID      | NPC      | 对话类型           | 人物资源   | 角色立绘表情              | 前置对话ID         | 说话人ID     | 对话内容                                                              | 回答选项           | 是否为结束   | 语音文件        | 被提取证词IDs           | 后置对话ID        | 触发事件           |
| string       | string    | nan      | string         | string | string              | string         | string    | string                                                            | string         | string  | string      | string             | string        | string         |
| D001         | SC101     | Morrison | AVG            | nan    | nan                 | nan            | NPC004    | 芝加哥警局！放下武器！Webb死了，你就是凶手！                                          | nan            | 0       | nan         | nan                | D002          | nan            |
| D002         | SC101     | Zack     | AVG            | nan    | nan                 | D001           | NPC009    | nan                                                               | D003,D004,D005 | 0       | nan         | nan                | nan           | nan            |
| D003         | SC101     | Zack     | AVG            | nan    | nan                 | nan            | NPC009    | 等等！我是私家侦探Zack Brennan...Webb约我来谈事情...                             | nan            | 0       | nan         | nan                | D006          | nan            |
| D004         | SC101     | Zack     | AVG            | nan    | nan                 | nan            | NPC009    | 我不知道发生了什么，但我绝对没有杀人！                                               | nan            | 0       | nan         | EV005              | D007          | nan            |
| D005         | SC101     | Zack     | AVG            | nan    | nan                 | nan            | NPC009    | 这一定是陷阱！有人想要陷害我！                                                   | nan            | 0       | nan         | EV006              | D008          | nan            |
| D006         | SC101     | Morrison | AVG            | nan    | nan                 | D003           | NPC004    | 私家侦探？你有什么证据证明Webb约你来？                                             | nan            | 0       | nan         | nan                | D009          | nan            |
| D007         | SC101     | Morrison | AVG            | nan    | nan                 | D004           | NPC004    | 不知道？那你手里的枪怎么解释？                                                   | nan            | 0       | nan         | nan                | D009          | nan            |
| D008         | SC101     | Morrison | AVG            | nan    | nan                 | D005           | NPC004    | 陷阱？是你自己心虚才这么说！                                                    | nan            | 0       | nan         | nan                | D009          | nan            |
| D009         | SC101     | Morrison | AVG            | nan    | nan                 | D006,D007,D008 | NPC004    | 证据确凿，逮捕他！                                                         | nan            | 0       | nan         | nan                | D010          | nan            |
| D010         | SC119     | Emma     | AVG            | nan    | nan                 | D009           | NPC010    | 慢着！这个人不是凶手！                                                       | nan            | 0       | nan         | nan                | D011          | nan            |
| D011         | SC119     | Morrison | AVG            | nan    | nan                 | D010           | NPC004    | 你是谁？                                                              | nan            | 0       | nan         | nan                | D012          | nan            |
| D012         | SC119     | Emma     | AVG            | nan    | nan                 | D011           | NPC010    | 《芝加哥先驱报》记者Emma O'Malley。我看到真凶从逃跑了！12点30分，一个黑衣男子离开现场！              | nan            | 0       | nan         | nan                | D013          | nan            |
| D013         | SC119     | Morrison | AVG            | nan    | nan                 | D012           | NPC004    | 你有什么证据？                                                           | nan            | 0       | nan         | nan                | D014          | nan            |
| D014         | SC119     | Emma     | AVG            | nan    | nan                 | D013           | NPC010    | 我拍到了黑衣人的背影！                                                       | nan            | 0       | nan         | nan                | D015          | nan            |
| D015         | SC119     | Emma     | AVG            | nan    | nan                 | D014           | NPC010    | Morrison警探，您来得太及时了。从案发到现场不到10分钟，除非您早知道会发生什么？                      | nan            | 0       | nan         | nan                | D016          | nan            |
| D016         | SC119     | Morrison | AVG            | nan    | nan                 | D015           | NPC004    | 我接到匿名电话...                                                        | nan            | 0       | nan         | nan                | D017          | nan            |
| D017         | SC119     | Emma     | AVG            | nan    | nan                 | D016           | NPC010    | 那为什么不先调查现场，而是直接认定Brennan是凶手？                                      | nan            | 0       | nan         | nan                | D018          | nan            |
| D018         | SC119     | Morrison | AVG            | nan    | nan                 | D017           | NPC004    | 好吧...事情比我想象的复杂。但Brennan，别以为这样就能洗清嫌疑。                              | nan            | 0       | nan         | nan                | D019          | nan            |
| D019         | SC119     | Morrison | AVG            | nan    | nan                 | D018           | NPC004    | 我给你们三天时间。找不到真凶，我就逮捕你，Brennan。O'Malley，妨碍司法的罪名够你受的。                | nan            | 0       | nan         | nan                | D020          | nan            |
| D020         | SC119     | Morrison | AVG            | nan    | nan                 | D019           | NPC004    | 三天，72小时。时间一到，我亲自给你戴手铐！                                            | nan            | 0       | nan         | nan                | D021          | nan            |
| D021         | SC119     | Morrison | AVG            | nan    | nan                 | D020           | NPC004    | 祈祷你们能找到那个黑衣人吧，否则Webb的死就算在你头上！                                     | nan            | 1       | nan         | nan                | D022          | nan            |
| D022         | SC102     | Zack     | AVG            | nan    | nan                 | D021           | NPC009    | 谢谢你救了我。但我需要知道，你真的拍到了那个黑衣人吗？                                       | nan            | 0       | nan         | nan                | D023          | nan            |
| D023         | SC102     | Emma     | AVG            | nan    | nan                 | D022           | NPC010    | 我确实看到有人离开，也拍了照片。但说实话，照片很模糊，可能不足以在法庭上作为证据。不过足以让Morrison产生怀疑了。      | nan            | 0       | nan         | nan                | D024          | nan            |
| D024         | SC102     | Zack     | AVG            | nan    | nan                 | D023           | NPC009    | 你为什么要救我？我们素不相识。                                                   | nan            | 0       | nan         | nan                | D025          | nan            |
| D025         | SC102     | Emma     | AVG            | nan    | nan                 | D024           | NPC010    | 因为我也在调查Webb的生意。几个月来，我一直怀疑他在进行某种非法活动。今晚我来这里就是想找到证据，没想到遇到了谋杀案。      | nan            | 0       | nan         | nan                | D026          | nan            |
| D026         | SC102     | Zack     | AVG            | nan    | nan                 | D025           | NPC009    | 那你觉得是谁杀了Webb？                                                     | nan            | 0       | nan         | nan                | D027          | nan            |
| D027         | SC102     | Emma     | AVG            | nan    | nan                 | D026           | NPC010    | 不知道，但我敢肯定不是你。一个真正的杀手不会让自己陷入这么明显的陷阱。而且...Morrison的反应很奇怪。他太急于给你定罪了。 | nan            | 0       | nan         | nan                | D028          | nan            |
| D028         | SC102     | Zack     | AVG            | nan    | nan                 | D027           | NPC009    | 我也注意到了。一个正常的警探会先调查所有可能性，但他从一开始就咬定是我。                              | nan            | 0       | nan         | nan                | D029          | nan            |
| D029         | SC102     | Emma     | AVG            | nan    | nan                 | D028           | NPC010    | 这说明要么他知道内情，要么他在掩盖什么。不管怎样，我们都需要找出真相。                               | nan            | 0       | nan         | nan                | D030          | nan            |
| D030         | SC102     | Zack     | AVG            | nan    | nan                 | D029           | NPC009    | nan                                                               | D031,D032,D033 | 0       | nan         | nan                | nan           | nan            |
| D031         | SC102     | Zack     | AVG            | nan    | nan                 | nan            | NPC009    | 你说得对，但我们要怎么找出真相？                                                  | nan            | 0       | nan         | nan                | D034          | nan            |
| D032         | SC102     | Zack     | AVG            | nan    | nan                 | nan            | NPC009    | 听起来你想和我合作调查这个案子？                                                  | nan            | 0       | nan         | nan                | D035          | nan            |
| D033         | SC102     | Zack     | AVG            | nan    | nan                 | nan            | NPC009    | 我同意，但这很危险，我们要小心行事                                                 | nan            | 0       | nan         | nan                | D036          | nan            |
| D034         | SC102     | Emma     | AVG            | nan    | nan                 | D031           | NPC010    | 我想我们应该合作。你是专业侦探，我有记者的资源和渠道。而且现在我们都在Morrison的怀疑名单上了。               | nan            | 0       | nan         | nan                | D037          | nan            |
| D035         | SC102     | Emma     | AVG            | nan    | nan                 | D032           | NPC010    | 是的，我认为我们应该合作。你是专业侦探，我有记者的资源，单独行动对我们都不利。                           | nan            | 0       | nan         | nan                | D037          | nan            |
| D036         | SC102     | Emma     | AVG            | nan    | nan                 | D033           | NPC010    | 确实危险，但正因如此我们更需要合作。我们现在都在Morrison的怀疑名单上，必须联手才能自保。                  | nan            | 0       | nan         | nan                | D037          | nan            |
| D037         | SC102     | Zack     | AVG            | nan    | nan                 | D034,D035,D036 | NPC009    | nan                                                               | D038,D039,D040 | 0       | nan         | nan                | nan           | nan            |
| D038         | SC102     | Zack     | AVG            | nan    | nan                 | nan            | NPC009    | 好吧。但我们需要制定规则——所有发现都要分享，谁也不能背叛谁                                    | nan            | 0       | nan         | nan                | D041          | nan            |
| D039         | SC102     | Zack     | AVG            | nan    | nan                 | nan            | NPC009    | 那我们先确认一下彼此的目标和底线                                                  | nan            | 0       | nan         | nan                | D042          | nan            |
| D040         | SC102     | Zack     | AVG            | nan    | nan                 | nan            | NPC009    | 既然如此，我们就是一条船上的人了                                                  | nan            | 0       | nan         | nan                | D044          | nan            |
| D041         | SC102     | Emma     | AVG            | nan    | nan                 | D038           | NPC010    | 当然，完全透明。成交。                                                       | nan            | 0       | nan         | nan                | D045          | nan            |
| D042         | SC102     | Emma     | AVG            | nan    | nan                 | D039           | NPC010    | 我的目标是找出真相，底线是不伤害无辜的人。你呢？                                          | nan            | 0       | nan         | nan                | D043          | nan            |
| D043         | SC102     | Zack     | AVG            | nan    | nan                 | D042           | NPC009    | 我的目标是洗清嫌疑，底线同样是保护无辜。看来我们能合作。                                      | nan            | 0       | nan         | nan                | D045          | nan            |
| D044         | SC102     | Emma     | AVG            | nan    | nan                 | D040           | NPC010    | 没错，现在我们要共同面对这个困境。                                                 | nan            | 0       | nan         | nan                | D045          | nan            |
| D045         | SC102     | Emma     | AVG            | nan    | nan                 | D041,D043,D044 | NPC010    | 成交。我们先回歌舞厅调查一下，看看有没有什么线索。                                         | nan            | 1       | nan         | nan                | nan           | nan            |

---

##  Event

| EventID   | TriggerCondition                 | NULL           | UnlockContent   | UnlockDialog   | IfInterrupt   | UnlockText   |
|:----------|:---------------------------------|:---------------|:----------------|:---------------|:--------------|:-------------|
| 事件ID      | 触发条件                             | 解锁条件备注         | 解锁场景            | 解锁对话           | 是否为打断式的       | 解锁tips文本     |
| string    | string                           | nan            | array           | array          | int           | string       |
| EVE001    | DLG003_Collected,EV007_Collected | 当证据毛巾被解锁,且对话解锁 | SC002           | D044           | 0             | XX场景已解锁      |
| EVE002    | DLG004_Collected                 | 当对话被解锁         | SC002           | nan            | 0             | XX场景已解锁      |
| EVE003    | DLG005_Collected                 | 当对话被解锁         | SC002           | nan            | 0             | XX场景已解锁      |

---

##  Task

| ID     | TaskText          | SecId   | TaskType   | TriggerCondition   | NULL   | CompleteCondition   | NULL.1   |
|:-------|:------------------|:--------|:-----------|:-------------------|:-------|:--------------------|:---------|
| 任务ID   | 任务内容              | 子章节ID   | 任务类型       | 触发条件               | 触发条件备注 | 完成条件                | 完成条件备注   |
| string | string            | string  | string     | string             | nan    | string              | nan      |
| TAS001 | 到底是谁把我迷晕了？        | SEC01   | Main       | nan                | nan    | nan                 | nan      |
| TAS002 | Morrison警官迷晕我的证据？ | SEC02   | Main       | nan                | nan    | nan                 | nan      |
| TAS003 | 任务                | SEC02   | Goal       | nan                | nan    | EVE002              | nan      |
| TAS004 | 任务                | SEC02   | Side       | EVE001             | nan    | EVE002              | nan      |

---

## Relationship

| NPCID   | ToNPCID    | LineToLineMessage   |
|:--------|:-----------|:--------------------|
| NPCID编号 | 连线终点 NPCID | 连线之间的描述内容           |
| string  | string     | string              |
| NPC001  | NPC002     | 朋友关系                |
| NPC001  | NPC003     | 生意关系                |
| NPC001  | NPC004     | 生意关系                |
| NPC001  | NPC005     | 生意关系                |
| NPC001  | NPC006     | 上下级关系               |
| NPC002  | NPC003     | nan                 |
| NPC003  | NPC004     | nan                 |
| NPC005  | NPC002     | nan                 |

---

## Timeline

| 时间线ID   | 所属章节      | 解锁事件        | 所属NPC   | 起始时间                | 结束时间                | 时间线详情       |
|:--------|:----------|:------------|:--------|:--------------------|:--------------------|:------------|
| TimeID  | ChapterID | UnlockEvent | NPCID   | StartTime           | EndTime             | TimeDetails |
| string  | string    | string      | string  | string              | string              | string      |
| TIM001  | CH001     | EVE002      | NPC001  | 1925/11/03-23:00:00 | 1925/11/03-23:10:00 | 在餐厅吃饭       |
| TIM002  | CH001     | EVE003      | NPC001  | 1925/11/03-23:20:00 | 1925/11/03-23:25:00 | 在化妆间化妆      |

---

## Scene-资产

| SceneChapter   | SceneID   |   所属循环 | SceneName     | Type      | NPCIDs   | BackgroundImage   | Unnamed: 7   | Unnamed: 8   | Unnamed: 9   | AmbientSound   | BGMFile   |
|:---------------|:----------|-------:|:--------------|:----------|:---------|:------------------|:-------------|:-------------|:-------------|:---------------|:----------|
| 场景隶属章节         | 场景ID      |    nan | 场景名称          | 对话场景/探索场景 | NPC列表    | 背景图片              | 场景道具         | 二级探索场景背景     | 二级探索场景道具     | 环境音效           | 背景音乐      |
| string         | string    |    nan | string        | array     | array    | string            | nan          | nan          | nan          | string         | string    |
| SEC01          | SC101     |    nan | Webb会客室       | 对话        | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| nan            | nan       |    nan | Webb会客室       | 探索        | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC102     |    nan | 歌舞厅外的街道       | 对话        | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC103     |    nan | Rosa的储藏室      | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| nan            | nan       |    nan | 地下室走廊         | 探索        | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC104     |    nan | 歌舞厅一楼走廊       | 探索        | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC105     |    nan | TOMMY的办公室     | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC106     |    nan | 酒吧大堂          | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC107     |    nan | Vivian的化妆室    | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC108     |    nan | Jimmy的厨房      | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC109     |    nan | Webb办公室       | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC110     |    nan | Jimmy的家中卧室    | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC111     |    nan | Jimmy的家中客厅    | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC112     |    nan | 歌舞厅二楼走廊       | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC113     |    nan | Morrison家中客厅  | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC114     |    nan | Morrison的家中书房 | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC115     |    nan | Morrison警局    | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC116     |    nan | 厨房通道          | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC117     |    nan | 酒吧歌舞厅         | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |
| SEC01          | SC118     |    nan | Morrion家中外景   | 对话,探索     | nan      | nan               | nan          | nan          | nan          | nan            | nan       |

---