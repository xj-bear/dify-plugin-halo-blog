"""
测试脚本：验证Halo插件的核心功能
"""

import sys
import logging
from unittest.mock import Mock, patch

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """测试所有核心模块的导入"""
    print("=== 测试模块导入 ===")
    
    try:
        from halo_plugin.exceptions import HaloPluginError, AuthenticationError
        print("✅ 异常模块导入成功")
        
        from halo_plugin.models.post import Post, PostCreateRequest
        print("✅ Post模型导入成功")
        
        from halo_plugin.models.moment import Moment, MomentCreateRequest
        print("✅ Moment模型导入成功")
        
        from halo_plugin.auth.authenticator import HaloAuthenticator
        print("✅ 认证模块导入成功")
        
        from halo_plugin.api.client import HaloAPIClient
        print("✅ API客户端导入成功")
        
        from halo_plugin.utils.validators import validate_url, validate_token
        print("✅ 验证工具导入成功")
        
        from halo_plugin.utils.formatters import format_post_summary, format_moment_summary
        print("✅ 格式化工具导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_validators():
    """测试验证器功能"""
    print("\n=== 测试验证器 ===")
    
    from halo_plugin.utils.validators import validate_url, validate_token, sanitize_content
    from halo_plugin.exceptions import ValidationError
    
    try:
        # 测试URL验证
        validate_url("https://blog.u2u.fun")
        print("✅ URL验证通过")
        
        # 测试token验证
        validate_token("test_token_123")
        print("✅ Token验证通过")
        
        # 测试内容清理
        clean_content = sanitize_content("Hello\x00World\n\rTest")
        print(f"✅ 内容清理成功: {repr(clean_content)}")
        
        # 测试错误情况
        try:
            validate_url("invalid-url")
            print("❌ URL验证应该失败")
            return False
        except ValidationError:
            print("✅ URL验证错误处理正确")
        
        return True
    except Exception as e:
        print(f"❌ 验证器测试失败: {e}")
        return False

def test_models():
    """测试数据模型"""
    print("\n=== 测试数据模型 ===")
    
    from halo_plugin.models.post import PostCreateRequest, Post
    from halo_plugin.models.moment import MomentCreateRequest, Moment
    
    try:
        # 测试创建Post请求模型
        post_request = PostCreateRequest(
            title="测试文章",
            content="这是测试内容",
            excerpt="测试摘要",
            tags=["tag1", "tag2"],
            categories=["category1"],
            publish_immediately=False
        )
        print(f"✅ PostCreateRequest创建成功: {post_request.title}")
        
        # 测试Post模型
        post = Post(
            name="test-post",
            title="测试文章",
            content="测试内容",
            published=False
        )
        print(f"✅ Post模型创建成功: {post.name}")
        
        # 测试Moment请求模型
        moment_request = MomentCreateRequest(
            content="这是一个测试动态",
            tags=["moment", "test"],
            visible="PUBLIC"
        )
        print(f"✅ MomentCreateRequest创建成功: {moment_request.content[:20]}...")
        
        return True
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}")
        return False

def test_formatters():
    """测试格式化器"""
    print("\n=== 测试格式化器 ===")
    
    from halo_plugin.models.post import Post
    from halo_plugin.models.moment import Moment
    from halo_plugin.utils.formatters import format_post_summary, format_moment_summary
    
    try:
        # 创建测试Post
        post = Post(
            name="test-post",
            title="测试文章标题",
            content="这是测试内容",
            excerpt="这是摘要",
            published=True,
            tags=["技术", "测试"],
            categories=["开发"]
        )
        
        post_summary = format_post_summary(post)
        print("✅ Post格式化成功:")
        print(post_summary[:100] + "...")
        
        # 创建测试Moment
        moment = Moment(
            name="test-moment",
            content="这是一个测试动态内容",
            tags=["动态", "测试"],
            visible="PUBLIC",
            approved=True
        )
        
        moment_summary = format_moment_summary(moment)
        print("✅ Moment格式化成功:")
        print(moment_summary[:100] + "...")
        
        return True
    except Exception as e:
        print(f"❌ 格式化器测试失败: {e}")
        return False

def test_mock_api():
    """测试模拟API调用"""
    print("\n=== 测试模拟API调用 ===")
    
    try:
        from halo_plugin.auth.authenticator import HaloAuthenticator
        from halo_plugin.api.client import HaloAPIClient
        from halo_plugin.models.post import PostCreateRequest
        
        # 创建模拟认证器
        auth = HaloAuthenticator("https://mock.example.com")
        
        # 模拟成功的认证
        with patch.object(auth, 'authenticate') as mock_auth:
            mock_auth.return_value = {
                "authenticated": True,
                "base_url": "https://mock.example.com",
                "token_valid": True
            }
            
            auth_result = auth.authenticate("mock_token")
            print(f"✅ 模拟认证成功: {auth_result}")
        
        # 测试API客户端
        api_client = HaloAPIClient(auth)
        
        # 模拟创建文章
        with patch.object(api_client, '_make_request') as mock_request:
            mock_request.return_value = {
                "metadata": {"name": "test-post-123"},
                "spec": {
                    "title": "测试文章",
                    "slug": "test-post",
                    "publish": False,
                    "tags": ["test"],
                    "categories": ["tech"]
                },
                "content": {"content": "测试内容"}
            }
            
            post_request = PostCreateRequest(
                title="测试文章",
                content="测试内容",
                tags=["test"],
                categories=["tech"]
            )
            
            result = api_client.create_post(post_request)
            print(f"✅ 模拟文章创建成功: {result.name}")
        
        return True
    except Exception as e:
        print(f"❌ 模拟API测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试Halo插件核心功能...\n")
    
    tests = [
        ("模块导入", test_imports),
        ("验证器功能", test_validators),
        ("数据模型", test_models),
        ("格式化器", test_formatters),
        ("模拟API", test_mock_api),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！插件核心功能正常。")
        return True
    else:
        print("⚠️  部分测试失败，需要检查相关功能。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 