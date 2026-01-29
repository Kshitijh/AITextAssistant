"""
Main Window
Primary application window with all UI components.
"""

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QTextEdit,
    QProgressBar, QStatusBar, QMenuBar, QMenu,
    QMessageBox, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction
from loguru import logger

from ui.editor import TextEditor
from ui.generate_button import GenerateButton
from suggestion.autocomplete import Autocomplete
from suggestion.text_replacer import TextReplacer


class DocumentIndexer(QThread):
    """Background thread for document indexing."""
    
    progress = Signal(int, str)  # progress percentage, status message
    finished = Signal(bool, str)  # success, message
    
    def __init__(self, folder_path: str, app_controller):
        """
        Initialize indexer thread.
        
        Args:
            folder_path: Path to documents folder
            app_controller: Application controller instance
        """
        super().__init__()
        self.folder_path = folder_path
        self.app_controller = app_controller
    
    def run(self):
        """Run indexing in background."""
        try:
            logger.info(f"Starting document indexing: {self.folder_path}")
            self.progress.emit(10, "Scanning documents...")
            
            # This will be connected to the actual indexing logic
            success = self.app_controller.index_documents(
                self.folder_path,
                progress_callback=self._on_progress
            )
            
            if success:
                self.finished.emit(True, "Documents indexed successfully!")
            else:
                self.finished.emit(False, "Indexing failed. Check logs.")
                
        except Exception as e:
            logger.error(f"Error in indexing thread: {e}")
            self.finished.emit(False, f"Error: {str(e)}")
    
    def _on_progress(self, progress: int, message: str):
        """Handle progress updates."""
        self.progress.emit(progress, message)


class MainWindow(QMainWindow):
    """
    Main application window.
    Contains editor, controls, and manages UI interactions.
    """
    
    def __init__(self, app_controller):
        """
        Initialize main window.
        
        Args:
            app_controller: Application controller instance
        """
        super().__init__()
        
        self.app_controller = app_controller
        self.autocomplete: Optional[Autocomplete] = None
        self.text_replacer: Optional[TextReplacer] = None
        self.indexer_thread: Optional[DocumentIndexer] = None
        
        self._init_ui()
        self._connect_signals()
        
        logger.info("Main window initialized")
    
    def _init_ui(self):
        """Initialize UI components."""
        self.setWindowTitle("AI Text Assistant")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create menu bar
        self._create_menu_bar()
        
        # Create toolbar
        toolbar_layout = self._create_toolbar()
        main_layout.addLayout(toolbar_layout)
        
        # Create splitter for editor and info panel
        splitter = QSplitter(Qt.Horizontal)
        
        # Create editor
        self.editor = TextEditor(debounce_ms=500)
        splitter.addWidget(self.editor)
        
        # Create info panel
        info_panel = self._create_info_panel()
        splitter.addWidget(info_panel)
        
        # Set splitter proportions
        splitter.setStretchFactor(0, 3)  # Editor gets 75%
        splitter.setStretchFactor(1, 1)  # Info gets 25%
        
        main_layout.addWidget(splitter)
        
        # Create generate button (floating)
        self.generate_btn = GenerateButton(self.editor)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _create_menu_bar(self):
        """Create menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        load_docs_action = QAction("&Load Documents", self)
        load_docs_action.triggered.connect(self._on_load_documents)
        file_menu.addAction(load_docs_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _create_toolbar(self) -> QHBoxLayout:
        """Create toolbar with controls."""
        toolbar = QHBoxLayout()
        
        # Load documents button
        self.load_docs_btn = QPushButton("📁 Load Documents")
        self.load_docs_btn.clicked.connect(self._on_load_documents)
        toolbar.addWidget(self.load_docs_btn)
        
        # Status label
        self.docs_status_label = QLabel("No documents loaded")
        toolbar.addWidget(self.docs_status_label)
        
        toolbar.addStretch()
        
        # Suggestions toggle
        self.suggestions_toggle = QPushButton("💡 Suggestions: ON")
        self.suggestions_toggle.setCheckable(True)
        self.suggestions_toggle.setChecked(True)
        self.suggestions_toggle.clicked.connect(self._toggle_suggestions)
        toolbar.addWidget(self.suggestions_toggle)
        
        return toolbar
    
    def _create_info_panel(self) -> QWidget:
        """Create information panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("<b>Suggestions</b>")
        layout.addWidget(title)
        
        # Suggestions display
        self.suggestions_display = QTextEdit()
        self.suggestions_display.setReadOnly(True)
        self.suggestions_display.setPlaceholderText("Suggestions will appear here...")
        layout.addWidget(self.suggestions_display)
        
        # Source info
        self.source_info_label = QLabel("Source: -")
        self.source_info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(self.source_info_label)
        
        return panel
    
    def _connect_signals(self):
        """Connect UI signals."""
        # Editor signals
        self.editor.text_changed_delayed.connect(self._on_text_changed)
        self.editor.selection_changed_signal.connect(self._on_selection_changed)
        
        # Generate button signals
        self.generate_btn.refine_requested.connect(self._on_refine_text)
        self.generate_btn.expand_requested.connect(self._on_expand_text)
        self.generate_btn.alternatives_requested.connect(self._on_get_alternatives)
    
    def _on_load_documents(self):
        """Handle load documents action."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Documents Folder",
            str(Path.home())
        )
        
        if folder:
            self._index_documents(folder)
    
    def _index_documents(self, folder_path: str):
        """
        Start document indexing.
        
        Args:
            folder_path: Path to documents folder
        """
        # Disable button
        self.load_docs_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        # Create and start indexer thread
        self.indexer_thread = DocumentIndexer(folder_path, self.app_controller)
        self.indexer_thread.progress.connect(self._on_indexing_progress)
        self.indexer_thread.finished.connect(self._on_indexing_finished)
        self.indexer_thread.start()
    
    def _on_indexing_progress(self, progress: int, message: str):
        """Handle indexing progress updates."""
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(message)
    
    def _on_indexing_finished(self, success: bool, message: str):
        """Handle indexing completion."""
        self.progress_bar.hide()
        self.load_docs_btn.setEnabled(True)
        
        if success:
            self.docs_status_label.setText("✅ Documents loaded")
            self.status_bar.showMessage(message, 5000)
            
            # Update autocomplete and text replacer
            self._initialize_suggestion_engines()
        else:
            self.docs_status_label.setText("❌ Loading failed")
            QMessageBox.warning(self, "Indexing Failed", message)
    
    def _initialize_suggestion_engines(self):
        """Initialize suggestion engines after indexing."""
        try:
            self.autocomplete = self.app_controller.get_autocomplete()
            self.text_replacer = self.app_controller.get_text_replacer()
            logger.info("Suggestion engines initialized")
        except Exception as e:
            logger.error(f"Error initializing suggestion engines: {e}")
    
    def _on_text_changed(self, text: str):
        """Handle debounced text changes."""
        if not self.suggestions_toggle.isChecked() or not self.autocomplete:
            return
        
        # Get context and generate suggestions
        context = self.editor.get_context(max_length=200)
        
        if len(context) > 10:  # Only suggest if meaningful context exists
            suggestions = self.autocomplete.get_suggestions(context, num_suggestions=3)
            self._display_suggestions(suggestions)
    
    def _display_suggestions(self, suggestions: list):
        """Display suggestions in info panel."""
        if suggestions:
            display_text = "\n\n---\n\n".join(
                f"{i+1}. {sugg}" for i, sugg in enumerate(suggestions)
            )
            self.suggestions_display.setPlainText(display_text)
            self.source_info_label.setText("Source: Local documents")
        else:
            self.suggestions_display.setPlainText("No suggestions available")
            self.source_info_label.setText("Source: -")
    
    def _on_selection_changed(self, selected_text: str):
        """Handle text selection changes."""
        if selected_text and len(selected_text) > 5:
            # Show generate button
            self.generate_btn.show_for_selection(selected_text)
        else:
            self.generate_btn.hide_button()
    
    def _on_refine_text(self, selected_text: str):
        """Handle refine text request."""
        if not self.text_replacer:
            QMessageBox.warning(self, "Not Ready", "Please load documents first")
            return
        
        self.status_bar.showMessage("Refining text...")
        
        context = self.editor.get_context(max_length=300)
        refined = self.text_replacer.refine_text(selected_text, context)
        
        if refined:
            self.editor.replace_selected_text(refined)
            self.status_bar.showMessage("Text refined!", 3000)
        else:
            self.status_bar.showMessage("Could not refine text", 3000)
        
        self.generate_btn.hide_button()
    
    def _on_expand_text(self, selected_text: str):
        """Handle expand text request."""
        if not self.text_replacer:
            QMessageBox.warning(self, "Not Ready", "Please load documents first")
            return
        
        self.status_bar.showMessage("Expanding text...")
        
        context = self.editor.get_context(max_length=300)
        expanded = self.text_replacer.expand_text(selected_text, context)
        
        if expanded:
            self.editor.replace_selected_text(expanded)
            self.status_bar.showMessage("Text expanded!", 3000)
        else:
            self.status_bar.showMessage("Could not expand text", 3000)
        
        self.generate_btn.hide_button()
    
    def _on_get_alternatives(self, selected_text: str):
        """Handle get alternatives request."""
        if not self.text_replacer:
            QMessageBox.warning(self, "Not Ready", "Please load documents first")
            return
        
        self.status_bar.showMessage("Finding alternatives...")
        
        alternatives = self.text_replacer.get_alternatives(selected_text, num_alternatives=3)
        
        if alternatives:
            # Show alternatives in suggestions panel
            alt_text = "\n\n---\n\n".join(
                f"Alt {i+1}: {alt}" for i, alt in enumerate(alternatives)
            )
            self.suggestions_display.setPlainText(alt_text)
            self.source_info_label.setText("Alternatives from local documents")
            self.status_bar.showMessage(f"Found {len(alternatives)} alternatives", 3000)
        else:
            self.status_bar.showMessage("No alternatives found", 3000)
        
        self.generate_btn.hide_button()
    
    def _toggle_suggestions(self):
        """Toggle suggestions on/off."""
        is_on = self.suggestions_toggle.isChecked()
        self.suggestions_toggle.setText(f"💡 Suggestions: {'ON' if is_on else 'OFF'}")
        
        if not is_on:
            self.suggestions_display.clear()
            self.source_info_label.setText("Source: -")
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About AI Text Assistant",
            "<h3>AI Text Assistant</h3>"
            "<p>An intelligent writing assistant powered by local documents.</p>"
            "<p>Version 1.0.0</p>"
            "<p>Built with PySide6, sentence-transformers, and FAISS.</p>"
        )
