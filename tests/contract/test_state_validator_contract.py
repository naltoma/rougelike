"""
Contract Test: StateValidator Interface

A*とゲームエンジンの状態比較機能の契約テスト。
このテストは実装前に失敗する必要があります（TDD）。
"""

import pytest
from typing import List
from src.stage_validator import StateValidator
from src.stage_validator.models import ExecutionLog, StateDifference


@pytest.mark.contract
@pytest.mark.state_validator
class TestStateValidatorContract:
    """StateValidatorインターフェースの契約テスト"""

    def test_state_validator_can_be_imported(self):
        """StateValidatorクラスをインポート可能であること"""
        # このテストは実装が存在しないため失敗するはず
        assert StateValidator is not None

    def test_validate_turn_by_turn_method_exists(self):
        """validate_turn_by_turn メソッドが存在すること"""
        validator = StateValidator()
        assert hasattr(validator, 'validate_turn_by_turn')
        assert callable(getattr(validator, 'validate_turn_by_turn'))

    def test_validate_turn_by_turn_accepts_solution_path(self):
        """validate_turn_by_turn が解法例リストを受け取ること"""
        validator = StateValidator()
        solution_path = ["move", "turn_left", "attack"]

        # 実装前なので ImportError や AttributeError で失敗するはず
        result = validator.validate_turn_by_turn(solution_path)
        assert isinstance(result, List)

    def test_validate_turn_by_turn_returns_differences_list(self):
        """validate_turn_by_turn が差異リストを返すこと"""
        validator = StateValidator()
        solution_path = ["move", "wait", "pickup"]

        differences = validator.validate_turn_by_turn(solution_path)
        assert isinstance(differences, List)
        # 空リストまたは StateDifference オブジェクトのリスト
        for diff in differences:
            assert isinstance(diff, StateDifference)

    def test_compare_states_method_exists(self):
        """compare_states メソッドが存在すること"""
        validator = StateValidator()
        assert hasattr(validator, 'compare_states')
        assert callable(getattr(validator, 'compare_states'))

    def test_compare_states_accepts_execution_logs(self):
        """compare_states が ExecutionLog を受け取ること"""
        validator = StateValidator()

        # ダミーの ExecutionLog（実装前なので作成できないはず）
        astar_log = ExecutionLog(
            step_number=1,
            engine_type="astar",
            player_position=(2, 3),
            player_direction="right",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        engine_log = ExecutionLog(
            step_number=1,
            engine_type="game_engine",
            player_position=(2, 3),
            player_direction="right",
            enemy_states=[],
            action_taken="move",
            game_over=False,
            victory=False
        )

        result = validator.compare_states(astar_log, engine_log)
        assert isinstance(result, List)

    def test_generate_debug_report_method_exists(self):
        """generate_debug_report メソッドが存在すること"""
        validator = StateValidator()
        assert hasattr(validator, 'generate_debug_report')
        assert callable(getattr(validator, 'generate_debug_report'))

    def test_generate_debug_report_returns_string(self):
        """generate_debug_report が文字列を返すこと"""
        validator = StateValidator()
        differences = []  # 空の差異リスト

        report = validator.generate_debug_report(differences)
        assert isinstance(report, str)

    def test_stage_file_parameter_handling(self):
        """ステージファイルパラメータの処理"""
        validator = StateValidator()

        # ステージファイルを指定して検証を実行
        stage_file = "stages/generated_patrol_2025.yml"
        solution_path = ["move", "turn_right", "wait"]

        # 実装前なので設定メソッドが存在しないはず
        if hasattr(validator, 'set_stage_file'):
            validator.set_stage_file(stage_file)

        differences = validator.validate_turn_by_turn(solution_path)
        assert isinstance(differences, List)

    def test_error_handling_for_invalid_solution_path(self):
        """無効な解法例に対するエラーハンドリング"""
        validator = StateValidator()

        # 無効なアクション
        invalid_solution = ["invalid_action", "another_invalid"]

        # 実装前なので適切なエラーハンドリングが存在しないはず
        with pytest.raises((ValueError, TypeError, AttributeError, ImportError)):
            validator.validate_turn_by_turn(invalid_solution)

    def test_concurrent_validation_support(self):
        """並行検証のサポート"""
        validator = StateValidator()

        # 複数の解法例を並行処理できるか
        solution1 = ["move", "move", "pickup"]
        solution2 = ["turn_left", "move", "attack"]

        # 実装前なので並行処理機能は存在しないはず
        if hasattr(validator, 'validate_multiple'):
            results = validator.validate_multiple([solution1, solution2])
            assert len(results) == 2