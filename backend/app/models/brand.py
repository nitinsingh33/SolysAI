"""
Brand Data Model
Represents EV brands and their information
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class VehicleType(str, Enum):
    ELECTRIC_SCOOTER = "electric_scooter"
    ELECTRIC_MOTORCYCLE = "electric_motorcycle"
    ELECTRIC_CAR = "electric_car"
    ELECTRIC_RICKSHAW = "electric_rickshaw"

class BrandStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MONITORING = "monitoring"

class Brand(BaseModel):
    """Main Brand Model"""
    id: Optional[str] = Field(None, alias="_id")
    
    # Basic Information
    brand_id: str = Field(..., description="Unique brand identifier (snake_case)")
    name: str = Field(..., description="Brand display name")
    company_name: Optional[str] = Field(None, description="Parent company name")
    
    # Keywords for identification
    keywords: List[str] = Field(..., description="Keywords used to identify mentions")
    aliases: List[str] = Field(default_factory=list, description="Alternative names/spellings")
    
    # Brand Details
    founded_year: Optional[int] = Field(None, description="Year the brand was founded")
    headquarters: Optional[str] = Field(None, description="Headquarters location")
    website: Optional[str] = Field(None, description="Official website URL")
    
    # Vehicle Information
    primary_vehicle_type: VehicleType = Field(..., description="Primary type of vehicles")
    vehicle_types: List[VehicleType] = Field(..., description="All vehicle types offered")
    
    # Popular Models
    popular_models: List[str] = Field(default_factory=list, description="List of popular vehicle models")
    
    # Social Media & Online Presence
    youtube_channels: List[str] = Field(default_factory=list, description="Official YouTube channel IDs")
    social_handles: Dict[str, str] = Field(default_factory=dict, description="Social media handles")
    
    # Monitoring Configuration
    status: BrandStatus = Field(BrandStatus.ACTIVE, description="Monitoring status")
    monitoring_keywords: List[str] = Field(default_factory=list, description="Additional keywords for monitoring")
    
    # Analytics
    total_mentions: int = Field(0, description="Total mentions across all platforms")
    last_mention_date: Optional[datetime] = Field(None, description="Date of last mention")
    sentiment_summary: Dict[str, Any] = Field(default_factory=dict, description="Overall sentiment summary")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "brand_id": "ola_electric",
                "name": "Ola Electric",
                "company_name": "ANI Technologies Pvt. Ltd.",
                "keywords": ["ola electric", "ola s1", "ola scooter"],
                "aliases": ["ola", "ola e-scooter"],
                "founded_year": 2017,
                "headquarters": "Bangalore, India",
                "website": "https://olaelectric.com",
                "primary_vehicle_type": "electric_scooter",
                "vehicle_types": ["electric_scooter"],
                "popular_models": ["S1", "S1 Pro", "S1 Air"],
                "status": "active"
            }
        }

class BrandCreate(BaseModel):
    """Model for creating brands"""
    brand_id: str
    name: str
    keywords: List[str]
    primary_vehicle_type: VehicleType
    vehicle_types: List[VehicleType]
    company_name: Optional[str] = None
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None

class BrandUpdate(BaseModel):
    """Model for updating brands"""
    name: Optional[str] = None
    keywords: Optional[List[str]] = None
    aliases: Optional[List[str]] = None
    popular_models: Optional[List[str]] = None
    status: Optional[BrandStatus] = None
    monitoring_keywords: Optional[List[str]] = None

class BrandStats(BaseModel):
    """Brand statistics model"""
    brand_id: str
    brand_name: str
    
    # Mention Statistics
    total_mentions: int
    mentions_this_month: int
    mentions_last_month: int
    growth_rate: float
    
    # Sentiment Statistics
    overall_sentiment: float
    sentiment_breakdown: Dict[str, int]  # {positive: 150, negative: 30, neutral: 20}
    sentiment_trend: str  # "improving", "declining", "stable"
    
    # Engagement Statistics
    total_likes: int
    total_replies: int
    average_engagement: float
    
    # Top Aspects
    top_positive_aspects: List[Dict[str, float]]
    top_negative_aspects: List[Dict[str, float]]
    
    # Time-based data
    daily_mentions: List[Dict[str, Any]]
    peak_activity_hours: List[int]
    
    # Comparison Data
    market_position: int  # Ranking among all brands
    sentiment_rank: int   # Ranking by sentiment
    
class BrandComparison(BaseModel):
    """Model for comparing multiple brands"""
    brands: List[str]
    comparison_metrics: Dict[str, Dict[str, float]]
    time_period: Dict[str, datetime]
    winner_by_metric: Dict[str, str]
    
# Default EV Brands Configuration
DEFAULT_BRANDS = [
    {
        "brand_id": "ola_electric",
        "name": "Ola Electric",
        "company_name": "ANI Technologies Pvt. Ltd.",
        "keywords": ["ola electric", "ola s1", "ola scooter", "ola e-scooter"],
        "aliases": ["ola"],
        "founded_year": 2017,
        "headquarters": "Bangalore, India",
        "website": "https://olaelectric.com",
        "primary_vehicle_type": "electric_scooter",
        "vehicle_types": ["electric_scooter"],
        "popular_models": ["S1", "S1 Pro", "S1 Air"]
    },
    {
        "brand_id": "ather_energy",
        "name": "Ather Energy",
        "keywords": ["ather", "ather 450x", "ather 450", "ather energy"],
        "founded_year": 2013,
        "headquarters": "Bangalore, India",
        "website": "https://atherenergy.com",
        "primary_vehicle_type": "electric_scooter",
        "vehicle_types": ["electric_scooter"],
        "popular_models": ["450X", "450 Plus", "450"]
    },
    {
        "brand_id": "bajaj_chetak",
        "name": "Bajaj Chetak",
        "company_name": "Bajaj Auto Ltd.",
        "keywords": ["bajaj chetak", "chetak electric", "bajaj electric"],
        "founded_year": 2019,
        "headquarters": "Pune, India",
        "website": "https://www.bajajchetak.com",
        "primary_vehicle_type": "electric_scooter",
        "vehicle_types": ["electric_scooter"],
        "popular_models": ["Chetak", "Chetak Premium"]
    }
    # Add more brands as needed
]
