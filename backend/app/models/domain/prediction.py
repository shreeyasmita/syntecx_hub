from pydantic import BaseModel, Field, validator
from typing import Optional, List
from enum import Enum
import pandas as pd


class PropertyType(str, Enum):
    SINGLE_FAMILY = "single_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    MULTI_FAMILY = "multi_family"


class PredictionRequest(BaseModel):
    """Request model for house price prediction"""
    
    # Core features
    area_sqft: float = Field(..., gt=0, le=20000, description="Property area in square feet")
    bedrooms: int = Field(..., ge=0, le=10, description="Number of bedrooms")
    bathrooms: float = Field(..., ge=0, le=10, description="Number of bathrooms")
    age_years: int = Field(..., ge=0, le=200, description="Property age in years")
    property_type: PropertyType = Field(..., description="Type of property")
    
    # Location features
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Longitude coordinate")
    zip_code: Optional[str] = Field(None, pattern=r'^\d{5}$', description="5-digit zip code")
    
    # Advanced features (optional)
    amenities_score: Optional[float] = Field(None, ge=0, le=10, description="Amenities score (0-10)")
    distance_to_center: Optional[float] = Field(None, ge=0, description="Distance to city center (miles)")
    school_rating: Optional[float] = Field(None, ge=0, le=10, description="Average school rating (0-10)")
    crime_index: Optional[float] = Field(None, ge=0, description="Crime index score")
    market_trend: Optional[float] = Field(None, description="Market trend indicator")
    environmental_score: Optional[float] = Field(None, ge=0, le=10, description="Environmental factors score")
    
    @validator('bathrooms')
    def validate_bathrooms(cls, v):
        if v != int(v) and v != int(v) + 0.5:
            raise ValueError('Bathrooms must be whole or half numbers')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "area_sqft": 2500,
                "bedrooms": 4,
                "bathrooms": 3.5,
                "age_years": 15,
                "property_type": "single_family",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "zip_code": "94102",
                "amenities_score": 8.5,
                "distance_to_center": 5.2,
                "school_rating": 9.0,
                "crime_index": 2.1,
                "market_trend": 1.05,
                "environmental_score": 7.8
            }
        }


class PredictionResponse(BaseModel):
    """Response model for house price prediction"""
    
    predicted_price: float = Field(..., description="Predicted house price")
    price_range: List[float] = Field(..., description="Price range [min, max]")
    confidence_score: float = Field(..., ge=0, le=1, description="Model confidence score")
    model_version: str = Field(..., description="Model version used")
    feature_importance: dict = Field(..., description="Feature importance scores")
    explanation: str = Field(..., description="Human-readable explanation")
    prediction_id: str = Field(..., description="Unique prediction identifier")
    processing_time: float = Field(..., description="Processing time in seconds")


class WhatIfAnalysisRequest(BaseModel):
    """Request model for what-if analysis"""
    
    base_property: PredictionRequest = Field(..., description="Base property for comparison")
    scenarios: List[dict] = Field(..., description="List of feature scenarios to test")
    
    class Config:
        schema_extra = {
            "example": {
                "base_property": {
                    "area_sqft": 2500,
                    "bedrooms": 4,
                    "bathrooms": 3.5,
                    "age_years": 15,
                    "property_type": "single_family"
                },
                "scenarios": [
                    {"bedrooms": 5, "bathrooms": 4},
                    {"area_sqft": 3000},
                    {"age_years": 5}
                ]
            }
        }


class WhatIfAnalysisResponse(BaseModel):
    """Response model for what-if analysis"""
    
    base_prediction: PredictionResponse = Field(..., description="Base prediction")
    scenario_predictions: List[PredictionResponse] = Field(..., description="Scenario predictions")
    comparison_analysis: dict = Field(..., description="Comparison metrics")