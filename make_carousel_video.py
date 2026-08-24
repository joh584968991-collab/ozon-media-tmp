#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ozon 轮播视频命令入口。

实现位于 ``ozon_video_pipeline.py``：只允许从源 xlsx 精确匹配 SKU，且每个
完成状态都由合规、Git 和 CDN 回执证明。保留原文件名以兼容既有 Agent 指令。
"""
from ozon_video_pipeline import main


if __name__ == '__main__':
    raise SystemExit(main())
