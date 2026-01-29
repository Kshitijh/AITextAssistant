"""
Vector Store Module
Handles FAISS-based vector database for efficient similarity search.
"""

import os
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
import faiss
from loguru import logger

from config.settings import config


class VectorStore:
    """
    FAISS-based vector store for efficient semantic search.
    Supports saving/loading and incremental updates.
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
        
        logger.info(f"Vector store initialized with dimension: {self.dimension}")
    
    def create_index(self) -> None:
        """Create a new FAISS index for cosine similarity search."""
        try:
            logger.info("Creating FAISS index...")
            
            # Use IndexFlatIP for inner product (cosine similarity with normalized vectors)
            self.index = faiss.IndexFlatIP(self.dimension)
            
            # Optionally wrap with IDMap for deletion support
            self.index = faiss.IndexIDMap(self.index)
            
            self._is_trained = True
            logger.info("FAISS index created successfully")
            
        except Exception as e:
            logger.error(f"Error creating FAISS index: {e}")
            raise
    
    def add_documents(self, embeddings: np.ndarray, documents: List[Dict]) -> None:
        """
        Add documents and their embeddings to the index.
        
        Args:
            embeddings: Numpy array of embeddings (shape: [n_docs, dimension])
            documents: List of document metadata dictionaries
        """
        if self.index is None:
            logger.info("Index not created. Creating now...")
            self.create_index()
        
        if len(embeddings) != len(documents):
            raise ValueError("Number of embeddings must match number of documents")
        
        try:
            # Convert to float32 if needed
            if embeddings.dtype != np.float32:
                embeddings = embeddings.astype(np.float32)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Generate IDs
            start_id = len(self.documents)
            ids = np.arange(start_id, start_id + len(documents), dtype=np.int64)
            
            # Add to index
            self.index.add_with_ids(embeddings, ids)
            
            # Store documents
            self.documents.extend(documents)
            
            logger.info(f"Added {len(documents)} documents to index. Total: {len(self.documents)}")
            
        except Exception as e:
            logger.error(f"Error adding documents to index: {e}")
            raise
    
    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of tuples (document, similarity_score)
        """
        if self.index is None or len(self.documents) == 0:
            logger.warning("Index is empty or not created")
            return []
        
        try:
            # Ensure query is 2D and float32
            if query_embedding.ndim == 1:
                query_embedding = query_embedding.reshape(1, -1)
            
            if query_embedding.dtype != np.float32:
                query_embedding = query_embedding.astype(np.float32)
            
            # Normalize query
            faiss.normalize_L2(query_embedding)
            
            # Search
            top_k = min(top_k, len(self.documents))
            distances, indices = self.index.search(query_embedding, top_k)
            
            # Prepare results
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx >= 0 and idx < len(self.documents):
                    # Distance is inner product (higher is better for cosine similarity)
                    similarity_score = float(dist)
                    results.append((self.documents[idx], similarity_score))
            
            logger.debug(f"Search returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error searching index: {e}")
            return []
    
    def save(self) -> None:
        """Save the index and documents to disk."""
        try:
            # Create directory if it doesn't exist
            self.index_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save FAISS index
            index_file = str(self.index_path) + ".index"
            faiss.write_index(self.index, index_file)
            
            # Save documents metadata
            docs_file = str(self.index_path) + ".docs"
            with open(docs_file, 'wb') as f:
                pickle.dump(self.documents, f)
            
            logger.info(f"Vector store saved to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            raise
    
    def load(self) -> bool:
        """
        Load the index and documents from disk.
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            index_file = str(self.index_path) + ".index"
            docs_file = str(self.index_path) + ".docs"
            
            if not os.path.exists(index_file) or not os.path.exists(docs_file):
                logger.warning(f"Index files not found at {self.index_path}")
                return False
            
            # Load FAISS index
            self.index = faiss.read_index(index_file)
            
            # Load documents
            with open(docs_file, 'rb') as f:
                self.documents = pickle.load(f)
            
            self._is_trained = True
            logger.info(f"Vector store loaded from {self.index_path}. Documents: {len(self.documents)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def clear(self) -> None:
        """Clear the index and all documents."""
        self.index = None
        self.documents = []
        self._is_trained = False
        logger.info("Vector store cleared")
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'num_documents': len(self.documents),
            'dimension': self.dimension,
            'is_trained': self._is_trained,
            'index_path': str(self.index_path)
        }
