'use client'

import { useState, useEffect } from 'react'
import dynamic from 'next/dynamic'

// Dynamically import components to avoid SSR issues
const Dashboard = dynamic(() => import('../components/Dashboard'), { 
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-screen bg-gray-50">Loading dashboard...</div>
})

export default function Home() {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate loading
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h2 className="text-2xl font-semibold text-gray-700">Loading SynTeCX Hub</h2>
          <p className="text-gray-500 mt-2">Preparing your AI-powered insights...</p>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Dashboard />
    </main>
  )
}