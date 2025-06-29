"""
Application directory management using platformdirs
Provides platform-appropriate directories for configuration, logs, and data
"""

from pathlib import Path
from typing import Optional
import platformdirs


class AppDirectories:
    """Manages application directories using platform-appropriate locations"""
    
    def __init__(self, app_name: str = "SRM Automation", app_author: str = "SRM-Automation"):
        self.app_name = app_name
        self.app_author = app_author
        self._platformdirs = platformdirs.PlatformDirs(
            appname=app_name,
            appauthor=app_author,
            ensure_exists=False  # We'll create directories as needed
        )
    
    @property
    def user_config_dir(self) -> Path:
        """Get the user configuration directory"""
        return Path(self._platformdirs.user_config_dir)
    
    @property
    def user_data_dir(self) -> Path:
        """Get the user data directory"""
        return Path(self._platformdirs.user_data_dir)
    
    @property
    def user_log_dir(self) -> Path:
        """Get the user log directory"""
        return Path(self._platformdirs.user_log_dir)
    
    @property
    def user_cache_dir(self) -> Path:
        """Get the user cache directory"""
        return Path(self._platformdirs.user_cache_dir)
    
    def get_config_file_path(self, filename: str = "srm_config.json") -> Path:
        """Get the full path to a configuration file
        
        Args:
            filename: Name of the configuration file
            
        Returns:
            Full path to the configuration file
        """
        return self.user_config_dir / filename
    
    def get_log_file_path(self, filename: str = "error.log") -> Path:
        """Get the full path to a log file
        
        Args:
            filename: Name of the log file
            
        Returns:
            Full path to the log file
        """
        return self.user_log_dir / filename
    
    def ensure_directories_exist(self) -> bool:
        """Create all necessary directories if they don't exist
        
        Returns:
            True if all directories were created successfully, False otherwise
        """
        try:
            self.user_config_dir.mkdir(parents=True, exist_ok=True)
            self.user_data_dir.mkdir(parents=True, exist_ok=True)
            self.user_log_dir.mkdir(parents=True, exist_ok=True)
            self.user_cache_dir.mkdir(parents=True, exist_ok=True)
            return True
        except (OSError, PermissionError):
            return False
    
    def migrate_legacy_config(self, legacy_config_path: Path) -> bool:
        """Migrate configuration from legacy location to new platform-appropriate location
        
        Args:
            legacy_config_path: Path to the old configuration file
            
        Returns:
            True if migration was successful, False otherwise
        """
        if not legacy_config_path.exists():
            return True  # Nothing to migrate
        
        try:
            # Ensure the new config directory exists
            self.user_config_dir.mkdir(parents=True, exist_ok=True)
            
            new_config_path = self.get_config_file_path()
            
            # Don't overwrite existing new config
            if new_config_path.exists():
                return True
            
            # Copy the legacy config to the new location
            import shutil
            shutil.copy2(legacy_config_path, new_config_path)
            
            return True
        except (OSError, PermissionError, Exception):
            return False
    
    def get_legacy_config_path(self, current_working_dir: Optional[Path] = None) -> Path:
        """Get the legacy configuration file path (current working directory)
        
        Args:
            current_working_dir: The working directory to check for legacy config
            
        Returns:
            Path to the legacy configuration file
        """
        if current_working_dir is None:
            current_working_dir = Path.cwd()
        
        return current_working_dir / "srm_config.json"


# Global instance for easy access
app_dirs = AppDirectories()
