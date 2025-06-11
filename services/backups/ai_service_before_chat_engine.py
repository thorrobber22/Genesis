#!/usr/bin/env python3
"""
Minimal AI Service - Fallback implementation
"""

from typing import List, Dict, Tuple
from openai import OpenAI
import os

class AIService:
    """Minimal working AI service"""
    
    def __init__(self):
        self.client = OpenAI()
        
    def get_ai_response(self, query: str, context: List[Dict]) -> Tuple[str, float]:
        """Get AI response with new OpenAI API"""
        
        if not context:
            return "No context provided.", 0.0
        
        try:
            # Prepare context text
            context_text = ""
            for doc in context[:3]:  # Limit to 3 documents
                source = doc.get('metadata', {}).get('source', 'Unknown')
                content = doc.get('content', '')[:1000]  # First 1000 chars
                context_text += f"\nSource: {source}\n{content}\n"
            
            # Create prompt
            prompt = f"""Based on the following SEC filing excerpts, answer this question: {query}

Context:
{context_text}

Provide a clear answer with citations to the source document."""
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful financial analyst assistant analyzing SEC filings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Simple confidence based on response length
            confidence = min(len(ai_response) / 100, 1.0) * 0.8
            
            return ai_response, confidence
            
        except Exception as e:
            return f"AI error: {str(e)}", 0.0
    
    def search_documents(self, *args, **kwargs):
        """Placeholder for document search"""
        return []
    
    def _calculate_confidence(self, *args, **kwargs):
        """Placeholder for confidence calculation"""
        return 0.5
