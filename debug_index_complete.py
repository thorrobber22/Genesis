#!/usr/bin/env python3
"""
Complete debug script for document indexing system
"""

import json
from pathlib import Path
import streamlit as st
from services.document_indexer import DocumentIndexer

st.set_page_config(page_title="Debug Index", layout="wide")
st.title("🔍 Complete Index Debug")

# Initialize indexer
try:
    indexer = DocumentIndexer()
    st.success("✅ DocumentIndexer initialized")
except Exception as e:
    st.error(f"❌ Failed to initialize indexer: {e}")
    st.stop()

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["Search Test", "Index Structure", "Vector Store", "Documents"])

with tab1:
    st.header("🔎 Search Test")
    
    # Test different queries
    test_queries = [
        "revenue",
        "financial",
        "AAPL",
        "Apple",
        "income",
        "2023",
        "risk factors"
    ]
    
    selected_query = st.selectbox("Select test query:", test_queries)
    custom_query = st.text_input("Or enter custom query:")
    
    query = custom_query if custom_query else selected_query
    
    if st.button("Search"):
        with st.spinner("Searching..."):
            try:
                results = indexer.search(query=query, limit=10)
                
                st.write(f"Query: '{query}'")
                st.write(f"Results type: {type(results)}")
                st.write(f"Number of results: {len(results) if results else 0}")
                
                if results:
                    st.success(f"Found {len(results)} results!")
                    for i, result in enumerate(results):
                        with st.expander(f"Result {i+1}"):
                            st.json(result)
                else:
                    st.warning("No results found")
                    
                    # Try to understand why
                    st.subheader("Debugging empty results:")
                    
                    # Check if collection exists
                    if hasattr(indexer, 'collection'):
                        st.write("Collection exists:", indexer.collection is not None)
                        if indexer.collection:
                            st.write("Collection name:", indexer.collection.name)
                            try:
                                count = indexer.collection.count()
                                st.write("Documents in collection:", count)
                            except:
                                st.write("Could not get collection count")
                    
            except Exception as e:
                st.error(f"Search error: {e}")
                import traceback
                st.code(traceback.format_exc())

with tab2:
    st.header("📁 Index File Structure")
    
    index_path = Path("data/indexed_documents/document_index.json")
    
    if index_path.exists():
        st.success(f"✅ Index file found: {index_path}")
        
        with open(index_path, 'r') as f:
            index_data = json.load(f)
        
        st.write(f"Index keys: {list(index_data.keys())}")
        
        sections = index_data.get('sections', [])
        st.write(f"Total sections: {len(sections)}")
        
        if sections:
            st.subheader("Sample Sections:")
            
            # Show first 3 sections
            for i, section in enumerate(sections[:3]):
                with st.expander(f"Section {i+1}"):
                    st.json(section)
            
            # Analyze structure
            st.subheader("Field Analysis:")
            all_fields = set()
            companies = set()
            
            for section in sections:
                all_fields.update(section.keys())
                # Try different company field names
                company = section.get('company') or section.get('Company') or section.get('ticker', 'Unknown')
                companies.add(company)
            
            st.write("All fields found:", sorted(all_fields))
            st.write("Companies found:", sorted(companies))
            
    else:
        st.error(f"❌ Index file not found at: {index_path}")

with tab3:
    st.header("🗄️ Vector Store Check")
    
    # Check ChromaDB
    try:
        import chromadb
        
        # Check persistent directory
        persist_dir = Path("data/chroma_db")
        st.write(f"ChromaDB directory: {persist_dir}")
        st.write(f"Directory exists: {persist_dir.exists()}")
        
        if persist_dir.exists():
            # List contents
            st.write("Directory contents:")
            for item in persist_dir.iterdir():
                st.write(f"  - {item.name}")
        
        # Try to connect
        client = chromadb.PersistentClient(path=str(persist_dir))
        collections = client.list_collections()
        
        st.write(f"Number of collections: {len(collections)}")
        
        for collection in collections:
            st.subheader(f"Collection: {collection.name}")
            try:
                count = collection.count()
                st.write(f"Documents: {count}")
                
                # Get sample
                if count > 0:
                    sample = collection.get(limit=1)
                    st.write("Sample document:")
                    st.json({
                        "ids": sample.get('ids', []),
                        "metadatas": sample.get('metadatas', []),
                        "documents": [doc[:200] + "..." if doc and len(doc) > 200 else doc 
                                    for doc in sample.get('documents', [])]
                    })
            except Exception as e:
                st.error(f"Error accessing collection: {e}")
                
    except Exception as e:
        st.error(f"ChromaDB error: {e}")

with tab4:
    st.header("📄 Document Files")
    
    sec_dir = Path("data/sec_documents")
    
    if sec_dir.exists():
        companies = [d.name for d in sec_dir.iterdir() if d.is_dir()]
        st.write(f"Companies with documents: {companies}")
        
        for company in companies[:5]:  # Show first 5
            company_dir = sec_dir / company
            docs = list(company_dir.glob("*.html"))
            st.write(f"{company}: {len(docs)} documents")
            
            if docs and st.checkbox(f"Show {company} documents", key=f"show_{company}"):
                for doc in docs[:3]:
                    st.write(f"  - {doc.name} ({doc.stat().st_size / 1024:.1f} KB)")
    else:
        st.error(f"Documents directory not found: {sec_dir}")

# Quick diagnostics
st.sidebar.header("🏥 Quick Diagnostics")

# Check if we need to reindex
reindex_needed = False

if not Path("data/indexed_documents/document_index.json").exists():
    st.sidebar.error("❌ No index file")
    reindex_needed = True
else:
    st.sidebar.success("✅ Index file exists")

if not Path("data/chroma_db").exists():
    st.sidebar.error("❌ No vector store")
    reindex_needed = True
else:
    st.sidebar.success("✅ Vector store exists")

if reindex_needed:
    st.sidebar.warning("⚠️ Reindexing needed!")
    
    if st.sidebar.button("🔄 Reindex Documents"):
        with st.spinner("Reindexing..."):
            try:
                # Run indexer
                indexer = DocumentIndexer()
                indexer.index_all_documents()
                st.sidebar.success("✅ Reindexing complete!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Reindex error: {e}")