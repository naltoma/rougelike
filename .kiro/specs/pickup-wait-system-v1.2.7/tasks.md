# Implementation Plan

## Core Command Implementation

- [ ] 1. WaitCommand基本実装
  - `engine/commands.py`にWaitCommandクラスを追加実装
  - ExecutionResultベースのWaitResult dataclass作成
  - execute()メソッドでプレイヤーターン消費ロジック実装
  - undo/can_undo メソッドを取り消し不可として実装
  - get_description()で「1ターン待機」メッセージ返却実装
  - _Requirements: 2.1, 2.4_

- [ ] 2. WaitCommand敵ターン統合
  - WaitCommand.execute()内で敵AIターン実行ロジック統合
  - game_state.enemiesを反復して各敵の標準行動実行
  - 敵の隣接判定と攻撃実行処理を組み込み
  - エラーハンドリングと教育的メッセージ追加
  - _Requirements: 2.2, 2.3, 2.5_

- [ ] 3. WaitCommand API統合
  - `engine/api.py`にwait()関数を追加実装
  - 既存のコマンドパターンに従ってWaitCommandを統合
  - 許可されたAPIリストにwaitを追加する仕組み実装
  - エラーハンドリングを既存move/attack系と統一
  - _Requirements: 7.1, 7.2_

## Enemy AI Enhancement

- [ ] 4. 敵AI移動システム基盤
  - `engine/enemy_system.py`のAdvancedEnemyクラスを拡張
  - patrol_pathフィールドとvision_rangeフィールドを追加
  - current_patrol_indexとmovement_modeの状態管理追加
  - 基本的なpatrol/chase状態遷移ロジック実装
  - _Requirements: 5.1, 5.4_

- [ ] 5. 巡回AI実装
  - AdvancedEnemyに時計回り巡回ロジック実装
  - 1マス壁周囲の経路計算アルゴリズム追加
  - get_next_patrol_position()メソッド実装
  - 巡回中の敵移動処理を既存ターンシステムに統合
  - _Requirements: 5.1_

- [ ] 6. 視界検出・追跡システム
  - プレイヤー検出ロジック（vision_range内判定）実装
  - detect_player()メソッドで視界範囲計算
  - 巡回→追跡モード切り替えロジック実装
  - 視界から外れた時の巡回モード復帰処理
  - _Requirements: 5.2, 5.3, 5.4_

## Stage Configuration

- [ ] 7. Stage07 YAML実装
  - `stages/stage07.yml`ファイル作成
  - 敵HP=60, attack=31設定で武器未装備時1撃死設定
  - 武器アイテム（attack+35効果）配置設定
  - 敵配置を正面攻撃限定となるよう調整
  - allowed_apis配列にpickup, attack, wait追加
  - _Requirements: 3.1, 3.2, 3.3, 3.5_

- [ ] 8. Stage08 YAML実装
  - `stages/stage08.yml`ファイル作成
  - board.sizeを10x10に拡張（従来5x5から2倍化）
  - ループ処理が効果的となるレイアウト設計
  - 移動距離を増やしてfor/while文使用を促すパス配置
  - learning_objectivesにループ処理学習目標を記載
  - _Requirements: 4.1, 4.4, 4.5_

- [ ] 9. Stage09 YAML実装
  - `stages/stage09.yml`ファイル作成  
  - 敵にbehavior: "patrol"とpatrol_path設定を追加
  - 1マス壁周囲の巡回経路を座標配列で定義
  - プレイヤー開始位置を敵視界外に設定
  - 武器取得→視界回避→攻撃の学習フロー設計
  - _Requirements: 5.1, 5.5_

## Session Logging Enhancement

- [ ] 10. pickup初回使用記録
  - `engine/session_logging.py`を拡張してpickup使用記録追加
  - first_pickup_timestamp フィールドをセッションデータに追加
  - pickup()初回呼び出し検出ロジック実装
  - JSONログにpickup学習開始マーカーを記録
  - _Requirements: 8.1_

- [ ] 11. see()機能拡張
  - `engine/api.py`のsee()関数を拡張
  - アイテム存在情報をitems配列として返却
  - 敵状態情報（HP、攻撃力、移動モード）を返却
  - 視界情報（敵の検出範囲）を返却する辞書構造実装
  - _Requirements: 7.3_

## Integration Testing

- [ ] 12. WaitCommand単体テスト
  - `tests/test_wait_command.py`ファイル作成
  - test_wait_command_execution()基本実行テスト実装
  - test_wait_with_adjacent_enemy()隣接敵処理テスト実装
  - test_wait_enemy_ai_response()敵AI応答確認テスト実装
  - test_wait_error_handling()エラーケーステスト実装
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 13. Enemy AI移動テスト
  - `tests/test_enemy_ai_movement.py`ファイル作成
  - test_patrol_movement_cycle()巡回サイクルテスト実装
  - test_player_detection_chase()プレイヤー検出→追跡テスト実装
  - test_vision_range_calculation()視界範囲計算テスト実装
  - test_chase_to_patrol_transition()追跡→巡回復帰テスト実装
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 14. Stage07統合テスト
  - `tests/test_stage07_integration.py`ファイル作成
  - test_stage07_weapon_pickup_victory()武器取得→勝利フローテスト実装
  - test_stage07_no_weapon_defeat()武器未取得→敗北フローテスト実装
  - test_stage07_balance_validation()バランス調整検証テスト実装
  - _Requirements: 3.1, 3.2, 3.3, 6.1, 6.2, 6.3_

- [ ] 15. Stage08-09統合テスト
  - `tests/test_stage08_stage09_integration.py`ファイル作成
  - test_stage08_loop_efficiency()ループ処理効率化テスト実装
  - test_stage09_ai_movement()敵AI移動・追跡テスト実装
  - test_stage09_vision_avoidance()視界回避戦略テスト実装
  - test_stage_size_scaling()ステージサイズ2倍検証テスト実装
  - _Requirements: 4.1, 4.2, 5.1, 5.2, 5.5_

## API Compatibility Validation

- [ ] 16. 既存機能回帰テスト
  - 既存のtest_api.pyを実行してpickup()機能確認
  - WaitCommand追加後のコマンドパターン整合性テスト実装
  - 既存attack()、move()機能とのAPI互換性検証テスト追加
  - エラーメッセージ一貫性のテストケース追加
  - _Requirements: 7.1, 7.2, 7.4_

- [ ] 17. ステージAPI制限テスト
  - stage01-06でのwait()使用制限テスト実装
  - allowed_apis配列による機能制限の動作確認
  - 制限時の教育的エラーメッセージ表示テスト追加
  - CUI/GUIモード両対応のメッセージ表示テスト実装
  - _Requirements: 7.4, 7.5_

## Game Balance Validation

- [ ] 18. バランス調整テスト
  - `tests/test_game_balance.py`ファイル作成
  - test_v127_enemy_player_balance()敵・プレイヤー能力バランステスト実装
  - test_weapon_effect_calculation()武器効果計算テスト実装
  - test_one_hit_scenarios()1撃シナリオの動作確認テスト実装
  - _Requirements: 6.1, 6.2, 6.3, 6.5_