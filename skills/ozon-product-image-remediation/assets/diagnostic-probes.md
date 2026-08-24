# Diagnostic probes for /v1/product/pictures/import

When the API returns `400 VALIDATION ERROR`, isolate the cause with minimal probes before debugging request payload.

## Probe sequence

1. Send just `{"product_id": <int>}` with no `images` field. If this fails, the issue is product state, not payload format.
2. Send a single image URL (any clean one, including an existing primary). If this fails, the issue is product state.
3. Repeat the same code and credentials against the known-good product_id `6048227055` (QK0014-11). If it succeeds there, the issue is the target product's state, not your code, key, or request shape.
4. Try both `cdn1.ozone.ru/s3/multimedia-1-*/...` and `ir-20.ozone.ru/s3/multimedia-1-*/...` URLs. Both work for products in good state.

## Root-cause matrix when product state is the blocker

| Symptom on `/v3/product/info/list` | Meaning | Resolution |
|---|---|---|
| `sku == 0` and `sources == []` | Product hasn't completed import | Wait for async SKU assignment (typically 30s–5min) or re-import |
| `errors[]` contains `image_not_upload` with `state=variant_wait` | Variant handshake incomplete | Re-run variant assignment via `/v1/product/import` or archive+recreate |
| `errors[]` contains `DESCRIPTION_DECLINE` for `attribute_id 4195` | Images themselves flagged for ads/markings | After sku is assigned, retry pictures/import with verified-clean image URLs |

When product state is the blocker, the picture-replacement call will keep returning `400 VALIDATION ERROR` until the state resolves. Do not retry the same payload expecting a different result.