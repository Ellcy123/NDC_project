# Unit3 探索场景目录

本目录放非 AVG 的物理地点底图类场景，包含自由探索场景、过渡走廊、可复用的指证场地。资源形态是“底图 / 环境 + NPC / Item / 事件挂载”，不是人物和场景合成的一张 AVG 图。

文件命名格式：

```text
EXP_SC{sceneId}_{地点名}.md
```

## 当前文件

| 文件 | 内部英文名 | 场景用途 |
|---|---|---|
| EXP_SC3001_楼下现场.md | `u3_exp_ground` / `u3_l2_ground_entrance` | 公寓楼下案发外部区域 + L2 Mary 拦截 / 指证入口 |
| EXP_SC3002_楼顶.md | `u3_exp_rooftop` | 楼顶案发现场，承载护栏、油痕、脚印等跨 Loop 搜证 |
| EXP_SC3003_Smith家_客厅.md | `u3_exp_smith_living` | Smith 家客厅，L2 起进入 |
| EXP_SC3004_警局.md | `u3_exp_police` | L1 Morrison 指证地点，可作为指证背景复用 |
| EXP_SC3005_法医办公室.md | `u3_exp_forensic` | 法医办公室，L1 / L4 / L6 多阶段信息更新 |
| EXP_SC3006_公寓二楼走廊.md | `u3_exp_2f_hall` | 二楼走廊，L6 挂载 Seamus 润滑油突发事件 |
| EXP_SC3007_教堂.md | `u3_exp_church` | St.Patrick 教堂 |
| EXP_SC3008_Helen家.md | `u3_exp_helen_home` | Helen 家，L3 / L4 指证与突发事件核心地点 |
| EXP_SC3009_湖滨信托银行公共区.md | `u3_exp_bank_lobby` | 银行公共区 |
| EXP_SC3010_Margaret鞋坊.md | `u3_exp_shoe_shop` | Margaret 鞋坊 |
| EXP_SC3011_Mickey办公室.md | `u3_exp_mickey_office` | Mickey 办公室，L5 / L6 使用，可作为控辩背景复用 |
| EXP_SC3012_Smith家_卧室.md | `u3_exp_smith_bedroom` | Smith 家卧室 |
| EXP_SC3013_已并入SC3001_公寓楼门口.md | `u3_exp_entrance` | 历史占位；已并入 SC3001，不独立开放 / 出图 |
| EXP_SC3014_Bernard办公室.md | `u3_exp_bernard_office` | Bernard 办公室，L5 指证与 Charles 突发事件地点 |
| EXP_SC3015_三楼走廊.md | `u3_exp_3f_hall` | Helen 家门口与上行楼梯过渡 |
| EXP_SC3016_公寓一楼走廊.md | `u3_exp_1f_hall` | Smith 家一楼入口过渡 |

Loop 差异写进同一个探索场景文件内部，不额外拆 `L1_楼顶`、`L4_楼顶` 这类文件。

## 日夜版本口径

Unit3 探索场景只分白天 / 夜晚两档。清晨、上午、中午、下午统一归白天；傍晚后、案发回溯、夜间调查统一归夜晚。

内部英文名仍保持短名，例如 `u3_exp_rooftop`。具体背景资源名在配置里加 `_day` / `_night` 后缀。

公寓楼动线必须具备白天 / 夜晚两版需求：SC3001 楼下入口、SC3016 一楼走廊、SC3006 二楼走廊、SC3015 三楼走廊、SC3002 楼顶。Helen 家因 L3 白天搜证与 L4 夜晚补充指证共用，也写白天 / 夜晚灯光差异。
