#!/usr/bin/env python3
"""
Update all scrapers to use the working SEC-compliant version
Date: 2025-06-06 22:35:16 UTC
Author: thorrobber22
"""

from pathlib import Path

# Update enhanced_sec_scraper.py to use the compliant version
enhanced_content = '''#!/usr/bin/env python3
"""
Enhanced SEC Scraper - Using SEC-compliant version
"""
from sec_compliant_scraper import SECCompliantScraper as EnhancedSECDocumentScraper

__all__ = ['EnhancedSECDocumentScraper']
'''

with open("scrapers/sec/enhanced_sec_scraper.py", 'w', encoding='utf-8') as f:
    f.write(enhanced_content)

print("✅ Updated enhanced_sec_scraper.py")

# Also update working_sec_scraper.py
working_content = '''#!/usr/bin/env python3
"""
Working SEC Scraper - Using SEC-compliant version
"""
from sec_compliant_scraper import SECCompliantScraper as WorkingSECDocumentScraper

__all__ = ['WorkingSECDocumentScraper']
'''

with open("scrapers/sec/working_sec_scraper.py", 'w', encoding='utf-8') as f:
    f.write(working_content)

print("✅ Updated working_sec_scraper.py")
print("\n🚀 All scrapers now use the SEC-compliant version that works!")