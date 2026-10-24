<div align="center">

<img src="docs/assets/wordmark.svg" alt="AI Mood Board Studio" width="720" />

**发现灵感，收藏线索，组合成你的下一张 Mood Board。**

A local-first visual research workspace with editable mood boards.

[下载 macOS 预览版](https://github.com/t0mAto1104/ai-moodboard-studio/releases/latest) · [使用指南](docs/user-guide.md) · [English](README.en.md) · [版本记录](CHANGELOG.md)

</div>

![桌面应用实际运行](docs/ui-desktop-package.png)

AI Mood Board Studio 将图片检索、标签收藏、本地视觉排序和可编辑画布放在同一个纯白工作区。核心流程在本机运行；云端大语言模型是可选项。

> **0.2.0 预览版** · Apple Silicon Mac · 安装包约 317 MB · 不含视觉模型、开发者密钥或用户数据 · 尚未完成 Apple Developer ID 签名和公证。

## 可以做什么

- **搜索灵感**：中文 / 英文需求，生成可修改的检索计划，聚合公开图库。
- **整理收藏**：自定义标签、多标签分组和未分组收藏，选取收藏图片直接制作画板。
- **视觉筛选**：可连接 SigLIP 2，在获准素材上分析语义、色彩、质量与重复度。
- **编辑画布**：三种布局；撤销重做、图层锁定、拖拽缩放、图片替换、文字样式和色卡。
- **本地保存**：项目、收藏和编辑状态存入 SQLite，重新启动后继续编辑。
- **合规输出**：许可满足要求时导出 PNG / PDF，并附署名和许可清单。

搜索、单张下载、AI 分析与拼贴导出分别检查权限；搜索得到图片不代表可以任意使用。

## 下载与安装

1. 前往 [Releases](https://github.com/t0mAto1104/ai-moodboard-studio/releases/latest)，下载 `.dmg`。
2. 打开镜像，将 **AI Mood Board Studio** 拖入 **Applications**。
3. 启动即可使用基础功能，按需配置图库密钥、云端 AI 和视觉模型。

| 项目 | 当前状态 |
| --- | --- |
| 安装包 | macOS / Apple Silicon（M 系列）；暂无 Intel / Windows 包 |
| 系统 | 目标 macOS 14+；实际验证 macOS 15.8.1 / M3 |
| 运行环境 | 已包含，无需另行安装 Python / Node |
| 视觉模型 | 不包含，不自动下载；缺少时使用基础排序 |
| Apple 签名 | ad-hoc 签名，尚未 Developer ID 签名或公证 |

若 macOS 阻止打开，先确认来源，再按系统提示处理；不要关闭全局安全防护。正式分发仍需完成签名、公证及其他电脑验证。[安装与排错](docs/user-guide.md)

## 第一次使用

**无密钥演示**：设置 → 开启「演示素材」，搜索时仅选择该来源 → 输入「简约冷色金属与磨砂玻璃」→ 收藏或创建画布 → 编辑 → 保存 / 导出。

演示素材是程序绘制的几何色彩研究图，用于验证流程，并非真实图库照片，也不是 AI 生成的不可编辑拼贴。真实素材请切换图库来源。[完整操作指南](docs/user-guide.md)

## AI 如何参与

| 任务 | 执行方式 |
| --- | --- |
| 基础中英文关键词解析 | 本机规则，无需密钥 |
| 增强自然语言检索计划 | 可选云端 LLM API / LiteLLM，自带密钥 |
| 图像 / 文本编码、二次排序 | 可选本机 SigLIP 2，需单独模型 |
| 颜色、去重、组合选择、布局 | 本机算法 |

不安装 Ollama，不运行本地 LLM。支持 OpenAI、Anthropic、Gemini、DeepSeek、Qwen、OpenRouter 和自定义 OpenAI-compatible API；模型 ID 可查询或手动填写。密钥由后端保存到系统钥匙串，不写入浏览器持久存储、Git 或项目导出。

视觉模型：`google/siglip2-base-patch16-224`，revision `75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2`，768 维。自动检测 CUDA → MPS → CPU。在设置中选择模型目录，可使用外接盘，不会复制权重到内部磁盘。[模型准备与连接](docs/model-setup.md)

远程视觉分析需要读取图片字节，当前在内存处理，不写图片文件缓存；仍需具备对应来源的分析权限。Unsplash 的本地 AI 分析需另行确认授权，普通 API Key 不自动提供该权限。

## 视觉模型安装

当前可用：**SigLIP 2 Base**，约 1.54 GB；Qwen 等尚未接入。安装包不含权重，也不会自行下载。

**已有完整目录**：复制模型文件及 `deployment_manifest.json`，在软件「设置 → 本机与缓存 → 选择文件夹」连接，可直接使用外接盘。

**首次下载**：先下载并解压 [源码 ZIP](https://github.com/t0mAto1104/ai-moodboard-studio/archive/refs/heads/main.zip)，在项目目录执行以下命令。Python 3.12 只用于模型准备；桌面应用日常使用不需要额外安装 Python。

```sh
python3.12 -m venv .model-tools
.model-tools/bin/python -m pip install 'huggingface_hub==0.36.2'
.model-tools/bin/python scripts/install_vision_model.py --directory '/Volumes/YOUR_DISK/AI_Models/siglip2-base-patch16-224'
```

把 `YOUR_DISK` 替换为实际已挂载的盘名，目标磁盘建议预留至少 3 GB。工具固定模型版本，核验大小与 SHA256，生成部署清单，并把权重及下载缓存留在指定磁盘；不覆盖无关已有文件。完成后在设置中连接该目录，对获准素材运行视觉筛选。[详细安装、迁移与排错](docs/model-setup.md)

## 图库 API 申请与配置

| 来源 / 官方入口 | 获取方式 | 软件中填写 |
| --- | --- | --- |
| [Unsplash 开发者平台](https://unsplash.com/developers) | 注册 / 登录 → Your apps → New Application → 查看 Keys | **Access Key**，不要填 Secret Key |
| [Pixabay API](https://pixabay.com/api/docs/) | 注册 / 登录后，在 API 文档页查看个人 Key | **API Key** |
| [Openverse](https://docs.openverse.org/api/) | 当前使用基础匿名搜索，无需申请 Key | 启用来源即可 |
| [Art Institute of Chicago](https://api.artic.edu/docs/) | 公开 API，无需注册 Key | 启用来源即可 |
| [The Met](https://metmuseum.github.io/) | 公开 API，无需注册 Key | 启用来源即可 |
| 演示素材 / 用户上传 | 无需图库账号；上传需确认使用权 | 软件内开启 / 导入 |

拿到 Key 后：**设置 → 图片来源 → 对应图库 → 粘贴并保存 → 启用 → 测试连接**；回到检索页，还需在本次来源菜单选中该图库。密钥只在本机钥匙串保存，不要贴到 GitHub。

Unsplash Demo 当前为 50 次 API 请求 / 小时，不是 50 张图片；更高额度需按官方 Production 流程申请。Pixabay 默认 100 次请求 / 60 秒，以账号和响应头为准。连接测试和下载事件也可能消耗 API 配额，避免反复测试。[逐步申请说明与错误排查](docs/image-api-setup.md)

图库密钥与云端大模型密钥不同。Unsplash / Pixabay 常规合规组合画布可导出；Unsplash ML 分析需额外授权，Openverse 索引素材未核实权利前仍作参考。各来源可能受网络、限流及素材权限影响。

没有接入或抓取 Pinterest。[素材许可](docs/licenses.md) · [收藏与下载](docs/library-and-downloads.md)

## 从源码运行

已验证 Python 3.12 / macOS arm64。Node 需满足 Vite 7：`^20.19.0 || >=22.12.0`。直接依赖已固定，其他平台尚未全面验证。

```sh
git clone https://github.com/t0mAto1104/ai-moodboard-studio.git
cd ai-moodboard-studio
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-tested.txt
npm --prefix apps/web ci
npm --prefix apps/web run build
bash scripts/start.sh
```

打开 <http://127.0.0.1:8765>，`Ctrl+C` 停止。启动脚本先迁移数据库，只监听本机。兼容旧开发环境的父目录 `.venv`，也可通过 `MOODBOARD_PYTHON` 指定解释器。

```sh
# 可选，连接现有模型，不会自动下载
export SIGLIP_MODEL_DIR='/Volumes/YOUR_DISK/AI_Models/siglip2-base-patch16-224'
export MOODBOARD_DATA_DIR='/absolute/path/to/moodboard-data'
bash scripts/start.sh
```

`.env.example` 仅供参考，程序不会自动加载 `.env`。桌面数据默认 `~/Library/Application Support/AI Mood Board Studio`，源码版默认 `.local/`；两者使用独立钥匙串服务，不自动迁移项目和密钥。

## 验证与开发

```sh
bash scripts/test.sh
# 可选：必须实际加载本地模型，降级会使测试失败
.venv/bin/python scripts/smoke.py --vision --output /tmp/moodboard-vision.json
```

已记录 **67 项后端、11 项前端测试通过**，并实际验证生产构建、独立 `.app` 启停、只读 DMG 搬移运行、收藏、项目重开、PNG/PDF 与署名导出，以及外接模型 CPU / MPS 编码。这不代表所有电脑、上游 API 或万张图片性能已经验证。

| 文档 | 内容 |
| --- | --- |
| [使用指南](docs/user-guide.md) | 搜索、收藏、编辑、导出与排错 |
| [图库 API 申请](docs/image-api-setup.md) | 注册入口、Key 类型、软件配置与配额 |
| [模型准备](docs/model-setup.md) | 固定版本、外接目录、离线加载 |
| [架构](docs/architecture.md) / [API](docs/api.md) | 模块与接口，运行后也可访问 `/docs` |
| [验证范围](docs/validation.md) / [性能](docs/performance.md) | 测试命令和测量限制 |
| [桌面构建](docs/desktop-packaging.md) | 打包、审计和签名状态 |
| [已知限制](docs/known-limitations.md) / [贡献指南](CONTRIBUTING.md) | 未完成事项与开发约定 |

## 权利与许可

本仓库暂未指定应用源码的开源许可证；公开可阅读不等于授予复制、修改或再分发许可。第三方依赖、模型和图库素材各自保留其许可条件。[权利说明](NOTICE.md)

### 从收藏制作画板

主页点击「制作画板」，可跨标签选择 1–24 张收藏图片，直接生成可编辑画板。支持文字与色卡、图层锁定与排序、撤销重做、图片替换、比例与背景、快捷键以及 PNG / PDF 导出。参见 [编辑器使用说明](docs/editor-guide.md) 与 [本轮验证记录](docs/editor-validation.md)。v0.2.0 安装包包含此轮编辑器更新。
