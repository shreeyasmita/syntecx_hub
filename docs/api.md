# API Documentation

## Overview

The SynTeCX House Price Prediction API provides machine learning-powered house price predictions with explainable AI features.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

Currently no authentication required for development. Production deployment will include JWT authentication.

## Endpoints

### Predictions

#### POST /predictions

Get house price prediction with explanation.

**Request Body:**
```json
{
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
```

**Response:**
```json
{
  "predicted_price": 650000.0,
  "price_range": [620000.0, 680000.0],
  "confidence_score": 0.87,
  "model_version": "2024-01-15",
  "feature_importance": {
    "area_sqft": 0.35,
    "location": 0.25,
    "bedrooms": 0.15,
    "school_rating": 0.12,
    "age_years": 0.08,
    "bathrooms": 0.05
  },
  "explanation": "This property is predicted to be worth $650,000. The key factors influencing this prediction are: Property size (2,500 sq ft) contributes significantly to the value. Location in this zip code adds premium value. Number of bedrooms (4) affects the price. High school district quality (9/10) adds significant premium value.",
  "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_time": 0.234
}
```

#### POST /predictions/what-if

Perform what-if analysis with multiple scenarios.

**Request Body:**
```json
{
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
```

**Response:**
```json
{
  "base_prediction": {
    "predicted_price": 650000.0,
    "price_range": [620000.0, 680000.0],
    "confidence_score": 0.87,
    "model_version": "2024-01-15",
    "feature_importance": {...},
    "explanation": "...",
    "prediction_id": "550e8400-e29b-41d4-a716-446655440000",
    "processing_time": 0.234
  },
  "scenario_predictions": [...],
  "comparison_analysis": {
    "base_price": 650000.0,
    "scenario_changes": [
      {"bedrooms": 5, "bathrooms": 4},
      {"area_sqft": 3000},
      {"age_years": 5}
    ],
    "price_impact": [85000.0, 120000.0, -25000.0],
    "percentage_changes": [13.1, 18.5, -3.8]
  }
}
```

### Models

#### GET /models/performance

Get detailed model performance metrics.

**Response:**
```json
{
  "model_version": "2024-01-15",
  "best_model": "random_forest",
  "model_scores": {
    "linear_regression": {
      "train_rmse": 45000.0,
      "test_rmse": 48000.0,
      "train_r2": 0.82,
      "test_r2": 0.79
    },
    "random_forest": {
      "train_rmse": 32000.0,
      "test_rmse": 38000.0,
      "train_r2": 0.91,
      "test_r2": 0.87
    },
    "xgboost": {
      "train_rmse": 35000.0,
      "test_rmse": 41000.0,
      "train_r2": 0.89,
      "test_r2": 0.85
    }
  },
  "feature_importance": {
    "area_sqft": 0.35,
    "location": 0.25,
    "bedrooms": 0.15,
    "school_rating": 0.12,
    "age_years": 0.08,
    "bathrooms": 0.05
  },
  "feature_count": 25,
  "last_updated": "2024-01-15T10:30:00Z"
}
```

#### POST /models/train

Train new model version.

**Request Body:**
```json
{
  "data_size": 2500,
  "force_retrain": false
}
```

**Response:**
```json
{
  "message": "Model training completed successfully",
  "new_model_version": "2024-01-16",
  "training_summary": {
    "model_scores": {...},
    "best_model": "random_forest",
    "dataset_size": 2500,
    "training_date": "2024-01-16T14:30:00Z"
  }
}
```

### Analytics

#### GET /analytics/feature-importance

Get current feature importance data for visualization.

**Response:**
```json
{
  "data": [
    {
      "name": "Area Sqft",
      "importance": 0.35,
      "value": 0.35
    },
    {
      "name": "Location",
      "importance": 0.25,
      "value": 0.25
    }
  ],
  "total_features": 25,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /analytics/price-trends

Get historical price trends data.

**Query Parameters:**
- `months`: Number of months of historical data (default: 12)

**Response:**
```json
{
  "trend_data": [
    {
      "date": "2023-01-31",
      "average_price": 350000.0,
      "min_price": 297500.0,
      "max_price": 402500.0,
      "volume": 125
    }
  ],
  "period": "12 months",
  "total_points": 12,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Health

#### GET /health

Comprehensive health check for the entire system.

**Response:**
```json
{
  "status": "healthy",
  "service": "SynTeCX House Price Prediction API",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00Z",
  "components": {
    "api": {
      "status": "healthy",
      "version": "1.0.0"
    },
    "database": {
      "status": "healthy",
      "connection": "active"
    },
    "redis": {
      "status": "healthy",
      "connection": "active"
    }
  }
}
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message",
  "error": true
}
```

Common HTTP status codes:
- `400`: Bad Request - Invalid input data
- `404`: Not Found - Resource not found
- `422`: Unprocessable Entity - Validation error
- `500`: Internal Server Error - Server error
- `503`: Service Unavailable - Service not ready

## Rate Limiting

Currently no rate limiting in development. Production will implement:
- 1000 requests per hour per IP
- 100 requests per minute per IP

## Data Validation

All numerical inputs are validated with appropriate ranges:
- `area_sqft`: 500-20000
- `bedrooms`: 0-10
- `bathrooms`: 0-10 (whole or half numbers)
- `age_years`: 0-200
- `amenities_score`: 0-10
- `school_rating`: 0-10
- `latitude`: -90 to 90
- `longitude`: -180 to 180