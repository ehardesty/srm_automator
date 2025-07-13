"""
Application constants and default values
Enhanced with platform-appropriate directories
"""

from .app_dirs import app_dirs


class Constants:
    """Application constants and default configuration values"""
    
    # Steam process names to monitor and kill
    STEAM_PROCESSES = ['steam.exe', 'steamservice.exe', 'steamwebhelper.exe']
    
    # Default timeout values in seconds
    DEFAULT_TIMEOUTS = {
        'steam_kill': 30,      # Timeout for killing Steam processes
        'srm_execute': 120,    # Timeout for SRM execution
        'steam_wait': 10       # Timeout for Steam process checks
    }
    
    # UI dimensions and layout
    UI_DIMENSIONS = {
        'width': 700,
        'height': 600
    }
    
    # Configuration file paths - now using platform-appropriate directories
    CONFIG_FILE = str(app_dirs.get_config_file_path())
    LEGACY_CONFIG_FILE = 'srm_config.json'  # For migration purposes
    
    # Log file path - platform-appropriate
    LOG_FILE = str(app_dirs.get_log_file_path())
    
    # Common Steam ROM Manager installation paths
    COMMON_SRM_PATHS = [
        r"C:\Users\{username}\AppData\Local\Programs\steam-rom-manager\Steam ROM Manager.exe",
        r"C:\Program Files\Steam ROM Manager\Steam ROM Manager.exe",
        r"C:\Program Files (x86)\Steam ROM Manager\Steam ROM Manager.exe",
    ]
    
    # Common Steam installation paths
    COMMON_STEAM_PATHS = [
        r"C:\Program Files (x86)\Steam",
        r"C:\Program Files\Steam",
    ]
    
    # Centralized log level and status color mappings
    LOG_LEVEL_MAPPING = {
        'SUCCESS': 'SUCCESS',
        'ERROR': 'ERROR', 
        'WARNING': 'WARNING',
        'INFO': 'INFO'
    }
    
    # UI Status colors
    STATUS_COLORS = {
        'ready': '#4caf50',      # Green
        'running': '#ff9800',    # Orange
        'success': '#4caf50',    # Green
        'failed': '#f44336',     # Red
        'warning': '#ff9800'     # Orange
    }
