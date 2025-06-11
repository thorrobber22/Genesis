"""
AI Service - Handles OpenAI and Gemini integration
Date: 2025-06-07 14:02:41 UTC
"""

import os
import openai
import google.generativeai as genai
from typing import Dict, List, Tuple, Optional
import chromadb
from chromadb.utils import embedding_functions
import re

class AIService:
    """Dual AI validation service"""
    
    def __init__(self):
        # Initialize API keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.openai_model = "gpt-4-turbo-preview"
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
            if self.openai_api_key:
                self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=self.openai_api_key,
                    model_name="text-embedding-3-small"
                )
        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
            self.chroma_client = None
    
    def search_documents(self, query: str, company: Optional[str] = None) -> List[Dict]:
        """Search ChromaDB for relevant documents"""
        if not self.chroma_client:
            return []
            
        try:
            collection_name = f"{company}_documents" if company else "all_documents"
            
            # Check if collection exists
            existing_collections = [col.name for col in self.chroma_client.list_collections()]
            if collection_name not in existing_collections:
                return []
            
            collection = self.chroma_client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            
            results = collection.query(
                query_texts=[query],
                n_results=5,
                include=['documents', 'metadatas', 'distances']
            )
            
            if not results['documents'][0]:
                return []
            
            return [{
                'content': doc,
                'metadata': meta,
                'score': 1 - dist
            } for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )]
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_ai_response(self, query: str, context: List[Dict]) -> Tuple[str, float]:
        """Get response from both AIs with confidence score"""
        
        if not context:
            return "No relevant documents found for your query.", 0.0
        
        # Prepare context
        context_text = "\n\n".join([
            f"Source: {doc['metadata'].get('source', 'Unknown')}\n{doc['content'][:500]}..."
            for doc in context[:3]
        ])
        
        prompt = f"""Based on the following SEC filing excerpts, answer this question: {query}

Context:
{context_text}

Provide a clear, specific answer with exact citations (document name and page number where available).
"""
        
        try:
            responses = []
            
            # Get OpenAI response if available
            if self.openai_api_key:
                openai_response = openai.ChatCompletion.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": "You are an SEC filing expert. Always cite specific documents and page numbers."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                responses.append(openai_response.choices[0].message.content)
            
            # Get Gemini response if available
            if self.gemini_api_key:
                gemini_response = self.gemini_model.generate_content(prompt)
                responses.append(gemini_response.text)
            
            if not responses:
                return "AI services not configured. Please check API keys.", 0.0
            
            # Calculate confidence
            if len(responses) == 2:
                confidence = self._calculate_confidence(responses[0], responses[1])
            else:
                confidence = 0.75  # Single AI response
            
            return responses[0], confidence
            
        except Exception as e:
            return f"AI error: {str(e)}", 0.0
    
    def _calculate_confidence(self, response1: str, response2: str) -> float:
        """Calculate confidence score based on AI agreement"""
        # Extract numbers from both responses
        numbers1 = set(re.findall(r'\d+', response1))
        numbers2 = set(re.findall(r'\d+', response2))
        
        # Extract key terms
        terms1 = set(response1.lower().split())
        terms2 = set(response2.lower().split())
        
        # Calculate overlap
        if numbers1 and numbers2:
            number_overlap = len(numbers1.intersection(numbers2)) / len(numbers1.union(numbers2))
        else:
            number_overlap = 0.5
        
        term_overlap = len(terms1.intersection(terms2)) / max(len(terms1.union(terms2)), 1)
        
        # Weight numbers more heavily for financial data
        confidence = (number_overlap * 0.7) + (term_overlap * 0.3)
        
        return min(confidence, 0.99)  # Cap at 99%
