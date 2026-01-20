"""
Main UI Module
Desktop application interface for managing the AI Text Assistant.
"""

import sys
import os
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit, QProgressBar,
    QStatusBar, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon
from loguru import logger

from src.config import config
from src.document_loader import DocumentLoader
from src.embedder import Embedder
from src.vector_store import VectorStore
from src.suggestion_engine import SuggestionEngine
from src.keystroke_listener import KeystrokeListener
from src.suggestion_overlay import SuggestionOverlay


class IndexBuilderThread(QThread):
    """Worker thread for building the document index."""
    
    progress = Signal(str)
    finished = Signal(bool, str)
    
    def __init__(self, folder_path: str, embedder: Embedder, vector_store: VectorStore):
        super().__init__()
        self.folder_path = folder_path
        self.embedder = embedder
        self.vector_store = vector_store
        
    def run(self):
        """Build the index in background."""
        try:
            self.progress.emit("Loading documents...")
            
            # Load documents
            loader = DocumentLoader(self.folder_path)
            documents = loader.load_all_documents()
            
            if not documents:
                self.finished.emit(False, "No documents found in folder")
                return
            
            self.progress.emit(f"Loaded {len(documents)} documents. Chunking...")
            
            # Chunk documents
            chunked_docs = loader.chunk_documents(documents)
            self.progress.emit(f"Created {len(chunked_docs)} chunks. Generating embeddings...")
            
            # Generate embeddings
            chunked_docs = self.embedder.embed_documents(chunked_docs)
            self.progress.emit("Embeddings generated. Building index...")
            
            # Clear and rebuild index
            self.vector_store.clear_index()
            self.vector_store.add_documents(chunked_docs)
            
            self.progress.emit("Saving index...")
            self.vector_store.save_index()
            
            self.finished.emit(True, f"Index built successfully with {len(chunked_docs)} chunks")
            
        except Exception as e:
            logger.error(f"Error building index: {e}")
            self.finished.emit(False, f"Error: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.embedder: Optional[Embedder] = None
        self.vector_store: Optional[VectorStore] = None
        self.suggestion_engine: Optional[SuggestionEngine] = None
        self.keystroke_listener: Optional[KeystrokeListener] = None
        self.suggestion_overlay: Optional[SuggestionOverlay] = None
        
        self.is_assistant_running = False
        self.index_builder_thread: Optional[IndexBuilderThread] = None
        
        self._init_components()
        self._setup_ui()
        self._load_existing_index()
        
    def _init_components(self):
        """Initialize core components."""
        try:
            logger.info("Initializing components...")
            
            # Initialize embedder
            self.embedder = Embedder()
            
            # Initialize vector store
            self.vector_store = VectorStore()
            
            # Initialize suggestion engine
            self.suggestion_engine = SuggestionEngine(self.embedder, self.vector_store)
            
            # Initialize keystroke listener
            self.keystroke_listener = KeystrokeListener(callback=self._on_typing_context)
            
            # Initialize suggestion overlay
            self.suggestion_overlay = SuggestionOverlay()
            self.suggestion_overlay.accepted.connect(self._on_suggestion_accepted)
            self.suggestion_overlay.dismissed.connect(self._on_suggestion_dismissed)
            
            logger.info("Components initialized")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            QMessageBox.critical(self, "Error", f"Failed to initialize components: {e}")
    
    def _setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("AI Text Assistant")
        self.setGeometry(100, 100, config.ui_window_width, config.ui_window_height)
        
        # Apply theme
        self._apply_theme()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("🤖 AI Text Assistant")
        title_font = QFont("Arial", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Document folder section
        folder_group = self._create_folder_section()
        main_layout.addWidget(folder_group)
        
        # Index management section
        index_group = self._create_index_section()
        main_layout.addWidget(index_group)
        
        # Assistant control section
        control_group = self._create_control_section()
        main_layout.addWidget(control_group)
        
        # Log section
        log_group = self._create_log_section()
        main_layout.addWidget(log_group)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        central_widget.setLayout(main_layout)
    
    def _apply_theme(self):
        """Apply color theme to the application."""
        if config.ui_theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QPushButton {
                    background-color: #0d47a1;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:pressed {
                    background-color: #0a3d91;
                }
                QPushButton:disabled {
                    background-color: #555555;
                    color: #999999;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #555555;
                    border-radius: 4px;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        # Light theme is default
    
    def _create_folder_section(self) -> QGroupBox:
        """Create document folder selection section."""
        group = QGroupBox("📁 Document Folder")
        layout = QVBoxLayout()
        
        # Folder path display
        self.folder_label = QLabel(config.documents_folder)
        self.folder_label.setWordWrap(True)
        layout.addWidget(self.folder_label)
        
        # Select folder button
        select_btn = QPushButton("Select Folder")
        select_btn.clicked.connect(self._select_folder)
        layout.addWidget(select_btn)
        
        group.setLayout(layout)
        return group
    
    def _create_index_section(self) -> QGroupBox:
        """Create index management section."""
        group = QGroupBox("🔨 Index Management")
        layout = QVBoxLayout()
        
        # Index status
        self.index_status_label = QLabel("Index: Not loaded")
        layout.addWidget(self.index_status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.build_index_btn = QPushButton("Build Index")
        self.build_index_btn.clicked.connect(self._build_index)
        btn_layout.addWidget(self.build_index_btn)
        
        self.load_index_btn = QPushButton("Load Index")
        self.load_index_btn.clicked.connect(self._load_existing_index)
        btn_layout.addWidget(self.load_index_btn)
        
        layout.addLayout(btn_layout)
        group.setLayout(layout)
        return group
    
    def _create_control_section(self) -> QGroupBox:
        """Create assistant control section."""
        group = QGroupBox("🎯 Assistant Control")
        layout = QVBoxLayout()
        
        # Status label
        self.assistant_status_label = QLabel("Status: Stopped")
        self.assistant_status_label.setAlignment(Qt.AlignCenter)
        font = QFont("Arial", 12, QFont.Bold)
        self.assistant_status_label.setFont(font)
        layout.addWidget(self.assistant_status_label)
        
        # Start/Stop button
        self.toggle_assistant_btn = QPushButton("Start Assistant")
        self.toggle_assistant_btn.clicked.connect(self._toggle_assistant)
        self.toggle_assistant_btn.setMinimumHeight(50)
        layout.addWidget(self.toggle_assistant_btn)
        
        # Info label
        info_label = QLabel("The assistant will monitor your typing and provide suggestions in real-time.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #888888; font-size: 10pt;")
        layout.addWidget(info_label)
        
        group.setLayout(layout)
        return group
    
    def _create_log_section(self) -> QGroupBox:
        """Create log display section."""
        group = QGroupBox("📋 Activity Log")
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        group.setLayout(layout)
        return group
    
    def _select_folder(self):
        """Open folder selection dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Document Folder",
            config.documents_folder
        )
        
        if folder:
            self.folder_label.setText(folder)
            config._config['documents']['folder_path'] = folder
            self._log(f"Folder selected: {folder}")
    
    def _build_index(self):
        """Build the document index."""
        if self.index_builder_thread and self.index_builder_thread.isRunning():
            QMessageBox.warning(self, "Warning", "Index building is already in progress")
            return
        
        folder_path = self.folder_label.text()
        
        if not Path(folder_path).exists():
            QMessageBox.critical(self, "Error", "Selected folder does not exist")
            return
        
        # Disable buttons
        self.build_index_btn.setEnabled(False)
        self.load_index_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        # Start index building thread
        self.index_builder_thread = IndexBuilderThread(
            folder_path,
            self.embedder,
            self.vector_store
        )
        self.index_builder_thread.progress.connect(self._log)
        self.index_builder_thread.finished.connect(self._on_index_built)
        self.index_builder_thread.start()
        
        self._log("Starting index build...")
    
    def _on_index_built(self, success: bool, message: str):
        """Handle index build completion."""
        self.build_index_btn.setEnabled(True)
        self.load_index_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        self._log(message)
        
        if success:
            self._update_index_status()
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
    
    def _load_existing_index(self):
        """Load existing index if available."""
        try:
            if self.vector_store.load_index():
                self._update_index_status()
                self._log("Existing index loaded successfully")
            else:
                self.index_status_label.setText("Index: Not found")
                self._log("No existing index found. Please build one.")
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            self._log(f"Error loading index: {e}")
    
    def _update_index_status(self):
        """Update index status display."""
        if self.vector_store and self.vector_store.document_count > 0:
            count = self.vector_store.document_count
            self.index_status_label.setText(f"Index: Loaded ({count} chunks)")
        else:
            self.index_status_label.setText("Index: Not loaded")
    
    def _toggle_assistant(self):
        """Start or stop the assistant."""
        if not self.is_assistant_running:
            self._start_assistant()
        else:
            self._stop_assistant()
    
    def _start_assistant(self):
        """Start the AI assistant."""
        # Check if index is loaded
        if not self.vector_store or self.vector_store.document_count == 0:
            QMessageBox.warning(
                self,
                "Warning",
                "Please build and load an index before starting the assistant."
            )
            return
        
        try:
            # Load models if not already loaded
            self._log("Loading models...")
            
            if self.embedder.model is None:
                self.embedder.load_model()
            
            if self.suggestion_engine and not self.suggestion_engine._is_loaded:
                self.suggestion_engine.load_model()
            
            # Start keystroke listener
            self.keystroke_listener.start()
            
            self.is_assistant_running = True
            self.assistant_status_label.setText("Status: 🟢 Running")
            self.toggle_assistant_btn.setText("Stop Assistant")
            self.toggle_assistant_btn.setStyleSheet("background-color: #d32f2f;")
            
            self._log("✅ Assistant started successfully!")
            self.status_bar.showMessage("Assistant is running")
            
        except Exception as e:
            logger.error(f"Error starting assistant: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start assistant: {e}")
            self._log(f"❌ Error starting assistant: {e}")
    
    def _stop_assistant(self):
        """Stop the AI assistant."""
        try:
            # Stop keystroke listener
            self.keystroke_listener.stop()
            
            # Hide overlay if visible
            if self.suggestion_overlay:
                self.suggestion_overlay.hide_suggestions()
            
            self.is_assistant_running = False
            self.assistant_status_label.setText("Status: ⭕ Stopped")
            self.toggle_assistant_btn.setText("Start Assistant")
            self.toggle_assistant_btn.setStyleSheet("")
            
            self._log("🛑 Assistant stopped")
            self.status_bar.showMessage("Assistant stopped")
            
        except Exception as e:
            logger.error(f"Error stopping assistant: {e}")
            self._log(f"Error stopping assistant: {e}")
    
    def _on_typing_context(self, context: str):
        """Handle typing context from keystroke listener."""
        if not self.is_assistant_running:
            return
        
        try:
            # Generate suggestions
            logger.debug(f"Generating suggestions for context: {context[-50:]}...")
            
            suggestions = self.suggestion_engine.get_multiple_suggestions(
                context,
                count=config.overlay_max_suggestions
            )
            
            # Show suggestions in overlay
            if suggestions:
                self.suggestion_overlay.show_suggestions(suggestions)
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
    
    def _on_suggestion_accepted(self, suggestion: str):
        """Handle suggestion acceptance."""
        self._log(f"✅ Suggestion accepted: {suggestion[:50]}...")
        # Note: Actual text insertion would require additional system integration
        # using pyautogui or similar library
    
    def _on_suggestion_dismissed(self):
        """Handle suggestion dismissal."""
        logger.debug("Suggestion dismissed")
    
    def _log(self, message: str):
        """Add message to log display."""
        self.log_text.append(message)
        logger.info(message)
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.is_assistant_running:
            self._stop_assistant()
        
        event.accept()


def run_application():
    """Run the main application."""
    app = QApplication(sys.argv)
    app.setApplicationName("AI Text Assistant")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_application()
