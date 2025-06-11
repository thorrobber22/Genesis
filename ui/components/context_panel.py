"""
Context Panel Component
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

class ContextPanel:
    def render(self, ticker=None):
        """Render context panel"""
        st.markdown("### CONTEXT")
        
        if not ticker:
            st.info("Ask about a specific ticker to see details")
            return
        
        st.caption(f"Current Topic: {ticker}")
        
        # Quick facts
        facts = self._get_quick_facts(ticker)
        if facts:
            st.markdown("#### QUICK FACTS")
            for key, value in facts.items():
                st.markdown(f"• **{key}:** {value}")
        
        # Documents
        docs = self._get_documents(ticker)
        if docs:
            st.markdown(f"#### DOCUMENTS ({len(docs)})")
            for doc in docs:
                with st.expander(f"{doc['type']} - {doc['size']}"):
                    upload_time = datetime.fromtimestamp(doc['time']).strftime("%Y-%m-%d %H:%M")
                    st.caption(f"Uploaded: {upload_time}")
                    if st.button("View", key=f"view_{doc['id']}"):
                        self._view_document(doc['path'])
        
        # Actions
        st.markdown("#### ACTIONS")
        col1, col2 = st.columns(2)
        with col1:
            st.button("📄 View S-1", key=f"s1_{ticker}")
        with col2:
            st.button("📊 Analysis", key=f"analysis_{ticker}")
        
        # Related questions
        st.markdown("#### RELATED QUESTIONS")
        questions = [
            f"What are {ticker}'s main risks?",
            f"Show me {ticker}'s financials",
            f"When does {ticker}'s lock-up expire?"
        ]
        for q in questions:
            if st.button(f'"{q}"', key=f"q_{q}"):
                st.session_state.pending_question = q
                st.rerun()
    
    def _get_quick_facts(self, ticker):
        """Get quick facts for ticker"""
        # Load from processed data
        processed_file = Path(f"data/processed/{ticker}_s1.json")
        if processed_file.exists():
            with open(processed_file) as f:
                data = json.load(f)
            
            return {
                "Price Range": data.get("price_range", "TBD"),
                "Shares": data.get("shares_offered", "TBD"),
                "Lock-up": data.get("lockup_period", "180 days"),
                "IPO Date": data.get("expected_date", "TBD")
            }
        return None
    
    def _get_documents(self, ticker):
        """Get uploaded documents for ticker"""
        docs = []
        doc_dir = Path("data/documents")
        
        if doc_dir.exists():
            for file in doc_dir.glob(f"{ticker}_*"):
                docs.append({
                    "id": file.stem,
                    "type": self._detect_doc_type(file.name),
                    "size": f"{file.stat().st_size / 1_048_576:.1f}MB",
                    "time": file.stat().st_mtime,
                    "path": str(file)
                })
        
        return sorted(docs, key=lambda x: x["time"], reverse=True)
    
    def _detect_doc_type(self, filename):
        """Detect document type from filename"""
        if "s1" in filename.lower() or "s-1" in filename.lower():
            return "S-1 Filing"
        elif "424b" in filename.lower():
            return "Final Prospectus"
        elif "exhibit" in filename.lower():
            return "Exhibit"
        else:
            return "Document"
    
    def _view_document(self, path):
        """Open document viewer"""
        st.info(f"Opening {path}...")
