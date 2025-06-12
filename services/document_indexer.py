#!/usr/bin/env python3
"""
Document Indexing Service with ChromaDB
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from datetime import datetime
import hashlib
from bs4 import BeautifulSoup
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentIndexer:
    def __init__(self):
        """Initialize the document indexer with ChromaDB"""
        self.index_dir = Path("data/indexed_documents")
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.chroma_dir = Path("data/chroma_db")
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        
        # Create persistent client
        self.client = chromadb.PersistentClient(path=str(self.chroma_dir))
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection("sec_documents")
            logger.info(f"Using existing collection with {self.collection.count()} documents")
        except:
            self.collection = self.client.create_collection(
                name="sec_documents",
                metadata={"description": "SEC filing documents"}
            )
            logger.info("Created new collection")
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for documents in the collection
        First tries exact company match, then falls back to semantic search
        """
        try:
            # Check if query is a company ticker (all caps, 2-5 letters)
            is_ticker = query.isupper() and query.isalpha() and 2 <= len(query) <= 5
            
            # First try exact company match if it looks like a ticker
            if is_ticker:
                logger.info(f"Searching for company ticker: {query}")
                results = self.collection.get(
                    where={"company": query},
                    limit=limit,
                    include=["metadatas", "documents"]
                )
                
                if results['ids']:
                    # Format results
                    formatted_results = []
                    for i in range(len(results['ids'])):
                        formatted_results.append({
                            'company': results['metadatas'][i].get('company', 'Unknown'),
                            'document': results['metadatas'][i].get('file_path', 'Unknown'),
                            'text': results['documents'][i][:500] if results['documents'][i] else '',
                            'metadata': results['metadatas'][i],
                            'score': 1.0  # Perfect match for exact company
                        })
                    logger.info(f"Found {len(formatted_results)} exact matches for company {query}")
                    return formatted_results
            
            # If no exact match or not a ticker, use semantic search
            logger.info(f"Performing semantic search for: {query}")
            
            # Split query to check for company + other terms (e.g., "TSLA revenue")
            query_parts = query.split()
            company_filter = None
            
            if len(query_parts) > 1:
                # Check if first part is a ticker
                potential_ticker = query_parts[0].upper()
                if potential_ticker.isalpha() and 2 <= len(potential_ticker) <= 5:
                    company_filter = potential_ticker
                    # Remove company from query for semantic search
                    semantic_query = " ".join(query_parts[1:])
                else:
                    semantic_query = query
            else:
                semantic_query = query
            
            # Perform semantic search
            if company_filter:
                # Search with company filter
                results = self.collection.query(
                    query_texts=[semantic_query],
                    n_results=limit,
                    where={"company": company_filter}
                )
            else:
                # General semantic search
                results = self.collection.query(
                    query_texts=[query],
                    n_results=limit
                )
            
            # Format results
            formatted_results = []
            
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'company': results['metadatas'][0][i].get('company', 'Unknown'),
                        'document': results['metadatas'][0][i].get('file_path', 'Unknown'),
                        'text': results['documents'][0][i][:500] if results['documents'][0][i] else '',
                        'metadata': results['metadatas'][0][i],
                        'score': 1 - (results['distances'][0][i] / 2) if 'distances' in results else 0.5
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    def index_document(self, file_path: Path, company: str, form_type: str = None, filing_date: str = None):
        """Index a single document"""
        try:
            # Read document
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract text
            text = soup.get_text()
            
            # Clean text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Split into sections (simple approach - split by common headers)
            sections = self._split_into_sections(text)
            
            # Index each section
            for i, section in enumerate(sections):
                if len(section['text']) < 50:  # Skip very short sections
                    continue
                
                # Create unique ID
                doc_id = hashlib.md5(f"{file_path}_{i}".encode()).hexdigest()
                section_id = f"{doc_id}_{i}"
                
                # Prepare metadata
                metadata = {
                    "file_path": str(file_path),
                    "document_name": file_path.name,
                    "company": company,
                    "ticker": company,  # Using company as ticker for now
                    "form_type": form_type or "Unknown",
                    "filing_date": filing_date or "Unknown",
                    "section_index": i,
                    "section_title": section['title'],
                    "indexed_at": datetime.now().isoformat()
                }
                
                # Add to ChromaDB
                self.collection.add(
                    documents=[section['text']],
                    metadatas=[metadata],
                    ids=[section_id]
                )
            
            logger.info(f"Indexed {file_path.name} with {len(sections)} sections")
            
        except Exception as e:
            logger.error(f"Error indexing {file_path}: {e}")
    
    def _split_into_sections(self, text: str) -> List[Dict]:
        """Split document text into sections"""
        sections = []
        
        # Common section headers in SEC filings
        section_patterns = [
            r'Item \d+[A-Z]?\.',
            r'Part [IVX]+',
            r'ITEM \d+[A-Z]?\.',
            r'PART [IVX]+',
            r'Financial Statements',
            r'Management\'s Discussion',
            r'Risk Factors',
            r'Business Overview',
            r'Notes to Financial Statements'
        ]
        
        # Combine patterns
        pattern = '|'.join(f'({p})' for p in section_patterns)
        
        # Split by sections
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        
        # Process parts
        current_section = {"title": "Introduction", "text": ""}
        
        for i, part in enumerate(parts):
            if part and len(part.strip()) > 0:
                # Check if this is a section header
                if any(re.match(p, part, re.IGNORECASE) for p in section_patterns):
                    # Save previous section
                    if current_section["text"]:
                        sections.append(current_section)
                    # Start new section
                    current_section = {"title": part.strip(), "text": ""}
                else:
                    # Add to current section
                    current_section["text"] += " " + part.strip()
        
        # Don't forget the last section
        if current_section["text"]:
            sections.append(current_section)
        
        # If no sections found, create one big section
        if not sections:
            sections.append({"title": "Full Document", "text": text})
        
        return sections
    
    def index_all_documents(self):
        """Index all documents in the sec_documents directory"""
        sec_dir = Path("data/sec_documents")
        
        if not sec_dir.exists():
            logger.error(f"Directory not found: {sec_dir}")
            return
        
        total_indexed = 0
        
        # Process each company directory
        for company_dir in sec_dir.iterdir():
            if not company_dir.is_dir():
                continue
            
            company = company_dir.name
            logger.info(f"Processing company: {company}")
            
            # Process each document
            for doc_path in company_dir.glob("*.html"):
                # Extract form type and date from filename if possible
                form_type = self._extract_form_type(doc_path.name)
                filing_date = self._extract_date(doc_path.name)
                
                self.index_document(doc_path, company, form_type, filing_date)
                total_indexed += 1
        
        logger.info(f"Total documents indexed: {total_indexed}")
        
        # Save index metadata
        self._save_index_metadata()
    
    def _extract_form_type(self, filename: str) -> str:
        """Extract form type from filename"""
        # Common form types
        form_types = ['10-K', '10-Q', '8-K', 'DEF 14A', 'S-1', '424B']
        
        for form in form_types:
            if form in filename.upper():
                return form
        
        return "Unknown"
    
    def _extract_date(self, filename: str) -> str:
        """Extract date from filename"""
        import re
        
        # Look for date pattern YYYY-MM-DD
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        match = re.search(date_pattern, filename)
        
        if match:
            return match.group(1)
        
        return "Unknown"
    
    def _save_index_metadata(self):
        """Save index metadata"""
        metadata = {
            "last_indexed": datetime.now().isoformat(),
            "total_documents": self.collection.count(),
            "index_version": "1.0"
        }
        
        metadata_path = self.index_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_statistics(self) -> Dict:
        """Get indexing statistics"""
        stats = {
            "total_documents": self.collection.count(),
            "index_size_mb": self._get_index_size(),
            "companies": self._get_indexed_companies()
        }
        
        return stats
    
    def _get_index_size(self) -> float:
        """Get total size of index in MB"""
        total_size = 0
        
        # ChromaDB directory size
        for path in self.chroma_dir.rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
        
        return total_size / (1024 * 1024)
    
    def _get_indexed_companies(self) -> List[str]:
        """Get list of indexed companies"""
        # Get unique companies from collection
        try:
            # Sample some documents to get companies
            sample = self.collection.get(limit=1000)
            companies = set()
            
            for metadata in sample['metadatas']:
                companies.add(metadata.get('company', 'Unknown'))
            
            return sorted(list(companies))
        except:
            return []

# Test the indexer
if __name__ == "__main__":
    indexer = DocumentIndexer()
    
    # Test search
    results = indexer.search("revenue financial", limit=5)
    print(f"Found {len(results)} results")
    
    for i, result in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"  Company: {result['company']}")
        print(f"  Document: {result['document_name']}")
        print(f"  Title: {result['title']}")
        print(f"  Relevance: {result['relevance']:.2f}")