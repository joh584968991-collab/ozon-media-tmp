# Ozon 主图模板设计方案 (2026-08-22)
<!-- project: github.com/joh584968991-collab/ozon-media-tmp -->

## 一、设计原则

**核心约束**（已严格遵守）：
- 宽高比 3:4（首选）
- 长边 ≤7680px（实现 900×1200）
- ≤10MB（实现 ~50KB）
- 白/浅背景
- 禁：黑白、模糊、居家、价格/折扣/联系方式/促销、广告文字、品牌Logo（无授权）

## 二、3 个模板变体（差异化保证不撞哈希）

| 变体 | 背景色 | 强调色 | 风格定位 |
|---|---|---|---|
| **V1 Minimal Clean** | #FFFFFF 纯白 | cyan #0EA5E9 | 简洁通用型 |
| **V2 Soft Gray** | #FAFAFA 浅灰 | emerald #10B981 | 高端精品感 |
| **V3 Cool Tint** | #F8FAFC 蓝白 | amber #F59E0B | 暖色活力感 |

## 三、布局结构（三个变体共用）

```
┌──────────────────────────────────────┐  ← 顶部 50-80px
│ ─────────── (细色线)               │     放 OEM 编号（仅技术信息）
│ OE REFERENCE │ 16100-MFJ-D01          │
│                                      │  ← 130px 顶部留白
│       ┌──────────────────┐          │
│       │                  │          │
│       │                  │          │
│       │   商品主体（居中）  │          │  ← 800px 商品展示区
│       │   75% 高度       │          │
│       │   72% 宽度       │          │
│       │                  │          │
│       │                  │          │
│       └──────────────────┘          │
│                                      │  ← 130px 底部留白
│ ━━━━━━ (细色线)                  │
│ ┌─────────┐                  SKU     │  ← 左下角：产品类型 chip
│ │AUTO PART│              QK3022    │     右下角：SKU 半透明水印
│ └─────────┘                          │
└──────────────────────────────────────┘
```

## 四、字体规范

| 元素 | 字体 | 颜色 | 大小 |
|---|---|---|---|
| 顶部 OE 编号 | Helvetica/PingFang SC | 深灰 #6B7280 | 16px |
| 左下产品类型 | Helvetica/PingFang SC | chip 主题色 | 14px |
| 右下 SKU 水印 | Helvetica/PingFang SC | 黑色 10-13% alpha | 22px |

**关键**：仅含技术信息（OE 编号、SKU、产品类型 chip），**零营销词**（无 Premium / Top / Best / Sale 等）。

## 五、示例图（已 push 到 GitHub）

```
https://cdn.jsdelivr.net/gh/joh584968991-collab/ozon-media-tmp@main/.tmp_template/main_template_V1.jpg
https://cdn.jsdelivr.net/gh/joh584968991-collab/ozon-media-tmp@main/.tmp_template/main_template_V2.jpg
https://cdn.jsdelivr.net/gh/joh584968991-collab/ozon-media-tmp@main/.tmp_template/main_template_V3.jpg
```

示例用的商品：QK3022_relist_1.jpeg（fuel petcock 金属件，干净白底）

## 六、复用方法（套到新 SKU）

```python
from PIL import Image, ImageDraw, ImageFont

def make_main_image(product_path, oe, sku, type_text, variant='V1', out_path='main.jpg'):
    bg_colors = {'V1': '#FFFFFF', 'V2': '#FAFAFA', 'V3': '#F8FAFC'}
    accents = {'V1': '#0EA5E9', 'V2': '#10B981', 'V3': '#F59E0B'}
    oem_colors = {'V1': '#6B7280', 'V2': '#4B5563', 'V3': '#475569'}
    
    W, H = 900, 1200
    canvas = Image.new('RGB', (W, H), bg_colors[variant])
    draw = ImageDraw.Draw(canvas)
    
    # 商品居中（占 80% 高度）
    product = Image.open(product_path).convert('RGB')
    product.thumbnail((720, 800), Image.LANCZOS)
    px = (W - product.width) // 2
    py = 130 + (800 - product.height) // 2
    canvas.paste(product, (px, py))
    
    # 顶部 OEM 标签 + 细线
    draw.line([(40, 80), (W-40, 80)], fill=accents[variant], width=2)
    font_oem = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 16)
    draw.text((40, 50), f'OE REFERENCE  |  {oe}', font=font_oem, fill=oem_colors[variant])
    
    # 左下角产品类型 chip
    font_chip = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 14)
    chip_text = type_text.upper()
    bbox = draw.textbbox((0,0), chip_text, font=font_chip)
    chip_w = bbox[2]-bbox[0] + 28
    chip_h = bbox[3]-bbox[1] + 12
    draw.rounded_rectangle([(32, H-chip_h-36), (32+chip_w, H-36)], 
                           radius=chip_h//2, fill='#F3F4F6')
    draw.text((46, H-chip_h-36+6), chip_text, font=font_chip, fill='#374151')
    
    # 右下角 SKU 半透明水印
    font_sku = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 22)
    sku_text = f'SKU  {sku}'
    overlay = Image.new('RGBA', canvas.size, (0,0,0,0))
    ImageDraw.Draw(overlay).text((W-180, H-50), sku_text, font=font_sku, fill=(0,0,0,30))
    canvas = Image.alpha_composite(canvas.convert('RGBA'), overlay).convert('RGB')
    
    # 底部分隔线
    draw = ImageDraw.Draw(canvas)
    draw.line([(40, H-100), (W-40, H-100)], fill=accents[variant], width=1)
    
    canvas.save(out_path, 'JPEG', quality=92)
    return out_path

# 用法
make_main_image('path/to/clean_product.jpg', '16100-MFJ-D01', 'QK3022', 'Auto Part', 'V1')
```

## 七、差异化策略（防哈希碰撞）

1. **3 个变体轮换使用** —— 不同 SKU 用 V1/V2/V3，3 套哈希
2. **OE 编号每个 SKU 唯一** —— 即便内容相同哈希也会变
3. **产品类型 chip 文字多样**（AUTO PART / ENGINE / BRAKE / SUSPENSION 等）
4. **强调色随变体**（cyan/emerald/amber）

## 八、合规检查清单

部署前必过：
- [ ] 商品主体清晰（无模糊）
- [ ] 背景白/浅灰
- [ ] 3:4 比例（900×1200）
- [ ] 无营销词（Premium / Top / Sale / Best 等）
- [ ] 无品牌 Logo（除非商品本身）
- [ ] 无价格/折扣/联系方式
- [ ] OE 编号（技术信息，可保留）
- [ ] SKU 水印（半透明，防复制）
