#!/usr/bin/env python3
"""
Test ChatEngine Integration
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent))

def test_chat_engine_directly():
    """Test ChatEngine directly"""
    print("🧪 TESTING CHAT ENGINE DIRECTLY")
    print("="*70)
    
    try:
        from core.chat_engine import ChatEngine
        
        engine = ChatEngine()
        print("✅ ChatEngine initialized")
        
        # Test query
        response = engine.get_response("What is an IPO lock-up period?")
        
        print(f"\nResponse: {response.get('content', 'No response')[:200]}...")
        print(f"Actions: {len(response.get('actions', []))} available")
        
        return True
        
    except Exception as e:
        print(f"❌ ChatEngine error: {e}")
        return False

def test_through_ai_service():
    """Test through AIService wrapper"""
    print("\n🧪 TESTING THROUGH AI SERVICE")
    print("="*70)
    
    try:
        from services.ai_service import AIService
        
        ai = AIService()
        
        # Test with context
        test_context = [{
            'content': 'Circle Internet Financial filed its S-1 for IPO...',
            'metadata': {'source': 'CRCL_S1.html', 'page': 1}
        }]
        
        response, confidence = ai.get_ai_response(
            "What company filed for IPO?",
            test_context
        )
        
        print(f"Response: {response[:200]}...")
        print(f"Confidence: {confidence}")
        
        return len(response) > 10
        
    except Exception as e:
        print(f"❌ AIService error: {e}")
        return False

def main():
    print("🔧 CHAT ENGINE INTEGRATION TEST")
    print("="*70)
    
    # Test both ways
    direct_works = test_chat_engine_directly()
    wrapper_works = test_through_ai_service()
    
    print("\n📊 RESULTS:")
    print(f"  ChatEngine direct: {'✅ PASS' if direct_works else '❌ FAIL'}")
    print(f"  AIService wrapper: {'✅ PASS' if wrapper_works else '❌ FAIL'}")
    
    if direct_works and wrapper_works:
        print("\n✅ Full integration successful!")
    else:
        print("\n❌ Integration needs fixes")

if __name__ == "__main__":
    main()
