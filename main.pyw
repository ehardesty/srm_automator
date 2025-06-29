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
    """Show enhanced but simpler error dialog"""
    try:
        # Create enhanced error dialog
        root = tk.Tk()
        root.title("Steam ROM Manager - Startup Error")
        root.geometry("600x400")
        root.configure(bg='#f0f0f0')
        
        # Make it stay on top
        root.attributes('-topmost', True)
        
        # Main frame
        main_frame = tk.Frame(root, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Error title
        title_label = tk.Label(
            main_frame, 
            text="Failed to start application:", 
            font=('Arial', 12, 'bold'), 
            fg='#d32f2f', 
            bg='#f0f0f0'
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # Error message
        error_label = tk.Label(
            main_frame, 
            text=error_msg,
            font=('Arial', 10), 
            fg='#000', 
            bg='#f0f0f0', 
            wraplength=550
        )
        error_label.pack(anchor='w', pady=(0, 15))
        
        # Details section
        details_label = tk.Label(
            main_frame, 
            text="Technical Details:",
            font=('Arial', 10, 'bold'), 
            fg='#000', 
            bg='#f0f0f0'
        )
        details_label.pack(anchor='w', pady=(0, 5))
        
        # Scrollable text for error details
        text_widget = scrolledtext.ScrolledText(
            main_frame, 
            wrap=tk.WORD, 
            font=('Consolas', 9),
            height=15,
            bg='white', 
            fg='black'
        )
        text_widget.pack(fill='both', expand=True, pady=(0, 15))
        text_widget.insert('1.0', detailed_error)
        text_widget.configure(state='disabled')
        
        # OK button
        def close_dialog():
            root.destroy()
        
        ok_button = tk.Button(
            main_frame, 
            text="OK", 
            command=close_dialog,
            bg='#4caf50', 
            fg='white', 
            font=('Arial', 10), 
            padx=30, 
            pady=5
        )
        ok_button.pack(pady=5)
        
        # Center window
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (600 // 2)
        y = (root.winfo_screenheight() // 2) - (400 // 2)
        root.geometry(f"600x400+{x}+{y}")
        
        # Keyboard shortcuts
        root.bind('<Return>', lambda e: close_dialog())
        root.bind('<Escape>', lambda e: close_dialog())
        
        # Focus and show
        ok_button.focus_set()
        root.mainloop()
        
    except Exception:
        # Simple fallback
        try:
            fallback_root = tk.Tk()
            fallback_root.withdraw()
            messagebox.showerror(
                "Startup Error",
                f"{error_msg}\n\nCheck error.log for detailed information."
            )
            fallback_root.destroy()
        except Exception:
            # Ultimate fallback - print to console
            print(f"ERROR: {error_msg}")
            print("Check error.log for details")


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
