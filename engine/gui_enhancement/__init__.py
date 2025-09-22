"""
GUI Enhancement Module for Rogue-like Educational Framework
Provides dynamic stage name display and status change highlighting.
"""

from .status_change_tracker import StatusChangeTracker
from .stage_name_resolver import StageNameResolver
from .display_state_manager import DisplayStateManager
from .display_types import EmphasisType, ColorConfig
from .data_types import FormattedText, ChangeResult

__version__ = "1.2.11"
__all__ = [
    "StatusChangeTracker",
    "StageNameResolver",
    "DisplayStateManager",
    "EmphasisType",
    "ColorConfig",
    "FormattedText",
    "ChangeResult",
]