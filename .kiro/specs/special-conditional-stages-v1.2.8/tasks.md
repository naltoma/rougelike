# Implementation Plan

## コアデータモデル拡張

- [ ] 1. 敵の新状態・モード定義追加
  - engine/__init__.pyにEnemyMode enum追加（CALM, RAGE, HUNTING, TRANSITIONING）
  - RageState dataclass作成（is_active, trigger_hp_threshold, turns_in_rage等）
  - ConditionalBehavior dataclass作成（violation_detected, required_sequence等）
  - Enemy classにenemy_mode, rage_state, conditional_behaviorフィールド追加
  - 新敵タイプ対応の__post_init__拡張（大型敵にRageState、特殊敵にConditionalBehavior自動初期化）
  - _Requirements: 1.1, 2.1, 3.1_

- [ ] 2. 大型敵・特殊敵サイズ定義拡張
  - engine/__init__.pyのEnemyType enumにLARGE_2X2, LARGE_3X3, SPECIAL_2X3確認・追加
  - Enemy.get_size()メソッドで新敵タイプサイズ対応（2x2, 3x3, 2x3）
  - Enemy.get_occupied_positions()メソッドで複数マス占有計算検証
  - 新敵タイプの単体テスト作成（サイズ計算、座標占有確認）
  - _Requirements: 1.1, 2.1, 3.1_

## 大型敵システム実装

- [ ] 3. LargeEnemySystem基盤クラス作成
  - engine/enemy_system.pyにLargeEnemySystemクラス追加
  - initialize_large_enemy()メソッド実装（大型敵初期配置・状態設定）
  - update_rage_state()メソッド実装（HP監視・怒りモード判定ロジック）
  - trigger_rage_mode()メソッド実装（HP50%以下での怒りモード発動）
  - reset_to_calm_mode()メソッド実装（範囲攻撃後の平常モード復帰）
  - _Requirements: 1.2, 1.3, 1.4, 2.4_

- [ ] 4. 怒りモード状態遷移システム実装
  - RageModeController内部クラスとしてLargeEnemySystem内に実装
  - 怒りモード1ターン遷移ロジック（transition_turn_count管理）
  - 怒りモード→範囲攻撃→平常モード サイクル制御
  - HP50%閾値での即座怒りモード移行システム（以降の攻撃で即発動）
  - 怒りモード状態のユニットテスト作成
  - _Requirements: 1.4, 1.5, 1.8, 2.4_

- [ ] 5. 範囲攻撃システム実装
  - execute_area_attack()メソッド実装（大型敵周囲1マス全体攻撃）
  - get_area_attack_range()メソッド実装（攻撃対象座標計算）
  - 2x2敵・3x3敵の範囲攻撃座標計算ロジック（周囲1マス判定）
  - プレイヤー範囲内判定・ダメージ処理統合
  - 範囲攻撃の座標計算ユニットテスト作成
  - _Requirements: 1.6, 2.5_

## 特殊敵システム実装

- [ ] 6. SpecialEnemySystem基盤クラス作成
  - engine/enemy_system.pyにSpecialEnemySystemクラス追加
  - initialize_special_enemy()メソッド実装（HP/ATK=10000設定）
  - 平常時反撃のみ行動制限実装（移動・巡視・追跡無効化）
  - activate_hunting_mode()メソッド実装（条件違反時プレイヤー追跡）
  - auto_eliminate()メソッド実装（条件達成時特殊敵消去）
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 7. 条件付き戦闘管理システム実装
  - ConditionalBattleManagerクラス作成（engine/enemy_system.py内）
  - register_attack_sequence()メソッド実装（攻撃順序記録）
  - validate_attack_sequence()メソッド実装（大型敵2x2→3x3順序検証）
  - check_conditional_violation()メソッド実装（特殊条件違反判定）
  - get_violation_feedback()メソッド実装（教育的フィードバック生成）
  - _Requirements: 6.2, 6.4_

## レンダラー拡張・視覚化システム

- [ ] 8. 大型敵・特殊敵描画システム拡張
  - engine/renderer.pyの敵描画メソッド拡張（2x2, 3x3, 2x3サイズ対応）
  - 怒りモード時の敵描画変更実装（色・エフェクト変更）
  - Enemy Info Panel拡張（敵モード状態・HP割合表示）
  - 特殊敵追跡モード時の視覚表示実装
  - GUI描画の単体テスト作成
  - _Requirements: 1.5, 1.7, 4.3_

- [ ] 9. 範囲攻撃視覚化システム実装
  - AreaAttackVisualizerクラス実装（engine/renderer.py内）
  - 範囲攻撃範囲の視覚的表示（攻撃前予告表示）
  - 攻撃範囲座標の色分け・ハイライト表示
  - 大型敵攻撃時の範囲攻撃アニメーション実装
  - see()コマンド出力での攻撃範囲情報追加
  - _Requirements: 1.6, 2.5, 4.3_

## ステージ定義システム拡張

- [ ] 10. YAML スキーマ拡張・ローダー修正
  - engine/stage_loader.pyでrage_threshold, area_attack_range属性対応
  - special_conditions セクション解析実装
  - 大型敵・特殊敵タイプのYAML読み込み対応
  - ステージ定義バリデーション強化（新属性必須チェック）
  - YAML拡張の単体テスト作成
  - _Requirements: 7.4_

- [ ] 11. Stage11-13 YAML定義ファイル作成
  - stages/stage11.yml作成（大型敵2x2、HP1500、rage_threshold: 0.5）
  - stages/stage12.yml作成（大型敵2x2+3x3、複数大型敵配置）
  - stages/stage13.yml作成（大型敵2体+特殊敵2x3、special_conditions定義）
  - 各ステージの学習目標・ヒント定義
  - ステージ読み込み・初期化の統合テスト作成
  - _Requirements: 4.1, 5.1, 6.1_

## エラーハンドリング・教育システム

- [ ] 12. 特殊ステージ専用エラー処理実装
  - engine/educational_errors.pyにSpecialStageError基底例外クラス追加
  - RageModeTransitionError実装（怒りモード遷移失敗）
  - ConditionalViolationError実装（特殊条件違反）
  - AreaAttackCalculationError実装（範囲攻撃計算エラー）
  - get_educational_error_message()関数実装（教育的エラーメッセージ生成）
  - _Requirements: 8.2_

- [ ] 13. セッションログ統合・学習支援機能
  - 新敵システムの学習成果記録（session_logging.py統合）
  - 特殊条件違反・成功データの記録実装
  - 段階的難易度システムの進捗追跡
  - see()コマンド拡張（敵状態・攻撃範囲観察学習支援）
  - 教育的価値メトリクス収集実装
  - _Requirements: 8.1, 8.3, 8.4_

## メインゲームループ統合

- [ ] 14. 敵システム統合・ターン制御拡張
  - engine/main_game_loop.pyで新敵システム統合
  - 大型敵・特殊敵のターン処理実装
  - 怒りモード遷移・範囲攻撃のターン管理
  - 条件付き戦闘の攻撃順序監視統合
  - プレイヤー攻撃→敵状態更新→レンダリング フロー確認
  - _Requirements: 7.3, 7.5_

- [ ] 15. API層統合・既存機能との互換性確保
  - engine/api.pyで既存wait(), attack(), see() APIとの統合確認
  - 新敵システム情報のsee()出力追加
  - 既存enemy_system.pyコンポーネントとの統合テスト
  - main_*.py非編集制約の検証テスト
  - 設定一元管理の確認・統合
  - _Requirements: 7.1, 7.2_

## 包括的テスト実装

- [ ] 16. 大型敵システム単体・統合テスト
  - test_large_enemy_system.py作成（怒りモード遷移テスト）
  - test_rage_mode_controller.py作成（状態管理テスト）
  - test_area_attack_system.py作成（範囲攻撃計算・実行テスト）
  - 2x2・3x3敵の行動パターンテスト
  - エッジケーステスト（境界HP値、複数攻撃等）
  - _Requirements: 1.1-1.8, 2.1-2.5_

- [ ] 17. 特殊敵・条件付き戦闘システムテスト
  - test_special_enemy_system.py作成（条件付き行動テスト）
  - test_conditional_battle_manager.py作成（攻撃順序監視テスト）
  - test_stage13_integration.py作成（特殊条件戦闘E2Eテスト）
  - 条件違反・達成シナリオの網羅的テスト
  - 教育的エラーメッセージのテスト
  - _Requirements: 3.1-3.4, 6.1-6.4_

- [ ] 18. Stage11-13 E2Eテスト・学習価値検証
  - test_stage11_learning_progression.py作成（怒りモード学習テスト）
  - test_stage12_tactical_thinking.py作成（複数敵戦術テスト）
  - test_stage13_conditional_logic.py作成（条件ロジック学習テスト）
  - パフォーマンステスト（大型敵処理<10ms、範囲攻撃計算<20ms）
  - 教育的価値メトリクス検証（学習者理解度測定）
  - _Requirements: All requirements need E2E validation_