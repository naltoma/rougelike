#!/usr/bin/env python3
"""CLI script for validating stage solvability"""
import argparse
import sys
import json
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from yaml_manager import load_stage_config, validate_schema
    from stage_validator.validation_models import ValidationResult
    from stage_validator.validator import StageValidator
    from stage_generator.data_models import StageConfiguration
    import multiprocessing
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Error: Required modules not available: {e}", file=sys.stderr)
    IMPORTS_AVAILABLE = False


def parse_max_nodes(value):
    """Parse max nodes specification (e.g., 1000000, 50M, unlimited)"""
    if not value:
        return None

    value = value.lower().strip()
    if value in ['unlimited', 'infinite', 'inf', 'no-limit']:
        return float('inf')

    # Handle suffix multipliers
    multipliers = {
        'k': 1000,
        'm': 1000000,
        'g': 1000000000,
        'b': 1000000000  # billion
    }

    if value[-1] in multipliers:
        try:
            number = float(value[:-1])
            return int(number * multipliers[value[-1]])
        except ValueError:
            raise ValueError(f"Invalid max-nodes format: {value}")

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Invalid max-nodes format: {value}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Validate roguelike stage solvability",
        prog="validate_stage.py"
    )

    parser.add_argument(
        "--file", "-f",
        type=str,
        required=True,
        help="Path to stage YAML file"
    )

    parser.add_argument(
        "--detailed", "-d",
        action="store_true",
        help="Show detailed analysis"
    )

    parser.add_argument(
        "--solution", "-s",
        action="store_true",
        help="Generate solution code examples"
    )

    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=60,
        help="Validation timeout in seconds (default: 60)"
    )

    parser.add_argument(
        "--max-nodes", "-n",
        type=str,
        default=None,
        help="Maximum nodes to explore (e.g., 1000000, 50M, unlimited). Default: auto-detect based on stage type"
    )

    parser.add_argument(
        "--format", "-F",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Stage Validator v1.2.9"
    )

    args = parser.parse_args()

    if not IMPORTS_AVAILABLE:
        print("Error: Stage validation system not available", file=sys.stderr)
        return 2

    # Check if file exists
    stage_file = Path(args.file)
    if not stage_file.exists():
        error_msg = f"Error: Stage file not found: {args.file}"
        if args.format == "json":
            result = {
                "success": False,
                "error": "file_not_found",
                "message": error_msg
            }
            print(json.dumps(result))
        else:
            print(error_msg, file=sys.stderr)
        return 2

    # Validate timeout
    if args.timeout < 1:
        print("Error: Timeout must be at least 1 second", file=sys.stderr)
        return 2

    # Parse max nodes
    max_nodes = None
    if args.max_nodes:
        try:
            max_nodes = parse_max_nodes(args.max_nodes)
            if max_nodes == float('inf'):
                print(f"Using unlimited node exploration")
            else:
                print(f"Using maximum {max_nodes:,} nodes for exploration")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2

    try:
        # Load and validate YAML structure
        stage_data = load_stage_config(str(stage_file))

        if not validate_schema(stage_data):
            error_msg = f"Error: Invalid stage file format: {args.file}"
            if args.format == "json":
                result = {
                    "success": False,
                    "error": "invalid_format",
                    "message": error_msg
                }
                print(json.dumps(result))
            else:
                print(error_msg, file=sys.stderr)
            return 2

        # Convert to StageConfiguration and run real validation
        stage_config = StageConfiguration.from_dict(stage_data)
        validator = StageValidator(timeout_seconds=args.timeout)

        # Set max_nodes if specified
        if max_nodes is not None:
            validator.max_nodes = max_nodes

        validation_result = validator.validate_stage(
            stage_config,
            detailed=args.detailed,
            generate_solution=args.solution
        )
        validation_result.stage_path = str(stage_file)

        # Output result
        if args.format == "json":
            result_dict = {
                "success": validation_result.success,
                "stage_path": validation_result.stage_path,
                "path_found": validation_result.path_found,
                "required_apis": validation_result.required_apis,
                "solution_length": validation_result.solution_length
            }

            if args.detailed and validation_result.detailed_analysis:
                result_dict["detailed_analysis"] = validation_result.detailed_analysis

            if args.solution and validation_result.solution_code:
                result_dict["solution_code"] = validation_result.solution_code

            print(json.dumps(result_dict, indent=2))
        else:
            # Text format output
            print(validation_result.to_report())

            if args.detailed:
                print("\nSolution Analysis:")
                print(f"  Steps: {validation_result.solution_length}")
                print(f"  APIs used: {', '.join(validation_result.required_apis)}")

                if validation_result.detailed_analysis:
                    print(f"  Board size: {validation_result.detailed_analysis['board_size']}")
                    print(f"  Validation: {validation_result.detailed_analysis['validation_method']}")

            if args.solution and validation_result.solution_code:
                print("\n" + "="*60)
                print("🎯 SOLUTION CODE EXAMPLES")
                print("="*60)

                print("\n📋 OPTIMIZED SOLUTION (Recommended):")
                print("-" * 40)
                print(validation_result.solution_code['optimized'])

                print("\n📚 EDUCATIONAL SOLUTION (With Comments):")
                print("-" * 40)
                print(validation_result.solution_code['educational'])

                print("\n⚡ SIMPLE SOLUTION (Step by Step):")
                print("-" * 40)
                print(validation_result.solution_code['simple'])

                print("\n💡 USAGE:")
                print("Copy any of the above solve() functions into your main.py file.")
                print("The optimized version is recommended for normal use.")
                print("="*60)

        return 0 if validation_result.success else 1

    except Exception as e:
        error_msg = f"Error: Validation failed: {e}"
        if args.format == "json":
            result = {
                "success": False,
                "error": "validation_error",
                "message": str(e)
            }
            print(json.dumps(result))
        else:
            print(error_msg, file=sys.stderr)
        return 2




if __name__ == "__main__":
    sys.exit(main())