# isekai-live 第一版选材记录

研究日期：2026-10-31。目标是验证“静态一眼能认出，长按后出现一个短动作”的制作体验；保留 isekai-live 名字。

## 已制作的两个经典猫梗示例

- **OIIA 旋转猫**：沿用已有 MiaoTI 代表性 GIF，视觉确认是 Ethel 旋转二创，不是 Maxwell。转换为 480×480、3 秒、无音轨 H.264 MP4；封面来自同一输出视频的第零帧。原 GIF 约 0.91 秒，重复播放到 3 秒，未伪造更多原始动作。
- **Banana Cat 香蕉猫**：沿用 MiaoTI 的 CLING GIF，实际画面是穿香蕉外壳的小猫晃动。转换为 480×480、3.6 秒、无音轨 MP4；封面来自同一输出第零帧。CLING 是旧产品里的分类名，不是这个梗的原创名称。

两份都保留原宽高比并置于白底，没有生成替代图，也没有 AI 伪造原梗。原素材分辨率有限，不称高清原片。文件哈希、既有素材 URL、加工方式与权利边界见 `web/media/sources.json`。没有改动 MiaoTI 原文件。

## 热度与来源边界

[OIIA 传播整理](https://knowyourmeme.com/memes/oo-ee-a-e-a-cat-remixes)记录 2023 年 Bilibili 二创和 2024 年末 TikTok 再传播；[Banana Cat 传播整理](https://knowyourmeme.com/memes/sad-banana-cat)记录 2023 年 TikTok 猫咪短剧传播。这里使用这些资料核对“已有传播历史”，不是读取当日热榜。两者在网页里应标为“经典猫梗 / 示例”，不能标“今日爆款”或附无实际读取的点赞数。

一级平台参考为 [OIIA 社区账号](https://www.tiktok.com/@oicatofficial) 与 [Banana Cat 早期 TikTok 条目](https://www.tiktok.com/@happyhappiihappy/video/7211511707007487259)。本轮直接访问受平台限制，未绕过；原始 GIF 编辑者和最初下载地址未在旧素材记录中保留。二级传播资料不等于同一 GIF 的原创作者证明。

抖音[宠物 AI 动态壁纸案例](https://www.douyin.com/video/7680498205821242659)可作为内容形式线索，本轮未下载或复刻作者素材，也没有将其热度写成已验证。

## 本轮淘汰的误识别

MiaoTI 的 WOAH GIF 是大眼畸变灰猫，不能因为“震惊”就把它写成 Huh / Ben Cat。ZOOM GIF 是灰白猫晃动，不是文件分类名所暗示的奔跑。STARE 为橘猫凝视二创，缺少足够具体的原始身份链路，未选入。

## 发布与下一步

这些是第三方经典梗的代表性二创版本，现有站点中已存不等于取得通用商业许可。本轮用于受保护个人实验；没有对外发布小红书，没有宣传原创或免费商用授权。若用于公开内容推广，优先换成用户自有宠物原片，或对选定作者的具体素材确认发布范围并保留归因。

下一步最便宜的验证：让用户在同一网站上传一份自己喜欢的已保存视频，挑 1–4 秒和一张明确封面，与这两个经典示例比较；记录能否顺利导出以及是否愿意留下/分享。先验证制作与保存体验，再建立有日期和出处的真实热门候选清单。

## 独立站与产品设计修订

用户随后澄清：需要独立网站，网站杂货铺仅提供跳转链接；独立站公开访问，汇总继续密码保护。此前子路径方案不满足这一目标。新生产站为 <https://isekai-live.pages.dev/>。

本轮研究 [Screen Studio Guide](https://screen.studio/guide)、[CapCut 在线裁剪](https://www.capcut.com/tools/online-video-trimmer) 和 [LIVP](https://livp.app/video-to-live-photo)。采用清晰的导入→时间线→封面→导出任务顺序，预览为主，设置按职责切换，导出按用途选择。上游的 iPhone、壁纸、平台兼容性宣传未直接继承为本项目的实测结论。

新版使用独立的浅色产品外壳、深色预览画布和蓝色操作色；新增真实缩略帧时间轴、片段拖动、封面标记、声音预览、片段/封面/分享面板、用途式导出窗口和手机固定导出入口。媒体仍在浏览器本机处理，已验证的编码和元数据配对逻辑复用。

公开示例为 Dzkouslavia 的 [Black Cat walking](https://commons.wikimedia.org/wiki/File:Black_Cat_walking.webm)，文件专属许可段落明确 CC0 1.0；截取原片 1–5 秒、缩放并去音轨，封面来自同一视频。详情见 `web/media/open-cat-source.json`。它是功能演示，不是热门证据；OIIA 与香蕉猫原记录保留，但不进入公开独立站包。

## 用户反馈后的 AI 与彩色界面修订

用户认为黑白编辑器普通、AI 未体现，并要求多个真实高赞梗自行挑选。核心问题成立：原版 app.js 只有剪辑，没有 AI 服务。新方向为“异世界照相馆”：淡紫、蜜桃与酸黄，照片式比较窗口，真实风格样张放在主舞台，剪辑收进制作台。

参考 [DomoAI](https://help.domoai.app/en/articles/12958715-video-to-video) 的选风格流程与 [Krea](https://www.krea.ai/blog/how-to-generate-images-with-style-references-in-krea) 的可视参考。实际复用 img-comparison-slider 8.0.7（MIT，commit c73939d61c8fb010342c9910f1de420edbf0b067），保留完整许可；没有复制商业站品牌素材。React Bits 当前是 MIT + Commons Clause，不当作普通 MIT 组件库。

通过内置 image_gen 将同一 CC0 黑猫帧生成动画与黏土两张静态封面，保存为 web/media/cat-ai-anime.png 与 cat-ai-clay.png。完整最终提示词、工具与来源保存在 web/media/ai-covers-source.json。用户切换风格后可直接把该真实 AI 封面与原视频配对导出。它是 AI 封面，不是完整视频转绘；未开放在线收费 AI 生成，也不把滤镜或过渡称为 AI。

web/media/meme-candidates.json 收录 7 个精确链接候选。5 条 YouTube 帖子于 2026-10-31 从平台 UI 读取累计赞数，其余两条明确为有日期历史二级证据。猫梗选题单提供多选和复制，不下载或再分发未获授权的视频。近期“妙脆角维修猫”独立列为待核原帖线索：新榜 2026-09-29 截图记录 163 万赞，原作者注明禁止搬运，不能作为本站下载模板。

仍待验证：用户真正选择哪种梗、自己的素材在线 AI 生成服务、整段 AI 视频效果，以及 iPhone/小红书原生实况保存。当前制作台只调用本地视频处理。
