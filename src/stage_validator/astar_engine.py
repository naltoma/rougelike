"""
AStarEngine Wrapper Implementation

既存のA*パスファインディング実装をラップして
ExecutionEngineインターフェースを提供する。
"""

from typing import List, Dict, Any, Optional, Tuple
import sys
import os
from pathlib import Path

# 既存のstage_validatorモジュールをインポート（オプショナル）
StagePathfinder = None
SolutionCodeGenerator = None

try:
    from src.stage_validator.pathfinding import StagePathfinder
    from src.stage_validator.solution_generator import SolutionCodeGenerator
except ImportError:
    try:
        # パス調整が必要な場合
        sys.path.append(str(Path(__file__).parent.parent.parent))
        from src.stage_validator.pathfinding import StagePathfinder
        from src.stage_validator.solution_generator import SolutionCodeGenerator
    except ImportError:
        # フォールバック: 依存関係が見つからない場合はNoneのまま
        pass

from .execution_engine import ExecutionEngine
from .models import ExecutionLog, EnemyState, EngineType, ValidationConfig
from .unified_enemy_ai import UnifiedEnemyAI


class AStarEngine(ExecutionEngine):
    """A*アルゴリズム実行エンジンラッパー"""

    def __init__(self, config: Optional[ValidationConfig] = None):
        super().__init__("AStar", config)

        self.pathfinder: Optional[AStarPathfinder] = None
        self.solution_generator: Optional[SolutionGenerator] = None
        self.unified_ai: Optional[UnifiedEnemyAI] = None

        # A*固有の状態
        self.stage_data: Optional[Dict] = None
        self.initial_player_pos: Tuple[int, int] = (0, 0)
        self.initial_player_dir: str = "up"
        self.initial_enemies: List[Dict] = []

        # 実行時状態
        self.current_player_pos: Tuple[int, int] = (0, 0)
        self.current_player_dir: str = "up"
        self.current_enemies: List[EnemyState] = []
        self.collected_items: set = set()

    def reset_stage(self, stage_file: str) -> None:
        """ステージを初期状態にリセット"""
        self.validate_stage_file(stage_file)
        self.current_stage_file = stage_file

        try:
            # 既存のYAMLロード機能を使用
            from src.yaml_manager.core import load_stage_config
            self.stage_data = load_stage_config(stage_file)

            # プレイヤー初期位置を設定
            self.initial_player_pos = tuple(self.stage_data.get('player_start', [1, 1]))
            self.initial_player_dir = self.stage_data.get('player_direction', 'up')

            # 敵初期状態を設定
            self.initial_enemies = self.stage_data.get('enemies', [])

            # A*パスファインダーを初期化
            if StagePathfinder is None or SolutionCodeGenerator is None:
                raise RuntimeError("A* pathfinding modules not available. Please check src.stage_validator dependencies.")

            self.pathfinder = StagePathfinder()  # StagePathfinderのコンストラクタを確認
            self.solution_generator = SolutionCodeGenerator()  # SolutionCodeGeneratorのコンストラクタを確認

            # 統一敵AIを初期化（後で実装）
            # self.unified_ai = UnifiedEnemyAI()

            # 現在状態を初期化
            self._reset_current_state()

            self.is_initialized = True
            self.logger.info(f"A* engine initialized with stage: {stage_file}")

        except Exception as e:
            self.logger.error(f"Failed to initialize A* engine: {e}")
            raise RuntimeError(f"A* engine initialization failed: {e}")

    def _reset_current_state(self) -> None:
        """現在状態を初期状態にリセット"""
        self.current_player_pos = self.initial_player_pos
        self.current_player_dir = self.initial_player_dir
        self.collected_items.clear()
        self.clear_logs()

        # 敵状態を初期化
        self.current_enemies = []
        for i, enemy_data in enumerate(self.initial_enemies):
            enemy_state = EnemyState(
                enemy_id=enemy_data.get('id', f'enemy_{i}'),
                position=tuple(enemy_data.get('position', [0, 0])),
                direction=enemy_data.get('direction', 'up'),
                patrol_index=enemy_data.get('patrol_index', 0),
                alert_state=enemy_data.get('alert_state', 'patrol'),
                vision_range=enemy_data.get('vision_range', 3),
                health=enemy_data.get('health', 1),
                enemy_type=enemy_data.get('type', 'patrol')
            )
            self.current_enemies.append(enemy_state)

    def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
        """解法例を実行してログを生成"""
        if not self.is_initialized:
            raise RuntimeError("Engine not initialized. Call reset_stage() first.")

        self.validate_solution_path(solution_path)
        self.clear_logs()
        self._reset_current_state()

        self.logger.info(f"Executing solution with {len(solution_path)} steps")

        try:
            for step_number, action in enumerate(solution_path):
                self.logger.debug(f"Step {step_number}: executing action '{action}'")

                # プレイヤーアクション実行
                success = self._execute_player_action(action)
                if not success:
                    self.logger.warning(f"Player action '{action}' failed at step {step_number}")

                # 敵行動を計算・実行
                self._execute_enemy_actions()

                # 現在状態をログに記録
                log = self._create_execution_log(step_number, action)
                self.execution_logs.append(log)

                # ゲーム終了条件チェック
                if self._check_game_over():
                    self.logger.info(f"Game ended at step {step_number}")
                    break

                if self._check_victory():
                    self.logger.info(f"Victory achieved at step {step_number}")
                    break

            self.logger.info(f"Solution execution completed: {len(self.execution_logs)} steps")
            return self.execution_logs

        except Exception as e:
            self.logger.error(f"Solution execution failed: {e}")
            raise RuntimeError(f"A* execution error: {e}")

    def _execute_player_action(self, action: str) -> bool:
        """プレイヤーアクション実行"""
        self.validate_action(action)

        if action == "move":
            next_pos = self.calculate_next_position(self.current_player_pos, self.current_player_dir)
            if self._is_valid_position(next_pos) and not self._is_wall(next_pos):
                self.current_player_pos = next_pos
                return True
            return False

        elif action == "turn_left":
            self.current_player_dir = self.rotate_direction(self.current_player_dir, "turn_left")
            return True

        elif action == "turn_right":
            self.current_player_dir = self.rotate_direction(self.current_player_dir, "turn_right")
            return True

        elif action == "pickup":
            return self._try_pickup_item()

        elif action == "dispose":
            return self._try_dispose_item()

        elif action == "attack":
            return self._try_attack()

        elif action == "wait":
            return True  # 常に成功

        return False

    def _execute_enemy_actions(self) -> None:
        """敵行動実行"""
        if not self.unified_ai:
            # 統一AIが未実装の場合は簡単なパトロール
            self._execute_simple_enemy_patrol()
            return

        # 統一AIを使用した敵行動
        for i, enemy in enumerate(self.current_enemies):
            try:
                # 敵のアクション計算
                enemy_action = self.unified_ai.calculate_enemy_action(enemy, self.current_player_pos)

                # アクション実行
                updated_enemy = self._execute_enemy_action(enemy, enemy_action)
                self.current_enemies[i] = updated_enemy

                # パトロール状態更新
                if enemy.enemy_type == "patrol":
                    self.current_enemies[i] = self.unified_ai.update_patrol_state(updated_enemy)

            except Exception as e:
                self.logger.warning(f"Enemy {enemy.enemy_id} action failed: {e}")

    def _execute_simple_enemy_patrol(self) -> None:
        """シンプルな敵パトロール（統一AI未実装時のフォールバック）"""
        for i, enemy in enumerate(self.current_enemies):
            if enemy.enemy_type == "patrol":
                # シンプルなパトロールロジック
                new_patrol_index = (enemy.patrol_index + 1) % 4

                # パトロールインデックスに基づく向き決定
                directions = ["up", "right", "down", "left"]
                new_direction = directions[new_patrol_index]

                updated_enemy = EnemyState(
                    enemy_id=enemy.enemy_id,
                    position=enemy.position,
                    direction=new_direction,
                    patrol_index=new_patrol_index,
                    alert_state=enemy.alert_state,
                    vision_range=enemy.vision_range,
                    health=enemy.health,
                    enemy_type=enemy.enemy_type
                )

                self.current_enemies[i] = updated_enemy

    def _execute_enemy_action(self, enemy: EnemyState, action: str) -> EnemyState:
        """個別の敵アクション実行"""
        if action == "move":
            next_pos = self.calculate_next_position(enemy.position, enemy.direction)
            if self._is_valid_position(next_pos) and not self._is_wall(next_pos):
                return EnemyState(
                    enemy_id=enemy.enemy_id,
                    position=next_pos,
                    direction=enemy.direction,
                    patrol_index=enemy.patrol_index,
                    alert_state=enemy.alert_state,
                    vision_range=enemy.vision_range,
                    health=enemy.health,
                    enemy_type=enemy.enemy_type
                )

        elif action in ["turn_left", "turn_right"]:
            new_direction = self.rotate_direction(enemy.direction, action)
            return EnemyState(
                enemy_id=enemy.enemy_id,
                position=enemy.position,
                direction=new_direction,
                patrol_index=enemy.patrol_index,
                alert_state=enemy.alert_state,
                vision_range=enemy.vision_range,
                health=enemy.health,
                enemy_type=enemy.enemy_type
            )

        # アクション実行できない場合は元の状態を返す
        return enemy

    def _create_execution_log(self, step_number: int, action: str) -> ExecutionLog:
        """実行ログ作成"""
        return ExecutionLog(
            step_number=step_number,
            engine_type=EngineType.ASTAR,
            player_position=self.current_player_pos,
            player_direction=self.current_player_dir,
            enemy_states=self.current_enemies.copy(),
            action_taken=action,
            game_over=self._check_game_over(),
            victory=self._check_victory()
        )

    def get_current_state(self) -> ExecutionLog:
        """現在状態を取得"""
        if self.execution_logs:
            return self.execution_logs[-1]

        return ExecutionLog(
            step_number=0,
            engine_type=EngineType.ASTAR,
            player_position=self.current_player_pos,
            player_direction=self.current_player_dir,
            enemy_states=self.current_enemies.copy(),
            action_taken="none",
            game_over=False,
            victory=False
        )

    def _is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """有効な位置かチェック"""
        if not self.stage_data:
            return True

        stage_size = self.stage_data.get('size', [20, 20])
        x, y = pos
        return 0 <= x < stage_size[0] and 0 <= y < stage_size[1]

    def _is_wall(self, pos: Tuple[int, int]) -> bool:
        """壁かどうかチェック"""
        if not self.stage_data:
            return False

        walls = self.stage_data.get('walls', [])
        return list(pos) in walls

    def _try_pickup_item(self) -> bool:
        """アイテム拾得試行"""
        if not self.stage_data:
            return False

        items = self.stage_data.get('items', [])
        for item in items:
            item_pos = tuple(item.get('position', [0, 0]))
            if item_pos == self.current_player_pos:
                item_id = item.get('id', f'item_{item_pos}')
                if item_id not in self.collected_items:
                    self.collected_items.add(item_id)
                    return True
        return False

    def _try_dispose_item(self) -> bool:
        """アイテム破棄試行"""
        if self.collected_items:
            # 最初に拾ったアイテムを破棄
            self.collected_items.pop()
            return True
        return False

    def _try_attack(self) -> bool:
        """攻撃試行"""
        attack_pos = self.calculate_next_position(self.current_player_pos, self.current_player_dir)

        for i, enemy in enumerate(self.current_enemies):
            if enemy.position == attack_pos and enemy.health > 0:
                # 敵にダメージを与える
                damaged_enemy = EnemyState(
                    enemy_id=enemy.enemy_id,
                    position=enemy.position,
                    direction=enemy.direction,
                    patrol_index=enemy.patrol_index,
                    alert_state=enemy.alert_state,
                    vision_range=enemy.vision_range,
                    health=max(0, enemy.health - 1),
                    enemy_type=enemy.enemy_type
                )
                self.current_enemies[i] = damaged_enemy
                return True

        return False

    def _check_game_over(self) -> bool:
        """ゲーム終了判定"""
        # プレイヤーと敵の衝突チェック
        return self.has_enemy_conflicts(self.current_player_pos, self.current_enemies)

    def _check_victory(self) -> bool:
        """勝利判定"""
        if not self.stage_data:
            return False

        goal_pos = tuple(self.stage_data.get('goal', [10, 10]))
        return self.current_player_pos == goal_pos

    def generate_solution(self, max_steps: Optional[int] = None) -> List[str]:
        """A*アルゴリズムで解法を生成"""
        if not self.is_initialized or not self.solution_generator:
            raise RuntimeError("Engine not initialized")

        try:
            solution = self.solution_generator.generate_solution(
                max_steps or self.config.max_solution_steps
            )
            self.logger.info(f"Generated solution with {len(solution)} steps")
            return solution
        except Exception as e:
            self.logger.error(f"Solution generation failed: {e}")
            raise RuntimeError(f"A* solution generation error: {e}")