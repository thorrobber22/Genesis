#!/usr/bin/env python3
"""
Fix document processor to integrate with vector store
Date: 2025-06-05 14:36:06 UTC
Author: thorrobber22
"""

from pathlib import Path

print("🔧 Updating document_processor.py for vector store integration...")

# Read current document processor
dp_path = Path("core/document_processor.py")
with open(dp_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add vector store import if not present
if "from core.vector_store import VectorStore" not in content:
    # Find imports section
    import_pos = content.find("# Import configuration")
    if import_pos > 0:
        insert_pos = content.rfind("\n", 0, import_pos)
        content = content[:insert_pos] + "\nfrom core.vector_store import VectorStore\n" + content[insert_pos:]
        print("✓ Added VectorStore import")

# Fix the chunk text issue - ensure text is always a string
chunk_fix = '''
            # Ensure text is a string
            chunk_text = chunk["text"]
            if isinstance(chunk_text, list):
                chunk_text = " ".join(str(t) for t in chunk_text)
            elif not isinstance(chunk_text, str):
                chunk_text = str(chunk_text)
            
            chunk["text"] = chunk_text'''

# Find where chunks are created and add the fix
if "chunk_text = chunk" not in content:
    # Add before "return ProcessedDocument"
    return_pos = content.find("return ProcessedDocument(")
    if return_pos > 0:
        # Find the end of vector_chunks creation
        chunks_end = content.rfind("}", 0, return_pos)
        if chunks_end > 0:
            # Insert the fix for each chunk
            insert_text = '''
        
        # Fix chunk text format
        for chunk in vector_chunks:''' + chunk_fix
            
            content = content[:chunks_end+1] + insert_text + "\n" + content[chunks_end+1:]
            print("✓ Added chunk text fix")

# Write back
with open(dp_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Updated document_processor.py")

# Create integration function
integration_code = '''#!/usr/bin/env python3
"""
Process and index documents
Date: 2025-06-05 14:36:06 UTC
Author: thorrobber22
"""

import asyncio
from pathlib import Path
from core.document_processor import process_document_sync
from core.vector_store import VectorStore

async def process_and_index_document(ticker: str, file_path: Path) -> dict:
    """Process document and index in vector store"""
    
    # Process document
    print(f"\\n📄 Processing {file_path.name}...")
    result = process_document_sync(ticker, file_path)
    
    if result["success"]:
        print(f"✓ Document processed: {result['document_type']}")
        
        # Load the processed data
        processed_path = Path(result["output_path"])
        
        # Index in vector store
        try:
            vs = VectorStore()
            
            # Get chunks from the result
            if "chunks" in result:
                chunks = result["chunks"]
            else:
                # Load from chunks file
                chunks_file = processed_path.parent / f"{processed_path.stem}_chunks.json"
                if chunks_file.exists():
                    import json
                    with open(chunks_file, 'r') as f:
                        chunks = json.load(f)
                else:
                    chunks = []
            
            if chunks:
                count = vs.add_document_chunks(
                    chunks, 
                    ticker, 
                    result["document_type"]
                )
                print(f"✓ Indexed {count} chunks in vector store")
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
            
            result = asyncio.run(process_and_index_document(ticker, test_doc))
            print(f"\\nResult: {result}")
        else:
            print("No documents found to test")
'''

with open('process_and_index.py', 'w', encoding='utf-8') as f:
    f.write(integration_code)

print("\n✓ Created process_and_index.py")
print("\nTest with: python process_and_index.py")