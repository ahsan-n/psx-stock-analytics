from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.financial_data import (
    Company, FinancialStatement, FinancialMetric, FinancialRatio,
    PeriodType, StatementType
)
from app.schemas.financial import (
    CompanyResponse,
    FinancialStatementResponse,
    FinancialRatioResponse
)

router = APIRouter()


@router.get("/companies", response_model=List[CompanyResponse])
async def get_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all companies"""
    companies = db.query(Company).all()
    return companies


@router.get("/companies/{symbol}", response_model=CompanyResponse)
async def get_company(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get company by symbol"""
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/statements/{symbol}", response_model=List[FinancialStatementResponse])
async def get_financial_statements(
    symbol: str,
    statement_type: Optional[StatementType] = Query(None),
    period_type: Optional[PeriodType] = Query(None),
    fiscal_year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get financial statements for a company"""
    # Get company
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Build query
    query = db.query(FinancialStatement).filter(FinancialStatement.company_id == company.id)
    
    if statement_type:
        query = query.filter(FinancialStatement.statement_type == statement_type)
    if period_type:
        query = query.filter(FinancialStatement.period_type == period_type)
    if fiscal_year:
        query = query.filter(FinancialStatement.fiscal_year == fiscal_year)
    
    statements = query.order_by(
        FinancialStatement.fiscal_year.desc(),
        FinancialStatement.quarter.desc()
    ).all()
    
    return statements


@router.get("/ratios/{symbol}", response_model=List[FinancialRatioResponse])
async def get_financial_ratios(
    symbol: str,
    period_type: Optional[PeriodType] = Query(None),
    fiscal_year: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get financial ratios for a company"""
    # Get company
    company = db.query(Company).filter(Company.symbol == symbol.upper()).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Build query
    query = db.query(FinancialRatio).filter(FinancialRatio.company_id == company.id)
    
    if period_type:
        query = query.filter(FinancialRatio.period_type == period_type)
    if fiscal_year:
        query = query.filter(FinancialRatio.fiscal_year == fiscal_year)
    
    ratios = query.order_by(
        FinancialRatio.fiscal_year.desc(),
        FinancialRatio.quarter.desc()
    ).all()
    
    return ratios
