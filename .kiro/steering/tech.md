# Technology Stack

## Architecture
- **パターン**: 教育用フレームワーク + ゲームエンジン
- **設計思想**: シンプルなAPI設計、段階的機能追加、可読性重視
- **配布方式**: conda環境配布、手動セットアップによる学習効果

## Frontend
- **GUI v1.2.2**: pygame（デフォルト表示・実行制御対応・Critical Fixes完了・セッションログ統合完了）
  - 2D描画、5x5〜10x10グリッド表示
  - キャラクター・敵・アイテム・壁の視覚化
  - 大型敵（2x2, 3x3）・特殊敵（2x3）対応
  - **🆕 実行制御パネル**: Step/Continue/Pause/Stopボタン
  - **🆕 一時停止機能**: solve()実行前の学習者確認
  - **🆕 キーボードショートカット**: Space/Enter/Esc対応
  - **🆕 v1.2.2 GUI最適化**: 900x505px画面（Player Info凡例完全表示）
- **CUI**: テキストベース表示（学習目的・デバッグ用）
  - 同一ロジック、切替可能設計
- **API設計**: 直感的関数名、向き制御重視
  ```python
  turn_left(), turn_right()  # 向き変更
  move()                     # 正面移動
  attack(), pickup()         # アクション
  see() -> dict             # 状況取得
  ```

## Backend
- **言語**: Python 3.x
- **ゲームエンジン**: pygame（GUI用）
- **データ処理**: 標準ライブラリ中心
  - json, csv（ログ出力）
  - yaml（ステージ定義読込）
  - hashlib（コードハッシュ）
- **API連携**: Google Sheets API（ログ送信）

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
python main.py          # GUI v1.2.2 mode（デフォルト・Critical Fixes完了・セッションログ統合完了）
python main.py --cui    # CUI mode
python main.py --gui    # 明示的GUI指定
python student_example.py  # 学生サンプル実行

# セッションログ確認（v1.2.2）
python show_session_logs.py  # ステージ別ディレクトリ対応版

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
- `GOOGLE_SHEETS_URL`: 送信先シートURL（教員設定）

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
- **ログ出力**: JSONL
  ```json
  {"timestamp": "2024-08-30T14:39:00", "student_id": "123456A", "stage_id": "stage01", "turns": 5, "attempts": 3, "result": "pass"}
  ```

## Security Considerations
- **認証**: 学籍番号ベース、匿名化なし
- **データ保護**: ローカル実行、最小限の外部通信
- **不正対策**: 将来実装（コード類似度検出、制限時間等）
- **プライバシー**: 学内ドメイン限定公開

## Performance Requirements
- **レスポンス**: ターン実行 < 100ms
- **メモリ**: < 100MB（pygame含む）
- **ファイルサイズ**: コード上限300行/32KB
- **レート制限**: Google Sheets 6件/分