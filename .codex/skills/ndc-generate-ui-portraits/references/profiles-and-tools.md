# 双规格对齐与工具

## 原版辅助线

辅助线资产在 `assets/guides/`，示意图在同目录；仅用于审核叠图，不进入正式PNG。全部从源目录逐字节复制。

| Profile | 颜色/语义 | 非透明主要色线覆盖行（包含端点） | 中心 |
|---|---|---|---|
| big | 红/头顶软参考 | 6–9 | 7.5 |
| big | 绿/眼睛 | 105–107 | 106 |
| big | 黄/下巴 | 191–194 | 192.5 |
| small | 红/眼睛 | 51–52 | 51.5 |
| small | 绿/下巴 | 108–109 | 108.5 |

实测来自原始RGBA辅助线PNG，不来自对示意人物的自动识别。测量定义和原图hash保存在 `assets/profiles.json`。最后由实际叠图检查，不能只根据标注代数自证脸部对齐。

## 标注

标注必须指向冻结母图原生坐标。眼睛选可见两眼瞳孔/眼裂中心，下巴选肉体下颌底，不用胡须尖、领口、帽檐或眉毛替代。阴影严重到无法可靠识别时返回母图审查。`face_center_x` 默认取双眼中点，若视觉居中需要偏移可填真实核对的中心x，并记录理由；不要将整个含背景画布居中等同于人脸居中。

标注 JSON 示例（坐标仅为格式示例，不能照抄用于真实角色）：

```json
{
  "source_sha256": "此处填真实母图SHA-256",
  "left_eye": [410, 450],
  "right_eye": [490, 450],
  "chin": [450, 750],
  "face_center_x": 450,
  "reviewer": "实际标注者",
  "note": "真实眼部和下巴坐标的核对依据"
}
```

设母图眼中点纵坐标 `ye`、下巴 `yc`，目标为 `Ye,Yc`，则 `s=(Yc-Ye)/(yc-ye)`、`ty=Ye-s*ye`；水平平移把已审查的人脸中心放到画布中心。反算源裁切框 `[left, top, left+W/s, top+H/s]`，用 `Image.resize(size, box=..., resample=LANCZOS)` 从母图单次重采样。允许正常像素取整，不允许非等比拉伸强行满足第三条头顶线。

## 执行

依赖：Python 3.10+，Pillow。运行前解析本机批准的Python环境；不要把安装目录写入团队Skill。Pillow是现成图像接口，不需要另造缩放算法。

从本 Skill 根运行（输出必须是新的过程目录）：

```text
python -B scripts/ui_portrait.py compose --input <master.png> --landmarks <landmarks.json> --stem <角色正式stem> --output-dir <新的过程目录>
python -B scripts/ui_portrait.py compose --input <master.png> --landmarks <landmarks.json> --stem <角色正式stem> --profile small --output-dir <仅补small的新过程目录>
python -B scripts/ui_portrait.py audit --receipt <过程目录/composition.json>
```

默认生成 big/small 两版；`--profile big` 或 `--profile small` 仅生成所选一版。每个所选规格附辅助线叠图和最近邻200%图，整图100%直接看输出本身。回执 `requested_profiles` 明示本次范围，各候选裁切参数及母图/标注/输出hash写入 `composition.json`。全部所选规格先预检再写文件；默认双版中任一计算失败都不先落盘另一版。技术审计重读原图和标注，仅重算回执声明的规格，不产生艺术批准，也不把单版技术通过当成双版交付完整。没有 `requested_profiles` 的旧 v1 回执仍要求 big/small 两版。

工具拒绝：非3:4母图、透明/无效输入、过期标注hash、非法点位、下巴不在眼下、上采样、越界裁切、危险文件名、覆盖已有输出、输出嵌套在Skill/已识别工程/只读源目录。工具不会改Alpha、修脸、自动判断表情或无白边；若需要Photoshop操作，仅走当前允许的MCP通道并读 [全局队列](../../ndc-photoshop-queue/SKILL.md)。同任务逐张保存并完成真实审核；PASS才推进相应依赖，FAIL按全局队列有据封存后仅继续独立资产；可恢复保存及固定审阅快照后的跨任务挂起释放不改变本图状态或配套big/small依赖，离线裁切工具本身不占PS。

失败路由：标注错误重新人工标注；几何越界或有效脸部像素不足回到母图输入重生；艺术通过但最后技术裁切错位，只从同一冻结母图重裁两版中的受影响版本。若只是做单版返修，保留另一版当前通过记录，不把失败候选覆盖旧成品。

审核完才能归档。单版回执与已通过的另一版回执共同进入完整交付清单，并核对身份与共享母图来源。对纯历史复用不得虚构母图关系。单版技术通过不允许覆盖另一版；完整任务的 big/small 覆盖仍由最终交付清单逐项检查。

跨任务 U1→U2/U3 交接只按 [UI 交接契约](../../ndc-art-stage-pipeline/references/ui-pipeline.md) 执行。领取、工作前和回收重验同一母图的当前接收绑定；新标注、回执和候选放入领取分配的独占工作目录，`compose` 使用其中尚不存在的子目录。实际母图继续引用原路径；既有另一版及旧回执不复制成新作、不覆盖、不补造其历史。回收的技术审核调用本脚本 `audit`，生产 PASS 还必须取得原 journal 中实际下游 job 的当前有效接收。
