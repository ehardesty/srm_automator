"""
Log section with scrollable output display and theme-aware colors
"""

import tkinter as tk
from tkinter import scrolledtext, ttk
import time

from utils.enums import LogLevel
from ui.theme_manager import ThemeManager


class LogSection:
    """Manages the log output display area"""
    
    def __init__(self, parent):
        self.parent = parent
        self._create_widgets()
        self._configure_text_colors()
    
    def _create_widgets(self):
        """Create the log section widgets"""
        self.frame = ttk.LabelFrame(self.parent, text="Output Log", padding="15")
        self.frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(15, 0))
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Scrolled text widget for output
        self.output_text = scrolledtext.ScrolledText(
            self.frame, 
            height=18, 
            width=80,
            wrap=tk.WORD, 
            state=tk.DISABLED,
            font=('Segoe UI', 9)
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    
    def _configure_text_colors(self):
        """Configure text colors based on current theme"""
        is_dark_theme = ThemeManager.is_dark_theme_active()
        
        if is_dark_theme:
            # Dark theme colors - light text on dark background
            self.output_text.tag_configure("info", foreground="#e0e0e0")
            self.output_text.tag_configure("success", foreground="#4ade80", font=('Segoe UI', 9, 'bold'))
            self.output_text.tag_configure("error", foreground="#f87171", font=('Segoe UI', 9, 'bold'))
            self.output_text.tag_configure("warning", foreground="#fbbf24", font=('Segoe UI', 9, 'bold'))
        else:
            # Light theme colors - dark text on light background
            self.output_text.tag_configure("info", foreground="#1f1f1f")
            self.output_text.tag_configure("success", foreground="#107c10", font=('Segoe UI', 9, 'bold'))
            self.output_text.tag_configure("error", foreground="#d13438", font=('Segoe UI', 9, 'bold'))
            self.output_text.tag_configure("warning", foreground="#ff8c00", font=('Segoe UI', 9, 'bold'))
    def log_message(self, message: str, level: LogLevel = LogLevel.INFO):
        """Add a message to the output log"""
        self.output_text.config(state=tk.NORMAL)
        timestamp = time.strftime("%H:%M:%S")
        self.output_text.insert(tk.END, f"[{timestamp}] {message}\n", level.value)
        self.output_text.see(tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Clear all log content"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def get_log_content(self) -> str:
        """Get all log content as string"""
        return self.output_text.get(1.0, tk.END)
    
    def refresh_colors(self):
        """Refresh text colors based on current theme"""
        self._configure_text_colors()
