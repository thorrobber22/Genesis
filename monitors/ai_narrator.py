"""
AI Narrator - Explain system status in plain English
"""

from typing import Dict

class AINarrator:
    def get_guidance(self, status: Dict) -> str:
        """Generate plain English guidance based on system status"""
        
        ipo_progress = status.get('ipo_progress', 0)
        s1_progress = status.get('s1_progress', 0)
        context_progress = status.get('context_progress', 0)
        ready = status.get('ready_for_testing', False)
        eta = status.get('eta_minutes', 10)
        
        guidance = "System Analysis:\n\n"
        
        # IPO Calendar status
        if ipo_progress == 100:
            guidance += "1. IPO Calendar: Fully loaded with this week's offerings\n"
        else:
            guidance += "1. IPO Calendar: Currently fetching data from IPOScoop...\n"
        
        # Document status
        if s1_progress > 0:
            guidance += f"2. Document Fetching: {int(s1_progress)}% complete - downloading S-1 filings\n"
        else:
            guidance += "2. Document Fetching: Waiting for IPO calendar to complete\n"
        
        # Context extraction
        if context_progress > 0:
            guidance += f"3. Context Building: {int(context_progress)}% - extracting key data\n"
        else:
            guidance += "3. Context Building: Pending document downloads\n"
        
        guidance += "\nRECOMMENDED ACTIONS:\n"
        
        if ready:
            guidance += "- System ready for testing! Try asking about specific IPOs\n"
            guidance += "- IPO Calendar view has complete data\n"
            guidance += "- Chat can answer questions about downloaded S-1s\n"
        else:
            guidance += f"- Wait approximately {eta} minutes for initial data load\n"
            guidance += "- You can browse IPO Calendar once it loads\n"
            guidance += "- Document analysis features require S-1 downloads\n"
        
        # Any issues
        if s1_progress < 100 and ipo_progress == 100:
            guidance += "\nNOTE: S-1 downloads depend on SEC server response times"
        
        return guidance
