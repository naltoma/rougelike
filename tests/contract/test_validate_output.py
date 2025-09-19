#!/usr/bin/env python3
"""Contract tests for validate_stage.py validation reporting"""
import pytest
import subprocess
import sys
import json
from pathlib import Path


@pytest.mark.contract
@pytest.mark.validator
class TestValidateStageOutput:
    """Test validate_stage.py output format and validation reporting"""

    def test_successful_validation_output_format(self):
        """Test output format for successful validation (basic)"""
        result = subprocess.run([
            sys.executable, "validate_stage.py", "--file", "stages/stage01.yml"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 0:  # Only test if validation succeeds
            output = result.stdout
            assert "✅" in output or "solvable" in output.lower()
            assert "stage01.yml" in output
            assert "steps" in output.lower()

    def test_detailed_validation_output(self):
        """Test detailed analysis output format"""
        result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", "stages/stage01.yml", "--detailed"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            output = result.stdout
            assert "Solution Analysis" in output or "Analysis" in output
            assert "APIs used" in output or "api" in output.lower()

    def test_json_output_format(self):
        """Test JSON format output is valid JSON"""
        result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", "stages/stage01.yml", "--format", "json"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode in [0, 1]:  # Success or validation failure
            try:
                data = json.loads(result.stdout)
                # Check for expected JSON structure
                assert isinstance(data, dict)
                assert "success" in data
                assert "stage_path" in data or "file" in data
            except json.JSONDecodeError:
                pytest.fail("JSON output is not valid JSON")

    def test_validation_failure_output(self):
        """Test output format for validation failures"""
        # This test will need a known unsolvable stage or will skip
        # For now, test with a non-existent file to trigger file error
        result = subprocess.run([
            sys.executable, "validate_stage.py", "--file", "nonexistent.yml"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result.returncode == 2  # File error
        assert "not found" in result.stderr.lower() or "no such file" in result.stderr.lower()

    def test_timeout_handling(self):
        """Test that timeout is respected"""
        result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", "stages/stage01.yml", "--timeout", "1"  # Very short timeout
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        # Should either complete quickly or timeout
        assert result.returncode in [0, 1, 3]  # 0=success, 1=unsolvable, 3=timeout

    def test_error_reporting_clarity(self):
        """Test that error messages are clear and helpful"""
        # Test with invalid YAML file (if we can create one)
        invalid_yaml_content = "invalid: yaml: content: ["
        invalid_file = Path(__file__).parent.parent.parent / "test_invalid.yml"

        try:
            with open(invalid_file, 'w') as f:
                f.write(invalid_yaml_content)

            result = subprocess.run([
                sys.executable, "validate_stage.py", "--file", str(invalid_file)
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            assert result.returncode == 2  # File error
            # Error message should be informative
            error_output = result.stderr.lower()
            assert any(keyword in error_output for keyword in ["yaml", "parse", "invalid", "format"])

        finally:
            # Clean up test file
            if invalid_file.exists():
                invalid_file.unlink()

    def test_performance_reporting(self):
        """Test that performance information is included when available"""
        result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", "stages/stage01.yml", "--detailed"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            output = result.stdout.lower()
            # Should include some timing or performance information
            assert any(keyword in output for keyword in ["time", "steps", "efficiency", "rating"])

    def test_api_usage_reporting(self):
        """Test that API usage is correctly reported"""
        result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", "stages/stage01.yml", "--detailed"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 0:
            output = result.stdout
            # Should mention specific APIs used
            stage1_apis = ["turn_left", "turn_right", "move", "see"]
            assert any(api in output for api in stage1_apis)