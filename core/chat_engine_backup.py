"""
Chat Engine with RAG and Dual AI Validation
"""

import os
from typing import Dict, List
import openai
import google.generativeai as genai
from chromadb import Client
from chromadb.config import Settings
import json
from pathlib import Path

class ChatEngine:
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
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
            # Primary response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an IPO analysis assistant. Always cite sources."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Validate with Gemini if context was found
            if context and os.getenv("GEMINI_API_KEY"):
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
    
    def _build_prompt(self, query: str, context: List[Dict]) -> str:
        """Build prompt with context"""
        prompt = f"User Question: {query}\n\n"
        
        if context:
            prompt += "Relevant Context:\n"
            for i, ctx in enumerate(context):
                source = ctx["metadata"].get("source", "Unknown")
                page = ctx["metadata"].get("page", "N/A")
                prompt += f"\n[Source {i+1}: {source}, Page {page}]\n"
                prompt += f"{ctx['content'][:500]}...\n"
        
        prompt += "\nProvide a clear answer based on the context. Always cite sources."
        
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
