#!/usr/bin/env python3
"""
Enhanced AI Service with Context Awareness
Fixed for OpenAI v1.0+ API
"""

import os
from typing import Dict, List, Optional, Tuple
from openai import OpenAI
from datetime import datetime
import json
from pathlib import Path

class AIService:
    def __init__(self):
        self.client = None
        self.conversation_history = []
        self.current_context = {}
        self.load_api_keys()
        
    def load_api_keys(self):
        """Load API keys from environment"""
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.client = OpenAI(api_key=openai_key)
            
    def set_document_context(self, company: str, document: str, content: str):
        """Set the current document context"""
        self.current_context = {
            "company": company,
            "document": document,
            "content": content[:5000],  # First 5000 chars
            "set_at": datetime.now().isoformat()
        }
        
    def get_contextual_response(self, query: str) -> Dict:
        """Get AI response with full context awareness"""
        
        # Build context-aware prompt
        system_prompt = """You are a financial analyst AI assistant specializing in SEC filings.
You have access to the current document context and should provide specific, detailed answers.
Always cite specific sections when referencing the document.
If asked about financials, extract actual numbers.
Format your responses with clear structure."""

        # Add document context if available
        if self.current_context:
            context_prompt = f"""
Current Document Context:
Company: {self.current_context['company']}
Document: {self.current_context['document']}
Content Preview: {self.current_context['content'][:1000]}...

Analyze this document to answer the user's question. Be specific and cite sections.
"""
        else:
            context_prompt = "No specific document loaded. Provide general SEC filing guidance."
            
        # Add conversation history for continuity
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": context_prompt}
        ]
        
        # Add last 5 conversations for context
        for conv in self.conversation_history[-5:]:
            messages.append({"role": "user", "content": conv["user"]})
            messages.append({"role": "assistant", "content": conv["assistant"]})
            
        # Add current query
        messages.append({"role": "user", "content": query})
        
        try:
            if self.client:
                # Use the new v1.0+ API
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                answer = response.choices[0].message.content
                
                # Save to history
                self.conversation_history.append({
                    "user": query,
                    "assistant": answer,
                    "timestamp": datetime.now().isoformat(),
                    "context": self.current_context.get("document", "General")
                })
                
                # Extract confidence based on response quality
                confidence = 0.95 if self.current_context else 0.7
                
                return {
                    "success": True,
                    "response": answer,
                    "confidence": confidence,
                    "context": self.current_context,
                    "sources": self._extract_sources(answer)
                }
            else:
                return {
                    "success": False,
                    "response": "AI service not configured. Please set OPENAI_API_KEY.",
                    "confidence": 0
                }
                
        except Exception as e:
            return {
                "success": False,
                "response": f"Error: {str(e)}",
                "confidence": 0
            }
            
    def _extract_sources(self, response: str) -> List[Dict]:
        """Extract source citations from response"""
        sources = []
        
        # Look for section references
        import re
        section_pattern = r'(?:Section|Part|Item)\s+([A-Z0-9.-]+)'
        sections = re.findall(section_pattern, response, re.IGNORECASE)
        
        for section in sections:
            sources.append({
                "type": "section",
                "reference": section,
                "document": self.current_context.get("document", "Unknown")
            })
            
        return sources
        
    def analyze_document(self, company: str, document_path: Path) -> Dict:
        """Perform deep analysis on a document"""
        
        try:
            with open(document_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Set context
            self.set_document_context(company, document_path.name, content)
            
            # Perform structured analysis
            analyses = {
                "summary": self.get_contextual_response("Provide a concise executive summary of this document"),
                "financials": self.get_contextual_response("Extract all key financial metrics and numbers"),
                "risks": self.get_contextual_response("What are the main risk factors mentioned?"),
                "outlook": self.get_contextual_response("What is the company's forward-looking guidance?")
            }
            
            return {
                "success": True,
                "company": company,
                "document": document_path.name,
                "analyses": analyses,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
            
    def search_across_documents(self, query: str, companies: List[str]) -> List[Dict]:
        """Search across multiple documents"""
        results = []
        
        sec_dir = Path("data/sec_documents")
        
        for company in companies:
            company_dir = sec_dir / company
            if company_dir.exists():
                for doc in company_dir.glob("*.html"):
                    try:
                        with open(doc, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        if query.lower() in content.lower():
                            # Get context around match
                            idx = content.lower().find(query.lower())
                            start = max(0, idx - 200)
                            end = min(len(content), idx + 200)
                            snippet = content[start:end]
                            
                            results.append({
                                "company": company,
                                "document": doc.name,
                                "snippet": snippet,
                                "relevance": 0.9
                            })
                            
                    except:
                        continue
                        
        return results
    
    def analyze_with_citations(self, query: str, search_results: List[Dict]) -> Dict:
        """Analyze with proper citations"""
        if not self.client:
            return {
                "response": "AI service not configured",
                "citations": []
            }
        
        # Build context from search results
        context_parts = []
        citations = []
        
        for i, result in enumerate(search_results[:5]):
            context_parts.append(f"[{i+1}] From {result['title']} ({result['company']}):\n{result.get('text', '')[:500]}\n")
            citations.append({
                'title': result['title'],
                'company': result['company'],
                'document': result.get('document', ''),
                'text': result.get('text', '')[:300]
            })
        
        prompt = f"""Based on these document sections:

{''.join(context_parts)}

Question: {query}
    def get_response_with_sources(self, query: str, context: str = None) -> Dict:
        """Get AI response with source documents"""
        from typing import Dict
        
        # Search for relevant documents
        search_query = query
        if context:
            search_query = f"{context} {query}"
        
        # Get relevant chunks from vector store (if available)
        relevant_chunks = []
        if hasattr(self, 'vector_store') and self.vector_store:
            try:
                relevant_chunks = self.vector_store.similarity_search(
                    search_query,
                    k=5  # Top 5 most relevant chunks
                )
            except:
                pass
        
        # Build context from chunks
        context_text = ""
        if relevant_chunks:
            context_text = "\n\n".join([
                f"[{i+1}] {chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)}"
                for i, chunk in enumerate(relevant_chunks)
            ])
        
        # Get AI response
        if context_text:
            prompt = f"""Based on the following context, answer the question.
        
Context:
{context_text}

Question: {query}

Answer: """
        else:
            prompt = query
        
        response = self.chat(prompt)
        
        # Return response with sources
        return {
            'response': response,
            'sources': [
                {
                    'text': chunk.page_content if hasattr(chunk, 'page_content') else str(chunk),
                    'metadata': chunk.metadata if hasattr(chunk, 'metadata') else {}
                }
                for chunk in relevant_chunks
            ]
        }


Please answer using the information above. Include citation numbers [1], [2], etc."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst. Use citations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return {
                "response": response.choices[0].message.content,
                "citations": citations
            }
        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "citations": []
            }