#!/usr/bin/env python3
"""
Webhook版セッションログアップロードツール
Webhook Session Log Upload Tool for Google Apps Script Integration

学生がセッションログをGoogle Apps Script webhookにアップロードするためのツールです。

使用方法:
    python upload_webhook.py stage01                    # stage01のログをアップロード
    python upload_webhook.py stage02 --student 123456A # 特定の学生IDでアップロード
    python upload_webhook.py --all                     # すべてのログをアップロード
    python upload_webhook.py --status                  # 設定状態確認
    python upload_webhook.py --test                    # 接続テスト
    python upload_webhook.py --setup                   # 初期設定
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, List
import time

# エンジンモジュールインポート
from engine.webhook_uploader import WebhookUploader, WebhookConfigManager, WebhookUploadError
from engine.session_log_loader import SessionLogLoader, SessionLogLoadError


class WebhookUploadToolError(Exception):
    """Webhookアップロードツール関連エラー"""
    pass


class WebhookUploadTool:
    """Webhookセッションログアップロードツール"""
    
    def __init__(self, verbose: bool = False):
        """
        ツール初期化
        
        Args:
            verbose: 詳細ログ出力
        """
        # ログ設定
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
        # コンポーネント初期化
        try:
            self.config_manager = WebhookConfigManager()
            self.log_loader = SessionLogLoader()
            self.uploader = WebhookUploader(self.config_manager)
            
        except Exception as e:
            print(f"❌ 初期化エラー: {e}")
            sys.exit(1)
    
    def print_banner(self):
        """バナー表示"""
        print("=" * 60)
        print("🚀 ローグライク演習 Webhookログアップロードツール v1.2.3")
        print("   （Google Apps Script版 - 完全無料）")
        print("=" * 60)
    
    def print_status(self) -> bool:
        """設定状態表示"""
        print("\n📊 現在の設定状態:")
        
        # Webhook設定確認
        webhook_url = self.config_manager.get_webhook_url()
        student_id = self.config_manager.get_student_id()
        
        print(f"🔗 Webhook URL: {'✅ 設定済み' if webhook_url else '❌ 未設定'}")
        if webhook_url:
            # URLの一部を表示（セキュリティのため）
            masked_url = webhook_url[:50] + "..." if len(webhook_url) > 50 else webhook_url
            print(f"   URL: {masked_url}")
        
        print(f"👤 学生ID: {'✅ 設定済み' if student_id else '❌ 未設定'}")
        if student_id:
            print(f"   ID: {student_id}")
        
        # セッションログファイル確認
        available_students = self.log_loader.get_available_students()
        available_stages = self.log_loader.get_available_stages()
        
        print(f"📝 セッションログ:")
        print(f"   利用可能学生: {len(available_students)} 名")
        print(f"   利用可能ステージ: {len(available_stages)} 個")
        
        if available_students:
            print(f"   学生ID: {', '.join(available_students[:5])}")  # 最初の5つまで表示
        
        if available_stages:
            print(f"   ステージ: {', '.join(sorted(available_stages))}")
        
        # アップロード統計
        stats = self.uploader.get_statistics()
        if stats['total_uploads'] > 0:
            print(f"📈 アップロード統計:")
            print(f"   総アップロード: {stats['total_uploads']} 件")
            print(f"   成功: {stats['successful_uploads']} 件")
            print(f"   失敗: {stats['failed_uploads']} 件")
        
        # 全体の準備状況
        ready = (webhook_url is not None and 
                student_id is not None and
                len(available_students) > 0)
        
        print(f"\n🎯 アップロード準備: {'✅ 完了' if ready else '❌ 未完了'}")
        
        return ready
    
    def setup_configuration(self):
        """設定セットアップ"""
        print("\n🔧 Webhookアップロード設定を開始します...\n")
        
        # 現在の設定確認
        current_webhook = self.config_manager.get_webhook_url()
        current_student = self.config_manager.get_student_id()
        
        print("📋 必要な情報:")
        print("1. 教員から提供されたWebhook URL")
        print("2. あなたの学生ID（6桁数字+1英字、例: 123456A）")
        
        # Webhook URL設定
        if current_webhook:
            print(f"\n現在のWebhook URL: {current_webhook[:50]}...")
            change_url = input("新しいURLに変更しますか？ [y/N]: ").strip().lower()
            if change_url == 'y':
                current_webhook = None
        
        if not current_webhook:
            while True:
                webhook_url = input("\n🔗 Webhook URLを入力してください: ").strip()
                
                if not webhook_url:
                    print("❌ URLが入力されませんでした")
                    continue
                
                try:
                    self.config_manager.set_webhook_url(webhook_url)
                    print("✅ Webhook URLを設定しました")
                    break
                except WebhookUploadError as e:
                    print(f"❌ {e}")
                    print("💡 正しいURL例: https://script.google.com/macros/s/YOUR_ID/exec")
        
        # 学生ID設定
        if current_student:
            print(f"\n現在の学生ID: {current_student}")
            change_student = input("学生IDを変更しますか？ [y/N]: ").strip().lower()
            if change_student == 'y':
                current_student = None
        
        if not current_student:
            while True:
                student_id = input("\n👤 学生IDを入力してください (例: 123456A): ").strip().upper()
                
                if not student_id:
                    print("❌ 学生IDが入力されませんでした")
                    continue
                
                try:
                    self.config_manager.set_student_id(student_id)
                    print("✅ 学生IDを設定しました")
                    break
                except WebhookUploadError as e:
                    print(f"❌ {e}")
        
        print("\n🎉 設定が完了しました！")
        print("💡 次は --test で接続テストを実行してください")
        return True
    
    def test_connection(self) -> bool:
        """接続テスト"""
        print("\n🔍 Webhook接続テストを実行中...")
        
        if not self.config_manager.is_configured():
            print("❌ 設定が完了していません。--setup で設定を行ってください。")
            return False
        
        try:
            success, message = self.uploader.test_webhook_connection()
            
            if success:
                print(f"✅ {message}")
                print("🎯 テストデータがスプレッドシートに記録されました")
                
                # 統計表示
                stats = self.uploader.get_statistics()
                print(f"📊 テスト後統計: 成功={stats['successful_uploads']} 失敗={stats['failed_uploads']}")
                
                return True
            else:
                print(f"❌ 接続テスト失敗: {message}")
                print("💡 トラブルシューティング:")
                print("   - Webhook URLが正しいか確認してください")
                print("   - Google Apps Scriptが正しくデプロイされているか確認してください")
                print("   - インターネット接続を確認してください")
                return False
                
        except Exception as e:
            print(f"❌ 接続テスト中にエラー: {e}")
            return False
    
    def upload_logs(self, stage: Optional[str] = None, 
                   student_id: Optional[str] = None,
                   upload_all: bool = False,
                   dry_run: bool = False) -> bool:
        """
        ログアップロード実行
        
        Args:
            stage: 対象ステージ
            student_id: 対象学生ID
            upload_all: 全ログアップロード
            dry_run: ドライラン（実際のアップロードなし）
        """
        try:
            print(f"\n📤 ログアップロード{'（ドライラン）' if dry_run else ''}を開始...")
            
            # 設定確認
            if not self.config_manager.is_configured():
                print("❌ 設定が完了していません。--setup で設定を行ってください。")
                return False
            
            # ログファイル検索
            print("🔍 ログファイルを検索中...")
            log_files = self.log_loader.find_session_log_files(
                student_id=student_id if not upload_all else None,
                stage=stage if not upload_all else None
            )
            
            if not log_files:
                print("❌ アップロード対象のログファイルが見つかりません。")
                return False
            
            print(f"📄 {len(log_files)} 個のログファイルを発見")
            for log_file in log_files[:5]:  # 最初の5つまで表示
                print(f"   - {log_file}")
            if len(log_files) > 5:
                print(f"   ... 他 {len(log_files) - 5} 個")
            
            # ログ読み込み
            print("\n📖 ログファイルを読み込み中...")
            load_result = self.log_loader.load_session_logs(log_files)
            
            if not load_result.success:
                print(f"❌ ログ読み込みエラー: {load_result.error_message}")
                return False
            
            if load_result.warnings:
                print("⚠️ 読み込み警告:")
                for warning in load_result.warnings[:3]:  # 最初の3つまで表示
                    print(f"   - {warning}")
            
            entries = load_result.entries
            print(f"📊 {len(entries)} 件のログエントリを読み込みました")
            
            if not entries:
                print("❌ 有効なログエントリがありません。")
                return False
            
            # 複数セッション警告表示
            if len(entries) > 1:
                print(f"⚠️ {len(entries)} 件のセッションが見つかりました。")
                print("   同じ学生・ステージの組み合わせでは1つのセッションのみアップロードできます。")
            else:
                print("✅ 単一セッションが見つかりました。")
            
            # 詳細サマリー表示（v1.2.2形式）
            print("\n📋 セッションログ詳細:")
            print("=" * 90)
            print("インデックス | 終了日時         | アクション数 | コード行数 | 完了フラグ")
            print("-" * 90)
            
            for i, entry in enumerate(entries):
                end_time = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if entry.timestamp else "N/A"
                action_count = entry.action_count if entry.action_count is not None else "N/A"
                code_lines = entry.code_lines if entry.code_lines is not None else "N/A"
                completed = "✅" if entry.completed_successfully else "❌" if entry.completed_successfully is not None else "N/A"
                print(f"{i+1:^9} | {end_time:^16} | {action_count:^12} | {code_lines:^10} | {completed:^10}")
            
            print("=" * 90)
            
            # ドライランの場合はここで終了
            if dry_run:
                print("\n✅ ドライラン完了（実際のアップロードは実行されていません）")
                return True
            
            # セッション選択（単一セッションのみ許可）
            if len(entries) > 1:
                print(f"\n🎯 アップロード対象セッションを選択してください（1つのみ選択可能）:")
                print("   - セッション番号: 1つの番号のみ（例: 2）")
                print("   - 最新セッション: 'latest' または Enter")
                print("   - キャンセル: 'q'")
                
                while True:
                    selection = input("\n選択: ").strip()
                    
                    if selection.lower() == 'q':
                        print("❌ アップロードをキャンセルしました。")
                        return False
                    
                    if selection.lower() == 'latest' or not selection:
                        # 最新セッションを選択
                        latest_entry = max(entries, key=lambda e: e.timestamp)
                        selected_entries = [latest_entry]
                        print(f"✅ 最新セッション（{latest_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}）を選択しました")
                        break
                    
                    try:
                        # 単一インデックス解析
                        idx = int(selection)
                        if idx < 1 or idx > len(entries):
                            print(f"❌ インデックス {idx} は無効です（1-{len(entries)}の範囲内で指定してください）")
                            continue
                        
                        selected_entries = [entries[idx-1]]
                        selected_entry = selected_entries[0]
                        print(f"✅ セッション{idx}（{selected_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}）を選択しました")
                        break
                        
                    except ValueError:
                        print("❌ 数値またはコマンドを入力してください。")
            else:
                # 単一セッション
                selected_entries = entries
                print(f"\n📤 単一セッションをアップロード準備完了")
            
            print(f"📤 選択されたセッション情報:")
            selected_entry = selected_entries[0]
            print(f"   終了日時: {selected_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   完了フラグ: {'✅' if selected_entry.completed_successfully else '❌'}")
            print(f"   アクション数: {selected_entry.action_count}")
            print(f"   コード行数: {selected_entry.code_lines}")
            
            # アップロード実行
            print(f"\n⬆️ Webhookにアップロード中...")
            
            def progress_callback(progress: float, status: str):
                print(f"   進捗: {progress:.1f}% - {status}")
            
            upload_result = self.uploader.upload_session_logs(
                selected_entries, 
                progress_callback=progress_callback
            )
            
            # 結果表示
            if upload_result['success']:
                print(f"\n✅ アップロード完了！")
                print(f"   アップロード済み: {upload_result['uploaded_count']} 件")
                print(f"   処理時間: {upload_result['processing_time_seconds']:.2f} 秒")
                print(f"   Webhook URL: {upload_result['webhook_url'][:50]}...")
                
                return True
            else:
                print(f"\n❌ アップロード失敗: {upload_result.get('error', '不明なエラー')}")
                
                if upload_result['failed_count'] > 0:
                    print(f"   失敗件数: {upload_result['failed_count']}")
                
                print("\n💡 トラブルシューティング:")
                print("   - --test で接続テストを実行してください")
                print("   - インターネット接続を確認してください")
                print("   - しばらく待ってからリトライしてください")
                
                return False
                
        except Exception as e:
            self.logger.error(f"ログアップロード中にエラー: {e}")
            print(f"❌ アップロード中にエラーが発生しました: {e}")
            return False
    
    def _parse_indices(self, selection: str, max_count: int) -> List[int]:
        """
        インデックス選択文字列を解析
        
        Args:
            selection: 選択文字列（例: "1,3,5" や "1-3"）
            max_count: 最大インデックス数
            
        Returns:
            選択されたインデックスのリスト（1ベース）
        """
        indices = set()
        
        try:
            for part in selection.split(','):
                part = part.strip()
                
                if '-' in part:
                    # 範囲選択（例: "1-3"）
                    start, end = part.split('-', 1)
                    start_idx = int(start.strip())
                    end_idx = int(end.strip())
                    
                    if start_idx < 1 or end_idx > max_count:
                        raise ValueError(f"範囲 {part} は無効です（1-{max_count}の範囲内で指定してください）")
                    
                    if start_idx > end_idx:
                        raise ValueError(f"範囲 {part} は無効です（開始は終了より小さくしてください）")
                    
                    for i in range(start_idx, end_idx + 1):
                        indices.add(i)
                else:
                    # 単一選択（例: "1"）
                    idx = int(part)
                    if idx < 1 or idx > max_count:
                        raise ValueError(f"インデックス {idx} は無効です（1-{max_count}の範囲内で指定してください）")
                    indices.add(idx)
        
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError("数値以外の文字が含まれています。正しい形式で入力してください。")
            raise e
        
        return sorted(list(indices))


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Webhook版セッションログアップロードツール v1.2.3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python upload_webhook.py stage01                    # stage01のログをアップロード
  python upload_webhook.py stage02 --student 123456A # 特定の学生IDでアップロード
  python upload_webhook.py --all                     # すべてのログをアップロード
  python upload_webhook.py --status                  # 設定状態確認
  python upload_webhook.py --test                    # 接続テスト
  python upload_webhook.py --setup                   # 初期設定
        """
    )
    
    # 位置引数
    parser.add_argument('stage', nargs='?', help='アップロード対象ステージ (例: stage01)')
    
    # オプション引数
    parser.add_argument('--student', '-s', help='特定の学生IDを指定')
    parser.add_argument('--all', '-a', action='store_true', help='すべてのログをアップロード')
    parser.add_argument('--status', action='store_true', help='設定状態確認')
    parser.add_argument('--test', '-t', action='store_true', help='接続テスト実行')
    parser.add_argument('--setup', action='store_true', help='設定セットアップ')
    parser.add_argument('--dry-run', '-n', action='store_true', help='ドライラン（実際のアップロードなし）')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細ログ出力')
    
    args = parser.parse_args()
    
    # ツール初期化
    tool = WebhookUploadTool(verbose=args.verbose)
    tool.print_banner()
    
    try:
        # モード別実行
        if args.setup:
            # 設定セットアップ
            success = tool.setup_configuration()
            sys.exit(0 if success else 1)
        
        elif args.status:
            # 設定状態表示
            ready = tool.print_status()
            print(f"\n💡 ヒント: {'アップロード準備完了です' if ready else '--setup で初期設定を行ってください'}")
            sys.exit(0)
        
        elif args.test:
            # 接続テスト
            success = tool.test_connection()
            sys.exit(0 if success else 1)
        
        else:
            # ログアップロード
            if not args.stage and not args.all:
                print("❌ ステージ名を指定するか、--all オプションを使用してください")
                parser.print_help()
                sys.exit(1)
            
            # アップロード実行
            success = tool.upload_logs(
                stage=args.stage,
                student_id=args.student,
                upload_all=args.all,
                dry_run=args.dry_run
            )
            
            if success:
                print("\n🎉 処理が正常に完了しました！")
                
                # 統計表示
                stats = tool.uploader.get_statistics()
                if stats['total_uploads'] > 0:
                    print(f"\n📈 アップロード統計:")
                    print(f"   総アップロード数: {stats['total_uploads']}")
                    print(f"   成功: {stats['successful_uploads']}")
                    print(f"   失敗: {stats['failed_uploads']}")
                
                print("\n📊 スプレッドシートで進捗を確認してください！")
                
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 処理が中断されました")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ 予期しないエラーが発生しました: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()