"""
Application Controller
Central orchestrator for all application components.
"""

import sys
from pathlib import Path
from typing import Optional, Callable, List

from loguru import logger

from config.settings import config
from ingestion.pdf_reader import PDFReader
from ingestion.docx_reader import DOCXReader
from ingestion.chunker import TextChunker
from embeddings.embedder import Embedder
from embeddings.vector_store import VectorStore
from retrieval.local_search import LocalSearch
from retrieval.online_search import OnlineSearch
from retrieval.ranker import Ranker
from suggestion.autocomplete import Autocomplete
from suggestion.text_replacer import TextReplacer


class ApplicationController:
    """
    Main application controller.
    Manages all components and coordinates their interactions.
    """
    
    def __init__(self):
        """Initialize the application controller."""
        logger.info("Initializing Application Controller")
        
        # Document processing components
        self.pdf_reader = PDFReader()
        self.docx_reader = DOCXReader()
        self.chunker = TextChunker(
            chunk_size=config.chunk_size,
            overlap=config.chunk_overlap
        )
        
        # Embedding and search components
        self.embedder: Optional[Embedder] = None
        self.vector_store: Optional[VectorStore] = None
        self.local_search: Optional[LocalSearch] = None
        self.online_search: Optional[OnlineSearch] = None
        self.ranker: Optional[Ranker] = None
        
        # Suggestion components
        self.autocomplete: Optional[Autocomplete] = None
        self.text_replacer: Optional[TextReplacer] = None
        
        # State
        self._is_initialized = False
        
        logger.info("Application Controller created")
    
    def initialize(self) -> bool:
        """
        Initialize core components (embedder, vector store, etc.).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Initializing core components...")
            
            # Initialize embedder
            logger.info("Loading embedding model...")
            self.embedder = Embedder()
            self.embedder.load_model()
            
            # Initialize vector store
            logger.info("Initializing vector store...")
            self.vector_store = VectorStore()
            
            # Try to load existing index
            if not self.vector_store.load():
                logger.info("No existing index found, will create on document load")
                self.vector_store.create_index()
            
            # Initialize search components
            self.local_search = LocalSearch(self.embedder, self.vector_store)
            
            if config.online_search_enabled:
                self.online_search = OnlineSearch(cache_enabled=True)
            
            self.ranker = Ranker()
            
            # Initialize suggestion components
            self.autocomplete = Autocomplete(
                self.local_search,
                self.online_search,
                self.ranker
            )
            
            self.text_replacer = TextReplacer(
                self.local_search,
                self.online_search,
                self.ranker
            )
            
            self._is_initialized = True
            logger.info("✓ Core components initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize core components: {e}")
            return False
    
    def index_documents(
        self,
        folder_path: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> bool:
        """
        Index all documents in a folder.
        
        Args:
            folder_path: Path to folder containing documents
            progress_callback: Optional callback for progress updates (progress%, message)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            folder = Path(folder_path)
            
            if not folder.exists():
                logger.error(f"Folder does not exist: {folder_path}")
                return False
            
            logger.info(f"Indexing documents from: {folder_path}")
            
            if progress_callback:
                progress_callback(10, "Scanning for documents...")
            
            # Find all supported documents
            documents = []
            for fmt in config.supported_formats:
                found = list(folder.glob(f"*.{fmt}"))
                documents.extend(found)
            
            logger.info(f"Found {len(documents)} documents to process")
            
            if not documents:
                logger.warning("No documents found")
                return False
            
            if progress_callback:
                progress_callback(20, f"Processing {len(documents)} documents...")
            
            # Process each document
            all_chunks = []
            processed_count = 0
            
            for doc_path in documents:
                try:
                    logger.info(f"Processing: {doc_path.name}")
                    
                    # Extract text based on file type
                    if doc_path.suffix.lower() == '.pdf':
                        text = self.pdf_reader.extract_text(doc_path)
                    elif doc_path.suffix.lower() in ['.docx', '.doc']:
                        text = self.docx_reader.extract_text(doc_path)
                    elif doc_path.suffix.lower() == '.txt':
                        text = doc_path.read_text(encoding='utf-8')
                    else:
                        logger.warning(f"Unsupported format: {doc_path.suffix}")
                        continue
                    
                    if not text:
                        logger.warning(f"No text extracted from {doc_path.name}")
                        continue
                    
                    # Chunk the text
                    metadata = {
                        'file_name': doc_path.name,
                        'file_path': str(doc_path),
                        'file_type': doc_path.suffix[1:]
                    }
                    
                    chunks = self.chunker.chunk_text(text, metadata)
                    all_chunks.extend(chunks)
                    
                    processed_count += 1
                    progress = 20 + int((processed_count / len(documents)) * 50)
                    
                    if progress_callback:
                        progress_callback(
                            progress,
                            f"Processed {processed_count}/{len(documents)} documents..."
                        )
                    
                except Exception as e:
                    logger.error(f"Error processing {doc_path.name}: {e}")
                    continue
            
            if not all_chunks:
                logger.error("No chunks created from documents")
                return False
            
            logger.info(f"Created {len(all_chunks)} chunks from {processed_count} documents")
            
            if progress_callback:
                progress_callback(70, "Generating embeddings...")
            
            # Generate embeddings
            chunk_texts = [chunk['text'] for chunk in all_chunks]
            embeddings = self.embedder.encode(chunk_texts)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            
            if progress_callback:
                progress_callback(85, "Building search index...")
            
            # Clear existing index and add new documents
            self.vector_store.clear()
            self.vector_store.create_index()
            self.vector_store.add_documents(embeddings, all_chunks)
            
            # Save index
            self.vector_store.save()
            
            if progress_callback:
                progress_callback(100, "Indexing complete!")
            
            logger.info("✓ Document indexing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            return False
    
    def get_autocomplete(self) -> Optional[Autocomplete]:
        """Get autocomplete instance."""
        return self.autocomplete
    
    def get_text_replacer(self) -> Optional[TextReplacer]:
        """Get text replacer instance."""
        return self.text_replacer
    
    def get_stats(self) -> dict:
        """
        Get application statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'initialized': self._is_initialized,
            'documents_indexed': 0,
            'embedding_model': None,
            'online_search_enabled': config.online_search_enabled
        }
        
        if self.vector_store:
            store_stats = self.vector_store.get_stats()
            stats['documents_indexed'] = store_stats['num_documents']
        
        if self.embedder:
            stats['embedding_model'] = self.embedder.model_name
        
        return stats
