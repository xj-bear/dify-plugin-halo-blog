#!/usr/bin/env python3
"""
Halo文章创建工具 - 简化版本
专注于核心功能，避免复杂的快照管理
"""

import json
import time
import uuid
import requests
from datetime import datetime
from typing import Any, Generator
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class HaloPostCreateSimpleTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        简化的Halo文章创建工具
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
            title = tool_parameters.get("title", "").strip()
            content = tool_parameters.get("content", "").strip()
            publish_immediately = tool_parameters.get("publish_immediately", False)
            
            if not title:
                yield self.create_text_message("❌ 文章标题不能为空")
                return
            
            if not content:
                yield self.create_text_message("❌ 文章内容不能为空")
                return
            
            # 创建HTTP会话
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}',
                'User-Agent': 'Dify-Halo-Plugin-Simple/1.0'
            })
            
            yield self.create_text_message("📝 正在创建文章...")
            
            # 生成文章ID和slug
            post_id = str(uuid.uuid4())
            slug = f"post-{int(time.time())}"
            
            # 🔧 关键修复：使用最简单的方法创建文章
            # 1. 创建文章时直接包含内容
            # 2. 使用正确的content-json格式
            # 3. 让Halo自动处理快照
            
            content_json = {
                "rawType": "markdown",
                "raw": content,
                "content": content
            }
            
            post_data = {
                "apiVersion": "content.halo.run/v1alpha1",
                "kind": "Post",
                "metadata": {
                    "name": post_id,
                    "annotations": {
                        "content.halo.run/content-json": json.dumps(content_json, ensure_ascii=False),
                        "content.halo.run/preferred-editor": "default",
                        "content.halo.run/content-type": "markdown"
                    }
                },
                "spec": {
                    "title": title,
                    "slug": slug,
                    "template": "",
                    "cover": "",
                    "deleted": False,
                    "publish": publish_immediately,
                    "pinned": False,
                    "allowComment": True,
                    "visible": "PUBLIC",
                    "priority": 0,
                    "excerpt": {
                        "autoGenerate": True,
                        "raw": ""
                    },
                    "categories": [],
                    "tags": [],
                    "owner": "jason",  # 简化用户处理
                    "htmlMetas": []
                }
            }
            
            # 如果立即发布，设置发布时间
            if publish_immediately:
                post_data["spec"]["publishTime"] = datetime.now().isoformat() + 'Z'
            
            # 创建文章
            response = session.post(
                f"{base_url}/apis/content.halo.run/v1alpha1/posts",
                json=post_data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                post_name = result.get("metadata", {}).get("name", post_id)
                post_title = result.get("spec", {}).get("title", title)
                is_published = result.get("spec", {}).get("publish", False)
                
                yield self.create_text_message("✅ 文章创建成功！")
                
                # 构建响应
                status = "已发布" if is_published else "草稿"
                editor_url = f"{base_url}/console/posts/editor?name={post_name}"
                
                response_text = f"""✅ **文章创建成功！**

📝 **标题**: {post_title}
🆔 **ID**: {post_name}
🔗 **Slug**: {slug}
📝 **状态**: {status}
📄 **内容**: 已设置 (✅ 简化模式)

🔗 **编辑器链接**: {editor_url}
💡 **提示**: 文章已创建，内容通过content-json注解设置"""

                yield self.create_text_message(response_text)
                
                # JSON响应
                yield self.create_json_message({
                    "success": True,
                    "post_id": post_name,
                    "title": post_title,
                    "slug": slug,
                    "published": is_published,
                    "editor_url": editor_url,
                    "content_method": "content-json annotation only",
                    "api_endpoint_used": "content.halo.run/v1alpha1/posts"
                })
                
            elif response.status_code == 401:
                yield self.create_text_message("❌ 认证失败，请检查访问令牌")
            elif response.status_code == 403:
                yield self.create_text_message("❌ 权限不足，请确保令牌具有文章管理权限")
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', error_data.get('message', response.text))
                except:
                    error_detail = response.text
                yield self.create_text_message(f"❌ 创建文章失败: HTTP {response.status_code} - {error_detail}")
                
        except Exception as e:
            yield self.create_text_message(f"❌ 创建过程中出错: {str(e)}")
