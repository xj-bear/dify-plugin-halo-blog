# API 接口设计文档

## 1. 接口概述

### 1.1 设计原则
- **RESTful 设计**: 遵循 REST 接口设计规范
- **一致性**: 统一的接口风格和数据格式
- **安全性**: 安全的认证和数据传输
- **易用性**: 简洁明了的接口参数和返回值
- **可扩展性**: 预留扩展空间，支持版本迭代

### 1.2 认证方式
所有 API 请求都需要在 HTTP 头中携带认证信息：
```
Authorization: Bearer {personal_access_token}
Content-Type: application/json
```

### 1.3 基础 URL
```
https://{your-halo-site}/api/v1alpha1
```

## 2. 工具接口定义

### 2.1 认证配置工具

#### 配置 Halo 连接
- **工具名称**: `setup_halo_connection`
- **功能描述**: 配置 Halo 站点连接信息和认证令牌

**输入参数**:
```json
{
  "site_url": {
    "type": "string",
    "required": true,
    "description": "Halo 站点 URL",
    "example": "https://example.com"
  },
  "access_token": {
    "type": "string",
    "required": true,
    "description": "个人访问令牌",
    "example": "pat_xxx..."
  }
}
```

**输出数据**:
```json
{
  "success": true,
  "message": "连接配置成功",
  "data": {
    "site_info": {
      "title": "我的博客",
      "version": "2.21.0",
      "user": {
        "name": "admin",
        "email": "admin@example.com"
      }
    }
  }
}
```

### 2.2 文章管理工具

#### 2.2.1 获取文章列表
- **工具名称**: `get_posts`
- **功能描述**: 获取 Halo 博客的文章列表

**输入参数**:
```json
{
  "page": {
    "type": "integer",
    "required": false,
    "default": 1,
    "description": "页码"
  },
  "size": {
    "type": "integer", 
    "required": false,
    "default": 10,
    "description": "每页数量，最大 100"
  },
  "keyword": {
    "type": "string",
    "required": false,
    "description": "关键词搜索"
  },
  "category": {
    "type": "string",
    "required": false,
    "description": "分类筛选"
  },
  "tag": {
    "type": "string", 
    "required": false,
    "description": "标签筛选"
  },
  "status": {
    "type": "string",
    "required": false,
    "enum": ["PUBLISHED", "DRAFT", "RECYCLE"],
    "description": "文章状态"
  }
}
```

**输出数据**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "post-1",
        "title": "文章标题",
        "excerpt": "文章摘要",
        "status": "PUBLISHED",
        "categories": ["技术"],
        "tags": ["Python", "AI"],
        "cover": "https://example.com/cover.jpg",
        "author": "admin",
        "created_at": "2024-12-01T10:00:00Z",
        "updated_at": "2024-12-01T12:00:00Z",
        "published_at": "2024-12-01T10:30:00Z",
        "permalink": "https://example.com/posts/post-1"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 10,
      "total": 25,
      "total_pages": 3,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

#### 2.2.2 获取文章详情
- **工具名称**: `get_post_detail`
- **功能描述**: 根据文章 ID 获取完整的文章信息

**输入参数**:
```json
{
  "post_id": {
    "type": "string",
    "required": true,
    "description": "文章 ID"
  }
}
```

**输出数据**:
```json
{
  "success": true,
  "data": {
    "id": "post-1",
    "title": "文章标题",
    "content": "# 文章标题\n\n这是文章内容...",
    "content_format": "markdown",
    "excerpt": "文章摘要",
    "cover": "https://example.com/cover.jpg",
    "categories": [
      {
        "id": "cat-1",
        "name": "技术",
        "slug": "tech"
      }
    ],
    "tags": [
      {
        "id": "tag-1", 
        "name": "Python",
        "slug": "python"
      }
    ],
    "status": "PUBLISHED",
    "allow_comment": true,
    "pinned": false,
    "priority": 0,
    "author": {
      "name": "admin",
      "avatar": "https://example.com/avatar.jpg"
    },
    "stats": {
      "visit": 100,
      "comment": 5,
      "like": 10
    },
    "created_at": "2024-12-01T10:00:00Z",
    "updated_at": "2024-12-01T12:00:00Z",
    "published_at": "2024-12-01T10:30:00Z",
    "permalink": "https://example.com/posts/post-1"
  }
}
```

#### 2.2.3 创建文章
- **工具名称**: `create_post`
- **功能描述**: 创建新的 Halo 博客文章

**输入参数**:
```json
{
  "title": {
    "type": "string",
    "required": true,
    "description": "文章标题"
  },
  "content": {
    "type": "string", 
    "required": true,
    "description": "文章内容，Markdown 格式"
  },
  "excerpt": {
    "type": "string",
    "required": false,
    "description": "文章摘要"
  },
  "cover": {
    "type": "string",
    "required": false,
    "description": "封面图片 URL"
  },
  "categories": {
    "type": "array",
    "items": {"type": "string"},
    "required": false,
    "description": "分类名称列表"
  },
  "tags": {
    "type": "array", 
    "items": {"type": "string"},
    "required": false,
    "description": "标签名称列表"
  },
  "publish_status": {
    "type": "string",
    "enum": ["PUBLISHED", "DRAFT"],
    "default": "DRAFT",
    "description": "发布状态"
  },
  "allow_comment": {
    "type": "boolean",
    "default": true,
    "description": "是否允许评论"
  },
  "pinned": {
    "type": "boolean", 
    "default": false,
    "description": "是否置顶"
  }
}
```

**输出数据**:
```json
{
  "success": true,
  "message": "文章创建成功",
  "data": {
    "id": "post-new-1",
    "title": "新文章标题",
    "status": "DRAFT",
    "permalink": "https://example.com/posts/post-new-1",
    "created_at": "2024-12-01T15:00:00Z"
  }
}
```

#### 2.2.4 更新文章
- **工具名称**: `update_post`
- **功能描述**: 更新现有的 Halo 博客文章

**输入参数**:
```json
{
  "post_id": {
    "type": "string",
    "required": true,
    "description": "文章 ID"
  },
  "title": {
    "type": "string",
    "required": false,
    "description": "文章标题"
  },
  "content": {
    "type": "string",
    "required": false, 
    "description": "文章内容，Markdown 格式"
  },
  "excerpt": {
    "type": "string",
    "required": false,
    "description": "文章摘要"
  },
  "cover": {
    "type": "string",
    "required": false,
    "description": "封面图片 URL"
  },
  "categories": {
    "type": "array",
    "items": {"type": "string"},
    "required": false,
    "description": "分类名称列表"
  },
  "tags": {
    "type": "array",
    "items": {"type": "string"}, 
    "required": false,
    "description": "标签名称列表"
  },
  "publish_status": {
    "type": "string",
    "enum": ["PUBLISHED", "DRAFT"],
    "required": false,
    "description": "发布状态"
  }
}
```

**输出数据**:
```json
{
  "success": true,
  "message": "文章更新成功",
  "data": {
    "id": "post-1",
    "title": "更新后的标题", 
    "status": "PUBLISHED",
    "permalink": "https://example.com/posts/post-1",
    "updated_at": "2024-12-01T16:00:00Z"
  }
}
```

### 2.3 瞬间管理工具

#### 2.3.1 创建瞬间
- **工具名称**: `create_moment`
- **功能描述**: 创建 Halo 瞬间内容

**输入参数**:
```json
{
  "content": {
    "type": "string",
    "required": false,
    "description": "瞬间文本内容"
  },
  "media_urls": {
    "type": "array",
    "items": {"type": "string"},
    "required": false,
    "description": "媒体文件 URL 列表"
  },
  "media_type": {
    "type": "string",
    "enum": ["PHOTO", "VIDEO", "AUDIO"],
    "default": "PHOTO",
    "description": "媒体类型"
  },
  "tags": {
    "type": "array",
    "items": {"type": "string"},
    "required": false,
    "description": "标签列表"
  },
  "visibility": {
    "type": "string",
    "enum": ["PUBLIC", "PRIVATE"],
    "default": "PUBLIC",
    "description": "可见性设置"
  }
}
```

**输出数据**:
```json
{
  "success": true,
  "message": "瞬间创建成功",
  "data": {
    "id": "moment-1",
    "content": "这是一个美好的瞬间",
    "media_count": 2,
    "tags": ["生活", "日常"],
    "visibility": "PUBLIC",
    "permalink": "https://example.com/moments/moment-1",
    "created_at": "2024-12-01T15:30:00Z"
  }
}
```

#### 2.3.2 获取瞬间列表
- **工具名称**: `get_moments`
- **功能描述**: 获取瞬间列表

**输入参数**:
```json
{
  "page": {
    "type": "integer",
    "required": false,
    "default": 1,
    "description": "页码"
  },
  "size": {
    "type": "integer",
    "required": false,
    "default": 10,
    "description": "每页数量"
  },
  "tag": {
    "type": "string",
    "required": false,
    "description": "标签筛选"
  }
}
```

**输出数据**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "moment-1",
        "content": "这是一个美好的瞬间",
        "media": [
          {
            "type": "PHOTO",
            "url": "https://example.com/photo1.jpg",
            "thumbnail": "https://example.com/thumb1.jpg"
          }
        ],
        "tags": ["生活"],
        "visibility": "PUBLIC",
        "author": "admin",
        "stats": {
          "like": 5,
          "comment": 2
        },
        "created_at": "2024-12-01T15:30:00Z",
        "permalink": "https://example.com/moments/moment-1"
      }
    ],
    "pagination": {
      "page": 1,
      "size": 10,
      "total": 15,
      "total_pages": 2,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

### 2.4 辅助工具

#### 2.4.1 获取分类列表
- **工具名称**: `get_categories`
- **功能描述**: 获取博客分类列表

**输入参数**: 无

**输出数据**:
```json
{
  "success": true,
  "data": [
    {
      "id": "cat-1",
      "name": "技术",
      "slug": "tech",
      "description": "技术相关文章",
      "post_count": 10,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 2.4.2 获取标签列表
- **工具名称**: `get_tags`
- **功能描述**: 获取博客标签列表

**输入参数**: 无

**输出数据**:
```json
{
  "success": true,
  "data": [
    {
      "id": "tag-1",
      "name": "Python",
      "slug": "python",
      "color": "#3776ab",
      "post_count": 5,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

## 3. 错误处理

### 3.1 错误响应格式
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息",
    "details": "详细错误信息",
    "timestamp": "2024-12-01T15:00:00Z"
  }
}
```

### 3.2 错误码定义

#### 3.2.1 认证错误 (AUTH_*)
| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| AUTH_TOKEN_MISSING | 401 | 缺少访问令牌 |
| AUTH_TOKEN_INVALID | 401 | 访问令牌无效 |
| AUTH_TOKEN_EXPIRED | 401 | 访问令牌已过期 |
| AUTH_PERMISSION_DENIED | 403 | 权限不足 |

#### 3.2.2 参数错误 (PARAM_*)
| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| PARAM_MISSING | 400 | 缺少必需参数 |
| PARAM_INVALID | 400 | 参数格式错误 |
| PARAM_OUT_OF_RANGE | 400 | 参数值超出范围 |

#### 3.2.3 资源错误 (RESOURCE_*)
| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| RESOURCE_NOT_FOUND | 404 | 资源不存在 |
| RESOURCE_CONFLICT | 409 | 资源冲突 |
| RESOURCE_LOCKED | 423 | 资源被锁定 |

#### 3.2.4 系统错误 (SYSTEM_*)
| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| SYSTEM_ERROR | 500 | 系统内部错误 |
| SYSTEM_TIMEOUT | 504 | 请求超时 |
| SYSTEM_UNAVAILABLE | 503 | 服务不可用 |

#### 3.2.5 网络错误 (NETWORK_*)
| 错误码 | HTTP状态码 | 描述 |
|--------|-----------|------|
| NETWORK_CONNECTION_FAILED | 0 | 网络连接失败 |
| NETWORK_TIMEOUT | 0 | 网络请求超时 |
| NETWORK_DNS_FAILED | 0 | DNS 解析失败 |

## 4. 数据验证规则

### 4.1 通用验证规则
- **字符串长度**: 标题最大 255 字符，内容最大 1MB
- **URL 格式**: 必须是有效的 HTTP/HTTPS URL
- **数组长度**: 分类和标签最多 20 个
- **文件大小**: 上传文件最大 10MB

### 4.2 特殊字段验证
- **站点 URL**: 必须以 http:// 或 https:// 开头
- **访问令牌**: 必须以 pat_ 开头，长度至少 32 字符
- **文章 ID**: 符合 Halo 资源命名规范
- **媒体 URL**: 支持的文件格式 jpg, png, gif, mp4, mp3

## 5. 接口限制

### 5.1 请求频率限制
- **认证请求**: 每分钟最多 10 次
- **读取操作**: 每分钟最多 100 次
- **写入操作**: 每分钟最多 50 次
- **上传操作**: 每分钟最多 10 次

### 5.2 数据大小限制
- **请求体大小**: 最大 10MB
- **响应数据**: 最大 50MB
- **单次查询**: 最多返回 100 条记录
- **批量操作**: 最多处理 50 个项目

## 6. 版本兼容性

### 6.1 API 版本支持
- **当前版本**: v1alpha1
- **最低支持**: Halo 2.21+
- **向后兼容**: 支持一个主版本的向后兼容

### 6.2 字段变更策略
- **新增字段**: 向后兼容，可选字段
- **废弃字段**: 至少保留一个版本周期
- **修改字段**: 新版本中实现，旧版本保持兼容

---

**文档版本**: v1.0.0  
**创建日期**: 2024年12月  
**API 负责人**: 后端开发工程师  
**审核人**: 技术经理 