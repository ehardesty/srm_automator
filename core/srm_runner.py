"""
Steam ROM Manager execution and command handling
Simplified with basic path validation
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple

from config.constants import Constants
from utils.platform_utils import get_subprocess_flags
from .exceptions import SRMError


class SRMRunner:
    """Handles Steam ROM Manager execution and command processing"""
    
    def __init__(self, srm_path: str, timeout: int = Constants.DEFAULT_TIMEOUTS['srm_execute']):
        self.srm_path = Path(srm_path)
        self.timeout = timeout
        self.subprocess_flags = get_subprocess_flags()
    
    def validate_path(self) -> Tuple[bool, str]:
        """Simple SRM executable validation
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.srm_path:
            return False, "No SRM path specified"
            
        try:
            path_obj = Path(self.srm_path)
            
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
    
    def execute_command(self, command: str = "add") -> Tuple[bool, str]:
        """Execute SRM with specified command"""
        is_valid, error_msg = self.validate_path()
        if not is_valid:
            raise SRMError(f"Steam ROM Manager validation failed: {error_msg}")
        
        try:
            cmd = [str(self.srm_path), command]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.srm_path.parent,
                **self.subprocess_flags
            )
            
            output = result.stdout + result.stderr
            return result.returncode == 0, output.strip()
            
        except subprocess.TimeoutExpired:
            raise SRMError(f"Steam ROM Manager timed out after {self.timeout}s")
        except Exception as e:
            raise SRMError(f"Failed to execute Steam ROM Manager: {e}")
