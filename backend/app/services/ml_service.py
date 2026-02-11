import pandas as pd
import numpy as np
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
from app.core.logging import logger
from app.models.domain.prediction import (
    PredictionRequest, PredictionResponse, 
    WhatIfAnalysisRequest, WhatIfAnalysisResponse
)
from ml.pipelines.feature_engineering import feature_pipeline
from ml.pipelines.model_training import model_trainer
from ml.utils.model_evaluator import model_evaluator, ModelExplainer


class MLServices:
    """Core ML services for house price prediction"""
    
    def __init__(self):
        self.is_initialized = False
        self.model_version = None
        
    async def initialize(self) -> bool:
        """Initialize ML services and load models"""
        try:
            if self.is_initialized:
                return True
                
            logger.info("Initializing ML services...")
            
            # Generate synthetic training data
            logger.info("Generating synthetic training data...")
            synthetic_data = feature_pipeline.generate_synthetic_data(2000)
            
            # Train models
            logger.info("Training models...")
            training_result = model_trainer.train_models(synthetic_data)
            self.model_version = training_result.get('training_date', '1.0.0')[:10]  # Use date as version
            
            self.is_initialized = True
            logger.info("ML services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing ML services: {str(e)}")
            return False
    
    def predict_price(self, request: PredictionRequest) -> PredictionResponse:
        """Make house price prediction with explanation"""
        try:
            start_time = time.time()
            
            if not self.is_initialized:
                raise ValueError("ML services not initialized. Call initialize() first.")
            
            if model_trainer.best_model is None:
                raise ValueError("No trained model available")
            
            # Convert request to DataFrame
            request_dict = request.dict()
            df = pd.DataFrame([request_dict])
            
            # Apply feature engineering
            processed_features = feature_pipeline.transform(df.drop(['latitude', 'longitude', 'zip_code'], axis=1, errors='ignore'))
            
            # Make prediction
            prediction = model_trainer.best_model.predict(processed_features)[0]
            
            # Get feature importance
            explainer = ModelExplainer(model_trainer.best_model, feature_pipeline.feature_names)
            feature_importance = explainer.get_feature_importance()
            
            # Calculate confidence score
            confidence_score = explainer.calculate_confidence_score(feature_importance)
            
            # Calculate price range based on confidence (1 - confidence) × 10% uncertainty
            uncertainty_factor = (1 - confidence_score) * 0.10
            price_uncertainty = prediction * uncertainty_factor
            lower_bound = prediction - price_uncertainty
            upper_bound = prediction + price_uncertainty
            
            # Ensure min and max are different
            if lower_bound == upper_bound:
                lower_bound = prediction * 0.95  # 5% below
                upper_bound = prediction * 1.05  # 5% above
            
            # Generate explanation with proper feature impact analysis
            explanation = explainer.generate_detailed_explanation(
                prediction, request_dict, feature_importance, confidence_score
            )
            
            processing_time = time.time() - start_time
            
            # Create response
            response = PredictionResponse(
                predicted_price=float(prediction),
                price_range=[float(lower_bound), float(upper_bound)],
                confidence_score=float(confidence_score),
                model_version=self.model_version,
                feature_importance=feature_importance,
                explanation=explanation,
                prediction_id=str(uuid.uuid4()),
                processing_time=processing_time
            )
            
            logger.info(f"Prediction completed: ${prediction:,.0f} (Confidence: {confidence_score:.2f})")
            return response
            
        except Exception as e:
            logger.error(f"Error in price prediction: {str(e)}")
            raise
    
    def what_if_analysis(self, request: WhatIfAnalysisRequest) -> WhatIfAnalysisResponse:
        """Perform what-if analysis with multiple scenarios"""
        try:
            start_time = time.time()
            
            if not self.is_initialized:
                raise ValueError("ML services not initialized. Call initialize() first.")
            
            # Get base prediction
            base_prediction = self.predict_price(request.base_property)
            
            # Process scenarios
            scenario_predictions = []
            
            for i, scenario in enumerate(request.scenarios):
                # Create modified property for this scenario
                scenario_property = request.base_property.copy(deep=True)
                
                # Apply scenario changes
                for key, value in scenario.items():
                    if hasattr(scenario_property, key):
                        setattr(scenario_property, key, value)
                
                # Make prediction for scenario
                scenario_prediction = self.predict_price(scenario_property)
                scenario_predictions.append(scenario_prediction)
            
            # Generate comparison analysis
            base_price = base_prediction.predicted_price
            scenario_prices = [pred.predicted_price for pred in scenario_predictions]
            
            comparison_analysis = {
                'base_price': base_price,
                'scenario_changes': [],
                'price_impact': [],
                'percentage_changes': []
            }
            
            for i, (scenario, pred) in enumerate(zip(request.scenarios, scenario_predictions)):
                scenario_price = pred.predicted_price
                price_change = scenario_price - base_price
                percentage_change = (price_change / base_price) * 100
                
                comparison_analysis['scenario_changes'].append(scenario)
                comparison_analysis['price_impact'].append(price_change)
                comparison_analysis['percentage_changes'].append(percentage_change)
            
            processing_time = time.time() - start_time
            
            response = WhatIfAnalysisResponse(
                base_prediction=base_prediction,
                scenario_predictions=scenario_predictions,
                comparison_analysis=comparison_analysis
            )
            
            logger.info(f"What-if analysis completed with {len(scenario_predictions)} scenarios")
            return response
            
        except Exception as e:
            logger.error(f"Error in what-if analysis: {str(e)}")
            raise
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get current model performance metrics"""
        try:
            if not self.is_initialized:
                return {"error": "ML services not initialized"}
            
            performance_data = {
                'model_version': self.model_version,
                'best_model': model_trainer.best_model_name,
                'model_scores': model_trainer.model_scores,
                'feature_count': len(feature_pipeline.feature_names) if feature_pipeline.feature_names else 0,
                'last_updated': datetime.now().isoformat()
            }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error getting model performance: {str(e)}")
            return {"error": str(e)}
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get current feature importance scores"""
        try:
            if not self.is_initialized or model_trainer.best_model is None:
                return {}
            
            explainer = ModelExplainer(model_trainer.best_model, feature_pipeline.feature_names)
            return explainer.get_feature_importance()
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return {}
    
    async def retrain_model(self) -> Dict[str, Any]:
        """Retrain model with new data"""
        try:
            logger.info("Starting model retraining...")
            
            # Generate new synthetic data
            new_data = feature_pipeline.generate_synthetic_data(2500)
            
            # Retrain models
            training_result = model_trainer.train_models(new_data)
            self.model_version = training_result.get('training_date', datetime.now().isoformat())[:10]
            
            logger.info("Model retraining completed successfully")
            return {
                'success': True,
                'new_model_version': self.model_version,
                'training_summary': training_result
            }
            
        except Exception as e:
            logger.error(f"Error in model retraining: {str(e)}")
            return {'success': False, 'error': str(e)}


# Global ML service instance
ml_service = MLServices()