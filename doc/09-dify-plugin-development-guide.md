# Dify插件开发完整指南 - 从开发到上线

本文档基于Dify官方插件开发文档整理，为Halo CMS插件项目提供从开发到上线的完整指南。

## 目录

1. [环境准备与开发准则](#1-环境准备与开发准则)
2. [插件开发流程](#2-插件开发流程)
3. [开发准则与代码规范](#3-开发准则与代码规范)
4. [远程调试与测试](#4-远程调试与测试)
5. [插件打包](#5-插件打包)
6. [数字签名与验证](#6-数字签名与验证)
7. [自动发布流程](#7-自动发布流程)
8. [发布到Marketplace](#8-发布到marketplace)
9. [高级功能](#9-高级功能)
10. [最佳实践](#10-最佳实践)

## 1. 环境准备与开发准则

### 🔧 技术要求
- **Python版本**: ≥ 3.12
- **Dify插件CLI工具**: dify-plugin-daemon
- **操作系统**: Windows/macOS/Linux

### 🛠️ CLI工具安装

**macOS（推荐Homebrew）:**
```bash
brew tap langgenius/dify
brew install dify
dify version  # 验证安装
```

**其他平台下载二进制文件:**
- 从 [Dify Plugin CLI Releases](https://github.com/langgenius/dify-plugin-daemon/releases) 下载
- 赋予执行权限：`chmod +x dify-plugin-*`
- 全局安装：`sudo mv dify /usr/local/bin/`

**Windows安装:**
```powershell
# 下载对应的Windows版本
# 设置环境变量或直接使用
.\dify-plugin-windows-amd64.exe version
```

## 2. 插件开发流程

### 🚀 项目初始化
```bash
# 1. 创建新插件项目
dify plugin init

# 2. 填写基本信息
# - 插件名称（小写字母、数字、连字符）
# - 作者标识  
# - 功能描述
# - 选择开发语言：Python
# - 选择插件类型：tool/model/agent/extension
```

### 📁 标准项目结构
```
halo_plugin/
├── __init__.py
├── auth/                    # 认证模块
│   ├── __init__.py
│   ├── authenticator.py     # 认证器
│   └── token_manager.py     # 令牌管理
├── api/                     # API客户端
│   ├── __init__.py
│   ├── client.py           # HTTP客户端
│   └── endpoints.py        # API端点定义
├── tools/                   # 工具集合
│   ├── __init__.py
│   ├── setup_tool.py       # 连接设置
│   ├── post_tools.py       # 文章管理
│   └── moment_tools.py     # 瞬间管理
├── utils/                   # 工具函数
│   ├── __init__.py
│   ├── validators.py       # 验证器
│   └── formatters.py       # 格式化器
├── models/                  # 数据模型
│   ├── __init__.py
│   ├── post.py            # 文章模型
│   └── moment.py          # 瞬间模型
├── exceptions.py           # 自定义异常
├── manifest.yaml          # 插件清单
├── requirements.txt       # 依赖声明
├── README.md             # 说明文档
├── PRIVACY.md           # 隐私政策
└── provider/            # 供应商配置
    ├── provider_name.py
    └── provider_name.yaml
```

## 3. 开发准则与代码规范

### 🎯 核心开发原则
- **模块化架构**: 明确分离关注点
- **类型提示**: 所有函数使用类型注解
- **错误处理**: 完善的异常捕获和处理
- **安全性**: 敏感信息加密存储，输入验证
- **性能**: 连接池、异步处理、缓存策略

### 📝 代码规范要求
- **PEP 8**: 严格遵循Python代码风格
- **Black格式化**: 使用Black进行代码格式化
- **类型提示**: 所有公共方法必须有类型注解
- **文档字符串**: 使用Google风格的docstrings
- **最大行长度**: 88字符
- **命名规范**: 
  - 类名：PascalCase
  - 函数/方法：snake_case
  - 常量：UPPER_SNAKE_CASE
  - 私有方法：前缀下划线

### 🔧 工具插件开发示例
```python
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from dify_plugin import Tool

class PostToolInput(BaseModel):
    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章内容（Markdown格式）")
    editor_type: str = Field(default="stackedit", description="编辑器类型")

class HaloPostTool(Tool):
    name: str = "halo_post_create"
    description: str = "创建Halo博客文章"
    parameters: PostToolInput
    
    def _invoke(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # 获取认证信息
            token = self.runtime.credentials["halo_pat_token"]
            
            # 执行业务逻辑
            result = self._create_post(
                token, 
                parameters["title"], 
                parameters["content"]
            )
            
            return {"success": True, "post_id": result["id"]}
            
        except Exception as e:
            logger.error(f"创建文章失败: {e}")
            raise ToolProviderError(f"操作失败: {str(e)}")
```

### 🛡️ 错误处理模式
```python
from dify_plugin.errors.tool import ToolProviderError

class HaloPluginError(Exception):
    """Halo插件基础异常"""
    pass

class AuthenticationError(HaloPluginError):
    """认证失败异常"""
    pass

class ValidationError(HaloPluginError):
    """输入验证异常"""
    pass

# 使用示例
try:
    result = api_call()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        raise AuthenticationError("PAT令牌无效或已过期")
    elif e.response.status_code == 400:
        raise ValidationError("请求参数验证失败")
    else:
        raise ToolProviderError(f"API调用失败: {e}")
```

## 4. 远程调试与测试

### 🔍 调试环境配置
1. **获取调试密钥**: 在Dify平台 -> 插件管理 -> 远程调试
2. **配置环境变量**:
```bash
cp .env.example .env
```

**.env配置示例:**
```env
INSTALL_METHOD=remote
REMOTE_INSTALL_HOST=your-dify-domain.com
REMOTE_INSTALL_PORT=5003
REMOTE_INSTALL_KEY=****-****-****-****-****
```

### 🚀 启动调试
```bash
# 激活虚拟环境（如果使用）
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 启动本地插件服务
python -m main

# 观察日志输出确认连接成功
```

### ✅ 测试流程
1. **功能测试**: 在Dify应用中调用插件功能
2. **边界测试**: 测试输入参数的边界值
3. **错误处理**: 测试各种异常情况
4. **性能测试**: 验证响应时间和资源使用
5. **安全测试**: 验证认证和权限控制
6. **兼容性测试**: 测试不同编辑器类型的兼容性

### 🐛 调试技巧
```python
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 在关键位置添加日志
logger = logging.getLogger(__name__)
logger.debug("开始处理请求")
logger.info("文章创建成功")
logger.warning("编辑器兼容性问题")
logger.error("API调用失败")
```

## 5. 插件打包

### 📦 打包准备
```bash
# 停止调试服务
# Ctrl+C

# 更新版本号（在manifest.yaml中）
version: "0.0.4"

# 检查依赖
pip freeze > requirements.txt
```

### 🎯 打包执行
```bash
# 在插件根目录执行
dify plugin package .

# 或指定输出路径
dify plugin package . -o halo-blog-tools-v0.0.4.difypkg
```

### 📋 打包前检查清单
- [ ] 所有依赖已在requirements.txt中声明
- [ ] manifest.yaml信息完整准确（版本号、作者、描述）
- [ ] 图标文件已放置在_assets目录
- [ ] README.md和PRIVACY.md已撰写
- [ ] 代码已通过linting检查
- [ ] 测试覆盖率达到90%+
- [ ] 敏感信息已移除（API密钥、调试信息）
- [ ] 所有文件编码为UTF-8

## 6. 数字签名与验证

### 🔐 生成密钥对
```bash
# 生成签名密钥对
dify signature generate -f your_key_pair

# 生成文件:
# - your_key_pair.private.pem (私钥，妥善保管)
# - your_key_pair.public.pem (公钥，用于验证)
```

### ✍️ 插件签名
```bash
# 为插件添加数字签名
dify signature sign your_plugin.difypkg -p your_key_pair.private.pem

# 生成 your_plugin.signed.difypkg
```

### 🔍 签名验证
```bash
# 验证插件签名
dify signature verify your_plugin.signed.difypkg -p your_key_pair.public.pem

# 使用Dify市场公钥验证（省略-p参数）
dify signature verify your_plugin.signed.difypkg
```

### 🔒 私钥安全管理
- 私钥不得提交到版本控制系统
- 使用环境变量或安全存储服务
- 定期轮换密钥对
- 设置密钥访问权限

## 7. 自动发布流程

### 🤖 GitHub Actions配置

**环境准备:**
1. Fork `dify-plugins` 仓库到个人账户
2. 在插件源码仓库设置`PLUGIN_ACTION` Secret（GitHub PAT）
3. 确保manifest.yaml中的author字段与GitHub用户名一致

**PAT权限要求:**
- `repo`: 完整仓库访问权限
- `workflow`: 工作流权限
- `write:packages`: 包写入权限

**工作流文件** (`.github/workflows/plugin-publish.yml`):
```yaml
name: Auto Create PR on Main Push
on:
  push:
    branches: [ main ]
jobs:
  create_pr:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Download CLI tool
        run: |
          mkdir -p $RUNNER_TEMP/bin
          cd $RUNNER_TEMP/bin
          wget https://github.com/langgenius/dify-plugin-daemon/releases/download/0.0.6/dify-plugin-linux-amd64
          chmod +x dify-plugin-linux-amd64
      
      - name: Get basic info from manifest
        id: get_basic_info
        run: |
          PLUGIN_NAME=$(grep "^name:" manifest.yaml | cut -d' ' -f2)
          echo "plugin_name=$PLUGIN_NAME" >> $GITHUB_OUTPUT
          VERSION=$(grep "^version:" manifest.yaml | cut -d' ' -f2)
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          AUTHOR=$(grep "^author:" manifest.yaml | cut -d' ' -f2)
          echo "author=$AUTHOR" >> $GITHUB_OUTPUT
      
      - name: Package Plugin
        run: |
          PACKAGE_NAME="${{ steps.get_basic_info.outputs.plugin_name }}-${{ steps.get_basic_info.outputs.version }}.difypkg"
          $RUNNER_TEMP/bin/dify-plugin-linux-amd64 plugin package . -o "$PACKAGE_NAME"
          echo "package_name=$PACKAGE_NAME" >> $GITHUB_OUTPUT
      
      # ... 其他步骤见完整配置
```

### 📤 发布步骤
1. **更新版本**: 修改manifest.yaml中的version字段
2. **提交更改**: 提交代码到本地仓库
3. **推送代码**: 推送到main分支
4. **自动处理**: GitHub Actions自动执行打包和PR创建
5. **等待审核**: Dify团队审核插件

### 🔄 版本管理策略
- **语义化版本**: 使用x.y.z格式
- **主版本(x)**: 破坏性更改
- **次版本(y)**: 新功能添加
- **修订版(z)**: 错误修复

## 8. 发布到Marketplace

### 📝 发布准则
1. **功能独特性**: 避免重复现有插件功能
2. **代码质量**: 遵循开发规范，代码整洁
3. **文档完整**: README、使用说明、隐私政策
4. **测试充分**: 功能正常，错误处理完善
5. **安全合规**: 数据处理符合隐私法规

### 📋 提交清单
- [ ] 插件功能完整且稳定
- [ ] 通过所有测试用例
- [ ] 文档详细且准确
- [ ] 隐私政策符合要求
- [ ] 代码审查通过
- [ ] 性能测试合格

### 🔄 审核流程
- **提交PR**: 向`langgenius/dify-plugins`提交
- **初步审核**: 1周内开始审核
- **反馈周期**: 14天内需回应审核意见
- **最终审核**: 问题解决后进行最终审核
- **合并发布**: 审核通过后合并到主分支
- **关闭规则**: 30天无响应将关闭PR

### 📊 审核重点
- **命名清晰**: 插件名称、描述清晰易懂
- **格式规范**: Manifest文件格式正确
- **功能验证**: 按说明测试插件功能
- **相关性检查**: 确保在Dify生态中有价值
- **安全审查**: 代码安全性检查
- **性能评估**: 资源使用合理性

## 9. 高级功能

### 🔧 第三方签名验证（社区版）

**环境配置:**
```yaml
# docker-compose.override.yaml
services:
  plugin_daemon:
    environment:
      FORCE_VERIFYING_SIGNATURE: true
      THIRD_PARTY_SIGNATURE_VERIFICATION_ENABLED: true
      THIRD_PARTY_SIGNATURE_VERIFICATION_PUBLIC_KEYS: /app/storage/public_keys/your_key.pem
```

**公钥部署:**
```bash
# 创建公钥目录
mkdir docker/volumes/plugin_daemon/public_keys

# 复制公钥文件
cp your_key_pair.public.pem docker/volumes/plugin_daemon/public_keys/

# 重启服务
cd docker
docker compose down
docker compose up -d
```

### 🛠️ 插件类型支持

**工具插件 (Tools)**:
- 集成第三方API和服务
- 执行特定业务逻辑
- 数据处理和转换

**模型插件 (Models)**:
- 集成AI模型
- 自定义推理逻辑
- 多模态支持

**Agent策略插件 (Agent Strategies)**:
- 自定义Agent推理策略
- 实现ReAct、CoT、ToT等方法
- 增强决策能力

**扩展插件 (Extensions)**:
- 扩展Dify平台功能
- 自定义Webhook处理
- 外部系统集成

### 📈 持久化存储

```python
from dify_plugin.interfaces.storage import Storage

class PluginStorage:
    def __init__(self, storage: Storage):
        self.storage = storage
    
    async def save_config(self, key: str, value: dict):
        """保存配置信息"""
        await self.storage.set(key, value)
    
    async def get_config(self, key: str) -> dict:
        """获取配置信息"""
        return await self.storage.get(key, {})
```

## 10. 最佳实践

### 🎯 性能优化

**连接池管理:**
```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class APIClient:
    def __init__(self):
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
```

**异步处理:**
```python
import asyncio
import aiohttp

async def batch_create_posts(posts_data):
    """批量创建文章"""
    async with aiohttp.ClientSession() as session:
        tasks = [create_post_async(session, data) for data in posts_data]
        results = await asyncio.gather(*tasks)
    return results
```

**缓存策略:**
```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_user_info(token: str):
    """缓存用户信息"""
    return fetch_user_info(token)

class TimedCache:
    def __init__(self, ttl: int = 300):
        self.cache = {}
        self.ttl = ttl
    
    def get(self, key: str):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            del self.cache[key]
        return None
    
    def set(self, key: str, value):
        self.cache[key] = (value, time.time())
```

### 🔒 安全最佳实践

**输入验证:**
```python
from pydantic import BaseModel, validator
import re

class PostCreateInput(BaseModel):
    title: str
    content: str
    slug: Optional[str] = None
    
    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('标题不能为空')
        if len(v) > 200:
            raise ValueError('标题长度不能超过200字符')
        return v.strip()
    
    @validator('slug')
    def validate_slug(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9-_]+$', v):
            raise ValueError('Slug只能包含字母、数字、连字符和下划线')
        return v
```

**敏感信息处理:**
```python
import os
from cryptography.fernet import Fernet

class SecureStorage:
    def __init__(self):
        key = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### 📊 监控与日志

**结构化日志:**
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(self, level: str, event: str, **kwargs):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': event,
            'level': level,
            **kwargs
        }
        getattr(self.logger, level)(json.dumps(log_data))

# 使用示例
logger = StructuredLogger('halo_plugin')
logger.log_event('info', 'post_created', 
                 post_id='123', user_id='456', 
                 execution_time=0.5)
```

**性能监控:**
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            success = False
            raise
        finally:
            execution_time = time.time() - start_time
            logger.log_event('info', 'function_execution',
                           function=func.__name__,
                           execution_time=execution_time,
                           success=success)
    return wrapper

@monitor_performance
def create_post(title: str, content: str):
    # 创建文章逻辑
    pass
```

### 🧪 测试策略

**单元测试:**
```python
import pytest
from unittest.mock import Mock, patch

class TestHaloPostTool:
    @pytest.fixture
    def tool(self):
        tool = HaloPostTool()
        tool.runtime = Mock()
        tool.runtime.credentials = {
            'halo_pat_token': 'test_token',
            'base_url': 'https://test.halo.com'
        }
        return tool
    
    @patch('requests.post')
    def test_create_post_success(self, mock_post, tool):
        # 模拟成功响应
        mock_post.return_value.json.return_value = {
            'metadata': {'name': 'post-123'}
        }
        mock_post.return_value.status_code = 201
        
        result = tool._invoke({
            'title': '测试文章',
            'content': '这是测试内容'
        })
        
        assert result['success'] is True
        assert 'post_id' in result
```

**集成测试:**
```python
@pytest.mark.integration
class TestHaloIntegration:
    def test_full_workflow(self):
        # 测试完整的工作流程
        # 1. 设置连接
        # 2. 创建文章
        # 3. 验证文章
        # 4. 清理资源
        pass
```

### 📈 持续改进

**版本管理:**
- 使用语义化版本控制
- 维护CHANGELOG.md
- 标记破坏性更改
- 提供迁移指南

**用户反馈:**
- 收集用户使用数据
- 建立反馈渠道
- 定期更新功能
- 响应安全漏洞

**代码质量:**
- 设置CI/CD流水线
- 自动化测试
- 代码覆盖率检查
- 定期重构优化

## 参考资源

### 📚 官方文档
- [Dify插件开发文档](https://docs.dify.ai/plugin-dev-zh/)
- [Dify Plugin CLI](https://github.com/langgenius/dify-plugin-daemon)
- [Dify官方插件仓库](https://github.com/langgenius/dify-plugins)

### 🛠️ 开发工具
- [Python官方文档](https://docs.python.org/3/)
- [Pydantic文档](https://pydantic-docs.helpmanual.io/)
- [Requests文档](https://docs.python-requests.org/)

### 🎯 最佳实践
- [Python代码规范PEP 8](https://pep8.org/)
- [语义化版本控制](https://semver.org/lang/zh-CN/)
- [Git提交规范](https://www.conventionalcommits.org/)

---

**文档版本**: v1.0.0  
**最后更新**: 2025-01-01  
**维护者**: Halo CMS插件开发团队  

如有问题或建议，请通过GitHub Issues反馈。 