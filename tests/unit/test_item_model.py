"""
Unit tests for Item model damage attribute extension
These tests MUST FAIL initially to follow TDD methodology
"""

import pytest
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from engine import Item, Position, ItemType


@pytest.mark.unit
@pytest.mark.bomb
@pytest.mark.core
class TestItemDamageAttribute:
    """Unit tests for Item class damage attribute"""

    def test_item_with_damage_attribute(self):
        """Given bomb item, when created with damage, then damage stored correctly"""
        # TODO: This test MUST FAIL initially - damage attribute doesn't exist yet
        item = Item(
            id="bomb1",
            item_type=ItemType.BOMB,
            position=Position(3, 4),
            name="爆弾",
            description="An item must be disposed",
            damage=75
        )

        assert hasattr(item, 'damage'), "Item should have damage attribute"
        assert item.damage == 75, "Damage should be stored correctly"
        assert item.item_type == ItemType.BOMB, "Item type should be bomb"

    def test_item_without_damage_attribute(self):
        """Given beneficial item, when created, then damage is None or not present"""
        item = Item(
            id="key1",
            item_type=ItemType.KEY,
            position=Position(1, 2),
            name="鍵",
            description="A useful key"
        )

        # Damage should be None or not present for non-bomb items
        if hasattr(item, 'damage'):
            assert item.damage is None, "Non-bomb items should have damage=None"

    def test_bomb_item_default_damage(self):
        """Given bomb item without explicit damage, when created, then default damage applied"""
        item = Item(
            id="bomb2",
            item_type=ItemType.BOMB,
            position=Position(5, 6),
            name="爆弾",
            description="Default damage bomb"
        )

        # Default damage should be 100 for bomb items
        assert hasattr(item, 'damage'), "Bomb item should have damage attribute"
        assert item.damage == 100, "Default bomb damage should be 100"

    def test_damage_validation_positive(self):
        """Given bomb item with positive damage, when created, then accepted"""
        valid_damages = [1, 50, 100, 999]

        for damage in valid_damages:
            item = Item(
                id=f"bomb_{damage}",
                item_type=ItemType.BOMB,
                position=Position(1, 1),
                damage=damage
            )
            assert item.damage == damage, f"Valid damage {damage} should be accepted"

    def test_damage_validation_invalid(self):
        """Given bomb item with invalid damage, when created, then raises ValueError"""
        invalid_damages = [-1, -50, 0]

        for damage in invalid_damages:
            with pytest.raises(ValueError, match="Damage must be positive"):
                Item(
                    id=f"invalid_bomb_{abs(damage)}",
                    item_type=ItemType.BOMB,
                    position=Position(1, 1),
                    damage=damage
                )

    def test_damage_validation_non_bomb_ignored(self):
        """Given non-bomb item with damage, when created, then damage ignored or raises error"""
        # For non-bomb items, damage should either be ignored or raise an error
        with pytest.raises((ValueError, TypeError), match="damage.*not allowed|damage.*bomb"):
            Item(
                id="key_with_damage",
                item_type=ItemType.KEY,
                position=Position(1, 1),
                damage=50  # This should not be allowed for non-bomb items
            )

    def test_bomb_item_serialization(self):
        """Given bomb item with damage, when serialized, then damage included"""
        item = Item(
            id="bomb_serialize",
            item_type=ItemType.BOMB,
            position=Position(2, 3),
            name="爆弾",
            description="Serialization test bomb",
            damage=85
        )

        # Test serialization (assuming Item has to_dict method)
        if hasattr(item, 'to_dict'):
            item_dict = item.to_dict()
            assert 'damage' in item_dict, "Serialized bomb should include damage"
            assert item_dict['damage'] == 85, "Serialized damage should match original"

    def test_item_comparison_with_damage(self):
        """Given bomb items with different damage, when compared, then compared correctly"""
        bomb1 = Item(
            id="bomb1",
            item_type=ItemType.BOMB,
            position=Position(1, 1),
            damage=50
        )

        bomb2 = Item(
            id="bomb1",  # Same id
            item_type=ItemType.BOMB,
            position=Position(1, 1),
            damage=75  # Different damage
        )

        # Items with same id but different damage should be considered different
        # (assuming Item implements __eq__)
        if hasattr(Item, '__eq__'):
            assert bomb1 != bomb2, "Items with different damage should not be equal"

    def test_item_repr_includes_damage(self):
        """Given bomb item, when string representation created, then damage included"""
        item = Item(
            id="bomb_repr",
            item_type=ItemType.BOMB,
            position=Position(4, 5),
            damage=120
        )

        item_str = str(item) or repr(item)
        assert "120" in item_str, "String representation should include damage value"
        assert "bomb" in item_str.lower(), "String representation should include type"

    def test_damage_type_validation(self):
        """Given bomb item with non-integer damage, when created, then raises TypeError"""
        invalid_damage_types = ["50", 50.5, None, [50], {"damage": 50}]

        for invalid_damage in invalid_damage_types:
            with pytest.raises((TypeError, ValueError), match="damage.*integer|damage.*must be.*int"):
                Item(
                    id="bomb_invalid_type",
                    item_type=ItemType.BOMB,
                    position=Position(1, 1),
                    damage=invalid_damage
                )


@pytest.mark.unit
@pytest.mark.bomb
class TestItemFactoryWithDamage:
    """Test Item creation through factory methods with damage support"""

    def test_create_bomb_item_factory(self):
        """Given bomb item creation via factory, when damage specified, then created correctly"""
        # Assuming there's a factory method for creating items
        if hasattr(Item, 'create_bomb'):
            bomb = Item.create_bomb(
                id="factory_bomb",
                position=Position(3, 3),
                damage=60,
                name="Factory Bomb"
            )

            assert bomb.item_type == "bomb", "Factory should create bomb type"
            assert bomb.damage == 60, "Factory should set damage correctly"

    def test_create_beneficial_item_factory(self):
        """Given beneficial item creation via factory, when created, then no damage attribute"""
        if hasattr(Item, 'create_key'):
            key = Item.create_key(
                id="factory_key",
                position=Position(2, 2),
                name="Factory Key"
            )

            assert key.item_type == "key", "Factory should create key type"
            if hasattr(key, 'damage'):
                assert key.damage is None, "Beneficial items should not have damage"