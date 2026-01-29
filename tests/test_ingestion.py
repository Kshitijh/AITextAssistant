"""
Unit Tests for Document Ingestion
"""

import pytest
from pathlib import Path
import tempfile

from ingestion.pdf_reader import PDFReader
from ingestion.docx_reader import DOCXReader
from ingestion.chunker import TextChunker


class TestPDFReader:
    """Test PDF reading functionality."""
    
    def test_pdf_reader_initialization(self):
        """Test PDF reader can be initialized."""
        reader = PDFReader()
        assert reader is not None
    
    # Add more tests with actual PDF files


class TestDOCXReader:
    """Test DOCX reading functionality."""
    
    def test_docx_reader_initialization(self):
        """Test DOCX reader can be initialized."""
        reader = DOCXReader()
        assert reader is not None
    
    # Add more tests with actual DOCX files


class TestTextChunker:
    """Test text chunking functionality."""
    
    def test_chunker_initialization(self):
        """Test chunker can be initialized."""
        chunker = TextChunker(chunk_size=100, overlap=10)
        assert chunker.chunk_size == 100
        assert chunker.overlap == 10
    
    def test_chunk_simple_text(self):
        """Test chunking simple text."""
        chunker = TextChunker(chunk_size=50, overlap=10)
        text = "This is a test sentence. " * 10
        
        chunks = chunker.chunk_text(text)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('chunk_index' in chunk for chunk in chunks)
    
    def test_chunk_with_metadata(self):
        """Test chunking with metadata."""
        chunker = TextChunker(chunk_size=100, overlap=10)
        text = "Sample text for testing."
        metadata = {'file_name': 'test.txt', 'source': 'test'}
        
        chunks = chunker.chunk_text(text, metadata)
        
        assert len(chunks) > 0
        assert chunks[0]['file_name'] == 'test.txt'
        assert chunks[0]['source'] == 'test'
    
    def test_empty_text(self):
        """Test chunking empty text."""
        chunker = TextChunker()
        chunks = chunker.chunk_text("")
        
        assert len(chunks) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
