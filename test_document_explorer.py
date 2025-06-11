#!/usr/bin/env python3
"""
Test the Document Explorer with integrated viewer
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from components.document_explorer import render_document_explorer

def test_document_explorer():
    st.set_page_config(page_title="Document Explorer Test", layout="wide")
    
    st.title("🧪 Document Explorer Integration Test")
    
    # Check prerequisites
    data_dir = Path("data/sec_documents")
    
    if not data_dir.exists() or not any(data_dir.iterdir()):
        st.error("❌ No documents found!")
        st.info("Please download some companies first using the admin panel")
        
        # Quick download option
        if st.button("Download Test Company (AAPL)"):
            from scrapers.sec.sec_compliant_scraper import SECCompliantScraper
            import asyncio
            
            async def download_test():
                scraper = SECCompliantScraper()
                return await scraper.scan_and_download_everything("AAPL", "0000320193")
            
            with st.spinner("Downloading Apple documents..."):
                result = asyncio.run(download_test())
                if result['success']:
                    st.success(f"✅ Downloaded {result['total_files']} files!")
                    st.rerun()
                else:
                    st.error(f"Failed: {result.get('error')}")
        return
    
    # Test checklist
    st.sidebar.markdown("### 🧪 Test Checklist")
    
    tests = {
        "Companies listed": False,
        "Documents grouped by type": False,
        "Document clickable": False,
        "Viewer displays content": False,
        "Search works": False,
        "Download button works": False
    }
    
    for test, status in tests.items():
        if status:
            st.sidebar.success(f"✅ {test}")
        else:
            st.sidebar.info(f"⏳ {test}")
    
    st.sidebar.markdown("### 📝 Instructions")
    st.sidebar.markdown("""
    1. Select a company from dropdown
    2. Click on a document
    3. Verify it displays in viewer
    4. Test search functionality
    5. Test download button
    """)
    
    # Render the explorer
    try:
        render_document_explorer()
        
        # Add test status updater
        if st.session_state.get('selected_document'):
            st.sidebar.success("✅ Document selected and displayed!")
        
    except Exception as e:
        st.error(f"❌ Error in explorer: {e}")
        st.exception(e)

if __name__ == "__main__":
    test_document_explorer()