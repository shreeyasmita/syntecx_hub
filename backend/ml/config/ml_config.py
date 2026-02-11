from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class MLConfig:
    """Machine Learning configuration settings"""
    
    # Model versions
    model_versions: List[str] = None
    default_version: str = "1.0.0"
    
    # Feature engineering
    feature_columns: List[str] = None
    categorical_features: List[str] = None
    numerical_features: List[str] = None
    
    # Model parameters
    random_forest_params: Dict[str, Any] = None
    xgboost_params: Dict[str, Any] = None
    linear_regression_params: Dict[str, Any] = None
    
    # Training configuration
    test_size: float = 0.2
    random_state: int = 42
    cv_folds: int = 5
    
    # Model selection criteria
    min_r2_threshold: float = 0.7
    min_rmse_threshold: float = 50000
    
    def __post_init__(self):
        if self.model_versions is None:
            self.model_versions = ["1.0.0"]
            
        if self.feature_columns is None:
            self.feature_columns = [
                'area_sqft', 'bedrooms', 'bathrooms', 'age_years',
                'property_type_single_family', 'property_type_condo',
                'property_type_townhouse', 'property_type_multi_family',
                'amenities_score', 'distance_to_center', 'school_rating',
                'crime_index', 'market_trend', 'environmental_score'
            ]
            
        if self.categorical_features is None:
            self.categorical_features = ['property_type']
            
        if self.numerical_features is None:
            self.numerical_features = [
                'area_sqft', 'bedrooms', 'bathrooms', 'age_years',
                'amenities_score', 'distance_to_center', 'school_rating',
                'crime_index', 'market_trend', 'environmental_score'
            ]
            
        if self.random_forest_params is None:
            self.random_forest_params = {
                'n_estimators': 100,
                'max_depth': 15,
                'min_samples_split': 5,
                'min_samples_leaf': 2,
                'random_state': 42,
                'n_jobs': -1
            }
            
        if self.xgboost_params is None:
            self.xgboost_params = {
                'n_estimators': 100,
                'max_depth': 6,
                'learning_rate': 0.1,
                'random_state': 42,
                'n_jobs': -1
            }
            
        if self.linear_regression_params is None:
            self.linear_regression_params = {
                'fit_intercept': True
            }


# Global ML configuration instance
ml_config = MLConfig()