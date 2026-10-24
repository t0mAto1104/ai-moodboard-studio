# macOS 桌面安装包

采用 PyInstaller 打包 Python 后端和依赖，pywebview / 系统 WKWebView 显示已构建的 React 页面。服务只监听 127.0.0.1 的动态端口，窗口关闭后停止服务。用户不需要安装 Python、Node 或运行终端命令。

本包包含 PyTorch / Transformers 运行依赖，**不包含任何视觉模型权重**。模型单独部署，在设置中选择目录；不会自动下载。目录需包含原部署生成的 `deployment_manifest.json`，模型 ID 和 revision 必须匹配项目配置。无模型时降级为元数据排序。

桌面数据：`~/Library/Application Support/AI Mood Board Studio`。独立钥匙串服务：`AI Mood Board Studio Desktop`。开发目录 `.local`、API 密钥、收藏、项目、缓存均不进入安装包。卸载应用不会自动删除用户数据。连接外接模型盘不会复制权重到内部磁盘。

## 复现构建

在 Apple Silicon Mac 中，从仓库目录执行：

```sh
python3.12 -m venv .build/venv
.build/venv/bin/python -m pip install -r desktop/requirements-build.txt
npm --prefix apps/web ci
.build/venv/bin/python scripts/collect-package-notices.py
bash scripts/build-macos.sh
bash scripts/create-dmg.sh
```

直接依赖固定于 `requirements-tested.txt` / `desktop/requirements-build.txt`；本次完整构建环境版本在 `desktop/build-runtime-lock.txt`，第三方许可收集在 `desktop/THIRD_PARTY_NOTICES.txt`。构建日志、包内容检查见 docs 中对应报告。

## 独立应用测试

```sh
'.build/dist/AI Mood Board Studio.app/Contents/MacOS/AI Mood Board Studio' \
  --data-dir /tmp/moodboard-test-unique-data \
  --self-test-report /tmp/moodboard-test-unique.json
```

每次使用新的空数据目录。自检涵盖数据库迁移、前端资源、Mock 搜索、收藏分组、项目保存、PNG / PDF 与署名导出、系统钥匙串、LLM 和视觉运行依赖、无模型降级。可增加 `--check-model-dir '/Volumes/…/siglip2-base-patch16-224'` 实际编码一张图片和文本，不修改模型文件。

## 发布范围

当前是 macOS arm64 本地测试构建。目标最低 macOS 14；实际验证仅覆盖 macOS 15.8.1 / M3。本机通过不能替代其他电脑上的干净环境验收。Intel / Windows 需要各自在目标系统构建和测试。

应用使用 ad-hoc 签名，尚无 Developer ID 签名和 Apple 公证。供他人正式下载安装前，需要发布者配置 Apple Developer 证书并完成签名、公证和 stapling。不要通过关闭 Gatekeeper 作为安装流程。
