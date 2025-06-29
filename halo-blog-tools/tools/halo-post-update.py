from collections.abc import Generator
from typing import Any
import logging
import requests
import json
import re
import time

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)


class HaloPostUpdateTool(Tool):
    """Halo CMS 文章更新工具"""
    
    def _ensure_tags_exist(self, session: requests.Session, base_url: str, tags: list) -> list:
        """确保标签存在，如果不存在则创建，返回标签ID列表"""
        existing_tags = []
        
        for tag_name in tags:
            try:
                # 检查标签是否存在
                tag_response = session.get(
                    f"{base_url}/apis/content.halo.run/v1alpha1/tags",
                    timeout=10
                )
                
                if tag_response.status_code == 200:
                    tag_data = tag_response.json()
                    items = tag_data.get("items", [])
                    
                    # 查找匹配的标签
                    found_tag = None
                    for item in items:
                        if item.get("spec", {}).get("displayName") == tag_name:
                            found_tag = item.get("metadata", {}).get("name")
                            break
                    
                    if found_tag:
                        existing_tags.append(found_tag)
                        logger.info(f"Found existing tag: {tag_name} -> {found_tag}")
                    else:
                        # 创建新标签
                        slug = tag_name.lower().replace(' ', '-').replace('中文', 'chinese')
                        tag_create_data = {
                            "apiVersion": "content.halo.run/v1alpha1",
                            "kind": "Tag",
                            "metadata": {
                                "generateName": "tag-"
                            },
                            "spec": {
                                "displayName": tag_name,
                                "slug": f"{slug}-{int(time.time())}",
                                "color": "#6366f1",
                                "cover": ""
                            }
                        }
                        
                        create_response = session.post(
                            f"{base_url}/apis/content.halo.run/v1alpha1/tags",
                            data=json.dumps(tag_create_data),
                            timeout=10
                        )
                        
                        if create_response.status_code in [200, 201]:
                            created_tag = create_response.json()
                            tag_id = created_tag['metadata']['name']
                            existing_tags.append(tag_id)
                            logger.info(f"标签 '{tag_name}' 创建成功: {tag_id}")
                        else:
                            logger.error(f"标签 '{tag_name}' 创建失败: {create_response.text}")
                            
            except Exception as e:
                logger.error(f"处理标签 '{tag_name}' 时出错: {e}")
        
        return existing_tags
    
    def _ensure_categories_exist(self, session: requests.Session, base_url: str, categories: list) -> list:
        """确保分类存在，如果不存在则创建，返回分类ID列表"""
        existing_categories = []
        
        for category_name in categories:
            try:
                # 检查分类是否存在
                category_response = session.get(
                    f"{base_url}/apis/content.halo.run/v1alpha1/categories",
                    timeout=10
                )
                
                if category_response.status_code == 200:
                    category_data = category_response.json()
                    existing_category = None
                    
                    # 查找现有分类
                    for category in category_data.get('items', []):
                        if category.get('spec', {}).get('displayName') == category_name:
                            existing_category = category
                            break
                    
                    if existing_category:
                        existing_categories.append(existing_category['metadata']['name'])
                        logger.info(f"分类 '{category_name}' 已存在: {existing_category['metadata']['name']}")
                    else:
                        # 创建新分类
                        slug = category_name.lower().replace(' ', '-').replace('中文', 'chinese')
                        category_create_data = {
                            "apiVersion": "content.halo.run/v1alpha1",
                            "kind": "Category",
                            "metadata": {
                                "generateName": "category-"
                            },
                            "spec": {
                                "displayName": category_name,
                                "slug": f"{slug}-{int(time.time())}",
                                "description": "",
                                "cover": "",
                                "template": "",
                                "priority": 0,
                                "children": []
                            }
                        }
                        
                        create_response = session.post(
                            f"{base_url}/apis/content.halo.run/v1alpha1/categories",
                            data=json.dumps(category_create_data),
                            timeout=10
                        )
                        
                        if create_response.status_code in [200, 201]:
                            created_category = create_response.json()
                            category_id = created_category['metadata']['name']
                            existing_categories.append(category_id)
                            logger.info(f"分类 '{category_name}' 创建成功: {category_id}")
                        else:
                            logger.error(f"分类 '{category_name}' 创建失败: {create_response.text}")
                            
            except Exception as e:
                logger.error(f"处理分类 '{category_name}' 时出错: {e}")
        
        return existing_categories
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        更新 Halo CMS 中的文章
        """
        try:
            # 获取凭据
            credentials = self.runtime.credentials
            base_url = credentials.get("base_url", "").strip().rstrip('/')
            access_token = credentials.get("access_token", "").strip()
            
            if not base_url or not access_token:
                yield self.create_text_message("❌ 缺少必要的连接配置")
                return
            
            # 获取参数
            post_id = tool_parameters.get("post_id", "").strip()
            title = tool_parameters.get("title")
            content = tool_parameters.get("content")
            categories_str = tool_parameters.get("categories")
            tags_str = tool_parameters.get("tags")
            slug = tool_parameters.get("slug")
            excerpt = tool_parameters.get("excerpt")
            cover = tool_parameters.get("cover")
            published = tool_parameters.get("published")
            
            if not post_id:
                yield self.create_text_message("❌ 文章 ID 不能为空")
                return
            
            # 创建HTTP会话
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'Dify-Halo-Plugin/1.0'
            })
            
            yield self.create_text_message(f"🔍 正在获取文章 {post_id} 的当前信息...")
            
            # 首先获取当前文章数据
            get_response = session.get(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                timeout=30
            )
            
            if get_response.status_code == 404:
                yield self.create_text_message(f"❌ 找不到ID为 {post_id} 的文章")
                return
            elif get_response.status_code != 200:
                yield self.create_text_message(f"❌ 获取文章信息失败: HTTP {get_response.status_code}")
                return
            
            current_data = get_response.json()
            
            # 更新指定字段
            update_data = current_data.copy()
            
            if title is not None:
                update_data["spec"]["title"] = title
            if slug is not None:
                update_data["spec"]["slug"] = slug
            if published is not None:
                update_data["spec"]["publish"] = published
            if cover is not None:
                update_data["spec"]["cover"] = cover
            
            # 处理分类字符串转换
            if categories_str is not None:
                if isinstance(categories_str, str):
                    categories = [cat.strip() for cat in categories_str.split(",") if cat.strip()]
                else:
                    categories = categories_str if isinstance(categories_str, list) else []
                
                # 确保分类存在
                if categories:
                    yield self.create_text_message("📂 正在处理分类...")
                    categories = self._ensure_categories_exist(session, base_url, categories)
                
                update_data["spec"]["categories"] = categories
            
            # 处理标签字符串转换
            if tags_str is not None:
                if isinstance(tags_str, str):
                    tags = [tag.strip() for tag in tags_str.split(",") if tag.strip()]
                else:
                    tags = tags_str if isinstance(tags_str, list) else []
                
                # 确保标签存在
                if tags:
                    yield self.create_text_message("🏷️ 正在处理标签...")
                    tags = self._ensure_tags_exist(session, base_url, tags)
                
                update_data["spec"]["tags"] = tags
            
            # 处理摘要
            if excerpt is not None:
                if "excerpt" not in update_data["spec"]:
                    update_data["spec"]["excerpt"] = {"autoGenerate": True, "raw": ""}
                update_data["spec"]["excerpt"]["raw"] = excerpt
                update_data["spec"]["excerpt"]["autoGenerate"] = not bool(excerpt)
            
            yield self.create_text_message("📝 正在更新文章基本信息...")
            
            # 记录更新数据用于调试
            logger.info(f"Updating post {post_id} with data: {json.dumps(update_data, indent=2)}")
            
            # 发送更新请求
            response = session.put(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                data=json.dumps(update_data),
                timeout=30
            )
            
            # 记录响应用于调试
            logger.info(f"Update post response status: {response.status_code}")
            logger.info(f"Update post response: {response.text}")
            
            if response.status_code == 401:
                yield self.create_text_message("❌ 认证失败，请检查访问令牌")
                return
            elif response.status_code == 403:
                yield self.create_text_message("❌ 权限不足，请确保令牌具有文章管理权限")
                return
            elif response.status_code == 422:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', error_data.get('message', response.text))
                except:
                    error_detail = response.text
                yield self.create_text_message(f"❌ 数据验证失败: {error_detail}")
                return
            elif response.status_code not in [200, 201]:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', error_data.get('message', response.text))
                except:
                    error_detail = response.text
                yield self.create_text_message(f"❌ 更新文章失败: HTTP {response.status_code} - {error_detail}")
                return
            
            # 更新内容（如果提供了）
            content_updated = False
            content_update_error = None
            if content is not None:
                yield self.create_text_message("📝 正在更新文章内容...")
                
                content_data = {
                    "raw": content,
                    "content": content,
                    "rawType": "markdown"
                }
                
                content_response = session.put(
                    f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_id}/content",
                    data=json.dumps(content_data),
                    timeout=30
                )
                
                if content_response.status_code in [200, 201]:
                    content_updated = True
                else:
                    content_update_error = f"HTTP {content_response.status_code}"
                    logger.warning(f"Failed to update post content: {content_response.status_code} - {content_response.text}")
            
            # 解析响应
            result = response.json()
            post_title = result.get("spec", {}).get("title", "")
            post_categories = result.get("spec", {}).get("categories", [])
            post_tags = result.get("spec", {}).get("tags", [])
            post_cover = result.get("spec", {}).get("cover", "")
            post_published = result.get("spec", {}).get("publish", False)
            
            # 格式化响应 - 根据实际更新结果显示状态
            status_emoji = "🚀" if post_published else "📝"
            status_text = "已发布" if post_published else "草稿"
            
            # 判断整体更新状态
            overall_success = True
            if content is not None and not content_updated:
                overall_success = False
            
            if overall_success:
                response_lines = [
                    f"✅ **文章更新成功！**",
                    "",
                    f"📝 **标题**: {post_title}",
                    f"🆔 **ID**: {post_id}",
                    f"{status_emoji} **状态**: {status_text}",
                ]
            else:
                response_lines = [
                    f"⚠️ **文章部分更新成功**",
                    "",
                    f"📝 **标题**: {post_title}",
                    f"🆔 **ID**: {post_id}",
                    f"{status_emoji} **状态**: {status_text}",
                ]
            
            if post_categories:
                response_lines.append(f"📂 **分类**: {len(post_categories)} 个")
            
            if post_tags:
                response_lines.append(f"🏷️ **标签**: {len(post_tags)} 个")
            
            if post_cover:
                response_lines.append(f"🖼️ **封面**: 已设置")
            
            # 详细更新状态
            if content is not None:
                if content_updated:
                    response_lines.append("📄 **内容**: 已更新")
                else:
                    response_lines.append(f"❌ **内容**: 更新失败 ({content_update_error})")
            
            yield self.create_text_message('\n'.join(response_lines))
            
            # 返回详细信息
            yield self.create_json_message({
                "success": True,
                "post_id": post_id,
                "title": post_title,
                "categories_count": len(post_categories),
                "tags_count": len(post_tags),
                "cover": post_cover,
                "published": post_published,
                "content_updated": content_updated,
                "updated_fields": {
                    "title": title is not None,
                    "content": content_updated,
                    "categories": categories_str is not None,
                    "tags": tags_str is not None,
                    "cover": cover is not None,
                    "published": published is not None,
                    "excerpt": excerpt is not None
                }
            })
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("❌ 请求超时")
        except requests.exceptions.ConnectionError:
            yield self.create_text_message("❌ 无法连接到服务器")
        except Exception as e:
            logger.error(f"Post update tool error: {e}")
            yield self.create_text_message(f"❌ 更新失败: {str(e)}") 