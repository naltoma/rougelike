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
        "--version",
        action="version",
        version="Stage Generator v1.2.9"
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

    # Create generation parameters
    params = GenerationParameters(
        stage_type=stage_type,
        seed=args.seed,
        output_path=args.output,
        validate=args.validate
    )

    try:
        # Generate stage using appropriate generator
        if not args.quiet:
            print(f"Generating {stage_type.value} stage with seed {args.seed}...")

        # Get the appropriate generator
        generator = _get_generator(stage_type, args.seed)

        # Generate the stage
        stage_config = generator.generate()

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


def _get_generator(stage_type: StageType, seed: int):
    """Get the appropriate generator for the stage type"""
    if stage_type == StageType.MOVE:
        return MoveStageGenerator(seed)
    elif stage_type == StageType.ATTACK:
        return AttackStageGenerator(seed)
    elif stage_type == StageType.PICKUP:
        return PickupStageGenerator(seed)
    elif stage_type == StageType.PATROL:
        return PatrolStageGenerator(seed)
    elif stage_type == StageType.SPECIAL:
        return SpecialStageGenerator(seed)
    else:
        raise UnsupportedStageTypeError(f"Unsupported stage type: {stage_type}")


if __name__ == "__main__":
    sys.exit(main())