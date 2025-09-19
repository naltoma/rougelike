#!/usr/bin/env python3
"""
高度な敵システム
敵AI、行動パターン、戦闘システム
"""

import random
import math
from enum import Enum
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from . import Enemy, EnemyType, Position, Direction, EnemyMode, RageState


class BehaviorPattern(Enum):
    """敵の行動パターン"""
    STATIC = "static"           # 静止
    PATROL = "patrol"           # 巡回
    GUARD = "guard"             # 警備（範囲内でプレイヤー追跡）
    HUNTER = "hunter"           # ハンター（積極的追跡）
    RANDOM_MOVE = "random"      # ランダム移動
    RETREAT = "retreat"         # 後退（HP低下時）
    BERSERKER = "berserker"     # バーサーカー（攻撃特化）


class EnemyState(Enum):
    """敵の状態"""
    IDLE = "idle"               # 待機
    PATROLLING = "patrolling"   # 巡回中
    ALERT = "alert"             # 警戒中
    CHASING = "chasing"         # 追跡中
    ATTACKING = "attacking"     # 攻撃中
    RETREATING = "retreating"   # 後退中
    STUNNED = "stunned"         # スタン中


@dataclass
class EnemyAI:
    """敵AI設定"""
    behavior_pattern: BehaviorPattern
    detection_range: int = 3
    attack_range: int = 1
    movement_speed: int = 1
    aggression_level: float = 0.5
    intelligence: float = 0.5
    patrol_points: List[Position] = None
    
    def __post_init__(self):
        if self.patrol_points is None:
            self.patrol_points = []


@dataclass
class EnemyStats:
    """敵のステータス"""
    base_hp: int = 30
    base_attack: int = 5
    defense: int = 0
    speed: int = 1
    critical_chance: float = 0.1
    dodge_chance: float = 0.05
    special_abilities: List[str] = None
    
    def __post_init__(self):
        if self.special_abilities is None:
            self.special_abilities = []


class AdvancedEnemy(Enemy):
    """高度な敵クラス"""
    
    def __init__(self, position: Position, direction: Direction,
                 enemy_type: EnemyType = EnemyType.NORMAL,
                 ai_config: Optional[EnemyAI] = None,
                 stats: Optional[EnemyStats] = None):
        
        # 基本ステータス設定
        if stats is None:
            stats = EnemyStats()
        
        super().__init__(
            position=position,
            direction=direction,
            hp=stats.base_hp,
            max_hp=stats.base_hp,
            attack_power=stats.base_attack,
            enemy_type=enemy_type
        )
        
        # 高度な設定
        self.ai_config = ai_config or EnemyAI(BehaviorPattern.STATIC)
        self.stats = stats
        self.current_state = EnemyState.IDLE
        self.target_position: Optional[Position] = None
        self.last_seen_player: Optional[Position] = None
        self.patrol_index = 0
        self.stun_duration = 0
        self.anger_level = 0.0
        self.memory: Dict[str, Any] = {}
        
        # v1.2.7 pickup-wait system 拡張フィールド
        self.patrol_path: List[Position] = []
        self.vision_range: int = 2
        self.current_patrol_index: int = 0
        self.movement_mode: str = "patrol"  # "patrol" or "chase"
        
        # 行動履歴
        self.action_history: List[str] = []
        self.damage_taken_history: List[int] = []
    
    def update_state(self, player_position: Position, board) -> None:
        """状態更新"""
        # スタン状態の処理
        if self.stun_duration > 0:
            self.current_state = EnemyState.STUNNED
            self.stun_duration -= 1
            return
        
        # プレイヤーとの距離計算
        distance_to_player = self.position.distance_to(player_position)
        
        # 視界内にプレイヤーがいるか確認
        player_visible = self.can_see_player(player_position, board)
        
        if player_visible:
            self.last_seen_player = player_position
            self.anger_level = min(1.0, self.anger_level + 0.1)
        
        # 状態遷移
        self._update_state_logic(distance_to_player, player_visible)
    
    def _update_state_logic(self, distance: float, player_visible: bool) -> None:
        """状態遷移ロジック - 統一された視界システム"""
        # シンプルに統一: player_visibleのみを使用（方向を考慮した視界判定）

        # 攻撃範囲内
        if distance <= self.ai_config.attack_range and player_visible:
            self.current_state = EnemyState.ATTACKING
            self.movement_mode = "chase"

        # 視界内にプレイヤーを検出
        elif player_visible:
            if self.ai_config.behavior_pattern in [BehaviorPattern.GUARD, BehaviorPattern.HUNTER]:
                self.current_state = EnemyState.CHASING
                self.movement_mode = "chase"
            elif self.ai_config.behavior_pattern == BehaviorPattern.PATROL:
                # 巡回敵の場合、プレイヤー検出時は追跡モードに切り替え
                self.current_state = EnemyState.CHASING
                self.movement_mode = "chase"
            elif self.ai_config.behavior_pattern == BehaviorPattern.RETREAT and self.hp < self.max_hp * 0.3:
                self.current_state = EnemyState.RETREATING
                self.movement_mode = "retreat"
            else:
                self.current_state = EnemyState.ALERT
        
        # 通常状態
        else:
            if self.ai_config.behavior_pattern == BehaviorPattern.PATROL:
                self.current_state = EnemyState.PATROLLING
                self.movement_mode = "patrol"
            else:
                self.current_state = EnemyState.IDLE
                self.movement_mode = "idle"
    
    def get_next_action(self, player_position: Position, board) -> Dict[str, Any]:
        """次の行動を決定"""
        action = {"type": "none", "direction": None, "target": None}
        
        if self.current_state == EnemyState.STUNNED:
            return action
        
        # 状態別行動
        if self.current_state == EnemyState.ATTACKING:
            action = self._get_attack_action(player_position)
        
        elif self.current_state == EnemyState.CHASING:
            action = self._get_chase_action(player_position, board)
        
        elif self.current_state == EnemyState.PATROLLING:
            action = self._get_patrol_action(board)
        
        elif self.current_state == EnemyState.RETREATING:
            action = self._get_retreat_action(player_position, board)
        
        elif self.ai_config.behavior_pattern == BehaviorPattern.RANDOM_MOVE:
            action = self._get_random_action(board)
        
        # 行動履歴に記録
        if action["type"] != "none":
            self.action_history.append(f"{action['type']}_{self.current_state.value}")
            if len(self.action_history) > 10:
                self.action_history.pop(0)
        
        return action
    
    def _get_attack_action(self, player_position: Position) -> Dict[str, Any]:
        """攻撃行動"""
        # プレイヤーの方向を向く
        direction_to_player = self._get_direction_to_target(player_position)
        
        return {
            "type": "attack",
            "direction": direction_to_player,
            "target": player_position
        }
    
    def _get_chase_action(self, player_position: Position, board) -> Dict[str, Any]:
        """追跡行動"""
        target = player_position if self.last_seen_player is None else self.last_seen_player
        
        # A*アルゴリズムで最適パス計算
        next_position = self._find_next_position_to_target(target, board)
        
        if next_position and next_position != self.position:
            direction = self._get_direction_to_position(next_position)
            return {
                "type": "move",
                "direction": direction,
                "target": next_position
            }
        
        return {"type": "none", "direction": None, "target": None}
    
    def _get_patrol_action(self, board) -> Dict[str, Any]:
        """巡回行動 - v1.2.7 拡張"""
        # 古いpatrol_pointsシステムとの互換性維持
        if self.ai_config.patrol_points:
            current_target = self.ai_config.patrol_points[self.patrol_index]
            
            # 到達したら次のポイントへ
            if self.position == current_target:
                self.patrol_index = (self.patrol_index + 1) % len(self.ai_config.patrol_points)
                current_target = self.ai_config.patrol_points[self.patrol_index]
            
            # 巡回ポイントに向かって移動
            next_position = self._find_next_position_to_target(current_target, board)
            
            if next_position and next_position != self.position:
                direction = self._get_direction_to_position(next_position)
                return {
                    "type": "move",
                    "direction": direction,
                    "target": next_position
                }
        
        # v1.2.7 新しいpatrol_pathシステム
        elif self.patrol_path:
            current_target = self.get_next_patrol_position()
            if current_target is None:
                return {"type": "none", "direction": None, "target": None}
            
            # 到達したら次のポイントへ
            if self.position == current_target:
                self.advance_patrol()
                current_target = self.get_next_patrol_position()
            
            if current_target and current_target != self.position:
                # シンプルな1マス移動計算
                dx = current_target.x - self.position.x
                dy = current_target.y - self.position.y
                
                # 最も近い方向を決定
                if abs(dx) > abs(dy):
                    direction = Direction.EAST if dx > 0 else Direction.WEST
                else:
                    direction = Direction.SOUTH if dy > 0 else Direction.NORTH
                
                # 移動先位置計算
                offset_x, offset_y = direction.get_offset()
                next_position = Position(self.position.x + offset_x, self.position.y + offset_y)
                
                # 移動可能性チェック
                if board.is_passable(next_position):
                    return {
                        "type": "move",
                        "direction": direction,
                        "target": next_position
                    }
        
        return {"type": "none", "direction": None, "target": None}
    
    def _get_retreat_action(self, player_position: Position, board) -> Dict[str, Any]:
        """後退行動"""
        # プレイヤーから最も遠い方向を探す
        best_position = None
        max_distance = 0
        
        for direction in Direction:
            next_pos = self.position.move(direction)
            if board.is_passable(next_pos):
                distance = next_pos.distance_to(player_position)
                if distance > max_distance:
                    max_distance = distance
                    best_position = next_pos
        
        if best_position:
            direction = self._get_direction_to_position(best_position)
            return {
                "type": "move",
                "direction": direction,
                "target": best_position
            }
        
        return {"type": "none", "direction": None, "target": None}
    
    def _get_random_action(self, board) -> Dict[str, Any]:
        """ランダム行動"""
        if random.random() < 0.7:  # 70%の確率で移動
            possible_directions = []
            for direction in Direction:
                next_pos = self.position.move(direction)
                if board.is_passable(next_pos):
                    possible_directions.append(direction)
            
            if possible_directions:
                chosen_direction = random.choice(possible_directions)
                return {
                    "type": "move",
                    "direction": chosen_direction,
                    "target": self.position.move(chosen_direction)
                }
        
        return {"type": "none", "direction": None, "target": None}
    
    
    def _has_line_of_sight(self, target: Position, board) -> bool:
        """視線が通っているか確認"""
        # Bresenham's line algorithm の簡単な実装
        dx = abs(target.x - self.position.x)
        dy = abs(target.y - self.position.y)
        
        if dx == 0 and dy == 0:
            return True
        
        steps = max(dx, dy)
        x_step = (target.x - self.position.x) / steps
        y_step = (target.y - self.position.y) / steps
        
        for i in range(1, steps):
            check_x = int(self.position.x + x_step * i)
            check_y = int(self.position.y + y_step * i)
            check_pos = Position(check_x, check_y)
            
            if board.is_wall(check_pos):
                return False
        
        return True
    
    def _find_next_position_to_target(self, target: Position, board) -> Optional[Position]:
        """目標への最適な次のポジションを見つける"""
        # 簡単なA*アルゴリズム実装
        best_position = None
        best_distance = float('inf')
        
        for direction in Direction:
            next_pos = self.position.move(direction)
            if board.is_passable(next_pos):
                distance = next_pos.distance_to(target)
                if distance < best_distance:
                    best_distance = distance
                    best_position = next_pos
        
        return best_position
    
    def _get_direction_to_target(self, target: Position) -> Optional[Direction]:
        """目標への方向を取得"""
        dx = target.x - self.position.x
        dy = target.y - self.position.y
        
        if abs(dx) > abs(dy):
            return Direction.EAST if dx > 0 else Direction.WEST
        elif dy != 0:
            return Direction.SOUTH if dy > 0 else Direction.NORTH
        
        return None
    
    def _get_direction_to_position(self, target_pos: Position) -> Optional[Direction]:
        """指定座標への方向を取得"""
        dx = target_pos.x - self.position.x
        dy = target_pos.y - self.position.y
        
        if dx == 1 and dy == 0:
            return Direction.EAST
        elif dx == -1 and dy == 0:
            return Direction.WEST
        elif dx == 0 and dy == 1:
            return Direction.SOUTH
        elif dx == 0 and dy == -1:
            return Direction.NORTH
        
        return None
    
    def execute_action(self, action: Dict[str, Any], board) -> bool:
        """行動実行"""
        print(f"🔧 DEBUG execute_action: 敵[{self.position.x},{self.position.y}]{self.direction.value} アクション={action}")

        if action["type"] == "move" and action["direction"]:
            new_position = self.position.move(action["direction"])
            if board.is_passable(new_position):
                old_pos = f"[{self.position.x},{self.position.y}]"
                old_dir = self.direction.value
                self.position = new_position
                new_pos = f"[{self.position.x},{self.position.y}]"
                # 🔧 移動時は方向変更を行わない（1ターン1アクション制限）
                # self.direction = action["direction"]
                print(f"🔧 DEBUG move実行: {old_pos}{old_dir} → {new_pos}{self.direction.value}")
                return True

        elif action["type"] == "turn":
            # 新しいアクションタイプ: 方向転換のみ
            if action["direction"]:
                old_dir = self.direction.value
                self.direction = action["direction"]
                print(f"🔧 DEBUG turn実行: [{self.position.x},{self.position.y}] {old_dir} → {self.direction.value}")
                return True

        elif action["type"] == "attack":
            if action["direction"]:
                old_dir = self.direction.value
                self.direction = action["direction"]
                print(f"🔧 DEBUG attack実行: [{self.position.x},{self.position.y}] {old_dir} → {self.direction.value}")
            return True

        return False
    
    def take_damage(self, damage: int, damage_type: str = "physical") -> int:
        """ダメージ処理（オーバーライド）"""
        # 防御力計算
        actual_damage = max(1, damage - self.stats.defense)
        
        # 回避判定
        if random.random() < self.stats.dodge_chance:
            return 0
        
        # ダメージ適用
        result = super().take_damage(actual_damage)
        
        # ダメージ履歴記録
        self.damage_taken_history.append(result)
        if len(self.damage_taken_history) > 5:
            self.damage_taken_history.pop(0)
        
        # 怒り値増加
        self.anger_level = min(1.0, self.anger_level + result / self.max_hp)
        
        return result
    
    def get_attack_damage(self) -> int:
        """攻撃ダメージ計算"""
        base_damage = self.attack_power
        
        # クリティカル判定
        if random.random() < self.stats.critical_chance:
            base_damage = int(base_damage * 1.5)
        
        # 怒り状態ボーナス
        if self.anger_level > 0.7:
            base_damage = int(base_damage * 1.2)
        
        return base_damage
    
    def apply_stun(self, duration: int) -> None:
        """スタン効果適用"""
        self.stun_duration = duration
    
    def get_next_patrol_position(self) -> Optional[Position]:
        """次の巡回位置を取得"""
        if not self.patrol_path:
            return None
        
        if self.current_patrol_index >= len(self.patrol_path):
            self.current_patrol_index = 0
        
        return self.patrol_path[self.current_patrol_index]
    
    def advance_patrol(self) -> None:
        """巡回インデックスを進める"""
        if self.patrol_path:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)
    
    def detect_player(self, player_position: Position) -> bool:
        """プレイヤー検出（get_vision_cellsと同じ方向視界ロジック）"""
        # 基底クラスのget_vision_cellsロジックを使用
        vision_cells = self.get_vision_cells(board=None)  # 壁判定なしの視界取得
        return player_position in vision_cells
    
    def get_status_info(self) -> Dict[str, Any]:
        """状態情報取得"""
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "state": self.current_state.value,
            "behavior": self.ai_config.behavior_pattern.value,
            "anger_level": self.anger_level,
            "stunned": self.stun_duration > 0,
            "position": (self.position.x, self.position.y),
            "direction": self.direction.value,
            "movement_mode": self.movement_mode,
            "vision_range": self.vision_range,
            "patrol_progress": f"{self.current_patrol_index}/{len(self.patrol_path)}" if self.patrol_path else "0/0"
        }
    
    # v1.2.6: カウンター攻撃システム
    def can_counter_attack(self, player_position: Position) -> bool:
        """カウンター攻撃可能かチェック"""
        if not self.is_alive() or self.stun_duration > 0:
            return False
        
        # 隣接位置チェック（8方向）
        dx = abs(self.position.x - player_position.x)
        dy = abs(self.position.y - player_position.y)
        return dx <= 1 and dy <= 1 and (dx + dy) > 0
    
    def counter_attack(self, player_position: Position) -> Dict[str, Any]:
        """プレイヤーへのカウンター攻撃実行"""
        if not self.can_counter_attack(player_position):
            return {
                "success": False,
                "message": "カウンター攻撃不可能",
                "damage": 0
            }
        
        # プレイヤー方向を向く
        self.turn_to_player(player_position)
        
        # 攻撃実行
        damage = self.get_attack_damage()
        
        # 怒り値増加（攻撃を受けたため）
        self.anger_level = min(1.0, self.anger_level + 0.3)
        self.current_state = EnemyState.ATTACKING
        
        return {
            "success": True,
            "message": f"敵のカウンター攻撃! {damage}ダメージ",
            "damage": damage,
            "critical": random.random() < self.stats.critical_chance
        }
    
    def turn_to_player(self, player_position: Position):
        """プレイヤー方向に向きを変更"""
        dx = player_position.x - self.position.x
        dy = player_position.y - self.position.y
        
        # 最も近い方向を選択
        if abs(dx) > abs(dy):
            # 水平方向が主
            if dx > 0:
                self.direction = Direction.EAST
            else:
                self.direction = Direction.WEST
        else:
            # 垂直方向が主
            if dy > 0:
                self.direction = Direction.SOUTH
            else:
                self.direction = Direction.NORTH


class EnemyManager:
    """敵管理システム"""
    
    def __init__(self):
        self.enemies: List[AdvancedEnemy] = []
        self.enemy_turn_order: List[int] = []
        self.current_turn_index = 0
    
    def add_enemy(self, enemy: AdvancedEnemy) -> None:
        """敵を追加"""
        self.enemies.append(enemy)
        self.enemy_turn_order.append(len(self.enemies) - 1)
    
    def remove_enemy(self, enemy: AdvancedEnemy) -> None:
        """敵を削除"""
        if enemy in self.enemies:
            index = self.enemies.index(enemy)
            self.enemies.remove(enemy)
            if index in self.enemy_turn_order:
                self.enemy_turn_order.remove(index)
    
    def update_all_enemies(self, player_position: Position, board) -> None:
        """全ての敵を更新"""
        for enemy in self.enemies:
            if enemy.is_alive():
                enemy.update_state(player_position, board)
    
    def process_enemy_turn(self, player_position: Position, board) -> List[Dict[str, Any]]:
        """敵のターン処理"""
        actions = []
        
        for enemy in self.enemies:
            if enemy.is_alive():
                action = enemy.get_next_action(player_position, board)
                if action["type"] != "none":
                    enemy.execute_action(action, board)
                    actions.append({
                        "enemy": enemy,
                        "action": action
                    })
        
        return actions
    
    def get_enemies_at_position(self, position: Position) -> List[AdvancedEnemy]:
        """指定座標の敵を取得"""
        enemies_at_pos = []
        for enemy in self.enemies:
            if enemy.is_alive():
                occupied_positions = enemy.get_occupied_positions()
                if position in occupied_positions:
                    enemies_at_pos.append(enemy)
        return enemies_at_pos
    
    def get_alive_enemies(self) -> List[AdvancedEnemy]:
        """生存敵を取得"""
        return [enemy for enemy in self.enemies if enemy.is_alive()]
    
    def cleanup_dead_enemies(self) -> List[AdvancedEnemy]:
        """死亡した敵を清理"""
        dead_enemies = [enemy for enemy in self.enemies if not enemy.is_alive()]
        self.enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        return dead_enemies


# 敵生成ファクトリー
class EnemyFactory:
    """敵生成ファクトリー"""
    
    @staticmethod
    def create_basic_enemy(position: Position, enemy_type: EnemyType = EnemyType.NORMAL) -> AdvancedEnemy:
        """基本的な敵を生成"""
        ai_config = EnemyAI(
            behavior_pattern=BehaviorPattern.STATIC,
            detection_range=3,
            attack_range=1
        )
        
        stats = EnemyStats(
            base_hp=30,
            base_attack=5,
            defense=0
        )
        
        return AdvancedEnemy(position, Direction.NORTH, enemy_type, ai_config, stats)
    
    @staticmethod
    def create_guard_enemy(position: Position, patrol_points: List[Position] = None) -> AdvancedEnemy:
        """警備敵を生成"""
        ai_config = EnemyAI(
            behavior_pattern=BehaviorPattern.GUARD,
            detection_range=4,
            attack_range=1,
            patrol_points=patrol_points or []
        )
        
        stats = EnemyStats(
            base_hp=50,
            base_attack=8,
            defense=2
        )
        
        return AdvancedEnemy(position, Direction.NORTH, EnemyType.NORMAL, ai_config, stats)
    
    @staticmethod
    def create_hunter_enemy(position: Position) -> AdvancedEnemy:
        """ハンター敵を生成"""
        ai_config = EnemyAI(
            behavior_pattern=BehaviorPattern.HUNTER,
            detection_range=6,
            attack_range=1,
            aggression_level=0.8
        )
        
        stats = EnemyStats(
            base_hp=40,
            base_attack=10,
            defense=1,
            speed=2
        )
        
        return AdvancedEnemy(position, Direction.NORTH, EnemyType.NORMAL, ai_config, stats)
    
    @staticmethod
    def create_large_enemy(position: Position, enemy_type: EnemyType = EnemyType.LARGE_2X2) -> AdvancedEnemy:
        """大型敵を生成"""
        ai_config = EnemyAI(
            behavior_pattern=BehaviorPattern.GUARD,
            detection_range=5,
            attack_range=2
        )
        
        hp_multiplier = 2 if enemy_type == EnemyType.LARGE_2X2 else 3
        stats = EnemyStats(
            base_hp=60 * hp_multiplier,
            base_attack=15,
            defense=5,
            dodge_chance=0.1
        )
        
        return AdvancedEnemy(position, Direction.NORTH, enemy_type, ai_config, stats)


# v1.2.8 特殊条件付きステージ - 大型敵システム実装
class LargeEnemySystem:
    """大型敵システム - v1.2.8特殊条件付きステージ"""
    
    def __init__(self):
        """初期化"""
        self.large_enemies: Dict[str, Enemy] = {}  # 敵ID -> 敵オブジェクト
        self.rage_controllers: Dict[str, 'RageModeController'] = {}
    
    def initialize_large_enemy(self, enemy: Enemy, enemy_id: str) -> None:
        """大型敵初期配置・状態設定"""
        if enemy.enemy_type not in [EnemyType.LARGE_2X2, EnemyType.LARGE_3X3]:
            raise ValueError(f"大型敵タイプではありません: {enemy.enemy_type}")
        
        # 大型敵登録
        self.large_enemies[enemy_id] = enemy
        
        # 怒りモード状態確認・初期化
        if enemy.rage_state is None:
            enemy.rage_state = RageState()
        
        enemy.enemy_mode = EnemyMode.CALM
        
        # 怒りモード制御器作成
        self.rage_controllers[enemy_id] = RageModeController(enemy, self)
    
    def update_rage_state(self, enemy_id: str, current_hp: int) -> None:
        """HP監視・怒りモード判定ロジック"""
        if enemy_id not in self.large_enemies:
            return
        
        enemy = self.large_enemies[enemy_id]
        
        # HP50%以下で怒りモード発動
        hp_ratio = current_hp / enemy.max_hp
        if hp_ratio <= enemy.rage_state.trigger_hp_threshold and not enemy.rage_state.is_active:
            self.trigger_rage_mode(enemy_id)
        
        # 注意: ターン管理は別の場所で呼び出される (update_rage_turn_for_enemy)
    
    def update_rage_turn_for_enemy(self, enemy_id: str) -> None:
        """指定敵の怒りモードターン管理"""
        if enemy_id not in self.rage_controllers:
            return
        controller = self.rage_controllers[enemy_id]
        controller.update_rage_turn()
    
    def trigger_rage_mode(self, enemy_id: str) -> None:
        """HP50%以下での怒りモード発動"""
        if enemy_id not in self.large_enemies:
            return
        
        enemy = self.large_enemies[enemy_id]
        
        # 怒りモード状態遷移
        enemy.enemy_mode = EnemyMode.TRANSITIONING
        enemy.rage_state.is_active = True
        enemy.rage_state.turns_in_rage = 0
        enemy.rage_state.area_attack_executed = False
        enemy.rage_state.transition_turn_count = 1  # 1ターン遷移期間
    
    def reset_to_calm_mode(self, enemy_id: str) -> None:
        """範囲攻撃後の平常モード復帰"""
        if enemy_id not in self.large_enemies:
            return
        
        enemy = self.large_enemies[enemy_id]
        
        # 平常モード復帰
        enemy.enemy_mode = EnemyMode.CALM
        enemy.rage_state.is_active = False
        enemy.rage_state.turns_in_rage = 0
        enemy.rage_state.area_attack_executed = False
        enemy.rage_state.transition_turn_count = 0
    
    def get_enemy_mode(self, enemy_id: str) -> Optional[str]:
        """敵のモード取得"""
        if enemy_id not in self.large_enemies:
            return None
        return self.large_enemies[enemy_id].enemy_mode.value
    
    def execute_area_attack(self, enemy_id: str, player_position: Position) -> Tuple[bool, int]:
        """大型敵周囲1マス全体攻撃実行"""
        if enemy_id not in self.large_enemies:
            return False, 0
        
        enemy = self.large_enemies[enemy_id]
        if enemy.enemy_mode != EnemyMode.RAGE:
            return False, 0
        
        # 攻撃範囲座標取得
        attack_range = self.get_area_attack_range(enemy_id)
        
        # プレイヤーが範囲内にいるかチェック
        if player_position in attack_range:
            damage = enemy.attack_power
            enemy.rage_state.area_attack_executed = True
            return True, damage
        
        # プレイヤーが範囲外でも攻撃は実行される
        enemy.rage_state.area_attack_executed = True
        return False, 0
    
    def get_area_attack_range(self, enemy_id: str) -> List[Position]:
        """攻撃対象座標計算"""
        if enemy_id not in self.large_enemies:
            return []
        
        enemy = self.large_enemies[enemy_id]
        attack_positions = []
        
        # 敵が占有するマスを取得
        occupied_positions = enemy.get_occupied_positions()
        
        # 各占有マスの周囲1マスを攻撃範囲に追加
        for pos in occupied_positions:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    # 自分自身の位置は除外
                    if dx == 0 and dy == 0:
                        continue
                    
                    attack_pos = Position(pos.x + dx, pos.y + dy)
                    if attack_pos not in attack_positions:
                        attack_positions.append(attack_pos)
        
        # 重複除去（敵が占有する位置は攻撃範囲から除外）
        final_positions = []
        for pos in attack_positions:
            if pos not in occupied_positions and pos not in final_positions:
                final_positions.append(pos)
        
        return final_positions


class RageModeController:
    """怒りモード制御器 - LargeEnemySystem内部クラス"""
    
    def __init__(self, enemy: Enemy, large_enemy_system: LargeEnemySystem):
        self.enemy = enemy
        self.system = large_enemy_system
    
    def update_rage_turn(self) -> None:
        """怒りモード1ターン遷移ロジック"""
        # 状態遷移中の処理
        if self.enemy.enemy_mode == EnemyMode.TRANSITIONING:
            self.enemy.rage_state.transition_turn_count -= 1
            if self.enemy.rage_state.transition_turn_count <= 0:
                self.enemy.enemy_mode = EnemyMode.RAGE
                # 怒りモードに入った時にもターン数をカウント
                self.enemy.rage_state.turns_in_rage += 1
        
        # 怒りモード中の処理
        elif self.enemy.enemy_mode == EnemyMode.RAGE:
            # 怒りモード最初のターンで範囲攻撃実行
            if self.enemy.rage_state.turns_in_rage == 1 and not self.enemy.rage_state.area_attack_executed:
                # 範囲攻撃実行権限付与
                self._prepare_area_attack()
                self.enemy.rage_state.turns_in_rage += 1
            elif self.enemy.rage_state.area_attack_executed:
                # 範囲攻撃後は平常モードに復帰
                enemy_id = self._get_enemy_id()
                if enemy_id:
                    self.system.reset_to_calm_mode(enemy_id)
            else:
                # その他の場合は通常のターン進行
                self.enemy.rage_state.turns_in_rage += 1
    
    def _prepare_area_attack(self) -> None:
        """範囲攻撃準備"""
        # 範囲攻撃準備完了マークを設定
        # 実際の範囲攻撃実行は外部システム（ゲームループ）で execute_area_attack を呼び出す
        self.enemy.rage_state.area_attack_executed = True
    
    def _get_enemy_id(self) -> Optional[str]:
        """敵IDを逆引き"""
        for enemy_id, enemy in self.system.large_enemies.items():
            if enemy is self.enemy:
                return enemy_id
        return None


# v1.2.8 特殊条件付きステージ - 特殊敵システム実装
class SpecialEnemySystem:
    """特殊敵システム - v1.2.8特殊条件付きステージ"""
    
    def __init__(self):
        """初期化"""
        self.special_enemies: Dict[str, Enemy] = {}  # 敵ID -> 敵オブジェクト
    
    def initialize_special_enemy(self, enemy: Enemy, enemy_id: str) -> None:
        """HP/ATK=10000設定・特殊敵初期化"""
        if enemy.enemy_type != EnemyType.SPECIAL_2X3:
            raise ValueError(f"特殊敵タイプではありません: {enemy.enemy_type}")
        
        # 特殊敵のHP・攻撃力を10000に設定
        enemy.hp = 10000
        enemy.max_hp = 10000
        enemy.attack_power = 10000
        
        # 特殊敵登録
        self.special_enemies[enemy_id] = enemy
        
        # 条件付き行動状態確認・初期化
        if enemy.conditional_behavior is None:
            from . import ConditionalBehavior
            enemy.conditional_behavior = ConditionalBehavior()
        
        # 初期状態は平常モード（反撃のみ）
        enemy.enemy_mode = EnemyMode.CALM
    
    def activate_hunting_mode(self, enemy_id: str, target_position: Position) -> None:
        """条件違反時プレイヤー追跡モード発動"""
        if enemy_id not in self.special_enemies:
            return
        
        enemy = self.special_enemies[enemy_id]
        
        # 追跡モードに遷移
        enemy.enemy_mode = EnemyMode.HUNTING
        enemy.conditional_behavior.violation_detected = True
        enemy.conditional_behavior.hunting_target = target_position
    
    def auto_eliminate(self, enemy_id: str) -> bool:
        """条件達成時特殊敵消去"""
        if enemy_id not in self.special_enemies:
            return False
        
        enemy = self.special_enemies[enemy_id]
        
        # 条件達成チェック（攻撃順序が正しい場合）
        if self._check_elimination_conditions(enemy):
            # 特殊敵を無力化（HP=0にする）
            enemy.hp = 0
            return True
        
        return False
    
    def is_behavior_restricted(self, enemy_id: str) -> bool:
        """平常時行動制限チェック（移動・巡視・追跡無効化）"""
        if enemy_id not in self.special_enemies:
            return False
        
        enemy = self.special_enemies[enemy_id]
        
        # 平常モードでは行動制限
        return enemy.enemy_mode == EnemyMode.CALM
    
    def get_special_enemy_mode(self, enemy_id: str) -> Optional[str]:
        """特殊敵のモード取得"""
        if enemy_id not in self.special_enemies:
            return None
        return self.special_enemies[enemy_id].enemy_mode.value
    
    def update_conditional_behavior(self, enemy_id: str, attack_sequence: List[str]) -> None:
        """攻撃順序更新"""
        if enemy_id not in self.special_enemies:
            return
        
        enemy = self.special_enemies[enemy_id]
        enemy.conditional_behavior.current_sequence = attack_sequence.copy()
    
    def _check_elimination_conditions(self, enemy: Enemy) -> bool:
        """特殊敵消去条件チェック"""
        # 必須攻撃順序が設定されていない場合は消去不可
        if not enemy.conditional_behavior.required_sequence:
            return False
        
        # 現在の攻撃順序が必須順序と一致するかチェック
        current = enemy.conditional_behavior.current_sequence
        required = enemy.conditional_behavior.required_sequence
        
        # 順序が一致し、すべて完了している場合
        return len(current) >= len(required) and current[:len(required)] == required


class ConditionalBattleManager:
    """条件付き戦闘管理システム - v1.2.8特殊条件付きステージ"""
    
    def __init__(self):
        """初期化"""
        self.attack_sequence: List[str] = []  # 攻撃順序記録
        self.required_sequence: List[str] = ["large_2x2", "large_3x3"]  # デフォルト必須順序
        self.violation_feedback: List[str] = []  # 教育的フィードバック
    
    def register_attack_sequence(self, enemy_type: str) -> None:
        """攻撃順序記録"""
        # 敵タイプを文字列として記録
        type_mapping = {
            "large_2x2": "2x2大型敵",
            "large_3x3": "3x3大型敵", 
            "special_2x3": "2x3特殊敵"
        }
        
        attack_target = type_mapping.get(enemy_type, enemy_type)
        self.attack_sequence.append(attack_target)
    
    def validate_attack_sequence(self) -> bool:
        """攻撃順序検証（大型敵2x2→3x3順序）"""
        if len(self.attack_sequence) < len(self.required_sequence):
            return True  # まだ判定段階ではない
        
        # 必須順序との比較
        for i, required_target in enumerate(self.required_sequence):
            # タイプマッピング（カスタム順序にも対応）
            type_mapping = {
                "large_2x2": "2x2大型敵",
                "large_3x3": "3x3大型敵", 
                "special_2x3": "2x3特殊敵"
            }
            expected = type_mapping.get(required_target, required_target)
            
            if i >= len(self.attack_sequence) or self.attack_sequence[i] != expected:
                return False
        
        return True
    
    def check_conditional_violation(self) -> bool:
        """特殊条件違反判定"""
        is_valid = self.validate_attack_sequence()
        
        if not is_valid:
            # 違反内容を記録
            self.violation_feedback.append(
                f"攻撃順序違反: 期待順序 {self.required_sequence}, 実際 {self.attack_sequence}"
            )
        
        return not is_valid
    
    def get_violation_feedback(self) -> List[str]:
        """教育的フィードバック生成"""
        if not self.violation_feedback:
            return ["正しい攻撃順序で進行しています。"]
        
        feedback = []
        feedback.extend(self.violation_feedback)
        feedback.append("ヒント: 大型敵は2x2 → 3x3の順序で攻撃してください。")
        
        return feedback
    
    def reset_sequence(self) -> None:
        """攻撃順序リセット"""
        self.attack_sequence.clear()
        self.violation_feedback.clear()
    
    def set_required_sequence(self, sequence: List[str]) -> None:
        """必須攻撃順序設定"""
        self.required_sequence = sequence.copy()