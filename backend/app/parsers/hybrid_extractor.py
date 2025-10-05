"""
Hybrid PDF Financial Statement Extractor
Combines text extraction with intelligent parsing for PSX reports
"""
import pdfplumber
import re
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class HybridFinancialExtractor:
    """Robust extractor that handles various PDF formats"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.company_symbol = None
        
    def extract_all(self) -> Dict:
        """Extract all financial statements"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                company_info = self._identify_company(pdf)
                self.company_symbol = company_info['symbol']
                
                # Extract each statement
                balance_sheet = self._extract_balance_sheet(pdf)
                income_statement = self._extract_income_statement(pdf)
                cash_flow = self._extract_cash_flow(pdf)
                
                return {
                    'company_info': company_info,
                    'balance_sheet': balance_sheet,
                    'income_statement': income_statement,
                    'cash_flow': cash_flow,
                    'extraction_metadata': {
                        'pdf_name': self.pdf_path.split('/')[-1],
                        'pages_processed': len(pdf.pages)
                    }
                }
        except Exception as e:
            logger.error(f"Error extracting from {self.pdf_path}: {e}")
            raise
    
    def _identify_company(self, pdf) -> Dict:
        """Identify company from PDF"""
        for page_num in range(min(10, len(pdf.pages))):
            text = pdf.pages[page_num].extract_text()
            if not text:
                continue
                
            text_lower = text.lower()
            
            if 'fauji cement' in text_lower or 'fccl' in text_lower:
                report_type = 'annual' if 'annual report' in text_lower else 'quarterly'
                quarter = self._extract_quarter(text)
                year = self._extract_fiscal_year(text)
                
                return {
                    'symbol': 'FCCL',
                    'name': 'Fauji Cement Company Limited',
                    'type': report_type,
                    'quarter': quarter,
                    'fiscal_year': year
                }
            
            if 'maple leaf cement' in text_lower or 'mlcf' in text_lower:
                report_type = 'quarterly' if 'condensed interim' in text_lower else 'annual'
                quarter = self._extract_quarter(text)
                year = self._extract_fiscal_year(text)
                
                return {
                    'symbol': 'MLCF',
                    'name': 'Maple Leaf Cement Factory Limited',
                    'type': report_type,
                    'quarter': quarter,
                    'fiscal_year': year
                }
        
        return {'symbol': 'UNKNOWN', 'name': 'Unknown', 'type': 'unknown', 'quarter': None, 'fiscal_year': None}
    
    def _extract_quarter(self, text: str) -> Optional[str]:
        """Extract quarter from text"""
        # Look for Q1, Q2, Q3, Q4, or first, second, third, fourth quarter
        if re.search(r'\bQ1\b|first quarter|1st quarter', text, re.IGNORECASE):
            return 'Q1'
        elif re.search(r'\bQ2\b|second quarter|2nd quarter', text, re.IGNORECASE):
            return 'Q2'
        elif re.search(r'\bQ3\b|third quarter|3rd quarter', text, re.IGNORECASE):
            return 'Q3'
        elif re.search(r'\bQ4\b|fourth quarter|4th quarter', text, re.IGNORECASE):
            return 'Q4'
        return None
    
    def _extract_fiscal_year(self, text: str) -> Optional[str]:
        """Extract fiscal year like 2023-24"""
        match = re.search(r'20\d{2}[-\s]20?\d{2}', text)
        if match:
            return match.group(0).replace(' ', '-')
        return None
    
    def _extract_balance_sheet(self, pdf) -> Dict:
        """Extract balance sheet"""
        # Find the balance sheet page
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            if not text:
                continue
            
            text_lower = text.lower()
            
            # Look for actual balance sheet (not table of contents)
            if ('statement of financial position' in text_lower or 'balance sheet' in text_lower) and \
               'rupees' in text_lower and page_num > 5:
                
                # Extract data from this page
                data = self._parse_balance_sheet_text(text)
                if data and (data['assets'] or data['liabilities'] or data['equity']):
                    return data
        
        return {'error': 'Balance sheet not found', 'assets': {}, 'liabilities': {}, 'equity': {}}
    
    def _extract_income_statement(self, pdf) -> Dict:
        """Extract income statement"""
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            if not text:
                continue
            
            text_lower = text.lower()
            
            if ('statement of profit or loss' in text_lower or 'income statement' in text_lower) and \
               'rupees' in text_lower and page_num > 5:
                
                data = self._parse_income_statement_text(text)
                if data and data['line_items']:
                    return data
        
        return {'error': 'Income statement not found', 'line_items': {}}
    
    def _extract_cash_flow(self, pdf) -> Dict:
        """Extract cash flow statement"""
        for page_num in range(len(pdf.pages)):
            page = pdf.pages[page_num]
            text = page.extract_text()
            
            if not text:
                continue
            
            text_lower = text.lower()
            
            if 'statement of cash flow' in text_lower and 'rupees' in text_lower and page_num > 5:
                data = self._parse_cash_flow_text(text)
                if data and (data['operating_activities'] or data['investing_activities'] or data['financing_activities']):
                    return data
        
        return {'error': 'Cash flow not found', 'operating_activities': {}, 'investing_activities': {}, 'financing_activities': {}}
    
    def _parse_balance_sheet_text(self, text: str) -> Dict:
        """Parse balance sheet from text"""
        lines = text.split('\n')
        
        data = {
            'current_year': None,
            'previous_year': None,
            'assets': {},
            'liabilities': {},
            'equity': {}
        }
        
        # Extract years from header
        for line in lines[:10]:
            years = re.findall(r'20\d{2}', line)
            if len(years) >= 2:
                data['current_year'] = int(years[0])
                data['previous_year'] = int(years[1])
                break
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Detect sections
            line_lower = line.lower()
            if 'asset' in line_lower and not any(c.isdigit() for c in line):
                current_section = 'assets'
                continue
            elif 'liabilit' in line_lower and not any(c.isdigit() for c in line):
                current_section = 'liabilities'
                continue
            elif ('equity' in line_lower or 'capital and reserves' in line_lower or 'share capital' in line_lower) and not any(c.isdigit() for c in line):
                current_section = 'equity'
                continue
            
            # Extract line items with numbers
            # Pattern: text followed by 2 numbers (current and previous year)
            # Example: "Property, plant and equipment 12,345,678 11,234,567"
            pattern = r'^(.+?)\s+([\d,]+(?:\.\d+)?)\s+([\d,]+(?:\.\d+)?)(?:\s|$)'
            match = re.match(pattern, line)
            
            if match and current_section:
                item_name = match.group(1).strip()
                current_val = self._parse_number(match.group(2))
                previous_val = self._parse_number(match.group(3))
                
                if item_name and current_val is not None and len(item_name) > 3:
                    data[current_section][item_name] = {
                        'current': current_val,
                        'previous': previous_val
                    }
        
        return data
    
    def _parse_income_statement_text(self, text: str) -> Dict:
        """Parse income statement from text"""
        lines = text.split('\n')
        
        data = {
            'current_year': None,
            'previous_year': None,
            'line_items': {}
        }
        
        # Extract years
        for line in lines[:10]:
            years = re.findall(r'20\d{2}', line)
            if len(years) >= 2:
                data['current_year'] = int(years[0])
                data['previous_year'] = int(years[1])
                break
        
        for line in lines:
            line = line.strip()
            
            # Pattern for line items
            pattern = r'^(.+?)\s+([\d,]+(?:\.\d+)?)\s+([\d,]+(?:\.\d+)?)(?:\s|$)'
            match = re.match(pattern, line)
            
            if match:
                item_name = match.group(1).strip()
                current_val = self._parse_number(match.group(2))
                previous_val = self._parse_number(match.group(3))
                
                if item_name and current_val is not None and len(item_name) > 3:
                    data['line_items'][item_name] = {
                        'current': current_val,
                        'previous': previous_val
                    }
        
        return data
    
    def _parse_cash_flow_text(self, text: str) -> Dict:
        """Parse cash flow statement from text"""
        lines = text.split('\n')
        
        data = {
            'current_year': None,
            'previous_year': None,
            'operating_activities': {},
            'investing_activities': {},
            'financing_activities': {}
        }
        
        # Extract years
        for line in lines[:10]:
            years = re.findall(r'20\d{2}', line)
            if len(years) >= 2:
                data['current_year'] = int(years[0])
                data['previous_year'] = int(years[1])
                break
        
        current_section = 'operating_activities'
        
        for line in lines:
            line = line.strip()
            line_lower = line.lower()
            
            # Detect section changes
            if 'investing activities' in line_lower:
                current_section = 'investing_activities'
                continue
            elif 'financing activities' in line_lower:
                current_section = 'financing_activities'
                continue
            elif 'operating activities' in line_lower:
                current_section = 'operating_activities'
                continue
            
            # Extract line items
            pattern = r'^(.+?)\s+([\d,]+(?:\.\d+)?)\s+([\d,]+(?:\.\d+)?)(?:\s|$)'
            match = re.match(pattern, line)
            
            if match:
                item_name = match.group(1).strip()
                current_val = self._parse_number(match.group(2))
                previous_val = self._parse_number(match.group(3))
                
                if item_name and current_val is not None and len(item_name) > 3:
                    data[current_section][item_name] = {
                        'current': current_val,
                        'previous': previous_val
                    }
        
        return data
    
    def _parse_number(self, value_str: str) -> Optional[float]:
        """Parse number string to float"""
        if not value_str:
            return None
        
        # Remove commas
        clean_str = value_str.replace(',', '').strip()
        
        try:
            return float(clean_str)
        except (ValueError, TypeError):
            return None


def extract_hybrid(pdf_path: str) -> Dict:
    """Convenience function for hybrid extraction"""
    extractor = HybridFinancialExtractor(pdf_path)
    return extractor.extract_all()
