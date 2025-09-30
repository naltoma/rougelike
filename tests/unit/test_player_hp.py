"""
Unit tests for Player HP system
These tests MUST FAIL initially to follow TDD methodology
"""

import pytest
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


@pytest.mark.unit
@pytest.mark.bomb
@pytest.mark.core
class TestPlayerHPSystem:
    """Unit tests for Player HP tracking system"""

    def test_player_default_hp(self):
        """Given new player, when created, then has default HP of 100"""
        # TODO: This test MUST FAIL initially - HP system doesn't exist yet
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player

        assert hasattr(player, 'hp'), "Player should have HP attribute"
        assert player.hp == 100, "Default HP should be 100"
        assert hasattr(player, 'max_hp'), "Player should have max_hp attribute"
        assert player.max_hp == 100, "Default max_hp should be 100"

    def test_player_hp_initialization(self):
        """Given player with custom HP, when initialized, then HP set correctly"""
        from engine.game_state import GameState

        game_state = GameState(player_hp=150, player_max_hp=200)
        player = game_state.player

        assert player.hp == 150, "Custom HP should be set correctly"
        assert player.max_hp == 200, "Custom max_hp should be set correctly"

    def test_player_take_damage(self):
        """Given player with HP, when takes damage, then HP reduced correctly"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player
        initial_hp = player.hp

        damage_taken = player.take_damage(30)

        assert player.hp == initial_hp - 30, "HP should be reduced by damage amount"
        assert damage_taken == 30, "take_damage should return actual damage taken"

    def test_player_damage_cannot_exceed_current_hp(self):
        """Given player with low HP, when takes large damage, then HP becomes 0"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player
        player.hp = 20  # Set low HP

        damage_taken = player.take_damage(50)  # More than current HP

        assert player.hp == 0, "HP should not go below 0"
        assert damage_taken == 20, "Actual damage taken should be capped at current HP"

    def test_player_hp_cannot_go_negative(self):
        """Given player HP reduction, when HP would go negative, then clamped to 0"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player
        player.hp = 10

        player.take_damage(20)

        assert player.hp >= 0, "HP should never be negative"
        assert player.hp == 0, "HP should be exactly 0 when damage exceeds current HP"

    def test_player_hp_cannot_exceed_max(self):
        """Given player HP increase, when HP would exceed max, then clamped to max"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player
        player.hp = 80

        if hasattr(player, 'heal'):
            player.heal(50)  # More than needed to reach max
            assert player.hp <= player.max_hp, "HP should not exceed max_hp"
            assert player.hp == player.max_hp, "HP should be clamped to max_hp"

    def test_player_disposed_items_tracking(self):
        """Given player, when items disposed, then disposed_items list updated"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player

        assert hasattr(player, 'disposed_items'), "Player should have disposed_items attribute"
        assert isinstance(player.disposed_items, list), "disposed_items should be a list"
        assert len(player.disposed_items) == 0, "Initial disposed_items should be empty"

        # Test adding disposed items
        player.add_disposed_item("bomb1")
        player.add_disposed_item("bomb2")

        assert "bomb1" in player.disposed_items, "Disposed item should be tracked"
        assert "bomb2" in player.disposed_items, "Multiple disposed items should be tracked"
        assert len(player.disposed_items) == 2, "disposed_items count should be correct"

    def test_player_disposed_items_no_duplicates(self):
        """Given player, when same item disposed twice, then no duplicates in list"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player

        player.add_disposed_item("bomb1")
        player.add_disposed_item("bomb1")  # Same item again

        assert player.disposed_items.count("bomb1") == 1, "No duplicate items in disposed_items"
        assert len(player.disposed_items) == 1, "disposed_items should contain unique items only"

    def test_player_hp_validation(self):
        """Given player HP modification, when invalid values set, then raises error"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player

        # Test invalid HP values
        with pytest.raises((ValueError, TypeError)):
            player.hp = -10  # Negative HP

        with pytest.raises((ValueError, TypeError)):
            player.hp = "100"  # String HP

        with pytest.raises((ValueError, TypeError)):
            player.max_hp = 0  # Zero max HP

    def test_player_damage_validation(self):
        """Given damage amount, when invalid, then raises appropriate error"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player

        # Test invalid damage values
        with pytest.raises((ValueError, TypeError)):
            player.take_damage(-5)  # Negative damage

        with pytest.raises((ValueError, TypeError)):
            player.take_damage("10")  # String damage

        with pytest.raises((ValueError, TypeError)):
            player.take_damage(None)  # None damage

    def test_player_is_alive(self):
        """Given player HP status, when checked, then returns correct alive status"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player

        assert player.is_alive(), "Player with HP > 0 should be alive"

        player.hp = 0
        assert not player.is_alive(), "Player with HP = 0 should not be alive"

    def test_player_hp_percentage(self):
        """Given player HP, when percentage calculated, then returns correct value"""
        from engine.game_state import GameState

        game_state = GameState()
        player = game_state.player
        player.max_hp = 100
        player.hp = 75

        if hasattr(player, 'hp_percentage'):
            percentage = player.hp_percentage()
            assert percentage == 75.0, "HP percentage should be calculated correctly"

            player.hp = 0
            percentage = player.hp_percentage()
            assert percentage == 0.0, "Zero HP should give 0% percentage"


@pytest.mark.unit
@pytest.mark.bomb
@pytest.mark.integration
class TestPlayerHPIntegration:
    """Integration tests for Player HP with game mechanics"""

    def test_bomb_pickup_reduces_hp(self):
        """Given player and bomb item, when bomb picked up, then HP reduced"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player
        initial_hp = player.hp

        # Create bomb item
        bomb_item = {
            "id": "test_bomb",
            "type": "bomb",
            "damage": 40,
            "position": player.position  # Same position as player
        }

        # Add bomb to game state
        game_state.items.append(bomb_item)

        # Execute pickup command
        pickup_command = PickupCommand()
        result = pickup_command.execute(game_state)

        assert result.success, "Pickup should succeed"
        assert player.hp == initial_hp - 40, "HP should be reduced by bomb damage"

    def test_bomb_default_damage_application(self):
        """Given bomb without damage specified, when picked up, then 100 damage applied"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player
        initial_hp = player.hp

        # Create bomb item without explicit damage
        bomb_item = {
            "id": "default_bomb",
            "type": "bomb",
            "position": player.position
            # No damage field - should default to 100
        }

        game_state.items.append(bomb_item)

        pickup_command = PickupCommand()
        pickup_command.execute(game_state)

        assert player.hp == initial_hp - 100, "Default bomb damage should be 100"

    def test_beneficial_item_no_hp_loss(self):
        """Given beneficial item, when picked up, then no HP loss"""
        from engine.game_state import GameState
        from engine.commands import PickupCommand

        game_state = GameState()
        player = game_state.player
        initial_hp = player.hp

        # Create beneficial item
        key_item = {
            "id": "test_key",
            "type": "key",
            "position": player.position
        }

        game_state.items.append(key_item)

        pickup_command = PickupCommand()
        pickup_command.execute(game_state)

        assert player.hp == initial_hp, "Beneficial items should not reduce HP"