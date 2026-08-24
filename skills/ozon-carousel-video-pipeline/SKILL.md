---
name: "ozon-carousel-video-pipeline"
description: "Ozon carousel video batch generation with mandatory pre-push compliance check; covers yuvj420p→yuv420p range conversion and FAIL remediation rules."
---

# Ozon Carousel Video Pipeline

Generate carousel videos in batch with machine-verifiable gates. A model must never infer completion from a plausible filename, URL, or partial command output.

## Trigger
Any batch task producing `carousel_<SKU>.mp4` files for the `ozon-media-tmp` repo. Standing rule from ozon-lister: every video must pass `check_video_compliance.py` before push.

## Workflow

1. Generate one or many videos.
   - Single: `python3 make_carousel_video.py <SKU>`
   - Input is one exact target SKU only. The script reads its unique xlsx row; only if that row is absent may it read the authoritative `组合采购价表.txt` and fall back to exactly one mapped component SKU. It does not accept ad-hoc image URLs, fuzzy SKU matches, or a guessed fallback SKU.
   - A derived video still uses `carousel_<组合SKU>.mp4` and targets the combination SKU in Ozon. Its `RESULT_JSON.image_source` must include `DERIVED_SINGLE_COMPONENT`, the source SKU, quantity, and mapping file. Multiple components are always blocked.
   - Output is valid only when the final `RESULT_JSON` says `CDN_READY`. `PUSHED_CDN_PENDING` means the Git push is proven but the link is still a candidate; retain the task and retry CDN verification later instead of claiming success.
   - If the result is `FAILED`, record its error and leave the SKU pending. Do not guess whether it is caused by missing images or retry a different SKU.

2. Run compliance check on every generated file (mandatory).
   - `python3 check_video_compliance.py carousel_<SKU>.mp4`
   - Required: 8-300 s duration, ≤2 GB, h264, **Main** profile, `yuv420p`, `color_range=tv`, and matching `.mp4`/`.mov` container.
   - PASS → push; FAIL → see FAIL remediation

3. Push only on PASS.
   - The generator itself performs the compliance gate and uses an isolated Git index so it commits only the target video. Do not manually run `git add/commit/push` to bypass it.
   - `CDN_READY` additionally proves that the remote `main` contains the returned commit and jsDelivr answered HTTP 200 with `content-type: video/mp4`.
   - Never push FAIL videos — Ozon rejects and you cannot recover the cost of an entire batch.

4. At batch end, re-scan all `carousel_*.mp4` and report PASS/FAIL totals.
   - Run the scan immediately before reporting. The `ozon-media-tmp` repo is shared with `Ozon Lister Bot`, so a remembered PASS/FAIL count from this or any prior session is not evidence — re-run the directory scan now, count both PASS and FAIL buckets, and treat any earlier count as stale until it is re-derived from a fresh scan.
   - Report each SKU separately as `CDN_READY`, `PUSHED_CDN_PENDING`, `FAILED`, or `BLOCKED`, including the command/API evidence.
   - Historical exceptions documented in `FAIL_HISTORICAL.md` remain exceptions; do not silently treat them as passing.

## FAIL Remediation

- **First, audit the full source pipeline before declaring "no source".** The carousel pipeline reads images from any of: the canonical xlsx, `62sku_info.json` in `ozon-lister/workbench/` (Ozon ir-20 image URLs), `_ozon_<i>.jpg` rework files produced by `ozon_compliant_rework.py`, and jsDelivr CDN images already pushed from a previous batch. A FAIL video whose xlsx row is empty is not necessarily unfixable — the rework artifacts, `62sku_info.json`, or a prior CDN push may still cover it. For each FAIL SKU, enumerate which sources contain ≥4 images and pick the highest-priority one that does. Only when every source is empty should the SKU be treated as truly unrepairable. This triage is what prevents recommending deletion of videos that are one re-source step away from PASS.

- **`yuvj420p` + `color_range=pc`** (most common): the `scale` filter in `ozon_video_pipeline.py` lacks `:out_range=tv`. Add it:
  ```
  scale=800:800:force_original_aspect_ratio=decrease:out_range=tv,
  pad=800:800:(ow-iw)/2:(oh-ih)/2:white,setsar=1,format=yuv420p[v%d]
  ```
  Root cause: input JPEGs default to full-range; `format=yuv420p` only rewrites the tag, not the range. Regenerate all affected SKUs after the script fix.

- **All sources empty after audit** (e.g. `QK1064`, `QK1135`, `QK1325`, `QK1590` in `FAIL_HISTORICAL.md`): truly cannot regenerate. Document in `FAIL_HISTORICAL.md` with reason; do NOT delete — existing jsDelivr URLs may be referenced by the Ozon backend.

- **Test files** (e.g. `carousel_full.mp4`, no matching SKU): after confirming they are not referenced, move them to Trash rather than deleting directly.

## Hygiene

- Remove `.tmp_<SKU>/` directories after each batch (untracked, ~2 MB each, clutter git status)
- Clean `__pycache__/` periodically
- Do not overwrite an existing `carousel_<SKU>.mp4` unless the user explicitly authorizes that exact SKU and reason via `--replace-existing`.
- Do not remove a SKU from the upstream pending list until it is `CDN_READY`.

## Anti-patterns

- Skipping step 2 because "the script worked yesterday" — historical batches have shown silent regressions when scale/filter params drift
- Committing when FAIL count > 0 to "get something through"
- Deleting historical FAIL files without checking whether Ozon URLs point to them
- Calling a candidate jsDelivr URL “available” before a 200 + `video/mp4` response
- Reusing images, URLs, commit IDs, or Ozon responses from a similarly named SKU
- Treating a cost-only file such as `combos.json` as proof of combination components; only `组合采购价表.txt` is authoritative for this fallback
