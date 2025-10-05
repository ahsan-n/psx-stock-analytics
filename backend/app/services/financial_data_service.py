"""
Financial Data Service
Business logic for processing and persisting financial data
"""
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date
import logging

from app.models.enhanced_financial_data import (
    Company, Report, BalanceSheet, IncomeStatement, 
    CashFlowStatement, PDFExtractionLog
)
from app.parsers.hybrid_extractor import extract_hybrid

logger = logging.getLogger(__name__)


class FinancialDataService:
    """Service for financial data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_pdf_report(self, pdf_path: str, uploaded_by_user_id: int) -> Dict:
        """
        Extract data from PDF and persist to database
        Returns: Summary of what was saved
        """
        try:
            # Step 1: Extract data from PDF
            logger.info(f"Extracting data from: {pdf_path}")
            extracted_data = extract_hybrid(pdf_path)
            
            # Step 2: Get or create company
            company = self._get_or_create_company(
                symbol=extracted_data['company_info']['symbol'],
                name=extracted_data['company_info']['name']
            )
            
            # Step 3: Create report record
            report = self._create_report(
                company_id=company.id,
                report_type=extracted_data['company_info']['type'],
                quarter=extracted_data['company_info'].get('quarter'),
                fiscal_year=extracted_data['company_info'].get('fiscal_year'),
                pdf_path=pdf_path
            )
            
            # Step 4: Save Balance Sheet
            balance_sheet_id = None
            if 'balance_sheet' in extracted_data and not extracted_data['balance_sheet'].get('error'):
                balance_sheet_id = self._save_balance_sheet(
                    report_id=report.id,
                    data=extracted_data['balance_sheet']
                )
            
            # Step 5: Save Income Statement
            income_statement_id = None
            if 'income_statement' in extracted_data and not extracted_data['income_statement'].get('error'):
                income_statement_id = self._save_income_statement(
                    report_id=report.id,
                    data=extracted_data['income_statement']
                )
            
            # Step 6: Save Cash Flow
            cash_flow_id = None
            if 'cash_flow' in extracted_data and not extracted_data['cash_flow'].get('error'):
                cash_flow_id = self._save_cash_flow(
                    report_id=report.id,
                    data=extracted_data['cash_flow']
                )
            
            # Step 7: Log extraction
            self._log_extraction(
                report_id=report.id,
                pdf_path=pdf_path,
                success=True,
                extracted_data=extracted_data
            )
            
            self.db.commit()
            
            return {
                'success': True,
                'company_id': company.id,
                'company_symbol': company.symbol,
                'report_id': report.id,
                'balance_sheet_id': balance_sheet_id,
                'income_statement_id': income_statement_id,
                'cash_flow_id': cash_flow_id,
                'message': f'Successfully processed {company.symbol} report'
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            self.db.rollback()
            
            # Try to log the failure
            try:
                self._log_extraction(
                    report_id=None,
                    pdf_path=pdf_path,
                    success=False,
                    error_message=str(e)
                )
                self.db.commit()
            except:
                pass
            
            return {
                'success': False,
                'error': str(e),
                'message': f'Failed to process report: {str(e)}'
            }
    
    def _get_or_create_company(self, symbol: str, name: str) -> Company:
        """Get existing company or create new one"""
        company = self.db.query(Company).filter(Company.symbol == symbol).first()
        
        if not company:
            company = Company(
                symbol=symbol,
                name=name,
                industry='Cement',  # Default for FCCL/MLCF
                sector='Materials'
            )
            self.db.add(company)
            self.db.flush()  # Get ID without committing
            logger.info(f"Created new company: {symbol}")
        
        return company
    
    def _create_report(
        self, 
        company_id: int,
        report_type: str,
        quarter: Optional[str],
        fiscal_year: Optional[str],
        pdf_path: str
    ) -> Report:
        """Create a new report record"""
        report = Report(
            company_id=company_id,
            report_type=report_type,
            quarter=quarter,
            fiscal_year=fiscal_year,
            report_date=datetime.now().date(),  # Could extract from PDF
            pdf_path=pdf_path,
            is_audited=(report_type == 'annual')
        )
        self.db.add(report)
        self.db.flush()
        logger.info(f"Created report ID: {report.id}")
        return report
    
    def _save_balance_sheet(self, report_id: int, data: Dict) -> Optional[int]:
        """Save balance sheet data"""
        if not data or not data.get('assets'):
            return None
        
        # Extract key items
        assets = data.get('assets', {})
        liabilities = data.get('liabilities', {})
        equity = data.get('equity', {})
        
        # Find totals
        total_assets = self._find_total(assets, ['total asset'])
        total_liabilities = self._find_total(liabilities, ['total liabilit'])
        total_equity = self._find_total(equity, ['total equity', 'equity'])
        
        # Find key asset items
        ppe = self._find_value(assets, ['property', 'plant', 'equipment'])
        cash = self._find_value(assets, ['cash', 'bank'])
        inventory = self._find_value(assets, ['inventor', 'stock'])
        trade_debts = self._find_value(assets, ['trade debt', 'receivable'])
        
        # Find key liability items
        long_term_debt = self._find_value(liabilities, ['long term loan', 'long term borrowing'])
        short_term_debt = self._find_value(liabilities, ['short term', 'current portion'])
        trade_payables = self._find_value(liabilities, ['trade payable', 'creditor'])
        
        # Find equity items
        share_capital = self._find_value(equity, ['share capital', 'paid-up'])
        retained_earnings = self._find_value(equity, ['retained', 'accumulated profit'])
        
        balance_sheet = BalanceSheet(
            report_id=report_id,
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            total_equity=total_equity,
            # Assets
            property_plant_equipment=ppe,
            cash_and_equivalents=cash,
            inventory=inventory,
            trade_debts=trade_debts,
            # Liabilities
            long_term_debt=long_term_debt,
            short_term_debt=short_term_debt,
            trade_payables=trade_payables,
            # Equity
            share_capital=share_capital,
            retained_earnings=retained_earnings
        )
        
        self.db.add(balance_sheet)
        self.db.flush()
        logger.info(f"Saved balance sheet ID: {balance_sheet.id}")
        return balance_sheet.id
    
    def _save_income_statement(self, report_id: int, data: Dict) -> Optional[int]:
        """Save income statement data"""
        if not data or not data.get('line_items'):
            return None
        
        items = data.get('line_items', {})
        
        # Extract key items
        revenue = self._find_value(items, ['revenue', 'sales', 'turnover'])
        cost_of_sales = self._find_value(items, ['cost of sales', 'cost of revenue'])
        gross_profit = self._find_value(items, ['gross profit'])
        operating_expenses = self._find_value(items, ['operating expense', 'admin', 'distribution'])
        operating_profit = self._find_value(items, ['operating profit', 'ebit'])
        finance_cost = self._find_value(items, ['finance cost', 'interest expense'])
        profit_before_tax = self._find_value(items, ['profit before tax', 'pbt'])
        tax_expense = self._find_value(items, ['tax', 'taxation'])
        net_profit = self._find_value(items, ['profit for the', 'profit after tax', 'net income'])
        
        income_statement = IncomeStatement(
            report_id=report_id,
            revenue=revenue,
            cost_of_sales=abs(cost_of_sales) if cost_of_sales and cost_of_sales < 0 else cost_of_sales,  # Make positive
            gross_profit=gross_profit,
            operating_expenses=abs(operating_expenses) if operating_expenses and operating_expenses < 0 else operating_expenses,
            operating_profit=operating_profit,
            finance_cost=abs(finance_cost) if finance_cost and finance_cost < 0 else finance_cost,
            profit_before_tax=profit_before_tax,
            tax_expense=abs(tax_expense) if tax_expense and tax_expense < 0 else tax_expense,
            net_profit=net_profit
        )
        
        self.db.add(income_statement)
        self.db.flush()
        logger.info(f"Saved income statement ID: {income_statement.id}")
        return income_statement.id
    
    def _save_cash_flow(self, report_id: int, data: Dict) -> Optional[int]:
        """Save cash flow statement data"""
        if not data:
            return None
        
        operating = data.get('operating_activities', {})
        investing = data.get('investing_activities', {})
        financing = data.get('financing_activities', {})
        
        # Extract key items
        cash_from_operations = self._find_total(operating, ['cash from operating', 'net cash from operating', 'cash generated from'])
        cash_from_investing = self._find_total(investing, ['cash from investing', 'net cash from investing', 'cash used in investing'])
        cash_from_financing = self._find_total(financing, ['cash from financing', 'net cash from financing', 'cash used in financing'])
        
        cash_flow = CashFlowStatement(
            report_id=report_id,
            cash_from_operations=cash_from_operations,
            cash_from_investing=cash_from_investing,
            cash_from_financing=cash_from_financing
        )
        
        self.db.add(cash_flow)
        self.db.flush()
        logger.info(f"Saved cash flow ID: {cash_flow.id}")
        return cash_flow.id
    
    def _log_extraction(
        self,
        report_id: Optional[int],
        pdf_path: str,
        success: bool,
        extracted_data: Optional[Dict] = None,
        error_message: Optional[str] = None
    ):
        """Log PDF extraction attempt"""
        log = PDFExtractionLog(
            report_id=report_id,
            pdf_path=pdf_path,
            extraction_success=success,
            error_message=error_message,
            pages_processed=extracted_data['extraction_metadata']['pages_processed'] if extracted_data else None
        )
        self.db.add(log)
    
    def _find_total(self, items: Dict, keywords: List[str]) -> Optional[float]:
        """Find total value from items dict"""
        for name, values in items.items():
            name_lower = name.lower()
            if any(keyword.lower() in name_lower for keyword in keywords):
                value = values.get('current') if isinstance(values, dict) else values
                if value is not None:
                    return float(value)
        return None
    
    def _find_value(self, items: Dict, keywords: List[str]) -> Optional[float]:
        """Find value from items dict based on keywords"""
        for name, values in items.items():
            name_lower = name.lower()
            if any(keyword.lower() in name_lower for keyword in keywords):
                value = values.get('current') if isinstance(values, dict) else values
                if value is not None:
                    return float(value)
        return None
    
    def get_company_reports(self, company_id: int) -> List[Report]:
        """Get all reports for a company"""
        return self.db.query(Report).filter(Report.company_id == company_id).order_by(Report.report_date.desc()).all()
    
    def get_latest_balance_sheet(self, company_id: int) -> Optional[BalanceSheet]:
        """Get latest balance sheet for a company"""
        return self.db.query(BalanceSheet).join(Report).filter(
            Report.company_id == company_id
        ).order_by(Report.report_date.desc()).first()
    
    def get_latest_income_statement(self, company_id: int) -> Optional[IncomeStatement]:
        """Get latest income statement for a company"""
        return self.db.query(IncomeStatement).join(Report).filter(
            Report.company_id == company_id
        ).order_by(Report.report_date.desc()).first()
