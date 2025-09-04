# Product Overview

## Product Description
Python初学者向け演習フレームワーク - ローグライク風ステージをプログラミングで攻略する教育システム

## Core Features
- **ゲーム感覚学習**: CUI/GUI両対応のローグライク風ステージ
- **段階的学習**: 移動→条件分岐→ループ→攻撃→アイテム取得の順次習得
- **自動評価**: 厳密なゴール判定とクリアログ自動生成
- **進捗管理**: Google Sheets連携による学習進捗の可視化
- **柔軟な環境**: conda環境での配布・運用
- **🆕 GUI v1.1**: ステップ実行制御、実行ボタンUI、一時停止機能
- **🆕 実行制御**: Step/Continue/Pause/Stopによる段階的コード実行
- **🆕 ハイパーパラメータ管理**: 学生ID・ステージ設定の自動検証

## Target Use Case
- **対象**: 大学初学年のPython初学者（プログラミング基礎演習）
- **学習時間**: 毎週30〜60分 × 7回程度
- **運用環境**: 各自PC（macOS/Windows混在）、conda環境
- **評価方式**: 提出状況確認 + 品質による加点評価

## Key Value Proposition
- **直感的操作**: turn_left/right, move, attack等のシンプルなAPI
- **視覚的フィードバック**: pygameによるGUI表示で学習内容を視覚化
- **段階的難易度**: 16ステージ+ランダム生成ステージによる体系的学習
- **共同学習**: 他学生の進捗参照と協力作業ログ機能
- **教員支援**: 自動ログ収集・分析による学習状況把握
- **高度テストシステム**: pytest対応、88.9%成功率、失敗分析・再実行機能

## Current Version: v1.2.2 (Session Logging Integration Complete)
- **コアエンジン**: 21ファイル (拡張) - 完全実装済み + v1.2.2機能
- **テストスイート**: 26ファイル - pytest統合、マーカー対応
- **品質評価**: 優良⭐ (機能カバレッジ100%, テスト成功率88.9%)
- **高機能テスト**: 失敗分析、再実行、並列実行、カバレッジ対応
- **🆕 v1.2.2新機能**: セッションログ統合・GUI改善（900x505px画面、ステージ別ログ管理、コード品質メトリクス）
- **📋 v1.2.3予定**: Google Sheets連携強化（学生間進捗共有、タイムスタンプソート機能）

## Core Implemented Features  
- GUI（pygame）+ CUI両対応、デフォルトGUI
- 包括的敵AIシステム（巡回、追跡、警備、ハンター）
- 完全アイテムシステム（装備、消耗品、エンチャント） 
- 戦闘・ドロップシステム
- YAML形式ステージ定義
- JSONL/CSV形式ログ出力
- Google Sheets連携機能（オプション）
- 教育的エラーメッセージ・フィードバック
- 無限ループ自動検出
- 段階的ヒントシステム
- リアルタイム学習データ収集
- 自動学習パターン分析

## 🆕 v1.1 GUI Enhancement Features
- **実行制御システム**: ExecutionController による段階的実行管理
- **GUIステップ実行**: Step/Continue/Pause/Stopボタン付きコントロールパネル
- **solve()実行前一時停止**: 学習者が準備してから実行開始
- **キーボードショートカット**: Space=Step, Enter=Continue, Esc=Stop
- **ハイパーパラメータ検証**: 学生ID・ステージID自動バリデーション
- **拡張セッションログ管理**: SessionLogManager による改善されたログ機能
- **アクション履歴トラッキング**: ActionHistoryTracker による詳細行動記録

## 🔧 v1.2.1 GUI Critical Fixes Features
- **Stepボタン完全修正**: 1ボタンで1アクションの確実実行、連続押下対応
- **Pauseボタン機能安定化**: 連続実行中のアクション境界での正確一時停止
- **Resetボタン包括修正**: システム全体の完全リセット（step_count、アクション履歴含む）
- **Continue実行最適化**: GUIループ継続条件修正による安定動作
- **状態管理強化**: ExecutionController状態管理とActionHistoryTrackerの統合改善

## 📊 v1.2.2 Session Logging Integration & GUI Enhancements Features
- **セッションログ統合実装**: SimpleSessionLogger統合による構造統一とコード品質メトリクス自動計算
- **ステージ別ログ管理**: `data/sessions/stage01/`形式の階層ディレクトリ構造導入  
- **GUI画面サイズ最適化**: 900x505px（Player Info凡例完全表示対応）
- **統合JSON形式**: 1セッション=1JSONファイル（冗長データ削除、構造最適化）
- **コード品質測定**: 行数、コメント数、空行数の自動計算とaction_count等の統合
- **show_session_logs.py対応**: 新ログ構造とステージ別ディレクトリ完全対応

## Advanced Testing Framework
- **pytest統合**: 高機能テスト実行と分析
- **失敗テスト分析**: 詳細レポートと再実行コマンド自動生成
- **テストマーカー**: unit/integration/gui分類実行
- **並列実行**: pytest-xdist対応で高速化
- **カバレッジ測定**: pytest-cov統合
- **Makefile対応**: make test/test-failed/test-coverage等

## Success Metrics
- **達成率**: ステージクリア率の向上
- **学習効率**: 平均試行回数・ターン数の最適化
- **コード品質**: solve()関数の論理行数削減
- **継続性**: 週次課題の提出継続率
- **理解度**: 発展ステージでの自動解法ロジック設計能力