#!/usr/bin/env python3
"""
Minimal vector store test
Date: 2025-06-05 14:34:15 UTC
Author: thorrobber22
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import os
print(f"Loaded API key: {os.getenv('OPENAI_API_KEY')[:20]}...")

try:
    from core.vector_store import VectorStore
    
    print("\nCreating vector store...")
    vs = VectorStore()
    
    print("\nTesting basic operations...")
    
    # Add a test chunk
    test_chunks = [{
        "chunk_id": "TEST_1",
        "text": "This is a test chunk",
        "metadata": {"test": True}
    }]
    
    result = vs.add_document_chunks(test_chunks, "TEST", "TEST")
    print(f"Added {result} chunks")
    
    # Search
    results = vs.search("test")
    print(f"Found {len(results)} results")
    
    # Cleanup
    vs.delete_document("TEST", "TEST")
    
    print("\nSUCCESS: Vector store is working!")
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()