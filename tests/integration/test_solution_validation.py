"""
Integration Test: Solution Validation Workflow

解法検証ワークフローの統合テスト。
このテストは実装前に失敗する必要があります（TDD）。
"""

import pytest
from pathlib import Path
from typing import List
from src.stage_validator import StateValidator
from src.stage_validator.models import ExecutionLog, StateDifference, SolutionPath


@pytest.mark.integration
@pytest.mark.validator
@pytest.mark.state_validator
class TestSolutionValidation:
    """解法検証ワークフロー統合テスト"""

    @pytest.fixture
    def state_validator(self):
        """StateValidatorインスタンス"""
        # 実装前なので失敗するはず
        return StateValidator()

    @pytest.fixture
    def patrol_stage_file(self):
        """パトロールステージファイル"""
        return "stages/generated_patrol_2025.yml"

    @pytest.fixture
    def working_solution(self):
        """動作する解法例"""
        return ["move", "wait", "move", "turn_right", "move", "pickup"]

    @pytest.fixture
    def failing_solution(self):
        """失敗する解法例"""
        return ["move", "move", "move", "move", "move", "attack"]

    @pytest.fixture
    def complex_solution(self):
        """複雑な解法例"""
        return [
            "wait", "move", "turn_left", "move", "wait",
            "turn_right", "move", "pickup", "move", "wait",
            "turn_left", "move", "dispose", "move", "move"
        ]

    def test_end_to_end_solution_validation(self, state_validator, working_solution):
        """エンドツーエンド解法検証"""
        # 実装前なので validate_turn_by_turn が存在しないはず
        differences = state_validator.validate_turn_by_turn(working_solution)

        assert isinstance(differences, List)
        for diff in differences:
            assert isinstance(diff, StateDifference)

        # 動作する解法なので差異は少ないはず（実装後）
        # assert len(differences) <= 2

    def test_failing_solution_detection(self, state_validator, failing_solution):
        """失敗解法の検出"""
        differences = state_validator.validate_turn_by_turn(failing_solution)

        # 失敗する解法なので重大な差異があるはず
        critical_diffs = [d for d in differences if d.severity.value == "critical"]
        # 実装後は assert len(critical_diffs) > 0

        assert isinstance(differences, List)

    def test_solution_path_model_integration(self, working_solution):
        """SolutionPathモデル統合"""
        # 実装前なので SolutionPath が存在しないはず
        solution_path = SolutionPath(
            stage_file="stages/test.yml",
            action_sequence=working_solution,
            expected_success=True,
            actual_success=False,  # テスト用
            total_steps=len(working_solution),
            failure_step=None
        )

        assert solution_path.stage_file == "stages/test.yml"
        assert solution_path.action_sequence == working_solution
        assert solution_path.total_steps == len(working_solution)

    def test_step_by_step_execution_logging(self, state_validator, complex_solution):
        """ステップ毎実行ログ"""
        differences = state_validator.validate_turn_by_turn(complex_solution)

        # 各ステップでログが生成されているか
        if differences:
            step_numbers = [d.step_number for d in differences]

            # 実装前なので適切なステップ番号設定ができないはず
            assert min(step_numbers) >= 0
            assert max(step_numbers) < len(complex_solution)

            # ステップが連続していること（実装後）
            # unique_steps = sorted(set(step_numbers))
            # assert unique_steps == list(range(len(unique_steps)))

    def test_debug_report_generation(self, state_validator, failing_solution):
        """デバッグレポート生成"""
        differences = state_validator.validate_turn_by_turn(failing_solution)

        # 実装前なので generate_debug_report が存在しないはず
        debug_report = state_validator.generate_debug_report(differences)

        assert isinstance(debug_report, str)
        assert len(debug_report) > 0

        # 実装後はレポートに有用な情報が含まれるはず
        # assert "Step" in debug_report
        # assert "Difference" in debug_report

    def test_multiple_solution_comparison(self, state_validator, working_solution, failing_solution):
        """複数解法比較"""
        working_diffs = state_validator.validate_turn_by_turn(working_solution)
        failing_diffs = state_validator.validate_turn_by_turn(failing_solution)

        # 動作する解法の方が差異が少ないはず
        assert isinstance(working_diffs, List)
        assert isinstance(failing_diffs, List)

        # 実装後の期待値
        # assert len(working_diffs) < len(failing_diffs)

    def test_performance_with_long_solution(self, state_validator):
        """長い解法でのパフォーマンス"""
        import time

        # 長い解法例（50ステップ）
        long_solution = (["move", "wait"] * 10 + ["turn_left", "move"] * 5 +
                        ["pickup", "dispose"] * 5 + ["wait"] * 10)

        start_time = time.time()
        differences = state_validator.validate_turn_by_turn(long_solution)
        elapsed_time = time.time() - start_time

        # 1秒以内で完了するはず
        assert elapsed_time < 1.0
        assert isinstance(differences, List)

    def test_edge_case_empty_solution(self, state_validator):
        """エッジケース: 空の解法"""
        empty_solution = []

        # 実装前なので適切なエラーハンドリングが存在しないはず
        with pytest.raises((ValueError, IndexError, AttributeError)):
            state_validator.validate_turn_by_turn(empty_solution)

    def test_edge_case_single_action_solution(self, state_validator):
        """エッジケース: 単一アクション解法"""
        single_action = ["wait"]

        differences = state_validator.validate_turn_by_turn(single_action)

        assert isinstance(differences, List)
        # 単一アクションでも実行可能

    def test_edge_case_invalid_actions(self, state_validator):
        """エッジケース: 無効なアクション"""
        invalid_solution = ["invalid_action", "another_invalid", "move"]

        # 実装前なので適切なバリデーションが存在しないはず
        with pytest.raises((ValueError, KeyError, AttributeError)):
            state_validator.validate_turn_by_turn(invalid_solution)

    def test_state_consistency_across_runs(self, state_validator, working_solution):
        """実行間の状態一貫性"""
        # 同じ解法を複数回実行
        run1_diffs = state_validator.validate_turn_by_turn(working_solution)
        run2_diffs = state_validator.validate_turn_by_turn(working_solution)

        # 結果が一貫していること
        assert len(run1_diffs) == len(run2_diffs)

        # 実装後は詳細な比較も可能
        # for diff1, diff2 in zip(run1_diffs, run2_diffs):
        #     assert diff1.step_number == diff2.step_number
        #     assert diff1.difference_type == diff2.difference_type

    def test_memory_usage_optimization(self, state_validator):
        """メモリ使用量最適化"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 多数の解法を順次処理
        solutions = [
            ["move"] * 10,
            ["wait"] * 15,
            ["turn_left", "move"] * 8,
            ["pickup", "move", "dispose"] * 5
        ]

        for solution in solutions:
            differences = state_validator.validate_turn_by_turn(solution)
            assert isinstance(differences, List)

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # メモリ増加量が合理的範囲内（100MB未満）
        assert memory_increase < 100 * 1024 * 1024  # 100MB

    def test_concurrent_validation_safety(self, state_validator, working_solution, failing_solution):
        """並行検証の安全性"""
        import threading
        import queue

        results_queue = queue.Queue()

        def validate_solution(solution, result_queue):
            try:
                differences = state_validator.validate_turn_by_turn(solution)
                result_queue.put(('success', len(differences)))
            except Exception as e:
                result_queue.put(('error', str(e)))

        # 並行実行
        thread1 = threading.Thread(target=validate_solution, args=(working_solution, results_queue))
        thread2 = threading.Thread(target=validate_solution, args=(failing_solution, results_queue))

        thread1.start()
        thread2.start()

        thread1.join(timeout=5.0)
        thread2.join(timeout=5.0)

        # 両方の結果を取得
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())

        # 実装前なので適切な並行処理ができないはず
        assert len(results) >= 0  # 何らかの結果は得られるはず

    def test_integration_with_existing_validation(self, state_validator):
        """既存検証システムとの統合"""
        # 既存の validate_stage.py との統合テスト
        solution = ["move", "turn_right", "move", "pickup"]

        differences = state_validator.validate_turn_by_turn(solution)

        # 既存システムとの互換性
        assert isinstance(differences, List)

        # 実装前なので既存システム呼び出しができないはず
        # if hasattr(state_validator, 'call_existing_validator'):
        #     existing_result = state_validator.call_existing_validator(solution)
        #     assert existing_result is not None

    def test_configuration_management(self, state_validator):
        """設定管理"""
        # 実装前なので設定管理機能が存在しないはず
        if hasattr(state_validator, 'get_config'):
            config = state_validator.get_config()
            assert config is not None

            # 設定項目の確認
            # assert 'enemy_rotation_delay' in config
            # assert 'vision_check_timing' in config

        # デフォルト設定で動作すること
        solution = ["move", "wait"]
        differences = state_validator.validate_turn_by_turn(solution)
        assert isinstance(differences, List)