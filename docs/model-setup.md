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

## 首次获取模型

当前版本**尚无面向新用户的一键模型安装器**。可使用可信的、针对上述固定版本创建的完整部署目录，连同 `deployment_manifest.json` 一起迁移；遵守模型的再分发条件。只有 Hugging Face 下载文件、没有本项目版本清单的目录，会被选择器拒绝。

如由开发者手动准备：使用 Hugging Face 官方客户端指定上述完整 revision，将文件和 HF 缓存下载到明确选择的目标磁盘；核对上游文件及内容哈希，然后生成清单。格式如下，`files` 需列出全部实际文件；`bytes` 和 `sha256` 必须计算，不要照抄占位值：

```json
{
  "repo": "google/siglip2-base-patch16-224",
  "revision": "75de2d55ec2d0b4efc50b3e9ad70dba96a7b2fa2",
  "files": [{"name": "config.json", "bytes": 253, "sha256": "actual-file-sha256"}]
}
```

源码版也可在启动前设置 `SIGLIP_MODEL_DIR`。本项目不提供模型权重的 GitHub Release，也不要求下载到 Mac 内部磁盘。

## 推理与缓存

模型按需加载且使用 `local_files_only=True`。自动选择 CUDA → MPS → CPU；模型加载失败时回退基础排序。HF / Torch 缓存路径指向模型所在父目录下的明确子目录，而非默认用户缓存位置。

分析从来源读取获准图片字节到内存，解码后提取向量；当前逐图、受锁控制。图片字节不会写入分析文件缓存。不具备持久存储许可时向量也不持久化。自动检测硬件不保证所有机器的速度表现，实际兼容性需在目标设备验证。

如需检查：连接目录后执行一次获准素材的视觉筛选，确认结果提示显示 SigLIP、设备及分析数量。开发者可执行 `scripts/smoke.py --vision`；此测试不接受元数据降级为成功。
