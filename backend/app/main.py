"""
EV Sentiment Analysis Platform - Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from .core.config import settings
from .core.database import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global database manager
db_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db_manager
    
    # Startup
    logger.info("🚀 Starting EV Sentiment Analysis Platform...")
    try:
        db_manager = DatabaseManager()
        await db_manager.connect()
        logger.info("✅ Database connected successfully")
        
        # Test database connection
        await db_manager.ping()
        logger.info("✅ Database ping successful")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    finally:
        # Shutdown
        if db_manager:
            await db_manager.disconnect()
            logger.info("🔌 Database disconnected")
        logger.info("👋 Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="EV Sentiment Analysis Platform",
    description="AI-powered sentiment analysis for Indian Electric Vehicle brands",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if db_manager:
            await db_manager.ping()
            db_status = "connected"
        else:
            db_status = "disconnected"
            
        return {
            "status": "healthy",
            "database": db_status,
            "version": "1.0.0",
            "environment": settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to EV Sentiment Analysis Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "supported_brands": list(settings.EV_BRANDS.keys()) if hasattr(settings, 'EV_BRANDS') else []
    }

# Include API routers
# from .api import comments_router, sentiment_router, brands_router, analytics_router
# 
# app.include_router(comments_router)
# app.include_router(sentiment_router)
# app.include_router(brands_router)
# app.include_router(analytics_router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
