#!/usr/bin/env python3
"""144 FAIL 视频统一修复脚本（用正确的 out_range=tv + color_range tv filter）"""
import os, sys, glob, subprocess, time
sys.path.insert(0, '/Users/capper/.openclaw/workspace-ozon-media')
from check_video_compliance import check
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

REPO = '/Users/capper/.openclaw/workspace-ozon-media'
INFO_62 = '/Users/capper/.openclaw/workspace-ozon-lister/workbench/62sku_info.json'


def fix_one(sku):
    """根据源数据修复单个 SKU"""
    # 先删旧 FAIL
    old = os.path.join(REPO, f'carousel_{sku}.mp4')

    # 找 _ozon_*.jpg 二创图（路径 B + C）
    reworks = sorted([f for f in glob.glob(f'{REPO}/{sku}_ozon_*.jpg')
                      if os.path.getsize(f) > 1000])[:9]

    if len(reworks) >= 4:
        # 路径 B: 直接用 _ozon_*.jpg 做视频
        return make_video(sku, reworks)

    # 路径 C: 从 62sku_info.json 取原图，先二创
    try:
        with open(INFO_62) as f:
            info = json.load(f)
        urls = info.get(sku, {}).get('images', [])
        if urls:
            reworks = []
            for i, url in enumerate(urls[:9]):
                # 用 ozon_compliant_rework 风格处理
                from PIL import Image, ImageDraw, ImageFont, ImageEnhance
                import urllib.request, io
                try:
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    data = urllib.request.urlopen(req, timeout=30).read()
                    if len(data) < 1000:
                        continue
                    img = Image.open(io.BytesIO(data)).convert('RGB')
                    w, h = img.size
                    # 3:4 白边
                    target_w, target_h = w, int(w * 4 / 3)
                    if target_h < h:
                        target_h, target_w = h, int(h * 3 / 4)
                    canvas = Image.new('RGB', (target_w, target_h), 'white')
                    canvas.paste(img, ((target_w - w) // 2, (target_h - h) // 2))
                    bw = int(target_w * 0.04)
                    bordered = Image.new('RGB', (target_w + 2 * bw, target_h + 2 * bw), 'white')
                    bordered.paste(canvas, (bw, bw))
                    bordered = ImageEnhance.Brightness(bordered).enhance(1.02)
                    bordered = ImageEnhance.Contrast(bordered).enhance(1.03)
                    bordered = ImageEnhance.Color(bordered).enhance(1.05)
                    # 水印
                    draw = ImageDraw.Draw(bordered)
                    W, H = bordered.size
                    try:
                        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', max(20, int(H * 0.035)))
                    except:
                        font = ImageFont.load_default()
                    bbox = draw.textbbox((0, 0), sku, font=font)
                    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    txt_layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                    tdraw = ImageDraw.Draw(txt_layer)
                    tdraw.text((W - tw - 40 + 1, H - th - 35 + 1), sku, font=font, fill=(0, 0, 0, 90))
                    tdraw.text((W - tw - 40, H - th - 35), sku, font=font, fill=(255, 255, 255, 100))
                    bordered = Image.alpha_composite(bordered.convert('RGBA'), txt_layer).convert('RGB')
                    out_rework = os.path.join(REPO, f'{sku}_ozon_{i}.jpg')
                    bordered.save(out_rework, 'JPEG', quality=88)
                    reworks.append(out_rework)
                except Exception as e:
                    pass
            if len(reworks) >= 4:
                return make_video(sku, reworks)
    except Exception:
        pass

    return ('FAIL', sku, 'no source')


def make_video(sku, images):
    """用正确 filter 链合成视频（out_range=tv + color_range tv）"""
    out = os.path.join(REPO, f'carousel_{sku}.mp4')

    inputs = []
    for f in images:
        inputs.extend(['-loop', '1', '-t', '2', '-i', f])
    n = len(images)

    filter_parts = []
    for i in range(n):
        filter_parts.append(
            f'[{i}:v]scale=800:800:force_original_aspect_ratio=decrease:out_range=tv,'
            f'pad=800:800:(ow-iw)/2:(oh-ih)/2:white,'
            f'setsar=1,format=yuv420p[v{i}]'
        )
    concat_in = ''.join(f'[v{i}]' for i in range(n))
    filter_parts.append(
        f'{concat_in}concat=n={n}:v=1:a=0,'
        'setparams=range=tv:color_primaries=bt709:color_trc=bt709:colorspace=bt709[outv]'
    )
    fc = ';'.join(filter_parts)

    cmd = [
        'ffmpeg', '-y', *inputs,
        '-filter_complex', fc,
        '-map', '[outv]', '-c:v', 'libx264', '-profile:v', 'main',
        '-pix_fmt', 'yuv420p', '-color_range', 'tv',
        '-movflags', '+faststart', out
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        # 自查
        iss, _ = check(out)
        if not iss:
            return ('PASS', sku, out)
        return ('FAIL_COMPLIANCE', sku, iss)
    return ('FFMPEG_FAIL', sku, r.stderr[-200:])


if __name__ == '__main__':
    # 收集所有 FAIL SKU
    fail_skus = []
    for f in sorted(glob.glob(f'{REPO}/carousel_*.mp4')):
        iss, _ = check(f)
        if iss:
            sku = os.path.basename(f).replace('carousel_', '').replace('.mp4', '')
            # 排除 QK1321_hq（特殊文件名，单独处理）
            if sku == 'QK1321_hq':
                continue
            fail_skus.append(sku)

    print(f'待修复 SKU: {len(fail_skus)}')

    # 并行处理
    start = time.time()
    results = {'PASS': [], 'FAIL': []}
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(fix_one, sku): sku for sku in fail_skus}
        for future in as_completed(futures):
            sku = futures[future]
            try:
                r = future.result()
                status = r[0]
                if status == 'PASS':
                    results['PASS'].append(sku)
                    print(f'  ✅ {sku}', flush=True)
                else:
                    results['FAIL'].append((sku, r[1], r[2]))
                    print(f'  ❌ {status} {sku}: {r[2] if r[2] else ""}', flush=True)
            except Exception as e:
                results['FAIL'].append((sku, 'EXC', str(e)[:200]))
                print(f'  ❌ EXC {sku}: {e}', flush=True)

    elapsed = time.time() - start
    print(f'\n=== {elapsed:.1f}s 完成 ===')
    print(f'✅ PASS: {len(results["PASS"])}')
    print(f'❌ FAIL: {len(results["FAIL"])}')
    if results['FAIL']:
        print('\nFAIL 详情:')
        for sku, st, info in results['FAIL'][:10]:
            print(f'  {sku}: {st} | {info}')
