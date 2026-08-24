# 项目上下文

## 项目概览
- 项目名称：Ozon媒体官
- 当前目标：在不放松证据门禁的前提下，让部分组合 SKU 可由其权威单品组成关系回退图片来源（本轮已完成）。
- 当前范围：组合 SKU 来源解析、生成回执的来源溯源、代理指令与流程说明。
- 非目标：重生成历史视频、修改商品数据、调用 Ozon 写接口或推送仓库。

## 技术与结构
- 技术栈：Python 3、openpyxl、ffmpeg/ffprobe、GitHub/jsDelivr、Ozon Seller API。
- 关键目录：根目录下的代理指令与 skills/；源图片表位于 workspace-ozon-lister/workbench/。
- 关键入口：make_carousel_video.py、check_video_compliance.py、AGENTS.md。
- 运行/构建：python3 make_carousel_video.py <SKU>。
- 测试方式：py_compile、脚本负向/正向样例、ffprobe 与合规检查。

## 约束与约定
- 代码风格：最小改动；脚本结果必须以退出码和机器可读回执为准。
- 接口或数据约束：SKU 必须精确匹配 xlsx 与产物文件名；Ozon 写操作必须 confirm_write=True。
- 环境限制：本次仅审查与本地修改，不调用 Ozon 写接口、不推送远程仓库。
- 外部依赖：xlsx 源表、ffmpeg/ffprobe、Ozon MCP、GitHub/jsDelivr。

## 当前结论
- 已确认：组合采购价表是 `组合 SKU → 单品 SKU × 数量` 的权威关系来源；组合 SKU 自身不在 xlsx 且只有一个精确单品组成、该单品在 xlsx 有图时，当前可安全候选 17 条。回执会记录 target/source/quantity/mapping_file。
- 待确认：是否另行处理多单品组合的专属素材策略；它们当前保持阻断。
