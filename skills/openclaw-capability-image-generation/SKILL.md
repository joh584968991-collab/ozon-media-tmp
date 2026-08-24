---
name: "openclaw-capability-image-generation"
description: "Generate AI product images via `openclaw capability image generate` with the configured local provider (e.g. minimax/image-01)."
---

# Generate images via the openclaw capability CLI

Use this when the task is generating, editing, or describing product / hero / lifestyle images and the workspace runs in an OpenClaw agent with the `openclaw` CLI available.

Do NOT use this skill for:
- Analyzing or describing existing images — use the first-class `image` tool.
- Direct HTTP calls to provider APIs (curl + endpoint).
- Video generation — see `ozon-carousel-video-pipeline` (or analog).
- Replacing existing product images on Ozon — see `ozon-product-image-remediation`.

## 1. Discover before guessing

The capability surface lives behind the `openclaw` CLI, not behind JS `exec` `tools.*` calls. Always walk the help tree before invoking.

1. `openclaw --help 2>&1 | grep -E "^\s+[a-z]+" | head -30` — find `capability` (alias `infer`).
2. `openclaw capability --help 2>&1 | head -20` — list capability areas: `image`, `audio`, `video`, `tts`, `embedding`, `model`.
3. `openclaw capability image --help 2>&1 | head -40` — list image subcommands: `generate`, `edit`, `describe`, `describe-many`, `providers`.
4. `openclaw capability image generate --help 2>&1 | head -50` — full flag matrix.

Completion: you have the exact flag list before writing the invocation.

## 2. Invoke generate

```
openclaw capability image generate \
  --model "minimax/image-01" \
  --prompt "<detailed product / scene prompt>" \
  --aspect-ratio "3:4" \
  --size "1024x1024" \
  --output "<abs-or-rel-path>.jpg" \
  --json
```

Flags actually present in `--help` output:
- `--model <provider/model>` — MiniMax image model is `minimax/image-01`. OpenAI slugs (`openai/...`) exist but must not be used without explicit user authorization; default to the configured local provider.
- `--prompt <text>` — descriptive prompt; front-load subject, lighting, background, prohibited elements.
- `--aspect-ratio <ratio>` — e.g. `16:9`, `3:4`, `1:1`. Observed: `--aspect-ratio 3:4 --size 1024x1024` returned `864x1152` (aspect ratio wins over size).
- `--size <WxH>` — pixel hint; optional when `--aspect-ratio` is set.
- `--output <path>` — destination file; extension drives format (`.jpg` → JPEG, `.png` → PNG).
- `--json` — emit structured JSON to stdout; required to capture the canonical output path.
- `--count <n>` — number of images.
- `--quality`, `--background`, `--resolution`, `--timeout-ms` — provider hints.

Run long calls with `--timeout-ms` or rely on the executor's `timeoutSeconds`; image generation can take 30–120s.

Completion: process exits 0.

## 3. Verify the output

The JSON payload is the source of truth — do not infer from the file alone.

1. Parse the `--json` stdout. Confirm `"ok": true` and at least one entry in `outputs[]`.
2. Read `outputs[0].path`, `mimeType`, `size`, `width`, `height`.
3. `ls -la <outputs[0].path>` to confirm the file is on disk.
4. Cross-check `width:height` matches the requested aspect ratio.
5. Use the first-class `image` tool to visually verify the AI image before composing overlays or pushing. Look for: wrong subject, hallucinated logos, off-style background, prohibited text.

Completion: file exists, dimensions match aspect ratio, visual content matches prompt intent.

## 4. Compose with PIL overlay (Ozon compliance)

After the AI image is verified, layer the Ozon compliance template (OE reference, fitment line, SKU watermark, category chip) using PIL on a 900×1200 white canvas. Keep the AI original in `.tmp_aigen/` and write the composited asset as the publishable file (`main_<SKU>_ai.jpg` etc.).

Always compose before pushing so the public asset is the compliant version, not the raw AI image.

Completion: composited image exists at the publishable path; raw AI image preserved locally in `.tmp_aigen/`.

## 5. Push and deliver

1. `git add <publishable-asset>` only — do not commit `.tmp_aigen/`.
2. `git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 commit -m "<SKU> main image (minimax/image-01 + Ozon template overlay)"`.
3. `git -c http.proxy=http://127.0.0.1:7897 -c https.proxy=http://127.0.0.1:7897 push origin main`.
4. jsDelivr URL: `https://cdn.jsdelivr.net/gh/<owner>/<repo>@main/<filename>`.
5. `curl -sIL <url>` — confirm HTTP 200.

Completion: jsDelivr URL returns 200 and the served bytes match the committed file.

## Common pitfalls — do NOT

- Do NOT call JS `exec` with `language: "javascript"` and `tools.search('image_generate')`. Catalog/provider tools are not exposed through the JS-exec surface in this environment; the entry point is the shell `openclaw` CLI. Multiple zsh parse errors confirm the surface mismatch.
- Do NOT call `openclaw image ...` as a top-level command — `image` is a subcommand of `capability` / `infer`.
- Do NOT default to OpenAI image models without explicit user authorization. Use the workspace's configured local provider (`minimax/image-01` in this environment).
- Do NOT skip `--output`; the CLI may write to a default location instead of the intended path.
- Do NOT pipe `--json` output through `tail -N` without checking that the JSON line survives — large JSON can wrap; prefer `python3 -c 'import json,sys; print(json.load(sys.stdin)["outputs"][0]["path"])'`.
- Do NOT publish the raw AI image; always compose with the Ozon compliance template first.

## Evidence

- Run `62c700a5-da2a-41f6-86da-32374f4fbd52`: agent tried JS `exec` `tools.search('image_generate')` six times, all returned zsh parse errors, before pivoting to `openclaw --help` → `openclaw capability image generate`, producing a valid 864×1152 JPEG on the first call with `transport: "local"`, `provider: "minimax"`, `model: "image-01"`.
- Flag surface observed in `--help` output; model identifier `minimax/image-01` confirmed by successful call.
- Aspect-ratio behavior (`3:4` overriding `1024x1024`) confirmed by returned dimensions in the JSON payload.
