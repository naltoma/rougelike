#!/usr/bin/env python3
"""
GUI Critical Fixes 自動テスト
Step/Pause/Resetボタンの機能を自動的にテスト
"""

import time
import threading
import sys
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock

# パス修正（tests/ディレクトリから親ディレクトリのengineにアクセス）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# テスト用のモック
class MockGameAPI:
    def __init__(self):
        self.move_calls = 0
        self.turn_calls = 0
        self.reset_calls = 0
        
    def move(self):
        self.move_calls += 1
        print(f"🔍 テスト: move() #{self.move_calls} 呼び出し")
        return True
        
    def turn_right(self):
        self.turn_calls += 1
        print(f"🔍 テスト: turn_right() #{self.turn_calls} 呼び出し")
        return True
        
    def reset_game(self):
        self.reset_calls += 1
        print(f"🔍 テスト: reset_game() #{self.reset_calls} 呼び出し")

class MockGameManager:
    def __init__(self):
        self.reset_calls = 0
        
    def reset_game(self):
        self.reset_calls += 1
        print(f"🔍 テスト: GameManager.reset_game() #{self.reset_calls} 呼び出し")

def test_step_button():
    """Stepボタンのテスト"""
    print("\n🧪 ===== STEP BUTTON TEST =====")
    
    try:
        from engine.execution_controller import ExecutionController
        from engine import ExecutionMode
        
        # モックAPIでExecutionControllerを初期化
        mock_api = MockGameAPI()
        controller = ExecutionController(mock_api)
        
        print(f"初期状態: {controller.state.mode}")
        
        # ステップ実行テスト
        print("🔍 ステップ実行テスト開始...")
        start_time = datetime.now()
        
        try:
            result = controller.step_execution()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            print(f"結果: success={result.success}")
            print(f"実行時間: {execution_time:.2f}ms")
            print(f"アクション実行数: {result.actions_executed}")
            print(f"新状態: {result.new_state}")
            
            if result.error_message:
                print(f"エラー: {result.error_message}")
                
            return result.success
            
        except Exception as e:
            print(f"❌ ステップ実行例外: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_pause_button():
    """Pauseボタンのテスト"""
    print("\n🧪 ===== PAUSE BUTTON TEST =====")
    
    try:
        from engine.execution_controller import ExecutionController
        from engine import ExecutionMode
        
        # モックAPIでExecutionControllerを初期化
        mock_api = MockGameAPI()
        controller = ExecutionController(mock_api)
        
        print(f"初期状態: {controller.state.mode}")
        
        # 連続実行モードに変更
        controller.continuous_execution()
        print(f"連続実行後の状態: {controller.state.mode}")
        
        # 短時間待機
        time.sleep(0.1)
        
        # 一時停止要求テスト
        print("🔍 一時停止要求テスト開始...")
        
        try:
            controller.pause_execution()
            print(f"一時停止要求後の状態: {controller.state.mode}")
            
            # PauseControllerの状態確認
            pause_status = controller.pause_controller.get_pause_status()
            print(f"一時停止ステータス: {pause_status}")
            
            return pause_status.get('is_pending', False)
            
        except Exception as e:
            print(f"❌ 一時停止例外: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_reset_button():
    """Resetボタンのテスト"""
    print("\n🧪 ===== RESET BUTTON TEST =====")
    
    try:
        from engine.execution_controller import ExecutionController
        from engine import ExecutionMode
        
        # モックAPIでExecutionControllerを初期化
        mock_api = MockGameAPI()
        controller = ExecutionController(mock_api)
        
        # モックGameManagerをセット
        mock_game_manager = MockGameManager()
        
        print(f"初期状態: {controller.state.mode}")
        
        # いくつかの操作を実行
        controller.state.step_count = 5
        print(f"ステップカウント設定: {controller.state.step_count}")
        
        # リセット実行テスト
        print("🔍 リセット実行テスト開始...")
        start_time = datetime.now()
        
        try:
            # グローバルAPIにモックを設定
            import engine.api
            
            # _global_apiが None の場合は初期化
            if engine.api._global_api is None:
                from engine.api import GameAPI
                engine.api._global_api = GameAPI()
            
            engine.api._global_api.game_manager = mock_game_manager
            
            result = controller.full_system_reset()
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            print(f"結果: success={result.success}")
            print(f"実行時間: {execution_time:.2f}ms")
            print(f"リセット対象: {result.components_reset}")
            print(f"エラー: {result.errors}")
            
            # ExecutionControllerの状態確認
            print(f"リセット後の状態: {controller.state.mode}")
            print(f"リセット後のステップカウント: {controller.state.step_count}")
            
            # GameManagerが呼ばれたか確認
            print(f"GameManager.reset_game() 呼び出し数: {mock_game_manager.reset_calls}")
            
            return result.success and mock_game_manager.reset_calls > 0
            
        except Exception as e:
            print(f"❌ リセット例外: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        return False

def test_step_execution_flow():
    """Step実行の詳細フローテスト"""
    print("\n🧪 ===== STEP EXECUTION FLOW TEST =====")
    
    try:
        from engine.execution_controller import ExecutionController
        from engine import ExecutionMode
        
        mock_api = MockGameAPI()
        controller = ExecutionController(mock_api)
        
        print("🔍 Step実行フロー詳細テスト...")
        
        # 初期フラグ状態確認
        print(f"pending_action初期値: {controller.pending_action}")
        print(f"action_completed初期値: {controller.action_completed}")
        print(f"step_event初期状態: {controller.step_event.is_set()}")
        
        # ステップ実行
        result = controller.step_execution()
        
        # 実行後のフラグ状態確認
        print(f"実行後pending_action: {controller.pending_action}")
        print(f"実行後action_completed: {controller.action_completed}")
        print(f"実行後step_event: {controller.step_event.is_set()}")
        
        # wait_for_actionのテスト（短時間だけ）
        print("🔍 wait_for_action()の動作テスト...")
        controller.state.mode = ExecutionMode.STEPPING
        controller.pending_action = True
        
        print("wait_for_action()呼び出し前のフラグ状態:")
        print(f"  pending_action: {controller.pending_action}")
        print(f"  current_action: {controller.state.current_action}")
        
        # wait_for_actionを呼ぶ（ただし短時間で中断）
        start_time = datetime.now()
        try:
            controller.wait_for_action()
        except Exception as e:
            print(f"wait_for_action()例外: {e}")
        
        print("wait_for_action()呼び出し後のフラグ状態:")
        print(f"  pending_action: {controller.pending_action}")
        print(f"  current_action: {controller.state.current_action}")
        print(f"  state.mode: {controller.state.mode}")
        
        return True
        
    except Exception as e:
        print(f"❌ Step実行フローテスト例外: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メインテスト実行"""
    print("🚀 GUI Critical Fixes 自動テスト開始")
    print("=" * 50)
    
    results = {}
    
    # 各テストを実行
    results['step'] = test_step_button()
    results['step_flow'] = test_step_execution_flow()
    results['pause'] = test_pause_button()
    results['reset'] = test_reset_button()
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("🎯 テスト結果サマリー")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name.upper():15} : {status}")
    
    # 総合結果
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("\n" + "-" * 30)
    print(f"総合結果: {passed_tests}/{total_tests} テスト通過")
    
    if passed_tests == total_tests:
        print("🎉 全テスト通過！")
        return 0
    else:
        print("⚠️ 一部テストが失敗しました")
        return 1

if __name__ == "__main__":
    exit(main())