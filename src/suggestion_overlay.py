"""
Suggestion Overlay Module
Floating window that displays autocomplete suggestions near the cursor.
"""

import sys
from typing import List, Optional
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QCursor
from loguru import logger

from src.config import config


class SuggestionOverlay(QWidget):
    """
    Floating overlay window that displays text suggestions near the cursor.
    """
    
    accepted = pyqtSignal(str)  # Signal emitted when suggestion is accepted
    dismissed = pyqtSignal()     # Signal emitted when suggestion is dismissed
    
    def __init__(self):
        """Initialize the suggestion overlay."""
        super().__init__()
        
        self.suggestions: List[str] = []
        self.current_index = 0
        self.is_visible_flag = False
        
        self._setup_ui()
        self._setup_shortcuts()
        
    def _setup_ui(self) -> None:
        """Setup the UI components."""
        # Window flags for frameless, always-on-top overlay
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowDoesNotAcceptFocus
        )
        
        # Make background semi-transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(config.overlay_opacity)
        
        # Setup layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Suggestion label
        self.suggestion_label = QLabel("")
        self.suggestion_label.setWordWrap(True)
        self.suggestion_label.setMaximumWidth(500)
        
        # Apply styling
        font = QFont(config.overlay_font_family, config.overlay_font_size)
        self.suggestion_label.setFont(font)
        
        # Set stylesheet based on theme
        if config.ui_theme == "dark":
            self.suggestion_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(45, 45, 45, 240);
                    color: #FFFFFF;
                    border: 1px solid #555555;
                    border-radius: 5px;
                    padding: 8px;
                }
            """)
        else:
            self.suggestion_label.setStyleSheet("""
                QLabel {
                    background-color: rgba(255, 255, 255, 240);
                    color: #000000;
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 8px;
                }
            """)
        
        layout.addWidget(self.suggestion_label)
        self.setLayout(layout)
        
        # Hide initially
        self.hide()
        
    def _setup_shortcuts(self) -> None:
        """Setup keyboard shortcuts (handled externally via global listener)."""
        # Shortcuts will be handled by the main application
        # because this window doesn't accept focus
        pass
    
    def show_suggestions(self, suggestions: List[str]) -> None:
        """
        Show suggestions in the overlay.
        
        Args:
            suggestions: List of suggestion strings
        """
        if not suggestions or all(not s.strip() for s in suggestions):
            self.hide_suggestions()
            return
        
        # Filter out empty suggestions
        self.suggestions = [s for s in suggestions if s.strip()]
        
        if not self.suggestions:
            self.hide_suggestions()
            return
        
        self.current_index = 0
        self._update_display()
        self._position_near_cursor()
        
        self.show()
        self.is_visible_flag = True
        logger.debug(f"Showing {len(self.suggestions)} suggestions")
    
    def _update_display(self) -> None:
        """Update the displayed suggestion."""
        if not self.suggestions or self.current_index >= len(self.suggestions):
            return
        
        suggestion = self.suggestions[self.current_index]
        
        # Format display text
        if len(self.suggestions) > 1:
            display_text = f"💡 {suggestion}\n\n({self.current_index + 1}/{len(self.suggestions)}) TAB: Accept | ESC: Dismiss | ↑↓: Navigate"
        else:
            display_text = f"💡 {suggestion}\n\nTAB: Accept | ESC: Dismiss"
        
        self.suggestion_label.setText(display_text)
        self.adjustSize()
    
    def _position_near_cursor(self) -> None:
        """Position the overlay near the cursor."""
        try:
            cursor_pos = QCursor.pos()
            
            # Offset from cursor
            x = cursor_pos.x() + config.overlay_position_offset_x
            y = cursor_pos.y() + config.overlay_position_offset_y
            
            # Ensure window stays on screen
            screen_geometry = QApplication.desktop().screenGeometry()
            
            if x + self.width() > screen_geometry.width():
                x = screen_geometry.width() - self.width() - 10
            
            if y + self.height() > screen_geometry.height():
                y = cursor_pos.y() - self.height() - 10
            
            self.move(x, y)
            
        except Exception as e:
            logger.error(f"Error positioning overlay: {e}")
    
    def hide_suggestions(self) -> None:
        """Hide the suggestion overlay."""
        self.hide()
        self.is_visible_flag = False
        self.suggestions = []
        self.current_index = 0
    
    def accept_current_suggestion(self) -> None:
        """Accept the currently displayed suggestion."""
        if self.suggestions and self.current_index < len(self.suggestions):
            suggestion = self.suggestions[self.current_index]
            logger.info(f"Suggestion accepted: {suggestion[:50]}...")
            self.accepted.emit(suggestion)
            self.hide_suggestions()
    
    def dismiss_suggestions(self) -> None:
        """Dismiss all suggestions."""
        logger.debug("Suggestions dismissed")
        self.dismissed.emit()
        self.hide_suggestions()
    
    def next_suggestion(self) -> None:
        """Show the next suggestion."""
        if len(self.suggestions) > 1:
            self.current_index = (self.current_index + 1) % len(self.suggestions)
            self._update_display()
    
    def previous_suggestion(self) -> None:
        """Show the previous suggestion."""
        if len(self.suggestions) > 1:
            self.current_index = (self.current_index - 1) % len(self.suggestions)
            self._update_display()
    
    def is_showing(self) -> bool:
        """
        Check if overlay is currently visible.
        
        Returns:
            True if visible, False otherwise
        """
        return self.is_visible_flag
