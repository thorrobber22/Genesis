"""
sec_service.py - SEC EDGAR API integration
Date: 2025-06-12 01:25:00 UTC
User: thorrobber22
"""

import requests
import json
from datetime import datetime

# SEC EDGAR base URL
EDGAR_BASE = "https://data.sec.gov"
EDGAR_ARCHIVES = "https://www.sec.gov/Archives/edgar/data"

# Headers required by SEC
HEADERS = {
    'User-Agent': 'Hedge Intelligence thorrobber22@email.com',
    'Accept': 'application/json'
}

def get_company_filings(cik, form_type=None):
    """Get company filings from SEC EDGAR"""
    try:
        # Pad CIK to 10 digits
        cik = str(cik).zfill(10)
        
        # Get submissions
        url = f"{EDGAR_BASE}/submissions/CIK{cik}.json"
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            filings = []
            
            recent = data.get('filings', {}).get('recent', {})
            forms = recent.get('form', [])
            dates = recent.get('filingDate', [])
            accessions = recent.get('accessionNumber', [])
            
            for i in range(min(len(forms), 20)):  # Last 20 filings
                if not form_type or forms[i] == form_type:
                    filings.append({
                        'form': forms[i],
                        'filing_date': dates[i],
                        'accession': accessions[i].replace('-', ''),
                        'url': f"{EDGAR_ARCHIVES}/{cik}/{accessions[i].replace('-', '')}/{accessions[i]}.txt"
                    })
            
            return filings
        else:
            return []
    except Exception as e:
        print(f"SEC API Error: {e}")
        return []

def get_filing_content(url):
    """Get filing content from URL"""
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.text
        return ""
    except:
        return ""

def search_company(name):
    """Search for company by name"""
    try:
        url = f"{EDGAR_BASE}/cgi-bin/cik_lookup"
        params = {'company': name}
        response = requests.get(url, params=params, headers=HEADERS)
        # Parse response and return CIK
        return "0001234567"  # Placeholder
    except:
        return None

def get_recent_s1_filings(days=30):
    """Get recent S-1 filings"""
    # Placeholder - would use EDGAR full-text search
    return [
        {
            'company': 'Recent IPO Corp',
            'cik': '0001234567',
            'filing_date': '2025-06-10',
            'form': 'S-1'
        }
    ]


def extract_financial_data(filing_content):
    """Extract financial data from SEC filing"""
    try:
        # This would use regex/parsing to extract financial tables
        # For now, return mock data
        return {
            "revenue": {
                "2024": 580000000,
                "2023": 380000000,
                "2022": 210000000
            },
            "net_income": {
                "2024": -120000000,
                "2023": -95000000,
                "2022": -78000000
            },
            "cash_burn": {
                "quarterly": 45000000,
                "runway_months": 18
            }
        }
    except Exception as e:
        return {}

def get_s1_financial_summary(cik):
    """Get financial summary from S-1 filing"""
    filings = get_company_filings(cik, "S-1")
    if filings:
        content = get_filing_content(filings[0]["url"])
        return extract_financial_data(content)
    return {}
