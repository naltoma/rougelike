"""
Display types and enums for GUI enhancement module.
Defines emphasis types, color configurations, and text formatting options.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional


class EmphasisType(Enum):
    """Visual emphasis type for status display."""
    DEFAULT = "default"
    DECREASED = "decreased"
    INCREASED = "increased"


@dataclass
class ColorConfig:
    """Color configuration for different emphasis types."""
    default_color: Tuple[int, int, int] = (255, 255, 255)  # White
    decreased_color: Tuple[int, int, int] = (255, 0, 0)    # Red
    increased_color: Tuple[int, int, int] = (0, 255, 0)    # Green

    def __post_init__(self):
        """Validate RGB color values."""
        for color_name, color_value in [
            ("default_color", self.default_color),
            ("decreased_color", self.decreased_color),
            ("increased_color", self.increased_color)
        ]:
            if not isinstance(color_value, tuple) or len(color_value) != 3:
                raise ValueError(f"{color_name} must be a 3-tuple")

            for component in color_value:
                if not isinstance(component, int) or component < 0 or component > 255:
                    raise ValueError(f"{color_name} RGB values must be integers 0-255")


@dataclass
class TextFormatConfig:
    """Text formatting configuration."""
    normal_font_size: int = 24
    bold_font_size: int = 24
    font_family: Optional[str] = None
    decrease_symbol: str = "-"
    increase_symbol: str = "+"

    def __post_init__(self):
        """Validate font configuration."""
        if self.normal_font_size <= 0:
            raise ValueError("normal_font_size must be positive")
        if self.bold_font_size <= 0:
            raise ValueError("bold_font_size must be positive")