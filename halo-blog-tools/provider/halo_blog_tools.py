from typing import Any
import logging
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

logger = logging.getLogger(__name__)


class HaloBlogToolsProvider(ToolProvider):
    """Halo CMS工具提供商"""
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证Halo CMS连接凭据
        
        Args:
            credentials: 包含base_url和access_token的凭据字典
            
        Raises:
            ToolProviderCredentialValidationError: 凭据验证失败时
        """
        try:
            base_url = credentials.get('base_url', '').strip()
            access_token = credentials.get('access_token', '').strip()
            
            # 检查必需字段
            if not base_url:
                raise ToolProviderCredentialValidationError("Halo CMS URL 不能为空")
            
            if not access_token:
                raise ToolProviderCredentialValidationError("访问令牌不能为空")
            
            # 清理URL
            base_url = base_url.rstrip('/')
            
            # 验证URL格式
            if not (base_url.startswith('http://') or base_url.startswith('https://')):
                raise ToolProviderCredentialValidationError("Halo CMS URL 必须以 http:// 或 https:// 开头")
            
            # 创建会话并设置认证头
            session = requests.Session()
            session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'User-Agent': 'Dify-Halo-Plugin/1.0'
            })
            
            # 尝试访问文章API来验证认证
            test_endpoints = [
                '/apis/content.halo.run/v1alpha1/posts?page=0&size=1',
                '/apis/content.halo.run/v1alpha1/categories?page=0&size=1'
            ]
            
            verification_passed = False
            last_error = None
            
            for endpoint in test_endpoints:
                try:
                    response = session.get(f"{base_url}{endpoint}", timeout=15)
                    
                    if response.status_code == 401:
                        raise ToolProviderCredentialValidationError(
                            "访问令牌无效或已过期，请检查令牌是否正确"
                        )
                    elif response.status_code == 403:
                        raise ToolProviderCredentialValidationError(
                            "访问令牌权限不足，请确保令牌具有 'post:manage' 和 'moment:manage' 权限"
                        )
                    elif response.status_code == 404:
                        # 404可能表示Halo版本不兼容或API路径错误
                        last_error = f"API端点不存在 ({response.status_code})"
                        continue
                    elif response.status_code in [200]:
                        # 成功访问API
                        verification_passed = True
                        break
                    else:
                        last_error = f"API返回错误状态码: {response.status_code}"
                        continue
                        
                except requests.exceptions.Timeout:
                    last_error = "连接超时"
                    continue
                except requests.exceptions.ConnectionError:
                    last_error = "无法连接到Halo CMS服务器"
                    continue
                except requests.exceptions.RequestException as e:
                    last_error = f"网络请求失败: {str(e)}"
                    continue
            
            if not verification_passed:
                if last_error:
                    raise ToolProviderCredentialValidationError(
                        f"验证失败: {last_error}。请检查URL是否正确以及服务器是否可访问"
                    )
                else:
                    raise ToolProviderCredentialValidationError(
                        "无法验证凭据，请检查URL和访问令牌是否正确"
                    )
            
            logger.info(f"Successfully validated Halo CMS credentials for {base_url}")
            
        except ToolProviderCredentialValidationError:
            # 重新抛出已知的验证错误
            raise
        except Exception as e:
            logger.error(f"Unexpected error during credential validation: {str(e)}")
            raise ToolProviderCredentialValidationError(
                f"验证过程中发生错误: {str(e)}"
            )
