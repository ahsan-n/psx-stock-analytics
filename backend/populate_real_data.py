"""
Populate database with REAL financial data from PDFs
This replaces the mock data with actual extracted data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.services.financial_data_service import FinancialDataService
from app.models.user import User
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_admin_user(db):
    """Create or get admin user for data population"""
    admin = db.query(User).filter(User.email == "admin@stockai.com").first()
    
    if not admin:
        admin = User(
            email="admin@stockai.com",
            full_name="System Admin",
            hashed_password=get_password_hash("admin123")
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info("✓ Created admin user")
    else:
        logger.info("✓ Admin user exists")
    
    return admin


def populate_fccl_data(db, admin_user_id):
    """Populate FCCL data from all reports"""
    logger.info("\n" + "="*80)
    logger.info("POPULATING FCCL DATA")
    logger.info("="*80)
    
    service = FinancialDataService(db)
    # Paths inside container - reports are mounted as volume
    reports_dir = Path("/app/reports/FCCL")
    
    # Process reports from newest to oldest for better demo
    years = ["2023-24", "2022-23", "2021-22", "2020-21"]
    reports_to_process = []
    
    for year in years:
        year_dir = reports_dir / year
        if year_dir.exists():
            # Get quarterly reports
            for quarter in ["Q1", "Q2", "Q3"]:
                pdf_path = year_dir / f"FCCL_{year}_{quarter}.pdf"
                if pdf_path.exists():
                    reports_to_process.append(str(pdf_path))
            
            # Get annual report
            annual_path = year_dir / f"FCCL_Annual_{year}.pdf"
            if annual_path.exists():
                reports_to_process.append(str(annual_path))
    
    logger.info(f"Found {len(reports_to_process)} FCCL reports to process\n")
    
    successful = 0
    failed = 0
    
    for i, pdf_path in enumerate(reports_to_process, 1):
        pdf_name = Path(pdf_path).name
        logger.info(f"[{i}/{len(reports_to_process)}] Processing: {pdf_name}")
        
        try:
            result = service.process_pdf_report(
                pdf_path=pdf_path,
                uploaded_by_user_id=admin_user_id
            )
            
            if result['success']:
                logger.info(f"  ✓ SUCCESS - Report ID: {result['report_id']}")
                logger.info(f"    Balance Sheet: {result.get('balance_sheet_id', 'N/A')}")
                logger.info(f"    Income Statement: {result.get('income_statement_id', 'N/A')}")
                logger.info(f"    Cash Flow: {result.get('cash_flow_id', 'N/A')}")
                successful += 1
            else:
                logger.error(f"  ✗ FAILED - {result.get('error', 'Unknown error')}")
                failed += 1
        except Exception as e:
            logger.error(f"  ✗ ERROR - {str(e)}")
            failed += 1
        
        logger.info("")
    
    logger.info(f"FCCL Summary: {successful} successful, {failed} failed\n")
    return successful, failed


def populate_mlcf_data(db, admin_user_id):
    """Populate MLCF data from all reports"""
    logger.info("\n" + "="*80)
    logger.info("POPULATING MLCF DATA")
    logger.info("="*80)
    
    service = FinancialDataService(db)
    # Paths inside container - reports are mounted as volume
    reports_dir = Path("/app/reports/MLCF")
    
    years = ["2023-24", "2022-23", "2021-22", "2020-21"]
    reports_to_process = []
    
    for year in years:
        year_dir = reports_dir / year
        if year_dir.exists():
            # Get quarterly reports
            for quarter in ["Q1", "Q2", "Q3"]:
                pdf_path = year_dir / f"MLCF_{year}_{quarter}.pdf"
                if pdf_path.exists():
                    reports_to_process.append(str(pdf_path))
            
            # Get annual report
            annual_path = year_dir / f"MLCF_Annual_{year}.pdf"
            if annual_path.exists():
                reports_to_process.append(str(annual_path))
    
    logger.info(f"Found {len(reports_to_process)} MLCF reports to process\n")
    
    successful = 0
    failed = 0
    
    for i, pdf_path in enumerate(reports_to_process, 1):
        pdf_name = Path(pdf_path).name
        logger.info(f"[{i}/{len(reports_to_process)}] Processing: {pdf_name}")
        
        try:
            result = service.process_pdf_report(
                pdf_path=pdf_path,
                uploaded_by_user_id=admin_user_id
            )
            
            if result['success']:
                logger.info(f"  ✓ SUCCESS - Report ID: {result['report_id']}")
                logger.info(f"    Balance Sheet: {result.get('balance_sheet_id', 'N/A')}")
                logger.info(f"    Income Statement: {result.get('income_statement_id', 'N/A')}")
                logger.info(f"    Cash Flow: {result.get('cash_flow_id', 'N/A')}")
                successful += 1
            else:
                logger.error(f"  ✗ FAILED - {result.get('error', 'Unknown error')}")
                failed += 1
        except Exception as e:
            logger.error(f"  ✗ ERROR - {str(e)}")
            failed += 1
        
        logger.info("")
    
    logger.info(f"MLCF Summary: {successful} successful, {failed} failed\n")
    return successful, failed


def show_summary(db):
    """Show summary of data in database"""
    from app.models.financial_data import Company
    from app.models.enhanced_financial_data import Report, BalanceSheet, IncomeStatement, CashFlowStatement
    
    logger.info("\n" + "="*80)
    logger.info("DATABASE SUMMARY")
    logger.info("="*80)
    
    companies = db.query(Company).all()
    logger.info(f"\n📊 Companies: {len(companies)}")
    for company in companies:
        reports_count = db.query(Report).filter(Report.company_id == company.id).count()
        balance_sheets_count = db.query(BalanceSheet).join(Report).filter(Report.company_id == company.id).count()
        income_statements_count = db.query(IncomeStatement).join(Report).filter(Report.company_id == company.id).count()
        cash_flows_count = db.query(CashFlowStatement).join(Report).filter(Report.company_id == company.id).count()
        
        logger.info(f"\n  {company.symbol} - {company.name}")
        logger.info(f"    Reports: {reports_count}")
        logger.info(f"    Balance Sheets: {balance_sheets_count}")
        logger.info(f"    Income Statements: {income_statements_count}")
        logger.info(f"    Cash Flows: {cash_flows_count}")
    
    # Show latest data for FCCL
    fccl = db.query(Company).filter(Company.symbol == "FCCL").first()
    if fccl:
        latest_income = db.query(IncomeStatement).join(Report).filter(
            Report.company_id == fccl.id
        ).order_by(Report.created_at.desc()).first()
        
        if latest_income:
            logger.info(f"\n  📈 Latest FCCL Financial Data:")
            logger.info(f"    Revenue: {latest_income.revenue:,.0f}" if latest_income.revenue else "    Revenue: N/A")
            logger.info(f"    Gross Profit: {latest_income.gross_profit:,.0f}" if latest_income.gross_profit else "    Gross Profit: N/A")
            logger.info(f"    Net Profit: {latest_income.net_profit:,.0f}" if latest_income.net_profit else "    Net Profit: N/A")


def main():
    """Main execution"""
    logger.info("\n" + "="*80)
    logger.info("🚀 POPULATING DATABASE WITH REAL FINANCIAL DATA")
    logger.info("="*80)
    logger.info("\nThis will:")
    logger.info("  1. Process all FCCL reports")
    logger.info("  2. Process all MLCF reports")
    logger.info("  3. Extract and persist financial statements")
    logger.info("  4. Replace mock data with real data")
    logger.info("\n⏱️  This may take a few minutes...\n")
    
    db = SessionLocal()
    
    try:
        # Create admin user
        admin = create_admin_user(db)
        
        # Populate data
        fccl_success, fccl_failed = populate_fccl_data(db, admin.id)
        mlcf_success, mlcf_failed = populate_mlcf_data(db, admin.id)
        
        # Show summary
        show_summary(db)
        
        # Final summary
        logger.info("\n" + "="*80)
        logger.info("✅ DATA POPULATION COMPLETE")
        logger.info("="*80)
        logger.info(f"\nTotal Reports Processed:")
        logger.info(f"  ✓ Successful: {fccl_success + mlcf_success}")
        logger.info(f"  ✗ Failed: {fccl_failed + mlcf_failed}")
        logger.info(f"\n💡 You can now:")
        logger.info(f"  - View data at: http://localhost:8000/docs")
        logger.info(f"  - Query via API: /api/v1/financial/companies")
        logger.info(f"  - Use frontend: http://localhost:3000")
        logger.info("="*80 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
