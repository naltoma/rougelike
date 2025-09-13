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
        self.special_error_handler: Optional[SpecialErrorHandler] = None
        # v1.2.8: 2x3敵用交互怒りモード履歴管理
        self.rage_mode_history: List[Dict[str, Any]] = []
    
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
                       player_attack_power: Optional[int] = None,
                       stage_id: Optional[str] = None,
                       error_config: Optional[Dict[str, Any]] = None) -> GameState:
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
            goal_position=goal_position,
            stage_id=stage_id  # ステージIDを設定
        )
        
        # 特殊ステージエラーハンドラーの初期化
        if stage_id:
            self.special_error_handler = SpecialErrorHandler(stage_id, error_config)
        
        # 初期状態を保存（リセット用）
        self.initial_state = self._copy_game_state(self.current_state)
        
        # コマンド履歴をクリア
        self.command_invoker.clear_history()
        
        # v1.2.8: 怒りモード履歴をクリア
        self.rage_mode_history = []
        
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
        
        # 特殊エラーハンドラーでアクションを記録
        if self.special_error_handler:
            action_name = command.__class__.__name__.lower().replace('command', '')
            context = {
                "turn": self.current_state.turn_count,
                "result": result.result.value,
                "message": result.message
            }
            self.special_error_handler.record_action(action_name, context)
        
        # ゲーム状態の更新（成功・失敗に関わらずターン消費）
        self._update_game_state()
        
        # 特殊条件チェック（コマンド実行後）- 2x3敵が存在する場合のみ
        if (self.special_error_handler and result.result == CommandResult.SUCCESS and 
            self._has_special_2x3_enemy_alive()):
            special_result = self.special_error_handler.check_special_conditions(self.current_state)
            if special_result:
                # 特殊エラーメッセージを結果に追加
                if special_result["type"] in ["wrong_sequence", "no_key_attack", "direct_attack"]:
                    result.message += f"\n💡 {special_result['message']}\nヒント: {special_result['hint']}"
                elif special_result["type"] == "success_sequence":
                    result.message += f"\n✨ {special_result['message']}"
                    # 影の王を即座に消滅させる
                    self._handle_special_enemy_elimination()
        
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
        
        # デバッグ: stage_idを確認
        print(f"🔧 _process_enemy_turns開始: stage_id={getattr(self.current_state, 'stage_id', 'None')}")
        
        # 各敵のAI行動を実行
        for enemy in self.current_state.enemies:
            if not enemy.is_alive():
                continue
            
            # Stage11/Stage12特別処理: stage11_special属性ベースでの判定
            if (hasattr(enemy, 'stage11_special') and enemy.stage11_special):
                # stage11_special=trueの敵は特殊行動パターン
                print(f"🔧 特殊敵処理開始: HP={enemy.hp}/{enemy.max_hp}")
                self._handle_stage11_enemy_behavior(enemy, player)
                continue
            
            # v1.2.8: 2x3敵特殊処理
            if (hasattr(enemy, 'enemy_type') and enemy.enemy_type.value == "special_2x3"):
                print(f"🔧 2x3特殊敵処理開始: HP={enemy.hp}/{enemy.max_hp}")
                self._handle_special_2x3_behavior(enemy, player)
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
    
    def _handle_stage11_enemy_behavior(self, enemy, player):
        """Stage11専用敵行動処理"""
        # HP50%チェック
        hp_ratio = enemy.hp / enemy.max_hp
        print(f"🔧 Stage11敵行動: HP比率={hp_ratio:.2f}")
        
        # 敵の状態管理
        if not hasattr(enemy, 'stage11_state'):
            enemy.stage11_state = "normal"  # "normal", "rage_countdown_3", "rage_countdown_2", "rage_countdown_1", "attacking"
        if not hasattr(enemy, 'stage11_turn_counter'):
            enemy.stage11_turn_counter = 0
            
        # 前ターンの範囲攻撃表示フラグをクリア
        if hasattr(enemy, 'stage11_area_attack_active'):
            enemy.stage11_area_attack_active = False
        
        # 前回のHPを記録して、攻撃を受けたかどうかを判定
        if not hasattr(enemy, 'stage11_previous_hp'):
            enemy.stage11_previous_hp = enemy.hp
        
        # 攻撃を受けたかどうかを判定（HPが減少した場合）
        was_attacked = enemy.hp < enemy.stage11_previous_hp
        
        # 状態に応じた処理
        if enemy.stage11_state == "normal":
            if hp_ratio < 0.5 and was_attacked:  # 50%を下回り、かつ攻撃を受けた時のみ
                # HP50%以下で攻撃を受けた瞬間：3ターンカウントダウン開始
                enemy.stage11_state = "rage_countdown_3"
                enemy.stage11_turn_counter = 3
                enemy.alerted = True  # 標準のalertedフラグを使用
                print(f"🔥 大型敵が怒りモードに突入！(HP: {enemy.hp}/{enemy.max_hp})")
                print(f"⚠️ 3ターン後に周囲1マス範囲への即死攻撃を実行予定（カウントダウン: 3）")
                
                # v1.2.8: 2x3敵用交互怒りモード履歴記録
                if hasattr(enemy, 'enemy_type') and enemy.enemy_type.value in ["large_2x2", "large_3x3"]:
                    enemy_id = getattr(enemy, 'id', f"{enemy.enemy_type.value}_{enemy.position.x}_{enemy.position.y}")
                    self.record_rage_mode_entry(enemy_id, enemy.enemy_type.value, self.current_state.turn_count)
                    print(f"📊 怒りモード履歴記録: {enemy.enemy_type.value} (ターン{self.current_state.turn_count})")
            else:
                # HP50%以上または攻撃を受けていない：完全に無行動
                enemy.alerted = False  # 平常モード
                print(f"🟢 Stage11敵は平常モード - 行動せず (HP: {enemy.hp}/{enemy.max_hp})")
        
        elif enemy.stage11_state == "rage_countdown_3":
            # 怒りモード1ターン目：カウントダウン3→2
            enemy.alerted = True  # 怒りモード継続
            enemy.stage11_state = "rage_countdown_2"
            enemy.stage11_turn_counter = 2
            print(f"⚠️ 怒りモードカウントダウン: 2ターン後に範囲攻撃実行")
        
        elif enemy.stage11_state == "rage_countdown_2":
            # 怒りモード2ターン目：カウントダウン2→1
            enemy.alerted = True  # 怒りモード継続
            enemy.stage11_state = "rage_countdown_1"
            enemy.stage11_turn_counter = 1
            print(f"⚠️ 怒りモードカウントダウン: 1ターン後に範囲攻撃実行")
        
        elif enemy.stage11_state == "rage_countdown_1":
            # 怒りモード3ターン目：次ターンで攻撃実行
            enemy.alerted = True  # 怒りモード継続
            enemy.stage11_state = "attacking"
            enemy.stage11_turn_counter = 0
            print(f"💀 危険！次ターンで周囲1マス範囲攻撃実行！")
        
        elif enemy.stage11_state == "attacking":
            # 怒りモード4ターン目：実際に範囲攻撃を実行して平常時復帰
            enemy.alerted = True  # 怒りモード継続
            print(f"💥 怒りモード攻撃ターン！周囲1マス範囲攻撃実行")
            self._execute_stage11_area_attack(enemy, player)
            
            # 攻撃実行後は平常時に戻る（HP50%以下でも次回攻撃を受けるまで平常時）
            enemy.stage11_state = "normal"
            enemy.alerted = False  # 平常モード復帰
            enemy.stage11_turn_counter = 0
            print(f"😴 怒りモード終了：平常モード復帰")
        
        # HPを記録（次回の攻撃判定用）
        enemy.stage11_previous_hp = enemy.hp
    
    def _handle_special_2x3_behavior(self, enemy, player):
        """special_2x3敵の行動処理（交互怒りモード監視）"""
        # 敵の状態管理
        if not hasattr(enemy, 'special_2x3_state'):
            enemy.special_2x3_state = "monitoring"  # "monitoring", "hunting", "eliminated"
        
        # 状態に応じた処理
        if enemy.special_2x3_state == "monitoring":
            # 交互判定停止条件をチェック
            if self.should_stop_alternating_check():
                if self.has_all_large_enemies_defeated():
                    # 全ての大型敵撃破 → 消滅
                    enemy.special_2x3_state = "eliminated"
                    enemy.hp = 0  # 即座に消滅
                    print(f"✨ 2x3敵が消滅！全ての大型敵が撃破され、特殊条件達成")
                    # 敵リストから即座に削除
                    self._remove_special_2x3_enemy()
                    return
                elif self.is_2x2_enemy_defeated():
                    # 2x2敵撃破により交互判定停止 → 待機モードに移行
                    print(f"🔄 2x3敵は待機モード - 2x2敵撃破により交互判定を停止")
                    enemy.alerted = False
                    return
            
            # 交互怒りモードパターンをチェック（2x2敵が生存している場合のみ）
            if not self.check_alternating_rage_pattern():
                # パターン違反検出 → 追跡モードに移行
                enemy.special_2x3_state = "hunting"
                enemy.alerted = True
                print(f"🚨 2x3敵が追跡モードに移行！交互怒りモードパターン違反検出")
                print(f"📊 期待: {self.get_next_expected_rage_type()}, 現在の履歴: {len(self.rage_mode_history)}件")
                return
            
            # 監視モード：基本的に無行動
            enemy.alerted = False
            print(f"👁️ 2x3敵は監視モード - 交互怒りモードパターンを監視中")
        
        elif enemy.special_2x3_state == "hunting":
            # 追跡モード：プレイヤーを追跡して即死攻撃
            enemy.alerted = True
            self._execute_2x3_hunting_behavior(enemy, player)
        
        elif enemy.special_2x3_state == "eliminated":
            # 消滅状態：何もしない（既にHP=0）
            pass
    
    def _execute_2x3_hunting_behavior(self, enemy, player):
        """2x3敵の追跡行動（即死攻撃）"""
        # プレイヤーとの距離をチェック
        distance = abs(enemy.position.x - player.position.x) + abs(enemy.position.y - player.position.y)
        
        if distance <= 1:
            # 隣接している場合は即死攻撃（HPを0にして死亡状態にする）
            print(f"💀 2x3敵の即死攻撃！プレイヤーが倒されました")
            player.hp = 0
            # 通常の死亡判定に任せる（既存のシステムを使用）
        else:
            # プレイヤーに向かって移動（簡単な追跡AI）
            dx = player.position.x - enemy.position.x
            dy = player.position.y - enemy.position.y
            
            # X方向またはY方向に1マス移動
            if abs(dx) > abs(dy):
                # X方向を優先
                new_x = enemy.position.x + (1 if dx > 0 else -1)
                new_pos = Position(new_x, enemy.position.y)
            else:
                # Y方向を優先
                new_y = enemy.position.y + (1 if dy > 0 else -1)
                new_pos = Position(enemy.position.x, new_y)
            
            # 移動先が有効かチェック
            if (self.current_state.board.is_valid_position(new_pos) and 
                new_pos not in self.current_state.board.walls and
                not self._is_position_occupied_by_enemy(new_pos, enemy)):
                
                enemy.position = new_pos
                print(f"🏃 2x3敵がプレイヤーを追跡中: {new_pos.x}, {new_pos.y}")
            else:
                print(f"🚧 2x3敵の移動がブロックされました")
    
    def _is_position_occupied_by_enemy(self, position: Position, exclude_enemy) -> bool:
        """指定位置が他の敵によって占有されているかチェック"""
        for enemy in self.current_state.enemies:
            if enemy != exclude_enemy and enemy.is_alive() and enemy.position == position:
                return True
        return False
    
    def _execute_stage11_area_attack(self, enemy, player):
        """大型敵の範囲即死攻撃を実行"""
        # 敵の攻撃範囲を取得（デフォルト1マス）
        attack_range = getattr(enemy, 'area_attack_range', 1)
        
        # プレイヤーが範囲内にいるかチェック
        enemy_positions = self._get_large_enemy_positions(enemy)
        
        # 大型敵の周囲N マス範囲を計算（敵自身のマスは除外）
        enemy_positions_set = set(enemy_positions)
        attack_range_positions = set()
        
        for enemy_pos in enemy_positions:
            for dx in range(-attack_range, attack_range + 1):
                for dy in range(-attack_range, attack_range + 1):
                    attack_pos = Position(enemy_pos.x + dx, enemy_pos.y + dy)
                    # 敵自身の占有マスは攻撃範囲から除外
                    if attack_pos not in enemy_positions_set:
                        attack_range_positions.add(attack_pos)
        
        # 範囲攻撃実行フラグを設定（描画用）
        enemy.stage11_area_attack_active = True
        enemy.stage11_attack_range = list(attack_range_positions)
        
        # 範囲攻撃描画メッセージ
        print(f"🔥 大型敵の範囲攻撃発動中！（{attack_range}マス範囲）")
        print(f"🗂️ 敵占有位置: {[(pos.x, pos.y) for pos in enemy_positions]}")
        print(f"💥 攻撃範囲座標: {[(pos.x, pos.y) for pos in sorted(attack_range_positions, key=lambda p: (p.y, p.x))]}")
        print(f"💥 攻撃範囲: {len(attack_range_positions)}マス")
        
        # プレイヤーが攻撃範囲内にいるかチェック
        if player.position in attack_range_positions:
            print(f"💥 大型敵の範囲攻撃！ プレイヤーに{player.hp}ダメージ（即死攻撃）")
            player.take_damage(player.hp)  # 現在HPと同じダメージで即死
            
            if not player.is_alive():
                print(f"☠️ プレイヤー死亡！")
                self.current_state.status = GameStatus.FAILED
        else:
            print(f"💨 大型敵の範囲攻撃をかわしました")
            
        # 攻撃範囲表示フラグは次ターンで自動リセットされる
    
    def _get_large_enemy_positions(self, enemy):
        """大型敵の占有位置リストを取得"""
        if hasattr(enemy, 'enemy_type'):
            base_pos = enemy.position
            if enemy.enemy_type.value == "large_2x2":
                # 2x2敵の場合（基準位置は左上）
                return [
                    Position(base_pos.x, base_pos.y),          # 左上（基準位置）
                    Position(base_pos.x + 1, base_pos.y),      # 右上
                    Position(base_pos.x, base_pos.y + 1),      # 左下
                    Position(base_pos.x + 1, base_pos.y + 1)   # 右下
                ]
            elif enemy.enemy_type.value == "large_3x3":
                # 3x3敵の場合（基準位置は左上）
                return [
                    Position(base_pos.x, base_pos.y),          # 左上（基準位置）
                    Position(base_pos.x + 1, base_pos.y),      # 上中
                    Position(base_pos.x + 2, base_pos.y),      # 右上
                    Position(base_pos.x, base_pos.y + 1),      # 左中
                    Position(base_pos.x + 1, base_pos.y + 1),  # 中央
                    Position(base_pos.x + 2, base_pos.y + 1),  # 右中
                    Position(base_pos.x, base_pos.y + 2),      # 左下
                    Position(base_pos.x + 1, base_pos.y + 2),  # 下中
                    Position(base_pos.x + 2, base_pos.y + 2)   # 右下
                ]
        return [enemy.position]  # デフォルト
    
    def _handle_special_enemy_elimination(self):
        """特殊敵の条件達成時の消滅処理"""
        if self.current_state is None or self.special_error_handler is None:
            return
        
        # 影の王（stage13）の処理
        enemies_to_remove = []
        for i, enemy in enumerate(self.current_state.enemies):
            if (hasattr(enemy, 'enemy_type') and 
                enemy.enemy_type.value == "special_2x3" and
                self.special_error_handler.should_eliminate_special_enemy("shadow_lord")):
                enemies_to_remove.append(i)
        
        # 逆順でリストから削除（インデックスのずれを防ぐ）
        for i in reversed(enemies_to_remove):
            del self.current_state.enemies[i]
    
    def reset_game(self) -> bool:
        """ゲームをリセット"""
        if self.initial_state is None:
            return False
        
        self.current_state = self._copy_game_state(self.initial_state)
        self.command_invoker.clear_history()
        
        # v1.2.8: 怒りモード履歴をクリア
        self.rage_mode_history = []
        
        # v1.2.8: 敵の特殊状態を強制的にリセット（動的属性は初期状態にないため）
        if self.current_state and self.current_state.enemies:
            for enemy in self.current_state.enemies:
                # 2x3敵の状態を強制的に初期化（監視モード）
                if hasattr(enemy, 'enemy_type') and enemy.enemy_type.value == "special_2x3":
                    enemy.special_2x3_state = "monitoring"
                    print(f"🔄 2x3敵の状態をリセット: monitoring")
                
                # stage11特殊敵の状態を初期化
                if hasattr(enemy, 'stage11_special') and enemy.stage11_special:
                    enemy.stage11_previous_hp = enemy.hp
                    enemy.stage11_rage_state = "normal"
                    enemy.stage11_rage_countdown = 0
                
                # 警戒状態をリセット
                enemy.alerted = False
        
        # 特殊エラーハンドラーもリセット
        if self.special_error_handler:
            stage_id = self.special_error_handler.stage_id
            error_config = self.special_error_handler.error_config
            self.special_error_handler = SpecialErrorHandler(stage_id, error_config)
        
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
            
            # v1.2.8: 拡張属性をコピー
            if hasattr(enemy, 'stage11_special'):
                enemy_copy.stage11_special = enemy.stage11_special
            if hasattr(enemy, 'area_attack_range'):
                enemy_copy.area_attack_range = enemy.area_attack_range
                
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
            goal_position=goal_copy,
            stage_id=state.stage_id  # ステージIDもコピー
        )
    
    def record_rage_mode_entry(self, enemy_id: str, enemy_type: str, turn: int) -> None:
        """怒りモード突入を記録（2x3敵用交互判定）"""
        self.rage_mode_history.append({
            "enemy_id": enemy_id,
            "enemy_type": enemy_type,
            "turn": turn,
            "timestamp": len(self.rage_mode_history)
        })
    
    def check_alternating_rage_pattern(self) -> bool:
        """2x2と3x3の交互怒りモードパターンをチェック"""
        if len(self.rage_mode_history) == 0:
            return True  # まだ誰も怒っていない = OK
        
        # 期待される交互パターン: 2x2 -> 3x3 -> 2x2 -> 3x3 ...
        expected_pattern = ["large_2x2", "large_3x3"]
        
        for i, entry in enumerate(self.rage_mode_history):
            expected_type = expected_pattern[i % 2]
            if entry["enemy_type"] != expected_type:
                return False  # パターン違反
        
        return True
    
    def get_next_expected_rage_type(self) -> str:
        """次に怒るべき敵タイプを取得"""
        pattern = ["large_2x2", "large_3x3"]
        next_index = len(self.rage_mode_history) % 2
        return pattern[next_index]
    
    def has_all_large_enemies_defeated(self) -> bool:
        """全ての大型敵（2x2, 3x3）が撃破されたかチェック"""
        if self.current_state is None:
            return False
        
        large_enemies = [e for e in self.current_state.enemies 
                        if e.is_alive() and hasattr(e, 'enemy_type') and 
                        e.enemy_type.value in ["large_2x2", "large_3x3"]]
        
        return len(large_enemies) == 0
    
    def is_2x2_enemy_defeated(self) -> bool:
        """2x2敵が撃破されたかチェック"""
        if self.current_state is None:
            return False
        
        alive_2x2_enemies = [e for e in self.current_state.enemies 
                           if e.is_alive() and hasattr(e, 'enemy_type') and 
                           e.enemy_type.value == "large_2x2"]
        
        return len(alive_2x2_enemies) == 0
    
    def should_stop_alternating_check(self) -> bool:
        """交互判定を停止すべきかチェック（2x2敵撃破時）"""
        # 2x2敵が撃破されたら交互判定を停止
        if self.is_2x2_enemy_defeated():
            return True
        
        # 全ての大型敵が撃破されたら交互判定を停止
        if self.has_all_large_enemies_defeated():
            return True
        
        return False
    
    def _remove_special_2x3_enemy(self) -> None:
        """special_2x3敵を敵リストから削除"""
        if self.current_state is None:
            return
        
        # 削除対象のインデックスを収集
        enemies_to_remove = []
        for i, enemy in enumerate(self.current_state.enemies):
            if (hasattr(enemy, 'enemy_type') and 
                enemy.enemy_type.value == "special_2x3"):
                enemies_to_remove.append(i)
                print(f"🗑️ 2x3敵をインデックス {i} から削除")
        
        # 逆順で削除（インデックスのずれを防ぐ）
        for i in reversed(enemies_to_remove):
            del self.current_state.enemies[i]
            print(f"✅ 2x3敵削除完了: インデックス {i}")
    
    def _has_special_2x3_enemy_alive(self) -> bool:
        """special_2x3敵が生存しているかチェック"""
        if self.current_state is None:
            return False
        
        for enemy in self.current_state.enemies:
            if (hasattr(enemy, 'enemy_type') and 
                enemy.enemy_type.value == "special_2x3" and 
                enemy.is_alive()):
                return True
        
        return False


class SpecialErrorHandler:
    """特殊ステージ専用エラー処理とヒントシステム"""
    
    def __init__(self, stage_id: str, error_config: Dict[str, Any] = None):
        self.stage_id = stage_id
        self.error_config = error_config or {}
        self.action_sequence = []  # プレイヤーの行動履歴
        self.special_flags = {}    # 特殊フラグ管理
    
    def record_action(self, action: str, context: Dict[str, Any] = None):
        """プレイヤーの行動を記録"""
        self.action_sequence.append({
            "action": action,
            "context": context or {},
            "turn": context.get("turn", 0) if context else 0
        })
        
        # 行動履歴の長さを制限（最新50アクションのみ保持）
        if len(self.action_sequence) > 50:
            self.action_sequence = self.action_sequence[-50:]
    
    def check_special_conditions(self, game_state: GameState) -> Optional[Dict[str, str]]:
        """特殊条件をチェックして適切なエラーメッセージを返す"""
        if self.stage_id != "stage13":
            return None  # stage13以外では特殊処理なし
        
        # stage13: 特殊敵との条件付き戦闘チェック
        return self._check_stage13_conditions(game_state)
    
    def _check_stage13_conditions(self, game_state: GameState) -> Optional[Dict[str, str]]:
        """stage13の特殊条件をチェック"""
        # 影の王（special_2x3敵）を探す
        shadow_lord = None
        for enemy in game_state.enemies:
            if hasattr(enemy, 'enemy_type') and enemy.enemy_type.value == "special_2x3":
                shadow_lord = enemy
                break
        
        if shadow_lord is None:
            return None  # 影の王がいない（すでに撃破済み）
        
        # 最近のアクション履歴を確認（最新10アクション）
        recent_actions = [a["action"] for a in self.action_sequence[-10:]]
        
        # プレイヤーが影の鍵を持っているかチェック
        has_shadow_key = self._player_has_key(game_state, "shadow_key")
        
        # 直接攻撃を試みた場合
        if "attack" in recent_actions and not self._has_correct_sequence():
            if not has_shadow_key:
                return {
                    "type": "no_key_attack",
                    "message": "影の王に対抗するには特別な準備が必要です。",
                    "hint": "影の鍵を探してから再挑戦してください"
                }
            else:
                return {
                    "type": "wrong_sequence", 
                    "message": "影の王には特別な方法でなければ勝てません。影の鍵を使った特殊な攻撃順序を試してみましょう。",
                    "hint": "pickup → wait → attack の順序を試してください"
                }
        
        # 正しいシーケンス（pickup → wait → attack）をチェック
        if has_shadow_key and len(recent_actions) >= 3:
            last_three = recent_actions[-3:]
            if last_three == ["pickup", "wait", "attack"]:
                # 正しいシーケンス実行済み - 特殊処理フラグを設定
                self.special_flags["shadow_lord_vulnerable"] = True
                return {
                    "type": "success_sequence",
                    "message": "影の鍵の力が発動！影の王の防御が解除されました。",
                    "hint": "今こそ決定打の時です！"
                }
        
        return None
    
    def _player_has_key(self, game_state: GameState, key_name: str) -> bool:
        """プレイヤーが指定された鍵を持っているかチェック"""
        # プレイヤーの装備やインベントリから鍵を探す
        # 簡略化: pickup済みの鍵があるかaction_sequenceから確認
        key_pickup_actions = [a for a in self.action_sequence if 
                             a["action"] == "pickup" and 
                             a.get("context", {}).get("item_name") == key_name]
        return len(key_pickup_actions) > 0
    
    def _has_correct_sequence(self) -> bool:
        """正しいアクションシーケンス（pickup → wait → attack）が実行されたかチェック"""
        if len(self.action_sequence) < 3:
            return False
        
        # 最新の3つのアクションをチェック
        recent_actions = [a["action"] for a in self.action_sequence[-3:]]
        return recent_actions == ["pickup", "wait", "attack"]
    
    def should_eliminate_special_enemy(self, enemy_id: str) -> bool:
        """特殊敵を即座に消滅させるべきかチェック"""
        return (self.stage_id == "stage13" and 
                enemy_id == "shadow_lord" and 
                self.special_flags.get("shadow_lord_vulnerable", False))
    
    def get_learning_hint(self, situation: str) -> Optional[str]:
        """状況に応じた学習ヒントを提供"""
        if self.stage_id == "stage13":
            hints = {
                "enemy_too_strong": "影の王は通常の攻撃では倒せません。特別な方法を探してみましょう。",
                "need_key": "このステージには特別なアイテムがあるようです。マップを探索してみてください。",
                "sequence_hint": "影の鍵を手に入れたら、wait()で待機してから攻撃してみてください。",
                "final_boss": "最終ステージです！これまで学んだすべてのスキルを活用しましょう。"
            }
            return hints.get(situation)
        
        return None
    
# エクスポート用
__all__ = ["GameStateManager", "SpecialErrorHandler"]