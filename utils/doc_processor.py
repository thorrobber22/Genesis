"""Document Processing Utilities"""
from bs4 import BeautifulSoup
import re

def clean_html(html_content):
    """Clean HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove scripts and styles
    for script in soup(["script", "style"]):
        script.decompose()
        
    # Get text
    text = soup.get_text()
    
    # Clean whitespace
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)
    
    return text

def extract_sections(document_text):
    """Extract document sections"""
    sections = {}
    
    # Common section patterns
    section_patterns = [
        r"ITEM\s+\d+[A-Z]?\.\s+([^\n]+)",
        r"Part\s+[IVX]+\s*[-–—]\s*([^\n]+)",
    ]
    
    for pattern in section_patterns:
        matches = re.finditer(pattern, document_text, re.IGNORECASE)
        for match in matches:
            section_name = match.group(1).strip()
            sections[section_name] = match.start()
            
    return sections
