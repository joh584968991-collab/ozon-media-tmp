---
name: "ozon-product-image-remediation"
description: "Ozon product image replacement via /v1/product/pictures/import; diagnose 400 VALIDATION ERROR caused by sku=0 or unfixed product state."
---

# Ozon Product Image Remediation

Replace images on an Ozon product via the seller API. Use when `/v1/product/pictures/import` returns `400 VALIDATION ERROR` on every payload, especially when the product is flagged for ad-marker violations (e.g., 1688 watermark, banner ads, third-party logos).

## When to load

- User asks to replace or remove specific images on an Ozon product
- `/v1/product/pictures/import` returns `{"code": 3, "message": "VALIDATION ERROR"}` regardless of payload
- `/v3/product/info/list` shows `image_not_upload`, `DESCRIPTION_DECLINE`, or `variant_wait` errors
- A control call to a known-good product succeeds but this product fails

## Step 1: Verify product state

Before debugging the payload, fetch product state:

```
POST /v3/product/info/list  body={"product_id": [PRODUCT_ID]}
```

Required fields on `items[0]`:
- `sku` non-zero
- `sources` non-empty
- `errors[]` does not contain `variant_wait` or unresolved `declined`
- `is_archived` and `is_autoarchived` both false

If `sku == 0` or `sources == []`, the product is in a half-baked state and `/v1/product/pictures/import` rejects all calls with `400 VALIDATION ERROR` regardless of payload shape. Stop and resolve the underlying errors first.

Completion: confirmed `sku != 0`, `sources != []`, and no blocking errors.

## Step 2: Issue the replacement

```
POST /v1/product/pictures/import
{
  "product_id": <int>,                 // int64, NOT offer_id string
  "images": ["https://...", ...]       // field name is "images", NOT "pictures"
}
```

Both `cdn1.ozone.ru/s3/multimedia-1-*/...` and `ir-20.ozone.ru/s3/multimedia-1-*/...` URLs work.

Completion: response 200 with `result.pictures[]` listing each URL with `state: "imported"`.

## Step 3: Verify after async

Wait ~60 seconds for Ozon async processing:

```
POST /v2/product/pictures/info  body={"product_id": [PRODUCT_ID]}
```

`primary_photo` is the main image, `photo` is the additional set, `errors` should be `[]`.

Completion: confirmed desired images appear and unwanted ones are absent.

## PIL delogo fallback (when delogo_rework.py fails)

`delogo_rework.py` wraps `ffmpeg -vf delogo=...` against the `image2` muxer. On many JPEGs it exits with `Could not open encoder before EOF` (encoder handshake failure on a still frame) and writes no output. When that error appears, switch to a PIL-only procedure instead of retrying ffmpeg:

1. Open the source with PIL and read dimensions: `w, h = Image.open(src).size`. Scale `x,y,w,h` if the coordinates came from a different image size.
2. Pick the fill strategy by the marker's location:
   - Top banner / colored header strip with the product below: fill the rectangle with `255,255,255`. White blends with the usual product-shot margins.
   - Corner watermark on a textured surface (e.g. 1688 / Taobao text on the product): sample 5 rows just above (or beside) the rectangle, compute the mean RGB, and fill the rectangle with that color. Matches the surrounding texture.
3. Save the cleaned file as `<SKU>_ozon_<index>.jpg`, commit/push to `ozon-media-tmp`, and confirm jsDelivr returns HTTP 200 before reporting the path back to the caller.

## Reference

- Known-good comparison product: QK0014-11 product_id=6048227055, ozon_sku=5545215531 (sources non-empty, errors empty).
- Diagnostic probe patterns and root-cause matrix: see [diagnostic-probes.md](assets/diagnostic-probes.md).
