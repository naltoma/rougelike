"""Data models for stage validation system"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Tuple, Set, Any


@dataclass
class ValidationResult:
    """Result of stage validation with detailed analysis"""
    success: bool
    stage_path: str
    path_found: bool
    required_apis: List[str]
    solution_length: Optional[int] = None
    error_details: Optional[str] = None
    detailed_analysis: Optional[Dict[str, Any]] = None
    solution_code: Optional[Dict[str, str]] = None

    def to_report(self) -> str:
        """Generate human-readable validation report"""
        if self.success:
            return f"✅ Stage {self.stage_path} is solvable in {self.solution_length} steps"
        else:
            return f"❌ Stage {self.stage_path} validation failed: {self.error_details}"


@dataclass
class SolutionPath:
    """Detailed solution path for a stage"""
    actions: List[str]      # Sequence of API calls
    positions: List[Tuple[int, int]]  # Player positions
    total_steps: int
    apis_used: Set[str]     # APIs required for solution


# Custom exceptions for validation errors
class FileNotFoundError(Exception):
    """Raised when stage file doesn't exist"""
    pass


class YAMLParseError(Exception):
    """Raised when YAML structure is invalid"""
    pass


class SchemaValidationError(Exception):
    """Raised when stage data doesn't match expected schema"""
    pass


class PathfindingTimeoutError(Exception):
    """Raised when validation takes too long"""
    pass


class UnsolvableStageError(Exception):
    """Raised when no valid solution path exists"""
    pass