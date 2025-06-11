#!/usr/bin/env python3
"""
Fix all issues - encoding, imports, and create test script
Date: 2025-06-06 17:38:34 UTC
Author: thorrobber22
"""

from pathlib import Path

# 1. Fix pipeline imports with proper encoding
pipeline_file = Path("scrapers/sec/pipeline_manager.py")

if pipeline_file.exists():
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the imports
    fixed_content = content.replace(
        "from scrapers.sec.iposcoop_scraper import IPOScoopScraper",
        "from iposcoop_scraper import IPOScoopScraper"
    ).replace(
        "from scrapers.sec.cik_resolver import CIKResolver",
        "from cik_resolver import CIKResolver"
    ).replace(
        "from scrapers.sec.sec_scraper import SECDocumentScraper",
        "from sec_scraper import SECDocumentScraper"
    )
    
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ Fixed pipeline_manager.py imports")

# 2. Create test script
test_script = '''#!/usr/bin/env python3
"""
Test SEC pipeline from main directory
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import
from scrapers.sec.pipeline_manager import IPOPipelineManager
import asyncio

async def test_pipeline():
    """Test the pipeline"""
    print("🧪 Testing SEC Pipeline...")
    
    manager = IPOPipelineManager()
    
    # Test 1: Scan for IPOs
    print("\\n1️⃣ Scanning for new IPOs...")
    new_count = await manager.scan_new_ipos()
    print(f"   Found {new_count} new IPOs")
    
    # Test 2: Get summary
    print("\\n2️⃣ Getting admin summary...")
    summary = manager.get_admin_summary()
    print(f"   Pending: {summary['pending']}")
    print(f"   Active: {summary['active']}")
    print(f"   Needs Attention: {len(summary['needs_attention'])}")
    
    # Test 3: Process one IPO (if any pending)
    if summary['pending'] > 0:
        print("\\n3️⃣ Processing pending IPOs...")
        await manager.process_pending_ipos()

if __name__ == "__main__":
    asyncio.run(test_pipeline())
'''

with open("test_sec_pipeline.py", 'w', encoding='utf-8') as f:
    f.write(test_script)
print("✅ Created test_sec_pipeline.py")

# 3. Add multi-document support to chat engine
chat_file = Path("core/chat_engine.py")

if chat_file.exists():
    with open(chat_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add multi-doc search method after the _search_documents method
    if "search_by_document_type" not in content:
        # Find where to insert
        search_pos = content.find("def _search_documents(")
        if search_pos > -1:
            # Find the end of this method (next method or end of class)
            next_def = content.find("\n    def ", search_pos + 1)
            
            # Insert new methods
            new_methods = '''
    
    def search_by_document_type(self, query: str, ticker: str, doc_types: list = None):
        """Search across multiple document types"""
        if not doc_types:
            doc_types = ["S-1", "424B4", "8-A", "Lock-up", "Financial"]
        
        all_results = []
        
        for doc_type in doc_types:
            try:
                # Search with metadata filter
                results = self.collection.query(
                    query_texts=[query],
                    n_results=3,
                    where={
                        "$and": [
                            {"ticker": {"$eq": ticker.upper()}},
                            {"document_type": {"$eq": doc_type}}
                        ]
                    }
                )
                
                # Process results
                if results and results['documents']:
                    for i, doc in enumerate(results['documents'][0]):
                        all_results.append({
                            'content': doc,
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                            'score': results['distances'][0][i] if results['distances'] else 0,
                            'source_document': doc_type
                        })
                        
            except Exception as e:
                print(f"Error searching {doc_type}: {e}")
        
        # Sort by relevance
        all_results.sort(key=lambda x: x.get('score', 0))
        return all_results[:10]
    
    def get_multi_doc_response(self, query: str, ticker: str):
        """Get response using multiple document types"""
        # Search across all document types
        results = self.search_by_document_type(query, ticker)
        
        if not results:
            return {
                "response": "I couldn't find relevant information in the documents.",
                "sources": [],
                "confidence": "low"
            }
        
        # Build context from multiple sources
        context_parts = []
        sources = []
        
        for result in results:
            doc_type = result.get('source_document', 'Unknown')
            content = result.get('content', '')
            
            if content:
                context_parts.append(f"[From {doc_type}]: {content}")
                sources.append({
                    'document_type': doc_type,
                    'ticker': ticker,
                    'relevance': result.get('score', 0)
                })
        
        # Generate response with multi-doc context
        context = '\\n\\n'.join(context_parts)
        response = self.get_response(f"Based on the following information from multiple documents:\\n\\n{context}\\n\\nQuestion: {query}")
        
        # Add source information
        response['sources'] = sources
        
        return response
'''
            
            if next_def > -1:
                # Insert before next method
                updated_content = content[:next_def] + new_methods + content[next_def:]
            else:
                # Add at end of class
                # Find last method
                last_brace = content.rfind("}")
                if last_brace > -1:
                    updated_content = content[:last_brace] + new_methods + "\n" + content[last_brace:]
                else:
                    updated_content = content + new_methods
            
            # Save updated version
            with open(chat_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ Added multi-document support to chat_engine.py")
        else:
            print("⚠️  Could not find _search_documents method")
    else:
        print("✅ Chat engine already has multi-document support")

print("\n✅ All fixes complete!")
print("\nNow you can run:")
print("  python test_sec_pipeline.py")