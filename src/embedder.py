"""
Embedder Module
Handles text embedding using TF-IDF (lightweight alternative to sentence-transformers).
"""

from typing import List, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from pathlib import Path
from loguru import logger

from src.config import config


class Embedder:
    """
    Text embedding generator using TF-IDF vectorization.
    Lightweight alternative to sentence-transformers - no PyTorch required!
    """
    
    def __init__(self, model_name: Optional[str] = None, device: Optional[str] = None):
        """
        Initialize the embedder with TF-IDF vectorizer.
        
        Args:
            model_name: Not used in TF-IDF version (kept for compatibility)
            device: Not used in TF-IDF version (kept for compatibility)
        """
        self.model_name = "TF-IDF"
        self.device = "cpu"
        self.vectorizer: Optional[TfidfVectorizer] = None
        self._embedding_dim: Optional[int] = None
        self._is_fitted = False
        
    def load_model(self) -> None:
        """Initialize the TF-IDF vectorizer."""
        try:
            logger.info("Initializing TF-IDF vectorizer...")
            
            # Create TF-IDF vectorizer with optimized parameters
            self.vectorizer = TfidfVectorizer(
                max_features=384,  # Match original embedding dimension
                ngram_range=(1, 2),  # Unigrams and bigrams
                min_df=1,
                max_df=0.95,
                sublinear_tf=True,
                strip_accents='unicode',
                lowercase=True
            )
            
            self._embedding_dim = 384
            logger.info("TF-IDF vectorizer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing TF-IDF vectorizer: {e}")
            raise
    
    @property
    def embedding_dimension(self) -> int:
        """Get the dimension of the embeddings."""
        return self._embedding_dim or 384
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as numpy array
        """
        if self.vectorizer is None:
            self.load_model()
        
        if not self._is_fitted:
            logger.warning("Vectorizer not fitted yet. Fitting on single text.")
            self.vectorizer.fit([text])
            self._is_fitted = True
        
        try:
            embedding = self.vectorizer.transform([text]).toarray()[0]
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of input texts
            batch_size: Not used (kept for compatibility)
            
        Returns:
            Array of embeddings
        """
        if self.vectorizer is None:
            self.load_model()
        
        try:
            logger.info(f"Fitting TF-IDF on {len(texts)} texts...")
            
            # Fit on all texts
            self.vectorizer.fit(texts)
            self._is_fitted = True
            
            # Transform to embeddings
            logger.info(f"Generating TF-IDF embeddings...")
            embeddings = self.vectorizer.transform(texts).toarray()
            
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
        # Reshape for sklearn
        emb1 = embedding1.reshape(1, -1)
        emb2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(emb1, emb2)[0][0]
        return float(similarity)
    
    def save_vectorizer(self, path: str) -> None:
        """Save the fitted vectorizer to disk."""
        if self.vectorizer and self._is_fitted:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(self.vectorizer, path)
            logger.info(f"Vectorizer saved to {path}")
    
    def load_vectorizer(self, path: str) -> bool:
        """Load a fitted vectorizer from disk."""
        if Path(path).exists():
            try:
                self.vectorizer = joblib.load(path)
                self._is_fitted = True
                logger.info(f"Vectorizer loaded from {path}")
                return True
            except Exception as e:
                logger.error(f"Error loading vectorizer: {e}")
                return False
        return False
