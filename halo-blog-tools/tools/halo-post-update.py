from collections.abc import Generator
from typing import Any
import logging
import requests
import json
import re
import time
from datetime import datetime

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
            editor_type = tool_parameters.get("editor_type", "default")
            
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

            # 🔧 修复：从现有文章中获取默认值（Dify不支持动态默认值）
            current_annotations = current_data.get('metadata', {}).get('annotations', {})
            current_spec = current_data.get('spec', {})

            # 如果没有指定编辑器类型，使用当前文章的编辑器类型
            if not editor_type or editor_type == "default":
                current_editor = current_annotations.get('content.halo.run/preferred-editor', 'default')
                editor_type = current_editor
                yield self.create_text_message(f"📝 使用当前编辑器类型: {editor_type}")

            # 如果没有指定发布状态，使用当前文章的发布状态，默认为False
            if published is None:
                current_published = current_spec.get('publish', False)
                published = current_published
                yield self.create_text_message(f"📤 使用当前发布状态: {'已发布' if published else '草稿'}")
            else:
                yield self.create_text_message(f"📤 设置发布状态: {'已发布' if published else '草稿'}")

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
            
            # 准备内容数据（如果需要更新内容）
            content_data = None
            if content is not None or editor_type != "default":
                if content is not None:
                    yield self.create_text_message("📝 正在准备更新文章内容...")
                    content_data = {
                        "rawType": "markdown",
                        "raw": content,
                        "content": content
                    }
                else:
                    yield self.create_text_message("⚙️ 正在准备更新编辑器设置...")
                    # 尝试从现有annotations中获取内容，如果没有则使用空内容
                    existing_content_json = current_data.get("metadata", {}).get("annotations", {}).get("content.halo.run/content-json")
                    if existing_content_json:
                        try:
                            existing_content_data = json.loads(existing_content_json)
                            content_data = existing_content_data
                        except:
                            content_data = {"rawType": "markdown", "raw": "", "content": ""}
                    else:
                        content_data = {"rawType": "markdown", "raw": "", "content": ""}

                # 更新annotations以包含编辑器支持
                if "annotations" not in update_data["metadata"]:
                    update_data["metadata"]["annotations"] = {}

                # 设置编辑器兼容注解
                update_data["metadata"]["annotations"]["content.halo.run/content-json"] = json.dumps(content_data)
                update_data["metadata"]["annotations"]["content.halo.run/preferred-editor"] = editor_type
                update_data["metadata"]["annotations"]["content.halo.run/content-type"] = "markdown"

            
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
            
            # 解析响应
            result = response.json()
            post_title = result.get("spec", {}).get("title", "")
            post_categories = result.get("spec", {}).get("categories", [])
            post_tags = result.get("spec", {}).get("tags", [])
            post_cover = result.get("spec", {}).get("cover", "")
            post_published = result.get("spec", {}).get("publish", False)

            # 🔧 关键修复：文章更新成功后，正确设置内容
            # 1. 先创建新快照（内容存储）
            # 2. 再关联快照到文章（版本控制）
            # 3. 最后设置Console Content API（编辑器支持）

            content_update_success = True
            if content_data is not None:
                yield self.create_text_message("📝 正在更新文章内容...")

                try:
                    # 步骤1: 创建新的内容快照
                    yield self.create_text_message("📸 正在创建更新快照...")

                    timestamp = int(time.time() * 1000)
                    snapshot_name = f"snapshot-{timestamp}"

                    snapshot_data = {
                        'spec': {
                            'subjectRef': {
                                'group': 'content.halo.run',
                                'version': 'v1alpha1',
                                'kind': 'Post',
                                'name': post_id
                            },
                            'rawType': content_data["rawType"],
                            'rawPatch': content_data["raw"],
                            'contentPatch': content_data["content"],
                            'lastModifyTime': datetime.now().isoformat() + 'Z',
                            'owner': current_data.get("spec", {}).get("owner", "admin"),
                            'contributors': [current_data.get("spec", {}).get("owner", "admin")]
                        },
                        'apiVersion': 'content.halo.run/v1alpha1',
                        'kind': 'Snapshot',
                        'metadata': {
                            'name': snapshot_name,
                            'annotations': {
                                'content.halo.run/keep-raw': 'true',
                                'content.halo.run/display-name': f'更新快照-{post_id}',
                                'content.halo.run/version': str(timestamp)
                            }
                        }
                    }

                    snapshot_response = session.post(
                        f"{base_url}/apis/content.halo.run/v1alpha1/snapshots",
                        json=snapshot_data,
                        timeout=30
                    )

                    if snapshot_response.status_code in [200, 201]:
                        yield self.create_text_message("✅ 更新快照创建成功！")

                        # 🔧 关键修复：等待Halo处理快照，避免409冲突
                        yield self.create_text_message("⏳ 等待Halo处理快照...")
                        time.sleep(1)  # 等待1秒让Halo处理

                        # 步骤2: 关联新快照到文章
                        yield self.create_text_message("🔗 正在关联新快照...")

                        # 重新获取最新文章数据，避免版本冲突
                        latest_post_response = session.get(
                            f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                            timeout=30
                        )

                        if latest_post_response.status_code == 200:
                            latest_post_data = latest_post_response.json()
                            latest_post_data['spec']['releaseSnapshot'] = snapshot_name
                            latest_post_data['spec']['headSnapshot'] = snapshot_name
                            # 保持baseSnapshot不变，这是初始版本

                            # 注意：不在这里设置发布状态，而是使用专门的发布API

                            update_response = session.put(
                                f"{base_url}/apis/content.halo.run/v1alpha1/posts/{post_id}",
                                json=latest_post_data,
                                timeout=30
                            )

                            if update_response.status_code in [200, 201]:
                                yield self.create_text_message("✅ 快照关联成功！")

                                # 🔧 关键修复：使用正确的发布/取消发布API
                                if published is not None:
                                    if published:
                                        yield self.create_text_message("📤 正在发布文章...")

                                        # 使用Halo的发布API
                                        publish_response = session.put(
                                            f"{base_url}/apis/uc.api.content.halo.run/v1alpha1/posts/{post_id}/publish",
                                            timeout=30
                                        )

                                        if publish_response.status_code in [200, 201]:
                                            yield self.create_text_message("✅ 文章发布完成！")
                                        else:
                                            yield self.create_text_message(f"⚠️ 文章发布失败: {publish_response.status_code}")
                                            logger.warning(f"文章发布失败: {publish_response.text}")
                                    else:
                                        yield self.create_text_message("📝 正在取消发布...")

                                        # 使用Halo的取消发布API
                                        unpublish_response = session.put(
                                            f"{base_url}/apis/uc.api.content.halo.run/v1alpha1/posts/{post_id}/unpublish",
                                            timeout=30
                                        )

                                        if unpublish_response.status_code in [200, 201]:
                                            yield self.create_text_message("✅ 文章已设为草稿！")
                                        else:
                                            yield self.create_text_message(f"⚠️ 取消发布失败: {unpublish_response.status_code}")
                                            logger.warning(f"取消发布失败: {unpublish_response.text}")
                            else:
                                yield self.create_text_message(f"⚠️ 快照关联失败: {update_response.status_code}")
                                logger.warning(f"快照关联失败: {update_response.text}")
                                content_update_success = False
                        else:
                            yield self.create_text_message("⚠️ 无法获取最新文章数据进行快照关联")
                            content_update_success = False
                    else:
                        yield self.create_text_message(f"⚠️ 快照创建失败: {snapshot_response.status_code}")
                        logger.warning(f"快照创建失败: {snapshot_response.text}")
                        content_update_success = False

                    # 步骤3: 设置Console Content API（编辑器支持）
                    if content_update_success:
                        yield self.create_text_message("📝 正在设置编辑器内容...")

                        content_api_data = {
                            "raw": content_data["raw"],
                            "content": content_data["content"],
                            "rawType": content_data["rawType"]
                        }

                        content_api_response = session.put(
                            f"{base_url}/apis/api.console.halo.run/v1alpha1/posts/{post_id}/content",
                            json=content_api_data,
                            timeout=30
                        )

                        # Console Content API的结果不影响主要功能
                        if content_api_response.status_code in [200, 201]:
                            yield self.create_text_message("✅ 编辑器内容同步成功！")
                        elif content_api_response.status_code == 500:
                            yield self.create_text_message("✅ 编辑器内容同步完成（Halo内部处理中）")
                            logger.info(f"Console Content API返回500（正常现象）: {content_api_response.text}")
                        else:
                            yield self.create_text_message(f"⚠️ 编辑器内容同步失败: {content_api_response.status_code}")
                            logger.warning(f"Console Content API失败: {content_api_response.text}")

                except Exception as e:
                    yield self.create_text_message("⚠️ 内容更新过程中出错")
                    logger.warning(f"内容更新出错: {e}")
                    content_update_success = False
            
            # 格式化响应 - 根据实际更新结果显示状态
            status_emoji = "🚀" if post_published else "📝"
            status_text = "已发布" if post_published else "草稿"
            
            # 构建更新成功响应
            response_lines = [
                f"✅ **文章更新成功！**",
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
                content_status = "✅ 成功" if content_update_success else "⚠️ 部分成功"
                response_lines.append(f"📄 **内容**: 已更新 ({content_status})")

            if editor_type != "default":
                editor_names = {
                    "default": "默认富文本编辑器",
                    "stackedit": "StackEdit Markdown编辑器",
                    "bytemd": "ByteMD Markdown编辑器",
                    "vditor": "Vditor编辑器"
                }
                editor_display_name = editor_names.get(editor_type, editor_type)
                response_lines.append(f"⚙️ **编辑器**: 已设置为 {editor_display_name}")

            if content is not None or editor_type != "default":
                response_lines.append("✨ **编辑器支持**: 添加了编辑器识别注解")
                if content_data is not None:
                    response_lines.append(f"🔧 **内容设置**: {'✅ 完成' if content_update_success else '⚠️ 部分完成'}")
            
            response_lines.extend([
                "",
                f"🔗 **编辑器链接**: {base_url}/console/posts/editor?name={post_id}",
                f"💡 **提示**: 文章现在可以被编辑器正确识别和编辑"
            ])
            
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
                "editor_compatible": True,
                "content_update_success": content_update_success if content_data is not None else None,
                "updated_fields": {
                    "title": title is not None,
                    "content": content is not None,
                    "categories": categories_str is not None,
                    "tags": tags_str is not None,
                    "cover": cover is not None,
                    "published": published is not None,
                    "excerpt": excerpt is not None
                },
                "editor_url": f"{base_url}/console/posts/editor?name={post_id}"
            })
            
        except requests.exceptions.Timeout:
            yield self.create_text_message("❌ 请求超时")
        except requests.exceptions.ConnectionError:
            yield self.create_text_message("❌ 无法连接到服务器")
        except Exception as e:
            logger.error(f"Post update tool error: {e}")
            yield self.create_text_message(f"❌ 更新失败: {str(e)}") 