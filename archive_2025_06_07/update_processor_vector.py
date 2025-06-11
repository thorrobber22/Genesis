#!/usr/bin/env python3
"""
Update document processor to auto-index in vector store
Date: 2025-06-05 14:07:41 UTC
Author: thorrobber22
"""

print("To integrate vector store with document processor:")
print("\n1. Add to document_processor.py imports:")
print("   from core.vector_store import VectorStore")
print("\n2. In process_document() after saving JSON:")
print("   # Index in vector store")
print("   vector_store = VectorStore()")
print("   chunks_added = vector_store.add_document_chunks(")
print("       processed_doc.vector_chunks,")
print("       processed_doc.ticker,")
print("       processed_doc.document_type.value")
print("   )")
print("   print(f'✓ Indexed {chunks_added} chunks in vector store')")
print("\n3. Also save chunks to a separate file:")
print("   chunks_path = output_path.parent / f'{output_path.stem}_chunks.json'")
print("   with open(chunks_path, 'w') as f:")
print("       json.dump(processed_doc.vector_chunks, f)")