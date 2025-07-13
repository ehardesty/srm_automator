"""
Simplified logging configuration using loguru
Maintains essential UI integration while reducing complexity
"""

import sys
from pathlib import Path
from typing import Optional, Callable
from loguru import logger
from utils.enums import LogLevel
from config.app_dirs import app_dirs


# Simple module-level logger reference
_current_logger = logger


class LogManager:
    """Simplified logging management with basic UI integration"""
    
    def __init__(self, log_level: str = "info", log_file: Optional[str] = None):
        self.log_level = log_level.upper()
        self.log_file = log_file
        self.ui_callback: Optional[Callable] = None
        
        # Remove default handler
        logger.remove()
        
        # Add console handler with colors
        try:
            console_sink = sys.stderr or sys.stdout
            if console_sink:
                logger.add(
                    console_sink,
                    level=self.log_level,
                    format="<green>{time:HH:mm:ss}</green> | "
                           "<level>{level: <8}</level> | "
                           "<level>{message}</level>",
                    colorize=True
                )
        except Exception:
            # Continue without console logging
            pass
        
        # Add file handler with basic rotation
        if self.log_file:
            try:
                log_path = Path(self.log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                logger.add(
                    self.log_file,
                    level=self.log_level,
                    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
                    rotation="50 MB",  # Simplified rotation
                    retention="30 days"
                )
            except Exception:
                # Continue without file logging
                pass
    
    def set_ui_callback(self, callback: Callable):
        """Set UI callback for log display"""
        self.ui_callback = callback
        
        # Add UI handler if callback is provided
        if callback:
            def ui_handler(record):
                try:
                    # Convert loguru level to our LogLevel enum
                    level_map = {
                        "DEBUG": LogLevel.INFO,
                        "INFO": LogLevel.INFO,
                        "SUCCESS": LogLevel.SUCCESS,
                        "WARNING": LogLevel.WARNING,
                        "ERROR": LogLevel.ERROR
                    }
                    ui_level = level_map.get(record["level"].name, LogLevel.INFO)
                    callback(record["message"], ui_level)
                except Exception:
                    # Ignore UI failures
                    pass
            
            logger.add(ui_handler, level=self.log_level)
    
    def get_logger(self):
        """Get the global logger instance"""
        return logger


def setup_logging(log_level: str = "info", log_file: Optional[str] = None) -> LogManager:
    """Simplified logging setup function"""
    # Use platform-appropriate log file if none specified
    if log_file is None:
        try:
            log_file = str(app_dirs.get_log_file_path())
        except Exception:
            log_file = "error.log"
    
    log_manager = LogManager(log_level=log_level, log_file=log_file)
    
    # Add set_ui_callback method to logger for compatibility
    def set_ui_callback(callback: Callable):
        log_manager.set_ui_callback(callback)
    
    logger.set_ui_callback = set_ui_callback
    
    return log_manager


def get_logger():
    """Get the global logger instance"""
    return _current_logger
