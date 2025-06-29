"""
Settings configuration dialog window
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
from pathlib import Path
from typing import Tuple

from config import ConfigManager
from utils.enums import LogLevel


class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent, config_manager: ConfigManager, logger=None):
        self.parent = parent
        self.config_manager = config_manager
        self.logger = logger
        self.window = None
        self.path_var = None
    
    def _validate_srm_path(self, path: str) -> Tuple[bool, str]:
        """Simple SRM path validation"""
        if not path or path == "auto-detect":
            return True, "Auto-detect enabled"
            
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return False, "File does not exist"
            
            if not path_obj.is_file():
                return False, "Path is not a file"
            
            # Check for .exe on Windows
            if sys.platform.startswith('win') and not str(path_obj).lower().endswith('.exe'):
                return False, "Must be an .exe file on Windows"
            
            return True, "Valid executable"
            
        except (OSError, ValueError) as e:
            return False, f"Invalid path: {e}"
    
    def show(self):
        """Show the settings dialog"""
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
            
        self._create_window()
    
    def _create_window(self):
        """Create the settings dialog window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Settings")
        self.window.geometry("500x200")
        self.window.resizable(False, False)
        
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # SRM Path setting
        ttk.Label(frame, text="Steam ROM Manager Path:").pack(anchor=tk.W, pady=(0, 5))
        
        path_frame = ttk.Frame(frame)
        path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.path_var = tk.StringVar(value=self.config_manager.config.srm_path)
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=60)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_button = ttk.Button(path_frame, text="Browse...", command=self._browse_srm_path)
        browse_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Auto-detect button
        detect_button = ttk.Button(frame, text="Auto-detect", command=self._auto_detect_path)
        detect_button.pack(anchor=tk.W, pady=(0, 20))
        
        # Save/Cancel buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Save", command=self._save_settings).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", command=self.window.destroy).pack(side=tk.RIGHT, padx=(0, 10))
    def _browse_srm_path(self):
        """Browse for SRM executable"""
        filename = filedialog.askopenfilename(
            title="Select Steam ROM Manager executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.path_var.set(filename)
    
    def _auto_detect_path(self):
        """Auto-detect SRM path"""
        detected = self.config_manager.auto_detect_srm_path()
        if detected:
            self.path_var.set(detected)
            if self.logger:
                self.logger(f"✓ Auto-detected SRM at: {detected}", LogLevel.SUCCESS)
        else:
            if self.logger:
                self.logger("✗ Could not auto-detect SRM installation", LogLevel.ERROR)
    
    def _save_settings(self):
        """Save settings and update configuration"""
        new_path = self.path_var.get()
        
        # Validate path
        valid, msg = self._validate_srm_path(new_path)
        if not valid and new_path != "auto-detect":
            messagebox.showerror("Invalid Path", f"Invalid SRM path: {msg}")
            return
        
        # Update configuration
        self.config_manager.config.srm_path = new_path
        success = self.config_manager.save_config()
        
        if success:
            if self.logger:
                self.logger(f"✓ Settings saved. SRM path: {new_path}", LogLevel.SUCCESS)
            self.window.destroy()
        else:
            # Error already logged by ConfigManager, just show dialog
            messagebox.showerror("Save Failed", "Failed to save settings. Check the log for details.")
