# 実装計画

## データモデルと基盤クラス

- [ ] 1. 実行制御とアクション履歴のデータモデルを作成
  - `engine/__init__.py`にExecutionMode、ExecutionState、ActionHistoryEntryのdataclassを追加
  - ExecutionModeをEnum（PAUSED, STEPPING, CONTINUOUS, COMPLETED）として定義
  - ExecutionStateにmode、sleep_interval、is_running、step_count、created_atフィールドを実装
  - ActionHistoryEntryにsequence、action_name、timestamp、execution_resultフィールドを実装
  - 各データクラスの基本的なvalidation メソッドとstr表現を実装
  - _Requirements: 1.1, 1.3, 1.6, 3.1, 3.2_

- [ ] 2. ハイパーパラメータ管理の基盤を実装
  - `engine/hyperparameter_manager.py`を新規作成
  - HyperParametersDataクラス（stage_id、student_id、log_enabled）をdataclassで実装
  - HyperParameterManagerクラスのvalidateメソッドで学生ID検証ロジックを実装
  - config.pyとの統合のためのload_from_configとsave_to_configメソッドを実装
  - 学生ID未設定時のわかりやすいエラーメッセージを日本語で実装
  - _Requirements: 2.1, 2.2, 2.3_

## 実行制御システム

- [ ] 3. ExecutionControllerの核心機能を実装
  - `engine/execution_controller.py`を新規作成
  - threading.EventとExecutionStateを使用した基本的な状態管理を実装
  - pause_before_solve()メソッド：solve()実行前の自動停止機能
  - step_execution()メソッド：1回のAPIアクション実行後の一時停止
  - continuous_execution()メソッド：sleep_intervalに基づく連続実行制御
  - stop_execution()メソッドとis_execution_complete()メソッドの基本実装
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 4. 速度制御とアニメーション機能を実装
  - ExecutionControllerに5段階のsleep_interval設定機能を追加
  - set_animation_speed()メソッドで1秒、0.5秒、0.25秒、0.125秒、0.0625秒の速度設定
  - continuous_execution()でのtime.sleep()による適切な間隔制御
  - 速度変更中の実行状態維持ロジックを実装
  - ExecutionControllerの単体テストを作成（`tests/test_execution_controller.py`）
  - _Requirements: 1.6_

## アクション履歴システム

- [ ] 5. ActionHistoryTrackerの履歴管理機能を実装
  - `engine/action_history_tracker.py`を新規作成
  - collections.dequeとthreading.Lockを使用したthread-safe実装
  - track_action()メソッド：アクション名と実行順序の記録機能
  - display_action_history()メソッド：「N: function_name()」形式での出力
  - reset_counter()とget_action_count()メソッドでカウンター管理
  - ActionHistoryTrackerの単体テストを作成（`tests/test_action_history_tracker.py`）
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

## main.py構造改善

- [ ] 6. main.pyの構造をリファクタリング
  - main.pyにハイパーパラメータ設定セクションを追加（solve()関数直前）
  - HyperParameterManagerを使用したstage_idとstudent_idの管理
  - ステージ初期化処理を別関数setup_stage()として分離
  - 凡例と初期状態表示を別関数show_initial_state()として分離
  - solve()関数をキャラクタ操作のみに純化
  - 結果表示を別関数show_results()として分離し、solve()完了後に実行
  - _Requirements: 2.1, 2.2, 2.4, 2.5, 2.6_

- [ ] 7. ExecutionControllerとmain.pyの統合
  - main.pyにExecutionControllerのインスタンスを統合
  - solve()実行直前でのpause_before_solve()自動呼び出し
  - solve()完了後の完了メッセージ表示と一時停止処理
  - HyperParameterManagerとの連携によるエラーハンドリング
  - リファクタリング後のmain.py動作確認テストを作成（`tests/test_main_integration.py`）
  - _Requirements: 1.1, 1.5, 2.3_

## GUI拡張機能

- [ ] 8. GuiRendererの実行制御UI要素を追加
  - `engine/renderer.py`のGuiRendererクラスに実行制御ボタン群を追加
  - pygame.Rectを使用してStep、Run、Stopボタンのレンダリング実装
  - 速度選択UI（5段階）をサイドバーに追加実装
  - ボタンの状態管理（有効/無効、押下状態）の視覚的フィードバック
  - ExecutionControllerとの基本連携メソッド（set_execution_controller）を実装
  - _Requirements: 1.2, 1.3, 1.4, 1.6_

- [ ] 9. GUIイベント処理と実行制御の統合
  - GuiRendererの_handle_events()メソッドを拡張
  - マウスクリックイベントでの実行制御ボタンの処理
  - キーボードショートカット（F1=Step、F2=Run、F3=Stop）の実装
  - ExecutionControllerのメソッド呼び出しとUI状態の同期
  - pygame イベント処理の50ms応答性要求の達成
  - GUI拡張機能の統合テストを作成（`tests/test_gui_execution_control.py`）
  - _Requirements: 1.2, 1.3, 1.4_

## セッションログ管理

- [ ] 10. SessionLogManagerの実装
  - `engine/session_log_manager.py`を新規作成
  - 既存SessionLoggerとの統合によるデフォルトログ有効化
  - enable_default_logging()メソッド：main.py実行時の自動ログ生成
  - notify_log_location()メソッド：生成されたログファイルパスの通知
  - provide_log_access_method()メソッド：ログ参照方法の提供
  - セッション完了時のログ記録機能強化
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

## APIレイヤー統合

- [ ] 11. APILayerにアクション履歴連携を実装
  - `engine/api.py`のAPILayerクラスにActionHistoryTrackerを統合
  - enable_action_tracking()メソッドの実装
  - 既存のAPIメソッド（turn_left、turn_right、move等）にtrack_action呼び出しを追加
  - ExecutionControllerとの連携によるstep実行制御
  - APIレイヤーでのアクション実行タイミング制御（100ms以内要求）
  - _Requirements: 3.1, 3.3_

- [ ] 12. 統合システムの連携とエラーハンドリング
  - 全コンポーネント（ExecutionController、ActionHistoryTracker、SessionLogManager）の統合
  - エラークラス（ExecutionControlError、ActionTrackingError）の実装
  - 既存EducationalErrorHandlerとの統合によるユーザーフレンドリーなエラーメッセージ
  - get_session_log_path()メソッドをAPILayerに追加
  - コンポーネント間の依存性注入パターンの実装
  - _Requirements: 4.3, 全要求事項のエラーハンドリング_

## テストと品質保証

- [ ] 13. 統合テストの実装
  - E2Eワークフロー（main.py実行→ステップ実行→履歴確認→完了）のテスト作成
  - pygame GUIと実行制御の統合動作テスト（`tests/test_gui_integration.py`）
  - ログシステム連携の統合テスト（`tests/test_session_logging_integration.py`）
  - パフォーマンス要求（50ms GUI応答、100ms履歴表示）の検証テスト
  - 既存v1.0.1 API互換性の回帰テスト
  - _Requirements: 全要求事項のE2E検証_

- [ ] 14. 品質保証とドキュメント更新
  - pytest実行による全テストの成功確認
  - 既存テストスイートとの統合確認
  - パフォーマンス目標値（50ms GUI応答、100ms履歴表示）の計測
  - コード品質メトリクス（新機能カバレッジ95%以上）の確認
  - v1.1機能のテストマーカー追加とMakefile対応
  - _Requirements: 全要求事項の品質保証_