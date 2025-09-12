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
from . import Enemy, EnemyType, Position, Direction


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
        player_visible = self._can_see_player(player_position, board)
        
        if player_visible:
            self.last_seen_player = player_position
            self.anger_level = min(1.0, self.anger_level + 0.1)
        
        # 状態遷移
        self._update_state_logic(distance_to_player, player_visible)
    
    def _update_state_logic(self, distance: float, player_visible: bool) -> None:
        """状態遷移ロジック - v1.2.7 視界検出拡張"""
        # v1.2.7 拡張: 新しいvision_range検出
        player_in_vision = self.detect_player(self.last_seen_player) if self.last_seen_player else player_visible
        
        # 攻撃範囲内
        if distance <= self.ai_config.attack_range and player_visible:
            self.current_state = EnemyState.ATTACKING
            self.movement_mode = "chase"
        
        # 検出範囲内（従来のdetection_range または新しいvision_range）
        elif (distance <= self.ai_config.detection_range and player_visible) or player_in_vision:
            if self.ai_config.behavior_pattern in [BehaviorPattern.GUARD, BehaviorPattern.HUNTER]:
                self.current_state = EnemyState.CHASING
                self.movement_mode = "chase"
            elif self.ai_config.behavior_pattern == BehaviorPattern.PATROL:
                # 巡回敵の場合、プレイヤー検出時は追跡モードに切り替え
                if player_in_vision:
                    self.current_state = EnemyState.CHASING
                    self.movement_mode = "chase"
                else:
                    self.current_state = EnemyState.PATROLLING
                    self.movement_mode = "patrol"
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
    
    def _can_see_player(self, player_position: Position, board) -> bool:
        """プレイヤーを視認できるか"""
        distance = self.position.distance_to(player_position)
        
        if distance > self.ai_config.detection_range:
            return False
        
        # 視線遮蔽判定（簡単な実装）
        return self._has_line_of_sight(player_position, board)
    
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
        if action["type"] == "move" and action["direction"]:
            new_position = self.position.move(action["direction"])
            if board.is_passable(new_position):
                self.position = new_position
                self.direction = action["direction"]
                return True
        
        elif action["type"] == "attack":
            if action["direction"]:
                self.direction = action["direction"]
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
        """プレイヤー検出（vision_range内判定）"""
        distance = abs(self.position.x - player_position.x) + abs(self.position.y - player_position.y)
        return distance <= self.vision_range
    
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