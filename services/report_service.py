"""
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
