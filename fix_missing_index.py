#!/usr/bin/env python3
"""
Fix missing index file by recreating it from ChromaDB
"""

import json
from pathlib import Path
from datetime import datetime
import chromadb
from tqdm import tqdm

print("🔧 Fixing missing index file...")

# Create directories
index_dir = Path("data/indexed_documents")
index_dir.mkdir(parents=True, exist_ok=True)

# Connect to ChromaDB
persist_dir = Path("data/chroma_db")
client = chromadb.PersistentClient(path=str(persist_dir))

# Get collection
collection = client.get_collection("sec_documents")
print(f"✅ Found collection with {collection.count()} documents")

# Get all documents
print("📥 Retrieving all documents from ChromaDB...")
all_data = collection.get()

# Build index structure
sections = []
for i in tqdm(range(len(all_data['ids'])), desc="Building index"):
    metadata = all_data['metadatas'][i]
    
    section = {
        "id": all_data['ids'][i],
        "company": metadata.get('company', 'Unknown'),
        "ticker": metadata.get('ticker', metadata.get('company', 'Unknown')),
        "document": metadata.get('file_path', ''),
        "document_name": metadata.get('document_name', ''),
        "title": metadata.get('section_title', 'Untitled'),
        "section_type": metadata.get('form_type', 'Unknown'),
        "filing_date": metadata.get('filing_date', 'Unknown'),
        "indexed_at": metadata.get('indexed_at', datetime.now().isoformat()),
        "section_index": metadata.get('section_index', 0),
        "text": all_data['documents'][i][:500] if all_data['documents'][i] else "",  # Preview
        "relevance": 1.0  # Default relevance
    }
    sections.append(section)

# Create index file
index_data = {
    "version": "1.0",
    "created_at": datetime.now().isoformat(),
    "total_sections": len(sections),
    "sections": sections
}

# Save index file
index_path = index_dir / "document_index.json"
print(f"💾 Saving index to {index_path}")
with open(index_path, 'w', encoding='utf-8') as f:
    json.dump(index_data, f, indent=2)

print(f"✅ Created index file with {len(sections)} sections")

# Verify
if index_path.exists():
    size_mb = index_path.stat().st_size / (1024 * 1024)
    print(f"📊 Index file size: {size_mb:.2f} MB")
    
    # Show sample companies
    companies = set(s['company'] for s in sections)
    print(f"🏢 Companies indexed: {sorted(companies)}")