"""
<<<<<<< HEAD
AI Service - Fixed version with get_ai_response
=======
Enhanced AI Service - IPO Intelligence Focused
Date: 2025-01-12 02:24:23 UTC
User: thorrobber22
>>>>>>> 7bda5bb3f199dc2d74016e366f0a956b33545e5c
"""
import os
from openai import OpenAI
<<<<<<< HEAD
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key) if api_key else None

def get_ai_response(prompt, context=""):
    """Get AI response for the chat - MAIN FUNCTION USED BY APP"""
    if not client:
        return "❌ OpenAI API key not configured. Please add OPENAI_API_KEY to .env file"
    
    try:
        # Build context-aware prompt
        system_message = "You are a helpful IPO research assistant for Hedge Intelligence. You have expertise in IPO analysis, S-1 filings, and market trends."
        
        # Add ticker context if available
        if context and context != "General":
            user_message = f"{context}\n\nUser Question: {prompt}"
        else:
            user_message = prompt
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Legacy class support (if needed elsewhere)
class AIService:
    """Legacy class - kept for compatibility"""
    def __init__(self):
        self.client = client
    
    def get_response(self, prompt, context=""):
        return get_ai_response(prompt, context)
=======
from datetime import datetime
import json

class IPOIntelligenceAI:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("[AI Service] IPO Intelligence AI initialized")
        
        # System prompt for IPO-focused responses
        self.system_prompt = """You are the AI assistant for Hedge Intelligence, an IPO tracking platform.

IMPORTANT INSTRUCTIONS:
1. Keep responses CONCISE (2-3 sentences unless asked for details)
2. You have access to real-time IPO data including:
   - Active IPOs: TECH, BIO, FINX (as examples)
   - Recent filings: S-1, S-1/A, 424B4 documents
   - Lockup periods and dates
3. When asked about "IPOs you're monitoring", mention specific tickers
4. Be specific, not generic
5. Focus on actionable intelligence

Current date: {date}
Platform: Hedge Intelligence Terminal
"""

    def get_ipo_context(self):
        """Get current IPO data context"""
        # In production, this would query your database
        return {
            "active_ipos": ["TECH", "BIO", "FINX", "CLOU", "SOFT"],
            "this_week": ["TECH (6/15)", "BIO (6/14)"],
            "watchlist": ["TECH", "FINX"],
            "recent_filings": {
                "TECH": "S-1/A filed 6/1",
                "BIO": "424B4 filed 6/10"
            }
        }

    def get_response(self, prompt, context="general"):
        """Get AI response with IPO context"""
        try:
            # Add IPO data to context
            ipo_data = self.get_ipo_context()
            
            # Enhanced prompt with context
            enhanced_prompt = f"""
User query: {prompt}

Available IPO data:
- Active IPOs: {', '.join(ipo_data['active_ipos'])}
- This week: {', '.join(ipo_data['this_week'])}
- On watchlist: {', '.join(ipo_data['watchlist'])}
"""
            
            messages = [
                {"role": "system", "content": self.system_prompt.format(date=datetime.now().strftime("%Y-%m-%d"))},
                {"role": "user", "content": enhanced_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=150,  # Limit response length
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {str(e)}"

# Global instance
ai_service = IPOIntelligenceAI()

def get_ai_response(prompt, context="general"):
    """Main function for compatibility"""
    return ai_service.get_response(prompt, context)
>>>>>>> 7bda5bb3f199dc2d74016e366f0a956b33545e5c
