---
name: ndc-coordinate-image-edit
description: Perform bounded NDC raster cleanup, replacement and structural repair with exact coordinates, protected pixels, seam checks and a final zero-drift audit. Use for localized removal, material repair, authorized evidence insertion or grid/line alignment; route broad same-scene state changes to ndc-scene-state-variation.
---

# NDC Coordinate Image Edit

## Photoshop MCP 强制前置

本 Skill 第一次实际调用 Photoshop MCP 前，必须完整读取当前环境的《PS MCP 操作参考手册》：维护工作区从项目根解析 `PS_MCP_操作参考手册.md`，工程镜像从仓库根解析 `production/art_pipeline/PS_MCP_操作参考手册.md`。在当前编辑作业记录中保存实际手册路径、版本、SHA-256 和当前会话能力快照；两处均不存在或哈希不一致时不得以历史记忆继续操作。手册负责通用效率、蒙版、路径、单引擎、超时回退和视觉/技术验收；本 Skill 的授权坐标、保护像素、零漂移和修复范围继续优先。实时目录只允许执行 supported 能力，手册本身不增加操作授权。

执行前读[对话任务独立额度](references/task-budget.md)：新对话完整新额度，其他对话的资产历史不扣减；已授权工作直接推进，不索要例行答复。此用户最新规则优先于旧预算说明。

实际使用原生 Photoshop MCP 前，确认 Bridge 已连接及所需命令可用，并协调本机同一时刻只有一个任务操作 Photoshop；不再调用排队或租约接口。同任务当前图须保存、完成技术及真实视觉检查并核对当前hash；未审完不得推进下一张。PASS可推进相应依赖；FAIL缺陷已记录且预算耗尽或用户要求封存时，保留候选和累计次数，仅继续独立资产；安全保存可恢复文件和固定审阅快照后，可安全交棒给其他独立任务。释放不是PASS，不解除原图及依赖的阻断、不重置预算；命令在途或结果未知时不得自行交棒。纯准备、生图等待和离线审阅不长期占用桥接，未授权的PS操作不会因连接可用而获得授权。

局部修图保留原图、坐标和授权区外像素。本 Skill 只交付调用者要求的局部修图结果；不默认制作道具母版、容器菜单、Map/Big/Icon 或工程热区。大范围同场景状态转换使用 [ndc-scene-state-variation](../ndc-scene-state-variation/SKILL.md)，整体状态成立后才回到这里修小范围缺陷。

## 开始与续接

1. 查验当前资产及批准来源，确认本次是否已有满足同一修改目标的已接受输出。已有结果按 [production-record.md](references/production-record.md) 检查当前字节、源图/父图、用途、要求和拒收状态；只有哈希相同不足以复用。明确要求重新修改时执行当前任务。
2. 锁定原始源图、实际修改目标、保护元素和合法编辑范围。需求可由当前授权及项目材料可靠确定时直接进入制作，不新增前后图或逐候选确认。
3. 在项目 `工作过程文件` 下建立或恢复同一作业目录；候选、蒙版、提示、manifest、审核和失败原因长期留在此处，不在系统临时目录开展项目生产，不随发布删除历史。
4. 使用 [scripts/coordinate_patch.py](scripts/coordinate_patch.py) 及其现有 manifest/命令；详见 [坐标作业操作](references/coordinate-job-mechanics.md)。旧 `scan-seam` / `repair-vertical-seam` 仅兼容旧记录，不用于新作业。

## 预算与故障处理

独立修图按同一资产、原始源图和已授权修改目标建立稳定生产 job，默认最多 **3 次实际生成，含首次**。子蒙版、区域、修补阶段、换位置、换目录或恢复任务都使用这个 job 的剩余次数，不能重置。每次提交前依 [production-record.md](references/production-record.md) 保留尝试，实际提交文本、候选、结果和拒收原因随即归档；不确定是否生成时先核对现存结果，不能直接重发。

已有候选的确定性配准、重合成、蒙版调整、授权内结构桥和核验不消耗生成次数，也不产生新额度。接受首张全部适用门禁通过的结果。第三次仍失败就保留未解决状态和历史，继续其他独立资产；不以新阶段/位置名启动第四次。继续同一失败任务不等于新预算；真正的新对话自动使用完整新额度，不询问追加次数；用户主动改变当前范围/次数时记录变更。

父生产 Skill 调用时继承父 job 的剩余预算，不额外开本 Skill 的 3 次。带 `ndc-prop-batch/v1` 的道具插入沿用原道具日志，详见 [道具适配](references/prop-adapter.md)，不双重计数。其他道具职责留给对应阶段 Skill。

## 图像与权限不变量

- 原图不覆盖。矩形使用已记录左上原点及半开区间 `[left,right)`、`[top,bottom)`。独立编辑按序合成：每步来源为上一步接受的全尺寸结果，最终仍对比最初原图。
- 去除/修复蒙版限于对象或结构组，覆盖投影、发光、残片与重建所需区域，同时排除受保护结构。羽化只向内；硬蒙版外每个像素必须与该步源图一致。
- 道具插入先读 [道具适配](references/prop-adapter.md) 的 3 倍/128px 父工作区和 64px 最终合成留边，不能把插入物的轮廓当作父授权区。
- 生成裁切优先采用足够真实上下文的 1024×1024；两边须为 16 的倍数，每边不超过 3840，长宽比不超过 3:1，总像素 655,360–8,294,400。通过扩大真实原图上下文满足限制，不缩放目标区域。
- 返回候选必须与准备裁切保持完全相同长宽比；不拉伸或居中裁切来伪装符合。最终 PNG 与原图尺寸和模式相同，所有已确认父蒙版并集外字节一致。
- 图像生成使用已授权原生工具及真实本地参考。编写实际输入时协作 [ndc-visual-description](../ndc-visual-description/SKILL.md)，在方案形成与最终输入就绪时核对可见变化和保持项；相同输入不重复创作分析。
- 保留项目的 Photoshop MCP 权限与同任务单图验收要求，跨任务桥接占用按上方全局队列管理。本 Skill 既有坐标/蒙版/验证辅助命令不授权用其他工具替代项目明确要求 Photoshop 完成的抠图、Alpha、变换或导出，也不授权扩大编辑范围。

## 按变化审核，当前接受链交付

源图/蒙版接受、每个新候选、像素重合成、结构修复及最终修图结果都必须实际检查对应风险。整图看授权目标、受保护上下文与整体融合，原像素或最近邻 200% 看受影响局部和边界；必要的完整覆盖规则继续有效。记录结构/残留、透视/尺度/接触、阴影/风格/纹理、边缘和任务确实要求的文字/可读性，不能强加不存在的道具输出角色。

每个当前新图或实质改变的验收合同须有 `ndc-stage-visual-self-check/v1`（或兼容的 `visual_review.json`），绑定阶段、审核人/日期、输入输出路径与 SHA-256、实际看过的整图/局部证据、适用检查项及具体 PASS/FAIL/NOT_CHECKED、返工归属。技术报告、尺寸、哈希、包含/接缝扫描不能自动写视觉 PASS。运行项目既有 `validate-ndc-stage-visual-self-check.py --record <record> --artifact <output>` 校验记录；未通过的当前输出不得下传。

选择、同字节复制与发布可依 [production-record.md](references/production-record.md) 引用有效旧审核：来源/父图、用途、要求、审核范围及拒收状态都须仍匹配。实质变化只失效受影响项及其依赖，像素变化仍执行其技术核验、局部新增风险及整体上下文复核，不能用哈希替代看图。

终验对最初原图执行授权蒙版并集零漂移、完整 manifest 顺序链及当前哈希匹配的边界/结构报告。当前接受依赖链和请求交付文件必须通过；被拒收或废弃候选保留 FAIL 历史，既不要求其改成 PASS，也不得作为接受链输入。父流程要求 `final_visual_record_presence_gate.json` 时只枚举当前接受链与实际交付角色；同一份兼容视觉记录可满足阶段和终验绑定，无须重造艺术结论。

只把本次请求的接受 PNG 交回调用者的正式路径，所有过程证据留在 `工作过程文件`。独立场景修图没有隐含父道具发布、XYposition、容器菜单或失败历史清理步骤。
