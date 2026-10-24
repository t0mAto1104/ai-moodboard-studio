## 收藏图片，直接制作画板

- 从主页按标签或逐张选择 1–24 张收藏图片，设置名称、比例和布局后创建可编辑画板。
- 新增撤销重做、图层锁定与排序、多选操作、画布对齐、缩放及键盘快捷键。
- 支持文字字体类别、字号、粗体、颜色、行高、对齐；矩形与圆形色卡、透明度、背景与比例调整。
- 可从收藏继续添加图片、替换素材，或导入拥有使用权的本地图片。
- 保存与 PNG/PDF 导出保留样式、来源和许可清单；继续检查素材权限。
- 保留现有白色 Studio 设计和导航。未接入 Canva，不包含其模板。

## 下载与更新

下载 **AI-Mood-Board-Studio-0.2.0-macOS-arm64.dmg**，退出旧版后将新应用拖入 Applications 替换。建议更新前备份本地应用数据目录。原有收藏、项目和钥匙串配置仍在独立数据目录；不随安装包分发。

约 **317 MB**，面向 Apple Silicon Mac，目标 macOS 14+。包含 Python 与推理运行依赖，**不含视觉模型权重、开发者密钥或用户项目**。用户自行配置 API 和模型；无视觉模型时可使用基础排序。

[编辑器指南](https://github.com/t0mAto1104/ai-moodboard-studio/blob/v0.2.0/docs/editor-guide.md) · [视觉模型部署](https://github.com/t0mAto1104/ai-moodboard-studio/blob/v0.2.0/docs/model-setup.md) · [图库 API 申请配置](https://github.com/t0mAto1104/ai-moodboard-studio/blob/v0.2.0/docs/image-api-setup.md)

## 验证与范围

18 项前端、69 项后端、5 项模型准备工具测试通过。生产构建、冻结应用自检、原生窗口建板与保存、窗口关闭退出、只读镜像复制后的自检，以及外接 SigLIP 2 的 MPS 图文编码通过。[完整验证记录](https://github.com/t0mAto1104/ai-moodboard-studio/blob/v0.2.0/docs/release-0.2.0.md)。

仍为 **ad-hoc 签名预览版，尚未 Apple Developer ID 签名或公证**。实际验证 macOS 15.8.1 / M3；其它机器仍需验证，暂无 Intel / Windows 安装包。多页、组合编辑、协作和自由裁切焦点暂未实现。

随附 `.sha256` 校验文件和中英文安装说明。旧版 Release 保留。
