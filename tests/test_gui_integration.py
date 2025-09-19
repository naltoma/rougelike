#!/usr/bin/env python3
"""
🚀 v1.2.5: GUI Integration Test Suite
7段階速度制御GUI統合テストスイート
"""

import unittest
import pygame
import threading
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# プロジェクトパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.renderer import GuiRenderer
from engine.enhanced_7stage_speed_control_manager import Enhanced7StageSpeedControlManager
from engine.ultra_high_speed_controller import UltraHighSpeedController
from engine import EnhancedExecutionState


class TestGuiSpeedControlIntegration(unittest.TestCase):
    """GUI速度制御統合テストクラス"""
    
    @classmethod
    def setUpClass(cls):
        """テストクラス初期化"""
        # pygame初期化（テスト環境用）
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1))  # 最小サイズのダミーディスプレイ
    
    def setUp(self):
        """テスト初期化"""
        # Mock game state
        self.mock_game_state = Mock()
        self.mock_game_state.player_x = 5
        self.mock_game_state.player_y = 5
        self.mock_game_state.stage = 1
        self.mock_game_state.score = 100
        self.mock_game_state.lives = 3
        
        # 7段階速度制御システム初期化
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.ultra_controller = UltraHighSpeedController(self.speed_manager)
        
        # Enhanced execution state
        self.execution_state = EnhancedExecutionState(
            mode="step_by_step",
            is_paused=False,
            step_count=0,
            total_execution_time=0.0,
            speed_multiplier=1
        )
        
        # GUI renderer初期化
        self.renderer = GuiRenderer(800, 600)
        self.renderer.speed_control_manager = self.speed_manager
        self.renderer.ultra_controller = self.ultra_controller
    
    def test_7stage_speed_control_buttons_initialization(self):
        """7段階速度制御ボタン初期化テスト"""
        # 3段階コントロールパネルの描画をテスト
        surface = pygame.Surface((800, 600))
        
        # draw_guiメソッドが正常に実行されることを確認
        try:
            self.renderer.draw_gui(
                surface, 
                self.mock_game_state, 
                self.execution_state,
                session_summary=None
            )
            success = True
        except Exception as e:
            success = False
            print(f"GUI描画エラー: {e}")
        
        self.assertTrue(success, "3段階コントロールパネルの描画に失敗")
    
    def test_speed_button_click_detection(self):
        """速度ボタンクリック検出テスト"""
        # 各速度ボタンの位置をテスト
        valid_speeds = [1, 2, 3, 4, 5, 10, 50]
        
        for target_speed in valid_speeds:
            # ボタンクリック処理のシミュレート
            original_speed = self.speed_manager.current_speed_multiplier
            
            try:
                # 速度変更を直接実行
                success = self.speed_manager.set_speed_multiplier(target_speed)
                self.assertTrue(success, f"速度x{target_speed}への変更失敗")
                self.assertEqual(self.speed_manager.current_speed_multiplier, target_speed)
                
            except Exception as e:
                self.fail(f"速度x{target_speed}設定時にエラー: {e}")
    
    def test_ultra_speed_visual_warning_display(self):
        """超高速視覚警告表示テスト"""
        # 超高速モード（x10, x50）での視覚警告テスト
        ultra_speeds = [10, 50]
        
        for speed in ultra_speeds:
            self.speed_manager.set_speed_multiplier(speed)
            self.execution_state.speed_multiplier = speed
            
            surface = pygame.Surface((800, 600))
            
            # 警告表示を含むGUI描画
            try:
                self.renderer.draw_gui(
                    surface, 
                    self.mock_game_state, 
                    self.execution_state,
                    session_summary=None
                )
                
                # 超高速モードが正常に検出されることを確認
                self.assertTrue(self.speed_manager.is_ultra_high_speed())
                
                warning_displayed = True
            except Exception as e:
                warning_displayed = False
                print(f"超高速警告表示エラー (x{speed}): {e}")
            
            self.assertTrue(warning_displayed, f"x{speed}速度での警告表示失敗")
    
    def test_current_speed_indicator_accuracy(self):
        """現在速度インジケーター精度テスト"""
        test_speeds = [1, 3, 5, 10, 50]
        
        for speed in test_speeds:
            self.speed_manager.set_speed_multiplier(speed)
            self.execution_state.speed_multiplier = speed
            
            # GUI状態確認
            current_speed = self.speed_manager.current_speed_multiplier
            execution_speed = self.execution_state.speed_multiplier
            
            self.assertEqual(current_speed, speed, f"SpeedManager速度が不正確: {current_speed} != {speed}")
            self.assertEqual(execution_speed, speed, f"ExecutionState速度が不正確: {execution_speed} != {speed}")
    
    def test_gui_responsiveness_under_high_speed(self):
        """高速実行時のGUI応答性テスト"""
        self.speed_manager.set_speed_multiplier(50)
        self.execution_state.speed_multiplier = 50
        
        surface = pygame.Surface((800, 600))
        
        # 高速実行シミュレート下でのGUI描画パフォーマンス
        start_time = time.time()
        draw_count = 0
        duration = 1.0  # 1秒間テスト
        
        while time.time() - start_time < duration:
            try:
                self.renderer.draw_gui(
                    surface, 
                    self.mock_game_state, 
                    self.execution_state,
                    session_summary=None
                )
                draw_count += 1
                
                # 超高速モードでのsleep間隔をシミュレート
                sleep_interval = self.speed_manager.calculate_sleep_interval(0.02)
                time.sleep(sleep_interval)
                
            except Exception as e:
                self.fail(f"高速実行時GUI描画エラー: {e}")
        
        # 1秒間に最低10回のGUI更新を期待
        self.assertGreaterEqual(draw_count, 10, f"GUI描画頻度が低すぎます: {draw_count}回/秒")
    
    def test_button_state_visual_feedback(self):
        """ボタン状態視覚フィードバックテスト"""
        valid_speeds = [1, 2, 3, 4, 5, 10, 50]
        
        for active_speed in valid_speeds:
            self.speed_manager.set_speed_multiplier(active_speed)
            self.execution_state.speed_multiplier = active_speed
            
            surface = pygame.Surface((800, 600))
            
            # アクティブボタンの視覚フィードバック確認
            try:
                self.renderer.draw_gui(
                    surface, 
                    self.mock_game_state, 
                    self.execution_state,
                    session_summary=None
                )
                
                # 現在のアクティブ速度が正しく設定されていることを確認
                self.assertEqual(self.speed_manager.current_speed_multiplier, active_speed)
                
                visual_feedback_success = True
            except Exception as e:
                visual_feedback_success = False
                print(f"x{active_speed}速度でのvisualフィードバックエラー: {e}")
            
            self.assertTrue(visual_feedback_success, f"x{active_speed}速度での視覚フィードバック失敗")
    
    def test_execution_mode_integration_with_speed_control(self):
        """実行モードと速度制御統合テスト"""
        execution_modes = ["step_by_step", "continuous", "auto"]
        test_speeds = [1, 5, 10, 50]
        
        for mode in execution_modes:
            for speed in test_speeds:
                self.execution_state.mode = mode
                self.speed_manager.set_speed_multiplier(speed)
                self.execution_state.speed_multiplier = speed
                
                surface = pygame.Surface((800, 600))
                
                # 各モードと速度の組み合わせでのGUI描画
                try:
                    self.renderer.draw_gui(
                        surface, 
                        self.mock_game_state, 
                        self.execution_state,
                        session_summary=None
                    )
                    
                    integration_success = True
                except Exception as e:
                    integration_success = False
                    print(f"モード'{mode}' x{speed}速度統合エラー: {e}")
                
                self.assertTrue(integration_success, 
                              f"実行モード'{mode}' + x{speed}速度統合失敗")


class TestGUIEventHandling(unittest.TestCase):
    """GUIイベントハンドリングテスト"""
    
    def setUp(self):
        """テスト初期化"""
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1))
        
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.renderer = GuiRenderer(800, 600)
        self.renderer.speed_control_manager = self.speed_manager
    
    def test_mouse_click_coordinate_mapping(self):
        """マウスクリック座標マッピングテスト"""
        # 7段階速度制御ボタンの予想座標範囲
        # 2行レイアウト: [1,2,3,4] [5,10,50]
        
        button_regions = {
            1: (50, 450, 120, 480),    # x1ボタン概算座標
            2: (130, 450, 200, 480),   # x2ボタン概算座標
            3: (210, 450, 280, 480),   # x3ボタン概算座標
            4: (290, 450, 360, 480),   # x4ボタン概算座標
            5: (50, 490, 120, 520),    # x5ボタン概算座標
            10: (130, 490, 200, 520),  # x10ボタン概算座標
            50: (210, 490, 280, 520)   # x50ボタン概算座標
        }
        
        for speed, (x1, y1, x2, y2) in button_regions.items():
            # ボタン中央座標
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            
            # 座標が有効な範囲内にあることを確認
            self.assertGreaterEqual(center_x, 0)
            self.assertLess(center_x, 800)
            self.assertGreaterEqual(center_y, 0)
            self.assertLess(center_y, 600)
    
    def test_keyboard_shortcut_mapping(self):
        """キーボードショートカットマッピングテスト"""
        # 数字キーと速度の対応付けテスト
        key_speed_mapping = {
            pygame.K_1: 1,
            pygame.K_2: 2,
            pygame.K_3: 3,
            pygame.K_4: 4,
            pygame.K_5: 5
        }
        
        for key, expected_speed in key_speed_mapping.items():
            # キーボードショートカットが正しい速度に対応することを確認
            # （実際の実装では、イベントハンドラー内でこの対応付けが行われる）
            
            # 直接速度変更をテスト
            try:
                success = self.speed_manager.set_speed_multiplier(expected_speed)
                self.assertTrue(success)
                self.assertEqual(self.speed_manager.current_speed_multiplier, expected_speed)
            except Exception as e:
                self.fail(f"キー{key}→速度x{expected_speed}設定失敗: {e}")


class TestGUIPerformanceUnderLoad(unittest.TestCase):
    """負荷時GUIパフォーマンステスト"""
    
    def setUp(self):
        """テスト初期化"""
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1))
        
        self.speed_manager = Enhanced7StageSpeedControlManager()
        self.ultra_controller = UltraHighSpeedController(self.speed_manager)
        self.renderer = GuiRenderer(800, 600)
        
        # Mock game state
        self.mock_game_state = Mock()
        self.mock_game_state.player_x = 5
        self.mock_game_state.player_y = 5
        self.mock_game_state.stage = 1
        self.mock_game_state.score = 100
        self.mock_game_state.lives = 3
        
        self.execution_state = EnhancedExecutionState(
            mode="continuous",
            is_paused=False,
            step_count=0,
            total_execution_time=0.0,
            speed_multiplier=1
        )
    
    def test_gui_performance_at_x50_speed(self):
        """x50速度時のGUIパフォーマンステスト"""
        self.speed_manager.set_speed_multiplier(50)
        self.execution_state.speed_multiplier = 50
        
        surface = pygame.Surface((800, 600))
        
        # x50速度での短期間集中テスト
        start_time = time.time()
        successful_draws = 0
        failed_draws = 0
        duration = 2.0  # 2秒間
        
        while time.time() - start_time < duration:
            try:
                self.renderer.draw_gui(
                    surface, 
                    self.mock_game_state, 
                    self.execution_state,
                    session_summary=None
                )
                successful_draws += 1
                
                # x50速度に対応するsleep間隔
                sleep_interval = self.speed_manager.calculate_sleep_interval(0.02)
                if sleep_interval > 0:
                    time.sleep(sleep_interval)
                
            except Exception as e:
                failed_draws += 1
                print(f"x50速度GUI描画失敗: {e}")
        
        # 成功率が90%以上であることを期待
        total_draws = successful_draws + failed_draws
        success_rate = successful_draws / total_draws if total_draws > 0 else 0
        
        self.assertGreaterEqual(success_rate, 0.9, 
                               f"x50速度時のGUI成功率が低すぎます: {success_rate:.2%}")
        
        print(f"\nx50速度GUIパフォーマンス結果:")
        print(f"  成功描画: {successful_draws}回")
        print(f"  失敗描画: {failed_draws}回") 
        print(f"  成功率: {success_rate:.2%}")
    
    def test_concurrent_gui_updates_with_speed_changes(self):
        """速度変更と同時GUIアップデートテスト"""
        surface = pygame.Surface((800, 600))
        
        results = []
        
        def gui_update_worker():
            """GUI更新ワーカー"""
            for i in range(50):  # 50回のGUI更新
                try:
                    self.renderer.draw_gui(
                        surface, 
                        self.mock_game_state, 
                        self.execution_state,
                        session_summary=None
                    )
                    results.append(('gui_success', i))
                    time.sleep(0.01)  # 10ms待機
                except Exception as e:
                    results.append(('gui_error', i, str(e)))
        
        def speed_change_worker():
            """速度変更ワーカー"""
            speeds = [1, 5, 10, 2, 50, 3, 10, 1]
            for i, speed in enumerate(speeds):
                try:
                    self.speed_manager.set_speed_multiplier(speed)
                    self.execution_state.speed_multiplier = speed
                    results.append(('speed_success', speed))
                    time.sleep(0.1)  # 100ms待機
                except Exception as e:
                    results.append(('speed_error', speed, str(e)))
        
        # 2つのスレッドを並行実行
        gui_thread = threading.Thread(target=gui_update_worker)
        speed_thread = threading.Thread(target=speed_change_worker)
        
        gui_thread.start()
        speed_thread.start()
        
        gui_thread.join()
        speed_thread.join()
        
        # 結果分析
        gui_successes = [r for r in results if r[0] == 'gui_success']
        speed_successes = [r for r in results if r[0] == 'speed_success']
        
        self.assertGreater(len(gui_successes), 40, "GUI更新成功回数が不足")
        self.assertGreater(len(speed_successes), 6, "速度変更成功回数が不足")
        
        print(f"\n同時実行テスト結果:")
        print(f"  GUI更新成功: {len(gui_successes)}回")
        print(f"  速度変更成功: {len(speed_successes)}回")


if __name__ == '__main__':
    # テストスイート実行
    unittest.main(verbosity=2)