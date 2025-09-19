"""Special stage generator for complex multi-mechanic scenarios"""
import random
from typing import List, Tuple, Set
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from stage_generator.data_models import (
    StageConfiguration, BoardConfiguration, PlayerConfiguration,
    GoalConfiguration, ItemConfiguration, EnemyConfiguration, ConstraintConfiguration
)


class SpecialStageGenerator:
    """Generator for special-type stages (complex multi-mechanic scenarios)"""

    def __init__(self, seed: int):
        self.random = random.Random(seed)
        self.seed = seed

    def generate(self) -> StageConfiguration:
        """Generate a special stage combining multiple game mechanics"""
        # Board size: 10x10 to 15x15 (per design specification - largest for complexity)
        width = self.random.randint(10, 15)
        height = self.random.randint(10, 15)

        # Generate complex board layout
        board = self._generate_board(width, height)

        # Place player and goal
        player_start, goal_position = self._place_player_and_goal(width, height, board['walls'])

        # Generate mixed scenario (items + enemies + special mechanics)
        items = self._generate_special_items(width, height, board['walls'], player_start, goal_position)
        enemies = self._generate_mixed_enemies(width, height, board['walls'], player_start, goal_position, items)

        # Determine special mechanics for this stage
        special_apis = self._determine_special_apis()

        # Create stage configuration
        stage_config = StageConfiguration(
            id=f"generated_special_{self.seed}",
            title="Generated Special Stage",
            description="Randomly generated advanced stage combining multiple game mechanics and challenges.",
            board=BoardConfiguration(
                size=(width, height),
                grid=board['grid'],
                legend={
                    ".": "empty",
                    "#": "wall",
                    "P": "player",
                    "G": "goal",
                    "I": "item",
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
            items=items,
            constraints=ConstraintConfiguration(
                max_turns=self._calculate_max_turns(width, height, len(items), len(enemies)),
                allowed_apis=special_apis
            )
        )

        return stage_config

    def _generate_board(self, width: int, height: int) -> dict:
        """Generate complex board with multiple zones and challenge areas"""
        # Variable wall density: 20-40% (complex layouts)
        total_cells = width * height
        target_wall_density = self.random.uniform(0.20, 0.40)
        target_wall_count = int(total_cells * target_wall_density)

        # Initialize empty board
        grid = [['.' for _ in range(width)] for _ in range(height)]
        walls = set()

        # Create complex multi-zone layout
        self._place_complex_walls(width, height, grid, walls, target_wall_count)

        # Convert grid to string list
        grid_strings = [''.join(row) for row in grid]

        return {
            'grid': grid_strings,
            'walls': walls
        }

    def _place_complex_walls(self, width: int, height: int, grid: List[List[str]],
                           walls: Set[Tuple[int, int]], target_count: int):
        """Place walls to create complex multi-zone layout"""
        placed_walls = 0

        # Zone 1: Central fortress/maze area
        center_x = width // 2
        center_y = height // 2
        fortress_size = min(width // 3, height // 3, 6)

        # Create fortress walls
        for i in range(fortress_size):
            for j in range(fortress_size):
                x = center_x - fortress_size // 2 + i
                y = center_y - fortress_size // 2 + j

                if (0 <= x < width and 0 <= y < height and placed_walls < target_count):
                    # Create fortress perimeter
                    if (i == 0 or i == fortress_size - 1 or
                        j == 0 or j == fortress_size - 1):
                        walls.add((x, y))
                        grid[y][x] = '#'
                        placed_walls += 1
                    # Create internal maze structure
                    elif (i % 2 == 0 and j % 2 == 0) and self.random.random() < 0.6:
                        walls.add((x, y))
                        grid[y][x] = '#'
                        placed_walls += 1

        # Add fortress entrances
        entrance_count = self.random.randint(2, 4)
        perimeter_positions = []
        for i in range(fortress_size):
            # Top and bottom
            perimeter_positions.append((center_x - fortress_size // 2 + i, center_y - fortress_size // 2))
            perimeter_positions.append((center_x - fortress_size // 2 + i, center_y + fortress_size // 2 - 1))
            # Left and right
            perimeter_positions.append((center_x - fortress_size // 2, center_y - fortress_size // 2 + i))
            perimeter_positions.append((center_x + fortress_size // 2 - 1, center_y - fortress_size // 2 + i))

        # Create entrances by removing some perimeter walls
        for _ in range(entrance_count):
            if perimeter_positions:
                entrance_pos = self.random.choice(perimeter_positions)
                if entrance_pos in walls:
                    walls.remove(entrance_pos)
                    grid[entrance_pos[1]][entrance_pos[0]] = '.'
                    placed_walls -= 1
                perimeter_positions.remove(entrance_pos)

        # Zone 2: Outer defensive structures
        structure_count = self.random.randint(2, 4)
        for _ in range(structure_count):
            if placed_walls >= target_count:
                break

            # Random structure position (avoid center)
            struct_x = self.random.choice([
                self.random.randint(0, width // 3),
                self.random.randint(2 * width // 3, width - 1)
            ])
            struct_y = self.random.choice([
                self.random.randint(0, height // 3),
                self.random.randint(2 * height // 3, height - 1)
            ])

            # Create small defensive structure
            structure_type = self.random.choice(['wall_line', 'bunker', 'barrier'])

            if structure_type == 'wall_line':
                # Create wall line (horizontal or vertical)
                if self.random.choice([True, False]):  # horizontal
                    line_length = self.random.randint(3, 6)
                    for i in range(line_length):
                        x = min(struct_x + i, width - 1)
                        if (x, struct_y) not in walls and placed_walls < target_count:
                            walls.add((x, struct_y))
                            grid[struct_y][x] = '#'
                            placed_walls += 1
                else:  # vertical
                    line_length = self.random.randint(3, 6)
                    for i in range(line_length):
                        y = min(struct_y + i, height - 1)
                        if (struct_x, y) not in walls and placed_walls < target_count:
                            walls.add((struct_x, y))
                            grid[y][struct_x] = '#'
                            placed_walls += 1

            elif structure_type == 'bunker':
                # Create small 2x2 bunker with opening
                bunker_positions = [
                    (struct_x, struct_y), (struct_x + 1, struct_y),
                    (struct_x, struct_y + 1), (struct_x + 1, struct_y + 1)
                ]
                # Remove one position for opening
                bunker_positions.pop(self.random.randint(0, len(bunker_positions) - 1))

                for x, y in bunker_positions:
                    if (0 <= x < width and 0 <= y < height and
                        (x, y) not in walls and placed_walls < target_count):
                        walls.add((x, y))
                        grid[y][x] = '#'
                        placed_walls += 1

        # Zone 3: Random scattered obstacles for remaining count
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
        """Place player and goal for maximum strategic challenge"""
        available_positions = [(x, y) for x in range(width) for y in range(height)
                              if (x, y) not in walls]

        if len(available_positions) < 2:
            return (0, 0), (width-1, height-1)

        # Player start: prefer corner positions for clear starting point
        corner_positions = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        valid_corners = [pos for pos in corner_positions if pos in available_positions]

        if valid_corners:
            player_start = self.random.choice(valid_corners)
        else:
            # Fallback to positions near edges
            edge_positions = [pos for pos in available_positions
                            if pos[0] == 0 or pos[0] == width-1 or pos[1] == 0 or pos[1] == height-1]
            player_start = self.random.choice(edge_positions) if edge_positions else self.random.choice(available_positions)

        # Goal: place at maximum distance or in central fortress area
        remaining_positions = [pos for pos in available_positions if pos != player_start]
        if not remaining_positions:
            return player_start, (min(width-1, player_start[0]+2), min(height-1, player_start[1]+2))

        # Prefer positions in center or at maximum distance
        center_x, center_y = width // 2, height // 2
        goal_candidates = []

        for pos in remaining_positions:
            dist = abs(pos[0] - player_start[0]) + abs(pos[1] - player_start[1])
            center_dist = abs(pos[0] - center_x) + abs(pos[1] - center_y)

            # Prefer central positions or maximum distance positions
            if center_dist <= 3 or dist >= max(width, height):
                goal_candidates.append(pos)

        if goal_candidates:
            goal_position = self.random.choice(goal_candidates)
        else:
            # Fallback to maximum distance
            distances = [(abs(pos[0] - player_start[0]) + abs(pos[1] - player_start[1]), pos)
                        for pos in remaining_positions]
            distances.sort(reverse=True)
            goal_position = distances[0][1]

        return player_start, goal_position

    def _generate_special_items(self, width: int, height: int, walls: Set[Tuple[int, int]],
                              player_start: Tuple[int, int], goal_position: Tuple[int, int]) -> List[ItemConfiguration]:
        """Generate special items with strategic placement"""
        available_positions = []
        for x in range(width):
            for y in range(height):
                if ((x, y) not in walls and
                    (x, y) != player_start and
                    (x, y) != goal_position):
                    available_positions.append((x, y))

        if not available_positions:
            return []

        # Item count: 1-3 items (fewer but more valuable in special stages)
        item_count = self.random.randint(1, min(3, len(available_positions)))
        selected_positions = self.random.sample(available_positions, item_count)

        items = []
        special_item_types = ["master_key", "power_crystal", "ancient_scroll", "magic_orb", "legendary_artifact"]

        for i, position in enumerate(selected_positions):
            item_type = self.random.choice(special_item_types)

            item = ItemConfiguration(
                id=f"{item_type}_{i+1}",
                type=item_type,
                position=position,
                name=f"{item_type.replace('_', ' ').title()}",
                description=f"A rare {item_type.replace('_', ' ')} with special properties",
                value=self.random.randint(50, 100)
            )
            items.append(item)

        return items

    def _generate_mixed_enemies(self, width: int, height: int, walls: Set[Tuple[int, int]],
                              player_start: Tuple[int, int], goal_position: Tuple[int, int],
                              items: List[ItemConfiguration]) -> List[EnemyConfiguration]:
        """Generate mixed enemy types with varying behaviors and strengths"""
        # Find positions not occupied by walls, player, goal, or items
        occupied_positions = {player_start, goal_position}
        occupied_positions.update(item.position for item in items)

        available_positions = []
        for x in range(width):
            for y in range(height):
                if ((x, y) not in walls and (x, y) not in occupied_positions):
                    available_positions.append((x, y))

        if not available_positions:
            return []

        # Enemy count: 3-6 enemies (challenging but manageable)
        enemy_count = self.random.randint(3, min(6, len(available_positions)))
        selected_positions = self.random.sample(available_positions, enemy_count)

        enemies = []
        enemy_types = ["normal", "patrol", "guardian", "elite"]
        behavior_types = ["normal", "patrol_horizontal", "patrol_vertical", "guard_area", "aggressive"]

        for i, position in enumerate(selected_positions):
            # Vary enemy types and strengths
            enemy_type = self.random.choice(enemy_types)
            behavior = self.random.choice(behavior_types)

            # Adjust HP based on enemy type
            if enemy_type == "elite":
                enemy_hp = self.random.randint(150, 300)
                attack_power = self.random.randint(40, 60)
            elif enemy_type == "guardian":
                enemy_hp = self.random.randint(100, 200)
                attack_power = self.random.randint(30, 50)
            elif enemy_type == "patrol":
                enemy_hp = self.random.randint(50, 100)
                attack_power = self.random.randint(20, 35)
            else:  # normal
                enemy_hp = self.random.randint(30, 80)
                attack_power = self.random.randint(15, 30)

            enemy = EnemyConfiguration(
                id=f"{enemy_type}_{i+1}",
                type=enemy_type,
                position=position,
                direction=self._random_direction(),
                hp=enemy_hp,
                max_hp=enemy_hp,
                attack_power=attack_power,
                behavior=behavior
            )
            enemies.append(enemy)

        return enemies

    def _determine_special_apis(self) -> List[str]:
        """Determine special API combinations for advanced stages"""
        # Base APIs always available
        base_apis = ["turn_left", "turn_right", "move", "see"]

        # Additional APIs based on random selection (multiple mechanics)
        additional_apis = []

        # Combat capability (high chance)
        if self.random.random() < 0.8:
            additional_apis.append("attack")

        # Item interaction (high chance)
        if self.random.random() < 0.7:
            additional_apis.append("pickup")

        # Stealth/timing mechanics (moderate chance)
        if self.random.random() < 0.6:
            additional_apis.append("wait")

        # Ensure at least one additional mechanic
        if not additional_apis:
            additional_apis.append(self.random.choice(["attack", "pickup", "wait"]))

        return base_apis + additional_apis

    def _random_direction(self) -> str:
        """Generate random direction"""
        directions = ["N", "S", "E", "W"]
        return self.random.choice(directions)

    def _calculate_max_turns(self, width: int, height: int, item_count: int, enemy_count: int) -> int:
        """Calculate max turns for complex multi-mechanic scenarios"""
        # Base movement turns (higher for complex navigation)
        base_turns = (width + height) * 4

        # Add turns for item collection
        collection_turns = item_count * self.random.randint(8, 15)

        # Add turns for combat (more enemies, more combat)
        combat_turns = enemy_count * self.random.randint(5, 12)

        # Add strategic planning buffer (highest for special stages)
        total_turns = int((base_turns + collection_turns + combat_turns) * 1.6)

        return max(80, min(800, total_turns))