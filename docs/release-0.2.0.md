# v0.2.0 — 收藏建板与编辑器

2026-10-24。保留纯白 Studio 风格与导航，新增从自定义标签收藏创建画板，以及常用图层、历史、文字、图形和排版编辑能力。不是 Canva 接口集成，也不包含 Canva 模板或用户设计。

## 验证

- React/Vitest：18 项通过。
- Python/pytest：后端 69 项、模型准备工具 5 项，共 74 项通过。
- TypeScript/Vite 生产构建通过。现有主包大小提示与上游 httpx 测试弃用提示仍存在。
- 本地浏览器实际验证：收藏选图建板、文字编辑、拖拽、旋转、缩放手柄、锁定、撤销、保存重开及 PNG 导出。见 [编辑器验证](editor-validation.md)。

- 冻结应用独立自检通过：收藏建板、样式与背景保存、PNG/PDF、许可拒绝、钥匙串服务隔离和未安装模型时的基础功能。
- 原生 WKWebView 实际完成收藏建板、文字输入、对齐与保存；关闭后测试进程退出且本地端口释放。
- 外接 SigLIP 2 实际使用 MPS 执行图片与文本编码，均输出 (1, 768)；没有下载或复制权重。CPU 在本轮未重测。
- DMG 只读挂载、签名校验、复制至临时目录后的完整独立自检均通过，测试后已卸载镜像。
- 安装包 316,863,171 字节（约 317 MB），包内容审计通过。SHA256：`3e227d72ad63f97ef496fb656df36ecb84f5232362e5331544705701593ecf29`。
- 图库导出自检采用明确的 Mock 网络；本轮没有使用商业图库凭证发起真实请求。

机器可读记录：[冻结自检](desktop-020-frozen-test.json)、[外接模型](desktop-020-model-test.json)、[镜像复制自检](desktop-020-dmg-test.json)、[发布汇总](desktop-release-report.json)。

## 安装与升级

从 [Release](https://github.com/t0mAto1104/ai-moodboard-studio/releases/tag/v0.2.0) 下载 Apple Silicon DMG，退出旧版后把新应用拖入 Applications 替换。用户数据库与钥匙串仍保存在原应用目录，安装包不包含开发者数据或密钥。文档中的样式新增字段在现有 JSON payload 中保存，旧项目使用默认值，不需要重建数据库。

仍为 ad-hoc 签名预览，未 Developer ID 签名或 Apple 公证。目标 macOS 14+，本机验证 macOS 15.8.1 / M3；其它 Mac、Intel 与 Windows 未在本轮验证。不关闭系统安全防护。

包内包含 Python 和视觉推理依赖，但不包含视觉模型权重。SigLIP 2 仍需单独准备并选择目录；无模型继续使用基础排序。参见 [模型部署](model-setup.md)、[图库配置](image-api-setup.md) 和 [编辑器指南](editor-guide.md)。

多页、组合/解组、多人协作、自由裁切焦点和跨平台字体像素级一致性仍是后续工作。
