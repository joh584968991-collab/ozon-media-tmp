#!/usr/bin/env python3
"""Ozon 视频上传规则自查（生成后、上传前执行）
用法: python3 check_video_compliance.py <video.mp4>
返回: PASS / FAIL + 违规项
"""
import sys
import json
import subprocess
from pathlib import Path


def probe(path):
    """ffprobe 提取视频信息"""
    if not Path(path).is_file():
        return {}, '文件不存在'
    cmd = ['ffprobe', '-v', 'error',
           '-show_entries', 'format=format_name,duration,size:stream=codec_name,codec_type,width,height,pix_fmt,profile',
           '-show_entries', 'stream=color_range',
           '-of', 'json', path]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        detail = (r.stderr or '没有 ffprobe 错误输出').strip()[-300:]
        return {}, 'ffprobe 执行失败：%s' % detail
    if not r.stdout:
        return {}, 'ffprobe 未返回视频信息'
    try:
        return json.loads(r.stdout), None
    except json.JSONDecodeError as exc:
        return {}, 'ffprobe 输出无法解析：%s' % exc


def check(path):
    issues = []
    info, probe_error = probe(path)
    if probe_error:
        return [probe_error], {
            'duration': None, 'size_mb': None, 'codec': None, 'pix_fmt': None,
            'color_range': None, 'profile': None, 'dims': None, 'format_name': None,
        }
    fmt = info.get('format', {})
    streams = info.get('streams', [])
    vstream = next((s for s in streams if s.get('codec_type') == 'video'), None)

    # 1. 时长 8s ~ 5min (300s)
    try:
        duration = float(fmt.get('duration', 0) or 0)
    except (TypeError, ValueError):
        duration = 0.0
        issues.append('无法读取视频时长')
    if duration < 8:
        issues.append('时长 %.1fs < 8s' % duration)
    if duration > 300:
        issues.append('时长 %.1fs > 5分钟' % duration)

    # 2. 大小 ≤2GB
    try:
        size = int(fmt.get('size', 0) or 0)
    except (TypeError, ValueError):
        size = 0
        issues.append('无法读取视频大小')
    if size > 2 * 1024 * 1024 * 1024:
        issues.append('大小 %.1fMB > 2GB' % (size / 1048576))

    # 3. 编码 h264 / Main / pix_fmt yuv420p / limited range
    if not vstream:
        issues.append('无视频流')
    else:
        codec = vstream.get('codec_name', '')
        pix = vstream.get('pix_fmt', '')
        crange = vstream.get('color_range', '')
        profile = vstream.get('profile', '')
        if codec != 'h264':
            issues.append('编码 %s ≠ h264' % codec)
        if profile != 'Main':
            issues.append('Profile %s ≠ Main' % (profile or '未标记'))
        if pix != 'yuv420p':
            issues.append('像素格式 %s ≠ yuv420p' % pix)
        if crange != 'tv':
            issues.append('色彩范围 %s ≠ tv(limited)' % (crange or '未标记'))

    # 4. 扩展名和容器必须一致，不能只靠改文件名伪装。
    suffix = Path(path).suffix.lower()
    if suffix not in ('.mp4', '.mov'):
        issues.append('扩展名非 mp4/mov')
    else:
        container_names = set((fmt.get('format_name') or '').split(','))
        expected_container = suffix[1:]
        if expected_container not in container_names:
            issues.append('容器 %s 与扩展名 %s 不一致' % (fmt.get('format_name') or '未标记', suffix))

    return issues, {'duration': round(duration, 1), 'size_mb': round(size / 1048576, 1),
                    'codec': vstream.get('codec_name') if vstream else None,
                    'pix_fmt': vstream.get('pix_fmt') if vstream else None,
                    'color_range': vstream.get('color_range') if vstream else None,
                    'profile': vstream.get('profile') if vstream else None,
                    'dims': '%sx%s' % (vstream.get('width'), vstream.get('height')) if vstream else None,
                    'format_name': fmt.get('format_name')}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: python3 check_video_compliance.py <video.mp4>')
        sys.exit(1)
    issues, meta = check(sys.argv[1])
    print('=== 视频信息 ===')
    for k, v in meta.items():
        print('  %s: %s' % (k, v))
    if issues:
        print('❌ FAIL:')
        for i in issues:
            print('  - %s' % i)
        sys.exit(1)
    else:
        print('✅ PASS: 符合 Ozon 视频上传规则')
