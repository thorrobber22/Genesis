"""
API Routes with proper IPO data mapping
Date: 2025-06-14 17:58:42 UTC
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Dict, Optional
from backend.services.data_service import DataService
from pathlib import Path
import json

router = APIRouter()
data_service = DataService()

def format_ipo_for_display(ipo: Dict) -> Dict:
    """Format IPO data for frontend display with ALL fields"""
    
    # Format the display data properly
    formatted = {
        # Date should show expected trade date
        'expected_date': ipo.get('expected_date', 'TBD'),
        
        # Core fields
        'ticker': ipo.get('ticker', ''),
        'company': ipo.get('company', ''),
        
        # Financial data
        'price_range': ipo.get('price_range', 'TBD'),
        'price_low': ipo.get('price_low', 0),
        'price_high': ipo.get('price_high', 0),
        'shares': f"{ipo.get('shares_millions', 0):.1f}M" if ipo.get('shares_millions') else '-',
        'volume': ipo.get('volume', '-'),
        
        # Status and metadata
        'status': ipo.get('status', 'Expected'),
        'documents': ipo.get('filing_count', 0),
        'lockup': ipo.get('lockup', '180 days'),
        
        # Additional fields
        'lead_managers': ipo.get('lead_managers', '-'),
        'scoop_rating': ipo.get('scoop_rating', '-'),
        'exchange': ipo.get('exchange', 'TBD'),
    }
    
    return formatted

@router.get("/calendar")
async def get_ipo_calendar(
    period: str = Query("all"),
    status: str = Query("all")
) -> List[Dict]:
    """Get IPO calendar with proper data"""
    
    # Get real data
    listings = data_service.get_ipo_calendar({'period': period, 'status': status})
    
    # Format for display
    formatted = [format_ipo_for_display(ipo) for ipo in listings]
    
    print(f"📊 API: Returning {len(formatted)} IPOs")
    if formatted:
        print(f"   First: {formatted[0].get('ticker')} - {formatted[0].get('expected_date')}")
    
    return formatted

@router.get("/companies/tree")
async def get_companies_tree() -> Dict:
    """Get companies organized by sector"""
    return data_service.get_companies_tree()

@router.get("/company/{ticker}")
async def get_company_details(ticker: str) -> Dict:
    """Get company details"""
    profile = data_service.get_company_profile(ticker)
    if not profile:
        raise HTTPException(status_code=404, detail="Company not found")
    
    profile['documents'] = data_service.get_company_documents(ticker)
    return profile

@router.get("/watchlist")
async def get_watchlist() -> Dict:
    """Get watchlist"""
    return {'tickers': data_service.get_watchlist()}

@router.post("/watchlist/{ticker}")
async def update_watchlist(ticker: str, action: str = "add") -> Dict:
    """Update watchlist"""
    success = data_service.update_watchlist(ticker, action)
    return {'success': success}
