"""
Data Extraction Component with Citations
Created: 2025-06-07 21:50:17 UTC
"""
import re
from typing import Dict, List

class DataExtractor:
    def __init__(self):
        self.extraction_patterns = {
            'revenue': [
                r'revenues?\s*[:=]\s*\$?([\d,]+\.?\d*)\s*(million|billion|M|B)',
                r'total\s+revenues?\s+of\s+\$?([\d,]+\.?\d*)',
            ],
            'net_income': [
                r'net\s+income\s*[:=]\s*\$?([\d,]+\.?\d*)\s*(million|billion|M|B)',
                r'net\s+earnings?\s+of\s+\$?([\d,]+\.?\d*)',
            ],
            'employees': [
                r'([\d,]+)\s+employees',
                r'employee\s+count\s*[:=]\s*([\d,]+)',
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
