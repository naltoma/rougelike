#!/usr/bin/env python3
"""
高度なゲーム状態管理
敵・アイテムシステム統合版
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from . import GameState, Character, Position, Direction, GameStatus, TurnPhase
from .enemy_system import EnemyManager, AdvancedEnemy, EnemyFactory
from .item_system import ItemManager, Inventory, AdvancedItem, ItemEffectProcessor
from .game_state import GameStateManager
from .commands import Command, ExecutionResult, CommandResult


@dataclass
class CombatResult:
    """戦闘結果"""
    attacker_damage: int = 0
    defender_damage: int = 0
    attacker_dead: bool = False
    defender_dead: bool = False
    messages: List[str] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []


class AdvancedGameState(GameState):
    """拡張ゲーム状態"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enemy_manager = EnemyManager()
        self.item_manager = ItemManager()
        self.player_inventory = Inventory()
        self.effect_processor = ItemEffectProcessor()
        self.combat_log: List[str] = []
        self.turn_events: List[str] = []
        
        # v1.2.6: ターンベース戦闘システム
        self.current_turn_phase: TurnPhase = TurnPhase.PLAYER
        self.turn_number: int = 1
        self.enemies_attacked_this_turn: List[int] = []  # 今ターンに攻撃を受けた敵のID
        
        # 敵とアイテムを高度なシステムに移行
        self._migrate_enemies()
        self._migrate_items()
    
    def _migrate_enemies(self):
        """基本敵を高度な敵システムに移行"""
        for enemy in self.enemies:
            advanced_enemy = EnemyFactory.create_basic_enemy(enemy.position, enemy.enemy_type)
            advanced_enemy.hp = enemy.hp
            advanced_enemy.max_hp = enemy.max_hp
            advanced_enemy.attack_power = enemy.attack_power
            advanced_enemy.direction = enemy.direction
            self.enemy_manager.add_enemy(advanced_enemy)
        
        # 基本敵リストをクリア
        self.enemies.clear()
    
    def _migrate_items(self):
        """基本アイテムを高度なアイテムシステムに移行"""
        for item in self.items:
            advanced_item = self.item_manager.create_item(
                template_name=item.name,
                position=item.position,
                quantity=1
            )
            if advanced_item:
                self.item_manager.place_item_at(item.position, advanced_item)
        
        # 基本アイテムリストをクリア
        self.items.clear()
    
    def get_enemies_at_position(self, position: Position) -> List[AdvancedEnemy]:
        """指定座標の敵を取得"""
        return self.enemy_manager.get_enemies_at_position(position)
    
    def get_items_at_position(self, position: Position) -> List[AdvancedItem]:
        """指定座標のアイテムを取得"""
        return self.item_manager.get_items_at(position)
    
    def process_enemy_turn(self) -> List[str]:
        """敵のターン処理"""
        self.enemy_manager.update_all_enemies(self.player.position, self.board)
        actions = self.enemy_manager.process_enemy_turn(self.player.position, self.board)
        
        messages = []
        for action_data in actions:
            enemy = action_data["enemy"]
            action = action_data["action"]
            
            if action["type"] == "attack" and action["target"] == self.player.position:
                # プレイヤーへの攻撃
                combat_result = self._resolve_combat(enemy, self.player)
                messages.extend(combat_result.messages)
            
            elif action["type"] == "move":
                messages.append(f"敵が移動しました")
        
        return messages
    
    def attack_enemy_at(self, position: Position) -> CombatResult:
        """指定座標の敵を攻撃"""
        enemies = self.get_enemies_at_position(position)
        
        if not enemies:
            return CombatResult(messages=["攻撃対象がありません"])
        
        target_enemy = enemies[0]  # 最初の敵を攻撃
        return self._resolve_combat(self.player, target_enemy)
    
    def _resolve_combat(self, attacker, defender) -> CombatResult:
        """戦闘解決"""
        result = CombatResult()
        
        # 攻撃力計算
        attacker_damage = attacker.attack_power
        if hasattr(attacker, 'get_attack_damage'):
            attacker_damage = attacker.get_attack_damage()
        
        # 装備効果適用（プレイヤーの場合）
        if attacker == self.player:
            equipment_effects = self.player_inventory.get_total_equipment_effects()
            attacker_damage += equipment_effects.get("attack_power", 0)
        
        # ダメージ適用
        actual_damage = defender.take_damage(attacker_damage)
        result.attacker_damage = actual_damage
        
        # メッセージ生成
        attacker_name = "プレイヤー" if attacker == self.player else "敵"
        defender_name = "敵" if defender != self.player else "プレイヤー"
        
        result.messages.append(f"{attacker_name}が{defender_name}に{actual_damage}ダメージを与えました")
        
        # 死亡判定
        if not defender.is_alive():
            result.defender_dead = True
            result.messages.append(f"{defender_name}を倒しました！")
            
            # 敵を倒した場合の処理
            if defender != self.player:
                self.enemy_manager.remove_enemy(defender)
                # 経験値やドロップアイテムの処理（将来の拡張）
        
        self.combat_log.extend(result.messages)
        return result
    
    def pickup_items_at(self, position: Position) -> List[str]:
        """指定座標のアイテムを拾う"""
        items = self.item_manager.pickup_items_at(position)
        messages = []
        
        for item in items:
            if self.player_inventory.add_item(item):
                messages.append(f"{item.data.base_item.name}を拾いました")
            else:
                messages.append("インベントリが満杯です")
                # アイテムを元の場所に戻す
                self.item_manager.place_item_at(position, item)
        
        return messages
    
    def use_item(self, item_name: str) -> List[str]:
        """アイテム使用"""
        item = self.player_inventory.find_item(item_name)
        
        if not item:
            return ["そのアイテムを持っていません"]
        
        if not item.can_use():
            return ["そのアイテムは使用できません"]
        
        # アイテム効果適用
        messages = self.effect_processor.apply_item_effect(item, self.player, self)
        
        # アイテム消費
        if item.use_item():
            messages.append(f"{item_name}を使用しました")
        
        return messages
    
    def equip_item(self, item_name: str, slot: str) -> List[str]:
        """アイテム装備"""
        if self.player_inventory.equip_item(item_name, slot):
            return [f"{item_name}を{slot}スロットに装備しました"]
        else:
            return ["装備できません"]
    
    def process_turn_end(self) -> List[str]:
        """ターン終了処理"""
        messages = []
        
        # 持続効果処理
        effect_messages = self.effect_processor.process_duration_effects()
        messages.extend(effect_messages)
        
        # 敵のターン処理
        enemy_messages = self.process_enemy_turn()
        messages.extend(enemy_messages)
        
        # 死亡した敵の清理
        dead_enemies = self.enemy_manager.cleanup_dead_enemies()
        for enemy in dead_enemies:
            # ドロップアイテム生成（将来の拡張）
            pass
        
        # ゲーム終了判定
        if not self.player.is_alive():
            self.status = GameStatus.FAILED
            messages.append("プレイヤーが倒れました...")
        elif len(self.enemy_manager.get_alive_enemies()) == 0 and self.goal_position:
            # 全敵撃破でゴール開放（ステージによる）
            pass
        
        self.turn_events = messages
        return messages
    
    def get_game_info(self) -> Dict[str, Any]:
        """ゲーム情報取得"""
        base_info = {
            "player_hp": f"{self.player.hp}/{self.player.max_hp}",
            "turn": f"{self.turn_count}/{self.max_turns}",
            "status": self.status.value,
            "position": (self.player.position.x, self.player.position.y),
            "direction": self.player.direction.value
        }
        
        # 敵情報
        alive_enemies = self.enemy_manager.get_alive_enemies()
        base_info["enemies_count"] = len(alive_enemies)
        base_info["enemy_info"] = [enemy.get_status_info() for enemy in alive_enemies]
        
        # インベントリ情報
        base_info["inventory"] = self.player_inventory.get_inventory_summary()
        
        # 装備情報
        equipment_effects = self.player_inventory.get_total_equipment_effects()
        if equipment_effects:
            base_info["equipment_effects"] = equipment_effects
        
        # 戦闘ログ
        if self.combat_log:
            base_info["recent_combat"] = self.combat_log[-3:]  # 最近の3件
        
        return base_info


class AdvancedGameStateManager(GameStateManager):
    """拡張ゲーム状態管理"""
    
    def initialize_game(self, *args, **kwargs) -> AdvancedGameState:
        """ゲーム初期化（拡張版）"""
        # 基本初期化を実行
        basic_state = super().initialize_game(*args, **kwargs)
        
        # 拡張状態に変換
        advanced_state = AdvancedGameState(
            player=basic_state.player,
            enemies=basic_state.enemies,
            items=basic_state.items,
            board=basic_state.board,
            turn_count=basic_state.turn_count,
            max_turns=basic_state.max_turns,
            status=basic_state.status,
            goal_position=basic_state.goal_position
        )
        
        self.current_state = advanced_state
        self.initial_state = self._copy_advanced_state(advanced_state)
        
        return advanced_state
    
    def _copy_advanced_state(self, state: AdvancedGameState) -> AdvancedGameState:
        """拡張ゲーム状態のコピー"""
        # 基本的なディープコピー実装
        return AdvancedGameState(
            player=Character(
                position=state.player.position,
                direction=state.player.direction,
                hp=state.player.hp,
                max_hp=state.player.max_hp,
                attack_power=state.player.attack_power
            ),
            enemies=[],  # 敵は移行済みなので空
            items=[],    # アイテムは移行済みなので空
            board=state.board,
            turn_count=state.turn_count,
            max_turns=state.max_turns,
            status=state.status,
            goal_position=state.goal_position
        )
    
    def execute_command(self, command: Command) -> ExecutionResult:
        """コマンド実行（拡張版）"""
        if not isinstance(self.current_state, AdvancedGameState):
            return ExecutionResult(
                result=CommandResult.FAILED,
                message="拡張ゲーム状態が必要です"
            )
        
        # 基本コマンド実行
        result = super().execute_command(command)
        
        # 拡張処理
        if result.is_success:
            turn_messages = self.current_state.process_turn_end()
            if turn_messages:
                # 結果にターン終了メッセージを追加
                result.message += "\n" + "\n".join(turn_messages)
        
        return result
    
    def get_advanced_state(self) -> Optional[AdvancedGameState]:
        """拡張ゲーム状態取得"""
        return self.current_state if isinstance(self.current_state, AdvancedGameState) else None


# 戦闘システム
class CombatSystem:
    """戦闘システム"""
    
    def __init__(self, game_state: AdvancedGameState):
        self.game_state = game_state
    
    def calculate_damage(self, attacker, defender) -> int:
        """ダメージ計算"""
        base_damage = attacker.attack_power
        
        # 攻撃力ボーナス（装備品）
        if attacker == self.game_state.player:
            equipment_effects = self.game_state.player_inventory.get_total_equipment_effects()
            base_damage += equipment_effects.get("attack_power", 0)
        
        # 防御力計算
        defense = 0
        if hasattr(defender, 'stats') and hasattr(defender.stats, 'defense'):
            defense = defender.stats.defense
        elif defender == self.game_state.player:
            equipment_effects = self.game_state.player_inventory.get_total_equipment_effects()
            defense = equipment_effects.get("defense", 0)
        
        # 最終ダメージ
        final_damage = max(1, base_damage - defense)
        return final_damage
    
    def resolve_attack(self, attacker, defender) -> CombatResult:
        """攻撃解決"""
        damage = self.calculate_damage(attacker, defender)
        actual_damage = defender.take_damage(damage)
        
        result = CombatResult(
            attacker_damage=actual_damage,
            defender_dead=not defender.is_alive()
        )
        
        # メッセージ生成
        attacker_name = "プレイヤー" if attacker == self.game_state.player else "敵"
        defender_name = "敵" if defender != self.game_state.player else "プレイヤー"
        
        result.messages.append(f"{attacker_name}が{defender_name}に{actual_damage}ダメージ!")
        
        if result.defender_dead:
            result.messages.append(f"{defender_name}を倒した!")
        
        return result


# アイテムドロップシステム
class DropSystem:
    """アイテムドロップシステム"""
    
    def __init__(self, item_manager: ItemManager):
        self.item_manager = item_manager
        self.drop_tables: Dict[str, List[Dict[str, Any]]] = {}
        self._initialize_drop_tables()
    
    def _initialize_drop_tables(self):
        """ドロップテーブル初期化"""
        # 基本敵のドロップテーブル
        self.drop_tables["normal_enemy"] = [
            {"item": "health_potion", "chance": 0.3, "quantity": 1},
            {"item": "iron_sword", "chance": 0.1, "quantity": 1}
        ]
        
        # 大型敵のドロップテーブル
        self.drop_tables["large_enemy"] = [
            {"item": "health_potion", "chance": 0.5, "quantity": 2},
            {"item": "leather_armor", "chance": 0.3, "quantity": 1},
            {"item": "iron_sword", "chance": 0.2, "quantity": 1}
        ]
    
    def generate_drops(self, enemy: AdvancedEnemy) -> List[AdvancedItem]:
        """敵からのドロップ生成"""
        import random
        
        drop_table_key = f"{enemy.enemy_type.value}_enemy"
        if drop_table_key not in self.drop_tables:
            drop_table_key = "normal_enemy"
        
        drops = []
        drop_table = self.drop_tables[drop_table_key]
        
        for drop_entry in drop_table:
            if random.random() < drop_entry["chance"]:
                item = self.item_manager.create_item(
                    drop_entry["item"],
                    enemy.position,
                    drop_entry["quantity"]
                )
                if item:
                    drops.append(item)
        
        return drops
    
    def place_drops(self, enemy: AdvancedEnemy) -> List[str]:
        """ドロップアイテムを配置"""
        drops = self.generate_drops(enemy)
        messages = []
        
        for item in drops:
            self.item_manager.place_item_at(enemy.position, item)
            messages.append(f"{item.data.base_item.name}がドロップされました")
        
        return messages
    
    # v1.2.6: ターンベース戦闘システム
    def next_turn(self):
        """次のターンに進む"""
        if self.current_turn_phase == TurnPhase.PLAYER:
            # プレイヤーターン終了、敵ターン開始
            self.current_turn_phase = TurnPhase.ENEMY
            self.turn_events.append(f"ターン {self.turn_number}: 敵フェーズ開始")
        else:
            # 敵ターン終了、次のプレイヤーターン開始
            self.current_turn_phase = TurnPhase.PLAYER
            self.turn_number += 1
            self.enemies_attacked_this_turn.clear()
            self.turn_events.append(f"ターン {self.turn_number}: プレイヤーフェーズ開始")
    
    def is_player_turn(self) -> bool:
        """プレイヤーのターンかどうか"""
        return self.current_turn_phase == TurnPhase.PLAYER
    
    def is_enemy_turn(self) -> bool:
        """敵のターンかどうか"""
        return self.current_turn_phase == TurnPhase.ENEMY
    
    def mark_enemy_attacked(self, enemy_id: int):
        """敵が攻撃を受けたことをマーク"""
        if enemy_id not in self.enemies_attacked_this_turn:
            self.enemies_attacked_this_turn.append(enemy_id)
    
    def was_enemy_attacked_this_turn(self, enemy_id: int) -> bool:
        """この敵が今ターン攻撃を受けたかチェック"""
        return enemy_id in self.enemies_attacked_this_turn