# isekai-live

[中文说明](./README.zh-CN.md)

Build, extract, remix, and import Live Photo-compatible assets from a chosen cover image and video.

`isekai-live` is a small CLI for creator-oriented Live Photo workflows:

- use a custom still image as the cover
- pair it with a chosen video
- extract and remix existing Live Photos
- generate a stylized cover with AI and package it back into a Live Photo

It is not a full editor. It focuses on asset pairing, packaging, and repeatable CLI workflows.

## Why This Project

Most Live Photo tooling either focuses on capture or on low-level metadata writing.

This project packages that into a clearer workflow:

- `build`: create a Live Photo pair from image + video
- `extract`: pull cover + video from an existing pair
- `remix`: replace one side and rebuild
- `ai-cover`: generate a new cover image from an existing one

The value is not "inventing Live Photo from scratch". The value is making the workflow explicit, scriptable, and easy to iterate on.

## Status

- `build`, `extract`, `remix`: implemented
- `ai-cover --provider qwen`: implemented
- `ai-cover --provider gemini`: CLI reserved, API integration not implemented yet
- `png` covers are accepted; `build` and `remix` convert them to `jpeg` automatically when needed

## Requirements

- Python `>= 3.14`
- macOS recommended
- `pip install -e .`
- for Qwen AI cover generation: a DashScope API key (`sk-...`)

## Install

```bash
git clone https://github.com/farmcan/isekai-gate.git
cd isekai-gate
pip install -e .
```

## Quick Start

Prepare:

```text
assets/
├── cover.jpg
└── clip.mov
```

Build a Live Photo package:

```bash
isekai-live build \
  --cover assets/cover.jpg \
  --video assets/clip.mov \
  --output-dir output
```

Typical output:

```text
Image: output/livephoto.jpg
Video: output/livephoto.mov
Package: output/livephoto.pvt
Asset ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Import into Photos on macOS:

```bash
open output/livephoto.pvt
```

## Examples

Extract a Live Photo pair:

```bash
isekai-live extract --input livephoto.jpg --output-dir extracted/
```

Remix with a new cover:

```bash
isekai-live remix \
  --input original.jpg \
  --new-cover new_cover.jpg \
  --output-dir remixed/
```

Generate a Qwen stylized cover:

```bash
isekai-live ai-cover \
  --input assets/cover.jpg \
  --prompt "Turn this photo into a clean cartoon illustration while keeping the original subject and composition." \
  --provider qwen \
  --qwen-key YOUR_DASHSCOPE_API_KEY \
  --output ai_cover.png
```

End-to-end AI cover workflow:

```bash
isekai-live extract --input original.jpg --output-dir assets/

isekai-live ai-cover \
  --input assets/cover.jpg \
  --prompt "Turn this photo into a clean cartoon illustration while keeping the original subject and composition. Bright colors, simple background, suitable for a Live Photo cover." \
  --provider qwen \
  --qwen-key YOUR_DASHSCOPE_API_KEY \
  --output ai_cover.png

isekai-live remix \
  --input original.jpg \
  --new-cover ai_cover.png \
  --output-dir remixed/

open remixed/livephoto.pvt
```

## How To Validate

Validation has two layers:

1. Asset-level validation
- confirm `livephoto.jpg`, `livephoto.mov`, and `livephoto.pvt` are generated
- confirm the image and video are paired as one Live Photo asset
- confirm `extract` can recover the pair

2. Photos-level validation
- import the `.pvt` package into macOS Photos
- verify Photos recognizes it as a Live Photo
- verify press-and-hold / playback behaves correctly

Why this matters: file generation alone does not prove Apple Photos will accept the result as a real Live Photo. The final acceptance test is Photos import and playback behavior.

## AI Cover Notes

- Qwen uses Alibaba DashScope image-to-image generation
- pass the key with `--qwen-key`, or set `QWEN_API_KEY`
- the generated output is written to `--output`
- if that output is `png`, later `build` / `remix` converts it to `jpeg` automatically for Live Photo packaging

## Official Sample Files

```bash
curl -LO https://raw.githubusercontent.com/RhetTbull/makelive/main/tests/test.jpeg
curl -LO https://raw.githubusercontent.com/RhetTbull/makelive/main/tests/test.mov

isekai-live build --cover test.jpeg --video test.mov --output-dir output
open output/livephoto.pvt
```

Source: [`makelive/tests`](https://github.com/RhetTbull/makelive/tree/main/tests)

## Implementation Notes

This project relies on [`makelive`](https://github.com/RhetTbull/makelive) for Live Photo metadata writing and `.pvt` packaging.

That dependency should be explicit. The contribution here is the workflow glue around it:

- clear CLI entrypoints
- reproducible outputs
- extract / remix loop
- AI cover generation feeding back into Live Photo packaging

## License

MIT
