#!/usr/bin/env python3
"""
改善されたロギングシステムのテスト
実際のmain.pyのsolve()関数の状態（南方向への移動がコメントアウト）をテスト
"""

from engine.session_log_manager import SessionLogManager
from engine.api import initialize_api, initialize_stage
from engine.api import turn_right, move, get_game_result
import engine.api as api
import time

def test_current_solve():
    """現在のsolve()の実装状況をテスト"""
    print("🧪 改善されたロギングシステム テスト開始")
    
    # APIとセッションログ初期化
    initialize_api("cui")  # CUIモードで初期化
    
    # _global_apiの確認
    print(f"🔍 api._global_api after init: {api._global_api}")
    
    manager = SessionLogManager()
    
    # セッションログ有効化
    result = manager.enable_default_logging("TEST002", "stage01")
    
    # APIレイヤーにセッションログマネージャーを設定
    if api._global_api:
        api._global_api.session_log_manager = manager
        print(f"✅ APIレイヤーにSessionLogManagerを設定しました")
        print(f"🔍 api._global_api.session_log_manager: {api._global_api.session_log_manager is not None}")
        print(f"🔍 manager.session_logger: {manager.session_logger is not None}")
    else:
        print("❌ api._global_apiがNoneです") 
    if not result.success:
        print(f"❌ ログ有効化失敗: {result.error_message}")
        return
        
    print(f"✅ ログ有効化成功! ログファイル: {result.log_path}")
    
    # ステージ初期化
    if not initialize_stage("stage01"):
        print("❌ ステージ初期化失敗")
        return
    
    print("✅ ステージ初期化完了")
    
    # ステージ初期化後に再度_global_apiを確認
    print(f"🔍 api._global_api after stage init: {api._global_api}")
    if api._global_api and not api._global_api.session_log_manager:
        api._global_api.session_log_manager = manager
        print("✅ ステージ初期化後にSessionLogManagerを設定しました")
    
    # solve()の実装（現在のmain.pyと同じ - 南方向コメントアウト状態）
    print("🎮 現在のsolve()実装を模擬実行...")
    
    # 1. 東を向く
    print("➡️ 東方向を向く...")
    turn_right()  
    time.sleep(0.1)
    
    # 2-5. 東に移動 (4回)
    for i in range(4):
        print(f"➡️ 東方向へ移動... ({i+1}/4)")
        move()
        time.sleep(0.1)
    
    # 注：南方向のコードはコメントアウトされているため実行されない
    print("⚠️ 南方向への移動はコメントアウトされているためスキップ")
    
    # ゲーム結果確認
    print("\n📊 ゲーム結果確認:")
    game_result = get_game_result()
    print(f"ゲーム結果: {game_result}")
    
    # アクション数確認
    if api._global_api and api._global_api.action_tracker:
        action_count = api._global_api.action_tracker.get_action_count()
        print(f"実行アクション数: {action_count}")
    else:
        print("⚠️ アクション追跡が利用できません")
    
    # セッション完了ログ記録（main.pyと同じロジック）
    if manager.session_logger:
        try:
            game_completed = "ゴール到達" in game_result or "ゲームクリア" in game_result
            actual_action_count = api._global_api.action_tracker.get_action_count() if api._global_api and api._global_api.action_tracker else 0
            
            execution_summary = {
                "completed_successfully": game_completed,
                "total_execution_time": "N/A",
                "action_count": actual_action_count
            }
            
            manager.session_logger.log_event("session_complete", execution_summary)
            print("✅ セッション完了ログ記録完了")
            
            print(f"📝 結果サマリー:")
            print(f"   ゲーム完了: {game_completed}")
            print(f"   アクション数: {actual_action_count}")
            
        except Exception as e:
            print(f"⚠️ セッション完了ログ記録エラー: {e}")
    
    print("🎉 テスト完了!")
    return result.log_path

if __name__ == "__main__":
    try:
        log_path = test_current_solve()
        if log_path:
            print(f"\n📂 生成されたログファイル: {log_path}")
            print("確認コマンド: python show_session_logs.py --latest")
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()