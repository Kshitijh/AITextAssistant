"""
Text Editor Widget
Main editor component with suggestion support.
"""

from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QTextCursor, QColor, QTextCharFormat
from loguru import logger


class TextEditor(QTextEdit):
    """
    Enhanced text editor with autocomplete support.
    Emits signals for text changes and selection.
    """
    
    # Signals
    text_changed_delayed = Signal(str)  # Emitted after debounce
    selection_changed_signal = Signal(str)  # Emitted when selection changes
    
    def __init__(self, parent=None, debounce_ms: int = 500):
        """
        Initialize the text editor.
        
        Args:
            parent: Parent widget
            debounce_ms: Debounce time for text change events
        """
        super().__init__(parent)
        
        self.debounce_ms = debounce_ms
        self._debounce_timer = QTimer()
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.timeout.connect(self._on_debounce_timeout)
        
        self._current_suggestion = None
        self._suggestion_format = QTextCharFormat()
        self._suggestion_format.setForeground(QColor(128, 128, 128))
        
        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        self.selectionChanged.connect(self._on_selection_changed)
        
        # Configure editor
        self.setPlaceholderText("Start typing or load documents...")
        
        logger.debug("TextEditor initialized")
    
    def _on_text_changed(self):
        """Handle text change events with debouncing."""
        # Restart debounce timer
        self._debounce_timer.stop()
        self._debounce_timer.start(self.debounce_ms)
    
    def _on_debounce_timeout(self):
        """Handle debounced text change."""
        text = self.toPlainText()
        self.text_changed_delayed.emit(text)
    
    def _on_selection_changed(self):
        """Handle selection change events."""
        cursor = self.textCursor()
        selected_text = cursor.selectedText()
        
        if selected_text:
            self.selection_changed_signal.emit(selected_text)
    
    def get_context(self, max_length: int = 200) -> str:
        """
        Get current context (text before cursor).
        
        Args:
            max_length: Maximum length of context
            
        Returns:
            Context string
        """
        cursor = self.textCursor()
        position = cursor.position()
        
        # Get text up to cursor
        full_text = self.toPlainText()
        context = full_text[:position]
        
        # Limit to max_length
        if len(context) > max_length:
            context = context[-max_length:]
        
        return context
    
    def show_suggestion(self, suggestion: str):
        """
        Display inline suggestion (ghost text).
        
        Args:
            suggestion: Suggestion text to display
        """
        # Clear previous suggestion
        self.clear_suggestion()
        
        if not suggestion:
            return
        
        # Store suggestion
        self._current_suggestion = suggestion
        
        # TODO: Implement ghost text display
        # This requires more complex cursor manipulation
        # For now, we'll show suggestions in a separate widget
        
        logger.debug(f"Suggestion ready: {suggestion[:50]}...")
    
    def clear_suggestion(self):
        """Clear current suggestion."""
        self._current_suggestion = None
    
    def accept_suggestion(self):
        """Accept and insert current suggestion."""
        if self._current_suggestion:
            cursor = self.textCursor()
            cursor.insertText(self._current_suggestion)
            self.clear_suggestion()
            logger.debug("Suggestion accepted")
    
    def get_selected_text(self) -> str:
        """
        Get currently selected text.
        
        Returns:
            Selected text string
        """
        return self.textCursor().selectedText()
    
    def replace_selected_text(self, new_text: str):
        """
        Replace selected text with new text.
        
        Args:
            new_text: Text to insert
        """
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.insertText(new_text)
            logger.debug(f"Replaced selection with: {new_text[:50]}...")
