"""
Table-based Financial Statement Extractor
Uses pdfplumber's table detection for better accuracy
"""
import pdfplumber
import re
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class TableFinancialExtractor:
    """Extract financial data using table detection"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        
    def extract_all(self) -> Dict:
        """Extract all statements using table detection"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                company_info = self._identify_company(pdf)
                statement_pages = self._find_statement_pages(pdf)
                
                # Extract using tables
                balance_sheet = self._extract_balance_sheet_tables(pdf, statement_pages.get('balance_sheet', []))
                income_statement = self._extract_income_statement_tables(pdf, statement_pages.get('income_statement', []))
                cash_flow = self._extract_cash_flow_tables(pdf, statement_pages.get('cash_flow', []))
                
                return {
                    'company_info': company_info,
                    'balance_sheet': balance_sheet,
                    'income_statement': income_statement,
                    'cash_flow': cash_flow,
                    'extraction_metadata': {
                        'pdf_name': self.pdf_path.split('/')[-1],
                        'pages_processed': len(pdf.pages),
                        'statement_pages': statement_pages
                    }
                }
        except Exception as e:
            logger.error(f"Error extracting from {self.pdf_path}: {e}")
            raise
    
    def _identify_company(self, pdf) -> Dict:
        """Identify company from PDF content"""
        for page_num in range(min(5, len(pdf.pages))):
            text = pdf.pages[page_num].extract_text()
            if not text:
                continue
                
            text_lower = text.lower()
            
            if 'fauji cement' in text_lower or 'fccl' in text_lower:
                return {
                    'symbol': 'FCCL',
                    'name': 'Fauji Cement Company Limited',
                    'type': 'annual' if 'annual report' in text_lower else 'quarterly'
                }
            
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
            
            # More precise detection
            if 'statement of financial position' in text_lower or \
               ('balance sheet' in text_lower and 'note' in text_lower):
                statement_pages['balance_sheet'].append(page_num)
            
            if 'statement of profit or loss' in text_lower or \
               'statement of profit and loss' in text_lower or \
               ('income statement' in text_lower and 'note' in text_lower):
                statement_pages['income_statement'].append(page_num)
            
            if 'statement of cash flow' in text_lower or \
               ('cash flow' in text_lower and 'operating activities' in text_lower):
                statement_pages['cash_flow'].append(page_num)
        
        return statement_pages
    
    def _extract_balance_sheet_tables(self, pdf, page_indices: List[int]) -> Dict:
        """Extract balance sheet using table detection"""
        if not page_indices:
            return {'error': 'Balance sheet pages not found', 'assets': {}, 'liabilities': {}, 'equity': {}}
        
        data = {
            'current_year': None,
            'previous_year': None,
            'assets': {},
            'liabilities': {},
            'equity': {}
        }
        
        # Process first 2 pages
        for page_idx in page_indices[:2]:
            if page_idx >= len(pdf.pages):
                continue
                
            page = pdf.pages[page_idx]
            tables = page.extract_tables()
            
            if not tables:
                continue
            
            # Find the main financial table (usually the largest one)
            main_table = max(tables, key=lambda t: len(t) if t else 0)
            
            if not main_table or len(main_table) < 3:
                continue
            
            # Extract years from header row
            header_row = main_table[0]
            years = self._extract_years_from_row(header_row)
            if len(years) >= 2:
                data['current_year'] = years[0]
                data['previous_year'] = years[1]
            
            # Process each row
            for row in main_table[1:]:
                if not row or len(row) < 2:
                    continue
                
                item_name = row[0]
                if not item_name or len(str(item_name).strip()) < 3:
                    continue
                
                item_name = str(item_name).strip()
                
                # Extract numeric values (skip 'Note' column)
                values = []
                for cell in row[1:]:
                    num = self._parse_cell_number(cell)
                    if num is not None:
                        values.append(num)
                
                if len(values) < 2:
                    continue
                
                # Take first two numbers as current and previous year
                current_val = values[0]
                previous_val = values[1] if len(values) > 1 else None
                
                # Categorize the item
                item_lower = item_name.lower()
                
                # Assets
                if any(keyword in item_lower for keyword in [
                    'asset', 'property', 'equipment', 'investment', 'stock', 
                    'trade debt', 'receivable', 'cash', 'bank', 'inventory',
                    'goodwill', 'intangible', 'deposit', 'advance'
                ]):
                    data['assets'][item_name] = {
                        'current': current_val,
                        'previous': previous_val
                    }
                
                # Liabilities
                elif any(keyword in item_lower for keyword in [
                    'liability', 'liabilities', 'payable', 'loan', 'borrowing',
                    'debt', 'provision', 'tax payable', 'accrued', 'creditor'
                ]):
                    data['liabilities'][item_name] = {
                        'current': current_val,
                        'previous': previous_val
                    }
                
                # Equity
                elif any(keyword in item_lower for keyword in [
                    'capital', 'reserve', 'equity', 'shareholder', 
                    'retained', 'surplus', 'share premium'
                ]):
                    data['equity'][item_name] = {
                        'current': current_val,
                        'previous': previous_val
                    }
        
        return data
    
    def _extract_income_statement_tables(self, pdf, page_indices: List[int]) -> Dict:
        """Extract income statement using table detection"""
        if not page_indices:
            return {'error': 'Income statement pages not found', 'line_items': {}}
        
        data = {
            'current_year': None,
            'previous_year': None,
            'line_items': {}
        }
        
        for page_idx in page_indices[:2]:
            if page_idx >= len(pdf.pages):
                continue
            
            page = pdf.pages[page_idx]
            tables = page.extract_tables()
            
            if not tables:
                continue
            
            main_table = max(tables, key=lambda t: len(t) if t else 0)
            
            if not main_table or len(main_table) < 3:
                continue
            
            # Extract years
            header_row = main_table[0]
            years = self._extract_years_from_row(header_row)
            if len(years) >= 2 and not data['current_year']:
                data['current_year'] = years[0]
                data['previous_year'] = years[1]
            
            # Process rows
            for row in main_table[1:]:
                if not row or len(row) < 2:
                    continue
                
                item_name = row[0]
                if not item_name or len(str(item_name).strip()) < 3:
                    continue
                
                item_name = str(item_name).strip()
                
                # Skip total rows and section headers
                if item_name.isupper() and len(item_name) > 20:
                    continue
                
                # Extract values
                values = []
                for cell in row[1:]:
                    num = self._parse_cell_number(cell)
                    if num is not None:
                        values.append(num)
                
                if len(values) >= 2:
                    data['line_items'][item_name] = {
                        'current': values[0],
                        'previous': values[1] if len(values) > 1 else None
                    }
        
        return data
    
    def _extract_cash_flow_tables(self, pdf, page_indices: List[int]) -> Dict:
        """Extract cash flow statement using table detection"""
        if not page_indices:
            return {
                'error': 'Cash flow pages not found',
                'operating_activities': {},
                'investing_activities': {},
                'financing_activities': {}
            }
        
        data = {
            'current_year': None,
            'previous_year': None,
            'operating_activities': {},
            'investing_activities': {},
            'financing_activities': {}
        }
        
        current_section = 'operating_activities'
        
        for page_idx in page_indices[:2]:
            if page_idx >= len(pdf.pages):
                continue
            
            page = pdf.pages[page_idx]
            tables = page.extract_tables()
            
            if not tables:
                continue
            
            main_table = max(tables, key=lambda t: len(t) if t else 0)
            
            if not main_table:
                continue
            
            # Extract years
            header_row = main_table[0]
            years = self._extract_years_from_row(header_row)
            if len(years) >= 2 and not data['current_year']:
                data['current_year'] = years[0]
                data['previous_year'] = years[1]
            
            # Process rows
            for row in main_table[1:]:
                if not row or len(row) < 2:
                    continue
                
                item_name = row[0]
                if not item_name:
                    continue
                
                item_name = str(item_name).strip()
                
                # Detect section changes
                item_lower = item_name.lower()
                if 'investing activities' in item_lower:
                    current_section = 'investing_activities'
                    continue
                elif 'financing activities' in item_lower:
                    current_section = 'financing_activities'
                    continue
                elif 'operating activities' in item_lower:
                    current_section = 'operating_activities'
                    continue
                
                if len(item_name) < 3:
                    continue
                
                # Extract values
                values = []
                for cell in row[1:]:
                    num = self._parse_cell_number(cell)
                    if num is not None:
                        values.append(num)
                
                if len(values) >= 2:
                    data[current_section][item_name] = {
                        'current': values[0],
                        'previous': values[1] if len(values) > 1 else None
                    }
        
        return data
    
    def _extract_years_from_row(self, row: List) -> List[int]:
        """Extract years from a row (usually header)"""
        years = []
        year_pattern = re.compile(r'20\d{2}')
        
        for cell in row:
            if cell:
                matches = year_pattern.findall(str(cell))
                for match in matches:
                    year = int(match)
                    if year not in years:
                        years.append(year)
        
        return sorted(years, reverse=True)
    
    def _parse_cell_number(self, cell_value) -> Optional[float]:
        """Parse a cell value to extract number"""
        if cell_value is None or cell_value == '':
            return None
        
        cell_str = str(cell_value).strip()
        
        # Skip if it's just a note reference or text
        if len(cell_str) < 1 or cell_str.isalpha():
            return None
        
        # Check for negative in parentheses
        is_negative = cell_str.startswith('(') and cell_str.endswith(')')
        
        # Remove common non-numeric characters
        clean_str = cell_str.replace('(', '').replace(')', '').replace(',', '').replace(' ', '')
        
        # Remove 'Rs' or other currency symbols
        clean_str = re.sub(r'[A-Za-z$€£¥₹]', '', clean_str)
        
        try:
            number = float(clean_str)
            return -number if is_negative else number
        except (ValueError, TypeError):
            return None


def extract_with_tables(pdf_path: str) -> Dict:
    """Convenience function for table-based extraction"""
    extractor = TableFinancialExtractor(pdf_path)
    return extractor.extract_all()
