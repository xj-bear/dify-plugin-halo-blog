"""
Moment data models for Halo CMS.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Moment(BaseModel):
    """Halo moment model."""
    
    name: str = Field(..., description="Moment unique name")
    content: str = Field(..., description="Moment content")
    tags: List[str] = Field(default_factory=list, description="Moment tags")
    visible: str = Field(default="PUBLIC", description="Moment visibility")
    approved: bool = Field(default=True, description="Whether moment is approved")
    approved_time: Optional[datetime] = Field(None, description="Approval time")
    priority: int = Field(default=0, description="Moment priority")
    
    # System fields
    metadata: Optional[Dict[str, Any]] = Field(None, description="Moment metadata")
    created_time: Optional[datetime] = Field(None, description="Creation time")
    updated_time: Optional[datetime] = Field(None, description="Last update time")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class MomentCreateRequest(BaseModel):
    """Request model for creating a moment."""
    
    content: str = Field(..., description="Moment content", min_length=1, max_length=1000)
    tags: List[str] = Field(default_factory=list, description="Moment tags")
    visible: str = Field(default="PUBLIC", description="Moment visibility (PUBLIC/PRIVATE)")
    approved: bool = Field(default=True, description="Auto approve moment")


class MomentListResponse(BaseModel):
    """Response model for moment list."""
    
    items: List[Moment] = Field(..., description="List of moments")
    total: int = Field(..., description="Total number of moments")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    has_next: bool = Field(..., description="Whether has next page")
    has_previous: bool = Field(..., description="Whether has previous page") 