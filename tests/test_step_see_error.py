#!/usr/bin/env python3
"""
Step実行中のsee()エラー再現テスト
"""

import threading
import time
from typing import Optional

def test_step_see_error():
    """Step実行中のsee()エラーを再現"""
    from engine.api import initialize_api, initialize_stage, see, _global_api
    
    try:
        print("GUI APIを初期化...")
        initialize_api()  # GUIモード
        
        print("ステージを初期化...")
        initialize_stage("stage09")
        
        # step実行コンテキストを模倣
        print("Step実行コンテキストでsee()を実行...")
        
        # execution_controllerがあるかチェック
        if hasattr(_global_api, 'execution_controller') and _global_api.execution_controller:
            print("ExecutionControllerが利用可能")
            # step実行を模倣
            _global_api.execution_controller.set_mode("stepping")
            
        # see()を呼び出してエラーを発生
        result = see()
        print(f"see()結果: {result}")
        
    except Exception as e:
        print(f"エラー発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_step_see_error()