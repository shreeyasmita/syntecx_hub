'use client'

import { useState, useEffect } from 'react'
import { ApiService, formatCurrency, formatPercentage } from '../lib/api'

export default function Dashboard() {
  const [propertyData, setPropertyData] = useState({
    area_sqft: 2000,
    bedrooms: 3,
    bathrooms: 2,
    age_years: 10,
    property_type: 'single_family'
  })
  
  const [prediction, setPrediction] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handlePredict = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await ApiService.predictPrice(propertyData)
      if (response.error) {
        setError(response.error)
      } else {
        setPrediction(response.data)
      }
    } catch (err) {
      setError('Failed to get prediction')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Auto-predict on initial load
    handlePredict()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              SynTeCX House Price Predictor
            </h1>
            <p className="text-xl text-gray-600">
              AI-powered real estate valuation with explainable insights
            </p>
          </div>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Form */}
          <div className="lg:col-span-1">
            <div className="card p-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-6">Property Details</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Area (sq ft)
                  </label>
                  <input
                    type="number"
                    value={propertyData.area_sqft}
                    onChange={(e) => setPropertyData({...propertyData, area_sqft: parseInt(e.target.value) || 0})}
                    className="input w-full"
                    min="500"
                    max="10000"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bedrooms
                  </label>
                  <select
                    value={propertyData.bedrooms}
                    onChange={(e) => setPropertyData({...propertyData, bedrooms: parseInt(e.target.value)})}
                    className="input w-full"
                  >
                    {[1,2,3,4,5,6].map(num => (
                      <option key={num} value={num}>{num} Bedroom{num > 1 ? 's' : ''}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Bathrooms
                  </label>
                  <select
                    value={propertyData.bathrooms}
                    onChange={(e) => setPropertyData({...propertyData, bathrooms: parseFloat(e.target.value)})}
                    className="input w-full"
                  >
                    {[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5].map(num => (
                      <option key={num} value={num}>{num}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Age (years)
                  </label>
                  <input
                    type="number"
                    value={propertyData.age_years}
                    onChange={(e) => setPropertyData({...propertyData, age_years: parseInt(e.target.value) || 0})}
                    className="input w-full"
                    min="0"
                    max="150"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Property Type
                  </label>
                  <select
                    value={propertyData.property_type}
                    onChange={(e) => setPropertyData({...propertyData, property_type: e.target.value})}
                    className="input w-full"
                  >
                    <option value="single_family">Single Family</option>
                    <option value="condo">Condo</option>
                    <option value="townhouse">Townhouse</option>
                    <option value="multi_family">Multi-Family</option>
                  </select>
                </div>

                <button
                  onClick={handlePredict}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? 'Calculating...' : 'Get Price Prediction'}
                </button>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="lg:col-span-2">
            {error && (
              <div className="card p-6 mb-6 bg-red-50 border-red-200">
                <div className="text-red-800">{error}</div>
              </div>
            )}

            {prediction && (
              <div className="space-y-6">
                {/* Main Prediction Card */}
                <div className="card p-6">
                  <h2 className="text-2xl font-semibold text-gray-800 mb-4">Price Prediction</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-3xl font-bold text-blue-700">
                        {formatCurrency(prediction.predicted_price)}
                      </div>
                      <div className="text-sm text-gray-600">Predicted Price</div>
                    </div>
                    
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-xl font-semibold text-green-700">
                        {formatCurrency(prediction.price_range[0])} - {formatCurrency(prediction.price_range[1])}
                      </div>
                      <div className="text-sm text-gray-600">Price Range</div>
                    </div>
                    
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-700">
                        {(prediction.confidence_score * 100).toFixed(1)}%
                      </div>
                      <div className="text-sm text-gray-600">Confidence Score</div>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-800 mb-2">Explanation</h3>
                    <p className="text-gray-700">{prediction.explanation}</p>
                  </div>
                </div>

                {/* Feature Importance */}
                {prediction.feature_importance && Object.keys(prediction.feature_importance).length > 0 && (
                  <div className="card p-6">
                    <h3 className="text-xl font-semibold text-gray-800 mb-4">Feature Importance</h3>
                    <div className="space-y-3">
                      {Object.entries(prediction.feature_importance)
                        .sort(([,a], [,b]) => (b as number) - (a as number))
                        .slice(0, 5)
                        .map(([feature, importance]) => (
                          <div key={feature} className="flex items-center">
                            <div className="w-32 text-sm text-gray-600">
                              {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </div>
                            <div className="flex-1 mx-4">
                              <div className="w-full bg-gray-200 rounded-full h-2">
                                <div 
                                  className="bg-blue-600 h-2 rounded-full" 
                                  style={{ width: `${(importance as number) * 100}%` }}
                                ></div>
                              </div>
                            </div>
                            <div className="w-16 text-sm text-gray-700 text-right">
                              {((importance as number) * 100).toFixed(1)}%
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-gray-500 text-sm">
          <p>Powered by SynTeCX Technologies • ML House Price Prediction Platform</p>
          <p className="mt-1">Version 1.0.0</p>
        </footer>
      </div>
    </div>
  )
}