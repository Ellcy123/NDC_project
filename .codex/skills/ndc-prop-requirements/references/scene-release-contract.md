# 道具按场景放行合同

本合同仅改变第二阶段到第三阶段的交接范围。某场景的全部道具及其完整关联前置已经确认且有效通过、没有未解决外部关联，即可进行该场景入景／菜单制作。另一独立场景缺图或失败不再阻塞它；不能按完成百分比或单个道具通过抢先放行。全批scope、jobs、required_artifacts和原尝试记录始终保留。

## 最少需要读取的材料

首次建立索引读完整总清单的场景成员及关联信息、相关内容档案和这些判断的确切来源，不要求逐张重新视觉审完所有旧资产。按场景续跑只读同一batch、当前不可覆盖的索引、scene-readiness列出的物品／前置／来源及其当前审核；无需重读其他生产阶段的全文。

场景物理成员清单包括该场景实际要制作／放入的全部道具、容器及内容物和必要状态；照片引用的人物身份、文书引用的另一物品日期等语义来源列在关联事实中，不因被提及就成为要制作的场景物。逐项核对同一物品跨场景共享、开合／前后状态、容器与内容物、照片所描绘对象、共同事实；没有关联也要有实际查阅来源。尚未确定照片内容、容器数量或跨场景对象是否同一物件时记unresolved，不能省略关联来放行。

## 可选索引字段

主批次继续使用ndc-prop-batch/v1。只新增scene_release_index指针，由迁移命令写入path、sha256；不要手填指针或改旧日志。索引schema为ndc-prop-scene-release/v1：

| 字段 | 要求 |
| --- | --- |
| batch_id、scope_sha256 | 对应原批次和完整scope的规范JSON摘要；不建立缩小子批次 |
| reviewer、reason | 实际执行关联核对者与具体来源判断 |
| items | 字典，键恰好覆盖scope.item_ids；逐项status=resolved/unresolved、sources、open_questions数组；未解决项写明问题 |
| scenes | 字典，键恰好覆盖scope.scene_ids；每项item_ids为场景全部物理制作成员，artifact_ids列该场景所需第三阶段非Icon产物，sources记录成员来源；纯语义来源另由relations绑定 |
| relations | 显式数组；无关联时允许空数组，但items里的核对来源仍必填 |

sources每项含原始证据path和SHA-256；输入索引可用相对路径，迁移按索引所在目录解析、核验并保存为绝对路径。迁移／修订还保存各item的requirements_sha256和每条关系所列事实的fact_values_sha256，记录本次实际核对的事实值；之后改档案不能沿用旧resolved声明，须实际复核并追加修订。哈希只证明来源字节和记录值没有变化，关联是否完整仍由执行者实际查阅核对。scope_sha256使用workflow_state.py中的digest(batch['scope'])计算，不能取整个batch文件的哈希代替。

每条relations包含以下字段：

```json
{
  "id": "photo_depicts_other_scene",
  "kind": "depicted_content",
  "status": "resolved",
  "item_ids": ["photo_item", "depicted_item"],
  "artifact_ids": ["depicted_scene.final"],
  "consumer_scene_ids": ["photo_display_scene"],
  "fact_refs": ["depicted_item.identity"],
  "sources": [{"path": "association_source.md", "sha256": "替换为实际64位SHA256"}],
  "reason": "按具体原文确认照片依赖另一场景的实际定稿内容"
}
```

示例仅说明字段，不是NDC默认事实或可直接通过的证据。kind允许shared_identity、state_variant、container_content、depicted_content、fact_reference。item_ids包含所有关联物品；fact_refs使用内容档案里的item.field。artifact_ids仅列确实要先取得的外部图像，填写时consumer_scene_ids必须明确列消费这些外部图像的场景，避免把来源场景变成自己的前置；只有事实引用时artifact_ids可为空，consumer_scene_ids仍可限定实际引用场景，不限定则为空数组。两种轻语义关系必须明确至少一个fact_refs或artifact_ids，不能用全部留空的resolved行放行。

scenes.artifact_ids必须覆盖原范围全部第三阶段非Icon必需产物，并包括每一菜单图、逐菜单预览和场景相关Big。已声明scene_id的产物必须落在该场景；没有scene_id的共享产物须显式分配到消费它的场景。场景内尚待制作的场景图／菜单／预览是本阶段输出，不能被关系索引再列为自己的入景前置。菜单父图仍在实际菜单attempt时检查。

## 门槛计算

从该场景全部物理成员开始，shared_identity、state_variant、container_content扩展为需要完整确认的物理物品组；收取组内物品在完整required_artifacts中的全部第二阶段母版、指定状态和普通Big，并追溯真实图像父依赖。共享母版即使scene_id为空或写在另一场景也不会漏查。同物多个状态属于同一item_id时，全部所需第二阶段状态仍会纳入；使用多个item_id表达状态时必须用state_variant关联。这三种强关系不能通过artifact_ids留空免除这些物理产物要求，也不能为抢跑改成事实引用。

fact_reference与depicted_content只扩展所列事实和来源，不自动要求被引用物品的其他母版／Big。图像确有实际外部父图时仍须在artifact_ids明确列出，其父依赖及物理物品随后进入生产前置。角色身份原图可登记为source_reference并由关系sources绑定现有批准依据；身份事实可记为照片本身的photo_item.depicted_identity，不为一个引用把角色加入道具产物分母或新增角色生产任务。跨物品artifact.fact_refs要有关系事实或强物理关联来源，不必把纯语义来源塞入场景物理成员。readiness分别输出production_item_ids、context_fact_refs和prerequisite_artifacts，便于解释为什么需要某张图或只需要某条事实。

物理物品组的关联状态resolved、open_questions为空，当前所用关系resolved且所列事实仍匹配确认快照，来源字节有效、实际图像前置审核及拒收状态均有效，门槛才通过。纯事实引用不读取被引用对象的无关图像状态／其他未引用事实；引用事实未确认或来源变动仍阻塞。失败输出和未知关联明确显示阻塞；本场景全部必要前置齐全后，无关母版／场景的未完成和失败不参与该门槛。全局索引必须结构完整，不能通过遗漏场景成员或产物来制造“无关”。

容器内容必须已确定且相关母版已通过，但该场景未来的Type7和菜单预览不作为自己的前置。照片只依赖已锁定身份／文字事实时用轻语义关系的fact_refs及来源；照片确实依赖另一场景定稿图时才列artifact_ids和consumer_scene_ids。例：A文书只引用B文书已确认日期，B的无关待产母版不挡A，日期改动或其来源变动会挡A。关联语义可以双向，实际图像生产依赖不能成环。

## 接入与续跑

以下命令使用同级ndc-prop-delivery-review/scripts/workflow_state.py的绝对路径。新批次先完成原init；已初始化旧批次直接迁移，不能再次init。

```text
python workflow_state.py migrate-scene-release --batch <原batch.json> --index <实际核对的完整索引.json> --reason "全范围成员与关联来源已核对，保留原作业与次数"
python workflow_state.py scene-readiness --batch <原batch.json> --scene <scene_id>
python workflow_state.py validate --batch <原batch.json> --stage 3 --scene <scene_id>
python workflow_state.py attempt --batch <原batch.json> --job "item|scene|scene_id|state" --prompt <实际提示.txt> --reason "具体首次制作或剩余额度内修正"
python workflow_state.py progress --batch <原batch.json>
```

迁移将核验过的索引保存至batch目录下scene_release_indexes，并在原attempt_log追加哈希串联的scene_release_index事件，不增减真实生成次数。之后关联内容变动，实际核对并准备完整新版索引，再运行：

```text
python workflow_state.py revise-scene-release --batch <原batch.json> --index <核对后的完整新版索引.json> --reason "明确哪些关联变化及依据"
```

每次保留旧索引快照和原日志。改scope/jobs、移除指针、篡改快照或截断原日志均会阻止接续；迁移／修订不能重置3次入景或6次母版额度。未知历史仍按原resolve-history规则处理。无索引旧批继续全局第二阶段门槛；stage 3不加--scene也保持全局核验。attempt自动从已锁job及产物所属场景计算门槛，不读取手工current_stage作为许可。

## 已产图失效与后续总闸

第三阶段非Icon产物的审核绑定加入scene_release_contexts；相关事实、关联来源、前置图像／审核版本改变或用户拒收会撤销其有效性及后代，即使场景自身字节未变。迁移旧图只补实际缺少的关联核对证据，保留已有效的观察和原图，不自动重画，也不把新binding当作新视觉PASS。affected会包含未写直接图像父边、但由关联前置影响的场景产物；progress只统计目前仍有效的PASS。

整批第三阶段非Icon必需图全通过后才制作Icon及专用来源；全批次stage 4仍要求必需上游结果和全部场景／菜单冻结；stage 5和正式发布仍检查完整总清单。--scene只可放宽stage 3入口，不能获得局部热区或局部正式发布许可。PS独立目标的调度、占用和检查等待另遵循共享PS协议，不改变这些图像交付条件。
