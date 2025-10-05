import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Layout } from '../components/Layout'
import { api } from '../services/api'
import { Building2, TrendingUp, ArrowRight } from 'lucide-react'

interface Company {
  id: number
  symbol: string
  name: string
  sector: string
}

export default function HomePage() {
  const [companies, setCompanies] = useState<Company[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadCompanies()
  }, [])

  const loadCompanies = async () => {
    try {
      const data = await api.getCompanies()
      setCompanies(data)
    } catch (error) {
      console.error('Failed to load companies:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center p-2 bg-primary-100 rounded-full mb-4">
            <TrendingUp className="h-12 w-12 text-primary-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            PSX Stock Analytics Platform
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Analyze Pakistan Stock Exchange companies with AI-powered insights, 
            comprehensive financial data, and interactive dashboards.
          </p>
        </div>

        {/* Companies Grid */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Available Companies</h2>
          
          {companies.length === 0 ? (
            <div className="bg-white rounded-xl shadow-sm p-12 text-center">
              <Building2 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No companies yet</h3>
              <p className="text-gray-600">
                Run <code className="px-2 py-1 bg-gray-100 rounded">make seed</code> to populate the database
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {companies.map((company) => (
                <button
                  key={company.id}
                  onClick={() => navigate(`/${company.symbol}`)}
                  className="bg-white rounded-xl shadow-sm hover:shadow-md transition p-6 text-left group"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="bg-primary-100 p-3 rounded-lg group-hover:bg-primary-200 transition">
                      <Building2 className="h-6 w-6 text-primary-600" />
                    </div>
                    <ArrowRight className="h-5 w-5 text-gray-400 group-hover:text-primary-600 transition" />
                  </div>
                  
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {company.symbol}
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    {company.name}
                  </p>
                  {company.sector && (
                    <span className="inline-block px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                      {company.sector}
                    </span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Financial Data</h3>
            <p className="text-gray-600 text-sm">
              Access comprehensive income statements, balance sheets, and cash flow data
            </p>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Building2 className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Key Ratios</h3>
            <p className="text-gray-600 text-sm">
              Analyze profitability, liquidity, leverage, and efficiency metrics
            </p>
          </div>
          
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Visual Insights</h3>
            <p className="text-gray-600 text-sm">
              Interactive charts and graphs to track trends over time
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}
