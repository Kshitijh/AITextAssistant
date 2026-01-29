"""
PDF Reader Module
Handles extraction of text from PDF files.
"""

from pathlib import Path
from typing import Optional
import fitz  # PyMuPDF
from loguru import logger


class PDFReader:
    """Extracts text content from PDF files."""
    
    def __init__(self):
        """Initialize PDF reader."""
        pass
    
    def extract_text(self, file_path: Path) -> Optional[str]:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            logger.info(f"Extracting text from PDF: {file_path.name}")
            
            doc = fitz.open(str(file_path))
            text_parts = []
            
            for page_num, page in enumerate(doc, 1):
                text = page.get_text("text")
                if text.strip():
                    text_parts.append(text)
                    logger.debug(f"Extracted {len(text)} chars from page {page_num}")
            
            doc.close()
            
            full_text = "\n".join(text_parts)
            logger.info(f"Successfully extracted {len(full_text)} characters from {file_path.name}")
            
            return full_text if full_text.strip() else None
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path.name}: {e}")
            return None
    
    def extract_metadata(self, file_path: Path) -> dict:
        """
        Extract metadata from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing metadata
        """
        try:
            doc = fitz.open(str(file_path))
            metadata = {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'pages': len(doc)
            }
            doc.close()
            return metadata
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path.name}: {e}")
            return {}
