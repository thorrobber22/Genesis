"""
AI Service - Fixed version with get_ai_response
"""
import os
from openai import OpenAI
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