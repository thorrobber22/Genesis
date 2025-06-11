#!/usr/bin/env python3
"""
Fix ChatEngine to use OpenAI v1.0+ API
"""

from pathlib import Path
import shutil

def fix_chat_engine():
    """Update ChatEngine to use new OpenAI API"""
    print("🔧 FIXING CHAT ENGINE OPENAI API")
    print("="*70)
    
    chat_engine_path = Path("core/chat_engine.py")
    
    if not chat_engine_path.exists():
        print("❌ core/chat_engine.py not found!")
        return False
    
    # Backup original
    backup_path = Path("core/chat_engine_original.py")
    shutil.copy2(chat_engine_path, backup_path)
    print(f"📄 Backed up to: {backup_path}")
    
    # Read current content
    with open(chat_engine_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply fixes
    original = content
    
    # Fix import
    if 'import openai' in content and 'from openai import OpenAI' not in content:
        content = content.replace('import openai', 'from openai import OpenAI')
        print("✅ Updated import statement")
    
    # Fix initialization
    if 'openai.api_key' in content:
        # Find the line and replace
        lines = content.split('\n')
        new_lines = []
        in_init = False
        
        for line in lines:
            if 'def __init__' in line:
                in_init = True
                new_lines.append(line)
            elif in_init and 'openai.api_key' in line:
                # Skip this line, we'll add client init instead
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + '# Initialize OpenAI client')
                new_lines.append(' ' * indent + 'self.openai_client = OpenAI()')
                print("✅ Added OpenAI client initialization")
            elif in_init and ('def ' in line or 'class ' in line) and '__init__' not in line:
                in_init = False
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Fix ChatCompletion calls
    if 'openai.ChatCompletion.create' in content:
        content = content.replace(
            'openai.ChatCompletion.create',
            'self.openai_client.chat.completions.create'
        )
        print("✅ Updated ChatCompletion.create calls")
    
    # Fix response access - the response format changed
    # Old: response.choices[0].message.content or response['choices'][0]['message']['content']
    # New: response.choices[0].message.content (already correct)
    
    # Write updated file
    if content != original:
        with open(chat_engine_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ ChatEngine updated for OpenAI v1.0+")
        return True
    else:
        print("⚠️  No changes made - manual fix needed")
        create_fixed_chat_engine()
        return False

def create_fixed_chat_engine():
    """Create a fully fixed version of ChatEngine"""
    print("\n📝 Creating fixed ChatEngine...")
    
    fixed_content = '''"""
Chat Engine with RAG and Dual AI Validation
Fixed for OpenAI v1.0+ API
"""

import os
from typing import Dict, List
from openai import OpenAI
import google.generativeai as genai
from chromadb import Client
from chromadb.config import Settings
import json
from pathlib import Path

class ChatEngine:
    def __init__(self):
        # Initialize OpenAI client (new v1.0+ way)
        self.openai_client = OpenAI()
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize ChromaDB for vector search
        self.chroma_client = Client(Settings(
            persist_directory="data/chroma",
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection("ipo_documents")
        except:
            self.collection = self.chroma_client.create_collection("ipo_documents")
    
    def get_response(self, query: str) -> Dict:
        """Get AI response with context and validation"""
        # Search for relevant documents
        context = self._search_documents(query)
        
        # Build prompt
        prompt = self._build_prompt(query, context)
        
        # Get AI response
        try:
            # Primary response from OpenAI (new v1.0+ API)
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # or gpt-4 if available
                messages=[
                    {"role": "system", "content": "You are an IPO analysis assistant. Always cite sources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Validate with Gemini if context was found
            if context and (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
                validation = self._validate_with_gemini(query, content, context)
                if validation.get("needs_correction"):
                    content = validation.get("corrected_response", content)
            
            # Add action buttons if relevant
            actions = self._generate_actions(content, query)
            
            return {
                "content": content,
                "actions": actions
            }
            
        except Exception as e:
            return {
                "content": f"I apologize, I encountered an error: {str(e)}",
                "actions": []
            }
    
    def _validate_with_gemini(self, query: str, response: str, context: List[Dict]) -> Dict:
        """Validate response accuracy with Gemini"""
        try:
            validation_prompt = f"""
            User Question: {query}
            
            AI Response: {response}
            
            Context Documents: {json.dumps(context[:2])}
            
            Please validate if the AI response is accurate based on the context.
            If there are any inaccuracies, provide a corrected response.
            """
            
            gemini_response = self.gemini_model.generate_content(validation_prompt)
            
            # Simple check - you'd implement more sophisticated validation
            if "inaccurate" in gemini_response.text.lower():
                return {
                    "needs_correction": True,
                    "corrected_response": gemini_response.text
                }
            
            return {"needs_correction": False}
            
        except Exception as e:
            # If Gemini fails, just return original response
            return {"needs_correction": False}
    
    def _search_documents(self, query: str, k: int = 5) -> List[Dict]:
        """Search relevant documents using ChromaDB"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=k
            )
            
            if results and results["documents"]:
                return [
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {}
                    }
                    for i, doc in enumerate(results["documents"][0])
                ]
        except:
            pass
        
        return []
    
    def search_by_document_type(self, query: str, ticker: str, doc_types: list = None):
        """Search across multiple document types"""
        if not doc_types:
            doc_types = ["S-1", "424B4", "8-A", "Lock-up", "Financial"]
        
        all_results = []
        
        for doc_type in doc_types:
            try:
                # Search with metadata filter
                results = self.collection.query(
                    query_texts=[query],
                    n_results=3,
                    where={
                        "$and": [
                            {"ticker": {"$eq": ticker.upper()}},
                            {"document_type": {"$eq": doc_type}}
                        ]
                    }
                )
                
                # Process results
                if results and results['documents']:
                    for i, doc in enumerate(results['documents'][0]):
                        all_results.append({
                            'content': doc,
                            'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                            'score': results['distances'][0][i] if results['distances'] else 0,
                            'source_document': doc_type
                        })
                        
            except Exception as e:
                print(f"Error searching {doc_type}: {e}")
        
        # Sort by relevance
        all_results.sort(key=lambda x: x.get('score', 0))
        return all_results[:10]
    
    def get_multi_doc_response(self, query: str, ticker: str):
        """Get response using multiple document types"""
        # Search across all document types
        results = self.search_by_document_type(query, ticker)
        
        if not results:
            return {
                "response": "I couldn't find relevant information in the documents.",
                "sources": [],
                "confidence": "low"
            }
        
        # Build context from multiple sources
        context_parts = []
        sources = []
        
        for result in results:
            doc_type = result.get('source_document', 'Unknown')
            content = result.get('content', '')
            
            if content:
                context_parts.append(f"[From {doc_type}]: {content}")
                sources.append({
                    'document_type': doc_type,
                    'ticker': ticker,
                    'relevance': result.get('score', 0)
                })
        
        # Generate response with multi-doc context
        context = '\\n\\n'.join(context_parts)
        response = self.get_response(f"Based on the following information from multiple documents:\\n\\n{context}\\n\\nQuestion: {query}")
        
        # Add source information
        response['sources'] = sources
        
        return response

    def _build_prompt(self, query: str, context: List[Dict]) -> str:
        """Build prompt with context"""
        prompt = f"User Question: {query}\\n\\n"
        
        if context:
            prompt += "Relevant Context:\\n"
            for i, ctx in enumerate(context):
                source = ctx["metadata"].get("source", "Unknown")
                page = ctx["metadata"].get("page", "N/A")
                prompt += f"\\n[Source {i+1}: {source}, Page {page}]\\n"
                prompt += f"{ctx['content'][:500]}...\\n"
        
        prompt += "\\nProvide a clear answer based on the context. Always cite sources."
        
        return prompt
    
    def _generate_actions(self, response: str, query: str) -> List[Dict]:
        """Generate relevant action buttons"""
        actions = []
        
        # Check if response mentions specific documents
        if "S-1" in response or "filing" in response.lower():
            actions.append({
                "label": "View Source",
                "key": "view_source",
                "callback": lambda: None  # Implement view logic
            })
        
        # Check if report generation would be useful
        if any(word in query.lower() for word in ["lock-up", "lockup", "report", "expiration"]):
            actions.append({
                "label": "Generate Report",
                "key": "gen_report",
                "callback": lambda: None  # Implement report logic
            })
        
        return actions
'''
    
    # Save fixed version
    fixed_path = Path("core/chat_engine_fixed.py")
    with open(fixed_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Created fixed ChatEngine at: {fixed_path}")
    print("\nTo apply the fix:")
    print("  copy core\\chat_engine_fixed.py core\\chat_engine.py")

def main():
    print("🔧 FIXING CHAT ENGINE FOR OPENAI v1.0+")
    print("="*70)
    
    # Try to fix automatically
    success = fix_chat_engine()
    
    if not success:
        print("\n📋 Manual fix needed!")
        print("Apply the fixed version:")
        print("  copy core\\chat_engine_fixed.py core\\chat_engine.py")
    
    print("\n📋 After fixing, run:")
    print("  python test_chat_engine_integration.py")
    print("  python test_complete_system.py")

if __name__ == "__main__":
    main()