"""
Progress section with progress bar and step indicators
"""

import tkinter as tk
from tkinter import ttk


class ProgressSection:
    """Manages the progress display area"""
    
    def __init__(self, parent):
        self.parent = parent
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the progress section widgets"""
        self.frame = ttk.LabelFrame(self.parent, text="Progress", padding="15")
        self.frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        self.frame.columnconfigure(0, weight=1)
        
        # Step label with icon
        step_frame = ttk.Frame(self.frame)
        step_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        step_frame.columnconfigure(1, weight=1)
        
        self.step_icon = ttk.Label(step_frame, text="⏳", font=('Segoe UI', 12))
        self.step_icon.grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        
        self.step_label = ttk.Label(
            step_frame, 
            text="Ready to start...", 
            font=('Segoe UI', 10)
        )
        self.step_label.grid(row=0, column=1, sticky=tk.W)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.frame, 
            length=500, 
            variable=self.progress_var, 
            maximum=100
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # Progress percentage and ETA
        info_frame = ttk.Frame(self.frame)
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        info_frame.columnconfigure(1, weight=1)
        
        self.progress_label = ttk.Label(info_frame, text="0%", font=('Segoe UI', 9))
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.eta_label = ttk.Label(info_frame, text="", font=('Segoe UI', 9))
        self.eta_label.grid(row=0, column=1, sticky=tk.E)
    def update_progress(self, step: int, percentage: float, message: str, icon: str = "⏳"):
        """Update the progress display"""
        if step > 0:
            self.step_label.config(text=f"Step {step}/4: {message}")
        else:
            self.step_label.config(text=message)
        
        self.step_icon.config(text=icon)
        self.progress_var.set(percentage)
        self.progress_label.config(text=f"{percentage:.0f}%")
