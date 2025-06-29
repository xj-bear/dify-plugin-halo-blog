# 测试计划文档

## 1. 测试概述

### 1.1 测试目标
- 确保插件功能完整性和正确性
- 验证系统稳定性和性能表现
- 保障数据安全和用户体验
- 建立可持续的质量保证体系

### 1.2 测试范围
- **功能测试**: 所有核心功能模块
- **集成测试**: Dify 平台和 Halo API 集成
- **性能测试**: 响应时间和并发处理能力
- **安全测试**: 认证、授权和数据保护
- **兼容性测试**: 多版本环境验证
- **用户体验测试**: 易用性和错误处理

### 1.3 测试环境
```
开发环境:
- Python 3.8+
- Dify 最新版本
- Halo 2.21+ 测试实例

测试环境:
- 模拟生产环境配置
- 多版本 Halo 实例
- 网络延迟模拟

生产验证环境:
- 真实用户数据量级
- 完整的监控系统
- 性能基准测试
```

## 2. 单元测试

### 2.1 测试策略
- **覆盖率目标**: ≥ 80%
- **测试框架**: pytest
- **Mock 策略**: 模拟外部 API 调用
- **断言库**: pytest + unittest.mock

### 2.2 认证模块测试

#### HaloAuthenticator 测试
```python
# tests/test_auth/test_authenticator.py
import pytest
from unittest.mock import Mock, patch
from halo_plugin.auth.authenticator import HaloAuthenticator

class TestHaloAuthenticator:
    def setup_method(self):
        self.auth = HaloAuthenticator(
            site_url="https://test.example.com",
            token="pat_test_token_123456789"
        )
    
    def test_init_normalizes_url(self):
        """测试URL标准化"""
        auth = HaloAuthenticator("https://test.com/", "token")
        assert auth.site_url == "https://test.com"
    
    def test_token_validation(self):
        """测试令牌格式验证"""
        # 有效令牌
        assert self.auth._is_valid_token_format("pat_123456789")
        
        # 无效令牌
        assert not self.auth._is_valid_token_format("invalid_token")
        assert not self.auth._is_valid_token_format("")
    
    @patch('requests.get')
    def test_authenticate_success(self, mock_get):
        """测试认证成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "admin"}
        mock_get.return_value = mock_response
        
        result = self.auth.authenticate()
        assert result is True
    
    @patch('requests.get')
    def test_authenticate_failure(self, mock_get):
        """测试认证失败"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.auth.authenticate()
        assert result is False
    
    def test_get_headers(self):
        """测试请求头生成"""
        headers = self.auth.get_headers()
        
        assert headers['Authorization'] == 'Bearer pat_test_token_123456789'
        assert headers['Content-Type'] == 'application/json'
        assert 'User-Agent' in headers
```

### 2.3 API 客户端测试

#### HaloAPIClient 测试
```python
# tests/test_api/test_client.py
import pytest
from unittest.mock import Mock, patch
from halo_plugin.api.client import HaloAPIClient
from halo_plugin.auth.authenticator import HaloAuthenticator

class TestHaloAPIClient:
    def setup_method(self):
        self.auth = Mock(spec=HaloAuthenticator)
        self.auth.site_url = "https://test.com"
        self.auth.get_headers.return_value = {
            'Authorization': 'Bearer token',
            'Content-Type': 'application/json'
        }
        self.client = HaloAPIClient(self.auth)
    
    @patch('requests.Session.get')
    def test_get_request_success(self, mock_get):
        """测试GET请求成功"""
        mock_response = Mock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get('/posts')
        
        assert result == {"data": "test"}
        mock_get.assert_called_once()
    
    @patch('requests.Session.post')
    def test_post_request_with_data(self, mock_post):
        """测试POST请求带数据"""
        mock_response = Mock()
        mock_response.json.return_value = {"id": "123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        data = {"title": "Test Post"}
        result = self.client.post('/posts', data=data)
        
        assert result == {"id": "123"}
        mock_post.assert_called_once()
        # 验证调用参数
        args, kwargs = mock_post.call_args
        assert kwargs['json'] == data
```

### 2.4 工具模块测试

#### ArticleTools 测试
```python
# tests/test_tools/test_article_tools.py
import pytest
from unittest.mock import Mock
from halo_plugin.tools.article_tools import ArticleTools

class TestArticleTools:
    def setup_method(self):
        self.mock_client = Mock()
        self.tools = ArticleTools(self.mock_client)
    
    def test_get_posts_default_params(self):
        """测试获取文章列表默认参数"""
        mock_response = {
            "items": [{"id": "1", "title": "Test"}],
            "page": 1,
            "size": 10,
            "total": 1
        }
        self.mock_client.get.return_value = mock_response
        
        result = self.tools.get_posts()
        
        # 验证API调用
        self.mock_client.get.assert_called_once_with(
            '/posts', 
            params={'page': 1, 'size': 10}
        )
        
        # 验证返回数据格式
        assert 'items' in result
        assert 'pagination' in result
    
    def test_create_post_validation(self):
        """测试创建文章数据验证"""
        # 测试缺少必需参数
        with pytest.raises(ValueError, match="标题不能为空"):
            self.tools.create_post("", "content")
        
        # 测试标题长度限制
        long_title = "x" * 256
        with pytest.raises(ValueError, match="标题长度不能超过255字符"):
            self.tools.create_post(long_title, "content")
    
    def test_create_post_success(self):
        """测试成功创建文章"""
        mock_response = {
            "metadata": {"name": "post-123"},
            "spec": {"title": "Test Post"}
        }
        self.mock_client.post.return_value = mock_response
        
        result = self.tools.create_post(
            title="Test Post",
            content="Test content",
            tags=["test"]
        )
        
        assert result['id'] == "post-123"
        assert result['title'] == "Test Post"
```

### 2.5 数据验证测试

#### DataValidator 测试
```python
# tests/test_utils/test_validators.py
import pytest
from halo_plugin.utils.validators import DataValidator

class TestDataValidator:
    def setup_method(self):
        self.validator = DataValidator()
    
    def test_validate_post_data_success(self):
        """测试有效文章数据验证"""
        data = {
            "title": "Valid Title",
            "content": "Valid content",
            "categories": ["Tech"],
            "tags": ["Python", "AI"]
        }
        
        result = self.validator.validate_post_data(data)
        assert result == data
    
    def test_validate_post_data_failures(self):
        """测试无效文章数据验证"""
        # 空标题
        with pytest.raises(ValueError, match="标题不能为空"):
            self.validator.validate_post_data({"title": "", "content": "test"})
        
        # 过长标题
        with pytest.raises(ValueError, match="标题长度不能超过255字符"):
            self.validator.validate_post_data({
                "title": "x" * 256,
                "content": "test"
            })
        
        # 过多分类
        with pytest.raises(ValueError, match="分类数量不能超过20个"):
            self.validator.validate_post_data({
                "title": "test",
                "content": "test",
                "categories": [f"cat{i}" for i in range(21)]
            })
```

## 3. 集成测试

### 3.1 测试策略
- **环境要求**: 完整的 Dify 和 Halo 测试环境
- **数据准备**: 测试数据集和清理策略
- **测试隔离**: 每个测试用例独立的数据环境

### 3.2 完整工作流测试

#### 文章创建工作流测试
```python
# tests/test_integration/test_article_workflow.py
import pytest
from halo_plugin import HaloPlugin

@pytest.mark.integration
class TestArticleWorkflow:
    def setup_method(self):
        self.plugin = HaloPlugin(
            site_url=pytest.config.get("HALO_SITE_URL"),
            token=pytest.config.get("HALO_TOKEN")
        )
    
    def test_complete_article_lifecycle(self):
        """测试文章完整生命周期"""
        # 1. 创建文章
        create_result = self.plugin.create_post(
            title="集成测试文章",
            content="# 测试\n这是集成测试文章",
            categories=["测试"],
            tags=["集成测试"],
            publish_status="DRAFT"
        )
        
        assert create_result['success'] is True
        post_id = create_result['data']['id']
        
        # 2. 获取文章详情
        detail_result = self.plugin.get_post_detail(post_id)
        assert detail_result['success'] is True
        assert detail_result['data']['title'] == "集成测试文章"
        
        # 3. 更新文章
        update_result = self.plugin.update_post(
            post_id,
            title="更新后的测试文章",
            publish_status="PUBLISHED"
        )
        assert update_result['success'] is True
        
        # 4. 验证更新
        updated_detail = self.plugin.get_post_detail(post_id)
        assert updated_detail['data']['title'] == "更新后的测试文章"
        assert updated_detail['data']['status'] == "PUBLISHED"
        
        # 5. 清理测试数据
        self.plugin.delete_post(post_id)
```

### 3.3 错误处理集成测试

#### 网络错误测试
```python
# tests/test_integration/test_error_handling.py
@pytest.mark.integration 
class TestErrorHandling:
    def test_network_timeout_handling(self):
        """测试网络超时处理"""
        plugin = HaloPlugin(
            site_url="https://unreachable.example.com",
            token="pat_fake_token"
        )
        
        result = plugin.get_posts()
        
        assert result['success'] is False
        assert 'network' in result['error']['code'].lower()
    
    def test_invalid_token_handling(self):
        """测试无效令牌处理"""
        plugin = HaloPlugin(
            site_url=pytest.config.get("HALO_SITE_URL"),
            token="pat_invalid_token"
        )
        
        result = plugin.get_posts()
        
        assert result['success'] is False
        assert result['error']['code'] == 'AUTH_TOKEN_INVALID'
```

## 4. 性能测试

### 4.1 性能基准
- **API 响应时间**: 95% 请求 ≤ 2秒
- **并发处理**: 支持 10 个并发请求
- **内存使用**: 正常操作 ≤ 100MB
- **错误率**: 正常环境 ≤ 1%

### 4.2 响应时间测试

#### API 性能测试
```python
# tests/test_performance/test_response_time.py
import time
import pytest
from concurrent.futures import ThreadPoolExecutor

@pytest.mark.performance
class TestResponseTime:
    def test_get_posts_response_time(self):
        """测试获取文章列表响应时间"""
        plugin = self._get_test_plugin()
        
        start_time = time.time()
        result = plugin.get_posts(size=10)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert result['success'] is True
        assert response_time < 2.0  # 2秒内响应
    
    def test_concurrent_requests(self):
        """测试并发请求处理"""
        plugin = self._get_test_plugin()
        
        def make_request():
            return plugin.get_posts(size=5)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
            end_time = time.time()
        
        # 验证所有请求成功
        success_count = sum(1 for r in results if r['success'])
        assert success_count >= 9  # 允许1个失败
        
        # 验证总时间合理
        total_time = end_time - start_time
        assert total_time < 10.0  # 10秒内完成所有请求
```

### 4.3 内存使用测试

#### 内存泄漏测试
```python
# tests/test_performance/test_memory.py
import gc
import psutil
import pytest

@pytest.mark.performance
class TestMemoryUsage:
    def test_memory_usage_during_operations(self):
        """测试操作过程中的内存使用"""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        plugin = self._get_test_plugin()
        
        # 执行多次操作
        for i in range(100):
            plugin.get_posts(page=i % 10 + 1, size=10)
            
            if i % 10 == 0:
                gc.collect()  # 强制垃圾回收
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # 内存增长应在合理范围内
        assert memory_increase < 50  # 不超过50MB增长
```

## 5. 安全测试

### 5.1 认证安全测试

#### 令牌安全测试
```python
# tests/test_security/test_auth_security.py
@pytest.mark.security
class TestAuthSecurity:
    def test_token_encryption_storage(self):
        """测试令牌加密存储"""
        from halo_plugin.auth.token_manager import SecureTokenManager
        
        manager = SecureTokenManager()
        original_token = "pat_sensitive_token_123"
        
        # 存储令牌
        manager.store_token("test.com", original_token)
        
        # 获取令牌
        retrieved_token = manager.get_token("test.com")
        
        assert retrieved_token == original_token
        
        # 验证存储的不是明文
        # 这里需要检查实际存储的内容是加密的
    
    def test_token_format_validation(self):
        """测试令牌格式验证"""
        from halo_plugin.auth.authenticator import HaloAuthenticator
        
        auth = HaloAuthenticator("https://test.com", "valid_token")
        
        # 有效格式
        assert auth._is_valid_token_format("pat_1234567890123456")
        
        # 无效格式
        assert not auth._is_valid_token_format("invalid")
        assert not auth._is_valid_token_format("")
        assert not auth._is_valid_token_format("pat_")
```

### 5.2 输入验证安全测试

#### SQL注入防护测试
```python
# tests/test_security/test_input_validation.py
@pytest.mark.security
class TestInputValidation:
    def test_sql_injection_prevention(self):
        """测试SQL注入防护"""
        plugin = self._get_test_plugin()
        
        # 尝试SQL注入攻击
        malicious_inputs = [
            "'; DROP TABLE posts; --",
            "1' OR '1'='1",
            "<script>alert('xss')</script>"
        ]
        
        for malicious_input in malicious_inputs:
            result = plugin.get_posts(keyword=malicious_input)
            
            # 应该安全处理，不应该出现SQL错误
            assert result['success'] in [True, False]  # 不应该崩溃
    
    def test_xss_prevention(self):
        """测试XSS攻击防护"""
        plugin = self._get_test_plugin()
        
        xss_content = "<script>alert('xss')</script>"
        
        result = plugin.create_post(
            title="XSS Test",
            content=xss_content
        )
        
        if result['success']:
            # 验证内容被正确转义
            detail = plugin.get_post_detail(result['data']['id'])
            assert '<script>' not in detail['data']['content']
```

## 6. 兼容性测试

### 6.1 版本兼容性测试

#### Halo版本兼容性
```python
# tests/test_compatibility/test_halo_versions.py
@pytest.mark.compatibility
@pytest.mark.parametrize("halo_version", ["2.21.0", "2.22.0", "2.23.0"])
class TestHaloVersionCompatibility:
    def test_basic_operations(self, halo_version):
        """测试基本操作在不同Halo版本的兼容性"""
        plugin = self._get_plugin_for_version(halo_version)
        
        # 测试基本操作
        posts_result = plugin.get_posts()
        assert posts_result['success'] is True
        
        categories_result = plugin.get_categories()
        assert categories_result['success'] is True
```

### 6.2 环境兼容性测试

#### Python版本兼容性
```python
# tests/test_compatibility/test_python_versions.py
import sys
import pytest

@pytest.mark.compatibility
class TestPythonVersionCompatibility:
    def test_python_version_support(self):
        """测试Python版本支持"""
        major, minor = sys.version_info[:2]
        
        # 确保支持的Python版本
        assert major == 3
        assert minor >= 8
    
    @pytest.mark.skipif(sys.version_info < (3, 9), reason="需要Python 3.9+")
    def test_python39_features(self):
        """测试Python 3.9+特性"""
        # 测试特定版本的功能
        pass
```

## 7. 用户体验测试

### 7.1 易用性测试

#### 错误信息友好性测试
```python
# tests/test_ux/test_error_messages.py
@pytest.mark.ux
class TestErrorMessages:
    def test_user_friendly_error_messages(self):
        """测试用户友好的错误信息"""
        plugin = HaloPlugin(
            site_url="invalid-url",
            token="invalid-token"
        )
        
        result = plugin.get_posts()
        
        assert result['success'] is False
        error = result['error']
        
        # 错误信息应该清晰友好
        assert 'message' in error
        assert len(error['message']) > 0
        assert not any(tech_term in error['message'].lower() 
                      for tech_term in ['traceback', 'exception', 'stack'])
```

### 7.2 配置便利性测试

#### 配置验证测试
```python
# tests/test_ux/test_configuration.py
@pytest.mark.ux
class TestConfiguration:
    def test_connection_validation(self):
        """测试连接配置验证"""
        # 测试有效配置
        valid_config = {
            "site_url": "https://demo.halo.run",
            "access_token": "pat_valid_token_123456"
        }
        
        result = self._validate_config(valid_config)
        assert result['valid'] is True
        
        # 测试无效配置
        invalid_configs = [
            {"site_url": "invalid-url", "access_token": "token"},
            {"site_url": "https://test.com", "access_token": ""},
            {"site_url": "", "access_token": "pat_token"}
        ]
        
        for config in invalid_configs:
            result = self._validate_config(config)
            assert result['valid'] is False
            assert 'message' in result
```

## 8. 测试自动化

### 8.1 CI/CD 集成

#### GitHub Actions配置
```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
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
        pip install -r requirements-test.txt
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=halo_plugin --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v -m "not slow"
      env:
        HALO_SITE_URL: ${{ secrets.HALO_SITE_URL }}
        HALO_TOKEN: ${{ secrets.HALO_TOKEN }}
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 8.2 测试报告

#### 覆盖率报告
```python
# pytest.ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra
    --cov=halo_plugin
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    security: Security tests
    compatibility: Compatibility tests
    ux: User experience tests
    slow: Slow running tests
```

### 8.3 性能监控

#### 性能基准测试
```python
# tests/benchmarks/benchmark_api.py
import pytest
import time
from statistics import mean, median

@pytest.mark.benchmark
class TestPerformanceBenchmark:
    def test_api_response_time_benchmark(self, benchmark):
        """API响应时间基准测试"""
        plugin = self._get_test_plugin()
        
        def api_call():
            return plugin.get_posts(size=10)
        
        result = benchmark(api_call)
        assert result['success'] is True
        
        # 验证性能指标
        assert benchmark.stats['mean'] < 1.0  # 平均响应时间 < 1秒
        assert benchmark.stats['max'] < 3.0   # 最大响应时间 < 3秒
```

## 9. 测试数据管理

### 9.1 测试数据准备

#### 测试夹具
```python
# tests/conftest.py
import pytest
from halo_plugin import HaloPlugin

@pytest.fixture(scope="session")
def test_plugin():
    """测试插件实例"""
    return HaloPlugin(
        site_url=pytest.config.get("HALO_SITE_URL"),
        token=pytest.config.get("HALO_TOKEN")
    )

@pytest.fixture
def sample_post_data():
    """示例文章数据"""
    return {
        "title": "测试文章",
        "content": "# 测试\n这是测试内容",
        "categories": ["测试"],
        "tags": ["unittest"],
        "publish_status": "DRAFT"
    }

@pytest.fixture
def cleanup_posts():
    """清理测试文章"""
    created_posts = []
    
    yield created_posts
    
    # 测试后清理
    plugin = test_plugin()
    for post_id in created_posts:
        try:
            plugin.delete_post(post_id)
        except:
            pass  # 忽略删除错误
```

### 9.2 测试环境隔离

#### 数据库隔离
```python
# tests/utils/test_isolation.py
class TestIsolation:
    def setup_method(self):
        """每个测试方法前的设置"""
        self.test_prefix = f"test_{int(time.time())}_"
        self.created_resources = []
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        self._cleanup_test_resources()
    
    def _cleanup_test_resources(self):
        """清理测试资源"""
        for resource in self.created_resources:
            try:
                self._delete_resource(resource)
            except Exception as e:
                # 记录但不中断清理过程
                print(f"清理资源失败: {resource}, 错误: {e}")
```

## 10. 测试执行计划

### 10.1 测试阶段安排

| 阶段 | 测试类型 | 时间安排 | 负责人 |
|------|----------|----------|--------|
| 开发阶段 | 单元测试 | 每日执行 | 开发工程师 |
| 集成阶段 | 集成测试 | 每次提交 | 测试工程师 |
| 发布前 | 全面测试 | 发布前1周 | QA团队 |
| 发布后 | 回归测试 | 发布后24小时 | 运维团队 |

### 10.2 测试通过标准

#### 发布标准
- [ ] 所有单元测试通过
- [ ] 代码覆盖率 ≥ 80%
- [ ] 集成测试通过率 ≥ 95%
- [ ] 性能测试符合基准
- [ ] 安全测试无高危漏洞
- [ ] 兼容性测试通过
- [ ] 用户体验测试反馈良好

#### 质量门禁
```python
# 质量检查脚本示例
def quality_gate_check():
    """质量门禁检查"""
    results = {
        'unit_tests': run_unit_tests(),
        'coverage': check_code_coverage(),
        'integration_tests': run_integration_tests(),
        'performance': check_performance_benchmarks(),
        'security': run_security_scan()
    }
    
    # 检查是否满足发布标准
    if all(results.values()):
        print("✅ 质量检查通过，可以发布")
        return True
    else:
        print("❌ 质量检查失败，请修复问题")
        return False
```

---

**文档版本**: v1.0.0  
**创建日期**: 2024年12月  
**测试负责人**: QA团队  
**审核人**: 技术经理 