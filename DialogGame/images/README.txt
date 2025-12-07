========================================
        图片文件夹说明
========================================

将 NPC 立绘和场景背景图放入此文件夹。

【支持的图片格式】
- PNG（推荐，支持透明背景）
- JPG / JPEG
- GIF
- WebP

【NPC 立绘】
- 建议尺寸：300x300 像素以上
- 最好使用正方形或接近正方形的图片
- 在 YAML 中使用：portrait: "文件名.png"

【场景背景】
- 建议尺寸：1920x1080 像素
- 在 YAML 中使用：background: "文件名.jpg"

【使用示例】
假设你有以下图片：
  images/
    anna.png        <- NPC立绘
    tommy.png       <- NPC立绘
    bg_cafe.jpg     <- 场景背景

在 YAML 中这样引用：
  scenes:
    - id: cafe
      name: "咖啡馆"
      background: "bg_cafe.jpg"
      npcs:
        - id: anna
          name: "安娜"
          portrait: "anna.png"

========================================
