# isekai-live

[中文说明](./README.zh-CN.md)

Build a Live Photo from a chosen still image and a chosen video, then export assets that Photos can actually import.

At a glance, the workflow looks like this:

- pick the cover you want people to see first
- pick the video you want to play on press
- build or remix the Live Photo package
- import it into Photos and verify the real result

This project is for creator-oriented workflows, not for full photo or video editing.

## Why It Is Interesting

Most Live Photo tooling focuses on capture, or on low-level metadata writing.

`isekai-live` is more specific: it lets you decouple the cover and the motion.

That means workflows like:

- an AI-generated portrait as the cover, with a real selfie video underneath
- a restored old photo as the cover, with a family clip as the motion
- an illustrated pet portrait as the cover, with the real pet video underneath

The result is not just "a moving photo". It is a deliberately designed preview-to-reveal experience.

## What The CLI Does

- `build`: create a Live Photo pair from image + video
- `extract`: pull cover + video from an existing Live Photo pair
- `remix`: replace one side and rebuild
- `ai-cover`: generate a stylized cover image from an existing one
- `ai-video`: generate a stylized video from an existing clip

## Status

- `build`, `extract`, `remix`: implemented
- `ai-cover --provider qwen`: implemented
- `ai-video --provider qwen`: implemented
- `ai-cover --provider gemini`: CLI reserved, API integration not implemented yet
- `png` covers are accepted; `build` and `remix` convert them to `jpeg` automatically when needed

## Install

```bash
git clone https://github.com/farmcan/isekai-gate.git
cd isekai-gate
pip install -e .
```

Requirements:

- Python `>= 3.14`
- macOS recommended
- for Qwen AI cover generation: a DashScope API key (`sk-...`)

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

## Two Useful Examples

Remix an existing Live Photo with a new cover:

```bash
isekai-live remix \
  --input original.jpg \
  --new-cover new_cover.jpg \
  --output-dir remixed/
```

Generate a stylized Qwen cover, then package it back into a Live Photo:

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

Stylize a source video with Qwen:

```bash
isekai-live ai-video \
  --input-video clip.mov \
  --style anime \
  --provider qwen \
  --qwen-key YOUR_DASHSCOPE_API_KEY \
  --output stylized.mp4
```

## What A Live Photo Really Is

From a user perspective, a Live Photo looks like one photo.

From an implementation perspective, it is closer to a paired asset:

- one still image for preview
- one short video for motion
- one shared identifier that lets Photos treat them as one Live Photo

That is why file generation alone is not enough. The final acceptance test is whether Photos imports and plays it correctly.

## How To Validate

Validation has two layers:

1. Asset-level validation
- confirm `livephoto.jpg`, `livephoto.mov`, and `livephoto.pvt` are generated
- confirm the image and video are paired as one Live Photo asset
- confirm `extract` can recover the pair

2. Photos-level validation
- import the `.pvt` package into macOS Photos
- verify Photos recognizes it as a Live Photo
- verify press-and-hold or playback behaves correctly

Why this matters: a command finishing successfully does not prove Apple Photos will accept the result as a real Live Photo.

## AI Cover Notes

- Qwen uses Alibaba DashScope image-to-image generation
- pass the key with `--qwen-key`, or set `QWEN_API_KEY`
- the generated output is written to `--output`
- if that output is `png`, later `build` or `remix` converts it to `jpeg` automatically for Live Photo packaging
- `ai-video` uses Qwen video style transformation and currently supports preset styles such as `anime`

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

That dependency is intentional and explicit. The contribution here is the workflow around it:

- clear CLI entrypoints
- reproducible outputs
- extract and remix loops
- AI cover generation feeding back into Live Photo packaging

## License

MIT
