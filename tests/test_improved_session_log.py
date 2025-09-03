#!/usr/bin/env python3
"""
改善されたセッションログシステムのテスト
action_count統一、attempt_count除去、ステージ別ディレクトリ構造のテスト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from engine.session_log_manager import SessionLogManager
from engine.api import initialize_api, initialize_stage
from engine.api import turn_right, move, get_game_result
import engine.api as api
import time

def test_improved_session_logging():
    """改善されたセッションログシステムをテスト"""
    print("🧪 改善されたセッションログシステム テスト開始")
    
    # APIとセッションログ初期化
    initialize_api("cui")
    manager = SessionLogManager()
    
    # セッションログ有効化
    result = manager.enable_default_logging("TEST003", "stage01") 
    if not result.success:
        print(f"❌ ログ有効化失敗: {result.error_message}")
        return
        
    print(f"✅ ログ有効化成功! ログファイル: {result.log_path}")
    print(f"🆔 セッションID: {result.session_id}")
    
    # ステージ初期化
    if not initialize_stage("stage01"):
        print("❌ ステージ初期化失敗")
        return
    
    print("✅ ステージ初期化完了")
    
    # APIレイヤーにSessionLogManagerを設定
    if api._global_api:
        api._global_api.session_log_manager = manager
        print("✅ APIレイヤーにSessionLogManagerを設定しました")
    
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
            actual_action_count = api._global_api.action_tracker.get_action_count() if api._global_api and api._global_api.action_tracker else 5
            
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
    
    # 挑戦回数テスト
    print("\n📊 挑戦回数確認:")
    attempt_count = manager.get_attempt_count_for_stage("TEST003", "stage01")
    print(f"TEST003のstage01挑戦回数: {attempt_count}")
    
    return result.log_path

def test_multiple_attempts():
    """複数回実行テスト（挑戦回数確認）"""
    print("\n🔄 複数回実行テスト開始")
    
    for i in range(3):
        print(f"\n--- {i+1}回目の実行 ---")
        try:
            log_path = test_improved_session_logging()
            if log_path:
                print(f"📂 生成されたログファイル: {log_path}")
        except Exception as e:
            print(f"❌ {i+1}回目のテスト中にエラー: {e}")
    
    # 最終的な挑戦回数確認
    manager = SessionLogManager()
    final_attempt_count = manager.get_attempt_count_for_stage("TEST003", "stage01")
    print(f"\n🎯 最終挑戦回数: {final_attempt_count}")

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--multiple":
            test_multiple_attempts()
        else:
            log_path = test_improved_session_logging()
            if log_path:
                print(f"\n📂 生成されたログファイル: {log_path}")
                print("確認コマンド: python show_session_logs.py --latest")
                print("複数回テスト: python test_improved_session_log.py --multiple")
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()