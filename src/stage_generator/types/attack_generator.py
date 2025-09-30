"""Attack stage generator for combat scenarios"""
import random
from typing import List, Tuple, Set
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from stage_generator.data_models import (
    StageConfiguration, BoardConfiguration, PlayerConfiguration,
    GoalConfiguration, EnemyConfiguration, ConstraintConfiguration,
    ALL_AVAILABLE_APIS
)


class AttackStageGenerator:
    """Generator for attack-type stages (combat scenarios)"""

    def __init__(self, seed: int):
        self.random = random.Random(seed)
        self.seed = seed

    def generate(self) -> StageConfiguration:
        """Generate an attack stage with combat challenges"""
        # Board size: 6x6 to 10x10 (per design specification)
        width = self.random.randint(6, 10)
        height = self.random.randint(6, 10)

        # Generate board with fewer walls (for tactical positioning)
        board = self._generate_board(width, height)

        # Place player and goal
        player_start, goal_position = self._place_player_and_goal(width, height, board['walls'])

        # Generate enemies (1-3 static enemies)
        enemies = self._generate_enemies(width, height, board['walls'], player_start, goal_position)

        # Create stage configuration
        stage_config = StageConfiguration(
            id=f"generated_attack_{self.seed}",
            title="Generated Attack Stage",
            description="Randomly generated stage focusing on combat and tactical positioning.",
            board=BoardConfiguration(
                size=(width, height),
                grid=board['grid'],
                legend={
                    ".": "empty",
                    "#": "wall",
                    "P": "player",
                    "G": "goal",
                    "E": "enemy"
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
            enemies=enemies,
            items=[],  # Attack stages focus on combat, no items
            constraints=ConstraintConfiguration(
                max_turns=self._calculate_max_turns(width, height, len(enemies)),
                allowed_apis=ALL_AVAILABLE_APIS
            ),
            victory_conditions=self._generate_victory_conditions(enemies)
        )

        return stage_config

    def _generate_board(self, width: int, height: int) -> dict:
        """Generate board with tactical wall placement"""
        # Lower wall density: 5-20% (for tactical movement)
        total_cells = width * height
        target_wall_density = self.random.uniform(0.05, 0.20)
        target_wall_count = int(total_cells * target_wall_density)

        # Initialize empty board
        grid = [['.' for _ in range(width)] for _ in range(height)]
        walls = set()

        # Place walls in tactical patterns
        self._place_tactical_walls(width, height, grid, walls, target_wall_count)

        # Convert grid to string list
        grid_strings = [''.join(row) for row in grid]

        return {
            'grid': grid_strings,
            'walls': walls
        }

    def _place_tactical_walls(self, width: int, height: int, grid: List[List[str]],
                            walls: Set[Tuple[int, int]], target_count: int):
        """Place walls in tactical patterns for combat scenarios"""
        placed_walls = 0

        # Pattern 1: Create some cover positions (small clusters)
        cluster_count = self.random.randint(1, 3)
        for _ in range(cluster_count):
            if placed_walls >= target_count:
                break

            # Choose cluster center
            center_x = self.random.randint(2, width - 3)
            center_y = self.random.randint(2, height - 3)

            # Place 2x2 or L-shaped cluster
            cluster_pattern = self.random.choice(['2x2', 'L_shape', 'line'])

            if cluster_pattern == '2x2':
                positions = [(center_x, center_y), (center_x+1, center_y),
                           (center_x, center_y+1), (center_x+1, center_y+1)]
            elif cluster_pattern == 'L_shape':
                positions = [(center_x, center_y), (center_x+1, center_y), (center_x, center_y+1)]
            else:  # line
                if self.random.choice([True, False]):  # horizontal
                    positions = [(center_x-1, center_y), (center_x, center_y), (center_x+1, center_y)]
                else:  # vertical
                    positions = [(center_x, center_y-1), (center_x, center_y), (center_x, center_y+1)]

            for x, y in positions:
                if (0 <= x < width and 0 <= y < height and
                    (x, y) not in walls and placed_walls < target_count):
                    walls.add((x, y))
                    grid[y][x] = '#'
                    placed_walls += 1

        # Pattern 2: Random scattered walls for remaining count
        attempts = 0
        while placed_walls < target_count and attempts < target_count * 2:
            x = self.random.randint(0, width - 1)
            y = self.random.randint(0, height - 1)

            if (x, y) not in walls:
                walls.add((x, y))
                grid[y][x] = '#'
                placed_walls += 1

            attempts += 1

    def _place_player_and_goal(self, width: int, height: int, walls: Set[Tuple[int, int]]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Place player and goal in tactically interesting positions"""
        available_positions = [(x, y) for x in range(width) for y in range(height)
                              if (x, y) not in walls]

        if len(available_positions) < 2:
            return (0, 0), (width-1, height-1)

        # Player start: prefer corners or edges for tactical advantage
        edge_positions = []
        corner_positions = []

        for x, y in available_positions:
            if (x == 0 or x == width-1) and (y == 0 or y == height-1):
                corner_positions.append((x, y))
            elif x == 0 or x == width-1 or y == 0 or y == height-1:
                edge_positions.append((x, y))

        if corner_positions:
            player_start = self.random.choice(corner_positions)
        elif edge_positions:
            player_start = self.random.choice(edge_positions)
        else:
            player_start = self.random.choice(available_positions)

        # Goal: place at reasonable distance, but not necessarily maximum
        remaining_positions = [pos for pos in available_positions if pos != player_start]
        if not remaining_positions:
            return player_start, (min(width-1, player_start[0]+1), min(height-1, player_start[1]+1))

        # Filter positions by distance (minimum distance of 3 Manhattan units)
        valid_goals = []
        for pos in remaining_positions:
            dist = abs(pos[0] - player_start[0]) + abs(pos[1] - player_start[1])
            if dist >= 3:
                valid_goals.append(pos)

        if valid_goals:
            goal_position = self.random.choice(valid_goals)
        else:
            # Fallback to any remaining position
            goal_position = self.random.choice(remaining_positions)

        return player_start, goal_position

    def _generate_enemies(self, width: int, height: int, walls: Set[Tuple[int, int]],
                         player_start: Tuple[int, int], goal_position: Tuple[int, int]) -> List[EnemyConfiguration]:
        """Generate 1-3 static enemies with varying HP"""
        available_positions = []
        for x in range(width):
            for y in range(height):
                if ((x, y) not in walls and
                    (x, y) != player_start and
                    (x, y) != goal_position):
                    available_positions.append((x, y))

        if not available_positions:
            return []

        # Enemy count: 1 only (attack stage should focus on single combat)
        enemy_count = 1
        selected_positions = self.random.sample(available_positions, enemy_count)

        enemies = []
        hp_ranges = [(10, 30), (40, 90), (100, 300)]  # Easy, medium, hard

        for i, position in enumerate(selected_positions):
            # Vary enemy difficulty
            hp_range = hp_ranges[i % len(hp_ranges)]
            enemy_hp = self.random.randint(hp_range[0], hp_range[1])

            enemy = EnemyConfiguration(
                id=f"guard_{i+1}",
                type="normal",
                position=position,
                direction=self._random_direction(),
                hp=enemy_hp,
                max_hp=enemy_hp,
                attack_power=self.random.randint(20, 40),
                behavior="static"
            )
            # 統一された視野設定
            enemy.vision_range = 2
            enemies.append(enemy)

        return enemies

    def _generate_victory_conditions(self, enemies: List[EnemyConfiguration]) -> List[dict]:
        """Generate victory conditions based on stage content"""
        conditions = []

        # Add defeat_all_enemies if enemies are present
        if enemies:
            conditions.append({"type": "defeat_all_enemies"})

        # Always include reach_goal
        conditions.append({"type": "reach_goal"})

        return conditions

    def _random_direction(self) -> str:
        """Generate random direction"""
        directions = ["N", "S", "E", "W"]
        return self.random.choice(directions)

    def _calculate_max_turns(self, width: int, height: int, enemy_count: int) -> int:
        """Calculate max turns based on board size and enemy count"""
        # Base movement turns
        base_turns = (width + height) * 2

        # Add turns for combat (estimated 3-10 turns per enemy)
        combat_turns = enemy_count * self.random.randint(3, 10)

        # Add tactical maneuvering buffer
        total_turns = int((base_turns + combat_turns) * 1.5)

        return max(30, min(300, total_turns))