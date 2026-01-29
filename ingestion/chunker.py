"""
Text Chunker Module
Intelligently splits text into semantic chunks for embedding.
"""

from typing import List, Dict
import re
from loguru import logger


class TextChunker:
    """
    Intelligently chunks text into semantic segments.
    Uses sentence boundaries and paragraph structure for better semantic preservation.
    """
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize text chunker.
        
        Args:
            chunk_size: Target size for each chunk (in characters)
            overlap: Overlap between consecutive chunks (in characters)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Sentence boundary patterns
        self.sentence_pattern = re.compile(r'(?<=[.!?])\s+')
        self.paragraph_pattern = re.compile(r'\n\s*\n')
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Split text into semantic chunks with metadata.
        
        Args:
            text: The text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of dictionaries containing chunk text and metadata
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to chunker")
            return []
        
        logger.info(f"Chunking text of length {len(text)}")
        
        # First split by paragraphs
        paragraphs = self.paragraph_pattern.split(text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for paragraph in paragraphs:
            # If paragraph is too long, split into sentences
            if len(paragraph) > self.chunk_size:
                sentences = self._split_sentences(paragraph)
                
                for sentence in sentences:
                    # If single sentence is too long, force split
                    if len(sentence) > self.chunk_size * 1.5:
                        forced_chunks = self._force_split(sentence)
                        for forced_chunk in forced_chunks:
                            chunks.append(self._create_chunk(forced_chunk, chunk_index, metadata))
                            chunk_index += 1
                    else:
                        # Add sentence to current chunk
                        if len(current_chunk) + len(sentence) > self.chunk_size:
                            if current_chunk:
                                chunks.append(self._create_chunk(current_chunk, chunk_index, metadata))
                                chunk_index += 1
                                # Start new chunk with overlap
                                current_chunk = self._get_overlap(current_chunk) + sentence
                            else:
                                current_chunk = sentence
                        else:
                            current_chunk += " " + sentence if current_chunk else sentence
            else:
                # Add paragraph to current chunk
                if len(current_chunk) + len(paragraph) > self.chunk_size:
                    if current_chunk:
                        chunks.append(self._create_chunk(current_chunk, chunk_index, metadata))
                        chunk_index += 1
                        # Start new chunk with overlap
                        current_chunk = self._get_overlap(current_chunk) + paragraph
                    else:
                        current_chunk = paragraph
                else:
                    current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        # Add final chunk
        if current_chunk:
            chunks.append(self._create_chunk(current_chunk, chunk_index, metadata))
        
        logger.info(f"Created {len(chunks)} chunks")
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = self.sentence_pattern.split(text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _force_split(self, text: str) -> List[str]:
        """Force split text that's too long even for a single chunk."""
        chunks = []
        for i in range(0, len(text), self.chunk_size - self.overlap):
            chunk = text[i:i + self.chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks
    
    def _get_overlap(self, text: str) -> str:
        """Get overlap text from the end of the current chunk."""
        if len(text) <= self.overlap:
            return text
        return text[-self.overlap:]
    
    def _create_chunk(self, text: str, index: int, metadata: Dict = None) -> Dict:
        """
        Create a chunk dictionary with metadata.
        
        Args:
            text: The chunk text
            index: The chunk index
            metadata: Optional metadata to include
            
        Returns:
            Dictionary with chunk data
        """
        chunk_data = {
            'text': text.strip(),
            'chunk_index': index,
            'char_count': len(text)
        }
        
        if metadata:
            chunk_data.update(metadata)
        
        return chunk_data
