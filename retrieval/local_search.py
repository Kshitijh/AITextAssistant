"""
Local Search Module
Handles semantic search within local document embeddings.
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from loguru import logger

from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from config.settings import config


class LocalSearch:
    """
    Performs semantic search on local document embeddings.
    Primary source for retrieving relevant context.
    """
    
    def __init__(self, embedder: Embedder, vector_store: VectorStore):
        """
        Initialize local search.
        
        Args:
            embedder: Embedder instance for query encoding
            vector_store: VectorStore instance with indexed documents
        """
        self.embedder = embedder
        self.vector_store = vector_store
        self.similarity_threshold = config.similarity_threshold
        
        logger.info("Local search initialized")
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Search for relevant documents based on query.
        
        Args:
            query: Search query text
            top_k: Number of top results to return (uses config default if None)
            
        Returns:
            List of result dictionaries with document, score, and source info
        """
        if not query or not query.strip():
            logger.warning("Empty query provided")
            return []
        
        try:
            # Encode query
            logger.debug(f"Searching for: {query[:100]}...")
            query_embedding = self.embedder.encode_single(query)
            
            # Search vector store
            top_k = top_k or config.top_k_results
            results = self.vector_store.search(query_embedding, top_k)
            
            # Filter by similarity threshold and format results
            filtered_results = []
            for doc, score in results:
                if score >= self.similarity_threshold:
                    result = {
                        'text': doc.get('text', ''),
                        'source': 'local',
                        'similarity_score': score,
                        'metadata': {
                            'file_name': doc.get('file_name', 'unknown'),
                            'chunk_index': doc.get('chunk_index', 0),
                            'file_path': doc.get('file_path', ''),
                        }
                    }
                    filtered_results.append(result)
                    
                    logger.debug(
                        f"Local result: {doc.get('file_name', 'unknown')} "
                        f"(chunk {doc.get('chunk_index', 0)}) - Score: {score:.3f}"
                    )
                else:
                    logger.debug(f"Filtered out result with score {score:.3f} (threshold: {self.similarity_threshold})")
            
            logger.info(f"Found {len(filtered_results)} local results above threshold")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error in local search: {e}")
            return []
    
    def get_context(self, query: str, max_length: Optional[int] = None) -> str:
        """
        Get concatenated context from top search results.
        
        Args:
            query: Search query
            max_length: Maximum total length of context (uses config default if None)
            
        Returns:
            Concatenated context string
        """
        results = self.search(query)
        max_length = max_length or config.max_context_length
        
        context_parts = []
        current_length = 0
        
        for result in results:
            text = result['text']
            if current_length + len(text) <= max_length:
                context_parts.append(text)
                current_length += len(text)
            else:
                # Add partial text to reach max_length
                remaining = max_length - current_length
                if remaining > 100:  # Only add if meaningful amount remains
                    context_parts.append(text[:remaining])
                break
        
        context = "\n\n".join(context_parts)
        logger.debug(f"Generated context of length {len(context)}")
        
        return context
    
    def has_relevant_results(self, query: str) -> bool:
        """
        Check if local search has any relevant results.
        
        Args:
            query: Search query
            
        Returns:
            True if relevant results exist, False otherwise
        """
        results = self.search(query, top_k=1)
        return len(results) > 0
