"""
AI Text Assistant - Main Entry Point
A local AI-powered writing assistant with document-based autocomplete.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from loguru import logger

from config.settings import config
from app_controller import ApplicationController
from ui.main_window import MainWindow


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
    log_path = config.logging_file_path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        str(log_path),
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
        
        # Create application controller
        logger.info("Creating application controller...")
        controller = ApplicationController()
        
        # Initialize core components
        logger.info("Initializing core components...")
        if not controller.initialize():
            logger.error("Failed to initialize application")
            sys.exit(1)
        
        # Create Qt application
        logger.info("Creating UI application...")
        app = QApplication(sys.argv)
        app.setApplicationName("AI Text Assistant")
        app.setOrganizationName("AITextAssistant")
        
        # Create and show main window
        logger.info("Creating main window...")
        window = MainWindow(controller)
        window.show()
        
        logger.info("Application started successfully")
        logger.info("=" * 60)
        
        # Run application
        sys.exit(app.exec())
        
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
