#!/usr/bin/env python3
"""
セッションログシステムテスト
Session Logging System Tests
"""

import sys
sys.path.append('..')

import time
import json
from datetime import datetime, timedelta
from pathlib import Path


def test_session_logger_basic():
    """セッションロガーの基本機能テスト"""
    print("🧪 セッションロガー基本テスト")
    print("=" * 50)
    
    try:
        from engine.session_logging import (
            SessionLogger, EventType, LogLevel, LogEntry, SessionSummary
        )
        
        # テスト用ディレクトリ
        test_dir = "test_data/sessions"
        logger = SessionLogger(test_dir, max_log_files=10)
        
        # セッション開始
        print("📝 セッション開始...")
        session_id = logger.start_session("test_student_001")
        print(f"  セッションID: {session_id}")
        
        # ステージ開始
        print("\n🎯 ステージ開始ログ...")
        logger.log_stage_start("stage01")
        
        # アクション記録
        print("\n🎮 アクション記録...")
        logger.log_action("move", True, "東に移動成功", turn_number=1)
        logger.log_action("turn_right", True, "右回転成功", turn_number=2)
        logger.log_action("move", False, "壁にぶつかりました", turn_number=3)
        
        # エラー記録
        print("\n❌ エラー記録...")
        try:
            raise ValueError("テスト用エラー")
        except ValueError as e:
            logger.log_error(e, "テストコンテキスト")
        
        # ヒント使用
        print("\n💡 ヒント使用記録...")
        logger.log_hint_used("右手法を試してみましょう")
        
        # ユーザー入力
        print("\n⌨️ ユーザー入力記録...")
        logger.log_user_input("m", "move command")
        
        # システムメッセージ
        print("\n📢 システムメッセージ記録...")
        logger.log_system_message("ゲーム設定完了", {"difficulty": "easy"})
        
        # パフォーマンスメトリック
        print("\n📊 パフォーマンスメトリック記録...")
        logger.log_performance_metric("response_time", 0.25, "seconds", "API call")
        
        # デバッグ情報
        print("\n🔧 デバッグ情報記録...")
        logger.log_debug("状態デバッグ", {"player_pos": (2, 3), "turn": 5})
        
        # ステージ終了
        print("\n🏁 ステージ終了ログ...")
        logger.log_stage_end("stage01", True)  # 成功
        
        # 少し待ってからセッション終了
        time.sleep(1)
        
        # セッション終了
        print("\n📝 セッション終了...")
        summary = logger.end_session()
        
        if summary:
            print(f"  セッション時間: {summary.duration}")
            print(f"  総アクション数: {summary.total_actions}")
            print(f"  エラー数: {summary.total_errors}")
            print(f"  成功率: {summary.success_rate:.1%}")
        
        print("✅ セッションロガー基本テスト完了")
        
        # テストファイル確認
        test_files = list(Path(test_dir).glob("*"))
        print(f"📁 生成ファイル数: {len(test_files)}")
        
        # テストデータクリーンアップ
        import shutil
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
            print("🧹 テストデータをクリーンアップしました")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_log_entry_serialization():
    """ログエントリーのシリアライゼーションテスト"""
    print("\n🧪 ログエントリーシリアライゼーションテスト")
    print("=" * 50)
    
    try:
        from engine.session_logging import LogEntry, EventType, LogLevel
        
        # ログエントリー作成
        entry = LogEntry(
            timestamp=datetime.now(),
            session_id="test_session",
            student_id="test_student",
            event_type=EventType.ACTION_EXECUTED,
            level=LogLevel.INFO,
            message="テストメッセージ",
            stage_id="stage01",
            turn_number=5,
            data={"test_key": "test_value"}
        )
        
        # 辞書に変換
        entry_dict = entry.to_dict()
        print("✅ 辞書変換成功")
        
        # 辞書から復元
        restored_entry = LogEntry.from_dict(entry_dict)
        print("✅ 辞書復元成功")
        
        # データ検証
        assert restored_entry.session_id == entry.session_id
        assert restored_entry.event_type == entry.event_type
        assert restored_entry.message == entry.message
        print("✅ データ整合性確認")
        
        # JSON シリアライゼーション
        json_str = json.dumps(entry_dict, ensure_ascii=False)
        loaded_dict = json.loads(json_str)
        final_entry = LogEntry.from_dict(loaded_dict)
        
        assert final_entry.message == entry.message
        print("✅ JSON シリアライゼーション成功")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_data_persistence():
    """セッションデータ永続化テスト"""
    print("\n🧪 セッションデータ永続化テスト")
    print("=" * 50)
    
    try:
        from engine.session_logging import SessionLogger
        
        test_dir = "test_data/persistence"
        
        # ファーストセッション
        logger1 = SessionLogger(test_dir)
        session_id = logger1.start_session("persistence_test")
        
        # いくつかのデータを記録
        logger1.log_stage_start("stage01")
        logger1.log_action("move", True, "移動成功")
        logger1.log_stage_end("stage01", True)
        
        summary1 = logger1.end_session()
        print(f"✅ セッション1終了: {session_id}")
        
        # 新しいロガーインスタンスでデータ読み込み
        logger2 = SessionLogger(test_dir)
        
        # セッションリスト確認
        sessions = logger2.list_sessions("persistence_test")
        assert session_id in sessions
        print("✅ セッションリスト取得成功")
        
        # セッションサマリー読み込み
        summary2 = logger2.get_session_summary(session_id)
        assert summary2 is not None
        assert summary2.student_id == "persistence_test"
        print("✅ セッションサマリー読み込み成功")
        
        # ログ読み込み
        logs = logger2.get_session_logs(session_id)
        assert len(logs) > 0
        print(f"✅ ログ読み込み成功: {len(logs)}エントリー")
        
        # エクスポートテスト
        export_file = f"{test_dir}/export_test.json"
        success = logger2.export_session_data(session_id, export_file)
        assert success
        print("✅ セッションデータエクスポート成功")
        
        # エクスポートファイル確認
        with open(export_file, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        assert "summary" in export_data
        assert "logs" in export_data
        print("✅ エクスポートデータ構造確認")
        
        # テストデータクリーンアップ
        import shutil
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
            print("🧹 テストデータをクリーンアップしました")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_integration():
    """API統合テスト"""
    print("\n🧪 API統合テスト")
    print("=" * 50)
    
    try:
        from engine.api import (
            initialize_api, set_student_id, initialize_stage, 
            turn_right, move, end_session, get_session_summary,
            list_session_history, log_user_input
        )
        
        # API初期化（セッションログ有効）
        print("📺 API初期化...")
        initialize_api("cui", enable_progression=True, 
                      enable_session_logging=True, student_id="api_test_001")
        
        # ユーザー入力記録
        print("\n⌨️ ユーザー入力記録...")
        log_user_input("python main.py", "startup command")
        
        # ステージプレイ
        print("\n🎮 ステージプレイ...")
        if initialize_stage("stage01"):
            turn_right()
            move()
            move()
        
        # セッションサマリー取得
        print("\n📊 セッションサマリー取得...")
        summary = get_session_summary()
        if summary:
            print(f"  総アクション数: {summary.get('total_actions', 0)}")
            print(f"  挑戦ステージ数: {len(summary.get('stages_attempted', []))}")
        
        # セッション履歴
        print("\n📜 セッション履歴...")
        history = list_session_history()
        print(f"  セッション数: {len(history)}")
        
        # セッション終了
        print("\n📝 セッション終了...")
        end_session()
        
        print("✅ API統合テスト完了")
        
        # テストデータクリーンアップ
        test_files = Path("data/sessions").glob("*api_test_001*")
        for file in test_files:
            try:
                file.unlink()
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance_and_scalability():
    """パフォーマンスとスケーラビリティテスト"""
    print("\n🧪 パフォーマンス・スケーラビリティテスト")
    print("=" * 50)
    
    try:
        from engine.session_logging import SessionLogger
        import time
        
        test_dir = "test_data/performance"
        logger = SessionLogger(test_dir, max_log_files=50)
        
        # 大量ログテスト
        print("📝 大量ログ記録テスト...")
        session_id = logger.start_session("perf_test")
        
        start_time = time.time()
        
        # 1000エントリーの記録
        for i in range(1000):
            logger.log_action(f"action_{i}", True, f"アクション{i}実行", i)
            
            if i % 100 == 0:
                print(f"  進捗: {i}/1000")
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"✅ 1000エントリー記録完了: {duration:.2f}秒")
        print(f"   平均: {duration/1000*1000:.2f}ms/エントリー")
        
        # メモリ使用量チェック（バッファサイズ）
        buffer_size = len(logger.log_buffer)
        print(f"📊 バッファサイズ: {buffer_size}エントリー")
        
        # セッション終了
        summary = logger.end_session()
        print(f"✅ セッション終了: 総アクション{summary.total_actions}件")
        
        # ログファイル確認
        log_files = list(Path(test_dir).glob("session_*.jsonl"))
        print(f"📁 ログファイル数: {len(log_files)}")
        
        if log_files:
            log_file_size = log_files[0].stat().st_size
            print(f"📏 ログファイルサイズ: {log_file_size/1024:.1f}KB")
        
        # テストデータクリーンアップ
        import shutil
        if Path(test_dir).exists():
            shutil.rmtree(test_dir)
            print("🧹 テストデータをクリーンアップしました")
        
        return True
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メインテスト実行"""
    print("🧪 セッションログシステム統合テスト開始")
    print("=" * 60)
    
    tests = [
        test_log_entry_serialization,
        test_session_logger_basic,
        test_session_data_persistence,
        test_api_integration,
        test_performance_and_scalability
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("🏁 テスト結果")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"成功: {passed}/{total}")
    
    if passed == total:
        print("🎉 全てのセッションログテストが成功しました！")
        print("✅ セッションログシステムが正常に実装されています")
    else:
        print(f"⚠️ {total - passed} 個のテストが失敗しました")


if __name__ == "__main__":
    main()