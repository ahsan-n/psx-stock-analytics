# Financial Report Structure Analysis

## Executive Summary

After thorough analysis of FCCL and MLCF reports, I've identified the key patterns and structures needed for automated extraction.

---

## FCCL (Fauji Cement Company Limited) - Annual Reports

### Document Structure
- **Total Pages**: ~287-345 pages
- **Financial Statements Location**: Pages 188-194
- **Format**: Audited Annual Financial Statements

### Statement Locations (2023-24 Report)

| Statement | Page Number | Header Text |
|-----------|-------------|-------------|
| Balance Sheet (Assets/Liabilities) | 190-191 | "STATEMENT OF FINANCIAL POSITION" |
| Income Statement | 192 | "STATEMENT OF PROFIT OR LOSS" |
| Comprehensive Income | 193 | "STATEMENT OF COMPREHENSIVE INCOME" |
| Cash Flow | 194 | "STATEMENT OF CASH FLOWS" |

### Balance Sheet Structure (Page 190-191)

**LEFT SIDE - EQUITY & LIABILITIES (Page 190):**
```
EQUITY AND RESERVES
- Share capital: 24,528,476
- Capital reserve - Premium: 15,253,134
- Revenue reserve - Accumulated profits: 33,617,243
Total: 73,398,853

NON-CURRENT LIABILITIES
- Long term loans - secured: 29,908,287
- Employee benefits: 250,230
- Lease liabilities: 117,454
- Deferred government grant: 2,164,959
- Deferred tax liabilities: 14,931,049
Total: 47,371,979

CURRENT LIABILITIES
- Loan from Parent: 7,387,000
- Trade and other payables: 5,966,191
- Accrued liabilities: 5,154,131
- Short term running finance: 1,450,934
- ... (10+ more items)
Total: 26,865,467

TOTAL EQUITY AND LIABILITIES: 147,636,299
```

**RIGHT SIDE - ASSETS (Page 191):**
```
NON-CURRENT ASSETS
- Property, plant and equipment: 110,845,663
- Right of use asset: 131,165
- Intangible assets and goodwill: 10,745,700
- Long term deposits: 129,700
Total: 121,852,228

CURRENT ASSETS
- Stores, spares and loose tools: 9,099,130
- Stock in trade: 7,495,705
- Trade debts: 5,545,241
- Advances: 145,244
- Cash and bank balances: 2,932,984
- ... (5+ more items)
Total: 25,784,071

TOTAL ASSETS: 147,636,299
```

### Income Statement Structure (Page 192)

```
Revenue - net: 80,026,226
Cost of sales: (54,345,821)
Gross profit: 25,680,405

Other income: 540,373
Selling and distribution expenses: (3,285,923)
Administrative expenses: (1,516,046)
Other expenses: (826,875)
Operating profit: 20,591,934

Finance cost: (5,536,298)
Finance income: 299,318
Net finance cost: (5,236,980)

Profit before income tax: 15,354,954
Final tax - levy: (55,223)
Income tax expense: (7,076,615)
Profit for the year: 8,223,116

Earnings per share: 3.35
```

### Cash Flow Structure (Page 194)

```
OPERATING ACTIVITIES
Profit before tax: 15,354,954
Adjustments: 9,787,476
Operating cash before WC changes: 25,142,430
Working capital changes: (782,030)
Cash from operations: 24,360,400
Payments (tax, benefits, etc.): (2,675,793)
Net cash from operating: 21,684,607

INVESTING ACTIVITIES
Purchase of PPE: (8,478,876)
Proceeds from disposal: 21,522
Income received: 299,318
Net cash from investing: (8,158,037)

FINANCING ACTIVITIES
Loan repayments: (2,053,004)
New loans: 644,239
Finance cost paid: (6,993,060)
Dividend paid: (355)
Net cash from financing: (8,479,996)

NET INCREASE IN CASH: 5,046,574
```

---

## MLCF (Maple Leaf Cement Factory) - Quarterly Reports

### Document Structure
- **Quarterly Reports**: ~40-50 pages
- **Annual Reports**: ~376-401 pages
- **Financial Statements Location**: Pages 7-12 (Quarterly)
- **Format**: Condensed Interim (Quarterly) / Full Audited (Annual)

### Statement Locations (Q1 2023-24 Report)

| Statement | Page Number | Header Text |
|-----------|-------------|-------------|
| Balance Sheet | 7-8 | "CONDENSED INTERIM UNCONSOLIDATED STATEMENT OF FINANCIAL POSITION" |
| Income Statement | 9 | "CONDENSED INTERIM UNCONSOLIDATED STATEMENT OF PROFIT OR LOSS" |
| Comprehensive Income | 10 | "STATEMENT OF COMPREHENSIVE INCOME" |
| Cash Flow | 11 | "STATEMENT OF CASH FLOWS" |

### Key Differences from FCCL

1. **Unconsolidated vs Consolidated**: MLCF reports both
2. **Quarterly Structure**: Nine months + Three months columns
3. **More Detailed Notes**: Extensive breakdown sections
4. **Different Account Names**: "Stores, spare parts" vs "Stores, spares"

### MLCF Balance Sheet Structure (Page 7-8)

Similar to FCCL but with differences:
- Uses "Surplus on revaluation of fixed assets - net of tax" in equity
- "Long term loan from Subsidiary Company" in liabilities
- "Retention money" as a separate non-current liability
- More detailed payables breakdown

### MLCF Income Statement (Page 9)

**Unique Features:**
- **Four Columns**: 
  - Nine months 2024 | Nine months 2023
  - Three months 2024 | Three months 2023
- Similar structure to FCCL but more granular

---

## Common Patterns Across Both Companies

### Number Format
```
Positive: 80,026,226
Negative: (54,345,821)
Unit: Rupees '000 (thousands)
```

### Column Structure
- **Current Year**: 2024
- **Previous Year**: 2023
- Always two columns for comparison

### Statement Identifiers
1. **"Note"** column indicates line items
2. **"Rupees'000" or "(Rupees in thousand)"** indicates unit
3. **Bold/ALL CAPS** section headers
4. **Indentation** shows hierarchy

---

## Key Extraction Challenges

### 1. Table Detection
- Financial statements are formatted as tables
- Multiple tables span across pages
- pdfplumber struggles with complex layouts

### 2. Line Item Recognition
Pattern: `Line Item Name [Note #] Value2024 Value2023`
- Need to extract item name, current value, previous value
- Need to handle parentheses for negatives
- Need to handle commas in numbers

### 3. Section Boundaries
- Need to detect section totals (e.g., "Total Current Assets")
- Need to identify main sections vs subsections

### 4. Page Continuity
- Balance sheet spans 2 pages (Assets on second page)
- Need to combine data across pages

---

## Extraction Strategy

### Phase 1: Text-Based Extraction
Use regex patterns to extract from text:
```python
# Pattern for line items
r'([A-Z][A-Za-z\s,&-]+)\s+(\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))\s+(\d{1,3}(?:,\d{3})*|\(\d{1,3}(?:,\d{3})*\))'
```

### Phase 2: Table-Based Extraction
Use pdfplumber to extract tables when structured properly

### Phase 3: Hybrid Approach
Combine text patterns with table detection for best results

---

## Validation Rules

### Balance Sheet
```
RULE 1: Total Assets = Total Equity + Total Liabilities
RULE 2: Non-Current Assets + Current Assets = Total Assets
RULE 3: Equity + Non-Current Liabilities + Current Liabilities = Total
```

### Income Statement
```
RULE 1: Revenue - Cost of Sales = Gross Profit
RULE 2: Operating Profit - Net Finance Cost = Profit Before Tax
RULE 3: Profit Before Tax - Tax = Profit After Tax
```

### Cash Flow
```
RULE 1: Operating + Investing + Financing = Net Change in Cash
RULE 2: Beginning Cash + Net Change = Ending Cash
```

---

## Data Extraction Priority

### High Priority (Always Extract)
1. Revenue
2. Gross Profit
3. Operating Profit
4. Profit After Tax
5. Total Assets
6. Total Liabilities
7. Total Equity
8. Cash from Operations

### Medium Priority (Good to Have)
9. Property, Plant & Equipment
10. Trade Debts
11. Current Liabilities
12. Long-term Loans
13. Cost of Sales
14. Administrative Expenses

### Low Priority (Optional)
15. Detailed expense breakdowns
16. Individual working capital items
17. Minor receivables/payables

---

## Next Steps for Parser Implementation

1. ✅ **Understanding Complete**: Structure documented
2. ⏳ **Build Text Extractor**: Regex-based line item extraction
3. ⏳ **Build Table Extractor**: pdfplumber table parsing
4. ⏳ **Build Validator**: Check extraction accuracy
5. ⏳ **Build DB Persister**: Save to enhanced schema
6. ⏳ **Build API**: Endpoints for extraction and retrieval

---

## Sample Extraction Code Structure

```python
def extract_balance_sheet(pdf_path):
    # 1. Locate balance sheet pages
    # 2. Extract text from those pages
    # 3. Parse line items using regex
    # 4. Validate totals
    # 5. Return structured data

def extract_income_statement(pdf_path):
    # Similar approach

def extract_cash_flow(pdf_path):
    # Similar approach

def validate_extraction(balance_sheet, income_statement):
    # Check mathematical relationships
    # Return confidence score
```

---

**Status**: Analysis complete, ready to implement parser
