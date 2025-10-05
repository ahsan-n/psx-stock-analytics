# Phase 2: PDF Parser & Data Persistence

## Overview

Phase 2 implements a comprehensive PDF parsing system that extracts financial statements from PSX company reports (FCCL and MLCF) and persists them to the PostgreSQL database.

## Architecture

```
┌─────────────────┐
│   PDF Report    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  HybridFinancialExtractor                   │
│  - Company identification                   │
│  - Statement page detection                 │
│  - Text extraction & parsing                │
│  - Data structure assembly                  │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  FinancialDataService                       │
│  - Business logic                           │
│  - Data validation                          │
│  - Database persistence                     │
│  - Transaction management                   │
└────────┬────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────┐
│  PostgreSQL Database                        │
│  - companies                                │
│  - reports                                  │
│  - balance_sheets                           │
│  - income_statements                        │
│  - cash_flow_statements                     │
│  - pdf_extraction_logs                      │
└─────────────────────────────────────────────┘
```

## Components

### 1. PDF Extractors

#### `backend/app/parsers/pdf_extractor.py`
- Basic regex-based extraction
- Pattern matching for financial line items
- Initial proof of concept

#### `backend/app/parsers/table_extractor.py`
- Table-based extraction using pdfplumber
- Handles structured PDF tables
- More robust for well-formatted reports

#### `backend/app/parsers/hybrid_extractor.py` (RECOMMENDED)
- **Production-ready extractor**
- Combines text extraction with intelligent parsing
- Handles various PDF formats and structures
- Features:
  - Company identification (FCCL/MLCF)
  - Report type detection (Annual/Quarterly)
  - Fiscal year and quarter extraction
  - Balance Sheet extraction
  - Income Statement extraction
  - Cash Flow Statement extraction

### 2. Data Validation

#### `backend/app/parsers/validators.py`
- Validates balance sheet equations (Assets = Liabilities + Equity)
- Checks income statement calculations (Revenue - Costs = Profit)
- Ensures required fields are present
- Returns confidence scores and issue lists

### 3. Business Logic Service

#### `backend/app/services/financial_data_service.py`
- `process_pdf_report()`: Main entry point for PDF processing
- `_get_or_create_company()`: Company management
- `_create_report()`: Report record creation
- `_save_balance_sheet()`: Balance sheet persistence
- `_save_income_statement()`: Income statement persistence
- `_save_cash_flow()`: Cash flow persistence
- `_log_extraction()`: Extraction logging for debugging

### 4. API Endpoints

#### `backend/app/api/v1/pdf_processing.py`

##### POST `/api/v1/pdf/process-pdf`
Process a single PDF from file system.

**Request:**
```json
{
  "pdf_path": "/absolute/path/to/report.pdf"
}
```

**Response:**
```json
{
  "success": true,
  "company_id": 1,
  "company_symbol": "FCCL",
  "report_id": 5,
  "balance_sheet_id": 12,
  "income_statement_id": 12,
  "cash_flow_id": 12,
  "message": "Successfully processed FCCL report"
}
```

##### POST `/api/v1/pdf/bulk-process`
Process multiple PDFs from a directory.

**Request:**
```json
{
  "pdf_directory": "/path/to/reports",
  "pattern": "*.pdf"
}
```

**Response:**
```json
{
  "total_files": 10,
  "successful": 8,
  "failed": 2,
  "results": [...]
}
```

##### POST `/api/v1/pdf/upload-and-process`
Upload and process a PDF in one request.

**Request:** Multipart form with PDF file

**Response:** Same as process-pdf

##### GET `/api/v1/pdf/processing-status/{report_id}`
Get processing status and results.

## Database Schema

### Enhanced Schema (from `enhanced_financial_data.py`)

**companies**
- `id`: Primary key
- `symbol`: Stock symbol (FCCL, MLCF)
- `name`: Company name
- `industry`, `sector`: Classification
- `listed_date`: IPO date

**reports**
- `id`: Primary key
- `company_id`: Foreign key to companies
- `report_type`: 'annual' or 'quarterly'
- `quarter`: Q1, Q2, Q3, Q4
- `fiscal_year`: e.g., '2023-24'
- `report_date`: Date of report
- `pdf_path`: Path to PDF file
- `is_audited`: Boolean

**balance_sheets**
- `id`: Primary key
- `report_id`: Foreign key to reports
- Assets:
  - `total_assets`
  - `property_plant_equipment`
  - `cash_and_equivalents`
  - `inventory`
  - `trade_debts`
  - `investments`
  - (many more fields...)
- Liabilities:
  - `total_liabilities`
  - `long_term_debt`
  - `short_term_debt`
  - `trade_payables`
  - (many more fields...)
- Equity:
  - `total_equity`
  - `share_capital`
  - `retained_earnings`
  - `reserves`

**income_statements**
- `id`: Primary key
- `report_id`: Foreign key to reports
- Revenue & Profitability:
  - `revenue`
  - `cost_of_sales`
  - `gross_profit`
  - `operating_expenses`
  - `operating_profit`
  - `net_profit`
- Costs & Expenses:
  - `finance_cost`
  - `tax_expense`
  - (many more fields...)

**cash_flow_statements**
- `id`: Primary key
- `report_id`: Foreign key to reports
- `cash_from_operations`
- `cash_from_investing`
- `cash_from_financing`
- `net_change_in_cash`

**pdf_extraction_logs**
- `id`: Primary key
- `report_id`: Foreign key to reports
- `pdf_path`: Path to source PDF
- `extraction_success`: Boolean
- `error_message`: If failed
- `pages_processed`: Number of pages
- `extracted_at`: Timestamp

## Usage Examples

### 1. Process a Single Report

```python
from app.services.financial_data_service import FinancialDataService
from app.core.database import SessionLocal

db = SessionLocal()
service = FinancialDataService(db)

result = service.process_pdf_report(
    pdf_path="/path/to/FCCL_Annual_2023-24.pdf",
    uploaded_by_user_id=1
)

print(f"Success: {result['success']}")
print(f"Company: {result['company_symbol']}")
print(f"Report ID: {result['report_id']}")
```

### 2. Using the API

```bash
# Login first
curl -X POST http://localhost:8000/api/v1/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"email": "user@example.com", "password": "password"}'

# Process PDF
curl -X POST http://localhost:8000/api/v1/pdf/process-pdf \\
  -H "Authorization: Bearer <token>" \\
  -H "Content-Type: application/json" \\
  -d '{"pdf_path": "/absolute/path/to/report.pdf"}'

# Bulk process
curl -X POST http://localhost:8000/api/v1/pdf/bulk-process \\
  -H "Authorization: Bearer <token>" \\
  -H "Content-Type: application/json" \\
  -d '{"pdf_directory": "/path/to/reports", "pattern": "*.pdf"}'
```

### 3. Test Script

```bash
cd backend
python3 test_api_pdf.py
```

## Extraction Process

### Step 1: Company Identification
- Scans first 10 pages
- Looks for company name keywords
- Identifies FCCL vs MLCF
- Determines report type (Annual/Quarterly)
- Extracts fiscal year and quarter

### Step 2: Statement Detection
- Searches all pages for financial statements
- Identifies:
  - Statement of Financial Position (Balance Sheet)
  - Statement of Profit or Loss (Income Statement)
  - Statement of Cash Flows
- Filters out table of contents pages
- Validates pages have actual data (numbers, notes, rupees)

### Step 3: Data Extraction
- Extracts text from identified pages
- Parses line by line
- Regex patterns match: `ItemName 123,456 789,012`
- Handles:
  - Comma-separated numbers
  - Multiple columns (current/previous year)
  - Negative values
  - Section headers

### Step 4: Data Categorization
- **Balance Sheet**:
  - Assets: keywords like 'property', 'cash', 'inventory'
  - Liabilities: keywords like 'loan', 'payable', 'debt'
  - Equity: keywords like 'capital', 'reserves', 'equity'
- **Income Statement**:
  - All line items with revenue/cost/profit keywords
- **Cash Flow**:
  - Sections: Operating, Investing, Financing activities

### Step 5: Persistence
- Get or create company record
- Create report record
- Extract and save key financial metrics
- Log extraction attempt (success/failure)
- Commit transaction

## Known Limitations

1. **PDF Format Dependency**
   - Works best with text-based PDFs
   - Struggles with scanned images
   - Table detection varies by PDF structure

2. **Regex Pattern Matching**
   - May miss items with unusual formatting
   - Sensitive to whitespace and line breaks
   - Requires exact number patterns

3. **Data Completeness**
   - Not all line items are captured
   - Focuses on key financial metrics
   - Some complex multi-page tables may be incomplete

4. **Validation**
   - Basic accounting equation checks
   - May not catch all data quality issues
   - Confidence scores are estimates

## Future Enhancements

1. **AI-Powered Extraction**
   - Use GPT-4 Vision for complex PDFs
   - Better table understanding
   - Context-aware field mapping

2. **Enhanced Validation**
   - Cross-statement validation
   - Historical trend analysis
   - Outlier detection

3. **More Financial Metrics**
   - Automatic ratio calculations
   - YoY growth rates
   - Quarter-over-quarter analysis

4. **UI Integration**
   - Upload interface in frontend
   - Real-time processing status
   - Visual data verification

5. **Support More Companies**
   - Extend to all PSX companies
   - Handle diverse report formats
   - Industry-specific metrics

## Testing

### Unit Tests
```bash
cd backend
pytest tests/test_parsers.py
pytest tests/test_services.py
```

### Integration Tests
```bash
python3 test_parser.py  # Test extractors directly
python3 test_api_pdf.py  # Test full API flow
```

### Manual Testing
1. Start backend: `make dev`
2. Open API docs: http://localhost:8000/docs
3. Try the `/pdf/process-pdf` endpoint
4. Check database for saved records

## Troubleshooting

### Issue: "No tables found"
- PDF may not have detectable tables
- Try `hybrid_extractor.py` instead of `table_extractor.py`

### Issue: "Balance sheet confidence 0%"
- Statement page not detected correctly
- Check page detection keywords
- May need custom patterns for specific company

### Issue: "Missing required field: revenue"
- Extractor couldn't find revenue line
- Check regex patterns in `_parse_income_statement_text`
- May need to add alternative keywords

### Issue: Database errors
- Ensure migrations are run: `make migrate`
- Check database connection in `.env`
- Verify schema matches models

## Performance

- **Processing Time**: ~2-5 seconds per PDF
- **Memory Usage**: ~50-100MB per PDF
- **Concurrent Processing**: Supports multiple requests
- **Rate Limiting**: None currently (add if needed)

## Security

- **Authentication Required**: All endpoints require JWT token
- **Path Validation**: Validates file paths exist
- **SQL Injection Protection**: Using SQLAlchemy ORM
- **Input Sanitization**: Pydantic models validate inputs

## Monitoring

Check `pdf_extraction_logs` table:
```sql
SELECT 
  pdf_path,
  extraction_success,
  error_message,
  pages_processed,
  extracted_at
FROM pdf_extraction_logs
ORDER BY extracted_at DESC
LIMIT 10;
```

## Conclusion

Phase 2 provides a robust foundation for extracting financial data from PDF reports and storing it in a structured database. The hybrid extraction approach balances accuracy with flexibility, while the service layer ensures data integrity and proper error handling.

**Next Step**: Phase 3 will build the AI layer for querying this data using natural language.
