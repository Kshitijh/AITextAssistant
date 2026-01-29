"""
Unit Tests for Retrieval System
"""

import pytest
import numpy as np

from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.local_search import LocalSearch
from retrieval.online_search import OnlineSearch
from retrieval.ranker import Ranker


class TestLocalSearch:
    """Test local search functionality."""
    
    @pytest.fixture
    def local_search(self, tmp_path):
        """Create local search instance with test data."""
        # Create embedder
        embedder = Embedder()
        embedder.load_model()
        
        # Create vector store
        index_path = tmp_path / "test_index"
        vector_store = VectorStore(index_path=str(index_path))
        vector_store.create_index()
        
        # Add test documents
        texts = [
            "Python is a programming language.",
            "Machine learning uses neural networks.",
            "Data science involves statistics."
        ]
        embeddings = embedder.encode(texts)
        documents = [
            {'text': text, 'file_name': f'doc{i}.txt'}
            for i, text in enumerate(texts)
        ]
        vector_store.add_documents(embeddings, documents)
        
        return LocalSearch(embedder, vector_store)
    
    def test_search(self, local_search):
        """Test searching."""
        results = local_search.search("programming", top_k=2)
        
        assert isinstance(results, list)
        # Results may be empty if below threshold
    
    def test_get_context(self, local_search):
        """Test context retrieval."""
        context = local_search.get_context("Python programming")
        
        assert isinstance(context, str)


class TestOnlineSearch:
    """Test online search functionality."""
    
    @pytest.fixture
    def online_search(self, tmp_path):
        """Create online search instance."""
        return OnlineSearch(cache_enabled=False)
    
    def test_search(self, online_search):
        """Test online searching."""
        # This will make actual API calls - use sparingly
        results = online_search.search("Python programming language")
        
        assert isinstance(results, list)
        # May be empty if Wikipedia is unreachable


class TestRanker:
    """Test ranker functionality."""
    
    def test_rank_results(self):
        """Test result ranking."""
        ranker = Ranker()
        
        local_results = [
            {'text': 'Local result 1', 'source': 'local', 'similarity_score': 0.9}
        ]
        online_results = [
            {'text': 'Online result 1', 'source': 'wikipedia', 'similarity_score': 0.0}
        ]
        
        ranked = ranker.rank_results(local_results, online_results)
        
        assert len(ranked) == 2
        assert ranked[0]['source'] == 'local'  # Local should be first


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
