"""
Tag data models for Halo CMS.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class Tag(BaseModel):
    """Halo tag model."""
    
    name: str = Field(..., description="Tag unique name")
    display_name: str = Field(..., description="Tag display name")
    slug: str = Field(..., description="Tag URL slug")
    color: Optional[str] = Field(None, description="Tag color")
    cover: Optional[str] = Field(None, description="Tag cover image URL")
    template: str = Field(default="", description="Tag template")
    
    # System fields
    metadata: Optional[Dict[str, Any]] = Field(None, description="Tag metadata")
    created_time: Optional[datetime] = Field(None, description="Creation time")
    updated_time: Optional[datetime] = Field(None, description="Last update time")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        } 