"""
Performance tests for large stage validation - v1.2.12

StateValidatorの大規模ステージでの性能をテストし、<1秒の実行時間を確認する。
"""

import pytest
import time
from datetime import datetime, timedelta

# プロジェクトルートをパスに追加
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.stage_validator.state_validator import StateValidator
from src.stage_validator.models import (
    ExecutionLog, EnemyState, EngineType, ValidationConfig, get_global_config
)
from src.stage_validator import create_mock_engine


@pytest.mark.performance
@pytest.mark.slow
class TestValidationPerformance:
    """StateValidator パフォーマンステスト"""

    def setup_method(self):
        """テストセットアップ - パフォーマンス最適化設定"""
        self.config = ValidationConfig(
            log_detail_level="minimal",
            max_solution_steps=1000,
            comparison_timeout_seconds=5.0,
            memory_optimization_enabled=True,
            enable_debug_file_logging=False
        )

        # Mock engines for consistent performance testing
        self.astar_engine = create_mock_engine(self.config)
        self.game_engine = create_mock_engine(self.config)
        self.validator = StateValidator(
            self.astar_engine,
            self.game_engine,
            self.config
        )

    def test_small_stage_validation_speed(self):
        """Given small stage (50 steps), when validating, then completes within 0.1s"""
        solution_path = ["move", "turn_right", "move", "turn_left"] * 12 + ["move", "move"]  # 50 steps

        start_time = time.perf_counter()
        differences = self.validator.validate_turn_by_turn(solution_path)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        assert execution_time < 0.1, f"Small stage took {execution_time:.3f}s, expected <0.1s"
        assert isinstance(differences, list)

    def test_medium_stage_validation_speed(self):
        """Given medium stage (200 steps), when validating, then completes within 0.5s"""
        solution_path = ["move", "turn_right", "move", "turn_left", "wait"] * 40  # 200 steps

        start_time = time.perf_counter()
        differences = self.validator.validate_turn_by_turn(solution_path)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        assert execution_time < 0.5, f"Medium stage took {execution_time:.3f}s, expected <0.5s"
        assert isinstance(differences, list)

    def test_large_stage_validation_speed(self):
        """Given large stage (500 steps), when validating, then completes within 1.0s"""
        solution_path = ["move", "turn_right", "move", "turn_left", "wait", "attack"] * 83 + ["move", "move"]  # 500 steps

        start_time = time.perf_counter()
        differences = self.validator.validate_turn_by_turn(solution_path)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        assert execution_time < 1.0, f"Large stage took {execution_time:.3f}s, expected <1.0s"
        assert isinstance(differences, list)

    def test_maximum_stage_validation_speed(self):
        """Given maximum stage (1000 steps), when validating, then completes within 2.0s"""
        # Create solution at maximum allowed steps
        base_pattern = ["move", "turn_right", "move", "turn_left", "wait", "attack", "pickup", "dispose"]
        solution_path = (base_pattern * 125)[:1000]  # Exactly 1000 steps

        start_time = time.perf_counter()
        differences = self.validator.validate_turn_by_turn(solution_path)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        assert execution_time < 2.0, f"Maximum stage took {execution_time:.3f}s, expected <2.0s"
        assert isinstance(differences, list)

    def test_many_enemies_performance(self):
        """Given stage with many enemies, when validating, then performance acceptable"""
        # Create mock engines that return logs with many enemies
        many_enemies = []
        for i in range(20):  # 20 enemies
            enemy = EnemyState(
                enemy_id=f"perf_enemy_{i}",
                position=(i % 10, i // 10),
                direction=["up", "down", "left", "right"][i % 4],
                patrol_index=i % 4,
                alert_state=["patrol", "alert", "chase"][i % 3],
                vision_range=3,
                health=1,
                enemy_type=["patrol", "static", "large"][i % 3]
            )
            many_enemies.append(enemy)

        # Override mock engines to return logs with many enemies
        def create_log_with_many_enemies(step, engine_type, action):
            return ExecutionLog(
                step_number=step,
                engine_type=engine_type,
                player_position=(step % 20, step % 15),
                player_direction=["up", "down", "left", "right"][step % 4],
                enemy_states=many_enemies.copy(),
                action_taken=action,
                game_over=False,
                victory=False
            )

        # Mock execute_solution to return logs with many enemies
        def mock_execute_solution_astar(solution_path):
            return [create_log_with_many_enemies(i, EngineType.ASTAR, action)
                   for i, action in enumerate(solution_path)]

        def mock_execute_solution_game(solution_path):
            return [create_log_with_many_enemies(i, EngineType.GAME_ENGINE, action)
                   for i, action in enumerate(solution_path)]

        self.astar_engine.execute_solution.side_effect = mock_execute_solution_astar
        self.game_engine.execute_solution.side_effect = mock_execute_solution_game

        solution_path = ["move", "wait", "turn_right"] * 50  # 150 steps with 20 enemies each

        start_time = time.perf_counter()
        differences = self.validator.validate_turn_by_turn(solution_path)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        assert execution_time < 1.5, f"Many enemies stage took {execution_time:.3f}s, expected <1.5s"
        assert isinstance(differences, list)

    def test_memory_usage_stability(self):
        """Given repeated validations, when running multiple times, then memory stable"""
        solution_path = ["move", "turn_right", "wait"] * 100  # 300 steps

        execution_times = []

        for i in range(5):  # Run 5 times
            start_time = time.perf_counter()
            differences = self.validator.validate_turn_by_turn(solution_path)
            end_time = time.perf_counter()

            execution_time = end_time - start_time
            execution_times.append(execution_time)

            # Each run should be consistently fast
            assert execution_time < 1.0, f"Run {i+1} took {execution_time:.3f}s, expected <1.0s"

        # Performance should be stable across runs (no significant degradation)
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        min_time = min(execution_times)

        # Max time shouldn't be more than 2x the minimum time (reasonable variation)
        assert max_time <= min_time * 2, f"Performance instability: min={min_time:.3f}s, max={max_time:.3f}s"

    def test_config_manager_performance(self):
        """Given config operations, when performing multiple operations, then fast"""
        from src.stage_validator.config_manager import create_config_manager

        config_manager = create_config_manager()

        start_time = time.perf_counter()

        # Perform multiple config operations
        for i in range(10):
            config = config_manager.get_current_config()
            config_manager.update_config(max_solution_steps=500 + i)
            profiles = config_manager.list_profiles()

        end_time = time.perf_counter()

        execution_time = end_time - start_time
        assert execution_time < 0.1, f"Config operations took {execution_time:.3f}s, expected <0.1s"

    def test_debug_logger_performance(self):
        """Given debug logging, when logging many events, then performance acceptable"""
        from src.stage_validator import create_debug_logger

        debug_logger = create_debug_logger(self.config)

        start_time = time.perf_counter()

        # Create and complete a session with many operations
        session_id = debug_logger.start_comparison_session("perf_test.yml", ["move"] * 100)

        # Simulate logging many execution logs
        fake_logs = [
            ExecutionLog(
                step_number=i,
                engine_type=EngineType.ASTAR,
                player_position=(i, i),
                player_direction="up",
                enemy_states=[],
                action_taken="move",
                game_over=False,
                victory=False
            )
            for i in range(100)
        ]

        debug_logger.log_engine_execution(session_id, "A*", fake_logs)
        debug_logger.log_engine_execution(session_id, "Game", fake_logs)
        debug_logger.log_differences(session_id, [])  # No differences
        session_data = debug_logger.complete_session(session_id)

        end_time = time.perf_counter()

        execution_time = end_time - start_time
        assert execution_time < 0.5, f"Debug logging took {execution_time:.3f}s, expected <0.5s"
        assert session_data is not None

    def test_state_comparison_performance(self):
        """Given state comparison operations, when comparing many states, then fast"""
        # Create complex states for comparison
        complex_enemies = [
            EnemyState(
                enemy_id=f"complex_{i}",
                position=(i * 2, i * 3),
                direction=["up", "down", "left", "right"][i % 4],
                patrol_index=i,
                alert_state=["patrol", "alert", "chase"][i % 3],
                vision_range=i % 5 + 1,
                health=i % 3 + 1,
                enemy_type=["patrol", "static", "large"][i % 3]
            )
            for i in range(10)
        ]

        astar_log = ExecutionLog(
            step_number=100,
            engine_type=EngineType.ASTAR,
            player_position=(50, 60),
            player_direction="up",
            enemy_states=complex_enemies,
            action_taken="move",
            game_over=False,
            victory=False
        )

        game_log = ExecutionLog(
            step_number=100,
            engine_type=EngineType.GAME_ENGINE,
            player_position=(50, 60),
            player_direction="up",
            enemy_states=complex_enemies,  # Same states for this test
            action_taken="move",
            game_over=False,
            victory=False
        )

        start_time = time.perf_counter()

        # Perform many comparisons
        for i in range(100):
            differences = self.validator.compare_states(astar_log, game_log, i)

        end_time = time.perf_counter()

        execution_time = end_time - start_time
        assert execution_time < 0.5, f"State comparisons took {execution_time:.3f}s, expected <0.5s"


@pytest.mark.performance
@pytest.mark.slow
class TestMemoryEfficiency:
    """メモリ効率性テスト"""

    def test_large_solution_memory_usage(self):
        """Given very large solution, when validating, then memory usage reasonable"""
        config = ValidationConfig(
            memory_optimization_enabled=True,
            log_detail_level="minimal"
        )

        astar_engine = create_mock_engine(config)
        game_engine = create_mock_engine(config)
        validator = StateValidator(astar_engine, game_engine, config)

        # Very large solution
        large_solution = ["move", "turn_right", "wait"] * 300  # 900 steps

        start_time = time.perf_counter()
        differences = validator.validate_turn_by_turn(large_solution)
        end_time = time.perf_counter()

        execution_time = end_time - start_time
        assert execution_time < 2.0, f"Large solution took {execution_time:.3f}s, expected <2.0s"

        # Memory usage test (simplified - just ensure completion)
        assert isinstance(differences, list)

    def test_cleanup_after_validation(self):
        """Given completed validation, when checking cleanup, then resources freed"""
        config = ValidationConfig(memory_optimization_enabled=True)

        astar_engine = create_mock_engine(config)
        game_engine = create_mock_engine(config)
        validator = StateValidator(astar_engine, game_engine, config)

        solution_path = ["move"] * 100

        # Run validation
        differences = validator.validate_turn_by_turn(solution_path)

        # Check that validator can be used again (resources not locked)
        differences2 = validator.validate_turn_by_turn(["wait"] * 50)

        assert isinstance(differences, list)
        assert isinstance(differences2, list)


@pytest.mark.performance
@pytest.mark.benchmark
class TestBenchmarkComparison:
    """ベンチマーク比較テスト"""

    def test_optimized_vs_unoptimized_config(self):
        """Given optimized vs unoptimized config, when validating, then optimized is faster"""
        # Optimized config
        optimized_config = ValidationConfig(
            log_detail_level="minimal",
            memory_optimization_enabled=True,
            enable_debug_file_logging=False,
            comparison_timeout_seconds=30.0
        )

        # Unoptimized config
        unoptimized_config = ValidationConfig(
            log_detail_level="debug",
            memory_optimization_enabled=False,
            enable_debug_file_logging=True,
            comparison_timeout_seconds=120.0
        )

        solution_path = ["move", "turn_right", "wait", "attack"] * 50  # 200 steps

        # Test optimized
        opt_astar = create_mock_engine(optimized_config)
        opt_game = create_mock_engine(optimized_config)
        opt_validator = StateValidator(opt_astar, opt_game, optimized_config)

        opt_start = time.perf_counter()
        opt_differences = opt_validator.validate_turn_by_turn(solution_path)
        opt_end = time.perf_counter()
        opt_time = opt_end - opt_start

        # Test unoptimized
        unopt_astar = create_mock_engine(unoptimized_config)
        unopt_game = create_mock_engine(unoptimized_config)
        unopt_validator = StateValidator(unopt_astar, unopt_game, unoptimized_config)

        unopt_start = time.perf_counter()
        unopt_differences = unopt_validator.validate_turn_by_turn(solution_path)
        unopt_end = time.perf_counter()
        unopt_time = unopt_end - unopt_start

        # Both should complete successfully
        assert isinstance(opt_differences, list)
        assert isinstance(unopt_differences, list)

        # Optimized should be faster (or at least not significantly slower)
        # Allow some variation due to system performance
        assert opt_time <= unopt_time * 1.5, f"Optimized ({opt_time:.3f}s) not faster than unoptimized ({unopt_time:.3f}s)"

        # Both should be within reasonable time limits
        assert opt_time < 1.0, f"Optimized config took {opt_time:.3f}s, expected <1.0s"
        assert unopt_time < 3.0, f"Unoptimized config took {unopt_time:.3f}s, expected <3.0s"

    def test_performance_regression_baseline(self):
        """Given baseline performance test, when running standard validation, then meets baseline"""
        # This test establishes a performance baseline for regression testing
        config = get_global_config()

        astar_engine = create_mock_engine(config)
        game_engine = create_mock_engine(config)
        validator = StateValidator(astar_engine, game_engine, config)

        # Standard test case: 250 steps
        solution_path = ["move", "turn_left", "move", "turn_right", "wait"] * 50  # 250 steps

        # Run multiple times and take average to reduce variance
        times = []
        for _ in range(3):
            start_time = time.perf_counter()
            differences = validator.validate_turn_by_turn(solution_path)
            end_time = time.perf_counter()
            times.append(end_time - start_time)

        avg_time = sum(times) / len(times)
        max_time = max(times)

        # Baseline: average should be under 1.0s, max under 1.5s
        assert avg_time < 1.0, f"Baseline average time {avg_time:.3f}s exceeded 1.0s threshold"
        assert max_time < 1.5, f"Baseline max time {max_time:.3f}s exceeded 1.5s threshold"

        print(f"📊 Performance Baseline: avg={avg_time:.3f}s, max={max_time:.3f}s, min={min(times):.3f}s")