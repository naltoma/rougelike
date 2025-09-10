"""
ゲーム状態管理システム
GameStateManagerクラスの実装
"""

from typing import List, Optional, Any, Dict
from . import GameState, Character, Enemy, Item, Board, Position, Direction, GameStatus
from .commands import Command, ExecutionResult, CommandInvoker, CommandResult


class GameStateManager:
    """ゲーム状態を管理するメインクラス"""
    
    def __init__(self):
        self.current_state: Optional[GameState] = None
        self.command_invoker = CommandInvoker()
        self.initial_state: Optional[GameState] = None
    
    def initialize_game(self, 
                       player_start: Position,
                       player_direction: Direction,
                       board: Board,
                       enemies: Optional[List[Enemy]] = None,
                       items: Optional[List[Item]] = None,
                       goal_position: Optional[Position] = None,
                       max_turns: int = 100) -> GameState:
        """ゲームを初期化"""
        if enemies is None:
            enemies = []
        if items is None:
            items = []
        
        # プレイヤー作成
        player = Character(
            position=player_start,
            direction=player_direction,
            hp=100,
            attack_power=30
        )
        
        # ゲーム状態作成
        self.current_state = GameState(
            player=player,
            enemies=enemies.copy(),  # リストのコピーを作成
            items=items.copy(),      # リストのコピーを作成
            board=board,
            turn_count=0,
            max_turns=max_turns,
            status=GameStatus.PLAYING,
            goal_position=goal_position
        )
        
        # 初期状態を保存（リセット用）
        self.initial_state = self._copy_game_state(self.current_state)
        
        # コマンド履歴をクリア
        self.command_invoker.clear_history()
        
        return self.current_state
    
    def execute_command(self, command: Command) -> ExecutionResult:
        """コマンドを実行してゲーム状態を更新"""
        if self.current_state is None:
            raise RuntimeError("ゲームが初期化されていません")
        
        if self.current_state.is_game_over():
            result = ExecutionResult(
                result=CommandResult.FAILED,
                message="ゲームが終了しています"
            )
            return result
        
        # コマンド実行
        result = self.command_invoker.execute_command(command, self.current_state)
        
        # ゲーム状態の更新
        if result.is_success:
            self._update_game_state()
        
        return result
    
    def _update_game_state(self):
        """ゲーム状態を更新（ターン増加、勝利判定など）"""
        if self.current_state is None:
            return
        
        # ターン数増加
        self.current_state.increment_turn()
        
        # プレイヤー死亡判定
        if not self.current_state.player.is_alive():
            self.current_state.status = GameStatus.FAILED
            return
        
        # v1.2.6: 勝利条件チェック（敵を倒してからゴール到達）
        if hasattr(self.current_state, 'check_victory_conditions'):
            if self.current_state.check_victory_conditions():
                self.current_state.status = GameStatus.WON
                return
        else:
            # フォールバック：従来のゴール到達判定
            if self.current_state.check_goal_reached():
                self.current_state.status = GameStatus.WON
                return
        
        # 敵が全滅した場合の処理（将来の拡張用）
        # ゴールが設定されておらず、敵もいない場合は勝利
        # ただし、初期状態（ターン0）では勝利としない
        if (not self.current_state.enemies and 
            self.current_state.goal_position is None and 
            self.current_state.turn_count > 0):
            self.current_state.status = GameStatus.WON
    
    def get_current_state(self) -> Optional[GameState]:
        """現在のゲーム状態を取得"""
        return self.current_state
    
    def is_game_finished(self) -> bool:
        """ゲーム終了判定"""
        if self.current_state is None:
            return True
        return self.current_state.is_game_over()
    
    def get_game_result(self) -> GameStatus:
        """ゲーム結果を取得"""
        if self.current_state is None:
            return GameStatus.ERROR
        return self.current_state.status
    
    def can_undo_last_action(self) -> bool:
        """最後のアクションを取り消し可能かチェック"""
        return self.command_invoker.can_undo()
    
    def undo_last_action(self) -> bool:
        """最後のアクションを取り消し"""
        if self.current_state is None:
            return False
        
        success = self.command_invoker.undo_last_command(self.current_state)
        
        if success:
            # ゲーム状態を前の状態に戻す
            if self.current_state.turn_count > 0:
                self.current_state.turn_count -= 1
            
            # ゲーム終了状態をリセット（必要に応じて）
            if self.current_state.status != GameStatus.PLAYING:
                self.current_state.status = GameStatus.PLAYING
        
        return success
    
    def reset_game(self) -> bool:
        """ゲームをリセット"""
        if self.initial_state is None:
            return False
        
        self.current_state = self._copy_game_state(self.initial_state)
        self.command_invoker.clear_history()
        return True
    
    def get_action_history(self) -> List[str]:
        """アクション履歴を取得"""
        return self.command_invoker.get_history()
    
    def get_turn_count(self) -> int:
        """現在のターン数を取得"""
        if self.current_state is None:
            return 0
        return self.current_state.turn_count
    
    def get_max_turns(self) -> int:
        """最大ターン数を取得"""
        if self.current_state is None:
            return 0
        return self.current_state.max_turns
    
    def get_remaining_turns(self) -> int:
        """残りターン数を取得"""
        if self.current_state is None:
            return 0
        return max(0, self.current_state.max_turns - self.current_state.turn_count)
    
    def _copy_game_state(self, state: GameState) -> GameState:
        """ゲーム状態の深いコピーを作成"""
        # プレイヤーのコピー
        player_copy = Character(
            position=Position(state.player.position.x, state.player.position.y),
            direction=state.player.direction,
            hp=state.player.hp,
            max_hp=state.player.max_hp,
            attack_power=state.player.attack_power
        )
        
        # 敵のコピー
        enemies_copy = []
        for enemy in state.enemies:
            enemy_copy = Enemy(
                position=Position(enemy.position.x, enemy.position.y),
                direction=enemy.direction,
                hp=enemy.hp,
                max_hp=enemy.max_hp,
                attack_power=enemy.attack_power,
                enemy_type=enemy.enemy_type,
                behavior_pattern=enemy.behavior_pattern,
                is_angry=enemy.is_angry
            )
            enemies_copy.append(enemy_copy)
        
        # アイテムのコピー
        items_copy = []
        for item in state.items:
            item_copy = Item(
                position=Position(item.position.x, item.position.y),
                item_type=item.item_type,
                name=item.name,
                effect=item.effect.copy(),
                auto_equip=item.auto_equip
            )
            items_copy.append(item_copy)
        
        # ゴール位置のコピー
        goal_copy = None
        if state.goal_position:
            goal_copy = Position(state.goal_position.x, state.goal_position.y)
        
        return GameState(
            player=player_copy,
            enemies=enemies_copy,
            items=items_copy,
            board=state.board,  # ボードは不変なのでそのまま
            turn_count=state.turn_count,
            max_turns=state.max_turns,
            status=state.status,
            goal_position=goal_copy
        )


# エクスポート用
__all__ = ["GameStateManager"]