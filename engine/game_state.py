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
                       error_config: Optional[Dict[str, Any]] = None,
                       victory_conditions: Optional[List[Dict[str, str]]] = None) -> GameState:
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
            stage_id=stage_id,  # ステージIDを設定
            victory_conditions=victory_conditions  # 勝利条件を設定
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

        # 🔧 ステップ実行モード時の敵ターン処理制御
        should_skip_enemy_turn = self._should_skip_enemy_turn_processing()

        print(f"🔧 敵ターン処理判定: should_skip={should_skip_enemy_turn}")

        if should_skip_enemy_turn:
            # ステップ実行中は敵ターン処理をスキップ
            print(f"🚫 敵ターン処理をスキップ（ステップ実行モード）")
        else:
            # 敵のターン処理を実行
            print(f"✅ 敵ターン処理を実行（通常モード）")
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

    def _should_skip_enemy_turn_processing(self) -> bool:
        """ステップ実行モード時の敵ターン処理スキップ判定"""
        try:
            # ExecutionControllerへの参照を取得
            from .api import _global_api

            if not hasattr(_global_api, 'execution_controller') or not _global_api.execution_controller:
                print(f"🔍 敵ターンスキップ判定: ExecutionController不存在 → False")
                return False

            execution_controller = _global_api.execution_controller

            # ステップ実行アクティブフラグをチェック
            is_step_active = getattr(execution_controller, 'is_step_execution_active', False)
            current_mode = getattr(execution_controller.state, 'mode', 'UNKNOWN')

            print(f"🔍 敵ターンスキップ判定: is_step_active={is_step_active}, mode={current_mode}")

            # 🔧 ステップ実行でも敵ターン処理を実行（正しいターン制のため）
            # プレイヤーアクション完了後に敵ターンが実行される
            return False  # 敵ターン処理を常に実行

        except Exception as e:
            # エラー時は通常処理を続行
            print(f"🔍 敵ターンスキップ判定エラー: {e} → False")
            return False

    def _process_enemy_turns(self):
        """敵のターン処理"""
        if self.current_state is None:
            return
            
        player = self.current_state.player
        
        # デバッグ: stage_idを確認
        print(f"🔧 _process_enemy_turns開始: stage_id={getattr(self.current_state, 'stage_id', 'None')}")
        
        # このターンで既に行動した敵を追跡するセット
        enemies_already_moved = set()

        # 第1段階: 先に敵の移動処理を実行
        for enemy in self.current_state.enemies:
            if not enemy.is_alive():
                continue

            # Stage11/Stage12特別処理: stage11_special属性ベースでの判定
            if (hasattr(enemy, 'stage11_special') and enemy.stage11_special):
                # stage11_special=trueの敵は特殊行動パターン
                print(f"🔧 特殊敵処理開始: HP={enemy.hp}/{enemy.max_hp}")
                self._handle_stage11_enemy_behavior(enemy, player)
                enemies_already_moved.add(id(enemy))  # 既に行動済みとしてマーク
                continue

            # v1.2.8: 2x3敵特殊処理
            if (hasattr(enemy, 'enemy_type') and enemy.enemy_type.value == "special_2x3"):
                print(f"🔧 2x3特殊敵処理開始: HP={enemy.hp}/{enemy.max_hp}")
                self._handle_special_2x3_behavior(enemy, player)
                enemies_already_moved.add(id(enemy))  # 既に行動済みとしてマーク
                continue

            # 移動処理を先に実行（非警戒状態の場合のみ）
            if not enemy.alerted:
                self._execute_enemy_movement(enemy, player)
                enemies_already_moved.add(id(enemy))  # 既に行動済みとしてマーク

        # 第2段階: 移動後の位置で視界判定と警戒状態更新
        for enemy in self.current_state.enemies:
            if not enemy.is_alive():
                continue

            # 特殊敵はスキップ
            if (hasattr(enemy, 'stage11_special') and enemy.stage11_special):
                continue
            if (hasattr(enemy, 'enemy_type') and enemy.enemy_type.value == "special_2x3"):
                continue

            # プレイヤーを視認できるかチェック（壁による視線遮蔽を考慮）
            can_see = enemy.can_see_player(player.position, self.current_state.board)

            # デバッグ: 視界判定の詳細ログ
            print(f"🔍 DEBUG enemy_turn - 敵{enemy.position}→プレイヤー{player.position}: can_see={can_see}, alerted={enemy.alerted}")

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

        # 第3段階: 警戒状態の敵の追跡・攻撃処理
        for enemy in self.current_state.enemies:
            if not enemy.is_alive():
                continue

            # 特殊敵はスキップ
            if (hasattr(enemy, 'stage11_special') and enemy.stage11_special):
                continue
            if (hasattr(enemy, 'enemy_type') and enemy.enemy_type.value == "special_2x3"):
                continue

            # 🔧 既に行動済みの敵はスキップ（1ターン1アクション制御）
            if id(enemy) in enemies_already_moved:
                print(f"🔧 既に行動済みの敵をスキップ: 敵{enemy.position}")
                continue

            # 🔧 警戒状態の敵処理
            if enemy.alerted:
                print(f"🔧 警戒状態敵処理開始: 敵[{enemy.position.x},{enemy.position.y}] プレイヤー[{player.position.x},{player.position.y}]")
                print(f"🔍 敵オブジェクト情報: type={type(enemy).__name__}")

                # すべての敵に対して統一的な追跡行動を実行
                # AdvancedEnemyシステムは複雑すぎるため、シンプルな追跡システムを使用
                print(f"🔧 統一追跡システム使用: _simple_chase_behavior")
                self._simple_chase_behavior(enemy, player.position)
            
            # 非警戒状態では基本行動パターンを実行 - _execute_enemy_movementで処理済み
            elif not enemy.alerted:
                # Stage 1で _execute_enemy_movement により移動処理完了済み
                pass

    def _simple_chase_behavior(self, enemy, player_pos):
        """基本敵オブジェクト用の知能的追跡行動"""
        try:
            current_pos = enemy.position

            # プレイヤーとの距離を計算
            dx = player_pos.x - current_pos.x
            dy = player_pos.y - current_pos.y
            distance = abs(dx) + abs(dy)

            print(f"🔧 知能追跡開始: 敵[{current_pos.x},{current_pos.y}] → プレイヤー[{player_pos.x},{player_pos.y}] 距離={distance}")
            print(f"🔍 敵状態: direction={enemy.direction.value}, alerted={enemy.alerted}")

            # 隣接している場合は攻撃
            if distance == 1:
                print(f"🎯 攻撃範囲内: 攻撃処理開始")
        except Exception as e:
            print(f"❌ _simple_chase_behavior 初期化エラー: {e}")
            import traceback
            traceback.print_exc()
            return

        try:
            if distance == 1:
                # プレイヤーの方向を向いて攻撃
                required_direction = None
                if abs(dx) > abs(dy):
                    required_direction = Direction.EAST if dx > 0 else Direction.WEST
                else:
                    required_direction = Direction.SOUTH if dy > 0 else Direction.NORTH

                print(f"🎯 攻撃処理: current_dir={enemy.direction.value}, required_dir={required_direction.value}")

                if enemy.direction == required_direction:
                    # 攻撃実行
                    damage = enemy.attack_power
                    player = self.current_state.player
                    actual_damage = player.take_damage(damage)
                    print(f"💀 敵の攻撃！ {actual_damage}ダメージ (プレイヤーHP: {player.hp}/{player.max_hp})")

                    if not player.is_alive():
                        print(f"☠️ プレイヤー死亡！")
                        self.current_state.status = GameStatus.FAILED
                else:
                    # 方向転換
                    enemy.direction = required_direction
                    print(f"🔄 攻撃準備: 方向転換 → {required_direction.value}")
                print(f"✅ 攻撃処理完了")
                return
        except Exception as e:
            print(f"❌ 攻撃処理エラー: {e}")
            import traceback
            traceback.print_exc()
            return

        try:
            # 移動処理
            print(f"🚶 移動処理開始: 距離={distance}")

            # プレイヤーに向かう最適方向を決定（大きな差分を優先）
            target_directions = []

            # X軸の移動
            if dx > 0:
                target_directions.append(Direction.EAST)
            elif dx < 0:
                target_directions.append(Direction.WEST)

            # Y軸の移動
            if dy > 0:
                target_directions.append(Direction.SOUTH)
            elif dy < 0:
                target_directions.append(Direction.NORTH)

            print(f"🎯 移動候補: {[d.value for d in target_directions]}")

            # より大きな軸差分を優先（効率的な追跡）
            if abs(dx) >= abs(dy):
                pass  # X軸が既に最初
            else:
                # Y軸を優先するため順序入れ替え
                if len(target_directions) == 2:
                    target_directions[0], target_directions[1] = target_directions[1], target_directions[0]

            # 優先順位で移動試行
            for direction in target_directions:
                new_pos = self._get_new_position(current_pos, direction)
                print(f"🔍 移動試行: {direction.value} → [{new_pos.x},{new_pos.y}]")

                # 有効な移動かチェック
                if self._is_valid_move(new_pos, enemy):
                    if direction == enemy.direction:
                        # 同じ方向なら即座に移動
                        enemy.position = new_pos
                        print(f"🏃 知能追跡: 移動 [{current_pos.x},{current_pos.y}] → [{new_pos.x},{new_pos.y}]")
                    else:
                        # 方向転換
                        enemy.direction = direction
                        print(f"🔄 知能追跡: 方向転換 → {direction.value}")
                    print(f"✅ 移動処理完了")
                    return
                else:
                    print(f"❌ 移動不可: {direction.value}")

            # 優先方向で移動できない場合は代替方向を試行
            print(f"🔄 代替移動試行")
            all_directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
            for direction in all_directions:
                if direction in target_directions:
                    continue  # 既に試行済み

                new_pos = self._get_new_position(current_pos, direction)
                if self._is_valid_move(new_pos, enemy):
                    # 現在距離と比較して悪化させない移動のみ許可
                    current_distance = abs(current_pos.x - player_pos.x) + abs(current_pos.y - player_pos.y)
                    new_distance = abs(new_pos.x - player_pos.x) + abs(new_pos.y - player_pos.y)

                    if new_distance <= current_distance:
                        if direction == enemy.direction:
                            enemy.position = new_pos
                            print(f"🏃 知能追跡: 代替移動 [{current_pos.x},{current_pos.y}] → [{new_pos.x},{new_pos.y}]")
                        else:
                            enemy.direction = direction
                            print(f"🔄 知能追跡: 代替方向転換 → {direction.value}")
                        print(f"✅ 代替移動処理完了")
                        return

            print(f"🚫 知能追跡: 全方向移動不可")

        except Exception as e:
            print(f"❌ 移動処理エラー: {e}")
            import traceback
            traceback.print_exc()

    def _get_new_position(self, current_pos, direction):
        """指定方向への新しい位置を取得"""
        if direction == Direction.NORTH:
            return Position(current_pos.x, current_pos.y - 1)
        elif direction == Direction.SOUTH:
            return Position(current_pos.x, current_pos.y + 1)
        elif direction == Direction.EAST:
            return Position(current_pos.x + 1, current_pos.y)
        else:  # WEST
            return Position(current_pos.x - 1, current_pos.y)

    def _is_valid_move(self, new_pos, enemy):
        """移動が有効かチェック"""
        # GameStateのボードシステムを使用
        if self.current_state is None or self.current_state.board is None:
            return False

        # is_passableメソッドを使用（境界とボードのチェックを一括実行）
        return self.current_state.board.is_passable(new_pos)

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
                id=item.id,  # v1.2.12: Required id parameter
                position=Position(item.position.x, item.position.y),
                item_type=item.item_type,
                name=item.name,
                effect=item.effect.copy(),
                auto_equip=item.auto_equip,
                damage=item.damage  # v1.2.12: For bomb items
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

    def _calculate_rotation_turns(self, current_direction: Direction, target_direction: Direction) -> int:
        """方向転換に必要なターン数を計算"""
        if current_direction == target_direction:
            return 0

        directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        current_index = directions.index(current_direction)
        target_index = directions.index(target_direction)

        # 時計回りと反時計回りの距離を計算
        clockwise_distance = (target_index - current_index) % 4
        counterclockwise_distance = (current_index - target_index) % 4

        # 最短距離を選択（各ステップ=1ターン）
        return min(clockwise_distance, counterclockwise_distance)

    def _get_next_rotation_step(self, current_direction: Direction, target_direction: Direction) -> Direction:
        """次の回転ステップを取得（時計回りまたは反時計回り、最短ルートを選択）"""
        if current_direction == target_direction:
            return current_direction

        directions = [Direction.NORTH, Direction.EAST, Direction.SOUTH, Direction.WEST]
        current_index = directions.index(current_direction)
        target_index = directions.index(target_direction)

        # 時計回りと反時計回りの距離を計算
        clockwise_distance = (target_index - current_index) % 4
        counterclockwise_distance = (current_index - target_index) % 4

        # 最短ルートを選択
        if clockwise_distance <= counterclockwise_distance:
            # 時計回りに1ステップ
            next_index = (current_index + 1) % 4
        else:
            # 反時計回りに1ステップ
            next_index = (current_index - 1) % 4

        return directions[next_index]

    def _execute_enemy_movement(self, enemy, player):
        """敵の移動処理のみ実行（視界判定は後で実行）"""
        print(f"🌀 敵は非警戒状態: 巡回モード")
        print(f"🔍 Debug - behavior_pattern: '{enemy.behavior_pattern}' (type: {type(enemy.behavior_pattern)})")
        print(f"🔍 Debug - patrol_path: {enemy.patrol_path} (type: {type(enemy.patrol_path)}, len: {len(enemy.patrol_path) if enemy.patrol_path else 'None'})")
        print(f"🔍 Debug - current_position: {enemy.position}")
        print(f"🔍 Debug - patrol条件チェック: pattern=='patrol'? {enemy.behavior_pattern == 'patrol'}, patrol_path存在? {bool(enemy.patrol_path)}")
        if enemy.patrol_path:
            print(f"🔍 Debug - patrol_path内容: {[f'({p.x},{p.y})' if hasattr(p, 'x') else f'({p[0]},{p[1]})' for p in enemy.patrol_path]}")
            print(f"🔍 Debug - current_patrol_index: {enemy.current_patrol_index}")
            next_target = enemy.get_next_patrol_position()
            print(f"🔍 Debug - get_next_patrol_position() 結果: {next_target}")
            if next_target:
                print(f"🔍 Debug - next_target座標: ({next_target.x},{next_target.y})")

        # patrol: 巡回処理
        if enemy.behavior_pattern == "patrol" and enemy.patrol_path:
            current_target = enemy.get_next_patrol_position()
            if current_target:
                # 目標位置に到達したかチェック
                if enemy.position == current_target:
                    # 次のパトロールポイントに進む
                    enemy.advance_patrol()
                    current_target = enemy.get_next_patrol_position()

                if current_target and current_target != enemy.position:
                    # 目標に向かう方向を計算
                    dx = current_target.x - enemy.position.x
                    dy = current_target.y - enemy.position.y

                    # 巡回パスに従って正確に移動するため、x軸優先で移動
                    if dx != 0:
                        required_direction = Direction.EAST if dx > 0 else Direction.WEST
                    elif dy != 0:
                        required_direction = Direction.SOUTH if dy > 0 else Direction.NORTH
                    else:
                        required_direction = enemy.direction

                    # 既に正しい方向を向いているかチェック
                    if enemy.direction == required_direction:
                        # 移動実行
                        next_pos = enemy.position.move(required_direction)
                        if self.current_state.board.is_passable(next_pos):
                            enemy.position = next_pos
                    else:
                        # 方向転換
                        enemy.direction = required_direction

    def _handle_alerted_enemy(self, enemy, player):
        """警戒状態の敵の処理 - 既存ロジックを使用"""
        # 既存の警戒状態処理を呼び出す（243行目以降のコード）
        distance = abs(player.position.x - enemy.position.x) + abs(player.position.y - enemy.position.y)
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

            # target_directionが設定されている場合は段階的回転を優先
            if hasattr(enemy, 'target_direction') and enemy.target_direction is not None:
                # 段階的回転システム：目標方向に向かって1ステップずつ回転
                if enemy.direction != enemy.target_direction:
                    next_direction = self._get_next_rotation_step(enemy.direction, enemy.target_direction)
                    turns_needed = self._calculate_rotation_turns(enemy.direction, enemy.target_direction)
                    print(f"🔄 段階的方向転換: {enemy.direction.value} → {next_direction.value} (目標: {enemy.target_direction.value}, 残りターン数: {turns_needed})")
                    enemy.direction = next_direction
                else:
                    # 目標方向に到達したので、target_directionをクリア
                    print(f"✅ 目標方向到達: {enemy.target_direction.value}")
                    enemy.target_direction = None

                    # 目標方向に到達したので攻撃を実行
                    damage = enemy.attack_power
                    actual_damage = player.take_damage(damage)
                    print(f"💀 敵の攻撃！ {actual_damage}ダメージ (プレイヤーHP: {player.hp}/{player.max_hp})")

                    if not player.is_alive():
                        print(f"☠️ プレイヤー死亡！")
                        self.current_state.status = GameStatus.FAILED

            # 通常の攻撃処理（target_directionが設定されていない場合）
            elif enemy.direction == required_direction:
                # プレイヤーを攻撃
                damage = enemy.attack_power
                actual_damage = player.take_damage(damage)
                print(f"💀 敵の攻撃！ {actual_damage}ダメージ (プレイヤーHP: {player.hp}/{player.max_hp})")

                if not player.is_alive():
                    print(f"☠️ プレイヤー死亡！")
                    self.current_state.status = GameStatus.FAILED
            else:
                # 正しい方向を向いていない場合は段階的方向転換（複数ターン消費の可能性）
                next_direction = self._get_next_rotation_step(enemy.direction, required_direction)
                turns_needed = self._calculate_rotation_turns(enemy.direction, required_direction)
                print(f"🔄 段階的方向転換: {enemy.direction.value} → {next_direction.value} (必要ターン数: {turns_needed})")
                enemy.direction = next_direction

        # 隣接していない場合は1マス近づく移動を試みる（警戒状態のみ）
        elif distance > 1:
            # 追跡目標を決定（現在のプレイヤー位置 or 最後に見た位置）
            can_see = enemy.can_see_player(player.position, self.current_state.board)
            target_position = player.position if can_see else enemy.last_seen_player
            if target_position is None:
                target_position = player.position  # フォールバック

            print(f"🏃 追跡開始: 敵[{enemy.position.x},{enemy.position.y}] → 目標[{target_position.x},{target_position.y}] 距離={distance} ({'直視' if can_see else '記憶'})")

            # プレイヤーに向かって移動
            dx = target_position.x - enemy.position.x
            dy = target_position.y - enemy.position.y

            # 移動方向を決定（シンプルな追跡アルゴリズム）
            move_direction = None
            if abs(dx) >= abs(dy):
                # x軸優先追跡
                print(f"🏃 同一距離追跡（接触重視x軸優先）: target_dx={dx}, target_dy={dy}, 選択方向={'E' if dx > 0 else 'W'}")
                move_direction = Direction.EAST if dx > 0 else Direction.WEST
            else:
                # y軸追跡
                print(f"🏃 y軸優先追跡: target_dy={dy}, 選択方向={'S' if dy > 0 else 'N'}")
                move_direction = Direction.SOUTH if dy > 0 else Direction.NORTH

            # 🔧 古いAIロジックを無効化 - 正規のenemy_systemに委譲
            print(f"🔧 古いAIロジック無効化: 正規のenemy_systemに委譲 (方向={move_direction.value})")
            # 移動方向が現在の方向と異なる場合は方向転換
            # if enemy.direction != move_direction:
            #     print(f"🔄 追跡方向転換: {enemy.direction.value} → {move_direction.value}")
            #     enemy.direction = move_direction
            # else:
            #     # 移動実行
            #     next_pos = enemy.position.move(move_direction)
            #     print(f"🏃 追跡移動試行: [{enemy.position.x},{enemy.position.y}] → [{next_pos.x},{next_pos.y}]")
            #
            #     if self.current_state.board.is_passable(next_pos):
            #         enemy.position = next_pos


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