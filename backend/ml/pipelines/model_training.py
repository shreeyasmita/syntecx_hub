import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor
import joblib
import os
from typing import Dict, Tuple, Any
from datetime import datetime
from app.core.logging import logger
from ml.config.ml_config import ml_config
from ml.pipelines.feature_engineering import feature_pipeline


class ModelTrainer:
    """Model training pipeline with multiple algorithms"""
    
    def __init__(self):
        self.models = {}
        self.model_scores = {}
        self.best_model = None
        self.best_model_name = None
        self.feature_names = None
    
    def train_models(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Train multiple models and select the best one"""
        try:
            logger.info("Starting model training process")
            
            # Separate features and target
            X = df.drop('price', axis=1)
            y = df['price']
            
            # Apply feature engineering
            X_processed, self.feature_names = feature_pipeline.fit_transform(X)
            
            logger.info(f"Training data shape: {X_processed.shape}")
            
            # Split data
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X_processed, y, test_size=ml_config.test_size, 
                random_state=ml_config.random_state
            )
            
            # Initialize models
            models = {
                'linear_regression': LinearRegression(**ml_config.linear_regression_params),
                'random_forest': RandomForestRegressor(**ml_config.random_forest_params),
                'xgboost': XGBRegressor(**ml_config.xgboost_params)
            }
            
            # Train and evaluate each model
            for name, model in models.items():
                logger.info(f"Training {name}...")
                
                # Train model
                model.fit(X_train, y_train)
                
                # Make predictions
                y_pred_train = model.predict(X_train)
                y_pred_test = model.predict(X_test)
                
                # Calculate metrics
                train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
                test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
                train_r2 = r2_score(y_train, y_pred_train)
                test_r2 = r2_score(y_test, y_pred_test)
                
                # Store results
                self.models[name] = model
                self.model_scores[name] = {
                    'train_rmse': train_rmse,
                    'test_rmse': test_rmse,
                    'train_r2': train_r2,
                    'test_r2': test_r2,
                    'train_size': len(X_train),
                    'test_size': len(X_test)
                }
                
                logger.info(f"{name} - Train RMSE: ${train_rmse:,.2f}, Test RMSE: ${test_rmse:,.2f}")
                logger.info(f"{name} - Train R²: {train_r2:.4f}, Test R²: {test_r2:.4f}")
            
            # Select best model based on test RMSE and R²
            self._select_best_model()
            
            # Save models
            self._save_models()
            
            training_summary = {
                'model_scores': self.model_scores,
                'best_model': self.best_model_name,
                'feature_names': self.feature_names,
                'training_date': datetime.now().isoformat(),
                'dataset_size': len(df)
            }
            
            logger.info(f"Model training completed. Best model: {self.best_model_name}")
            return training_summary
            
        except Exception as e:
            logger.error(f"Error in model training: {str(e)}")
            raise
    
    def _select_best_model(self):
        """Select the best model based on performance criteria"""
        try:
            best_score = float('inf')
            
            for name, scores in self.model_scores.items():
                test_rmse = scores['test_rmse']
                test_r2 = scores['test_r2']
                
                # Check minimum thresholds
                if test_r2 >= ml_config.min_r2_threshold and test_rmse <= ml_config.min_rmse_threshold:
                    # Lower RMSE is better
                    if test_rmse < best_score:
                        best_score = test_rmse
                        self.best_model = self.models[name]
                        self.best_model_name = name
            
            if self.best_model is None:
                # If no model meets thresholds, select based on R²
                logger.warning("No model meets performance thresholds, selecting based on R²")
                best_r2 = -1
                for name, scores in self.model_scores.items():
                    if scores['test_r2'] > best_r2:
                        best_r2 = scores['test_r2']
                        self.best_model = self.models[name]
                        self.best_model_name = name
            
            logger.info(f"Selected best model: {self.best_model_name}")
            
        except Exception as e:
            logger.error(f"Error selecting best model: {str(e)}")
            raise
    
    def _save_models(self):
        """Save trained models to disk"""
        try:
            model_dir = ml_config.model_versions[0]  # Using default version for now
            model_path = os.path.join("ml", "models", model_dir)
            
            # Create directory if it doesn't exist
            os.makedirs(model_path, exist_ok=True)
            
            # Save each model
            for name, model in self.models.items():
                model_file = os.path.join(model_path, f"{name}.pkl")
                joblib.dump(model, model_file)
                logger.info(f"Saved {name} model to {model_file}")
            
            # Save feature pipeline
            pipeline_file = os.path.join(model_path, "feature_pipeline.pkl")
            joblib.dump(feature_pipeline, pipeline_file)
            logger.info(f"Saved feature pipeline to {pipeline_file}")
            
            # Save metadata
            metadata = {
                'best_model': self.best_model_name,
                'model_scores': self.model_scores,
                'feature_names': self.feature_names,
                'training_date': datetime.now().isoformat(),
                'config': ml_config.__dict__
            }
            
            metadata_file = os.path.join(model_path, "metadata.json")
            import json
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Saved model metadata to {metadata_file}")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            raise
    
    def load_models(self, version: str = None) -> bool:
        """Load trained models from disk"""
        try:
            if version is None:
                version = ml_config.default_version
            
            model_path = os.path.join("ml", "models", version)
            
            if not os.path.exists(model_path):
                logger.warning(f"Model version {version} not found")
                return False
            
            # Load models
            for model_name in ['linear_regression', 'random_forest', 'xgboost']:
                model_file = os.path.join(model_path, f"{model_name}.pkl")
                if os.path.exists(model_file):
                    self.models[model_name] = joblib.load(model_file)
                    logger.info(f"Loaded {model_name} model")
            
            # Load feature pipeline
            pipeline_file = os.path.join(model_path, "feature_pipeline.pkl")
            if os.path.exists(pipeline_file):
                global feature_pipeline
                feature_pipeline = joblib.load(pipeline_file)
                logger.info("Loaded feature pipeline")
            
            # Load metadata to get best model
            metadata_file = os.path.join(model_path, "metadata.json")
            if os.path.exists(metadata_file):
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                self.best_model_name = metadata['best_model']
                self.best_model = self.models.get(self.best_model_name)
                self.model_scores = metadata['model_scores']
                self.feature_names = metadata['feature_names']
                
                logger.info(f"Loaded model metadata. Best model: {self.best_model_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False


# Global model trainer instance
model_trainer = ModelTrainer()