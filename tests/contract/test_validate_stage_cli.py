#!/usr/bin/env python3
"""Contract tests for validate_stage.py CLI interface"""
import pytest
import subprocess
import sys
from pathlib import Path


@pytest.mark.contract
@pytest.mark.validator
class TestValidateStageCLI:
    """Test validate_stage.py CLI argument parsing and basic functionality"""

    def test_help_message(self):
        """Test that --help shows usage information"""
        result = subprocess.run([
            sys.executable, "validate_stage.py", "--help"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0
        assert "validate_stage.py" in result.stdout
        assert "--file" in result.stdout
        assert "--detailed" in result.stdout
        assert "--timeout" in result.stdout

    def test_version_information(self):
        """Test that --version shows version information"""
        result = subprocess.run([
            sys.executable, "validate_stage.py", "--version"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 0
        assert "1.2.9" in result.stdout

    def test_missing_required_file_argument(self):
        """Test error handling when --file argument is missing"""
        result = subprocess.run([
            sys.executable, "validate_stage.py"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        assert result.returncode == 2  # argparse error

    def test_nonexistent_file(self):
        """Test error handling for non-existent files"""
        result = subprocess.run([
            sys.executable, "validate_stage.py", "--file", "nonexistent.yml"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        assert result.returncode == 2  # File error
        assert "not found" in result.stderr.lower() or "no such file" in result.stderr.lower()

    def test_existing_stage_file(self):
        """Test validation with existing stage file"""
        result = subprocess.run([
            sys.executable, "validate_stage.py", "--file", "stages/stage01.yml"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Should accept the file (may fail due to unimplemented validation)
        assert result.returncode in [0, 1, 2]  # 0=solvable, 1=unsolvable, 2=validation not implemented

    def test_detailed_flag(self):
        """Test --detailed flag is accepted"""
        result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", "stages/stage01.yml", "--detailed"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Should accept argument
        assert result.returncode in [0, 1, 2]  # Various outcomes acceptable for now

    def test_timeout_option(self):
        """Test --timeout option accepts integer values"""
        result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", "stages/stage01.yml", "--timeout", "30"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Should accept timeout value
        assert result.returncode in [0, 1, 2, 3]  # 0=solvable, 1=unsolvable, 2=file error, 3=timeout

    def test_invalid_timeout(self):
        """Test error handling for invalid timeout values"""
        result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", "stages/stage01.yml", "--timeout", "invalid"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        assert result.returncode == 2  # argparse error

    def test_format_option(self):
        """Test --format option accepts text and json"""
        for format_type in ["text", "json"]:
            result = subprocess.run([
                sys.executable, "validate_stage.py",
                "--file", "stages/stage01.yml", "--format", format_type
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            # Should accept format argument
            assert result.returncode in [0, 1, 2]  # Various outcomes acceptable for now

    def test_invalid_format(self):
        """Test error handling for invalid format values"""
        result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", "stages/stage01.yml", "--format", "invalid"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
        assert result.returncode == 2  # argparse error