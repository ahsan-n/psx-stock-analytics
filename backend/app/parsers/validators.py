"""
Financial Statement Validators
Validates extracted data for accuracy and completeness
"""
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class FinancialStatementValidator:
    """Validate extracted financial statements"""
    
    def __init__(self, tolerance: float = 0.01):
        """
        Args:
            tolerance: Acceptable percentage difference for validation (default 1%)
        """
        self.tolerance = tolerance
        self.validation_results = []
    
    def validate_balance_sheet(self, balance_sheet: Dict) -> Tuple[bool, float, List[str]]:
        """
        Validate balance sheet accounting equations
        Returns: (is_valid, confidence_score, issues)
        """
        issues = []
        validations_passed = 0
        total_validations = 0
        
        assets = balance_sheet.get('assets', {})
        liabilities = balance_sheet.get('liabilities', {})
        equity = balance_sheet.get('equity', {})
        
        # Extract totals
        total_assets_current = self._find_total(assets, 'current', ['total asset'])
        total_assets_previous = self._find_total(assets, 'previous', ['total asset'])
        
        total_liabilities_current = self._find_total(liabilities, 'current', ['total liabilit'])
        total_liabilities_previous = self._find_total(liabilities, 'previous', ['total liabilit'])
        
        total_equity_current = self._find_total(equity, 'current', ['total equity', 'equity'])
        total_equity_previous = self._find_total(equity, 'previous', ['total equity', 'equity'])
        
        # Validation 1: Assets = Liabilities + Equity (Current Year)
        if total_assets_current and total_liabilities_current and total_equity_current:
            total_validations += 1
            calculated_assets = total_liabilities_current + total_equity_current
            if self._is_close(total_assets_current, calculated_assets):
                validations_passed += 1
            else:
                diff = abs(total_assets_current - calculated_assets)
                issues.append(f"Current year: Assets ({total_assets_current:,.0f}) != Liabilities + Equity ({calculated_assets:,.0f}), diff: {diff:,.0f}")
        
        # Validation 2: Assets = Liabilities + Equity (Previous Year)
        if total_assets_previous and total_liabilities_previous and total_equity_previous:
            total_validations += 1
            calculated_assets = total_liabilities_previous + total_equity_previous
            if self._is_close(total_assets_previous, calculated_assets):
                validations_passed += 1
            else:
                diff = abs(total_assets_previous - calculated_assets)
                issues.append(f"Previous year: Assets ({total_assets_previous:,.0f}) != Liabilities + Equity ({calculated_assets:,.0f}), diff: {diff:,.0f}")
        
        # Validation 3: Check for required fields
        required_fields = ['property', 'cash', 'equity', 'share capital']
        total_validations += len(required_fields)
        
        all_items = {**assets, **liabilities, **equity}
        for field in required_fields:
            if self._has_field(all_items, field):
                validations_passed += 1
            else:
                issues.append(f"Missing required field: {field}")
        
        # Calculate confidence score
        confidence = validations_passed / total_validations if total_validations > 0 else 0.0
        is_valid = confidence >= 0.7  # 70% threshold
        
        return is_valid, confidence, issues
    
    def validate_income_statement(self, income_statement: Dict) -> Tuple[bool, float, List[str]]:
        """
        Validate income statement calculations
        Returns: (is_valid, confidence_score, issues)
        """
        issues = []
        validations_passed = 0
        total_validations = 0
        
        line_items = income_statement.get('line_items', {})
        
        # Find key items
        revenue_current = self._find_value(line_items, 'current', ['revenue', 'sales'])
        cost_of_sales_current = self._find_value(line_items, 'current', ['cost of sales'])
        gross_profit_current = self._find_value(line_items, 'current', ['gross profit'])
        
        net_profit_current = self._find_value(line_items, 'current', ['profit after', 'profit for the year', 'net income'])
        
        # Validation 1: Revenue - Cost of Sales = Gross Profit
        if revenue_current and cost_of_sales_current and gross_profit_current:
            total_validations += 1
            # Cost of sales is typically negative, so add them
            calculated_gross = revenue_current + cost_of_sales_current
            if self._is_close(calculated_gross, gross_profit_current):
                validations_passed += 1
            else:
                diff = abs(calculated_gross - gross_profit_current)
                issues.append(f"Gross profit mismatch: Revenue ({revenue_current:,.0f}) - Cost ({cost_of_sales_current:,.0f}) = {calculated_gross:,.0f}, but reported {gross_profit_current:,.0f}, diff: {diff:,.0f}")
        
        # Validation 2: Check for required fields
        required_fields = ['revenue', 'profit', 'expense']
        total_validations += len(required_fields)
        
        for field in required_fields:
            if self._has_field(line_items, field):
                validations_passed += 1
            else:
                issues.append(f"Missing required field: {field}")
        
        # Validation 3: Revenue should be positive
        if revenue_current:
            total_validations += 1
            if revenue_current > 0:
                validations_passed += 1
            else:
                issues.append(f"Revenue should be positive, got: {revenue_current:,.0f}")
        
        # Validation 4: Net profit should exist
        if net_profit_current is not None:
            total_validations += 1
            validations_passed += 1
        else:
            issues.append("Net profit not found")
        
        confidence = validations_passed / total_validations if total_validations > 0 else 0.0
        is_valid = confidence >= 0.6  # 60% threshold for income statement
        
        return is_valid, confidence, issues
    
    def validate_cash_flow(self, cash_flow: Dict) -> Tuple[bool, float, List[str]]:
        """
        Validate cash flow statement
        Returns: (is_valid, confidence_score, issues)
        """
        issues = []
        validations_passed = 0
        total_validations = 3
        
        operating = cash_flow.get('operating_activities', {})
        investing = cash_flow.get('investing_activities', {})
        financing = cash_flow.get('financing_activities', {})
        
        # Check for required sections
        if operating:
            validations_passed += 1
        else:
            issues.append("Operating activities section empty")
        
        if investing:
            validations_passed += 1
        else:
            issues.append("Investing activities section empty")
        
        if financing:
            validations_passed += 1
        else:
            issues.append("Financing activities section empty")
        
        confidence = validations_passed / total_validations
        is_valid = confidence >= 0.67  # At least 2 out of 3 sections
        
        return is_valid, confidence, issues
    
    def validate_all(self, extracted_data: Dict) -> Dict:
        """
        Validate all extracted statements
        Returns: validation summary with scores and issues
        """
        results = {
            'overall_valid': False,
            'overall_confidence': 0.0,
            'balance_sheet': {},
            'income_statement': {},
            'cash_flow': {},
            'all_issues': []
        }
        
        # Validate Balance Sheet
        if 'balance_sheet' in extracted_data:
            bs_valid, bs_conf, bs_issues = self.validate_balance_sheet(extracted_data['balance_sheet'])
            results['balance_sheet'] = {
                'valid': bs_valid,
                'confidence': bs_conf,
                'issues': bs_issues
            }
            results['all_issues'].extend([f"BS: {issue}" for issue in bs_issues])
        
        # Validate Income Statement
        if 'income_statement' in extracted_data:
            is_valid, is_conf, is_issues = self.validate_income_statement(extracted_data['income_statement'])
            results['income_statement'] = {
                'valid': is_valid,
                'confidence': is_conf,
                'issues': is_issues
            }
            results['all_issues'].extend([f"IS: {issue}" for issue in is_issues])
        
        # Validate Cash Flow
        if 'cash_flow' in extracted_data:
            cf_valid, cf_conf, cf_issues = self.validate_cash_flow(extracted_data['cash_flow'])
            results['cash_flow'] = {
                'valid': cf_valid,
                'confidence': cf_conf,
                'issues': cf_issues
            }
            results['all_issues'].extend([f"CF: {issue}" for issue in cf_issues])
        
        # Calculate overall confidence
        confidences = [
            results['balance_sheet'].get('confidence', 0),
            results['income_statement'].get('confidence', 0),
            results['cash_flow'].get('confidence', 0)
        ]
        results['overall_confidence'] = sum(confidences) / len(confidences) if confidences else 0.0
        results['overall_valid'] = results['overall_confidence'] >= 0.6
        
        return results
    
    def _find_total(self, items: Dict, year_key: str, keywords: List[str]) -> float:
        """Find total value from items dict"""
        for name, values in items.items():
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in keywords):
                value = values.get(year_key)
                if value is not None:
                    return value
        return None
    
    def _find_value(self, items: Dict, year_key: str, keywords: List[str]) -> float:
        """Find value from items dict based on keywords"""
        for name, values in items.items():
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in keywords):
                value = values.get(year_key)
                if value is not None:
                    return value
        return None
    
    def _has_field(self, items: Dict, keyword: str) -> bool:
        """Check if any item name contains keyword"""
        for name in items.keys():
            if keyword.lower() in name.lower():
                return True
        return False
    
    def _is_close(self, value1: float, value2: float) -> bool:
        """Check if two values are close within tolerance"""
        if value1 == 0 and value2 == 0:
            return True
        if value1 == 0 or value2 == 0:
            return abs(value1 - value2) < 1000  # Small absolute difference
        
        percentage_diff = abs(value1 - value2) / max(abs(value1), abs(value2))
        return percentage_diff <= self.tolerance
