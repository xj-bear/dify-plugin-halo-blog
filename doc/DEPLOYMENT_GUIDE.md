# Halo CMS Dify 插件部署指南

本文档详细介绍如何部署和使用 Halo CMS Dify 插件。

## 环境要求

### 系统要求
- Python 3.8+
- Dify 平台环境
- Halo CMS 2.x

### 依赖要求
- `requests` >= 2.28.0
- `dify-plugin` >= 0.1.0

## 安装步骤

### 1. 获取插件包

从GitHub下载最新版本的插件包：
```bash
git clone https://github.com/your-repo/halo-dify-plugin.git
cd halo-dify-plugin
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置Halo API

#### 3.1 生成PAT Token

1. 登录Halo管理后台
2. 进入 `用户 -> 个人资料 -> 个人令牌`
3. 点击 `新建令牌`
4. 设置令牌名称和权限：
   - `content:posts:manage`
   - `content:snapshots:manage`
   - `api:console:posts:content:manage`
5. 保存生成的令牌

#### 3.2 配置环境变量

创建 `.env` 文件（不要提交到版本控制）：
```env
HALO_BASE_URL=https://your-halo-domain.com
HALO_PAT_TOKEN=your_pat_token_here
```

### 4. 打包插件

```bash
# 使用官方打包工具
dify plugin package
```

### 5. 上传到Dify

1. 进入Dify工作台
2. 选择 `工具 -> 自定义工具`
3. 上传生成的 `.difypkg` 文件
4. 配置插件参数

## 配置说明

### 必需配置

| 参数 | 说明 | 示例 |
|------|------|------|
| base_url | Halo站点地址 | https://blog.example.com |
| pat_token | 个人访问令牌 | halo_pat_... |

### 可选配置

| 参数 | 说明 | 默认值 |
|------|------|--------|
| timeout | API请求超时时间 | 30秒 |
| retry_count | 失败重试次数 | 3次 |
| default_editor | 默认编辑器类型 | stackedit |

## 功能使用

### 1. 文章管理

#### 创建文章
```python
# 基本创建
result = halo_post_create(
    title="我的文章标题",
    content="# 文章内容\n这是文章正文...",
    editor_type="stackedit"
)

# 完整创建
result = halo_post_create(
    title="完整文章示例",
    content="# 标题\n文章内容...",
    slug="complete-article-example",
    tags="技术,分享,Halo",
    categories="技术博客",
    excerpt="这是文章摘要",
    publish_immediately=True,
    editor_type="stackedit"
)
```

#### 更新文章
```python
result = halo_post_update(
    post_id="post-12345",
    title="更新后的标题",
    content="# 更新内容\n这是更新后的内容..."
)
```

#### 获取文章
```python
# 获取单篇文章
article = halo_post_get(post_id="post-12345")

# 获取文章列表
articles = halo_post_list(
    size=10,
    published=True,
    category="技术博客"
)
```

#### 删除文章
```python
result = halo_post_delete(post_id="post-12345")
```

### 2. 瞬间管理

#### 创建瞬间
```python
moment = halo_moment_create(
    content="今天天气不错 #生活",
    tags="生活,随记",
    visible="PUBLIC"
)
```

#### 获取瞬间列表
```python
moments = halo_moment_list(
    size=20,
    approved=True
)
```

### 3. 标签和分类管理

#### 获取标签列表
```python
tags = halo_tags_list()
```

#### 获取分类列表
```python
categories = halo_categories_list()
```

### 4. 系统设置

#### 初始化连接
```python
setup_result = halo_setup(
    base_url="https://blog.example.com",
    pat_token="your_token_here"
)
```

## 编辑器选择指南

### StackEdit（推荐用于Markdown）
- **适用场景**：技术博客、文档类内容
- **优势**：实时预览、丰富的Markdown功能
- **最佳实践**：适合长篇技术文章

### ByteMD
- **适用场景**：轻量级博客、简单文档
- **优势**：加载快速、插件丰富
- **最佳实践**：适合日常博客写作

### 默认编辑器
- **适用场景**：富文本内容、混合媒体
- **优势**：稳定性好、功能完整
- **最佳实践**：适合包含图片、视频的文章

### Vditor（需要安装插件）
- **适用场景**：高级用户、复杂文档
- **优势**：功能最全面、自定义程度高
- **最佳实践**：适合专业写作场景

## 故障排除

### 常见问题

#### 1. 认证失败（401错误）
**症状**：API调用返回401 Unauthorized
**解决方案**：
- 检查PAT Token是否正确
- 确认Token未过期
- 验证Token权限设置

#### 2. 内容不显示（编辑器兼容性问题）
**症状**：文章创建成功但编辑器中显示为空
**解决方案**：
- 插件已实现三重修复机制
- 检查快照是否正确创建
- 验证Console Content API设置

#### 3. 发布失败（权限问题）
**症状**：文章创建成功但无法发布
**解决方案**：
- 检查用户是否有发布权限
- 确认文章状态设置正确
- 验证分类和标签权限

#### 4. API超时
**症状**：请求超时，操作未完成
**解决方案**：
- 增加timeout设置
- 检查网络连接
- 验证Halo服务器状态

### 调试模式

开启调试模式查看详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 日志分析

关键日志信息：
- `✅ 快照创建成功` - 快照机制正常
- `✅ 编辑器内容设置成功` - Console Content API正常
- `✅ 编辑器兼容性注解更新成功` - 注解设置正常

## 性能优化

### 1. 批量操作
```python
# 批量创建文章时，复用session
session = requests.Session()
# ... 执行多个操作
```

### 2. 异步处理
```python
# 对于大量文章操作，考虑异步处理
import asyncio
import aiohttp

async def create_articles_batch(articles):
    # 异步创建多篇文章
    pass
```

### 3. 缓存策略
```python
# 缓存用户信息和权限
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_info(token):
    # 缓存用户信息
    pass
```

## 安全注意事项

### 1. Token管理
- 定期轮换PAT Token
- 不在代码中硬编码Token
- 使用环境变量存储敏感信息

### 2. 权限控制
- 遵循最小权限原则
- 定期审查Token权限
- 监控API使用情况

### 3. 数据保护
- 验证用户输入
- 防止XSS和注入攻击
- 定期备份重要数据

## 版本兼容性

| 插件版本 | Halo版本 | Dify版本 | 状态 |
|----------|----------|----------|------|
| 1.0.x | 2.11+ | 0.6+ | 当前版本 |
| 0.9.x | 2.10+ | 0.5+ | 维护版本 |

## 更新说明

### v1.0.0
- ✅ 解决编辑器兼容性问题
- ✅ 实现三重修复机制
- ✅ 支持多种编辑器类型
- ✅ 完善错误处理

### v0.9.0
- 基础功能实现
- 文章CRUD操作
- 瞬间管理功能

## 技术支持

如遇到问题，请按以下顺序寻求帮助：

1. **查看文档**：[技术解决方案文档](./TECHNICAL_SOLUTIONS.md)
2. **检查日志**：开启调试模式查看详细信息
3. **社区支持**：在GitHub Issues中搜索相似问题
4. **提交Issue**：详细描述问题和环境信息

## 贡献指南

欢迎贡献代码和改进建议：

1. Fork项目仓库
2. 创建特性分支
3. 提交代码更改
4. 创建Pull Request

确保遵循项目的代码规范和测试要求。 