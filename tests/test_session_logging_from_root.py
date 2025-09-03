#!/usr/bin/env python3
"""
セッションログ機能のテスト・デモ用スクリプト

使用方法:
  python test_session_logging.py

このスクリプトでセッションログの生成・確認方法を学べます。
"""

import sys
from pathlib import Path
from engine.session_log_manager import SessionLogManager, LogConfig

def test_session_logging():
    """セッションログ機能のテスト"""
    print("🧪 セッションログ機能テスト")
    print("=" * 50)
    
    # SessionLogManagerの初期化
    manager = SessionLogManager()
    
    # 1. システム診断
    print("\n📋 1. システム診断")
    print("-" * 30)
    report = manager.diagnose_logging_system()
    print(report.format_report())
    
    # 2. デフォルトログの有効化
    print("\n📝 2. デフォルトログ有効化")
    print("-" * 30)
    result = manager.enable_default_logging("TEST001", "stage01")
    if result.success:
        print(f"✅ ログ有効化成功!")
        print(f"📂 ログファイル: {result.log_path}")
        print(f"🆔 セッションID: {result.session_id}")
    else:
        print(f"❌ ログ有効化失敗: {result.error_message}")
        return
    
    # 3. いくつかのイベントをログに記録
    print("\n📊 3. イベントログ記録")
    print("-" * 30)
    if manager.session_logger:
        events = [
            ("test_start", {"message": "テスト開始"}),
            ("player_move", {"direction": "east", "position": {"x": 1, "y": 0}}),
            ("player_move", {"direction": "south", "position": {"x": 1, "y": 1}}),
            ("item_collect", {"item": "key", "score": 10}),
            ("test_complete", {"message": "テスト完了", "total_score": 10})
        ]
        
        for event_type, event_data in events:
            try:
                manager.session_logger.log_event(event_type, event_data)
                print(f"📝 ログ記録: {event_type}")
            except Exception as e:
                print(f"⚠️ ログ記録エラー: {e}")
    
    # 4. ログ情報の表示
    print("\n📊 4. ログ情報表示")
    print("-" * 30)
    manager.show_log_info()
    
    # 5. ログの整合性チェック
    print("\n🔍 5. ログ整合性チェック")
    print("-" * 30)
    validation_result = manager.validate_log_integrity()
    manager.show_validation_report(validation_result)
    
    # 6. 設定情報の表示
    print("\n⚙️ 6. 現在の設定")
    print("-" * 30)
    manager.show_current_config()
    
    # 7. 最新ログファイルパスの取得
    print("\n📁 7. 最新ログファイルパス取得")
    print("-" * 30)
    latest_log = manager.get_latest_log_path()
    if latest_log:
        print(f"📂 最新ログ: {latest_log}")
        print(f"📏 ファイルサイズ: {latest_log.stat().st_size} bytes")
    else:
        print("📂 ログファイルが見つかりませんでした")
    
    print("\n" + "=" * 50)
    print("✅ セッションログ機能テスト完了!")
    print()
    print("📖 使用方法まとめ:")
    print("  1. SessionLogManager() でマネージャーを初期化")
    print("  2. enable_default_logging(student_id, stage_id) でログ有効化")
    print("  3. session_logger.log_event(type, data) でイベント記録")
    print("  4. show_log_info() でログファイル一覧表示")
    print("  5. validate_log_integrity() で整合性チェック")
    print("  6. get_latest_log_path() で最新ログパス取得")
    print()

def demonstrate_log_config():
    """ログ設定のデモ"""
    print("\n⚙️ ログ設定デモ")
    print("=" * 50)
    
    manager = SessionLogManager()
    
    # カスタム設定の適用
    custom_config = LogConfig(
        logging_level='DEBUG',
        max_file_size_mb=5,
        max_log_files=50,
        google_sheets_enabled=False,
        backup_enabled=True,
        auto_cleanup_enabled=True
    )
    
    print("📝 カスタム設定を適用中...")
    success = manager.configure_logging(custom_config)
    if success:
        print("✅ 設定適用成功!")
    else:
        print("❌ 設定適用失敗")
    
    manager.show_current_config()
    
    print("\n🔄 デフォルト設定にリセット中...")
    manager.reset_to_default_config()
    

if __name__ == "__main__":
    print("🎮 セッションログ機能デモ・テスト")
    print("=" * 60)
    
    try:
        test_session_logging()
        demonstrate_log_config()
        
        print("\n🎉 全テスト完了!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()