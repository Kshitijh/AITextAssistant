"""
Configuration Settings
Central configuration management for the application.
"""

import os
from pathlib import Path
from typing import List
import yaml
from loguru import logger


class Settings:
    """Application configuration manager."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize settings from YAML configuration file.
        
        Args:
            config_path: Path to the configuration file
        """
        if config_path is None:
            # Default to config.yaml in project root
            self.config_path = Path(__file__).parent.parent / "config.yaml"
        else:
            self.config_path = Path(config_path)
        
        self._config = {}
        self.load_config()
        
    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}. Using defaults.")
                self._set_defaults()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            
            logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            self._set_defaults()
    
    def _set_defaults(self) -> None:
        """Set default configuration values."""
        self._config = {
            'documents': {
                'folder_path': './data',
                'supported_formats': ['pdf', 'docx', 'txt'],
                'chunk_size': 512,
                'chunk_overlap': 50
            },
            'embedding': {
                'model_name': 'sentence-transformers/all-MiniLM-L6-v2',
                'device': 'cpu',
                'batch_size': 32
            },
            'vector_store': {
                'index_path': './models/faiss_index',
                'dimension': 384,
                'metric': 'cosine'
            },
            'retrieval': {
                'top_k_results': 5,
                'similarity_threshold': 0.3,
                'max_context_length': 1500
            },
            'suggestion': {
                'context_window_size': 100,
                'trigger_threshold': 3,
                'debounce_ms': 500
            },
            'online_search': {
                'enabled': True,
                'cache_enabled': True,
                'cache_path': './models/online_cache.pkl',
                'max_results': 3
            },
            'logging': {
                'level': 'INFO',
                'file_path': './logs/app.log'
            }
        }
    
    # Document settings
    @property
    def documents_folder(self) -> Path:
        """Get documents folder path."""
        return Path(self._config['documents']['folder_path'])
    
    @property
    def supported_formats(self) -> List[str]:
        """Get list of supported document formats."""
        return self._config['documents']['supported_formats']
    
    @property
    def chunk_size(self) -> int:
        """Get text chunk size for processing."""
        return self._config['documents']['chunk_size']
    
    @property
    def chunk_overlap(self) -> int:
        """Get chunk overlap size."""
        return self._config['documents']['chunk_overlap']
    
    # Embedding settings
    @property
    def embedding_model(self) -> str:
        """Get embedding model name."""
        return self._config['embedding']['model_name']
    
    @property
    def embedding_device(self) -> str:
        """Get device for embedding model."""
        return self._config['embedding']['device']
    
    @property
    def embedding_batch_size(self) -> int:
        """Get batch size for embedding generation."""
        return self._config['embedding']['batch_size']
    
    # Vector store settings
    @property
    def vector_store_path(self) -> Path:
        """Get vector store index path."""
        return Path(self._config['vector_store']['index_path'])
    
    @property
    def vector_dimension(self) -> int:
        """Get embedding dimension."""
        return self._config['vector_store']['dimension']
    
    # Retrieval settings
    @property
    def top_k_results(self) -> int:
        """Get number of top results to retrieve."""
        return self._config['retrieval']['top_k_results']
    
    @property
    def similarity_threshold(self) -> float:
        """Get minimum similarity threshold."""
        return self._config['retrieval']['similarity_threshold']
    
    @property
    def max_context_length(self) -> int:
        """Get maximum context length."""
        return self._config['retrieval']['max_context_length']
    
    # Suggestion settings
    @property
    def context_window_size(self) -> int:
        """Get context window size for suggestions."""
        return self._config['suggestion']['context_window_size']
    
    @property
    def trigger_threshold(self) -> int:
        """Get trigger threshold for suggestions."""
        return self._config['suggestion']['trigger_threshold']
    
    @property
    def debounce_ms(self) -> int:
        """Get debounce time in milliseconds."""
        return self._config['suggestion']['debounce_ms']
    
    # Online search settings
    @property
    def online_search_enabled(self) -> bool:
        """Check if online search is enabled."""
        return self._config['online_search']['enabled']
    
    @property
    def online_cache_path(self) -> Path:
        """Get online search cache path."""
        return Path(self._config['online_search']['cache_path'])
    
    @property
    def online_max_results(self) -> int:
        """Get maximum online search results."""
        return self._config['online_search']['max_results']
    
    # Logging settings
    @property
    def logging_level(self) -> str:
        """Get logging level."""
        return self._config['logging']['level']
    
    @property
    def logging_file_path(self) -> Path:
        """Get log file path."""
        return Path(self._config['logging']['file_path'])


# Global settings instance
config = Settings()
