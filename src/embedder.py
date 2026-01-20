"""
Embedder Module
Handles text embedding using sentence-transformers.
"""

from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger

from src.config import config


class Embedder:
    """
    Text embedding generator using sentence-transformers.
    Converts text into dense vector representations for semantic search.
    """
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize the embedder with a sentence-transformer model.
        
        Args:
            model_name: Name of the sentence-transformer model
            device: Device to run the model on ('cpu' or 'cuda')
        """
        self.model_name = model_name or config.embedding_model_name
        self.device = device or config.embedding_device
        self.model: Optional[SentenceTransformer] = None
        self._embedding_dim: Optional[int] = None
        
    def load_model(self) -> None:
        """Load the sentence-transformer model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            
            # Get embedding dimension
            test_embedding = self.model.encode("test", show_progress_bar=False)
            self._embedding_dim = len(test_embedding)
            
            logger.info(f"Model loaded successfully. Embedding dimension: {self._embedding_dim}")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        if self._embedding_dim is None:
            if self.model is None:
                self.load_model()
            # Dimension should be set after loading
        return self._embedding_dim or 384  # Default fallback
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        if self.model is None:
            self.load_model()
        
        try:
            embedding = self.model.encode(text, show_progress_bar=False, convert_to_numpy=True)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            Array of embeddings
        """
        if self.model is None:
            self.load_model()
        
        batch_size = batch_size or config.embedding_batch_size
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts...")
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def embed_documents(self, documents: List[dict]) -> List[dict]:
        """
        Generate embeddings for a list of document dictionaries.
        
        Args:
            documents: List of document dictionaries with 'text' key
            
        Returns:
            Documents with added 'embedding' key
        """
        texts = [doc['text'] for doc in documents]
        embeddings = self.embed_batch(texts)
        
        # Add embeddings to documents
        for doc, embedding in zip(documents, embeddings):
            doc['embedding'] = embedding
        
        return documents
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0 to 1)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)
