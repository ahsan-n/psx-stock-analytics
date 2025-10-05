import { useEffect, useState } from 'react'
import { api } from '../services/api'

interface FinancialTableProps {
  symbol: string
  statementType: 'income_statement' | 'balance_sheet' | 'cash_flow'
  periodType: 'quarterly' | 'annual'
}

interface FinancialMetric {
  metric_name: string
  metric_label: string
  value: number
  unit: string
}

interface FinancialStatement {
  id: number
  fiscal_year: number
  quarter: number | null
  period_end_date: string
  metrics: FinancialMetric[]
}

export function FinancialTable({ symbol, statementType, periodType }: FinancialTableProps) {
  const [statements, setStatements] = useState<FinancialStatement[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadStatements()
  }, [symbol, statementType, periodType])

  const loadStatements = async () => {
    setIsLoading(true)
    try {
      const data = await api.getFinancialStatements(symbol, {
        statement_type: statementType,
        period_type: periodType,
      })
      setStatements(data)
    } catch (error) {
      console.error('Failed to load statements:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatCurrency = (value: number) => {
    const billions = value / 1000000000
    return `${billions.toFixed(2)}B`
  }

  const formatPeriod = (statement: FinancialStatement) => {
    if (statement.quarter) {
      return `Q${statement.quarter} ${statement.fiscal_year}`
    }
    return `FY ${statement.fiscal_year}`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (statements.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No data available for this period
      </div>
    )
  }

  // Get unique metric labels
  const metricLabels = statements[0]?.metrics.map(m => ({
    name: m.metric_name,
    label: m.metric_label
  })) || []

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-gray-50 border-b-2 border-gray-200">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky left-0 bg-gray-50">
              Metric
            </th>
            {statements.slice(0, 5).reverse().map((statement) => (
              <th key={statement.id} className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap">
                {formatPeriod(statement)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {metricLabels.map((metricInfo) => {
            const values = statements.slice(0, 5).reverse().map(statement => {
              const metric = statement.metrics.find(m => m.metric_name === metricInfo.name)
              return metric?.value || 0
            })

            return (
              <tr key={metricInfo.name} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 sticky left-0 bg-white">
                  {metricInfo.label}
                </td>
                {values.map((value, index) => (
                  <td key={index} className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-700">
                    {value < 0 ? (
                      <span className="text-red-600">({formatCurrency(Math.abs(value))})</span>
                    ) : (
                      formatCurrency(value)
                    )}
                  </td>
                ))}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
