"""
Post data models for Halo CMS.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Post(BaseModel):
    """Halo post model."""
    
    name: str = Field(..., description="Post unique name/slug")
    title: str = Field(..., description="Post title")
    content: Optional[str] = Field(None, description="Post content in Markdown")
    excerpt: Optional[str] = Field(None, description="Post excerpt")
    cover: Optional[str] = Field(None, description="Post cover image URL")
    slug: Optional[str] = Field(None, description="Post URL slug")
    publish_time: Optional[datetime] = Field(None, description="Publish time")
    pinned: bool = Field(default=False, description="Whether post is pinned")
    allow_comment: bool = Field(default=True, description="Allow comments")
    visible: str = Field(default="PUBLIC", description="Post visibility")
    priority: int = Field(default=0, description="Post priority")
    template: str = Field(default="", description="Post template")
    tags: List[str] = Field(default_factory=list, description="Post tags")
    categories: List[str] = Field(default_factory=list, description="Post categories")
    
    # System fields
    metadata: Optional[Dict[str, Any]] = Field(None, description="Post metadata")
    created_time: Optional[datetime] = Field(None, description="Creation time")
    updated_time: Optional[datetime] = Field(None, description="Last update time")
    published: bool = Field(default=False, description="Whether post is published")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class PostCreateRequest(BaseModel):
    """Request model for creating a post."""
    
    title: str = Field(..., description="Post title", min_length=1, max_length=200)
    content: str = Field(..., description="Post content in Markdown")
    excerpt: Optional[str] = Field(None, description="Post excerpt", max_length=500)
    cover: Optional[str] = Field(None, description="Post cover image URL")
    slug: Optional[str] = Field(None, description="Custom URL slug")
    tags: List[str] = Field(default_factory=list, description="Post tags")
    categories: List[str] = Field(default_factory=list, description="Post categories")
    publish_immediately: bool = Field(default=False, description="Publish immediately")
    allow_comment: bool = Field(default=True, description="Allow comments")
    pinned: bool = Field(default=False, description="Pin post")
    template: str = Field(default="", description="Post template")


class PostUpdateRequest(BaseModel):
    """Request model for updating a post."""
    
    title: Optional[str] = Field(None, description="Post title", min_length=1, max_length=200)
    content: Optional[str] = Field(None, description="Post content in Markdown")
    excerpt: Optional[str] = Field(None, description="Post excerpt", max_length=500)
    cover: Optional[str] = Field(None, description="Post cover image URL")
    slug: Optional[str] = Field(None, description="Custom URL slug")
    tags: Optional[List[str]] = Field(None, description="Post tags")
    categories: Optional[List[str]] = Field(None, description="Post categories")
    published: Optional[bool] = Field(None, description="Publish status")
    allow_comment: Optional[bool] = Field(None, description="Allow comments")
    pinned: Optional[bool] = Field(None, description="Pin post")
    template: Optional[str] = Field(None, description="Post template")


class PostListResponse(BaseModel):
    """Response model for post list."""
    
    items: List[Post] = Field(..., description="List of posts")
    total: int = Field(..., description="Total number of posts")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether has next page")
    has_previous: bool = Field(..., description="Whether has previous page") 