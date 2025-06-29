from collections.abc import Generator
from typing import Any
import logging
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)


class HaloPostGetTool(Tool):
    """Halo 文章获取工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        从 Halo CMS 获取指定文章
        
        Args:
            tool_parameters: 工具参数
                - post_id (str): 文章ID
                - include_content (bool, optional): 是否包含文章内容
        
        Returns:
            文章详细信息
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
            include_content = tool_parameters.get("include_content", True)
            
            # 验证必需参数
            if not post_id:
                yield self.create_text_message("❌ 文章 ID 不能为空。")
                return
            
            # 创建HTTP会话
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'Dify-Halo-Plugin/1.0'
            })
            
            yield self.create_text_message(f"🔍 正在获取文章 {post_id}...")
            
            # 获取文章基本信息
            response = session.get(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                timeout=30
            )
            
            if response.status_code == 404:
                yield self.create_text_message(f"❓ 未找到ID为 `{post_id}` 的文章。请检查文章ID是否正确。")
                return
            elif response.status_code == 401:
                yield self.create_text_message("❌ 认证失败，请检查访问令牌")
                return
            elif response.status_code == 403:
                yield self.create_text_message("❌ 权限不足")
                return
            elif response.status_code != 200:
                yield self.create_text_message(f"❌ 获取文章失败: HTTP {response.status_code}")
                return
            
            post_data = response.json()
            
            # 获取文章内容（如果需要）
            content = ""
            if include_content:
                try:
                    content_response = session.get(
                        f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_id}/content",
                        timeout=30
                    )
                    if content_response.status_code == 200:
                        content_data = content_response.json()
                        content = content_data.get("content", "")
                except Exception as e:
                    logger.warning(f"Failed to fetch post content: {e}")
            
            # 解析文章数据
            spec = post_data.get("spec", {})
            status = post_data.get("status", {})
            metadata = post_data.get("metadata", {})
            
            # 获取分类名称（而不是ID）
            category_names = []
            for cat_id in spec.get("categories", []):
                try:
                    cat_response = session.get(
                        f"{base_url}/apis/content.halo.run/v1alpha1/categories/{cat_id}",
                        timeout=10
                    )
                    if cat_response.status_code == 200:
                        cat_data = cat_response.json()
                        cat_name = cat_data.get("spec", {}).get("displayName", cat_id)
                        category_names.append(cat_name)
                    else:
                        category_names.append(cat_id)
                except:
                    category_names.append(cat_id)
            
            # 获取标签名称（而不是ID）
            tag_names = []
            for tag_id in spec.get("tags", []):
                try:
                    tag_response = session.get(
                        f"{base_url}/apis/content.halo.run/v1alpha1/tags/{tag_id}",
                        timeout=10
                    )
                    if tag_response.status_code == 200:
                        tag_data = tag_response.json()
                        tag_name = tag_data.get("spec", {}).get("displayName", tag_id)
                        tag_names.append(tag_name)
                    else:
                        tag_names.append(tag_id)
                except:
                    tag_names.append(tag_id)
            
            # 格式化响应
            response_lines = [
                "✅ **文章获取成功！**",
                "",
                f"📝 **标题**: {spec.get('title', '')}",
                f"🆔 **ID**: {metadata.get('name', '')}",
                f"🔗 **别名**: {spec.get('slug', '')}",
                f"📊 **状态**: {'已发布' if spec.get('publish', False) else '草稿'}",
                f"📌 **置顶**: {'是' if spec.get('pinned', False) else '否'}",
                f"💬 **允许评论**: {'是' if spec.get('allowComment', True) else '否'}",
            ]
            
            if category_names:
                response_lines.append(f"📁 **分类**: {', '.join(category_names)}")
            
            if tag_names:
                response_lines.append(f"🏷️ **标签**: {', '.join(tag_names)}")
            
            excerpt = spec.get("excerpt", {}).get("raw", "")
            if excerpt:
                response_lines.append(f"📄 **摘要**: {excerpt}")
            
            response_lines.extend([
                f"🕒 **创建时间**: {metadata.get('creationTimestamp', '')}",
                f"🔄 **修改时间**: {metadata.get('lastModificationTimestamp', '')}",
            ])
            
            if include_content and content:
                content_preview = content[:300] + ("..." if len(content) > 300 else "")
                response_lines.extend([
                    "",
                    "📄 **内容预览**:",
                    f"```markdown\n{content_preview}\n```"
                ])
            
            yield self.create_text_message('\n'.join(response_lines))
            
            # 返回详细的JSON信息
            result_info = {
                "success": True,
                "post": {
                    "id": metadata.get('name', ''),
                    "title": spec.get('title', ''),
                    "slug": spec.get('slug', ''),
                    "published": spec.get('publish', False),
                    "pinned": spec.get('pinned', False),
                    "allow_comment": spec.get('allowComment', True),
                    "tags": tag_names,
                    "tag_ids": spec.get('tags', []),
                    "categories": category_names,
                    "category_ids": spec.get('categories', []),
                    "excerpt": excerpt,
                    "cover": spec.get('cover', ''),
                    "created_time": metadata.get('creationTimestamp', ''),
                    "updated_time": metadata.get('lastModificationTimestamp', ''),
                    "content": content if include_content else None
                }
            }
            
            yield self.create_json_message(result_info)
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("❌ 请求超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            yield self.create_text_message("❌ 连接失败，请检查站点地址是否正确")
        except Exception as e:
            logger.error(f"Unexpected error in post get tool: {e}")
            yield self.create_text_message(f"❌ 获取文章失败: {str(e)}") 