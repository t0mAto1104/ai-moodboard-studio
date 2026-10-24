# 验证范围

0.1.0 已在 macOS 15.8.1 / Apple M3 上运行验证。完整安装包与运行库不包含视觉模型文件。下面区分自动化、独立包、真实模型和第三方联网验证，避免将 Mock 成功等同于真实 API 成功。

| 层次 | 已记录结果 | 范围 |
| --- | --- | --- |
| Python / pytest | 60 passed | 规则解析、Schema、图库契约与失败、许可、算法、布局、项目、下载安全、收藏和模型目录 |
| React / Vitest | 9 passed | 主流程、来源设置、收藏标签、卡片、视觉入口 |
| 生产构建 | passed | TypeScript + Vite |
| Frozen app | passed | 新数据目录、迁移、静态页面、Mock 搜索、收藏、项目、PNG/PDF、署名与钥匙串运行库 |
| 安装镜像 | passed | 校验和、ad-hoc 签名完整性、只读挂载并从不同目录自检 |
| 原生窗口 | passed | 桌面窗口打开 / 关闭，关闭后动态 localhost 服务停止 |
| 独立模型 | CPU / MPS passed | 从外接目录加载固定版本，实际编码图片与文本，各 1×768 |

云端 LLM / 商业图库需要接收者自己的凭证；Release 不携带开发者账号。历史联网检查可能因上游规则、地区和限流变化而失效。ArtIC 图片和 Met 曾出现 403；不能保证每个来源随时可用。

## 复现

```sh
bash scripts/test.sh
.venv/bin/python scripts/smoke.py --output /tmp/moodboard-smoke.json
# 可选，需现有固定版本模型
.venv/bin/python scripts/smoke.py --vision --output /tmp/moodboard-vision.json
```

上述 smoke 使用临时数据库，不修改现有项目。安装包自检和构建见 [桌面文档](desktop-packaging.md)。机器可读概要见 [desktop-release-report.json](desktop-release-report.json)。

## 不应推断的结论

- 固定几何演示集不证明真实图像的检索相关性。评估目录中的描述尚需人工相关性标注；Precision@10、NDCG@10、人工保留率不能虚构。
- 单次冷启动不代表稳态吞吐量。没有完成一万张图片的完整压力测试。
- CPU / MPS 历史基准的沙箱上下文不同，不能据此宣称 CPU 必然更快或 MPS 必然更省内存。
- 本机验证不能代替其他 macOS 版本、Intel / Windows 或所有设备的安装验收。

详细延迟和内存口径见 [performance.md](performance.md)。
