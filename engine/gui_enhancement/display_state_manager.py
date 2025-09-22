"""
DisplayStateManager implementation for managing visual formatting of status changes.
Handles color formatting, emphasis states, and pygame text rendering integration.
"""

from typing import Dict, Optional
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

from .display_types import EmphasisType, ColorConfig, TextFormatConfig
from .data_types import FormattedText, PygameSurface


class DisplayStateManager:
    """Manages visual formatting states for status values based on change detection."""

    def __init__(self, color_config: Optional[ColorConfig] = None,
                 text_config: Optional[TextFormatConfig] = None):
        """
        Initialize display state manager.

        Args:
            color_config: Color configuration for different emphasis types
            text_config: Text formatting configuration
        """
        self.color_config = color_config or ColorConfig()
        self.text_config = text_config or TextFormatConfig()
        self.emphasis_state: Dict[str, Dict[str, EmphasisType]] = {}

        # Initialize pygame fonts if available
        if PYGAME_AVAILABLE:
            try:
                pygame.font.init()
                self.normal_font = pygame.font.Font(None, self.text_config.normal_font_size)
                self.bold_font = pygame.font.Font(None, self.text_config.bold_font_size)
                self.bold_font.set_bold(True)
            except Exception:
                # Fallback if pygame font initialization fails
                self.normal_font = None
                self.bold_font = None
        else:
            self.normal_font = None
            self.bold_font = None

    def format_status_text(self, entity_id: str, status_key: str, value: int, change: int) -> FormattedText:
        """
        Create formatted text object based on status value and change.

        Args:
            entity_id: Entity identifier
            status_key: Status key (e.g., "hp", "attack")
            value: Current status value
            change: Change delta (positive=increase, negative=decrease, 0=no change)

        Returns:
            FormattedText with appropriate formatting
        """
        # Determine emphasis type
        emphasis_type = self.get_emphasis_type(change)

        # Build content string
        if change < 0:
            content = f"{value} ({self.text_config.decrease_symbol}{abs(change)})"
        elif change > 0:
            content = f"{value} ({self.text_config.increase_symbol}{change})"
        else:
            content = str(value)

        # Determine color based on emphasis
        if emphasis_type == EmphasisType.DECREASED:
            color = self.color_config.decreased_color
        elif emphasis_type == EmphasisType.INCREASED:
            color = self.color_config.increased_color
        else:
            color = self.color_config.default_color

        # Determine if bold
        is_bold = emphasis_type != EmphasisType.DEFAULT

        # Store emphasis state
        if entity_id not in self.emphasis_state:
            self.emphasis_state[entity_id] = {}
        self.emphasis_state[entity_id][status_key] = emphasis_type

        return FormattedText(
            content=content,
            color=color,
            is_bold=is_bold,
            emphasis_type=emphasis_type
        )

    def get_emphasis_type(self, change_delta: int) -> EmphasisType:
        """
        Determine emphasis type based on change delta.

        Args:
            change_delta: Change value (negative=decrease, positive=increase, 0=no change)

        Returns:
            Appropriate EmphasisType
        """
        if change_delta < 0:
            return EmphasisType.DECREASED
        elif change_delta > 0:
            return EmphasisType.INCREASED
        else:
            return EmphasisType.DEFAULT

    def apply_color_formatting(self, text: str, emphasis: EmphasisType):
        """
        Render text with appropriate color and font formatting for pygame.

        Args:
            text: Text to render
            emphasis: Emphasis type for formatting

        Returns:
            pygame.Surface or mock surface for testing
        """
        if not PYGAME_AVAILABLE or self.normal_font is None:
            # Return mock surface for testing
            return PygameSurface(
                width=len(text) * 10,  # Approximate width
                height=24,
                content_hash=f"{text}_{emphasis.value}"
            )

        try:
            # Choose font based on emphasis
            if emphasis == EmphasisType.DEFAULT:
                font = self.normal_font
            else:
                font = self.bold_font if self.bold_font else self.normal_font

            # Choose color based on emphasis
            if emphasis == EmphasisType.DECREASED:
                color = self.color_config.decreased_color
            elif emphasis == EmphasisType.INCREASED:
                color = self.color_config.increased_color
            else:
                color = self.color_config.default_color

            # Render text
            antialias = True
            surface = font.render(text, antialias, color)
            return surface

        except Exception:
            # Fallback to mock surface if rendering fails
            return PygameSurface(
                width=len(text) * 10,
                height=24,
                content_hash=f"{text}_{emphasis.value}_fallback"
            )

    def reset_emphasis(self, entity_id: str) -> None:
        """
        Reset all emphasis states for given entity to default.

        Args:
            entity_id: Entity identifier
        """
        if entity_id in self.emphasis_state:
            # Reset all status keys for this entity to default
            for status_key in self.emphasis_state[entity_id]:
                self.emphasis_state[entity_id][status_key] = EmphasisType.DEFAULT