"""
PDF Processing API Endpoints
Upload and process financial reports
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.financial_data_service import FinancialDataService
from pydantic import BaseModel

router = APIRouter()


class ProcessPDFRequest(BaseModel):
    """Request to process an existing PDF file"""
    pdf_path: str


class ProcessPDFResponse(BaseModel):
    """Response after processing PDF"""
    success: bool
    company_id: int | None = None
    company_symbol: str | None = None
    report_id: int | None = None
    balance_sheet_id: int | None = None
    income_statement_id: int | None = None
    cash_flow_id: int | None = None
    message: str
    error: str | None = None


class BulkProcessRequest(BaseModel):
    """Request to process multiple PDFs"""
    pdf_directory: str
    pattern: str = "*.pdf"  # Glob pattern


class BulkProcessResponse(BaseModel):
    """Response after bulk processing"""
    total_files: int
    successful: int
    failed: int
    results: List[ProcessPDFResponse]


@router.post("/process-pdf", response_model=ProcessPDFResponse)
def process_pdf_report(
    request: ProcessPDFRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process a PDF financial report and save to database
    
    - Extracts financial statements
    - Validates data
    - Persists to database
    - Returns summary of saved data
    """
    # Validate file exists
    if not os.path.exists(request.pdf_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PDF file not found: {request.pdf_path}"
        )
    
    # Process the PDF
    service = FinancialDataService(db)
    result = service.process_pdf_report(
        pdf_path=request.pdf_path,
        uploaded_by_user_id=current_user.id
    )
    
    return ProcessPDFResponse(**result)


@router.post("/bulk-process", response_model=BulkProcessResponse)
def bulk_process_pdfs(
    request: BulkProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Process multiple PDF reports from a directory
    
    - Scans directory for PDFs matching pattern
    - Processes each PDF
    - Returns summary of all operations
    """
    # Validate directory exists
    directory = Path(request.pdf_directory)
    if not directory.exists() or not directory.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Directory not found: {request.pdf_directory}"
        )
    
    # Find all matching PDFs
    pdf_files = list(directory.glob(request.pattern))
    
    if not pdf_files:
        return BulkProcessResponse(
            total_files=0,
            successful=0,
            failed=0,
            results=[],
            message=f"No PDF files found matching pattern: {request.pattern}"
        )
    
    # Process each PDF
    service = FinancialDataService(db)
    results = []
    successful = 0
    failed = 0
    
    for pdf_file in pdf_files:
        try:
            result = service.process_pdf_report(
                pdf_path=str(pdf_file),
                uploaded_by_user_id=current_user.id
            )
            results.append(ProcessPDFResponse(**result))
            
            if result['success']:
                successful += 1
            else:
                failed += 1
                
        except Exception as e:
            results.append(ProcessPDFResponse(
                success=False,
                message=f"Failed to process {pdf_file.name}",
                error=str(e)
            ))
            failed += 1
    
    return BulkProcessResponse(
        total_files=len(pdf_files),
        successful=successful,
        failed=failed,
        results=results
    )


@router.post("/upload-and-process")
async def upload_and_process_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a PDF file and process it immediately
    
    - Accepts PDF upload
    - Saves to temporary location
    - Processes and extracts data
    - Returns processed results
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads/reports")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    file_path = upload_dir / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )
    
    # Process the PDF
    service = FinancialDataService(db)
    result = service.process_pdf_report(
        pdf_path=str(file_path),
        uploaded_by_user_id=current_user.id
    )
    
    return ProcessPDFResponse(**result)


@router.get("/processing-status/{report_id}")
def get_processing_status(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the processing status and results for a report
    """
    from app.models.enhanced_financial_data import Report, PDFExtractionLog
    
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Get extraction log
    extraction_log = db.query(PDFExtractionLog).filter(
        PDFExtractionLog.report_id == report_id
    ).order_by(PDFExtractionLog.extracted_at.desc()).first()
    
    return {
        "report_id": report.id,
        "company_id": report.company_id,
        "report_type": report.report_type,
        "fiscal_year": report.fiscal_year,
        "quarter": report.quarter,
        "has_balance_sheet": report.balance_sheets.count() > 0 if hasattr(report, 'balance_sheets') else False,
        "has_income_statement": report.income_statements.count() > 0 if hasattr(report, 'income_statements') else False,
        "has_cash_flow": report.cash_flows.count() > 0 if hasattr(report, 'cash_flows') else False,
        "extraction_success": extraction_log.extraction_success if extraction_log else None,
        "extracted_at": extraction_log.extracted_at if extraction_log else None,
        "error_message": extraction_log.error_message if extraction_log else None
    }
