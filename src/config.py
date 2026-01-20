"""
Configuration Module
Handles loading and managing application configuration from YAML file.
"""

import os
import yaml
from typing import Dict, Any, List
from pathlib import Path
from loguru import logger


class Config:
    """
    Configuration manager for the AI Text Assistant.
    Loads settings from config.yaml and provides easy access to configuration values.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration from YAML file.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load_config()
        self._ensure_directories()
        
    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found: {self.config_path}")
                self._create_default_config()
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            
            logger.info(f"Configuration loaded from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise
    
    def _create_default_config(self) -> None:
        """Create default configuration file if it doesn't exist."""
        logger.info("Creating default configuration file...")
        # Default config would be created here if needed
        
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.documents_folder,
            Path(self.vector_store_path).parent,
            Path(self.logging_file_path).parent,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.
        
        Args:
            key: Configuration key in dot notation (e.g., 'llm.temperature')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
                
        return value if value is not None else default
    
    # Document Processing
    @property
    def documents_folder(self) -> str:
        return self.get('documents.folder_path', './data')
    
    @property
    def supported_formats(self) -> List[str]:
        return self.get('documents.supported_formats', ['pdf', 'docx', 'txt'])
    
    @property
    def chunk_size(self) -> int:
        return self.get('documents.chunk_size', 750)
    
    @property
    def chunk_overlap(self) -> int:
        return self.get('documents.chunk_overlap', 100)
    
    # Embedding
    @property
    def embedding_model_name(self) -> str:
        return self.get('embedding.model_name', 'sentence-transformers/all-MiniLM-L6-v2')
    
    @property
    def embedding_device(self) -> str:
        return self.get('embedding.device', 'cpu')
    
    @property
    def embedding_batch_size(self) -> int:
        return self.get('embedding.batch_size', 32)
    
    # Vector Store
    @property
    def vector_store_path(self) -> str:
        return self.get('vector_store.index_path', './models/faiss_index')
    
    @property
    def vector_dimension(self) -> int:
        return self.get('vector_store.dimension', 384)
    
    # LLM
    @property
    def llm_backend(self) -> str:
        return self.get('llm.backend', 'gpt4all')
    
    @property
    def llm_model_path(self) -> str:
        return self.get('llm.model_path', './models/gpt4all-model.bin')
    
    @property
    def llm_model_name(self) -> str:
        return self.get('llm.model_name', 'orca-mini-3b-gguf2-q4_0.gguf')
    
    @property
    def llm_temperature(self) -> float:
        return self.get('llm.temperature', 0.7)
    
    @property
    def llm_max_tokens(self) -> int:
        return self.get('llm.max_tokens', 100)
    
    @property
    def llm_top_k(self) -> int:
        return self.get('llm.top_k', 40)
    
    @property
    def llm_top_p(self) -> float:
        return self.get('llm.top_p', 0.9)
    
    # RAG
    @property
    def rag_top_k(self) -> int:
        return self.get('rag.top_k_results', 3)
    
    @property
    def rag_similarity_threshold(self) -> float:
        return self.get('rag.similarity_threshold', 0.5)
    
    @property
    def rag_max_context_length(self) -> int:
        return self.get('rag.max_context_length', 1500)
    
    # Keystroke Listener
    @property
    def listener_context_window(self) -> int:
        return self.get('listener.context_window_size', 200)
    
    @property
    def listener_trigger_threshold(self) -> int:
        return self.get('listener.trigger_threshold', 10)
    
    @property
    def listener_debounce_ms(self) -> int:
        return self.get('listener.debounce_ms', 300)
    
    @property
    def listener_excluded_apps(self) -> List[str]:
        return self.get('listener.excluded_apps', [])
    
    # Overlay
    @property
    def overlay_font_size(self) -> int:
        return self.get('overlay.font_size', 12)
    
    @property
    def overlay_font_family(self) -> str:
        return self.get('overlay.font_family', 'Consolas')
    
    @property
    def overlay_opacity(self) -> float:
        return self.get('overlay.opacity', 0.95)
    
    @property
    def overlay_max_suggestions(self) -> int:
        return self.get('overlay.max_suggestions', 3)
    
    # UI
    @property
    def ui_theme(self) -> str:
        return self.get('ui.theme', 'dark')
    
    @property
    def ui_window_width(self) -> int:
        return self.get('ui.window_width', 800)
    
    @property
    def ui_window_height(self) -> int:
        return self.get('ui.window_height', 600)
    
    # Logging
    @property
    def logging_level(self) -> str:
        return self.get('logging.level', 'INFO')
    
    @property
    def logging_file_path(self) -> str:
        return self.get('logging.file_path', './logs/app.log')
    
    @property
    def performance_num_threads(self) -> int:
        return self.get('performance.num_threads', 4)
    
    @property
    def performance_cache_embeddings(self) -> bool:
        return self.get('performance.cache_embeddings', True)


# Global config instance
config = Config()
