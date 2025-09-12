"""
コマンドパターン実装
学生の行動（turn_left, move, attack等）をコマンドとして実装
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any, Dict
from enum import Enum

from . import GameState, Position, Direction, ItemType
from .validator import Validator


class CommandResult(Enum):
    """コマンド実行結果"""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    INVALID = "invalid"
    ERROR = "error"


@dataclass
class ExecutionResult:
    """コマンド実行結果の詳細"""
    result: CommandResult
    message: str = ""
    old_position: Optional[Position] = None
    new_position: Optional[Position] = None
    damage_dealt: int = 0
    item_collected: Optional[str] = None
    extra_data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.extra_data is None:
            self.extra_data = {}
    
    @property
    def is_success(self) -> bool:
        """成功したかどうか"""
        return self.result == CommandResult.SUCCESS
    
    @property
    def is_failed(self) -> bool:
        """失敗したかどうか"""
        return self.result == CommandResult.FAILED
    
    @property
    def is_blocked(self) -> bool:
        """ブロックされたかどうか（壁にぶつかった等）"""
        return self.result == CommandResult.BLOCKED


@dataclass
class AttackResult(ExecutionResult):
    """攻撃結果の詳細"""
    target_defeated: bool = False
    target_hp_remaining: int = 0
    
    def __post_init__(self):
        super().__post_init__()


@dataclass
class PickupResult(ExecutionResult):
    """アイテム取得結果の詳細"""
    item_name: str = ""
    item_effect: Dict[str, int] = None
    auto_equipped: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        if self.item_effect is None:
            self.item_effect = {}


@dataclass
class WaitResult(ExecutionResult):
    """待機結果の詳細"""
    enemy_actions_triggered: int = 0
    
    def __post_init__(self):
        super().__post_init__()


class Command(ABC):
    """コマンドベースクラス"""
    
    def __init__(self):
        self.executed = False
        self.result: Optional[ExecutionResult] = None
    
    @abstractmethod
    def execute(self, game_state: GameState) -> ExecutionResult:
        """コマンドを実行"""
        pass
    
    @abstractmethod
    def undo(self, game_state: GameState) -> bool:
        """コマンドを取り消し（可能な場合）"""
        pass
    
    @abstractmethod
    def can_undo(self) -> bool:
        """取り消し可能かどうか"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """コマンドの説明を取得"""
        pass


class TurnLeftCommand(Command):
    """左回転コマンド"""
    
    def execute(self, game_state: GameState) -> ExecutionResult:
        """左に90度回転"""
        old_direction = game_state.player.direction
        new_direction = old_direction.turn_left()
        
        # 実際に回転を実行
        game_state.player.direction = new_direction
        
        result = ExecutionResult(
            result=CommandResult.SUCCESS,
            message=f"{old_direction.value}から{new_direction.value}に回転しました",
            extra_data={
                "old_direction": old_direction.value,
                "new_direction": new_direction.value
            }
        )
        
        self.executed = True
        self.result = result
        return result
    
    def undo(self, game_state: GameState) -> bool:
        """右回転で取り消し"""
        if not self.can_undo():
            return False
        
        game_state.player.direction = game_state.player.direction.turn_right()
        self.executed = False
        return True
    
    def can_undo(self) -> bool:
        """常に取り消し可能"""
        return self.executed
    
    def get_description(self) -> str:
        return "左に90度回転"


class TurnRightCommand(Command):
    """右回転コマンド"""
    
    def execute(self, game_state: GameState) -> ExecutionResult:
        """右に90度回転"""
        old_direction = game_state.player.direction
        new_direction = old_direction.turn_right()
        
        # 実際に回転を実行
        game_state.player.direction = new_direction
        
        result = ExecutionResult(
            result=CommandResult.SUCCESS,
            message=f"{old_direction.value}から{new_direction.value}に回転しました",
            extra_data={
                "old_direction": old_direction.value,
                "new_direction": new_direction.value
            }
        )
        
        self.executed = True
        self.result = result
        return result
    
    def undo(self, game_state: GameState) -> bool:
        """左回転で取り消し"""
        if not self.can_undo():
            return False
        
        game_state.player.direction = game_state.player.direction.turn_left()
        self.executed = False
        return True
    
    def can_undo(self) -> bool:
        """常に取り消し可能"""
        return self.executed
    
    def get_description(self) -> str:
        return "右に90度回転"


class MoveCommand(Command):
    """移動コマンド"""
    
    def execute(self, game_state: GameState) -> ExecutionResult:
        """正面方向に1マス移動"""
        player = game_state.player
        validator = Validator()
        
        old_position = player.position
        
        # Validatorを使用した移動可能性チェック
        movement_result = validator.validate_movement(
            old_position, player.direction, game_state
        )
        
        if not movement_result.is_valid:
            # 移動不可能
            result = ExecutionResult(
                result=CommandResult.BLOCKED,
                message=f"{movement_result.reason}。移動できません",
                old_position=old_position,
                new_position=old_position
            )
        else:
            # 移動実行
            new_position = movement_result.target_position
            player.position = new_position
            result = ExecutionResult(
                result=CommandResult.SUCCESS,
                message=f"({old_position.x}, {old_position.y})から({new_position.x}, {new_position.y})に移動しました",
                old_position=old_position,
                new_position=new_position
            )
        
        self.executed = True
        self.result = result
        return result
    
    def undo(self, game_state: GameState) -> bool:
        """元の位置に戻す"""
        if not self.can_undo():
            return False
        
        if self.result and self.result.old_position:
            game_state.player.position = self.result.old_position
            self.executed = False
            return True
        return False
    
    def can_undo(self) -> bool:
        """成功した移動のみ取り消し可能"""
        return self.executed and self.result and self.result.is_success
    
    def get_description(self) -> str:
        return "正面方向に1マス移動"


class AttackCommand(Command):
    """攻撃コマンド"""
    
    def execute(self, game_state: GameState) -> AttackResult:
        """正面1マスを攻撃"""
        player = game_state.player
        validator = Validator()
        
        # Validatorを使用した攻撃対象チェック
        can_attack, enemy, message = validator.can_attack_target(
            player.position, player.direction, game_state
        )
        
        if not can_attack:
            result = AttackResult(
                result=CommandResult.FAILED,
                message=message
            )
        else:
            # 攻撃実行
            damage = player.attack_power
            actual_damage = enemy.take_damage(damage)
            
            defeated = not enemy.is_alive()
            if defeated:
                # 敵を削除
                game_state.enemies.remove(enemy)
            
            # カウンター攻撃処理は _process_enemy_turns で統一処理
            # AttackCommand での即座の反撃は無効化（重複攻撃を防ぐ）
            counter_message = ""
            counter_damage = 0
            player_defeated = False
            
            
            # メッセージ構築
            base_message = f"敵に{actual_damage}ダメージを与えました"
            if defeated:
                base_message += "（敵を倒した）"
            else:
                base_message += " → 敵のターンで反撃があります"
            
            result = AttackResult(
                result=CommandResult.SUCCESS,
                message=base_message,
                damage_dealt=actual_damage,
                target_defeated=defeated,
                target_hp_remaining=enemy.hp if not defeated else 0,
                extra_data={
                    "enemy_position": enemy.position,
                    "counter_damage": counter_damage,
                    "player_defeated": player_defeated
                }
            )
        
        self.executed = True
        self.result = result
        return result
    
    def undo(self, game_state: GameState) -> bool:
        """攻撃は基本的に取り消し不可"""
        return False
    
    def can_undo(self) -> bool:
        """攻撃は取り消し不可"""
        return False
    
    def get_description(self) -> str:
        return "正面1マスを攻撃"


class PickupCommand(Command):
    """アイテム取得コマンド"""
    
    def execute(self, game_state: GameState) -> PickupResult:
        """足元のアイテムを取得"""
        player = game_state.player
        current_pos = player.position
        
        # アイテムの存在チェック
        item = game_state.get_item_at(current_pos)
        if item is None:
            result = PickupResult(
                result=CommandResult.FAILED,
                message="ここにはアイテムがありません"
            )
        else:
            # アイテム取得実行
            game_state.items.remove(item)
            
            # 自動装備処理（簡単な実装）
            auto_equipped = item.auto_equip
            if auto_equipped:
                # 攻撃力や防御力を適用（簡易実装）
                if "attack" in item.effect:
                    player.attack_power += item.effect["attack"]
                # 他の効果も必要に応じて実装
            
            result = PickupResult(
                result=CommandResult.SUCCESS,
                message=f"{item.name}を取得しました" + ("（自動装備）" if auto_equipped else ""),
                item_collected=item.name,
                item_name=item.name,
                item_effect=item.effect.copy(),
                auto_equipped=auto_equipped,
                extra_data={"item_type": item.item_type.value}
            )
        
        self.executed = True
        self.result = result
        return result
    
    def undo(self, game_state: GameState) -> bool:
        """アイテム取得は基本的に取り消し不可"""
        return False
    
    def can_undo(self) -> bool:
        """アイテム取得は取り消し不可"""
        return False
    
    def get_description(self) -> str:
        return "足元のアイテムを取得"


class WaitCommand(Command):
    """待機コマンド"""
    
    def execute(self, game_state: GameState) -> WaitResult:
        """1ターン待機"""
        # プレイヤーは何もせず1ターンを過ごす
        # 敵の処理はGameStateManagerの_update_game_state()で行われる
        
        result = WaitResult(
            result=CommandResult.SUCCESS,
            message="1ターン待機しました",
            enemy_actions_triggered=0
        )
        
        self.executed = True
        self.result = result
        return result
    
    def undo(self, game_state: GameState) -> bool:
        """待機は取り消し不可"""
        return False
    
    def can_undo(self) -> bool:
        """待機は取り消し不可"""
        return False
    
    def get_description(self) -> str:
        return "1ターン待機"


class CommandInvoker:
    """コマンド実行管理クラス"""
    
    def __init__(self):
        self.history: list[Command] = []
        self.current_index = -1
    
    def execute_command(self, command: Command, game_state: GameState) -> ExecutionResult:
        """コマンドを実行し、履歴に追加"""
        result = command.execute(game_state)
        
        # 履歴に追加（現在位置以降を削除してから追加）
        self.history = self.history[:self.current_index + 1]
        self.history.append(command)
        self.current_index += 1
        
        return result
    
    def undo_last_command(self, game_state: GameState) -> bool:
        """最後のコマンドを取り消し"""
        if self.current_index < 0:
            return False
        
        command = self.history[self.current_index]
        if command.can_undo():
            success = command.undo(game_state)
            if success:
                self.current_index -= 1
            return success
        return False
    
    def can_undo(self) -> bool:
        """取り消し可能かチェック"""
        if self.current_index < 0:
            return False
        return self.history[self.current_index].can_undo()
    
    def get_history(self) -> list[str]:
        """実行履歴を取得"""
        return [cmd.get_description() for cmd in self.history[:self.current_index + 1]]
    
    def clear_history(self) -> None:
        """履歴をクリア"""
        self.history.clear()
        self.current_index = -1


# エクスポート用
__all__ = [
    "Command", "ExecutionResult", "AttackResult", "PickupResult", "WaitResult",
    "CommandResult", "CommandInvoker",
    "TurnLeftCommand", "TurnRightCommand", "MoveCommand", 
    "AttackCommand", "PickupCommand", "WaitCommand"
]