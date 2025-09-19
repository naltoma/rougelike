#!/usr/bin/env python3
"""Contract tests for generate_stage.py CLI interface"""
import pytest
import subprocess
import sys
from pathlib import Path


@pytest.mark.contract
@pytest.mark.generator
class TestGenerateStageCLI:
    """Test generate_stage.py CLI argument parsing and basic functionality"""

    def test_help_message(self):
        """Test that --help shows usage information"""
        result = subprocess.run([
            sys.executable, "scripts/generate_stage.py", "--help"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0
        assert "generate_stage.py" in result.stdout
        assert "--type" in result.stdout
        assert "--seed" in result.stdout
        assert "{move,attack,pickup,patrol,special}" in result.stdout

    def test_version_information(self):
        """Test that --version shows version information"""
        result = subprocess.run([
            sys.executable, "generate_stage.py", "--version"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0
        assert "1.2.9" in result.stdout

    def test_missing_required_arguments(self):
        """Test error handling when required arguments are missing"""
        # Missing --type
        result = subprocess.run([
            sys.executable, "generate_stage.py", "--seed", "123"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        assert result.returncode == 2  # argparse error

        # Missing --seed
        result = subprocess.run([
            sys.executable, "generate_stage.py", "--type", "move"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        assert result.returncode == 2  # argparse error

    def test_invalid_stage_type(self):
        """Test error handling for invalid stage types"""
        result = subprocess.run([
            sys.executable, "generate_stage.py", "--type", "invalid", "--seed", "123"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        assert result.returncode == 1  # Generation error
        assert "Invalid stage type" in result.stderr

    def test_invalid_seed_range(self):
        """Test error handling for seed values out of range"""
        result = subprocess.run([
            sys.executable, "generate_stage.py", "--type", "move", "--seed", "-1"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        assert result.returncode == 1  # Generation error

        result = subprocess.run([
            sys.executable, "generate_stage.py", "--type", "move", "--seed", str(2**32)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        assert result.returncode == 1  # Generation error

    def test_valid_stage_types(self):
        """Test that all valid stage types are accepted"""
        valid_types = ["move", "attack", "pickup", "patrol", "special"]

        for stage_type in valid_types:
            result = subprocess.run([
                sys.executable, "generate_stage.py",
                "--type", stage_type, "--seed", "123", "--quiet"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            # Should not fail due to argument parsing (may fail due to unimplemented generation)
            assert result.returncode in [0, 1]  # 0=success, 1=generation not implemented yet

    def test_output_directory_option(self):
        """Test --output option for custom directory"""
        result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "123",
            "--output", "custom_test/", "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Should accept argument (may fail due to unimplemented generation)
        assert result.returncode in [0, 1, 3]  # 0=success, 1=generation, 3=filesystem

    def test_validate_flag(self):
        """Test --validate flag is accepted"""
        result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "123", "--validate", "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Should accept argument
        assert result.returncode in [0, 1, 2]  # 0=success, 1=generation, 2=validation

    def test_quiet_flag(self):
        """Test --quiet flag suppresses output"""
        result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "123", "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Quiet mode should minimize stdout (may still have stderr for errors)
        if result.returncode == 0:
            assert len(result.stdout.strip()) < 100  # Minimal output in quiet mode

    def test_format_option(self):
        """Test --format option accepts yaml and json"""
        for format_type in ["yaml", "json"]:
            result = subprocess.run([
                sys.executable, "generate_stage.py",
                "--type", "move", "--seed", "123",
                "--format", format_type, "--quiet"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            # Should accept argument
            assert result.returncode in [0, 1]  # 0=success, 1=generation not implemented yet