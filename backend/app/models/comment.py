"""
Comment Data Model
Represents YouTube comments and their metadata
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class CommentSource(str, Enum):
    YOUTUBE = "youtube"
    TWITTER = "twitter" 
    REDDIT = "reddit"
    INSTAGRAM = "instagram"

class CommentStatus(str, Enum):
    RAW = "raw"
    PROCESSED = "processed"
    ANALYZED = "analyzed"
    FLAGGED = "flagged"

class Comment(BaseModel):
    """Main Comment Model"""
    id: Optional[str] = Field(None, alias="_id")
    
    # Content
    text: str = Field(..., description="Comment text content")
    language: Optional[str] = Field("en", description="Detected language")
    
    # Source Information
    source: CommentSource = Field(..., description="Platform where comment was found")
    source_id: str = Field(..., description="Unique ID from source platform")
    source_url: Optional[str] = Field(None, description="URL of the original post/video")
    video_id: Optional[str] = Field(None, description="YouTube video ID if applicable")
    
    # Author Information
    author_name: str = Field(..., description="Comment author name")
    author_id: Optional[str] = Field(None, description="Author's platform ID")
    author_avatar: Optional[str] = Field(None, description="Author profile picture URL")
    
    # Engagement Metrics
    likes_count: int = Field(0, description="Number of likes/hearts")
    replies_count: int = Field(0, description="Number of replies")
    shares_count: int = Field(0, description="Number of shares")
    
    # Brand Association
    brand_mentioned: Optional[str] = Field(None, description="EV brand mentioned in comment")
    brand_keywords: List[str] = Field(default_factory=list, description="Keywords that matched brand")
    
    # Timestamps
    published_at: datetime = Field(..., description="When comment was published")
    scraped_at: datetime = Field(default_factory=datetime.utcnow, description="When comment was scraped")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    
    # Processing Status
    status: CommentStatus = Field(CommentStatus.RAW, description="Processing status")
    is_spam: bool = Field(False, description="Whether comment is identified as spam")
    is_bot: bool = Field(False, description="Whether author appears to be a bot")
    
    # Additional Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional platform-specific data")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "text": "Just bought Ola S1 Pro and loving the performance! Great range and smooth ride.",
                "source": "youtube",
                "source_id": "UgxABC123xyz",
                "video_id": "dQw4w9WgXcQ",
                "author_name": "EVEnthusiast2024",
                "likes_count": 15,
                "brand_mentioned": "ola_electric",
                "brand_keywords": ["ola", "s1 pro"],
                "published_at": "2024-08-29T10:30:00Z"
            }
        }

class CommentCreate(BaseModel):
    """Model for creating new comments"""
    text: str
    source: CommentSource
    source_id: str
    source_url: Optional[str] = None
    video_id: Optional[str] = None
    author_name: str
    author_id: Optional[str] = None
    likes_count: int = 0
    replies_count: int = 0
    published_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

class CommentUpdate(BaseModel):
    """Model for updating comments"""
    status: Optional[CommentStatus] = None
    is_spam: Optional[bool] = None
    is_bot: Optional[bool] = None
    brand_mentioned: Optional[str] = None
    brand_keywords: Optional[List[str]] = None

class CommentFilter(BaseModel):
    """Model for filtering comments"""
    brand: Optional[str] = None
    source: Optional[CommentSource] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_likes: Optional[int] = None
    status: Optional[CommentStatus] = None
    language: Optional[str] = None
    limit: int = Field(50, le=100)
    skip: int = Field(0, ge=0)
