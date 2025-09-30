#!/usr/bin/env python3
"""CLI script for generating random stages"""
import argparse
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from stage_generator.data_models import StageType, GenerationParameters, InvalidSeedError, UnsupportedStageTypeError
    from stage_generator.types.move_generator import MoveStageGenerator
    from stage_generator.types.attack_generator import AttackStageGenerator
    from stage_generator.types.pickup_generator import PickupStageGenerator
    from stage_generator.types.patrol_generator import PatrolStageGenerator
    from stage_generator.types.special_generator import SpecialStageGenerator
    from yaml_manager import save_stage_config
    from stage_validator.validator import StageValidator
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Error: Required modules not available: {e}", file=sys.stderr)
    IMPORTS_AVAILABLE = False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Generate random roguelike stages",
        prog="generate_stage.py"
    )

    parser.add_argument(
        "--type", "-t",
        choices=["move", "attack", "pickup", "patrol", "special"],
        required=True,
        help="Stage type to generate"
    )

    parser.add_argument(
        "--seed", "-s",
        type=int,
        required=True,
        help="Random seed for reproducible generation (0 to 2^32-1)"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file path (default: stages/generated_[type]_[seed].yml)"
    )

    parser.add_argument(
        "--validate", "-v",
        action="store_true",
        help="Validate solvability after generation"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output messages"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["yaml", "json"],
        default="yaml",
        help="Output format (default: yaml)"
    )

    parser.add_argument(
        "--include-bombs",
        action="store_true",
        help="Include bomb items in generation (v1.2.12)"
    )

    parser.add_argument(
        "--bomb-ratio",
        type=float,
        default=0.3,
        help="Ratio of bomb items to total items (0.0-1.0, default: 0.3)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Stage Generator v1.2.12"
    )

    args = parser.parse_args()

    if not IMPORTS_AVAILABLE:
        print("Error: Stage generation system not available", file=sys.stderr)
        return 1

    # Validate seed range
    if not (0 <= args.seed <= 2**32 - 1):
        print("Error: Seed must be between 0 and 2^32-1", file=sys.stderr)
        return 1

    # Convert string stage type to enum
    try:
        stage_type = StageType(args.type)
    except ValueError:
        print(f"Error: Invalid stage type '{args.type}'", file=sys.stderr)
        print("Supported types: move, attack, pickup, patrol, special", file=sys.stderr)
        return 1

    # Validate bomb ratio
    if not (0.0 <= args.bomb_ratio <= 1.0):
        print("Error: Bomb ratio must be between 0.0 and 1.0", file=sys.stderr)
        return 1

    # Create generation parameters
    params = GenerationParameters(
        stage_type=stage_type,
        seed=args.seed,
        output_path=args.output,
        validate=args.validate
    )

    # Add bomb parameters (v1.2.12)
    params.include_bombs = args.include_bombs
    params.bomb_ratio = args.bomb_ratio

    try:
        # Generate stage using appropriate generator
        if not args.quiet:
            bomb_info = f" (with bombs: {args.bomb_ratio:.1%})" if args.include_bombs else ""
            print(f"Generating {stage_type.value} stage with seed {args.seed}{bomb_info}...")

        # Get the appropriate generator with bomb parameters
        generator = _get_generator(stage_type, args.seed, args.include_bombs, args.bomb_ratio)

        # Generate the stage
        stage_config = generator.generate()

        # Post-process to add bomb items if requested (v1.2.12)
        if args.include_bombs:
            # Replace or enhance items with bomb items
            original_items = stage_config.items or []
            item_count = len(original_items) if original_items else 2  # Default to 2 items if none

            # Get board information for proper positioning
            board_width, board_height = stage_config.board.size
            board_grid = stage_config.board.grid

            # Get position information from stage config
            player_start = stage_config.player.start if hasattr(stage_config.player, 'start') else None
            goal_position = stage_config.goal.position if hasattr(stage_config.goal, 'position') else None
            enemy_positions = [enemy.position for enemy in stage_config.enemies] if stage_config.enemies else []

            # Generate new items including bombs
            enhanced_items = generate_items_with_bombs(
                stage_type.value,
                max(item_count, 2),  # Ensure at least 2 items total
                include_bombs=True,
                bomb_ratio=args.bomb_ratio,
                seed=args.seed + 1000,  # Offset seed to avoid conflicts
                board_size=(board_width, board_height),  # Pass board dimensions
                board_grid=board_grid,  # Pass board layout for empty space detection
                player_start=player_start,  # Pass player position to exclude
                goal_position=goal_position,  # Pass goal position to exclude
                enemy_positions=enemy_positions  # Pass enemy positions to exclude
            )

            # Update stage configuration items
            stage_config.items = enhanced_items

        # Save to file
        if args.output:
            output_file = Path(args.output)
        else:
            # Default output file name
            output_file = Path(f"stages/{params.get_filename()}")

        # Create output directory if it doesn't exist
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if save_stage_config(stage_config, str(output_file)):
            if not args.quiet:
                print(f"✅ Generated {stage_type.value} stage with seed {args.seed}")
                print(f"   File: {output_file}")
                board_size = stage_config.board.size
                print(f"   Size: {board_size[0]}x{board_size[1]}")
                print(f"   Enemies: {len(stage_config.enemies)}")
                print(f"   Items: {len(stage_config.items)}")

            # Run validation if requested
            if args.validate:
                if not args.quiet:
                    print("🔍 Validating stage solvability...")

                validator = StageValidator(timeout_seconds=30)
                validation_result = validator.validate_stage(stage_config)

                if validation_result.success:
                    if not args.quiet:
                        print(f"✅ Validation passed: Stage is solvable")
                        print(f"   Solution length: {validation_result.solution_length} steps")
                else:
                    if not args.quiet:
                        print(f"❌ Validation failed: {validation_result.error_details}")
                    return 2

            return 0
        else:
            print("Error: Failed to save stage file", file=sys.stderr)
            return 3

    except Exception as e:
        print(f"Error: Generation failed: {e}", file=sys.stderr)
        return 1


def _get_generator(stage_type: StageType, seed: int, include_bombs: bool = False, bomb_ratio: float = 0.3):
    """Get the appropriate generator for the stage type"""
    # Create base generator
    if stage_type == StageType.MOVE:
        generator = MoveStageGenerator(seed)
    elif stage_type == StageType.ATTACK:
        generator = AttackStageGenerator(seed)
    elif stage_type == StageType.PICKUP:
        generator = PickupStageGenerator(seed)
    elif stage_type == StageType.PATROL:
        generator = PatrolStageGenerator(seed)
    elif stage_type == StageType.SPECIAL:
        generator = SpecialStageGenerator(seed)
    else:
        raise UnsupportedStageTypeError(f"Unsupported stage type: {stage_type}")

    # Configure bomb parameters if requested (v1.2.12)
    if include_bombs and hasattr(generator, 'set_bomb_parameters'):
        generator.set_bomb_parameters(include_bombs=True, bomb_ratio=bomb_ratio)

    return generator


def generate_items_with_bombs(stage_type: str, item_count: int, include_bombs: bool = False, bomb_ratio: float = 0.3, seed: int = None, board_size: tuple = (10, 10), board_grid: list = None, player_start: tuple = None, goal_position: tuple = None, enemy_positions: list = None) -> list:
    """Generate items including potential bomb items - v1.2.12

    Args:
        stage_type: Type of stage being generated
        item_count: Number of items to generate
        include_bombs: Whether to include bomb items
        bomb_ratio: Ratio of bomb items to total items (0.0-1.0)
        seed: Random seed for reproducible generation
        board_size: Board dimensions (width, height) for position bounds
        board_grid: Board layout grid for empty space detection
        player_start: Player start position to exclude
        goal_position: Goal position to exclude
        enemy_positions: List of enemy positions to exclude

    Returns:
        List of ItemConfiguration objects including bombs
    """
    import random
    from stage_generator.data_models import ItemConfiguration

    if seed is not None:
        random.seed(seed)

    items = []
    beneficial_types = ["key", "potion", "coin", "gem"]  # Use only valid types from stage_loader.py
    bomb_damages = [30, 50, 75, 100]

    # Find all empty spaces on the board
    board_width, board_height = board_size
    empty_positions = []

    # Create set of positions to exclude (player, goal, enemies)
    excluded_positions = set()
    if player_start:
        excluded_positions.add(tuple(player_start))
    if goal_position:
        excluded_positions.add(tuple(goal_position))
    if enemy_positions:
        for pos in enemy_positions:
            excluded_positions.add(tuple(pos))

    if board_grid:
        for y in range(board_height):
            for x in range(board_width):
                if y < len(board_grid) and x < len(board_grid[y]):
                    if board_grid[y][x] == '.' and (x, y) not in excluded_positions:  # Empty space, not excluded
                        empty_positions.append((x, y))

    # Fallback to border-avoiding random if no grid provided
    if not empty_positions:
        min_x, max_x = 1, board_width - 2  # Leave 1-cell border
        min_y, max_y = 1, board_height - 2
        if max_x < min_x:
            max_x = board_width - 1
        if max_y < min_y:
            max_y = board_height - 1
        # Generate fallback positions, excluding player/goal/enemy positions
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if (x, y) not in excluded_positions:
                    empty_positions.append((x, y))

    # Calculate number of bombs to generate
    bomb_count = 0
    if include_bombs:
        if item_count == 0:
            bomb_count = 1  # Always at least 1 bomb when include_bombs is True
        else:
            # Ensure at least 1 bomb, then apply ratio to remaining items
            bomb_count = max(1, int(item_count * bomb_ratio))
            bomb_count = min(bomb_count, item_count)  # Can't exceed total items

    # Ensure we don't exceed available positions
    max_items = min(item_count, len(empty_positions))
    if max_items < item_count:
        item_count = max_items
        bomb_count = min(bomb_count, item_count)

    # Track used positions to avoid duplicates
    used_positions = set()

    def get_random_empty_position():
        """Get a random empty position that hasn't been used"""
        available_positions = [pos for pos in empty_positions if pos not in used_positions]
        if not available_positions:
            return None
        return random.choice(available_positions)

    # Generate bomb items first
    for i in range(bomb_count):
        position = get_random_empty_position()
        if position is None:
            break  # No more positions available

        used_positions.add(position)
        bomb_item = ItemConfiguration(
            id=f"bomb_{i+1}",
            type="bomb",
            position=position,
            name=f"爆弾 {i+1}",
            damage=random.choice(bomb_damages),
            description="Dangerous explosive device - dispose safely!"
        )
        items.append(bomb_item)

    # Generate remaining beneficial items
    remaining_items = item_count - len(items)
    for i in range(remaining_items):
        position = get_random_empty_position()
        if position is None:
            break  # No more positions available

        used_positions.add(position)
        item_config = ItemConfiguration(
            id=f"item_{i+1}",
            type=random.choice(beneficial_types),
            position=position,
            name=f"Generated Item {i+1}"
        )
        items.append(item_config)

    # Shuffle to randomize placement order
    random.shuffle(items)
    return items


def validate_bomb_item_config(item_config: dict) -> bool:
    """Validate bomb item configuration - v1.2.12

    Args:
        item_config: Item configuration dictionary

    Returns:
        bool: True if valid bomb configuration
    """
    required_fields = ["id", "type", "position"]

    # Check required fields
    for field in required_fields:
        if field not in item_config:
            return False

    # Validate bomb-specific requirements
    if item_config["type"] == "bomb":
        # Damage must be positive if specified
        if "damage" in item_config:
            damage = item_config["damage"]
            if not isinstance(damage, int) or damage <= 0:
                return False

        # Position must be valid coordinates
        position = item_config["position"]
        if not isinstance(position, list) or len(position) != 2:
            return False

        if not all(isinstance(coord, int) for coord in position):
            return False

        return True

    # For non-bomb items, reject damage attribute
    if "damage" in item_config:
        return False

    return True


if __name__ == "__main__":
    sys.exit(main())