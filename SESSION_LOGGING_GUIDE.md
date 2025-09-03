# セッションログシステム使用ガイド（v1.2.2対応）

Python初学者向けローグライクフレームワークのセッション詳細ログ機能

## 概要

セッションログシステムは、学生の学習セッション中に発生する全てのイベントを詳細に記録・分析するシステムです。v1.2.2で大幅に改善され、構造統一とコード品質メトリクスが追加されました。

### 主要機能（v1.2.2更新）

- **自動ログ生成**: main.py実行時にデフォルトで有効化
- **統合JSON形式**: 1セッション = 1JSONファイル（構造統一済み）
- **ステージ別管理**: `data/sessions/stage01/` 形式のディレクトリ構造
- **コード品質メトリクス**: 行数、コメント数、空行数の自動計算
- **重複除去**: action_count、completed_successfully等の統一

## 新しいログ構造（v1.2.2）

### 統合JSON形式

```json
{
  "session_id": "9a780567",
  "student_id": "TEST003", 
  "stage_id": "stage01",
  "start_time": "2025-09-03T23:58:05.824682",
  "end_time": "2025-09-03T23:58:06.348822",
  "solve_code": "def solve():\n    # 学生のコード\n    ...",
  "events": [
    {
      "timestamp": "2025-09-03T23:58:05.827249",
      "event_type": "turn_right"
    },
    {
      "timestamp": "2025-09-03T23:58:06.348806",
      "event_type": "session_complete"
    }
  ],
  "result": {
    "completed_successfully": false,
    "action_count": 5,
    "code_quality": {
      "line_count": 40,
      "code_lines": 25,
      "comment_lines": 7,
      "blank_lines": 8
    }
  }
}
```

### 改善されたデータ構造

- **統一されたresultセクション**: action_count、completed_successfullyが1箇所に集約
- **削除された冗長データ**: total_execution_time（ステップ実行では無意味）、attempt_count（ファイル数から計算）
- **追加されたcode_quality**: 自動コード分析メトリクス

## 使用方法

### 1. 基本セットアップ（デフォルト有効）

```python
# main.py実行で自動的にセッションログが有効化
python main.py

# 学生IDはconfig.STUDENT_IDまたは環境変数から自動取得
```

### 2. ログ確認方法

```bash
# 全ログ一覧表示
python show_session_logs.py

# 最新ログの詳細表示
python show_session_logs.py --latest

# ログ整合性チェック
python show_session_logs.py --validate

# システム診断
python show_session_logs.py --diagnose
```

### 3. プログラムからの使用

```python
from engine.session_log_manager import SessionLogManager

# マネージャー初期化
manager = SessionLogManager()

# ログ有効化
result = manager.enable_default_logging("STUDENT001", "stage01")
if result.success:
    print(f"ログファイル: {result.log_path}")

# 挑戦回数取得（ファイル数ベース）
attempt_count = manager.get_attempt_count_for_stage("STUDENT001", "stage01")
print(f"挑戦回数: {attempt_count}")

# 最新ログ取得
latest_path = manager.get_latest_log_path()
print(f"最新ログ: {latest_path}")
```

## ファイル構造（v1.2.2更新）

### ステージ別ディレクトリ構造

```
data/sessions/
├── stage01/
│   ├── 20250903_235805_TEST003.json
│   ├── 20250903_235758_TEST_FIX.json
│   └── ...
├── stage02/
│   ├── 20250904_101234_STUDENT001.json
│   └── ...
└── ...
```

### ログファイル命名規則
- 形式: `YYYYMMDD_HHMMSS_STUDENT_ID.json`
- 例: `20250903_235805_TEST003.json`

## コード品質メトリクス（新機能）

### 自動計測項目
```json
"code_quality": {
  "line_count": 40,        // 総行数
  "code_lines": 25,        // 実コード行数（コメント・空行除く）
  "comment_lines": 7,      // コメント行数
  "blank_lines": 8         // 空行数
}
```

### 活用方法
```python
# ログファイルからコード品質を分析
import json

with open('data/sessions/stage01/20250903_235805_TEST003.json') as f:
    data = json.load(f)
    quality = data['result']['code_quality']
    
    comment_ratio = quality['comment_lines'] / quality['line_count'] * 100
    print(f"コメント率: {comment_ratio:.1f}%")
    
    code_density = quality['code_lines'] / quality['line_count'] * 100
    print(f"コード密度: {code_density:.1f}%")
```

## 教育的活用

### 1. 学習進捗の可視化

```python
def analyze_student_progress(student_id, stage_id):
    """学生の学習進捗を分析"""
    from pathlib import Path
    import json
    
    stage_dir = Path(f"data/sessions/{stage_id}")
    student_logs = list(stage_dir.glob(f"*_{student_id}.json"))
    
    if not student_logs:
        print("ログファイルが見つかりません")
        return
    
    print(f"📊 {student_id}の{stage_id}学習進捗")
    print(f"挑戦回数: {len(student_logs)}回")
    
    # 各試行の分析
    for i, log_file in enumerate(sorted(student_logs), 1):
        with open(log_file) as f:
            data = json.load(f)
            
        result = data['result']
        quality = result.get('code_quality', {})
        
        print(f"試行{i}: アクション{result['action_count']}回, " + 
              f"コード{quality.get('line_count', 0)}行, " +
              f"完了: {'✅' if result['completed_successfully'] else '❌'}")
```

### 2. コード品質の追跡

```python
def track_code_quality(student_id):
    """コード品質の推移を追跡"""
    from pathlib import Path
    import json
    
    # 全ステージのログを取得
    sessions_dir = Path("data/sessions")
    all_logs = []
    
    for stage_dir in sessions_dir.iterdir():
        if stage_dir.is_dir():
            student_logs = list(stage_dir.glob(f"*_{student_id}.json"))
            all_logs.extend(student_logs)
    
    if not all_logs:
        print("ログファイルが見つかりません")
        return
    
    print(f"📈 {student_id}のコード品質推移")
    
    # 時系列でソート
    all_logs.sort(key=lambda f: f.stat().st_mtime)
    
    for log_file in all_logs:
        with open(log_file) as f:
            data = json.load(f)
        
        quality = data['result'].get('code_quality', {})
        stage = data.get('stage_id', 'unknown')
        
        if quality:
            comment_ratio = quality['comment_lines'] / quality['line_count'] * 100
            print(f"{stage}: {quality['line_count']}行 (コメント{comment_ratio:.1f}%)")
```

## パフォーマンス考慮事項

### メモリ効率
- 統合JSON形式により冗長性を削減
- ログファイルサイズの最適化

### ディスク効率
- ステージ別ディレクトリによる整理
- 自動ローテーション機能（設定可能）

## マイグレーション情報

### v1.2.1からの変更点
- **ログ構造**: JSONL形式から統合JSON形式へ
- **保存場所**: `data/sessions/`直下から`data/sessions/stage##/`へ
- **データ統合**: 重複フィールドの除去
- **機能追加**: コード品質メトリクス

### 後方互換性
- show_session_logs.pyは両形式に対応
- 既存のJSONLログも引き続き表示可能

## トラブルシューティング

### よくある問題

**Q: セッションログが生成されない**
```bash
# システム診断で原因特定
python show_session_logs.py --diagnose
```

**Q: ログファイルが見つからない**
```bash
# ステージ別ディレクトリを確認
ls -la data/sessions/stage01/
```

**Q: コード品質が計算されない**
```bash
# solve()関数のコードが正しく取得されているか確認
python show_session_logs.py --latest
```

## APIリファレンス

### SessionLogManager主要メソッド
- `enable_default_logging(student_id, stage_id)`: ログ機能有効化
- `get_latest_log_path()`: 最新ログファイルパス取得（再帰検索対応）
- `get_attempt_count_for_stage(student_id, stage_id)`: 挑戦回数取得
- `show_log_info()`: ログファイル一覧表示（ステージ別対応）

### SimpleSessionLogger（内部クラス）
- `set_session_info(stage_id, solve_code)`: セッション情報設定
- `log_event(event_type, data)`: イベントログ記録
- `_calculate_code_metrics(solve_code)`: コード品質計算（新機能）

---

詳細な技術情報は、[セッションログ機能詳細](docs/session-log-features.md)および[v1.2.2リリースノート](docs/v1.2.2.md)を参照してください。