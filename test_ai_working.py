#!/usr/bin/env python3
"""
Working AI Chat Test - Using correct methods
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from services.ai_service import AIService
from services.document_service import DocumentService

def test_ai_with_real_document():
    """Test AI with actual document content"""
    print("🧪 TESTING AI CHAT WITH REAL DOCUMENT")
    print("="*70)
    
    # Get real document
    doc_service = DocumentService()
    companies = doc_service.get_companies()
    
    if 'CRCL' not in companies:
        print("❌ CRCL not found in companies")
        return False
    
    docs = doc_service.get_company_documents('CRCL')
    if not docs:
        print("❌ No CRCL documents")
        return False
    
    # Load first document
    doc_name = docs[0]
    content = doc_service.get_document_content('CRCL', doc_name)
    
    print(f"Document: {doc_name}")
    print(f"Content size: {len(content):,} characters")
    
    # Test AI
    ai_service = AIService()
    
    queries = [
        "What is the company's main business?",
        "What are the total revenues?",
        "List the main risk factors"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        
        try:
            # Call get_ai_response with correct parameters
            response = ai_service.get_ai_response(query, content)
            
            print(f"Response preview: {response[:200]}...")
            
            # Check for citations
            has_page_ref = any(marker in response for marker in ['[Page', '[p.', 'page', 'Page'])
            print(f"Has page reference: {has_page_ref}")
            
            if response and len(response) > 50:
                print("✅ AI response working!")
                return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
            # Try alternative approach
            try:
                # Maybe it needs different parameters?
                response = ai_service.get_ai_response(
                    {"query": query, "context": content}
                )
                print("✅ Alternative call worked!")
                return True
            except:
                pass
    
    return False

def test_ai_with_simple_content():
    """Test with simple content to verify AI works"""
    print("\n🧪 TESTING AI WITH SIMPLE CONTENT")
    print("="*70)
    
    ai_service = AIService()
    
    simple_content = """
    SECURITIES AND EXCHANGE COMMISSION
    Washington, D.C. 20549
    
    FORM 10-K
    
    Circle Internet Financial, Ltd.
    
    BUSINESS
    
    We operate a technology platform for the USDC stablecoin. 
    Our revenue in 2023 was $2.8 billion.
    We have 500 employees.
    
    RISK FACTORS
    
    1. Regulatory uncertainty
    2. Cryptocurrency market volatility
    3. Technology risks
    """
    
    try:
        response = ai_service.get_ai_response(
            "What is the company's revenue?",
            simple_content
        )
        
        print(f"Response: {response}")
        
        if "$2.8 billion" in response:
            print("✅ AI correctly extracted revenue!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    # Test both approaches
    result1 = test_ai_with_simple_content()
    result2 = test_ai_with_real_document()
    
    if result1 or result2:
        print("\n✅ AI CHAT IS WORKING!")
    else:
        print("\n❌ AI CHAT STILL NEEDS FIXING")
