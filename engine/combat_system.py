"""
戦闘処理エンジン - v1.2.6 攻撃システム統合
プレイヤー・敵間の戦闘処理、ダメージ計算、撃破判定
"""

from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass
from . import Character, Enemy, Position, Direction
from .enemy_system import AdvancedEnemy


@dataclass
class CombatResult:
    """戦闘結果"""
    success: bool
    attacker_damage_dealt: int = 0
    defender_damage_taken: int = 0
    defender_defeated: bool = False
    attacker_defeated: bool = False
    messages: List[str] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []


class CombatSystem:
    """戦闘処理システム"""
    
    # ダメージ設定
    PLAYER_ATTACK_DAMAGE = 30
    DEFAULT_ENEMY_DAMAGE = 20
    
    # 敵タイプ別ダメージ設定
    ENEMY_DAMAGE_TABLE = {
        "goblin": 15,
        "orc": 25,
        "dragon": 40,
        "boss": 50,
        "normal": 20
    }
    
    def __init__(self):
        self.combat_log: List[str] = []
    
    def player_attack_enemy(self, player: Character, enemy: Enemy, target_pos: Position) -> CombatResult:
        """
        プレイヤーが敵を攻撃する
        
        Args:
            player: プレイヤーキャラクター
            enemy: 攻撃対象の敵
            target_pos: 攻撃対象位置
            
        Returns:
            CombatResult: 戦闘結果
        """
        if not player.is_alive():
            return CombatResult(
                success=False,
                messages=["プレイヤーが行動不能です"]
            )
        
        if not enemy.is_alive():
            return CombatResult(
                success=False,
                messages=["対象の敵は既に倒されています"]
            )
        
        # 攻撃範囲チェック（正面1マス）
        if not self._is_in_attack_range(player.position, player.direction, target_pos):
            return CombatResult(
                success=False,
                messages=["攻撃範囲外です"]
            )
        
        # ダメージ計算
        damage = self.PLAYER_ATTACK_DAMAGE
        actual_damage = enemy.take_damage(damage)
        
        messages = [f"プレイヤーの攻撃! {actual_damage}ダメージを与えた"]
        
        # 敵撃破判定
        defeated = not enemy.is_alive()
        if defeated:
            messages.append(f"敵を倒しました!")
        
        # 戦闘ログに記録
        log_message = f"Player -> Enemy: {actual_damage} damage"
        if defeated:
            log_message += " (DEFEATED)"
        self.combat_log.append(log_message)
        
        return CombatResult(
            success=True,
            attacker_damage_dealt=actual_damage,
            defender_damage_taken=actual_damage,
            defender_defeated=defeated,
            messages=messages
        )
    
    def enemy_attack_player(self, enemy: Enemy, player: Character) -> CombatResult:
        """
        敵がプレイヤーを攻撃する
        
        Args:
            enemy: 攻撃する敵
            player: プレイヤーキャラクター
            
        Returns:
            CombatResult: 戦闘結果
        """
        if not enemy.is_alive():
            return CombatResult(
                success=False,
                messages=["敵が行動不能です"]
            )
        
        if not player.is_alive():
            return CombatResult(
                success=False,
                messages=["プレイヤーは既に倒されています"]
            )
        
        # 攻撃範囲チェック（隣接1マス）
        if not self._is_adjacent(enemy.position, player.position):
            return CombatResult(
                success=False,
                messages=["攻撃範囲外です"]
            )
        
        # ダメージ計算（敵の実際の攻撃力を使用）
        damage = enemy.attack_power
        
        actual_damage = player.take_damage(damage)
        
        messages = [f"敵の攻撃! {actual_damage}ダメージを受けた"]
        
        # プレイヤー敗北判定
        defeated = not player.is_alive()
        if defeated:
            messages.append("プレイヤーが倒されました...")
        
        # 戦闘ログに記録
        log_message = f"Enemy -> Player: {actual_damage} damage"
        if defeated:
            log_message += " (PLAYER DEFEATED)"
        self.combat_log.append(log_message)
        
        return CombatResult(
            success=True,
            attacker_damage_dealt=actual_damage,
            defender_damage_taken=actual_damage,
            attacker_defeated=defeated,
            messages=messages
        )
    
    def _is_in_attack_range(self, attacker_pos: Position, attacker_direction: Direction, 
                           target_pos: Position) -> bool:
        """攻撃範囲内かチェック（正面1マス）"""
        dx, dy = attacker_direction.get_offset()
        expected_pos = Position(attacker_pos.x + dx, attacker_pos.y + dy)
        return expected_pos == target_pos
    
    def _is_adjacent(self, pos1: Position, pos2: Position) -> bool:
        """隣接位置かチェック（8方向）"""
        dx = abs(pos1.x - pos2.x)
        dy = abs(pos1.y - pos2.y)
        return dx <= 1 and dy <= 1 and (dx + dy) > 0
    
    def get_enemies_in_attack_range(self, player_pos: Position, player_direction: Direction,
                                   enemies: List[Enemy]) -> List[Tuple[Enemy, Position]]:
        """攻撃範囲内の敵を取得"""
        dx, dy = player_direction.get_offset()
        target_pos = Position(player_pos.x + dx, player_pos.y + dy)
        
        enemies_in_range = []
        for enemy in enemies:
            if not enemy.is_alive():
                continue
                
            # 通常敵（1x1）
            if enemy.position == target_pos:
                enemies_in_range.append((enemy, target_pos))
            # 大型敵の場合は占有位置をチェック
            elif hasattr(enemy, 'get_occupied_positions'):
                occupied_positions = enemy.get_occupied_positions()
                if target_pos in occupied_positions:
                    enemies_in_range.append((enemy, target_pos))
        
        return enemies_in_range
    
    def clear_combat_log(self):
        """戦闘ログをクリア"""
        self.combat_log.clear()
    
    def get_combat_log(self) -> List[str]:
        """戦闘ログを取得"""
        return self.combat_log.copy()
    
    def get_combat_summary(self) -> Dict[str, Any]:
        """戦闘サマリーを取得"""
        return {
            "total_battles": len(self.combat_log),
            "combat_log": self.get_combat_log()
        }


# グローバル戦闘システムインスタンス
_combat_system = CombatSystem()

def get_combat_system() -> CombatSystem:
    """グローバル戦闘システムを取得"""
    return _combat_system

def reset_combat_system():
    """戦闘システムをリセット"""
    global _combat_system
    _combat_system = CombatSystem()