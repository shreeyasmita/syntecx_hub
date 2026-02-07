# ML Pipeline Documentation

## Overview

The SynTeCX House Price Prediction platform uses a sophisticated machine learning pipeline with multiple algorithms, automated model selection, and explainable AI features.

## Architecture

```
Input Data → Feature Engineering → Model Training → Model Selection → Prediction
     ↓              ↓                    ↓              ↓             ↓
Validation    Preprocessing         Evaluation      Confidence    Explanation
```

## Feature Engineering

### Core Features
- **area_sqft**: Property area in square feet (500-20000)
- **bedrooms**: Number of bedrooms (0-10)
- **bathrooms**: Number of bathrooms (0-10, whole/half numbers)
- **age_years**: Property age in years (0-200)
- **property_type**: Categorical (single_family, condo, townhouse, multi_family)

### Advanced Features
- **amenities_score**: Composite score of nearby amenities (0-10)
- **distance_to_center**: Distance to city center in miles (0+)
- **school_rating**: Average school rating in area (0-10)
- **crime_index**: Local crime statistics (0+)
- **market_trend**: Current market conditions indicator
- **environmental_score**: Environmental factors score (0-10)

### Feature Processing Pipeline

1. **Data Validation**: Range checking and type validation
2. **Missing Value Imputation**: 
   - Numerical: Median imputation
   - Categorical: "missing" category
3. **Scaling**: StandardScaler for numerical features
4. **Encoding**: OneHotEncoder with drop='first' for categorical features
5. **Feature Selection**: Automatic based on model importance

## Models

### Implemented Algorithms

#### 1. Linear Regression
- **Purpose**: Baseline model for comparison
- **Parameters**: 
  - fit_intercept: True
  - normalize: False
- **Strengths**: Interpretable, fast training
- **Weaknesses**: Assumes linear relationships

#### 2. Random Forest
- **Purpose**: Non-linear pattern detection
- **Parameters**:
  - n_estimators: 100
  - max_depth: 15
  - min_samples_split: 5
  - min_samples_leaf: 2
  - random_state: 42
- **Strengths**: Handles non-linear relationships, feature importance
- **Weaknesses**: Can overfit with insufficient data

#### 3. XGBoost
- **Purpose**: Gradient boosting for high performance
- **Parameters**:
  - n_estimators: 100
  - max_depth: 6
  - learning_rate: 0.1
  - random_state: 42
- **Strengths**: High accuracy, handles complex patterns
- **Weaknesses**: More complex, longer training time

### Model Selection Process

1. **Training**: All models trained on same dataset
2. **Evaluation**: Test set RMSE and R² calculated
3. **Threshold Check**: 
   - Minimum R²: 0.7
   - Maximum RMSE: $50,000
4. **Selection**: Model with best test RMSE meeting thresholds
5. **Fallback**: If no model meets thresholds, select highest R²

### Performance Metrics

- **RMSE**: Root Mean Square Error (lower is better)
- **R²**: Coefficient of Determination (higher is better)
- **MAE**: Mean Absolute Error
- **Directional Accuracy**: Percentage of correct trend predictions

## Model Versioning

### Version Format
Semantic versioning: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes to model architecture
- MINOR: New features or performance improvements
- PATCH: Bug fixes, minor improvements

### Storage Structure
```
ml/models/
├── 1.0.0/
│   ├── linear_regression.pkl
│   ├── random_forest.pkl
│   ├── xgboost.pkl
│   ├── feature_pipeline.pkl
│   └── metadata.json
└── 1.1.0/
    ├── linear_regression.pkl
    ├── random_forest.pkl
│   ├── xgboost.pkl
│   ├── feature_pipeline.pkl
│   └── metadata.json
```

### Metadata Format
```json
{
  "best_model": "random_forest",
  "model_scores": {
    "linear_regression": {...},
    "random_forest": {...},
    "xgboost": {...}
  },
  "feature_names": ["area_sqft", "bedrooms", ...],
  "training_date": "2024-01-15T10:30:00Z",
  "config": {...}
}
```

## Training Process

### Data Generation
- **Synthetic Data**: 2000+ samples generated using realistic distributions
- **Feature Correlations**: Built-in relationships between features
- **Price Formula**: Realistic pricing based on feature weights
- **Noise**: Added Gaussian noise for realistic variation

### Cross-Validation
- **Folds**: 5-fold cross-validation
- **Test Split**: 20% held out for final evaluation
- **Random State**: Fixed for reproducibility

### Retraining
- **Trigger**: New data available or performance degradation
- **Process**: Full pipeline re-execution
- **Validation**: New model must meet performance thresholds
- **Rollback**: Automatic rollback if new model performs worse

## Explainable AI

### Feature Importance
- **Calculation**: Model-specific importance scores
- **Normalization**: Values sum to 1.0
- **Visualization**: Bar charts and rankings
- **Interpretation**: Higher values indicate more influence

### Confidence Scoring
- **Method**: Based on feature importance distribution and model performance
- **Range**: 0.0 to 1.0
- **Factors**:
  - Feature importance consistency
  - Model R² score
  - Prediction stability

### Human-Readable Explanations
- **Template-based**: Structured natural language generation
- **Key Features**: Top 3 most important features highlighted
- **Contextual**: Property-specific details included
- **Actionable**: Clear factors affecting the price

## Performance Benchmarks

### Industry Standards
- **Excellent**: RMSE < $30,000, R² > 0.9
- **Good**: RMSE < $50,000, R² > 0.8
- **Acceptable**: RMSE < $80,000, R² > 0.7

### Current Performance
- **Typical RMSE**: $35,000 - $45,000
- **Typical R²**: 0.85 - 0.92
- **Confidence Score**: 0.80 - 0.95

## Monitoring and Maintenance

### Performance Tracking
- **Prediction Logging**: All predictions stored with features
- **Drift Detection**: Statistical tests for feature distribution changes
- **Accuracy Monitoring**: Ongoing performance evaluation
- **Alerts**: Automated notifications for performance degradation

### Model Updates
- **Scheduled Retraining**: Monthly or when significant new data available
- **A/B Testing**: Compare new vs current models
- **Gradual Rollout**: Percentage-based deployment
- **Rollback Capability**: Instant version switching

## Future Enhancements

### Planned Features
- **Deep Learning**: Neural network architectures
- **Time Series**: Temporal price prediction
- **Geospatial**: Location-based clustering
- **Ensemble Methods**: Stacking and blending techniques
- **AutoML**: Automated hyperparameter tuning

### Scalability Improvements
- **Distributed Training**: Multi-node model training
- **Model Compression**: Quantization and pruning
- **Caching**: Prediction result caching
- **Batch Processing**: Bulk prediction capabilities