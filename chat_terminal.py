"""
Chat Terminal - Direct test without UI
Date: 2025-01-12 02:16:53 UTC
User: thorrobber22
"""

import os
import sys
from datetime import datetime

# Import AI service directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.ai_service import get_ai_response

print("="*60)
print("HEDGE INTELLIGENCE CHAT TERMINAL")
print("="*60)
print("Type 'exit' to quit\n")

# Test mode
test_mode = input("Enable test mode? (y/n): ").lower() == 'y'

if test_mode:
    print("\nTEST MODE: Checking AI service...")
    try:
        response = get_ai_response("test", "test")
        print(f"✓ AI Service OK: {response[:50]}...")
    except Exception as e:
        print(f"✗ AI Service Error: {e}")

print("\nChat ready. Ask about IPOs, companies, or markets.\n")

# Chat loop
while True:
    try:
        user_input = input("You: ")
        
        if user_input.lower() == 'exit':
            break
            
        # Add context
        context = f"[IPO Intelligence System] {user_input}"
        
        print("AI: ", end="", flush=True)
        response = get_ai_response(context, "ipo_analysis")
        print(response)
        print()
        
    except KeyboardInterrupt:
        print("\n\nExiting...")
        break
    except Exception as e:
        print(f"Error: {e}")
        print()

print("\nChat terminal closed.")
