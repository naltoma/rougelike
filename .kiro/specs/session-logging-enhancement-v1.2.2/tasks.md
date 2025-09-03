# Implementation Plan

## データモデルとインフラストラクチャ

- [ ] 1. コアデータモデルの実装
  - `engine/session_log_manager.py`にLogResult、DiagnosticReport、LogFileInfo、LogConfig、ValidationResultのdataclassを追加
  - 各データモデルにformat_report()やformat_display()などのヘルパーメソッドを実装
  - LogLevelとEventTypeのEnumをsession_logging.pyから再利用・拡張
  - データモデルの基本的な単体テストを作成
  - _Requirements: 1.1, 2.1, 3.1, 4.1, 5.1_

- [ ] 2. エラーハンドリングクラスの実装
  - `engine/session_log_manager.py`にLogFileAccessError、LogValidationError、ConfigurationErrorクラスを追加
  - 既存のLoggingSystemErrorを拡張してエラーヒエラルキーを構築
  - エラー回復戦略のベースメソッドを各エラークラスに実装
  - エラーハンドリングの単体テストを作成
  - _Requirements: 4.2, 4.4_

## セッションログマネージャーの強化

- [ ] 3. SessionLogManagerの診断機能実装
  - diagnose_logging_system()メソッドを実装してシステム状況をチェック
  - check_log_directories()、check_session_logger_status()、verify_permissions()を実装
  - DiagnosticReportを生成してissuesとrecommendationsを提供
  - コンソール出力用のformat_report()メソッドを実装
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 4. デフォルトログ生成機能の実装
  - enable_default_logging()メソッドを拡張して実際のSessionLoggerを初期化
  - 「簡易版」実装を削除し、既存のSessionLoggerとの統合を実装
  - デフォルト学生IDでのログ生成（DEFAULT_USER使用）を実装
  - ログファイルパスの通知とLogResultオブジェクトの返却を実装
  - _Requirements: 2.1, 2.2, 2.3, 2.5_

- [ ] 5. ログ情報表示機能の実装
  - show_log_info()メソッドを実装して利用可能ログファイル一覧を表示
  - get_latest_log_path()メソッドを実装して最新ログパスを返却
  - ログファイルメタデータ（ファイルサイズ、エントリ数、最終更新日時）の取得
  - 日時順ソート機能とフォーマット済み表示の実装
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

## 設定管理とバリデーション

- [ ] 6. ログ設定管理システムの実装
  - configure_logging()メソッドでLogConfigオブジェクトから設定を適用
  - 環境変数（LOGGING_LEVEL等）からの設定読み込み機能
  - ログローテーションとファイルサイズ制限の実装
  - Google Sheets同期設定とデフォルト設定への復帰機能
  - _Requirements: 5.1, 5.2, 5.3, 5.5_

- [ ] 7. ログバリデーション機能の実装
  - validate_log_integrity()メソッドでログファイル整合性をチェック
  - 破損エントリの検出と不足フィールドの特定機能
  - ValidationResultオブジェクトの生成と推奨事項の提供
  - システム異常終了からのデータ復旧ロジック実装
  - _Requirements: 4.1, 4.3, 4.5_

## テスト機能とシステム統合

- [ ] 8. 包括的テスト機能の実装
  - test_session_logging()メソッドで全ログ機能をテスト
  - 権限エラー、ディスク容量不足等のエラーシナリオ対応
  - 代替保存場所への自動切り替え機能
  - TestResultオブジェクトによる詳細テスト結果の報告
  - _Requirements: 4.1, 4.2, 4.4_

- [ ] 9. main.py統合とシステム初期化
  - main.pyにinitialize_logging_system()関数を追加
  - システム起動時の診断実行とコンソール出力
  - force_enable=Trueでのデフォルトログ有効化
  - 既存のSessionLogManager初期化コードとの統合
  - _Requirements: 1.1, 2.1, 3.1_

## APIレイヤー拡張

- [ ] 10. グローバルAPI関数の実装
  - `engine/api.py`にshow_log_info()グローバル関数を追加
  - get_current_session_log()とconfigure_session_logging()の実装
  - test_logging_system()グローバル関数の実装
  - 既存APIとの整合性を保持しながら新機能を統合
  - _Requirements: 3.1, 3.3, 4.1, 5.1_

- [ ] 11. ディレクトリ構造の拡張
  - `data/diagnostics/`、`data/exports/`、`data/backup/archived/`ディレクトリの自動作成
  - 既存の`data/sessions/`との統合とファイル管理
  - パス設定の`config.py`への追加とディレクトリ権限設定
  - ディレクトリ作成の単体テストとエラー処理
  - _Requirements: 1.5, 3.4, 4.2_

## 統合テストとバリデーション

- [ ] 12. エンドツーエンドテストの実装
  - `tests/test_session_logging_enhanced.py`を作成
  - 全5つの要件領域をカバーする包括的テストクラス
  - モックを使用したGoogle Sheets統合テスト
  - リアルファイルシステムを使用した統合テスト（一時ディレクトリ使用）
  - _Requirements: All requirements need E2E validation_

- [ ] 13. 既存機能への影響検証
  - 既存のsession_logging.pyとの互換性テスト
  - GUI/CUI両モードでのログ機能動作確認
  - パフォーマンス測定（ログ書き込み<10ms、診断<100ms）
  - 回帰テストの実行と既存テストの修正
  - _Requirements: All requirements need backward compatibility verification_

- [ ] 14. エラー処理とリカバリテスト
  - 権限エラー、ディスク容量不足等の異常系テスト
  - ネットワーク障害時のGoogle Sheets連携テスト
  - 設定ファイル破損からの復旧テスト  
  - システム異常終了後のログデータ復旧テスト
  - _Requirements: 4.2, 4.4, 4.5, 5.4_