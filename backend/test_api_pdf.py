"""
Test PDF Processing API
Demonstrates how to use the PDF processing endpoints
"""
import requests
import json
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"


def login():
    """Login and get access token"""
    print("="*80)
    print("1. AUTHENTICATING")
    print("="*80)
    
    # Try to register (might fail if user exists, that's ok)
    try:
        requests.post(
            f"{API_BASE}/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "full_name": "Test User"
            }
        )
        print("✓ Registered new user")
    except:
        print("✓ User already exists")
    
    # Login
    response = requests.post(
        f"{API_BASE}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ Logged in successfully")
        print(f"  Token: {token[:20]}...")
        return token
    else:
        print(f"✗ Login failed: {response.text}")
        return None


def process_single_pdf(token, pdf_path):
    """Process a single PDF"""
    print("\n" + "="*80)
    print("2. PROCESSING SINGLE PDF")
    print("="*80)
    print(f"PDF: {pdf_path}")
    print("-" * 60)
    
    response = requests.post(
        f"{API_BASE}/pdf/process-pdf",
        json={"pdf_path": pdf_path},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ SUCCESS")
        print(f"  Company: {result.get('company_symbol')} (ID: {result.get('company_id')})")
        print(f"  Report ID: {result.get('report_id')}")
        print(f"  Balance Sheet ID: {result.get('balance_sheet_id')}")
        print(f"  Income Statement ID: {result.get('income_statement_id')}")
        print(f"  Cash Flow ID: {result.get('cash_flow_id')}")
        print(f"  Message: {result.get('message')}")
        return result
    else:
        print(f"\n✗ FAILED")
        print(f"  Status: {response.status_code}")
        print(f"  Error: {response.text}")
        return None


def bulk_process_pdfs(token, directory, pattern="*.pdf"):
    """Bulk process PDFs from a directory"""
    print("\n" + "="*80)
    print("3. BULK PROCESSING PDFs")
    print("="*80)
    print(f"Directory: {directory}")
    print(f"Pattern: {pattern}")
    print("-" * 60)
    
    response = requests.post(
        f"{API_BASE}/pdf/bulk-process",
        json={
            "pdf_directory": directory,
            "pattern": pattern
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ BULK PROCESSING COMPLETE")
        print(f"  Total Files: {result['total_files']}")
        print(f"  Successful: {result['successful']}")
        print(f"  Failed: {result['failed']}")
        
        if result['results']:
            print(f"\n  Detailed Results:")
            for i, r in enumerate(result['results'][:5], 1):  # Show first 5
                status_icon = "✓" if r['success'] else "✗"
                print(f"    {status_icon} {i}. {r.get('company_symbol', 'N/A')}: {r['message']}")
        
        return result
    else:
        print(f"\n✗ FAILED")
        print(f"  Status: {response.status_code}")
        print(f"  Error: {response.text}")
        return None


def get_company_data(token, company_id):
    """Get financial data for a company"""
    print("\n" + "="*80)
    print("4. RETRIEVING COMPANY DATA")
    print("="*80)
    print(f"Company ID: {company_id}")
    print("-" * 60)
    
    response = requests.get(
        f"{API_BASE}/financial/companies/{company_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        company = response.json()
        print(f"\n✓ Company Data:")
        print(f"  Symbol: {company.get('symbol')}")
        print(f"  Name: {company.get('name')}")
        print(f"  Industry: {company.get('industry')}")
        return company
    else:
        print(f"\n✗ Failed to retrieve company data")
        return None


def main():
    """Main test flow"""
    print("\n🧪 TESTING PDF PROCESSING API\n")
    
    # Step 1: Login
    token = login()
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    # Step 2: Process a single MLCF PDF
    mlcf_pdf = str(Path("../reports/MLCF/2020-21/MLCF_2020-21_Q1.pdf").absolute())
    result = process_single_pdf(token, mlcf_pdf)
    
    if result and result.get('company_id'):
        # Step 3: Get company data
        get_company_data(token, result['company_id'])
    
    # Step 4: Bulk process FCCL PDFs (optional, commented out to save time)
    # fccl_dir = str(Path("../reports/FCCL/2023-24").absolute())
    # bulk_process_pdfs(token, fccl_dir)
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\n📝 Next Steps:")
    print("  1. Check the database for saved records")
    print("  2. Query the financial data through the API")
    print("  3. Process more reports as needed")
    print("\n💡 API Documentation: http://localhost:8000/docs")
    print("="*80)


if __name__ == "__main__":
    print("\n⚠️  PREREQUISITES:")
    print("  1. Backend must be running: cd backend && make dev")
    print("  2. Database must be initialized")
    print("  3. Reports must be in ../reports/ directory")
    print("\n  Press Ctrl+C to cancel, or Enter to continue...")
    input()
    
    main()
