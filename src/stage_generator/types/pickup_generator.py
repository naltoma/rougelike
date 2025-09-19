"""Pickup stage generator for collection scenarios"""
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


class PickupStageGenerator:
    """Generator for pickup-type stages (collection scenarios)"""

    def __init__(self, seed: int):
        self.random = random.Random(seed)
        self.seed = seed

    def generate(self) -> StageConfiguration:
        """Generate a pickup stage with item collection challenges"""
        # Board size: 7x7 to 10x10 (per design specification)
        width = self.random.randint(7, 10)
        height = self.random.randint(7, 10)

        # Generate board with mixed wall density
        board = self._generate_board(width, height)

        # Place player and goal
        player_start, goal_position = self._place_player_and_goal(width, height, board['walls'])

        # Generate items (2-4 items for collection)
        items = self._generate_items(width, height, board['walls'], player_start, goal_position)

        # Generate optional enemies (0-2 enemies for added challenge)
        enemies = self._generate_enemies(width, height, board['walls'], player_start, goal_position, items)

        # Create stage configuration
        stage_config = StageConfiguration(
            id=f"generated_pickup_{self.seed}",
            title="Generated Pickup Stage",
            description="Randomly generated stage focusing on item collection and resource management.",
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
                allowed_apis=["turn_left", "turn_right", "move", "pickup", "see"] +
                           (["attack"] if enemies else [])
            ),
            victory_conditions=[
                {"type": "collect_all_items"},
                {"type": "reach_goal"}
            ] if items else [{"type": "reach_goal"}]
        )

        return stage_config

    def _generate_board(self, width: int, height: int) -> dict:
        """Generate board with moderate wall placement for item collection"""
        # Lower wall density: 8-20% (ensure better connectivity for collection scenarios)
        total_cells = width * height
        target_wall_density = self.random.uniform(0.08, 0.20)
        target_wall_count = int(total_cells * target_wall_density)

        # Initialize empty board
        grid = [['.' for _ in range(width)] for _ in range(height)]
        walls = set()

        # Place walls with corridor patterns for exploration
        self._place_corridor_walls(width, height, grid, walls, target_wall_count)

        # Convert grid to string list
        grid_strings = [''.join(row) for row in grid]

        return {
            'grid': grid_strings,
            'walls': walls
        }

    def _place_corridor_walls(self, width: int, height: int, grid: List[List[str]],
                            walls: Set[Tuple[int, int]], target_count: int):
        """Place walls to create corridor-like exploration areas"""
        placed_walls = 0

        # Pattern 1: Create room-like structures with openings
        room_count = self.random.randint(1, 2)
        for _ in range(room_count):
            if placed_walls >= target_count:
                break

            # Room dimensions
            room_width = self.random.randint(3, min(width//2, 5))
            room_height = self.random.randint(3, min(height//2, 5))

            # Room position (avoid edges)
            room_x = self.random.randint(1, width - room_width - 1)
            room_y = self.random.randint(1, height - room_height - 1)

            # Create room walls (with openings)
            room_walls = []

            # Top and bottom walls
            for x in range(room_x, room_x + room_width):
                room_walls.append((x, room_y))  # Top
                room_walls.append((x, room_y + room_height - 1))  # Bottom

            # Left and right walls
            for y in range(room_y, room_y + room_height):
                room_walls.append((room_x, y))  # Left
                room_walls.append((room_x + room_width - 1, y))  # Right

            # Remove some walls to create openings (1-2 openings per room)
            opening_count = self.random.randint(1, 2)
            for _ in range(opening_count):
                if room_walls:
                    opening_pos = self.random.choice(room_walls)
                    room_walls.remove(opening_pos)

            # Place remaining walls
            for x, y in room_walls:
                if (0 <= x < width and 0 <= y < height and
                    (x, y) not in walls and placed_walls < target_count):
                    walls.add((x, y))
                    grid[y][x] = '#'
                    placed_walls += 1

        # Pattern 2: Random scattered walls (avoid edges to preserve connectivity)
        attempts = 0
        while placed_walls < target_count and attempts < target_count * 2:
            # Place walls mainly in interior to preserve edge connectivity
            if width >= 3 and height >= 3:
                x = self.random.randint(1, width - 2)  # Avoid edges
                y = self.random.randint(1, height - 2)  # Avoid edges
            else:
                x = self.random.randint(0, width - 1)
                y = self.random.randint(0, height - 1)

            if (x, y) not in walls:
                walls.add((x, y))
                grid[y][x] = '#'
                placed_walls += 1

            attempts += 1

    def _place_player_and_goal(self, width: int, height: int, walls: Set[Tuple[int, int]]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Place player and goal with guaranteed connectivity"""
        available_positions = [(x, y) for x in range(width) for y in range(height)
                              if (x, y) not in walls]

        if len(available_positions) < 2:
            return (0, 0), (width-1, height-1)

        # For pickup stages, ensure simple connectivity by placing player and goal in corners
        # This reduces chance of isolated regions

        # Try corner positions first for maximum separation
        corner_positions = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        valid_corners = [pos for pos in corner_positions if pos in available_positions]

        if len(valid_corners) >= 2:
            # Choose two different corners
            selected_corners = self.random.sample(valid_corners, 2)
            player_start = selected_corners[0]
            goal_position = selected_corners[1]
        else:
            # Fallback: use edge positions with good separation
            edge_positions = [pos for pos in available_positions
                            if pos[0] == 0 or pos[0] == width-1 or pos[1] == 0 or pos[1] == height-1]

            if len(edge_positions) >= 2:
                # Choose two edge positions with maximum distance
                max_dist = 0
                best_pair = None
                for i, pos1 in enumerate(edge_positions):
                    for pos2 in edge_positions[i+1:]:
                        dist = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
                        if dist > max_dist:
                            max_dist = dist
                            best_pair = (pos1, pos2)

                if best_pair:
                    player_start, goal_position = best_pair
                else:
                    player_start = edge_positions[0]
                    goal_position = edge_positions[1] if len(edge_positions) > 1 else available_positions[1]
            else:
                # Final fallback: any two positions with good separation
                player_start = available_positions[0]
                remaining_positions = [pos for pos in available_positions if pos != player_start]

                # Find position with maximum distance
                max_dist = 0
                goal_position = remaining_positions[0]
                for pos in remaining_positions:
                    dist = abs(pos[0] - player_start[0]) + abs(pos[1] - player_start[1])
                    if dist > max_dist:
                        max_dist = dist
                        goal_position = pos

        return player_start, goal_position

    def _generate_items(self, width: int, height: int, walls: Set[Tuple[int, int]],
                       player_start: Tuple[int, int], goal_position: Tuple[int, int]) -> List[ItemConfiguration]:
        """Generate 2-4 items spread across the stage"""
        available_positions = []
        for x in range(width):
            for y in range(height):
                if ((x, y) not in walls and
                    (x, y) != player_start and
                    (x, y) != goal_position):
                    available_positions.append((x, y))

        if not available_positions:
            return []

        # Item count: 2-4 items (per design specification)
        item_count = self.random.randint(2, min(4, len(available_positions)))
        selected_positions = self.random.sample(available_positions, item_count)

        items = []
        item_types = ["key", "coin", "potion", "gem", "scroll"]

        for i, position in enumerate(selected_positions):
            item_type = self.random.choice(item_types)

            # Generate appropriate Japanese names based on item type
            name_map = {
                "key": "古い鍵",
                "coin": "金貨",
                "potion": "回復薬",
                "gem": "宝石",
                "scroll": "巻物"
            }

            item = ItemConfiguration(
                id=f"{item_type}_{i+1}",
                type=item_type,
                position=position,
                name=name_map.get(item_type, f"{item_type.capitalize()} {i+1}"),
                description=f"A valuable {item_type} to collect",
                value=self.random.randint(10, 50)
            )
            items.append(item)

        return items

    def _generate_enemies(self, width: int, height: int, walls: Set[Tuple[int, int]],
                         player_start: Tuple[int, int], goal_position: Tuple[int, int],
                         items: List[ItemConfiguration]) -> List[EnemyConfiguration]:
        """Generate 0-2 enemies to add challenge without overwhelming collection focus"""
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

        # Enemy count: 0-2 enemies (40% chance of no enemies for pure collection)
        if self.random.random() < 0.4:
            return []

        enemy_count = self.random.randint(1, min(2, len(available_positions)))
        selected_positions = self.random.sample(available_positions, enemy_count)

        enemies = []
        for i, position in enumerate(selected_positions):
            # Light enemies for pickup stages (lower HP than attack stages)
            enemy_hp = self.random.randint(15, 50)

            enemy = EnemyConfiguration(
                id=f"collector_{i+1}",
                type="normal",
                position=position,
                direction=self._random_direction(),
                hp=enemy_hp,
                max_hp=enemy_hp,
                attack_power=self.random.randint(15, 25),
                behavior="normal"
            )
            enemies.append(enemy)

        return enemies

    def _random_direction(self) -> str:
        """Generate random direction"""
        directions = ["N", "S", "E", "W"]
        return self.random.choice(directions)

    def _calculate_max_turns(self, width: int, height: int, item_count: int, enemy_count: int) -> int:
        """Calculate max turns based on collection and combat requirements"""
        # Base movement turns
        base_turns = (width + height) * 2

        # Add turns for item collection (estimated 5-8 turns per item)
        collection_turns = item_count * self.random.randint(5, 8)

        # Add turns for combat if enemies present
        combat_turns = enemy_count * self.random.randint(2, 6) if enemy_count > 0 else 0

        # Add exploration buffer
        total_turns = int((base_turns + collection_turns + combat_turns) * 1.3)

        return max(40, min(400, total_turns))