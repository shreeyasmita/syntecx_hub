from fastapi import APIRouter
from app.api.v1.endpoints import predictions, models, analytics, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(predictions.router, tags=["predictions"])
api_router.include_router(models.router, tags=["models"])
api_router.include_router(analytics.router, tags=["analytics"])
api_router.include_router(health.router, tags=["health"])