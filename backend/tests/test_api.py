import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data


def test_system_info():
    """Test the system info endpoint"""
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "features" in data


def test_prediction_endpoint_validation():
    """Test prediction endpoint with invalid data"""
    # Test missing required fields
    response = client.post("/api/v1/predictions", json={})
    assert response.status_code == 422  # Validation error
    
    # Test invalid values
    invalid_data = {
        "area_sqft": -100,  # Invalid negative value
        "bedrooms": 15,     # Too many bedrooms
        "bathrooms": 15,    # Too many bathrooms
        "age_years": -5,    # Invalid negative age
        "property_type": "invalid_type"
    }
    
    response = client.post("/api/v1/predictions", json=invalid_data)
    assert response.status_code == 422


def test_model_endpoints():
    """Test model management endpoints"""
    # Test model performance endpoint
    response = client.get("/api/v1/models/performance")
    assert response.status_code == 200
    
    # Test feature importance endpoint
    response = client.get("/api/v1/models/feature-importance")
    assert response.status_code == 200


def test_analytics_endpoints():
    """Test analytics endpoints"""
    # Test feature importance analytics
    response = client.get("/api/v1/analytics/feature-importance")
    assert response.status_code == 200
    
    # Test price trends with parameter
    response = client.get("/api/v1/analytics/price-trends?months=6")
    assert response.status_code == 200


def test_cors_headers():
    """Test CORS headers are properly set"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    # Check that CORS headers are present
    assert "access-control-allow-origin" in response.headers or "Access-Control-Allow-Origin" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])