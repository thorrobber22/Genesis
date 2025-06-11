#!/usr/bin/env python3
"""
Create report generator for professional PDF exports
Date: 2025-06-06 17:25:20 UTC
Author: thorrobber22
"""

from pathlib import Path

report_generator = '''#!/usr/bin/env python3
"""
Professional Report Generator
Generates LaTeX-style PDFs with full citations
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import json
from pathlib import Path

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.create_custom_styles()
    
    def create_custom_styles(self):
        """Create professional styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='Citation',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#7f8c8d'),
            leftIndent=20
        ))
    
    def generate_ipo_report(self, ticker_data, output_path):
        """Generate comprehensive IPO report"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Title Page
        elements.append(Paragraph(f"IPO Analysis Report", self.styles['CustomTitle']))
        elements.append(Paragraph(f"{ticker_data['company_name']}", self.styles['CustomTitle']))
        elements.append(Paragraph(f"Ticker: {ticker_data['ticker']}", self.styles['Heading2']))
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        elements.append(PageBreak())
        
        # Executive Summary
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Paragraph(ticker_data.get('summary', 'No summary available'), self.styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Float Calculation
        if 'float_calculation' in ticker_data:
            elements.append(Paragraph("Float Calculation", self.styles['SectionHeader']))
            
            # Create calculation table
            calc_data = [
                ['Component', 'Shares', 'Source'],
                ['Shares Offered', f"{ticker_data['float_calculation']['shares_offered']:,}", 'S-1 Filing'],
                ['Insider Shares', f"-{ticker_data['float_calculation']['insider_shares']:,}", 'Lock-up Agreement'],
                ['Employee RSUs', f"-{ticker_data['float_calculation']['employee_rsus']:,}", '8-K Filing'],
                ['Public Float', f"{ticker_data['float_calculation']['public_float']:,}", 'Calculated'],
            ]
            
            table = Table(calc_data, colWidths=[3*inch, 1.5*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.yellow),
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Lock-up Analysis
        if 'lockup_analysis' in ticker_data:
            elements.append(Paragraph("Lock-up Expiration Analysis", self.styles['SectionHeader']))
            
            lockup = ticker_data['lockup_analysis']
            elements.append(Paragraph(f"IPO Date: {lockup['ipo_date']}", self.styles['Normal']))
            elements.append(Paragraph(f"Lock-up Period: {lockup['period']} days", self.styles['Normal']))
            elements.append(Paragraph(f"Expiration Date: {lockup['expiration_date']}", self.styles['Normal']))
            elements.append(Paragraph(f"Shares Subject to Lock-up: {lockup['shares_locked']:,}", self.styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Add citation
            elements.append(Paragraph("Source: Lock-up Agreement filed with SEC", self.styles['Citation']))
            elements.append(Spacer(1, 0.2*inch))
        
        # Risk Factors
        if 'risk_factors' in ticker_data:
            elements.append(Paragraph("Key Risk Factors", self.styles['SectionHeader']))
            
            for i, risk in enumerate(ticker_data['risk_factors'][:5], 1):
                elements.append(Paragraph(f"{i}. {risk}", self.styles['Normal']))
            
            elements.append(Spacer(1, 0.1*inch))
            elements.append(Paragraph("Source: S-1 Registration Statement", self.styles['Citation']))
        
        # Build PDF
        doc.build(elements)
        return output_path
    
    def generate_daily_summary(self, summary_data, output_path):
        """Generate daily summary report for admin"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        
        # Header
        elements.append(Paragraph("Daily IPO Summary", self.styles['CustomTitle']))
        elements.append(Paragraph(f"{datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))
        
        # Statistics
        elements.append(Paragraph("Overview", self.styles['SectionHeader']))
        stats_data = [
            ['Metric', 'Count'],
            ['Active IPOs', str(summary_data['active_ipos'])],
            ['Documents Processed', str(summary_data['documents_processed'])],
            ['New Filings', str(summary_data['new_filings'])],
            ['User Queries', str(summary_data['user_queries'])],
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(stats_table)
        
        # Build
        doc.build(elements)
        return output_path

# Example usage
if __name__ == "__main__":
    generator = ReportGenerator()
    
    # Sample IPO data
    sample_data = {
        'ticker': 'RDDT',
        'company_name': 'Reddit, Inc.',
        'summary': 'Social media platform going public...',
        'float_calculation': {
            'shares_offered': 15900000,
            'insider_shares': 10000000,
            'employee_rsus': 2000000,
            'public_float': 3900000
        },
        'lockup_analysis': {
            'ipo_date': '2024-03-21',
            'period': 180,
            'expiration_date': '2024-09-17',
            'shares_locked': 120000000
        },
        'risk_factors': [
            'Competition from other social platforms',
            'Regulatory scrutiny',
            'User growth deceleration',
            'Monetization challenges',
            'Content moderation costs'
        ]
    }
    
    # Generate report
    output = generator.generate_ipo_report(sample_data, 'RDDT_analysis.pdf')
    print(f"Generated: {output}")
'''

# Save report generator
report_path = Path("core/report_generator.py")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_generator)

print("✅ Created core/report_generator.py")