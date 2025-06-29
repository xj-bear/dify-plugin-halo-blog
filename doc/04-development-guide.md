# 开发指南

## 1. 开发环境搭建

### 1.1 环境要求
- **Python**: 3.8 或更高版本
- **Dify**: 最新版本
- **网络**: 能够访问 Halo 实例的网络环境
- **编辑器**: VSCode (推荐) 或其他 Python IDE

### 1.2 依赖安装
创建并激活虚拟环境：
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (macOS/Linux)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 1.3 项目结构初始化
```bash
# 创建项目目录
mkdir dify-halo-plugin
cd dify-halo-plugin

# 创建基础目录结构
mkdir -p halo_plugin/{auth,api,tools,utils,config,tests}
touch halo_plugin/__init__.py
touch halo_plugin/{auth,api,tools,utils,config,tests}/__init__.py
```

### 1.4 开发工具配置

#### VSCode 配置 (.vscode/settings.json)
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### requirements.txt
```txt
# Dify Plugin Framework
dify-plugin-framework>=1.0.0

# HTTP 客户端
requests>=2.28.0
httpx>=0.24.0

# 数据处理
pydantic>=1.10.0

# 加密和安全
cryptography>=3.4.0

# 配置管理
pyyaml>=6.0

# 开发工具
pytest>=7.0.0
pytest-asyncio>=0.21.0
black>=22.0.0
isort>=5.12.0
pylint>=2.15.0
mypy>=1.0.0

# 调试工具
pdb-attach>=3.0.0
```

## 2. 编码规范

### 2.1 代码风格
- 使用 **Black** 进行代码格式化
- 使用 **isort** 进行导入排序
- 遵循 **PEP 8** 编码规范
- 行长度限制为 88 字符

### 2.2 命名规范
- **文件名**: 使用小写字母和下划线 `snake_case`
- **类名**: 使用大驼峰命名 `PascalCase`
- **函数/变量名**: 使用小写字母和下划线 `snake_case`
- **常量名**: 使用大写字母和下划线 `UPPER_CASE`

### 2.3 文档字符串规范
```python
def create_post(self, title: str, content: str, **kwargs) -> dict:
    """创建新的 Halo 博客文章
    
    Args:
        title: 文章标题
        content: 文章内容，Markdown 格式
        **kwargs: 其他可选参数
            excerpt: 文章摘要
            categories: 分类列表
            tags: 标签列表
            publish_status: 发布状态
    
    Returns:
        创建的文章信息字典
        
    Raises:
        HaloAPIException: API 调用失败
        ValidationError: 参数验证失败
        
    Example:
        >>> tool = ArticleTools(client)
        >>> result = tool.create_post(
        ...     title="我的文章",
        ...     content="# 标题\n内容...",
        ...     tags=["Python", "AI"]
        ... )
    """
```

### 2.4 类型注解
```python
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass

@dataclass
class PostData:
    title: str
    content: str
    excerpt: Optional[str] = None
    categories: List[str] = None
    tags: List[str] = None

def process_posts(posts: List[PostData]) -> Dict[str, Any]:
    """处理文章数据"""
    pass
```

## 3. 核心模块开发

### 3.1 认证模块开发

#### 认证器实现
```python
# halo_plugin/auth/authenticator.py
import requests
from typing import Optional
from ..utils.exceptions import AuthenticationError

class HaloAuthenticator:
    def __init__(self, site_url: str, token: str):
        self.site_url = site_url.rstrip('/')
        self.token = token
        self._session: Optional[requests.Session] = None
    
    def authenticate(self) -> bool:
        """验证认证信息"""
        try:
            response = self._get_user_info()
            return response.status_code == 200
        except Exception as e:
            raise AuthenticationError(f"认证失败: {str(e)}")
    
    def get_headers(self) -> dict:
        """获取请求头"""
        return {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Dify-Halo-Plugin/1.0.0'
        }
    
    def _get_user_info(self) -> requests.Response:
        """获取用户信息"""
        url = f"{self.site_url}/api/v1alpha1/users/-"
        return requests.get(url, headers=self.get_headers())
```

### 3.2 API 客户端开发

#### HTTP 客户端实现
```python
# halo_plugin/api/client.py
import requests
from typing import Optional, Dict, Any
from ..auth.authenticator import HaloAuthenticator
from ..utils.exceptions import APIException

class HaloAPIClient:
    def __init__(self, authenticator: HaloAuthenticator):
        self.auth = authenticator
        self.base_url = f"{authenticator.site_url}/api/v1alpha1"
        self.session = requests.Session()
        self.session.headers.update(authenticator.get_headers())
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> dict:
        """GET 请求"""
        return self._request('GET', endpoint, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> dict:
        """POST 请求"""
        return self._request('POST', endpoint, json=data)
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> dict:
        """PUT 请求"""
        return self._request('PUT', endpoint, json=data)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """发送 HTTP 请求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise APIException(f"API 请求失败: {str(e)}")
```

### 3.3 工具类开发

#### 文章工具实现
```python
# halo_plugin/tools/article_tools.py
from typing import Dict, List, Optional, Any
from ..api.client import HaloAPIClient
from ..utils.validators import validate_post_data
from .base_tool import BaseTool

class ArticleTools(BaseTool):
    def __init__(self, client: HaloAPIClient):
        super().__init__(client)
    
    def get_posts(self, page: int = 1, size: int = 10, **filters) -> Dict[str, Any]:
        """获取文章列表"""
        params = {
            'page': page,
            'size': min(size, 100),  # 限制最大页面大小
            **{k: v for k, v in filters.items() if v is not None}
        }
        
        response = self.client.get('/posts', params=params)
        return self._format_posts_response(response)
    
    def create_post(self, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """创建文章"""
        # 验证输入数据
        post_data = validate_post_data({
            'title': title,
            'content': content,
            **kwargs
        })
        
        # 格式化请求数据
        request_data = self._format_post_request(post_data)
        
        # 发送创建请求
        response = self.client.post('/posts', data=request_data)
        return self._format_post_response(response)
    
    def _format_post_request(self, data: Dict) -> Dict:
        """格式化文章请求数据"""
        # 实现数据转换逻辑
        pass
```

## 4. 测试开发

### 4.1 单元测试
```python
# tests/test_auth.py
import pytest
from unittest.mock import Mock, patch
from halo_plugin.auth.authenticator import HaloAuthenticator

class TestHaloAuthenticator:
    def setup_method(self):
        self.auth = HaloAuthenticator(
            site_url="https://test.example.com",
            token="pat_test_token"
        )
    
    @patch('requests.get')
    def test_authenticate_success(self, mock_get):
        """测试认证成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        assert self.auth.authenticate() is True
    
    def test_get_headers(self):
        """测试请求头生成"""
        headers = self.auth.get_headers()
        
        assert headers['Authorization'] == 'Bearer pat_test_token'
        assert headers['Content-Type'] == 'application/json'
```

### 4.2 集成测试
```python
# tests/test_integration.py
import pytest
from halo_plugin import HaloPlugin

@pytest.mark.integration
class TestHaloPluginIntegration:
    def setup_method(self):
        self.plugin = HaloPlugin(
            site_url="https://demo.halo.run",
            token="your_test_token"
        )
    
    def test_full_workflow(self):
        """测试完整工作流"""
        # 1. 连接测试
        assert self.plugin.setup_connection()
        
        # 2. 获取文章列表
        posts = self.plugin.get_posts(size=5)
        assert len(posts['items']) <= 5
        
        # 3. 创建测试文章
        result = self.plugin.create_post(
            title="测试文章",
            content="# 测试\n这是一篇测试文章"
        )
        assert result['success'] is True
```

## 5. 调试和优化

### 5.1 日志配置
```python
# halo_plugin/utils/logger.py
import logging
import sys

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
```

### 5.2 性能监控
```python
# halo_plugin/utils/performance.py
import time
import functools
from typing import Callable

def timing_decorator(func: Callable) -> Callable:
    """性能计时装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        print(f"{func.__name__} 执行时间: {end_time - start_time:.3f}s")
        return result
    
    return wrapper
```

### 5.3 错误处理最佳实践
```python
# halo_plugin/utils/exceptions.py
class HaloPluginException(Exception):
    """插件基础异常"""
    pass

class AuthenticationError(HaloPluginException):
    """认证错误"""
    pass

class APIException(HaloPluginException):
    """API 调用异常"""
    pass

class ValidationError(HaloPluginException):
    """数据验证异常"""
    pass

# 使用示例
def safe_api_call(func):
    """安全的 API 调用装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.ConnectionError:
            raise APIException("网络连接失败，请检查网络设置")
        except requests.Timeout:
            raise APIException("请求超时，请稍后重试")
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError("认证失败，请检查访问令牌")
            raise APIException(f"HTTP 错误: {e.response.status_code}")
    
    return wrapper
```

## 6. 部署和发布

### 6.1 打包配置
```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="dify-halo-plugin",
    version="1.0.0",
    description="Dify Halo 集成插件",
    packages=find_packages(),
    install_requires=[
        "dify-plugin-framework>=1.0.0",
        "requests>=2.28.0",
        "pydantic>=1.10.0",
        "cryptography>=3.4.0",
        "pyyaml>=6.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
```

### 6.2 持续集成配置
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Lint with pylint
      run: pylint halo_plugin
    
    - name: Test with pytest
      run: pytest tests/ -v --cov=halo_plugin
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

## 7. 开发最佳实践

### 7.1 代码审查清单
- [ ] 代码符合 PEP 8 规范
- [ ] 函数和类有完整的文档字符串
- [ ] 添加了适当的类型注解
- [ ] 包含错误处理逻辑
- [ ] 编写了相应的单元测试
- [ ] 性能考虑（缓存、连接池等）
- [ ] 安全考虑（输入验证、敏感信息处理）

### 7.2 Git 工作流
```bash
# 创建功能分支
git checkout -b feature/article-management

# 提交代码
git add .
git commit -m "feat: 添加文章管理功能"

# 推送到远程
git push origin feature/article-management

# 创建 Pull Request
```

### 7.3 版本管理
- 使用语义化版本号 (Semantic Versioning)
- 主版本号：不兼容的 API 修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

---

**文档版本**: v1.0.0  
**创建日期**: 2024年12月  
**开发负责人**: 技术团队  
**审核人**: 技术经理 