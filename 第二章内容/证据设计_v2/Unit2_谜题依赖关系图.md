# Unit2 谜题依赖关系图 (Puzzle Dependency Diagram)

> **设计方法**: Ron Gilbert (Lucasfilm Games, Maniac Mansion)
> **生成日期**: 2025-12-25
> **最后更新**: 2025-12-25

---

## 循环核心任务总览

| 循环 | 核心任务 | 指证对象 | 轮次 |
|:---:|:---|:---:|:---:|
| L1 | 死者是谁？ | Morrison | 2轮 |
| L2 | Frank身上发生了什么？ | Leonard | 3轮 |
| L3 | 贷款的真相是什么？ | Moore | 3轮 |
| L4 | Rose是骗子还是真爱？ | Danny | 3轮 |
| L5 | Frank当晚发生了什么？ | Vinnie | 1轮 |
| L6 | 谁是真凶？ | Leonard | 4轮 |

---

## 图例说明

| 元素 | 含义 |
|:---:|:---|
| 红色节点 | 指证节点（含对象和轮次） |
| 绿色节点 | 自白/供出节点 |
| 蓝色节点 | 特殊场景（码头营救） |
| 黄色区块 | 证据合并/分析操作 |
| 实线箭头 | 依赖关系 |
| "硬切" | 剧情强制跳转 |
| "解锁" | 完成前置后开放 |

---

## 完整依赖关系图

```mermaid
flowchart TB
    subgraph L1["循环1: 死者是谁？"]
        L1_START["L1开场 硬切"]
        L1_1A["1A 鞋坊店铺区"]
        L1_1B["1B 鞋坊卧室区"]
        L1_E101["101 尸体手指照片"]
        L1_E102["102 Margaret相册"]
        L1_E103["103 空首饰盒"]
        L1_E104["104 现场地面照片"]
        L1_E108["108 通信小本"]
        L1_E111["111 身份证"]
        L1_ACCUSE1["指证Morrison 2轮"]

        L1_START --> L1_1A
        L1_START --> L1_1B
        L1_1A --> L1_E101
        L1_1A --> L1_E104
        L1_1B --> L1_E102
        L1_1B --> L1_E103
        L1_1B --> L1_E108
        L1_E101 & L1_E102 & L1_E103 & L1_E104 --> L1_ACCUSE1
    end

    subgraph COMBINE1["证据合并"]
        ADDR_COMBINE["111+108 = Frank地址"]
    end

    L1_E108 --> ADDR_COMBINE
    L1_E111 --> ADDR_COMBINE

    subgraph L2["循环2: Frank身上发生了什么？"]
        L2_FRANK["Frank家"]
        L2_OHARA["O'Hara家"]
        L2_CASINO["赌场"]
        L2_BANK["银行"]

        L2_E201["201 怀表"]
        L2_E202["202 O'Hara证词"]
        L2_E206["206 催款单"]
        L2_E207["207 O'Hara钞票"]
        L2_E208["208 Vinnie钞票"]
        L2_E217["217 Leonard曾用名"]
        L2_ACCUSE2["指证Leonard 3轮"]

        L2_FRANK --> L2_E201
        L2_FRANK --> L2_E206
        L2_OHARA --> L2_E202
        L2_OHARA --> L2_E207
        L2_E202 -->|对话解锁| L2_CASINO
        L2_CASINO --> L2_E208
        L2_E206 -->|地址解锁| L2_BANK
        L2_BANK --> L2_E217
    end

    ADDR_COMBINE -->|解锁| L2_FRANK
    ADDR_COMBINE -->|解锁| L2_OHARA
    L1_ACCUSE1 --> L2

    subgraph COMBINE2["证据分析"]
        BILL_ANALYZE["207+208 = 连号分析"]
    end

    L2_E207 --> BILL_ANALYZE
    L2_E208 --> BILL_ANALYZE
    BILL_ANALYZE --> L2_ACCUSE2
    L2_E217 --> L2_ACCUSE2

    subgraph L3["循环3: 贷款的真相是什么？"]
        L3_START["L3开场 硬切"]
        L3_CITY["市政厅"]
        L3_ARCHIVE["档案室"]
        L3_OFFICE["Leonard办公室"]

        L3_E304["304 搜查令"]
        L3_E311["311 遗嘱副本"]
        L3_E312["312 贷款协议"]
        L3_E318["318 旧照片"]
        L3_ACCUSE3["指证Moore 3轮"]

        L3_START --> L3_CITY
        L3_CITY --> L3_E304
        L3_E304 -->|搜查令解锁| L3_ARCHIVE
        L3_E304 -->|搜查令解锁| L3_OFFICE
        L3_ARCHIVE --> L3_E311
        L3_ARCHIVE --> L3_E312
        L3_OFFICE --> L3_E318
        L3_E312 --> L3_ACCUSE3
    end

    L2_ACCUSE2 --> L3

    subgraph L4["循环4: Rose是骗子还是真爱？"]
        L4_BASEMENT["地下室"]
        L4_DANNY["Danny房间"]

        L4_E418["418 枯萎玫瑰"]
        L4_E419["419 水杯"]
        L4_E421["421 银戒指"]
        L4_E423["423 空怀表盒"]
        L4_E425["425 钥匙"]
        L4_ACCUSE4["指证Danny 3轮"]
        L4_DANNY_CONFESS["Danny自白: 盒子位置"]

        L4_E425 -->|钥匙解锁| L4_BASEMENT
        L4_BASEMENT --> L4_E418
        L4_BASEMENT --> L4_E419
        L4_DANNY --> L4_E423
        L4_ACCUSE4 --> L4_DANNY_CONFESS
    end

    L3_ACCUSE3 --> L4
    L3_E311 -->|遗嘱提及| L4_E425

    subgraph COMBINE3["证据合并"]
        ROSE_COMBINE["418+419 = 玫瑰复活"]
        WATCH_COMBINE["201+423 = 偷表真相"]
    end

    L4_E418 --> ROSE_COMBINE
    L4_E419 --> ROSE_COMBINE
    ROSE_COMBINE --> L4_E421
    L2_E201 --> WATCH_COMBINE
    L4_E423 --> WATCH_COMBINE
    WATCH_COMBINE --> L4_ACCUSE4

    subgraph L5["循环5: Frank当晚发生了什么？"]
        L5_START["L5开场"]
        L5_FLOOR["Frank家 地板缝隙盒子"]

        L5_E502["502 举报材料"]
        L5_E503["503 遗书"]
        L5_ACCUSE5["指证Vinnie 1轮"]
        L5_VINNIE_CONFESS["Vinnie供出: 码头"]
        L5_DOCK["码头营救"]
        L5_E501["501 打火机"]

        L5_START --> L5_FLOOR
        L5_FLOOR --> L5_E502
        L5_FLOOR --> L5_E503
        L5_E502 & L5_E503 --> L5_ACCUSE5
        L5_ACCUSE5 --> L5_VINNIE_CONFESS
        L5_VINNIE_CONFESS --> L5_DOCK
        L5_DOCK --> L5_E501
    end

    L4_ACCUSE4 --> L5
    L4_DANNY_CONFESS -->|位置| L5_FLOOR
    L4_E421 -->|1920密码| L5_FLOOR

    subgraph L6["循环6: 谁是真凶？"]
        L6_START["L6开场 硬切"]
        L6_HOSPITAL["医院"]
        L6_SHOP["鞋坊重访"]
        L6_LEONARD["Leonard住所"]

        L6_E601["601 烛台"]
        L6_E606["606 抵押照片"]
        L6_E608["608 眼镜碎片"]
        L6_E610["610 空相框"]
        L6_E612["612 搜查令"]
        L6_E617["617 镊子"]
        L6_ACCUSE6["指证Leonard 4轮"]

        L6_START --> L6_HOSPITAL
        L6_HOSPITAL --> L6_E606
        L6_HOSPITAL --> L6_E617
        L6_HOSPITAL --> L6_E612
        L6_E612 -->|搜查令解锁| L6_LEONARD
        L6_LEONARD --> L6_E610
        L6_SHOP --> L6_E601
    end

    L5_DOCK --> L6

    subgraph COMBINE4["证据对比"]
        PHOTO_COMPARE["606照片找茬"]
        GLASS_COMBINE["617+烛台 = 眼镜碎片"]
        FRAME_COMBINE["318+610 = 兄弟关系"]
    end

    L6_E606 --> PHOTO_COMPARE
    PHOTO_COMPARE --> L6_SHOP
    L6_E617 --> GLASS_COMBINE
    L6_E601 --> GLASS_COMBINE
    GLASS_COMBINE --> L6_E608
    L3_E318 --> FRAME_COMBINE
    L6_E610 --> FRAME_COMBINE
    L6_E608 & FRAME_COMBINE --> L6_ACCUSE6

    style L1_ACCUSE1 fill:#ff6b6b
    style L2_ACCUSE2 fill:#ff6b6b
    style L3_ACCUSE3 fill:#ff6b6b
    style L4_ACCUSE4 fill:#ff6b6b
    style L5_ACCUSE5 fill:#ff6b6b
    style L6_ACCUSE6 fill:#ff6b6b,stroke:#000,stroke-width:3px
    style L4_DANNY_CONFESS fill:#90EE90
    style L5_VINNIE_CONFESS fill:#90EE90
    style L5_DOCK fill:#87CEEB

    style COMBINE1 fill:#ffd93d
    style COMBINE2 fill:#ffd93d
    style COMBINE3 fill:#ffd93d
    style COMBINE4 fill:#ffd93d
```

---

## 关键依赖链总结

### 主线推进
```
L1 死者是谁？ → 指证Morrison(2轮) → 确认死者是Frank
    ↓
L2 Frank身上发生了什么？ → 指证Leonard(3轮) → 揭露银行-黑帮勾结
    ↓
L3 贷款的真相是什么？ → 指证Moore(3轮) → 揭露掠夺性贷款 + 获取遗嘱
    ↓
L4 Rose是骗子还是真爱？ → 指证Danny(3轮) → 证明Rose清白 + Danny自白位置
    ↓
L5 Frank当晚发生了什么？ → 开盒子获取遗书 → 指证Vinnie(1轮) → Vinnie供出码头 → 救Margaret
    ↓
L6 谁是真凶？ → 指证Leonard(4轮) → 诱导招供 → 揭露真凶
```

### L5流程详解（重要）
```
L4指证Danny → Danny自白(盒子位置) + 戒指421(1920密码)
    ↓
L5开场 → Frank家地板缝隙盒子 → 502举报材料 + 503遗书（情感高点）
    ↓
指证Vinnie(1轮) → Vinnie供出码头位置
    ↓
Mickey带领 → 码头营救Margaret → 501打火机
    ↓
L6开场硬切医院
```

### 场景解锁机制

| 循环 | 场景 | 解锁方式 |
|:---:|:---|:---|
| L1 | 鞋坊店铺+卧室 | 开场硬切 |
| L2 | Frank家+O'Hara家 | 111身份证+108小本子→地址 |
| L2 | 赌场 | O'Hara对话202 |
| L2 | 银行贵宾室 | 催款单206地址 |
| L3 | 市政厅 | 开场硬切 |
| L3 | 档案室+办公室 | 搜查令304 |
| L4 | 地下室 | 遗嘱311→钥匙425 |
| L5 | 地板缝隙盒子 | Danny自白(位置) + 戒指421(密码) |
| L5 | 码头 | Vinnie供出 |
| L6 | 医院 | 开场硬切 |
| L6 | 鞋坊(重访) | 606照片找茬玩法 |
| L6 | Leonard住所 | 搜查令612 |

### 跨循环证据合并

| 合并项 | 来源循环 | 结果 |
|:---|:---:|:---|
| 111身份证 + 108小本子 | L1 | Frank地址 → 解锁L2场景 |
| 207 O'Hara钞票 + 208 Vinnie钞票 | L2 | 连号分析 → 证明资金来源 |
| 201怀表 + 423空盒 | L2+L4 | Danny偷拿真相 |
| 418枯萎玫瑰 + 419水杯 | L4 | 鲜活玫瑰 → 银戒指(密码) |
| 318旧照片 + 610空相框 | L3+L6 | Leonard与Vinnie是兄弟 |
| 606照片 + 现场观察 | L6 | 找茬 → 发现烛台变化 |
| 617镊子 + 烛台下缝隙 | L6 | 眼镜碎片 |

---

## 设计要点

1. **线性但非单调**: 主线严格L1→L6，但每循环内有多条并行探索路径
2. **证据合并驱动**: 关键进展需要合并/分析证据，而非单纯收集
3. **跨循环伏笔**: L2怀表在L4才揭示真相，L3照片在L6才完成合并
4. **玩法多样化**: 包含对话解锁、物品解锁、密码解锁、找茬玩法等
5. **任务导向**: 每个循环有明确的核心疑问，引导玩家探索方向
6. **情感节奏**: L5开盒子获取遗书是Frank与Rose情感线的高点
