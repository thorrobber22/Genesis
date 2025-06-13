"""
ai_service.py - OpenAI integration service (FIXED)
Date: 2025-06-12 01:40:16 UTC
User: thorrobber22
"""

import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("[WARNING] No OPENAI_API_KEY found in .env file")
    api_key = None

# Initialize OpenAI client
try:
    if api_key:
        client = OpenAI(api_key=api_key)
        print(f"[AI Service] OpenAI client initialized")
    else:
        client = None
        print("[AI Service] Running without OpenAI - mock mode")
except Exception as e:
    print(f"[AI Service] Error initializing OpenAI: {e}")
    client = None

def get_ai_response(prompt, context=None):
    """Get AI response from GPT-4 with error handling"""
    
    # If no client, return mock response
    if not client:
        return f"[Mock Response] I would analyze: {prompt[:50]}... (OpenAI API key not configured)"
    
    try:
        messages = [
            {"role": "system", "content": "You are an expert financial analyst specializing in IPO analysis. Provide clear, concise insights."}
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Context: {context}"})
        
        messages.append({"role": "user", "content": prompt})
        
        # Make API call with error handling
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Use turbo for faster responses
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        error_msg = str(e)
        print(f"[AI Service Error] {error_msg}")
        
        # Return helpful error message
        if "api_key" in error_msg.lower():
            return "Error: Invalid API key. Please check your OPENAI_API_KEY in .env file."
        elif "rate_limit" in error_msg.lower():
            return "Error: Rate limit reached. Please wait a moment and try again."
        elif "model" in error_msg.lower():
            return "Error: Model not available. Trying to use GPT-4, but you may need GPT-3.5-turbo."
        else:
            return f"Error: Unable to get AI response. {error_msg[:100]}"

def analyze_company(ticker, data):
    """Analyze company data"""
    prompt = f"""Analyze {ticker} IPO prospect:
    Data: {str(data)[:500]}
    
    Provide:
    1. Investment thesis
    2. Key risks
    3. Growth potential
    """
    return get_ai_response(prompt)

def summarize_filing(filing_text):
    """Summarize SEC filing"""
    prompt = f"Summarize this SEC filing in 3 key points: {filing_text[:2000]}"
    return get_ai_response(prompt)

# Test on import
if __name__ == "__main__":
    print("Testing AI service...")
    test = get_ai_response("Say hello")
    print(f"Test response: {test}")
