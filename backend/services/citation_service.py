"""Citation Service for document processing"""

from pathlib import Path
from bs4 import BeautifulSoup
import hashlib
import json
from typing import Dict, List, Optional

class CitationService:
    """Handle citation processing for documents"""
    
    def __init__(self):
        self.indices_dir = Path("data/indices")
        self.indices_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_document(self, doc_path: str) -> Dict:
        """Add citation IDs to every citable element"""
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        citations = []
        page_num = 1
        
        # Add IDs to all citable elements
        for idx, elem in enumerate(soup.find_all(['h1', 'h2', 'h3', 'p', 'table', 'li'])):
            # Skip empty elements
            if not elem.get_text(strip=True):
                continue
            
            # Generate stable citation ID
            text_preview = elem.get_text()[:50]
            citation_id = f"cite-{idx}-{hashlib.md5(text_preview.encode()).hexdigest()[:6]}"
            elem['id'] = citation_id
            elem['data-cite'] = 'true'
            
            # Estimate page number (rough calculation)
            if 'page' in elem.get_text().lower():
                page_match = re.search(r'page\s+(\d+)', elem.get_text(), re.I)
                if page_match:
                    page_num = int(page_match.group(1))
            
            citations.append({
                "id": citation_id,
                "text": elem.get_text()[:200] + "..." if len(elem.get_text()) > 200 else elem.get_text(),
                "type": elem.name,
                "page": page_num,
                "position": idx * 100,  # Rough position for scrolling
                "tag": elem.name
            })
        
        # Save processed HTML
        processed_path = doc_path.replace('.html', '_cited.html')
        with open(processed_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        # Save citation index
        doc_name = Path(doc_path).stem
        index_path = self.indices_dir / f"{doc_name}_citations.json"
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump({
                "document": doc_name,
                "total_citations": len(citations),
                "citations": citations,
                "processed_date": datetime.now(timezone.utc).isoformat()
            }, f, indent=2)
        
        return {
            "path": processed_path,
            "citations": citations,
            "total": len(citations)
        }
    
    async def get_citations(self, doc_id: str) -> List[Dict]:
        """Get citations for a document"""
        
        index_path = self.indices_dir / f"{doc_id}_citations.json"
        
        if index_path.exists():
            with open(index_path, 'r') as f:
                data = json.load(f)
                return data.get('citations', [])
        
        return []
    
    def find_citation_by_text(self, doc_id: str, search_text: str) -> Optional[Dict]:
        """Find a citation containing specific text"""
        
        citations = self.get_citations(doc_id)
        
        search_lower = search_text.lower()
        for citation in citations:
            if search_lower in citation['text'].lower():
                return citation
        
        return None
