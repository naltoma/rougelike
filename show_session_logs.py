#!/usr/bin/env python3
"""
セッションログ確認スクリプト

使用方法:
  python show_session_logs.py         # 全ログ表示
  python show_session_logs.py --latest # 最新ログのみ表示
  python show_session_logs.py --validate # ログ整合性チェック
"""

import argparse
import sys
from engine.session_log_manager import SessionLogManager

def main():
    parser = argparse.ArgumentParser(description="セッションログ確認ツール")
    parser.add_argument("--latest", action="store_true", help="最新ログのみ表示")
    parser.add_argument("--validate", action="store_true", help="ログ整合性チェック")
    parser.add_argument("--config", action="store_true", help="現在の設定表示")
    parser.add_argument("--diagnose", action="store_true", help="システム診断")
    
    args = parser.parse_args()
    
    manager = SessionLogManager()
    
    try:
        if args.latest:
            print("📂 最新ログファイル情報")
            print("=" * 40)
            latest_path = manager.get_latest_log_path()
            if latest_path:
                print(f"ファイル: {latest_path}")
                print(f"内容:")
                
                if latest_path.suffix == '.json':
                    # JSON形式：整理された表示
                    import json
                    with open(latest_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print(f"🆔 セッションID: {data.get('session_id', 'N/A')}")
                    print(f"👤 学生ID: {data.get('student_id', 'N/A')}")
                    print(f"🎯 ステージID: {data.get('stage_id', 'N/A')}")
                    
                    # action_countはresultセクションから取得
                    action_count = 'N/A'
                    if 'result' in data and 'action_count' in data['result']:
                        action_count = data['result']['action_count']
                    elif 'action_count' in data:  # 旧形式との互換性
                        action_count = data['action_count']
                    print(f"⚡ アクション数: {action_count}")
                    
                    # completed_successfullyもresultセクションから取得
                    completed = 'N/A'
                    if 'result' in data and 'completed_successfully' in data['result']:
                        completed = data['result']['completed_successfully']
                    print(f"✅ 完了状況: {completed}")
                    
                    # コード品質情報を表示
                    if 'result' in data and 'code_quality' in data['result']:
                        quality = data['result']['code_quality']
                        print(f"📊 コード品質: {quality.get('line_count', 0)}行 (コード:{quality.get('code_lines', 0)}, コメント:{quality.get('comment_lines', 0)}, 空行:{quality.get('blank_lines', 0)})")
                    print(f"⏰ 開始時刻: {data.get('start_time', 'N/A')}")
                    print(f"⏰ 終了時刻: {data.get('end_time', 'N/A')}")
                    
                    if 'solve_code' in data and data['solve_code']:
                        print(f"\n📝 solve()コード:")
                        print("-" * 30)
                        print(data['solve_code'])
                        print("-" * 30)
                    
                    print(f"\n📊 イベント履歴 ({len(data.get('events', []))}件):")
                    for i, event in enumerate(data.get('events', []), 1):
                        print(f"  {i}. [{event.get('event_type', 'unknown')}] {event.get('timestamp', 'N/A')}")
                        if event.get('type'):  # アクション詳細
                            print(f"     └ {event['type']} (ステップ{event.get('step', 'N/A')})")
                else:
                    # JSONL形式：そのまま表示
                    with open(latest_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(content)
            else:
                print("❌ ログファイルが見つかりません")
                
        elif args.validate:
            print("🔍 ログ整合性チェック")
            print("=" * 40)
            result = manager.validate_log_integrity()
            manager.show_validation_report(result)
            
        elif args.config:
            print("⚙️ 現在の設定")
            print("=" * 40)
            manager.show_current_config()
            
        elif args.diagnose:
            print("🏥 システム診断")
            print("=" * 40)
            report = manager.diagnose_logging_system()
            print(report.format_report())
            
        else:
            print("📊 全ログファイル情報")
            print("=" * 40)
            manager.show_log_info()
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()