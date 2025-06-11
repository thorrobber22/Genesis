"""
Hedge Intelligence Configuration
Generated: 2025-06-05 13:15:41 UTC
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
VECTOR_DIR = DATA_DIR / "vectors"
EXPORT_DIR = BASE_DIR / "exports"
LOG_DIR = BASE_DIR / "logs"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Server Configuration
ADMIN_HOST = "0.0.0.0"
ADMIN_PORT = 8080
USER_HOST = "0.0.0.0"
USER_PORT = 8501

# Document Types
SUPPORTED_DOCUMENTS = {
    "S-1": ["S1", "S-1", "S1A", "S-1/A"],
    "424B4": ["424B4", "PROSPECTUS"],
    "LOCK_UP": ["LOCK-UP", "LOCKUP", "MARKET_STANDOFF"],
    "UNDERWRITING": ["UNDERWRITING", "PURCHASE_AGREEMENT"],
    "8-A": ["8-A", "8A", "FORM_8-A"]
}

# Processing Configuration
CHUNK_SIZE = 1000  # tokens
CHUNK_OVERLAP = 100  # tokens
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4"
VALIDATION_MODEL = "gemini-pro"

# Scheduler Configuration
SCRAPE_INTERVAL = 30  # minutes
DOCUMENT_CHECK_INTERVAL = 60  # minutes
MORNING_REPORT_TIME = "06:00"  # UTC

# ChromaDB Configuration
CHROMA_PERSIST_DIR = str(VECTOR_DIR)
COLLECTION_NAME = "ipo_documents"

# Report Configuration
REPORT_FONT_FAMILY = "Helvetica"
REPORT_MARGINS = {
    "top": 72,  # 1 inch
    "bottom": 72,
    "left": 90,  # 1.25 inch
    "right": 90
}
