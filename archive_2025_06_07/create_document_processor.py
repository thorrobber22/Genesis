#!/usr/bin/env python3
"""
Create AI Document Processor for SEC filings
Date: 2025-06-06 23:17:58 UTC
Author: thorrobber22
"""

from pathlib import Path

processor_content = '''#!/usr/bin/env python3
"""
SEC Document Processor - Indexes documents for AI search
"""

import chromadb
from chromadb.config import Settings
import google.generativeai as genai
import openai
from pathlib import Path
import json
from datetime import datetime
import re
from bs4 import BeautifulSoup
import PyPDF2
import asyncio
from typing import Dict, List, Tuple
import hashlib

class SECDocumentProcessor:
    def __init__(self, openai_key: str, gemini_key: str):
        """Initialize with API keys"""
        self.openai_key = openai_key
        self.gemini_key = gemini_key
        
        # Initialize APIs
        openai.api_key = openai_key
        genai.configure(api_key=gemini_key)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path="data/chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection("sec_documents")
        except:
            self.collection = self.chroma_client.create_collection(
                name="sec_documents",
                metadata={"hnsw:space": "cosine"}
            )
        
        self.sec_dir = Path("data/sec_documents")
        
    def extract_text_from_file(self, filepath: Path) -> str:
        """Extract text from various file types"""
        try:
            if filepath.suffix.lower() in ['.html', '.htm']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    text = soup.get_text()
                    # Clean up text
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = ' '.join(chunk for chunk in chunks if chunk)
                    return text[:50000]  # Limit to 50k chars
                    
            elif filepath.suffix.lower() == '.txt':
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()[:50000]
                    
            elif filepath.suffix.lower() == '.pdf':
                text = ""
                with open(filepath, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num in range(min(10, len(pdf_reader.pages))):  # First 10 pages
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text()
                return text[:50000]
                
        except Exception as e:
            print(f"Error extracting from {filepath}: {e}")
            return ""
            
    def chunk_document(self, text: str, chunk_size: int = 1500) -> List[str]:
        """Split document into overlapping chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - 200):  # 200 word overlap
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk) > 100:  # Minimum chunk size
                chunks.append(chunk)
                
        return chunks
        
    def extract_metadata(self, filepath: Path, text: str) -> Dict:
        """Extract metadata from document"""
        filename = filepath.name
        parts = filename.split('_')
        
        # Extract filing type
        filing_type = parts[0] if parts else "Unknown"
        
        # Extract date
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        date_match = re.search(date_pattern, filename)
        filing_date = date_match.group(1) if date_match else "Unknown"
        
        # Extract company info
        ticker = filepath.parent.name
        
        # Try to extract lock-up info
        lockup_days = None
        lockup_patterns = [
            r'lock[- ]?up.{0,50}(\d+)\s*days',
            r'(\d+)[- ]?day.{0,20}lock[- ]?up',
            r'restricted.{0,50}(\d+)\s*days'
        ]
        
        for pattern in lockup_patterns:
            match = re.search(pattern, text.lower())
            if match:
                lockup_days = int(match.group(1))
                break
                
        return {
            'ticker': ticker,
            'filing_type': filing_type,
            'filing_date': filing_date,
            'filename': filename,
            'filepath': str(filepath),
            'file_size': filepath.stat().st_size,
            'lockup_days': lockup_days
        }
        
    async def process_company(self, company_dir: Path) -> Dict:
        """Process all documents for a company"""
        ticker = company_dir.name
        results = {
            'ticker': ticker,
            'documents_processed': 0,
            'chunks_created': 0,
            'errors': []
        }
        
        print(f"\\n📊 Processing {ticker}...")
        
        files = list(company_dir.glob("*.*"))
        files = [f for f in files if f.suffix.lower() in ['.html', '.htm', '.txt', '.pdf']]
        
        for file in files:
            try:
                # Skip if already processed
                doc_id = hashlib.md5(str(file).encode()).hexdigest()
                existing = self.collection.get(ids=[doc_id])
                
                if existing['ids']:
                    continue
                    
                # Extract text
                text = self.extract_text_from_file(file)
                if not text:
                    continue
                    
                # Extract metadata
                metadata = self.extract_metadata(file, text)
                
                # Chunk document
                chunks = self.chunk_document(text)
                
                # Create embeddings and store
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}_{i}"
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = i
                    chunk_metadata['total_chunks'] = len(chunks)
                    
                    # Store in ChromaDB (it will create embeddings automatically)
                    self.collection.add(
                        documents=[chunk],
                        metadatas=[chunk_metadata],
                        ids=[chunk_id]
                    )
                    
                results['documents_processed'] += 1
                results['chunks_created'] += len(chunks)
                
            except Exception as e:
                results['errors'].append(f"{file.name}: {str(e)}")
                
        return results
        
    async def process_all_documents(self):
        """Process all downloaded SEC documents"""
        print("🚀 Starting SEC Document Processing")
        print("="*60)
        
        companies = [d for d in self.sec_dir.iterdir() if d.is_dir()]
        total_results = {
            'companies_processed': 0,
            'total_documents': 0,
            'total_chunks': 0,
            'start_time': datetime.now().isoformat()
        }
        
        for company_dir in companies:
            result = await self.process_company(company_dir)
            total_results['companies_processed'] += 1
            total_results['total_documents'] += result['documents_processed']
            total_results['total_chunks'] += result['chunks_created']
            
            print(f"   ✅ {result['documents_processed']} documents → {result['chunks_created']} chunks")
            
        total_results['end_time'] = datetime.now().isoformat()
        
        # Save processing log
        with open('data/processing_log.json', 'w') as f:
            json.dump(total_results, f, indent=2)
            
        print(f"\\n✅ Processing Complete!")
        print(f"   • Companies: {total_results['companies_processed']}")
        print(f"   • Documents: {total_results['total_documents']}")
        print(f"   • Chunks: {total_results['total_chunks']}")
        
        return total_results

# Test run
async def test():
    # You'll need to add your API keys
    processor = SECDocumentProcessor(
        openai_key="your-openai-key",
        gemini_key="your-gemini-key"
    )
    
    # Process one company as test
    test_company = Path("data/sec_documents/CRCL")
    if test_company.exists():
        result = await processor.process_company(test_company)
        print(f"Test result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    asyncio.run(test())
'''

# Save processor
Path("processors").mkdir(exist_ok=True)
with open("processors/document_processor.py", 'w', encoding='utf-8') as f:
    f.write(processor_content)

print("✅ Created document_processor.py")