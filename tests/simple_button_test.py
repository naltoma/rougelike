#!/usr/bin/env python3
"""
シンプル版 ExecutionController テスト
"""

import time
import sys
import os
from datetime import datetime

# パス修正（tests/ディレクトリから親ディレクトリのengineにアクセス）
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_simple_execution_controller():
    """シンプル版ExecutionControllerのテスト"""
    print("🧪 シンプル版ExecutionController テスト開始")
    
    try:
        from engine.execution_controller import ExecutionController
        from engine import ExecutionMode
        
        # ExecutionControllerを初期化
        controller = ExecutionController()
        print(f"✅ 初期化成功: {controller.state.mode}")
        
        # 1. Step実行テスト
        print("\n🔍 Step実行テスト:")
        result = controller.step_execution()
        print(f"  結果: success={result.success}")
        print(f"  実行時間: {result.execution_time_ms:.2f}ms")
        print(f"  状態: {controller.state.mode}")
        
        # 2. Continuous実行テスト
        print("\n▶️ Continuous実行テスト:")
        controller.continuous_execution()
        print(f"  状態: {controller.state.mode}")
        
        # 短時間後に一時停止
        time.sleep(0.1)
        controller.pause_execution()
        print(f"  一時停止後の状態: {controller.state.mode}")
        
        # 3. Reset実行テスト
        print("\n🔄 Reset実行テスト:")
        reset_result = controller.full_system_reset()
        print(f"  結果: success={reset_result.success}")
        print(f"  リセット対象: {reset_result.components_reset}")
        print(f"  状態: {controller.state.mode}")
        
        print("\n🎉 全テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_simple_execution_controller()