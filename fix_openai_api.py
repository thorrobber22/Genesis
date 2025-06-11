#!/usr/bin/env python3
"""
Fix OpenAI API calls to use new v1.0+ syntax
"""

from pathlib import Path
import re

def fix_ai_service_openai():
    """Update AIService to use new OpenAI API syntax"""
    print("🔧 FIXING OPENAI API CALLS")
    print("="*70)
    
    ai_service_path = Path("services/ai_service.py")
    
    if not ai_service_path.exists():
        print("❌ services/ai_service.py not found!")
        return
    
    with open(ai_service_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Backup current version
    backup_path = Path("services/ai_service_pre_openai_fix.py")
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📄 Backed up to {backup_path}")
    
    # Check current OpenAI usage
    print("\n🔍 Current OpenAI usage:")
    if 'openai.ChatCompletion' in content:
        print("  ❌ Using old API: openai.ChatCompletion")
    if 'from openai import OpenAI' in content:
        print("  ✅ Already has new import")
    
    # Apply fixes
    original_content = content
    
    # Fix imports
    if 'import openai' in content and 'from openai import OpenAI' not in content:
        # Replace old import with new
        content = re.sub(
            r'import openai\s*\n',
            'from openai import OpenAI\n',
            content
        )
        print("\n✅ Updated import statement")
    
    # Add client initialization if needed
    if 'from openai import OpenAI' in content and 'self.client = OpenAI' not in content:
        # Find __init__ method and add client
        init_pattern = r'(def __init__\(self.*?\):\s*\n)'
        init_replacement = r'\1        self.client = OpenAI()\n'
        content = re.sub(init_pattern, init_replacement, content)
        print("✅ Added OpenAI client initialization")
    
    # Fix ChatCompletion calls
    if 'openai.ChatCompletion.create' in content:
        # Replace with new syntax
        content = re.sub(
            r'openai\.ChatCompletion\.create\(',
            'self.client.chat.completions.create(',
            content
        )
        print("✅ Updated ChatCompletion.create calls")
    
    # Fix response access
    if '.choices[0].message.content' in content:
        # This is correct for new API
        print("✅ Response access is already correct")
    elif "['choices'][0]['message']['content']" in content:
        # Update to new format
        content = re.sub(
            r"\['choices'\]\[0\]\['message'\]\['content'\]",
            '.choices[0].message.content',
            content
        )
        print("✅ Updated response access pattern")
    
    # Write updated file
    if content != original_content:
        with open(ai_service_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("\n✅ AIService updated for OpenAI v1.0+")
    else:
        print("\n⚠️  No changes needed or manual fix required")
    
    # Show a sample of the fixed code
    show_fixed_sample(ai_service_path)

def show_fixed_sample(ai_service_path):
    """Show how the fixed code should look"""
    print("\n📄 Sample of how get_ai_response should look:")
    
    sample_code = '''
    def get_ai_response(self, query: str, context: List[Dict]) -> Tuple[str, float]:
        """Get response from AI with confidence score"""
        
        try:
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": "You are a financial analyst assistant."},
                {"role": "user", "content": f"Query: {query}\\n\\nContext: {context}"}
            ]
            
            # Call OpenAI API (new syntax)
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            
            # Extract response (new syntax)
            ai_response = response.choices[0].message.content
            
            return ai_response, 0.8  # confidence
            
        except Exception as e:
            return f"AI error: {str(e)}", 0.0
'''
    
    print(sample_code)

def create_minimal_ai_service():
    """Create a minimal working AIService as fallback"""
    
    minimal_service = '''#!/usr/bin/env python3
"""
Minimal AI Service - Fallback implementation
"""

from typing import List, Dict, Tuple
from openai import OpenAI
import os

class AIService:
    """Minimal working AI service"""
    
    def __init__(self):
        self.client = OpenAI()
        
    def get_ai_response(self, query: str, context: List[Dict]) -> Tuple[str, float]:
        """Get AI response with new OpenAI API"""
        
        if not context:
            return "No context provided.", 0.0
        
        try:
            # Prepare context text
            context_text = ""
            for doc in context[:3]:  # Limit to 3 documents
                source = doc.get('metadata', {}).get('source', 'Unknown')
                content = doc.get('content', '')[:1000]  # First 1000 chars
                context_text += f"\\nSource: {source}\\n{content}\\n"
            
            # Create prompt
            prompt = f"""Based on the following SEC filing excerpts, answer this question: {query}

Context:
{context_text}

Provide a clear answer with citations to the source document."""
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful financial analyst assistant analyzing SEC filings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Simple confidence based on response length
            confidence = min(len(ai_response) / 100, 1.0) * 0.8
            
            return ai_response, confidence
            
        except Exception as e:
            return f"AI error: {str(e)}", 0.0
    
    def search_documents(self, *args, **kwargs):
        """Placeholder for document search"""
        return []
    
    def _calculate_confidence(self, *args, **kwargs):
        """Placeholder for confidence calculation"""
        return 0.5
'''
    
    backup_dir = Path("services/backups")
    backup_dir.mkdir(exist_ok=True)
    
    minimal_path = backup_dir / "ai_service_minimal.py"
    with open(minimal_path, 'w', encoding='utf-8') as f:
        f.write(minimal_service)
    
    print(f"\n✅ Created minimal AIService at: {minimal_path}")
    print("   You can copy this over if the fix doesn't work")

def check_openai_version():
    """Check installed OpenAI version"""
    print("\n🔍 Checking OpenAI version...")
    
    try:
        import openai
        version = openai.__version__
        print(f"  OpenAI version: {version}")
        
        if version.startswith('0.'):
            print("  ⚠️  Old version - need to upgrade!")
            print("  Run: pip install openai --upgrade")
        else:
            print("  ✅ Version 1.0+ installed")
            
    except ImportError:
        print("  ❌ OpenAI not installed!")
        print("  Run: pip install openai")

def main():
    print("🔧 OPENAI API COMPATIBILITY FIX")
    print("="*70)
    
    # Check version
    check_openai_version()
    
    # Fix AIService
    fix_ai_service_openai()
    
    # Create minimal version as backup
    create_minimal_ai_service()
    
    print("\n📋 Next steps:")
    print("1. Run: python test_complete_system.py")
    print("2. If still failing, copy the minimal service:")
    print("   cp services/backups/ai_service_minimal.py services/ai_service.py")

if __name__ == "__main__":
    main()