"""
Custom exception classes for the Steam ROM Manager automation application
"""


class SteamError(Exception):
    """Steam-related operation errors"""
    pass


class SRMError(Exception):
    """Steam ROM Manager operation errors"""
    pass


class ConfigError(Exception):
    """Configuration-related errors"""
    pass
