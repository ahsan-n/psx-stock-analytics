from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)  # e.g., "FCCL"
    name = Column(String, nullable=False)  # e.g., "Fauji Cement Company Limited"
    sector = Column(String, nullable=True)  # e.g., "Cement"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    financial_statements = relationship("FinancialStatement", back_populates="company")
    financial_metrics = relationship("FinancialMetric", back_populates="company")
    financial_ratios = relationship("FinancialRatio", back_populates="company")


class PeriodType(str, enum.Enum):
    QUARTERLY = "quarterly"
    ANNUAL = "annual"


class StatementType(str, enum.Enum):
    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    statement_type = Column(Enum(StatementType), nullable=False)
    period_type = Column(Enum(PeriodType), nullable=False)
    fiscal_year = Column(Integer, nullable=False)  # e.g., 2024
    quarter = Column(Integer, nullable=True)  # 1, 2, 3, 4 (null for annual)
    period_end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="financial_statements")
    metrics = relationship("FinancialMetric", back_populates="statement")


class FinancialMetric(Base):
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    statement_id = Column(Integer, ForeignKey("financial_statements.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    metric_name = Column(String, nullable=False)  # e.g., "revenue", "net_income"
    metric_label = Column(String, nullable=False)  # e.g., "Revenue", "Net Income"
    value = Column(Float, nullable=False)
    unit = Column(String, default="PKR")  # Currency or unit
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    statement = relationship("FinancialStatement", back_populates="metrics")
    company = relationship("Company", back_populates="financial_metrics")


class FinancialRatio(Base):
    __tablename__ = "financial_ratios"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    quarter = Column(Integer, nullable=True)
    period_type = Column(Enum(PeriodType), nullable=False)
    
    # Profitability Ratios
    gross_profit_margin = Column(Float, nullable=True)
    operating_profit_margin = Column(Float, nullable=True)
    net_profit_margin = Column(Float, nullable=True)
    return_on_assets = Column(Float, nullable=True)
    return_on_equity = Column(Float, nullable=True)
    
    # Liquidity Ratios
    current_ratio = Column(Float, nullable=True)
    quick_ratio = Column(Float, nullable=True)
    cash_ratio = Column(Float, nullable=True)
    
    # Leverage Ratios
    debt_to_equity = Column(Float, nullable=True)
    debt_to_assets = Column(Float, nullable=True)
    equity_multiplier = Column(Float, nullable=True)
    
    # Efficiency Ratios
    asset_turnover = Column(Float, nullable=True)
    inventory_turnover = Column(Float, nullable=True)
    receivables_turnover = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="financial_ratios")
