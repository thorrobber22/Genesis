"""
AI Service Enhanced - With citation extraction
Date: 2025-06-14 02:51:06 UTC
Author: thorrobber22
"""

import openai
import json
import re
import os
from typing import Dict, List, Optional
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EnhancedAIService:
    """AI service with document understanding and citations"""
    
    def __init__(self):
        # Try to get API key from environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            openai.api_key = self.api_key
            print("✅ OpenAI API key loaded from .env")
        else:
            print("⚠️ No OpenAI API key found - using mock responses")
    
    def get_document_response(self, query: str, document_context: dict) -> dict:
        """Get AI response with citations for document questions"""
        
        # Build context
        context = f"""
        Document: {document_context.get('title', 'Unknown')}
        Current Page: {document_context.get('current_page', 1)}
        Total Pages: {document_context.get('total_pages', 0)}
        
        Page Text:
        {document_context.get('page_text', '')}
        """
        
        # System prompt for citation awareness
        system_prompt = """
        You are a financial analyst assistant analyzing IPO documents.
        When answering questions:
        1. Provide specific, accurate information
        2. Always cite the page number where you found the information
        3. Use this format for citations: [Page 147]
        4. Be concise but thorough
        5. If information spans multiple pages, cite all relevant pages
        """
        
        # If we have API key, use real OpenAI
        if self.api_key:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                answer = response.choices[0].message.content
                
                # Extract citations
                citations = self._extract_citations(answer)
                
                return {
                    'answer': answer,
                    'citations': citations,
                    'confidence': 0.95
                }
                
            except Exception as e:
                print(f"OpenAI API error: {e}")
                # Fall through to mock response
        
        # Use mock response if no API key or error
        return {
            'answer': self._get_mock_response(query, document_context),
            'citations': self._extract_citations(self._get_mock_response(query, document_context)),
            'confidence': 0.8
        }
    
    def _get_mock_response(self, query: str, context: dict) -> str:
        """Provide mock responses for demo purposes"""
        query_lower = query.lower()
        
        if "lockup" in query_lower or "lock-up" in query_lower:
            return """The lockup period is **180 days** from IPO [Page 147]
            
            Key terms:
            - Coverage: **85%** of outstanding shares
            - Executive extension: **+90 days** (270 total)
            - Early release: If stock >40% above IPO for 10 days
            
            The lockup prevents insiders from selling shares immediately after IPO, providing market stability."""
            
        elif "risk" in query_lower:
            return """Key risk factors identified [Page 52-67]:
            
            1. **Market Competition** - Intense competition from established players
            2. **Regulatory Changes** - Subject to evolving regulations
            3. **Key Personnel Dependency** - Reliance on founding team
            4. **Technology Risks** - Platform scalability concerns
            5. **Customer Concentration** - Top 10 customers = 45% of revenue"""
            
        elif "financial" in query_lower or "revenue" in query_lower:
            return """Financial Highlights [Page 201]:
            
            - Revenue: **$450M** (67% YoY growth)
            - Gross Margin: **72%** (up from 68%)
            - Operating Loss: **($45M)** improving from ($89M)
            - Cash: **$125M** (18 months runway)
            - ARR: **$520M** (75% growth)"""
            
        elif "underwriter" in query_lower:
            return """Lead Underwriters [Page 23]:
            
            - **Goldman Sachs & Co. LLC** (Lead Left)
            - **Morgan Stanley** (Lead Right)
            - **J.P. Morgan Securities LLC**
            - **BofA Securities, Inc.**
            
            Total underwriting fees: 7% of gross proceeds"""
            
        else:
            return f"""I can help you analyze this {context.get('title', 'document')}. 
            
            Try asking about:
            - Lockup terms and restrictions
            - Risk factors and challenges
            - Financial performance and metrics
            - Underwriters and offering details
            - Use of proceeds"""
    
    def _extract_citations(self, text: str) -> List[Dict]:
        """Extract page citations from AI response"""
        citations = []
        
        # Pattern for [Page 123] format
        pattern = r'\[Page\s+(\d+)(?:-(\d+))?\]'
        matches = re.finditer(pattern, text)
        
        for match in matches:
            page_num = int(match.group(1))
            end_page = int(match.group(2)) if match.group(2) else page_num
            
            citations.append({
                'page': page_num,
                'end_page': end_page,
                'text': match.group(0),
                'start': match.start(),
                'end': match.end()
            })
        
        return citations
    
    def get_quick_analysis(self, doc_type: str, doc_path: str) -> list:
        """Generate quick analysis options based on document type"""
        
        quick_actions = {
            'S-1': [
                "What are the lockup terms?",
                "Show me risk factors",
                "Summarize financials",
                "What is the use of proceeds?",
                "Who are the underwriters?"
            ],
            'S-1/A': [
                "What changed in this amendment?",
                "Show me updated financials",
                "What are the lockup terms?",
                "Any new risk factors?"
            ],
            '10-K': [
                "What was revenue growth?",
                "Show me segment breakdown",
                "Summarize key metrics",
                "What are main risks?"
            ]
        }
        
        # Determine document type
        doc_type_key = 'S-1'
        if 'S-1/A' in doc_type:
            doc_type_key = 'S-1/A'
        elif '10-K' in doc_type:
            doc_type_key = '10-K'
            
        return quick_actions.get(doc_type_key, ["Summarize this document"])
    
    def compare_companies(self, ticker1: str, ticker2: str, metric: str) -> dict:
        """Compare two companies on specific metrics"""
        
        return {
            'comparison': f"Comparing {ticker1} vs {ticker2} on {metric}",
            'data': {
                ticker1: {"value": "Data from documents", "source": "S-1 Page 89"},
                ticker2: {"value": "Data from documents", "source": "S-1 Page 112"}
            }
        }

# Create singleton
ai_service = EnhancedAIService()
