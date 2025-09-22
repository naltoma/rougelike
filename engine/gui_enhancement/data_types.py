"""
Data types for GUI enhancement module.
Defines structured data objects for formatted text, change results, and stage resolution.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional
from .display_types import EmphasisType


@dataclass
class FormattedText:
    """Represents formatted text with visual properties."""
    content: str
    color: Tuple[int, int, int]
    is_bold: bool
    emphasis_type: EmphasisType


@dataclass
class ChangeResult:
    """Result of status change tracking."""
    entity_id: str
    status_changes: Dict[str, int]
    has_any_changes: bool
    emphasis_map: Dict[str, EmphasisType]


@dataclass
class StageResolution:
    """Result of stage name resolution."""
    stage_id: str
    file_path: str
    resolved_name: str
    is_cached: bool


@dataclass
class ValidationResult:
    """Result of stage ID validation."""
    is_valid: bool
    stage_id: str
    error_message: Optional[str] = None


@dataclass
class PygameSurface:
    """Mock pygame surface for testing purposes."""
    width: int
    height: int
    content_hash: str