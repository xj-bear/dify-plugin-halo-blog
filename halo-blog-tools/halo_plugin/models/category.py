"""
Category data models for Halo CMS.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Category(BaseModel):
    """Halo category model."""
    
    name: str = Field(..., description="Category unique name")
    display_name: str = Field(..., description="Category display name")
    slug: str = Field(..., description="Category URL slug")
    description: Optional[str] = Field(None, description="Category description")
    cover: Optional[str] = Field(None, description="Category cover image URL")
    template: str = Field(default="", description="Category template")
    priority: int = Field(default=0, description="Category priority")
    
    # System fields
    metadata: Optional[Dict[str, Any]] = Field(None, description="Category metadata")
    created_time: Optional[datetime] = Field(None, description="Creation time")
    updated_time: Optional[datetime] = Field(None, description="Last update time")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        } 