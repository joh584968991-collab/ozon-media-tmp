---
name: "ozon-product-image-quality-control"
description: "Run Ozon 5-image visual compliance QC, select one main plus four product-only images, and audit the final report for gaps."
---

# Ozon Product Image Quality Control

Inspect a fixed Ozon image set, select a compliant main image plus four additional images per SKU, and issue a validated delivery report.

## Step 1: Build an exact inventory

List every requested SKU and each source identifier, such as `relist_1` through `relist_5`. Resolve the actual extension per file and use the same one-based identifier everywhere.

Record each source as present or missing. Do not substitute zero-based array positions for source filenames.

Completion: every requested SKU has an explicit one-based source record, and every recorded file exists.

## Step 2: Inspect every image individually

Evaluate each image against the requested compliance rules: no brand logo, watermark, advertising copy, contact details, URL, promotion, or Chinese text, with a clean white or light background.

Record each image as compliant, non-compliant, or needs review. Give a concrete reason for every non-compliant image.

For an ambiguous mark such as a stamped brand, OE number, or text embedded on the product, record `needs review` instead of silently accepting or rejecting it without a governing policy.

Completion: every inventoried image has one disposition and a reason for every non-compliant or review outcome.

## Step 3: Select exactly one main and four additional images

Choose one compliant, product-dominant, light-background image as the main image. Choose four other distinct compliant images as additional images.

Never fill missing slots with a borderline, background, marketing, branded, or merely less-bad image. If five compliant images do not exist, report the exact shortfall and list every non-compliant image; do not call the SKU complete.

Completion: each complete SKU has one main and four additional images, and no image appears twice.

## Step 4: Validate references mechanically

Generate each URL or file path from the resolved one-based source identifier. Reject placeholders such as `{SKU}`, `{N}`, or `{jpg|jpeg}` in deliverable rows.

Check every selected path and extension against the inventory. Normalize equivalent URL forms before delivery.

Completion: every deliverable reference resolves to one existing source file and uses its resolved extension.

## Step 5: Reconcile the complete report

Derive summary counts from the per-SKU rows, not from memory or a second hand-maintained count. Verify that:

- every requested SKU appears exactly once;
- statuses are mutually exclusive;
- complete, partial, and no-compliant-image totals add up to the SKU count;
- every reported failure reason maps to the same per-SKU evidence;
- no summary name is listed in two categories;
- every final image URL passes the reference check.

Correct discrepancies before describing the batch as complete.

Completion: a fresh count from the final rows exactly matches the reported totals, with no duplicate SKU or invalid image reference.

## Step 6: Deliver the actionable result

Return one section per SKU with the main image, four additional image references, and a concise non-compliant-image explanation. Put partial sets and no-compliant-image sets in a separate shortfall section.

Include the totals for complete, partial, and no-compliant-image SKUs, and identify any item requiring policy review.

Completion: the recipient can copy every complete SKU directly and knows exactly what is missing or unsafe for every incomplete SKU.
