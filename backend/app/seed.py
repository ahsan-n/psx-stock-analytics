"""
Seed script to populate database with mock FCCL financial data
Run with: docker-compose exec backend python -m app.seed
"""
from datetime import date
from app.core.database import SessionLocal
from app.models.financial_data import (
    Company, FinancialStatement, FinancialMetric, FinancialRatio,
    PeriodType, StatementType
)


def create_company(db):
    """Create FCCL company"""
    company = Company(
        symbol="FCCL",
        name="Fauji Cement Company Limited",
        sector="Cement"
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def create_income_statement(db, company_id, fiscal_year, quarter, period_type):
    """Create income statement with metrics"""
    # Mock data - adjust based on period
    base_revenue = 12000000000 if period_type == PeriodType.ANNUAL else 3000000000
    multiplier = 1 + (fiscal_year - 2022) * 0.1  # 10% growth per year
    quarter_factor = quarter * 0.05 if quarter else 0  # Seasonal variation
    
    statement = FinancialStatement(
        company_id=company_id,
        statement_type=StatementType.INCOME_STATEMENT,
        period_type=period_type,
        fiscal_year=fiscal_year,
        quarter=quarter,
        period_end_date=date(fiscal_year, 3 * quarter if quarter else 12, 28 if quarter else 31)
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    
    # Add metrics
    metrics_data = [
        ("revenue", "Revenue", base_revenue * multiplier * (1 + quarter_factor)),
        ("cost_of_sales", "Cost of Sales", base_revenue * multiplier * 0.65 * (1 + quarter_factor)),
        ("gross_profit", "Gross Profit", base_revenue * multiplier * 0.35 * (1 + quarter_factor)),
        ("operating_expenses", "Operating Expenses", base_revenue * multiplier * 0.15 * (1 + quarter_factor)),
        ("operating_profit", "Operating Profit", base_revenue * multiplier * 0.20 * (1 + quarter_factor)),
        ("finance_cost", "Finance Cost", base_revenue * multiplier * 0.03 * (1 + quarter_factor)),
        ("profit_before_tax", "Profit Before Tax", base_revenue * multiplier * 0.17 * (1 + quarter_factor)),
        ("tax_expense", "Tax Expense", base_revenue * multiplier * 0.05 * (1 + quarter_factor)),
        ("net_income", "Net Income", base_revenue * multiplier * 0.12 * (1 + quarter_factor)),
    ]
    
    for metric_name, metric_label, value in metrics_data:
        metric = FinancialMetric(
            statement_id=statement.id,
            company_id=company_id,
            metric_name=metric_name,
            metric_label=metric_label,
            value=value,
            unit="PKR"
        )
        db.add(metric)
    
    db.commit()


def create_balance_sheet(db, company_id, fiscal_year, quarter, period_type):
    """Create balance sheet with metrics"""
    base_assets = 50000000000 if period_type == PeriodType.ANNUAL else 48000000000
    multiplier = 1 + (fiscal_year - 2022) * 0.08
    
    statement = FinancialStatement(
        company_id=company_id,
        statement_type=StatementType.BALANCE_SHEET,
        period_type=period_type,
        fiscal_year=fiscal_year,
        quarter=quarter,
        period_end_date=date(fiscal_year, 3 * quarter if quarter else 12, 28 if quarter else 31)
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    
    metrics_data = [
        ("cash", "Cash and Cash Equivalents", base_assets * multiplier * 0.08),
        ("receivables", "Trade Receivables", base_assets * multiplier * 0.12),
        ("inventory", "Inventory", base_assets * multiplier * 0.15),
        ("current_assets", "Current Assets", base_assets * multiplier * 0.35),
        ("ppe", "Property, Plant & Equipment", base_assets * multiplier * 0.55),
        ("intangibles", "Intangible Assets", base_assets * multiplier * 0.05),
        ("non_current_assets", "Non-Current Assets", base_assets * multiplier * 0.65),
        ("total_assets", "Total Assets", base_assets * multiplier),
        ("current_liabilities", "Current Liabilities", base_assets * multiplier * 0.20),
        ("long_term_debt", "Long-Term Debt", base_assets * multiplier * 0.25),
        ("total_liabilities", "Total Liabilities", base_assets * multiplier * 0.45),
        ("share_capital", "Share Capital", base_assets * multiplier * 0.30),
        ("retained_earnings", "Retained Earnings", base_assets * multiplier * 0.25),
        ("total_equity", "Total Equity", base_assets * multiplier * 0.55),
    ]
    
    for metric_name, metric_label, value in metrics_data:
        metric = FinancialMetric(
            statement_id=statement.id,
            company_id=company_id,
            metric_name=metric_name,
            metric_label=metric_label,
            value=value,
            unit="PKR"
        )
        db.add(metric)
    
    db.commit()


def create_cash_flow(db, company_id, fiscal_year, quarter, period_type):
    """Create cash flow statement with metrics"""
    base_cash_flow = 4000000000 if period_type == PeriodType.ANNUAL else 1000000000
    multiplier = 1 + (fiscal_year - 2022) * 0.12
    
    statement = FinancialStatement(
        company_id=company_id,
        statement_type=StatementType.CASH_FLOW,
        period_type=period_type,
        fiscal_year=fiscal_year,
        quarter=quarter,
        period_end_date=date(fiscal_year, 3 * quarter if quarter else 12, 28 if quarter else 31)
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)
    
    metrics_data = [
        ("operating_cash_flow", "Cash from Operating Activities", base_cash_flow * multiplier * 1.2),
        ("investing_cash_flow", "Cash from Investing Activities", -base_cash_flow * multiplier * 0.8),
        ("financing_cash_flow", "Cash from Financing Activities", -base_cash_flow * multiplier * 0.3),
        ("net_cash_flow", "Net Change in Cash", base_cash_flow * multiplier * 0.1),
        ("beginning_cash", "Cash at Beginning", base_cash_flow * multiplier * 2.0),
        ("ending_cash", "Cash at End", base_cash_flow * multiplier * 2.1),
    ]
    
    for metric_name, metric_label, value in metrics_data:
        metric = FinancialMetric(
            statement_id=statement.id,
            company_id=company_id,
            metric_name=metric_name,
            metric_label=metric_label,
            value=value,
            unit="PKR"
        )
        db.add(metric)
    
    db.commit()


def create_financial_ratios(db, company_id, fiscal_year, quarter, period_type):
    """Create financial ratios"""
    # Mock ratios with slight variation by year
    year_factor = 1 + (fiscal_year - 2022) * 0.02
    
    ratio = FinancialRatio(
        company_id=company_id,
        fiscal_year=fiscal_year,
        quarter=quarter,
        period_type=period_type,
        # Profitability
        gross_profit_margin=35.2 * year_factor,
        operating_profit_margin=20.5 * year_factor,
        net_profit_margin=12.3 * year_factor,
        return_on_assets=8.5 * year_factor,
        return_on_equity=15.2 * year_factor,
        # Liquidity
        current_ratio=1.75 * year_factor,
        quick_ratio=1.2 * year_factor,
        cash_ratio=0.4 * year_factor,
        # Leverage
        debt_to_equity=0.82 * year_factor,
        debt_to_assets=0.45 * year_factor,
        equity_multiplier=1.82 * year_factor,
        # Efficiency
        asset_turnover=0.7 * year_factor,
        inventory_turnover=8.5 * year_factor,
        receivables_turnover=12.3 * year_factor,
    )
    db.add(ratio)
    db.commit()


def seed_database():
    """Main seeding function"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing = db.query(Company).filter(Company.symbol == "FCCL").first()
        if existing:
            print("⚠️  Data already exists. Skipping seed.")
            return
        
        print("🌱 Seeding database with FCCL mock data...")
        
        # Create company
        company = create_company(db)
        print(f"✅ Created company: {company.name} ({company.symbol})")
        
        # Create financial data for 3 years (2022, 2023, 2024)
        for year in [2022, 2023, 2024]:
            print(f"\n📅 Creating data for FY{year}...")
            
            # Annual statements
            create_income_statement(db, company.id, year, None, PeriodType.ANNUAL)
            create_balance_sheet(db, company.id, year, None, PeriodType.ANNUAL)
            create_cash_flow(db, company.id, year, None, PeriodType.ANNUAL)
            create_financial_ratios(db, company.id, year, None, PeriodType.ANNUAL)
            print(f"  ✅ Annual statements created")
            
            # Quarterly statements
            for quarter in [1, 2, 3, 4]:
                create_income_statement(db, company.id, year, quarter, PeriodType.QUARTERLY)
                create_balance_sheet(db, company.id, year, quarter, PeriodType.QUARTERLY)
                create_cash_flow(db, company.id, year, quarter, PeriodType.QUARTERLY)
                create_financial_ratios(db, company.id, year, quarter, PeriodType.QUARTERLY)
            print(f"  ✅ Quarterly statements created (Q1-Q4)")
        
        print("\n✅ Database seeding completed successfully!")
        print(f"📊 Created data for {company.symbol} - {company.name}")
        print("   - 3 fiscal years (2022-2024)")
        print("   - Annual and quarterly statements")
        print("   - Income Statement, Balance Sheet, Cash Flow")
        print("   - Financial ratios")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
