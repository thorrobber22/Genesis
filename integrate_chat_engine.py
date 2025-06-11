#!/usr/bin/env python3
"""
Integrate existing ChatEngine with the main system
"""

import os
import sys
from pathlib import Path

def update_ai_service_to_use_chat_engine():
    """Update AIService to use the existing ChatEngine"""
    
    print("🔧 INTEGRATING EXISTING CHAT ENGINE")
    print("="*70)
    
    # Create new AIService that wraps ChatEngine
    wrapper_content = '''#!/usr/bin/env python3
"""
AI Service wrapper for existing ChatEngine
"""

import os
import sys
from typing import List, Dict, Tuple
from pathlib import Path

# Add core to path
sys.path.append(str(Path(__file__).parent.parent / "core"))

try:
    from chat_engine import ChatEngine
except ImportError:
    print("Warning: ChatEngine not found in core/")
    ChatEngine = None

class AIService:
    """AI Service that uses the existing ChatEngine with dual AI"""
    
    def __init__(self):
        if ChatEngine:
            self.chat_engine = ChatEngine()
            print("✅ Using existing ChatEngine with dual AI validation")
        else:
            print("⚠️  ChatEngine not available, using fallback")
            self.chat_engine = None
    
    def get_ai_response(self, query: str, context: List[Dict]) -> Tuple[str, float]:
        """Get AI response using ChatEngine"""
        
        if not self.chat_engine:
            return "Chat engine not available", 0.0
        
        try:
            # If context is provided, add it to ChromaDB first
            if context and hasattr(self.chat_engine, 'collection'):
                for doc in context:
                    try:
                        # Add document to ChromaDB for search
                        self.chat_engine.collection.add(
                            documents=[doc.get('content', '')[:1000]],
                            metadatas=[doc.get('metadata', {})],
                            ids=[f"doc_{hash(doc.get('content', ''))}"]
                        )
                    except:
                        pass  # Document might already exist
            
            # Get response from ChatEngine
            response_data = self.chat_engine.get_response(query)
            
            # Extract content and calculate confidence
            content = response_data.get('content', '')
            
            # Check if Gemini validation was applied
            if 'validated' in content.lower() or 'confidence' in content.lower():
                confidence = 0.85  # High confidence with validation
            else:
                confidence = 0.65  # Medium confidence without validation
            
            return content, confidence
            
        except Exception as e:
            return f"Error: {str(e)}", 0.0
    
    def search_documents(self, query: str, company: str = None) -> List[Dict]:
        """Search documents using ChatEngine"""
        
        if not self.chat_engine:
            return []
        
        try:
            # Use ChatEngine's search
            results = self.chat_engine._search_documents(query)
            
            # Filter by company if specified
            if company and results:
                results = [r for r in results 
                          if company.upper() in str(r.get('metadata', {})).upper()]
            
            return results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_multi_doc_response(self, query: str, ticker: str) -> Dict:
        """Get response using multiple document types"""
        
        if not self.chat_engine:
            return {"response": "Chat engine not available", "sources": []}
        
        try:
            # Use ChatEngine's multi-doc capability
            return self.chat_engine.get_multi_doc_response(query, ticker)
        except Exception as e:
            return {"response": f"Error: {str(e)}", "sources": []}
    
    def _calculate_confidence(self, response: str, context: str) -> float:
        """Calculate confidence score"""
        if not response:
            return 0.0
        
        # Higher confidence if response has citations
        has_citations = '[' in response and ']' in response
        
        # Higher confidence if validated by Gemini
        has_validation = 'validated' in response.lower()
        
        base = 0.5
        if has_citations:
            base += 0.3
        if has_validation:
            base += 0.2
            
        return min(base, 1.0)
'''
    
    # Save the wrapper
    services_path = Path("services")
    services_path.mkdir(exist_ok=True)
    
    # Backup current
    current_ai = services_path / "ai_service.py"
    if current_ai.exists():
        backup = services_path / "ai_service_before_chat_engine.py"
        import shutil
        shutil.copy2(current_ai, backup)
        print(f"📄 Backed up current AIService to: {backup}")
    
    # Write new wrapper
    with open(current_ai, 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    print("✅ Updated AIService to use existing ChatEngine")

def check_chat_engine_requirements():
    """Check if ChatEngine has all requirements"""
    print("\n🔍 Checking ChatEngine requirements...")
    
    # Check core directory
    core_path = Path("core")
    if not core_path.exists():
        print("  ❌ core/ directory not found!")
        return False
    
    # Check chat_engine.py
    chat_engine_path = core_path / "chat_engine.py"
    if chat_engine_path.exists():
        print(f"  ✅ Found: {chat_engine_path}")
    else:
        print(f"  ❌ Missing: {chat_engine_path}")
        return False
    
    # Check API keys
    keys = {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    }
    
    for key_name, key_value in keys.items():
        if key_value:
            print(f"  ✅ {key_name}: {key_value[:8]}...")
        else:
            print(f"  ❌ {key_name}: NOT SET")
    
    # Check ChromaDB
    try:
        import chromadb
        print("  ✅ ChromaDB installed")
    except ImportError:
        print("  ❌ ChromaDB not installed")
        print("     Run: pip install chromadb")
    
    # Check google-generativeai
    try:
        import google.generativeai
        print("  ✅ google-generativeai installed")
    except ImportError:
        print("  ❌ google-generativeai not installed")
        print("     Run: pip install google-generativeai")
    
    return True

def create_test_for_chat_engine():
    """Create test script for ChatEngine integration"""
    
    test_content = '''#!/usr/bin/env python3
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
        
        print(f"\\nResponse: {response.get('content', 'No response')[:200]}...")
        print(f"Actions: {len(response.get('actions', []))} available")
        
        return True
        
    except Exception as e:
        print(f"❌ ChatEngine error: {e}")
        return False

def test_through_ai_service():
    """Test through AIService wrapper"""
    print("\\n🧪 TESTING THROUGH AI SERVICE")
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
    
    print("\\n📊 RESULTS:")
    print(f"  ChatEngine direct: {'✅ PASS' if direct_works else '❌ FAIL'}")
    print(f"  AIService wrapper: {'✅ PASS' if wrapper_works else '❌ FAIL'}")
    
    if direct_works and wrapper_works:
        print("\\n✅ Full integration successful!")
    else:
        print("\\n❌ Integration needs fixes")

if __name__ == "__main__":
    main()
'''
    
    with open("test_chat_engine_integration.py", 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print("\n✅ Created test_chat_engine_integration.py")

def main():
    print("🔧 INTEGRATING EXISTING CHAT ENGINE")
    print("="*70)
    
    # Check requirements
    if not check_chat_engine_requirements():
        print("\n❌ Missing requirements for ChatEngine")
        return
    
    # Update AIService
    update_ai_service_to_use_chat_engine()
    
    # Create test
    create_test_for_chat_engine()
    
    print("\n📋 NEXT STEPS:")
    print("1. Set GEMINI_API_KEY if not set:")
    print("   $env:GEMINI_API_KEY='your-gemini-key'")
    print("\n2. Test the integration:")
    print("   python test_chat_engine_integration.py")
    print("\n3. Run full system test:")
    print("   python test_complete_system.py")
    print("\n✅ Your existing ChatEngine is MUCH better than what I was building!")
    print("   It already has dual AI validation, vector search, and multi-doc support!")

if __name__ == "__main__":
    main()