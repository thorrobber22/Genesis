#!/usr/bin/env python3
"""
Safely update chat engine for multi-document search
Date: 2025-06-06 17:25:20 UTC
Author: thorrobber22
"""

from pathlib import Path
import shutil

# Backup current chat engine
chat_path = Path("core/chat_engine.py")
backup_path = Path("core/chat_engine_backup.py")

if chat_path.exists():
    shutil.copy(chat_path, backup_path)
    print(f"✅ Backed up to {backup_path}")
    
    with open(chat_path, 'r') as f:
        content = f.read()
    
    # Check if it needs multi-doc support
    needs_update = True
    
    if "document_type" in content or "doc_type" in content:
        print("✅ Chat engine already has document type support")
        needs_update = False
    
    if needs_update:
        # Find where to insert the new method
        class_start = content.find("class ChatEngine")
        if class_start == -1:
            class_start = content.find("class")
        
        # Find the search method
        search_pos = content.find("def search(", class_start)
        if search_pos == -1:
            search_pos = content.find("async def search(", class_start)
        
        if search_pos > -1:
            # Find the end of the search method
            indent = "    "  # Assume 4 spaces
            next_method = content.find("\n" + indent + "def ", search_pos + 1)
            if next_method == -1:
                next_method = content.find("\n" + indent + "async def ", search_pos + 1)
            
            if next_method == -1:
                # No next method, insert at end of class
                next_method = len(content)
            
            # Insert new method
            new_method = f'''
    
    def search_by_document_type(self, query: str, ticker: str, doc_types: list = None):
        """Search across multiple document types with source tracking"""
        if not doc_types:
            doc_types = ["S-1", "424B4", "8-A", "Lock-up", "Financial"]
        
        all_results = []
        
        for doc_type in doc_types:
            try:
                # Search in specific document type
                metadata_filter = {{
                    "ticker": ticker.upper(),
                    "document_type": doc_type
                }}
                
                # Use existing search method
                results = self.vector_store.search(
                    query=query,
                    filter=metadata_filter,
                    top_k=3
                )
                
                # Add source info to each result
                for result in results:
                    result['source_document'] = doc_type
                    result['source_ticker'] = ticker
                    all_results.append(result)
                    
            except Exception as e:
                print(f"Error searching {{doc_type}}: {{e}}")
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        # Return top results
        return all_results[:10]
    
    def get_context_with_sources(self, query: str, ticker: str):
        """Get context with clear source attribution"""
        results = self.search_by_document_type(query, ticker)
        
        if not results:
            return {{
                'context': 'No relevant information found.',
                'sources': []
            }}
        
        # Group by document type
        context_parts = []
        sources = []
        
        for result in results:
            doc_type = result.get('source_document', 'Unknown')
            content = result.get('content', '')
            
            if content:
                context_parts.append(f"[From {{doc_type}}]: {{content}}")
                
                source = {{
                    'document_type': doc_type,
                    'ticker': ticker,
                    'relevance': result.get('score', 0)
                }}
                
                if source not in sources:
                    sources.append(source)
        
        return {{
            'context': '\\n\\n'.join(context_parts),
            'sources': sources
        }}
'''
            
            # Insert the new method
            updated_content = content[:next_method] + new_method + "\n" + content[next_method:]
            
            # Save updated version
            with open(chat_path, 'w') as f:
                f.write(updated_content)
            
            print("✅ Updated chat engine with multi-document search methods")
            print("   - Added search_by_document_type()")
            print("   - Added get_context_with_sources()")
        else:
            print("⚠️ Could not find search method in chat engine")
            print("   You may need to manually add multi-document support")
else:
    print("❌ Chat engine file not found!")