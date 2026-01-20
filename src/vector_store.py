"""
Vector Store Module
Handles vector database for semantic search using sklearn's NearestNeighbors.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.neighbors import NearestNeighbors
from loguru import logger

from src.config import config


class VectorStore:
    """
    Sklearn NearestNeighbors-based vector store for efficient semantic search.
    Lightweight alternative to FAISS - no external dependencies!
    """
    
    def __init__(self, index_path: Optional[str] = None, dimension: Optional[int] = None):
        """
        Initialize the vector store.
        
        Args:
            index_path: Path to save/load the index
            dimension: Dimension of the embedding vectors
        """
        self.index_path = Path(index_path or config.vector_store_path)
        self.dimension = dimension or config.vector_dimension
        self.index: Optional[NearestNeighbors] = None
        self.documents: List[Dict] = []
        self.embeddings_matrix: Optional[np.ndarray] = None
        self._is_trained = False
        
    def create_index(self) -> None:
        """Create a new NearestNeighbors index."""
        try:
            logger.info(f"Creating NearestNeighbors index")
            
            # Use cosine similarity
            self.index = NearestNeighbors(
                n_neighbors=10,
                algorithm='brute',
                metric='cosine'
            )
            
            logger.info("NearestNeighbors index created successfully")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
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
            
            # Store embeddings matrix
            if self.embeddings_matrix is None:
                self.embeddings_matrix = embeddings
            else:
                self.embeddings_matrix = np.vstack([self.embeddings_matrix, embeddings])
            
            # Fit the index
            self.index.fit(self.embeddings_matrix)
            self._is_trained = True
            
            # Store document metadata (without embeddings to save memory)
            for doc in documents:
                doc_copy = {k: v for k, v in doc.items() if k != 'embedding'}
                self.documents.append(doc_copy)
            
            logger.info(f"Added {len(documents)} documents to index. Total: {len(self.documents)}")
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
        if self.index is None or not self._is_trained or len(self.documents) == 0:
            logger.warning("Index is empty or not initialized")
            return []
        
        try:
            # Reshape query
            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            
            # Search
            k = min(k, len(self.documents))
            distances, indices = self.index.kneighbors(query_embedding, n_neighbors=k)
            
            # Convert distances to similarity scores (1 - cosine distance)
            similarities = 1 - distances[0]
            
            # Build results
            results = []
            threshold = threshold or config.rag_similarity_threshold
            
            for idx, similarity in zip(indices[0], similarities):
                if similarity >= threshold:
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
        Save the index and documents to disk.
        
        Args:
            custom_path: Custom path to save index (optional)
        """
        if self.index is None:
            logger.warning("No index to save")
            return
        
        save_path = Path(custom_path) if custom_path else self.index_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save everything as pickle
            save_file = str(save_path) + '.pkl'
            with open(save_file, 'wb') as f:
                pickle.dump({
                    'index': self.index,
                    'documents': self.documents,
                    'embeddings_matrix': self.embeddings_matrix,
                    'dimension': self.dimension
                }, f)
            
            logger.info(f"Index saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}")
            raise
    
    def load_index(self, custom_path: Optional[str] = None) -> bool:
        """
        Load the index and documents from disk.
        
        Args:
            custom_path: Custom path to load index from (optional)
            
        Returns:
            True if successful, False otherwise
        """
        load_path = Path(custom_path) if custom_path else self.index_path
        load_file = str(load_path) + '.pkl'
        
        if not Path(load_file).exists():
            logger.warning(f"Index file not found at {load_file}")
            return False
        
        try:
            # Load everything from pickle
            with open(load_file, 'rb') as f:
                data = pickle.load(f)
                self.index = data['index']
                self.documents = data['documents']
                self.embeddings_matrix = data['embeddings_matrix']
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
        self.embeddings_matrix = None
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
            'index_size': len(self.documents)
        }
