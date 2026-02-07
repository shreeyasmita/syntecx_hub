import pytest
import pandas as pd
import numpy as np
from ml.pipelines.feature_engineering import feature_pipeline
from ml.pipelines.model_training import model_trainer
from ml.utils.model_evaluator import model_evaluator


def test_feature_pipeline():
    """Test feature engineering pipeline"""
    # Generate test data
    test_data = pd.DataFrame({
        'area_sqft': [2000, 2500, 1800],
        'bedrooms': [3, 4, 2],
        'bathrooms': [2.5, 3, 2],
        'age_years': [10, 5, 15],
        'property_type': ['single_family', 'condo', 'townhouse'],
        'amenities_score': [8.5, 7.2, 6.8],
        'distance_to_center': [5.2, 3.1, 8.7],
        'school_rating': [9.0, 8.5, 7.0],
        'crime_index': [2.1, 1.8, 3.2],
        'market_trend': [1.05, 1.02, 0.98],
        'environmental_score': [7.8, 8.2, 6.5],
        'price': [500000, 650000, 400000]
    })
    
    # Test feature engineering
    processed_features, feature_names = feature_pipeline.fit_transform(test_data.drop('price', axis=1))
    
    assert isinstance(processed_features, pd.DataFrame)
    assert len(processed_features) == 3
    assert len(feature_names) > 0
    assert 'area_sqft' in feature_names


def test_synthetic_data_generation():
    """Test synthetic data generation"""
    # Generate synthetic data
    synthetic_data = feature_pipeline.generate_synthetic_data(100)
    
    assert isinstance(synthetic_data, pd.DataFrame)
    assert len(synthetic_data) == 100
    assert 'price' in synthetic_data.columns
    assert 'area_sqft' in synthetic_data.columns
    assert synthetic_data['price'].min() >= 50000
    assert synthetic_data['price'].max() <= 2000000


def test_model_training():
    """Test model training process"""
    # Generate training data
    train_data = feature_pipeline.generate_synthetic_data(500)
    
    # Train models
    training_result = model_trainer.train_models(train_data)
    
    assert 'model_scores' in training_result
    assert 'best_model' in training_result
    assert training_result['best_model'] is not None
    assert len(model_trainer.models) > 0
    assert model_trainer.best_model is not None


def test_model_evaluation():
    """Test model evaluation utilities"""
    # Test metrics calculation
    y_true = np.array([100000, 200000, 300000])
    y_pred = np.array([110000, 190000, 310000])
    
    metrics = model_evaluator.calculate_metrics(y_true, y_pred)
    
    assert 'rmse' in metrics
    assert 'r2' in metrics
    assert 'mae' in metrics
    assert metrics['rmse'] >= 0
    assert -1 <= metrics['r2'] <= 1


def test_confidence_interval():
    """Test confidence interval calculation"""
    predictions = np.array([500000, 520000, 480000, 510000, 490000])
    
    lower, upper = model_evaluator.confidence_interval(predictions, confidence_level=0.95)
    
    assert lower < np.mean(predictions)
    assert upper > np.mean(predictions)
    assert lower < upper


if __name__ == "__main__":
    pytest.main([__file__, "-v"])