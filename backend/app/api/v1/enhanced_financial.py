"""
Enhanced Financial Data API
Uses the new enhanced models with real parsed data
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.financial_data import Company
from app.models.enhanced_financial_data import (
    Report, BalanceSheet, IncomeStatement, CashFlowStatement
)
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Response Models
class ReportResponse(BaseModel):
    id: int
    company_id: int
    report_type: str
    quarter: Optional[str]
    fiscal_year: Optional[str]
    report_date: datetime
    pdf_path: Optional[str]
    is_audited: bool

class BalanceSheetResponse(BaseModel):
    id: int
    report_id: int
    total_assets: Optional[float]
    total_liabilities: Optional[float]
    total_equity: Optional[float]
    property_plant_equipment: Optional[float]
    cash_and_bank_balances: Optional[float]
    stock_in_trade: Optional[float]
    trade_debts: Optional[float]
    long_term_loans: Optional[float]
    short_term_borrowings: Optional[float]
    trade_and_other_payables: Optional[float]
    share_capital: Optional[float]
    retained_earnings: Optional[float]
    
    class Config:
        from_attributes = True

class IncomeStatementResponse(BaseModel):
    id: int
    report_id: int
    revenue: Optional[float]
    cost_of_sales: Optional[float]
    gross_profit: Optional[float]
    distribution_costs: Optional[float]
    administrative_expenses: Optional[float]
    operating_profit: Optional[float]
    finance_costs: Optional[float]
    profit_before_tax: Optional[float]
    total_taxation: Optional[float]
    profit_after_tax: Optional[float]
    
    class Config:
        from_attributes = True

class CashFlowResponse(BaseModel):
    id: int
    report_id: int
    net_cash_from_operating_activities: Optional[float]
    net_cash_used_in_investing_activities: Optional[float]
    net_cash_from_financing_activities: Optional[float]
    
    class Config:
        from_attributes = True

class CompanyFinancialSummary(BaseModel):
    company: dict
    reports_count: int
    latest_balance_sheet: Optional[BalanceSheetResponse]
    latest_income_statement: Optional[IncomeStatementResponse]
    latest_cash_flow: Optional[CashFlowResponse]

@router.get("/companies/{symbol}/summary", response_model=CompanyFinancialSummary)
async def get_company_financial_summary(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive financial summary for a company"""
    # Get company
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Get reports count
    reports_count = db.query(Report).filter(Report.company_id == company.id).count()
    
    # Get latest financial statements
    latest_report = db.query(Report).filter(
        Report.company_id == company.id
    ).order_by(Report.created_at.desc()).first()
    
    latest_balance_sheet = None
    latest_income_statement = None
    latest_cash_flow = None
    
    if latest_report:
        latest_balance_sheet = db.query(BalanceSheet).filter(
            BalanceSheet.report_id == latest_report.id
        ).first()
        
        latest_income_statement = db.query(IncomeStatement).filter(
            IncomeStatement.report_id == latest_report.id
        ).first()
        
        latest_cash_flow = db.query(CashFlowStatement).filter(
            CashFlowStatement.report_id == latest_report.id
        ).first()
    
    return CompanyFinancialSummary(
        company={
            "id": company.id,
            "symbol": company.symbol,
            "name": company.name,
            "sector": company.sector,
            "industry": getattr(company, 'industry', None)
        },
        reports_count=reports_count,
        latest_balance_sheet=latest_balance_sheet,
        latest_income_statement=latest_income_statement,
        latest_cash_flow=latest_cash_flow
    )

@router.get("/companies/{symbol}/reports", response_model=List[ReportResponse])
async def get_company_reports(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all reports for a company"""
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    reports = db.query(Report).filter(
        Report.company_id == company.id
    ).order_by(Report.created_at.desc()).all()
    
    return reports

@router.get("/companies/{symbol}/balance-sheets", response_model=List[BalanceSheetResponse])
async def get_company_balance_sheets(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all balance sheets for a company"""
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    balance_sheets = db.query(BalanceSheet).join(Report).filter(
        Report.company_id == company.id
    ).order_by(Report.created_at.desc()).all()
    
    return balance_sheets

@router.get("/companies/{symbol}/income-statements", response_model=List[IncomeStatementResponse])
async def get_company_income_statements(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all income statements for a company"""
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    income_statements = db.query(IncomeStatement).join(Report).filter(
        Report.company_id == company.id
    ).order_by(Report.created_at.desc()).all()
    
    return income_statements

@router.get("/companies/{symbol}/cash-flows", response_model=List[CashFlowResponse])
async def get_company_cash_flows(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all cash flow statements for a company"""
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    cash_flows = db.query(CashFlowStatement).join(Report).filter(
        Report.company_id == company.id
    ).order_by(Report.created_at.desc()).all()
    
    return cash_flows
