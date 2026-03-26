# TimeLineEvent表配置规则文档

## 第一部分：配置表字段说明

### 1.1 字段列表

| 字段名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| TimeEvent | string | 是 | 时间事件ID，格式：TIM + 序号(3位) |
| name | string | 是 | 人物名（英文） |
| cnDay | string | 是 | 中文日期，如 11.03 |
| enDay | string | 是 | 英文日期，如 Nov.02 |
| startTime | number | 是 | 开始时间（24小时制，如23.5=23:30） |
| endTime | number | 是 | 结束时间（24小时制） |
| cnDescribe | string | 是 | 中文事件描述 |
| enDescribe | string | 是 | 英文事件描述 |
| Color | string | 否 | 显示颜色 |
| dayStart | number | 否 | 时间轴显示起点（小时） |
| dayEnd | number | 否 | 时间轴显示终点（小时） |

---

### 1.2 ID命名规则

**格式：`TIM` + `序号(3位)`**

| 位置 | 含义 | 说明 |
|------|------|------|
| TIM | 固定前缀 | TimeLine |
| 序号 | 3位数字 | 001-999 |

**示例：**
- `TIM001` = 第1个时间事件

---

### 1.3 时间格式说明

| 字段 | 格式 | 示例 |
|------|------|------|
| startTime/endTime | 小数表示时间 | 23.5 = 23:30，0.5 = 00:30 |
| cnDay | 月.日 | 11.03 = 11月3日 |
| enDay | 英文月份.日 | Nov.02 = November 2nd |

---

### 1.4 Color 颜色说明

| 颜色值 | 颜色 | 色值 |
|--------|------|------|
| red | 红色 | #d00000 |
| yellow | 黄色 | #d0c801 |
| orange | 橙色 | #f47800 |
| blue | 蓝色 | #6f83ff |
| cyan | 青色 | #43bd91 |
| purple | 紫色 | #f753ed |
| green | 绿色 | #1d9600 |

---

### 1.5 完整配置示例

```yaml
- TimeEvent: TIM001
  name: Tommy
  cnDay: 11.03
  enDay: Nov.02
  startTime: 23.5
  endTime: 23.5
  cnDescribe: 听到一声枪响
  enDescribe: gunshots
  Color: yellow
  dayStart: 20
  dayEnd: 24
```

---

## 第二部分：注意事项

1. **ID唯一性**：TimeEvent必须唯一
2. **时间格式**：使用小数表示分钟（0.5=30分钟）
3. **时间轴范围**：dayStart/dayEnd定义该事件在时间轴上的显示范围

---

## 第三部分：更新日志

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| v1.0 | 2025-11-29 | 初始版本 |
