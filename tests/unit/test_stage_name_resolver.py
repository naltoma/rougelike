"""
Unit tests for StageNameResolver implementation.
Tests dynamic stage ID resolution and validation logic.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.gui_enhancement.stage_name_resolver import StageNameResolver
from engine.gui_enhancement.data_types import StageResolution, ValidationResult


class TestStageNameResolverUnit(unittest.TestCase):
    """Unit tests for StageNameResolver implementation."""

    def setUp(self):
        """Set up test instance and temp directory."""
        self.resolver = StageNameResolver()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_test_file(self, filename: str, content: str) -> str:
        """Helper to create test files."""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path

    def test_init_creates_empty_cache(self):
        """Test initialization creates empty cache."""
        self.assertEqual(len(self.resolver.cache), 0)

    def test_resolve_stage_name_valid_file(self):
        """Test resolving stage name from valid file."""
        content = '''#!/usr/bin/env python3
"""Test stage file"""

STAGE_ID = "stage05"
STUDENT_ID = "123456A"

def solve():
    pass
'''
        file_path = self.create_test_file("main_stage05.py", content)

        result = self.resolver.resolve_stage_name(file_path)

        self.assertIsInstance(result, StageResolution)
        self.assertEqual(result.file_path, file_path)
        self.assertEqual(result.stage_id, "stage05")
        self.assertEqual(result.resolved_name, "Stage 05")
        self.assertFalse(result.is_cached)

    def test_resolve_stage_name_caching(self):
        """Test caching behavior for repeated calls."""
        content = '''STAGE_ID = "stage01"'''
        file_path = self.create_test_file("main_stage01.py", content)

        # First call - not cached
        result1 = self.resolver.resolve_stage_name(file_path)
        self.assertFalse(result1.is_cached)

        # Second call - cached
        result2 = self.resolver.resolve_stage_name(file_path)
        self.assertTrue(result2.is_cached)
        self.assertEqual(result1.stage_id, result2.stage_id)
        self.assertEqual(result1.resolved_name, result2.resolved_name)

    def test_resolve_stage_name_missing_stage_id(self):
        """Test handling file without STAGE_ID."""
        content = '''#!/usr/bin/env python3
"""Test file without STAGE_ID"""

STUDENT_ID = "123456A"

def solve():
    pass
'''
        file_path = self.create_test_file("main_nostageid.py", content)

        result = self.resolver.resolve_stage_name(file_path)

        self.assertEqual(result.stage_id, "unknown")
        self.assertEqual(result.resolved_name, "Unknown Stage")
        self.assertFalse(result.is_cached)

    def test_resolve_stage_name_nonexistent_file(self):
        """Test handling nonexistent file."""
        nonexistent_path = os.path.join(self.temp_dir, "nonexistent.py")

        result = self.resolver.resolve_stage_name(nonexistent_path)

        self.assertEqual(result.stage_id, "unknown")
        self.assertEqual(result.resolved_name, "Unknown Stage")
        self.assertEqual(result.file_path, nonexistent_path)

    def test_resolve_stage_name_invalid_python_syntax(self):
        """Test handling file with invalid Python syntax."""
        content = '''
STAGE_ID = "stage01"
invalid python syntax here !!!
'''
        file_path = self.create_test_file("main_invalid.py", content)

        result = self.resolver.resolve_stage_name(file_path)

        self.assertEqual(result.stage_id, "unknown")
        self.assertEqual(result.resolved_name, "Unknown Stage")

    def test_validate_stage_id_valid_formats(self):
        """Test validation of valid stage ID formats."""
        valid_ids = [
            "stage01",
            "stage09",
            "stage10",
            "stage99"
        ]

        for stage_id in valid_ids:
            result = self.resolver.validate_stage_id(stage_id)
            self.assertIsInstance(result, ValidationResult)
            self.assertTrue(result.is_valid, f"Expected {stage_id} to be valid")
            self.assertIsNone(result.error_message)

    def test_validate_stage_id_invalid_formats(self):
        """Test validation of invalid stage ID formats."""
        invalid_cases = [
            ("stage1", "Stage ID must be in format 'stageXX' where XX is a two-digit number (01-99)"),
            ("stage001", "Stage ID must be in format 'stageXX' where XX is a two-digit number (01-99)"),
            ("stageAB", "Stage ID must be in format 'stageXX' where XX is a two-digit number (01-99)"),
            ("level01", "Stage ID must be in format 'stageXX' where XX is a two-digit number (01-99)"),
            ("stage", "Stage ID must be in format 'stageXX' where XX is a two-digit number (01-99)"),
            ("", "Stage ID cannot be empty"),
            ("stage00", "Stage number must be between 01 and 99"),
            ("stage100", "Stage ID must be in format 'stageXX' where XX is a two-digit number (01-99)"),
        ]

        for stage_id, expected_error in invalid_cases:
            result = self.resolver.validate_stage_id(stage_id)
            self.assertFalse(result.is_valid, f"Expected {stage_id} to be invalid")
            self.assertEqual(result.error_message, expected_error)

    def test_format_stage_name_standard_format(self):
        """Test stage name formatting for standard IDs."""
        test_cases = [
            ("stage01", "Stage 01"),
            ("stage09", "Stage 09"),
            ("stage10", "Stage 10"),
            ("stage99", "Stage 99"),
        ]

        for stage_id, expected_name in test_cases:
            result = self.resolver._format_stage_name(stage_id)
            self.assertEqual(result, expected_name)

    def test_format_stage_name_unknown_format(self):
        """Test stage name formatting for unknown/invalid IDs."""
        unknown_cases = [
            "unknown",
            "invalid_format",
            "stage1",
            "",
        ]

        for stage_id in unknown_cases:
            result = self.resolver._format_stage_name(stage_id)
            self.assertEqual(result, "Unknown Stage")

    def test_cache_independence_across_files(self):
        """Test cache works independently for different files."""
        content1 = '''STAGE_ID = "stage01"'''
        content2 = '''STAGE_ID = "stage02"'''

        file1 = self.create_test_file("main_stage01.py", content1)
        file2 = self.create_test_file("main_stage02.py", content2)

        # Resolve both files
        result1 = self.resolver.resolve_stage_name(file1)
        result2 = self.resolver.resolve_stage_name(file2)

        # Check cache has both
        self.assertEqual(len(self.resolver.cache), 2)
        self.assertIn(file1, self.resolver.cache)
        self.assertIn(file2, self.resolver.cache)

        # Verify cached results
        cached1 = self.resolver.resolve_stage_name(file1)
        cached2 = self.resolver.resolve_stage_name(file2)

        self.assertTrue(cached1.is_cached)
        self.assertTrue(cached2.is_cached)
        self.assertEqual(cached1.stage_id, "stage01")
        self.assertEqual(cached2.stage_id, "stage02")

    def test_clear_cache_removes_all_entries(self):
        """Test clear_cache removes all cached entries."""
        content = '''STAGE_ID = "stage01"'''
        file_path = self.create_test_file("main_stage01.py", content)

        # Cache a result
        self.resolver.resolve_stage_name(file_path)
        self.assertEqual(len(self.resolver.cache), 1)

        # Clear cache
        self.resolver.clear_cache()
        self.assertEqual(len(self.resolver.cache), 0)

        # Next resolution should not be cached
        result = self.resolver.resolve_stage_name(file_path)
        self.assertFalse(result.is_cached)

    def test_different_stage_id_variable_names(self):
        """Test handling of different variable names (should only find STAGE_ID)."""
        variations = [
            ('STAGEID = "stage01"', "unknown"),
            ('stage_id = "stage01"', "unknown"),
            ('Stage_ID = "stage01"', "unknown"),
            ('STAGE_ID = "stage01"', "stage01"),
        ]

        for content, expected_stage_id in variations:
            file_path = self.create_test_file(f"test_{expected_stage_id}.py", content)
            result = self.resolver.resolve_stage_name(file_path)
            self.assertEqual(result.stage_id, expected_stage_id)

    def test_stage_id_with_different_quote_styles(self):
        """Test STAGE_ID with different quote styles."""
        quote_variations = [
            'STAGE_ID = "stage01"',
            "STAGE_ID = 'stage01'",
            'STAGE_ID = """stage01"""',
            "STAGE_ID = '''stage01'''",
        ]

        for content in quote_variations:
            file_path = self.create_test_file(f"test_quotes.py", content)
            result = self.resolver.resolve_stage_name(file_path)
            self.assertEqual(result.stage_id, "stage01")
            # Clear cache for next iteration
            self.resolver.clear_cache()

    def test_stage_id_as_non_string_value(self):
        """Test STAGE_ID with non-string values."""
        non_string_cases = [
            'STAGE_ID = 1',
            'STAGE_ID = ["stage01"]',
            'STAGE_ID = {"stage": "01"}',
            'STAGE_ID = None',
        ]

        for content in non_string_cases:
            file_path = self.create_test_file(f"test_nonstring.py", content)
            result = self.resolver.resolve_stage_name(file_path)
            self.assertEqual(result.stage_id, "unknown")
            # Clear cache for next iteration
            self.resolver.clear_cache()

    def test_complex_file_content_extraction(self):
        """Test extraction from complex file with multiple variables."""
        content = '''#!/usr/bin/env python3
"""
Complex test file with multiple variables
"""

import sys
from pathlib import Path

STUDENT_ID = "123456A"
STAGE_ID = "stage07"  # This should be found
OTHER_VAR = "stage99"  # This should be ignored
STAGE_NAME = "Test Stage"

class GameSolver:
    def __init__(self):
        self.stage = "stage08"  # This should be ignored

    def solve(self):
        pass

def main():
    solver = GameSolver()
    solver.solve()

if __name__ == "__main__":
    main()
'''
        file_path = self.create_test_file("main_complex.py", content)
        result = self.resolver.resolve_stage_name(file_path)

        self.assertEqual(result.stage_id, "stage07")
        self.assertEqual(result.resolved_name, "Stage 07")

    def test_error_handling_import_error(self):
        """Test handling of files that cause import errors."""
        content = '''
import nonexistent_module  # This will cause ImportError
STAGE_ID = "stage01"
'''
        file_path = self.create_test_file("main_import_error.py", content)
        result = self.resolver.resolve_stage_name(file_path)

        self.assertEqual(result.stage_id, "unknown")
        self.assertEqual(result.resolved_name, "Unknown Stage")

    def test_state_isolation_between_instances(self):
        """Test that different resolver instances don't share cache."""
        resolver1 = StageNameResolver()
        resolver2 = StageNameResolver()

        content = '''STAGE_ID = "stage01"'''
        file_path = self.create_test_file("main_isolation.py", content)

        # Cache in first instance
        result1 = resolver1.resolve_stage_name(file_path)
        self.assertFalse(result1.is_cached)

        # Should not be cached in second instance
        result2 = resolver2.resolve_stage_name(file_path)
        self.assertFalse(result2.is_cached)

        # Cache check in first instance
        cached1 = resolver1.resolve_stage_name(file_path)
        self.assertTrue(cached1.is_cached)


if __name__ == '__main__':
    unittest.main()