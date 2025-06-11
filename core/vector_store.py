"""
Hedge Intelligence Vector Store
Created: 2025-06-05 14:25:13 UTC
Author: thorrobber22

Manages vector embeddings for IPO documents using ChromaDB
with OpenAI embeddings for semantic search
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import asyncio
from dataclasses import dataclass

# Vector database
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# AI/ML
import openai
import numpy as np

# Load environment variables first
from dotenv import load_dotenv
load_dotenv(override=True)

# Configuration - Define everything here to avoid import issues
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DIR = DATA_DIR / "vectors"
VECTOR_DB_DIR = DATA_DIR / "vector_db"
EMBEDDING_MODEL = "text-embedding-3-small"
COLLECTION_NAME = "ipo_documents"
MAX_RESULTS = 10
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

@dataclass
class SearchResult:
    """Structure for search results"""
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any]
    document_type: str
    ticker: str
    filename: str

class VectorStore:
    """Main vector store management class"""
    
    def __init__(self):
        """Initialize ChromaDB and OpenAI"""
        # Check for required API key
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required for vector embeddings.\n"
                "Please set it in your .env file or environment:\n"
                "OPENAI_API_KEY=your-api-key-here"
            )
        
        # Note: Gemini API key is used in document_processor.py for validation
        # It's not needed here in the vector store
        
        # Ensure directories exist
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(
            path=str(VECTOR_DB_DIR),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize OpenAI embedding function
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=openai_api_key,
            model_name=EMBEDDING_MODEL
        )
        
        # Get or create collection
        self.collection = self._get_or_create_collection()
        
        print(f"✓ Vector store initialized with OpenAI embeddings ({EMBEDDING_MODEL})")
        
    def _get_or_create_collection(self):
        """Get or create the IPO documents collection"""
        try:
            # Try to get existing collection
            collection = self.client.get_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function
            )
            print(f"✓ Loaded existing collection: {COLLECTION_NAME}")
        except:
            # Create new collection
            collection = self.client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            print(f"✓ Created new collection: {COLLECTION_NAME}")
        
        return collection
    
    def add_document_chunks(self, chunks: List[Dict[str, Any]], ticker: str, doc_type: str) -> int:
        """Add document chunks to vector store"""
        if not chunks:
            return 0
        
        # Prepare data for ChromaDB
        ids = []
        texts = []
        metadatas = []
        
        for chunk in chunks:
            chunk_id = chunk.get("chunk_id", f"{ticker}_{doc_type}_{len(ids)}")
            
            # Ensure unique ID
            unique_id = f"{chunk_id}_{hashlib.md5(chunk['text'].encode()).hexdigest()[:8]}"
            
            ids.append(unique_id)
            texts.append(chunk["text"])
            
            # Prepare metadata
            metadata = chunk.get("metadata", {})
            metadata.update({
                "ticker": ticker,
                "document_type": doc_type,
                "chunk_index": chunk.get("chunk_index", 0),
                "indexed_at": datetime.now().isoformat()
            })
            metadatas.append(metadata)
        
        # Add to collection
        try:
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            print(f"✓ Added {len(ids)} chunks for {ticker} {doc_type}")
            return len(ids)
        except Exception as e:
            print(f"✗ Error adding chunks: {e}")
            return 0
    
    def search(self, 
               query: str, 
               ticker: Optional[str] = None,
               doc_types: Optional[List[str]] = None,
               n_results: int = None) -> List[SearchResult]:
        """Search vector store with optional filters"""
        if n_results is None:
            n_results = MAX_RESULTS
            
        # Build where clause for filtering
        where_clause = {}
        if ticker:
            where_clause["ticker"] = ticker
        if doc_types:
            where_clause["document_type"] = {"$in": doc_types}
        
        # Perform search
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert to SearchResult objects
            search_results = []
            
            if results and results["ids"] and results["ids"][0]:
                for i, chunk_id in enumerate(results["ids"][0]):
                    metadata = results["metadatas"][0][i]
                    
                    search_results.append(SearchResult(
                        chunk_id=chunk_id,
                        text=results["documents"][0][i],
                        score=1 - results["distances"][0][i],  # Convert distance to similarity
                        metadata=metadata,
                        document_type=metadata.get("document_type", "UNKNOWN"),
                        ticker=metadata.get("ticker", "UNKNOWN"),
                        filename=metadata.get("filename", "")
                    ))
            
            return search_results
            
        except Exception as e:
            print(f"✗ Search error: {e}")
            return []
    
    def get_document_chunks(self, ticker: str, doc_type: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        where_clause = {
            "$and": [
                {"ticker": {"$eq": ticker}},
                {"document_type": {"$eq": doc_type}}
            ]
        }
        
        try:
            results = self.collection.get(
                where=where_clause,
                include=["documents", "metadatas"]
            )
            
            chunks = []
            if results and results["ids"]:
                for i, chunk_id in enumerate(results["ids"]):
                    chunks.append({
                        "id": chunk_id,
                        "text": results["documents"][i],
                        "metadata": results["metadatas"][i]
                    })
            
            # Sort by chunk index
            chunks.sort(key=lambda x: x["metadata"].get("chunk_index", 0))
            
            return chunks
            
        except Exception as e:
            print(f"✗ Error getting chunks: {e}")
            return []
    
    def delete_document(self, ticker: str, doc_type: str) -> int:
        """Delete all chunks for a document"""
        where_clause = {
            "$and": [
                {"ticker": {"$eq": ticker}},
                {"document_type": {"$eq": doc_type}}
            ]
        }
        
        try:
            # Get IDs to delete
            results = self.collection.get(where=where_clause)
            
            if results and results["ids"]:
                self.collection.delete(ids=results["ids"])
                print(f"✓ Deleted {len(results['ids'])} chunks for {ticker} {doc_type}")
                return len(results["ids"])
            
            return 0
            
        except Exception as e:
            print(f"✗ Error deleting chunks: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        try:
            # Get all unique tickers and document types
            all_metadata = self.collection.get(include=["metadatas"])
            
            stats = {
                "total_chunks": len(all_metadata["ids"]) if all_metadata["ids"] else 0,
                "tickers": set(),
                "document_types": set(),
                "documents": {}
            }
            
            if all_metadata["metadatas"]:
                for metadata in all_metadata["metadatas"]:
                    ticker = metadata.get("ticker", "UNKNOWN")
                    doc_type = metadata.get("document_type", "UNKNOWN")
                    
                    stats["tickers"].add(ticker)
                    stats["document_types"].add(doc_type)
                    
                    # Count by document
                    doc_key = f"{ticker}_{doc_type}"
                    stats["documents"][doc_key] = stats["documents"].get(doc_key, 0) + 1
            
            # Convert sets to lists for JSON serialization
            stats["tickers"] = sorted(list(stats["tickers"]))
            stats["document_types"] = sorted(list(stats["document_types"]))
            
            return stats
            
        except Exception as e:
            print(f"✗ Error getting stats: {e}")
            return {
                "total_chunks": 0,
                "tickers": [],
                "document_types": [],
                "documents": {}
            }
    
    def semantic_comparison(self, ticker1: str, ticker2: str, aspect: str = "business") -> Dict[str, Any]:
        """Compare two companies on a specific aspect"""
        comparison_queries = {
            "business": "What is the company's main business and revenue model?",
            "risks": "What are the main risk factors?",
            "financials": "What are the key financial metrics and performance?",
            "management": "Who are the key executives and their experience?",
            "competitive": "What is the competitive landscape and market position?"
        }
        
        query = comparison_queries.get(aspect, aspect)
        
        # Search for both tickers
        results1 = self.search(query, ticker=ticker1, n_results=3)
        results2 = self.search(query, ticker=ticker2, n_results=3)
        
        comparison = {
            "aspect": aspect,
            "query": query,
            ticker1: {
                "found": len(results1) > 0,
                "top_results": [
                    {
                        "text": r.text[:500] + "...",
                        "score": r.score,
                        "source": r.document_type
                    }
                    for r in results1[:2]
                ]
            },
            ticker2: {
                "found": len(results2) > 0,
                "top_results": [
                    {
                        "text": r.text[:500] + "...",
                        "score": r.score,
                        "source": r.document_type
                    }
                    for r in results2[:2]
                ]
            }
        }
        
        return comparison
    
    def find_similar_chunks(self, text: str, exclude_ticker: Optional[str] = None, n_results: int = 5) -> List[SearchResult]:
        """Find chunks similar to given text"""
        where_clause = {}
        if exclude_ticker:
            where_clause["ticker"] = {"$ne": exclude_ticker}
        
        return self.search(text, n_results=n_results)

# Utility functions for integration

async def index_processed_document(processed_doc_path: Path, vector_store: Optional[VectorStore] = None) -> Dict[str, Any]:
    """Index a processed document JSON file"""
    try:
        if vector_store is None:
            vector_store = VectorStore()  # Will raise error if no API key
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }
    
    try:
        with open(processed_doc_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)
        
        ticker = doc_data["ticker"]
        doc_type = doc_data["document_type"]
        
        # Load chunks from the processed file
        chunks_file = processed_doc_path.parent / f"{processed_doc_path.stem}_chunks.json"
        
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks = json.load(f)
        else:
            # Create simple chunks from sections
            chunks = []
            for section_name, section_text in doc_data.get("sections", {}).items():
                if section_text:
                    chunks.append({
                        "chunk_id": f"{ticker}_{doc_type}_{section_name}",
                        "text": section_text[:2000],  # Limit size
                        "metadata": {
                            "section": section_name,
                            "ticker": ticker,
                            "document_type": doc_type
                        }
                    })
        
        # Add to vector store
        if chunks:
            count = vector_store.add_document_chunks(chunks, ticker, doc_type)
            return {
                "success": True,
                "chunks_indexed": count,
                "ticker": ticker,
                "document_type": doc_type
            }
        else:
            return {
                "success": False,
                "error": "No chunks found to index"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def search_ipo_info(query: str, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
    """Simple search interface for IPO information"""
    try:
        vector_store = VectorStore()
        results = vector_store.search(query, ticker=ticker, n_results=5)
        
        return [
            {
                "ticker": r.ticker,
                "document_type": r.document_type,
                "text": r.text,
                "score": r.score
            }
            for r in results
        ]
    except ValueError as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    # Test vector store
    print("Testing Vector Store...")
    
    try:
        vs = VectorStore()
        stats = vs.get_collection_stats()
        
        print(f"\nVector Store Stats:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Tickers: {', '.join(stats['tickers'])}")
        print(f"  Document types: {', '.join(stats['document_types'])}")
        
        # Test search if we have data
        if stats['total_chunks'] > 0:
            test_query = "What is the lock-up period?"
            print(f"\nTest search: '{test_query}'")
            results = vs.search(test_query, n_results=3)
            
            for i, result in enumerate(results):
                print(f"\n{i+1}. {result.ticker} - {result.document_type} (score: {result.score:.3f})")
                print(f"   {result.text[:200]}...")
                
    except ValueError as e:
        print(f"\n❌ {e}")
        print("\nMake sure you have set the following in your .env file:")
        print("OPENAI_API_KEY=your-openai-api-key")
        print("GEMINI_API_KEY=your-gemini-api-key  (for document validation)")
