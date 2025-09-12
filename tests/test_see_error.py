#!/usr/bin/env python3
"""
see()実行エラー再現テスト
"""

import time
import sys
import os

# パスの調整
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_see_error():
    """see()エラーを再現"""
    try:
        # 直接API初期化でGUIなしでテスト
        from engine.api import initialize_api, initialize_stage, see
        
        print("API初期化...")
        initialize_api()
        
        print("ステージを初期化...")
        initialize_stage("stage09")
        
        print("see()を実行してエラーを再現...")
        result = see()
        print(f"see()結果: {result}")
        
    except Exception as e:
        print(f"エラー発生: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_see_error()