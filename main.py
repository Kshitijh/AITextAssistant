"""
AI Text Assistant - Main Entry Point
A local AI-powered writing assistant with document-based autocomplete.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from loguru import logger
from src.config import config
from src.ui import run_application


def setup_logging():
    """Configure logging for the application."""
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=config.logging_level
    )
    
    # Add file logger
    log_path = Path(config.logging_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        config.logging_file_path,
        rotation="10 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        level=config.logging_level
    )
    
    logger.info("=" * 60)
    logger.info("AI Text Assistant Starting...")
    logger.info("=" * 60)


def main():
    """Main entry point for the application."""
    try:
        # Setup logging
        setup_logging()
        
        # Log configuration
        logger.info(f"Documents folder: {config.documents_folder}")
        logger.info(f"Vector store path: {config.vector_store_path}")
        logger.info(f"LLM backend: {config.llm_backend}")
        logger.info(f"Embedding model: {config.embedding_model_name}")
        
        # Run the application
        run_application()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
