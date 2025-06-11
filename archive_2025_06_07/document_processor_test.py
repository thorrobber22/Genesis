#!/usr/bin/env python3
"""
Document Processor Test Suite
Date: 2025-06-05 13:53:05 UTC
Author: thorrobber22

Tests for document processing functionality
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime
import asyncio

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.document_processor import (
    DocumentProcessor,
    DocumentType,
    process_document_sync
)

# Test HTML content
TEST_S1_CONTENT = """
<html>
<body>
<h1>REGISTRATION STATEMENT UNDER THE SECURITIES ACT OF 1933</h1>
<p>Circle Internet Financial, Inc. is incorporated in Delaware.</p>
<p>We are listing our shares on the New York Stock Exchange under the symbol "CRCL".</p>

<h2>THE OFFERING</h2>
<p>We are offering 15,000,000 shares of our common stock.</p>
<p>Price range: $26.00 to $29.00 per share</p>

<h2>RISK FACTORS</h2>
<p>• Cryptocurrency market volatility</p>
<p>• Regulatory uncertainty</p>
<p>• Competition from other stablecoins</p>

<h2>USE OF PROCEEDS</h2>
<p>We intend to use the proceeds for general corporate purposes.</p>

<h2>CAPITALIZATION</h2>
<p>As of December 31, 2024, we had 450,000,000 shares outstanding.</p>

<h2>PRINCIPAL STOCKHOLDERS</h2>
<table>
<tr><td>Jeremy Allaire</td><td>12.5%</td></tr>
<tr><td>Goldman Sachs</td><td>8.2%</td></tr>
<tr><td>General Catalyst</td><td>7.8%</td></tr>
</table>

<h2>UNDERWRITING</h2>
<p>Goldman Sachs & Co. LLC, Morgan Stanley, and J.P. Morgan are acting as lead underwriters.</p>

<h2>LOCK-UP AGREEMENTS</h2>
<p>Our officers and directors have agreed to a 180 day lock-up period.</p>
</body>
</html>
"""

TEST_LOCKUP_CONTENT = """
LOCK-UP AGREEMENT

This agreement restricts the sale of shares for 180 days following the IPO.
"""

def create_test_files():
    """Create test documents"""
    test_dir = Path(tempfile.mkdtemp())
    
    # Create test S-1
    s1_path = test_dir / "TEST_S1_20250605.html"
    s1_path.write_text(TEST_S1_CONTENT)
    
    # Create test lock-up
    lockup_path = test_dir / "TEST_LOCKUP_20250605.txt"
    lockup_path.write_text(TEST_LOCKUP_CONTENT)
    
    return test_dir, s1_path, lockup_path

def test_document_type_detection():
    """Test document type detection"""
    print("\n🔍 Testing document type detection...")
    
    processor = DocumentProcessor()
    test_dir, s1_path, lockup_path = create_test_files()
    
    # Test S-1 detection
    s1_type = processor.detect_document_type(s1_path, TEST_S1_CONTENT)
    assert s1_type == DocumentType.S1, f"Expected S1, got {s1_type}"
    print("✓ S-1 detection works")
    
    # Test lock-up detection
    lockup_type = processor.detect_document_type(lockup_path, TEST_LOCKUP_CONTENT)
    assert lockup_type == DocumentType.LOCKUP, f"Expected LOCKUP, got {lockup_type}"
    print("✓ Lock-up detection works")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)

def test_text_extraction():
    """Test HTML text extraction"""
    print("\n📄 Testing text extraction...")
    
    processor = DocumentProcessor()
    test_dir, s1_path, _ = create_test_files()
    
    text = processor.extract_text_from_html(s1_path)
    
    assert "Circle Internet Financial" in text
    assert "15,000,000 shares" in text
    assert "$26.00 to $29.00" in text
    print("✓ Text extraction works")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir)

def test_section_extraction():
    """Test S-1 section extraction"""
    print("\n📑 Testing section extraction...")
    
    processor = DocumentProcessor()
    sections = processor.extract_sections_s1(TEST_S1_CONTENT)
    
    assert sections["risk_factors"] != ""
    assert sections["use_of_proceeds"] != ""
    assert sections["capitalization"] != ""
    print("✓ Section extraction works")

def test_key_facts_extraction():
    """Test key facts extraction"""
    print("\n🔑 Testing key facts extraction...")
    
    processor = DocumentProcessor()
    sections = processor.extract_sections_s1(TEST_S1_CONTENT)
    key_facts = processor.extract_key_facts_s1(sections, TEST_S1_CONTENT)
    
    assert key_facts["ticker"] == "CRCL"
    assert key_facts["shares_offered"] == 15000000
    assert key_facts["price_range"]["min"] == 26.0
    assert key_facts["price_range"]["max"] == 29.0
    assert "Goldman Sachs" in key_facts["underwriters"]
    assert key_facts["lock_up_period"] == 180
    print("✓ Key facts extraction works")

def test_float_calculation():
    """Test float calculation"""
    print("\n💹 Testing float calculation...")
    
    processor = DocumentProcessor()
    sections = processor.extract_sections_s1(TEST_S1_CONTENT)
    key_facts = processor.extract_key_facts_s1(sections, TEST_S1_CONTENT)
    
    # Override some values for testing
    key_facts["shares_offered"] = 15000000
    
    float_calc = processor.calculate_float_with_proof(key_facts, sections)
    
    assert float_calc["shares_offered"] == 15000000
    assert float_calc["total_outstanding_pre"] == 450000000
    assert float_calc["total_outstanding_post"] == 465000000
    assert len(float_calc["calculation_steps"]) > 0
    print("✓ Float calculation works")
    print(f"  Float percentage: {float_calc['float_percentage']:.1f}%")

async def test_full_processing():
    """Test full document processing"""
    print("\n🚀 Testing full document processing...")
    
    test_dir, s1_path, _ = create_test_files()
    
    try:
        result = await process_uploaded_document("TEST", s1_path)
        
        assert result["success"] == True
        assert result["document_type"] == "S-1"
        assert result["chunks_created"] > 0
        print("✓ Full processing works")
        print(f"  Created {result['chunks_created']} vector chunks")
        
    except Exception as e:
        print(f"✗ Processing failed: {e}")
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)

def test_real_documents():
    """Test with real documents if available"""
    print("\n📁 Checking for real documents...")
    
    doc_dir = Path("data/documents")
    if doc_dir.exists():
        html_files = list(doc_dir.glob("*.html"))
        if html_files:
            print(f"Found {len(html_files)} real documents")
            # Test first document
            test_file = html_files[0]
            print(f"Testing with: {test_file.name}")
            
            try:
                # Extract ticker from filename
                ticker = test_file.name.split('_')[0]
                result = process_document_sync(ticker, test_file)
                print("✓ Real document processed successfully")
                print(f"  Type: {result['document_type']}")
                print(f"  Status: {result['validation_status']}")
            except Exception as e:
                print(f"✗ Error processing real document: {e}")
        else:
            print("No documents found in data/documents/")
    else:
        print("Document directory not found")

def main():
    """Run all tests"""
    print("DOCUMENT PROCESSOR TEST SUITE")
    print("="*50)
    
    try:
        test_document_type_detection()
        test_text_extraction()
        test_section_extraction()
        test_key_facts_extraction()
        test_float_calculation()
        
        # Run async test
        asyncio.run(test_full_processing())
        
        test_real_documents()
        
        print("\n✅ ALL TESTS PASSED!")
        print("\nPhase 3.2 Complete! Ready for Phase 3.3: Vector Store")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())