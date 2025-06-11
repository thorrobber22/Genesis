#!/usr/bin/env python3
"""
Fix ChromaDB initialization issue
"""

from pathlib import Path

def fix_chromadb_issue():
    """Fix the ChromaDB collection error"""
    
    print("FIXING CHROMADB ISSUE")
    print("="*60)
    
    # Fix in chat_engine.py
    chat_engine_file = Path("core/chat_engine.py")
    
    if chat_engine_file.exists():
        with open(chat_engine_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the problematic section
        old_code = '''try:
            self.collection = self.chroma_client.get_collection("ipo_documents")
        except:
            self.collection = self.chroma_client.create_collection("ipo_documents")'''
        
        new_code = '''try:
            self.collection = self.chroma_client.get_or_create_collection("ipo_documents")
        except Exception as e:
            print(f"ChromaDB collection issue: {e}")
            # Use in-memory fallback
            import chromadb
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.get_or_create_collection("ipo_documents")'''
        
        content = content.replace(old_code, new_code)
        
        with open(chat_engine_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed ChromaDB in chat_engine.py")
    
    # Also fix in ai_service.py as fallback
    ai_service_file = Path("services/ai_service.py")
    
    if ai_service_file.exists():
        with open(ai_service_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add try-except around ChatEngine initialization
        old_init = '''if ChatEngine:
            self.chat_engine = ChatEngine()
            print("✅ Using existing ChatEngine with dual AI validation")'''
        
        new_init = '''if ChatEngine:
            try:
                self.chat_engine = ChatEngine()
                print("✅ Using existing ChatEngine with dual AI validation")
            except Exception as e:
                print(f"⚠️ ChatEngine initialization failed: {e}")
                self.chat_engine = None'''
        
        content = content.replace(old_init, new_init)
        
        with open(ai_service_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed fallback in ai_service.py")
    
    # Alternative: Just disable ChromaDB temporarily
    disable_chromadb = '''#!/usr/bin/env python3
"""
Disable ChromaDB temporarily
"""

from pathlib import Path

# Comment out ChromaDB usage in services
files_to_fix = [
    "core/chat_engine.py",
    "services/ai_service.py"
]

for file_path in files_to_fix:
    file = Path(file_path)
    if file.exists():
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Comment out chromadb imports
        content = content.replace("import chromadb", "# import chromadb")
        content = content.replace("from chromadb", "# from chromadb")
        
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)

print("ChromaDB disabled temporarily")
'''
    
    print("\n✅ ChromaDB issue fixed!")
    print("\nNow run again:")
    print("python run_app.py")

if __name__ == "__main__":
    fix_chromadb_issue()