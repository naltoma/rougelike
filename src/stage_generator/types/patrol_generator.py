"""Patrol stage generator for stealth and timing scenarios"""
import random
from typing import List, Tuple, Set
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from stage_generator.data_models import (
    StageConfiguration, BoardConfiguration, PlayerConfiguration,
    GoalConfiguration, EnemyConfiguration, ConstraintConfiguration
)


class PatrolStageGenerator:
    """Generator for patrol-type stages (stealth and timing scenarios)"""

    def __init__(self, seed: int):
        self.random = random.Random(seed)
        self.seed = seed

    def generate(self) -> StageConfiguration:
        """Generate a patrol stage with moving enemies and stealth challenges"""
        # Board size: 8x8 to 12x12 (per design specification)
        width = self.random.randint(8, 12)
        height = self.random.randint(8, 12)

        # Generate board with patrol-friendly layout
        board = self._generate_board(width, height)

        # Place player and goal
        player_start, goal_position = self._place_player_and_goal(width, height, board['walls'])

        # Determine if attack item should be included (30% chance)
        include_attack_item = self.random.choice([True, False, False])  # 30% chance

        # Generate items (attack item if decided)
        items = self._generate_patrol_items(width, height, board['walls'], player_start, goal_position, include_attack_item)

        # Generate patrolling enemies with HP adjusted for items
        enemies = self._generate_patrol_enemies(width, height, board['walls'], player_start, goal_position, include_attack_item)

        # Create stage configuration
        stage_config = StageConfiguration(
            id=f"generated_patrol_{self.seed}",
            title="Generated Patrol Stage",
            description="Randomly generated stage focusing on stealth navigation and enemy patrol patterns.",
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
                hp=30,  # Low HP - enemy can defeat in one hit
                max_hp=30,
                attack_power=50  # High attack to defeat enemies quickly
            ),
            goal=GoalConfiguration(
                position=goal_position
            ),
            enemies=enemies,
            items=items,
            constraints=ConstraintConfiguration(
                max_turns=self._calculate_max_turns(width, height, len(enemies)),
                allowed_apis=["turn_left", "turn_right", "move", "wait", "see", "attack"]
            ),
            victory_conditions=[
                {"type": "defeat_all_enemies"},
                {"type": "reach_goal"}
            ]
        )

        return stage_config

    def _generate_board(self, width: int, height: int) -> dict:
        """Generate board with single pillar for patrol routes"""
        # Initialize empty board
        grid = [['.' for _ in range(width)] for _ in range(height)]
        walls = set()

        # Create single central pillar for patrol
        self._place_patrol_pillar(width, height, grid, walls)

        # Convert grid to string list
        grid_strings = [''.join(row) for row in grid]

        return {
            'grid': grid_strings,
            'walls': walls,
            'pillar_center': getattr(self, '_pillar_center', None)
        }

    def _place_patrol_pillar(self, width: int, height: int, grid: List[List[str]], walls: Set[Tuple[int, int]]):
        """Place a single central pillar for enemy patrol routes"""
        # Calculate center position, ensuring at least 2 cells from edges for patrol clearance
        min_x, max_x = 2, width - 3
        min_y, max_y = 2, height - 3

        # Ensure we have valid bounds
        if min_x >= max_x or min_y >= max_y:
            # Board too small, place pillar at center
            pillar_x = width // 2
            pillar_y = height // 2
        else:
            pillar_x = self.random.randint(min_x, max_x)
            pillar_y = self.random.randint(min_y, max_y)

        # Place the single pillar
        walls.add((pillar_x, pillar_y))
        grid[pillar_y][pillar_x] = '#'

        # Store pillar center for enemy placement
        self._pillar_center = (pillar_x, pillar_y)

    def _place_player_and_goal(self, width: int, height: int, walls: Set[Tuple[int, int]]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Place player and goal for stealth navigation scenarios, ensuring player starts outside enemy vision"""
        available_positions = [(x, y) for x in range(width) for y in range(height)
                              if (x, y) not in walls]

        if len(available_positions) < 2:
            return (0, 0), (width-1, height-1)

        # Get pillar center to determine safe starting positions
        pillar_center = getattr(self, '_pillar_center', None)

        # Calculate safe positions (outside enemy vision range)
        safe_positions = []

        for x, y in available_positions:
            is_safe = True

            if pillar_center:
                # Check distance from pillar area (enemy patrol zone)
                pillar_x, pillar_y = pillar_center

                # Enemy vision range: assume 3-cell radius from patrol positions around pillar
                # Patrol positions are around pillar (±1 from pillar center)
                for patrol_dx in [-1, 0, 1]:
                    for patrol_dy in [-1, 0, 1]:
                        if patrol_dx == 0 and patrol_dy == 0:  # Skip pillar center
                            continue

                        patrol_x = pillar_x + patrol_dx
                        patrol_y = pillar_y + patrol_dy

                        # Check if player position is within enemy vision range (3 cells)
                        distance = abs(x - patrol_x) + abs(y - patrol_y)  # Manhattan distance
                        if distance <= 3:
                            is_safe = False
                            break

                    if not is_safe:
                        break

            if is_safe:
                safe_positions.append((x, y))

        # Use safe positions if available, otherwise fallback to corners
        if safe_positions:
            player_start = self.random.choice(safe_positions)
        else:
            # Fallback to corner positions (furthest from center)
            corner_positions = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
            valid_corners = [pos for pos in corner_positions if pos in available_positions]
            player_start = self.random.choice(valid_corners) if valid_corners else self.random.choice(available_positions)

        # Goal: place at significant distance requiring navigation through patrol zones
        remaining_positions = [pos for pos in available_positions if pos != player_start]
        if not remaining_positions:
            return player_start, (min(width-1, player_start[0]+1), min(height-1, player_start[1]+1))

        # Filter by distance (minimum 6 Manhattan units for stealth challenge)
        valid_goals = []
        for pos in remaining_positions:
            dist = abs(pos[0] - player_start[0]) + abs(pos[1] - player_start[1])
            if dist >= 6:
                valid_goals.append(pos)

        if valid_goals:
            goal_position = self.random.choice(valid_goals)
        else:
            goal_position = self.random.choice(remaining_positions)

        return player_start, goal_position

    def _generate_patrol_enemies(self, width: int, height: int, walls: Set[Tuple[int, int]],
                               player_start: Tuple[int, int], goal_position: Tuple[int, int], include_attack_item: bool = False) -> List[EnemyConfiguration]:
        """Generate 2-4 patrolling enemies positioned around the central pillar"""
        # Get pillar center if available
        pillar_center = getattr(self, '_pillar_center', None)

        if pillar_center:
            # Generate positions around the pillar (1-cell radius)
            pillar_x, pillar_y = pillar_center
            patrol_positions = []

            # 8 directions around the pillar
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:  # Skip pillar center
                        continue

                    pos_x, pos_y = pillar_x + dx, pillar_y + dy

                    # Check if position is valid
                    if (0 <= pos_x < width and 0 <= pos_y < height and
                        (pos_x, pos_y) not in walls and
                        (pos_x, pos_y) != player_start and
                        (pos_x, pos_y) != goal_position):
                        patrol_positions.append((pos_x, pos_y))

            # Use patrol positions if available, otherwise fall back to general positions
            if patrol_positions:
                available_positions = patrol_positions
            else:
                # Fallback: get all available positions
                available_positions = [(x, y) for x in range(width) for y in range(height)
                                     if ((x, y) not in walls and
                                         (x, y) != player_start and
                                         (x, y) != goal_position)]
        else:
            # No pillar center, use all available positions
            available_positions = [(x, y) for x in range(width) for y in range(height)
                                 if ((x, y) not in walls and
                                     (x, y) != player_start and
                                     (x, y) != goal_position)]

        if not available_positions:
            return []

        # Single patrolling enemy around the pillar (1 enemy per pillar)
        enemy_count = 1

        enemies = []

        if pillar_center and patrol_positions:
            # Select one position around the pillar for the patrol enemy
            selected_position = self.random.choice(patrol_positions)

            # HP adjustment based on attack item availability
            if include_attack_item:
                # Attack item present: enemy should be defeated in 1 hit with item (assume item provides +50 attack)
                # Player base attack (50) + item attack (+50) = 100 total attack
                enemy_hp = self.random.randint(80, 100)  # 1-hit kill with item
            else:
                # No attack item: enemy should be defeated in 2 hits with default attack (50)
                # Player base attack (50) * 2 = 100 total damage needed
                enemy_hp = self.random.randint(80, 100)  # 2-hit kill with default attack

            # Use existing enemy types for patrol stages
            enemy_types = ["normal", "goblin", "orc"]
            enemy_type = self.random.choice(enemy_types)

            # Generate patrol path around the pillar
            patrol_path = self._generate_patrol_path_around_pillar(pillar_center)

            # Set initial direction based on patrol path and current position
            initial_direction = self._get_patrol_direction(selected_position, patrol_path)

            enemy = EnemyConfiguration(
                id="patrol_guard",
                type=enemy_type,
                position=selected_position,
                direction=initial_direction,
                hp=enemy_hp,
                max_hp=enemy_hp,
                attack_power=self.random.randint(30, 40),  # Enough to defeat player in one hit (30 HP)
                behavior="patrol",  # Single enemy patrols around pillar
                patrol_path=patrol_path,  # Add patrol path for movement
                vision_range=2  # Fixed vision range for patrol enemies
            )
            enemies.append(enemy)

        # Add 1-2 additional guard enemies in other areas (not around pillar)
        other_positions = [pos for pos in available_positions
                          if pillar_center is None or pos not in patrol_positions]

        if other_positions:
            additional_guards = self.random.randint(1, min(2, len(other_positions)))
            selected_other_positions = self.random.sample(other_positions, additional_guards)

            for i, position in enumerate(selected_other_positions):
                # HP adjustment based on attack item availability (same as patrol enemy)
                if include_attack_item:
                    enemy_hp = self.random.randint(80, 100)  # 1-hit kill with item
                else:
                    enemy_hp = self.random.randint(80, 100)  # 2-hit kill with default attack

                enemy_types = ["normal", "goblin", "orc"]
                enemy_type = self.random.choice(enemy_types)

                enemy = EnemyConfiguration(
                    id=f"guard_{i+1}",
                    type=enemy_type,
                    position=position,
                    direction=self._random_direction(),
                    hp=enemy_hp,
                    max_hp=enemy_hp,
                    attack_power=self.random.randint(30, 40),  # Enough to defeat player in one hit (30 HP)
                    behavior="guard",  # Other enemies are stationary guards
                    vision_range=2  # Fixed vision range for guard enemies
                )
                enemies.append(enemy)

        return enemies

    def _generate_patrol_path_around_pillar(self, pillar_center: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Generate a clockwise patrol path around the pillar"""
        if not pillar_center:
            return []

        pillar_x, pillar_y = pillar_center

        # Create a clockwise patrol path around the pillar (8 positions)
        # Starting from the north and going clockwise (right turn around pillar)
        patrol_path = [
            (pillar_x, pillar_y - 1),     # North of pillar
            (pillar_x + 1, pillar_y - 1), # Northeast of pillar
            (pillar_x + 1, pillar_y),     # East of pillar
            (pillar_x + 1, pillar_y + 1), # Southeast of pillar
            (pillar_x, pillar_y + 1),     # South of pillar
            (pillar_x - 1, pillar_y + 1), # Southwest of pillar
            (pillar_x - 1, pillar_y),     # West of pillar
            (pillar_x - 1, pillar_y - 1)  # Northwest of pillar
        ]

        return patrol_path

    def _get_patrol_direction(self, current_position: Tuple[int, int], patrol_path: List[Tuple[int, int]]) -> str:
        """Get initial direction for enemy based on current position and patrol path"""
        if not patrol_path or current_position not in patrol_path:
            return self._random_direction()

        # Find current position in patrol path
        current_index = patrol_path.index(current_position)

        # Get next position in clockwise direction
        next_index = (current_index + 1) % len(patrol_path)
        next_position = patrol_path[next_index]

        # Calculate direction from current to next position
        dx = next_position[0] - current_position[0]
        dy = next_position[1] - current_position[1]

        # Convert to direction string
        if dx > 0:
            return "E"  # Moving East
        elif dx < 0:
            return "W"  # Moving West
        elif dy > 0:
            return "S"  # Moving South
        elif dy < 0:
            return "N"  # Moving North
        else:
            return self._random_direction()  # Fallback

    def _random_direction(self) -> str:
        """Generate random direction"""
        directions = ["N", "S", "E", "W"]
        return self.random.choice(directions)

    def _calculate_max_turns(self, width: int, height: int, enemy_count: int) -> int:
        """Calculate max turns based on stealth navigation requirements"""
        # Base movement turns (longer for stealth navigation)
        base_turns = (width + height) * 3

        # Add turns for stealth mechanics (waiting for patrol patterns)
        stealth_turns = enemy_count * self.random.randint(8, 15)

        # Add tactical planning buffer
        total_turns = int((base_turns + stealth_turns) * 1.4)

        return max(60, min(500, total_turns))

    def _generate_patrol_items(self, width: int, height: int, walls: Set[Tuple[int, int]],
                              player_start: Tuple[int, int], goal_position: Tuple[int, int], include_attack_item: bool) -> List:
        """Generate items for patrol stage (attack item if specified)"""
        from stage_generator.data_models import ItemConfiguration

        if not include_attack_item:
            return []

        # Find suitable positions for the attack item
        available_positions = [(x, y) for x in range(width) for y in range(height)
                              if ((x, y) not in walls and
                                  (x, y) != player_start and
                                  (x, y) != goal_position)]

        if not available_positions:
            return []

        # Place attack item at a random available position
        item_position = self.random.choice(available_positions)

        # Attack weapon types
        weapon_types = ["sword", "axe", "bow", "dagger"]
        weapon_type = self.random.choice(weapon_types)

        attack_item = ItemConfiguration(
            id="patrol_weapon",
            type="weapon",
            name=f"enhanced_{weapon_type}",
            description=f"A powerful {weapon_type} that increases attack power by 50.",
            position=item_position,
            value=50  # Attack power bonus
        )

        return [attack_item]