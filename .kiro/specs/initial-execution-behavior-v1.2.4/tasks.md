# Implementation Plan

## データモデル拡張

- [ ] 1. HyperParametersDataクラスの拡張
  - engine/hyperparameter_manager.pyのHyperParametersDataクラスに初回確認モード関連フィールドを追加
  - initial_confirmation_mode: bool = Falseフィールドを追加（デフォルトは確認モード）
  - stage_intro_displayed: Dict[str, bool] = field(default_factory=dict)フィールドを追加
  - __post_init__メソッドでの新フィールドバリデーション処理を実装
  - 新フィールドに対する単体テストを作成
  - _Requirements: 6.1, 6.2_

## 初回確認モード管理システム

- [ ] 2. InitialConfirmationFlagManagerクラスの実装
  - engine/initial_confirmation_flag_manager.pyファイルを新規作成
  - InitialConfirmationFlagManagerクラスを実装（HyperParameterManagerとの統合）
  - get_confirmation_mode()メソッドでフラグ状態取得機能を実装
  - set_confirmation_mode(enabled: bool)メソッドでフラグ設定機能を実装
  - is_first_execution(stage_id, student_id)メソッドで初回実行判定機能を実装
  - _Requirements: 1.1, 1.2, 1.4_

- [ ] 3. 初回確認モードフラグ統合テスト
  - tests/test_initial_confirmation_flag.pyファイルを新規作成
  - デフォルト値がFalse（確認モード）であることを検証するテストを実装
  - フラグ遷移機能（False→True→False）の単体テストを実装
  - HyperParameterManagerとの統合が正しく動作することを検証するテストを実装
  - フラグ状態の即座反映機能をテストで確認
  - _Requirements: 1.3, 1.4_

## ステージ説明表示システム

- [ ] 4. StageDescriptionRendererクラスの実装
  - engine/stage_description_renderer.pyファイルを新規作成
  - StageDescriptionRendererクラスを実装（StageLoaderとの統合）
  - display_stage_conditions(stage)メソッドでステージクリア条件表示機能を実装
  - format_description_text(description)メソッドで説明文フォーマット機能を実装
  - display_fallback_message(stage_id)メソッドでフォールバック表示機能を実装
  - _Requirements: 2.1, 2.3, 2.4_

- [ ] 5. ステージ説明表示機能のテストと統合
  - tests/test_stage_description_renderer.pyファイルを新規作成
  - YAML description項目が存在する場合の表示テストを実装
  - description項目が存在しない場合のフォールバック表示テストを実装
  - 説明文の可読性向上フォーマット機能のテストを実装
  - StageLoaderとの統合動作を検証するテストを実装
  - _Requirements: 2.2, 2.4, 2.5_

## セッションログ条件制御システム

- [ ] 6. ConditionalSessionLoggerクラスの実装
  - engine/conditional_session_logger.pyファイルを新規作成
  - ConditionalSessionLoggerクラスを実装（SessionLogManagerとの統合）
  - should_log_session(confirmation_mode)メソッドでログ生成条件判定機能を実装
  - conditional_log_start(**kwargs)メソッドで条件付きセッション開始ログ機能を実装
  - conditional_log_end(**kwargs)メソッドで条件付きセッション終了ログ機能を実装
  - _Requirements: 3.1, 3.4, 3.5_

- [ ] 7. セッションログ除外機能のテスト実装
  - tests/test_conditional_session_logger.pyファイルを新規作成
  - 確認モード（False）時にログを生成しないことを検証するテストを実装
  - 実行モード（True）時に通常通りログを生成することを検証するテストを実装
  - action_count等の学習データ記録除外機能をテストで確認
  - SessionLogManagerとの統合動作を検証するテストを実装
  - _Requirements: 3.2, 3.3, 3.5_

## main.py統合とフロー制御

- [ ] 8. main.pyの確認モード統合実装
  - main.pyに初回確認モード判定ロジックを追加
  - setup_confirmation_mode()関数を実装してフラグマネージャー初期化処理を追加
  - 確認モード時のステージ説明表示フローを実装
  - 確認モード時のセッションログ除外処理を統合
  - 実行モード時の通常フロー継続処理を実装
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 9. GUI表示制御統合
  - main.pyのGUIループに確認モード表示制御を統合
  - 確認モード時の一時停止状態維持機能を実装
  - モード切替ガイダンス表示機能をターミナル出力に統合
  - GUI更新継続処理の確認モード対応を実装
  - エラー時のグレースフルデグラデーション処理を実装
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

## 設定とエラーハンドリング

- [ ] 10. 設定ファイルの更新とエラーハンドリング
  - config.pyにv1.2.4初回確認モード設定を追加
  - INITIAL_CONFIRMATION_MODE_DEFAULT = False設定を追加
  - STAGE_DESCRIPTION_MAX_WIDTH = 80設定を追加
  - InitialConfirmationModeError例外クラスを実装
  - StageDescriptionError例外クラスを実装
  - _Requirements: 6.3, 6.4, 6.5_

## 統合テストと品質保証

- [ ] 11. 統合テスト実装
  - tests/test_initial_execution_behavior_integration.pyファイルを新規作成
  - 確認モード→実行モードの完全フロー統合テストを実装
  - main.py実行フローの統合テスト（確認モード・実行モード両方）を実装
  - セッションログ生成・除外の統合動作テストを実装
  - エラーハンドリングとフォールバック機能の統合テストを実装
  - _Requirements: すべての要件の統合検証が必要_

- [ ] 12. E2Eテストと最終検証
  - tests/test_e2e_initial_execution.pyファイルを新規作成
  - 学生初回体験の完全フロー（ステージ理解→フラグ変更→実行）のE2Eテストを実装
  - モード切替ワークフローのE2Eテストを実装
  - 既存機能への影響がないことを確認する回帰テストを実装
  - パフォーマンス目標（フラグ判定<1ms、説明表示<50ms）の検証テストを実装
  - _Requirements: すべての要件のE2E検証が必要_