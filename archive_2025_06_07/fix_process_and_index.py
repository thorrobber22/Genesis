#!/usr/bin/env python3
"""
Fix process and index async issues
Date: 2025-06-05 14:42:15 UTC
Author: thorrobber22
"""

process_code = '''#!/usr/bin/env python3
"""
Process and index documents
Date: 2025-06-05 14:42:15 UTC
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
    print(f"\\n📄 Processing {file_path.name}...")
    result = await process_uploaded_document(ticker, file_path)
    
    if result["success"]:
        print(f"✓ Document processed: {result['document_type']}")
        
        # Load the processed data
        processed_path = Path(result["output_path"])
        
        # Index in vector store
        try:
            vs = VectorStore()
            
            # Load chunks from the chunks file
            chunks_file = processed_path.parent / f"{processed_path.stem}_chunks.json"
            
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
                    result["document_type"]
                )
                print(f"✓ Indexed {count} chunks in vector store")
                result["chunks_indexed"] = count
            else:
                # Try to create chunks from sections
                with open(processed_path, 'r') as f:
                    doc_data = json.load(f)
                
                chunks = []
                for section_name, section_text in doc_data.get("sections", {}).items():
                    if section_text and isinstance(section_text, str):
                        chunks.append({
                            "chunk_id": f"{ticker}_{result['document_type']}_{section_name}",
                            "text": section_text[:2000],
                            "metadata": {
                                "section": section_name,
                                "ticker": ticker,
                                "document_type": result["document_type"]
                            }
                        })
                
                if chunks:
                    count = vs.add_document_chunks(chunks, ticker, result["document_type"])
                    print(f"✓ Indexed {count} chunks from sections")
                    result["chunks_indexed"] = count
                else:
                    print("⚠️  No chunks to index")
                    result["chunks_indexed"] = 0
                
        except Exception as e:
            print(f"✗ Vector indexing error: {e}")
            result["vector_error"] = str(e)
    
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
            
            print(f"\\nResult Summary:")
            print(f"  Success: {result.get('success', False)}")
            print(f"  Document Type: {result.get('document_type', 'Unknown')}")
            print(f"  Chunks Indexed: {result.get('chunks_indexed', 0)}")
            if 'error' in result:
                print(f"  Error: {result['error']}")
        else:
            print("No documents found to test")
'''

with open('process_and_index.py', 'w') as f:
    f.write(process_code)

print("✓ Fixed process_and_index.py")
print("\nNow test with: python process_and_index.py")