"""
Formatting utilities for Halo plugin.
"""

from typing import Dict, Any, List
from datetime import datetime

from ..models.post import Post
from ..models.moment import Moment


def format_post_summary(post: Post) -> str:
    """
    Format post information for display.
    
    Args:
        post: Post object
        
    Returns:
        Formatted post summary
    """
    lines = [
        f"📝 **{post.title}**",
        f"ID: `{post.name}`",
    ]
    
    if post.slug:
        lines.append(f"URL Slug: `{post.slug}`")
    
    if post.excerpt:
        lines.append(f"摘要: {post.excerpt[:100]}{'...' if len(post.excerpt) > 100 else ''}")
    
    lines.append(f"状态: {'✅ 已发布' if post.published else '📝 草稿'}")
    
    if post.pinned:
        lines.append("📌 置顶")
    
    if post.tags:
        lines.append(f"标签: {', '.join(post.tags)}")
    
    if post.categories:
        lines.append(f"分类: {', '.join(post.categories)}")
    
    if post.created_time:
        try:
            if isinstance(post.created_time, str):
                created_time = datetime.fromisoformat(post.created_time.replace('Z', '+00:00'))
            else:
                created_time = post.created_time
            lines.append(f"创建时间: {created_time.strftime('%Y-%m-%d %H:%M')}")
        except:
            lines.append(f"创建时间: {post.created_time}")
    
    return '\n'.join(lines)


def format_moment_summary(moment: Moment) -> str:
    """
    Format moment information for display.
    
    Args:
        moment: Moment object
        
    Returns:
        Formatted moment summary
    """
    lines = [
        f"💭 **Moment**",
        f"ID: `{moment.name}`",
        f"内容: {moment.content[:100]}{'...' if len(moment.content) > 100 else ''}",
    ]
    
    lines.append(f"状态: {'✅ 已审核' if moment.approved else '⏳ 待审核'}")
    lines.append(f"可见性: {'🌍 公开' if moment.visible == 'PUBLIC' else '🔒 私密'}")
    
    if moment.tags:
        lines.append(f"标签: {', '.join(moment.tags)}")
    
    if moment.created_time:
        try:
            if isinstance(moment.created_time, str):
                created_time = datetime.fromisoformat(moment.created_time.replace('Z', '+00:00'))
            else:
                created_time = moment.created_time
            lines.append(f"创建时间: {created_time.strftime('%Y-%m-%d %H:%M')}")
        except:
            lines.append(f"创建时间: {moment.created_time}")
    
    return '\n'.join(lines)


def format_api_response(data: Dict[str, Any], title: str = "响应") -> str:
    """
    Format API response for display.
    
    Args:
        data: Response data
        title: Response title
        
    Returns:
        Formatted response string
    """
    lines = [f"## {title}"]
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"**{key}**: {type(value).__name__}")
            else:
                lines.append(f"**{key}**: {value}")
    else:
        lines.append(str(data))
    
    return '\n'.join(lines)


def format_error_message(error: Exception) -> str:
    """
    Format error message for user display.
    
    Args:
        error: Exception object
        
    Returns:
        User-friendly error message
    """
    error_type = type(error).__name__
    
    # Map technical errors to user-friendly messages
    error_mapping = {
        'AuthenticationError': '🔐 认证失败',
        'ValidationError': '❌ 输入验证错误',
        'APIError': '🌐 API请求失败',
        'ResourceNotFoundError': '❓ 资源未找到',
        'ConfigurationError': '⚙️ 配置错误',
    }
    
    prefix = error_mapping.get(error_type, '❌ 操作失败')
    
    return f"{prefix}: {str(error)}"


def format_list_response(items: List[Any], item_formatter, title: str = "列表") -> str:
    """
    Format list response for display.
    
    Args:
        items: List of items
        item_formatter: Function to format each item
        title: List title
        
    Returns:
        Formatted list string
    """
    if not items:
        return f"## {title}\n\n暂无数据"
    
    lines = [f"## {title} ({len(items)} 项)"]
    
    for i, item in enumerate(items, 1):
        lines.append(f"\n### {i}. {item_formatter(item)}")
    
    return '\n'.join(lines)


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..." 