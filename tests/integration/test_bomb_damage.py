"""
Integration tests for HP damage from bomb pickup
These tests MUST FAIL initially to follow TDD methodology
"""

import pytest
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine import Position


@pytest.mark.integration
@pytest.mark.bomb
@pytest.mark.core
class TestBombDamageIntegration:
    """Integration tests for bomb pickup damage system"""

    def test_bomb_pickup_reduces_hp_by_damage_amount(self):
        """Given bomb with specific damage, when picked up, then HP reduced by exact amount"""
        # TODO: This test MUST FAIL initially - bomb damage system doesn't exist yet
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player
        initial_hp = player.hp

        # Setup bomb with specific damage
        bomb_item = {
            "id": "damage_test_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y],
            "damage": 45
        }
        game_state.items = [bomb_item]

        # Execute pickup
        pickup_command = PickupCommand()
        result = pickup_command.execute(game_state)

        assert result.success, "Bomb pickup should succeed"
        assert player.hp == initial_hp - 45, "HP should be reduced by bomb damage (45)"
        assert len(game_state.items) == 0, "Bomb should be removed after pickup"

    def test_bomb_pickup_default_damage_100(self):
        """Given bomb without damage field, when picked up, then HP reduced by 100"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player
        initial_hp = player.hp

        # Setup bomb without explicit damage (should default to 100)
        bomb_item = {
            "id": "default_damage_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y]
            # No damage field
        }
        game_state.items = [bomb_item]

        pickup_command = PickupCommand()
        pickup_command.execute(game_state)

        assert player.hp == initial_hp - 100, "HP should be reduced by default damage (100)"

    def test_bomb_damage_cannot_reduce_hp_below_zero(self):
        """Given player with low HP, when bomb damage exceeds HP, then HP becomes 0"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player
        player.hp = 20  # Set low HP

        # Setup bomb with damage higher than current HP
        bomb_item = {
            "id": "overkill_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y],
            "damage": 50  # More than current HP
        }
        game_state.items = [bomb_item]

        pickup_command = PickupCommand()
        pickup_command.execute(game_state)

        assert player.hp == 0, "HP should not go below 0"
        assert not player.is_alive(), "Player should not be alive with 0 HP"

    def test_multiple_bomb_pickups_cumulative_damage(self):
        """Given multiple bombs, when picked up sequentially, then damage accumulates"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player
        initial_hp = player.hp

        # Setup multiple bombs
        bomb1 = {
            "id": "cumulative_bomb_1",
            "type": "bomb",
            "position": [1, 1],
            "damage": 25
        }
        bomb2 = {
            "id": "cumulative_bomb_2",
            "type": "bomb",
            "position": [2, 2],
            "damage": 35
        }
        game_state.items = [bomb1, bomb2]

        pickup_command = PickupCommand()

        # Pickup first bomb
        player.position = Position(1, 1)
        pickup_command.execute(game_state)
        expected_hp_after_first = initial_hp - 25
        assert player.hp == expected_hp_after_first, "HP should be reduced by first bomb"

        # Pickup second bomb
        player.position = Position(2, 2)
        pickup_command.execute(game_state)
        expected_hp_after_second = expected_hp_after_first - 35
        assert player.hp == expected_hp_after_second, "HP should be reduced cumulatively"

    def test_beneficial_item_pickup_no_damage(self):
        """Given beneficial item, when picked up, then no HP damage"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player
        initial_hp = player.hp

        # Setup beneficial item
        key_item = {
            "id": "safe_key",
            "type": "key",
            "position": [player.position.x, player.position.y]
        }
        game_state.items = [key_item]

        pickup_command = PickupCommand()
        pickup_command.execute(game_state)

        assert player.hp == initial_hp, "HP should not change for beneficial items"

    def test_bomb_damage_with_zero_damage(self):
        """Given bomb with 0 damage, when picked up, then no HP loss"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player
        initial_hp = player.hp

        # Setup bomb with zero damage
        bomb_item = {
            "id": "harmless_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y],
            "damage": 0
        }
        game_state.items = [bomb_item]

        pickup_command = PickupCommand()
        pickup_command.execute(game_state)

        assert player.hp == initial_hp, "Zero damage bomb should not reduce HP"

    def test_bomb_damage_logging(self):
        """Given bomb pickup, when damage applied, then damage logged"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand
        import logging

        game_state = GameState()
        player = game_state.player

        bomb_item = {
            "id": "logged_damage_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y],
            "damage": 60
        }
        game_state.items = [bomb_item]

        pickup_command = PickupCommand()

        # Capture logs
        with pytest.LoggingHandler() as log_capture:
            pickup_command.execute(game_state)

            logs = log_capture.get_logs()
            # Verify damage is logged
            damage_logged = any("60" in log and "damage" in log.lower() for log in logs)
            assert damage_logged, "Bomb damage should be logged"

    def test_bomb_pickup_execution_result_includes_damage(self):
        """Given bomb pickup, when executed, then result includes damage information"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player

        bomb_item = {
            "id": "result_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y],
            "damage": 30
        }
        game_state.items = [bomb_item]

        pickup_command = PickupCommand()
        result = pickup_command.execute(game_state)

        assert result.success, "Bomb pickup should succeed"
        assert "30" in result.message or "damage" in result.message.lower(), "Result should mention damage"


@pytest.mark.integration
@pytest.mark.bomb
@pytest.mark.performance
class TestBombDamagePerformance:
    """Performance tests for bomb damage system"""

    def test_bomb_damage_calculation_performance(self):
        """Given many bomb pickups, when executed, then performs within acceptable time"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand
        import time

        game_state = GameState()
        player = game_state.player

        # Setup many bombs for performance testing
        bombs = []
        for i in range(100):
            bomb = {
                "id": f"perf_bomb_{i}",
                "type": "bomb",
                "position": [i % 10, i // 10],
                "damage": 1  # Small damage to avoid killing player
            }
            bombs.append(bomb)

        pickup_command = PickupCommand()

        start_time = time.time()

        # Process all bombs
        for bomb in bombs:
            game_state.items = [bomb]
            player.position = Position(bomb["position"][0], bomb["position"][1])
            pickup_command.execute(game_state)

        end_time = time.time()
        processing_time = end_time - start_time

        # Should process 100 bomb pickups in under 1 second
        assert processing_time < 1.0, f"Bomb damage processing too slow: {processing_time}s"


@pytest.mark.integration
@pytest.mark.bomb
@pytest.mark.edge_cases
class TestBombDamageEdgeCases:
    """Edge case tests for bomb damage system"""

    def test_bomb_with_negative_damage_validation(self):
        """Given bomb with negative damage, when processed, then handled appropriately"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player

        # Setup bomb with negative damage (should be prevented or treated as 0)
        bomb_item = {
            "id": "negative_damage_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y],
            "damage": -10  # Negative damage
        }
        game_state.items = [bomb_item]

        pickup_command = PickupCommand()

        # Should either fail validation or treat as 0 damage
        try:
            result = pickup_command.execute(game_state)
            # If it succeeds, HP should not increase
            assert player.hp <= 100, "Negative damage should not heal player"
        except (ValueError, TypeError):
            # Or it should raise an error for invalid damage
            pass

    def test_bomb_with_extremely_high_damage(self):
        """Given bomb with very high damage, when picked up, then handled correctly"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player

        bomb_item = {
            "id": "massive_damage_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y],
            "damage": 999999  # Extremely high damage
        }
        game_state.items = [bomb_item]

        pickup_command = PickupCommand()
        pickup_command.execute(game_state)

        # Should handle gracefully
        assert player.hp == 0, "Extreme damage should result in 0 HP"
        assert player.hp >= 0, "HP should never be negative"

    def test_bomb_damage_with_string_damage_value(self):
        """Given bomb with string damage value, when processed, then handles type error"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player

        bomb_item = {
            "id": "string_damage_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y],
            "damage": "50"  # String instead of int
        }
        game_state.items = [bomb_item]

        pickup_command = PickupCommand()

        # Should either convert string to int or raise type error
        try:
            result = pickup_command.execute(game_state)
            # If conversion happens, damage should be applied
            assert player.hp <= 100, "String damage should be converted and applied"
        except (TypeError, ValueError):
            # Or should raise type error for invalid type
            pass

    def test_bomb_pickup_concurrent_hp_modification(self):
        """Given bomb pickup with concurrent HP modifications, when executed, then handled atomically"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand
        import threading

        game_state = GameState()
        player = game_state.player

        bomb_item = {
            "id": "concurrent_bomb",
            "type": "bomb",
            "position": [player.position.x, player.position.y],
            "damage": 25
        }
        game_state.items = [bomb_item]

        pickup_command = PickupCommand()

        # Simulate concurrent modifications
        def modify_hp():
            if hasattr(player, 'take_damage'):
                player.take_damage(10)

        # Start concurrent modification
        thread = threading.Thread(target=modify_hp)
        thread.start()

        # Execute bomb pickup
        result = pickup_command.execute(game_state)
        thread.join()

        # Final HP should be consistent (either 65 or 75, depending on execution order)
        assert player.hp in [65, 75], "Concurrent HP modifications should be handled consistently"