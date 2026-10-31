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

## 2026-11-01：榜单对照、产品路线与内容联动

本轮是研究和方案，不修改线上产品，不付费生成，不发帖，不新增定时采集。观察日期为北京时间 2026-11-01。

### 可核验的发现入口

- [小红书官方 vibecoding 作品榜](https://cowork.xiaohongshu.com/s/vibe-app-rank/)：浏览器实际切换并读取“图像创作”和“互动玩法”。平台注明按热度、活跃、新鲜度综合推荐；累计使用不是独立用户、完成、分享或收入。两类各 60 条可见行已保存在本地研究快照。
- 图像类具体对照：POVY 的照片风格包装（50.6 万累计使用）、CUT MOMENT 的打孔图像效果（49.3 万）、拼豆工坊（26.2 万）、梗图表情包制作器（12.3 万）、可旋转吧唧（3.6 万）、双图揭晓作品（4,101）。这些是榜单介绍和平台字段；原帖网页提示当前无法浏览、要求 App，不能据此宣称已经试玩，不能凭介绍断定其 AI 技术实现。
- 原帖分别为 [POVY](https://www.xiaohongshu.com/explore/6a955e430000000021030c12)、[CUT MOMENT](https://www.xiaohongshu.com/explore/6a7efa6c0000000033011e2f)、[拼豆工坊](https://www.xiaohongshu.com/explore/6a8d0e830000000016008e2b)、[梗图制作器](https://www.xiaohongshu.com/explore/6a9e7bfb000000002b002d5b)、[吧唧生成器](https://www.xiaohongshu.com/explore/6a9ffb040000000028002604)、[双图拼法](https://www.xiaohongshu.com/explore/6accc8f9000000001a02a529)。没有绕过 App 或登录限制。
- [新红](https://xh.newrank.cn/) 是第三方内容研究服务。其[官方历史功能说明](https://www.newrank.cn/article/detail/24858)记载爆款/暴增笔记、热门品类话题等功能；本轮未读取当前完整榜，不把 2023 年说明或估算数当实时热榜。千瓜主页可读取，详细榜读取失败且存在登录入口，本轮无实测数据。
- [Product Hunt](https://www.producthunt.com/) 适合发现完整产品和发布包装；票数是平台投票，不是活跃用户。[Hugging Face Spaces](https://huggingface.co/spaces) 和 [Replicate Explore](https://replicate.com/explore) 适合发现可运行模型/样例，仓库点赞与模型运行次数不等于消费需求或独立用户。

### 产品判断与取舍

推断：上述视觉工具把入口表述成一个具体成品或动作。不能把同行累计使用归因于这种包装，但它值得作为本站的验证方向。保留 isekai-live 名字，把它定位为“让自己的猫格、宠物或演奏片段变成可分享的异世界瞬间”。差异应是已有内容联动、短交互和实况保存，通用 AI 视频编辑可先用现成产品，不重复建设。

首页建议以 3 个具体内容模板开场：猫猫出道、打工猫反应、我的演奏小舞台。每个模板先展示真实原片与生成结果，让用户再决定放入自己的内容；风格名称和高级参数退到模板内。此为待验证模板，不声称已经制作或流行。结果页承担对比、长按、保存、换一个世界和再做同款；选取可公开使用的原片，不把热门帖子链接转为下载素材库。

### 最少增量的实现顺序

1. 先用已有生成产品/接口，对同一份已授权素材做少量真实效果试验；记录身份保持、动作、生成等待、失败和单次消耗。效果不足就调整模板，不先扩展整套生成平台。
2. 第一条站内闭环是用户视频本地抽一帧 → 服务端生成 AI 封面 → 带回浏览器 → 复用现有自选封面和 Live Photo 配对导出。现有预生成样张不能替代这条自有素材链路。生成帧需要上传时明确告知，不能继续笼统宣传全部文件留在本机。
3. 新增一个薄的异步生成适配层：Worker 只做参数校验、密钥保管、作业提交和状态读取；作业元数据与临时媒体分别按需要使用 D1/R2。首次只接一个供应商、少量风格并设置费用/重试上限。浏览器继续剪辑/封装；不要在边缘 Worker 内训练或运行大型视频模型。用户私人结果须由作业会话鉴权读取，公用模板与私人结果分开，临时媒体可删除。
4. 真正整段转绘是第二条能力：先裁短片段再调用视频编辑模型，输出实际 AI 视频后才标“AI 动态”；与“AI 封面＋原片动态”分别标注。已有 Python video-style-transform 适配可参考，但当前模型可用性、账户资格和质量必须重新真实调用验证，旧样片不证明网站已经接入。

验收以一份自有/授权输入从上传、真实生成、对比到导出为准；记录同一资源的 Apple 解码，iPhone 和平台原生保存另做设备验收。生成效果、等待或费用不满足目标时停止扩展，不能靠更多界面遮盖未跑通的链路。

### 现有内容联动

- **MiaoTI → isekai-live**：猫格结果页增加“把这个猫格做成实况”的明确入口，只传模板/风格标识；不在链接塞用户答案、私人图片或访问凭据。现有猫格小剧场是本地对照小样，不能当作已验证提升分享的机制。优先用自有或许可明确素材。
- **Miao Beat → isekai-live**：当前源码已有 MediaRecorder + canvas.captureStream 的视频导出，按浏览器支持输出 MP4/WebM。第一版先“保存演奏视频 → 导入实况工具”，这是最省新代码的连接；一键跨站传文件后续再做，不能只跳转空页面就称联动完成。
- **内容发布 → 做同款 → 再发布**：用同一模板的原片/AI 结果/实况演示组织短内容，作品卡带可识别模板名，接回同一模板入口。平台原生玩法与站外链接的进入条件不同，站外回流须实测，不假定能直接复制官方榜流量。
- Miao Beat 当前 family-referrals.js 已有匿名站间 click/arrival 框架，但允许列表未纳入 isekai-live。可复用这套口径接站间来源，再单独记录选择模板、生成成功、导出完成；点击/到达不等于真实分享或设备保存。第一轮手动策展和小样验证，不启用自动追榜、自动发帖。

### 同类产品与工程核验

- [Krea Nodes](https://www.krea.ai/docs/user-guide/features/nodes) 已提供把生成工作流包装成简化 App、分享及嵌入的机制；需要账号和功能权限。它可以先作为效果试验工具，不重复造通用节点编辑器。参考交互而非复制其商业 UI 与资产，本轮没有调用或验证账户权限。
- [fal Wan VACE Video Edit](https://fal.ai/models/fal-ai/wan-vace-apps/video-edit/api) 是现成异步视频编辑接口，官方当前标为 Wan 2.2 VACE Fun，有 submit/status/result 及输出视频地址。官方 [fal-js](https://github.com/fal-ai/fal-js/tree/8086bfc4a1957e43ead8646439935b6cc25e627e) 代码为 MIT；主分支 client 仍是 alpha，不直接当稳定版引入。接口需要有效密钥与余额，本轮未生成、未测等待/失败计费/账单。
- [VACE 源码](https://github.com/ali-vilab/VACE/tree/48eb44f1c4be87cc65a98bff985a26976841e9f3) 及相应 Wan2.1 权重有 Apache-2.0 来源；依赖 Python、CUDA、PyTorch、模型权重等，不适合作为首个网页样例的自建后端。当前托管 fal 模型不能自动视作同版本开源仓库部署。
- [motion-live-photo](https://github.com/flashlab/motion-live-photo/tree/48b884713c496ed4e4ad5ba688e84e6eb82ca059) 是 MIT 本地媒体工具，可定点参考 Motion Photo helper。本站已有本地导出，不整站迁移 React；Android Motion Photo JPEG 和 Apple 配对 JPEG/MOV 各自验收。

建议下一次真正付费生成前，先确定一个目标：若验证 AI 封面，就上传一张用户帧；若验证“异世界动态”，就只做一个有权使用的 3 秒片段、一个风格的真实视频编辑试验。把输入、模型、提示词、request_id、结果和成本留下，再决定是否接入网页或扩成多模板。当前无付费作业和外部生成成本发生。
