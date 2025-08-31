"""
移動と衝突判定システム
Validatorクラスの実装
"""

from typing import List, Optional, Tuple
from . import GameState, Position, Direction, Character, Enemy, Board


class MovementResult:
    """移動結果の詳細クラス"""
    
    def __init__(self, 
                 is_valid: bool, 
                 reason: str = "", 
                 blocked_by: str = "",
                 target_position: Optional[Position] = None):
        self.is_valid = is_valid
        self.reason = reason
        self.blocked_by = blocked_by
        self.target_position = target_position
    
    @property
    def is_blocked(self) -> bool:
        """移動がブロックされているか"""
        return not self.is_valid


class Validator:
    """移動可能性チェックと衝突検出クラス"""
    
    def __init__(self):
        pass
    
    def validate_movement(self, 
                         current_pos: Position, 
                         direction: Direction, 
                         game_state: GameState) -> MovementResult:
        """移動可能性を総合的にチェック"""
        target_pos = current_pos.move(direction)
        
        # 1. 境界値チェック
        if not self._is_within_bounds(target_pos, game_state.board):
            return MovementResult(
                is_valid=False,
                reason="ボードの境界外です",
                blocked_by="boundary",
                target_position=target_pos
            )
        
        # 2. 壁衝突チェック
        if self._is_wall_collision(target_pos, game_state.board):
            return MovementResult(
                is_valid=False,
                reason="壁があります",
                blocked_by="wall",
                target_position=target_pos
            )
        
        # 3. 移動禁止マスチェック
        if self._is_forbidden_cell(target_pos, game_state.board):
            return MovementResult(
                is_valid=False,
                reason="移動不可マスです",
                blocked_by="forbidden",
                target_position=target_pos
            )
        
        # 4. 敵との衝突チェック
        enemy_collision = self._check_enemy_collision(target_pos, game_state.enemies)
        if enemy_collision:
            return MovementResult(
                is_valid=False,
                reason="敵がいます",
                blocked_by="enemy",
                target_position=target_pos
            )
        
        # 全てのチェックをパス
        return MovementResult(
            is_valid=True,
            reason="移動可能です",
            target_position=target_pos
        )
    
    def _is_within_bounds(self, pos: Position, board: Board) -> bool:
        """境界値チェック"""
        return board.is_valid_position(pos)
    
    def _is_wall_collision(self, pos: Position, board: Board) -> bool:
        """壁衝突検出"""
        return board.is_wall(pos)
    
    def _is_forbidden_cell(self, pos: Position, board: Board) -> bool:
        """移動禁止マスチェック"""
        return board.is_forbidden(pos)
    
    def _check_enemy_collision(self, pos: Position, enemies: List[Enemy]) -> bool:
        """敵との衝突チェック"""
        for enemy in enemies:
            if pos in enemy.get_occupied_positions():
                return True
        return False
    
    def can_attack_target(self, 
                         attacker_pos: Position, 
                         attacker_direction: Direction, 
                         game_state: GameState) -> Tuple[bool, Optional[Enemy], str]:
        """攻撃対象がいるかチェック"""
        target_pos = attacker_pos.move(attacker_direction)
        
        # 攻撃範囲チェック（ボード内か）
        if not game_state.board.is_valid_position(target_pos):
            return False, None, "攻撃範囲外です"
        
        # 攻撃対象の敵を探す
        for enemy in game_state.enemies:
            if target_pos in enemy.get_occupied_positions():
                return True, enemy, "攻撃対象があります"
        
        return False, None, "攻撃対象がいません"
    
    def validate_player_direction(self, direction: Direction) -> bool:
        """プレイヤーの向きの妥当性チェック"""
        return isinstance(direction, Direction)
    
    def get_reachable_positions(self, 
                               start_pos: Position, 
                               game_state: GameState, 
                               max_steps: int = 10) -> List[Position]:
        """到達可能な位置を取得（BFS アルゴリズム）"""
        visited = set()
        queue = [(start_pos, 0)]  # (position, steps)
        reachable = []
        
        while queue:
            current_pos, steps = queue.pop(0)
            
            if current_pos in visited or steps > max_steps:
                continue
            
            visited.add(current_pos)
            reachable.append(current_pos)
            
            # 4方向への移動を試行
            for direction in Direction:
                movement_result = self.validate_movement(current_pos, direction, game_state)
                if movement_result.is_valid and movement_result.target_position:
                    target_pos = movement_result.target_position
                    if target_pos not in visited:
                        queue.append((target_pos, steps + 1))
        
        return reachable
    
    def is_goal_reachable(self, 
                         start_pos: Position, 
                         goal_pos: Position, 
                         game_state: GameState) -> bool:
        """ゴールに到達可能かチェック"""
        reachable_positions = self.get_reachable_positions(start_pos, game_state, max_steps=50)
        return goal_pos in reachable_positions
    
    def get_movement_cost(self, 
                         from_pos: Position, 
                         to_pos: Position, 
                         game_state: GameState) -> int:
        """移動コストを計算（将来の拡張用）"""
        # 現在は単純に距離を返す
        return int(from_pos.distance_to(to_pos))
    
    def validate_large_enemy_movement(self, 
                                     enemy: Enemy, 
                                     target_direction: Direction, 
                                     game_state: GameState) -> MovementResult:
        """大型敵の移動可能性をチェック"""
        enemy_size = enemy.get_size()
        current_pos = enemy.position
        target_pos = current_pos.move(target_direction)
        
        # 大型敵が占有する全ての座標をチェック
        for dx in range(enemy_size[0]):
            for dy in range(enemy_size[1]):
                check_pos = Position(target_pos.x + dx, target_pos.y + dy)
                
                # 境界チェック
                if not self._is_within_bounds(check_pos, game_state.board):
                    return MovementResult(
                        is_valid=False,
                        reason=f"大型敵の一部が境界外になります ({check_pos.x}, {check_pos.y})",
                        blocked_by="boundary",
                        target_position=target_pos
                    )
                
                # 壁チェック
                if self._is_wall_collision(check_pos, game_state.board):
                    return MovementResult(
                        is_valid=False,
                        reason=f"大型敵の一部が壁と衝突します ({check_pos.x}, {check_pos.y})",
                        blocked_by="wall",
                        target_position=target_pos
                    )
                
                # プレイヤーとの衝突チェック
                if check_pos == game_state.player.position:
                    return MovementResult(
                        is_valid=False,
                        reason="プレイヤーと衝突します",
                        blocked_by="player",
                        target_position=target_pos
                    )
                
                # 他の敵との衝突チェック
                for other_enemy in game_state.enemies:
                    if other_enemy != enemy and check_pos in other_enemy.get_occupied_positions():
                        return MovementResult(
                            is_valid=False,
                            reason="他の敵と衝突します",
                            blocked_by="enemy",
                            target_position=target_pos
                        )
        
        return MovementResult(
            is_valid=True,
            reason="大型敵の移動が可能です",
            target_position=target_pos
        )
    
    def get_adjacent_positions(self, pos: Position, game_state: GameState) -> List[Position]:
        """隣接する移動可能な位置を取得"""
        adjacent = []
        for direction in Direction:
            movement_result = self.validate_movement(pos, direction, game_state)
            if movement_result.is_valid and movement_result.target_position:
                adjacent.append(movement_result.target_position)
        return adjacent


# エクスポート用
__all__ = ["Validator", "MovementResult"]