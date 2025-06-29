"""
Main application window and coordination logic
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from typing import Optional

from config import ConfigManager, Constants
from core import SteamManager, SRMRunner, SteamError, SRMError
from utils.enums import ProcessStatus, LogLevel
from utils import get_logger
from ui.theme_manager import ThemeManager
from ui.components import SimpleComponents, ProgressSection, LogSection
from ui.dialogs import SettingsDialog


class SteamROMManagerGUI:
    """Main application window and coordination logic"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        # Initialize log_section as None initially
        self.log_section = None
        
        # Get the global logger
        self.logger = get_logger()
        
        self.config_manager = ConfigManager(logger=self._log_config_message)
        self.config = self.config_manager.config
        
        # Update logger level based on config
        if hasattr(self.config, 'log_level'):
            # Note: loguru level update would need to be handled differently
            # For now, we'll keep the existing level
            pass
        
        self.status = ProcessStatus.READY
        self.process_count = 0  # Track how many times process has run
        
        # Initialize managers
        self.steam_manager = SteamManager(self.config.timeout_steam)
        self.theme_manager = ThemeManager()
        
        # Setup SRM path and runner
        self.srm_path = self._resolve_srm_path()
        if self.srm_path:
            self.srm_runner = SRMRunner(self.srm_path, self.config.timeout_srm)
        else:
            self.srm_runner = None
        
        # Setup UI
        self._setup_window()
        self._setup_ui()
        self._initialize_app()
    
    def _resolve_srm_path(self) -> Optional[str]:
        """Resolve SRM executable path"""
        if self.config.srm_path == "auto-detect":
            detected = self.config_manager.auto_detect_srm_path()
            if detected:
                # Only save if the path actually changed
                if self.config.srm_path != detected:
                    self.config.srm_path = detected
                    success = self.config_manager.save_config()
                    if not success:
                        self.log_message("⚠ Auto-detected SRM path but failed to save config", LogLevel.WARNING)
                else:
                    # Path is already correct, no need to save
                    pass
            return detected
        return self.config.srm_path
    def _setup_window(self):
        """Configure main window"""
        self.root.title("Steam ROM Manager Automation")
        self.root.geometry(f"{Constants.UI_DIMENSIONS['width']}x{Constants.UI_DIMENSIONS['height']}")
        self.root.resizable(True, True)
        
        # Apply theme
        self.applied_theme = self.theme_manager.apply_theme(self.config.theme)
        
        # Keyboard shortcuts
        self.root.bind('<F5>', lambda e: self.start_process())
        self.root.bind('<Control-c>', lambda e: self._copy_logs())
        self.root.bind('<Control-s>', lambda e: self._export_logs())
    
    def _setup_ui(self):
        """Setup the user interface components"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Create UI sections
        
        # Simple components (title + controls) with callbacks
        simple_callbacks = {
            'start_process': self.start_process,
            'open_settings': self._open_settings,
            'export_logs': self._export_logs,
            'close_application': self.close_application
        }
        self.simple_components = SimpleComponents(main_frame, simple_callbacks)
        
        self.progress_section = ProgressSection(main_frame)
        
        # Log section
        self.log_section = LogSection(main_frame)
        
        # Connect logger to UI
        self.logger.set_ui_callback(self.log_message)
    
    def _initialize_app(self):
        """Initialize the application after UI setup"""
        # Log theme information
        self.log_message(f"🎨 Theme applied: {self.applied_theme}", LogLevel.INFO)
        
        # Debug theme detection
        try:
            import darkdetect
            detected = darkdetect.theme()
            self.log_message(f"🔍 Theme detection: darkdetect found '{detected}'", LogLevel.INFO)
        except ImportError:
            self.log_message("🔍 Theme detection: darkdetect not available, using light theme", LogLevel.INFO)
        except Exception as e:
            self.log_message(f"🔍 Theme detection: darkdetect failed - {e}", LogLevel.WARNING)
        
        # Configure text colors after theme is set
        self.log_section.refresh_colors()
        
        # Run preflight checks
        self._run_preflight_checks()
        
        # Auto-start if configured
        if self.config.auto_start and self.srm_runner:
            self.root.after(1000, self.start_process)
    def _validate_steam_installation(self) -> bool:
        """Simple Steam installation check"""
        from pathlib import Path
        for path in Constants.COMMON_STEAM_PATHS:
            if Path(path).exists():
                return True
        return False
    
    def _run_preflight_checks(self):
        """Run initial system validation"""
        self.log_message("Running preflight checks...", LogLevel.INFO)
        
        # Check Steam installation
        if self._validate_steam_installation():
            self.log_message("✓ Steam installation found", LogLevel.SUCCESS)
        else:
            self.log_message("⚠ Steam installation not found in common locations", LogLevel.WARNING)
        
        # Check SRM path
        if self.srm_runner:
            valid, msg = self.srm_runner.validate_path()
            if valid:
                self.log_message(f"✓ Steam ROM Manager: {msg}", LogLevel.SUCCESS)
            else:
                self.log_message(f"✗ Steam ROM Manager: {msg}", LogLevel.ERROR)
                self.log_message("Click Settings to configure SRM path", LogLevel.INFO)
        else:
            self.log_message("✗ Steam ROM Manager path not configured", LogLevel.ERROR)
        
        self.log_message("Preflight checks complete. Ready to start.", LogLevel.INFO)
    
    def log_message(self, message: str, level: LogLevel = LogLevel.INFO):
        """Add a message to the output log"""
        if self.log_section:
            self.log_section.log_message(message, level)
            self.root.update_idletasks()
            self.root.update_idletasks()
    
    def _log_config_message(self, message: str, level=None):
        """Log configuration-related messages to the main window"""
        # Handle both LogLevel objects and string level names
        from utils.enums import LogLevel
        
        if isinstance(level, str):
            # Convert string to LogLevel
            level_map = {
                'SUCCESS': LogLevel.SUCCESS,
                'ERROR': LogLevel.ERROR,
                'WARNING': LogLevel.WARNING,
                'INFO': LogLevel.INFO
            }
            level = level_map.get(level, LogLevel.INFO)
        elif level is None:
            level = LogLevel.INFO
        
        # Add appropriate emoji based on level
        if level == LogLevel.SUCCESS:
            emoji = "✓"
        elif level == LogLevel.ERROR:
            emoji = "✗"
        elif level == LogLevel.WARNING:
            emoji = "⚠"
        else:
            emoji = "⚙"
        
        self.log_message(f"{emoji} Config: {message}", level)
    
    def update_progress(self, step: int, percentage: float, message: str, icon: str = "⏳"):
        """Update progress display"""
        self.progress_section.update_progress(step, percentage, message, icon)
        self.root.update_idletasks()
    
    def _update_status_indicator(self, status: ProcessStatus):
        """Update visual status indicator"""
        self.status = status
        self.simple_components.update_status(status)
    def automation_process(self):
        """Main automation process"""
        start_time = time.time()
        
        try:
            self._update_status_indicator(ProcessStatus.RUNNING)
            self.simple_components.set_start_button_state(tk.DISABLED)
            
            # Log start of process
            self.logger.info("Starting automation process")
            
            # Step 1: Kill Steam processes
            self.update_progress(1, 25, "Terminating Steam processes...", "🔄")
            self.log_message("Step 1: Checking Steam processes...", LogLevel.INFO)
            
            success, message = self.steam_manager.graceful_shutdown()
            if success:
                self.log_message(f"✓ {message}", LogLevel.SUCCESS)
                self.logger.success(f"Steam processes terminated: {message}")
            else:
                self.log_message(f"⚠ {message}", LogLevel.WARNING)
                self.logger.warning(f"Steam termination issue: {message}")
            
            # Step 2: Verify closure
            self.update_progress(2, 50, "Verifying Steam is closed...", "🔍")
            self.log_message("Step 2: Final verification...", LogLevel.INFO)
            
            if self.steam_manager.is_running():
                error_msg = "Steam is still running! Manual intervention required."
                self.log_message(f"✗ {error_msg}", LogLevel.ERROR)
                self.logger.error(error_msg)
                self.update_progress(0, 0, "Failed - Steam still running", "✗")
                self._update_status_indicator(ProcessStatus.FAILED)
                return
            else:
                self.log_message("✓ Steam is completely closed", LogLevel.SUCCESS)
                self.logger.success("Steam processes verified as closed")
            
            # Step 3: Execute SRM
            self.update_progress(3, 75, "Running Steam ROM Manager...", "⚙")
            self.log_message("Step 3: Executing Steam ROM Manager...", LogLevel.INFO)
            self.logger.info("Starting Steam ROM Manager execution")
            
            success, output = self.srm_runner.execute_command("add")
            
            # Step 4: Complete
            if success:
                elapsed = time.time() - start_time
                self.update_progress(4, 100, "Process completed successfully!", "✓")
                self.log_message("✓ Steam ROM Manager completed successfully!", LogLevel.SUCCESS)
                self.log_message("✓ ROMs have been added to Steam", LogLevel.SUCCESS)
                self.log_message(f"⏱ Total time: {elapsed:.1f}s", LogLevel.INFO)
                if output:
                    self.log_message(f"Output: {output}", LogLevel.INFO)
                self.logger.success(f"Automation process completed successfully in {elapsed:.1f}s")
                if output:
                    self.logger.info(f"SRM output: {output}")
                self._update_status_indicator(ProcessStatus.SUCCESS)
            else:
                self.update_progress(4, 0, "Process failed - see log for details", "✗")
                self.log_message("✗ Steam ROM Manager failed!", LogLevel.ERROR)
                if output:
                    self.log_message(f"Error: {output}", LogLevel.ERROR)
                    self.logger.error(f"SRM execution failed: {output}")
                else:
                    self.logger.error("SRM execution failed with no output")
                self._update_status_indicator(ProcessStatus.FAILED)
                
        except (SteamError, SRMError) as e:
            self.log_message(f"✗ Operation failed: {e}", LogLevel.ERROR)
            self.logger.error(f"Steam/SRM operation failed: {e}")
            self.update_progress(0, 0, "Process failed - see log", "✗")
            self._update_status_indicator(ProcessStatus.FAILED)
        except Exception as e:
            self.log_message(f"✗ Unexpected error: {e}", LogLevel.ERROR)
            self.logger.error(f"Unexpected error in automation process: {e}")
            self.update_progress(0, 0, "Process failed - unexpected error", "✗")
            self._update_status_indicator(ProcessStatus.FAILED)
        finally:
            self.simple_components.set_start_button_state(tk.NORMAL)
            self.logger.info("Automation process finished")
    def start_process(self):
        """Start the automation process"""
        if self.status == ProcessStatus.RUNNING:
            return
        
        if not self.srm_runner:
            self.log_message("✗ Cannot start: Steam ROM Manager path not configured", LogLevel.ERROR)
            self._open_settings()
            return
        
        # Only clear log on subsequent runs (not first auto-start)
        if self.process_count > 0:
            self.log_section.clear_log()
        
        self.process_count += 1
        self.log_message("🚀 Starting Steam ROM Manager automation...", LogLevel.INFO)
        
        # Start in separate thread
        thread = threading.Thread(target=self.automation_process, daemon=True)
        thread.start()
    
    def _open_settings(self):
        """Open settings dialog"""
        settings_dialog = SettingsDialog(
            self.root, 
            self.config_manager, 
            logger=self.log_message
        )
        settings_dialog.show()
        
        # Update SRM runner if path changed
        new_path = self.config_manager.config.srm_path
        if new_path != "auto-detect" and new_path != self.srm_path:
            self.srm_path = new_path
            self.srm_runner = SRMRunner(self.srm_path, self.config.timeout_srm)
    
    def _copy_logs(self):
        """Copy current logs to clipboard"""
        try:
            content = self.log_section.get_log_content()
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.log_message("📋 Logs copied to clipboard", LogLevel.INFO)
        except Exception as e:
            self.log_message(f"Failed to copy logs: {e}", LogLevel.ERROR)
    
    def _export_logs(self):
        """Export logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Export Log File"
            )
            if filename:
                content = self.log_section.get_log_content()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Steam ROM Manager Automation Log\n")
                    f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*50 + "\n\n")
                    f.write(content)
                self.log_message(f"💾 Log exported to: {filename}", LogLevel.SUCCESS)
        except Exception as e:
            self.log_message(f"Failed to export logs: {e}", LogLevel.ERROR)
    
    def close_application(self):
        """Close the application"""
        if self.status == ProcessStatus.RUNNING:
            if messagebox.askyesno("Confirm", "A process is currently running. Are you sure you want to close?"):
                self.root.quit()
        else:
            self.root.quit()
