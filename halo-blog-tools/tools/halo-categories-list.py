from typing import Any, Dict, List, Optional, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class HaloCategoriesListTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        获取分类列表
        
        Args:
            tool_parameters: 工具参数
            
        Yields:
            ToolInvokeMessage: 包含分类列表的消息
        """
        try:
            # 获取认证信息
            base_url = self.runtime.credentials.get('base_url')
            access_token = self.runtime.credentials.get('access_token')
            
            if not base_url or not access_token:
                yield self.create_text_message("缺少 Halo 站点配置")
                return
            
            # 清理 base_url
            base_url = base_url.rstrip('/')
            
            # 获取参数
            page = tool_parameters.get('page', 0)
            size = tool_parameters.get('size', 50)  # 分类通常数量不多，默认获取更多
            keyword = tool_parameters.get('keyword', '').strip()
            
            # 构建API URL
            api_url = f"{base_url}/apis/content.halo.run/v1alpha1/categories"
            
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
            
            if keyword:
                params['keyword'] = keyword
            
            # 发送请求
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 401:
                yield self.create_text_message('认证失败，请检查访问令牌是否正确')
                return
            elif response.status_code == 403:
                yield self.create_text_message('权限不足，请检查访问令牌权限')
                return
            elif response.status_code != 200:
                yield self.create_text_message(f'API请求失败: {response.status_code} - {response.text}')
                return
            
            data = response.json()
            
            # 格式化分类列表
            categories = []
            for item in data.get('items', []):
                spec = item.get('spec', {})
                status = item.get('status', {})
                metadata = item.get('metadata', {})
                
                category = {
                    'id': metadata.get('name', ''),
                    'name': spec.get('displayName', ''),
                    'slug': spec.get('slug', ''),
                    'description': spec.get('description', ''),
                    'cover': spec.get('cover', ''),
                    'color': spec.get('color', ''),
                    'priority': spec.get('priority', 0),
                    'visible_in_list': spec.get('visibleInList', True),
                    'hide_from_list': spec.get('hideFromList', False),
                    'prevent_parent_post_cascade_query': spec.get('preventParentPostCascadeQuery', False),
                    'parent': spec.get('parent', ''),
                    'children': spec.get('children', []),
                    'template': spec.get('template', ''),
                    'permalink': status.get('permalink', ''),
                    'post_count': status.get('postCount', 0),
                    'visible_post_count': status.get('visiblePostCount', 0),
                    'creation_time': metadata.get('creationTimestamp'),
                    'full_path': status.get('fullPath', '')
                }
                categories.append(category)
            
            # 分页信息
            pagination = {
                'page': data.get('page', 0),
                'size': data.get('size', 50),
                'total': data.get('total', 0),
                'total_pages': data.get('totalPages', 0),
                'has_previous': data.get('hasPrevious', False),
                'has_next': data.get('hasNext', False)
            }
            
            # 构建友好的结果摘要
            filter_text = ""
            if keyword:
                filter_text = f"（搜索关键词：'{keyword}'）"
            
            summary = f"成功获取第{page + 1}页分类列表，共{len(categories)}个分类{filter_text}。总计{pagination['total']}个分类，共{pagination['total_pages']}页。"
            
            # 添加分类统计信息
            total_posts = sum(cat['post_count'] for cat in categories)
            categories_with_posts = len([cat for cat in categories if cat['post_count'] > 0])
            
            result = {
                'success': True,
                'summary': summary,
                'categories': categories,
                'pagination': pagination,
                'statistics': {
                    'total_categories': len(categories),
                    'categories_with_posts': categories_with_posts,
                    'total_posts_in_categories': total_posts
                },
                'filters': {
                    'keyword': keyword
                }
            }
            
            yield self.create_json_message(result)
            
        except requests.exceptions.Timeout:
            yield self.create_text_message('请求超时，请检查网络连接')
        except requests.exceptions.ConnectionError:
            yield self.create_text_message('连接失败，请检查站点地址是否正确')
        except Exception as e:
            yield self.create_text_message(f'获取分类列表失败: {str(e)}') 