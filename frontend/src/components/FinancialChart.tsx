import { useEffect, useState } from 'react'
import { api } from '../services/api'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface FinancialChartProps {
  symbol: string
  statementType: 'income_statement' | 'balance_sheet' | 'cash_flow'
  periodType: 'quarterly' | 'annual'
  metrics: string[]
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
  metrics: FinancialMetric[]
}

const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

export function FinancialChart({ symbol, statementType, periodType, metrics }: FinancialChartProps) {
  const [chartData, setChartData] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadChartData()
  }, [symbol, statementType, periodType, metrics])

  const loadChartData = async () => {
    setIsLoading(true)
    try {
      const data = await api.getFinancialStatements(symbol, {
        statement_type: statementType,
        period_type: periodType,
      })

      // Transform data for chart
      const transformed = data
        .slice(0, 8)
        .reverse()
        .map((statement: FinancialStatement) => {
          const period = statement.quarter
            ? `Q${statement.quarter} ${statement.fiscal_year}`
            : `FY ${statement.fiscal_year}`

          const dataPoint: any = { period }

          metrics.forEach((metricName) => {
            const metric = statement.metrics.find(m => m.metric_name === metricName)
            if (metric) {
              dataPoint[metric.metric_label] = metric.value / 1000000000 // Convert to billions
            }
          })

          return dataPoint
        })

      setChartData(transformed)
    } catch (error) {
      console.error('Failed to load chart data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (chartData.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No chart data available
      </div>
    )
  }

  // Get metric labels from first data point
  const metricLabels = Object.keys(chartData[0]).filter(key => key !== 'period')

  return (
    <div className="bg-gray-50 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Trend Analysis</h3>
      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis 
            dataKey="period" 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#6b7280"
            style={{ fontSize: '12px' }}
            tickFormatter={(value) => `${value.toFixed(1)}B`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '12px',
            }}
            formatter={(value: any) => [`${value.toFixed(2)}B PKR`, '']}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="line"
          />
          {metricLabels.map((label, index) => (
            <Line
              key={label}
              type="monotone"
              dataKey={label}
              stroke={COLORS[index % COLORS.length]}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
