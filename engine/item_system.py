#!/usr/bin/env python3
"""
高度なアイテムシステム
アイテム効果、装備システム、インベントリ管理
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass
from . import Item, ItemType, Position


class ItemRarity(Enum):
    """アイテムレアリティ"""
    COMMON = "common"           # 一般
    UNCOMMON = "uncommon"       # 珍しい
    RARE = "rare"              # レア
    EPIC = "epic"              # エピック
    LEGENDARY = "legendary"     # 伝説


class EffectType(Enum):
    """効果タイプ"""
    IMMEDIATE = "immediate"     # 即時効果
    DURATION = "duration"       # 持続効果
    PERMANENT = "permanent"     # 永続効果
    CONDITIONAL = "conditional" # 条件効果


class ItemCategory(Enum):
    """アイテムカテゴリ"""
    CONSUMABLE = "consumable"   # 消耗品
    EQUIPMENT = "equipment"     # 装備品
    KEY_ITEM = "key_item"      # 重要アイテム
    MATERIAL = "material"       # 素材
    QUEST = "quest"            # クエストアイテム


@dataclass
class ItemEffect:
    """アイテム効果"""
    effect_type: EffectType
    stat_modifiers: Dict[str, int]
    duration: int = 0
    conditions: Dict[str, Any] = None
    special_effects: List[str] = None
    
    def __post_init__(self):
        if self.conditions is None:
            self.conditions = {}
        if self.special_effects is None:
            self.special_effects = []


@dataclass
class ItemData:
    """拡張アイテムデータ"""
    base_item: Item
    rarity: ItemRarity = ItemRarity.COMMON
    category: ItemCategory = ItemCategory.CONSUMABLE
    effects: List[ItemEffect] = None
    stack_size: int = 1
    tradeable: bool = True
    destructible: bool = True
    required_level: int = 1
    description: str = ""
    flavor_text: str = ""
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = []


class AdvancedItem:
    """高度なアイテムクラス"""
    
    def __init__(self, item_data: ItemData, quantity: int = 1):
        self.data = item_data
        self.quantity = quantity
        self.durability = 100.0 if self.is_equipment() else 0.0
        self.max_durability = self.durability
        self.enchantments: Dict[str, int] = {}
        self.custom_properties: Dict[str, Any] = {}
        self.creation_time = None
        self.last_used_time = None
        self.use_count = 0
    
    def is_equipment(self) -> bool:
        """装備品かどうか"""
        return self.data.category == ItemCategory.EQUIPMENT
    
    def is_consumable(self) -> bool:
        """消耗品かどうか"""
        return self.data.category == ItemCategory.CONSUMABLE
    
    def is_stackable(self) -> bool:
        """スタック可能かどうか"""
        return self.data.stack_size > 1
    
    def can_use(self, player_level: int = 1) -> bool:
        """使用可能かどうか"""
        return (
            player_level >= self.data.required_level and
            self.quantity > 0 and
            (not self.is_equipment() or self.durability > 0)
        )
    
    def use_item(self) -> bool:
        """アイテム使用"""
        if not self.can_use():
            return False
        
        self.use_count += 1
        
        # 消耗品は数量減少
        if self.is_consumable():
            self.quantity = max(0, self.quantity - 1)
        
        # 装備品は耐久度減少
        elif self.is_equipment():
            self.reduce_durability(1.0)
        
        return True
    
    def reduce_durability(self, amount: float) -> None:
        """耐久度減少"""
        if self.is_equipment():
            self.durability = max(0.0, self.durability - amount)
    
    def repair(self, amount: float) -> float:
        """修理"""
        if not self.is_equipment():
            return 0.0
        
        old_durability = self.durability
        self.durability = min(self.max_durability, self.durability + amount)
        return self.durability - old_durability
    
    def get_total_effects(self) -> Dict[str, int]:
        """総合効果取得"""
        total_effects = {}
        
        # 基本効果
        for effect in self.data.effects:
            for stat, value in effect.stat_modifiers.items():
                total_effects[stat] = total_effects.get(stat, 0) + value
        
        # エンチャント効果
        for enchant, level in self.enchantments.items():
            bonus = self._get_enchantment_bonus(enchant, level)
            for stat, value in bonus.items():
                total_effects[stat] = total_effects.get(stat, 0) + value
        
        # 耐久度による効果減少
        if self.is_equipment() and self.max_durability > 0:
            durability_ratio = self.durability / self.max_durability
            if durability_ratio < 0.5:
                for stat in total_effects:
                    total_effects[stat] = int(total_effects[stat] * durability_ratio)
        
        return total_effects
    
    def _get_enchantment_bonus(self, enchant: str, level: int) -> Dict[str, int]:
        """エンチャント効果計算"""
        enchant_effects = {
            "power": {"attack_power": level * 2},
            "protection": {"defense": level * 1},
            "agility": {"speed": level * 1},
            "vitality": {"max_hp": level * 5},
            "fortune": {"luck": level * 1}
        }
        return enchant_effects.get(enchant, {})
    
    def add_enchantment(self, enchant: str, level: int) -> bool:
        """エンチャント追加"""
        if not self.is_equipment():
            return False
        
        max_enchant_level = 5
        if level <= max_enchant_level:
            self.enchantments[enchant] = level
            return True
        return False
    
    def get_value(self) -> int:
        """アイテム価値計算"""
        base_value = 10
        
        # レアリティボーナス
        rarity_multipliers = {
            ItemRarity.COMMON: 1.0,
            ItemRarity.UNCOMMON: 2.0,
            ItemRarity.RARE: 5.0,
            ItemRarity.EPIC: 10.0,
            ItemRarity.LEGENDARY: 25.0
        }
        
        value = int(base_value * rarity_multipliers[self.data.rarity])
        
        # エンチャントボーナス
        for enchant, level in self.enchantments.items():
            value += level * 50
        
        # 耐久度による価値減少
        if self.is_equipment() and self.max_durability > 0:
            durability_ratio = self.durability / self.max_durability
            value = int(value * durability_ratio)
        
        return max(1, value * self.quantity)
    
    def get_description(self) -> str:
        """アイテム説明取得"""
        desc_parts = [self.data.description]
        
        # 効果説明
        effects = self.get_total_effects()
        if effects:
            effect_desc = "効果: " + ", ".join(f"{k}+{v}" for k, v in effects.items() if v > 0)
            desc_parts.append(effect_desc)
        
        # エンチャント説明
        if self.enchantments:
            enchant_desc = "エンチャント: " + ", ".join(f"{k} Lv.{v}" for k, v in self.enchantments.items())
            desc_parts.append(enchant_desc)
        
        # 耐久度
        if self.is_equipment():
            durability_desc = f"耐久度: {self.durability:.1f}/{self.max_durability:.1f}"
            desc_parts.append(durability_desc)
        
        return "\n".join(filter(None, desc_parts))


class Inventory:
    """インベントリシステム"""
    
    def __init__(self, max_capacity: int = 20):
        self.items: List[AdvancedItem] = []
        self.max_capacity = max_capacity
        self.equipped_items: Dict[str, AdvancedItem] = {}
        self.equipment_slots = ["weapon", "armor", "accessory"]
    
    def add_item(self, item: AdvancedItem, quantity: int = 1) -> bool:
        """アイテム追加"""
        # スタック可能アイテムの処理
        if item.is_stackable():
            for existing_item in self.items:
                if (existing_item.data.base_item.name == item.data.base_item.name and
                    existing_item.quantity < item.data.stack_size):
                    
                    can_add = min(quantity, item.data.stack_size - existing_item.quantity)
                    existing_item.quantity += can_add
                    quantity -= can_add
                    
                    if quantity <= 0:
                        return True
        
        # 新しいスロットに追加
        if len(self.items) < self.max_capacity:
            new_item = AdvancedItem(item.data, quantity)
            self.items.append(new_item)
            return True
        
        return False
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """アイテム削除"""
        for item in self.items:
            if item.data.base_item.name == item_name:
                if item.quantity >= quantity:
                    item.quantity -= quantity
                    if item.quantity <= 0:
                        self.items.remove(item)
                    return True
        return False
    
    def find_item(self, item_name: str) -> Optional[AdvancedItem]:
        """アイテム検索"""
        for item in self.items:
            if item.data.base_item.name == item_name:
                return item
        return None
    
    def equip_item(self, item_name: str, slot: str) -> bool:
        """アイテム装備"""
        item = self.find_item(item_name)
        
        if (item and item.is_equipment() and 
            slot in self.equipment_slots and
            item.can_use()):
            
            # 既に装備されているアイテムを外す
            if slot in self.equipped_items:
                self.unequip_item(slot)
            
            # 新しいアイテムを装備
            self.equipped_items[slot] = item
            return True
        
        return False
    
    def unequip_item(self, slot: str) -> bool:
        """アイテム装備解除"""
        if slot in self.equipped_items:
            del self.equipped_items[slot]
            return True
        return False
    
    def get_total_equipment_effects(self) -> Dict[str, int]:
        """装備効果総計"""
        total_effects = {}
        
        for item in self.equipped_items.values():
            item_effects = item.get_total_effects()
            for stat, value in item_effects.items():
                total_effects[stat] = total_effects.get(stat, 0) + value
        
        return total_effects
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """インベントリ概要"""
        return {
            "total_items": len(self.items),
            "capacity": self.max_capacity,
            "equipped_count": len(self.equipped_items),
            "total_value": sum(item.get_value() for item in self.items),
            "categories": self._get_category_counts()
        }
    
    def _get_category_counts(self) -> Dict[str, int]:
        """カテゴリ別アイテム数"""
        counts = {}
        for item in self.items:
            category = item.data.category.value
            counts[category] = counts.get(category, 0) + item.quantity
        return counts


class ItemManager:
    """アイテム管理システム"""
    
    def __init__(self):
        self.field_items: Dict[Position, List[AdvancedItem]] = {}
        self.item_templates: Dict[str, ItemData] = {}
        self._initialize_templates()
    
    def _initialize_templates(self) -> None:
        """アイテムテンプレート初期化"""
        # 基本武器
        sword_item = Item(
            position=Position(0, 0),
            item_type=ItemType.WEAPON,
            name="iron_sword",
            effect={"attack_power": 10}
        )
        
        sword_data = ItemData(
            base_item=sword_item,
            rarity=ItemRarity.COMMON,
            category=ItemCategory.EQUIPMENT,
            effects=[ItemEffect(
                effect_type=EffectType.PERMANENT,
                stat_modifiers={"attack_power": 10}
            )],
            description="鉄製の剣。基本的な武器。"
        )
        
        self.item_templates["iron_sword"] = sword_data
        
        # 基本防具
        armor_item = Item(
            position=Position(0, 0),
            item_type=ItemType.ARMOR,
            name="leather_armor",
            effect={"defense": 5}
        )
        
        armor_data = ItemData(
            base_item=armor_item,
            rarity=ItemRarity.COMMON,
            category=ItemCategory.EQUIPMENT,
            effects=[ItemEffect(
                effect_type=EffectType.PERMANENT,
                stat_modifiers={"defense": 5}
            )],
            description="革製の鎧。軽量で動きやすい。"
        )
        
        self.item_templates["leather_armor"] = armor_data
        
        # 回復ポーション
        potion_item = Item(
            position=Position(0, 0),
            item_type=ItemType.POTION,
            name="health_potion",
            effect={"heal": 30}
        )
        
        potion_data = ItemData(
            base_item=potion_item,
            rarity=ItemRarity.COMMON,
            category=ItemCategory.CONSUMABLE,
            effects=[ItemEffect(
                effect_type=EffectType.IMMEDIATE,
                stat_modifiers={"heal": 30}
            )],
            stack_size=10,
            description="体力を回復するポーション。"
        )
        
        self.item_templates["health_potion"] = potion_data
    
    def place_item_at(self, position: Position, item: AdvancedItem) -> None:
        """アイテムを配置"""
        if position not in self.field_items:
            self.field_items[position] = []
        self.field_items[position].append(item)
    
    def pickup_items_at(self, position: Position) -> List[AdvancedItem]:
        """指定座標のアイテムを拾う"""
        items = self.field_items.get(position, [])
        if position in self.field_items:
            del self.field_items[position]
        return items
    
    def get_items_at(self, position: Position) -> List[AdvancedItem]:
        """指定座標のアイテム取得"""
        return self.field_items.get(position, [])
    
    def create_item(self, template_name: str, position: Position, 
                   quantity: int = 1, rarity: Optional[ItemRarity] = None) -> Optional[AdvancedItem]:
        """アイテム生成"""
        if template_name not in self.item_templates:
            return None
        
        template = self.item_templates[template_name]
        
        # テンプレートをコピーして位置設定
        item_data = ItemData(
            base_item=Item(
                position=position,
                item_type=template.base_item.item_type,
                name=template.base_item.name,
                effect=template.base_item.effect.copy()
            ),
            rarity=rarity or template.rarity,
            category=template.category,
            effects=template.effects.copy(),
            stack_size=template.stack_size,
            description=template.description
        )
        
        return AdvancedItem(item_data, quantity)
    
    def create_random_item(self, position: Position, level: int = 1) -> AdvancedItem:
        """ランダムアイテム生成"""
        import random
        
        template_names = list(self.item_templates.keys())
        template_name = random.choice(template_names)
        
        # レベルに応じてレアリティ決定
        rarity_weights = {
            ItemRarity.COMMON: max(1, 10 - level),
            ItemRarity.UNCOMMON: min(5, level),
            ItemRarity.RARE: min(3, max(0, level - 3)),
            ItemRarity.EPIC: min(2, max(0, level - 6)),
            ItemRarity.LEGENDARY: min(1, max(0, level - 10))
        }
        
        rarities = list(rarity_weights.keys())
        weights = list(rarity_weights.values())
        rarity = random.choices(rarities, weights=weights)[0]
        
        item = self.create_item(template_name, position, 1, rarity)
        
        # 高レアリティアイテムにエンチャント追加
        if item and rarity in [ItemRarity.RARE, ItemRarity.EPIC, ItemRarity.LEGENDARY]:
            enchants = ["power", "protection", "agility", "vitality", "fortune"]
            enchant = random.choice(enchants)
            level = random.randint(1, min(3, int(rarity.value == "legendary") + 1))
            item.add_enchantment(enchant, level)
        
        return item
    
    def get_all_field_items(self) -> Dict[Position, List[AdvancedItem]]:
        """全てのフィールドアイテム取得"""
        return self.field_items.copy()


# アイテム効果適用システム
class ItemEffectProcessor:
    """アイテム効果処理システム"""
    
    def __init__(self):
        self.active_effects: List[Dict[str, Any]] = []
        self.effect_handlers: Dict[str, Callable] = {
            "heal": self._handle_heal,
            "damage": self._handle_damage,
            "stat_boost": self._handle_stat_boost,
            "teleport": self._handle_teleport
        }
    
    def apply_item_effect(self, item: AdvancedItem, target, game_state) -> List[str]:
        """アイテム効果適用"""
        messages = []
        
        for effect in item.data.effects:
            if effect.effect_type == EffectType.IMMEDIATE:
                messages.extend(self._apply_immediate_effect(effect, target, game_state))
            
            elif effect.effect_type == EffectType.DURATION:
                self._apply_duration_effect(effect, target, game_state)
                messages.append(f"{effect.duration}ターンの間、効果が続きます")
        
        return messages
    
    def _apply_immediate_effect(self, effect: ItemEffect, target, game_state) -> List[str]:
        """即時効果適用"""
        messages = []
        
        for stat, value in effect.stat_modifiers.items():
            if stat == "heal" and hasattr(target, 'heal'):
                healed = target.heal(value)
                messages.append(f"{healed}HP回復しました")
            
            elif stat == "damage" and hasattr(target, 'take_damage'):
                damage = target.take_damage(value)
                messages.append(f"{damage}ダメージを受けました")
        
        return messages
    
    def _apply_duration_effect(self, effect: ItemEffect, target, game_state) -> None:
        """持続効果適用"""
        self.active_effects.append({
            "effect": effect,
            "target": target,
            "remaining_duration": effect.duration
        })
    
    def process_duration_effects(self) -> List[str]:
        """持続効果処理"""
        messages = []
        expired_effects = []
        
        for active_effect in self.active_effects:
            active_effect["remaining_duration"] -= 1
            
            if active_effect["remaining_duration"] <= 0:
                expired_effects.append(active_effect)
                messages.append("効果が終了しました")
        
        # 期限切れ効果を削除
        for expired in expired_effects:
            self.active_effects.remove(expired)
        
        return messages
    
    def _handle_heal(self, target, value: int) -> str:
        """回復効果処理"""
        if hasattr(target, 'heal'):
            healed = target.heal(value)
            return f"{healed}HP回復"
        return ""
    
    def _handle_damage(self, target, value: int) -> str:
        """ダメージ効果処理"""
        if hasattr(target, 'take_damage'):
            damage = target.take_damage(value)
            return f"{damage}ダメージ"
        return ""
    
    def _handle_stat_boost(self, target, boost_data: Dict[str, int]) -> str:
        """ステータス上昇処理"""
        # 実装は対象オブジェクトの仕様による
        return "ステータスが上昇しました"
    
    def _handle_teleport(self, target, position_data: Dict[str, int]) -> str:
        """テレポート効果処理"""
        # 実装は対象オブジェクトの仕様による
        return "テレポートしました"