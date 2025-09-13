# Technology Stack

## Architecture
- **パターン**: 教育用フレームワーク + ゲームエンジン
- **設計思想**: シンプルなAPI設計、段階的機能追加、可読性重視
- **配布方式**: conda環境配布、手動セットアップによる学習効果

## Frontend
- **GUI v1.2.7**: pygame（デフォルト表示・実行制御対応・Critical Fixes完了・セッションログ統合完了・Webhook連携対応・Attack System統合完了・Wait API & Enemy AI Vision System統合完了）
  - 2D描画、5x5〜10x10グリッド表示
  - キャラクター・敵・アイテム・壁の視覚化
  - 大型敵（2x2, 3x3）・特殊敵（2x3）対応
  - **✅ 実行制御パネル**: Step/Continue/Pause/Stopボタン（v1.2.1で安定化完了）
  - **✅ 一時停止機能**: solve()実行前の学習者確認
  - **✅ キーボードショートカット**: Space/Enter/Esc対応
  - **✅ GUI最適化**: 900x505px→540px高さ（Enemy Info Panel対応、v1.2.6で完了）
  - **⚔️ 敵インデックス表示**: 複数敵の識別（1,2,3...）マップ上と右サイドバーに表示
  - **⚔️ Enemy Info Panel**: 敵のHP/攻撃力情報表示（v1.2.6新機能）
- **CUI**: テキストベース表示（学習目的・デバッグ用）
  - 同一ロジック、切替可能設計
- **API設計**: 直感的関数名、向き制御重視
  ```python
  turn_left(), turn_right()  # 向き変更
  move()                     # 正面移動
  attack()                   # 攻撃 (v1.2.6完全統合)
  pickup()                   # アイテム取得 (v1.2.8予定)
  wait()                     # 戦術的待機 (v1.2.7完全統合)
  see() -> dict             # 状況取得
  ```

## Backend
- **言語**: Python 3.x
- **ゲームエンジン**: pygame（GUI用）
- **データ処理**: 標準ライブラリ中心
  - json, csv（ログ出力）
  - yaml（ステージ定義読込）
  - hashlib（コードハッシュ）
- **API連携**: Google Apps Script Webhook（ログ送信、v1.2.3で完了）

## 🆕 v1.1 Backend Components
- **実行制御システム**: ExecutionController
  - 段階的実行管理（Step/Continue/Pause/Stop）
  - solve()実行前一時停止
  - ExecutionMode状態管理（PAUSED/RUNNING/STOPPED）
- **ハイパーパラメータ管理**: HyperParameterManager
  - 学生ID自動検証（6桁数字+英大文字1桁）
  - ステージID検証とバリデーション
  - ログ設定管理と検証
- **拡張セッションログ**: SessionLogManager
  - 簡易版ログ機能の改善実装
  - セッション開始・完了ログ記録
  - エラーハンドリング強化
- **アクション履歴**: ActionHistoryTracker
  - 詳細な行動記録とトラッキング
  - 学習分析用データ収集

## 🔧 v1.2.1 Backend Critical Fixes
- **ExecutionController最適化**: Step実行状態管理の改善
  - 1ボタン1アクション実行の確実な制御
  - step_countの正確な管理とリセット処理
  - pause_requestedフラグの適切な状態遷移
- **main.py GUIループ修正**: should_continue_main_loop()にCONTINUOUSモード追加
  - 連続実行フローの安定化
  - GUI画面更新の最適化
- **ActionHistoryTracker統合強化**: reset_counter()のシステムリセット統合
  - 完全なシステムリセット処理
  - アクション履歴番号の適切なリセット

## 📊 v1.2.2 Backend Session Logging Integration
- **SimpleSessionLogger統合実装**: session_logging.py統合によるコード品質メトリクス自動計算
  - action_count、completed_successfully等の重複データ削除
  - 行数、コメント数、空行数の自動計算機能
  - 構造統一による一貫性向上
- **ステージ別ディレクトリ管理**: `data/sessions/stage01/`形式の階層構造導入
  - SessionLogManagerの再帰検索対応実装
  - ファイル名解析の`.json`対応（従来は`.jsonl`のみ）
- **統合JSON形式**: 1セッション=1JSONファイル（冗長データ削除）
  - total_execution_time削除（ステップ実行では無意味）
  - データ構造最適化とサイズ削減

## 🚀 v1.2.5 Continue Execution Speed Control Components (COMPLETED)
- **Enhanced7StageSpeedControlManager**: 7段階速度制御システム
  - x1〜x50の細かい速度調整（2.0秒〜0.001秒）
  - 高精度スリープ制御（1ms精度対応）
  - リアルタイム速度変更機能
- **UltraHighSpeedController**: 超高速実行専用コントローラー
  - x10〜x50の超高速実行対応
  - デバッグ用途の視認不可レベル速度
  - パフォーマンス最適化された実行制御
- **SpeedControlErrorHandler**: 速度制御専用エラー処理
  - Enhanced7StageSpeedErrors例外クラス
  - 速度設定エラーの適切な処理
  - フォールバック機能とエラー回復

## ⚔️ v1.2.6 Attack System Integration Components (COMPLETED)
- **Attack System統合**: プレイヤー攻撃機能の完全実装
  - attack()API完全統合とダメージ計算統一
  - プレイヤー攻撃力30統一（表示値と実際値一致）
  - 敵HP設定統一（max_hp = hp）
- **敵AIカウンター攻撃システム**: 攻撃を受けた敵の反撃機能
  - 方向転換機能（攻撃前にプレイヤー方向を向く）
  - ターン制戦闘（方向転換と攻撃を別ターンに分離）
- **Combat System強化**: 戦闘ロジックの最適化
  - ダメージ表示と実際のダメージ値の完全一致
  - 敵HP管理とステージファイル連動
- **Stage04-06追加**: 戦闘ベース学習ステージ
  - 段階的攻撃学習（基本攻撃→複数回攻撃→長期戦闘）
- **Session Log Code Lines計算改善**: 学習データ純度向上
  - フレームワーク必須行除外（def, from, set_auto_render, print()）
  - 実際の学習コード行のみ記録

## 🛡️ v1.2.7 Wait API & Enemy AI Vision System Components (COMPLETED)
- **wait()API統合**: 戦術的待機システム実装
  - 1ターン待機による敵行動観察機能
  - プレイヤーアクションとして完全統合
  - 戦略的タイミング判断学習支援
- **敵AI視覚システム**: 高度な敵行動AI実装
  - 方向性視覚システム（前方視界・視線方向制御）
  - 壁遮蔽システム（視線ブロック・見通し判定）
  - 警戒追跡システム（プレイヤー発見・追跡・記憶）
  - 巡回パターンAI（巡視ルート・方向転換）
- **Stage07-10追加**: wait()・敵AI視覚活用ステージ
  - 段階的戦術学習（敵行動観察→視界回避→巡回パターン→高度戦術）
  - 敵AI行動パターン学習とタイミング戦略
- **ステージ毎プレイヤー設定**: 柔軟なゲームバランス調整
  - プレイヤーHP・攻撃力のステージ毎設定
  - YAML定義による動的パラメータ制御

## 🔗 v1.2.3 Google Apps Script Webhook Integration Components (COMPLETED)
- **WebhookUploader**: Google Apps Script Webhook送信機能
  - HTTP POST通信による無料Webhook連携
  - JSON形式データ送信（v1.2.2互換）
  - 接続テスト・エラーハンドリング機能
- **WebhookConfigManager**: 設定管理システム
  - webhook_config.json自動生成・管理
  - 初回セットアップウィザード機能
  - 設定状態確認・バリデーション
- **SessionLogLoader**: ログファイル読み込み機能
  - ステージ別ディレクトリ対応（data/sessions/stage01/）
  - 複数セッション選択・フィルタリング機能
  - コード品質メトリクス統合読み込み
- **Google Apps Script (Code.gs)**: サーバーサイド処理
  - ステージ別シート自動作成・管理
  - 同一学生データ自動上書き機能
  - 共有フォルダ配置・権限管理

## 📋 v1.2.4 Initial Execution Behavior Enhancement Components (COMPLETED)
- **InitialConfirmationFlagManager**: 初回実行管理システム
  - 初回実行判定とステージ履歴管理
  - 確認モード/実行モードの状態切り替え
  - HyperParametersData拡張による永続化
- **StageDescriptionRenderer**: ステージ説明表示システム
  - 構造化されたステージ詳細情報表示
  - YAML定義からの自動情報抽出
  - フォールバック機能とエラー処理
- **ConditionalSessionLogger**: 条件付きログシステム
  - 実行モードに応じた選択的ログ記録
  - 確認モード時のログ除外機能
  - 既存SessionLoggerとの統合設計
- **専用エラーハンドリング**: 教育的エラー管理
  - StageDescriptionError (ステージ説明関連)
  - InitialConfirmationModeError (確認モード関連)
  - 分離された例外クラスによる適切な処理

## Development Environment
- **Python**: 3.8+ 必須
- **仮想環境**: conda推奨
- **パッケージ管理**: pip（教育目的で手動インストール手順）
- **設定ファイル**: 
  - `requirements.txt` : pip環境定義（pytest統合）
  - `conftest.py` : pytest設定
  - `config.py` : プロジェクト設定

## Testing Infrastructure (v1.0.1)
- **フレームワーク**: pytest 7.4.0+
- **プラグイン**: 
  - pytest-html (HTML レポート)
  - pytest-json-report (JSON出力)
  - pytest-cov (カバレッジ測定)
  - pytest-xdist (並列実行)
  - pytest-mock (モック機能)
  - pytest-clarity (改善された出力)
  - pytest-sugar (プログレス表示)
  - pytest-benchmark (ベンチマーク)

## Common Commands
```bash
# 環境構築（教育目的で段階的に）
conda create -n rougelike python=3.8+
conda activate rougelike
pip install -r requirements.txt

# 実行
python main.py          # GUI v1.2.7 mode（デフォルト・7段階速度制御・初回確認モード・Webhook対応・Attack System統合・Wait API & Enemy AI Vision System統合）
python main.py --cui    # CUI mode
python main.py --gui    # 明示的GUI指定
python student_example.py  # 学生サンプル実行
# v1.2.7: Wait API & Enemy AI Vision System統合・Stage07-10追加・ステージ毎プレイヤー設定
# ENABLE_LOGGING = False (確認モード) / True (実行モード)

# セッションログ確認（v1.2.2）
python show_session_logs.py  # ステージ別ディレクトリ対応版

# Google Sheets Webhook連携（v1.2.3新機能）
python upload_webhook.py --setup      # 初回セットアップ
python upload_webhook.py stage01      # ステージログアップロード
python upload_webhook.py --test       # 接続テスト
python upload_webhook.py --status     # 設定状態確認
python test_multiple_students.py "https://..." stage01 -n 10  # 複数学生テスト

# テスト実行（推奨: pytest統合）
python run_tests.py     # 高機能実行（失敗分析付き）
pytest -v               # 基本pytest実行
pytest --lf -v          # 失敗テストのみ再実行
pytest -m "not gui" -v  # GUIテスト以外
pytest -k "progression" -v  # パターンマッチ

# Makefile実行
make test               # 全テスト実行
make test-failed        # 失敗テストのみ
make test-no-gui        # GUIテスト以外
make test-coverage      # カバレッジ付き
make test-parallel      # 並列実行
```

## Environment Variables
- `STUDENT_ID`: 6桁数字+英大文字1桁
- `PERFORMED_DATE`: YYYY-MM-DD形式（遅延判定用）
- `COLLABORATORS`: カンマ区切り学籍番号
- `WEBHOOK_URL`: Google Apps Script WebhookエンドポイントURL（v1.2.3）
- `SHARED_FOLDER_URL`: Google Drive共有フォルダURL（オプション、v1.2.3）

## Port Configuration
- **開発時**: なし（スタンドアロン実行）
- **将来拡張**: 
  - ローカルサーバー: 8080（ダッシュボード用）
  - WebSocket: 8081（リアルタイム進捗共有）

## Data Formats
- **ステージ定義**: YAML
  ```yaml
  id: stage01
  board:
    size: {w: 5, h: 5}
    repr:
      grid: |
        P....
        .....
        ..G..
  api: {allowed: [turn_left, turn_right, move]}
  ```
- **ログ出力**: JSON（v1.2.2統合形式）
  ```json
  {"timestamp": "2024-08-30T14:39:00", "student_id": "123456A", "stage_id": "stage01", "turns": 5, "attempts": 3, "result": "pass"}
  ```
- **Webhookデータ**: JSON（v1.2.3形式）
  ```json
  {
    "student_id": "123456A",
    "stage_id": "stage01", 
    "end_time": "2025-09-04T19:30:00",
    "solve_code": "def solve(): ...",
    "completed_successfully": true,
    "action_count": 10,
    "code_lines": 25
  }
  ```

## Security Considerations
- **認証**: 学籍番号ベース、匿名化なし
- **データ保護**: ローカル実行、最小限の外部通信
- **Webhook通信**: HTTPS/TLS暗号化通信（v1.2.3）
- **Google Apps Script**: 実行権限のみ（OAuth2認証不要）
- **不正対策**: 将来実装（コード類似度検出、制限時間等）
- **プライバシー**: 学内ドメイン限定公開

## Performance Requirements
- **レスポンス**: ターン実行 < 100ms
- **メモリ**: < 100MB（pygame含む）
- **ファイルサイズ**: コード上限300行/32KB
- **レート制限**: Google Sheets 6件/分