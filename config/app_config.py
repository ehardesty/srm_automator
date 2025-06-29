"""
Application configuration data structure using Pydantic Settings
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application configuration settings with validation"""
    
    srm_path: str = Field(default="auto-detect", description="Path to Steam ROM Manager executable")
    theme: str = Field(default="auto", description="UI theme (auto, light, dark)")
    auto_start: bool = Field(default=True, description="Auto-start the process on application start")
    log_level: str = Field(default="info", description="Logging level (debug, info, warning, error)")
    timeout_steam: int = Field(default=30, ge=5, le=300, description="Timeout for Steam process termination (seconds)")
    timeout_srm: int = Field(default=120, ge=10, le=600, description="Timeout for SRM execution (seconds)")
    backup_shortcuts: bool = Field(default=True, description="Create backup of shortcuts before modification")
    
    class Config:
        env_prefix = "SRM_"  # Environment variables like SRM_THEME, SRM_AUTO_START
        env_file = ".env"
        case_sensitive = False
        json_file = "srm_config.json"
        json_file_encoding = "utf-8"
    
    @field_validator('theme')
    @classmethod
    def validate_theme(cls, v: str) -> str:
        """Validate theme value"""
        valid_themes = {'auto', 'light', 'dark'}
        if v.lower() not in valid_themes:
            raise ValueError(f"Theme must be one of: {', '.join(valid_themes)}")
        return v.lower()
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level value"""
        valid_levels = {'debug', 'info', 'warning', 'error'}
        if v.lower() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.lower()
    
    @field_validator('srm_path')
    @classmethod
    def validate_srm_path(cls, v: str) -> str:
        """Validate SRM path if not auto-detect"""
        if v != "auto-detect" and v:
            path = Path(v)
            if not path.exists():
                # Don't raise error, just return the path for later auto-detection
                pass
            elif not path.is_file():
                raise ValueError(f"SRM path must be a file: {v}")
            elif not str(path).endswith('.exe'):
                raise ValueError(f"SRM path must be an executable (.exe) file: {v}")
        return v
