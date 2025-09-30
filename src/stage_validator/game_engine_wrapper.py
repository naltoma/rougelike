"""
GameEngineWrapper Implementation

既存のゲームエンジン（engine/）をラップして
ExecutionEngineインターフェースを提供する。
main_*.py の編集を回避し、既存APIとの互換性を維持。
"""

from typing import List, Dict, Any, Optional, Tuple
import sys
import os
from pathlib import Path
import time

# 既存のゲームエンジンをインポート
try:
    from engine.game_state import GameState
    from engine.api import move, turn_left, turn_right, attack, pickup, wait, dispose, see
    from engine.commands import Command
except ImportError:
    # パス調整が必要な場合
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from engine.game_state import GameState
    from engine.api import move, turn_left, turn_right, attack, pickup, wait, dispose, see
    from engine.commands import Command

from .execution_engine import ExecutionEngine
from .models import ExecutionLog, EnemyState, EngineType, ValidationConfig


class GameEngineWrapper(ExecutionEngine):
    """ゲームエンジンラッパー"""

    def __init__(self, config: Optional[ValidationConfig] = None):
        super().__init__("GameEngine", config)

        self.game_state: Optional[GameState] = None
        self.api_functions: Dict[str, Any] = {
            "move": move,
            "turn_left": turn_left,
            "turn_right": turn_right,
            "attack": attack,
            "pickup": pickup,
            "wait": wait,
            "dispose": dispose
        }

        # ゲームエンジン固有の状態
        self.original_stdout = None
        self.step_delay = 0.0

    def reset_stage(self, stage_file: str) -> None:
        """ステージを初期状態にリセット"""
        self.validate_stage_file(stage_file)
        self.current_stage_file = stage_file

        try:
            # 既存のゲームエンジンを初期化
            self.game_state = GameState(stage_file)
            self.step_delay = self.config.game_engine_step_delay

            # 出力制御設定
            if not self.config.enable_visual_mode:
                self._suppress_game_output()

            self.clear_logs()
            self.is_initialized = True
            self.logger.info(f"Game engine initialized with stage: {stage_file}")

        except Exception as e:
            self.logger.error(f"Failed to initialize game engine: {e}")
            raise RuntimeError(f"Game engine initialization failed: {e}")

    def _suppress_game_output(self) -> None:
        """ゲームエンジンの出力を抑制（パフォーマンス最適化）"""
        if self.config.memory_optimization_enabled:
            # 必要に応じてstdout/stderrをリダイレクト
            pass

    def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
        """解法例を実行してログを生成"""
        if not self.is_initialized or not self.game_state:
            raise RuntimeError("Engine not initialized. Call reset_stage() first.")

        self.validate_solution_path(solution_path)
        self.clear_logs()

        # ゲーム状態をリセット
        self._reset_game_state()

        self.logger.info(f"Executing solution with {len(solution_path)} steps")

        try:
            for step_number, action in enumerate(solution_path):
                self.logger.debug(f"Step {step_number}: executing action '{action}'")

                # アクション実行前の状態を記録
                pre_action_log = self._capture_current_state(step_number, "none")

                # プレイヤーアクション実行
                success = self._execute_game_action(action)
                if not success and self.config.auto_reset_on_failure:
                    self.logger.warning(f"Action '{action}' failed at step {step_number}, auto-resetting")
                    break

                # ステップ遅延
                if self.step_delay > 0:
                    time.sleep(self.step_delay)

                # アクション実行後の状態を記録
                log = self._capture_current_state(step_number, action)
                self.execution_logs.append(log)

                # ゲーム終了条件チェック
                if log.game_over or log.victory:
                    self.logger.info(f"Game ended at step {step_number}: victory={log.victory}, game_over={log.game_over}")
                    break

                # タイムアウトチェック
                if step_number >= self.config.max_solution_steps:
                    self.logger.warning(f"Solution execution timeout at step {step_number}")
                    break

            self.logger.info(f"Solution execution completed: {len(self.execution_logs)} steps")
            return self.execution_logs

        except Exception as e:
            self.logger.error(f"Solution execution failed: {e}")
            raise RuntimeError(f"Game engine execution error: {e}")

    def _reset_game_state(self) -> None:
        """ゲーム状態をリセット"""
        if self.game_state and hasattr(self.game_state, 'reset'):
            self.game_state.reset()
        else:
            # GameStateを再初期化
            self.game_state = GameState(self.current_stage_file)

    def _execute_game_action(self, action: str) -> bool:
        """ゲームエンジンでアクション実行"""
        self.validate_action(action)

        if action not in self.api_functions:
            self.logger.warning(f"Unknown action: {action}")
            return False

        try:
            # 既存のAPI関数を呼び出し
            api_function = self.api_functions[action]
            result = api_function()

            # 結果の評価（API関数の戻り値による）
            if isinstance(result, dict):
                return result.get('success', True)
            elif isinstance(result, bool):
                return result
            else:
                # 戻り値がない場合は成功とみなす
                return True

        except Exception as e:
            self.logger.warning(f"Action '{action}' execution failed: {e}")
            return False

    def _capture_current_state(self, step_number: int, action: str) -> ExecutionLog:
        """現在のゲーム状態をキャプチャ"""
        try:
            # プレイヤー状態取得
            player_pos = self._get_player_position()
            player_dir = self._get_player_direction()

            # 敵状態取得
            enemy_states = self._get_enemy_states()

            # ゲーム終了状態取得
            game_over = self._is_game_over()
            victory = self._is_victory()

            return ExecutionLog(
                step_number=step_number,
                engine_type=EngineType.GAME_ENGINE,
                player_position=player_pos,
                player_direction=player_dir,
                enemy_states=enemy_states,
                action_taken=action,
                game_over=game_over,
                victory=victory
            )

        except Exception as e:
            self.logger.error(f"Failed to capture game state: {e}")
            # フォールバック状態
            return ExecutionLog(
                step_number=step_number,
                engine_type=EngineType.GAME_ENGINE,
                player_position=(0, 0),
                player_direction="up",
                enemy_states=[],
                action_taken=action,
                game_over=True,  # エラー時は終了扱い
                victory=False
            )

    def _get_player_position(self) -> Tuple[int, int]:
        """プレイヤー位置取得"""
        if hasattr(self.game_state, 'player'):
            player = self.game_state.player
            if hasattr(player, 'position'):
                return tuple(player.position)
            elif hasattr(player, 'x') and hasattr(player, 'y'):
                return (player.x, player.y)

        # see()関数を使用して位置を取得
        try:
            vision_data = see()
            if isinstance(vision_data, dict) and 'player_position' in vision_data:
                return tuple(vision_data['player_position'])
        except Exception:
            pass

        # デフォルト位置
        return (1, 1)

    def _get_player_direction(self) -> str:
        """プレイヤー向き取得"""
        if hasattr(self.game_state, 'player'):
            player = self.game_state.player
            if hasattr(player, 'direction'):
                return player.direction

        # see()関数を使用して向きを取得
        try:
            vision_data = see()
            if isinstance(vision_data, dict) and 'player_direction' in vision_data:
                return vision_data['player_direction']
        except Exception:
            pass

        # デフォルト向き
        return "up"

    def _get_enemy_states(self) -> List[EnemyState]:
        """敵状態取得"""
        enemy_states = []

        try:
            # GameStateから敵情報を取得
            if hasattr(self.game_state, 'enemies'):
                enemies = self.game_state.enemies
                for i, enemy in enumerate(enemies):
                    enemy_id = getattr(enemy, 'id', f'enemy_{i}')
                    position = getattr(enemy, 'position', (0, 0))
                    direction = getattr(enemy, 'direction', 'up')
                    patrol_index = getattr(enemy, 'patrol_index', 0)
                    alert_state = getattr(enemy, 'alert_state', 'patrol')
                    vision_range = getattr(enemy, 'vision_range', 3)
                    health = getattr(enemy, 'health', 1)
                    enemy_type = getattr(enemy, 'type', 'patrol')

                    enemy_state = EnemyState(
                        enemy_id=enemy_id,
                        position=tuple(position) if isinstance(position, (list, tuple)) else position,
                        direction=direction,
                        patrol_index=patrol_index,
                        alert_state=alert_state,
                        vision_range=vision_range,
                        health=health,
                        enemy_type=enemy_type
                    )
                    enemy_states.append(enemy_state)

            # see()関数からも敵情報を取得
            vision_data = see()
            if isinstance(vision_data, dict) and 'enemies' in vision_data:
                seen_enemies = vision_data['enemies']
                # GameStateの敵と統合（重複を避ける）
                seen_enemy_ids = {e.enemy_id for e in enemy_states}

                for seen_enemy in seen_enemies:
                    enemy_id = seen_enemy.get('id', f'seen_enemy_{len(enemy_states)}')
                    if enemy_id not in seen_enemy_ids:
                        enemy_state = EnemyState(
                            enemy_id=enemy_id,
                            position=tuple(seen_enemy.get('position', (0, 0))),
                            direction=seen_enemy.get('direction', 'up'),
                            patrol_index=seen_enemy.get('patrol_index', 0),
                            alert_state=seen_enemy.get('alert_state', 'patrol'),
                            vision_range=seen_enemy.get('vision_range', 3),
                            health=seen_enemy.get('health', 1),
                            enemy_type=seen_enemy.get('type', 'patrol')
                        )
                        enemy_states.append(enemy_state)

        except Exception as e:
            self.logger.debug(f"Could not retrieve enemy states: {e}")

        return enemy_states

    def _is_game_over(self) -> bool:
        """ゲーム終了判定"""
        try:
            if hasattr(self.game_state, 'is_game_over'):
                return self.game_state.is_game_over()
            elif hasattr(self.game_state, 'game_over'):
                return self.game_state.game_over
            elif hasattr(self.game_state, 'player'):
                player = self.game_state.player
                if hasattr(player, 'is_dead'):
                    return player.is_dead()
                elif hasattr(player, 'health'):
                    return player.health <= 0

            # API経由でのチェック
            vision_data = see()
            if isinstance(vision_data, dict) and 'game_over' in vision_data:
                return vision_data['game_over']

        except Exception as e:
            self.logger.debug(f"Could not determine game over state: {e}")

        return False

    def _is_victory(self) -> bool:
        """勝利判定"""
        try:
            if hasattr(self.game_state, 'is_victory'):
                return self.game_state.is_victory()
            elif hasattr(self.game_state, 'victory'):
                return self.game_state.victory

            # API経由でのチェック
            vision_data = see()
            if isinstance(vision_data, dict) and 'victory' in vision_data:
                return vision_data['victory']

        except Exception as e:
            self.logger.debug(f"Could not determine victory state: {e}")

        return False

    def get_current_state(self) -> ExecutionLog:
        """現在状態を取得"""
        if self.execution_logs:
            return self.execution_logs[-1]

        # 現在の状態を直接キャプチャ
        return self._capture_current_state(0, "none")

    def get_stage_info(self) -> Dict[str, Any]:
        """ステージ情報取得"""
        try:
            if hasattr(self.game_state, 'get_stage_info'):
                return self.game_state.get_stage_info()

            # 基本情報を構築
            info = {
                "stage_file": self.current_stage_file,
                "player_position": self._get_player_position(),
                "player_direction": self._get_player_direction(),
                "enemy_count": len(self._get_enemy_states()),
                "is_initialized": self.is_initialized
            }

            # see()関数から追加情報を取得
            vision_data = see()
            if isinstance(vision_data, dict):
                info.update({
                    "visible_area": vision_data.get('visible', []),
                    "walls": vision_data.get('walls', []),
                    "items": vision_data.get('items', [])
                })

            return info

        except Exception as e:
            self.logger.error(f"Failed to get stage info: {e}")
            return {"error": str(e)}

    def __del__(self):
        """デストラクタ - リソース清理"""
        if hasattr(self, 'original_stdout') and self.original_stdout:
            sys.stdout = self.original_stdout