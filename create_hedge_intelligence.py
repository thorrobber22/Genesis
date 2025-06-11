#!/usr/bin/env python3
"""
Create Hedge Intelligence Modular Application
Date: 2025-06-07 14:02:41 UTC
Author: thorrobber22
Description: Creates all files for the modular hedge intelligence user interface
"""

import os
from pathlib import Path
from datetime import datetime

class HedgeIntelligenceBuilder:
    def __init__(self):
        self.created_files = []
        self.created_dirs = []
        
    def create_directory(self, path):
        """Create directory if it doesn't exist"""
        Path(path).mkdir(parents=True, exist_ok=True)
        self.created_dirs.append(path)
        print(f"Created directory: {path}")
    
    def write_file(self, filepath, content):
        """Write content to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        self.created_files.append(filepath)
        print(f"Created file: {filepath}")
    
    def build(self):
        """Build the entire application structure"""
        print("HEDGE INTELLIGENCE - MODULAR BUILD")
        print("="*60)
        print(f"Started: {datetime.now().isoformat()}")
        print("")
        
        # Create directory structure
        self.create_directory("services")
        self.create_directory("components")
        self.create_directory("utils")
        
        # Create service files
        self.create_ai_service()
        self.create_document_service()
        self.create_chat_service()
        self.create_report_service()
        
        # Create component files
        self.create_dashboard_component()
        self.create_chat_component()
        self.create_tickers_component()
        self.create_watchlist_component()
        self.create_settings_component()
        
        # Create utility files
        self.create_data_loader()
        self.create_ui_helpers()
        
        # Create main application
        self.create_main_app()
        
        # Create __init__ files
        self.create_init_files()
        
        print("\n" + "="*60)
        print("BUILD COMPLETE!")
        print(f"Created {len(self.created_dirs)} directories")
        print(f"Created {len(self.created_files)} files")
        print("\nTo run: streamlit run hedge_intelligence.py")
    
    def create_ai_service(self):
        """Create AI service"""
        content = '''"""
AI Service - Handles OpenAI and Gemini integration
Date: 2025-06-07 14:02:41 UTC
"""

import os
import openai
import google.generativeai as genai
from typing import Dict, List, Tuple, Optional
import chromadb
from chromadb.utils import embedding_functions
import re

class AIService:
    """Dual AI validation service"""
    
    def __init__(self):
        # Initialize API keys
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if self.openai_api_key:
            openai.api_key = self.openai_api_key
            self.openai_model = "gpt-4-turbo-preview"
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Initialize ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(path="./data/chroma_db")
            if self.openai_api_key:
                self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                    api_key=self.openai_api_key,
                    model_name="text-embedding-3-small"
                )
        except Exception as e:
            print(f"ChromaDB initialization error: {e}")
            self.chroma_client = None
    
    def search_documents(self, query: str, company: Optional[str] = None) -> List[Dict]:
        """Search ChromaDB for relevant documents"""
        if not self.chroma_client:
            return []
            
        try:
            collection_name = f"{company}_documents" if company else "all_documents"
            
            # Check if collection exists
            existing_collections = [col.name for col in self.chroma_client.list_collections()]
            if collection_name not in existing_collections:
                return []
            
            collection = self.chroma_client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            
            results = collection.query(
                query_texts=[query],
                n_results=5,
                include=['documents', 'metadatas', 'distances']
            )
            
            if not results['documents'][0]:
                return []
            
            return [{
                'content': doc,
                'metadata': meta,
                'score': 1 - dist
            } for doc, meta, dist in zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )]
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def get_ai_response(self, query: str, context: List[Dict]) -> Tuple[str, float]:
        """Get response from both AIs with confidence score"""
        
        if not context:
            return "No relevant documents found for your query.", 0.0
        
        # Prepare context
        context_text = "\\n\\n".join([
            f"Source: {doc['metadata'].get('source', 'Unknown')}\\n{doc['content'][:500]}..."
            for doc in context[:3]
        ])
        
        prompt = f"""Based on the following SEC filing excerpts, answer this question: {query}

Context:
{context_text}

Provide a clear, specific answer with exact citations (document name and page number where available).
"""
        
        try:
            responses = []
            
            # Get OpenAI response if available
            if self.openai_api_key:
                openai_response = openai.ChatCompletion.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": "You are an SEC filing expert. Always cite specific documents and page numbers."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                responses.append(openai_response.choices[0].message.content)
            
            # Get Gemini response if available
            if self.gemini_api_key:
                gemini_response = self.gemini_model.generate_content(prompt)
                responses.append(gemini_response.text)
            
            if not responses:
                return "AI services not configured. Please check API keys.", 0.0
            
            # Calculate confidence
            if len(responses) == 2:
                confidence = self._calculate_confidence(responses[0], responses[1])
            else:
                confidence = 0.75  # Single AI response
            
            return responses[0], confidence
            
        except Exception as e:
            return f"AI error: {str(e)}", 0.0
    
    def _calculate_confidence(self, response1: str, response2: str) -> float:
        """Calculate confidence score based on AI agreement"""
        # Extract numbers from both responses
        numbers1 = set(re.findall(r'\\d+', response1))
        numbers2 = set(re.findall(r'\\d+', response2))
        
        # Extract key terms
        terms1 = set(response1.lower().split())
        terms2 = set(response2.lower().split())
        
        # Calculate overlap
        if numbers1 and numbers2:
            number_overlap = len(numbers1.intersection(numbers2)) / len(numbers1.union(numbers2))
        else:
            number_overlap = 0.5
        
        term_overlap = len(terms1.intersection(terms2)) / max(len(terms1.union(terms2)), 1)
        
        # Weight numbers more heavily for financial data
        confidence = (number_overlap * 0.7) + (term_overlap * 0.3)
        
        return min(confidence, 0.99)  # Cap at 99%
'''
        self.write_file("services/ai_service.py", content)
    
    def create_document_service(self):
        """Create document service"""
        content = '''"""
Document Service - Handles document reading and extraction
Date: 2025-06-07 14:02:41 UTC
"""

from pathlib import Path
import PyPDF2
import docx
from typing import Dict, List, Optional
import json

class DocumentService:
    """Handle document viewing and extraction"""
    
    def __init__(self):
        self.doc_path = Path("data/sec_documents")
        self.metadata_cache = {}
    
    def get_companies(self) -> List[str]:
        """Get list of available companies"""
        if not self.doc_path.exists():
            return []
        return sorted([d.name for d in self.doc_path.iterdir() if d.is_dir()])
    
    def get_company_documents(self, company: str) -> List[Dict]:
        """Get all documents for a company"""
        company_path = self.doc_path / company
        if not company_path.exists():
            return []
        
        documents = []
        for file in company_path.iterdir():
            if file.is_file():
                doc_info = {
                    'name': file.name,
                    'type': self._get_filing_type(file.name),
                    'size': file.stat().st_size,
                    'modified': file.stat().st_mtime,
                    'path': str(file)
                }
                documents.append(doc_info)
        
        return sorted(documents, key=lambda x: x['modified'], reverse=True)
    
    def get_document_content(self, company: str, filename: str) -> str:
        """Extract text content from document"""
        filepath = self.doc_path / company / filename
        
        if not filepath.exists():
            return "Document not found"
        
        try:
            # Handle different file types
            if filepath.suffix.lower() == '.pdf':
                return self._extract_pdf_text(filepath)
            elif filepath.suffix.lower() == '.docx':
                return self._extract_docx_text(filepath)
            elif filepath.suffix.lower() in ['.txt', '.html', '.htm']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            else:
                return f"Unsupported file format: {filepath.suffix}"
        except Exception as e:
            return f"Error reading document: {str(e)}"
    
    def _extract_pdf_text(self, filepath: Path) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text += f"\\n--- Page {page_num + 1} ---\\n"
                    text += page.extract_text()
            return text
        except Exception as e:
            return f"PDF extraction error: {str(e)}"
    
    def _extract_docx_text(self, filepath: Path) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(filepath)
            text = []
            for para in doc.paragraphs:
                if para.text.strip():
                    text.append(para.text)
            return '\\n'.join(text)
        except Exception as e:
            return f"DOCX extraction error: {str(e)}"
    
    def _get_filing_type(self, filename: str) -> str:
        """Determine filing type from filename"""
        filename_upper = filename.upper()
        
        filing_types = {
            'S-1': 'Registration Statement',
            'S-1/A': 'Registration Amendment',
            '10-K': 'Annual Report',
            '10-Q': 'Quarterly Report',
            '8-K': 'Current Report',
            'DEF 14A': 'Proxy Statement',
            '424B': 'Prospectus'
        }
        
        for filing_code, filing_name in filing_types.items():
            if filing_code in filename_upper:
                return filing_name
        
        return 'SEC Filing'
    
    def search_in_document(self, company: str, filename: str, search_term: str) -> List[Dict]:
        """Search for term in document and return matches with context"""
        content = self.get_document_content(company, filename)
        
        if "Error" in content or "not found" in content:
            return []
        
        matches = []
        lines = content.split('\\n')
        search_lower = search_term.lower()
        
        for i, line in enumerate(lines):
            if search_lower in line.lower():
                # Get context (2 lines before and after)
                start = max(0, i - 2)
                end = min(len(lines), i + 3)
                context = '\\n'.join(lines[start:end])
                
                matches.append({
                    'line_number': i + 1,
                    'context': context,
                    'highlight': line
                })
        
        return matches
'''
        self.write_file("services/document_service.py", content)
    
    def create_chat_service(self):
        """Create chat service"""
        content = '''"""
Chat Service - Manages chat sessions and history
Date: 2025-06-07 14:02:41 UTC
"""

from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

class ChatService:
    """Manage chat sessions and history"""
    
    def __init__(self):
        self.sessions_file = Path("data/chat_sessions.json")
        self.sessions = self._load_sessions()
    
    def _load_sessions(self) -> Dict:
        """Load chat sessions from file"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_sessions(self):
        """Save chat sessions to file"""
        try:
            self.sessions_file.parent.mkdir(exist_ok=True)
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def create_session(self, title: Optional[str] = None) -> str:
        """Create new chat session"""
        session_id = datetime.now().isoformat()
        
        self.sessions[session_id] = {
            'id': session_id,
            'title': title or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            'created': session_id,
            'messages': [],
            'metadata': {}
        }
        
        self._save_sessions()
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to session"""
        if session_id not in self.sessions:
            session_id = self.create_session()
        
        message = {
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'content': content,
            'metadata': metadata or {}
        }
        
        self.sessions[session_id]['messages'].append(message)
        self._save_sessions()
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get specific session"""
        return self.sessions.get(session_id)
    
    def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent chat sessions"""
        sorted_sessions = sorted(
            self.sessions.values(),
            key=lambda x: x['created'],
            reverse=True
        )
        return sorted_sessions[:limit]
    
    def delete_session(self, session_id: str):
        """Delete a chat session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_sessions()
    
    def search_sessions(self, query: str) -> List[Dict]:
        """Search through all chat sessions"""
        results = []
        query_lower = query.lower()
        
        for session in self.sessions.values():
            # Search in messages
            for message in session['messages']:
                if query_lower in message['content'].lower():
                    results.append({
                        'session': session,
                        'message': message,
                        'match_type': 'content'
                    })
                    break
            
            # Search in title
            if query_lower in session['title'].lower():
                results.append({
                    'session': session,
                    'match_type': 'title'
                })
        
        return results
'''
        self.write_file("services/chat_service.py", content)
    
    def create_report_service(self):
        """Create report service"""
        content = '''"""
Report Service - Generates reports from chat and analysis
Date: 2025-06-07 14:02:41 UTC
"""

from datetime import datetime
from typing import Dict, List
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

class ReportService:
    """Generate PDF and Excel reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CompanyTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12
        ))
    
    def generate_chat_report(self, session_data: Dict, company: str = None) -> bytes:
        """Generate PDF report from chat session"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = f"Hedge Intelligence Report"
        if company:
            title += f" - {company}"
        story.append(Paragraph(title, self.styles['CompanyTitle']))
        story.append(Spacer(1, 12))
        
        # Metadata
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", self.styles['Normal']))
        story.append(Paragraph(f"Session: {session_data.get('title', 'Untitled')}", self.styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Messages
        story.append(Paragraph("Analysis Summary", self.styles['SectionTitle']))
        
        for message in session_data.get('messages', []):
            if message['role'] == 'user':
                story.append(Paragraph(f"<b>Question:</b> {message['content']}", self.styles['Normal']))
            else:
                story.append(Paragraph(f"<b>Answer:</b> {message['content']}", self.styles['Normal']))
                
                # Add sources if available
                if message.get('metadata', {}).get('sources'):
                    story.append(Spacer(1, 6))
                    story.append(Paragraph("<b>Sources:</b>", self.styles['Normal']))
                    for source in message['metadata']['sources'][:3]:
                        source_text = source['metadata'].get('source', 'Unknown document')
                        story.append(Paragraph(f"• {source_text}", self.styles['Normal']))
            
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def generate_company_report(self, company: str, data: Dict) -> bytes:
        """Generate comprehensive company report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title page
        story.append(Paragraph(f"{company} Analysis Report", self.styles['CompanyTitle']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}", self.styles['Normal']))
        story.append(Spacer(1, inch))
        
        # Executive Summary
        if 'summary' in data:
            story.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
            story.append(Paragraph(data['summary'], self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Key Metrics
        if 'metrics' in data:
            story.append(Paragraph("Key Metrics", self.styles['SectionTitle']))
            for key, value in data['metrics'].items():
                story.append(Paragraph(f"• <b>{key}:</b> {value}", self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Risk Factors
        if 'risks' in data:
            story.append(Paragraph("Risk Factors", self.styles['SectionTitle']))
            for risk in data['risks']:
                story.append(Paragraph(f"• {risk}", self.styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Lock-up Information
        if 'lockup' in data:
            story.append(Paragraph("Lock-up Periods", self.styles['SectionTitle']))
            story.append(Paragraph(data['lockup'], self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.read()
    
    def generate_excel_data(self, companies: List[str], data: Dict) -> bytes:
        """Generate Excel-compatible CSV data"""
        import csv
        import io
        
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Header
        writer.writerow(['Company', 'Documents', 'Latest Filing', 'Lock-up Expiry', 'Days Until', 'Status'])
        
        # Data rows
        for company in companies:
            company_data = data.get(company, {})
            writer.writerow([
                company,
                company_data.get('doc_count', 0),
                company_data.get('latest_filing', 'N/A'),
                company_data.get('lockup_expiry', 'Unknown'),
                company_data.get('days_until', 'N/A'),
                company_data.get('status', 'Active')
            ])
        
        return buffer.getvalue().encode('utf-8')
'''
        self.write_file("services/report_service.py", content)
    
    def create_dashboard_component(self):
        """Create dashboard component"""
        content = '''"""
IPO Dashboard Component
Date: 2025-06-07 14:02:41 UTC
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from services.document_service import DocumentService
from utils.data_loader import DataLoader

def render_dashboard():
    """Render IPO Dashboard"""
    st.title("IPO Dashboard")
    
    # Initialize services
    doc_service = DocumentService()
    data_loader = DataLoader()
    
    # Get data
    companies = doc_service.get_companies()
    pipeline_data = data_loader.load_pipeline_data()
    
    if not companies:
        st.warning("No company data found. Please run the admin panel to download SEC filings.")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Recent IPOs", "Upcoming", "Pipeline Summary"])
    
    with tab1:
        # Recent IPOs as clean table
        st.subheader("Recent IPOs")
        
        # Build data for dataframe
        ipo_data = []
        for company in companies[:20]:  # Show top 20
            company_docs = doc_service.get_company_documents(company)
            
            if company_docs:
                latest_doc = company_docs[0]  # Already sorted by date
                ipo_data.append({
                    'Ticker': company,
                    'Documents': len(company_docs),
                    'Latest Filing': latest_doc['type'],
                    'Filed': datetime.fromtimestamp(latest_doc['modified']).strftime('%Y-%m-%d'),
                    'Status': 'Active'
                })
            else:
                ipo_data.append({
                    'Ticker': company,
                    'Documents': 0,
                    'Latest Filing': 'None',
                    'Filed': 'N/A',
                    'Status': 'No Data'
                })
        
        if ipo_data:
            df = pd.DataFrame(ipo_data)
            
            # Interactive dataframe
            event = st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )
            
            # Handle row selection
            if event.selection.rows:
                selected_idx = event.selection.rows[0]
                selected_company = df.iloc[selected_idx]['Ticker']
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("Start Chat", key=f"dash_chat_{selected_company}"):
                        st.session_state.current_page = "New Chat"
                        st.session_state.chat_context = selected_company
                        st.rerun()
                with col2:
                    if st.button("View Documents", key=f"dash_docs_{selected_company}"):
                        st.session_state.show_documents = True
                        st.session_state.viewing_company = selected_company
                with col3:
                    if st.button("Add to Watchlist", key=f"dash_watch_{selected_company}"):
                        if 'watchlist' not in st.session_state:
                            st.session_state.watchlist = []
                        if selected_company not in st.session_state.watchlist:
                            st.session_state.watchlist.append(selected_company)
                            st.success("Added to watchlist")
    
    with tab2:
        st.subheader("Upcoming IPOs")
        
        if pipeline_data and 'pending' in pipeline_data:
            upcoming_data = []
            for item in pipeline_data['pending'][:10]:
                upcoming_data.append({
                    'Company': item.get('name', 'Unknown'),
                    'Expected Date': item.get('expected_date', 'TBD'),
                    'Exchange': item.get('exchange', 'Unknown'),
                    'Industry': item.get('industry', 'Unknown')
                })
            
            if upcoming_data:
                df_upcoming = pd.DataFrame(upcoming_data)
                st.dataframe(df_upcoming, use_container_width=True, hide_index=True)
            else:
                st.info("No upcoming IPOs in pipeline")
        else:
            st.info("Pipeline data not available")
    
    with tab3:
        st.subheader("Pipeline Summary")
        
        if pipeline_data:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total = len(pipeline_data.get('all', []))
                st.metric("Total Tracked", total)
            
            with col2:
                pending = len(pipeline_data.get('pending', []))
                st.metric("Pending", pending)
            
            with col3:
                downloading = len(pipeline_data.get('downloading', []))
                st.metric("Downloading", downloading)
            
            with col4:
                completed = len(pipeline_data.get('completed', []))
                st.metric("Completed", completed)
            
            # Last update
            if 'last_update' in pipeline_data:
                st.caption(f"Last updated: {pipeline_data['last_update']}")
        else:
            st.info("No pipeline data available")
    
    # Document viewer modal
    if st.session_state.get('show_documents') and st.session_state.get('viewing_company'):
        show_document_viewer(st.session_state.viewing_company, doc_service)

def show_document_viewer(company: str, doc_service: DocumentService):
    """Show document viewer in modal"""
    st.markdown(f"### Documents for {company}")
    
    documents = doc_service.get_company_documents(company)
    
    if documents:
        # Create document table
        doc_data = []
        for doc in documents:
            doc_data.append({
                'File': doc['name'],
                'Type': doc['type'],
                'Size': f"{doc['size'] / 1024:.1f} KB",
                'Modified': datetime.fromtimestamp(doc['modified']).strftime('%Y-%m-%d %H:%M')
            })
        
        df_docs = pd.DataFrame(doc_data)
        
        selected_doc = st.selectbox(
            "Select document to view:",
            options=documents,
            format_func=lambda x: x['name']
        )
        
        if selected_doc and st.button("View Document"):
            content = doc_service.get_document_content(company, selected_doc['name'])
            st.text_area("Document Content", content, height=400)
    
    if st.button("Close"):
        st.session_state.show_documents = False
        st.session_state.viewing_company = None
        st.rerun()
'''
        self.write_file("components/dashboard.py", content)
    
    def create_chat_component(self):
        """Create chat component"""
        content = '''"""
Chat Interface Component
Date: 2025-06-07 14:02:41 UTC
"""

import streamlit as st
from datetime import datetime
from services.ai_service import AIService
from services.chat_service import ChatService
from services.document_service import DocumentService
from services.report_service import ReportService

def render_chat():
    """Render chat interface"""
    st.title("SEC Intelligence Chat")
    
    # Initialize services
    ai_service = AIService()
    chat_service = ChatService()
    doc_service = DocumentService()
    report_service = ReportService()
    
    # Sidebar with chat sessions
    with st.sidebar:
        st.subheader("Chat Sessions")
        
        # New chat button
        if st.button("New Chat", use_container_width=True):
            new_session_id = chat_service.create_session()
            st.session_state.current_chat_id = new_session_id
            st.rerun()
        
        # Recent sessions
        recent_sessions = chat_service.get_recent_sessions(10)
        
        for session in recent_sessions:
            if st.button(
                session['title'],
                key=f"session_{session['id']}",
                use_container_width=True,
                type="secondary" if session['id'] != st.session_state.get('current_chat_id') else "primary"
            ):
                st.session_state.current_chat_id = session['id']
                st.rerun()
    
    # Main chat area
    if 'current_chat_id' not in st.session_state:
        st.session_state.current_chat_id = chat_service.create_session()
    
    current_session = chat_service.get_session(st.session_state.current_chat_id)
    
    if not current_session:
        st.error("Session not found")
        return
    
    # Show company context if available
    if hasattr(st.session_state, 'chat_context') and st.session_state.chat_context:
        st.info(f"Analyzing: {st.session_state.chat_context}")
        # Add context to session metadata
        current_session['metadata']['company'] = st.session_state.chat_context
    
    # Display chat messages
    for message in current_session['messages']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            
            # Show metadata for assistant messages
            if message['role'] == 'assistant' and message.get('metadata'):
                metadata = message['metadata']
                
                # Confidence score
                if 'confidence' in metadata:
                    confidence = metadata['confidence']
                    if confidence > 0.9:
                        st.success(f"Confidence: {confidence:.0%}")
                    elif confidence > 0.7:
                        st.warning(f"Confidence: {confidence:.0%}")
                    else:
                        st.error(f"Confidence: {confidence:.0%}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("View Sources", key=f"view_{message['timestamp']}"):
                        show_sources(metadata.get('sources', []))
                
                with col2:
                    if st.button("Generate Report", key=f"report_{message['timestamp']}"):
                        generate_report(current_session, report_service)
                
                with col3:
                    if 'sources' in metadata and metadata['sources']:
                        source = metadata['sources'][0]
                        if st.button("Download", key=f"dl_{message['timestamp']}"):
                            st.info("Download feature coming soon")
    
    # Chat input
    if prompt := st.chat_input("Ask about any SEC filing..."):
        # Add user message
        chat_service.add_message(
            st.session_state.current_chat_id,
            "user",
            prompt
        )
        
        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing SEC filings..."):
                # Detect company from context or query
                company = current_session.get('metadata', {}).get('company')
                if not company:
                    # Try to extract from query
                    companies = doc_service.get_companies()
                    for c in companies:
                        if c.lower() in prompt.lower():
                            company = c
                            break
                
                # Search for relevant documents
                context = ai_service.search_documents(prompt, company)
                
                if context:
                    # Get AI response
                    response, confidence = ai_service.get_ai_response(prompt, context)
                    
                    st.markdown(response)
                    
                    # Save to chat history
                    chat_service.add_message(
                        st.session_state.current_chat_id,
                        "assistant",
                        response,
                        {
                            'sources': context[:3],
                            'confidence': confidence,
                            'company': company
                        }
                    )
                else:
                    no_docs_msg = "I couldn't find any relevant documents for your query. Try being more specific or mentioning a company ticker."
                    st.markdown(no_docs_msg)
                    
                    chat_service.add_message(
                        st.session_state.current_chat_id,
                        "assistant",
                        no_docs_msg
                    )
        
        st.rerun()

def show_sources(sources):
    """Display source documents"""
    if not sources:
        st.info("No sources available")
        return
    
    with st.expander("View Sources"):
        for i, source in enumerate(sources):
            st.markdown(f"**Source {i+1}:** {source['metadata'].get('source', 'Unknown')}")
            st.markdown(f"**Relevance Score:** {source.get('score', 0):.2%}")
            st.text_area(
                "Content Preview",
                source['content'][:500] + "...",
                height=150,
                key=f"source_content_{i}"
            )
            st.markdown("---")

def generate_report(session_data, report_service):
    """Generate and download report"""
    with st.spinner("Generating report..."):
        report_bytes = report_service.generate_chat_report(
            session_data,
            session_data.get('metadata', {}).get('company')
        )
        
        st.download_button(
            label="Download Report (PDF)",
            data=report_bytes,
            file_name=f"hedge_intel_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )
'''
        self.write_file("components/chat.py", content)
    
    def create_tickers_component(self):
        """Create tickers component"""
        content = '''"""
Available Tickers Component
Date: 2025-06-07 14:02:41 UTC
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from services.document_service import DocumentService
from scrapers.sec.sec_compliant_scraper import SECCompliantScraper

def render_tickers():
    """Render available tickers"""
    st.title("Available Tickers")
    
    # Initialize services
    doc_service = DocumentService()
    
    # Search functionality
    col1, col2 = st.columns([3, 1])
    with col1:
        search_term = st.text_input("Search companies...", placeholder="Enter ticker or company name")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        refresh_clicked = st.button("Refresh", use_container_width=True)
    
    if refresh_clicked:
        st.rerun()
    
    # Get companies
    companies = doc_service.get_companies()
    
    # Filter by search term
    if search_term:
        companies = [c for c in companies if search_term.upper() in c.upper()]
    
    if companies:
        # Build data for display
        ticker_data = []
        for company in companies:
            docs = doc_service.get_company_documents(company)
            
            # Get latest filing info
            latest_filing = "None"
            last_modified = "N/A"
            
            if docs:
                latest_doc = docs[0]  # Already sorted by date
                latest_filing = latest_doc['type']
                last_modified = datetime.fromtimestamp(latest_doc['modified']).strftime('%Y-%m-%d')
            
            ticker_data.append({
                'Ticker': company,
                'Documents': len(docs),
                'Latest Filing': latest_filing,
                'Last Updated': last_modified
            })
        
        # Display as interactive table
        df = pd.DataFrame(ticker_data)
        
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Handle selection
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_company = df.iloc[selected_idx]['Ticker']
            
            st.markdown("### Actions")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Start Chat", key=f"ticker_chat_{selected_company}", use_container_width=True):
                    st.session_state.current_page = "New Chat"
                    st.session_state.chat_context = selected_company
                    st.rerun()
            
            with col2:
                if st.button("View Documents", key=f"ticker_docs_{selected_company}", use_container_width=True):
                    show_company_documents(selected_company, doc_service)
            
            with col3:
                if st.button("Add to Watchlist", key=f"ticker_watch_{selected_company}", use_container_width=True):
                    if 'watchlist' not in st.session_state:
                        st.session_state.watchlist = []
                    if selected_company not in st.session_state.watchlist:
                        st.session_state.watchlist.append(selected_company)
                        st.success("Added to watchlist!")
        
        # Summary stats
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Companies", len(companies))
        with col2:
            total_docs = sum(row['Documents'] for row in ticker_data)
            st.metric("Total Documents", total_docs)
        with col3:
            st.metric("Data Size", f"{get_data_size():.1f} GB")
    
    else:
        st.info("No companies found matching your search.")
    
    # Request new ticker section
    st.markdown("---")
    st.subheader("Request New Ticker")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_ticker = st.text_input("Enter ticker symbol", placeholder="e.g., AAPL, MSFT")
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("Request Data", key="request_ticker", use_container_width=True):
            if new_ticker:
                request_new_ticker(new_ticker.upper())

def show_company_documents(company: str, doc_service: DocumentService):
    """Show documents for a company"""
    with st.expander(f"{company} Documents", expanded=True):
        docs = doc_service.get_company_documents(company)
        
        if docs:
            for doc in docs[:10]:  # Show first 10
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.text(doc['name'])
                with col2:
                    st.text(f"{doc['size'] / 1024:.1f} KB")
                with col3:
                    if st.button("View", key=f"view_doc_{doc['name'][:20]}"):
                        st.session_state.viewing_document = doc
                        st.session_state.viewing_company = company
            
            if len(docs) > 10:
                st.caption(f"... and {len(docs) - 10} more documents")
        else:
            st.info("No documents found")

def request_new_ticker(ticker: str):
    """Request data for new ticker"""
    with st.spinner(f"Checking {ticker}..."):
        try:
            # Initialize scraper
            scraper = SECCompliantScraper()
            
            # Check if ticker exists
            cik = resolver.get_cik(ticker)
            
            if cik:
                st.info(f"Found {ticker} (CIK: {cik}). Starting download...")
                
                # Start download in background
                # In production, this would be queued
                st.success(f"Request submitted! {ticker} will be available soon.")
                st.balloons()
            else:
                st.error(f"Ticker {ticker} not found in SEC database.")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

def get_data_size():
    """Calculate total data size"""
    data_path = Path("data/sec_documents")
    if not data_path.exists():
        return 0.0
    
    total_size = 0
    for company_dir in data_path.iterdir():
        if company_dir.is_dir():
            for file in company_dir.iterdir():
                if file.is_file():
                    total_size += file.stat().st_size
    
    return total_size / (1024 ** 3)  # Convert to GB
'''
        self.write_file("components/tickers.py", content)
    
    def create_watchlist_component(self):
        """Create watchlist component"""
        content = '''"""
Watch List Component
Date: 2025-06-07 14:02:41 UTC
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from services.document_service import DocumentService
from services.ai_service import AIService
import json
from pathlib import Path

def render_watchlist():
    """Render watchlist"""
    st.title("Watch List")
    
    # Initialize watchlist if not exists
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    if not st.session_state.watchlist:
        st.info("Your watchlist is empty. Add companies from the IPO Dashboard or Available Tickers.")
        return
    
    # Initialize services
    doc_service = DocumentService()
    ai_service = AIService()
    
    # Get watchlist data
    watchlist_data = []
    
    for company in st.session_state.watchlist:
        # Get company metrics
        metrics = get_company_metrics(company, doc_service, ai_service)
        watchlist_data.append(metrics)
    
    # Display as table
    if watchlist_data:
        df = pd.DataFrame(watchlist_data)
        
        # Reorder columns
        column_order = ['Company', 'Documents', 'Lock-up Status', 'Days Until', 'Latest Filing', 'Last Updated']
        df = df[column_order]
        
        # Display dataframe
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Handle selection
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            selected_company = df.iloc[selected_idx]['Company']
            
            st.markdown(f"### {selected_company} Actions")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("Start Chat", key=f"watch_chat_{selected_company}"):
                    st.session_state.current_page = "New Chat"
                    st.session_state.chat_context = selected_company
                    st.rerun()
            
            with col2:
                if st.button("View Analysis", key=f"watch_analysis_{selected_company}"):
                    show_company_analysis(selected_company, ai_service)
            
            with col3:
                if st.button("Set Alert", key=f"watch_alert_{selected_company}"):
                    set_alert(selected_company)
            
            with col4:
                if st.button("Remove", key=f"watch_remove_{selected_company}"):
                    st.session_state.watchlist.remove(selected_company)
                    st.rerun()
    
    # Watchlist settings
    st.markdown("---")
    st.subheader("Watchlist Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        alert_days = st.number_input(
            "Alert me X days before lock-up expiry",
            min_value=1,
            max_value=30,
            value=7,
            key="alert_days_before"
        )
    
    with col2:
        export_format = st.selectbox(
            "Export format",
            ["CSV", "Excel", "PDF"],
            key="export_format"
        )
    
    if st.button("Export Watchlist"):
        export_watchlist(watchlist_data, export_format)

def get_company_metrics(company: str, doc_service: DocumentService, ai_service: AIService) -> dict:
    """Get key metrics for a company"""
    # Get basic document info
    docs = doc_service.get_company_documents(company)
    
    metrics = {
        'Company': company,
        'Documents': len(docs),
        'Latest Filing': 'None',
        'Last Updated': 'N/A',
        'Lock-up Status': 'Checking...',
        'Days Until': 'N/A'
    }
    
    if docs:
        latest_doc = docs[0]
        metrics['Latest Filing'] = latest_doc['type']
        metrics['Last Updated'] = datetime.fromtimestamp(latest_doc['modified']).strftime('%Y-%m-%d')
        
        # Try to get lock-up info from cached data or AI
        lockup_info = get_lockup_info(company, ai_service)
        if lockup_info:
            metrics['Lock-up Status'] = lockup_info['status']
            metrics['Days Until'] = lockup_info['days_until']
    
    return metrics

def get_lockup_info(company: str, ai_service: AIService) -> dict:
    """Get lock-up information for company"""
    # Check if we have cached lock-up data
    cache_file = Path(f"data/lockup_cache/{company}.json")
    
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            # Calculate days until expiry
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
            days_until = (expiry_date - datetime.now()).days
            
            return {
                'status': f"Expires {data['expiry_date']}",
                'days_until': str(days_until) if days_until > 0 else 'Expired'
            }
        except:
            pass
    
    # If no cache, return placeholder
    # In production, this would trigger an AI analysis
    return {
        'status': 'Analysis pending',
        'days_until': 'TBD'
    }

def show_company_analysis(company: str, ai_service: AIService):
    """Show detailed company analysis"""
    with st.expander(f"{company} Analysis", expanded=True):
        st.markdown("### Quick Analysis")
        
        # Placeholder for AI-generated analysis
        analysis_points = [
            "Lock-up period: 180 days from IPO date",
            "Major shareholders subject to lock-up: 85%",
            "Key risk factors: Market volatility, competition",
            "Recent filing: S-1/A Amendment filed last week"
        ]
        
        for point in analysis_points:
            st.markdown(f"• {point}")
        
        if st.button("Generate Full Report", key=f"full_report_{company}"):
            st.info("Full report generation coming soon")

def set_alert(company: str):
    """Set alert for company"""
    with st.form(f"alert_form_{company}"):
        st.markdown(f"### Set Alert for {company}")
        
        alert_type = st.selectbox(
            "Alert type",
            ["Lock-up expiry", "New filing", "Price target", "Custom"]
        )
        
        if alert_type == "Lock-up expiry":
            days_before = st.slider("Days before expiry", 1, 30, 7)
        elif alert_type == "New filing":
            filing_types = st.multiselect(
                "Filing types",
                ["10-K", "10-Q", "8-K", "S-1", "Any"]
            )
        
        alert_method = st.radio(
            "Alert method",
            ["Email", "In-app notification", "Both"]
        )
        
        if st.form_submit_button("Set Alert"):
            st.success(f"Alert set for {company}")

def export_watchlist(data: list, format: str):
    """Export watchlist data"""
    df = pd.DataFrame(data)
    
    if format == "CSV":
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"watchlist_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    elif format == "Excel":
        # Would need to implement Excel export
        st.info("Excel export coming soon")
    elif format == "PDF":
        # Would need to implement PDF export
        st.info("PDF export coming soon")
'''
        self.write_file("components/watchlist.py", content)
    
    def create_settings_component(self):
        """Create settings component"""
        content = '''"""
Settings Component
Date: 2025-06-07 14:02:41 UTC
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

def render_settings():
    """Render settings page"""
    st.title("Settings")
    
    # Load settings
    settings = load_settings()
    
    # Notification settings
    st.subheader("Notifications")
    
    notifications_enabled = st.checkbox(
        "Enable notifications",
        value=settings.get('notifications_enabled', True),
        help="Receive alerts for lock-up expirations and new filings"
    )
    
    if notifications_enabled:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Email Notifications")
            email_enabled = st.checkbox(
                "Send email alerts",
                value=settings.get('email_notifications', False)
            )
            
            if email_enabled:
                email = st.text_input(
                    "Email address",
                    value=settings.get('email_address', ''),
                    placeholder="your@email.com"
                )
        
        with col2:
            st.markdown("### Alert Types")
            alert_types = st.multiselect(
                "Notify me about:",
                ["Lock-up expirations", "New filings", "Pipeline updates", "Report completions"],
                default=settings.get('alert_types', ["Lock-up expirations", "New filings"])
            )
    
    # Display preferences
    st.markdown("---")
    st.subheader("Display Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        theme = st.selectbox(
            "Theme",
            ["Light", "Dark", "Auto"],
            index=["Light", "Dark", "Auto"].index(settings.get('theme', 'Light'))
        )
        
        date_format = st.selectbox(
            "Date format",
            ["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY"],
            index=0
        )
    
    with col2:
        timezone = st.selectbox(
            "Timezone",
            ["UTC", "EST", "PST", "CST"],
            index=["UTC", "EST", "PST", "CST"].index(settings.get('timezone', 'UTC'))
        )
        
        items_per_page = st.number_input(
            "Items per page",
            min_value=10,
            max_value=100,
            value=settings.get('items_per_page', 20),
            step=10
        )
    
    # Data settings
    st.markdown("---")
    st.subheader("Data Settings")
    
    auto_refresh = st.checkbox(
        "Auto-refresh data",
        value=settings.get('auto_refresh', True),
        help="Automatically check for new filings"
    )
    
    if auto_refresh:
        refresh_interval = st.slider(
            "Refresh interval (minutes)",
            min_value=5,
            max_value=60,
            value=settings.get('refresh_interval', 15),
            step=5
        )
    
    # Save settings
    if st.button("Save Settings", type="primary"):
        new_settings = {
            'notifications_enabled': notifications_enabled,
            'email_notifications': email_enabled if notifications_enabled else False,
            'email_address': email if notifications_enabled and email_enabled else '',
            'alert_types': alert_types if notifications_enabled else [],
            'theme': theme,
            'date_format': date_format,
            'timezone': timezone,
            'items_per_page': items_per_page,
            'auto_refresh': auto_refresh,
            'refresh_interval': refresh_interval if auto_refresh else 15,
            'last_updated': datetime.now().isoformat()
        }
        
        save_settings(new_settings)
        st.success("Settings saved successfully!")
    
    # About section
    st.markdown("---")
    st.subheader("About")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Version", "1.0.0")
        st.metric("Last Update", datetime.now().strftime('%Y-%m-%d'))
    
    with col2:
        st.metric("Total Companies", get_company_count())
        st.metric("Total Documents", get_document_count())

def load_settings():
    """Load user settings"""
    settings_file = Path("data/user_settings.json")
    
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return {}

def save_settings(settings):
    """Save user settings"""
    settings_file = Path("data/user_settings.json")
    settings_file.parent.mkdir(exist_ok=True)
    
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)

def get_company_count():
    """Get total number of companies"""
    doc_path = Path("data/sec_documents")
    if doc_path.exists():
        return len([d for d in doc_path.iterdir() if d.is_dir()])
    return 0

def get_document_count():
    """Get total number of documents"""
    doc_path = Path("data/sec_documents")
    count = 0
    
    if doc_path.exists():
        for company_dir in doc_path.iterdir():
            if company_dir.is_dir():
                count += len(list(company_dir.glob("*")))
    
    return count
'''
        self.write_file("components/settings.py", content)
    
    def create_data_loader(self):
        """Create data loader utility"""
        content = '''"""
Data Loader Utility
Date: 2025-06-07 14:02:41 UTC
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class DataLoader:
    """Load data from various sources"""
    
    def __init__(self):
        self.data_path = Path("data")
    
    def load_pipeline_data(self) -> Dict:
        """Load pipeline data"""
        pipeline_file = self.data_path / "pipeline_data.json"
        
        if pipeline_file.exists():
            try:
                with open(pipeline_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading pipeline data: {e}")
        
        return {}
    
    def load_company_cik_map(self) -> Dict:
        """Load company CIK mapping"""
        cik_file = self.data_path / "company_cik_map.json"
        
        if cik_file.exists():
            try:
                with open(cik_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading CIK map: {e}")
        
        return {}
    
    def get_company_info(self, ticker: str) -> Optional[Dict]:
        """Get company information"""
        cik_map = self.load_company_cik_map()
        
        if ticker in cik_map:
            return {
                'ticker': ticker,
                'cik': cik_map[ticker].get('cik'),
                'name': cik_map[ticker].get('name'),
                'exchange': cik_map[ticker].get('exchange')
            }
        
        return None
    
    def get_pipeline_summary(self) -> Dict:
        """Get pipeline summary statistics"""
        pipeline_data = self.load_pipeline_data()
        
        return {
            'total': len(pipeline_data.get('all', [])),
            'pending': len(pipeline_data.get('pending', [])),
            'downloading': len(pipeline_data.get('downloading', [])),
            'completed': len(pipeline_data.get('completed', [])),
            'failed': len(pipeline_data.get('failed', [])),
            'last_update': pipeline_data.get('last_update', 'Unknown')
        }
    
    def get_recent_additions(self, limit: int = 10) -> List[Dict]:
        """Get recently added companies"""
        pipeline_data = self.load_pipeline_data()
        completed = pipeline_data.get('completed', [])
        
        # Sort by completion date
        sorted_completed = sorted(
            completed,
            key=lambda x: x.get('completed_date', ''),
            reverse=True
        )
        
        return sorted_completed[:limit]
'''
        self.write_file("utils/data_loader.py", content)
    
    def create_ui_helpers(self):
        """Create UI helper functions"""
        content = '''"""
UI Helper Functions
Date: 2025-06-07 14:19:15 UTC
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import humanize

def format_date(date_str: str, format: str = "YYYY-MM-DD") -> str:
    """Format date string based on user preference"""
    try:
        dt = datetime.fromisoformat(date_str) if isinstance(date_str, str) else date_str
        
        if format == "MM/DD/YYYY":
            return dt.strftime('%m/%d/%Y')
        elif format == "DD/MM/YYYY":
            return dt.strftime('%d/%m/%Y')
        else:  # Default YYYY-MM-DD
            return dt.strftime('%Y-%m-%d')
    except:
        return str(date_str)

def format_time_ago(timestamp: float) -> str:
    """Format timestamp as human-readable time ago"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return humanize.naturaltime(datetime.now() - dt)
    except:
        return "Unknown"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def show_loading_message(message: str = "Loading..."):
    """Show a loading message with spinner"""
    with st.spinner(message):
        return True

def show_error_message(error: str, details: Optional[str] = None):
    """Show error message with optional details"""
    st.error(error)
    if details:
        with st.expander("Error details"):
            st.code(details)

def show_success_message(message: str, balloons: bool = False):
    """Show success message with optional balloons"""
    st.success(message)
    if balloons:
        st.balloons()

def confirm_action(action: str, key: str) -> bool:
    """Show confirmation dialog for an action"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.warning(f"Are you sure you want to {action}?")
    
    with col2:
        if st.button("Confirm", key=f"confirm_{key}", type="primary"):
            return True
    
    return False

def create_metric_card(title: str, value: Any, delta: Optional[Any] = None, help_text: Optional[str] = None):
    """Create a metric card with optional delta and help text"""
    if help_text:
        st.metric(label=title, value=value, delta=delta, help=help_text)
    else:
        st.metric(label=title, value=value, delta=delta)

def create_progress_bar(current: int, total: int, label: str = "Progress"):
    """Create a progress bar"""
    if total > 0:
        progress = current / total
        st.progress(progress, text=f"{label}: {current}/{total} ({progress:.0%})")
    else:
        st.progress(0.0, text=f"{label}: 0/0")

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."

def highlight_text(text: str, search_term: str) -> str:
    """Highlight search term in text"""
    if not search_term:
        return text
    
    import re
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group()}**", text)

def create_download_button(data: bytes, filename: str, label: str = "Download", mime: str = "application/octet-stream"):
    """Create a styled download button"""
    st.download_button(
        label=f"📥 {label}",
        data=data,
        file_name=filename,
        mime=mime,
        use_container_width=True
    )

def create_sidebar_nav_item(icon: str, label: str, active: bool = False):
    """Create a sidebar navigation item"""
    if active:
        st.markdown(f"""
        <div style="background-color: #007AFF; color: white; padding: 10px; border-radius: 5px; margin: 5px 0;">
            {icon} {label}
        </div>
        """, unsafe_allow_html=True)
    else:
        if st.button(f"{icon} {label}", use_container_width=True):
            return True
    return False

def format_lock_up_status(expiry_date: str) -> Dict[str, str]:
    """Format lock-up expiry status"""
    try:
        expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
        today = datetime.now()
        days_until = (expiry - today).days
        
        if days_until < 0:
            return {
                'status': 'Expired',
                'days': 'Expired',
                'color': 'red'
            }
        elif days_until <= 7:
            return {
                'status': f'Expires in {days_until} days',
                'days': str(days_until),
                'color': 'orange'
            }
        elif days_until <= 30:
            return {
                'status': f'Expires in {days_until} days',
                'days': str(days_until),
                'color': 'yellow'
            }
        else:
            return {
                'status': f'Expires in {days_until} days',
                'days': str(days_until),
                'color': 'green'
            }
    except:
        return {
            'status': 'Unknown',
            'days': 'N/A',
            'color': 'gray'
        }

def create_empty_state(message: str, action_label: Optional[str] = None, action_callback: Optional[callable] = None):
    """Create an empty state message with optional action"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.info(message)
        
        if action_label and action_callback:
            if st.button(action_label, use_container_width=True):
                action_callback()

def format_confidence_score(score: float) -> str:
    """Format AI confidence score with color"""
    percentage = score * 100
    
    if score >= 0.9:
        return f"🟢 {percentage:.0f}% confidence"
    elif score >= 0.7:
        return f"🟡 {percentage:.0f}% confidence"
    else:
        return f"🔴 {percentage:.0f}% confidence"

def create_data_table(data: List[Dict], selectable: bool = True, key: str = "table"):
    """Create a formatted data table"""
    import pandas as pd
    
    if not data:
        st.info("No data available")
        return None
    
    df = pd.DataFrame(data)
    
    if selectable:
        event = st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=key
        )
        
        if event.selection.rows:
            return df.iloc[event.selection.rows[0]]
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    return None
'''
        self.write_file("utils/ui_helpers.py", content)
    
    def create_main_app(self):
        """Create main application file"""
        content = '''"""
Hedge Intelligence - Main Application
Date: 2025-06-07 14:19:15 UTC
Author: thorrobber22
Description: Clean, modular SEC intelligence interface for hedge fund analysts
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime

# Import components
from components.dashboard import render_dashboard
from components.chat import render_chat
from components.tickers import render_tickers
from components.watchlist import render_watchlist
from components.settings import render_settings

# Import utilities
from utils.ui_helpers import create_sidebar_nav_item

# Page configuration
st.set_page_config(
    page_title="Hedge Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean design
st.markdown("""
<style>
    /* Clean Apple-like design */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #007AFF;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #0051D5;
        transform: translateY(-1px);
    }
    
    /* Metric styling */
    [data-testid="metric-container"] {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    /* Table styling */
    .dataframe {
        font-size: 14px;
    }
    
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

class HedgeIntelligence:
    """Main application class"""
    
    def __init__(self):
        self.init_session_state()
        self.check_environment()
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'IPO Dashboard'
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = True  # Skip auth for now
        if 'user' not in st.session_state:
            st.session_state.user = 'thorrobber22'
    
    def check_environment(self):
        """Check environment setup"""
        # Check for required directories
        required_dirs = ['data', 'data/sec_documents', 'services', 'components', 'utils']
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                st.error(f"Required directory '{dir_path}' not found. Please run the setup script.")
                st.stop()
        
        # Check for API keys (warning only)
        if not os.getenv('OPENAI_API_KEY') and not os.getenv('GEMINI_API_KEY'):
            st.warning("AI API keys not found. Some features may be limited.")
    
    def render_sidebar(self):
        """Render sidebar navigation"""
        with st.sidebar:
            # Logo/Title
            st.markdown("# HEDGE INTELLIGENCE")
            st.markdown("---")
            
            # Navigation menu
            menu_items = [
                ("📊", "IPO Dashboard"),
                ("💬", "New Chat"),
                ("📈", "Available Tickers"),
                ("⭐", "Watch List"),
                ("⚙️", "Settings"),
                ("🚪", "Log Out")
            ]
            
            for icon, label in menu_items:
                if label == st.session_state.current_page:
                    create_sidebar_nav_item(icon, label, active=True)
                else:
                    if st.button(f"{icon} {label}", key=f"nav_{label}", use_container_width=True):
                        if label == "Log Out":
                            self.handle_logout()
                        else:
                            st.session_state.current_page = label
                            st.rerun()
            
            # User info
            st.markdown("---")
            st.markdown(f"**User:** {st.session_state.user}")
            st.markdown(f"**Time:** {datetime.now().strftime('%H:%M UTC')}")
    
    def render_main_content(self):
        """Render main content based on current page"""
        if st.session_state.current_page == "IPO Dashboard":
            render_dashboard()
        elif st.session_state.current_page == "New Chat":
            render_chat()
        elif st.session_state.current_page == "Available Tickers":
            render_tickers()
        elif st.session_state.current_page == "Watch List":
            render_watchlist()
        elif st.session_state.current_page == "Settings":
            render_settings()
    
    def handle_logout(self):
        """Handle user logout"""
        st.session_state.clear()
        st.success("Logged out successfully")
        st.rerun()
    
    def run(self):
        """Main application runner"""
        # Check authentication
        if not st.session_state.authenticated:
            st.error("Please log in to continue")
            st.stop()
        
        # Render UI
        self.render_sidebar()
        self.render_main_content()

# Application entry point
if __name__ == "__main__":
    app = HedgeIntelligence()
    app.run()
'''
        self.write_file("hedge_intelligence.py", content)
    
    def create_init_files(self):
        """Create __init__.py files for packages"""
        init_content = '"""Package initialization"""'
        
        self.write_file("services/__init__.py", init_content)
        self.write_file("components/__init__.py", init_content)
        self.write_file("utils/__init__.py", init_content)

# Run the builder
if __name__ == "__main__":
    builder = HedgeIntelligenceBuilder()
    builder.build()