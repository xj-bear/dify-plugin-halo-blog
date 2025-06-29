from collections.abc import Generator
from typing import Any, Dict, List, Optional
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class HaloPostListTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        获取博客文章列表
        
        Args:
            user_id: 用户ID
            tool_parameters: 工具参数
            
        Returns:
            包含文章列表的字典
        """
        try:
            # 获取认证信息
            base_url = self.runtime.credentials.get('base_url')
            access_token = self.runtime.credentials.get('access_token')
            
            if not base_url or not access_token:
                raise ToolProviderCredentialValidationError("缺少 Halo 站点配置")
            
            # 清理 base_url
            base_url = base_url.rstrip('/')
            
            # 获取参数
            page = tool_parameters.get('page', 0)
            size = tool_parameters.get('size', 10)
            published = tool_parameters.get('published')
            keyword = tool_parameters.get('keyword', '').strip()
            category = tool_parameters.get('category', '').strip()
            tag = tool_parameters.get('tag', '').strip()
            
            # 构建API URL
            api_url = f"{base_url}/apis/content.halo.run/v1alpha1/posts"
            
            # 准备请求头
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # 构建查询参数
            params = {
                'page': page,
                'size': size
            }
            
            # 添加筛选参数
            if published is not None:
                params['published'] = str(published).lower()
            
            if keyword:
                params['keyword'] = keyword
                
            if category:
                params['category'] = category
                
            if tag:
                params['tag'] = tag
            
            # 发送请求
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 401:
                yield self.create_text_message('❌ 认证失败，请检查访问令牌是否正确')
                return
            elif response.status_code == 403:
                yield self.create_text_message('❌ 权限不足，请检查访问令牌权限')
                return
            elif response.status_code != 200:
                yield self.create_text_message(f'❌ API请求失败: {response.status_code} - {response.text}')
                return
            
            data = response.json()
            
            # 格式化文章列表
            posts = []
            for item in data.get('items', []):
                spec = item.get('spec', {})
                status = item.get('status', {})
                
                post = {
                    'id': item.get('metadata', {}).get('name', ''),
                    'title': spec.get('title', '未知标题'),
                    'slug': spec.get('slug', ''),
                    'excerpt': spec.get('excerpt', ''),
                    'cover': spec.get('cover', ''),
                    'published': spec.get('publish', False),
                    'pinned': spec.get('pinned', False),
                    'allowComment': spec.get('allowComment', True),
                    'visible': spec.get('visible', 'PUBLIC'),
                    'priority': spec.get('priority', 0),
                    'tags': spec.get('tags', []),
                    'categories': spec.get('categories', []),
                    'publishTime': spec.get('publishTime'),
                    'permalink': status.get('permalink', ''),
                    'excerpt_from_content': status.get('excerpt', ''),
                    'word_count': status.get('size', 0),
                    'creation_time': item.get('metadata', {}).get('creationTimestamp'),
                    'last_modified': status.get('lastModifyTime')
                }
                posts.append(post)
            
            # 分页信息
            pagination = {
                'page': data.get('page', 0),
                'size': data.get('size', 10),
                'total': data.get('total', 0),
                'total_pages': data.get('totalPages', 0),
                'has_previous': data.get('hasPrevious', False),
                'has_next': data.get('hasNext', False)
            }
            
            # 构建友好的结果摘要
            summary_parts = []
            
            if keyword:
                summary_parts.append(f"关键词'{keyword}'")
            if category:
                summary_parts.append(f"分类'{category}'")
            if tag:
                summary_parts.append(f"标签'{tag}'")
            if published is not None:
                status_text = "已发布" if published else "草稿"
                summary_parts.append(f"状态：{status_text}")
            
            filter_text = "，".join(summary_parts)
            if filter_text:
                filter_text = f"（筛选条件：{filter_text}）"
            
            summary = f"成功获取第{page + 1}页文章列表，共{len(posts)}篇文章{filter_text}。总计{pagination['total']}篇文章，共{pagination['total_pages']}页。"
            
            # 返回文本摘要
            yield self.create_text_message(summary)
            
            # 返回详细数据
            result_data = {
                'success': True,
                'summary': summary,
                'posts': posts,
                'pagination': pagination,
                'filters': {
                    'keyword': keyword,
                    'category': category,
                    'tag': tag,
                    'published': published
                }
            }
            yield self.create_json_message(result_data)
            
        except requests.exceptions.Timeout:
            yield self.create_text_message('❌ 请求超时，请检查网络连接')
        except requests.exceptions.ConnectionError:
            yield self.create_text_message('❌ 连接失败，请检查站点地址是否正确')
        except Exception as e:
            yield self.create_text_message(f'❌ 获取文章列表失败: {str(e)}') 