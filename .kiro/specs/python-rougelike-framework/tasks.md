# Implementation Plan

## プロジェクトセットアップと基盤構築

- [ ] 1. プロジェクト構造とコア設定の作成
  - プロジェクトルートディレクトリとサブディレクトリ構造を作成（engine/, stages/, scripts/, tests/, assets/, logs/）
  - conda環境設定ファイル（env.yml）とpip依存関係（requirements.txt）を作成
  - main.pyエントリーポイントとargparse設定（GUI/CUIモード切替）を実装
  - 基本的なロギング設定とconfig.pyファイルを作成
  - _Requirements: 8.1, 8.2, 8.5, 8.6_

- [x] 2. コアデータモデルの実装
  - engine/__init__.pyとenums（Direction, GameStatus, ItemType）を定義
  - Position、Character、Enemy、Item、Boardクラスをdataclassで実装
  - GameState、Stage、LogEntryクラスをdataclassで実装
  - 基本的な型ヒント・バリデーション機能を追加
  - _Requirements: 1.1, 1.3_

- [ ] 3. コマンドパターンの実装
  - Commandベースクラスとコマンド具象クラス（TurnLeft, TurnRight, Move, Attack, Pickup）を実装
  - ExecutionResult、AttackResult、PickupResultクラスを定義
  - コマンド実行・取り消し機能の基盤コードを作成
  - 単体テストでコマンドパターンの動作を検証
  - _Requirements: 1.1, 1.4, 2.1, 2.2_

## ゲーム状態管理システム

- [ ] 4. GameStateManagerの実装
  - GameStateManagerクラスをengine/game_state.pyに実装
  - initialize_game、execute_command、get_current_state、is_game_finishedメソッドを実装
  - ターン数管理、最大ターン制限、勝利・敗北条件判定を追加
  - 単体テストでゲーム状態遷移を検証
  - _Requirements: 1.1, 1.3, 1.4_

- [ ] 5. 移動と衝突判定の実装
  - engine/validator.pyにValidator クラスを実装
  - 移動可能性チェック、壁衝突検出、境界値チェックを実装
  - プレイヤー向き管理とDirection enum との連携
  - 移動・回転コマンドの実行結果処理を実装
  - _Requirements: 2.3, 2.4, 10.2_

## ステージシステムとYAML設定

- [ ] 6. YAML ステージローダーの実装
  - engine/stage_loader.pyにStageLoaderクラスを実装
  - PyYAMLを使用してYAMLファイル解析機能を実装
  - load_stage、validate_stage、get_available_stagesメソッドを実装
  - YAML schema バリデーション（board.size、api.allowed）を追加
  - _Requirements: 3.1, 3.2, 3.3_

- [ ] 7. グリッド表記パーサーの実装
  - stages/にstage01.yml〜stage03.yml基本ステージを作成
  - grid文字列をPosition座標配列に変換するパーサーを実装
  - legend定義（P=player、G=goal、#=wall、.=empty）を処理
  - プレイヤー開始位置・向き、ゴール位置の抽出機能を実装
  - _Requirements: 3.4, 3.5, 3.6_

- [ ] 8. ステージバリデーションの実装
  - ステージ定義の整合性チェック（プレイヤー位置の重複、到達可能性）を実装
  - 許可API制限（allowed: [turn_left, turn_right, move]）の検証を追加
  - 最大ターン数制限の妥当性チェックを実装
  - エラーメッセージの日本語化とValidationResultクラスを作成
  - _Requirements: 3.2, 3.7, 10.1_

## 学生向けAPIレイヤー

- [ ] 9. 基本API関数の実装
  - engine/api.pyにAPILayerクラスを実装
  - turn_left、turn_right、moveメソッドをGameStateManagerと連携して実装
  - APIの呼び出し記録とグローバル状態管理を追加
  - 単体テストで基本移動機能を検証
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 10. 上級API関数の実装
  - attack、pickup、seeメソッドを実装（将来の拡張性を考慮）
  - 段階制限チェック（Stage01-03ではattack/pickup使用不可）を追加
  - see()の戻り値構造（正面、左右、足元情報）を実装
  - APIUsageError例外クラスと教育的エラーメッセージを作成
  - _Requirements: 2.5, 2.6, 2.7, 4.7_

## デュアル表示システム

- [ ] 11. レンダラー基盤の実装
  - engine/renderer.pyにRendererベースクラスを実装
  - RendererFactoryパターンでGUI/CUI選択機能を実装
  - GameStateの変更通知をObserverパターンで実装
  - render_frame、update_displayメソッドの共通インターフェースを定義
  - _Requirements: 5.6, 5.1, 5.2_

- [ ] 12. CUIレンダラーの実装
  - CuiRendererクラスをRenderer基底クラスから実装
  - テキストベースのグリッド表示（文字記号：P=プレイヤー、G=ゴール）を実装
  - ゲーム状態表示（ターン数、結果、エラーメッセージ）を追加
  - コンソール出力のフォーマッティングとクリア機能を実装
  - _Requirements: 5.2, 5.4_

- [ ] 13. pygame GUIレンダラーの実装
  - GuiRendererクラスを実装し、pygameの初期化と基本描画を設定
  - 5x5グリッドの視覚的表示（セルサイズ、色設定）を実装
  - キャラクター、壁、ゴールのスプライト描画（基本的な矩形）を実装
  - ゲーム状態テキスト表示とイベントループ統合を追加
  - _Requirements: 5.1, 5.3_

## 段階的学習システム

- [ ] 14. 進行度管理の実装
  - ProgressionManagerクラスをengine/progression.pyに実装
  - ステージ段階判定（Stage01-03: 移動のみ、Stage04-06: 攻撃追加）を実装
  - API使用制限チェックとeducational フィードバック生成を追加
  - 段階的機能開示（Progressive Disclosure）のロジックを実装
  - _Requirements: 4.1, 4.2, 4.3, 4.7_

- [ ] 15. 学習進捗計算の実装
  - QualityMetricsクラスでコード行数計算を実装
  - solve()関数の抽出・解析・メトリクス算出機能を追加
  - 試行回数、成功ターン数の追跡機能を実装
  - 学習効果指標の計算と統計処理を追加
  - _Requirements: 4.4, 4.5, 4.6_

## ロギング・進捗追跡システム

- [ ] 16. セッションロガーの実装
  - engine/logger.pyにLoggerクラスを実装
  - start_session、log_action、end_sessionメソッドを実装
  - JSONL形式のログ出力機能を追加
  - ログエントリのタイムスタンプ、学生ID、アクション記録を実装
  - _Requirements: 6.1, 6.2, 6.3_

- [ ] 17. 品質メトリクス分析の実装
  - ProgressAnalyzerクラスでコード品質評価を実装
  - solve()関数の論理行数計算、コードハッシュ生成を追加
  - 協力作業者記録（COLLABORATORS定数）の処理を実装
  - 遅延提出判定（PERFORMED_DATE定数）とフラグ設定を追加
  - _Requirements: 6.4, 6.5, 6.6, 6.7_

## エラーハンドリング・教育支援

- [ ] 18. 教育的エラーハンドリングの実装
  - engine/error_handler.pyにEducationalErrorクラス階層を実装
  - MovementError、APIUsageError、LogicError例外クラスを作成
  - 平易な日本語エラーメッセージとヒント生成機能を実装
  - エラー文脈に応じた学習支援メッセージを追加
  - _Requirements: 10.1, 10.2, 10.5_

- [ ] 19. 教育フィードバックシステムの実装
  - ErrorHandlerクラスにhandle_error、generate_hint メソッドを実装
  - ステージ別のヒント生成ロジック（段階に応じた指導）を追加
  - 無限ループ検出、よくある間違いパターンの識別を実装
  - コード改善提案機能と学習効果を高めるフィードバックを実装
  - _Requirements: 10.3, 10.4_

## Google Sheets連携

- [ ] 20. データアップローダーの実装
  - scripts/upload_logs.pyにDataUploaderクラスを実装
  - Google Sheets API連携、認証処理、データ送信機能を実装
  - レート制限（6件/分）チェックとオフライン保存を追加
  - 同一学生×ステージの上書きロジックを実装
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 21. シート管理・バッチ処理の実装
  - ステージ別シート分類機能（stage01, stage02...）を実装
  - バッチログ処理と一括アップロード機能を追加
  - データ形式変換（JSONL → Sheets形式）を実装
  - エラー処理、リトライ機能、ログ管理を実装
  - _Requirements: 7.5, 7.6_

## 高度な機能と統合

- [ ] 22. 敵・アイテムシステムの実装
  - Enemy、Item、EnemyDefinition、ItemDefinitionクラスを実装
  - 攻撃システム、HP管理、アイテム取得・装備機能を追加
  - 大型敵（2x2、3x3）のサイズ表現とレンダリングを実装
  - 敵AI基盤（巡回、追跡パターン）の基本構造を作成
  - _Requirements: 4.2, 4.3, 4.6, 5.5_

- [ ] 23. ランダムステージ生成の実装
  - StageGeneratorクラスをengine/stage_generator.pyに実装
  - ランダム配置アルゴリズム（壁、敵、アイテム）を実装
  - 解法存在性の事前検証機能を追加
  - テンプレートベース生成（R1-movement、R2-attack、R3-pickup）を実装
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 24. メインループ統合
  - main.pyの完全実装（引数解析、モード選択、エラーハンドリング）
  - GameStateManager、Renderer、Logger の統合動作を実装
  - solve()関数の動的実行・検証・フィードバックループを追加
  - システム全体の初期化・実行・終了処理を実装
  - _Requirements: 1.2, 8.3, 8.4_

## テスト・検証

- [ ] 25. 統合テストスイートの実装
  - tests/ディレクトリに主要機能のテストコードを作成
  - 学生の典型的学習フローをE2Eテストとして実装
  - API関数の動作検証、エラーハンドリングのテストを追加
  - YAML読み込み、進捗記録、Google Sheets連携のテストを実装
  - _Requirements: 全要件の検証が必要_

- [ ] 26. 実装完了・品質保証
  - 全コンポーネントの統合動作確認とパフォーマンステストを実行
  - エラーメッセージの日本語表記・可読性確認を実施
  - 学習ワークフローの動作検証（Stage01〜Stage03）を実行
  - コード品質チェック、型ヒント完備、ドキュメンテーション確認を実施
  - _Requirements: 全要件の最終検証が必要_