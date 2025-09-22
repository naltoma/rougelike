"""
Contract tests for StageNameResolver API
These tests MUST FAIL initially to follow TDD principles.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine.gui_enhancement.stage_name_resolver import StageNameResolver
from engine.gui_enhancement.data_types import StageResolution, ValidationResult


class TestStageNameResolverContract(unittest.TestCase):
    """Contract tests for StageNameResolver API based on yaml specification."""

    def setUp(self):
        """Set up test instance and temporary files."""
        self.resolver = StageNameResolver()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_temp_main_file(self, stage_id: str) -> str:
        """Create a temporary main_*.py file with STAGE_ID."""
        file_path = os.path.join(self.temp_dir, f"main_{stage_id}.py")
        content = f'''#!/usr/bin/env python3
"""Test main file"""

# Stage configuration
STAGE_ID = "{stage_id}"
STUDENT_ID = "123456A"

def solve():
    pass
'''
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path

    def test_resolve_stage_name_contract_valid_file(self):
        """Test resolve_stage_name contract: valid file returns StageResolution."""
        # Arrange
        file_path = self.create_temp_main_file("stage09")

        # Act
        result = self.resolver.resolve_stage_name(file_path)

        # Assert - Contract requirements
        self.assertIsInstance(result, StageResolution)
        self.assertEqual(result.stage_id, "stage09")
        self.assertEqual(result.file_path, file_path)
        self.assertIsInstance(result.resolved_name, str)
        self.assertIsInstance(result.is_cached, bool)

        # Stage name should be formatted correctly
        self.assertEqual(result.resolved_name, "Stage 09")

    def test_resolve_stage_name_contract_nonexistent_file(self):
        """Test resolve_stage_name contract: nonexistent file returns unknown stage."""
        # Arrange
        nonexistent_path = "/nonexistent/file.py"

        # Act
        result = self.resolver.resolve_stage_name(nonexistent_path)

        # Assert - Contract requirements
        self.assertIsInstance(result, StageResolution)
        self.assertEqual(result.stage_id, "unknown")
        self.assertEqual(result.resolved_name, "Unknown Stage")

    def test_resolve_stage_name_contract_missing_stage_id(self):
        """Test resolve_stage_name contract: missing STAGE_ID returns unknown stage."""
        # Arrange
        file_path = os.path.join(self.temp_dir, "main_no_stage.py")
        content = '''#!/usr/bin/env python3
"""Test main file without STAGE_ID"""

STUDENT_ID = "123456A"

def solve():
    pass
'''
        with open(file_path, 'w') as f:
            f.write(content)

        # Act
        result = self.resolver.resolve_stage_name(file_path)

        # Assert - Contract requirements
        self.assertIsInstance(result, StageResolution)
        self.assertEqual(result.stage_id, "unknown")
        self.assertEqual(result.resolved_name, "Unknown Stage")

    def test_validate_stage_id_contract_valid_format(self):
        """Test validate_stage_id contract: valid format returns ValidationResult."""
        # Arrange
        valid_stage_id = "stage09"

        # Act
        result = self.resolver.validate_stage_id(valid_stage_id)

        # Assert - Contract requirements
        self.assertIsInstance(result, ValidationResult)
        self.assertTrue(result.is_valid)
        self.assertEqual(result.stage_id, valid_stage_id)
        self.assertIsNone(result.error_message)

    def test_validate_stage_id_contract_invalid_format(self):
        """Test validate_stage_id contract: invalid format returns ValidationResult with error."""
        # Arrange
        invalid_stage_id = "invalid_stage"

        # Act
        result = self.resolver.validate_stage_id(invalid_stage_id)

        # Assert - Contract requirements
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.is_valid)
        self.assertEqual(result.stage_id, invalid_stage_id)
        self.assertIsNotNone(result.error_message)

    def test_get_display_name_contract(self):
        """Test get_display_name contract: returns formatted string."""
        # Arrange
        stage_id = "stage09"

        # Act
        result = self.resolver.get_display_name(stage_id)

        # Assert - Contract requirements
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Stage: stage09")

    def test_clear_cache_contract(self):
        """Test clear_cache contract: returns None and clears cache."""
        # Arrange
        file_path = self.create_temp_main_file("stage01")
        # First resolution to populate cache
        self.resolver.resolve_stage_name(file_path)

        # Act
        result = self.resolver.clear_cache()

        # Assert - Contract requirements
        self.assertIsNone(result)

        # Verify cache is cleared by checking is_cached flag
        new_result = self.resolver.resolve_stage_name(file_path)
        self.assertFalse(new_result.is_cached)

    def test_caching_behavior_contract(self):
        """Test caching behavior: second call should be cached."""
        # Arrange
        file_path = self.create_temp_main_file("stage05")

        # Act
        first_result = self.resolver.resolve_stage_name(file_path)
        second_result = self.resolver.resolve_stage_name(file_path)

        # Assert - Contract requirements
        self.assertFalse(first_result.is_cached)
        self.assertTrue(second_result.is_cached)
        self.assertEqual(first_result.stage_id, second_result.stage_id)


if __name__ == '__main__':
    unittest.main()