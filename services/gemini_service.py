#!/usr/bin/env python3
"""
Gemini AI Service - Google's AI for document analysis
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import google.generativeai as genai
from datetime import datetime
import json
import re

class GeminiService:
    def __init__(self):
        """Initialize Gemini AI service"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model (Gemini 1.5 Pro for best performance)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Cache for document chunks
        self.chunk_cache = {}
        
    def analyze_document_with_citations(self, 
                                      query: str, 
                                      document_sections: List[Dict],
                                      temperature: float = 0.3) -> Dict:
        """
        Analyze document with Gemini and return citations
        
        Args:
            query: User's question
            document_sections: List of document sections with metadata
            temperature: Model temperature (0.0-1.0)
            
        Returns:
            Dict with response and citations
        """
        try:
            # Build context from document sections
            context_parts = []
            citation_map = {}
            
            for idx, section in enumerate(document_sections[:10]):  # Limit to top 10
                citation_id = f"[{idx+1}]"
                citation_map[citation_id] = {
                    'title': section.get('title', 'Untitled'),
                    'company': section.get('company', 'Unknown'),
                    'document': section.get('document', 'Unknown'),
                    'section_type': section.get('section_type', 'general'),
                    'text': section.get('text', '')[:500]  # Preview
                }
                
                context_parts.append(
                    f"{citation_id} {section.get('title', 'Section')} - {section.get('company', 'Company')}\n"
                    f"{section.get('text', '')[:1000]}\n"
                )
            
            # Build the prompt
            prompt = self._build_analysis_prompt(query, context_parts, citation_map)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=2048,
                )
            )
            
            # Extract citations from response
            response_text = response.text
            citations_used = self._extract_citations(response_text, citation_map)
            
            return {
                'response': response_text,
                'citations': citations_used,
                'model': 'gemini-1.5-pro',
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'temperature': temperature
            }
            
        except Exception as e:
            return {
                'response': f"Error with Gemini analysis: {str(e)}",
                'citations': [],
                'model': 'gemini-1.5-pro',
                'error': str(e)
            }
    
    def _build_analysis_prompt(self, query: str, context_parts: List[str], citation_map: Dict) -> str:
        """Build the analysis prompt for Gemini"""
        prompt = f"""You are a financial analyst assistant analyzing SEC documents. 
You have access to the following document sections:

{''.join(context_parts)}

IMPORTANT INSTRUCTIONS:
1. Answer the following question using ONLY the information provided above
2. You MUST cite your sources using [1], [2], etc. when referencing information
3. Be specific and accurate - this is for hedge fund analysis
4. If information is not available in the provided sections, say so clearly
5. Use multiple citations if drawing from multiple sources

Question: {query}

Remember to include [citation numbers] whenever you reference information from the sections above."""
        
        return prompt
    
    def _extract_citations(self, response: str, citation_map: Dict) -> List[Dict]:
        """Extract citations used in the response"""
        citations = []
        
        # Find all citation references in the response
        citation_pattern = r'\[(\d+)\]'
        matches = re.findall(citation_pattern, response)
        
        # Get unique citations in order of appearance
        seen = set()
        for match in matches:
            citation_id = f"[{match}]"
            if citation_id not in seen and citation_id in citation_map:
                seen.add(citation_id)
                citations.append(citation_map[citation_id])
        
        return citations
    
    def compare_with_gpt(self, query: str, gpt_response: Dict, document_sections: List[Dict]) -> Dict:
        """
        Run the same query through Gemini for comparison
        
        Args:
            query: Original query
            gpt_response: Response from GPT-4
            document_sections: Document sections used
            
        Returns:
            Comparison analysis
        """
        # Get Gemini's analysis
        gemini_result = self.analyze_document_with_citations(
            query=query,
            document_sections=document_sections,
            temperature=0.3
        )
        
        # Build comparison prompt
        comparison_prompt = f"""Compare these two AI analyses of SEC documents:

QUERY: {query}

GPT-4 ANALYSIS:
{gpt_response.get('response', 'No response')}

GEMINI ANALYSIS:
{gemini_result.get('response', 'No response')}

Provide a brief comparison highlighting:
1. Key agreements between the analyses
2. Any significant differences or contradictions
3. Which points seem most reliable based on citations
4. Overall confidence level in the combined analysis

Keep it concise and focused on actionable insights."""
        
        # Get comparison
        comparison = self.model.generate_content(comparison_prompt)
        
        return {
            'gemini_response': gemini_result,
            'comparison': comparison.text,
            'timestamp': datetime.now().isoformat()
        }
    
    def extract_key_metrics(self, document_text: str, company: str) -> Dict:
        """Extract key financial metrics using Gemini"""
        prompt = f"""Extract key financial metrics from this SEC document for {company}.

Document excerpt:
{document_text[:4000]}

Extract and return in a structured format:
1. Revenue figures (with periods)
2. Profit/Loss numbers
3. Key ratios mentioned
4. Growth percentages
5. Any forward-looking guidance

If a metric is not found, omit it. Be precise with numbers and include units."""
        
        try:
            response = self.model.generate_content(prompt)
            return {
                'metrics': response.text,
                'company': company,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}

# Singleton instance
_gemini_service = None

def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service