"""
Integration test for dynamic stage name display functionality.
Based on quickstart scenario 1: Dynamic Stage Name Resolution.
"""

import unittest
import tempfile
import os
import sys
from unittest.mock import patch, MagicMock

# Add engine path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


class TestStageNameDisplay(unittest.TestCase):
    """Integration tests for dynamic stage name display based on quickstart scenarios."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def create_main_file(self, stage_id: str) -> str:
        """Create a main_*.py file with specified STAGE_ID."""
        file_path = os.path.join(self.temp_dir, f"main_{stage_id}.py")
        content = f'''#!/usr/bin/env python3
"""
Python初学者向けローグライク演習フレームワーク
メインエントリーポイント
"""

# ステージ設定
STAGE_ID = "{stage_id}"
STUDENT_ID = "123456A"

def solve():
    pass

if __name__ == "__main__":
    pass
'''
        with open(file_path, 'w') as f:
            f.write(content)
        return file_path

    @patch('pygame.display.set_mode')
    @patch('pygame.font.Font')
    def test_stage_name_display_integration(self, mock_font, mock_display):
        """
        Integration test: GUI shows correct stage name from STAGE_ID variable.

        Scenario from quickstart.md:
        1. Setup: Ensure main_stage09.py has STAGE_ID = "stage09"
        2. Action: Launch GUI
        3. Verify: Left-upper corner shows "Stage: stage09"
        """
        # Arrange
        from engine.gui_enhancement.stage_name_resolver import StageNameResolver
        from engine.renderer import GuiRenderer

        stage09_file = self.create_main_file("stage09")
        resolver = StageNameResolver()

        # Mock pygame components
        mock_surface = MagicMock()
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_font_instance.render.return_value = mock_surface
        mock_display.return_value = mock_surface

        # Act - Resolve stage name
        resolution = resolver.resolve_stage_name(stage09_file)

        # Assert - Should resolve to correct stage name
        self.assertEqual(resolution.stage_id, "stage09")
        self.assertEqual(resolution.resolved_name, "Stage: stage09")

        # Additional assertion for GUI integration
        # (This will be implemented when GuiRenderer is enhanced)
        self.assertTrue(resolution.resolved_name.startswith("Stage:"))

    @patch('pygame.display.set_mode')
    @patch('pygame.font.Font')
    def test_stage_name_change_integration(self, mock_font, mock_display):
        """
        Integration test: Stage name updates when STAGE_ID changes.

        Scenario from quickstart.md:
        4. Modify: Change STAGE_ID to "stage05" in main_stage09.py
        5. Rerun: Launch GUI again
        6. Verify: Left-upper corner now shows "Stage: stage05"
        """
        # Arrange
        from engine.gui_enhancement.stage_name_resolver import StageNameResolver

        # Create initial file with stage09
        main_file = self.create_main_file("stage09")
        resolver = StageNameResolver()

        # Mock pygame components
        mock_surface = MagicMock()
        mock_font_instance = MagicMock()
        mock_font.return_value = mock_font_instance
        mock_font_instance.render.return_value = mock_surface
        mock_display.return_value = mock_surface

        # Act 1 - First resolution
        first_resolution = resolver.resolve_stage_name(main_file)

        # Modify file to have different STAGE_ID
        modified_content = '''#!/usr/bin/env python3
"""Modified main file"""

# ステージ設定
STAGE_ID = "stage05"
STUDENT_ID = "123456A"

def solve():
    pass
'''
        with open(main_file, 'w') as f:
            f.write(modified_content)

        # Clear cache to ensure re-reading
        resolver.clear_cache()

        # Act 2 - Second resolution after modification
        second_resolution = resolver.resolve_stage_name(main_file)

        # Assert - Should show updated stage name
        self.assertEqual(first_resolution.stage_id, "stage09")
        self.assertEqual(second_resolution.stage_id, "stage05")
        self.assertEqual(second_resolution.resolved_name, "Stage: stage05")

    def test_multiple_stage_files_integration(self):
        """
        Integration test: Different main_*.py files show different stage names.
        """
        # Arrange
        from engine.gui_enhancement.stage_name_resolver import StageNameResolver

        stage01_file = self.create_main_file("stage01")
        stage09_file = self.create_main_file("stage09")
        resolver = StageNameResolver()

        # Act
        stage01_resolution = resolver.resolve_stage_name(stage01_file)
        stage09_resolution = resolver.resolve_stage_name(stage09_file)

        # Assert
        self.assertEqual(stage01_resolution.stage_id, "stage01")
        self.assertEqual(stage01_resolution.resolved_name, "Stage: stage01")
        self.assertEqual(stage09_resolution.stage_id, "stage09")
        self.assertEqual(stage09_resolution.resolved_name, "Stage: stage09")

    def test_stage_name_fallback_integration(self):
        """
        Integration test: Missing STAGE_ID shows fallback display.
        """
        # Arrange
        from engine.gui_enhancement.stage_name_resolver import StageNameResolver

        # Create file without STAGE_ID
        file_path = os.path.join(self.temp_dir, "main_no_stage.py")
        content = '''#!/usr/bin/env python3
"""Main file without STAGE_ID"""

STUDENT_ID = "123456A"

def solve():
    pass
'''
        with open(file_path, 'w') as f:
            f.write(content)

        resolver = StageNameResolver()

        # Act & Assert - Should handle missing STAGE_ID gracefully
        with self.assertRaises(AttributeError):
            resolver.resolve_stage_name(file_path)


if __name__ == '__main__':
    unittest.main()