"""
Steam process management and control using psutil
"""

import time
from typing import Tuple, List
import psutil

from config.constants import Constants


class SteamManager:
    """Handles Steam process operations and lifecycle management"""
    
    def __init__(self, timeout: int = Constants.DEFAULT_TIMEOUTS['steam_kill']):
        self.timeout = timeout
    
    def _get_steam_processes(self) -> List[psutil.Process]:
        """Get all running Steam processes"""
        steam_processes = []
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() in [p.lower() for p in Constants.STEAM_PROCESSES]:
                    steam_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # Process might have ended during iteration
                continue
        return steam_processes
    
    def is_running(self) -> bool:
        """Check if any Steam processes are running"""
        try:
            return len(self._get_steam_processes()) > 0
        except Exception:
            return False
    
    def kill_processes(self) -> bool:
        """Terminate Steam processes gracefully, then forcefully if needed"""
        steam_processes = self._get_steam_processes()
        if not steam_processes:
            return True
        
        success = True
        
        # First attempt: graceful termination
        for proc in steam_processes:
            try:
                proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process already ended or access denied
                continue
            except Exception:
                success = False
        
        # Wait a moment for graceful termination
        time.sleep(1)
        
        # Second attempt: force kill any remaining processes
        remaining_processes = self._get_steam_processes()
        for proc in remaining_processes:
            try:
                proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Process already ended or access denied
                continue
            except Exception:
                success = False
        
        return success
    
    def wait_for_closure(self, max_wait: int = None) -> bool:
        """Wait for Steam to fully close with exponential backoff"""
        max_wait = max_wait or self.timeout
        wait_time = 0.5
        total_waited = 0
        
        while total_waited < max_wait:
            if not self.is_running():
                return True
            
            time.sleep(wait_time)
            total_waited += wait_time
            wait_time = min(wait_time * 1.5, 3)  # Exponential backoff, max 3s
        
        return False
    
    def graceful_shutdown(self) -> Tuple[bool, str]:
        """Attempt graceful Steam shutdown"""
        if not self.is_running():
            return True, "Steam not running"
        
        # Try to kill processes
        if not self.kill_processes():
            return False, "Failed to terminate Steam processes"
        
        # Wait for complete closure
        if not self.wait_for_closure():
            return False, f"Steam still running after {self.timeout}s timeout"
        
        return True, "Steam closed successfully"
