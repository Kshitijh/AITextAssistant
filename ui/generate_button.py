"""
Generate Button Widget
Floating button that appears when text is selected.
"""

from PySide6.QtWidgets import QPushButton, QMenu
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QCursor
from loguru import logger


class GenerateButton(QPushButton):
    """
    Floating button that appears above selected text.
    Provides options for text generation/refinement.
    """
    
    # Signals
    refine_requested = Signal(str)  # Emitted when refine is requested
    expand_requested = Signal(str)  # Emitted when expand is requested
    alternatives_requested = Signal(str)  # Emitted when alternatives requested
    
    def __init__(self, parent=None):
        """
        Initialize the generate button.
        
        Args:
            parent: Parent widget
        """
        super().__init__("✨ Generate", parent)
        
        self._selected_text = ""
        
        # Configure button appearance
        self.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """)
        
        # Create context menu
        self._create_menu()
        
        # Connect signals
        self.clicked.connect(self._on_clicked)
        
        # Hide by default
        self.hide()
        
        logger.debug("GenerateButton initialized")
    
    def _create_menu(self):
        """Create context menu with generation options."""
        self._menu = QMenu(self)
        
        # Add menu actions
        self._refine_action = self._menu.addAction("✍️ Refine Text")
        self._expand_action = self._menu.addAction("📝 Expand Text")
        self._alternatives_action = self._menu.addAction("🔄 Get Alternatives")
        
        # Connect actions
        self._refine_action.triggered.connect(self._on_refine)
        self._expand_action.triggered.connect(self._on_expand)
        self._alternatives_action.triggered.connect(self._on_alternatives)
    
    def _on_clicked(self):
        """Handle button click - show menu."""
        self._menu.exec(QCursor.pos())
    
    def _on_refine(self):
        """Handle refine action."""
        if self._selected_text:
            logger.info("Refine requested")
            self.refine_requested.emit(self._selected_text)
    
    def _on_expand(self):
        """Handle expand action."""
        if self._selected_text:
            logger.info("Expand requested")
            self.expand_requested.emit(self._selected_text)
    
    def _on_alternatives(self):
        """Handle alternatives action."""
        if self._selected_text:
            logger.info("Alternatives requested")
            self.alternatives_requested.emit(self._selected_text)
    
    def show_for_selection(self, selected_text: str, position: QPoint = None):
        """
        Show button for selected text.
        
        Args:
            selected_text: The selected text
            position: Position to show button (uses cursor if None)
        """
        self._selected_text = selected_text
        
        if position is None:
            position = QCursor.pos()
        
        # Position button near selection
        self.move(position.x(), position.y() - self.height() - 5)
        self.show()
        self.raise_()
        
        logger.debug(f"Generate button shown for: {selected_text[:30]}...")
    
    def hide_button(self):
        """Hide the button."""
        self._selected_text = ""
        self.hide()
