"""
Steam process management and control using psutil
"""

import time
import subprocess
from typing import Tuple, List, Optional
from pathlib import Path
import psutil

from config.constants import Constants


class SteamManager:
    """Handles Steam process operations and lifecycle management"""
    
    def __init__(self, timeout: int = Constants.DEFAULT_TIMEOUTS['steam_kill']):
        self.timeout = timeout
        self.was_running_before_shutdown = False
        self.steam_executable_path: Optional[str] = None
    
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
        """Attempt graceful Steam shutdown and record state for potential restart"""
        if not self.is_running():
            self.was_running_before_shutdown = False
            return True, "Steam not running"
        
        # Record that Steam was running and try to find its executable
        self.was_running_before_shutdown = True
        self.steam_executable_path = self.find_steam_executable()
        
        # Try to kill processes
        if not self.kill_processes():
            return False, "Failed to terminate Steam processes"
        
        # Wait for complete closure
        if not self.wait_for_closure():
            return False, f"Steam still running after {self.timeout}s timeout"
        
        return True, "Steam closed successfully"
    
    def find_steam_executable(self) -> Optional[str]:
        """Find Steam executable path from common installation locations"""
        for exe_path in Constants.COMMON_STEAM_EXECUTABLE_PATHS:
            if Path(exe_path).exists():
                return exe_path
        
        # Try to find Steam from running processes
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                if proc.info['name'] and proc.info['name'].lower() == 'steam.exe':
                    if proc.info['exe']:
                        return proc.info['exe']
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        
        return None
    
    def start_steam(self, steam_path: Optional[str] = None) -> Tuple[bool, str]:
        """Start Steam process
        
        Args:
            steam_path: Optional path to Steam executable. If None, will auto-detect.
            
        Returns:
            Tuple of (success, message)
        """
        if not steam_path:
            steam_path = self.steam_executable_path or self.find_steam_executable()
        
        if not steam_path:
            return False, "Steam executable not found"
        
        if not Path(steam_path).exists():
            return False, f"Steam executable not found at: {steam_path}"
        
        try:
            # Start Steam with minimal output
            subprocess.Popen(
                [steam_path, "-silent"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            
            # Give Steam a moment to start
            time.sleep(2)
            
            # Verify it started
            if self.is_running():
                return True, "Steam started successfully"
            else:
                return False, "Steam process started but not detected as running"
                
        except Exception as e:
            return False, f"Failed to start Steam: {e}"
