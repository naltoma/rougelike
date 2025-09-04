# Implementation Plan

## 認証システムと基盤設定 (Authentication System & Foundation Setup)

- [ ] 1. requirements.txtの更新とGoogle認証ライブラリのセットアップ
  - `google-auth>=2.23.0`, `google-auth-oauthlib>=1.1.0`, `google-auth-httplib2>=0.1.0`を追加
  - 既存の`oauth2client`依存を削除し、deprecation warningを解決
  - 新しいライブラリでのimport動作を確認するテストを作成  
  - `.oauth_credentials/`ディレクトリ構造をセットアップ
  - _Requirements: All requirements need foundational authentication setup_

- [ ] 2. GoogleAuthManagerクラスの実装
  - `engine/google_auth_manager.py`を新規作成
  - OAuth2認証フロー実装（`initiate_oauth_flow()`メソッド）
  - 認証情報の安全な保存・読み込み機能（`save_credentials()`, `load_credentials()`）
  - トークンリフレッシュ機能（`refresh_credentials()`）の実装
  - 認証状態確認機能（`ensure_authenticated()`）の実装
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 3. SharedFolderConfigManagerクラスの実装  
  - `engine/shared_folder_config_manager.py`を新規作成
  - `config.py`からGoogle共有フォルダURL設定読み込み機能
  - 共有フォルダURL検証とエラーハンドリング
  - 設定未設定時のガイダンスメッセージ機能
  - 教員向け設定ヘルパー機能の実装
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

## セッションログデータ処理 (Session Log Data Processing)

- [ ] 4. StudentLogEntryデータモデルの実装
  - `engine/session_data_models.py`を新規作成  
  - StudentLogEntry, LogSummaryItem, UploadResult, SheetConfigurationデータクラス定義
  - 学生ID形式バリデーション（6桁数字+英大文字1桁）
  - ISO8601形式のタイムスタンプ処理機能
  - コード品質メトリクス（行数、コメント数、空行数）計算機能
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 5. SessionLogLoaderクラスの実装
  - `engine/session_log_loader.py`を新規作成
  - `data/sessions/stageXX/`からJSONファイル読み込み機能
  - セッションログの既存JSON構造からStudentLogEntry変換
  - ステージ指定でのログファイル検索とフィルタリング
  - ログサマリ表示用のLogSummaryItemリスト生成
  - エラーハンドリング（ファイル不存在、JSON破損対応）
  - _Requirements: 1.2, 1.5, 7.6_

- [ ] 6. LogSummaryDisplayerとUserInputHandlerの実装  
  - `engine/log_summary_displayer.py`を新規作成
  - セッションログサマリのインデックス付き表形式表示機能
  - 実行終了時間、行数、アクション数、ゴール到達状況表示
  - ユーザーインデックス選択とバリデーション機能
  - 不正入力時のエラーメッセージ表示
  - 選択確認とキャンセル機能の実装
  - _Requirements: 1.2, 1.3, 1.4, 8.4_

## Google Sheets統合コンポーネント (Google Sheets Integration Components)

- [ ] 7. StageSheetManagerクラスの実装
  - `engine/stage_sheet_manager.py`を新規作成
  - ステージ別スプレッドシート検索・作成機能（`get_or_create_stage_spreadsheet()`）
  - 4シート構造初期化（Timestamp Sort, Action Count Sort, Code Lines Sort, Original Data）
  - `log-stageXX`命名規則でのファイル作成機能
  - Google Drive共有フォルダ内でのファイル管理
  - スプレッドシート権限設定とエラーハンドリング
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 8. MultiSortProcessorクラスの実装
  - `engine/multi_sort_processor.py`を新規作成  
  - 3種類のソート機能（timestamp desc, action_count asc, code_lines asc）
  - Google Sheets batchUpdate APIを使用したソート処理
  - 全ソートシート同期更新機能（`update_all_sort_sheets()`）
  - ソート処理エラー時のOriginal Dataシートフォールバック
  - バッチ操作によるAPI呼び出し最適化
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 9. StudentDataOverwriteHandlerクラスの実装
  - `engine/student_data_overwrite_handler.py`を新規作成
  - 既存学生データ検索機能（`find_existing_student_row()`）
  - 学生データ上書き更新機能（`overwrite_student_data()`）
  - 全ソートシートでの一貫した上書き処理
  - データ整合性検証機能（`validate_data_integrity()`）
  - 上書き完了メッセージとログ出力機能
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

## アップロードシステム統合 (Upload System Integration)

- [ ] 10. GoogleSheetsUploaderメインクラスの実装
  - `engine/google_sheets_uploader.py`を新規作成
  - 全コンポーネント統合（Auth, StageSheet, MultiSort, Overwrite）
  - セッションログアップロードのメイン処理フロー（`upload_session_log()`）
  - 認証状態確認と自動認証機能（`ensure_authenticated()`）
  - ステージログサマリ取得機能（`get_stage_logs_summary()`）
  - アップロード結果のUploadResult生成
  - _Requirements: 1.1, 1.4, 2.1, 4.5, 6.1_

- [ ] 11. ErrorHandlingSystemとProgressIndicatorの実装
  - `engine/error_handling_system.py`を新規作成
  - 4種類のエラー分類（認証、ネットワーク、データ整合性、設定）
  - エラー種別ごとの具体的解決策メッセージ
  - 進捗インジケーター表示機能（アップロード中の状態表示）
  - リトライ機能とレート制限対応（指数バックオフ）
  - 詳細エラーログとユーザー向け簡潔メッセージの分離
  - _Requirements: 8.1, 8.2, 8.3, 8.5, 2.5_

- [ ] 12. 既存data_uploader.pyのmodernization
  - `engine/data_uploader.py`の`oauth2client`から`google-auth`への移行
  - 新しい認証フローとの互換性確保
  - 既存機能を維持しつつ新しいGoogleAuthManagerとの統合
  - 非推奨警告の削除とライブラリ更新
  - 既存テストの修正と新しい認証方式での動作確認
  - _Requirements: All requirements need legacy code compatibility_

## CLIツール実装 (CLI Tool Implementation)

- [ ] 13. upload.pyコマンドラインインターフェースの実装  
  - プロジェクトルートに`upload.py`を新規作成
  - argparseを使用したステージID引数処理とバリデーション
  - 使用方法表示機能（引数なし実行時）
  - GoogleSheetsUploaderの初期化とエラーハンドリング統合
  - メイン処理フローの実装（認証→ログ選択→アップロード）
  - _Requirements: 1.1, 1.2, 8.4_

- [ ] 14. CLIインタラクティブフローの実装  
  - upload.pyにログ選択インターフェース統合
  - LogSummaryDisplayerとUserInputHandlerとの連携
  - アップロード確認ダイアログとプログレス表示
  - 成功時のスプレッドシートURLとアクセス方法表示
  - エラー時の解決策ガイダンス表示
  - _Requirements: 1.3, 1.4, 8.4, 8.5_

## 設定システム統合 (Configuration System Integration)  

- [ ] 15. config.pyのGoogle Sheets設定項目追加
  - `config.py`にGoogle共有フォルダURL設定項目を追加
  - OAuth認証設定項目（client_id, client_secret）の追加
  - 設定バリデーション機能とデフォルト値設定
  - 環境変数からの設定読み込み機能
  - 設定サンプルファイルとドキュメンテーションコメント
  - _Requirements: 3.1, 3.2, 2.1_

- [ ] 16. セキュリティとプライバシー機能の実装
  - 認証トークンの暗号化保存機能（`.oauth_credentials/`内）
  - 学生ID仮名化オプション（設定による切り替え）
  - ソースコード列の非表示設定（デフォルト非表示、要求時のみ展開）
  - セキュリティ監査ログ機能（認証イベント、データアクセス記録）
  - 異常活動検出（大量アップロード等）のアラート機能
  - _Requirements: All requirements need security measures_

## 統合テストと検証 (Integration Testing & Validation)

- [ ] 17. Google Sheets統合テストスイートの実装
  - `tests/test_google_sheets_integration_v1_2_3.py`を新規作成
  - GoogleAuthManager, StageSheetManager, MultiSortProcessorの単体テスト
  - エンドツーエンドアップロードフローの統合テスト
  - エラーシナリオテスト（ネットワークエラー、認証失敗、権限不足）
  - モックオブジェクトを使用したGoogle Sheets APIテスト
  - _Requirements: All requirements need comprehensive testing_

- [ ] 18. CLIツールと既存システムの統合テスト
  - upload.pyのコマンドライン引数処理テスト
  - 既存session_loggingシステムとの連携テスト
  - エラーハンドリングと復旧シナリオテスト
  - パフォーマンステスト（5秒以内アップロード、バッチ処理50 rows/sec）
  - セキュリティテスト（認証フロー、データ暗号化）
  - _Requirements: All requirements need final E2E validation_

## 最終統合と要件検証 (Final Integration & Requirements Validation)

- [ ] 19. 全要件の動作検証とバグ修正
  - 8つの要件すべての受け入れ基準（EARS）動作確認
  - 重複学生データ上書き機能の詳細テスト
  - マルチソート表示機能の正確性検証
  - エラーメッセージとユーザーガイダンスの改善
  - パフォーマンス目標（応答時間、スループット）の達成確認
  - _Requirements: All requirements final validation_

- [ ] 20. ドキュメント統合とリリース準備
  - requirements.txtの依存関係最終確認と更新
  - 既存テストスイートでの新機能回帰テスト実行
  - エラーログとデバッグ情報の最適化
  - プロダクション環境でのセキュリティ設定確認
  - 学生・教員向け使用手順の技術的検証
  - _Requirements: All requirements need production readiness_