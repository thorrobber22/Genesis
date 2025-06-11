#!/usr/bin/env python3
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
    print("\n1️⃣ Scanning for new IPOs...")
    new_count = await manager.scan_new_ipos()
    print(f"   Found {new_count} new IPOs")
    
    # Test 2: Get summary
    print("\n2️⃣ Getting admin summary...")
    summary = manager.get_admin_summary()
    print(f"   Pending: {summary['pending']}")
    print(f"   Active: {summary['active']}")
    print(f"   Needs Attention: {len(summary['needs_attention'])}")
    
    # Test 3: Process one IPO (if any pending)
    if summary['pending'] > 0:
        print("\n3️⃣ Processing pending IPOs...")
        await manager.process_pending_ipos()

if __name__ == "__main__":
    asyncio.run(test_pipeline())
