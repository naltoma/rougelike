#!/usr/bin/env python3
"""
CLI command for stage_name_resolver library.
Provides command-line interface for testing and validating stage name resolution.
"""

import argparse
import json
import sys
import tempfile
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from engine.gui_enhancement.stage_name_resolver import StageNameResolver


def validate_stage_files(args):
    """Validate stage ID format in multiple files."""
    resolver = StageNameResolver()

    print("=== Stage Name Validation ===")
    print()

    if args.files:
        for file_path in args.files:
            try:
                resolution = resolver.resolve_stage_name(file_path)
                validation = resolver.validate_stage_id(resolution.stage_id)

                print(f"File: {file_path}")
                print(f"  Stage ID: {resolution.stage_id}")
                print(f"  Display Name: {resolution.resolved_name}")
                print(f"  Valid Format: {validation.is_valid}")
                print(f"  Cached: {resolution.is_cached}")

                if not validation.is_valid:
                    print(f"  Error: {validation.error_message}")

                print()

            except Exception as e:
                print(f"File: {file_path}")
                print(f"  Error: {e}")
                print()
    else:
        print("No files specified. Use --files option.")


def test_stage_resolution(args):
    """Test stage resolution with sample files."""
    resolver = StageNameResolver()

    print("=== Stage Name Resolution Test ===")
    print()

    # Create temporary test files
    temp_dir = tempfile.mkdtemp()
    test_files = []

    try:
        # Valid stage file
        valid_file = Path(temp_dir) / "main_stage05.py"
        valid_content = '''#!/usr/bin/env python3
"""Test stage file"""

STAGE_ID = "stage05"
STUDENT_ID = "123456A"

def solve():
    pass
'''
        with open(valid_file, 'w') as f:
            f.write(valid_content)
        test_files.append(str(valid_file))

        # Invalid stage ID format
        invalid_file = Path(temp_dir) / "main_invalid.py"
        invalid_content = '''#!/usr/bin/env python3
"""Test stage file with invalid ID"""

STAGE_ID = "invalid_stage"
STUDENT_ID = "123456A"

def solve():
    pass
'''
        with open(invalid_file, 'w') as f:
            f.write(invalid_content)
        test_files.append(str(invalid_file))

        # Missing STAGE_ID
        missing_file = Path(temp_dir) / "main_missing.py"
        missing_content = '''#!/usr/bin/env python3
"""Test stage file without STAGE_ID"""

STUDENT_ID = "123456A"

def solve():
    pass
'''
        with open(missing_file, 'w') as f:
            f.write(missing_content)
        test_files.append(str(missing_file))

        # Test each file
        for file_path in test_files:
            print(f"Testing: {Path(file_path).name}")
            try:
                resolution = resolver.resolve_stage_name(file_path)
                validation = resolver.validate_stage_id(resolution.stage_id)

                result = {
                    "file": Path(file_path).name,
                    "stage_id": resolution.stage_id,
                    "display_name": resolution.resolved_name,
                    "is_valid": validation.is_valid,
                    "is_cached": resolution.is_cached
                }

                if not validation.is_valid:
                    result["error"] = validation.error_message

                if args.format == "json":
                    print(json.dumps(result, indent=2))
                else:
                    print(f"  Stage ID: {result['stage_id']}")
                    print(f"  Display: {result['display_name']}")
                    print(f"  Valid: {result['is_valid']}")
                    print(f"  Cached: {result['is_cached']}")
                    if "error" in result:
                        print(f"  Error: {result['error']}")

            except Exception as e:
                print(f"  Error: {e}")

            print()

        # Test caching behavior
        print("Testing caching behavior:")
        print("First resolution (should not be cached):")
        resolution1 = resolver.resolve_stage_name(str(valid_file))
        print(f"  Cached: {resolution1.is_cached}")

        print("Second resolution (should be cached):")
        resolution2 = resolver.resolve_stage_name(str(valid_file))
        print(f"  Cached: {resolution2.is_cached}")

    finally:
        # Clean up temp files
        import shutil
        shutil.rmtree(temp_dir)


def validate_stage_id_format(args):
    """Test stage ID format validation."""
    resolver = StageNameResolver()

    print("=== Stage ID Format Validation ===")
    print()

    test_ids = [
        "stage01",      # Valid
        "stage09",      # Valid
        "stage99",      # Valid
        "stage1",       # Invalid: single digit
        "stage001",     # Invalid: three digits
        "stageAB",      # Invalid: letters
        "level01",      # Invalid: wrong prefix
        "stage",        # Invalid: no number
        "",             # Invalid: empty
    ]

    for stage_id in test_ids:
        validation = resolver.validate_stage_id(stage_id)

        if args.format == "json":
            result = {
                "stage_id": stage_id,
                "is_valid": validation.is_valid,
                "error_message": validation.error_message
            }
            print(json.dumps(result))
        else:
            status = "✓ VALID" if validation.is_valid else "✗ INVALID"
            print(f"{stage_id:12} - {status}")
            if not validation.is_valid:
                print(f"             Error: {validation.error_message}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Stage Name Resolver CLI - Test and validate stage name resolution"
    )
    parser.add_argument(
        "--format",
        choices=["human", "json"],
        default="human",
        help="Output format (default: human)"
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Specific main_*.py files to validate"
    )
    parser.add_argument(
        "--test-resolution",
        action="store_true",
        help="Run stage resolution tests with sample files"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Test stage ID format validation"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="stage_name_resolver 1.2.11"
    )

    args = parser.parse_args()

    if args.validate:
        validate_stage_id_format(args)
    elif args.test_resolution:
        test_stage_resolution(args)
    elif args.files:
        validate_stage_files(args)
    else:
        # Default: show help
        parser.print_help()


if __name__ == "__main__":
    main()