"""
Keystroke Listener Module
Captures global keyboard input and maintains typing context.
"""

import time
import threading
from collections import deque
from typing import Optional, Callable, Deque
from loguru import logger

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logger.warning("pynput not available")

from src.config import config


class KeystrokeListener:
    """
    Global keystroke listener that captures typing input.
    Maintains a rolling window of recent text and triggers suggestions.
    """
    
    def __init__(self, callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the keystroke listener.
        
        Args:
            callback: Function to call with context when suggestion should be triggered
        """
        self.callback = callback
        self.context_window_size = config.listener_context_window
        self.trigger_threshold = config.listener_trigger_threshold
        self.debounce_ms = config.listener_debounce_ms
        
        self.context_buffer: Deque[str] = deque(maxlen=self.context_window_size)
        self.listener: Optional[keyboard.Listener] = None
        self.is_running = False
        
        self._last_trigger_time = 0
        self._char_count_since_trigger = 0
        self._shift_pressed = False
        self._ctrl_pressed = False
        self._alt_pressed = False
        
    def start(self) -> None:
        """Start listening to keyboard events."""
        if not PYNPUT_AVAILABLE:
            logger.error("pynput is not available. Cannot start keystroke listener.")
            return
        
        if self.is_running:
            logger.warning("Listener is already running")
            return
        
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            
            self.listener.start()
            self.is_running = True
            logger.info("Keystroke listener started")
            
        except Exception as e:
            logger.error(f"Error starting keystroke listener: {e}")
    
    def stop(self) -> None:
        """Stop listening to keyboard events."""
        if not self.is_running:
            return
        
        try:
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            self.is_running = False
            logger.info("Keystroke listener stopped")
            
        except Exception as e:
            logger.error(f"Error stopping keystroke listener: {e}")
    
    def _on_key_press(self, key) -> None:
        """
        Handle key press events.
        
        Args:
            key: The key that was pressed
        """
        try:
            # Track modifier keys
            if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self._shift_pressed = True
                return
            elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
                self._ctrl_pressed = True
                return
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_r:
                self._alt_pressed = True
                return
            
            # Ignore if modifiers are pressed (except shift for capitals)
            if self._ctrl_pressed or self._alt_pressed:
                return
            
            # Handle special keys
            if key == keyboard.Key.space:
                self._add_to_buffer(' ')
            elif key == keyboard.Key.enter:
                self._add_to_buffer('\n')
            elif key == keyboard.Key.backspace:
                self._handle_backspace()
            elif key == keyboard.Key.tab:
                self._add_to_buffer('\t')
            elif hasattr(key, 'char') and key.char:
                # Regular character
                self._add_to_buffer(key.char)
            
        except Exception as e:
            logger.error(f"Error handling key press: {e}")
    
    def _on_key_release(self, key) -> None:
        """
        Handle key release events.
        
        Args:
            key: The key that was released
        """
        try:
            # Track modifier key releases
            if key == keyboard.Key.shift or key == keyboard.Key.shift_r:
                self._shift_pressed = False
            elif key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_r:
                self._ctrl_pressed = False
            elif key == keyboard.Key.alt or key == keyboard.Key.alt_r:
                self._alt_pressed = False
                
        except Exception as e:
            logger.error(f"Error handling key release: {e}")
    
    def _add_to_buffer(self, char: str) -> None:
        """
        Add a character to the context buffer.
        
        Args:
            char: Character to add
        """
        self.context_buffer.append(char)
        self._char_count_since_trigger += 1
        
        # Check if we should trigger a suggestion
        self._check_trigger()
    
    def _handle_backspace(self) -> None:
        """Handle backspace key (remove last character from buffer)."""
        if len(self.context_buffer) > 0:
            self.context_buffer.pop()
    
    def _check_trigger(self) -> None:
        """Check if we should trigger a suggestion callback."""
        if not self.callback:
            return
        
        # Check debounce time
        current_time = time.time()
        time_since_last = (current_time - self._last_trigger_time) * 1000  # Convert to ms
        
        if time_since_last < self.debounce_ms:
            return
        
        # Check if we've typed enough characters
        if self._char_count_since_trigger < self.trigger_threshold:
            return
        
        # Get current context
        context = self.get_context()
        
        # Only trigger if context ends with a space or punctuation
        if context and len(context) > 0:
            last_char = context[-1]
            if last_char in [' ', '.', ',', '!', '?', '\n']:
                # Trigger callback in a separate thread to avoid blocking
                threading.Thread(
                    target=self._trigger_callback,
                    args=(context,),
                    daemon=True
                ).start()
                
                # Reset trigger tracking
                self._last_trigger_time = current_time
                self._char_count_since_trigger = 0
    
    def _trigger_callback(self, context: str) -> None:
        """
        Trigger the callback with the current context.
        
        Args:
            context: Current typing context
        """
        try:
            if self.callback:
                self.callback(context)
        except Exception as e:
            logger.error(f"Error in suggestion callback: {e}")
    
    def get_context(self) -> str:
        """
        Get the current typing context.
        
        Returns:
            Current context as a string
        """
        return ''.join(self.context_buffer)
    
    def clear_context(self) -> None:
        """Clear the context buffer."""
        self.context_buffer.clear()
        self._char_count_since_trigger = 0
        logger.debug("Context buffer cleared")
    
    def get_last_n_chars(self, n: int) -> str:
        """
        Get the last N characters from the context buffer.
        
        Args:
            n: Number of characters to retrieve
            
        Returns:
            Last N characters as a string
        """
        buffer_list = list(self.context_buffer)
        return ''.join(buffer_list[-n:])
    
    def get_last_sentence(self) -> str:
        """
        Get the last complete sentence from the context.
        
        Returns:
            Last sentence as a string
        """
        context = self.get_context()
        
        # Find last sentence boundary
        for delimiter in ['.', '!', '?', '\n']:
            idx = context.rfind(delimiter)
            if idx != -1:
                return context[idx+1:].strip()
        
        # No sentence boundary found, return last 100 chars
        return context[-100:].strip()
    
    def set_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set or update the callback function.
        
        Args:
            callback: New callback function
        """
        self.callback = callback
        logger.debug("Callback function updated")
