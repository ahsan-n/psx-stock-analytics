from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.financial import CompanyResponse

router = APIRouter()


@router.get("/", response_model=List[CompanyResponse])
async def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available company reports"""
    from app.models.financial_data import Company
    companies = db.query(Company).all()
    return companies
