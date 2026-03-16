# isekai-live

[English README](./README.md)

从指定封面图和视频出发，构建、提取、重混并导入可被 Photos 识别的 Live Photo 资产。

`isekai-live` 是一个偏创作工作流的命令行工具，适合这类场景：

- 用一张指定静态图作为 Live Photo 封面
- 用一段指定视频作为动态内容
- 提取并重混已有的 Live Photo
- 用 AI 生成风格化封面，再重新打包回 Live Photo

它不是完整编辑器，重点在于资产配对、打包，以及可重复执行的 CLI 工作流。

## 项目定位

大多数 Live Photo 工具要么偏拍摄，要么偏底层元数据处理。

这个项目把常见操作收敛成清晰的命令行工作流：

- `build`：由图片 + 视频构建 Live Photo 资产
- `extract`：从已有 Live Photo 中提取封面和视频
- `remix`：替换其中一侧并重新构建
- `ai-cover`：从已有封面生成新的 AI 风格封面

这个项目的价值不在于“从零发明 Live Photo”，而在于把工作流做得更清楚、可脚本化、便于反复试素材。

## 当前状态

- `build`、`extract`、`remix`：已实现
- `ai-cover --provider qwen`：已实现
- `ai-cover --provider gemini`：CLI 接口已预留，实际 API 还未实现
- `png` 封面可直接输入；在 `build` / `remix` 时会按需自动转成 `jpeg`

## 环境要求

- Python `>= 3.14`
- 推荐 macOS
- `pip install -e .`
- 如果要使用 Qwen AI 封面生成，需要 DashScope API key（`sk-...`）

## 安装

```bash
git clone https://github.com/farmcan/isekai-gate.git
cd isekai-gate
pip install -e .
```

## 快速开始

准备素材：

```text
assets/
├── cover.jpg
└── clip.mov
```

构建 Live Photo 包：

```bash
isekai-live build \
  --cover assets/cover.jpg \
  --video assets/clip.mov \
  --output-dir output
```

典型输出：

```text
Image: output/livephoto.jpg
Video: output/livephoto.mov
Package: output/livephoto.pvt
Asset ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

在 macOS Photos 中导入：

```bash
open output/livephoto.pvt
```

## 示例

提取已有 Live Photo：

```bash
isekai-live extract --input livephoto.jpg --output-dir extracted/
```

替换封面后重混：

```bash
isekai-live remix \
  --input original.jpg \
  --new-cover new_cover.jpg \
  --output-dir remixed/
```

使用 Qwen 生成风格化封面：

```bash
isekai-live ai-cover \
  --input assets/cover.jpg \
  --prompt "把这张照片改成高质量卡通插画风格，保留主体构图与姿态，颜色明快，细节干净" \
  --provider qwen \
  --qwen-key YOUR_DASHSCOPE_API_KEY \
  --output ai_cover.png
```

完整 AI 工作流：

```bash
isekai-live extract --input original.jpg --output-dir assets/

isekai-live ai-cover \
  --input assets/cover.jpg \
  --prompt "把这张照片改成高质量卡通插画风格，保留主体构图与姿态，颜色明快，细节干净，适合做 Live Photo 封面" \
  --provider qwen \
  --qwen-key YOUR_DASHSCOPE_API_KEY \
  --output ai_cover.png

isekai-live remix \
  --input original.jpg \
  --new-cover ai_cover.png \
  --output-dir remixed/

open remixed/livephoto.pvt
```

## 如何验证结果

验证要分两层看：

1. 资产层验证
- 确认生成了 `livephoto.jpg`、`livephoto.mov`、`livephoto.pvt`
- 确认图片和视频属于同一个 Live Photo 资产
- 确认能用 `extract` 反向提取出配对结果

2. Photos 层验证
- 把 `.pvt` 导入 macOS Photos
- 确认 Photos 将其识别为 Live Photo
- 确认长按 / 播放时行为正确

为什么必须这样验证：

只看到文件生成成功，并不能证明 Apple Photos 会把它当成真正可用的 Live Photo。端到端验收标准仍然是：`.pvt` 可导入，并且导入后的播放行为正确。

## AI 封面说明

- Qwen 走阿里云 DashScope 图生图接口
- 可以通过 `--qwen-key` 传 key，也可以设置 `QWEN_API_KEY`
- 生成结果会直接写入 `--output`
- 如果输出是 `png`，后续 `build` / `remix` 会自动转成 `jpeg` 再打包

## 官方测试素材

```bash
curl -LO https://raw.githubusercontent.com/RhetTbull/makelive/main/tests/test.jpeg
curl -LO https://raw.githubusercontent.com/RhetTbull/makelive/main/tests/test.mov

isekai-live build --cover test.jpeg --video test.mov --output-dir output
open output/livephoto.pvt
```

来源：[`makelive/tests`](https://github.com/RhetTbull/makelive/tree/main/tests)

## 实现说明

这个项目依赖 [`makelive`](https://github.com/RhetTbull/makelive) 完成 Live Photo 元数据写入和 `.pvt` 打包。

这一点应该明确写出来。这个项目本身的贡献在于围绕它补齐完整工作流：

- 清晰的 CLI 入口
- 可复现的输出结果
- `extract / remix` 循环
- AI 封面生成再回流到 Live Photo 打包

## License

MIT
