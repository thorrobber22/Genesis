# HEDGE INTELLIGENCE - FULL CONTEXT DUMP
*Generated: 2025-06-08 20:32:26 UTC*  
*User: thorrobber22*

## 🎯 PROJECT OVERVIEW

**Name:** Hedge Intelligence  
**Purpose:** SEC Document Analysis Platform with AI Chat  
**Core Features:**
- Document Explorer (file tree navigation)
- AI Chat with citations
- Automatic data extraction
- IPO tracking
- Professional grey theme

## 📁 FILE STRUCTURE

### Key Files:

**hedge_intelligence.py**
- Lines: 235
- Classes: None
- Functions: 5

**services/ai_service.py**
- Lines: 157
- Classes: AIService
- Functions: 4

**services/document_service.py**
- Lines: 71
- Classes: DocumentService
- Functions: 5

**components/document_explorer.py**
- Lines: 72
- Classes: DocumentExplorer
- Functions: 4

**components/persistent_chat.py**
- Lines: 93
- Classes: PersistentChat
- Functions: 3

**components/data_extractor.py**
- Lines: 67
- Classes: DataExtractor
- Functions: 3

**components/ipo_tracker_enhanced.py**
- Lines: 75
- Classes: IPOTrackerEnhanced
- Functions: 3

## 📊 DATA SUMMARY

**SEC Documents:**
- Total Companies: 8
- Total Files: 74

**Companies:**
- CRCL: 10 files
- DLHZ: 11 files
- FGO: 15 files
- FMFC: 12 files
- MSFT: 0 files

## 📦 DEPENDENCIES

**Required:**
- # Core Framework
- streamlit==1.31.0
- fastapi==0.109.0
- uvicorn==0.27.0
- 
- # AI/ML
- openai==1.35.0
- google-generativeai==0.3.2
- chromadb==0.4.22
- numpy==1.26.4
- pandas==2.1.4
- 
- # Document Processing
- beautifulsoup4==4.12.3
- lxml==5.1.0
- python-multipart==0.0.6
- 
- # PDF Generation
- reportlab==4.0.4
- 
- # Async Operations
- aiohttp==3.9.3
- aiofiles==23.2.1
- 
- # Utilities
- python-dotenv==1.0.0
- requests==2.31.0
- apscheduler==3.10.4
- 
- # Development
- watchdog==3.0.0
