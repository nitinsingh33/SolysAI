"""
Application Configuration
Centralized configuration management using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "EV Sentiment Analysis Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    redis_url: str = "redis://localhost:6379"
    database_name: str = "ev_sentiment"
    
    # API Keys
    openai_api_key: str = ""
    youtube_api_key: str = ""
    gemini_api_key: str = ""
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # API Settings
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    max_comments_per_request: int = 100
    
    # YouTube Scraping
    youtube_rate_limit: int = 100  # requests per hour
    max_comments_per_video: int = 500
    
    # Sentiment Analysis
    sentiment_confidence_threshold: float = 0.7
    batch_size: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()

# EV Brands Configuration
EV_BRANDS = {
    "ola_electric": {
        "name": "Ola Electric",
        "keywords": ["ola electric", "ola s1", "ola scooter"],
        "category": "electric_scooter",
        "founded": 2017
    },
    "ather_energy": {
        "name": "Ather Energy", 
        "keywords": ["ather", "ather 450x", "ather 450"],
        "category": "electric_scooter",
        "founded": 2013
    },
    "bajaj_chetak": {
        "name": "Bajaj Chetak",
        "keywords": ["bajaj chetak", "chetak electric"],
        "category": "electric_scooter", 
        "founded": 2019
    },
    "tvs_iqube": {
        "name": "TVS iQube",
        "keywords": ["tvs iqube", "iqube electric"],
        "category": "electric_scooter",
        "founded": 2020
    },
    "hero_electric": {
        "name": "Hero Electric",
        "keywords": ["hero electric", "hero vida"],
        "category": "electric_scooter",
        "founded": 2007
    },
    "ampere": {
        "name": "Ampere Vehicles",
        "keywords": ["ampere", "ampere magnus", "ampere zeal"],
        "category": "electric_scooter",
        "founded": 2008
    },
    "river_mobility": {
        "name": "River Mobility", 
        "keywords": ["river indie", "river electric"],
        "category": "electric_scooter",
        "founded": 2021
    },
    "ultraviolette": {
        "name": "Ultraviolette Automotive",
        "keywords": ["ultraviolette", "ultraviolette f77"],
        "category": "electric_motorcycle",
        "founded": 2016
    },
    "revolt_motors": {
        "name": "Revolt Motors",
        "keywords": ["revolt", "revolt rv400"],
        "category": "electric_motorcycle", 
        "founded": 2019
    },
    "bgauss": {
        "name": "BGauss",
        "keywords": ["bgauss", "bgauss a2"],
        "category": "electric_scooter",
        "founded": 2018
    }
}
