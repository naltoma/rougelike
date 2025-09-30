"""Solution code generator for validated stages"""
from typing import List, Optional, Dict, Any
from collections import Counter

from stage_validator.pathfinding import ActionType
from stage_generator.data_models import StageConfiguration


class SolutionCodeGenerator:
    """Generate Python solve() function code from pathfinding solution"""

    def __init__(self, stage: StageConfiguration, solution_path: List[ActionType]):
        self.stage = stage
        self.solution_path = solution_path

    def generate_solve_function(self, style: str = "optimized") -> str:
        """
        Generate solve() function code

        Args:
            style: Code generation style
                - "simple": Simple step-by-step code
                - "optimized": Optimized with loops and comments
                - "educational": Educational with detailed comments

        Returns:
            String containing complete solve() function
        """
        if not self.solution_path:
            return self._generate_unsolvable_function()

        if style == "simple":
            return self._generate_simple_solution()
        elif style == "optimized":
            return self._generate_optimized_solution()
        elif style == "educational":
            return self._generate_educational_solution()
        else:
            return self._generate_optimized_solution()

    def _generate_simple_solution(self) -> str:
        """Generate simple step-by-step solution"""
        lines = [
            "def solve():",
            "    \"\"\"",
            "    Auto-generated solution for stage validation",
            "    Smart item handling with is_available() logic",
            "    \"\"\"",
        ]

        # Generate smart solution with conditional logic
        optimized_lines = self._generate_smart_solution_lines()
        lines.extend(optimized_lines)

        return "\n".join(lines)

    def _generate_optimized_solution(self) -> str:
        """Generate optimized solution with loops"""
        lines = [
            "def solve():",
            "    \"\"\"",
            "    Auto-generated optimized solution",
            f"    Total steps: {len(self.solution_path)}",
            "    \"\"\"",
        ]

        # Analyze action patterns for optimization
        optimized_actions = self._optimize_action_sequence(self.solution_path)

        for action_group in optimized_actions:
            if action_group["count"] == 1:
                api_call = self._action_to_api_call(action_group["action"])
                lines.append(f"    {api_call}")
            else:
                api_call = self._action_to_api_call(action_group["action"])
                lines.append(f"    for _ in range({action_group['count']}):")
                lines.append(f"        {api_call}")

        return "\n".join(lines)

    def _generate_educational_solution(self) -> str:
        """Generate educational solution with detailed comments"""
        lines = [
            "def solve():",
            "    \"\"\"",
            "    Educational solution with detailed explanations",
            f"    Stage: {self.stage.id}",
            f"    Total actions: {len(self.solution_path)}",
            "    \"\"\"",
        ]

        # Add stage analysis
        lines.extend(self._generate_stage_analysis())

        # Add solution steps with explanations
        optimized_actions = self._optimize_action_sequence(self.solution_path)
        step_number = 1

        for action_group in optimized_actions:
            explanation = self._get_action_explanation(action_group["action"])

            if action_group["count"] == 1:
                api_call = self._action_to_api_call(action_group["action"])
                lines.append(f"    # Step {step_number}: {explanation}")
                lines.append(f"    {api_call}")
                step_number += 1
            else:
                api_call = self._action_to_api_call(action_group["action"])
                lines.append(f"    # Steps {step_number}-{step_number + action_group['count'] - 1}: {explanation} (repeated {action_group['count']} times)")
                lines.append(f"    for _ in range({action_group['count']}):")
                lines.append(f"        {api_call}")
                step_number += action_group["count"]

        return "\n".join(lines)

    def _generate_unsolvable_function(self) -> str:
        """Generate function for unsolvable stages"""
        return '''def solve():
    """
    This stage appears to be unsolvable with the given constraints.
    Consider checking:
    - Stage configuration
    - Available APIs
    - Turn limits
    """
    # No solution found
    pass'''

    def _optimize_action_sequence(self, actions: List[ActionType]) -> List[Dict[str, Any]]:
        """Optimize action sequence by grouping consecutive identical actions"""
        if not actions:
            return []

        optimized = []
        current_action = actions[0]
        current_count = 1

        for action in actions[1:]:
            if action == current_action:
                current_count += 1
            else:
                optimized.append({
                    "action": current_action,
                    "count": current_count
                })
                current_action = action
                current_count = 1

        # Add the last group
        optimized.append({
            "action": current_action,
            "count": current_count
        })

        return optimized

    def _action_to_api_call(self, action: ActionType) -> str:
        """Convert ActionType to API function call"""
        api_mapping = {
            ActionType.MOVE: "move()",
            ActionType.TURN_LEFT: "turn_left()",
            ActionType.TURN_RIGHT: "turn_right()",
            ActionType.ATTACK: "attack()",
            ActionType.PICKUP: "pickup()",
            ActionType.WAIT: "wait()",
            ActionType.IS_AVAILABLE: "is_available()",  # v1.2.12
            ActionType.DISPOSE: "dispose()"  # v1.2.12
        }
        return api_mapping.get(action, f"# Unknown action: {action}")

    def _get_action_explanation(self, action: ActionType) -> str:
        """Get human-readable explanation for action"""
        explanations = {
            ActionType.MOVE: "Move forward one cell",
            ActionType.TURN_LEFT: "Turn 90 degrees counterclockwise",
            ActionType.TURN_RIGHT: "Turn 90 degrees clockwise",
            ActionType.ATTACK: "Attack enemy in front",
            ActionType.PICKUP: "Pick up item at current position",
            ActionType.WAIT: "Wait for one turn",
            ActionType.IS_AVAILABLE: "Check if item available without consuming turn",  # v1.2.12
            ActionType.DISPOSE: "Dispose item at current position"  # v1.2.12
        }
        return explanations.get(action, f"Perform {action.value}")

    def _generate_stage_analysis(self) -> List[str]:
        """Generate stage analysis comments"""
        lines = [
            "",
            "    # Stage Analysis:",
            f"    # Board size: {self.stage.board.size[0]}x{self.stage.board.size[1]}",
            f"    # Enemies: {len(self.stage.enemies)}",
            f"    # Items: {len(self.stage.items)}",
            f"    # Available APIs: {', '.join(self.stage.constraints.allowed_apis)}",
            ""
        ]

        # Add action distribution analysis
        action_counts = Counter(self.solution_path)
        lines.append("    # Solution breakdown:")
        for action, count in action_counts.most_common():
            lines.append(f"    # - {action.value}: {count} times")
        lines.append("")

        return lines

    def generate_multiple_styles(self) -> Dict[str, str]:
        """Generate solutions in multiple styles"""
        return {
            "simple": self.generate_solve_function("simple"),
            "optimized": self.generate_solve_function("optimized"),
            "educational": self.generate_solve_function("educational")
        }

    def get_solution_stats(self) -> Dict[str, Any]:
        """Get statistics about the solution"""
        if not self.solution_path:
            return {"solvable": False}

        action_counts = Counter(self.solution_path)
        return {
            "solvable": True,
            "total_steps": len(self.solution_path),
            "action_breakdown": dict(action_counts),
            "unique_actions": len(action_counts),
            "efficiency_score": self._calculate_efficiency_score()
        }

    def _calculate_efficiency_score(self) -> float:
        """Calculate efficiency score (lower is better)"""
        # Simple efficiency: solution length vs Manhattan distance
        start = self.stage.player.start
        goal = self.stage.goal.position
        manhattan_dist = abs(goal[0] - start[0]) + abs(goal[1] - start[1])

        if manhattan_dist == 0:
            return 1.0

        return len(self.solution_path) / manhattan_dist

    def _generate_smart_solution_lines(self) -> List[str]:
        """Generate solution lines with smart item handling logic (API constraint aware)"""
        lines = []

        # Check available APIs for conditional logic
        allowed_apis = self.stage.constraints.allowed_apis
        has_is_available = "is_available" in allowed_apis
        has_dispose = "dispose" in allowed_apis

        # Track if we need item handling logic
        solution_has_dispose = ActionType.DISPOSE in self.solution_path
        solution_has_pickup = ActionType.PICKUP in self.solution_path

        if solution_has_dispose and solution_has_pickup and has_is_available and has_dispose:
            # Generate conditional item handling only if APIs are available
            lines.extend(self._generate_conditional_item_handling())
        else:
            # Generate simple step-by-step solution respecting API constraints
            for i, action in enumerate(self.solution_path, 1):
                if action == ActionType.DISPOSE and has_dispose:
                    if has_is_available:
                        lines.append("    # Smart item disposal")
                        lines.append("    if is_available():")
                        lines.append("        pickup()   # Beneficial item")
                        lines.append("    else:")
                        lines.append("        dispose()  # Dangerous bomb")
                    else:
                        lines.append(f"    dispose()  # Step {i}")
                elif action == ActionType.PICKUP:
                    if has_is_available and has_dispose:
                        lines.append("    # Smart item pickup")
                        lines.append("    if is_available():")
                        lines.append("        pickup()   # Beneficial item")
                        lines.append("    else:")
                        lines.append("        dispose()  # Dangerous bomb")
                    else:
                        lines.append(f"    pickup()  # Step {i}")
                else:
                    api_call = self._action_to_api_call(action)
                    lines.append(f"    {api_call}  # Step {i}")

        return lines

    def _generate_conditional_item_handling(self) -> List[str]:
        """Generate solution with conditional item handling logic (API constraint aware)"""
        lines = []
        step_num = 1

        # Check available APIs
        allowed_apis = self.stage.constraints.allowed_apis
        has_is_available = "is_available" in allowed_apis
        has_dispose = "dispose" in allowed_apis

        for action in self.solution_path:
            if action in [ActionType.DISPOSE, ActionType.PICKUP]:
                if has_is_available and has_dispose:
                    lines.append(f"    # Step {step_num}: Smart item handling with is_available()")
                    lines.append("    if is_available():")
                    lines.append("        pickup()   # Beneficial item - safe to collect")
                    lines.append("    else:")
                    lines.append("        dispose()  # Dangerous item (bomb) - dispose safely")
                else:
                    # Fall back to simple API call if advanced APIs not available
                    api_call = self._action_to_api_call(action)
                    lines.append(f"    {api_call}  # Step {step_num}")
            else:
                api_call = self._action_to_api_call(action)
                lines.append(f"    {api_call}  # Step {step_num}")
            step_num += 1

        return lines