# AI Mood Board Studio 0.1.0 — macOS Preview

本地优先的图片检索、标签收藏与可编辑情绪板工作区。

## 下载 / Download

- `AI-Mood-Board-Studio-0.1.0-macOS-arm64.dmg`：Apple Silicon Mac，316,176,384 bytes（约 316 MB）。
- `.dmg.sha256`：安装包 SHA256 校验文件。
- `安装说明.txt`：简要安装与模型连接说明。

打开 DMG，将应用拖入 Applications。运行环境已包含；不需要额外安装 Python / Node。**不包含视觉模型权重、开发者 API Key、项目或收藏。**

The installer includes the application runtime, but no model weights, developer credentials or user data. Download, drag into Applications, and configure your own providers. Optional vision connects a separately prepared model folder.

## 功能

中英文检索计划、多来源图片搜索、自定义标签收藏、可选本地 SigLIP 2 排序、三种可编辑布局、项目保存重开、许可允许的单张下载与 PNG/PDF + 署名导出。无需账号即可用明确标注的演示素材验证主流程。

## 兼容与验证

目标 macOS 14+ / Apple Silicon；实际测试 macOS 15.8.1 / M3。没有 Intel 或 Windows 包。60 项后端、9 项前端测试通过；实际验证独立应用启停、只读 DMG 搬移运行、项目与 PNG/PDF 流程，以及外接模型 CPU / MPS 编码。图库和云端服务的可用性依赖各自网络、凭证和规则。

**当前只有 ad-hoc 签名，尚未使用 Apple Developer ID 签名或公证。** 其他电脑可能阻止打开；先确认来源，再按 macOS 的系统提示处理，不要关闭全局安全防护。正式签名和更多目标机器验收仍是后续工作。

模型、AI/ML 使用权限与图库密钥均由使用者自行准备。没有模型时使用基础排序；云端 AI 未配置时使用本机规则。当前没有一键模型安装器、自动更新或开发版数据自动迁移。

详见仓库 README、docs/user-guide.md、docs/model-setup.md 与 docs/known-limitations.md。应用源码尚未选定开源许可；第三方依赖、模型和素材各自许可继续适用。
