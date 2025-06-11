#!/usr/bin/env python3
"""
Automated Production Test - Actually test the app programmatically
"""

import subprocess
import time
import requests
from pathlib import Path
import json
import psutil
import socket
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import threading

class AutomatedProductionTest:
    def __init__(self):
        self.app_process = None
        self.driver = None
        self.base_url = "http://localhost:8501"
        self.test_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "user": "thorrobber22",
            "tests": {}
        }
    
    def start_streamlit_app(self):
        """Start the Streamlit app"""
        print("🚀 Starting Streamlit app...")
        
        # Check if already running
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'streamlit' in str(proc.info['cmdline']):
                print("⚠️  Streamlit already running, killing existing process...")
                proc.terminate()
                time.sleep(2)
        
        # Start new instance
        self.app_process = subprocess.Popen(
            ["streamlit", "run", "hedge_intelligence.py", "--server.headless=true"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for app to start
        print("⏳ Waiting for app to start...")
        for i in range(30):
            try:
                response = requests.get(self.base_url)
                if response.status_code == 200:
                    print("✅ App started successfully!")
                    return True
            except:
                time.sleep(1)
        
        print("❌ App failed to start!")
        return False
    
    def setup_browser(self):
        """Setup Selenium browser"""
        print("🌐 Setting up browser...")
        
        options = Options()
        options.add_argument('--headless')  # Run in background
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.set_window_size(1920, 1080)
            print("✅ Browser ready")
            return True
        except Exception as e:
            print(f"❌ Browser setup failed: {e}")
            print("💡 Install ChromeDriver: https://chromedriver.chromium.org/")
            return False
    
    def test_navigation(self):
        """Test all navigation pages"""
        print("\n📍 Testing Navigation...")
        
        results = {"pages": {}}
        
        try:
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Find navigation dropdown
            nav_selector = self.driver.find_element(By.XPATH, "//select[@key='main_navigation']")
            
            pages = [
                "Dashboard",
                "Document Explorer",
                "IPO Tracker",
                "Search",
                "Watchlist",
                "Company Management"
            ]
            
            for page in pages:
                try:
                    # Select page
                    nav_selector.send_keys(page)
                    time.sleep(2)
                    
                    # Check for errors
                    error_elements = self.driver.find_elements(By.CLASS_NAME, "stException")
                    
                    if error_elements:
                        results["pages"][page] = {
                            "status": "ERROR",
                            "error": error_elements[0].text
                        }
                        print(f"   ❌ {page}: ERROR")
                    else:
                        results["pages"][page] = {"status": "SUCCESS"}
                        print(f"   ✅ {page}: Loaded successfully")
                        
                except Exception as e:
                    results["pages"][page] = {
                        "status": "FAIL",
                        "error": str(e)
                    }
                    print(f"   ❌ {page}: {e}")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Navigation test failed: {e}")
        
        self.test_results["tests"]["navigation"] = results
    
    def test_document_explorer(self):
        """Test document explorer functionality"""
        print("\n📁 Testing Document Explorer...")
        
        results = {}
        
        try:
            # Navigate to Document Explorer
            self.driver.get(f"{self.base_url}?page=Document%20Explorer")
            time.sleep(3)
            
            # Find company expanders
            expanders = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'streamlit-expanderHeader')]")
            
            results["company_count"] = len(expanders)
            print(f"   📊 Found {len(expanders)} companies")
            
            if expanders:
                # Click first company
                expanders[0].click()
                time.sleep(2)
                
                # Find documents
                doc_links = self.driver.find_elements(By.XPATH, "//button[contains(text(), '.html')]")
                results["document_count"] = len(doc_links)
                print(f"   📄 Found {len(doc_links)} documents in first company")
                
                if doc_links:
                    # Click first document
                    doc_links[0].click()
                    time.sleep(3)
                    
                    # Check if document viewer opened
                    viewer = self.driver.find_elements(By.XPATH, "//iframe")
                    if viewer:
                        results["viewer_works"] = True
                        print("   ✅ Document viewer working")
                    else:
                        results["viewer_works"] = False
                        print("   ❌ Document viewer not found")
            
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Document Explorer test failed: {e}")
        
        self.test_results["tests"]["document_explorer"] = results
    
    def test_ai_chat(self):
        """Test AI chat functionality"""
        print("\n💬 Testing AI Chat...")
        
        results = {}
        
        try:
            # Make sure we have a document open
            self.test_document_explorer()
            
            # Find chat input
            chat_input = self.driver.find_element(By.XPATH, "//input[@placeholder='Ask about this document...']")
            chat_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Send')]")
            
            # Send test message
            test_message = "What is the main topic of this document?"
            chat_input.send_keys(test_message)
            chat_button.click()
            
            print("   ⏳ Waiting for AI response...")
            time.sleep(10)  # Wait for AI response
            
            # Check for response
            chat_messages = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'chat-message')]")
            
            if len(chat_messages) > 1:
                results["response_received"] = True
                print("   ✅ AI response received")
                
                # Check for citations
                citations = self.driver.find_elements(By.XPATH, "//a[contains(text(), '[Page')]")
                if citations:
                    results["citations_found"] = len(citations)
                    print(f"   ✅ Found {len(citations)} citations")
                else:
                    results["citations_found"] = 0
                    print("   ⚠️  No citations found")
            else:
                results["response_received"] = False
                print("   ❌ No AI response")
                
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ AI Chat test failed: {e}")
        
        self.test_results["tests"]["ai_chat"] = results
    
    def test_ipo_tracker(self):
        """Test IPO tracker"""
        print("\n📈 Testing IPO Tracker...")
        
        results = {}
        
        try:
            # Navigate to IPO Tracker
            self.driver.get(f"{self.base_url}?page=IPO%20Tracker")
            time.sleep(3)
            
            # Check for IPO data
            tables = self.driver.find_elements(By.XPATH, "//table")
            
            if tables:
                results["table_found"] = True
                
                # Count rows
                rows = tables[0].find_elements(By.TAG_NAME, "tr")
                results["ipo_count"] = len(rows) - 1  # Minus header
                print(f"   📊 Found {results['ipo_count']} IPOs displayed")
            else:
                results["table_found"] = False
                print("   ⚠️  No IPO table found")
                
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ IPO Tracker test failed: {e}")
        
        self.test_results["tests"]["ipo_tracker"] = results
    
    def test_search(self):
        """Test search functionality"""
        print("\n🔍 Testing Search...")
        
        results = {}
        
        try:
            # Navigate to Search
            self.driver.get(f"{self.base_url}?page=Search")
            time.sleep(3)
            
            # Find search input
            search_input = self.driver.find_element(By.XPATH, "//input[contains(@placeholder, 'Search')]")
            
            # Perform search
            search_input.send_keys("revenue")
            search_input.submit()
            
            time.sleep(5)
            
            # Check for results
            results_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'search-result')]")
            
            if results_elements:
                results["search_works"] = True
                results["result_count"] = len(results_elements)
                print(f"   ✅ Search returned {len(results_elements)} results")
            else:
                # Check if "coming soon" message
                info_messages = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'coming soon')]")
                if info_messages:
                    results["search_works"] = False
                    results["status"] = "NOT_IMPLEMENTED"
                    print("   ⚠️  Search not implemented yet")
                    
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Search test failed: {e}")
        
        self.test_results["tests"]["search"] = results
    
    def test_admin_panel(self):
        """Test admin panel"""
        print("\n🔐 Testing Admin Panel...")
        
        results = {}
        
        try:
            # Start admin panel in separate process
            admin_process = subprocess.Popen(
                ["streamlit", "run", "admin/admin_panel.py", "--server.port=8502", "--server.headless=true"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            time.sleep(5)
            
            # Navigate to admin
            self.driver.get("http://localhost:8502")
            time.sleep(3)
            
            # Enter password
            password_input = self.driver.find_element(By.XPATH, "//input[@type='password']")
            password_input.send_keys("hedgeadmin2025")
            password_input.submit()
            
            time.sleep(3)
            
            # Check if logged in
            if "SEC Pipeline" in self.driver.page_source:
                results["login_success"] = True
                print("   ✅ Admin login successful")
                
                # Check for pending requests
                pending_elements = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Pending')]")
                if pending_elements:
                    results["shows_pending"] = True
                    print("   ✅ Shows pending requests")
            else:
                results["login_success"] = False
                print("   ❌ Admin login failed")
            
            # Cleanup
            admin_process.terminate()
            
        except Exception as e:
            results["error"] = str(e)
            print(f"   ❌ Admin panel test failed: {e}")
        
        self.test_results["tests"]["admin_panel"] = results
    
    def run_all_tests(self):
        """Run all automated tests"""
        print("="*80)
        print("HEDGE INTELLIGENCE - AUTOMATED PRODUCTION TEST")
        print("="*80)
        print(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"User: thorrobber22")
        print("="*80)
        
        # Start app
        if not self.start_streamlit_app():
            print("❌ Cannot start app - aborting tests")
            return
        
        # Setup browser
        if not self.setup_browser():
            print("❌ Cannot setup browser - aborting tests")
            self.cleanup()
            return
        
        try:
            # Run tests
            self.test_navigation()
            self.test_document_explorer()
            self.test_ai_chat()
            self.test_ipo_tracker()
            self.test_search()
            self.test_admin_panel()
            
        finally:
            self.cleanup()
        
        # Save results
        self.save_results()
    
    def cleanup(self):
        """Clean up processes"""
        print("\n🧹 Cleaning up...")
        
        if self.driver:
            self.driver.quit()
        
        if self.app_process:
            self.app_process.terminate()
    
    def save_results(self):
        """Save test results"""
        output_file = Path("automated_test_results.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2)
        
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80)
        
        # Summary
        total_tests = len(self.test_results["tests"])
        passed = sum(1 for t in self.test_results["tests"].values() 
                    if not t.get("error") and t.get("status") != "ERROR")
        
        print(f"✅ Tests passed: {passed}/{total_tests}")
        print(f"📄 Full results: {output_file}")

if __name__ == "__main__":
    # Check if selenium is installed
    try:
        import selenium
    except ImportError:
        print("❌ Selenium not installed!")
        print("Run: pip install selenium")
        print("Also download ChromeDriver from: https://chromedriver.chromium.org/")
        exit(1)
    
    tester = AutomatedProductionTest()
    tester.run_all_tests()