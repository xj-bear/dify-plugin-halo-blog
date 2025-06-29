from typing import Any, Dict, List, Optional, Generator
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class HaloMomentListTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        获取瞬间列表
        
        Args:
            tool_parameters: 工具参数
            
        Yields:
            ToolInvokeMessage: 包含瞬间列表的消息
        """
        try:
            # 获取认证信息
            credentials = self.runtime.credentials
            base_url = credentials.get('base_url', '').strip().rstrip('/')
            access_token = credentials.get('access_token', '').strip()
            
            if not base_url or not access_token:
                yield self.create_text_message("缺少 Halo 站点配置")
                return
            
            # 获取参数
            page = tool_parameters.get('page', 0)
            size = tool_parameters.get('size', 10)
            approved = tool_parameters.get('approved')
            visible = tool_parameters.get('visible')
            keyword = tool_parameters.get('keyword', '').strip()
            
            # 构建API URL
            api_url = f"{base_url}/apis/moment.halo.run/v1alpha1/moments"
            
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
            if approved is not None:
                params['approved'] = str(approved).lower()
                
            if visible is not None:
                params['visible'] = str(visible).lower()
            
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
            
            # 格式化瞬间列表
            moments = []
            items = data.get('items', [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        spec = item.get('spec', {})
                        status = item.get('status', {})
                        metadata = item.get('metadata', {})
                        
                        # 处理媒体文件 - 官方API使用medium字段
                        media_items = []
                        content_data = spec.get('content', {})
                        if isinstance(content_data, dict):
                            medium_list = content_data.get('medium', [])
                            if isinstance(medium_list, list):
                                for medium in medium_list:
                                    if isinstance(medium, dict):
                                        media_items.append({
                                            'type': medium.get('type', ''),
                                            'url': medium.get('url', ''),
                                            'origin_type': medium.get('originType', '')
                                        })
                        
                        # 处理标签
                        tags = spec.get('tags', [])
                        if not isinstance(tags, list):
                            tags = []
                        
                        # 处理内容
                        if isinstance(content_data, dict):
                            raw_content = content_data.get('raw', '')
                            html_content = content_data.get('html', '')
                        else:
                            raw_content = str(content_data) if content_data else ''
                            html_content = raw_content
                        
                        moment = {
                            'id': metadata.get('name', ''),
                            'content': raw_content,
                            'html_content': html_content,
                            'media': media_items,
                            'tags': tags,
                            'approved': spec.get('approved', False),
                            'visible': spec.get('visible', True),
                            'allow_comment': spec.get('allowComment', True),
                            'creation_time': metadata.get('creationTimestamp'),
                            'release_time': spec.get('releaseTime'),
                            'owner': spec.get('owner', {}).get('name', '') if isinstance(spec.get('owner'), dict) else '',
                            'owner_display_name': spec.get('owner', {}).get('displayName', '') if isinstance(spec.get('owner'), dict) else '',
                            'permalink': status.get('permalink', ''),
                            'media_count': len(media_items),
                            'comment_count': status.get('commentCount', 0)
                        }
                        moments.append(moment)
            
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
            if approved is not None:
                status_text = "已审核" if approved else "待审核"
                summary_parts.append(f"审核状态：{status_text}")
            if visible is not None:
                visibility_text = "可见" if visible else "隐藏"
                summary_parts.append(f"可见性：{visibility_text}")
            
            filter_text = "，".join(summary_parts)
            if filter_text:
                filter_text = f"（筛选条件：{filter_text}）"
            
            summary = f"成功获取第{page + 1}页瞬间列表，共{len(moments)}条瞬间{filter_text}。总计{pagination['total']}条瞬间，共{pagination['total_pages']}页。"
            
            result = {
                'success': True,
                'summary': summary,
                'moments': moments,
                'pagination': pagination,
                'filters': {
                    'keyword': keyword,
                    'approved': approved,
                    'visible': visible
                }
            }
            
            yield self.create_json_message(result)
            
        except requests.exceptions.Timeout:
            yield self.create_text_message('请求超时，请检查网络连接')
        except requests.exceptions.ConnectionError:
            yield self.create_text_message('连接失败，请检查站点地址是否正确')
        except Exception as e:
            yield self.create_text_message(f'获取瞬间列表失败: {str(e)}') 