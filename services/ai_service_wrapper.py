#!/usr/bin/env python3
"""
AI Service Wrapper - Handles parameter compatibility
"""

from services.ai_service import AIService as OriginalAIService

class AIServiceWrapper:
    """Wrapper that handles different parameter formats"""
    
    def __init__(self):
        self.original_service = OriginalAIService()
        
    def get_ai_response(self, query_or_dict, context=None):
        """Handle both dictionary and separate parameters"""
        
        # If it's a dictionary
        if isinstance(query_or_dict, dict):
            return self.original_service.get_ai_response(query_or_dict)
        
        # If it's separate parameters
        elif isinstance(query_or_dict, str) and context is not None:
            # Convert to expected format
            params = {
                'query': query_or_dict,
                'context': context
            }
            return self.original_service.get_ai_response(params)
        
        # If just a query string
        elif isinstance(query_or_dict, str):
            params = {
                'query': query_or_dict,
                'context': ''
            }
            return self.original_service.get_ai_response(params)
        
        else:
            raise ValueError(f"Unexpected parameter type: {type(query_or_dict)}")
    
    def __getattr__(self, name):
        """Pass through other methods"""
        return getattr(self.original_service, name)

# Export wrapper as AIService
AIService = AIServiceWrapper
