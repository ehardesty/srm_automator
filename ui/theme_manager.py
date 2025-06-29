"""
Theme detection and management for the application
"""

# Optional dependency imports
try:
    import sv_ttk
    SV_TTK_AVAILABLE = True
except ImportError:
    SV_TTK_AVAILABLE = False

try:
    import darkdetect
    DARKDETECT_AVAILABLE = True
except ImportError:
    DARKDETECT_AVAILABLE = False


class ThemeManager:
    """Handles application theme detection and application"""
    
    @staticmethod
    def detect_windows_theme() -> str:
        """Detect Windows dark/light theme preference"""
        if DARKDETECT_AVAILABLE:
            try:
                theme = darkdetect.theme()  # Returns 'Dark' or 'Light'
                detected = theme.lower() if theme else "light"
                return detected
            except Exception:
                return "light"
        else:
            return "light"  # Default fallback
    
    @staticmethod
    def apply_theme(theme: str = "auto") -> str:
        """Apply theme and return applied theme name"""
        if not SV_TTK_AVAILABLE:
            return "default (sv_ttk not available)"
        
        if theme == "auto":
            if DARKDETECT_AVAILABLE:
                detected_theme = ThemeManager.detect_windows_theme()
                theme = detected_theme
            else:
                theme = "light"
        
        try:
            sv_ttk.set_theme(theme)
            return theme
        except Exception:
            sv_ttk.set_theme("light")
            return "light (fallback)"
    
    @staticmethod
    def is_dark_theme_active() -> bool:
        """Check if dark theme is currently active"""
        if DARKDETECT_AVAILABLE:
            try:
                theme = darkdetect.theme()
                return theme and theme.lower() == 'dark'
            except:
                pass
        return False
