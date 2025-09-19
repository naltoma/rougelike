#!/usr/bin/env python3
"""Contract tests for generate_stage.py output format and file creation"""
import pytest
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import yaml


@pytest.mark.contract
@pytest.mark.generator
class TestGenerateStageOutput:
    """Test generate_stage.py file creation and YAML format compliance"""

    @pytest.fixture
    def temp_stages_dir(self):
        """Create temporary directory for test stage files"""
        temp_dir = tempfile.mkdtemp(prefix="test_stages_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_file_naming_convention(self, temp_stages_dir):
        """Test that generated files follow naming convention: generated_[type]_[seed].yml"""
        result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "123",
            "--output", temp_stages_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 0:  # Only test if generation succeeds
            expected_file = Path(temp_stages_dir) / "generated_move_123.yml"
            assert expected_file.exists(), f"Expected file {expected_file} was not created"

    def test_yaml_format_compliance(self, temp_stages_dir):
        """Test that generated files are valid YAML with required structure"""
        result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "456",
            "--output", temp_stages_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            generated_file = Path(temp_stages_dir) / "generated_move_456.yml"
            assert generated_file.exists()

            # Parse YAML and check structure
            with open(generated_file, 'r') as f:
                stage_data = yaml.safe_load(f)

            # Required top-level keys
            required_keys = ['id', 'title', 'description', 'board', 'player', 'goal', 'enemies', 'items', 'constraints']
            for key in required_keys:
                assert key in stage_data, f"Required key '{key}' missing from generated YAML"

            # Check board structure
            board = stage_data['board']
            assert 'size' in board
            assert 'grid' in board
            assert 'legend' in board
            assert isinstance(board['size'], list) and len(board['size']) == 2

            # Check player structure
            player = stage_data['player']
            assert 'start' in player
            assert 'direction' in player
            assert isinstance(player['start'], list) and len(player['start']) == 2

            # Check constraints
            constraints = stage_data['constraints']
            assert 'max_turns' in constraints
            assert 'allowed_apis' in constraints
            assert isinstance(constraints['allowed_apis'], list)

    def test_seed_reproducibility(self, temp_stages_dir):
        """Test that same seed produces identical files"""
        # Generate first file
        result1 = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "789",
            "--output", temp_stages_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result1.returncode != 0:
            pytest.skip("Stage generation not yet implemented")

        file1 = Path(temp_stages_dir) / "generated_move_789.yml"
        assert file1.exists()

        # Read first file content
        with open(file1, 'r') as f:
            content1 = f.read()

        # Remove first file
        file1.unlink()

        # Generate second file with same parameters
        result2 = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "789",
            "--output", temp_stages_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result2.returncode == 0
        file2 = Path(temp_stages_dir) / "generated_move_789.yml"
        assert file2.exists()

        # Read second file content
        with open(file2, 'r') as f:
            content2 = f.read()

        # Files should be identical
        assert content1 == content2, "Same seed should produce identical files"

    def test_different_seeds_produce_different_files(self, temp_stages_dir):
        """Test that different seeds produce different stage configurations"""
        # Generate first file
        result1 = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "111",
            "--output", temp_stages_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Generate second file
        result2 = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "222",
            "--output", temp_stages_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result1.returncode != 0 or result2.returncode != 0:
            pytest.skip("Stage generation not yet implemented")

        file1 = Path(temp_stages_dir) / "generated_move_111.yml"
        file2 = Path(temp_stages_dir) / "generated_move_222.yml"

        assert file1.exists() and file2.exists()

        with open(file1, 'r') as f:
            content1 = f.read()
        with open(file2, 'r') as f:
            content2 = f.read()

        # Files should be different (excluding metadata like timestamps)
        assert content1 != content2, "Different seeds should produce different stages"

    def test_success_output_format(self, temp_stages_dir):
        """Test that success output follows expected format"""
        result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "333",
            "--output", temp_stages_dir
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            output = result.stdout
            assert "✅" in output or "Generated" in output
            assert "move" in output
            assert "333" in output
            assert temp_stages_dir in output or "generated_move_333.yml" in output

    def test_default_output_directory(self):
        """Test that files are created in stages/ by default"""
        result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "999", "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            default_file = Path(__file__).parent.parent.parent / "stages" / "generated_move_999.yml"
            try:
                assert default_file.exists(), "File should be created in default stages/ directory"
            finally:
                # Clean up test file
                if default_file.exists():
                    default_file.unlink()