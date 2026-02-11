import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from app.core.logging import logger


class ModelEvaluator:
    """Model evaluation and performance metrics"""
    
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate comprehensive model performance metrics"""
        try:
            metrics = {
                'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
                'mae': mean_absolute_error(y_true, y_pred),
                'r2': r2_score(y_true, y_pred),
                'mean_error': np.mean(y_pred - y_true),
                'median_error': np.median(y_pred - y_true),
                'std_error': np.std(y_pred - y_true),
                'max_error': np.max(np.abs(y_pred - y_true)),
                'mean_absolute_percentage_error': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
            }
            
            # Add directional accuracy
            correct_direction = np.sum(np.sign(y_pred[1:] - y_pred[:-1]) == np.sign(y_true[1:] - y_true[:-1]))
            metrics['directional_accuracy'] = correct_direction / (len(y_true) - 1)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            raise
    
    @staticmethod
    def confidence_interval(predictions: np.ndarray, confidence_level: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval for predictions"""
        try:
            mean_pred = np.mean(predictions)
            std_pred = np.std(predictions)
            
            # For 95% confidence interval, use ~1.96 standard deviations
            if confidence_level == 0.95:
                z_score = 1.96
            elif confidence_level == 0.90:
                z_score = 1.645
            else:
                # Approximate z-score for other confidence levels
                from scipy import stats
                z_score = stats.norm.ppf((1 + confidence_level) / 2)
            
            margin_error = z_score * std_pred
            lower_bound = mean_pred - margin_error
            upper_bound = mean_pred + margin_error
            
            return float(lower_bound), float(upper_bound)
            
        except Exception as e:
            logger.error(f"Error calculating confidence interval: {str(e)}")
            raise
    
    @staticmethod
    def performance_benchmark(metrics: Dict[str, float]) -> Dict[str, str]:
        """Provide performance benchmarking against industry standards"""
        try:
            benchmarks = {
                'rmse': {'excellent': 30000, 'good': 50000, 'acceptable': 80000},
                'r2': {'excellent': 0.9, 'good': 0.8, 'acceptable': 0.7},
                'mae': {'excellent': 20000, 'good': 35000, 'acceptable': 50000}
            }
            
            ratings = {}
            
            for metric, benchmark in benchmarks.items():
                if metric in metrics:
                    value = metrics[metric]
                    
                    if metric == 'r2':  # Higher is better
                        if value >= benchmark['excellent']:
                            ratings[metric] = 'excellent'
                        elif value >= benchmark['good']:
                            ratings[metric] = 'good'
                        elif value >= benchmark['acceptable']:
                            ratings[metric] = 'acceptable'
                        else:
                            ratings[metric] = 'poor'
                    else:  # Lower is better (RMSE, MAE)
                        if value <= benchmark['excellent']:
                            ratings[metric] = 'excellent'
                        elif value <= benchmark['good']:
                            ratings[metric] = 'good'
                        elif value <= benchmark['acceptable']:
                            ratings[metric] = 'acceptable'
                        else:
                            ratings[metric] = 'poor'
            
            return ratings
            
        except Exception as e:
            logger.error(f"Error in performance benchmarking: {str(e)}")
            raise


class ModelExplainer:
    """Explainable AI for model predictions"""
    
    def __init__(self, model, feature_names: List[str]):
        self.model = model
        self.feature_names = feature_names
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        try:
            importance_scores = {}
            
            if hasattr(self.model, 'feature_importances_'):
                # Tree-based models
                importances = self.model.feature_importances_
                for i, feature in enumerate(self.feature_names):
                    importance_scores[feature] = float(importances[i])
                    
            elif hasattr(self.model, 'coef_'):
                # Linear models
                importances = np.abs(self.model.coef_)
                for i, feature in enumerate(self.feature_names):
                    importance_scores[feature] = float(importances[i])
            
            # Sort by importance
            sorted_importance = dict(sorted(importance_scores.items(), 
                                          key=lambda x: x[1], reverse=True))
            
            return sorted_importance
            
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            return {}
    
    def generate_explanation(self, prediction: float, feature_values: Dict[str, Any], 
                           feature_importance: Dict[str, float]) -> str:
        """Generate human-readable explanation for prediction"""
        try:
            # Get top 3 most important features
            top_features = list(feature_importance.items())[:3]
            
            explanation_parts = [
                f"This property is predicted to be worth ${prediction:,.0f}.",
                "The key factors influencing this prediction are:"
            ]
            
            for feature, importance in top_features:
                value = feature_values.get(feature, 'N/A')
                if feature == 'area_sqft':
                    explanation_parts.append(f"- Property size ({value:,} sq ft) contributes significantly to the value")
                elif feature == 'bedrooms':
                    explanation_parts.append(f"- Number of bedrooms ({value}) affects the price")
                elif feature == 'bathrooms':
                    explanation_parts.append(f"- Number of bathrooms ({value}) impacts the valuation")
                elif feature == 'age_years':
                    explanation_parts.append(f"- Property age ({value} years) influences depreciation")
                elif 'property_type' in feature:
                    property_type = feature.split('_')[-1].replace('_', ' ').title()
                    explanation_parts.append(f"- Property type ({property_type}) affects market value")
                elif feature == 'school_rating':
                    explanation_parts.append(f"- School district quality ({value}/10) adds premium value")
                elif feature == 'amenities_score':
                    explanation_parts.append(f"- Local amenities score ({value}/10) enhances property appeal")
                elif feature == 'crime_index':
                    explanation_parts.append(f"- Crime levels ({value}) impact desirability")
                else:
                    explanation_parts.append(f"- {feature.replace('_', ' ').title()} ({value}) contributes to the valuation")
            
            # Add confidence context
            explanation_parts.append("\nThis prediction is based on market analysis and comparable properties in the area.")
            
            return " ".join(explanation_parts)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {str(e)}")
            return f"This property is predicted to be worth ${prediction:,.0f} based on market analysis."
    
    def generate_detailed_explanation(self, prediction: float, feature_values: Dict[str, Any], 
                                    feature_importance: Dict[str, float], confidence_score: float) -> str:
        """Generate detailed explanation with confidence context"""
        try:
            # Get top 3-5 most important features with their impact
            top_features = list(feature_importance.items())[:5]
            
            explanation_parts = [
                f"This property is predicted to be worth ${prediction:,.0f}.",
                "Key factors influencing this valuation:"
            ]
            
            for feature, importance in top_features:
                value = feature_values.get(feature, 'N/A')
                impact_strength = self._get_impact_strength(importance)
                
                if feature == 'area_sqft':
                    explanation_parts.append(f"• Property size ({value:,} sq ft) has {impact_strength} positive impact on value")
                elif feature == 'bedrooms':
                    explanation_parts.append(f"• Number of bedrooms ({value}) has {impact_strength} influence on price")
                elif feature == 'bathrooms':
                    explanation_parts.append(f"• Number of bathrooms ({value}) has {impact_strength} impact on valuation")
                elif feature == 'age_years':
                    explanation_parts.append(f"• Property age ({value} years) has {impact_strength} effect on depreciation")
                elif 'property_type' in feature:
                    property_type = feature.split('_')[-1].replace('_', ' ').title()
                    explanation_parts.append(f"• Property type ({property_type}) has {impact_strength} market impact")
                elif feature == 'school_rating':
                    explanation_parts.append(f"• School district quality ({value}/10) provides {impact_strength} premium value")
                elif feature == 'amenities_score':
                    explanation_parts.append(f"• Local amenities score ({value}/10) creates {impact_strength} buyer appeal")
                elif feature == 'crime_index':
                    explanation_parts.append(f"• Crime levels ({value}) have {impact_strength} effect on desirability")
                else:
                    explanation_parts.append(f"• {feature.replace('_', ' ').title()} ({value}) contributes {impact_strength} to valuation")
            
            # Add confidence context
            confidence_label = self._get_confidence_label(confidence_score)
            explanation_parts.append(f"\nModel confidence: {confidence_label} ({confidence_score*100:.0f}%)")
            explanation_parts.append("This estimate is generated by a machine learning model and is for informational purposes only.")
            
            return " ".join(explanation_parts)
            
        except Exception as e:
            logger.error(f"Error generating detailed explanation: {str(e)}")
            return f"This property is predicted to be worth ${prediction:,.0f} based on market analysis. This estimate is generated by a machine learning model and is for informational purposes only."
    
    def _get_impact_strength(self, importance: float) -> str:
        """Convert importance score to descriptive strength"""
        if importance >= 0.3:
            return "strong"
        elif importance >= 0.15:
            return "moderate"
        elif importance >= 0.05:
            return "mild"
        else:
            return "minimal"
    
    def _get_confidence_label(self, confidence_score: float) -> str:
        """Convert confidence score to label according to specified ranges"""
        if confidence_score < 0.4:
            return "Low"
        elif confidence_score <= 0.7:
            return "Medium"
        else:
            return "High"
    
    def calculate_confidence_score(self, feature_importance: Dict[str, float], 
                                 prediction_metrics: Dict[str, float] = None) -> float:
        """Calculate confidence score for prediction"""
        try:
            # Base confidence from feature importance distribution
            importance_values = list(feature_importance.values())
            if importance_values:
                # More evenly distributed importance = higher confidence
                importance_std = np.std(importance_values)
                base_confidence = 1.0 - min(importance_std / np.mean(importance_values), 1.0)
            else:
                base_confidence = 0.5
            
            # Adjust based on model performance if available
            if prediction_metrics and 'r2' in prediction_metrics:
                performance_adjustment = min(prediction_metrics['r2'], 1.0)
                confidence = (base_confidence + performance_adjustment) / 2
            else:
                confidence = base_confidence
            
            # Ensure confidence is between 0 and 1
            return float(np.clip(confidence, 0.0, 1.0))
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            return 0.5


# Global instances
model_evaluator = ModelEvaluator()