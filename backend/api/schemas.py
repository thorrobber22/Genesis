"""
Pydantic models for type safety
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class IPOListing(BaseModel):
    ticker: str
    company: str
    date: str
    status: str
    documents: int
    lockup: Optional[str]
    exchange: str

class CompanyProfile(BaseModel):
    ticker: str
    name: str  
    sector: str
    documents: List[str]

class Citation(BaseModel):
    text: str
    section_id: str
    page: int
