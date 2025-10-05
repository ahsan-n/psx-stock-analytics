"""
PDF Financial Statement Extractor
Extracts Balance Sheet, Income Statement, and Cash Flow from PSX company reports
"""
import pdfplumber
import re
from typing import Dict, List, Optional, Tuple
from datetime import date
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FinancialStatementExtractor:
    """Extract financial statements from PDF reports"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf_name = Path(pdf_path).name
        
    def extract_all(self) -> Dict:
        """Extract all financial statements from PDF"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                # Determine company type and format
                company_info = self._identify_company(pdf)
                
                # Find statement pages
                statement_pages = self._find_statement_pages(pdf)
                
                # Extract each statement
                balance_sheet = self._extract_balance_sheet(pdf, statement_pages.get('balance_sheet', []))
                income_statement = self._extract_income_statement(pdf, statement_pages.get('income_statement', []))
                cash_flow = self._extract_cash_flow(pdf, statement_pages.get('cash_flow', []))
                
                return {
                    'company_info': company_info,
                    'balance_sheet': balance_sheet,
                    'income_statement': income_statement,
                    'cash_flow': cash_flow,
                    'extraction_metadata': {
                        'pdf_name': self.pdf_name,
                        'pages_processed': len(pdf.pages),
                        'statement_pages': statement_pages
                    }
                }
        except Exception as e:
            logger.error(f"Error extracting from {self.pdf_name}: {e}")
            raise
    
    def _identify_company(self, pdf) -> Dict:
        """Identify company from PDF content"""
        # Check first few pages for company name
        for page_num in range(min(10, len(pdf.pages))):
            text = pdf.pages[page_num].extract_text()
            if not text:
                continue
                
            text_lower = text.lower()
            
            # Check for FCCL
            if 'fauji cement' in text_lower or 'fccl' in text_lower:
                return {
                    'symbol': 'FCCL',
                    'name': 'Fauji Cement Company Limited',
                    'type': 'annual' if 'annual report' in text_lower else 'quarterly'
                }
            
            # Check for MLCF
            if 'maple leaf cement' in text_lower or 'mlcf' in text_lower:
                return {
                    'symbol': 'MLCF',
                    'name': 'Maple Leaf Cement Factory Limited',
                    'type': 'quarterly' if 'condensed interim' in text_lower else 'annual'
                }
        
        return {'symbol': 'UNKNOWN', 'name': 'Unknown', 'type': 'unknown'}
    
    def _find_statement_pages(self, pdf) -> Dict[str, List[int]]:
        """Find pages containing financial statements"""
        statement_pages = {
            'balance_sheet': [],
            'income_statement': [],
            'cash_flow': []
        }
        
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
                
            text_lower = text.lower()
            
            # Look for statements with 'note' and 'rupees' (indicates actual financial data)
            has_data = 'note' in text_lower and 'rupees' in text_lower
            
            if has_data:
                # Balance Sheet / Statement of Financial Position
                if 'statement of financial position' in text_lower or \
                   ('assets' in text_lower and 'liabilities' in text_lower and 'equity' in text_lower):
                    statement_pages['balance_sheet'].append(page_num)
                
                # Income Statement / Profit or Loss
                if 'statement of profit or loss' in text_lower or \
                   'statement of profit and loss' in text_lower or \
                   ('revenue' in text_lower and 'cost of sales' in text_lower):
                    statement_pages['income_statement'].append(page_num)
                
                # Cash Flow Statement
                if 'statement of cash flow' in text_lower or \
                   'cash flows from operating activities' in text_lower:
                    statement_pages['cash_flow'].append(page_num)
        
        return statement_pages
    
    def _extract_balance_sheet(self, pdf, page_indices: List[int]) -> Dict:
        """Extract balance sheet data"""
        if not page_indices:
            return {'error': 'Balance sheet pages not found'}
        
        data = {
            'assets': {},
            'liabilities': {},
            'equity': {},
            'current_year': None,
            'previous_year': None
        }
        
        # Combine text from all balance sheet pages
        combined_text = ""
        for page_idx in page_indices[:3]:  # Max 3 pages
            if page_idx < len(pdf.pages):
                combined_text += pdf.pages[page_idx].extract_text() + "\n"
        
        # Extract line items using patterns
        data = self._parse_balance_sheet_text(combined_text)
        
        return data
    
    def _extract_income_statement(self, pdf, page_indices: List[int]) -> Dict:
        """Extract income statement data"""
        if not page_indices:
            return {'error': 'Income statement pages not found'}
        
        text = ""
        for page_idx in page_indices[:2]:  # Max 2 pages
            if page_idx < len(pdf.pages):
                text += pdf.pages[page_idx].extract_text() + "\n"
        
        return self._parse_income_statement_text(text)
    
    def _extract_cash_flow(self, pdf, page_indices: List[int]) -> Dict:
        """Extract cash flow statement data"""
        if not page_indices:
            return {'error': 'Cash flow pages not found'}
        
        text = ""
        for page_idx in page_indices[:2]:  # Max 2 pages
            if page_idx < len(pdf.pages):
                text += pdf.pages[page_idx].extract_text() + "\n"
        
        return self._parse_cash_flow_text(text)
    
    def _parse_balance_sheet_text(self, text: str) -> Dict:
        """Parse balance sheet from text using regex patterns"""
        data = {
            'current_year': None,
            'previous_year': None,
            'assets': {},
            'liabilities': {},
            'equity': {}
        }
        
        # Extract years
        year_pattern = r'20\d{2}'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            data['current_year'] = int(years[0])
            data['previous_year'] = int(years[1])
        
        # Pattern for line items: Name followed by two numbers
        # Matches: "Property, plant and equipment 110,845,663 104,425,181"
        line_pattern = r'([A-Z][A-Za-z\s,&\'-]+?)\s+(\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))\s+(\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))'
        
        # Extract all line items
        matches = re.findall(line_pattern, text)
        
        # Categorize line items
        for name, current_val, prev_val in matches:
            name = name.strip()
            current = self._parse_number(current_val)
            previous = self._parse_number(prev_val)
            
            name_lower = name.lower()
            
            # Skip if name is too short or looks like a header
            if len(name) < 5 or name.isupper():
                continue
            
            # Categorize based on keywords
            if any(word in name_lower for word in ['asset', 'property', 'equipment', 'investment', 'deposit', 
                                                     'receivable', 'stock', 'cash', 'bank', 'inventory']):
                data['assets'][name] = {'current': current, 'previous': previous}
            
            elif any(word in name_lower for word in ['liability', 'liabilities', 'payable', 'loan', 
                                                       'borrowing', 'debt', 'provision']):
                data['liabilities'][name] = {'current': current, 'previous': previous}
            
            elif any(word in name_lower for word in ['capital', 'reserve', 'equity', 'profit', 'retained']):
                data['equity'][name] = {'current': current, 'previous': previous}
        
        # Extract key totals using specific patterns
        totals_pattern = r'(Total\s+[A-Za-z\s]+|TOTAL\s+[A-Z\s]+)\s+(\d{1,3}(?:,\d{3})*)\s+(\d{1,3}(?:,\d{3})*)'
        totals = re.findall(totals_pattern, text)
        
        for total_name, current_val, prev_val in totals:
            total_name = total_name.strip()
            current = self._parse_number(current_val)
            previous = self._parse_number(prev_val)
            
            if 'asset' in total_name.lower():
                data['assets'][total_name] = {'current': current, 'previous': previous}
            elif 'liabilit' in total_name.lower():
                data['liabilities'][total_name] = {'current': current, 'previous': previous}
            elif 'equity' in total_name.lower():
                data['equity'][total_name] = {'current': current, 'previous': previous}
        
        return data
    
    def _parse_income_statement_text(self, text: str) -> Dict:
        """Parse income statement from text"""
        data = {
            'current_year': None,
            'previous_year': None,
            'line_items': {}
        }
        
        # Extract years
        year_pattern = r'20\d{2}'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            data['current_year'] = int(years[0])
            data['previous_year'] = int(years[1])
        
        # Pattern for line items with potential negatives
        line_pattern = r'([A-Z][A-Za-z\s,&\'-]+?)\s+(\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))\s+(\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))'
        
        matches = re.findall(line_pattern, text)
        
        for name, current_val, prev_val in matches:
            name = name.strip()
            
            # Skip if name is too short
            if len(name) < 5:
                continue
            
            current = self._parse_number(current_val)
            previous = self._parse_number(prev_val)
            
            data['line_items'][name] = {
                'current': current,
                'previous': previous
            }
        
        return data
    
    def _parse_cash_flow_text(self, text: str) -> Dict:
        """Parse cash flow statement from text"""
        data = {
            'current_year': None,
            'previous_year': None,
            'operating_activities': {},
            'investing_activities': {},
            'financing_activities': {}
        }
        
        # Extract years
        year_pattern = r'20\d{2}'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            data['current_year'] = int(years[0])
            data['previous_year'] = int(years[1])
        
        # Pattern for line items
        line_pattern = r'([A-Z][A-Za-z\s,&\'-]+?)\s+(\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))\s+(\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))'
        
        matches = re.findall(line_pattern, text)
        
        # Simple categorization based on position in text
        current_section = 'operating_activities'
        
        for name, current_val, prev_val in matches:
            name = name.strip()
            
            if len(name) < 5:
                continue
            
            # Detect section changes
            name_lower = name.lower()
            if 'investing' in name_lower:
                current_section = 'investing_activities'
            elif 'financing' in name_lower:
                current_section = 'financing_activities'
            
            current = self._parse_number(current_val)
            previous = self._parse_number(prev_val)
            
            data[current_section][name] = {
                'current': current,
                'previous': previous
            }
        
        return data
    
    def _parse_number(self, value_str: str) -> Optional[float]:
        """Parse number string to float (handles negatives in parentheses)"""
        if not value_str:
            return None
        
        # Remove whitespace
        value_str = value_str.strip()
        
        # Check for negative (in parentheses)
        is_negative = value_str.startswith('(') and value_str.endswith(')')
        
        # Remove parentheses and commas
        clean_str = value_str.replace('(', '').replace(')', '').replace(',', '')
        
        try:
            number = float(clean_str)
            return -number if is_negative else number
        except ValueError:
            return None


def extract_from_pdf(pdf_path: str) -> Dict:
    """Convenience function to extract from a PDF file"""
    extractor = FinancialStatementExtractor(pdf_path)
    return extractor.extract_all()
