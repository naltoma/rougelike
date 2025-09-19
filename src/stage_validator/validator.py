"""Stage validation system using A* pathfinding"""
from typing import Optional, List, Dict, Any
import time
from pathlib import Path

from stage_generator.data_models import StageConfiguration
from stage_validator.pathfinding import StagePathfinder, ActionType
from stage_validator.validation_models import ValidationResult
from stage_validator.solution_generator import SolutionCodeGenerator
from stage_validator.patrol_validator import PatrolStageValidator, PatrolValidationResult


class StageValidator:
    """Main validator for stage solvability and quality"""

    def __init__(self, timeout_seconds: int = 60):
        self.timeout_seconds = timeout_seconds

    def validate_stage(self, stage: StageConfiguration, detailed: bool = False,
                      generate_solution: bool = False) -> ValidationResult:
        """
        Validate a stage for solvability and quality

        Args:
            stage: The stage configuration to validate
            detailed: Whether to include detailed analysis
            generate_solution: Whether to generate solution code

        Returns:
            ValidationResult with validation outcome
        """
        start_time = time.time()

        try:
            # Basic structural validation
            structure_issues = self._validate_structure(stage)
            if structure_issues:
                return ValidationResult(
                    success=False,
                    stage_path="",
                    path_found=False,
                    required_apis=[],
                    solution_length=0,
                    error_details=f"Structure validation failed: {'; '.join(structure_issues)}",
                    detailed_analysis=None
                )

            # Skip patrol-specific validation to force A* pathfinding for testing
            # if self._is_patrol_stage(stage):
            #     patrol_result = self._try_patrol_validation(stage, detailed, generate_solution, start_time)
            #     if patrol_result.success:
            #         return patrol_result

            # Standard A* pathfinding validation with enhanced limits
            pathfinder = StagePathfinder(stage)

            # Set max_nodes if specified via command line
            if hasattr(self, 'max_nodes'):
                pathfinder.max_nodes = self.max_nodes

            solution_path = pathfinder.find_path()  # No timeout parameter

            path_found = solution_path is not None
            solution_length = len(solution_path) if solution_path else 0

            # Analyze solution quality
            quality_analysis = self._analyze_solution_quality(stage, solution_path) if detailed else None

            # Generate solution code if requested
            solution_code = None
            if generate_solution and solution_path:
                solution_generator = SolutionCodeGenerator(stage, solution_path)
                solution_code = solution_generator.generate_multiple_styles()

            # Prepare detailed analysis
            detailed_analysis = None
            if detailed:
                detailed_analysis = {
                    "validation_method": "enhanced_a_star_pathfinding",
                    "stage_type": self._infer_stage_type(stage),
                    "board_size": stage.board.size,
                    "api_count": len(stage.constraints.allowed_apis),
                    "enemy_count": len(stage.enemies),
                    "item_count": len(stage.items),
                    "wall_density": self._calculate_wall_density(stage),
                    "validation_time": time.time() - start_time,
                    "solution_analysis": quality_analysis,
                    "solution_code": solution_code
                }

            return ValidationResult(
                success=path_found,
                stage_path="",
                path_found=path_found,
                required_apis=stage.constraints.allowed_apis,
                solution_length=solution_length,
                error_details=None if path_found else "No valid path found to goal",
                detailed_analysis=detailed_analysis,
                solution_code=solution_code
            )

        except Exception as e:
            return ValidationResult(
                success=False,
                stage_path="",
                path_found=False,
                required_apis=[],
                solution_length=0,
                error_details=f"Validation error: {str(e)}",
                detailed_analysis=None,
                solution_code=None
            )

    def _validate_structure(self, stage: StageConfiguration) -> List[str]:
        """Validate basic stage structure"""
        issues = []

        # Check board size
        width, height = stage.board.size
        if width < 3 or height < 3:
            issues.append("Board too small (minimum 3x3)")

        if width > 20 or height > 20:
            issues.append("Board too large (maximum 20x20)")

        # Check grid consistency
        if len(stage.board.grid) != height:
            issues.append("Grid height doesn't match board size")

        for i, row in enumerate(stage.board.grid):
            if len(row) != width:
                issues.append(f"Row {i} width doesn't match board size")

        # Check player start position
        px, py = stage.player.start
        if not (0 <= px < width and 0 <= py < height):
            issues.append("Player start position out of bounds")
        elif self._is_wall_at(stage, px, py):
            issues.append("Player starts in a wall")

        # Check goal position
        gx, gy = stage.goal.position
        if not (0 <= gx < width and 0 <= gy < height):
            issues.append("Goal position out of bounds")
        elif self._is_wall_at(stage, gx, gy):
            issues.append("Goal is in a wall")

        # Check enemy positions
        for i, enemy in enumerate(stage.enemies):
            ex, ey = enemy.position
            if not (0 <= ex < width and 0 <= ey < height):
                issues.append(f"Enemy {i} position out of bounds")
            elif self._is_wall_at(stage, ex, ey):
                issues.append(f"Enemy {i} is in a wall")

        # Check item positions
        for i, item in enumerate(stage.items):
            ix, iy = item.position
            if not (0 <= ix < width and 0 <= iy < height):
                issues.append(f"Item {i} position out of bounds")
            elif self._is_wall_at(stage, ix, iy):
                issues.append(f"Item {i} is in a wall")

        # Check API constraints
        if not stage.constraints.allowed_apis:
            issues.append("No APIs allowed")

        required_apis = {"turn_left", "turn_right", "move", "see"}
        if not required_apis.issubset(set(stage.constraints.allowed_apis)):
            missing = required_apis - set(stage.constraints.allowed_apis)
            issues.append(f"Missing required APIs: {', '.join(missing)}")

        # Check turn limit
        if stage.constraints.max_turns < 10:
            issues.append("Max turns too low (minimum 10)")

        return issues

    def _is_wall_at(self, stage: StageConfiguration, x: int, y: int) -> bool:
        """Check if there's a wall at the given position"""
        if 0 <= y < len(stage.board.grid) and 0 <= x < len(stage.board.grid[y]):
            return stage.board.grid[y][x] == '#'
        return True  # Out of bounds treated as wall

    def _infer_stage_type(self, stage: StageConfiguration) -> str:
        """Infer the stage type based on its characteristics"""
        has_enemies = len(stage.enemies) > 0
        has_items = len(stage.items) > 0
        has_attack = "attack" in stage.constraints.allowed_apis
        has_pickup = "pickup" in stage.constraints.allowed_apis
        has_wait = "wait" in stage.constraints.allowed_apis

        if not has_enemies and not has_items:
            return "move"
        elif has_enemies and has_attack and not has_items:
            return "attack"
        elif has_items and has_pickup and not has_enemies:
            return "pickup"
        elif has_enemies and has_wait:
            return "patrol"
        elif has_enemies and has_items and has_attack and has_pickup:
            return "special"
        else:
            return "unknown"

    def _calculate_wall_density(self, stage: StageConfiguration) -> float:
        """Calculate the wall density of the stage"""
        total_cells = stage.board.size[0] * stage.board.size[1]
        wall_count = 0

        for row in stage.board.grid:
            wall_count += row.count('#')

        return wall_count / total_cells if total_cells > 0 else 0.0

    def _analyze_solution_quality(self, stage: StageConfiguration,
                                solution_path: Optional[List[ActionType]]) -> Dict[str, Any]:
        """Analyze the quality of the solution path"""
        if not solution_path:
            return {
                "solvable": False,
                "efficiency": 0.0,
                "complexity": 0.0
            }

        # Calculate theoretical minimum steps (Manhattan distance)
        px, py = stage.player.start
        gx, gy = stage.goal.position
        manhattan_distance = abs(gx - px) + abs(gy - py)

        # Add minimum steps for item collection
        item_steps = len(stage.items) * 2  # Rough estimate

        theoretical_minimum = manhattan_distance + item_steps

        # Calculate efficiency (lower is better)
        efficiency = len(solution_path) / max(theoretical_minimum, 1)

        # Calculate complexity based on action variety
        action_types = set(solution_path)
        complexity = len(action_types) / len(ActionType)

        # Count specific action types
        action_counts = {}
        for action in ActionType:
            action_counts[action.value] = solution_path.count(action)

        return {
            "solvable": True,
            "solution_length": len(solution_path),
            "theoretical_minimum": theoretical_minimum,
            "efficiency_ratio": efficiency,
            "complexity_score": complexity,
            "action_distribution": action_counts,
            "path_quality": "excellent" if efficiency < 1.5 else
                           "good" if efficiency < 2.0 else
                           "acceptable" if efficiency < 3.0 else "poor"
        }

    def _is_patrol_stage(self, stage: StageConfiguration) -> bool:
        """Check if this is a patrol stage"""
        # Check if any enemy has patrol behavior with valid patrol_path and wait API is available
        has_valid_patrol_enemy = any(
            enemy.behavior == "patrol" and enemy.patrol_path
            for enemy in stage.enemies
        )
        has_wait_api = "wait" in stage.constraints.allowed_apis
        has_attack_api = "attack" in stage.constraints.allowed_apis

        return has_valid_patrol_enemy and has_wait_api and has_attack_api

    def _try_patrol_validation(self, stage: StageConfiguration, detailed: bool,
                             generate_solution: bool, start_time: float) -> ValidationResult:
        """Try patrol-specific validation"""
        patrol_validator = PatrolStageValidator()
        patrol_result = patrol_validator.validate(stage)

        if patrol_result.success:
            # Convert PatrolValidationResult to ValidationResult
            solution_code = None
            if generate_solution:
                solution_code = self._generate_patrol_solution_code(patrol_result)

            detailed_analysis = None
            if detailed:
                detailed_analysis = {
                    "validation_method": "patrol_pattern_based",
                    "stage_type": "patrol",
                    "strategy_used": patrol_result.strategy_used.value if patrol_result.strategy_used else None,
                    "board_size": stage.board.size,
                    "api_count": len(stage.constraints.allowed_apis),
                    "enemy_count": len(stage.enemies),
                    "item_count": len(stage.items),
                    "wall_density": self._calculate_wall_density(stage),
                    "validation_time": time.time() - start_time,
                    "solution_code": solution_code
                }

            return ValidationResult(
                success=True,
                stage_path="",
                path_found=True,
                required_apis=stage.constraints.allowed_apis,
                solution_length=patrol_result.total_turns,
                error_details=None,
                detailed_analysis=detailed_analysis,
                solution_code=solution_code
            )

        return ValidationResult(
            success=False,
            stage_path="",
            path_found=False,
            required_apis=stage.constraints.allowed_apis,
            solution_length=0,
            error_details=patrol_result.error_message,
            detailed_analysis=None,
            solution_code=None
        )

    def _generate_patrol_solution_code(self, patrol_result: PatrolValidationResult) -> Dict[str, str]:
        """Generate solution code from patrol validation result"""
        actions = patrol_result.solution_actions

        # Generate optimized solution
        optimized_code = self._actions_to_code(actions, "optimized")

        # Generate educational solution with comments
        educational_code = self._actions_to_code(actions, "educational")

        # Generate simple solution
        simple_code = self._actions_to_code(actions, "simple")

        return {
            "optimized": optimized_code,
            "educational": educational_code,
            "simple": simple_code
        }

    def _actions_to_code(self, actions: List[ActionType], style: str) -> str:
        """Convert action list to Python code"""
        if not actions:
            return "def solve():\n    pass  # No solution found"

        lines = ["def solve():"]

        if style == "educational":
            lines.append("    # Patrol stage solution using tactical combat strategy")

        # Group consecutive actions
        grouped_actions = []
        current_action = actions[0]
        count = 1

        for action in actions[1:]:
            if action == current_action:
                count += 1
            else:
                grouped_actions.append((current_action, count))
                current_action = action
                count = 1
        grouped_actions.append((current_action, count))

        # Generate code
        for action, count in grouped_actions:
            if count == 1:
                if style == "educational" and action == ActionType.WAIT:
                    lines.append(f"    {action.value}()  # Wait for enemy timing")
                elif style == "educational" and action == ActionType.ATTACK:
                    lines.append(f"    {action.value}()  # Attack enemy")
                else:
                    lines.append(f"    {action.value}()")
            else:
                if style == "educational" and action == ActionType.MOVE:
                    lines.append(f"    for i in range({count}): {action.value}()  # Navigate to position")
                elif style == "educational" and action == ActionType.WAIT:
                    lines.append(f"    for i in range({count}): {action.value}()  # Strategic waiting")
                else:
                    lines.append(f"    for i in range({count}): {action.value}()")

        return "\n".join(lines)