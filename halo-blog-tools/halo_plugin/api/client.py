"""
Halo API client for managing posts, moments and other resources.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import requests
from urllib.parse import urlencode

from ..auth.authenticator import HaloAuthenticator
from ..models.post import Post, PostCreateRequest, PostUpdateRequest, PostListResponse
from ..models.moment import Moment, MomentCreateRequest, MomentListResponse
from ..models.category import Category
from ..models.tag import Tag
from ..exceptions import APIError, ResourceNotFoundError, ValidationError

logger = logging.getLogger(__name__)


class HaloAPIClient:
    """Halo CMS API client."""
    
    def __init__(self, authenticator: HaloAuthenticator):
        """
        Initialize API client.
        
        Args:
            authenticator: Configured Halo authenticator
        """
        self.auth = authenticator
        self.base_url = authenticator.base_url
        self.session = authenticator.get_session()
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Halo API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint (full path including /apis/...)
            data: Request body data
            params: Query parameters
            
        Returns:
            Response data
            
        Raises:
            APIError: If request fails
            ResourceNotFoundError: If resource not found
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=self.auth.timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=self.auth.timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, timeout=self.auth.timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=self.auth.timeout)
            else:
                raise APIError(f"Unsupported HTTP method: {method}")
            
            if response.status_code == 404:
                raise ResourceNotFoundError("Resource not found")
            elif response.status_code == 400:
                error_msg = response.text
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', error_msg)
                except:
                    pass
                raise ValidationError(f"Bad request: {error_msg}")
            elif response.status_code >= 400:
                raise APIError(
                    f"API request failed: HTTP {response.status_code} - {response.text}",
                    response.status_code
                )
            
            if response.content:
                return response.json()
            else:
                return {}
                
        except requests.exceptions.Timeout:
            raise APIError("API request timed out")
        except requests.exceptions.ConnectionError:
            raise APIError("Cannot connect to Halo CMS server")
        except requests.exceptions.RequestException as e:
            raise APIError(f"API request failed: {str(e)}")
    
    # Post management methods
    def create_post(self, request: PostCreateRequest) -> Post:
        """Create a new post."""
        # Generate unique name if not provided
        import time
        import uuid
        post_name = f"post-{int(time.time())}-{str(uuid.uuid4())[:8]}"
        
        post_data = {
            "metadata": {
                "name": post_name,
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "title": request.title,
                "slug": request.slug or "",
                "template": request.template,
                "cover": request.cover or "",
                "deleted": False,
                "publish": request.publish_immediately,
                "publishTime": datetime.now().isoformat() if request.publish_immediately else None,
                "pinned": request.pinned,
                "allowComment": request.allow_comment,
                "visible": "PUBLIC",
                "priority": 0,
                "excerpt": {
                    "autoGenerate": True,
                    "raw": request.excerpt or ""
                },
                "categories": request.categories,
                "tags": request.tags,
                "htmlMetas": []
            },
            "content": {
                "raw": request.content,
                "content": request.content,
                "rawType": "markdown"
            }
        }
        
        result = self._make_request("POST", "/apis/content.halo.run/v1alpha1/posts", data=post_data)
        logger.info(f"Created post: {post_name}")
        return self._convert_post_response(result)
    
    def get_post(self, name: str, include_content: bool = True) -> Post:
        """Get post by name."""
        endpoint = f"/apis/content.halo.run/v1alpha1/posts/{name}"
        
        result = self._make_request("GET", endpoint)
        
        # Get content separately if needed
        if include_content:
            try:
                content_result = self._make_request("GET", f"{endpoint}/content")
                result["content"] = content_result
            except Exception as e:
                logger.warning(f"Failed to fetch post content: {e}")
                result["content"] = {"content": ""}
        
        return self._convert_post_response(result)
    
    def update_post(self, name: str, request: PostUpdateRequest) -> Post:
        """Update an existing post."""
        # First get current post data
        current_post = self.get_post(name, include_content=False)
        current_data = self._make_request("GET", f"/apis/content.halo.run/v1alpha1/posts/{name}")
        
        # Update only provided fields
        update_data = current_data.copy()
        
        if request.title is not None:
            update_data["spec"]["title"] = request.title
        if request.slug is not None:
            update_data["spec"]["slug"] = request.slug
        if request.cover is not None:
            update_data["spec"]["cover"] = request.cover
        if request.template is not None:
            update_data["spec"]["template"] = request.template
        if request.published is not None:
            update_data["spec"]["publish"] = request.published
        if request.pinned is not None:
            update_data["spec"]["pinned"] = request.pinned
        if request.allow_comment is not None:
            update_data["spec"]["allowComment"] = request.allow_comment
        if request.categories is not None:
            update_data["spec"]["categories"] = request.categories
        if request.tags is not None:
            update_data["spec"]["tags"] = request.tags
        if request.excerpt is not None:
            update_data["spec"]["excerpt"]["raw"] = request.excerpt
        
        result = self._make_request("PUT", f"/apis/content.halo.run/v1alpha1/posts/{name}", data=update_data)
        
        # Update content separately if provided
        if request.content is not None:
            content_data = {
                "raw": request.content,
                "content": request.content,
                "rawType": "markdown"
            }
            self._make_request("PUT", f"/apis/api.console.halo.run/v1alpha1/posts/{name}/content", data=content_data)
        
        logger.info(f"Updated post: {name}")
        return self._convert_post_response(result)
    
    def delete_post(self, name: str) -> bool:
        """Delete a post."""
        self._make_request("DELETE", f"/apis/content.halo.run/v1alpha1/posts/{name}")
        logger.info(f"Deleted post: {name}")
        return True
    
    def list_posts(
        self, 
        page: int = 0, 
        size: int = 10, 
        published: Optional[bool] = None,
        category: Optional[str] = None,
        tag: Optional[str] = None
    ) -> PostListResponse:
        """List posts with pagination."""
        params = {
            "page": page,
            "size": size
        }
        
        if published is not None:
            params["published"] = str(published).lower()
        if category:
            params["category"] = category
        if tag:
            params["tag"] = tag
        
        result = self._make_request("GET", "/apis/content.halo.run/v1alpha1/posts", params=params)
        
        items = [self._convert_post_response(item) for item in result.get("items", [])]
        
        return PostListResponse(
            items=items,
            total=result.get("total", 0),
            page=result.get("page", page),
            size=result.get("size", size),
            has_next=result.get("hasNext", False),
            has_previous=result.get("hasPrevious", False)
        )
    
    # Moment management methods
    def create_moment(self, request: MomentCreateRequest) -> Moment:
        """Create a new moment."""
        import time
        import uuid
        moment_name = f"moment-{int(time.time())}-{str(uuid.uuid4())[:8]}"
        
        moment_data = {
            "metadata": {
                "name": moment_name,
                "labels": {},
                "annotations": {}
            },
            "spec": {
                "content": {
                    "raw": request.content,
                    "html": request.content,
                    "medium": []
                },
                "releaseTime": datetime.now().isoformat(),
                "tags": request.tags,
                "visible": request.visible,
                "approved": request.approved,
                "approvedTime": datetime.now().isoformat() if request.approved else None,
                "priority": 0,
                "owner": {
                    "kind": "User",
                    "name": "admin"  # This should be the actual user
                }
            }
        }
        
        result = self._make_request("POST", "/apis/moment.halo.run/v1alpha1/moments", data=moment_data)
        logger.info(f"Created moment: {moment_name}")
        return self._convert_moment_response(result)
    
    def list_moments(self, page: int = 0, size: int = 10) -> MomentListResponse:
        """List moments with pagination."""
        params = {
            "page": page,
            "size": size
        }
        
        result = self._make_request("GET", "/apis/moment.halo.run/v1alpha1/moments", params=params)
        
        items = [self._convert_moment_response(item) for item in result.get("items", [])]
        
        return MomentListResponse(
            items=items,
            total=result.get("total", 0),
            page=result.get("page", page),
            size=result.get("size", size),
            has_next=result.get("hasNext", False),
            has_previous=result.get("hasPrevious", False)
        )
    
    # Category and Tag methods
    def list_categories(self) -> List[Category]:
        """List all categories."""
        result = self._make_request("GET", "/apis/content.halo.run/v1alpha1/categories")
        return [self._convert_category_response(item) for item in result.get("items", [])]
    
    def list_tags(self) -> List[Tag]:
        """List all tags."""
        result = self._make_request("GET", "/apis/content.halo.run/v1alpha1/tags")
        return [self._convert_tag_response(item) for item in result.get("items", [])]
    
    # Response conversion methods
    def _convert_post_response(self, data: Dict[str, Any]) -> Post:
        """Convert API response to Post model."""
        metadata = data.get("metadata", {})
        spec = data.get("spec", {})
        status = data.get("status", {})
        
        return Post(
            name=metadata.get("name", ""),
            title=spec.get("title", ""),
            content=data.get("content", {}).get("content", ""),
            excerpt=spec.get("excerpt", {}).get("raw", ""),
            cover=spec.get("cover", ""),
            slug=spec.get("slug", ""),
            publish_time=spec.get("publishTime"),
            pinned=spec.get("pinned", False),
            allow_comment=spec.get("allowComment", True),
            visible=spec.get("visible", "PUBLIC"),
            priority=spec.get("priority", 0),
            template=spec.get("template", ""),
            tags=spec.get("tags", []),
            categories=spec.get("categories", []),
            metadata=metadata,
            created_time=metadata.get("creationTimestamp"),
            published=spec.get("publish", False)
        )
    
    def _convert_moment_response(self, data: Dict[str, Any]) -> Moment:
        """Convert API response to Moment model."""
        metadata = data.get("metadata", {})
        spec = data.get("spec", {})
        
        return Moment(
            name=metadata.get("name", ""),
            content=spec.get("content", {}).get("raw", ""),
            tags=spec.get("tags", []),
            visible=spec.get("visible", "PUBLIC"),
            approved=spec.get("approved", True),
            approved_time=spec.get("approvedTime"),
            priority=spec.get("priority", 0),
            metadata=metadata,
            created_time=metadata.get("creationTimestamp")
        )
    
    def _convert_category_response(self, data: Dict[str, Any]) -> Category:
        """Convert API response to Category model."""
        metadata = data.get("metadata", {})
        spec = data.get("spec", {})
        
        return Category(
            name=metadata.get("name", ""),
            display_name=spec.get("displayName", ""),
            slug=spec.get("slug", ""),
            description=spec.get("description", ""),
            cover=spec.get("cover", ""),
            template=spec.get("template", ""),
            priority=spec.get("priority", 0),
            metadata=metadata,
            created_time=metadata.get("creationTimestamp")
        )
    
    def _convert_tag_response(self, data: Dict[str, Any]) -> Tag:
        """Convert API response to Tag model."""
        metadata = data.get("metadata", {})
        spec = data.get("spec", {})
        
        return Tag(
            name=metadata.get("name", ""),
            display_name=spec.get("displayName", ""),
            slug=spec.get("slug", ""),
            color=spec.get("color", ""),
            cover=spec.get("cover", ""),
            template=spec.get("template", ""),
            metadata=metadata,
            created_time=metadata.get("creationTimestamp")
        ) 