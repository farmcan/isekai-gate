# isekai-live

中文在前，English below.

`isekai-live` is a Python CLI for building a Live Photo-style asset pair where the cover image and the motion video intentionally present different identities, such as "anime cover, real-person playback".

## 中文

### 项目目标

这个项目用来生成一组可被 Apple Photos 识别的 Live Photo 资源：

- 一张静态封面图
- 一段动态视频
- 一份可导入 Photos 的 `.pvt` 包

它适合做这种效果：

- 相册封面是 AI 动漫图
- 点开或导入后，动态内容是真人视频

### 当前实现

当前版本提供一个本地 Python CLI：

- 输入一张封面图
- 输入一段视频
- 复制到输出目录
- 为图片和视频写入相同的 Live Photo Content Identifier
- 生成 `.pvt` 包，方便在 macOS Photos 中导入验证

输出内容：

- `livephoto.jpg` 或 `livephoto.heic`
- `livephoto.mov` 或 `livephoto.mp4`
- `livephoto.pvt`

### 为什么不走 ffmpeg + exiftool

这个项目一开始验证过 `ffmpeg + exiftool` 路线，但没有作为第一版方案保留，原因是：

- `exiftool` 对 Live Photo 相关 Apple 元数据并不总是能稳定写入
- `ffmpeg` 更适合媒体转码，不适合充当 Apple Live Photo 元数据的唯一构建器
- 实际运行时，这条链路已经出现了标签写入告警和容器处理问题
- 对这个项目来说，目标不是“文件里有几个字段”，而是“系统真的认它是 Live Photo”

因此当前版本采用更稳妥的方式：通过 Python 调用基于 Apple 原生框架的实现来写入配对元数据。

### 安装

要求：

- macOS
- Python 3.14+

安装依赖：

```bash
python3 -m pip install --user --break-system-packages -e .
```

### 一条命令跑起来

如果你已经在仓库根目录，并且已经安装了依赖，直接执行：

```bash
PYTHONPATH=src python3 -m isekai_live --cover cover.jpg --video source.mov --output-dir out && open out/livephoto.pvt
```

这条命令会：

- 生成 `out/livephoto.*`
- 生成 `out/livephoto.pvt`
- 自动交给 macOS 打开，用于导入 Photos 预览

### 用法

```bash
PYTHONPATH=src python3 -m isekai_live --cover cover.jpg --video source.mov --output-dir out
```

或者安装脚本入口后直接运行：

```bash
isekai-live --cover cover.jpg --video source.mov --output-dir out
```

如果你只想看帮助：

```bash
PYTHONPATH=src python3 -m isekai_live --help
```

### 输出验证

当前仓库已经验证过以下结果：

- 命令能生成输出图片
- 命令能生成输出视频
- 命令能生成 `.pvt` 包
- 输出图片和视频具有相同的 Live Photo ID

验证方式示例：

```bash
python3 - <<'PY'
from pathlib import Path
from makelive import live_id, is_live_photo_pair

image = Path("out/livephoto.jpg")
video = Path("out/livephoto.mov")

print(live_id(image))
print(live_id(video))
print(is_live_photo_pair(image, video))
PY
```

如果三项结果一致，说明文件对已经被正确标记为同一组 Live Photo 资源。

### 如何预览

`HTML` 只能做效果模拟，不能验证 Apple 是否真的认这组文件是 Live Photo。

更可靠的预览方式是：

1. 把 `.pvt` 包导入 macOS Photos
2. 或把生成的资源同步到 iPhone 相册
3. 在系统相册里检查是否按 Live Photo 方式播放

最快路径：

```bash
PYTHONPATH=src python3 -m isekai_live --cover cover.jpg --video source.mov --output-dir out && open out/livephoto.pvt
```

### 项目状态

当前版本是第一版 CLI 骨架，重点在于：

- 生成可验证的资源对
- 提供稳定的命令行接口
- 为后续自研元数据写入、Photos 导入、AI 工作流集成留出接口

## English

### Goal

`isekai-live` builds an Apple Photos-compatible Live Photo asset pair:

- one still cover image
- one motion video
- one `.pvt` package for import into Photos

The intended use case is a contrast effect such as:

- anime-style cover image
- real-person motion playback

### Current Scope

The current version ships a local Python CLI that:

- accepts a cover image and a source video
- copies them into an output directory
- writes a shared Live Photo content identifier into both assets
- creates a `.pvt` package for easier Photos import and validation

Generated files:

- `livephoto.jpg` or `livephoto.heic`
- `livephoto.mov` or `livephoto.mp4`
- `livephoto.pvt`

### Why Not ffmpeg + exiftool

This project tested an `ffmpeg + exiftool` path early on, but did not keep it as the main implementation because:

- `exiftool` is not a reliable single solution for all Apple Live Photo metadata cases
- `ffmpeg` is excellent for media processing, but not an ideal sole builder for Apple-specific pairing metadata
- real execution exposed tag-writing warnings and container handling issues
- the real success criterion is not "some fields exist", but "Apple systems recognize the pair as a Live Photo"

For that reason, the current implementation uses a Python wrapper around a native-framework-based approach.

### Install

Requirements:

- macOS
- Python 3.14+

Install the project:

```bash
python3 -m pip install --user --break-system-packages -e .
```

### One-Liner

If you are already in the repository root and dependencies are installed, run:

```bash
PYTHONPATH=src python3 -m isekai_live --cover cover.jpg --video source.mov --output-dir out && open out/livephoto.pvt
```

This command will:

- generate `out/livephoto.*`
- generate `out/livephoto.pvt`
- hand the package to macOS for Photos import preview

### Usage

```bash
isekai-live --cover cover.jpg --video source.mov --output-dir out
```

If you have not installed the entrypoint yet:

```bash
PYTHONPATH=src python3 -m isekai_live --cover cover.jpg --video source.mov --output-dir out
```

If you only want help output:

```bash
PYTHONPATH=src python3 -m isekai_live --help
```

### Validation

This repository has already validated the following:

- the CLI generates an output image
- the CLI generates an output video
- the CLI generates a `.pvt` package
- the image and video share the same Live Photo ID

Validation example:

```bash
python3 - <<'PY'
from pathlib import Path
from makelive import live_id, is_live_photo_pair

image = Path("out/livephoto.jpg")
video = Path("out/livephoto.mov")

print(live_id(image))
print(live_id(video))
print(is_live_photo_pair(image, video))
PY
```

Matching results indicate that both files are tagged as the same Live Photo pair.

### Preview

An `HTML` page can simulate the effect, but it cannot prove that Apple Photos recognizes the output as a Live Photo.

For real validation, use:

1. import the `.pvt` package into macOS Photos
2. or sync the generated assets to an iPhone
3. verify playback in the system Photos app

Fastest path:

```bash
PYTHONPATH=src python3 -m isekai_live --cover cover.jpg --video source.mov --output-dir out && open out/livephoto.pvt
```

### Status

This is the first CLI-focused version. Its priorities are:

- generating verifiable asset pairs
- providing a stable command-line interface
- leaving room for future native metadata work, Photos import automation, and AI pipeline integration
