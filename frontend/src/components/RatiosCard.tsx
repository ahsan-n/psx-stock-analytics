import { useEffect, useState } from 'react'
import { api } from '../services/api'
import { TrendingUp, TrendingDown } from 'lucide-react'

interface RatiosCardProps {
  symbol: string
  periodType: 'quarterly' | 'annual'
}

interface FinancialRatio {
  fiscal_year: number
  quarter: number | null
  period_type: string
  gross_profit_margin: number
  operating_profit_margin: number
  net_profit_margin: number
  return_on_assets: number
  return_on_equity: number
  current_ratio: number
  quick_ratio: number
  cash_ratio: number
  debt_to_equity: number
  debt_to_assets: number
  equity_multiplier: number
  asset_turnover: number
  inventory_turnover: number
  receivables_turnover: number
}

export function RatiosCard({ symbol, periodType }: RatiosCardProps) {
  const [ratios, setRatios] = useState<FinancialRatio[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadRatios()
  }, [symbol, periodType])

  const loadRatios = async () => {
    setIsLoading(true)
    try {
      const data = await api.getFinancialRatios(symbol, { period_type: periodType })
      setRatios(data)
    } catch (error) {
      console.error('Failed to load ratios:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (ratios.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No ratio data available
      </div>
    )
  }

  const latestRatio = ratios[0]
  const previousRatio = ratios[1]

  const formatRatio = (value: number | null, suffix = '%') => {
    if (value === null) return 'N/A'
    return `${value.toFixed(2)}${suffix}`
  }

  const getTrend = (current: number | null, previous: number | null) => {
    if (!current || !previous) return null
    return current > previous ? 'up' : 'down'
  }

  const RatioItem = ({ 
    label, 
    value, 
    previousValue,
    suffix = '%',
    higherIsBetter = true 
  }: { 
    label: string
    value: number | null
    previousValue: number | null
    suffix?: string
    higherIsBetter?: boolean
  }) => {
    const trend = getTrend(value, previousValue)
    const isPositive = trend === 'up' ? higherIsBetter : !higherIsBetter

    return (
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-start justify-between mb-2">
          <span className="text-sm text-gray-600">{label}</span>
          {trend && (
            <span className={`flex items-center text-xs ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {trend === 'up' ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
            </span>
          )}
        </div>
        <div className="text-2xl font-bold text-gray-900">
          {formatRatio(value, suffix)}
        </div>
        {previousValue && (
          <div className="text-xs text-gray-500 mt-1">
            Previous: {formatRatio(previousValue, suffix)}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Profitability Ratios */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Profitability Ratios</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <RatioItem 
            label="Gross Profit Margin" 
            value={latestRatio.gross_profit_margin}
            previousValue={previousRatio?.gross_profit_margin}
          />
          <RatioItem 
            label="Operating Profit Margin" 
            value={latestRatio.operating_profit_margin}
            previousValue={previousRatio?.operating_profit_margin}
          />
          <RatioItem 
            label="Net Profit Margin" 
            value={latestRatio.net_profit_margin}
            previousValue={previousRatio?.net_profit_margin}
          />
          <RatioItem 
            label="Return on Assets" 
            value={latestRatio.return_on_assets}
            previousValue={previousRatio?.return_on_assets}
          />
          <RatioItem 
            label="Return on Equity" 
            value={latestRatio.return_on_equity}
            previousValue={previousRatio?.return_on_equity}
          />
        </div>
      </div>

      {/* Liquidity Ratios */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Liquidity Ratios</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <RatioItem 
            label="Current Ratio" 
            value={latestRatio.current_ratio}
            previousValue={previousRatio?.current_ratio}
            suffix="x"
          />
          <RatioItem 
            label="Quick Ratio" 
            value={latestRatio.quick_ratio}
            previousValue={previousRatio?.quick_ratio}
            suffix="x"
          />
          <RatioItem 
            label="Cash Ratio" 
            value={latestRatio.cash_ratio}
            previousValue={previousRatio?.cash_ratio}
            suffix="x"
          />
        </div>
      </div>

      {/* Leverage Ratios */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Leverage Ratios</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <RatioItem 
            label="Debt to Equity" 
            value={latestRatio.debt_to_equity}
            previousValue={previousRatio?.debt_to_equity}
            suffix="x"
            higherIsBetter={false}
          />
          <RatioItem 
            label="Debt to Assets" 
            value={latestRatio.debt_to_assets}
            previousValue={previousRatio?.debt_to_assets}
            suffix="x"
            higherIsBetter={false}
          />
          <RatioItem 
            label="Equity Multiplier" 
            value={latestRatio.equity_multiplier}
            previousValue={previousRatio?.equity_multiplier}
            suffix="x"
          />
        </div>
      </div>

      {/* Efficiency Ratios */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Efficiency Ratios</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <RatioItem 
            label="Asset Turnover" 
            value={latestRatio.asset_turnover}
            previousValue={previousRatio?.asset_turnover}
            suffix="x"
          />
          <RatioItem 
            label="Inventory Turnover" 
            value={latestRatio.inventory_turnover}
            previousValue={previousRatio?.inventory_turnover}
            suffix="x"
          />
          <RatioItem 
            label="Receivables Turnover" 
            value={latestRatio.receivables_turnover}
            previousValue={previousRatio?.receivables_turnover}
            suffix="x"
          />
        </div>
      </div>
    </div>
  )
}
