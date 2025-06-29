from collections.abc import Generator
from typing import Any
import logging
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)


class HaloPostDeleteTool(Tool):
    """Halo 文章删除工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        删除 Halo CMS 中的文章
        
        Args:
            tool_parameters: 工具参数
                - post_id (str): 文章ID
                - confirm (bool): 确认删除
        
        Returns:
            删除操作结果
        """
        try:
            # 获取凭据
            credentials = self.runtime.credentials
            base_url = credentials.get("base_url", "").strip().rstrip('/')
            access_token = credentials.get("access_token", "").strip()
            
            if not base_url or not access_token:
                yield self.create_text_message("❌ 缺少必要的连接配置。请先使用设置工具配置 Halo CMS 连接。")
                return
            
            # 获取参数
            post_id = tool_parameters.get("post_id", "").strip()
            confirm = tool_parameters.get("confirm", False)
            
            # 验证必需参数
            if not post_id:
                yield self.create_text_message("❌ 文章 ID 不能为空。")
                return
            
            if not confirm:
                yield self.create_text_message(
                    "⚠️ **安全确认**\n\n"
                    "删除文章是永久性操作，无法撤销。\n"
                    "如果您确定要删除此文章，请将 `confirm` 参数设置为 `true`。\n\n"
                    f"要删除的文章ID: `{post_id}`"
                )
                return
            
            # 创建HTTP会话
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'Dify-Halo-Plugin/1.0'
            })
            
            # 先获取文章信息，用于确认和记录
            yield self.create_text_message(f"🔍 正在获取文章 {post_id} 的信息...")
            
            get_response = session.get(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                timeout=30
            )
            
            if get_response.status_code == 404:
                yield self.create_text_message(f"❓ 未找到ID为 `{post_id}` 的文章。可能已经被删除或ID不正确。")
                return
            elif get_response.status_code != 200:
                yield self.create_text_message(f"❌ 获取文章信息失败: HTTP {get_response.status_code}")
                return
            
            post_data = get_response.json()
            post_title = post_data.get("spec", {}).get("title", "未知标题")
            post_published = post_data.get("spec", {}).get("publish", False)
            post_tags = post_data.get("spec", {}).get("tags", [])
            post_categories = post_data.get("spec", {}).get("categories", [])
            
            # 显示要删除的文章信息
            yield self.create_text_message(
                f"📄 **即将删除的文章**：\n\n"
                f"- 标题: {post_title}\n"
                f"- ID: {post_id}\n"
                f"- 状态: {'已发布' if post_published else '草稿'}\n"
                f"- 标签: {', '.join(post_tags) if post_tags else '无'}\n"
                f"- 分类: {', '.join(post_categories) if post_categories else '无'}\n\n"
                f"🗑️ 正在执行删除操作..."
            )
            
            # 执行删除
            delete_response = session.delete(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                timeout=30
            )
            
            if delete_response.status_code == 404:
                yield self.create_text_message(f"❓ 文章 {post_id} 可能已经被删除")
                return
            elif delete_response.status_code == 401:
                yield self.create_text_message("❌ 认证失败，请检查访问令牌")
                return
            elif delete_response.status_code == 403:
                yield self.create_text_message("❌ 权限不足，请确保令牌具有文章删除权限")
                return
            elif delete_response.status_code not in [200, 204]:
                error_detail = ""
                try:
                    error_data = delete_response.json()
                    error_detail = error_data.get('detail', delete_response.text)
                except:
                    error_detail = delete_response.text
                yield self.create_text_message(f"❌ 删除文章失败: HTTP {delete_response.status_code} - {error_detail}")
                return
            
            response_lines = [
                "✅ **文章删除成功！**",
                "",
                f"📋 **已删除文章信息**：",
                f"- ID: `{post_id}`",
                f"- 标题: {post_title}",
                f"- 状态: {'已发布' if post_published else '草稿'}",
            ]
            
            if post_tags:
                response_lines.append(f"- 标签: {', '.join(post_tags)}")
            if post_categories:
                response_lines.append(f"- 分类: {', '.join(post_categories)}")
            
            response_lines.extend([
                "",
                "⚠️ **注意**：此操作已永久完成，无法撤销。"
            ])
            
            yield self.create_text_message('\n'.join(response_lines))
            
            # 返回删除结果信息
            result_info = {
                "success": True,
                "deleted_post": {
                    "id": post_id,
                    "title": post_title,
                    "published": post_published,
                    "tags": post_tags,
                    "categories": post_categories
                }
            }
            
            yield self.create_json_message(result_info)
                
        except requests.exceptions.Timeout:
            yield self.create_text_message("❌ 请求超时")
        except requests.exceptions.ConnectionError:
            yield self.create_text_message("❌ 无法连接到服务器")
        except Exception as e:
            logger.error(f"Unexpected error in post delete tool: {e}")
            yield self.create_text_message(f"❌ 删除文章失败: {str(e)}") 