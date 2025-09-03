# セッションログ機能詳細

## 概要

セッションログ機能は、学生のプログラミング学習活動を自動記録し、学習支援と評価を行うためのシステムです。v1.2.2で大幅に改善され、構造的一貫性と機能拡張を実現しています。

## 機能特徴

### 🔄 自動ログ生成
- **デフォルト有効**: main.py実行時に自動でセッションログが生成
- **学生ID自動取得**: `config.STUDENT_ID`または環境変数`STUDENT_ID`から取得
- **セッション一意識別**: UUIDベースのセッションID生成

### 📁 ステージ別管理
```
data/sessions/
├── stage01/          # Stage 01専用ログ
├── stage02/          # Stage 02専用ログ
└── ...
```

### 📊 統合JSON形式
- **単一ファイル**: 1セッション = 1 JSONファイル
- **構造統一**: データの重複や不整合を解消
- **読みやすさ**: 人間が読みやすい階層構造

## ログ構造詳細

### 基本情報
```json
{
  "session_id": "9a780567",           // セッション一意識別子
  "student_id": "TEST003",            // 学生ID
  "stage_id": "stage01",              // ステージ識別子
  "start_time": "2025-09-03T23:58:05.824682",  // 開始時刻
  "end_time": "2025-09-03T23:58:06.348822",    // 終了時刻
  "solve_code": "def solve():\n..."   // solve()関数ソースコード
}
```

### イベント履歴
```json
"events": [
  {
    "timestamp": "2025-09-03T23:58:05.827249",
    "event_type": "turn_right"         // アクション種別
  },
  {
    "timestamp": "2025-09-03T23:58:06.348806", 
    "event_type": "session_complete"   // セッション完了
  }
]
```

### 結果サマリー（統合セクション）
```json
"result": {
  "completed_successfully": false,    // ゲーム完了状況
  "action_count": 5,                  // 実行アクション数
  "code_quality": {                   // コード品質メトリクス
    "line_count": 40,                // 総行数
    "code_lines": 25,                // コード行数
    "comment_lines": 7,              // コメント行数
    "blank_lines": 8                 // 空行数
  }
}
```

## 改善点（v1.2.2）

### ❌ 修正前の問題
- `action_count`が3箇所に分散（0, 5, 5の不整合）
- `completed_successfully`の重複記録
- `total_execution_time`の無意味なデータ
- `attempt_count`の不正確な計算（常に1）

### ✅ 修正後の改善
- **統一性**: 各データ項目が1箇所に集約
- **正確性**: attempt_countはファイル数から動的計算
- **効率性**: 不要なデータ除去
- **拡張性**: コード品質メトリクス追加

## 使用方法

### コマンドライン
```bash
# 全ログ一覧表示
python show_session_logs.py

# 最新ログの詳細表示
python show_session_logs.py --latest

# ログ整合性チェック
python show_session_logs.py --validate

# システム診断
python show_session_logs.py --diagnose

# 設定確認
python show_session_logs.py --config
```

### プログラムからの使用
```python
from engine.session_log_manager import SessionLogManager

# マネージャー初期化
manager = SessionLogManager()

# ログ有効化
result = manager.enable_default_logging("STUDENT001", "stage01")
if result.success:
    print(f"ログファイル: {result.log_path}")

# 挑戦回数取得
attempt_count = manager.get_attempt_count_for_stage("STUDENT001", "stage01")
print(f"挑戦回数: {attempt_count}")

# 最新ログ取得
latest_path = manager.get_latest_log_path()
print(f"最新ログ: {latest_path}")
```

## コード品質メトリクス

### 計測項目
- **line_count**: ソースコードの総行数
- **code_lines**: 実際のコード行数（コメント・空行除く）
- **comment_lines**: コメント行数
- **blank_lines**: 空行数

### 活用例
- 学習進度の把握
- コードスタイルの評価
- コメント記述の習慣化支援
- プログラミング量の可視化

## セキュリティ・プライバシー

### データ保護
- ローカルファイルシステムに保存
- 外部送信は行わない
- 学生IDの匿名化サポート

### ファイル権限
- 適切なファイル権限設定（644）
- ディレクトリ権限管理（755）

## トラブルシューティング

### よくある問題

**Q: ログファイルが生成されない**
```bash
# システム診断で原因特定
python show_session_logs.py --diagnose
```

**Q: 権限エラーが発生する**
```bash
# ディレクトリ権限確認
ls -la data/sessions/

# 権限修正
chmod 755 data/sessions/
```

**Q: ログが破損している**
```bash
# 整合性チェック
python show_session_logs.py --validate
```

## APIリファレンス

### SessionLogManager主要メソッド
- `enable_default_logging(student_id, stage_id)`: ログ機能有効化
- `get_latest_log_path()`: 最新ログファイルパス取得
- `get_attempt_count_for_stage(student_id, stage_id)`: 挑戦回数取得
- `show_log_info()`: ログファイル一覧表示
- `validate_log_integrity(file_path)`: ログ整合性検証

### SimpleSessionLogger主要メソッド
- `set_session_info(stage_id, solve_code)`: セッション情報設定
- `log_event(event_type, data)`: イベントログ記録
- `_calculate_code_metrics(solve_code)`: コード品質計算

## 今後の拡張予定

- Google Sheets連携（オプション）
- 学習分析ダッシュボード
- 多言語対応
- バックアップ・復元機能

---

詳細な実装情報は、[v1.2.2リリースノート](v1.2.2.md)を参照してください。