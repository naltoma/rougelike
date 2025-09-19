"""Move stage generator for basic navigation stages"""
import random
from typing import List, Tuple, Set
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from stage_generator.data_models import (
    StageConfiguration, BoardConfiguration, PlayerConfiguration,
    GoalConfiguration, ConstraintConfiguration
)


class MoveStageGenerator:
    """Generator for move-type stages (basic navigation)"""

    def __init__(self, seed: int):
        self.random = random.Random(seed)
        self.seed = seed

    def generate(self) -> StageConfiguration:
        """Generate a move stage with basic navigation challenges"""
        # Board size: 5x5 to 8x8 (per design specification)
        width = self.random.randint(5, 8)
        height = self.random.randint(5, 8)

        # Generate board with walls
        board = self._generate_board(width, height)

        # Place player and goal
        player_start, goal_position = self._place_player_and_goal(width, height, board['walls'])

        # Create stage configuration
        stage_config = StageConfiguration(
            id=f"generated_move_{self.seed}",
            title="Generated Movement Stage",
            description="Randomly generated stage focusing on basic movement and navigation skills.",
            board=BoardConfiguration(
                size=(width, height),
                grid=board['grid'],
                legend={
                    ".": "empty",
                    "#": "wall",
                    "P": "player",
                    "G": "goal"
                }
            ),
            player=PlayerConfiguration(
                start=player_start,
                direction=self._random_direction(),
                hp=100,
                max_hp=100,
                attack_power=30
            ),
            goal=GoalConfiguration(
                position=goal_position
            ),
            enemies=[],  # Move stages have no enemies
            items=[],    # Move stages have no items
            constraints=ConstraintConfiguration(
                max_turns=self._calculate_max_turns(width, height),
                allowed_apis=["turn_left", "turn_right", "move", "see"]
            ),
            victory_conditions=[{"type": "reach_goal"}]
        )

        return stage_config

    def _generate_board(self, width: int, height: int) -> dict:
        """Generate board with walls and empty spaces"""
        # Wall density: 10-25% (per design specification)
        total_cells = width * height
        target_wall_density = self.random.uniform(0.10, 0.25)
        target_wall_count = int(total_cells * target_wall_density)

        # Initialize empty board
        grid = [['.' for _ in range(width)] for _ in range(height)]
        walls = set()

        # Place walls randomly, but ensure connectivity
        attempts = 0
        while len(walls) < target_wall_count and attempts < target_wall_count * 3:
            x = self.random.randint(0, width - 1)
            y = self.random.randint(0, height - 1)

            if (x, y) not in walls:
                # Temporarily place wall and check connectivity
                walls.add((x, y))
                if self._check_basic_connectivity(width, height, walls):
                    grid[y][x] = '#'
                else:
                    walls.remove((x, y))

            attempts += 1

        # Convert grid to string list
        grid_strings = [''.join(row) for row in grid]

        return {
            'grid': grid_strings,
            'walls': walls
        }

    def _check_basic_connectivity(self, width: int, height: int, walls: Set[Tuple[int, int]]) -> bool:
        """Basic connectivity check - ensure corners can still be connected"""
        # Simple check: ensure there's at least one path from corners
        # More sophisticated pathfinding will be done during validation

        corner_positions = [(0, 0), (width-1, height-1), (0, height-1), (width-1, 0)]
        accessible_corners = 0

        for corner in corner_positions:
            if corner not in walls:
                # Check if corner has at least one accessible neighbor
                x, y = corner
                neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                has_accessible_neighbor = False

                for nx, ny in neighbors:
                    if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                        has_accessible_neighbor = True
                        break

                if has_accessible_neighbor:
                    accessible_corners += 1

        # Need at least 2 accessible corners to ensure some connectivity
        return accessible_corners >= 2

    def _place_player_and_goal(self, width: int, height: int, walls: Set[Tuple[int, int]]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Place player and goal in valid positions"""
        available_positions = []

        # Find all available positions (not walls)
        for x in range(width):
            for y in range(height):
                if (x, y) not in walls:
                    available_positions.append((x, y))

        if len(available_positions) < 2:
            # Fallback: use corners if insufficient space
            available_positions = [(0, 0), (width-1, height-1)]

        # Select player start (prefer corner or edge)
        preferred_starts = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        valid_starts = [pos for pos in preferred_starts if pos in available_positions]

        if valid_starts:
            player_start = self.random.choice(valid_starts)
        else:
            player_start = self.random.choice(available_positions)

        # Select goal position (maximize distance from player)
        remaining_positions = [pos for pos in available_positions if pos != player_start]
        if not remaining_positions:
            # Fallback if only one position available
            goal_position = (min(width-1, player_start[0]+1), min(height-1, player_start[1]+1))
        else:
            # Choose position with maximum Manhattan distance
            distances = []
            for pos in remaining_positions:
                dist = abs(pos[0] - player_start[0]) + abs(pos[1] - player_start[1])
                distances.append((dist, pos))

            distances.sort(reverse=True)
            # Select from top 25% of distances to add some variety
            top_25_percent = max(1, len(distances) // 4)
            goal_position = self.random.choice(distances[:top_25_percent])[1]

        return player_start, goal_position

    def _random_direction(self) -> str:
        """Generate random starting direction"""
        directions = ["N", "S", "E", "W"]
        return self.random.choice(directions)

    def _calculate_max_turns(self, width: int, height: int) -> int:
        """Calculate reasonable max turns based on board size"""
        # Base turns: board perimeter + some buffer
        base_turns = (width + height) * 2

        # Add buffer for navigation challenges (25-50% extra)
        buffer_multiplier = self.random.uniform(1.25, 1.5)
        max_turns = int(base_turns * buffer_multiplier)

        return max(20, min(200, max_turns))  # Reasonable bounds