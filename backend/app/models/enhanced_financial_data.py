"""
Enhanced Financial Data Models for Phase 2
Supports detailed line items from actual financial statements
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Date, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base


class ReportType(str, enum.Enum):
    ANNUAL = "annual"
    Q1 = "q1"
    Q2 = "q2"
    Q3 = "q3"
    Q4 = "q4"


# ==================== BALANCE SHEET ====================

class BalanceSheet(Base):
    """Comprehensive Balance Sheet / Statement of Financial Position"""
    __tablename__ = "balance_sheets"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    report_type = Column(Enum(ReportType), nullable=False)
    period_end_date = Column(Date, nullable=False)
    currency = Column(String, default="PKR")
    unit = Column(String, default="thousands")  # thousands, millions
    
    # NON-CURRENT ASSETS
    property_plant_equipment = Column(Float, nullable=True)
    right_of_use_assets = Column(Float, nullable=True)
    intangible_assets = Column(Float, nullable=True)
    goodwill = Column(Float, nullable=True)
    long_term_investments = Column(Float, nullable=True)
    long_term_deposits = Column(Float, nullable=True)
    deferred_tax_assets = Column(Float, nullable=True)
    total_non_current_assets = Column(Float, nullable=True)
    
    # CURRENT ASSETS
    stores_spares = Column(Float, nullable=True)
    stock_in_trade = Column(Float, nullable=True)
    trade_debts = Column(Float, nullable=True)
    advances = Column(Float, nullable=True)
    short_term_prepayments = Column(Float, nullable=True)
    sales_tax_refundable = Column(Float, nullable=True)
    advance_tax = Column(Float, nullable=True)
    other_receivables = Column(Float, nullable=True)
    short_term_investments = Column(Float, nullable=True)
    cash_and_bank_balances = Column(Float, nullable=True)
    total_current_assets = Column(Float, nullable=True)
    
    total_assets = Column(Float, nullable=True)
    
    # EQUITY
    share_capital = Column(Float, nullable=True)
    share_premium = Column(Float, nullable=True)
    reserves = Column(Float, nullable=True)
    retained_earnings = Column(Float, nullable=True)
    total_equity = Column(Float, nullable=True)
    
    # NON-CURRENT LIABILITIES
    long_term_loans = Column(Float, nullable=True)
    long_term_lease_liabilities = Column(Float, nullable=True)
    employee_benefits_non_current = Column(Float, nullable=True)
    deferred_tax_liabilities = Column(Float, nullable=True)
    deferred_government_grant = Column(Float, nullable=True)
    total_non_current_liabilities = Column(Float, nullable=True)
    
    # CURRENT LIABILITIES
    short_term_borrowings = Column(Float, nullable=True)
    current_portion_long_term_loans = Column(Float, nullable=True)
    current_portion_lease_liabilities = Column(Float, nullable=True)
    trade_and_other_payables = Column(Float, nullable=True)
    accrued_liabilities = Column(Float, nullable=True)
    contract_liabilities = Column(Float, nullable=True)
    employee_benefits_current = Column(Float, nullable=True)
    provision_for_taxation = Column(Float, nullable=True)
    unclaimed_dividend = Column(Float, nullable=True)
    security_deposits_payable = Column(Float, nullable=True)
    total_current_liabilities = Column(Float, nullable=True)
    
    total_liabilities = Column(Float, nullable=True)
    total_equity_and_liabilities = Column(Float, nullable=True)
    
    # METADATA
    created_at = Column(DateTime, default=datetime.utcnow)
    extracted_from_pdf = Column(Boolean, default=False)
    extraction_confidence = Column(Float, nullable=True)  # 0-1 score
    notes = Column(Text, nullable=True)
    
    # Relationships
    company = relationship("Company")


# ==================== INCOME STATEMENT ====================

class IncomeStatement(Base):
    """Comprehensive Income Statement / Statement of Profit or Loss"""
    __tablename__ = "income_statements"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    report_type = Column(Enum(ReportType), nullable=False)
    period_end_date = Column(Date, nullable=False)
    currency = Column(String, default="PKR")
    unit = Column(String, default="thousands")
    
    # REVENUE AND GROSS PROFIT
    revenue = Column(Float, nullable=True)
    cost_of_sales = Column(Float, nullable=True)
    gross_profit = Column(Float, nullable=True)
    
    # OPERATING EXPENSES
    distribution_costs = Column(Float, nullable=True)
    administrative_expenses = Column(Float, nullable=True)
    other_operating_expenses = Column(Float, nullable=True)
    total_operating_expenses = Column(Float, nullable=True)
    
    # OPERATING PROFIT
    operating_profit = Column(Float, nullable=True)
    
    # OTHER INCOME AND EXPENSES
    other_income = Column(Float, nullable=True)
    finance_costs = Column(Float, nullable=True)
    share_of_profit_from_associates = Column(Float, nullable=True)
    
    # PROFIT BEFORE TAX
    profit_before_tax = Column(Float, nullable=True)
    
    # TAXATION
    current_tax = Column(Float, nullable=True)
    deferred_tax = Column(Float, nullable=True)
    total_taxation = Column(Float, nullable=True)
    
    # NET PROFIT
    profit_after_tax = Column(Float, nullable=True)
    
    # OTHER COMPREHENSIVE INCOME
    other_comprehensive_income = Column(Float, nullable=True)
    total_comprehensive_income = Column(Float, nullable=True)
    
    # EARNINGS PER SHARE
    basic_eps = Column(Float, nullable=True)
    diluted_eps = Column(Float, nullable=True)
    
    # ADDITIONAL METRICS
    ebitda = Column(Float, nullable=True)
    depreciation_amortization = Column(Float, nullable=True)
    
    # METADATA
    created_at = Column(DateTime, default=datetime.utcnow)
    extracted_from_pdf = Column(Boolean, default=False)
    extraction_confidence = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    company = relationship("Company")


# ==================== CASH FLOW STATEMENT ====================

class CashFlowStatement(Base):
    """Comprehensive Cash Flow Statement"""
    __tablename__ = "cash_flow_statements"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    report_type = Column(Enum(ReportType), nullable=False)
    period_end_date = Column(Date, nullable=False)
    currency = Column(String, default="PKR")
    unit = Column(String, default="thousands")
    
    # OPERATING ACTIVITIES
    cash_from_customers = Column(Float, nullable=True)
    cash_paid_to_vendors_employees = Column(Float, nullable=True)
    cash_generated_from_operations = Column(Float, nullable=True)
    finance_costs_paid = Column(Float, nullable=True)
    income_tax_paid = Column(Float, nullable=True)
    employee_benefits_paid = Column(Float, nullable=True)
    net_cash_from_operating_activities = Column(Float, nullable=True)
    
    # INVESTING ACTIVITIES
    purchase_of_ppe = Column(Float, nullable=True)
    proceeds_from_sale_of_ppe = Column(Float, nullable=True)
    purchase_of_investments = Column(Float, nullable=True)
    proceeds_from_sale_of_investments = Column(Float, nullable=True)
    interest_received = Column(Float, nullable=True)
    dividend_received = Column(Float, nullable=True)
    net_cash_used_in_investing_activities = Column(Float, nullable=True)
    
    # FINANCING ACTIVITIES
    proceeds_from_long_term_loans = Column(Float, nullable=True)
    repayment_of_long_term_loans = Column(Float, nullable=True)
    proceeds_from_short_term_borrowings = Column(Float, nullable=True)
    repayment_of_short_term_borrowings = Column(Float, nullable=True)
    dividend_paid = Column(Float, nullable=True)
    lease_payments = Column(Float, nullable=True)
    net_cash_from_financing_activities = Column(Float, nullable=True)
    
    # NET CHANGE IN CASH
    net_increase_decrease_in_cash = Column(Float, nullable=True)
    cash_at_beginning_of_period = Column(Float, nullable=True)
    cash_at_end_of_period = Column(Float, nullable=True)
    
    # METADATA
    created_at = Column(DateTime, default=datetime.utcnow)
    extracted_from_pdf = Column(Boolean, default=False)
    extraction_confidence = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    company = relationship("Company")


# ==================== ENHANCED RATIOS ====================

class EnhancedFinancialRatios(Base):
    """Enhanced Financial Ratios with more comprehensive metrics"""
    __tablename__ = "enhanced_financial_ratios"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    fiscal_year = Column(Integer, nullable=False)
    report_type = Column(Enum(ReportType), nullable=False)
    
    # PROFITABILITY RATIOS
    gross_profit_margin = Column(Float, nullable=True)
    operating_profit_margin = Column(Float, nullable=True)
    net_profit_margin = Column(Float, nullable=True)
    return_on_assets = Column(Float, nullable=True)
    return_on_equity = Column(Float, nullable=True)
    return_on_capital_employed = Column(Float, nullable=True)
    ebitda_margin = Column(Float, nullable=True)
    
    # LIQUIDITY RATIOS
    current_ratio = Column(Float, nullable=True)
    quick_ratio = Column(Float, nullable=True)
    cash_ratio = Column(Float, nullable=True)
    working_capital = Column(Float, nullable=True)
    
    # LEVERAGE RATIOS
    debt_to_equity = Column(Float, nullable=True)
    debt_to_assets = Column(Float, nullable=True)
    equity_multiplier = Column(Float, nullable=True)
    interest_coverage_ratio = Column(Float, nullable=True)
    debt_service_coverage_ratio = Column(Float, nullable=True)
    
    # EFFICIENCY RATIOS
    asset_turnover = Column(Float, nullable=True)
    inventory_turnover = Column(Float, nullable=True)
    receivables_turnover = Column(Float, nullable=True)
    payables_turnover = Column(Float, nullable=True)
    days_inventory_outstanding = Column(Float, nullable=True)
    days_sales_outstanding = Column(Float, nullable=True)
    days_payables_outstanding = Column(Float, nullable=True)
    cash_conversion_cycle = Column(Float, nullable=True)
    
    # VALUATION RATIOS
    earnings_per_share = Column(Float, nullable=True)
    price_to_earnings = Column(Float, nullable=True)
    price_to_book = Column(Float, nullable=True)
    dividend_per_share = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    dividend_payout_ratio = Column(Float, nullable=True)
    
    # METADATA
    created_at = Column(DateTime, default=datetime.utcnow)
    calculated_from_extracted_data = Column(Boolean, default=False)
    
    # Relationships
    company = relationship("Company")


# ==================== PDF EXTRACTION LOG ====================

class PDFExtractionLog(Base):
    """Log of PDF extraction attempts and results"""
    __tablename__ = "pdf_extraction_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    pdf_filename = Column(String, nullable=False)
    fiscal_year = Column(Integer, nullable=True)
    report_type = Column(String, nullable=True)
    
    extraction_date = Column(DateTime, default=datetime.utcnow)
    extraction_status = Column(String, nullable=False)  # success, partial, failed
    pages_processed = Column(Integer, nullable=True)
    statements_found = Column(Integer, nullable=True)
    
    error_message = Column(Text, nullable=True)
    extraction_method = Column(String, nullable=True)  # pymupdf, pdfplumber, camelot
    processing_time_seconds = Column(Float, nullable=True)
    
    # Relationships
    company = relationship("Company")
