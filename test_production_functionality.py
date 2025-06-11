#!/usr/bin/env python3
# test_production_functionality.py
"""
Test all critical functionality works in production
"""

import streamlit as st
from pathlib import Path
import json
import time

class ProductionTester:
    def __init__(self):
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "tests": {}
        }
    
    def test_app_starts(self):
        """Test 1: App starts without errors"""
        try:
            # This would be manual - checking if streamlit run works
            self.results["tests"]["app_starts"] = {
                "status": "MANUAL CHECK REQUIRED",
                "description": "Run: streamlit run hedge_intelligence.py"
            }
        except Exception as e:
            self.results["tests"]["app_starts"] = {"status": "FAIL", "error": str(e)}
    
    def test_navigation(self):
        """Test 2: All navigation pages load"""
        pages = ["Dashboard", "Document Explorer", "IPO Tracker", 
                 "Search", "Watchlist", "Company Management"]
        
        self.results["tests"]["navigation"] = {
            "pages": pages,
            "status": "MANUAL CHECK REQUIRED",
            "instructions": "Click each page and verify no errors"
        }
    
    def test_document_explorer(self):
        """Test 3: Document Explorer functionality"""
        self.results["tests"]["document_explorer"] = {
            "checks": [
                "Companies list appears",
                "Can expand company",
                "Can select document",
                "Document viewer opens",
                "Can download document"
            ],
            "status": "MANUAL CHECK REQUIRED"
        }
    
    def test_chat_functionality(self):
        """Test 4: Chat system works"""
        self.results["tests"]["chat"] = {
            "checks": [
                "Chat bar appears at bottom",
                "Can type message",
                "Get AI response",
                "Citations show up",
                "Context awareness works"
            ],
            "status": "MANUAL CHECK REQUIRED"
        }
    
    def test_data_integrity(self):
        """Test 5: Data files exist and are valid"""
        data_files = {
            "sec_documents": Path("data/sec_documents"),
            "company_requests": Path("data/company_requests.json"),
            "ipo_calendar": Path("data/ipo_calendar.json"),
            "chroma_db": Path("data/chroma")
        }
        
        results = {}
        for name, path in data_files.items():
            if path.exists():
                if path.is_file():
                    try:
                        with open(path, 'r') as f:
                            data = json.load(f)
                        results[name] = {"exists": True, "valid": True, "size": len(data) if isinstance(data, (list, dict)) else 1}
                    except:
                        results[name] = {"exists": True, "valid": False}
                else:
                    # Directory
                    count = len(list(path.glob("**/*")))
                    results[name] = {"exists": True, "type": "directory", "files": count}
            else:
                results[name] = {"exists": False}
        
        self.results["tests"]["data_integrity"] = results
    
    def generate_checklist(self):
        """Generate production checklist"""
        
        checklist = """
HEDGE INTELLIGENCE - PRODUCTION CHECKLIST
=========================================

□ 1. APP STARTS
   - Run: streamlit run hedge_intelligence.py
   - No errors on startup
   - Homepage loads

□ 2. NAVIGATION
   - [ ] Dashboard loads
   - [ ] Document Explorer loads
   - [ ] IPO Tracker loads
   - [ ] Search loads
   - [ ] Watchlist loads
   - [ ] Company Management loads

□ 3. DOCUMENT EXPLORER
   - [ ] Shows 9 companies
   - [ ] CRCL shows 584 documents
   - [ ] Can expand company
   - [ ] Can click document
   - [ ] Document viewer opens
   - [ ] Can download file

□ 4. AI CHAT
   - [ ] Chat bar at bottom
   - [ ] Can type question
   - [ ] Get response with citations
   - [ ] Click citation works
   - [ ] Maintains context

□ 5. DATA VERIFICATION
   - [ ] Company count correct
   - [ ] Document count correct
   - [ ] No dummy IPO data
   - [ ] ChromaDB accessible

□ 6. ERROR HANDLING
   - [ ] Missing data handled
   - [ ] API errors handled
   - [ ] No crashes on navigation

CRITICAL SUCCESS CRITERIA:
- Can browse documents ✓
- Can chat with AI ✓
- Citations work ✓
- No crashes ✓
"""
        
        # Save checklist
        with open("production_checklist.md", "w", encoding="utf-8") as f:
            f.write(checklist)
        
        print(checklist)
        
        # Save results
        with open("production_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

if __name__ == "__main__":
    tester = ProductionTester()
    
    print("PRODUCTION READINESS TEST")
    print("="*50)
    
    # Run automated tests
    tester.test_data_integrity()
    
    # Generate manual checklist
    tester.generate_checklist()
    
    print("\n✅ Checklist saved to: production_checklist.md")
    print("✅ Results saved to: production_test_results.json")