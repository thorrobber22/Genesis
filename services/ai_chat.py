"""
AI Chat wrapper for compatibility
This wraps the existing ai_service.py to provide the expected interface
"""

from services.ai_service import AIService
from services.gemini_service import GeminiService, get_gemini_service
from services.document_indexer import DocumentIndexer
import os
from typing import Optional, Dict, List

class AIChat:
    """Wrapper class to provide compatibility with expected interface"""
    
    def __init__(self):
        """Initialize with existing services"""
        self.ai_service = AIService()
        
        # Try to initialize Gemini if available
        self.gemini_service = None
        if os.getenv('GEMINI_API_KEY'):
            try:
                self.gemini_service = get_gemini_service()
            except Exception as e:
                print(f"Gemini not available: {e}")
        
        self.indexer = DocumentIndexer()
        
    def get_response(self, user_message: str, context: Optional[str] = None) -> str:
        """
        Get AI response - compatible interface
        
        Args:
            user_message: User's question
            context: Document context
            
        Returns:
            String response
        """
        if context:
            # Parse context to extract company and document info
            lines = context.split('\n')
            company = None
            document = None
            
            for line in lines:
                if 'From' in line and len(line.split()) > 1:
                    parts = line.split()
                    if len(parts) >= 2:
                        company = parts[1]
                    if len(parts) >= 3:
                        document = parts[2].rstrip(':')
                    break
            
            # Set document context if we have it
            if company and document:
                self.ai_service.set_document_context(company, document, context)
        
        # Get response from AI service
        result = self.ai_service.get_contextual_response(user_message)
        
        if result['success']:
            return result['response']
        else:
            return result['response']  # Error message
    
    def analyze_with_citations(self, query: str, search_results: List[Dict]) -> Dict:
        """Use the existing analyze_with_citations method"""
        return self.ai_service.analyze_with_citations(query, search_results)
    
    def summarize_document(self, document_text: str, focus: Optional[str] = None) -> str:
        """Summarize a document"""
        if focus:
            query = f"Summarize this document with focus on {focus}"
        else:
            query = "Provide a concise summary of this document"
            
        # Set context and get response
        self.ai_service.set_document_context("Unknown", "document", document_text)
        result = self.ai_service.get_contextual_response(query)
        
        return result['response'] if result['success'] else "Could not generate summary"
    
    def compare_companies(self, company_data: dict) -> str:
        """Compare multiple companies"""
        # Build a comparison query
        companies = list(company_data.keys())
        query = f"Compare these companies based on their SEC filings: {', '.join(companies)}. Focus on key financial metrics, growth, and risks."
        
        # Combine all context
        combined_context = ""
        for company, data in company_data.items():
            combined_context += f"\n\n=== {company} ===\n{data}"
        
        # Set context and get response
        self.ai_service.set_document_context("Multiple", "comparison", combined_context)
        result = self.ai_service.get_contextual_response(query)
        
        return result['response'] if result['success'] else "Could not generate comparison"

# For backward compatibility
def get_ai_service():
    """Get AI service instance"""
    return AIService()

def get_dual_ai_chat():
    """Get dual AI chat instance"""
    from components.ai_dual_chat import DualAIChat
    return DualAIChat()
