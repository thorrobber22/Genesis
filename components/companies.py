"""
Companies View - File Explorer Interface
Date: 2025-06-13 23:35:00 UTC
Following the exact design from master reference
"""
import streamlit as st
from services.data_service import data_service
import time

def render_companies():
    """Render file explorer interface for companies"""
    
    # Add custom CSS for file explorer
    st.markdown("""
    <style>
    .file-explorer {
        background-color: #202123;
        border-radius: 8px;
        padding: 20px;
        font-family: monospace;
    }
    
    .folder {
        cursor: pointer;
        padding: 8px;
        border-radius: 4px;
        transition: background-color 0.2s ease;
    }
    
    .folder:hover {
        background-color: #2A2B2D;
    }
    
    .file {
        cursor: pointer;
        padding: 8px 8px 8px 32px;
        border-radius: 4px;
        transition: all 0.2s ease;
    }
    
    .file:hover {
        background-color: #2A2B2D;
        transform: translateX(4px);
    }
    
    .expanded {
        animation: expand 0.3s ease-out;
    }
    
    @keyframes expand {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("### 📁 Companies")
    
    # Search bar
    search = st.text_input("Search companies...", key="company_search", 
                          placeholder="Type company name or ticker...")
    
    # Get company tree
    company_tree = data_service.get_companies_tree()
    
    # Initialize expanded state
    if "expanded_folders" not in st.session_state:
        st.session_state.expanded_folders = set()
    
    # Render file explorer
    st.markdown('<div class="file-explorer">', unsafe_allow_html=True)
    
    for sector, companies in company_tree.items():
        if not companies:
            continue
            
        # Sector folder
        col1, col2 = st.columns([10, 1])
        with col1:
            folder_icon = "📂" if sector in st.session_state.expanded_folders else "📁"
            if st.button(f"{folder_icon} {sector} ({len(companies)})", 
                        key=f"folder_{sector}",
                        use_container_width=True):
                if sector in st.session_state.expanded_folders:
                    st.session_state.expanded_folders.remove(sector)
                else:
                    st.session_state.expanded_folders.add(sector)
                st.rerun()
        
        # Show companies if expanded
        if sector in st.session_state.expanded_folders:
            for company in companies:
                # Apply search filter
                if search and search.lower() not in company['name'].lower()                    and search.lower() not in company['ticker'].lower():
                    continue
                
                col1, col2, col3 = st.columns([8, 1, 1])
                with col1:
                    display_name = f"📄 {company['name']} ({company['ticker']})"
                    info_text = f"{company['documents']} documents · Last: {company['last_update']}"
                    
                    if st.button(f"{display_name} - {info_text}", 
                               key=f"company_{company['ticker']}",
                               use_container_width=True):
                        st.session_state.selected_company = company['ticker']
                        st.session_state.show_documents = True
                        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show documents for selected company
    if st.session_state.get('show_documents') and st.session_state.get('selected_company'):
        show_company_documents(st.session_state.selected_company)

def show_company_documents(ticker: str):
    """Show documents for a specific company"""
    st.markdown("---")
    st.markdown(f"### 📁 {ticker} Documents")
    
    # Back button
    if st.button("← Back to Companies", key="back_to_companies"):
        st.session_state.show_documents = False
        st.rerun()
    
    # Get documents
    documents = data_service.get_company_documents(ticker)
    
    # Last sync info
    st.caption(f"Last sync: 2 min ago 🔄")
    
    # Document list
    for doc in documents:
        col1, col2, col3 = st.columns([6, 2, 2])
        
        with col1:
            st.markdown(f"**📄 {doc['name']}**")
        
        with col2:
            st.caption(doc['date'])
        
        with col3:
            # View button
            if st.button("View", key=f"view_{doc['name']}", 
                        use_container_width=True):
                # Set document viewing mode
                st.session_state.document_mode = True
                st.session_state.current_document = doc
                st.session_state.current_ticker = ticker
                st.rerun()
            
            # SEC link
            sec_url = data_service.get_sec_url(ticker, doc['type'])
            st.markdown(f"[SEC ↗]({sec_url})")
