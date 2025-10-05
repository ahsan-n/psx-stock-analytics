# Phase 2: PDF Data Extraction Analysis

## Reports Available

### FCCL (Fauji Cement Company Limited)
- **Years**: 2020-21, 2021-22, 2022-23, 2023-24, 2024-25
- **Periods**: Annual + Q1, Q2, Q3 for each year
- **Total**: 20 reports
- **Structure**: Well-organized in `/reports/FCCL/`

### MLCF (Maple Leaf Cement Factory)
- **Files**: 18 numbered PDF files in root directory
- **Years**: Appears to cover 2020-2022 based on initial analysis
- **Structure**: Needs organization

## Financial Statement Structure (from FCCL 2023-24)

### Statement of Financial Position (Balance Sheet) - Page 191
Found detailed asset and liability classifications:

**Non-Current Assets:**
- Property, plant and equipment
- Right of use asset
- Intangible assets and goodwill
- Long term deposits

**Current Assets:**
- Stores, spares and loose tools
- Stock in trade
- Trade debts
- Advances
- Sales tax refundable-net
- Trade deposits and short term prepayments
- Advance tax - net
- Other receivables
- Short term investments
- Cash and bank balances

**Equity:**
- Share capital
- Premium/(Discount) on issue of shares
- Accumulated profits/retained earnings

**Non-Current Liabilities:**
- Long term loans - secured
- Employee benefits
- Lease liabilities
- Deferred government grant
- Deferred tax liabilities - net

**Current Liabilities:**
- Loan from Parent - unsecured
- Trade and other payables
- Accrued liabilities
- Security deposits payable
- Contract liabilities
- Employee benefits - current portion
- Payable to employees' provident fund trust
- Unclaimed dividend
- Short term borrowings
- Provision for tax-net
- Current portion of lease liability
- Current portion of long term loans
- Current portion of deferred government grant

### Statement of Profit or Loss (Income Statement)
Typically includes:
- Revenue from contracts
- Cost of sales
- Gross profit
- Operating expenses (Distribution, Administrative)
- Operating profit
- Finance cost
- Other income
- Profit before tax
- Taxation
- Profit after tax

### Statement of Cash Flows - Page 194
**Operating Activities:**
- Cash receipts from customers
- Cash paid to vendors & employees
- Taxes paid
- Net cash from operations

**Investing Activities:**
- Additions in PPE
- Proceeds from disposal
- Income from investments

**Financing Activities:**
- Repayment of loans
- New loan disbursements
- Dividend paid
- Finance cost paid

## Enhanced Database Schema Requirements

### Current Schema Limitations
- Only 9 generic metrics per statement
- No detailed breakdown of assets/liabilities
- Missing important line items
- No support for notes/references

### Required Enhancements

1. **Detailed Balance Sheet Fields** (30+ line items)
2. **Detailed Income Statement Fields** (15+ line items)
3. **Detailed Cash Flow Fields** (15+ line items)
4. **Additional Metadata**:
   - Report type (Annual/Quarterly)
   - Auditor information
   - Notes references
   - Currency unit
   - Thousands/Millions indicator

5. **Comparative Data Support**:
   - Current year vs previous year
   - Year-over-year change percentages

## PDF Parsing Challenges

1. **Table Detection**: Financial statements are in tabular format
2. **Multi-Page Tables**: Tables span multiple pages
3. **Formatting Variations**: Different report formats between companies
4. **Text Extraction Quality**: PyPDF2 sometimes struggles with formatting
5. **Number Parsing**: Need to handle thousands, millions, brackets for negatives

## Implementation Strategy

### Step 1: Organize MLCF Reports
- Analyze each numbered PDF to determine period
- Create `/reports/MLCF/` directory structure
- Rename files appropriately

### Step 2: Enhanced Database Schema
- Create migration for detailed financial line items
- Add support for comparative periods
- Add metadata fields

### Step 3: PDF Parser Development
- Use pdfplumber or camelot for better table extraction
- Build pattern matching for financial statements
- Create validation rules

### Step 4: Data Extraction Pipeline
- Extract from all FCCL reports first (well-organized)
- Validate extraction accuracy
- Extract from MLCF reports
- Store in database

### Step 5: Update Frontend
- Display additional fields in tables
- Add more detailed charts
- Show year-over-year comparisons

## Next Steps

1. ✅ Analysis complete
2. ⏳ Organize MLCF reports
3. ⏳ Design enhanced schema
4. ⏳ Build PDF parser
5. ⏳ Extract and validate data
6. ⏳ Update frontend
