"""
Hedge Intelligence Document Processor
Created: 2025-06-05 13:53:05 UTC
Author: thorrobber22

Processes uploaded IPO documents, detects types, extracts information,
and prepares data for vector storage
"""

import os
import json
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Document parsing
from bs4 import BeautifulSoup
import pandas as pd

# AI/ML
import openai
import google.generativeai as genai

# Text processing
from dataclasses import dataclass
from enum import Enum

# Import config
try:
    from config import *
except ImportError:
    # Fallback config
    from pathlib import Path
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    PROCESSED_DIR = DATA_DIR / "processed"
    CACHE_DIR = DATA_DIR / "cache"
    VECTOR_DIR = DATA_DIR / "vectors"
    
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 100
    VALIDATION_MODEL = "gemini-pro"

# Document types enum
class DocumentType(Enum):
    S1 = "S-1"
    S1A = "S-1/A"
    FOURTWOFOURB4 = "424B4"
    LOCKUP = "LOCK_UP"
    UNDERWRITING = "UNDERWRITING"
    EIGHTA = "8-A"
    UNKNOWN = "UNKNOWN"

@dataclass
class ProcessedDocument:
    """Structured output from document processing"""
    ticker: str
    document_type: DocumentType
    filename: str
    processed_date: str
    sections: Dict[str, str]
    metadata: Dict[str, Any]
    key_facts: Dict[str, Any]
    vector_chunks: List[Dict[str, Any]]
    validation_status: str
    validation_notes: str

class DocumentProcessor:
    """Main document processing engine"""
    
    def __init__(self):
        """Initialize processor with AI models"""
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.gemini_model = genai.GenerativeModel(VALIDATION_MODEL)
        
        # Ensure directories exist
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        VECTOR_DIR.mkdir(parents=True, exist_ok=True)
    
    def detect_document_type(self, file_path: Path, content: str = None) -> DocumentType:
        """Detect document type from filename and content"""
        filename = file_path.name.upper()
        
        # First try filename patterns
        type_patterns = {
            DocumentType.S1: ["S-1", "S1_", "REGISTRATION"],
            DocumentType.S1A: ["S-1/A", "S1A", "AMENDMENT"],
            DocumentType.FOURTWOFOURB4: ["424B4", "PROSPECTUS"],
            DocumentType.LOCKUP: ["LOCK-UP", "LOCKUP", "MARKET_STANDOFF"],
            DocumentType.UNDERWRITING: ["UNDERWRITING", "PURCHASE_AGREEMENT"],
            DocumentType.EIGHTA: ["8-A", "8A", "FORM_8-A"]
        }
        
        for doc_type, patterns in type_patterns.items():
            for pattern in patterns:
                if pattern in filename:
                    return doc_type
        
        # If not found in filename, check content
        if content:
            content_upper = content[:5000].upper()  # Check first 5000 chars
            
            if "REGISTRATION STATEMENT" in content_upper and "S-1" in content_upper:
                return DocumentType.S1A if "AMENDMENT" in content_upper else DocumentType.S1
            elif "424B4" in content_upper or "FINAL PROSPECTUS" in content_upper:
                return DocumentType.FOURTWOFOURB4
            elif "LOCK-UP" in content_upper or "MARKET STAND-OFF" in content_upper:
                return DocumentType.LOCKUP
            elif "UNDERWRITING AGREEMENT" in content_upper:
                return DocumentType.UNDERWRITING
            elif "FORM 8-A" in content_upper:
                return DocumentType.EIGHTA
        
        return DocumentType.UNKNOWN
    
    def extract_text_from_html(self, file_path: Path) -> str:
        """Extract clean text from HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            print(f"Error extracting text from {file_path}: {e}")
            return ""
    
    def extract_sections_s1(self, content: str) -> Dict[str, str]:
        """Extract key sections from S-1 document"""
        sections = {
            "prospectus_summary": "",
            "risk_factors": "",
            "use_of_proceeds": "",
            "dividend_policy": "",
            "dilution": "",
            "capitalization": "",
            "business": "",
            "management": "",
            "principal_stockholders": "",
            "underwriting": "",
            "shares_eligible": "",
            "lock_up_agreements": ""
        }
        
        # Define section patterns
        section_patterns = {
            "prospectus_summary": r"PROSPECTUS SUMMARY(.*?)(?=RISK FACTORS|THE OFFERING|$)",
            "risk_factors": r"RISK FACTORS(.*?)(?=USE OF PROCEEDS|FORWARD-LOOKING|$)",
            "use_of_proceeds": r"USE OF PROCEEDS(.*?)(?=DIVIDEND POLICY|CAPITALIZATION|$)",
            "dividend_policy": r"DIVIDEND POLICY(.*?)(?=DILUTION|CAPITALIZATION|$)",
            "dilution": r"DILUTION(.*?)(?=CAPITALIZATION|SELECTED|$)",
            "capitalization": r"CAPITALIZATION(.*?)(?=SELECTED|MANAGEMENT|$)",
            "business": r"(?:OUR )?BUSINESS(.*?)(?=MANAGEMENT|RISK FACTORS|$)",
            "management": r"MANAGEMENT(.*?)(?=EXECUTIVE COMPENSATION|PRINCIPAL|$)",
            "principal_stockholders": r"PRINCIPAL (?:AND SELLING )?STOCKHOLDERS(.*?)(?=DESCRIPTION|SHARES|$)",
            "underwriting": r"UNDERWRITING(.*?)(?=LEGAL MATTERS|EXPERTS|$)",
            "shares_eligible": r"SHARES ELIGIBLE FOR FUTURE SALE(.*?)(?=MATERIAL|LEGAL|$)",
            "lock_up_agreements": r"LOCK-?UP AGREEMENTS?(.*?)(?=REGISTRATION|LEGAL|$)"
        }
        
        content_upper = content.upper()
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, content_upper, re.DOTALL)
            if match:
                sections[section_name] = match.group(1).strip()[:5000]  # Limit section size
        
        return sections
    
    def extract_key_facts_s1(self, sections: Dict[str, str], content: str) -> Dict[str, Any]:
        """Extract key facts from S-1 sections"""
        key_facts = {
            "company_name": "",
            "ticker": "",
            "exchange": "",
            "shares_offered": 0,
            "price_range": {"min": 0, "max": 0},
            "underwriters": [],
            "use_of_proceeds": "",
            "lock_up_period": 180,  # Default
            "risk_factors_count": 0,
            "voting_structure": "",
            "major_shareholders": []
        }
        
        # Extract company name
        name_match = re.search(r"(?:incorporated|organized).*?(?:under|in).*?(?:Delaware|Nevada|[\w\s]+)", 
                              content[:2000], re.IGNORECASE)
        if name_match:
            # Look for company name before "incorporated"
            before_text = content[:name_match.start()][-200:]
            company_match = re.search(r"([A-Z][A-Za-z0-9\s,\.]+?)(?:\s+is|\s+was)", before_text)
            if company_match:
                key_facts["company_name"] = company_match.group(1).strip()
        
        # Extract ticker symbol
        ticker_match = re.search(r"(?:symbol|ticker)[:\s\"']+([A-Z]{2,5})[\"\']?", content, re.IGNORECASE)
        if ticker_match:
            key_facts["ticker"] = ticker_match.group(1)
        
        # Extract exchange
        exchange_match = re.search(r"(?:listed|listing) on (?:the )?([A-Za-z\s]+)(?:Stock Exchange|Exchange|Market)", 
                                  content, re.IGNORECASE)
        if exchange_match:
            key_facts["exchange"] = exchange_match.group(1).strip()
        
        # Extract shares offered
        shares_match = re.search(r"(?:offering|offer|selling)\s+(?:of\s+)?(\d{1,3}(?:,\d{3})*)\s+shares", 
                                content, re.IGNORECASE)
        if shares_match:
            key_facts["shares_offered"] = int(shares_match.group(1).replace(",", ""))
        
        # Extract price range
        price_match = re.search(r"\$(\d+(?:\.\d{2})?)\s*(?:to|-)\s*\$(\d+(?:\.\d{2})?)\s*per\s+share", 
                               content, re.IGNORECASE)
        if price_match:
            key_facts["price_range"]["min"] = float(price_match.group(1))
            key_facts["price_range"]["max"] = float(price_match.group(2))
        
        # Extract underwriters from underwriting section
        if sections.get("underwriting"):
            underwriter_section = sections["underwriting"][:1000]
            # Look for lead underwriters
            underwriter_matches = re.findall(r"(?:Morgan Stanley|Goldman Sachs|J\.P\. Morgan|" +
                                           r"Bank of America|Citigroup|Wells Fargo|Barclays|" +
                                           r"Credit Suisse|Deutsche Bank|UBS|RBC|Jefferies|" +
                                           r"Piper Sandler|William Blair|Cowen|Stifel|" +
                                           r"[\w\s]+?(?:Securities|Capital|Partners))", 
                                           underwriter_section, re.IGNORECASE)
            key_facts["underwriters"] = list(set(underwriter_matches[:5]))  # Top 5 unique
        
        # Extract lock-up period
        if sections.get("lock_up_agreements"):
            lockup_match = re.search(r"(\d+)\s*days?\s*(?:after|following|from)", 
                                   sections["lock_up_agreements"], re.IGNORECASE)
            if lockup_match:
                key_facts["lock_up_period"] = int(lockup_match.group(1))
        
        # Count risk factors
        if sections.get("risk_factors"):
            risk_bullets = re.findall(r"(?:•|·|\*|(?:\d+\.))\s*[A-Z]", sections["risk_factors"])
            key_facts["risk_factors_count"] = len(risk_bullets)
        
        return key_facts
    
    def calculate_float_with_proof(self, key_facts: Dict[str, Any], sections: Dict[str, str]) -> Dict[str, Any]:
        """Calculate available float with detailed proof of work"""
        float_calculation = {
            "shares_offered": key_facts.get("shares_offered", 0),
            "total_outstanding_pre": 0,
            "total_outstanding_post": 0,
            "float_shares": 0,
            "float_percentage": 0,
            "locked_shares": 0,
            "insider_ownership_pct": 0,
            "calculation_steps": [],
            "sources": []
        }
        
        # Step 1: Find total shares outstanding
        cap_section = sections.get("capitalization", "")
        outstanding_match = re.search(r"(\d{1,3}(?:,\d{3})*(?:,\d{3})?)\s*shares?\s*(?:of\s*)?(?:common\s*)?(?:stock\s*)?outstanding", 
                                    cap_section, re.IGNORECASE)
        if outstanding_match:
            float_calculation["total_outstanding_pre"] = int(outstanding_match.group(1).replace(",", ""))
            float_calculation["calculation_steps"].append(
                f"Pre-IPO shares outstanding: {float_calculation['total_outstanding_pre']:,}"
            )
            float_calculation["sources"].append("Capitalization section")
        
        # Step 2: Calculate post-IPO shares
        if float_calculation["total_outstanding_pre"] > 0 and float_calculation["shares_offered"] > 0:
            float_calculation["total_outstanding_post"] = (
                float_calculation["total_outstanding_pre"] + float_calculation["shares_offered"]
            )
            float_calculation["calculation_steps"].append(
                f"Post-IPO shares: {float_calculation['total_outstanding_pre']:,} + {float_calculation['shares_offered']:,} = {float_calculation['total_outstanding_post']:,}"
            )
        
        # Step 3: Calculate locked shares from principal stockholders
        stockholders_section = sections.get("principal_stockholders", "")
        ownership_matches = re.findall(r"(\d+(?:\.\d+)?)\s*%", stockholders_section)
        
        if ownership_matches:
            total_insider_pct = sum(float(pct) for pct in ownership_matches[:10])  # Top 10
            float_calculation["insider_ownership_pct"] = min(total_insider_pct, 100)
            
            if float_calculation["total_outstanding_post"] > 0:
                float_calculation["locked_shares"] = int(
                    float_calculation["total_outstanding_post"] * (float_calculation["insider_ownership_pct"] / 100)
                )
                float_calculation["calculation_steps"].append(
                    f"Locked shares (insiders): {float_calculation['insider_ownership_pct']:.1f}% of {float_calculation['total_outstanding_post']:,} = {float_calculation['locked_shares']:,}"
                )
                float_calculation["sources"].append("Principal Stockholders section")
        
        # Step 4: Calculate float
        if float_calculation["total_outstanding_post"] > 0:
            # Float = New shares + (Outstanding - Locked)
            float_calculation["float_shares"] = (
                float_calculation["shares_offered"] + 
                max(0, float_calculation["total_outstanding_pre"] - float_calculation["locked_shares"])
            )
            
            float_calculation["float_percentage"] = (
                float_calculation["float_shares"] / float_calculation["total_outstanding_post"] * 100
            )
            
            float_calculation["calculation_steps"].append(
                f"Float calculation: {float_calculation['shares_offered']:,} (new) + {max(0, float_calculation['total_outstanding_pre'] - float_calculation['locked_shares']):,} (unlocked existing) = {float_calculation['float_shares']:,}"
            )
            float_calculation["calculation_steps"].append(
                f"Float percentage: {float_calculation['float_shares']:,} / {float_calculation['total_outstanding_post']:,} = {float_calculation['float_percentage']:.1f}%"
            )
        
        return float_calculation
    
    def chunk_document(self, text: str, doc_type: DocumentType, metadata: Dict) -> List[Dict[str, Any]]:
        """Chunk document for vector storage"""
        chunks = []
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Simple chunking by character count with overlap
        chunk_size = CHUNK_SIZE * 4  # Approximate characters per token
        overlap_size = CHUNK_OVERLAP * 4
        
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to end at sentence boundary
            if end < len(text):
                # Look for sentence end
                sentence_end = text.rfind('. ', start + overlap_size, end)
                if sentence_end > 0:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    "chunk_id": f"{metadata['ticker']}_{doc_type.value}_{chunk_id}",
                    "text": chunk_text,
                    "metadata": {
                        **metadata,
                        "chunk_index": chunk_id,
                        "document_type": doc_type.value,
                        "char_start": start,
                        "char_end": end
                    }
                })
                chunk_id += 1
            
            # Move start position
            start = end - overlap_size if end < len(text) else end
        
        return chunks
    
    async def validate_with_gemini(self, document: ProcessedDocument) -> Tuple[str, str]:
        """Validate extracted information with Gemini"""
        try:
            # Prepare validation prompt
            prompt = f"""
            Please validate the following extracted information from a {document.document_type.value} document:
            
            Company: {document.key_facts.get('company_name', 'Unknown')}
            Ticker: {document.key_facts.get('ticker', 'Unknown')}
            Shares Offered: {document.key_facts.get('shares_offered', 0):,}
            Price Range: ${document.key_facts.get('price_range', {}).get('min', 0)}-${document.key_facts.get('price_range', {}).get('max', 0)}
            
            Key sections found:
            {', '.join(k for k, v in document.sections.items() if v)}
            
            Please confirm:
            1. Does this information appear reasonable for an IPO filing?
            2. Are there any obvious errors or missing critical information?
            3. Rate the extraction quality: GOOD, FAIR, or POOR
            
            Respond in JSON format: {{"quality": "GOOD/FAIR/POOR", "notes": "brief explanation"}}
            """
            
            response = self.gemini_model.generate_content(prompt)
            
            # Parse response
            try:
                result = json.loads(response.text)
                return result.get("quality", "UNKNOWN"), result.get("notes", "No notes provided")
            except:
                # Fallback if JSON parsing fails
                if "GOOD" in response.text:
                    return "GOOD", "Validation passed"
                elif "POOR" in response.text:
                    return "POOR", "Validation identified issues"
                else:
                    return "FAIR", "Validation completed with minor issues"
                    
        except Exception as e:
            return "ERROR", f"Validation failed: {str(e)}"
    
    async def process_document(self, ticker: str, file_path: Path) -> ProcessedDocument:
        """Main processing pipeline for a document"""
        print(f"Processing {file_path.name} for {ticker}...")
        
        # Extract text
        if file_path.suffix.lower() in ['.html', '.htm']:
            content = self.extract_text_from_html(file_path)
        else:
            # For PDF/TXT files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        
        # Detect document type
        doc_type = self.detect_document_type(file_path, content)
        
        # Initialize processed document
        processed_doc = ProcessedDocument(
            ticker=ticker,
            document_type=doc_type,
            filename=file_path.name,
            processed_date=datetime.now().isoformat(),
            sections={},
            metadata={
                "file_size": file_path.stat().st_size,
                "file_hash": hashlib.md5(content.encode()).hexdigest(),
                "processing_version": "1.0"
            },
            key_facts={},
            vector_chunks=[],
            validation_status="PENDING",
            validation_notes=""
        )
        
        # Extract sections based on document type
        if doc_type in [DocumentType.S1, DocumentType.S1A]:
            processed_doc.sections = self.extract_sections_s1(content)
            processed_doc.key_facts = self.extract_key_facts_s1(processed_doc.sections, content)
            
            # Calculate float for S-1
            float_calc = self.calculate_float_with_proof(processed_doc.key_facts, processed_doc.sections)
            processed_doc.key_facts["float_calculation"] = float_calc
            
        elif doc_type == DocumentType.LOCKUP:
            # Extract lock-up specific information
            processed_doc.sections["lockup_terms"] = content[:10000]
            
            # Extract lock-up period
            lockup_match = re.search(r"(\d+)\s*days?\s*(?:after|following|from)", content, re.IGNORECASE)
            if lockup_match:
                processed_doc.key_facts["lockup_days"] = int(lockup_match.group(1))
                
        elif doc_type == DocumentType.FOURTWOFOURB4:
            # Extract final pricing information
            final_price_match = re.search(r"\$(\d+(?:\.\d{2})?)\s*per\s+share", content, re.IGNORECASE)
            if final_price_match:
                processed_doc.key_facts["final_price"] = float(final_price_match.group(1))
        
        # Create vector chunks
        chunk_metadata = {
            "ticker": ticker,
            "filename": file_path.name,
            "processed_date": processed_doc.processed_date
        }
        processed_doc.vector_chunks = self.chunk_document(content, doc_type, chunk_metadata)
        
        # Validate with Gemini
        validation_status, validation_notes = await self.validate_with_gemini(processed_doc)
        processed_doc.validation_status = validation_status
        processed_doc.validation_notes = validation_notes
        
        # Save processed document
        output_path = PROCESSED_DIR / f"{ticker}_{doc_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert to dict for JSON serialization
        doc_dict = {
            "ticker": processed_doc.ticker,
            "document_type": processed_doc.document_type.value,
            "filename": processed_doc.filename,
            "processed_date": processed_doc.processed_date,
            "sections": processed_doc.sections,
            "metadata": processed_doc.metadata,
            "key_facts": processed_doc.key_facts,
            "vector_chunks_count": len(processed_doc.vector_chunks),
            "validation_status": processed_doc.validation_status,
            "validation_notes": processed_doc.validation_notes
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(doc_dict, f, indent=2)
        
        print(f"✓ Processed {file_path.name}: {doc_type.value} ({validation_status})")
        
        return processed_doc

# Standalone processing function for admin panel
async def process_uploaded_document(ticker: str, file_path: Path) -> Dict[str, Any]:
    """Process a single uploaded document"""
    processor = DocumentProcessor()
    result = await processor.process_document(ticker, file_path)
    
    return {
        "success": True,
        "document_type": result.document_type.value,
        "validation_status": result.validation_status,
        "key_facts": result.key_facts,
        "chunks_created": len(result.vector_chunks)
    }

def process_document_sync(ticker: str, file_path: Path) -> Dict[str, Any]:
    """Synchronous wrapper for document processing"""
    return asyncio.run(process_uploaded_document(ticker, file_path))

if __name__ == "__main__":
    # Test processing
    test_file = Path("data/documents/CRCL_S1_20250601.html")
    if test_file.exists():
        result = process_document_sync("CRCL", test_file)
        print(f"Test result: {json.dumps(result, indent=2)}")
    else:
        print("No test file found. Upload documents through admin panel.")