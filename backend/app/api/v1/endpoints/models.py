from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel
from app.core.logging import logger
from app.services.ml_service import ml_service

router = APIRouter()


class ModelInfo(BaseModel):
    name: str
    version: str
    performance_metrics: Dict[str, Any]
    feature_count: int
    last_updated: str


class RetrainRequest(BaseModel):
    data_size: int = 2500
    force_retrain: bool = False


@router.get("/models", response_model=List[ModelInfo])
async def list_models() -> List[ModelInfo]:
    """List available models and their information"""
    try:
        logger.info("Listing available models")
        
        if not ml_service.is_initialized:
            success = await ml_service.initialize()
            if not success:
                raise HTTPException(status_code=503, detail="ML service not available")
        
        # Get current model info
        performance = ml_service.get_model_performance()
        feature_importance = ml_service.get_feature_importance()
        
        models = [
            ModelInfo(
                name=performance.get('best_model', 'unknown'),
                version=performance.get('model_version', '1.0.0'),
                performance_metrics=performance.get('model_scores', {}),
                feature_count=len(feature_importance),
                last_updated=performance.get('last_updated', '')
            )
        ]
        
        return models
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list models: {str(e)}")


@router.get("/models/performance")
async def get_model_performance() -> Dict[str, Any]:
    """Get detailed model performance metrics"""
    try:
        logger.info("Getting model performance metrics")
        
        if not ml_service.is_initialized:
            return {"error": "ML service not initialized"}
        
        performance = ml_service.get_model_performance()
        feature_importance = ml_service.get_feature_importance()
        
        detailed_performance = {
            **performance,
            "feature_importance": feature_importance,
            "feature_count": len(feature_importance)
        }
        
        return detailed_performance
        
    except Exception as e:
        logger.error(f"Error getting model performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance: {str(e)}")


@router.post("/models/train")
async def train_model(request: RetrainRequest) -> Dict[str, Any]:
    """Train new model version"""
    try:
        logger.info(f"Starting model training with {request.data_size} samples")
        
        # Perform retraining
        result = await ml_service.retrain_model()
        
        if result.get('success'):
            logger.info("Model training completed successfully")
            return {
                "message": "Model training completed successfully",
                "new_model_version": result.get('new_model_version'),
                "training_summary": result.get('training_summary')
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Training failed'))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in model training: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")


@router.get("/models/feature-importance")
async def get_feature_importance() -> Dict[str, Any]:
    """Get current feature importance scores"""
    try:
        logger.info("Getting feature importance")
        
        if not ml_service.is_initialized:
            success = await ml_service.initialize()
            if not success:
                raise HTTPException(status_code=503, detail="ML service not available")
        
        importance = ml_service.get_feature_importance()
        
        # Format for frontend visualization
        formatted_importance = [
            {"feature": feature, "importance": importance[feature]}
            for feature in sorted(importance.keys(), key=lambda x: importance[x], reverse=True)
        ]
        
        return {
            "feature_importance": formatted_importance,
            "total_features": len(formatted_importance)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature importance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get feature importance: {str(e)}")


@router.get("/models/health")
async def model_health() -> Dict[str, Any]:
    """Check model service health"""
    try:
        health_status = {
            "status": "healthy" if ml_service.is_initialized else "initializing",
            "model_loaded": ml_service.is_initialized,
            "model_version": ml_service.model_version if ml_service.is_initialized else None,
            "service": "model_management"
        }
        
        if ml_service.is_initialized:
            performance = ml_service.get_model_performance()
            health_status["best_model"] = performance.get('best_model', 'unknown')
            health_status["model_scores"] = performance.get('model_scores', {})
        
        return health_status
        
    except Exception as e:
        logger.error(f"Model health check error: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}