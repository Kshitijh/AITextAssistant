"""
Unit Tests for Embeddings and Vector Store
"""

import pytest
import numpy as np

from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore


class TestEmbedder:
    """Test embedding functionality."""
    
    @pytest.fixture
    def embedder(self):
        """Create embedder instance for testing."""
        return Embedder()
    
    def test_embedder_initialization(self, embedder):
        """Test embedder can be initialized."""
        assert embedder is not None
        assert embedder.model_name is not None
    
    def test_load_model(self, embedder):
        """Test model loading."""
        embedder.load_model()
        assert embedder.is_loaded()
    
    def test_encode_single_text(self, embedder):
        """Test encoding single text."""
        embedder.load_model()
        embedding = embedder.encode_single("This is a test sentence.")
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == embedder.embedding_dimension
    
    def test_encode_multiple_texts(self, embedder):
        """Test encoding multiple texts."""
        embedder.load_model()
        texts = ["First sentence.", "Second sentence.", "Third sentence."]
        embeddings = embedder.encode(texts)
        
        assert isinstance(embeddings, np.ndarray)
        assert len(embeddings) == 3
        assert embeddings.shape[1] == embedder.embedding_dimension


class TestVectorStore:
    """Test vector store functionality."""
    
    @pytest.fixture
    def vector_store(self, tmp_path):
        """Create vector store instance for testing."""
        index_path = tmp_path / "test_index"
        return VectorStore(index_path=str(index_path), dimension=384)
    
    def test_vector_store_initialization(self, vector_store):
        """Test vector store can be initialized."""
        assert vector_store is not None
        assert vector_store.dimension == 384
    
    def test_create_index(self, vector_store):
        """Test index creation."""
        vector_store.create_index()
        assert vector_store.index is not None
    
    def test_add_and_search(self, vector_store):
        """Test adding documents and searching."""
        vector_store.create_index()
        
        # Create sample embeddings and documents
        embeddings = np.random.rand(5, 384).astype(np.float32)
        documents = [
            {'text': f'Document {i}', 'id': i}
            for i in range(5)
        ]
        
        vector_store.add_documents(embeddings, documents)
        
        # Search
        query = embeddings[0]
        results = vector_store.search(query, top_k=3)
        
        assert len(results) > 0
        assert len(results) <= 3
    
    def test_save_and_load(self, vector_store):
        """Test saving and loading index."""
        vector_store.create_index()
        
        # Add some data
        embeddings = np.random.rand(3, 384).astype(np.float32)
        documents = [{'text': f'Doc {i}'} for i in range(3)]
        vector_store.add_documents(embeddings, documents)
        
        # Save
        vector_store.save()
        
        # Create new store and load
        new_store = VectorStore(
            index_path=str(vector_store.index_path),
            dimension=384
        )
        success = new_store.load()
        
        assert success
        assert len(new_store.documents) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
