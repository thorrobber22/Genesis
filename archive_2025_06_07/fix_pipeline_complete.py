#!/usr/bin/env python3
"""
Complete fix for pipeline manager
Date: 2025-06-06 22:02:39 UTC
Author: thorrobber22
"""

from pathlib import Path

# Create a completely new pipeline manager with enhanced scraper
pipeline_content = '''#!/usr/bin/env python3
"""
IPO Pipeline Manager - Orchestrates the complete flow
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
import sys

# Handle imports from different directories
try:
    # When run from main directory
    from scrapers.sec.iposcoop_scraper import IPOScoopScraper
    from scrapers.sec.cik_resolver import CIKResolver
    from scrapers.sec.enhanced_sec_scraper import EnhancedSECDocumentScraper
except ImportError:
    # When run from scrapers/sec directory
    from iposcoop_scraper import IPOScoopScraper
    from cik_resolver import CIKResolver
    from enhanced_sec_scraper import EnhancedSECDocumentScraper

class IPOPipelineManager:
    def __init__(self):
        self.ipo_scraper = IPOScoopScraper()
        self.cik_resolver = CIKResolver()
        self.sec_scraper = EnhancedSECDocumentScraper()
        
        # Data directory
        self.data_dir = Path("data/ipo_pipeline")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline files
        self.pending_file = self.data_dir / "pending.json"
        self.active_file = self.data_dir / "active.json"
        self.completed_file = self.data_dir / "completed.json"
        
        # Initialize files if they don't exist
        for file_path in [self.pending_file, self.active_file, self.completed_file]:
            if not file_path.exists():
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def load_pipeline_data(self) -> dict:
        """Load current pipeline state"""
        try:
            with open(self.pending_file, 'r') as f:
                pending = json.load(f)
            with open(self.active_file, 'r') as f:
                active = json.load(f)
            with open(self.completed_file, 'r') as f:
                completed = json.load(f)
            
            return {
                'pending': pending,
                'active': active,
                'completed': completed
            }
        except Exception as e:
            print(f"Error loading pipeline data: {e}")
            return {'pending': [], 'active': [], 'completed': []}
    
    def save_pipeline_data(self, data: dict):
        """Save pipeline state"""
        try:
            with open(self.pending_file, 'w') as f:
                json.dump(data.get('pending', []), f, indent=2)
            with open(self.active_file, 'w') as f:
                json.dump(data.get('active', []), f, indent=2)
            with open(self.completed_file, 'w') as f:
                json.dump(data.get('completed', []), f, indent=2)
        except Exception as e:
            print(f"Error saving pipeline data: {e}")
    
    async def scan_new_ipos(self) -> int:
        """Scan for new IPOs from IPOScoop"""
        print("📊 Scanning IPOScoop for new IPOs...")
        
        try:
            # Get current IPOs from IPOScoop
            new_ipos = await self.ipo_scraper.scrape_calendar()
            
            # Load current pipeline
            data = self.load_pipeline_data()
            
            # Check which ones are new
            existing_tickers = set()
            for ipo_list in [data['pending'], data['active'], data['completed']]:
                for ipo in ipo_list:
                    existing_tickers.add(ipo['ticker'])
            
            # Add new ones
            added_count = 0
            for ipo in new_ipos:
                if ipo['ticker'] not in existing_tickers:
                    print(f"✅ New IPO: {ipo['ticker']} - {ipo['company_name']}")
                    ipo['status'] = 'pending_cik'
                    ipo['added_date'] = datetime.now().isoformat()
                    data['pending'].append(ipo)
                    added_count += 1
            
            # Save updated pipeline
            self.save_pipeline_data(data)
            
            print(f"📊 Found {added_count} new IPOs")
            return added_count
            
        except Exception as e:
            print(f"❌ Error scanning IPOs: {e}")
            return 0
    
    async def process_pending_ipos(self):
        """Process all pending IPOs"""
        data = self.load_pipeline_data()
        pending = data['pending'][:]  # Copy to avoid modification during iteration
        
        print(f"🔄 Processing {len(pending)} pending IPOs...")
        
        for ipo in pending:
            print(f"\\n📍 Processing {ipo['ticker']} - {ipo['company_name']}")
            
            try:
                # Step 1: Resolve CIK if needed
                if 'cik' not in ipo or not ipo.get('cik'):
                    cik_result = await self.cik_resolver.get_cik(
                        ipo['company_name'], 
                        ipo['ticker']
                    )
                    
                    if cik_result:
                        ipo['cik'] = cik_result['cik']
                        ipo['cik_confidence'] = cik_result['confidence']
                        ipo['sec_name'] = cik_result['name']
                        print(f"  ✅ Found CIK: {cik_result['cik']} (confidence: {cik_result['confidence']}%)")
                    else:
                        print(f"  ❌ Could not resolve CIK")
                        ipo['status'] = 'needs_manual_cik'
                        continue
                
                # Step 2: Download documents using ENHANCED scraper
                if 'cik' in ipo:
                    result = await self.sec_scraper.scan_and_download_everything(
                        ipo['ticker'],
                        ipo['cik']
                    )
                    
                    if result['success']:
                        # Update IPO with document info
                        ipo['documents_count'] = result['total_files']
                        ipo['filings_count'] = result['filings_downloaded']
                        ipo['last_scan'] = datetime.now().isoformat()
                        ipo['status'] = 'active'
                        
                        # Move from pending to active
                        data['pending'].remove(ipo)
                        data['active'].append(ipo)
                        
                        print(f"  ✅ Downloaded {result['total_files']} files")
                    else:
                        print(f"  ❌ Download failed: {result.get('error', 'Unknown error')}")
                        ipo['status'] = 'download_failed'
                        ipo['error'] = result.get('error', 'Unknown error')
                
            except Exception as e:
                print(f"  ❌ Error processing {ipo['ticker']}: {e}")
                ipo['status'] = 'error'
                ipo['error'] = str(e)
        
        # Save updated pipeline
        self.save_pipeline_data(data)
    
    def get_admin_summary(self) -> dict:
        """Get summary for admin dashboard"""
        data = self.load_pipeline_data()
        
        # Identify issues
        needs_attention = []
        
        for ipo in data['pending']:
            if ipo.get('status') == 'needs_manual_cik':
                needs_attention.append({
                    'ticker': ipo['ticker'],
                    'issue': 'Could not resolve CIK automatically',
                    'action': 'Manual CIK lookup required'
                })
            elif ipo.get('status') == 'download_failed':
                needs_attention.append({
                    'ticker': ipo['ticker'],
                    'issue': f"Download failed: {ipo.get('error', 'Unknown')}",
                    'action': 'Check SEC website manually'
                })
        
        return {
            'pending': len(data['pending']),
            'active': len(data['active']),
            'completed': len(data['completed']),
            'needs_attention': needs_attention,
            'recent_activity': []  # Could add recent processing log
        }
'''

# Save the new pipeline manager
pipeline_file = Path("scrapers/sec/pipeline_manager.py")
with open(pipeline_file, 'w', encoding='utf-8') as f:
    f.write(pipeline_content)

print("✅ Created new pipeline_manager.py with enhanced scraper integration")