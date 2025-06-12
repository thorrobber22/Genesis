"""
Streamlit UI for Hedge Fund Intelligence System
"""

import streamlit as st
from services.ai_chat import AIChat
from services.document_indexer import DocumentIndexer
import pandas as pd
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Hedge Fund Intelligence",
    page_icon="📈",
    layout="wide"
)

# Initialize services
@st.cache_resource
def init_services():
    return AIChat(), DocumentIndexer()

ai_chat, doc_indexer = init_services()

# Title
st.title("📈 Hedge Fund Intelligence System")
st.markdown("AI-powered analysis of SEC filings")

# Sidebar
with st.sidebar:
    st.header("System Info")
    doc_count = doc_indexer.collection.count()
    st.metric("Documents Indexed", doc_count)
    
    st.header("Companies")
    companies = ["AAPL", "TSLA", "MSFT", "NVDA", "AMZN", "CRCL"]
    selected_company = st.selectbox("Filter by company:", ["All"] + companies)
    
    st.header("Quick Searches")
    if st.button("Latest 10-Q filings"):
        st.session_state.search_query = "10-Q"
    if st.button("Risk factors"):
        st.session_state.search_query = "risk factors"
    if st.button("Revenue analysis"):
        st.session_state.search_query = "revenue growth"

# Main content
tab1, tab2, tab3 = st.tabs(["💬 Chat", "🔍 Search", "📊 Analysis"])

with tab1:
    st.header("Chat with AI")
    
    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "sources" in message:
                with st.expander("Sources"):
                    for source in message["sources"]:
                        st.write(f"- {source['company']}: {source['document'].split('/')[-1]}")
    
    # Chat input
    if prompt := st.chat_input("Ask about SEC filings..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                # Search for relevant documents
                if selected_company != "All":
                    search_query = f"{selected_company} {prompt}"
                else:
                    search_query = prompt
                    
                search_results = doc_indexer.search(search_query, limit=5)
                
                # Prepare context
                context = ""
                sources = []
                
                if search_results:
                    for result in search_results:
                        context += f"\n\nFrom {result['company']} {result['document']}:\n{result['text']}"
                        sources.append({
                            'company': result['company'],
                            'document': result['document'],
                            'score': result.get('score', 0)
                        })
                
                # Get AI response
                response = ai_chat.get_response(prompt, context)
                st.write(response)
                
                # Show sources
                if sources:
                    with st.expander("Sources"):
                        for source in sources:
                            st.write(f"- {source['company']}: {source['document'].split('/')[-1]} (Score: {source['score']:.2f})")
                
                # Add to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "sources": sources
                })

with tab2:
    st.header("Document Search")
    
    # Search input
    search_query = st.text_input("Search query:", value=st.session_state.get("search_query", ""))
    col1, col2 = st.columns([3, 1])
    with col1:
        limit = st.slider("Number of results:", 1, 20, 10)
    with col2:
        search_button = st.button("Search", type="primary")
    
    if search_button and search_query:
        with st.spinner("Searching..."):
            results = doc_indexer.search(search_query, limit=limit)
            
            if results:
                st.success(f"Found {len(results)} results")
                
                # Display results
                for i, result in enumerate(results):
                    with st.expander(f"{result['company']} - {result['document'].split('/')[-1]} (Score: {result.get('score', 0):.2f})"):
                        st.write(result['text'][:1000] + "...")
                        st.caption(f"Document: {result['document']}")
            else:
                st.warning("No results found")

with tab3:
    st.header("Company Analysis")
    
    # Company selector
    company = st.selectbox("Select company:", companies)
    
    if st.button("Analyze", type="primary"):
        with st.spinner(f"Analyzing {company}..."):
            # Get company documents
            company_docs = doc_indexer.search(company, limit=10)
            
            if company_docs:
                st.subheader(f"{company} Document Summary")
                
                # Document types
                doc_types = {}
                for doc in company_docs:
                    doc_name = doc['document'].split('/')[-1]
                    if '10-Q' in doc_name:
                        doc_types['10-Q'] = doc_types.get('10-Q', 0) + 1
                    elif '10-K' in doc_name:
                        doc_types['10-K'] = doc_types.get('10-K', 0) + 1
                    elif '8-K' in doc_name:
                        doc_types['8-K'] = doc_types.get('8-K', 0) + 1
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("10-Q Reports", doc_types.get('10-Q', 0))
                with col2:
                    st.metric("10-K Reports", doc_types.get('10-K', 0))
                with col3:
                    st.metric("8-K Reports", doc_types.get('8-K', 0))
                
                # AI Analysis
                st.subheader("AI Analysis")
                analysis_prompt = f"Provide a brief analysis of {company} based on their recent SEC filings. Focus on key financial metrics and risk factors."
                
                # Prepare context from company docs
                context = ""
                for doc in company_docs[:5]:
                    context += f"\n\nFrom {doc['document']}:\n{doc['text'][:500]}"
                
                analysis = ai_chat.get_response(analysis_prompt, context)
                st.write(analysis)
                
                # Document list
                st.subheader("Available Documents")
                for doc in company_docs:
                    st.write(f"- {doc['document'].split('/')[-1]}")
            else:
                st.error(f"No documents found for {company}")

# Footer
st.markdown("---")
st.caption("Hedge Fund Intelligence System - Powered by AI and SEC EDGAR data")
