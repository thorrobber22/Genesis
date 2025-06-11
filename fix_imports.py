#!/usr/bin/env python3
"""
Fix import errors in pipeline_manager.py
Date: 2025-06-07 13:44:34 UTC
"""

import os

# Fix the import in pipeline_manager.py
pipeline_file = "scrapers/sec/pipeline_manager.py"

if os.path.exists(pipeline_file):
    with open(pipeline_file, 'r') as f:
        content = f.read()
    
    # Replace the incorrect import
    content = content.replace(
        'from iposcoop_scraper import IPOScoopScraper',
        'from scrapers.sec.iposcoop_scraper import IPOScoopScraper'
    )
    
    # Also check for any other relative imports that might be wrong
    content = content.replace(
        'from .iposcoop_scraper import IPOScoopScraper',
        'from scrapers.sec.iposcoop_scraper import IPOScoopScraper'
    )
    
    with open(pipeline_file, 'w') as f:
        f.write(content)
    
    print("Fixed import in pipeline_manager.py")

# Also update hedge_intelligence.py to handle missing services gracefully
hedge_file = "hedge_intelligence.py"

if os.path.exists(hedge_file):
    with open(hedge_file, 'r') as f:
        lines = f.readlines()
    
    # Find the import section and wrap in try-except
    new_lines = []
    for i, line in enumerate(lines):
        if line.strip().startswith('from scrapers.sec.pipeline_manager'):
            new_lines.append('try:\n')
            new_lines.append('    ' + line)
            new_lines.append('except ImportError:\n')
            new_lines.append('    PipelineManager = None\n')
        elif line.strip().startswith('from processors.document_processor'):
            new_lines.append('try:\n')
            new_lines.append('    ' + line)
            new_lines.append('except ImportError:\n')
            new_lines.append('    SECDocumentProcessor = None\n')
        else:
            new_lines.append(line)
    
    with open(hedge_file, 'w') as f:
        f.writelines(new_lines)
    
    print("Updated hedge_intelligence.py with error handling")

print("Import fixes complete!")