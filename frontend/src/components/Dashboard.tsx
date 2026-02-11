'use client'

import { useState, useEffect } from 'react'
import { ApiService, formatCurrency } from '../lib/api'

interface PredictionResult {
  predicted_price: number;
  price_range: [number, number];
  confidence_score: number;
  model_version: string;
  feature_importance: Record<string, number>;
  explanation: string;
  prediction_id: string;
  processing_time: number;
}

export default function Dashboard() {
  const [propertyData, setPropertyData] = useState({
    area_sqft: 2000,
    bedrooms: 3,
    bathrooms: 2,
    age_years: 10,
    property_type: 'single_family'
  })
  
  const [prediction, setPrediction] = useState<PredictionResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handlePredict = async () => {
    setLoading(true)
    setError('')
    
    try {
      const response = await ApiService.predictPrice(propertyData)
      if (response.error) {
        setError('Unable to calculate price prediction. Please try again.')
      } else {
        setPrediction(response.data)
      }
    } catch (err) {
      setError('Connection error. Please check your network and try again.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Auto-predict on initial load
    handlePredict()
  }, [])

  const getConfidenceText = (score: number): string => {
    if (score > 0.7) return 'High';
    if (score > 0.4) return 'Medium';
    return 'Low';
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-3">
            House Price Predictor
          </h1>
          <p className="text-gray-600">
            Get instant property value estimates
          </p>
        </header>

        {/* Input Form */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-6">Property Details</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Living Area (sq ft)</label>
              <input
                type="number"
                value={propertyData.area_sqft}
                onChange={(e) => setPropertyData({...propertyData, area_sqft: parseInt(e.target.value) || 0})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min="500"
                max="10000"
                placeholder="Enter square footage"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bedrooms</label>
              <select
                value={propertyData.bedrooms}
                onChange={(e) => setPropertyData({...propertyData, bedrooms: parseInt(e.target.value)})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {[1,2,3,4,5,6].map(num => (
                  <option key={num} value={num}>{num} {num === 1 ? 'Bedroom' : 'Bedrooms'}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bathrooms</label>
              <select
                value={propertyData.bathrooms}
                onChange={(e) => setPropertyData({...propertyData, bathrooms: parseFloat(e.target.value)})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5].map(num => (
                  <option key={num} value={num}>{num}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Property Age (years)</label>
              <input
                type="number"
                value={propertyData.age_years}
                onChange={(e) => setPropertyData({...propertyData, age_years: parseInt(e.target.value) || 0})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                min="0"
                max="150"
                placeholder="Years since built"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Property Type</label>
              <select
                value={propertyData.property_type}
                onChange={(e) => setPropertyData({...propertyData, property_type: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="single_family">Single Family Home</option>
                <option value="condo">Condominium</option>
                <option value="townhouse">Townhouse</option>
                <option value="multi_family">Multi-Family</option>
              </select>
            </div>
          </div>

          <button
            onClick={handlePredict}
            disabled={loading}
            className="w-full mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Calculating...' : 'Get Price Estimate'}
          </button>
        </div>

        {/* Results */}
        <div>
          {/* Status Messages */}
          {loading && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
              <div className="flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
                <div>
                  <h3 className="text-blue-800 font-medium">Analyzing your property...</h3>
                  <p className="text-blue-600 text-sm mt-1">Our AI is processing your property details</p>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
              <div className="flex items-start">
                <div className="text-red-500 mr-3 mt-0.5">⚠️</div>
                <div>
                  <h3 className="text-red-800 font-medium">Unable to process your request</h3>
                  <p className="text-red-600 text-sm mt-1">{error}</p>
                  <button 
                    onClick={handlePredict}
                    className="mt-3 text-red-700 hover:text-red-900 text-sm font-medium"
                  >
                    Try Again
                  </button>
                </div>
              </div>
            </div>
          )}

          {prediction && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Price Estimate</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center p-6 bg-blue-50 rounded-xl border border-blue-200">
                  <div className="text-3xl font-bold text-blue-800 mb-2">
                    {formatCurrency(prediction.predicted_price)}
                  </div>
                  <div className="text-blue-700 font-medium">Estimated Value</div>
                </div>
                
                <div className="text-center p-6 bg-green-50 rounded-xl border border-green-200">
                  <div className="text-xl font-bold text-green-800 mb-2">
                    {formatCurrency(prediction.price_range[0])} - {formatCurrency(prediction.price_range[1])}
                  </div>
                  <div className="text-green-700 font-medium">Price Range</div>
                </div>
                
                <div className="text-center p-6 bg-purple-50 rounded-xl border border-purple-200">
                  <div className="text-2xl font-bold text-purple-800 mb-2">
                    {getConfidenceText(prediction.confidence_score)}
                  </div>
                  <div className="text-purple-700 font-medium">Confidence Level</div>
                  <div className="text-xs text-purple-600 mt-1">
                    {(prediction.confidence_score * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              <div className="border-t pt-6">
                <h3 className="font-semibold text-gray-800 mb-3">Analysis Details</h3>
                <div className="text-gray-700">
                  {prediction.explanation.split('\n').map((line, index) => (
                    <p key={index} className="mb-2">
                      {line.trim()}
                    </p>
                  ))}
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <p className="text-gray-500 text-sm italic">
                    This estimate is generated by a machine learning model and is for informational purposes only.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}