from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
from app.models.financial_data import PeriodType, StatementType


class CompanyBase(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FinancialMetricResponse(BaseModel):
    metric_name: str
    metric_label: str
    value: float
    unit: str

    class Config:
        from_attributes = True


class FinancialStatementResponse(BaseModel):
    id: int
    statement_type: StatementType
    period_type: PeriodType
    fiscal_year: int
    quarter: Optional[int]
    period_end_date: date
    metrics: List[FinancialMetricResponse]

    class Config:
        from_attributes = True


class FinancialRatioResponse(BaseModel):
    fiscal_year: int
    quarter: Optional[int]
    period_type: PeriodType
    
    # Profitability
    gross_profit_margin: Optional[float]
    operating_profit_margin: Optional[float]
    net_profit_margin: Optional[float]
    return_on_assets: Optional[float]
    return_on_equity: Optional[float]
    
    # Liquidity
    current_ratio: Optional[float]
    quick_ratio: Optional[float]
    cash_ratio: Optional[float]
    
    # Leverage
    debt_to_equity: Optional[float]
    debt_to_assets: Optional[float]
    equity_multiplier: Optional[float]
    
    # Efficiency
    asset_turnover: Optional[float]
    inventory_turnover: Optional[float]
    receivables_turnover: Optional[float]

    class Config:
        from_attributes = True


class FinancialDataRequest(BaseModel):
    symbol: str
    fiscal_year: Optional[int] = None
    period_type: Optional[PeriodType] = None
    statement_type: Optional[StatementType] = None
