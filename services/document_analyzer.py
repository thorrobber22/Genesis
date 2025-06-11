#!/usr/bin/env python3
"""
Real Analysis Component
Extracts actual financial data and insights
"""

import re
from pathlib import Path
import json
from typing import Dict, List

class DocumentAnalyzer:
    def __init__(self):
        self.patterns = {
            'revenue': r'(?:revenue|net sales).*?\$([\d,]+(?:\.\d+)?)[\s]?(?:million|billion)?',
            'income': r'(?:net income|net earnings).*?\$([\d,]+(?:\.\d+)?)[\s]?(?:million|billion)?',
            'eps': r'(?:earnings per share|eps).*?\$([\d.]+)',
            'assets': r'(?:total assets).*?\$([\d,]+(?:\.\d+)?)[\s]?(?:million|billion)?'
        }
        
    def extract_financials(self, content: str) -> Dict:
        """Extract real financial numbers from document"""
        
        financials = {}
        
        for metric, pattern in self.patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Clean and convert
                value = matches[0].replace(',', '')
                try:
                    financials[metric] = float(value)
                except:
                    financials[metric] = value
                    
        return financials
        
    def extract_risk_factors(self, content: str) -> List[str]:
        """Extract actual risk factors"""
        
        risks = []
        
        # Find risk factors section
        risk_section = re.search(r'risk factors(.*?)(?:item \d|$)', content, re.IGNORECASE | re.DOTALL)
        
        if risk_section:
            # Extract bullet points or numbered items
            risk_text = risk_section.group(1)
            
            # Find patterns like "• text" or "- text" or "1. text"
            risk_patterns = re.findall(r'(?:[•·∙▪-]|\d+\.)\s*([^\n]+)', risk_text)
            
            for risk in risk_patterns[:10]:  # Top 10
                cleaned = risk.strip()
                if len(cleaned) > 20 and len(cleaned) < 200:
                    risks.append(cleaned)
                    
        return risks
        
    def extract_tables(self, content: str) -> List[Dict]:
        """Extract financial tables"""
        
        tables = []
        
        # Find HTML tables
        table_pattern = r'<table[^>]*>(.*?)</table>'
        table_matches = re.findall(table_pattern, content, re.IGNORECASE | re.DOTALL)
        
        for table_html in table_matches[:5]:  # First 5 tables
            # Extract rows
            rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.IGNORECASE | re.DOTALL)
            
            if rows:
                table_data = []
                for row in rows:
                    cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.IGNORECASE)
                    cleaned_cells = [re.sub(r'<[^>]+>', '', cell).strip() for cell in cells]
                    if any(cleaned_cells):
                        table_data.append(cleaned_cells)
                        
                if table_data:
                    tables.append({
                        'rows': len(table_data),
                        'cols': len(table_data[0]) if table_data else 0,
                        'data': table_data[:10]  # First 10 rows
                    })
                    
        return tables
        
    def generate_insights(self, company: str, document: str, content: str) -> Dict:
        """Generate real insights from document"""
        
        # Extract components
        financials = self.extract_financials(content)
        risks = self.extract_risk_factors(content)
        tables = self.extract_tables(content)
        
        # Generate insights
        insights = {
            'company': company,
            'document': document,
            'financials': financials,
            'risk_factors': risks[:5],  # Top 5
            'tables_found': len(tables),
            'key_metrics': {},
            'summary': ''
        }
        
        # Calculate key metrics
        if 'revenue' in financials and 'income' in financials:
            insights['key_metrics']['profit_margin'] = (financials['income'] / financials['revenue']) * 100
            
        # Generate summary
        if financials:
            insights['summary'] = f"Found {len(financials)} financial metrics. "
            if 'revenue' in financials:
                insights['summary'] += f"Revenue: ${financials['revenue']:,.0f}. "
            if risks:
                insights['summary'] += f"Identified {len(risks)} risk factors."
                
        return insights
