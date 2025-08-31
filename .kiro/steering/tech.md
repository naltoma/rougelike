# Technology Stack

## Architecture
- **パターン**: 教育用フレームワーク + ゲームエンジン
- **設計思想**: シンプルなAPI設計、段階的機能追加、可読性重視
- **配布方式**: conda環境配布、手動セットアップによる学習効果

## Frontend
- **GUI**: pygame（デフォルト表示）
  - 2D描画、5x5〜10x10グリッド表示
  - キャラクター・敵・アイテム・壁の視覚化
  - 大型敵（2x2, 3x3）・特殊敵（2x3）対応
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

## Development Environment
- **仮想環境**: conda推奨
- **パッケージ管理**: pip（教育目的で手動インストール手順）
- **設定ファイル**: 
  - `env.yml` : conda環境定義
  - `requirements.txt` : pip環境定義（併記）

## Common Commands
```bash
# 環境構築（教育目的で段階的に）
conda create -n rougelike python=3.x
conda activate rougelike
pip install pygame PyYAML requests

# 実行
python main.py          # GUI mode（デフォルト）
python main.py --cui    # CUI mode

# ログ送信
python upload_logs.py   # 手動実行
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