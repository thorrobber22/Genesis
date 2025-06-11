#!/usr/bin/env python3
"""
Full integration test - Admin → Explorer → Viewer
"""

import streamlit as st
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).parent))

def test_full_integration():
    st.set_page_config(page_title="Full Integration Test", layout="wide")
    
    st.title("🧪 Full Integration Test")
    
    # Test status tracker
    test_results = {}
    
    st.markdown("### 1️⃣ Data Pipeline Test")
    
    # Check IPO data
    ipo_file = Path("data/ipo_data/ipo_calendar_latest.json")
    if ipo_file.exists():
        with open(ipo_file, 'r') as f:
            ipo_data = json.load(f)
        
        total_ipos = sum(len(ipo_data.get(k, [])) for k in ['recently_priced', 'upcoming', 'filed'])
        st.success(f"✅ IPO Data: {total_ipos} companies found")
        test_results['ipo_scraper'] = True
    else:
        st.error("❌ No IPO data found")
        test_results['ipo_scraper'] = False
    
    # Check company requests
    requests_file = Path("data/company_requests.json")
    if requests_file.exists():
        with open(requests_file, 'r') as f:
            requests = json.load(f)
        st.success(f"✅ Company Requests: {len(requests)} total")
        test_results['requests'] = True
    else:
        st.error("❌ No company requests found")
        test_results['requests'] = False
    
    st.markdown("### 2️⃣ Document Storage Test")
    
    # Check SEC documents
    sec_dir = Path("data/sec_documents")
    if sec_dir.exists():
        companies = [d for d in sec_dir.iterdir() if d.is_dir()]
        total_docs = sum(len(list(c.glob("*.html"))) for c in companies)
        st.success(f"✅ SEC Documents: {len(companies)} companies, {total_docs} documents")
        test_results['sec_documents'] = True
    else:
        st.error("❌ No SEC documents found")
        test_results['sec_documents'] = False
    
    st.markdown("### 3️⃣ Component Test")
    
    # Test imports
    try:
        from components.document_viewer import DocumentViewer
        from components.document_explorer import render_document_explorer
        st.success("✅ Components imported successfully")
        test_results['components'] = True
    except ImportError as e:
        st.error(f"❌ Component import failed: {e}")
        test_results['components'] = False
    
    st.markdown("### 4️⃣ Feature Test")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Test Document Viewer", use_container_width=True):
            st.switch_page("test_document_viewer.py")
    
    with col2:
        if st.button("Test Explorer", use_container_width=True):
            st.switch_page("test_document_explorer.py")
    
    with col3:
        if st.button("Test Admin Panel", use_container_width=True):
            st.switch_page("admin/admin_panel.py")
    
    # Summary
    st.markdown("### 📊 Test Summary")
    
    passed = sum(1 for v in test_results.values() if v)
    total = len(test_results)
    
    if passed == total:
        st.balloons()
        st.success(f"🎉 All tests passed! ({passed}/{total})")
    else:
        st.warning(f"⚠️ {passed}/{total} tests passed")
    
    # Detailed results
    with st.expander("Detailed Results"):
        for test, result in test_results.items():
            if result:
                st.success(f"✅ {test}")
            else:
                st.error(f"❌ {test}")

if __name__ == "__main__":
    test_full_integration()