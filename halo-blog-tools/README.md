# Halo CMS Dify Plugin

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Halo Version](https://img.shields.io/badge/Halo-2.21+-blue.svg)](https://halo.run)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-green.svg)](https://dify.ai)

一个功能强大的 Dify 插件，用于与 Halo CMS 博客系统进行集成，支持文章管理、动态发布、分类标签管理等功能。

## 🚀 功能特性

### 📝 文章管理
- **文章创建** - 支持 Markdown 和富文本编辑器，自动处理分类标签
- **文章更新** - 修改已发布的文章内容，保持版本历史
- **文章获取** - 根据 ID 或 slug 获取文章详情和元数据
- **文章列表** - 获取文章列表，支持分页、关键词搜索和状态筛选
- **文章删除** - 安全删除指定文章
- **发布控制** - 支持草稿保存和立即发布，灵活的发布策略

### 🌟 动态管理
- **动态创建** - 发布瞬间动态内容，支持媒体附件
- **动态列表** - 获取动态列表，支持分页浏览
- **标签支持** - 动态内容支持标签分类

### 🏷️ 分类标签
- **分类管理** - 获取博客分类列表，支持层级结构
- **标签管理** - 获取标签列表，支持自动创建新标签
- **智能匹配** - 自动匹配现有分类标签，避免重复创建

### 🔧 系统功能
- **连接测试** - 验证 Halo CMS 连接状态和权限
- **用户信息** - 获取当前用户信息和权限范围
- **错误处理** - 完善的错误处理和日志记录

## 📦 安装使用

### 前置要求
- Halo CMS 版本 ≥ 2.21
- 有效的 Halo CMS 个人访问令牌（PAT）
- 对应的用户权限（文章管理、动态发布等）

### 安装方式

#### 方式一：通过 .difypkg 文件安装
1. 下载最新的 `halo-blog-tools.difypkg` 文件
2. 在 Dify 插件管理页面选择"通过本地文件安装"
3. 上传 .difypkg 文件完成安装
4. 配置必要的连接参数

#### 方式二：远程调试模式
1. 在 Dify 插件管理页面获取调试密钥
2. 配置 .env 环境变量文件
3. 运行 `python -m main` 启动远程调试

### 配置参数

使用插件前需要配置以下参数：

- **base_url** - Halo CMS 站点地址（如：https://your-blog.com）
- **access_token** - Halo CMS 个人访问令牌

## 🛠️ 工具详情

| 工具名称 | 功能描述 | 主要参数 | 返回结果 |
|---------|----------|----------|----------|
| halo-setup | 测试连接状态 | base_url, access_token | 连接状态和用户信息 |
| halo-post-create | 创建新文章 | title, content, categories, tags, editor_type | 文章ID和发布状态 |
| halo-post-update | 更新文章 | post_id, title, content, categories, tags | 更新结果 |
| halo-post-get | 获取文章详情 | post_id 或 slug | 完整文章信息 |
| halo-post-list | 获取文章列表 | page, size, keyword, status | 文章列表和分页信息 |
| halo-post-delete | 删除文章 | post_id | 删除结果 |
| halo-moment-create | 创建动态 | content, tags, media_urls | 动态ID和创建时间 |
| halo-moment-list | 获取动态列表 | page, size | 动态列表和分页信息 |
| halo-categories-list | 获取分类列表 | - | 所有分类信息 |
| halo-tags-list | 获取标签列表 | - | 所有标签信息 |

## 💡 使用示例

### 创建技术文章
```
工具：halo-post-create
参数：
- title: "深入理解 Halo CMS 插件开发"
- content: "# 插件开发指南\n\n本文介绍如何开发 Halo CMS 插件..."
- categories: "技术分享"
- tags: "Halo,插件开发,Java"
- editor_type: "markdown"
- publish_immediately: true
```

### 发布生活动态
```
工具：halo-moment-create
参数：
- content: "今天完成了 Halo CMS Dify 插件的开发，感觉很有成就感！🎉"
- tags: "开发日记,成就感"
- media_urls: ["https://example.com/image.jpg"]
```

### 搜索相关文章
```
工具：halo-post-list
参数：
- page: 1
- size: 10
- keyword: "Halo"
- status: "PUBLISHED"
```

### 更新文章内容
```
工具：halo-post-update
参数：
- post_id: "123"
- title: "深入理解 Halo CMS 插件开发（更新版）"
- content: "# 插件开发指南（2024版）\n\n本文介绍最新的插件开发方法..."
```

## 🔧 编辑器支持

插件支持多种编辑器类型，自动适配内容格式：

- **default** - 默认编辑器，自动检测内容类型
- **markdown** - Markdown 编辑器，支持完整的 Markdown 语法
- **richtext** - 富文本编辑器，支持 HTML 格式

## 🎯 特色功能

### 智能标签管理
- 自动检测现有标签，避免重复创建
- 支持批量标签处理
- 标签名称智能匹配和建议

### 灵活的发布策略
- 支持草稿保存和定时发布
- 文章状态智能管理
- 版本历史保持

### 完善的错误处理
- 详细的错误信息和解决建议
- 网络异常自动重试
- 权限验证和友好提示

### 高性能设计
- 异步请求处理
- 智能缓存机制
- 批量操作优化

## 🔒 安全说明

- 所有 API 请求均通过 HTTPS 加密传输
- 访问令牌安全存储，不会记录在日志中
- 支持权限范围限制，确保操作安全

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个插件！

### 开发环境
- Python 3.12+
- Halo CMS 2.21+ 测试环境
- Dify 插件开发工具

## 📋 版本信息

- **当前版本**: 0.0.1
- **兼容性**: Halo CMS 2.21+
- **开发语言**: Python 3.12+
- **依赖框架**: dify-plugin
- **许可证**: MIT

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。
