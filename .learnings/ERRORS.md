# Errors

## [ERR-20260820-001] apply_patch

**Logged**: 2026-08-20T00:00:00+08:00
**Priority**: low
**Status**: resolved
**Area**: docs

### Summary
补丁工具不支持在同一个补丁中删除并重新添加同一路径。

### Error
```
apply_patch verification failed: invalid patch: multiple operations target /Users/capper/.openclaw/workspace-ozon-media/make_carousel_video.py
```

### Context
- 尝试用单个补丁完整替换 make_carousel_video.py。
- 未有任何文件内容实际变更。

### Suggested Fix
后续完整替换同一路径时只使用 Update File 操作，或拆成两个独立补丁。

### Metadata
- Reproducible: yes
- Related Files: make_carousel_video.py

### Resolution
- **Resolved**: 2026-08-20T00:00:00+08:00
- **Notes**: 改用单一 Update File 补丁。

---

## [ERR-20260821-001] combo_mapping_empty_entry

**Logged**: 2026-08-21T00:00:00+08:00
**Priority**: medium
**Status**: resolved
**Area**: backend

### Summary
组合采购价表含一条没有单品组成的组合 SKU，首次解析器把它计为有效映射。

### Error
```
AssertionError: 246
```

### Context
- 预期有 245 个可解析组合关系，解析结果包含一个空 components 列表。
- 空组合没有触发图片回退，但会让映射计数与权威成本台账不一致。

### Suggested Fix
解析完成后移除空组成条目；请求该 SKU 时视为“无映射”并保持阻断。

### Metadata
- Reproducible: yes
- Related Files: ozon_video_pipeline.py, /Users/capper/.openclaw/workspace-ozon-lister/workbench/cost/组合采购价表.txt

### Resolution
- **Resolved**: 2026-08-21T00:00:00+08:00
- **Notes**: 空组成条目不再进入可用映射；不会被用于组合 SKU 回退。

---

## [ERR-20260820-003] local_path_discovery

**Logged**: 2026-08-20T00:00:00+08:00
**Priority**: low
**Status**: resolved
**Area**: docs

### Summary
初次读取共享媒体防错配脚本时使用了项目清单中的相对展示路径，实际文件并不在该位置。

### Error
```
sed: /Users/capper/.openclaw/workspace-ozon-lister/workbench/ozon-auto/media_guard.py: No such file or directory
```

### Context
- 项目清单中描述了 `ozon-auto/media_guard.py`，但该路径未位于 workbench 根目录。
- 后续发现组合 SKU 的权威来源是 `workbench/cost/combos.json` 与组合采购价表。

### Suggested Fix
读取项目前先用 `rg --files` 解析实际路径；不要把清单中的展示路径当作绝对位置。

### Metadata
- Reproducible: yes
- Related Files: /Users/capper/.openclaw/workspace-ozon-lister/workbench/项目清单_v1.md

### Resolution
- **Resolved**: 2026-08-20T00:00:00+08:00
- **Notes**: 已改为基于实际映射资产继续审查。

---

## [ERR-20260820-002] exec_command_cleanup

**Logged**: 2026-08-20T00:00:00+08:00
**Priority**: low
**Status**: resolved
**Area**: tests

### Summary
环境策略拒绝了测试临时目录的 `rm -rf` 清理命令。

### Error
```
Rejected: rm -f style commands are not permitted. Use a safer approach
```

### Context
- 目标是本次创建并已核对内容的 `/tmp/ozon-media-verify.WYDvCc`。
- 未执行删除，临时验证产物仍存在。

### Suggested Fix
对已核验的临时产物使用系统 `trash`，而不是 `rm -rf`。

### Metadata
- Reproducible: yes
- Related Files: /tmp/ozon-media-verify.WYDvCc

### Resolution
- **Resolved**: 2026-08-20T00:00:00+08:00
- **Notes**: 已改用可恢复的系统废纸篓操作。

---
