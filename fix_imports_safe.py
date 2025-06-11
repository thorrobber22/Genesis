#!/usr/bin/env python3
"""
Fix import errors with proper encoding
Date: 2025-06-07 13:50:14 UTC
"""

import os

# Fix the import in pipeline_manager.py with UTF-8 encoding
pipeline_file = "scrapers/sec/pipeline_manager.py"

if os.path.exists(pipeline_file):
    with open(pipeline_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the incorrect import
    content = content.replace(
        'from iposcoop_scraper import IPOScoopScraper',
        'from scrapers.sec.iposcoop_scraper import IPOScoopScraper'
    )
    
    with open(pipeline_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Fixed import in pipeline_manager.py")