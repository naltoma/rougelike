"""
Contract Test: ExecutionEngine Interface

ゲーム実行エンジンの抽象インターフェースの契約テスト。
このテストは実装前に失敗する必要があります（TDD）。
"""

import pytest
from typing import List
from src.stage_validator import ExecutionEngine
from src.stage_validator.models import ExecutionLog


@pytest.mark.contract
@pytest.mark.state_validator
class TestExecutionEngineContract:
    """ExecutionEngineインターフェースの契約テスト"""

    def test_execution_engine_can_be_imported(self):
        """ExecutionEngineクラスをインポート可能であること"""
        # このテストは実装が存在しないため失敗するはず
        assert ExecutionEngine is not None

    def test_execution_engine_is_abstract(self):
        """ExecutionEngineが抽象クラスであること"""
        # 抽象クラスなので直接インスタンス化はできないはず
        with pytest.raises(TypeError):
            ExecutionEngine()

    def test_execute_solution_method_exists(self):
        """execute_solution メソッドが抽象メソッドとして定義されていること"""
        # 実装前なのでメソッド定義が存在しないはず
        assert hasattr(ExecutionEngine, 'execute_solution')

        # 抽象メソッドかチェック
        method = getattr(ExecutionEngine, 'execute_solution')
        assert hasattr(method, '__isabstractmethod__')

    def test_get_current_state_method_exists(self):
        """get_current_state メソッドが抽象メソッドとして定義されていること"""
        assert hasattr(ExecutionEngine, 'get_current_state')

        method = getattr(ExecutionEngine, 'get_current_state')
        assert hasattr(method, '__isabstractmethod__')

    def test_reset_stage_method_exists(self):
        """reset_stage メソッドが抽象メソッドとして定義されていること"""
        assert hasattr(ExecutionEngine, 'reset_stage')

        method = getattr(ExecutionEngine, 'reset_stage')
        assert hasattr(method, '__isabstractmethod__')

    def test_concrete_implementation_required(self):
        """具象実装が必要であること"""

        # 不完全な実装クラス
        class IncompleteEngine(ExecutionEngine):
            # execute_solution のみ実装
            def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
                return []

        # 抽象メソッドが未実装なのでインスタンス化できないはず
        with pytest.raises(TypeError):
            IncompleteEngine()

    def test_complete_implementation_possible(self):
        """完全な実装が可能であること"""

        class CompleteEngine(ExecutionEngine):
            def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
                return []

            def get_current_state(self) -> ExecutionLog:
                # 実装前なので ExecutionLog が存在しないはず
                return ExecutionLog(
                    step_number=0,
                    engine_type="test",
                    player_position=(0, 0),
                    player_direction="up",
                    enemy_states=[],
                    action_taken="none",
                    game_over=False,
                    victory=False
                )

            def reset_stage(self, stage_file: str) -> None:
                pass

        # 完全実装なのでインスタンス化可能
        engine = CompleteEngine()
        assert engine is not None

    def test_execute_solution_signature(self):
        """execute_solution メソッドのシグネチャ"""

        class TestEngine(ExecutionEngine):
            def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
                # 実装前なので ExecutionLog リストを返せないはず
                logs = []
                for i, action in enumerate(solution_path):
                    log = ExecutionLog(
                        step_number=i,
                        engine_type="test_engine",
                        player_position=(i, i),
                        player_direction="up",
                        enemy_states=[],
                        action_taken=action,
                        game_over=False,
                        victory=False
                    )
                    logs.append(log)
                return logs

            def get_current_state(self) -> ExecutionLog:
                return ExecutionLog(
                    step_number=0,
                    engine_type="test",
                    player_position=(0, 0),
                    player_direction="up",
                    enemy_states=[],
                    action_taken="none",
                    game_over=False,
                    victory=False
                )

            def reset_stage(self, stage_file: str) -> None:
                pass

        engine = TestEngine()
        solution = ["move", "turn_left"]
        result = engine.execute_solution(solution)

        assert isinstance(result, List)
        assert len(result) == 2
        assert all(isinstance(log, ExecutionLog) for log in result)

    def test_get_current_state_signature(self):
        """get_current_state メソッドのシグネチャ"""

        class TestEngine(ExecutionEngine):
            def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
                return []

            def get_current_state(self) -> ExecutionLog:
                return ExecutionLog(
                    step_number=5,
                    engine_type="test",
                    player_position=(3, 4),
                    player_direction="down",
                    enemy_states=[],
                    action_taken="wait",
                    game_over=True,
                    victory=False
                )

            def reset_stage(self, stage_file: str) -> None:
                pass

        engine = TestEngine()
        current_state = engine.get_current_state()

        assert isinstance(current_state, ExecutionLog)
        assert current_state.step_number == 5
        assert current_state.player_position == (3, 4)

    def test_reset_stage_signature(self):
        """reset_stage メソッドのシグネチャ"""

        class TestEngine(ExecutionEngine):
            def __init__(self):
                self.stage_file = None

            def execute_solution(self, solution_path: List[str]) -> List[ExecutionLog]:
                return []

            def get_current_state(self) -> ExecutionLog:
                return ExecutionLog(
                    step_number=0,
                    engine_type="test",
                    player_position=(0, 0),
                    player_direction="up",
                    enemy_states=[],
                    action_taken="none",
                    game_over=False,
                    victory=False
                )

            def reset_stage(self, stage_file: str) -> None:
                self.stage_file = stage_file

        engine = TestEngine()
        stage_file = "stages/test.yml"

        # None を返すこと
        result = engine.reset_stage(stage_file)
        assert result is None
        assert engine.stage_file == stage_file