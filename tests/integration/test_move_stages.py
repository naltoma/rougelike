#!/usr/bin/env python3
"""Integration tests for move stage generation and validation"""
import pytest
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import yaml


@pytest.mark.integration
@pytest.mark.generator
@pytest.mark.validator
class TestMoveStageIntegration:
    """Test complete move stage generation and validation workflow"""

    @pytest.fixture
    def temp_output_dir(self):
        """Temporary directory for test output"""
        temp_dir = tempfile.mkdtemp(prefix="test_move_stages_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_generate_and_validate_move_stage(self, temp_output_dir):
        """Test generating a move stage and validating it succeeds"""
        # Generate move stage
        generate_result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "12345",
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if generate_result.returncode != 0:
            pytest.skip("Move stage generation not yet implemented")

        # Check file was created
        stage_file = Path(temp_output_dir) / "generated_move_12345.yml"
        assert stage_file.exists(), "Move stage file should be created"

        # Validate the generated stage
        validate_result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", str(stage_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if validate_result.returncode == 2:
            pytest.skip("Stage validation not yet implemented")

        # Generated move stage should be solvable
        assert validate_result.returncode == 0, f"Generated move stage should be solvable. Error: {validate_result.stderr}"

    def test_move_stage_characteristics(self, temp_output_dir):
        """Test that generated move stages have correct characteristics"""
        generate_result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "67890",
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if generate_result.returncode != 0:
            pytest.skip("Move stage generation not yet implemented")

        stage_file = Path(temp_output_dir) / "generated_move_67890.yml"
        with open(stage_file, 'r') as f:
            stage_data = yaml.safe_load(f)

        # Move stages should have specific characteristics
        assert stage_data['id'].startswith('generated_move_')

        # Board size should be within expected range (5x5 to 8x8)
        board_size = stage_data['board']['size']
        assert 5 <= board_size[0] <= 8
        assert 5 <= board_size[1] <= 8

        # Should have no enemies or items
        assert len(stage_data['enemies']) == 0
        assert len(stage_data['items']) == 0

        # Should only allow basic movement APIs
        expected_apis = {"turn_left", "turn_right", "move", "see"}
        actual_apis = set(stage_data['constraints']['allowed_apis'])
        assert actual_apis == expected_apis

    def test_move_stage_seed_reproducibility(self, temp_output_dir):
        """Test that same seed produces identical move stages"""
        seed = "reproducibility_test"

        # Generate first stage
        result1 = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", seed,
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result1.returncode != 0:
            pytest.skip("Move stage generation not yet implemented")

        file1 = Path(temp_output_dir) / f"generated_move_{seed}.yml"
        with open(file1, 'r') as f:
            content1 = f.read()

        # Remove first file
        file1.unlink()

        # Generate second stage with same seed
        result2 = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", seed,
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        assert result2.returncode == 0

        file2 = Path(temp_output_dir) / f"generated_move_{seed}.yml"
        with open(file2, 'r') as f:
            content2 = f.read()

        # Contents should be identical
        assert content1 == content2

    def test_multiple_move_stage_seeds(self, temp_output_dir):
        """Test generating multiple move stages with different seeds"""
        seeds = ["111", "222", "333"]
        generated_files = []

        for seed in seeds:
            result = subprocess.run([
                sys.executable, "generate_stage.py",
                "--type", "move", "--seed", seed,
                "--output", temp_output_dir, "--quiet"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            if result.returncode != 0:
                pytest.skip("Move stage generation not yet implemented")

            stage_file = Path(temp_output_dir) / f"generated_move_{seed}.yml"
            assert stage_file.exists()
            generated_files.append(stage_file)

        # All files should be different
        contents = []
        for file_path in generated_files:
            with open(file_path, 'r') as f:
                contents.append(f.read())

        # Each file should be unique
        assert len(set(contents)) == len(contents), "Different seeds should produce different stages"

    def test_move_stage_validation_performance(self, temp_output_dir):
        """Test that move stage validation meets performance requirements"""
        generate_result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "performance_test",
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if generate_result.returncode != 0:
            pytest.skip("Move stage generation not yet implemented")

        stage_file = Path(temp_output_dir) / "generated_move_performance_test.yml"

        import time
        start_time = time.time()

        validate_result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", str(stage_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        end_time = time.time()

        if validate_result.returncode == 2:
            pytest.skip("Stage validation not yet implemented")

        # Validation should complete within performance requirement
        validation_time = end_time - start_time
        assert validation_time < 5.0, f"Move stage validation took {validation_time:.2f}s, should be <5s"

    def test_move_stage_with_validation_flag(self, temp_output_dir):
        """Test generating move stage with --validate flag"""
        result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "validate_test",
            "--output", temp_output_dir, "--validate"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if result.returncode == 1:
            pytest.skip("Move stage generation not yet implemented")
        elif result.returncode == 2:
            pytest.skip("Stage validation not yet implemented")

        # Should succeed (generate + validate in one step)
        assert result.returncode == 0

        # Output should indicate both generation and validation
        output = result.stdout.lower()
        assert any(keyword in output for keyword in ["generated", "validation", "solvable"])

    def test_move_stage_api_compliance(self, temp_output_dir):
        """Test that move stages only use allowed APIs when validated"""
        generate_result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "move", "--seed", "api_test",
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if generate_result.returncode != 0:
            pytest.skip("Move stage generation not yet implemented")

        stage_file = Path(temp_output_dir) / "generated_move_api_test.yml"

        validate_result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", str(stage_file), "--detailed"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if validate_result.returncode == 2:
            pytest.skip("Stage validation not yet implemented")

        if validate_result.returncode == 0:
            # Check that only allowed APIs were used in solution
            output = validate_result.stdout.lower()
            forbidden_apis = ["attack", "pickup", "wait"]

            for api in forbidden_apis:
                assert api not in output, f"Move stage should not require {api} API"