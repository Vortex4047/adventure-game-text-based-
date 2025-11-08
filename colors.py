"""
Color output system for enhanced UI
"""
import sys
from typing import Optional


class Colors:
    """ANSI color codes for terminal output"""
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Reset
    RESET = '\033[0m'
    
    # Semantic colors
    SUCCESS = GREEN
    ERROR = RED
    WARNING = YELLOW
    INFO = CYAN
    CRITICAL = BRIGHT_RED
    HEALTH = BRIGHT_GREEN
    DAMAGE = RED
    GOLD = YELLOW
    EXP = BRIGHT_CYAN
    
    @staticmethod
    def is_supported() -> bool:
        """Check if terminal supports colors"""
        import os
        return sys.stdout.isatty() and (sys.platform != 'win32' or 'ANSICON' in os.environ)
    
    @classmethod
    def disable(cls) -> None:
        """Disable all colors"""
        for attr in dir(cls):
            if not attr.startswith('_') and attr.isupper():
                setattr(cls, attr, '')


# Auto-disable colors if not supported
if not Colors.is_supported():
    Colors.disable()


def colored(text: str, color: str, bold: bool = False) -> str:
    """Return colored text"""
    if bold:
        return f"{Colors.BOLD}{color}{text}{Colors.RESET}"
    return f"{color}{text}{Colors.RESET}"


def success(text: str) -> str:
    """Green success message"""
    return colored(text, Colors.SUCCESS)


def error(text: str) -> str:
    """Red error message"""
    return colored(text, Colors.ERROR)


def warning(text: str) -> str:
    """Yellow warning message"""
    return colored(text, Colors.WARNING)


def info(text: str) -> str:
    """Cyan info message"""
    return colored(text, Colors.INFO)


def health_bar(current: int, maximum: int, width: int = 20) -> str:
    """Create a colored health bar"""
    percentage = current / maximum if maximum > 0 else 0
    filled = int(percentage * width)
    empty = width - filled
    
    # Color based on health percentage
    if percentage > 0.6:
        color = Colors.BRIGHT_GREEN
    elif percentage > 0.3:
        color = Colors.YELLOW
    else:
        color = Colors.RED
    
    bar = f"{color}{'█' * filled}{Colors.RESET}{'░' * empty}"
    return f"[{bar}] {current}/{maximum}"


def rarity_color(rarity: str) -> str:
    """Get color for item rarity"""
    rarity_colors = {
        "common": Colors.WHITE,
        "uncommon": Colors.GREEN,
        "rare": Colors.BLUE,
        "epic": Colors.MAGENTA,
        "legendary": Colors.YELLOW
    }
    return rarity_colors.get(rarity.lower(), Colors.WHITE)
