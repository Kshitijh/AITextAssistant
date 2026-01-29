"""
Embedder Module
Handles text embedding generation using sentence-transformers.
"""

from typing import List, Optional, Union
import numpy as np
from sentence_transformers import SentenceTransformer
from loguru import logger

from config.settings import config


class Embedder:
    """
    Generates embeddings for text using sentence-transformers.
    Provides high-quality semantic representations for similarity search.
    """
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize the embedder.
        
        Args:
            model_name: Name of the sentence-transformers model
            device: Device to use ('cpu' or 'cuda')
        """
        self.model_name = model_name or config.embedding_model
        self.device = device or config.embedding_device
        self.model: Optional[SentenceTransformer] = None
        self._embedding_dim: Optional[int] = None
        
        logger.info(f"Initializing Embedder with model: {self.model_name}")
    
    def load_model(self) -> None:
        """Load the sentence-transformers model."""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self._embedding_dim = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"Model loaded successfully. Embedding dimension: {self._embedding_dim}")
            
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def encode(self, texts: Union[str, List[str]], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Generate embeddings for text(s).
        
        Args:
            texts: Single text string or list of text strings
            batch_size: Batch size for encoding (uses config default if None)
            
        Returns:
            numpy array of embeddings (shape: [n_texts, embedding_dim])
        """
        if self.model is None:
            logger.warning("Model not loaded. Loading now...")
            self.load_model()
        
        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            logger.warning("Empty text list provided")
            return np.array([])
        
        try:
            batch_size = batch_size or config.embedding_batch_size
            
            logger.debug(f"Encoding {len(texts)} texts with batch size {batch_size}")
            
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=len(texts) > 100,
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalize for cosine similarity
            )
            
            logger.debug(f"Generated embeddings shape: {embeddings.shape}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Error encoding texts: {e}")
            raise
    
    def encode_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to encode
            
        Returns:
            1D numpy array of embedding
        """
        embeddings = self.encode([text])
        return embeddings[0] if len(embeddings) > 0 else np.array([])
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        if self._embedding_dim is None:
            if self.model is None:
                self.load_model()
            self._embedding_dim = self.model.get_sentence_embedding_dimension()
        return self._embedding_dim
    
    def is_loaded(self) -> bool:
        """Check if the model is loaded."""
        return self.model is not None
