#!/usr/bin/env python3
"""
Fix pipeline manager imports
Date: 2025-06-06 17:36:32 UTC
Author: thorrobber22
"""

import sys
from pathlib import Path

# Go back to the scrapers/sec directory
sec_dir = Path(__file__).parent if Path(__file__).parent.name == "sec" else Path("scrapers/sec")

# Fix the pipeline_manager.py
pipeline_file = sec_dir / "pipeline_manager.py"

if pipeline_file.exists():
    with open(pipeline_file, 'r') as f:
        content = f.read()
    
    # Replace the imports to work from any directory
    fixed_content = content.replace(
        "from scrapers.sec.iposcoop_scraper import IPOScoopScraper",
        "from iposcoop_scraper import IPOScoopScraper"
    ).replace(
        "from scrapers.sec.cik_resolver import CIKResolver",
        "from cik_resolver import CIKResolver"
    ).replace(
        "from scrapers.sec.sec_scraper import SECDocumentScraper",
        "from sec_scraper import SECDocumentScraper"
    )
    
    # Save the fixed version
    with open(pipeline_file, 'w') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed imports in {pipeline_file}")
else:
    print("❌ Could not find pipeline_manager.py")

# Also create a test script that can be run from the main directory
test_script = '''#!/usr/bin/env python3
"""
Test SEC pipeline from main directory
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import
from scrapers.sec.pipeline_manager import IPOPipelineManager
import asyncio

async def test_pipeline():
    """Test the pipeline"""
    print("🧪 Testing SEC Pipeline...")
    
    manager = IPOPipelineManager()
    
    # Test 1: Scan for IPOs
    print("\\n1️⃣ Scanning for new IPOs...")
    new_count = await manager.scan_new_ipos()
    print(f"   Found {new_count} new IPOs")
    
    # Test 2: Get summary
    print("\\n2️⃣ Getting admin summary...")
    summary = manager.get_admin_summary()
    print(f"   Pending: {summary['pending']}")
    print(f"   Active: {summary['active']}")
    print(f"   Needs Attention: {len(summary['needs_attention'])}")
    
    # Test 3: Process one IPO (if any pending)
    if summary['pending'] > 0:
        print("\\n3️⃣ Processing pending IPOs...")
        await manager.process_pending_ipos()

if __name__ == "__main__":
    asyncio.run(test_pipeline())
'''

# Save test script in main directory
test_file = Path("test_sec_pipeline.py")
with open(test_file, 'w') as f:
    f.write(test_script)

print(f"✅ Created {test_file}")
print("\nRun from main directory: python test_sec_pipeline.py")