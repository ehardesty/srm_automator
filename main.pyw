#!/usr/bin/env python3
"""
Steam ROM Manager GUI Automation Script
Simplified main entry point for the application
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import sys
import traceback
from pathlib import Path


def setup_basic_logging():
    """Setup basic error logging for startup issues"""
    import logging
    
    try:
        # Get script directory with fallbacks
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller bundle
            script_dir = Path(sys._MEIPASS)
        elif __file__:
            # Normal execution
            script_dir = Path(__file__).resolve().parent
        else:
            # Fallback
            script_dir = Path.cwd()
        
        log_file = script_dir / "error.log"
        
    except Exception:
        log_file = Path("error.log")
    
    logging.basicConfig(
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler() if sys.stderr else logging.NullHandler()
        ]
    )
    return logging.getLogger(__name__)


def show_error_dialog(error_msg, detailed_error):
    """Show simplified error dialog"""
    try:
        # Try standard messagebox first
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Combine messages for display
        full_message = f"{error_msg}\n\nTechnical Details:\n{detailed_error[:500]}..."
        if len(detailed_error) <= 500:
            full_message = f"{error_msg}\n\nTechnical Details:\n{detailed_error}"
        
        messagebox.showerror(
            "Steam ROM Manager - Startup Error",
            full_message
        )
        root.destroy()
        
    except Exception:
        # Console fallback
        print(f"ERROR: {error_msg}")
        print(f"Details: {detailed_error}")
        print("Check error.log for full details")


def check_basic_dependencies():
    """Check essential dependencies"""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter (Python GUI library)")
    
    try:
        # Test import of main modules
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))
        
        from ui import SteamROMManagerGUI
    except ImportError as e:
        missing_deps.append(f"Application modules: {e}")
    
    return missing_deps


def main():
    """Simplified main application entry point"""
    logger = setup_basic_logging()
    
    try:
        logger.info("Starting Steam ROM Manager application...")
        
        # Check dependencies
        missing_deps = check_basic_dependencies()
        if missing_deps:
            error_msg = "Missing required dependencies"
            detailed_error = "Missing dependencies:\n" + "\n".join(f"- {dep}" for dep in missing_deps)
            logger.error(f"{error_msg}: {detailed_error}")
            show_error_dialog(error_msg, detailed_error)
            return 1
        
        # Import after dependency check
        from ui import SteamROMManagerGUI
        from utils import setup_logging

        # Setup logging system
        try:
            log_manager = setup_logging(log_level="info")
            logger = log_manager.get_logger()
            logger.info("Application starting with enhanced logging")
            
        except Exception as log_error:
            error_details = f"Logging setup error: {log_error}"
            try:
                log_manager = setup_logging(log_level="info", log_file=None)
                logger = log_manager.get_logger()
                logger.error(error_details)
            except Exception:
                # Continue without enhanced logging
                logger.error("Failed to setup enhanced logging, continuing with basic logging")
        
        # Create and run application
        root = tk.Tk()
        
        # Simple error handler for tkinter
        def handle_tk_error(exc, val, tb):
            error_msg = f"GUI Error: {val}"
            detailed_error = ''.join(traceback.format_exception(exc, val, tb))
            
            if logger:
                logger.error(f"Tkinter error: {detailed_error}")
            
            try:
                messagebox.showerror(
                    "Application Error", 
                    f"An error occurred:\n\n{error_msg}\n\nThe application may be unstable."
                )
            except:
                pass
        
        root.report_callback_exception = handle_tk_error
        
        # Create and run GUI
        logger.info("Creating main window...")
        gui = SteamROMManagerGUI(root)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        logger.info("Starting main event loop...")
        root.mainloop()
        
        logger.info("Application closed normally")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
        
    except ImportError as e:
        error_msg = "Failed to import required modules"
        detailed_error = f"Import Error: {e}\n\n{traceback.format_exc()}"
        logger.error(f"{error_msg}: {detailed_error}")
        show_error_dialog(error_msg, detailed_error)
        return 1
        
    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        detailed_error = traceback.format_exc()
        logger.error(f"Unexpected error: {detailed_error}")
        show_error_dialog(error_msg, detailed_error)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
