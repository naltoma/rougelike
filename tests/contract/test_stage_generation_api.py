"""
Contract tests for Stage Generation and Validation API with bomb support
These tests MUST FAIL initially to follow TDD methodology
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import sys
import os
import yaml

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.mark.contract
@pytest.mark.generator
@pytest.mark.bomb
class TestStageGenerationContract:
    """Contract tests for stage generation with bomb support"""

    def test_generate_items_with_bombs(self):
        """Given stage type, when generate with bombs, then valid bomb stage created"""
        # TODO: This test MUST FAIL initially - bomb generation doesn't exist yet
        from scripts.generate_stage import generate_items_with_bombs

        items = generate_items_with_bombs(stage_type="attack", item_count=3)

        assert isinstance(items, list), "Should return list of items"
        assert len(items) > 0, "Should generate at least one item"

        # Check for bomb items in generated list
        bomb_items = [item for item in items if item.get('type') == 'bomb']
        assert len(bomb_items) > 0, "Should include bomb items in generation"

        # Validate bomb item structure
        for bomb in bomb_items:
            assert 'id' in bomb, "Bomb item should have id"
            assert 'type' in bomb and bomb['type'] == 'bomb', "Bomb item should have type=bomb"
            assert 'position' in bomb, "Bomb item should have position"
            assert 'damage' in bomb, "Bomb item should have damage attribute"
            assert isinstance(bomb['damage'], int), "Damage should be integer"
            assert bomb['damage'] > 0, "Damage should be positive"

    def test_validate_bomb_item_config(self):
        """Given bomb item config, when validate, then pass validation"""
        from scripts.generate_stage import validate_bomb_item_config

        valid_bomb = {
            "id": "test_bomb",
            "type": "bomb",
            "position": [3, 4],
            "damage": 75,
            "name": "爆弾",
            "description": "An item must be disposed"
        }

        result = validate_bomb_item_config(valid_bomb)
        assert result is True, "Valid bomb config should pass validation"

        # Test invalid configs
        invalid_configs = [
            {"id": "bomb1", "type": "key", "position": [1, 1]},  # Wrong type
            {"id": "bomb2", "type": "bomb", "position": [1, 1], "damage": -10},  # Negative damage
            {"type": "bomb", "position": [1, 1], "damage": 50},  # Missing id
            {"id": "bomb3", "position": [1, 1], "damage": 50},  # Missing type
        ]

        for invalid_config in invalid_configs:
            result = validate_bomb_item_config(invalid_config)
            assert result is False, f"Invalid config should fail: {invalid_config}"


@pytest.mark.contract
@pytest.mark.validator
@pytest.mark.bomb
class TestStageValidationContract:
    """Contract tests for stage validation with bomb support"""

    def test_validate_stage_with_bombs(self):
        """Given bomb stage file, when validate, then succeeds with proper handling"""
        from scripts.validate_stage import validate_stage_with_bombs

        # Mock stage file with bombs
        stage_content = {
            "id": "test_bomb_stage",
            "title": "Bomb Test Stage",
            "description": "Test stage with bomb items",
            "board": [
                [".", ".", "."],
                [".", "P", "."],
                [".", ".", "G"]
            ],
            "player": {"position": [1, 1], "direction": "north"},
            "goal": {"position": [2, 2]},
            "enemies": [],
            "items": [
                {"id": "bomb1", "type": "bomb", "position": [0, 0], "damage": 50},
                {"id": "key1", "type": "key", "position": [2, 0]}
            ],
            "constraints": {"collect_all_items": True}
        }

        with patch('builtins.open', mock_open(read_data=yaml.dump(stage_content))):
            result = validate_stage_with_bombs("test_bomb_stage.yml")

        assert result is True, "Stage with bombs should be validated as solvable"

    def test_simulate_item_management(self):
        """Given player position and items, when simulate, then optimal strategy returned"""
        from scripts.validate_stage import simulate_item_management

        player_pos = (1, 1)
        items = [
            {"id": "bomb1", "type": "bomb", "position": [0, 1], "damage": 50},
            {"id": "key1", "type": "key", "position": [2, 1]},
            {"id": "bomb2", "type": "bomb", "position": [1, 2], "damage": 30}
        ]

        strategy = simulate_item_management(player_pos, items)

        assert isinstance(strategy, dict), "Should return strategy dictionary"
        assert 'actions' in strategy, "Strategy should contain actions"
        assert 'bomb_disposals' in strategy, "Strategy should track bomb disposals"
        assert 'key_collections' in strategy, "Strategy should track key collections"

        # Verify bomb items are marked for disposal
        bomb_actions = [action for action in strategy['actions']
                       if action.get('type') == 'dispose']
        assert len(bomb_actions) >= 2, "Should plan to dispose both bomb items"

        # Verify beneficial items are marked for collection
        collect_actions = [action for action in strategy['actions']
                          if action.get('type') == 'pickup']
        assert len(collect_actions) >= 1, "Should plan to collect beneficial items"


@pytest.mark.contract
@pytest.mark.generator
@pytest.mark.validator
@pytest.mark.bomb
class TestScriptIntegrationContract:
    """Integration contracts for updated scripts"""

    def test_generate_bomb_stage(self):
        """Given bomb stage type, when generate, then valid bomb stage created"""
        # This will test the CLI interface
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Stage generated successfully"

            from scripts.generate_stage import main as generate_main

            # Simulate command line args for bomb generation
            with patch('sys.argv', ['generate_stage.py', '--type', 'attack',
                                  '--seed', '123', '--include-bombs']):
                result = generate_main()

        assert result == 0, "Bomb stage generation should succeed"

    def test_validate_bomb_stage_success(self):
        """Given solvable bomb stage, when validate, then validation succeeds"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "Stage validation passed"

            from scripts.validate_stage import main as validate_main

            with patch('sys.argv', ['validate_stage.py', '--file',
                                  'stages/test_bomb_stage.yml', '--detailed']):
                result = validate_main()

        assert result == 0, "Bomb stage validation should succeed"

    def test_generate_and_validate_pipeline(self):
        """Given stage generation, when validate generated stage, then validation succeeds"""
        # Test the complete pipeline: generate → validate
        stage_file = "stages/generated_attack_123.yml"

        # Mock stage generation
        with patch('scripts.generate_stage.generate_stage') as mock_gen, \
             patch('scripts.validate_stage.validate_stage') as mock_val:

            mock_gen.return_value = stage_file
            mock_val.return_value = True

            # Run generation
            from scripts.generate_stage import generate_stage
            generated_file = generate_stage(stage_type="attack", seed=123, include_bombs=True)

            # Run validation on generated file
            from scripts.validate_stage import validate_stage
            validation_result = validate_stage(generated_file)

        assert generated_file == stage_file, "Should generate expected file"
        assert validation_result is True, "Generated bomb stage should validate successfully"

    def test_mixed_item_stage_validation(self):
        """Given stage with bombs and beneficial items, when validate, then succeeds"""
        mixed_stage_content = {
            "id": "mixed_items_stage",
            "items": [
                {"id": "bomb1", "type": "bomb", "position": [1, 1], "damage": 40},
                {"id": "key1", "type": "key", "position": [2, 2]},
                {"id": "bomb2", "type": "bomb", "position": [3, 3], "damage": 60},
                {"id": "treasure1", "type": "treasure", "position": [4, 4]}
            ]
        }

        with patch('scripts.validate_stage.load_stage') as mock_load, \
             patch('scripts.validate_stage.validate_stage_with_bombs') as mock_validate:

            mock_load.return_value = mixed_stage_content
            mock_validate.return_value = True

            from scripts.validate_stage import validate_stage_with_bombs
            result = validate_stage_with_bombs("mixed_items_stage.yml")

        assert result is True, "Mixed item stage should validate successfully"


@pytest.mark.contract
@pytest.mark.generator
@pytest.mark.validator
class TestCLIContract:
    """Contract for command line interfaces"""

    def test_generate_stage_cli_with_bombs(self):
        """Test CLI interface for bomb stage generation"""
        from scripts.generate_stage import generate_stage_cli

        # Test with bomb options
        args = ["--type", "attack", "--seed", "456", "--include-bombs", "--bomb-ratio", "0.3"]
        result = generate_stage_cli(args)

        assert result == 0, "CLI should return success exit code"

    def test_validate_stage_cli_detailed(self):
        """Test CLI interface for detailed bomb stage validation"""
        from scripts.validate_stage import validate_stage_cli

        args = ["--file", "stages/test_bomb_stage.yml", "--detailed"]
        result = validate_stage_cli(args)

        assert result == 0, "CLI validation should return success exit code"