#!/usr/bin/env python3
"""
Update admin panel to use integrated processing
Date: 2025-06-05 14:36:06 UTC
Author: thorrobber22
"""

print("📝 Instructions to update admin.py:")
print("\n1. Add to imports:")
print("   from process_and_index import process_and_index_document")
print("\n2. In show_upload(), replace the process_document_sync call with:")
print("""
                # Process and index document
                result = asyncio.run(process_and_index_document(ticker, file_path))
                
                if result["success"]:
                    st.success(f"✓ Processed as {result['document_type']}")
                    if result.get("chunks_indexed", 0) > 0:
                        st.info(f"✓ Indexed {result['chunks_indexed']} chunks for search")
""")

print("\n3. Add a new search tab to the admin panel")
print("   This will allow searching indexed documents")