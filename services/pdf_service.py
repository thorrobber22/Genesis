"""
PDF Service - Document rendering and navigation
Date: 2025-06-14 02:42:43 UTC
Author: thorrobber22
"""

import fitz  # PyMuPDF
import base64
from pathlib import Path
from typing import Tuple, Optional
import streamlit as st

class PDFService:
    """Handle PDF rendering, navigation, and highlighting"""
    
    def __init__(self):
        self.current_doc = None
        self.current_page = 1
        self.zoom_level = 1.0
        
    def load_document(self, doc_path: str) -> bool:
        """Load a PDF document"""
        try:
            self.current_doc = fitz.open(doc_path)
            return True
        except Exception as e:
            st.error(f"Error loading document: {e}")
            return False
    
    def render_page(self, page_num: int = 1, zoom: float = 1.0) -> str:
        """Render PDF page as base64 image"""
        if not self.current_doc:
            return ""
            
        try:
            # Get page
            page = self.current_doc[page_num - 1]
            
            # Render at higher resolution
            mat = fitz.Matrix(zoom * 2, zoom * 2)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to base64
            img_b64 = base64.b64encode(img_data).decode()
            
            return f"data:image/png;base64,{img_b64}"
            
        except Exception as e:
            st.error(f"Error rendering page: {e}")
            return ""
    
    def get_page_text(self, page_num: int) -> str:
        """Extract text from specific page"""
        if not self.current_doc:
            return ""
            
        try:
            page = self.current_doc[page_num - 1]
            return page.get_text()
        except:
            return ""
    
    def search_text(self, search_term: str) -> list:
        """Search for text across all pages"""
        results = []
        if not self.current_doc:
            return results
            
        for page_num in range(len(self.current_doc)):
            page = self.current_doc[page_num]
            text_instances = page.search_for(search_term)
            
            if text_instances:
                results.append({
                    'page': page_num + 1,
                    'instances': len(text_instances),
                    'rects': text_instances
                })
                
        return results
    
    def highlight_text(self, page_num: int, search_term: str) -> str:
        """Render page with highlighted text"""
        if not self.current_doc:
            return ""
            
        try:
            page = self.current_doc[page_num - 1]
            
            # Search for text
            text_instances = page.search_for(search_term)
            
            # Highlight each instance
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors({"stroke": [1, 0.86, 0.24]})  # Yellow
                highlight.update()
            
            # Render page
            mat = fitz.Matrix(self.zoom_level * 2, self.zoom_level * 2)
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to base64
            img_b64 = base64.b64encode(img_data).decode()
            
            return f"data:image/png;base64,{img_b64}"
            
        except Exception as e:
            st.error(f"Error highlighting: {e}")
            return ""
    
    def jump_to_citation(self, page_num: int, highlight_text: str = None) -> dict:
        """Jump to specific page and optionally highlight text"""
        self.current_page = page_num
        
        result = {
            'page': page_num,
            'total_pages': len(self.current_doc) if self.current_doc else 0,
            'image': self.render_page(page_num, self.zoom_level)
        }
        
        if highlight_text:
            result['highlighted_image'] = self.highlight_text(page_num, highlight_text)
            
        return result

# Singleton instance
pdf_service = PDFService()
