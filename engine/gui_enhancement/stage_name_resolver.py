"""
StageNameResolver implementation for dynamically reading STAGE_ID from main_*.py files.
Provides accurate stage name display by parsing Python module variables.
"""

import importlib.util
import re
from pathlib import Path
from typing import Dict
from .data_types import StageResolution, ValidationResult


class StageNameResolver:
    """Dynamically reads STAGE_ID variable from main_*.py files for accurate stage name display."""

    def __init__(self):
        """Initialize the stage name resolver."""
        self.cache: Dict[str, StageResolution] = {}

    def resolve_stage_name(self, file_path: str) -> StageResolution:
        """
        Extract STAGE_ID from file and return resolution info.

        Args:
            file_path: Path to main_*.py file containing STAGE_ID

        Returns:
            StageResolution with stage information
        """
        # Check cache first
        if file_path in self.cache:
            cached_result = self.cache[file_path]
            # Return cached result with is_cached=True
            return StageResolution(
                stage_id=cached_result.stage_id,
                file_path=cached_result.file_path,
                resolved_name=cached_result.resolved_name,
                is_cached=True
            )

        stage_id = "unknown"

        try:
            # Validate file exists
            if not Path(file_path).exists():
                stage_id = "unknown"
            else:
                # Load module dynamically
                spec = importlib.util.spec_from_file_location("temp_module", file_path)
                if spec is not None and spec.loader is not None:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # Extract STAGE_ID
                    if hasattr(module, 'STAGE_ID'):
                        stage_id_value = getattr(module, 'STAGE_ID')
                        # Only accept string values
                        if isinstance(stage_id_value, str):
                            stage_id = stage_id_value
                        else:
                            stage_id = "unknown"
                    else:
                        stage_id = "unknown"
                else:
                    stage_id = "unknown"

        except Exception:
            # Any error results in unknown stage
            stage_id = "unknown"

        # Create display name
        resolved_name = self._format_stage_name(stage_id)

        # Create resolution result
        resolution = StageResolution(
            stage_id=stage_id,
            file_path=file_path,
            resolved_name=resolved_name,
            is_cached=False
        )

        # Cache the result
        self.cache[file_path] = resolution

        return resolution

    def validate_stage_id(self, stage_id: str) -> ValidationResult:
        """
        Validate stage_id format (stage + 2 digits).

        Args:
            stage_id: Stage identifier to validate

        Returns:
            ValidationResult with validation info
        """
        if not isinstance(stage_id, str):
            return ValidationResult(
                is_valid=False,
                stage_id=str(stage_id),
                error_message="stage_id must be a string"
            )

        if stage_id == "":
            return ValidationResult(
                is_valid=False,
                stage_id=stage_id,
                error_message="Stage ID cannot be empty"
            )

        # Pattern: "stage" + exactly 2 digits
        pattern = r'^stage(\d{2})$'
        match = re.match(pattern, stage_id)

        if not match:
            return ValidationResult(
                is_valid=False,
                stage_id=stage_id,
                error_message="Stage ID must be in format 'stageXX' where XX is a two-digit number (01-99)"
            )

        # Check if stage number is in valid range (01-99)
        stage_number = int(match.group(1))
        if stage_number == 0:
            return ValidationResult(
                is_valid=False,
                stage_id=stage_id,
                error_message="Stage number must be between 01 and 99"
            )

        return ValidationResult(
            is_valid=True,
            stage_id=stage_id,
            error_message=None
        )

    def get_display_name(self, stage_id: str) -> str:
        """
        Convert stage_id to human-readable display name.

        Args:
            stage_id: Stage identifier

        Returns:
            Formatted display name
        """
        return f"Stage: {stage_id}"

    def _format_stage_name(self, stage_id: str) -> str:
        """
        Format stage name for display (used by tests).

        Args:
            stage_id: Stage identifier

        Returns:
            Formatted display name
        """
        if stage_id == "unknown" or not isinstance(stage_id, str):
            return "Unknown Stage"

        # Try to format as "Stage XX" for valid stage IDs
        pattern = r'^stage(\d{2})$'
        match = re.match(pattern, stage_id)
        if match:
            stage_number = match.group(1)
            return f"Stage {stage_number}"
        else:
            return "Unknown Stage"

    def clear_cache(self) -> None:
        """Clear all cached stage resolutions."""
        self.cache.clear()