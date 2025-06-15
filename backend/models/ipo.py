# backend/models/ipo.py (NOT ipo_model.py)
"""IPO Data Models"""

from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime

class LockupCitation(BaseModel):
    """Individual lockup mention in document"""
    text: str
    days: int
    context: str
    page: Optional[int] = None
    section: Optional[str] = None
    confidence: float

class LockupMetadata(BaseModel):
    """Complete lockup information as metadata"""
    period_days: Optional[int] = None
    citations: List[LockupCitation] = []
    verified_by_ai: bool = False
    confidence_score: float = 0.0
    last_updated: datetime

class IPOListing(BaseModel):
    """IPO listing with all metadata"""
    # Basic fields
    ticker: str
    company: str
    cik: Optional[str] = None
    
    # IPO details
    exchange: str
    price_range: str
    shares: str
    expected_date: str
    status: str
    
    # Metadata (lockup is just another field!)
    sector: Optional[str] = None
    lockup: Optional[LockupMetadata] = None
    
    # Documents
    filing_count: int = 0
    filings: List[Dict] = []
    
    # Validation
    validation_status: Optional[Dict] = None
    profile: Optional[str] = None

class IPOFilter(BaseModel):
    """Filter parameters for calendar"""
    period: str = "all"
    status: str = "all"
    exchange: Optional[str] = None