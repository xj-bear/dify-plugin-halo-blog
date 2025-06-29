from collections.abc import Generator
from typing import Any
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)


class HaloSetupTool(Tool):
    """Halo CMS 连接设置工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        测试 Halo CMS 连接和认证
        
        Returns:
            连接状态和用户信息
        """
        try:
            # 获取凭据
            credentials = self.runtime.credentials
            base_url = credentials.get("base_url", "").strip()
            access_token = credentials.get("access_token", "").strip()
            
            if not base_url or not access_token:
                yield self.create_text_message("❌ 缺少必要的连接配置。请检查 Halo CMS URL 和访问令牌设置。")
                return
            
            # 基本格式验证
            if not base_url.startswith(('http://', 'https://')):
                yield self.create_text_message("❌ 无效的URL格式。URL必须以 http:// 或 https:// 开头。")
                return
            
            if len(access_token) < 10:
                yield self.create_text_message("❌ 访问令牌格式无效。令牌长度过短。")
                return
            
            # 创建HTTP会话
            session = requests.Session()
            
            # 配置重试策略
            retry_strategy = Retry(
                total=2,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
            )
            
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            
            # 设置请求头
            session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'Dify-Halo-Plugin/1.0'
            })
            
            yield self.create_text_message("🔍 正在验证连接和令牌...")
            
            # 严格的token验证 - 尝试访问需要认证的API
            test_endpoints = [
                "/apis/content.halo.run/v1alpha1/posts?page=0&size=1",
                "/apis/api.console.halo.run/v1alpha1/users/-/profile"
            ]
            
            valid_token = False
            for endpoint in test_endpoints:
                try:
                    response = session.get(
                        f"{base_url.rstrip('/')}{endpoint}",
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        valid_token = True
                        break
                    elif response.status_code == 401:
                        yield self.create_text_message("❌ 访问令牌无效或已过期。请检查令牌是否正确。")
                        return
                    elif response.status_code == 403:
                        yield self.create_text_message("❌ 令牌权限不足。请确保令牌具有以下权限：\n- post:manage（文章管理）\n- moment:manage（动态管理）")
                        return
                        
                except requests.exceptions.ConnectionError:
                    yield self.create_text_message(f"❌ 无法连接到 {base_url}。请检查URL是否正确，或网络连接。")
                    return
                except requests.exceptions.Timeout:
                    continue
            
            if not valid_token:
                yield self.create_text_message("❌ 令牌验证失败。请检查访问令牌是否有效。")
                return
            
            # 获取系统信息
            posts_total = 0
            try:
                posts_response = session.get(
                    f"{base_url.rstrip('/')}/apis/content.halo.run/v1alpha1/posts?page=0&size=1",
                    timeout=10
                )
                if posts_response.status_code == 200:
                    posts_data = posts_response.json()
                    posts_total = posts_data.get("total", 0)
            except Exception:
                pass
            
            # 获取分类信息
            categories_total = 0
            try:
                cat_response = session.get(
                    f"{base_url.rstrip('/')}/apis/content.halo.run/v1alpha1/categories?page=0&size=1",
                    timeout=10
                )
                if cat_response.status_code == 200:
                    cat_data = cat_response.json()
                    categories_total = cat_data.get("total", 0)
            except Exception:
                pass
            
            # 获取动态信息
            moments_total = 0
            try:
                moment_response = session.get(
                    f"{base_url.rstrip('/')}/apis/moment.halo.run/v1alpha1/moments?page=0&size=1",
                    timeout=10
                )
                if moment_response.status_code == 200:
                    moment_data = moment_response.json()
                    moments_total = moment_data.get("total", 0)
            except Exception:
                pass
            
            # 格式化响应
            response_lines = [
                "✅ **Halo CMS 连接成功**",
                "",
                f"🌐 **站点信息**",
                f"- URL: {base_url}",
                f"- 认证状态: 已验证 ✓",
                "",
                "📊 **系统统计**",
                f"- 分类数量: {categories_total}",
                f"- 文章总数: {posts_total}",
                f"- 动态总数: {moments_total}",
                "",
                "🔧 **可用功能**",
                "- ✅ 文章管理 (创建、读取、更新、删除、列表)",
                "- ✅ 动态管理 (创建、列表)",
                "- ✅ 分类和标签查询",
                "",
                "🎉 您可以开始使用 Halo 博客工具了！"
            ]
            
            yield self.create_text_message('\n'.join(response_lines))
            
            # 返回详细的JSON信息供调试
            debug_info = {
                "connection_status": "success",
                "base_url": base_url,
                "authenticated": True,
                "token_validated": True,
                "system_stats": {
                    "categories_count": categories_total,
                    "posts_total": posts_total,
                    "moments_total": moments_total
                }
            }
            
            yield self.create_json_message(debug_info)
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("❌ 连接超时，请检查网络连接和服务器状态")
        except requests.exceptions.ConnectionError:
            yield self.create_text_message("❌ 无法连接到 Halo CMS 服务器，请检查 URL 是否正确")
        except Exception as e:
            logger.error(f"Setup tool error: {e}")
            yield self.create_text_message(f"❌ 连接测试失败: {str(e)}\n\n请检查网络连接和配置信息。") 