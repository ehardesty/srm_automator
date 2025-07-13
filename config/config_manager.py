"""
Configuration file management and persistence using Pydantic Settings
Enhanced with platform-appropriate directories and legacy migration
"""

import json
import os
from pathlib import Path
from typing import Optional, Callable
from pydantic import ValidationError

from .app_config import AppConfig
from .constants import Constants
from .app_dirs import app_dirs


class ConfigManager:
    """Handles loading, saving, and managing application configuration with platform-appropriate directories"""
    
    def __init__(self, config_file: Optional[str] = None, logger: Optional[Callable] = None):
        self.logger = logger
        
        # Use platform-appropriate config file if none specified
        if config_file is None:
            self.config_file = Path(Constants.CONFIG_FILE)
        else:
            self.config_file = Path(config_file)
        
        # Ensure directories exist
        app_dirs.ensure_directories_exist()
        
        self.config = self.load_config()
    
    def _log(self, message: str, level_name: str = "ERROR"):
        """Log message using provided logger or fallback to print"""
        if self.logger:
            try:
                from utils.enums import LogLevel
                from .constants import Constants
                
                level_map = {
                    'SUCCESS': LogLevel.SUCCESS,
                    'ERROR': LogLevel.ERROR,
                    'WARNING': LogLevel.WARNING,
                    'INFO': LogLevel.INFO
                }
                log_level = level_map.get(level_name, LogLevel.ERROR)
                self.logger(message, log_level)
            except Exception:
                print(f"Config: {message}")
        else:
            print(f"Config: {message}")
    
    def load_config(self) -> AppConfig:
        """Load configuration from file, environment variables, or create default"""
        try:
            # First try to load from JSON file if it exists
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    json_data = json.load(f)
                
                # Create config with JSON data and environment variable overrides
                config = AppConfig(**json_data)
                return config
            else:
                # Create default config (will still check environment variables)
                config = AppConfig()
                # Save the default config for future use
                self.save_config_internal(config)
                return config
                
        except ValidationError as e:
            self._log(f"Configuration validation failed: {e}", "ERROR")
            # Return default config on validation error
            return AppConfig()
        except json.JSONDecodeError as e:
            self._log(f"Config file corrupted, using defaults: {e}", "WARNING")
        except FileNotFoundError:
            self._log(f"Config file not found: {self.config_file}", "INFO")
        except PermissionError:
            self._log(f"Permission denied reading config file: {self.config_file}", "ERROR")
        except Exception as e:
            self._log(f"Unexpected error reading config file: {e}", "ERROR")
        
        # Return default config if any error occurred
        return AppConfig()
    
    def can_write_config(self) -> bool:
        """Check if we can write to the config file location"""
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Try to open the file in write mode (this will create it if it doesn't exist)
            with open(self.config_file, 'a'):
                pass
            return True
        except (PermissionError, OSError):
            return False
    
    def save_config(self) -> bool:
        """Save current configuration to file with retry logic
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        return self.save_config_internal(self.config)
    
    def save_config_internal(self, config: AppConfig) -> bool:
        """Simplified method to save configuration
        
        Args:
            config: AppConfig instance to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Simple write to file
            with open(self.config_file, 'w') as f:
                json.dump(config.model_dump(), f, indent=2)
            
            self._log(f"Configuration saved to {self.config_file}", "SUCCESS")
            return True
            
        except PermissionError:
            self._log(f"Permission denied writing config file: {self.config_file}", "ERROR")
            return False
            
        except Exception as e:
            self._log(f"Failed to save config: {e}", "ERROR")
            return False
    
    def auto_detect_srm_path(self) -> Optional[str]:
        """Auto-detect Steam ROM Manager installation path"""
        username = os.getenv('USERNAME', 'User')
        
        for path_template in Constants.COMMON_SRM_PATHS:
            path = path_template.format(username=username)
            if Path(path).exists():
                return path
        
        return None
