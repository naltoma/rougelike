#!/usr/bin/env python3
"""
main.pyのエラー修正テスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.session_log_manager import SessionLogManager

def test_main_fix():
    """main.pyの修正をテスト"""
    print("🧪 main.py修正テスト開始")
    
    try:
        # SessionLogManagerを初期化
        manager = SessionLogManager()
        
        # セッションログ有効化
        result = manager.enable_default_logging("TEST_FIX", "stage01")
        if not result.success:
            print(f"❌ ログ有効化失敗: {result.error_message}")
            return False
            
        print(f"✅ ログ有効化成功! ログファイル: {result.log_path}")
        
        # solve()関数のソースコード取得（main.pyと同じ処理）
        def _get_solve_function_code() -> str:
            """solve()関数のソースコードを取得"""
            try:
                import inspect
                sys.path.append('..')
                from main import solve
                source_code = inspect.getsource(solve)
                return source_code
            except Exception as e:
                return f"# ソースコード取得エラー: {e}"
        
        solve_code = _get_solve_function_code()
        
        # セッション情報を設定（修正後のAPI）
        if manager.session_logger:
            manager.session_logger.set_session_info(
                stage_id="stage01", 
                solve_code=solve_code
            )
            print("✅ set_session_info 成功（attempt_count除去済み）")
            
            # セッション開始イベント
            manager.session_logger.log_event("session_start", {
                "display_mode": "cui",
                "framework_version": "v1.2.2",
                "stage_id": "stage01",
                "student_id": "TEST_FIX"
            })
            print("✅ セッション開始ログ記録成功")
            
            # テスト用セッション完了
            manager.session_logger.log_event("session_complete", {
                "completed_successfully": False,
                "total_execution_time": "N/A",
                "action_count": 0
            })
            print("✅ セッション完了ログ記録成功")
            
        print("🎉 main.py修正テスト完了 - エラーなし!")
        return True
        
    except Exception as e:
        print(f"❌ エラー発生: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_main_fix()
    if success:
        print("\n✅ 修正成功: main.pyは正常に動作するはずです")
    else:
        print("\n❌ 修正失敗: 追加の修正が必要です")