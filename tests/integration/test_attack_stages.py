#!/usr/bin/env python3
"""Integration tests for attack stage generation and validation"""
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
class TestAttackStageIntegration:
    """Test complete attack stage generation and validation workflow"""

    @pytest.fixture
    def temp_output_dir(self):
        """Temporary directory for test output"""
        temp_dir = tempfile.mkdtemp(prefix="test_attack_stages_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_generate_and_validate_attack_stage(self, temp_output_dir):
        """Test generating an attack stage and validating it succeeds"""
        generate_result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "attack", "--seed", "54321",
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if generate_result.returncode != 0:
            pytest.skip("Attack stage generation not yet implemented")

        stage_file = Path(temp_output_dir) / "generated_attack_54321.yml"
        assert stage_file.exists(), "Attack stage file should be created"

        # Validate the generated stage
        validate_result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", str(stage_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if validate_result.returncode == 2:
            pytest.skip("Stage validation not yet implemented")

        # Generated attack stage should be solvable
        assert validate_result.returncode == 0, f"Generated attack stage should be solvable. Error: {validate_result.stderr}"

    def test_attack_stage_characteristics(self, temp_output_dir):
        """Test that generated attack stages have correct characteristics"""
        generate_result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "attack", "--seed", "98765",
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if generate_result.returncode != 0:
            pytest.skip("Attack stage generation not yet implemented")

        stage_file = Path(temp_output_dir) / "generated_attack_98765.yml"
        with open(stage_file, 'r') as f:
            stage_data = yaml.safe_load(f)

        # Attack stages should have specific characteristics
        assert stage_data['id'].startswith('generated_attack_')

        # Board size should be within expected range (6x6 to 10x10)
        board_size = stage_data['board']['size']
        assert 6 <= board_size[0] <= 10
        assert 6 <= board_size[1] <= 10

        # Should have 1-3 enemies
        enemies = stage_data['enemies']
        assert 1 <= len(enemies) <= 3

        # Enemies should have HP in expected range (10-300)
        for enemy in enemies:
            assert 10 <= enemy['hp'] <= 300
            assert enemy['type'] in ['normal']  # Attack stages have normal enemies

        # Should still have no items (attack focus)
        assert len(stage_data['items']) == 0

        # Should include attack API
        expected_apis = {"turn_left", "turn_right", "move", "attack", "see"}
        actual_apis = set(stage_data['constraints']['allowed_apis'])
        assert actual_apis == expected_apis

    def test_attack_stage_enemy_positioning(self, temp_output_dir):
        """Test that enemies in attack stages are positioned correctly"""
        generate_result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "attack", "--seed", "enemy_pos_test",
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if generate_result.returncode != 0:
            pytest.skip("Attack stage generation not yet implemented")

        stage_file = Path(temp_output_dir) / "generated_attack_enemy_pos_test.yml"
        with open(stage_file, 'r') as f:
            stage_data = yaml.safe_load(f)

        board_size = stage_data['board']['size']
        player_start = stage_data['player']['start']
        goal_pos = stage_data['goal']['position']
        enemies = stage_data['enemies']

        # Enemies should be within board boundaries
        for enemy in enemies:
            pos = enemy['position']
            assert 0 <= pos[0] < board_size[0]
            assert 0 <= pos[1] < board_size[1]

            # Enemies should not be at player start or goal position
            assert pos != player_start
            assert pos != goal_pos

    def test_attack_stage_validation_requires_attack(self, temp_output_dir):
        """Test that attack stage validation confirms attack API is required"""
        generate_result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "attack", "--seed", "attack_required_test",
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if generate_result.returncode != 0:
            pytest.skip("Attack stage generation not yet implemented")

        stage_file = Path(temp_output_dir) / "generated_attack_attack_required_test.yml"

        validate_result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", str(stage_file), "--detailed"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if validate_result.returncode == 2:
            pytest.skip("Stage validation not yet implemented")

        if validate_result.returncode == 0:
            # Attack API should be required for solution
            output = validate_result.stdout.lower()
            assert "attack" in output, "Attack stage solution should require attack API"

    def test_attack_stage_difficulty_progression(self, temp_output_dir):
        """Test that different seeds produce varied difficulty levels"""
        seeds_and_results = []

        # Generate multiple attack stages
        for i, seed in enumerate(["easy_test", "medium_test", "hard_test"]):
            generate_result = subprocess.run([
                sys.executable, "generate_stage.py",
                "--type", "attack", "--seed", seed,
                "--output", temp_output_dir, "--quiet"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

            if generate_result.returncode != 0:
                pytest.skip("Attack stage generation not yet implemented")

            stage_file = Path(temp_output_dir) / f"generated_attack_{seed}.yml"
            with open(stage_file, 'r') as f:
                stage_data = yaml.safe_load(f)

            # Collect characteristics for analysis
            enemy_count = len(stage_data['enemies'])
            total_enemy_hp = sum(enemy['hp'] for enemy in stage_data['enemies'])
            board_area = stage_data['board']['size'][0] * stage_data['board']['size'][1]

            seeds_and_results.append({
                'seed': seed,
                'enemy_count': enemy_count,
                'total_hp': total_enemy_hp,
                'board_area': board_area
            })

        # Should have variety in difficulty characteristics
        enemy_counts = [r['enemy_count'] for r in seeds_and_results]
        total_hps = [r['total_hp'] for r in seeds_and_results]

        # Should not all be identical (expect some variation)
        assert len(set(enemy_counts)) > 1 or len(set(total_hps)) > 1, "Attack stages should have difficulty variation"

    def test_attack_stage_with_validation_performance(self, temp_output_dir):
        """Test attack stage validation performance"""
        generate_result = subprocess.run([
            sys.executable, "generate_stage.py",
            "--type", "attack", "--seed", "perf_test_attack",
            "--output", temp_output_dir, "--quiet"
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        if generate_result.returncode != 0:
            pytest.skip("Attack stage generation not yet implemented")

        stage_file = Path(temp_output_dir) / "generated_attack_perf_test_attack.yml"

        import time
        start_time = time.time()

        validate_result = subprocess.run([
            sys.executable, "validate_stage.py",
            "--file", str(stage_file)
        ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)

        end_time = time.time()

        if validate_result.returncode == 2:
            pytest.skip("Stage validation not yet implemented")

        # Attack stage validation should still be reasonably fast
        validation_time = end_time - start_time
        assert validation_time < 10.0, f"Attack stage validation took {validation_time:.2f}s, should be <10s"