"""
Vector Store Module
Handles FAISS vector database for semantic search.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
import faiss
from loguru import logger

from src.config import config


class VectorStore:
    """
    FAISS-based vector store for efficient semantic search.
    Stores document embeddings and enables fast similarity search.
    """
    
    def __init__(self, index_path: Optional[str] = None, dimension: Optional[int] = None):
        """
        Initialize the vector store.
        
        Args:
            index_path: Path to save/load the FAISS index
            dimension: Dimension of the embedding vectors
        """
        self.index_path = Path(index_path or config.vector_store_path)
        self.dimension = dimension or config.vector_dimension
        self.index: Optional[faiss.Index] = None
        self.documents: List[Dict] = []
        self._is_trained = False
        
    def create_index(self) -> None:
        """Create a new FAISS index."""
        try:
            logger.info(f"Creating FAISS index with dimension {self.dimension}")
            
            # Use IndexFlatL2 for exact search with L2 distance
            # For cosine similarity, we normalize vectors before adding
            self.index = faiss.IndexFlatL2(self.dimension)
            self._is_trained = True
            
            logger.info("FAISS index created successfully")
        except Exception as e:
            logger.error(f"Error creating FAISS index: {e}")
            raise
    
    def add_documents(self, documents: List[Dict]) -> None:
        """
        Add documents with embeddings to the index.
        
        Args:
            documents: List of document dicts with 'embedding' key
        """
        if self.index is None:
            self.create_index()
        
        try:
            # Extract embeddings
            embeddings = np.array([doc['embedding'] for doc in documents], dtype=np.float32)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to index
            self.index.add(embeddings)
            
            # Store document metadata (without embeddings to save memory)
            for doc in documents:
                doc_copy = {k: v for k, v in doc.items() if k != 'embedding'}
                self.documents.append(doc_copy)
            
            logger.info(f"Added {len(documents)} documents to index. Total: {self.index.ntotal}")
        except Exception as e:
            logger.error(f"Error adding documents to index: {e}")
            raise
    
    def search(self, query_embedding: np.ndarray, k: int = 5, 
               threshold: Optional[float] = None) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            threshold: Similarity threshold (optional)
            
        Returns:
            List of similar documents with scores
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty or not initialized")
            return []
        
        try:
            # Normalize query embedding
            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            faiss.normalize_L2(query_embedding)
            
            # Search
            k = min(k, self.index.ntotal)
            distances, indices = self.index.search(query_embedding, k)
            
            # Convert distances to similarity scores (for L2 distance on normalized vectors)
            # similarity = 1 - (distance^2 / 2)
            similarities = 1 - (distances[0] ** 2 / 2)
            
            # Build results
            results = []
            threshold = threshold or config.rag_similarity_threshold
            
            for idx, similarity in zip(indices[0], similarities):
                if idx != -1 and similarity >= threshold:
                    doc = self.documents[idx].copy()
                    doc['similarity'] = float(similarity)
                    results.append(doc)
            
            logger.debug(f"Found {len(results)} results above threshold {threshold}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            return []
    
    def save_index(self, custom_path: Optional[str] = None) -> None:
        """
        Save the FAISS index and documents to disk.
        
        Args:
            custom_path: Custom path to save index (optional)
        """
        if self.index is None:
            logger.warning("No index to save")
            return
        
        save_path = Path(custom_path) if custom_path else self.index_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save FAISS index
            index_file = str(save_path) + '.faiss'
            faiss.write_index(self.index, index_file)
            
            # Save documents metadata
            docs_file = str(save_path) + '.pkl'
            with open(docs_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'dimension': self.dimension
                }, f)
            
            logger.info(f"Index saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise
    
    def load_index(self, custom_path: Optional[str] = None) -> bool:
        """
        Load the FAISS index and documents from disk.
        
        Args:
            custom_path: Custom path to load index from (optional)
            
        Returns:
            True if successful, False otherwise
        """
        load_path = Path(custom_path) if custom_path else self.index_path
        index_file = str(load_path) + '.faiss'
        docs_file = str(load_path) + '.pkl'
        
        if not Path(index_file).exists() or not Path(docs_file).exists():
            logger.warning(f"Index files not found at {load_path}")
            return False
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_file)
            
            # Load documents metadata
            with open(docs_file, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.dimension = data['dimension']
            
            self._is_trained = True
            logger.info(f"Index loaded from {load_path}. Contains {len(self.documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            return False
    
    def clear_index(self) -> None:
        """Clear the index and all documents."""
        self.index = None
        self.documents = []
        self._is_trained = False
        logger.info("Index cleared")
    
    @property
    def document_count(self) -> int:
        """Get the number of documents in the index."""
        return len(self.documents)
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with stats
        """
        return {
            'document_count': self.document_count,
            'dimension': self.dimension,
            'is_trained': self._is_trained,
            'index_size': self.index.ntotal if self.index else 0
        }
