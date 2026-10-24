# 视觉模型准备与连接

安装包不包含模型权重，也不会自动下载。没有模型也能使用规则解析、检索、收藏、编辑和许可允许的导出；视觉排序会降级。

## 当前模型

- ID：`google/siglip2-base-patch16-224`
- 固定 revision：`75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2`
- 向量：768 维，不与其他模型或 revision 混用。
- 已验证完整目录约 1.54 GB（十进制）；另需运行时内存。
- [官方模型页面](https://huggingface.co/google/siglip2-base-patch16-224)。单独获取模型时应查看该版本的模型卡和许可。

## 已有部署目录

桌面版：设置 → 本机与缓存 → 选择文件夹 / 输入路径 → 连接模型。目录可以位于外接盘。连接记录保存到应用数据目录，不复制或修改权重。不要选择外层 `AI_Models`，应选择其中实际包含权重的目录。

目录应包含权重、Processor / Tokenizer 配置，以及原部署流程生成的版本清单：

```text
siglip2-base-patch16-224/
├── config.json
├── model.safetensors
├── preprocessor_config.json
├── tokenizer.json
├── tokenizer.model
├── tokenizer_config.json
├── special_tokens_map.json
├── README.md
└── deployment_manifest.json
```

应用检查必需文件、固定模型 ID / revision 和清单中的文件大小。版本清单是部署元数据，不是来自模型发布者的签名证明；不能单凭它判断未知来源文件可信。

## 方式 A：迁移已有模型（无需准备 Python）

将可信的完整模型目录连同 `deployment_manifest.json` 复制到目标电脑或外接盘，保留文件名和模型卡。接入时选择最内层模型目录。软件不把外接权重复制到内部磁盘；原始部署者应遵守模型许可和再分发条件。

## 方式 B：首次从 Hugging Face 下载

需要联网及 Python 3.12（仅模型准备工具需要；桌面应用平时启动仍不需要另装 Python）。没有 Python 可从 [Python 官方下载页](https://www.python.org/downloads/) 获取。先 [下载本项目源码 ZIP](https://github.com/t0mAto1104/ai-moodboard-studio/archive/refs/heads/main.zip) 并解压，或使用 Git 克隆；在解压后的项目目录打开终端。无需为准备模型安装 Node 或全部 PyTorch 依赖。请使用这里链接的 **main 源码 ZIP**；旧 Release 附带的源码快照可能没有新增的准备工具。

```sh
python3.12 -m venv .model-tools
.model-tools/bin/python -m pip install 'huggingface_hub==0.36.2'
.model-tools/bin/python scripts/install_vision_model.py --directory '/Volumes/YOUR_DISK/AI_Models/siglip2-base-patch16-224'
```

将 `YOUR_DISK` 替换为实际已挂载的磁盘名，不能原样照抄；也可以明确选择本机目录。建议目标磁盘预留至少 **3 GB**。模型文件实际合计约 **1.54 GB**，运行时内存另计；已在 16 GB M3 Mac 验证，其他机器需实际测试。

这个准备工具：

- 只从官方模型仓库下载固定完整 revision 的 8 个文件，不下载 Qwen 或本地大语言模型；公开模型不需要图库 API Key。
- 把权重和 HF / Xet 缓存明确放在所选目录或其父目录下，不使用默认内部模型缓存。
- 校验固定文件大小和 SHA256，生成应用需要的 `deployment_manifest.json`；只下载 Hugging Face 文件而没有此清单，应用选择器会拒绝连接。
- 不覆盖无关的已有文件；已有完整且符合版本的目录会验证后复用。由本工具标记的未完成下载可以再次执行相同命令继续；其他非空残缺目录需另选新目录。
- 外接盘未挂载时停止；下载不需要 `sudo`，也不会格式化磁盘。校验失败不写成功清单，不要通过手改清单跳过。

下载完成后，软件 → 设置 → 本机与缓存 → 选择文件夹 → 连接模型，再对获准素材执行一次视觉筛选。结果应显示实际模型、设备与分析数量；尚未执行推理时显示“尚未加载”属于按需加载行为。

### 已有目录的只读校验

下面的命令不访问网络、不下载权重，也不修改已有模型或清单；可以用标准 Python 运行：

```sh
python3.12 scripts/install_vision_model.py --directory '/Volumes/YOUR_DISK/AI_Models/siglip2-base-patch16-224' --verify-only
```

### 源码版指定目录

```sh
export SIGLIP_MODEL_DIR='/Volumes/YOUR_DISK/AI_Models/siglip2-base-patch16-224'
bash scripts/start.sh
```

已有设置中保存的模型路径优先于环境变量；切换时请在设置中重新选择。程序不会自动读取 `.env`。模型初次下载需要网络，连接完成后的推理使用本地离线文件。

## 其他视觉模型

当前只有上述 SigLIP 2 Base 实现可用。Qwen3-VL Embedding 等尚未接入，不要把其他模型放进此目录或仅改名称冒充 SigLIP。不同模型的向量不能混用；云端 LLM API Key 也不能代替视觉模型权重。

## 故障排查与官方依据

| 情况 | 处理 |
| --- | --- |
| 缺少 `deployment_manifest.json` | 使用准备工具核验完整目录后生成；不要复制示例中的占位值 |
| 版本 / SHA256 不匹配 | 确认固定 revision，保持原目录，另选空目录重新准备 |
| 下载中断 | 保持磁盘挂载，在本工具创建的目标目录再次执行同一命令 |
| 空间不足 | 确认模型及父目录缓存都在目标磁盘，预留至少 3 GB；不要删除其他文件腾空间 |
| 视觉筛选仍为基础排序 | 检查路径、外接盘和文件完整性，以及素材是否获准 ML 分析 |

[固定版本模型卡](https://huggingface.co/google/siglip2-base-patch16-224/blob/75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2/README.md) 标注 Apache-2.0；下载时保留模型卡并遵循上游许可。[Hugging Face 下载文档](https://huggingface.co/docs/huggingface_hub/v0.36.0/guides/download) 说明固定 revision、文件筛选和本地目录下载方式。本项目的固定文件摘要见 `scripts/siglip2-files.json`，核对日期 2026-10-24。

## 推理与缓存

模型按需加载且使用 `local_files_only=True`。自动选择 CUDA → MPS → CPU；模型加载失败时回退基础排序。HF / Torch 缓存路径指向模型所在父目录下的明确子目录，而非默认用户缓存位置。

分析从来源读取获准图片字节到内存，解码后提取向量；当前逐图、受锁控制。图片字节不会写入分析文件缓存。不具备持久存储许可时向量也不持久化。自动检测硬件不保证所有机器的速度表现，实际兼容性需在目标设备验证。

如需检查：连接目录后执行一次获准素材的视觉筛选，确认结果提示显示 SigLIP、设备及分析数量。开发者可执行 `scripts/smoke.py --vision`；此测试不接受元数据降级为成功。
