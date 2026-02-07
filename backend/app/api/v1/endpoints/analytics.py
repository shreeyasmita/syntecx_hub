from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from app.core.logging import logger
from app.services.ml_service import ml_service

router = APIRouter()


@router.get("/analytics/feature-importance")
async def get_feature_importance() -> Dict[str, Any]:
    """Get feature importance data for visualization"""
    try:
        logger.info("Getting feature importance for analytics")
        
        if not ml_service.is_initialized:
            success = await ml_service.initialize()
            if not success:
                raise HTTPException(status_code=503, detail="ML service not available")
        
        importance = ml_service.get_feature_importance()
        
        # Format for chart visualization
        chart_data = [
            {
                "name": feature.replace('_', ' ').title(),
                "importance": round(importance[feature], 4),
                "value": importance[feature]  # For chart libraries that expect 'value'
            }
            for feature in sorted(importance.keys(), key=lambda x: importance[x], reverse=True)
        ]
        
        return {
            "data": chart_data,
            "total_features": len(chart_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feature importance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get feature importance: {str(e)}")


@router.get("/analytics/price-trends")
async def get_price_trends(months: int = 12) -> Dict[str, Any]:
    """Get historical price trends data"""
    try:
        logger.info(f"Generating price trends for {months} months")
        
        if not ml_service.is_initialized:
            success = await ml_service.initialize()
            if not success:
                raise HTTPException(status_code=503, detail="ML service not available")
        
        # Generate synthetic trend data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)
        
        # Create date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='M')
        
        # Generate realistic price trends
        np.random.seed(42)
        base_price = 350000
        trend_data = []
        
        for i, date in enumerate(date_range):
            # Simulate market trends with some seasonality and growth
            months_from_start = i
            seasonal_factor = 1 + 0.05 * np.sin(2 * np.pi * months_from_start / 12)
            growth_factor = 1 + (months_from_start * 0.015)  # 1.5% monthly growth
            market_noise = np.random.normal(0, 0.02)  # 2% monthly volatility
            
            price = base_price * seasonal_factor * growth_factor * (1 + market_noise)
            
            trend_data.append({
                "date": date.strftime('%Y-%m-%d'),
                "average_price": round(price, 2),
                "min_price": round(price * 0.85, 2),
                "max_price": round(price * 1.15, 2),
                "volume": np.random.randint(50, 200)  # Number of transactions
            })
        
        return {
            "trend_data": trend_data,
            "period": f"{months} months",
            "total_points": len(trend_data),
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating price trends: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate price trends: {str(e)}")


@router.get("/analytics/model-performance")
async def get_model_performance_history() -> Dict[str, Any]:
    """Get model performance history and comparison"""
    try:
        logger.info("Getting model performance history")
        
        if not ml_service.is_initialized:
            success = await ml_service.initialize()
            if not success:
                raise HTTPException(status_code=503, detail="ML service not available")
        
        performance = ml_service.get_model_performance()
        
        # Format performance data for comparison charts
        model_scores = performance.get('model_scores', {})
        comparison_data = []
        
        for model_name, scores in model_scores.items():
            comparison_data.append({
                "model": model_name.replace('_', ' ').title(),
                "rmse": round(scores.get('test_rmse', 0), 2),
                "r2": round(scores.get('test_r2', 0), 4),
                "mae": round(scores.get('test_mae', scores.get('test_rmse', 0) * 0.8), 2),
                "accuracy": round(scores.get('test_r2', 0) * 100, 2)
            })
        
        # Add overall metrics
        best_model = performance.get('best_model', 'unknown')
        overall_metrics = {
            "best_model": best_model.replace('_', ' ').title() if best_model != 'unknown' else 'Unknown',
            "total_models": len(comparison_data),
            "average_rmse": round(np.mean([d['rmse'] for d in comparison_data]), 2) if comparison_data else 0,
            "best_r2": max([d['r2'] for d in comparison_data]) if comparison_data else 0
        }
        
        return {
            "model_comparison": comparison_data,
            "overall_metrics": overall_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get model performance: {str(e)}")


@router.get("/analytics/market-insights")
async def get_market_insights() -> Dict[str, Any]:
    """Get market insights and statistics"""
    try:
        logger.info("Generating market insights")
        
        if not ml_service.is_initialized:
            success = await ml_service.initialize()
            if not success:
                raise HTTPException(status_code=503, detail="ML service not available")
        
        # Generate synthetic market insights
        insights = {
            "market_conditions": {
                "trend": "moderately increasing",
                "volatility": "low",
                "seasonality": "strong summer demand",
                "inventory_levels": "moderate"
            },
            "price_statistics": {
                "median_price": 375000,
                "price_range": "$250K - $750K",
                "average_price_per_sqft": 185,
                "price_appreciation_yoy": 8.2
            },
            "demand_factors": {
                "interest_rates": "low",
                "employment": "stable",
                "population_growth": "moderate",
                "housing_supply": "limited"
            },
            "regional_variations": {
                "urban_core": {"change": 12.5, "description": "Strong growth in city center"},
                "suburbs": {"change": 6.8, "description": "Steady suburban demand"},
                "rural": {"change": 3.2, "description": "Slow but stable growth"}
            }
        }
        
        return {
            "insights": insights,
            "generated_at": datetime.now().isoformat(),
            "data_source": "synthetic_market_data"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating market insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate market insights: {str(e)}")


@router.get("/analytics/health")
async def analytics_health() -> Dict[str, Any]:
    """Check analytics service health"""
    try:
        health_status = {
            "status": "healthy",
            "service": "analytics",
            "model_available": ml_service.is_initialized,
            "timestamp": datetime.now().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Analytics health check error: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}