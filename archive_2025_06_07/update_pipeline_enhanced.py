#!/usr/bin/env python3
"""
Update pipeline manager to use enhanced scraper
Date: 2025-06-06 21:34:49 UTC
Author: thorrobber22
"""

from pathlib import Path

# Read current pipeline manager
pipeline_file = Path("scrapers/sec/pipeline_manager.py")

with open(pipeline_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the import
updated_content = content.replace(
    "from sec_scraper import SECDocumentScraper",
    "from enhanced_sec_scraper import EnhancedSECDocumentScraper as SECDocumentScraper"
)

# Save updated version
with open(pipeline_file, 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("✅ Updated pipeline_manager.py to use enhanced scraper")

# Also copy the enhanced scraper to the right location
import shutil

# Copy enhanced scraper
shutil.copy("enhanced_sec_scraper.py", "scrapers/sec/enhanced_sec_scraper.py")
print("✅ Copied enhanced_sec_scraper.py to scrapers/sec/")

# Update the sec_scraper.py to be a wrapper
wrapper_content = '''#!/usr/bin/env python3
"""
SEC Scraper - Wrapper for enhanced version
"""
from enhanced_sec_scraper import EnhancedSECDocumentScraper as SECDocumentScraper

__all__ = ['SECDocumentScraper']
'''

with open("scrapers/sec/sec_scraper.py", 'w', encoding='utf-8') as f:
    f.write(wrapper_content)

print("✅ Updated sec_scraper.py as wrapper")
print("\n🚀 Enhanced scraper system ready!")
print("\nNow run: streamlit run admin_sec.py")