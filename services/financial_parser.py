"""
services/financial_parser.py - Extract financial data from S-1 filings
Date: 2025-06-11 21:40:33 UTC
User: thorrobber22
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd

class FinancialParser:
    def __init__(self):
        self.financial_patterns = {
            'revenue': [
                r'total\s+(?:net\s+)?revenue[s]?\s*[:$]\s*([\d,]+)',
                r'revenue[s]?\s*[:$]\s*\$?([\d,]+(?:\.\d+)?)\s*(?:million|thousand)?',
                r'net\s+revenue[s]?\s*[:$]\s*\$?([\d,]+)',
                r'total\s+revenue[s]?\s+were\s+\$?([\d,]+)'
            ],
            'net_loss': [
                r'net\s+loss\s*[:$]\s*\$?([\d,]+)',
                r'net\s+loss\s+of\s+\$?([\d,]+)',
                r'loss\s+from\s+operations\s*[:$]\s*\$?([\d,]+)',
                r'operating\s+loss\s*[:$]\s*\$?([\d,]+)'
            ],
            'cash': [
                r'cash\s+and\s+cash\s+equivalents\s*[:$]\s*\$?([\d,]+)',
                r'cash\s*[:$]\s*\$?([\d,]+(?:\.\d+)?)\s*(?:million|thousand)?',
                r'total\s+cash\s*[:$]\s*\$?([\d,]+)'
            ],
            'shares_outstanding': [
                r'([\d,]+)\s+shares\s+outstanding',
                r'outstanding\s+shares\s*[:]\s*([\d,]+)',
                r'common\s+stock\s+outstanding\s*[:]\s*([\d,]+)'
            ]
        }
        
        self.multipliers = {
            'million': 1_000_000,
            'thousand': 1_000,
            'billion': 1_000_000_000
        }
    
    def parse_s1_financials(self, ticker: str) -> Dict:
        """Parse financial data from S-1 filing"""
        financials = {
            'ticker': ticker,
            'revenue': [],
            'net_loss': [],
            'cash_position': None,
            'burn_rate': None,
            'runway_months': None,
            'shares_outstanding': None,
            'valuation_metrics': {},
            'parsed_at': datetime.now().isoformat()
        }
        
        # Find S-1 documents
        s1_path = self._find_s1_document(ticker)
        if not s1_path:
            return financials
        
        # Read and parse document
        try:
            with open(s1_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract financial data
            financials['revenue'] = self._extract_revenue(content)
            financials['net_loss'] = self._extract_net_loss(content)
            financials['cash_position'] = self._extract_cash(content)
            financials['shares_outstanding'] = self._extract_shares(content)
            
            # Calculate metrics
            if financials['net_loss'] and financials['cash_position']:
                financials['burn_rate'] = self._calculate_burn_rate(financials['net_loss'])
                financials['runway_months'] = self._calculate_runway(
                    financials['cash_position'], 
                    financials['burn_rate']
                )
            
            # Calculate valuation metrics
            financials['valuation_metrics'] = self._calculate_valuation_metrics(financials)
            
        except Exception as e:
            print(f"Error parsing {ticker}: {str(e)}")
        
        return financials
    
    def _find_s1_document(self, ticker: str) -> Optional[Path]:
        """Find S-1 document for a company"""
        # Check processed documents first
        processed_dir = Path('data/processed')
        if processed_dir.exists():
            for s1_file in processed_dir.glob(f'{ticker}_S-1*.json'):
                return s1_file
        
        # Check SEC documents
        sec_dir = Path(f'data/sec_documents/{ticker}')
        if sec_dir.exists():
            for s1_file in sec_dir.glob('*S-1*.html'):
                return s1_file
        
        return None
    
    def _extract_revenue(self, content: str) -> List[Dict]:
        """Extract revenue figures"""
        revenues = []
        
        for pattern in self.financial_patterns['revenue']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                value = self._parse_number(match.group(1))
                if value:
                    # Check for multiplier
                    context = content[max(0, match.start()-50):match.end()+50]
                    multiplier = self._get_multiplier(context)
                    revenues.append({
                        'value': value * multiplier,
                        'context': context.strip()
                    })
        
        return revenues
    
    def _extract_net_loss(self, content: str) -> List[Dict]:
        """Extract net loss figures"""
        losses = []
        
        for pattern in self.financial_patterns['net_loss']:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                value = self._parse_number(match.group(1))
                if value:
                    context = content[max(0, match.start()-50):match.end()+50]
                    multiplier = self._get_multiplier(context)
                    losses.append({
                        'value': value * multiplier,
                        'context': context.strip()
                    })
        
        return losses
    
    def _extract_cash(self, content: str) -> Optional[float]:
        """Extract cash position"""
        for pattern in self.financial_patterns['cash']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = self._parse_number(match.group(1))
                if value:
                    context = content[max(0, match.start()-50):match.end()+50]
                    multiplier = self._get_multiplier(context)
                    return value * multiplier
        
        return None
    
    def _extract_shares(self, content: str) -> Optional[float]:
        """Extract shares outstanding"""
        for pattern in self.financial_patterns['shares_outstanding']:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = self._parse_number(match.group(1))
                if value:
                    return value
        
        return None
    
    def _parse_number(self, text: str) -> Optional[float]:
        """Parse number from text"""
        try:
            # Remove commas and convert to float
            clean_text = text.replace(',', '')
            return float(clean_text)
        except:
            return None
    
    def _get_multiplier(self, context: str) -> float:
        """Get multiplier from context"""
        context_lower = context.lower()
        for unit, multiplier in self.multipliers.items():
            if unit in context_lower:
                return multiplier
        return 1
    
    def _calculate_burn_rate(self, losses: List[Dict]) -> Optional[float]:
        """Calculate monthly burn rate"""
        if not losses:
            return None
        
        # Use most recent loss
        recent_loss = max(losses, key=lambda x: x['value'])
        # Assume annual figure, convert to monthly
        return recent_loss['value'] / 12
    
    def _calculate_runway(self, cash: float, burn_rate: float) -> Optional[int]:
        """Calculate runway in months"""
        if not burn_rate or burn_rate <= 0:
            return None
        
        return int(cash / burn_rate)
    
    def _calculate_valuation_metrics(self, financials: Dict) -> Dict:
        """Calculate valuation metrics"""
        metrics = {}
        
        # Revenue multiple (if we have revenue)
        if financials['revenue']:
            latest_revenue = max(financials['revenue'], key=lambda x: x['value'])['value']
            if latest_revenue > 0:
                metrics['revenue_multiple'] = 'TBD'  # Would need valuation
        
        # Cash burn metrics
        if financials['burn_rate']:
            metrics['monthly_burn'] = f"${financials['burn_rate']:,.0f}"
            
        if financials['runway_months']:
            metrics['runway'] = f"{financials['runway_months']} months"
        
        return metrics
    
    def generate_financial_summary(self, ticker: str) -> str:
        """Generate financial summary text"""
        financials = self.parse_s1_financials(ticker)
        
        summary = f"**Financial Summary for {ticker}**\n\n"
        
        if financials['revenue']:
            latest_revenue = max(financials['revenue'], key=lambda x: x['value'])
            summary += f"📈 **Revenue**: ${latest_revenue['value']:,.0f}\n"
        
        if financials['net_loss']:
            latest_loss = max(financials['net_loss'], key=lambda x: x['value'])
            summary += f"📉 **Net Loss**: ${latest_loss['value']:,.0f}\n"
        
        if financials['cash_position']:
            summary += f"💰 **Cash Position**: ${financials['cash_position']:,.0f}\n"
        
        if financials['burn_rate']:
            summary += f"🔥 **Monthly Burn Rate**: ${financials['burn_rate']:,.0f}\n"
        
        if financials['runway_months']:
            summary += f"⏰ **Runway**: {financials['runway_months']} months\n"
        
        return summary
