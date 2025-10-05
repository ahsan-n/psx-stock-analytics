import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Layout } from '../components/Layout'
import { api } from '../services/api'
import { 
  TrendingUp, 
  TrendingDown, 
  FileText, 
  DollarSign, 
  PieChart 
} from 'lucide-react'
import { FinancialTable } from '../components/FinancialTable'
import { FinancialChart } from '../components/FinancialChart'
import { RatiosCard } from '../components/RatiosCard'

type PeriodType = 'quarterly' | 'annual'
type StatementType = 'income_statement' | 'balance_sheet' | 'cash_flow'

interface Company {
  id: number
  symbol: string
  name: string
  sector: string
}

export default function CompanyPage() {
  const { symbol } = useParams<{ symbol: string }>()
  const [company, setCompany] = useState<Company | null>(null)
  const [periodType, setPeriodType] = useState<PeriodType>('annual')
  const [activeTab, setActiveTab] = useState<StatementType | 'ratios'>('income_statement')
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (symbol) {
      loadCompany()
    }
  }, [symbol])

  const loadCompany = async () => {
    try {
      const data = await api.getCompany(symbol!.toUpperCase())
      setCompany(data)
    } catch (error) {
      console.error('Failed to load company:', error)
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

  if (!company) {
    return (
      <Layout>
        <div className="text-center py-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Company not found</h2>
          <p className="text-gray-600">The requested company could not be found.</p>
        </div>
      </Layout>
    )
  }

  const tabs = [
    { id: 'income_statement', label: 'Income Statement', icon: DollarSign },
    { id: 'balance_sheet', label: 'Balance Sheet', icon: FileText },
    { id: 'cash_flow', label: 'Cash Flow', icon: TrendingUp },
    { id: 'ratios', label: 'Ratios', icon: PieChart },
  ]

  return (
    <Layout title={company.symbol}>
      <div className="space-y-6">
        {/* Company Header */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{company.name}</h1>
              <div className="flex items-center space-x-4">
                <span className="text-lg text-gray-600">{company.symbol}</span>
                {company.sector && (
                  <span className="px-3 py-1 bg-primary-100 text-primary-700 text-sm font-medium rounded-full">
                    {company.sector}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Period Toggle */}
        <div className="bg-white rounded-xl shadow-sm p-4">
          <div className="flex items-center justify-between">
            <div className="flex space-x-2">
              <button
                onClick={() => setPeriodType('annual')}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  periodType === 'annual'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Annual
              </button>
              <button
                onClick={() => setPeriodType('quarterly')}
                className={`px-6 py-2 rounded-lg font-medium transition ${
                  periodType === 'quarterly'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Quarterly
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm">
          <div className="border-b border-gray-200">
            <div className="flex space-x-1 p-4">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition ${
                      activeTab === tab.id
                        ? 'bg-primary-50 text-primary-700 border border-primary-200'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    <span>{tab.label}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'income_statement' && (
              <div className="space-y-6">
                <FinancialTable 
                  symbol={company.symbol} 
                  statementType="income_statement" 
                  periodType={periodType}
                />
                <FinancialChart 
                  symbol={company.symbol} 
                  statementType="income_statement" 
                  periodType={periodType}
                  metrics={['revenue', 'gross_profit', 'net_income']}
                />
              </div>
            )}

            {activeTab === 'balance_sheet' && (
              <div className="space-y-6">
                <FinancialTable 
                  symbol={company.symbol} 
                  statementType="balance_sheet" 
                  periodType={periodType}
                />
                <FinancialChart 
                  symbol={company.symbol} 
                  statementType="balance_sheet" 
                  periodType={periodType}
                  metrics={['total_assets', 'total_liabilities', 'total_equity']}
                />
              </div>
            )}

            {activeTab === 'cash_flow' && (
              <div className="space-y-6">
                <FinancialTable 
                  symbol={company.symbol} 
                  statementType="cash_flow" 
                  periodType={periodType}
                />
                <FinancialChart 
                  symbol={company.symbol} 
                  statementType="cash_flow" 
                  periodType={periodType}
                  metrics={['operating_cash_flow', 'investing_cash_flow', 'financing_cash_flow']}
                />
              </div>
            )}

            {activeTab === 'ratios' && (
              <RatiosCard symbol={company.symbol} periodType={periodType} />
            )}
          </div>
        </div>
      </div>
    </Layout>
  )
}
