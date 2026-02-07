import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from typing import Dict, Any, Tuple
from app.core.logging import logger
from ml.config.ml_config import ml_config


class FeatureEngineeringPipeline:
    """Feature engineering pipeline for house price prediction"""
    
    def __init__(self):
        self.preprocessor = None
        self.feature_names = None
        self._build_pipeline()
    
    def _build_pipeline(self):
        """Build the preprocessing pipeline"""
        try:
            # Numerical features pipeline
            numerical_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ])
            
            # Categorical features pipeline
            categorical_pipeline = Pipeline([
                ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
                ('onehot', OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore'))
            ])
            
            # Combine pipelines
            self.preprocessor = ColumnTransformer([
                ('num', numerical_pipeline, ml_config.numerical_features),
                ('cat', categorical_pipeline, ml_config.categorical_features)
            ])
            
            logger.info("Feature engineering pipeline built successfully")
            
        except Exception as e:
            logger.error(f"Error building feature pipeline: {str(e)}")
            raise
    
    def fit_transform(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, list]:
        """Fit and transform the data"""
        try:
            # Fit the preprocessor
            transformed_data = self.preprocessor.fit_transform(df)
            
            # Get feature names
            self.feature_names = self._get_feature_names()
            
            # Create DataFrame with proper column names
            result_df = pd.DataFrame(transformed_data, columns=self.feature_names)
            
            logger.info(f"Feature engineering completed. Shape: {result_df.shape}")
            return result_df, self.feature_names
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {str(e)}")
            raise
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform new data using fitted pipeline"""
        try:
            if self.preprocessor is None:
                raise ValueError("Pipeline not fitted. Call fit_transform first.")
            
            transformed_data = self.preprocessor.transform(df)
            result_df = pd.DataFrame(transformed_data, columns=self.feature_names)
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error transforming data: {str(e)}")
            raise
    
    def _get_feature_names(self) -> list:
        """Get feature names after transformation"""
        try:
            feature_names = []
            
            # Get numerical feature names
            feature_names.extend(ml_config.numerical_features)
            
            # Get categorical feature names
            if hasattr(self.preprocessor.named_transformers_['cat'], 'named_steps'):
                onehot = self.preprocessor.named_transformers_['cat'].named_steps['onehot']
                if hasattr(onehot, 'get_feature_names_out'):
                    cat_feature_names = onehot.get_feature_names_out(ml_config.categorical_features)
                    feature_names.extend(cat_feature_names.tolist())
            
            return feature_names
            
        except Exception as e:
            logger.error(f"Error getting feature names: {str(e)}")
            # Fallback to config feature columns
            return ml_config.feature_columns
    
    def generate_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate synthetic training data"""
        try:
            np.random.seed(42)
            
            # Generate realistic property data
            data = {
                'area_sqft': np.random.normal(2000, 800, n_samples),
                'bedrooms': np.random.choice([1, 2, 3, 4, 5, 6], n_samples, p=[0.05, 0.15, 0.3, 0.25, 0.2, 0.05]),
                'bathrooms': np.random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5], n_samples),
                'age_years': np.random.exponential(20, n_samples),
                'property_type': np.random.choice(
                    ['single_family', 'condo', 'townhouse', 'multi_family'],
                    n_samples,
                    p=[0.6, 0.2, 0.15, 0.05]
                ),
                'amenities_score': np.random.beta(2, 1, n_samples) * 10,
                'distance_to_center': np.random.exponential(8, n_samples),
                'school_rating': np.random.beta(2, 1.5, n_samples) * 10,
                'crime_index': np.random.gamma(2, 2, n_samples),
                'market_trend': np.random.normal(1.0, 0.1, n_samples),
                'environmental_score': np.random.beta(1.5, 1, n_samples) * 10
            }
            
            # Create DataFrame and apply realistic constraints
            df = pd.DataFrame(data)
            
            # Apply constraints
            df['area_sqft'] = np.clip(df['area_sqft'], 500, 10000)
            df['age_years'] = np.clip(df['age_years'], 0, 150)
            df['crime_index'] = np.clip(df['crime_index'], 0, 20)
            df['market_trend'] = np.clip(df['market_trend'], 0.5, 2.0)
            
            # Generate realistic prices based on features
            base_price = 200000
            price = (
                base_price +
                df['area_sqft'] * 100 +
                df['bedrooms'] * 15000 +
                df['bathrooms'] * 12000 +
                (10 - df['age_years'] / 10) * 2000 +
                np.where(df['property_type'] == 'single_family', 50000, 0) +
                df['amenities_score'] * 8000 +
                (10 - df['distance_to_center']) * 3000 +
                df['school_rating'] * 12000 -
                df['crime_index'] * 2000 +
                (df['market_trend'] - 1) * 100000 +
                df['environmental_score'] * 5000 +
                np.random.normal(0, 25000, n_samples)  # Add noise
            )
            
            df['price'] = np.clip(price, 50000, 2000000)
            
            logger.info(f"Generated {n_samples} synthetic data samples")
            return df
            
        except Exception as e:
            logger.error(f"Error generating synthetic data: {str(e)}")
            raise


# Global feature engineering instance
feature_pipeline = FeatureEngineeringPipeline()