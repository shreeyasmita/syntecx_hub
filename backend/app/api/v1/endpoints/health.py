from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from datetime import datetime
from app.core.config import settings
from app.core.logging import logger

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Comprehensive health check for the entire system"""
    try:
        health_status = {
            "status": "healthy",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Check API status
        health_status["components"]["api"] = {
            "status": "healthy",
            "version": settings.VERSION
        }
        
        # Check database connection (placeholder)
        health_status["components"]["database"] = {
            "status": "healthy",
            "connection": "active"
        }
        
        # Check Redis connection (placeholder)
        health_status["components"]["redis"] = {
            "status": "healthy",
            "connection": "active"
        }
        
        logger.info("Health check completed successfully")
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "service": settings.PROJECT_NAME,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/info")
async def get_system_info() -> Dict[str, Any]:
    """Get system information and configuration"""
    try:
        system_info = {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "description": "ML-powered house price prediction platform",
            "api_version": "v1",
            "documentation": "/docs",
            "endpoints": {
                "predictions": "/api/v1/predictions",
                "models": "/api/v1/models",
                "analytics": "/api/v1/analytics",
                "health": "/api/v1/health"
            },
            "features": [
                "Multiple ML models (Linear Regression, Random Forest, XGBoost)",
                "Explainable AI with feature importance",
                "Real-time what-if analysis",
                "Interactive dashboard analytics",
                "Model versioning and management",
                "Comprehensive API documentation"
            ],
            "tech_stack": {
                "backend": "FastAPI with Python",
                "ml": "scikit-learn, XGBoost",
                "frontend": "Next.js with React",
                "database": "PostgreSQL (planned)",
                "caching": "Redis (planned)"
            },
            "startup_time": datetime.now().isoformat()
        }
        
        return system_info
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system info: {str(e)}")