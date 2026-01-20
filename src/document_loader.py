"""
Document Loader Module
Handles loading and parsing various document formats (PDF, DOCX, TXT).
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
import re

import fitz  # PyMuPDF
from docx import Document
from loguru import logger

from src.config import config


class DocumentLoader:
    """
    Loads and extracts text from various document formats.
    Supports PDF, DOCX, and TXT files.
    """
    
    def __init__(self, folder_path: Optional[str] = None):
        """
        Initialize the document loader.
        
        Args:
            folder_path: Path to the folder containing documents
        """
        self.folder_path = Path(folder_path or config.documents_folder)
        self.supported_formats = config.supported_formats
        
    def scan_documents(self) -> List[Path]:
        """
        Scan the folder for supported document files.
        
        Returns:
            List of Path objects for found documents
        """
        if not self.folder_path.exists():
            logger.warning(f"Document folder does not exist: {self.folder_path}")
            return []
        
        documents = []
        for ext in self.supported_formats:
            pattern = f"*.{ext}"
            found = list(self.folder_path.glob(pattern))
            documents.extend(found)
            logger.info(f"Found {len(found)} {ext.upper()} files")
        
        logger.info(f"Total documents found: {len(documents)}")
        return documents
    
    def load_document(self, file_path: Path) -> Optional[Dict[str, str]]:
        """
        Load a single document and extract its text.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary containing document metadata and text
        """
        try:
            ext = file_path.suffix.lower().lstrip('.')
            
            if ext == 'pdf':
                text = self._load_pdf(file_path)
            elif ext == 'docx':
                text = self._load_docx(file_path)
            elif ext == 'txt':
                text = self._load_txt(file_path)
            else:
                logger.warning(f"Unsupported file format: {ext}")
                return None
            
            if not text or not text.strip():
                logger.warning(f"No text extracted from {file_path.name}")
                return None
            
            # Clean the text
            text = self._clean_text(text)
            
            return {
                'filename': file_path.name,
                'filepath': str(file_path),
                'format': ext,
                'text': text,
                'length': len(text)
            }
            
        except Exception as e:
            logger.error(f"Error loading document {file_path}: {e}")
            return None
    
    def load_all_documents(self) -> List[Dict[str, str]]:
        """
        Load all documents from the folder.
        
        Returns:
            List of document dictionaries
        """
        file_paths = self.scan_documents()
        documents = []
        
        for file_path in file_paths:
            doc = self.load_document(file_path)
            if doc:
                documents.append(doc)
                logger.info(f"Loaded: {doc['filename']} ({doc['length']} chars)")
        
        logger.info(f"Successfully loaded {len(documents)} documents")
        return documents
    
    def _load_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        text = []
        
        with fitz.open(file_path) as doc:
            for page_num, page in enumerate(doc, 1):
                page_text = page.get_text()
                if page_text.strip():
                    text.append(page_text)
        
        return '\n'.join(text)
    
    def _load_docx(self, file_path: Path) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text
        """
        doc = Document(file_path)
        text = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        
        return '\n'.join(text)
    
    def _load_txt(self, file_path: Path) -> str:
        """
        Load text from TXT file.
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            File content
        """
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\'\"]', '', text)
        
        # Remove multiple consecutive punctuation
        text = re.sub(r'([\.!?]){2,}', r'\1', text)
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def chunk_text(self, text: str, chunk_size: Optional[int] = None, 
                   overlap: Optional[int] = None) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters
            
        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or config.chunk_size
        overlap = overlap or config.chunk_overlap
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending within next 100 chars
                sentence_end = text[end:end+100].find('. ')
                if sentence_end != -1:
                    end = end + sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        logger.info(f"Split text into {len(chunks)} chunks")
        return chunks
    
    def chunk_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Chunk all documents into smaller pieces.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of chunked document dictionaries
        """
        chunked_docs = []
        
        for doc in documents:
            chunks = self.chunk_text(doc['text'])
            
            for i, chunk in enumerate(chunks):
                chunked_doc = {
                    'filename': doc['filename'],
                    'filepath': doc['filepath'],
                    'format': doc['format'],
                    'chunk_id': i,
                    'total_chunks': len(chunks),
                    'text': chunk,
                    'length': len(chunk)
                }
                chunked_docs.append(chunked_doc)
        
        logger.info(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
        return chunked_docs
