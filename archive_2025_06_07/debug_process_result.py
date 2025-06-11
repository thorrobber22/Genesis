#!/usr/bin/env python3
"""
Debug process result to see what's returned
Date: 2025-06-06 11:47:52 UTC
Author: thorrobber22
"""

import asyncio
from pathlib import Path
from core.document_processor import process_uploaded_document
import json

async def debug_process():
    """Debug what process_uploaded_document returns"""
    
    doc_dir = Path("data/documents")
    if doc_dir.exists():
        docs = list(doc_dir.glob("*.html"))
        if docs:
            test_doc = docs[0]
            ticker = test_doc.name.split('_')[0]
            
            print(f"Testing with: {test_doc.name}")
            print(f"Ticker: {ticker}")
            print("-" * 50)
            
            result = await process_uploaded_document(ticker, test_doc)
            
            print("\nResult keys:", list(result.keys()))
            print("\nFull result:")
            print(json.dumps(result, indent=2, default=str))
            
            # Check for processed files
            processed_dir = Path("data/processed")
            if processed_dir.exists():
                print(f"\nFiles in processed directory:")
                for f in processed_dir.glob(f"{ticker}*"):
                    print(f"  - {f.name}")

if __name__ == "__main__":
    asyncio.run(debug_process())