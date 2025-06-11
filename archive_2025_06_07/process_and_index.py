#!/usr/bin/env python3
"""
Process and index documents with proper error handling
Date: 2025-06-06 11:47:52 UTC
Author: thorrobber22
"""

import json
from pathlib import Path
from core.document_processor import process_uploaded_document
from core.vector_store import VectorStore

def process_and_index_document_sync(ticker: str, file_path: Path) -> dict:
    """Process document and index in vector store (synchronous wrapper)"""
    import asyncio
    
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            process_and_index_document(ticker, file_path)
        )
        return result
    finally:
        loop.close()

async def process_and_index_document(ticker: str, file_path: Path) -> dict:
    """Process document and index in vector store"""
    
    # Process document
    print(f"Processing {file_path.name}...")
    result = await process_uploaded_document(ticker, file_path)
    
    if result.get("success") and result.get("status") != "ERROR":
        print(f"Document processed: {result.get('document_type', 'Unknown')}")
        
        # Try to find the output file
        processed_dir = Path("data/processed")
        output_path = None
        
        # Look for the processed file
        if processed_dir.exists():
            # Try to find by pattern
            pattern = f"{ticker}_{result.get('document_type', '*')}_*.json"
            files = list(processed_dir.glob(pattern))
            
            if files:
                # Get the most recent one
                output_path = max(files, key=lambda p: p.stat().st_mtime)
                print(f"Found processed file: {output_path.name}")
            else:
                # Try without document type
                files = list(processed_dir.glob(f"{ticker}_*.json"))
                if files:
                    output_path = max(files, key=lambda p: p.stat().st_mtime)
                    print(f"Found processed file: {output_path.name}")
        
        if output_path:
            # Index in vector store
            try:
                vs = VectorStore()
                
                # Load the processed data
                with open(output_path, 'r') as f:
                    doc_data = json.load(f)
                
                # Try chunks file first
                chunks_file = output_path.parent / f"{output_path.stem}_chunks.json"
                
                if chunks_file.exists():
                    with open(chunks_file, 'r') as f:
                        chunks = json.load(f)
                    
                    # Fix any text format issues
                    for chunk in chunks:
                        if isinstance(chunk.get("text"), list):
                            chunk["text"] = " ".join(str(t) for t in chunk["text"])
                    
                    count = vs.add_document_chunks(
                        chunks, 
                        ticker, 
                        result.get("document_type", "Unknown")
                    )
                    print(f"Indexed {count} chunks in vector store")
                    result["chunks_indexed"] = count
                else:
                    # Create chunks from sections
                    chunks = []
                    sections = doc_data.get("sections", {})
                    
                    for section_name, section_text in sections.items():
                        if section_text and isinstance(section_text, str):
                            # Create smaller chunks if section is large
                            chunk_size = 1500
                            if len(section_text) > chunk_size:
                                for i in range(0, len(section_text), chunk_size):
                                    chunk_text = section_text[i:i+chunk_size]
                                    chunks.append({
                                        "chunk_id": f"{ticker}_{result.get('document_type')}_{section_name}_{i}",
                                        "text": chunk_text,
                                        "metadata": {
                                            "section": section_name,
                                            "ticker": ticker,
                                            "document_type": result.get("document_type", "Unknown"),
                                            "chunk_index": i // chunk_size
                                        }
                                    })
                            else:
                                chunks.append({
                                    "chunk_id": f"{ticker}_{result.get('document_type')}_{section_name}",
                                    "text": section_text,
                                    "metadata": {
                                        "section": section_name,
                                        "ticker": ticker,
                                        "document_type": result.get("document_type", "Unknown")
                                    }
                                })
                    
                    if chunks:
                        count = vs.add_document_chunks(chunks, ticker, result.get("document_type", "Unknown"))
                        print(f"Indexed {count} chunks from sections")
                        result["chunks_indexed"] = count
                    else:
                        print("No chunks to index")
                        result["chunks_indexed"] = 0
                
                result["indexed_file"] = str(output_path)
                    
            except Exception as e:
                print(f"Vector indexing error: {e}")
                result["vector_error"] = str(e)
        else:
            print("Could not find processed output file")
            result["chunks_indexed"] = 0
            result["error"] = "No output file found"
    else:
        print(f"Document processing failed: {result.get('error', 'Unknown error')}")
        result["chunks_indexed"] = 0
    
    return result

if __name__ == "__main__":
    # Test with a document
    doc_dir = Path("data/documents")
    if doc_dir.exists():
        docs = list(doc_dir.glob("*.html"))
        if docs:
            test_doc = docs[0]
            ticker = test_doc.name.split('_')[0]
            print(f"Testing with: {test_doc.name}")
            
            result = process_and_index_document_sync(ticker, test_doc)
            
            print(f"\nResult Summary:")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Status: {result.get('status', 'Unknown')}")
            print(f"  Document Type: {result.get('document_type', 'Unknown')}")
            print(f"  Chunks Indexed: {result.get('chunks_indexed', 0)}")
            if 'error' in result:
                print(f"  Error: {result['error']}")
            if 'indexed_file' in result:
                print(f"  Indexed from: {Path(result['indexed_file']).name}")
        else:
            print("No documents found to test")
