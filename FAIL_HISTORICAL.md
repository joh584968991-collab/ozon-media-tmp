# 历史 FAIL 视频说明

以下 4 个视频是历史遗留（2026-08-16 / 8-17 生成），不符合 Ozon 规则：
- `carousel_QK1064.mp4`
- `carousel_QK1135.mp4`  
- `carousel_QK1325.mp4`
- `carousel_QK1590.mp4`

**原因**：当前 xlsx 表 `workbench/ozon8_final3_titles_fixed.xlsx` 中**没有这 4 个 SKU 的图片**（xlsx 图数 = 0），无法重新生成。

**处理**：
- 不在 `skus_video_pending.txt` 待备货清单中（已被 ozon-lister 上架流程处理）
- jsDelivr 上的旧链接保留（Ozon 后台可能已引用）
- 如需重新生成，需先在 xlsx 中补图片 URL

**自查脚本状态**：check_video_compliance.py 检测 FAIL 是预期的（非任务污染）。
