from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import asyncio
from app.core.logging import logger
from app.models.domain.prediction import (
    PredictionRequest, PredictionResponse,
    WhatIfAnalysisRequest, WhatIfAnalysisResponse
)
from app.services.ml_service import ml_service

router = APIRouter()


@router.post("/predictions", response_model=PredictionResponse)
async def predict_price(request: PredictionRequest) -> PredictionResponse:
    """Get house price prediction with explanation"""
    try:
        logger.info(f"Prediction request received: {request.area_sqft} sqft, {request.bedrooms} bedrooms")
        
        # Initialize ML service if not already done
        if not ml_service.is_initialized:
            success = await ml_service.initialize()
            if not success:
                raise HTTPException(status_code=503, detail="ML service initialization failed")
        
        # Make prediction
        response = ml_service.predict_price(request)
        
        logger.info(f"Prediction completed: ${response.predicted_price:,.0f}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/predictions/what-if", response_model=WhatIfAnalysisResponse)
async def what_if_analysis(request: WhatIfAnalysisRequest) -> WhatIfAnalysisResponse:
    """Perform what-if analysis with multiple scenarios"""
    try:
        logger.info(f"What-if analysis request received with {len(request.scenarios)} scenarios")
        
        # Initialize ML service if not already done
        if not ml_service.is_initialized:
            success = await ml_service.initialize()
            if not success:
                raise HTTPException(status_code=503, detail="ML service initialization failed")
        
        # Perform what-if analysis
        response = ml_service.what_if_analysis(request)
        
        logger.info("What-if analysis completed successfully")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"What-if analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"What-if analysis failed: {str(e)}")


@router.get("/predictions/health")
async def prediction_health() -> Dict[str, Any]:
    """Check prediction service health"""
    try:
        health_status = {
            "status": "healthy" if ml_service.is_initialized else "initializing",
            "model_loaded": ml_service.is_initialized,
            "model_version": ml_service.model_version if ml_service.is_initialized else None,
            "service": "prediction"
        }
        
        if ml_service.is_initialized:
            health_status["best_model"] = getattr(ml_service, 'best_model_name', 'unknown')
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}