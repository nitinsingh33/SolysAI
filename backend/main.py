"""
SolysAI - EV Sentiment Analysis Platform
Production-ready FastAPI backend with MongoDB Atlas integration
"""
import os
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# FastAPI imports
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# MongoDB imports
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
import pymongo.errors

# Pydantic models
from pydantic import BaseModel, Field
from bson import ObjectId

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'solysai-db')
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3001')

# MongoDB client and database
mongodb_client: Optional[AsyncIOMotorClient] = None
database = None

# Pydantic Models
class Comment(BaseModel):
    text: str
    author: str
    likes: int = 0
    time: str
    date: str
    video_id: str
    is_reply: bool = False
    extraction_method: str = "manual"
    sentiment: str = "neutral"
    sentiment_score: float = 0.0
    oem: str
    month: str

class CommentResponse(BaseModel):
    id: str = Field(alias="_id")
    text: str
    author: str
    likes: int
    time: str
    date: str
    video_id: str
    is_reply: bool
    extraction_method: str
    sentiment: str
    sentiment_score: float
    oem: str
    month: str

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class StatsResponse(BaseModel):
    total_comments: int
    total_oems: int
    oem_breakdown: Dict[str, int]
    sentiment_breakdown: Dict[str, int]
    monthly_breakdown: Dict[str, int]
    last_updated: str

class PaginatedCommentsResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# FastAPI app
app = FastAPI(
    title="SolysAI - EV Sentiment Analysis",
    description="Advanced sentiment analysis platform for electric vehicle comments",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
if ENVIRONMENT == "production":
    allowed_origins = [
        "https://your-frontend-domain.vercel.app",
        "https://solysai.com",  # Replace with your actual domain
    ]
else:
    allowed_origins = ["http://localhost:3000", "http://localhost:3001"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Database connection functions
async def connect_to_mongo():
    """Connect to MongoDB Atlas"""
    global mongodb_client, database
    try:
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
        database = mongodb_client[DATABASE_NAME]
        
        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB Atlas - Database: {DATABASE_NAME}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        return False

async def create_indexes():
    """Create database indexes for optimal performance"""
    if database is None:
        return False
    
    try:
        # Try to create unique compound index, but handle existing index gracefully
        try:
            await database.comments.create_index([
                ("video_id", ASCENDING),
                ("author", ASCENDING),
                ("text", ASCENDING)
            ], unique=True, name="unique_comment_index")
            logger.info("✅ Created unique comment index")
        except Exception as idx_err:
            if "already exists" in str(idx_err) or "duplicate key" in str(idx_err) or "E11000" in str(idx_err):
                logger.info("ℹ️ Unique index already exists or has duplicate data - skipping")
            else:
                logger.warning(f"⚠️ Index creation issue: {idx_err}")
        
        # Create performance indexes (these are safer)
        indexes_to_create = [
            ([("oem", ASCENDING)], "oem_index"),
            ([("sentiment", ASCENDING)], "sentiment_index"),
            ([("date", ASCENDING)], "date_index"),
            ([("month", ASCENDING)], "month_index")
        ]
        
        for index_spec, index_name in indexes_to_create:
            try:
                await database.comments.create_index(index_spec, name=index_name)
            except Exception:
                pass  # Index might already exist
        
        logger.info("✅ Database indexes setup completed")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Index setup had issues but continuing: {e}")
        return True  # Don't fail startup for index issues

async def get_database():
    """Dependency to get database instance"""
    if database is None:
        raise HTTPException(status_code=500, detail="Database not connected")
    return database

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("🚀 Starting SolysAI EV Sentiment Analysis Platform...")
    
    # Connect to MongoDB
    if await connect_to_mongo():
        await create_indexes()
        
        # Check data availability
        if database is not None:
            count = await database.comments.count_documents({})
            logger.info(f"📊 Database contains {count:,} comments")
            
        logger.info("🎉 Platform ready!")
        logger.info(f"🌐 API Documentation: http://localhost:8000/docs")
    else:
        logger.warning("⚠️ Running without database connection")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    if mongodb_client:
        mongodb_client.close()
        logger.info("🔌 Database connection closed")

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "SolysAI - EV Sentiment Analysis Platform",
        "version": "2.0.0",
        "status": "active",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "connected" if database else "disconnected"
    
    if database:
        try:
            # Quick ping to check database health
            await mongodb_client.admin.command('ping')
            db_status = "healthy"
        except:
            db_status = "unhealthy"
    
    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/stats", response_model=StatsResponse)
async def get_stats(db = Depends(get_database)):
    """Get comprehensive statistics from the database"""
    try:
        # Total comments
        total_comments = await db.comments.count_documents({})
        
        # OEM breakdown
        oem_pipeline = [
            {"$group": {"_id": "$oem", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        oem_results = await db.comments.aggregate(oem_pipeline).to_list(None)
        oem_breakdown = {item["_id"]: item["count"] for item in oem_results}
        
        # Sentiment breakdown
        sentiment_pipeline = [
            {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        sentiment_results = await db.comments.aggregate(sentiment_pipeline).to_list(None)
        sentiment_breakdown = {item["_id"]: item["count"] for item in sentiment_results}
        
        # Monthly breakdown
        monthly_pipeline = [
            {"$group": {"_id": "$month", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        monthly_results = await db.comments.aggregate(monthly_pipeline).to_list(None)
        monthly_breakdown = {item["_id"]: item["count"] for item in monthly_results}
        
        return StatsResponse(
            total_comments=total_comments,
            total_oems=len(oem_breakdown),
            oem_breakdown=oem_breakdown,
            sentiment_breakdown=sentiment_breakdown,
            monthly_breakdown=monthly_breakdown,
            last_updated=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

@app.get("/comments", response_model=PaginatedCommentsResponse)
async def get_comments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    oem: Optional[str] = Query(None, description="Filter by OEM"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    search: Optional[str] = Query(None, description="Search in comment text"),
    db = Depends(get_database)
):
    """Get comments with pagination and filtering"""
    try:
        # Build filter query
        filter_query = {}
        
        if oem:
            filter_query["oem"] = oem
            
        if sentiment:
            filter_query["sentiment"] = sentiment
            
        if search:
            filter_query["text"] = {"$regex": search, "$options": "i"}
        
        # Get total count
        total = await db.comments.count_documents(filter_query)
        
        # Calculate pagination
        skip = (page - 1) * limit
        total_pages = (total + limit - 1) // limit
        
        # Get comments
        cursor = db.comments.find(filter_query).skip(skip).limit(limit).sort("date", -1)
        comments_data = await cursor.to_list(None)
        
        # Convert to response models
        comments = []
        for comment in comments_data:
            comment["id"] = str(comment["_id"])
            comments.append(CommentResponse(**comment))
        
        return PaginatedCommentsResponse(
            comments=comments,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch comments")

@app.get("/oems")
async def get_oems(db = Depends(get_database)):
    """Get list of all OEMs in the database"""
    try:
        pipeline = [
            {"$group": {"_id": "$oem", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        results = await db.comments.aggregate(pipeline).to_list(None)
        
        return {
            "oems": [{"name": item["_id"], "count": item["count"]} for item in results],
            "total": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error fetching OEMs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch OEMs")

@app.post("/comments", response_model=Dict[str, str])
async def create_comment(comment: Comment, db = Depends(get_database)):
    """Create a new comment (for future YouTube API integration)"""
    try:
        comment_dict = comment.dict()
        result = await db.comments.insert_one(comment_dict)
        
        return {
            "message": "Comment created successfully",
            "id": str(result.inserted_id)
        }
        
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Comment already exists")
    except Exception as e:
        logger.error(f"Error creating comment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create comment")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting SolysAI EV Sentiment Analysis Platform")
    logger.info("=" * 60)
    logger.info(f"Backend: http://localhost:8000")
    logger.info(f"Frontend: {FRONTEND_URL}")
    logger.info(f"API Docs: http://localhost:8000/docs")
    logger.info("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if ENVIRONMENT == "development" else False,
        log_level="info"
    )
