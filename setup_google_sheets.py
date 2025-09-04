#!/usr/bin/env python3
"""
Google Sheets連携セットアップツール
Google Sheets Integration Setup Tool for v1.2.3

教員・管理者がGoogle Sheets連携の初期設定を行うためのツールです。

使用方法:
    python setup_google_sheets.py              # 対話式セットアップ
    python setup_google_sheets.py --check      # 設定状態確認
    python setup_google_sheets.py --reset      # 設定リセット
    python setup_google_sheets.py --validate   # 設定妥当性検証
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any
import logging

from engine.google_auth_manager import GoogleAuthManager, create_sample_client_config
from engine.shared_folder_config_manager import SharedFolderConfigManager


class GoogleSheetsSetupTool:
    """Google Sheets連携セットアップツール"""
    
    def __init__(self, verbose: bool = False):
        """
        セットアップツール初期化
        
        Args:
            verbose: 詳細ログ出力
        """
        # ログ設定
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # コンポーネント初期化
        self.auth_manager = GoogleAuthManager()
        self.config_manager = SharedFolderConfigManager()
    
    def print_banner(self):
        """バナー表示"""
        print("=" * 70)
        print("🔧 ローグライク演習 Google Sheets連携セットアップツール v1.2.3")
        print("=" * 70)
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """前提条件チェック"""
        print("\n🔍 前提条件をチェック中...")
        
        results = {
            'python_version': sys.version_info >= (3, 7),
            'required_directories': True,
            'google_libs_available': True
        }
        
        # Pythonバージョン確認
        if results['python_version']:
            print(f"✅ Python バージョン: {sys.version.split()[0]}")
        else:
            print(f"❌ Python 3.7以降が必要です（現在: {sys.version.split()[0]}）")
        
        # 必要ディレクトリ確認・作成
        try:
            directories = ['.oauth_credentials', 'data', 'logs']
            for dir_name in directories:
                dir_path = Path(dir_name)
                dir_path.mkdir(exist_ok=True)
            print("✅ 必要ディレクトリ: 作成済み")
        except Exception as e:
            print(f"❌ ディレクトリ作成エラー: {e}")
            results['required_directories'] = False
        
        # Google認証ライブラリ確認
        try:
            import google.auth  # noqa: F401
            import google_auth_oauthlib.flow  # noqa: F401
            import gspread  # noqa: F401
            print("✅ Google認証ライブラリ: インストール済み")
        except ImportError as e:
            print(f"❌ ライブラリ不足: {e}")
            print("   pip install google-auth google-auth-oauthlib gspread を実行してください")
            results['google_libs_available'] = False
        
        return results
    
    def interactive_setup(self) -> bool:
        """対話式セットアップ"""
        print("\n🛠️ Google Sheets連携の対話式セットアップを開始します\n")
        
        # 前提条件チェック
        prereq_results = self.check_prerequisites()
        if not all(prereq_results.values()):
            print("\n❌ 前提条件が満たされていません。上記の問題を解決してから再実行してください。")
            return False
        
        # Phase 1: Google Cloud Console設定
        print("\n" + "="*50)
        print("📋 Phase 1: Google Cloud Console設定")
        print("="*50)
        
        print("""
1️⃣ Google Cloud Consoleでの設定手順:
   
   a) Google Cloud Console (https://console.cloud.google.com/) にアクセス
   b) 新しいプロジェクトを作成または既存プロジェクトを選択
   c) 「APIとサービス」→「ライブラリ」から以下のAPIを有効化:
      - Google Sheets API
      - Google Drive API
   d) 「APIとサービス」→「認証情報」でOAuth 2.0クライアントIDを作成
   e) アプリケーションの種類: 「デスクトップアプリ」を選択
   f) 作成後、JSONファイルをダウンロード
        """)
        
        # クライアント設定ファイル配置確認
        client_config_path = Path('.oauth_credentials/client_config.json')
        
        if not client_config_path.exists():
            print(f"\n📁 クライアント設定ファイルの配置:")
            print(f"   ダウンロードしたJSONファイルを以下の場所に配置してください:")
            print(f"   {client_config_path.absolute()}")
            
            # サンプルファイル作成オプション
            create_sample = input("\n❓ サンプル設定ファイルを作成しますか？ [y/N]: ").strip().lower()
            if create_sample == 'y':
                sample_path = create_sample_client_config()
                print(f"✅ サンプル設定ファイルを作成しました: {sample_path}")
                print("   YOUR_CLIENT_ID_HERE と YOUR_CLIENT_SECRET_HERE を実際の値に置き換えてください")
            
            input("\n⏳ クライアント設定ファイルの配置が完了したらEnterキーを押してください...")
        
        # クライアント設定ファイル確認
        if not client_config_path.exists():
            print("❌ クライアント設定ファイルが見つかりません")
            return False
        
        print("✅ クライアント設定ファイルを確認しました")
        
        # Phase 2: Google Drive共有フォルダ設定
        print("\n" + "="*50)
        print("📁 Phase 2: Google Drive共有フォルダ設定")
        print("="*50)
        
        print(self.config_manager.get_teacher_setup_instructions())
        
        # 共有フォルダURL入力
        while True:
            folder_url = input("\n🔗 Google Drive共有フォルダのURLを入力してください: ").strip()
            
            if not folder_url:
                print("❌ URLが入力されていません")
                continue
            
            if self.config_manager.validate_folder_url(folder_url):
                self.config_manager.set_shared_folder_url(folder_url)
                print("✅ 共有フォルダURLを設定しました")
                break
            else:
                print("❌ 無効なGoogle DriveフォルダURLです")
                print("   例: https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j")
                retry = input("   再入力しますか？ [Y/n]: ").strip().lower()
                if retry == 'n':
                    return False
        
        # Phase 3: OAuth認証テスト
        print("\n" + "="*50)
        print("🔐 Phase 3: OAuth認証テスト")
        print("="*50)
        
        print("Google認証フローをテストします...")
        print("ブラウザが開いてGoogle認証画面が表示されます。")
        
        auth_confirm = input("認証テストを開始しますか？ [Y/n]: ").strip().lower()
        if auth_confirm != 'n':
            try:
                if self.auth_manager.ensure_authenticated():
                    print("✅ Google認証が成功しました！")
                else:
                    print("❌ Google認証に失敗しました")
                    return False
            except Exception as e:
                print(f"❌ 認証エラー: {e}")
                return False
        
        # Phase 4: 接続テスト
        print("\n" + "="*50)
        print("🔍 Phase 4: 接続テスト")
        print("="*50)
        
        try:
            from engine.google_sheets_uploader import GoogleSheetsUploader
            
            uploader = GoogleSheetsUploader(self.auth_manager, self.config_manager)
            success, message = uploader.test_connection()
            
            if success:
                print(f"✅ 接続テスト成功: {message}")
                
                # サンプルシート作成
                sample_url = uploader.create_sample_spreadsheet("セットアップテスト用シート")
                if sample_url:
                    print(f"✅ サンプルスプレッドシート作成: {sample_url}")
                
            else:
                print(f"❌ 接続テスト失敗: {message}")
                return False
        
        except Exception as e:
            print(f"❌ 接続テスト中にエラー: {e}")
            return False
        
        # セットアップ完了
        print("\n" + "="*50)
        print("🎉 セットアップ完了!")
        print("="*50)
        
        print("\n✅ Google Sheets連携の設定が完了しました！")
        print("\n📋 次のステップ:")
        print("1. 学生に upload.py の使用方法を説明")
        print("2. python upload.py --test で動作確認")
        print("3. python upload.py stage01 でテストアップロード")
        
        # 設定サマリー保存
        self.save_setup_summary()
        
        return True
    
    def check_configuration(self) -> Dict[str, Any]:
        """設定状態確認"""
        print("\n📊 現在の設定状態を確認中...")
        
        status = {
            'timestamp': None,
            'auth_status': {},
            'config_status': {},
            'validation_results': {},
            'ready_for_use': False
        }
        
        from datetime import datetime
        status['timestamp'] = datetime.now().isoformat()
        
        # 認証状態確認
        status['auth_status'] = self.auth_manager.get_auth_status()
        
        # 設定状態確認
        status['config_status'] = self.config_manager.get_configuration_status()
        
        # 妥当性検証
        status['validation_results'] = self.config_manager.validate_configuration()
        
        # 使用準備完了判定
        status['ready_for_use'] = (
            status['auth_status']['authenticated'] and
            status['config_status']['configured'] and
            status['config_status']['url_valid'] and
            status['validation_results']['valid']
        )
        
        # 結果表示
        self._print_status_report(status)
        
        return status
    
    def _print_status_report(self, status: Dict[str, Any]):
        """設定状態レポート表示"""
        print("\n" + "="*50)
        print("📋 設定状態レポート")
        print("="*50)
        
        # 認証状態
        auth = status['auth_status']
        print(f"\n🔐 認証状態:")
        print(f"   認証済み: {'✅' if auth['authenticated'] else '❌'}")
        print(f"   認証ファイル: {'✅' if auth['credentials_file_exists'] else '❌'}")
        print(f"   クライアント設定: {'✅' if auth['client_config_exists'] else '❌'}")
        
        # 共有フォルダ設定
        config = status['config_status']
        print(f"\n📁 共有フォルダ設定:")
        print(f"   設定済み: {'✅' if config['configured'] else '❌'}")
        if config['configured']:
            print(f"   URL有効性: {'✅' if config['url_valid'] else '❌'}")
            print(f"   フォルダID: {config['folder_id']}")
        
        # 妥当性検証
        validation = status['validation_results']
        print(f"\n✅ 妥当性検証:")
        print(f"   全体的妥当性: {'✅' if validation['valid'] else '❌'}")
        
        if validation['errors']:
            print("   エラー:")
            for error in validation['errors']:
                print(f"     ❌ {error}")
        
        if validation['warnings']:
            print("   警告:")
            for warning in validation['warnings']:
                print(f"     ⚠️ {warning}")
        
        # 総合判定
        print(f"\n🎯 使用準備: {'✅ 完了' if status['ready_for_use'] else '❌ 未完了'}")
        
        if not status['ready_for_use']:
            print("\n💡 次のアクション:")
            if not auth['authenticated']:
                print("   - Google認証を完了してください")
            if not config['configured']:
                print("   - Google Drive共有フォルダを設定してください")
            if not validation['valid']:
                print("   - 設定エラーを修正してください")
    
    def reset_configuration(self) -> bool:
        """設定リセット"""
        print("\n🔄 設定リセットを実行します...")
        
        reset_confirm = input("⚠️ 全ての設定を削除します。続行しますか？ [y/N]: ").strip().lower()
        if reset_confirm != 'y':
            print("❌ リセットをキャンセルしました")
            return False
        
        try:
            # 認証情報削除
            self.auth_manager.clear_credentials()
            print("✅ 認証情報を削除しました")
            
            # OAuth設定ディレクトリ削除
            oauth_dir = Path('.oauth_credentials')
            if oauth_dir.exists():
                import shutil
                shutil.rmtree(oauth_dir)
                print("✅ OAuth設定ディレクトリを削除しました")
            
            # 設定ファイル削除（存在する場合）
            config_files = ['config.py', 'config_sample.py', 'setup_summary.json']
            for config_file in config_files:
                config_path = Path(config_file)
                if config_path.exists():
                    config_path.unlink()
                    print(f"✅ {config_file} を削除しました")
            
            print("\n✅ 設定リセットが完了しました")
            print("💡 --setup で再セットアップを実行してください")
            
            return True
            
        except Exception as e:
            print(f"❌ リセット中にエラー: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """設定妥当性検証"""
        print("\n🔍 設定妥当性検証を実行中...")
        
        validation_results = self.config_manager.validate_configuration()
        
        if validation_results['valid']:
            print("✅ 全ての設定が有効です")
            
            # 接続テスト実行
            try:
                from engine.google_sheets_uploader import GoogleSheetsUploader
                uploader = GoogleSheetsUploader(self.auth_manager, self.config_manager)
                success, message = uploader.test_connection()
                
                if success:
                    print(f"✅ 接続テスト成功: {message}")
                else:
                    print(f"❌ 接続テスト失敗: {message}")
                    return False
                    
            except Exception as e:
                print(f"❌ 接続テスト中にエラー: {e}")
                return False
        
        else:
            print("❌ 設定に問題があります:")
            for error in validation_results['errors']:
                print(f"   - {error}")
        
        if validation_results['warnings']:
            print("⚠️ 警告:")
            for warning in validation_results['warnings']:
                print(f"   - {warning}")
        
        return validation_results['valid']
    
    def save_setup_summary(self):
        """セットアップサマリー保存"""
        try:
            from datetime import datetime
            
            summary = {
                'setup_completed': True,
                'setup_timestamp': datetime.now().isoformat(),
                'version': 'v1.2.3',
                'auth_status': self.auth_manager.get_auth_status(),
                'config_status': self.config_manager.get_configuration_status(),
                'validation_results': self.config_manager.validate_configuration()
            }
            
            summary_path = Path('setup_summary.json')
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"📄 セットアップサマリーを保存しました: {summary_path}")
            
        except Exception as e:
            print(f"⚠️ サマリー保存エラー: {e}")
    
    def create_config_template(self) -> str:
        """設定テンプレート作成"""
        template_path = self.config_manager.create_sample_config_file()
        print(f"📝 設定テンプレートを作成しました: {template_path}")
        print("   必要な値を入力後、config.py にリネームしてください")
        return template_path


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="Google Sheets連携セットアップツール v1.2.3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python setup_google_sheets.py              # 対話式セットアップ
  python setup_google_sheets.py --check      # 設定状態確認
  python setup_google_sheets.py --reset      # 設定リセット
  python setup_google_sheets.py --validate   # 設定妥当性検証
        """
    )
    
    parser.add_argument('--setup', action='store_true', help='対話式セットアップ実行')
    parser.add_argument('--check', '-c', action='store_true', help='設定状態確認')
    parser.add_argument('--reset', '-r', action='store_true', help='設定リセット')
    parser.add_argument('--validate', '-v', action='store_true', help='設定妥当性検証')
    parser.add_argument('--template', '-t', action='store_true', help='設定テンプレート作成')
    parser.add_argument('--verbose', action='store_true', help='詳細ログ出力')
    
    args = parser.parse_args()
    
    # デフォルトはセットアップモード
    if not any([args.check, args.reset, args.validate, args.template]):
        args.setup = True
    
    # ツール初期化
    tool = GoogleSheetsSetupTool(verbose=args.verbose)
    tool.print_banner()
    
    try:
        if args.setup:
            success = tool.interactive_setup()
            sys.exit(0 if success else 1)
        
        elif args.check:
            status = tool.check_configuration()
            sys.exit(0 if status['ready_for_use'] else 1)
        
        elif args.reset:
            success = tool.reset_configuration()
            sys.exit(0 if success else 1)
        
        elif args.validate:
            valid = tool.validate_configuration()
            sys.exit(0 if valid else 1)
        
        elif args.template:
            tool.create_config_template()
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\n⏹️ セットアップが中断されました")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ セットアップ中にエラーが発生しました: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()