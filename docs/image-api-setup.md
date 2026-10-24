# 图库 API 申请与连接

以下步骤对应当前已接入的来源，官方页面核对日期：2026-10-24。配额和申请界面可能调整，以各自后台及官方文档为准。图库密钥与云端大模型密钥不是同一类，不能互相代用。

## 快速选择

| 来源 | 是否需要申请 Key | 官方入口 | 在软件中填写 |
| --- | --- | --- | --- |
| Unsplash | 需要开发者应用 | [开发者平台](https://unsplash.com/developers) / [我的应用](https://unsplash.com/oauth/applications) | **Access Key**，不是 Secret Key |
| Pixabay | 需要注册并登录 | [API 文档与个人 Key](https://pixabay.com/api/docs/) | **API Key** |
| Openverse | 基础匿名搜索无需 | [官方 API](https://api.openverse.org/v1/) / [说明](https://docs.openverse.org/api/) | 不填 Key，启用即可 |
| Art Institute of Chicago | 无需 | [官方文档](https://api.artic.edu/docs/) | 不填 Key，启用即可 |
| The Met | 无需 | [官方文档](https://metmuseum.github.io/) | 不填 Key，启用即可 |
| 演示素材 | 无需账号和网络 | 软件内置 | 开启「演示素材」 |

## Unsplash

1. 注册或登录 [Unsplash](https://unsplash.com/)，进入开发者平台与「Your apps」。
2. 选择 **New Application**，自行阅读平台要求，填写你的应用名称与用途，例如本地设计灵感检索和 Mood Board 制作。
3. 在该应用的 Keys 中复制 **Access Key**；当前公开图片搜索不需要填写 Secret Key 或个人 OAuth Token。
4. 软件 → 设置 → 图片来源 → Unsplash，粘贴到 API Key 输入框并保存，启用来源，再点击「测试连接」。
5. 回到检索页，在来源菜单选中 Unsplash，尝试搜索 `metal texture` 等简短英文词。

官方目前说明 Demo 配额为 **50 次 API 请求 / 小时**。这不是 50 张图片：搜索分页、查询扩展、下载事件都可能产生 API 请求；图片文件请求本身不计入该 JSON API 配额。需要更高额度时，按照应用后台的 **Apply for Production** 流程申请审核，不由本软件自动开通。[注册与限流文档](https://unsplash.com/documentation)

本软件保留官方图片热链接、作者 / Unsplash 署名以及选择、下载和导出事件上报。普通 Access Key 不自动包含 AI/ML 权限；只有已有相应授权时才开启「本地视觉分析（已获授权）」。常规合规拼贴导出与 ML 授权分开处理。

## Pixabay

1. 注册或登录 [Pixabay](https://pixabay.com/)。
2. 打开 [API 文档](https://pixabay.com/api/docs/)，在登录状态查看页面提供的个人 API Key；未登录时页面可能只提示登录。
3. 软件 → 设置 → 图片来源 → Pixabay，输入 API Key、保存、启用并测试连接。
4. 检索页选中 Pixabay，再执行搜索。

官方当前默认 **100 次请求 / 60 秒**，实际以响应头与账号配置为准。API 搜索响应应缓存 24 小时，不允许系统性批量下载。临时搜索预览可以使用返回的图片 URL；持久画布使用本地副本，避免永久热链接。[API 文档](https://pixabay.com/api/docs/)

符合 Content License 的组合画布可以导出；仅缩放或裁切单张图片不作为新的组合创作放行。商标、肖像及其他第三方权利仍需结合用途判断。[内容许可](https://pixabay.com/service/terms/)

## 三个无需 Key 的公开来源

- **Openverse**：在设置中启用，并在检索页勾选即可。匿名访问受限流约束；当前软件使用匿名路径，没有提供 Openverse OAuth 配置入口。索引中的许可标签不等于原站权利已核实，未核实的素材仍作参考。
- **Art Institute of Chicago**：无需注册 Key，直接启用。使用官方 `is_public_domain` 与 `image_id` 等字段检查素材；允许访问的检索元数据不保证图像服务器在每个地区都可用。[认证说明](https://api.artic.edu/docs/#authentication)
- **The Met**：无需 Key，直接启用。软件使用新版 `v1.1/search`，再获取对象详情核实公有领域及图片 URL。旧 `v1/search` 已被官方列入退役流程。[接口与迁移说明](https://metmuseum.github.io/)

若来源返回 403 / 429，不要寻找不存在的 Key 或绕过验证；查看连接诊断，稍后重试或使用其他来源。历史测试中部分博物馆图像请求曾返回 403，当前环境需重新确认。

## 密钥和错误排查

- 密钥只填在软件的对应图库设置中，不要写进 README、GitHub Issue、截图、`.env` 或公开仓库；保存由后端使用系统钥匙串完成。
- 每位使用者配置自己的开发者凭证；安装包不会附带维护者 Key。更大规模产品分发还需遵守供应商的应用注册、生产审核和分发规则。
- **401**：确认 Key 类型、复制内容、是否保存；Unsplash 应填 Access Key。
- **403**：查看来源返回的信息，可能是权限、账号或网络访问限制，不能仅凭状态码判断 Key 错误。
- **429**：等待配额恢复，减少查询和重复测试；连接测试也会消耗请求。
- **连接成功但没有结果**：确认设置开关和本次来源均已勾选，换短英文词，并检查是否使用了过窄的筛选条件。
- **不知道网络还是程序故障**：仅启用演示素材验证主流程；演示素材正常不代表真实图库已连通。

Pinterest、Pexels 当前未接入；无需为本版本申请它们的 Key，也不支持用其他网站的 Key 代替。
