#!/usr/bin/env python3
"""
Proper AI Service Test - Using correct context format
"""

from services.ai_service import AIService
from services.document_service import DocumentService

def test_with_real_document():
    """Test with real document in correct format"""
    print("🧪 TESTING AI WITH REAL DOCUMENT FORMAT")
    print("="*70)
    
    # Get real document
    doc_service = DocumentService()
    companies = doc_service.get_companies()
    
    if 'CRCL' not in companies:
        print("❌ No CRCL company found")
        return False
    
    docs = doc_service.get_company_documents('CRCL')
    if not docs:
        print("❌ No CRCL documents")
        return False
    
    # Load document
    doc_name = docs[0]
    doc_content = doc_service.get_document_content('CRCL', doc_name)
    
    print(f"Document: {doc_name}")
    print(f"Content size: {len(doc_content):,} chars")
    
    # Create context in AIService expected format
    context = [
        {
            'content': doc_content[:2000],  # First 2000 chars
            'metadata': {
                'source': doc_name,
                'company': 'CRCL',
                'type': '10-K'
            }
        }
    ]
    
    # Test AI
    ai = AIService()
    
    queries = [
        "What type of company is this?",
        "What are the main products or services?",
        "What is mentioned in the filing?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        
        try:
            response, confidence = ai.get_ai_response(query, context)
            
            print(f"Response: {str(response)[:300]}...")
            print(f"Confidence: {confidence}")
            
            if response and len(str(response)) > 50:
                print("✅ Got valid response!")
                return True
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return False

def test_with_mock_context():
    """Test with mock context in correct format"""
    print("\n🧪 TESTING WITH MOCK CONTEXT")
    print("="*70)
    
    ai = AIService()
    
    # Mock SEC filing context
    mock_context = [
        {
            'content': """UNITED STATES
SECURITIES AND EXCHANGE COMMISSION
Washington, D.C. 20549

FORM 10-K

ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE SECURITIES EXCHANGE ACT OF 1934

CIRCLE INTERNET FINANCIAL, LTD.

ITEM 1. BUSINESS

We are a global financial technology firm that enables businesses of all sizes to harness the power of digital currencies and public blockchains for payments, commerce and financial applications worldwide. Circle is the principal operator of USD Coin (USDC), which has become the fastest growing, regulated and fully reserved dollar digital currency.

ITEM 1A. RISK FACTORS

The regulatory environment for digital assets is uncertain and evolving.

ITEM 8. FINANCIAL STATEMENTS

For the year ended December 31, 2023:
- Total Revenue: $2.8 billion (page 47)
- Net Income: $850 million (page 48)
- Total Assets: $4.2 billion (page 49)""",
            'metadata': {
                'source': 'CRCL_10K_2023.html',
                'filing_date': '2024-03-15',
                'cik': '0001876042'
            }
        }
    ]
    
    queries_and_expected = [
        ("What is Circle's main product?", "USDC"),
        ("What was the total revenue?", "$2.8 billion"),
        ("What page is the revenue on?", "47")
    ]
    
    success_count = 0
    
    for query, expected in queries_and_expected:
        print(f"\nQuery: {query}")
        print(f"Expected to find: {expected}")
        
        try:
            response, confidence = ai.get_ai_response(query, mock_context)
            
            print(f"Response: {str(response)[:200]}...")
            print(f"Confidence: {confidence}")
            
            if expected.lower() in str(response).lower():
                print("✅ Found expected content!")
                success_count += 1
            else:
                print("⚠️  Expected content not found")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return success_count >= 2  # At least 2 out of 3 should work

if __name__ == "__main__":
    # Test both approaches
    result1 = test_with_mock_context()
    result2 = test_with_real_document()
    
    if result1 or result2:
        print("\n✅ AI SERVICE IS WORKING CORRECTLY!")
    else:
        print("\n❌ AI SERVICE STILL HAS ISSUES")
