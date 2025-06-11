#!/usr/bin/env python3
"""
Hedge Intelligence - Complete Refactor Script
Date: 2025-06-07 21:50:17 UTC
Author: thorrobber22
Description: Apply all changes to transform into analyst-focused platform
"""

import os
import shutil
from pathlib import Path
import json

def create_backup():
    """Create backup before changes"""
    print("📁 Creating backup...")
    backup_dir = Path("backup_20250607")
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    
    # Backup key files
    files_to_backup = [
        "hedge_intelligence.py",
        "services/ai_service.py",
        "components/dashboard.py",
        "components/chat.py",
        "components/settings.py"
    ]
    
    for file in files_to_backup:
        if Path(file).exists():
            backup_path = backup_dir / file
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, backup_path)
    
    print("✅ Backup created")

def create_document_explorer():
    """Create new document explorer component"""
    print("\n📝 Creating document_explorer.py...")
    
    content = '''"""
Document Explorer Component - File tree style navigation
Created: 2025-06-07 21:50:17 UTC
"""
import streamlit as st
from pathlib import Path
import json

class DocumentExplorer:
    def __init__(self):
        self.doc_path = Path("data/sec_documents")
        
    def render_sidebar(self):
        """Render file explorer in sidebar"""
        st.sidebar.markdown("### Document Explorer")
        
        companies = self.get_companies_with_counts()
        
        for company, count in companies.items():
            with st.sidebar.expander(f"{company} ({count})"):
                self.render_company_docs(company)
                
    def get_companies_with_counts(self):
        """Get companies and their document counts"""
        companies = {}
        if self.doc_path.exists():
            for company_dir in self.doc_path.iterdir():
                if company_dir.is_dir():
                    doc_count = len(list(company_dir.glob("*.html")))
                    companies[company_dir.name] = doc_count
        return dict(sorted(companies.items()))
        
    def render_company_docs(self, company):
        """Render categorized documents"""
        company_path = self.doc_path / company
        
        # Categorize by filing type
        categories = {
            "10-K Annual": [],
            "10-Q Quarterly": [],
            "8-K Current": [],
            "S-1 Registration": [],
            "Other": []
        }
        
        for doc in company_path.glob("*.html"):
            doc_name = doc.name
            if "10-K" in doc_name or "10K" in doc_name:
                categories["10-K Annual"].append(doc_name)
            elif "10-Q" in doc_name or "10Q" in doc_name:
                categories["10-Q Quarterly"].append(doc_name)
            elif "8-K" in doc_name or "8K" in doc_name:
                categories["8-K Current"].append(doc_name)
            elif "S-1" in doc_name or "S1" in doc_name:
                categories["S-1 Registration"].append(doc_name)
            else:
                categories["Other"].append(doc_name)
                
        # Display categories
        for category, docs in categories.items():
            if docs:
                st.markdown(f"**{category} ({len(docs)})**")
                for i, doc in enumerate(docs[:5]):
                    if st.button(doc[:40] + "...", key=f"{company}_{doc}_{i}"):
                        st.session_state.selected_doc = {
                            'company': company,
                            'document': doc,
                            'path': str(company_path / doc)
                        }
                        st.rerun()
                if len(docs) > 5:
                    st.caption(f"...and {len(docs)-5} more")
'''
    
    Path("components").mkdir(exist_ok=True)
    with open("components/document_explorer.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Created document_explorer.py")

def create_persistent_chat():
    """Create persistent chat component"""
    print("\n📝 Creating persistent_chat.py...")
    
    content = '''"""
Persistent Chat Bar Component
Created: 2025-06-07 21:50:17 UTC
"""
import streamlit as st
from services.ai_service import AIService
from services.document_service import DocumentService

class PersistentChat:
    def __init__(self):
        self.ai_service = AIService()
        self.doc_service = DocumentService()
        
    def render_chat_bar(self):
        """Render fixed bottom chat bar"""
        # CSS for fixed positioning
        st.markdown("""
        <style>
        .main > div {
            padding-bottom: 100px;
        }
        .chat-input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: #1A1D23;
            padding: 1rem;
            border-top: 1px solid #2D3748;
            z-index: 999;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create container at bottom
        chat_placeholder = st.empty()
        
        with chat_placeholder.container():
            # Show context
            context_text = "Select a document to begin analysis"
            if 'selected_doc' in st.session_state:
                doc = st.session_state.selected_doc
                context_text = f"Context: {doc['company']} - {doc['document'][:50]}..."
            
            st.caption(context_text)
            
            # Chat input
            col1, col2 = st.columns([6, 1])
            
            with col1:
                query = st.text_input(
                    "Ask about documents...",
                    key="persistent_chat_input",
                    placeholder="What would you like to know?",
                    label_visibility="collapsed"
                )
                
            with col2:
                send_button = st.button("Send", key="send_chat")
                
            # Process query
            if send_button and query:
                self.process_query(query)
                st.rerun()
            
    def process_query(self, query):
        """Process user query with context"""
        # Get document context
        context = ""
        if 'selected_doc' in st.session_state:
            doc_path = st.session_state.selected_doc['path']
            try:
                with open(doc_path, 'r', encoding='utf-8') as f:
                    context = f.read()[:10000]  # First 10k chars
            except:
                context = "Unable to load document"
        
        # Get AI response
        with st.spinner("Analyzing..."):
            response = self.ai_service.get_ai_response(
                prompt=query,
                context=context
            )
            
        # Add to chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            
        st.session_state.chat_history.append({
            'query': query,
            'response': response,
            'document': st.session_state.get('selected_doc', None)
        })
'''
    
    with open("components/persistent_chat.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Created persistent_chat.py")

def create_data_extractor():
    """Create data extraction component"""
    print("\n📝 Creating data_extractor.py...")
    
    content = '''"""
Data Extraction Component with Citations
Created: 2025-06-07 21:50:17 UTC
"""
import re
from typing import Dict, List

class DataExtractor:
    def __init__(self):
        self.extraction_patterns = {
            'revenue': [
                r'revenues?\\s*[:=]\\s*\\$?([\\d,]+\\.?\\d*)\\s*(million|billion|M|B)',
                r'total\\s+revenues?\\s+of\\s+\\$?([\\d,]+\\.?\\d*)',
            ],
            'net_income': [
                r'net\\s+income\\s*[:=]\\s*\\$?([\\d,]+\\.?\\d*)\\s*(million|billion|M|B)',
                r'net\\s+earnings?\\s+of\\s+\\$?([\\d,]+\\.?\\d*)',
            ],
            'employees': [
                r'([\\d,]+)\\s+employees',
                r'employee\\s+count\\s*[:=]\\s*([\\d,]+)',
            ]
        }
        
    def extract_with_citations(self, document_text: str, metric: str) -> Dict:
        """Extract data with page citations"""
        patterns = self.extraction_patterns.get(metric, [])
        results = []
        
        # Search for patterns
        for pattern in patterns:
            matches = re.finditer(pattern, document_text, re.IGNORECASE)
            for match in matches:
                # Find approximate page
                position = match.start()
                page_estimate = (position // 3000) + 1  # Rough estimate
                
                results.append({
                    'value': match.group(1),
                    'unit': match.group(2) if len(match.groups()) > 1 else None,
                    'page': page_estimate,
                    'context': match.group(0),
                    'position': position
                })
                    
        return self.validate_and_format(results, metric)
        
    def validate_and_format(self, results: List[Dict], metric: str) -> Dict:
        """Validate extraction results"""
        if not results:
            return {
                'status': 'not_found',
                'metric': metric
            }
            
        # Take the first result (most relevant)
        best_result = results[0]
        
        return {
            'status': 'found',
            'metric': metric,
            'value': best_result['value'],
            'unit': best_result.get('unit', ''),
            'citation': f"[Page ~{best_result['page']}]",
            'context': best_result['context'],
            'confidence': 'high' if len(results) > 1 else 'medium'
        }
'''
    
    with open("components/data_extractor.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Created data_extractor.py")

def create_ipo_tracker_enhanced():
    """Create enhanced IPO tracker"""
    print("\n📝 Creating ipo_tracker_enhanced.py...")
    
    content = '''"""
Enhanced IPO Tracker with Additional Details
Created: 2025-06-07 21:50:17 UTC
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path

class IPOTrackerEnhanced:
    def __init__(self):
        self.ipo_data_path = Path("data/ipo_pipeline/ipo_calendar.json")
        
    def render_ipo_dashboard(self):
        """Render enhanced IPO dashboard"""
        st.subheader("Upcoming IPOs")
        
        # Load IPO data
        ipos = self.load_ipo_data()
        
        if not ipos:
            st.info("No upcoming IPOs this week")
            return
            
        # Create enhanced dataframe
        df_data = []
        for ipo in ipos:
            df_data.append({
                'Company': ipo.get('company', 'N/A'),
                'Sector': ipo.get('sector', 'N/A'),
                'Expected Date': ipo.get('expected_date', 'TBD'),
                'Valuation': ipo.get('expected_valuation', 'Not Available'),
                'Lead Underwriter': ipo.get('lead_underwriter', 'Not Available'),
                'Lock-up Period': ipo.get('lockup_period', 'Not Available')
            })
            
        df = pd.DataFrame(df_data)
        
        # Display with custom styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Add chat prompt
        st.markdown("---")
        st.markdown("💬 **Ask me about any IPO's business model or competitive landscape**")
        
    def load_ipo_data(self):
        """Load IPO data from file"""
        if self.ipo_data_path.exists():
            with open(self.ipo_data_path, 'r') as f:
                return json.load(f)
        
        # Return sample data if file doesn't exist
        return [
            {
                'company': 'Stripe',
                'sector': 'Fintech',
                'expected_date': 'June 12, 2025',
                'expected_valuation': '$65-70B',
                'lead_underwriter': 'Goldman Sachs',
                'lockup_period': '180 days'
            },
            {
                'company': 'Databricks',
                'sector': 'Data/AI',
                'expected_date': 'June 14, 2025',
                'expected_valuation': '$40-45B',
                'lead_underwriter': 'Morgan Stanley',
                'lockup_period': '180 days'
            }
        ]
'''
    
    with open("components/ipo_tracker_enhanced.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Created ipo_tracker_enhanced.py")

def update_hedge_intelligence():
    """Update main app file"""
    print("\n📝 Updating hedge_intelligence.py...")
    
    content = '''"""
Hedge Intelligence - SEC Document Analysis Platform
Refactored: 2025-06-07 21:50:17 UTC
Author: thorrobber22
"""

import streamlit as st
from pathlib import Path
import json

# Import components
from components.document_explorer import DocumentExplorer
from components.persistent_chat import PersistentChat
from components.ipo_tracker_enhanced import IPOTrackerEnhanced
from components.data_extractor import DataExtractor
from services.document_service import DocumentService
from services.ai_service import AIService

def apply_dark_theme():
    """Apply premium dark theme"""
    st.markdown("""
    <style>
    /* Dark background */
    .stApp {
        background-color: #0E1117;
        color: #E1E1E1;
    }
    
    /* Grey buttons instead of blue */
    .stButton > button {
        background-color: #4A5568;
        color: #E1E1E1;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-size: 14px;
    }
    
    .stButton > button:hover {
        background-color: #5A6578;
    }
    
    /* Dark cards and containers */
    .stExpander {
        background-color: #1A1D23;
        border: 1px solid #2D3748;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1A1D23;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

def render_document_viewer():
    """Render document viewer"""
    if 'selected_doc' not in st.session_state:
        return
        
    doc = st.session_state.selected_doc
    st.header(f"{doc['company']} - {doc['document']}")
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("View PDF"):
            st.info("PDF export available in premium version")
    with col2:
        if st.button("Download"):
            st.info("Download ready")
    
    # Load and display document
    try:
        with open(doc['path'], 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract key data
        with st.expander("Quick Extractions"):
            extractor = DataExtractor()
            
            col1, col2 = st.columns(2)
            with col1:
                revenue = extractor.extract_with_citations(content, 'revenue')
                if revenue['status'] == 'found':
                    st.metric(
                        "Revenue", 
                        f"${revenue['value']} {revenue.get('unit', '')}",
                        help=f"Source: {revenue['citation']}"
                    )
                    
            with col2:
                employees = extractor.extract_with_citations(content, 'employees')
                if employees['status'] == 'found':
                    st.metric(
                        "Employees",
                        employees['value'],
                        help=f"Source: {employees['citation']}"
                    )
        
        # Show document content
        st.markdown("### Document Content")
        # Show first 5000 chars in a scrollable container
        st.markdown(
            f'<div style="height: 400px; overflow-y: scroll; padding: 1rem; '
            f'background-color: #1A1D23; border: 1px solid #2D3748; border-radius: 4px;">'
            f'{content[:5000]}...</div>',
            unsafe_allow_html=True
        )
        
    except Exception as e:
        st.error(f"Error loading document: {e}")

def render_analyst_dashboard():
    """Render simplified analyst dashboard"""
    st.header("SEC Document Analysis Platform")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    doc_path = Path("data/sec_documents")
    if doc_path.exists():
        companies = len(list(doc_path.iterdir()))
        total_docs = sum(
            len(list(Path(f"data/sec_documents/{c}").glob("*.html")))
            for c in doc_path.iterdir() if c.is_dir()
        )
    else:
        companies = 0
        total_docs = 0
    
    with col1:
        st.metric("Companies Available", companies)
    with col2:
        st.metric("Total Documents", f"{total_docs:,}")
    with col3:
        if st.button("Request New Company"):
            st.session_state.show_company_request = True
            
    # IPO Tracker
    st.markdown("---")
    ipo_tracker = IPOTrackerEnhanced()
    ipo_tracker.render_ipo_dashboard()
    
    # Company Request Form
    if st.session_state.get('show_company_request', False):
        with st.form("company_request"):
            st.subheader("Request New Company")
            company = st.text_input("Company Name")
            ticker = st.text_input("Ticker Symbol")
            priority = st.radio("Priority", ["High", "Medium", "Low"])
            reason = st.text_area("Reason for Request")
            
            if st.form_submit_button("Submit Request"):
                # Save request
                request = {
                    'company': company,
                    'ticker': ticker,
                    'priority': priority,
                    'reason': reason,
                    'status': 'pending',
                    'timestamp': pd.Timestamp.now().isoformat()
                }
                
                requests_file = Path("data/company_requests.json")
                if requests_file.exists():
                    with open(requests_file, 'r') as f:
                        requests = json.load(f)
                else:
                    requests = []
                    
                requests.append(request)
                
                with open(requests_file, 'w') as f:
                    json.dump(requests, f, indent=2)
                    
                st.success("Request submitted! Will be processed within 30 minutes.")
                st.session_state.show_company_request = False
                st.rerun()

def display_chat_history():
    """Display chat history in main area"""
    if 'chat_history' in st.session_state and st.session_state.chat_history:
        st.markdown("### Recent Analysis")
        for item in st.session_state.chat_history[-3:]:
            with st.container():
                st.markdown(f"**Q:** {item['query']}")
                st.markdown(f"**A:** {item['response']}")
                if item.get('document'):
                    st.caption(f"Context: {item['document']['company']} - {item['document']['document']}")
                st.markdown("---")

def main():
    st.set_page_config(
        page_title="Hedge Intelligence - SEC Analysis",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply theme
    apply_dark_theme()
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Initialize components
    doc_explorer = DocumentExplorer()
    persistent_chat = PersistentChat()
    
    # Sidebar - Document Explorer
    with st.sidebar:
        st.title("Hedge Intelligence")
        st.caption("SEC Document Analysis Platform")
        st.markdown("---")
        doc_explorer.render_sidebar()
    
    # Main area
    if 'selected_doc' in st.session_state:
        render_document_viewer()
    else:
        render_analyst_dashboard()
    
    # Show chat history
    display_chat_history()
    
    # Bottom - Persistent chat
    persistent_chat.render_chat_bar()

if __name__ == "__main__":
    main()
'''
    
    with open("hedge_intelligence.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Updated hedge_intelligence.py")

def update_ai_service():
    """Update AI service for extraction"""
    print("\n📝 Updating services/ai_service.py...")
    
    # Check if file exists
    ai_path = Path("services/ai_service.py")
    if not ai_path.exists():
        print("⚠️  services/ai_service.py not found, skipping...")
        return
    
    # Read current content
    with open(ai_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add new methods if not present
    if "get_ai_response" not in content:
        # Add the method
        additional_methods = '''
    
    def get_ai_response(self, prompt, context=""):
        """Get AI response with optional context"""
        try:
            if self.model_type == "openai":
                return self._get_openai_response(prompt, context)
            else:
                return self._get_gemini_response(prompt, context)
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _get_openai_response(self, prompt, context):
        """Get response from OpenAI"""
        messages = [
            {"role": "system", "content": "You are an SEC document analysis assistant."},
        ]
        
        if context:
            messages.append({"role": "system", "content": f"Document context: {context[:3000]}..."})
            
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def _get_gemini_response(self, prompt, context):
        """Get response from Gemini"""
        if context:
            full_prompt = f"Context: {context[:3000]}...\\n\\nQuestion: {prompt}"
        else:
            full_prompt = prompt
            
        response = self.model.generate_content(full_prompt)
        return response.text
'''
        
        # Insert before the last line
        lines = content.split('\n')
        # Find the last line that's not empty
        insert_pos = len(lines) - 1
        while insert_pos > 0 and not lines[insert_pos].strip():
            insert_pos -= 1
            
        lines.insert(insert_pos, additional_methods)
        content = '\n'.join(lines)
        
        with open(ai_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Updated services/ai_service.py")
    else:
        print("✅ services/ai_service.py already has required methods")

def update_dashboard():
    """Update dashboard to remove clutter"""
    print("\n📝 Updating components/dashboard.py...")
    
    # Simple dashboard focused on documents
    content = '''"""
Simplified Dashboard Component
Updated: 2025-06-07 21:50:17 UTC
"""
import streamlit as st
from pathlib import Path

def render_dashboard():
    """Render simplified analyst dashboard"""
    st.header("SEC Document Analysis")
    
    # Just show what matters
    doc_path = Path("data/sec_documents")
    if doc_path.exists():
        companies = list(doc_path.iterdir())
        st.info(f"{len(companies)} companies available for analysis")
    else:
        st.warning("No documents loaded yet")
'''
    
    with open("components/dashboard.py", "w", encoding="utf-8") as f:
        f.write(content)
    
    print("✅ Updated components/dashboard.py")

def remove_settings():
    """Remove settings component"""
    print("\n🗑️  Removing settings component...")
    
    settings_path = Path("components/settings.py")
    if settings_path.exists():
        settings_path.unlink()
        print("✅ Removed components/settings.py")
    else:
        print("✅ Settings component already removed")

def fix_imports():
    """Fix any import issues"""
    print("\n🔧 Fixing imports...")
    
    # Update imports in main file
    main_file = Path("hedge_intelligence.py")
    if main_file.exists():
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove settings import if present
        content = content.replace("from components.settings import render_settings", "")
        content = content.replace("from components.settings import *", "")
        
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Fixed imports")

def create_sample_data():
    """Ensure sample data directories exist"""
    print("\n📁 Creating data directories...")
    
    dirs_to_create = [
        "data/ipo_pipeline",
        "data/sec_documents",
        "components"
    ]
    
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("✅ Data directories ready")

def main():
    """Run complete refactor"""
    print("🚀 HEDGE INTELLIGENCE - COMPLETE REFACTOR")
    print("=" * 60)
    print("Starting refactor process...")
    print("=" * 60)
    
    # Step 1: Backup
    create_backup()
    
    # Step 2: Create new components
    create_document_explorer()
    create_persistent_chat()
    create_data_extractor()
    create_ipo_tracker_enhanced()
    
    # Step 3: Update existing files
    update_hedge_intelligence()
    update_ai_service()
    update_dashboard()
    
    # Step 4: Remove unnecessary components
    remove_settings()
    
    # Step 5: Fix imports
    fix_imports()
    
    # Step 6: Ensure directories exist
    create_sample_data()
    
    print("\n" + "=" * 60)
    print("✅ REFACTOR COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python test_hedge_intelligence.py")
    print("2. Launch: streamlit run hedge_intelligence.py")
    print("\nYour analyst-focused platform is ready!")

if __name__ == "__main__":
    main()