# 执行档位、事实分支与单入口终结

本协议把同一人物入景工作流按交付深度分为 `probe`、`provisional`、`formal` 三个执行档位。它们共享同一套身份、场景、UI、尺度和整场审核规则，不是三套可漂移的 Skill。档位只控制本轮必须产出的证据和允许返回的状态。

## 1. 三个档位

| 档位 | 最小目标 | 必须生成 | 允许结果 |
|---|---|---|---|
| `probe` | 尽快证实站位、尺度、动作大类、支撑、UI 与第一条提取路线 | 带真实 UI 的 Layout Preview 与首个可用 RGBA 的 Pixel Proof Preview | `PIXEL_PROOF_READY` 或 `PROBE_BLOCKED`；不算场景包 |
| `provisional` | 第一份可用 RGBA 到场后不中断下游验证 | Pixel Proof Preview、黑/白/深场景色一张批量 Alpha 板；需要时 XY/重建 | `PROVISIONAL_SCENE_PACKAGE`；只有真实 H0 才为 `H0_BLOCKED_PACKAGE` |
| `formal` | 当前完整 scope 的正式冻结和一次性打包 | 上述预览、正式 RGBA、适用验证器、需要时 XY/逐像素重建 | `FORMAL_CANDIDATE` 或 `FORMAL_REVIEW_BLOCKED` |

不得因为切换档位重置生成次数、Photoshop 轮次、用户否定或来源历史。`probe` 默认在一份有用候选和首次像素预览后停止正式精修，只保留未改原始下载、尝试 RGBA、快速合成和最小来源/哈希记录；它不要求五阶段正式 ledger、多路线耗尽或正式打包。`provisional` 不是降低正式门禁，而是让已有可打开的非生成 RGBA 继续产生可审核的整场证据。

## 2. 永远执行的基础项与事实分支

每个含 NPC 的场景固定执行以下七项，不得从截图或旧文件名推断为“不适用”：

1. `scope_timeline`：角色、状态、进退场和同时在场快照；
2. `actual_ui`：真实对话 UI；`ui.required` 永远为 `true`，`variant` 只可为 `left`、`right`、`both_or_dynamic`；
3. `support_contact`：承托、接触和必要投影；
4. `scene_scale`：场景绝对尺度及单人也适用的头身/深度关系；
5. `occlusion_layer_order`：角色与原场景结构遮挡；单人场景仍执行；
6. `identity_action_orientation`：身份、动作大类、主朝向及 active 视线；
7. `whole_scene_review`：整场关系、读图和最终画面审核。

只有下列子检查按已锁定的场景事实启用：

- `idle_click_continuity`：`exploration-click-pair`；
- `multicast_links`、`multi_actor_relative_scale` 与 `pairwise_actor_occlusion`：同时在场人数至少 2；
- `multicast_back_composition`：同时在场人数至少 3；
- `soft_support_response`：确有床垫、枕头、软椅、被褥等承托响应；
- `reclining_elevated_projection`：躺卧或床、沙发、担架、桌面等高位承托。

“纯剧情”“单状态”“单角色”只关闭与事实不符的子检查，不关闭 UI、尺度、承托、遮挡或整场审核。

## 3. 两张关键预览

- `Layout Preview`：直接使用现有联合白模/布局源叠加当前真实 UI，不额外触发生图。目标是尽早发现错误站位、支撑、层次和 UI 遮挡。
- `Pixel Proof Preview`：第一份通过 H0 结构检查的可用 RGBA 一产生，立即贴回实际场景并叠加真实 UI；不要等待边缘润色、其它角色或所有提取路线结束。它证明真实像素能否进入整场，而不是正式放行。

`provisional` 和 `formal` 的 Alpha 审阅均使用一张批量 contact sheet，包含每个 RGBA 的黑底、白底、从实际场景取样并压暗的深场景色底。三块背景是同一次审阅的面板，不是三个手工阶段。实际场景关系另由 Pixel Proof Preview 检查。

## 4. Alpha 分层与路线停止条件

- H0 结构：真实 RGBA、有可见与透明像素、没有整块矩形场景、无重大人体/服装/关键道具截断。失败时不能进入该角色的 provisional 或 formal 合成。
- H1/H2 边缘：少量 halo、残色、发丝/半透明边缘、局部衣角或鞋边瑕疵。可记录为 `PROVISIONAL` 并继续待审包；formal 必须实际审核为 PASS。

提取路线遵循单向短路：

1. 优先选择当前能力快照中端到端 `supported` 的“主体选择到 Alpha”或“移除背景到 RGBA”最短路线；任何一段无法落地时立即换适用独立路线，不把按钮名当能力证明；
2. `first_usable_rgba`：立即保存未改原图、结果和回执，生成 Pixel Proof Preview，同时继续尚未实测的适用路线；
3. `first_formal_rgba`：立刻停止该角色剩余路线，避免为了填满日志继续低价值操作；
4. `no_formal_rgba`：只有全部适用且实时 `supported` 的独立非生成路线已有实测、`NOT_APPLICABLE` 或 `UNSUPPORTED` 证据后，才可登记整体能力失败。

一个按钮失败只终止该路线；原样命令最多重试一次。路线日志保存命令回执、输入/输出哈希、视觉结论和精确失败点。

## 5. 白模的最小硬判定

白模只为下游锁定：角色/状态、头身比、动作大类、主要朝向、承托类型、粗略景深和[人体覆盖模式](efficiency-and-state-contract.md)。`FULL_IN_FRAME` 与 `SCENE_OCCLUDED` 需要完整头到脚母版范围；`FRAME_CROPPED_FOREGROUND` 需要完整可见解剖至自然出框边界及画外尺度/支撑证据，不要求生成永远画外的腿脚。允许在正确承托锚点上做统一平移、等比缩放和必要旋转。

下列内容不单独触发再生成：halo、抠图边缘、衣纹/手指/面部精修、小型局部遗漏、精确 XY、精确最终尺寸。只有动作前提、主要朝向、承托类型、粗略深度错误，或解剖/完整母版范围已无法供正式阶段使用时，才返回白模生成。正式角色仍必须是完整独立人体并通过最终细节审核。

## 6. 单入口终结器

运行：

```powershell
python -B scripts/art_pipeline/ndc_art.py run ndc-character-scene-integration character_scene_pipeline.py -- `
  finalize-scene --manifest <scene-finalization.json> --profile probe
```

`--profile` 可为 `probe`、`provisional`、`formal`。清单使用 `ndc-character-scene-finalization/v2`，关键结构如下；路径相对清单解析，示例名不是固定项目路径：

```json
{
  "schema": "ndc-character-scene-finalization/v2",
  "sceneId": "scene-revision-id",
  "scope": {
    "interactionType": "pure-narrative",
    "simultaneousCastCount": 1,
    "supportTypes": ["ground"],
    "hasSoftSupport": false,
    "hasRecliningOrElevatedActor": false,
    "requiredLayerIds": ["actor-a:state-1"],
    "anatomyCoverage": [{
      "id": "actor-a:state-1",
      "mode": "FRAME_CROPPED_FOREGROUND",
      "visibleAnatomyReview": "PASS",
      "naturalFrameExit": true,
      "visibleAnatomyComplete": true,
      "offFrameScaleSupportEvidence": [{"path": "scale-review.json", "sha256": "..."}],
      "evidence": [{"path": "anatomy-review.json", "sha256": "..."}]
    }]
  },
  "ui": {
    "required": true,
    "variant": "left",
    "references": {"left": "ui-left.png", "right": "ui-right.png"}
  },
  "artifacts": {
    "sourceScene": "scene.png",
    "layoutSource": "combined-whitebox.png"
  },
  "criteria": {
    "scope_timeline": {"status": "PASS", "evidence": [{"path": "timeline-report.json", "sha256": "..."}]},
    "actual_ui": {"status": "PASS", "evidence": [{"path": "ui-report.json", "sha256": "..."}]}
  },
  "extraction": {
    "layers": [{
      "id": "actor-a:state-1",
      "path": "actor-a.png",
      "quality": "usable",
      "xy": [120, 240],
      "structuralReview": "PASS",
      "edgeReview": "PROVISIONAL",
      "reviewEvidence": [{"path": "alpha-review.json", "sha256": "..."}]
    }],
    "routeExhaustion": [{"id": "native-alpha", "status": "FAILED"}]
  },
  "validators": [
    {"name": "production-ledger", "contract": "post-generation-ledger.json", "profiles": ["formal"]},
    {"name": "final-conformance", "contract": "final-conformance.json", "profiles": ["formal"]}
  ],
  "psSession": {
    "used": true,
    "ownerTaskId": "current-task",
    "openDocumentCount": 0,
    "inFlightCommandCount": 0,
    "unknownCommandCount": 0,
    "handoffStatus": "RELEASED",
    "capabilitySnapshot": {"path": "ps-capability.json", "sha256": "..."},
    "evidence": [{"path": "ps-release.json", "sha256": "..."}]
  },
  "reconstruction": {"enabled": true},
  "outputDir": "finalization-output",
  "timingLedger": []
}
```

`criteria` 必须覆盖基础项和解析出的全部事实分支；每项只接受当前文件 SHA-256 绑定的显式 `PASS`、`PROVISIONAL`、`FAIL` 或 `NOT_CHECKED`。`FAIL/NOT_CHECKED` 还需标注真实 `tier`：H0 在所有档位阻断；H1–H3 可进入 provisional，但 formal 仍阻断。provisional 中缺少某个重复证据字段只形成待补证据说明，不让已有可用像素归零。每个 RGBA 的结构/边缘结论仍用 `reviewEvidence` 绑定真实审核文件。终结器不把图片统计、文件存在或验证器成功转换成艺术判断。`formal` 至少实际调用 `production-ledger` 与 `final-conformance`。

`outputDir` 始终位于 `{WORK_ROOT}`；终结器只写过程预览、证据和待审重建，不自动把整包过程资料推进交付根。输出目录包含 `finalization.json`、`finalization-summary.txt`、档位缓存报告和确定性的 `package-index.json`。底层 `result` 仍为 `PASS`、`PROVISIONAL` 或 `BLOCKED`，对外以 `packageState` 表示上表状态。`formal` 只有完整 scope、人体覆盖、每个正式 RGBA、H0/H1/H2、全部适用审阅和必需验证器均通过时才产生 `FORMAL_CANDIDATE`。

终结后，当前任务必须从包中明确选出实际准备交付的图片；只对这些图运行 [交付候选登记](delivery-contract.md#delivery-candidate-registry)。正式角色/合成图登记为 `delivery_candidate`，参考图本身被明确选为交付件时登记为 `selected_reference`。候选图以字节一致副本进入 `{DELIVERY_ROOT}` 下的 `交付候选/<candidate-id>`，源文件与完整证据仍在 `{WORK_ROOT}`。`PROVISIONAL_SCENE_PACKAGE` 或 `H0_BLOCKED_PACKAGE` 也可以提供一个明确选定的交付候选，但候选清单必须原样保留其状态；进入候选区不改变 finalizer 结果、审阅结论或正式门禁。

## 7. 缓存与失效

缓存键只绑定：源场景、布局、实际 UI、RGBA 像素哈希，执行档位，适用事实分支，结构/边缘状态，相关审阅证据哈希和验证器合同哈希。备注、时间戳、显示名、输出目录说明等 metadata 改动不触发像素重审。

像素、UI、角色/状态范围、支撑、尺度、遮挡、身份/动作解释、用户否定或任何相关审阅文件变化都会产生新键并重跑受影响工作。缓存命中只复用已生成的像素预览/联系表；既有验证器仍在当前依赖上重新执行，以捕获合同未改但引用文件已漂移的情况。缓存命中仍追加本轮 timing 记录，不伪造新的 inspection 时间。

## 8. 节拍记录与自动止损

每个阶段记录 `phase`、`started_at`、`finished_at`、`active_seconds`、`external_wait_seconds`、`cache_hit`、`result`、`block_reason`。网页生成、登录、验证码、网络下载和外部传输等待只计入 `external_wait_seconds`，不掩盖本地活动时间。

- Layout Preview：目标不超过 10 分钟 active time；
- 下载/提取后 Pixel Proof Preview：目标不超过 15 分钟 active time；
- finalization：目标不超过 10 分钟 active time；
- 累计 30 分钟 active time 仍无 Pixel Proof Preview：停止当前方法并切换另一条已授权可行路线；
- 累计 60 分钟 active time：停止低价值润色，至少形成明确标记的 provisional 包；若 H0 不成立，则保存阻断证据而不是伪造 provisional RGBA。

终结报告会保存超时动作提示；它不重发未知网页提交，也不突破授权、正式门禁或用户暂停。
