"""
Enumeration types for the Steam ROM Manager automation application
"""

from enum import Enum


class ProcessStatus(Enum):
    """Process execution status"""
    READY = "ready"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevel(Enum):
    """Log message levels"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
