"""
Platform-specific utilities for subprocess handling
"""

import sys
import subprocess


def get_subprocess_flags() -> dict:
    """Get platform-specific subprocess flags to hide command windows"""
    if sys.platform == "win32":
        # Prevent subprocess from creating command windows
        flags = {
            'creationflags': subprocess.CREATE_NO_WINDOW,
            'startupinfo': subprocess.STARTUPINFO()
        }
        flags['startupinfo'].dwFlags |= subprocess.STARTF_USESHOWWINDOW
        flags['startupinfo'].wShowWindow = subprocess.SW_HIDE
        return flags
    else:
        return {}
