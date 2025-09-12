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
                       max_turns: int = 100,
                       player_hp: Optional[int] = None,
                       player_max_hp: Optional[int] = None,
                       player_attack_power: Optional[int] = None) -> GameState:
        """ゲームを初期化"""
        if enemies is None:
            enemies = []
        if items is None:
            items = []
        
        # プレイヤーのステータス決定（ステージ設定 > デフォルト値）
        final_hp = player_hp if player_hp is not None else 100
        final_max_hp = player_max_hp if player_max_hp is not None else final_hp
        final_attack_power = player_attack_power if player_attack_power is not None else 30
        
        # プレイヤー作成
        player = Character(
            position=player_start,
            direction=player_direction,
            hp=final_hp,
            max_hp=final_max_hp,
            attack_power=final_attack_power
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
        
        # ゲーム状態の更新（成功・失敗に関わらずターン消費）
        self._update_game_state()
        
        return result
    
    def _update_game_state(self):
        """ゲーム状態を更新（ターン増加、勝利判定など）"""
        if self.current_state is None:
            return
        
        # ターン数増加
        self.current_state.increment_turn()
        
        # 敵のターン処理を実行
        self._process_enemy_turns()
        
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
    
    def _process_enemy_turns(self):
        """敵のターン処理"""
        if self.current_state is None:
            return
            
        player = self.current_state.player
        
        # 各敵のAI行動を実行
        for enemy in self.current_state.enemies:
            if not enemy.is_alive():
                continue
            
            # プレイヤーを視認できるかチェック（壁による視線遮蔽を考慮）
            can_see = enemy.can_see_player(player.position, self.current_state.board)
            
            # 重要な状態変化のみログ出力
            
            # プレイヤーを発見した場合は警戒状態にする
            if can_see:
                if not enemy.alerted:
                    print(f"🚨 敵がプレイヤーを発見！警戒状態に移行")
                enemy.alerted = True
                enemy.alert_cooldown = 10  # 10ターンの間追跡を続ける（持続性向上）
                # 最後に見た位置を更新
                enemy.last_seen_player = Position(player.position.x, player.position.y)
            elif enemy.alert_cooldown > 0:
                # 見失っても一定時間追跡を続ける
                enemy.alert_cooldown -= 1
                print(f"🔍 追跡中... クールダウン残り{enemy.alert_cooldown}ターン")
                if enemy.alert_cooldown <= 0:
                    enemy.alerted = False
                    print(f"😴 警戒解除: 巡回モードに復帰")
            
            # 警戒状態または隣接時のみ積極的行動
            distance = abs(player.position.x - enemy.position.x) + abs(player.position.y - enemy.position.y)
            if enemy.alerted or distance == 1:
                print(f"⚔️ 敵が積極的行動開始: 警戒={enemy.alerted} 距離={distance}")
                # 敵とプレイヤーの位置関係を計算
                dx = player.position.x - enemy.position.x
                dy = player.position.y - enemy.position.y
                distance = abs(dx) + abs(dy)  # マンハッタン距離
                
                # 隣接している場合（距離1）の処理
                if distance == 1:
                    print(f"⚔️ 隣接判定: 敵[{enemy.position.x},{enemy.position.y}] → プレイヤー[{player.position.x},{player.position.y}]")
                    
                    # 攻撃に必要な方向を計算
                    if abs(dx) > abs(dy):
                        required_direction = Direction.EAST if dx > 0 else Direction.WEST
                    else:
                        required_direction = Direction.SOUTH if dy > 0 else Direction.NORTH
                    
                    # 既に正しい方向を向いている場合のみ攻撃実行
                    if enemy.direction == required_direction:
                        # プレイヤーを攻撃
                        damage = enemy.attack_power
                        actual_damage = player.take_damage(damage)
                        print(f"💀 敵の攻撃！ {actual_damage}ダメージ (プレイヤーHP: {player.hp}/{player.max_hp})")
                        
                        if not player.is_alive():
                            print(f"☠️ プレイヤー死亡！")
                            self.current_state.status = GameStatus.FAILED
                    else:
                        # 正しい方向を向いていない場合は方向転換のみ（1ターン消費）
                        print(f"🔄 攻撃前方向転換: {enemy.direction.value} → {required_direction.value}")
                        enemy.direction = required_direction
                
                # 隣接していない場合は1マス近づく移動を試みる（警戒状態のみ）
                elif distance > 1 and enemy.alerted:
                    # 追跡目標を決定（現在のプレイヤー位置 or 最後に見た位置）
                    target_position = player.position if can_see else enemy.last_seen_player
                    if target_position is None:
                        target_position = player.position  # フォールバック
                    
                    # 最後に見た位置に到達しているが、プレイヤーが見つからない場合の探索強化
                    if (not can_see and enemy.last_seen_player is not None and 
                        enemy.position == enemy.last_seen_player):
                        print(f"🔍 最後の目撃地点に到達: 周辺探索モードに移行")
                        # プレイヤーの現在位置を新たな目標として更新（推測に基づく）
                        target_position = player.position
                    
                    target_dx = target_position.x - enemy.position.x
                    target_dy = target_position.y - enemy.position.y
                    target_distance = abs(target_dx) + abs(target_dy)
                    
                    print(f"🏃 追跡開始: 敵[{enemy.position.x},{enemy.position.y}] → 目標[{target_position.x},{target_position.y}] 距離={target_distance} ({'直視' if can_see else '記憶'})")
                    # 目標位置に最も近づく方向を決定（接触維持を優先した改良版）
                    required_direction = None
                    if abs(target_dx) > abs(target_dy):
                        required_direction = Direction.EAST if target_dx > 0 else Direction.WEST
                        print(f"🏃 x軸優先追跡: target_dx={target_dx}, 選択方向={required_direction.value}")
                    elif abs(target_dy) > abs(target_dx):
                        required_direction = Direction.SOUTH if target_dy > 0 else Direction.NORTH
                        print(f"🏃 y軸優先追跡: target_dy={target_dy}, 選択方向={required_direction.value}")
                    else:
                        # 同一距離の場合は接触維持を重視してx軸を優先
                        required_direction = Direction.EAST if target_dx > 0 else Direction.WEST
                        print(f"🏃 同一距離追跡（接触重視x軸優先）: target_dx={target_dx}, target_dy={target_dy}, 選択方向={required_direction.value}")
                    
                    # 既に正しい方向を向いているかチェック
                    if enemy.direction != required_direction:
                        # 方向転換のみ（1ターン消費）
                        print(f"🔄 追跡方向転換: {enemy.direction.value} → {required_direction.value}")
                        enemy.direction = required_direction
                    else:
                        # 正しい方向を向いているので移動実行
                        offset_x, offset_y = required_direction.get_offset()
                        new_position = Position(enemy.position.x + offset_x, enemy.position.y + offset_y)
                        
                        print(f"🏃 追跡移動試行: [{enemy.position.x},{enemy.position.y}] → [{new_position.x},{new_position.y}]")
                        
                        # 移動先が有効で通行可能な場合のみ移動
                        if (self.current_state.board.is_passable(new_position) and 
                            self.current_state.get_enemy_at(new_position) is None and
                            new_position != player.position):
                            
                            print(f"✅ 追跡移動成功: [{enemy.position.x},{enemy.position.y}] → [{new_position.x},{new_position.y}]")
                            enemy.position = new_position
                        else:
                            print(f"❌ 追跡移動失敗: 通行不可 または 他の敵 または プレイヤー位置")
                            # 壁に詰まった場合、代替ルートを試す
                            print(f"🔄 代替ルート検索中...")
                            alternative_directions = []
                            if required_direction in [Direction.EAST, Direction.WEST]:
                                # x軸移動が失敗した場合、y軸を試す
                                if target_dy > 0:
                                    alternative_directions.append(Direction.SOUTH)
                                elif target_dy < 0:
                                    alternative_directions.append(Direction.NORTH)
                            elif required_direction in [Direction.NORTH, Direction.SOUTH]:
                                # y軸移動が失敗した場合、x軸を試す
                                if target_dx > 0:
                                    alternative_directions.append(Direction.EAST)
                                elif target_dx < 0:
                                    alternative_directions.append(Direction.WEST)
                            
                            # 代替方向がない場合は全方向を試す（デッドロック回避）
                            if not alternative_directions:
                                print("🔄 全方向探索モードに切り替え")
                                all_directions = [Direction.EAST, Direction.WEST, Direction.NORTH, Direction.SOUTH]
                                for dir_candidate in all_directions:
                                    if dir_candidate != required_direction:
                                        alternative_directions.append(dir_candidate)
                            
                            # 代替方向を試行
                            for alt_direction in alternative_directions:
                                alt_offset_x, alt_offset_y = alt_direction.get_offset()
                                alt_position = Position(enemy.position.x + alt_offset_x, enemy.position.y + alt_offset_y)
                                
                                if (self.current_state.board.is_passable(alt_position) and 
                                    self.current_state.get_enemy_at(alt_position) is None and
                                    alt_position != player.position):
                                    
                                    print(f"✅ 代替ルート成功: [{enemy.position.x},{enemy.position.y}] → [{alt_position.x},{alt_position.y}] (方向:{alt_direction.value})")
                                    if enemy.direction != alt_direction:
                                        print(f"🔄 代替方向転換: {enemy.direction.value} → {alt_direction.value}")
                                        enemy.direction = alt_direction
                                    else:
                                        enemy.position = alt_position
                                    break
                            else:
                                print(f"❌ 全ての代替ルートが失敗")
            
            # 非警戒状態では基本行動パターンを実行
            elif not enemy.alerted:
                print(f"🌀 敵は非警戒状態: 巡回モード")
                # patrol: 巡回処理
                if enemy.behavior_pattern == "patrol" and enemy.patrol_path:
                    current_target = enemy.get_next_patrol_position()
                    if current_target:
                        # 目標位置に到達したかチェック
                        if enemy.position == current_target:
                            # 目標到達（デバッグログ削除）
                            # 次のパトロールポイントに進む
                            enemy.advance_patrol()
                            current_target = enemy.get_next_patrol_position()
                            # 新しい目標設定（デバッグログ削除）
                        
                        if current_target and current_target != enemy.position:
                            # デバッグログ：敵の現在位置と目標位置
                            # 敵巡回処理（デバッグログ削除）
                            
                            # 目標に向かう方向を計算
                            dx = current_target.x - enemy.position.x
                            dy = current_target.y - enemy.position.y
                            
                            # 巡回パスに従って正確に移動するため、x軸優先で移動
                            # まずx方向の差を解消してからy方向に移動
                            if dx != 0:
                                required_direction = Direction.EAST if dx > 0 else Direction.WEST
                                # x軸移動（デバッグログ削除）
                            elif dy != 0:
                                required_direction = Direction.SOUTH if dy > 0 else Direction.NORTH
                                # y軸移動（デバッグログ削除）
                            else:
                                # 既に目標位置にいる場合（通常は発生しない）
                                required_direction = enemy.direction
                                # 目標位置到達（デバッグログ削除）
                            
                            # 既に正しい方向を向いているかチェック
                            if enemy.direction != required_direction:
                                # 方向転換のみ（1ターン消費）
                                enemy.direction = required_direction
                            else:
                                # 正しい方向を向いているので移動実行
                                offset_x, offset_y = required_direction.get_offset()
                                new_position = Position(enemy.position.x + offset_x, enemy.position.y + offset_y)
                                
                                # 移動可能性をチェック
                                if (self.current_state.board.is_passable(new_position) and 
                                    self.current_state.get_enemy_at(new_position) is None and
                                    new_position != player.position):
                                    
                                    enemy.position = new_position
                # static: その場で待機（何もしない）
    
    def get_current_state(self) -> Optional[GameState]:
        """現在のゲーム状態を取得"""
        # Thread safety: current_stateのスナップショットを取得
        current_state_snapshot = self.current_state
        
        # デバッグ用: 返す値のタイプをチェック
        if current_state_snapshot is not None:
            state_type = type(current_state_snapshot).__name__
            if state_type != "GameState":
                import traceback
                logger.error(f"🚨 get_current_state() 異常: expected GameState, got {state_type} - {current_state_snapshot}")
                print(f"🚨 get_current_state() Reset後の型エラー:")
                print(f"   期待: GameState, 実際: {state_type}")
                print(f"   値: {current_state_snapshot}")
                print(f"   呼び出し元スタック:")
                traceback.print_stack()
                # 異常な場合、Noneを返してクラッシュを防ぐ
                return None
        return current_state_snapshot
    
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
            # patrol_pathのコピー
            patrol_path_copy = []
            if enemy.patrol_path:
                for pos in enemy.patrol_path:
                    patrol_path_copy.append(Position(pos.x, pos.y))
            
            enemy_copy = Enemy(
                position=Position(enemy.position.x, enemy.position.y),
                direction=enemy.direction,
                hp=enemy.hp,
                max_hp=enemy.max_hp,
                attack_power=enemy.attack_power,
                enemy_type=enemy.enemy_type,
                behavior_pattern=enemy.behavior_pattern,
                is_angry=enemy.is_angry,
                vision_range=enemy.vision_range,
                alerted=enemy.alerted,
                patrol_path=patrol_path_copy,
                current_patrol_index=enemy.current_patrol_index,
                alert_cooldown=enemy.alert_cooldown
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