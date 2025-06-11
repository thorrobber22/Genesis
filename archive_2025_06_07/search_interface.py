"""
Search interface for Hedge Intel admin
Date: 2025-06-05 14:36:06 UTC
Author: thorrobber22
"""

import streamlit as st
from core.vector_store import VectorStore, search_ipo_info

def show_search_interface():
    """Show vector search interface"""
    st.header("🔍 Search IPO Documents")
    
    # Initialize vector store
    try:
        vs = VectorStore()
        stats = vs.get_collection_stats()
        
        # Show stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Chunks", stats["total_chunks"])
        with col2:
            st.metric("Companies", len(stats["tickers"]))
        with col3:
            st.metric("Document Types", len(stats["document_types"]))
        
        # Search interface
        st.subheader("Semantic Search")
        
        query = st.text_input("Enter your search query:", 
                             placeholder="e.g., What is the lock-up period?")
        
        # Optional filters
        with st.expander("Search Filters"):
            ticker_filter = st.selectbox(
                "Filter by company:",
                ["All"] + stats["tickers"]
            )
            
            doc_type_filter = st.multiselect(
                "Document types:",
                stats["document_types"],
                default=stats["document_types"]
            )
        
        if st.button("Search", type="primary") and query:
            # Perform search
            ticker = None if ticker_filter == "All" else ticker_filter
            
            with st.spinner("Searching..."):
                results = vs.search(
                    query, 
                    ticker=ticker,
                    doc_types=doc_type_filter if doc_type_filter else None,
                    n_results=10
                )
            
            # Display results
            if results:
                st.success(f"Found {len(results)} results")
                
                for i, result in enumerate(results):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{i+1}. {result.ticker} - {result.document_type}**")
                        with col2:
                            st.caption(f"Score: {result.score:.3f}")
                        
                        # Show text excerpt
                        st.text_area(
                            "Excerpt:",
                            result.text[:500] + "..." if len(result.text) > 500 else result.text,
                            height=100,
                            key=f"result_{i}"
                        )
                        
                        # Show metadata
                        with st.expander("Details"):
                            st.json(result.metadata)
                        
                        st.divider()
            else:
                st.warning("No results found")
        
        # Company comparison
        st.subheader("Compare Companies")
        
        if len(stats["tickers"]) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                company1 = st.selectbox("Company 1:", stats["tickers"], key="comp1")
            with col2:
                company2 = st.selectbox("Company 2:", stats["tickers"], key="comp2")
            
            aspect = st.selectbox(
                "Compare aspect:",
                ["business", "risks", "financials", "management", "competitive"]
            )
            
            if st.button("Compare"):
                comparison = vs.semantic_comparison(company1, company2, aspect)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"### {company1}")
                    if comparison[company1]["found"]:
                        for res in comparison[company1]["top_results"]:
                            st.caption(f"Source: {res['source']} (score: {res['score']:.3f})")
                            st.text_area("", res["text"], height=200, key=f"{company1}_{res['source']}")
                    else:
                        st.info("No data found")
                
                with col2:
                    st.markdown(f"### {company2}")
                    if comparison[company2]["found"]:
                        for res in comparison[company2]["top_results"]:
                            st.caption(f"Source: {res['source']} (score: {res['score']:.3f})")
                            st.text_area("", res["text"], height=200, key=f"{company2}_{res['source']}")
                    else:
                        st.info("No data found")
        else:
            st.info("Need at least 2 companies indexed to use comparison")
            
    except ValueError as e:
        st.error(f"Vector store error: {e}")
        st.info("Make sure OPENAI_API_KEY is set in your .env file")

if __name__ == "__main__":
    # Test standalone
    st.set_page_config(page_title="Search Test", page_icon="🔍")
    show_search_interface()
