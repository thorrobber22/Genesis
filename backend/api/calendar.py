"""
Calendar API endpoints
"""

from fastapi import APIRouter, Query
from typing import List, Dict, Optional

from backend.services.data_service import DataService

router = APIRouter()
data_service = DataService()

@router.get("")
async def get_calendar(
    period: Optional[str] = Query("all", description="Filter by period"),
    status: Optional[str] = Query("all", description="Filter by status")
) -> List[Dict]:
    """Get IPO calendar data"""
    
    # Get all IPOs
    ipos = data_service.get_ipo_calendar()
    
    # Apply filters if needed
    # For now, return all
    return ipos

@router.get("/{ticker}")
async def get_ipo_details(ticker: str) -> Dict:
    """Get details for specific IPO"""
    
    return data_service.get_company_profile(ticker)
