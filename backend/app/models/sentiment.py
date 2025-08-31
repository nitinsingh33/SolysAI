"""
Sentiment Analysis Data Model
Represents sentiment analysis results and metrics
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime
from enum import Enum

class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative" 
    NEUTRAL = "neutral"
    MIXED = "mixed"

class EmotionLabel(str, Enum):
    JOY = "joy"
    ANGER = "anger"
    FEAR = "fear"
    SADNESS = "sadness"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"

class AnalysisMethod(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    HUGGINGFACE = "huggingface"
    RULE_BASED = "rule_based"
    ENSEMBLE = "ensemble"

class SentimentAnalysis(BaseModel):
    """Main Sentiment Analysis Model"""
    id: Optional[str] = Field(None, alias="_id")
    
    # Reference to original comment
    comment_id: str = Field(..., description="Reference to comment being analyzed")
    comment_text: str = Field(..., description="Text that was analyzed")
    
    # Basic Sentiment
    sentiment_label: SentimentLabel = Field(..., description="Primary sentiment classification")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0, description="Sentiment score from -1 (negative) to 1 (positive)")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in the analysis")
    
    # Detailed Emotions
    emotions: Dict[EmotionLabel, float] = Field(default_factory=dict, description="Emotion scores")
    dominant_emotion: Optional[EmotionLabel] = Field(None, description="Most prominent emotion")
    
    # Brand-Specific Analysis
    brand_mentioned: str = Field(..., description="EV brand being discussed")
    brand_sentiment: float = Field(..., ge=-1.0, le=1.0, description="Sentiment specifically toward the brand")
    
    # Aspect-Based Sentiment (for EV features)
    aspects: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Sentiment for specific aspects")
    # Example: {"battery": {"sentiment": 0.8, "confidence": 0.9}, "design": {"sentiment": -0.2, "confidence": 0.7}}
    
    # Analysis Metadata
    analysis_method: AnalysisMethod = Field(..., description="Method used for analysis")
    model_version: Optional[str] = Field(None, description="Version of the AI model used")
    processing_time_ms: Optional[int] = Field(None, description="Time taken for analysis in milliseconds")
    
    # Context Analysis
    sarcasm_detected: bool = Field(False, description="Whether sarcasm was detected")
    comparison_mentioned: bool = Field(False, description="Whether comparison with other brands was made")
    compared_brands: List[str] = Field(default_factory=list, description="Other brands mentioned for comparison")
    
    # Timestamps
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="When analysis was performed")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    
    # Additional Insights
    keywords_positive: List[str] = Field(default_factory=list, description="Positive keywords found")
    keywords_negative: List[str] = Field(default_factory=list, description="Negative keywords found")
    themes: List[str] = Field(default_factory=list, description="Main themes discussed")
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "comment_id": "64f7b1234567890abcdef123",
                "comment_text": "Love my Ola S1 Pro! Amazing battery life but charging infrastructure needs improvement.",
                "sentiment_label": "positive",
                "sentiment_score": 0.6,
                "confidence_score": 0.85,
                "brand_mentioned": "ola_electric",
                "brand_sentiment": 0.7,
                "aspects": {
                    "battery": {"sentiment": 0.9, "confidence": 0.95},
                    "charging_infrastructure": {"sentiment": -0.4, "confidence": 0.8}
                },
                "analysis_method": "openai",
                "keywords_positive": ["love", "amazing", "battery life"],
                "keywords_negative": ["needs improvement"],
                "themes": ["performance", "infrastructure"]
            }
        }

class SentimentCreate(BaseModel):
    """Model for creating sentiment analysis"""
    comment_id: str
    comment_text: str
    brand_mentioned: str
    analysis_method: AnalysisMethod = AnalysisMethod.OPENAI

class SentimentBatch(BaseModel):
    """Model for batch sentiment analysis"""
    comments: List[SentimentCreate]
    analysis_method: AnalysisMethod = AnalysisMethod.OPENAI

class SentimentStats(BaseModel):
    """Model for sentiment statistics"""
    brand: str
    total_comments: int
    sentiment_breakdown: Dict[SentimentLabel, int]
    average_sentiment: float
    confidence_average: float
    date_range: Dict[str, datetime]
    top_aspects: Dict[str, Dict[str, float]]
    
class SentimentTrend(BaseModel):
    """Model for sentiment trends over time"""
    brand: str
    period: str  # "daily", "weekly", "monthly"
    data_points: List[Dict[str, Any]]  # [{date, sentiment_avg, comment_count}, ...]
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0.0 to 1.0

# EV-Specific Aspects for Analysis
EV_ASPECTS = {
    "battery": ["battery", "range", "charging", "mileage", "backup"],
    "performance": ["speed", "acceleration", "power", "torque", "handling"],
    "design": ["look", "design", "appearance", "style", "aesthetics"],
    "build_quality": ["quality", "build", "material", "durability", "finish"],
    "features": ["features", "technology", "connectivity", "app", "digital"],
    "service": ["service", "support", "maintenance", "repair", "dealer"],
    "price": ["price", "cost", "value", "expensive", "affordable"],
    "charging_infrastructure": ["charging station", "infrastructure", "availability"]
}
