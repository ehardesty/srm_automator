"""
Simple UI components - consolidated title and control sections
Simplified from multiple files for easier maintenance
"""

import tkinter as tk
from tkinter import ttk

from utils.enums import ProcessStatus


class SimpleComponents:
    """Manages simple UI elements: title and control buttons"""
    
    def __init__(self, parent, callbacks=None):
        self.parent = parent
        self.callbacks = callbacks or {}
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the title and control widgets"""
        self._create_title_section()
        self._create_control_section()
    
    def _create_title_section(self):
        """Create the title section with status indicator"""
        self.title_frame = ttk.Frame(self.parent)
        self.title_frame.grid(row=0, column=0, pady=(0, 25), sticky=(tk.W, tk.E))
        self.title_frame.columnconfigure(1, weight=1)
        
        # Application title
        self.title_label = ttk.Label(
            self.title_frame, 
            text="Steam ROM Manager Automation", 
            font=('Segoe UI', 18, 'bold')
        )
        self.title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Status indicator
        self.status_label = ttk.Label(self.title_frame, text="●", font=('Segoe UI', 16))
        self.status_label.grid(row=0, column=2, sticky=tk.E)
        
        # Initialize with ready status
        self.update_status(ProcessStatus.READY)
    
    def _create_control_section(self):
        """Create the control buttons section"""
        self.control_frame = ttk.Frame(self.parent)
        self.control_frame.grid(row=2, column=0, pady=15)
        
        # Start button
        self.start_button = ttk.Button(
            self.control_frame, 
            text="▶ Start Process", 
            command=self.callbacks.get('start_process')
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Settings button
        self.settings_button = ttk.Button(
            self.control_frame, 
            text="⚙ Settings", 
            command=self.callbacks.get('open_settings')
        )
        self.settings_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        self.export_button = ttk.Button(
            self.control_frame, 
            text="💾 Export Log", 
            command=self.callbacks.get('export_logs')
        )
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        self.close_button = ttk.Button(
            self.control_frame, 
            text="✕ Close", 
            command=self.callbacks.get('close_application')
        )
        self.close_button.pack(side=tk.LEFT)
    
    def update_status(self, status: ProcessStatus):
        """Update the visual status indicator"""
        colors = {
            ProcessStatus.READY: "#6c757d",
            ProcessStatus.RUNNING: "#ffc107", 
            ProcessStatus.SUCCESS: "#28a745",
            ProcessStatus.FAILED: "#dc3545",
            ProcessStatus.CANCELLED: "#6c757d"
        }
        self.status_label.config(foreground=colors.get(status, "#6c757d"))
    
    def set_start_button_state(self, state: str):
        """Enable or disable the start button"""
        self.start_button.config(state=state)
