#!/usr/bin/env python3
"""
Debug script to check index structure
"""

import json
from pathlib import Path
import streamlit as st
from services.document_indexer import DocumentIndexer

st.set_page_config(page_title="Debug Index", layout="wide")
st.title("🔍 Debug Document Index")

# Load the indexer
indexer = DocumentIndexer()

# Do a test search
test_query = "revenue financial"
results = indexer.search(query=test_query, limit=5)

st.header("Search Results Structure")
st.write(f"Query: '{test_query}'")
st.write(f"Number of results: {len(results)}")

if results:
    st.subheader("First Result Fields:")
    st.json(results[0])
    
    st.subheader("All Results:")
    for i, result in enumerate(results):
        with st.expander(f"Result {i+1}"):
            st.json(result)

# Check index file directly
st.header("Index File Structure")
index_path = Path("data/indexed_documents/document_index.json")

if index_path.exists():
    with open(index_path, 'r') as f:
        index_data = json.load(f)
    
    st.write(f"Total sections: {len(index_data.get('sections', []))}")
    
    if index_data.get('sections'):
        st.subheader("First Section Structure:")
        st.json(index_data['sections'][0])
else:
    st.error("Index file not found!")

# Check what companies are indexed
st.header("Indexed Companies")
if index_path.exists():
    companies = set()
    for section in index_data.get('sections', []):
        # Check different possible field names
        company = section.get('company') or section.get('Company') or 'Unknown'
        companies.add(company)
    
    st.write("Companies found:", sorted(companies))