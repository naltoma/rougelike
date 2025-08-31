# セッションログシステム使用ガイド

Python初学者向けローグライクフレームワークのセッション詳細ログ機能

## 概要

セッションログシステムは、学生の学習セッション中に発生する全てのイベントを詳細に記録・分析するシステムです。進捗管理システムと連携して、包括的な学習データを提供します。

### 主要機能

- **リアルタイムログ記録**: 全アクション、エラー、状態変化を即座に記録
- **構造化ログデータ**: JSON Lines形式での効率的なデータ保存
- **セッション分析**: 各学習セッションの詳細統計とメトリクス
- **データエクスポート**: 外部分析ツール用のデータ出力
- **パフォーマンス監視**: システムパフォーマンスとレスポンス時間の追跡

## ログレベルとイベントタイプ

### ログレベル

- **DEBUG**: デバッグ情報、詳細な実行フロー
- **INFO**: 一般的な情報、正常な操作
- **WARNING**: 警告、注意が必要な状況
- **ERROR**: エラー、失敗した操作
- **CRITICAL**: 重大なエラー、システムの継続困難

### イベントタイプ

1. **SESSION_START/END**: セッション開始・終了
2. **STAGE_START/END**: ステージ開始・終了
3. **ACTION_EXECUTED**: ゲームアクション実行
4. **ERROR_OCCURRED**: エラー発生
5. **HINT_USED**: ヒント使用
6. **STATE_CHANGED**: ゲーム状態変化
7. **USER_INPUT**: ユーザー入力
8. **SYSTEM_MESSAGE**: システムメッセージ
9. **PERFORMANCE_METRIC**: パフォーマンス計測
10. **DEBUG_INFO**: デバッグ情報

## 使用方法

### 1. 基本セットアップ

```python
from engine.api import initialize_api, set_student_id

# セッションログを有効にしてAPI初期化
initialize_api("cui", enable_session_logging=True)

# 学生ID設定（自動的にセッション開始）
set_student_id("student_001")
```

### 2. 自動ログ記録

通常のゲームプレイ中、以下が自動的に記録されます：

```python
# 全て自動記録される
initialize_stage("stage01")  # ステージ開始
turn_right()                 # アクション実行
move()                       # アクション実行
# ... ゲーム終了時にステージ終了記録
```

### 3. 手動ログ記録

特定の情報を明示的に記録：

```python
from engine.api import log_user_input, log_debug_info

# ユーザー入力記録
log_user_input("help", "ヘルプコマンド実行")

# デバッグ情報記録
log_debug_info("状態確認", {
    "player_position": (3, 4),
    "current_turn": 10,
    "remaining_hp": 85
})
```

### 4. セッション管理

```python
from engine.api import get_session_summary, end_session, list_session_history

# 現在のセッション情報取得
summary = get_session_summary()
print(f"総アクション数: {summary['total_actions']}")
print(f"エラー率: {summary['total_errors'] / summary['total_actions']:.1%}")

# セッション履歴確認
history = list_session_history("student_001")
print(f"過去のセッション: {len(history)}回")

# セッション明示的終了
end_session()
```

### 5. データエクスポート

```python
from engine.api import export_session_data

# セッションデータをJSONファイルにエクスポート
export_session_data("session_abc123", "analysis/session_data.json")
```

## データ構造

### ログエントリー形式

各ログエントリーは以下の構造を持ちます：

```json
{
  "timestamp": "2024-01-01T10:30:15.123456",
  "session_id": "abc12345",
  "student_id": "student_001",
  "event_type": "action_executed",
  "level": "info",
  "message": "アクション: move - 東に移動成功",
  "stage_id": "stage01",
  "turn_number": 5,
  "game_state": {
    "player_position": {"x": 2, "y": 3},
    "player_direction": "E",
    "turn_count": 5,
    "status": "playing"
  },
  "data": {
    "action": "move",
    "success": true,
    "result_message": "東に移動成功"
  }
}
```

### セッションサマリー形式

```json
{
  "session_id": "abc12345",
  "student_id": "student_001",
  "start_time": "2024-01-01T10:00:00",
  "end_time": "2024-01-01T10:45:30",
  "stages_attempted": ["stage01", "stage02"],
  "total_actions": 125,
  "total_errors": 8,
  "hints_used": 3,
  "successful_stages": 2,
  "total_play_time": "0:25:15"
}
```

## ファイル構造

### ログファイル保存場所

```
data/sessions/
├── session_abc12345.jsonl    # セッション詳細ログ（JSON Lines）
├── summary_abc12345.json     # セッションサマリー
├── session_def67890.jsonl    # 他のセッション
├── summary_def67890.json     # 他のセッションサマリー
└── system.log                # システム全体のログ
```

### JSON Lines形式

ログファイルは1行1JSONの形式で保存されます：

```
{"timestamp":"2024-01-01T10:00:00","event_type":"session_start",...}
{"timestamp":"2024-01-01T10:00:01","event_type":"stage_start",...}
{"timestamp":"2024-01-01T10:00:02","event_type":"action_executed",...}
```

## 教育的活用

### 1. 学習行動分析

```python
def analyze_learning_behavior(session_id):
    """学習行動の分析"""
    from engine.session_logging import SessionLogger
    
    logger = SessionLogger()
    logs = logger.get_session_logs(session_id)
    
    # エラーパターン分析
    errors = [log for log in logs if log.event_type == EventType.ERROR_OCCURRED]
    error_types = {}
    for error in errors:
        error_type = error.data.get('error_type', 'unknown')
        error_types[error_type] = error_types.get(error_type, 0) + 1
    
    print("エラー傾向:")
    for error_type, count in error_types.items():
        print(f"  {error_type}: {count}回")
    
    # 行動パターン分析
    actions = [log for log in logs if log.event_type == EventType.ACTION_EXECUTED]
    action_sequence = [log.data.get('action') for log in actions]
    
    print(f"アクション実行順序: {' → '.join(action_sequence[:10])}...")
```

### 2. リアルタイム指導支援

```python
def real_time_guidance(student_id):
    """リアルタイム指導支援"""
    from engine.api import get_session_summary
    
    summary = get_session_summary()
    
    # エラー率が高い場合の介入
    if summary and summary['total_actions'] > 10:
        error_rate = summary['total_errors'] / summary['total_actions']
        
        if error_rate > 0.3:  # 30%以上のエラー率
            print("🚨 支援推奨: エラー率が高くなっています")
            print("💡 基本操作の復習をお勧めします")
```

### 3. 学習パフォーマンス評価

```python
def evaluate_performance(session_logs):
    """学習パフォーマンス評価"""
    from datetime import datetime
    
    # 反応速度分析
    reaction_times = []
    for i in range(1, len(session_logs)):
        prev_time = datetime.fromisoformat(session_logs[i-1]['timestamp'])
        curr_time = datetime.fromisoformat(session_logs[i]['timestamp'])
        reaction_times.append((curr_time - prev_time).total_seconds())
    
    avg_reaction_time = sum(reaction_times) / len(reaction_times)
    print(f"平均反応時間: {avg_reaction_time:.2f}秒")
    
    # 学習進歩の指標
    # 前半と後半のエラー率を比較
    mid_point = len(session_logs) // 2
    first_half = session_logs[:mid_point]
    second_half = session_logs[mid_point:]
    
    first_errors = sum(1 for log in first_half if log.get('level') == 'error')
    second_errors = sum(1 for log in second_half if log.get('level') == 'error')
    
    improvement = (first_errors - second_errors) / len(first_half) * 100
    print(f"学習改善度: {improvement:+.1f}% (エラー削減)")
```

## 高度な分析

### 1. データマイニング

```python
import json
from collections import Counter

def analyze_session_patterns(session_files):
    """セッションパターン分析"""
    all_actions = []
    
    for session_file in session_files:
        with open(session_file, 'r', encoding='utf-8') as f:
            for line in f:
                log = json.loads(line)
                if log['event_type'] == 'action_executed':
                    all_actions.append(log['data']['action'])
    
    # 最頻出アクション
    action_freq = Counter(all_actions)
    print("アクション頻度:")
    for action, count in action_freq.most_common(5):
        print(f"  {action}: {count}回")
    
    # アクションシーケンス分析
    sequences = []
    for i in range(len(all_actions) - 1):
        sequences.append((all_actions[i], all_actions[i+1]))
    
    sequence_freq = Counter(sequences)
    print("頻出アクション組み合わせ:")
    for sequence, count in sequence_freq.most_common(3):
        print(f"  {sequence[0]} → {sequence[1]}: {count}回")
```

### 2. 統計レポート生成

```python
def generate_statistics_report(student_id, period_days=7):
    """統計レポート生成"""
    from datetime import datetime, timedelta
    from engine.session_logging import SessionLogger
    
    logger = SessionLogger()
    sessions = logger.list_sessions(student_id)
    
    # 期間フィルタリング
    cutoff_date = datetime.now() - timedelta(days=period_days)
    recent_sessions = []
    
    for session_id in sessions:
        summary = logger.get_session_summary(session_id)
        if summary and summary.start_time >= cutoff_date:
            recent_sessions.append(summary)
    
    if not recent_sessions:
        print("対象期間にセッションデータがありません")
        return
    
    # 統計計算
    total_time = sum((s.duration.total_seconds() for s in recent_sessions 
                     if s.duration), 0)
    total_actions = sum(s.total_actions for s in recent_sessions)
    total_errors = sum(s.total_errors for s in recent_sessions)
    
    # レポート出力
    print(f"📊 学習統計レポート ({period_days}日間)")
    print("=" * 40)
    print(f"学習セッション数: {len(recent_sessions)}")
    print(f"総学習時間: {total_time/3600:.1f}時間")
    print(f"総アクション数: {total_actions}")
    print(f"平均エラー率: {total_errors/total_actions:.1%}")
    print(f"平均セッション時間: {total_time/len(recent_sessions)/60:.1f}分")
    
    # 成功率推移
    success_rates = [s.success_rate for s in recent_sessions]
    if len(success_rates) > 1:
        trend = success_rates[-1] - success_rates[0]
        print(f"成功率推移: {trend:+.1%}")
```

## トラブルシューティング

### よくある問題

1. **ログファイルが作成されない**
   - `data/sessions/` ディレクトリの書き込み権限確認
   - セッションが正常に開始されているか確認

2. **セッションが終了しない**
   - `end_session()` を明示的に呼び出す
   - プログラム終了時の自動クリーンアップ確認

3. **ログファイルサイズが大きくなりすぎる**
   - 自動ログローテーション設定確認
   - 古いログファイルの定期削除

### デバッグ用コード

```python
def debug_session_logging():
    """セッションログのデバッグ"""
    from engine.api import _global_api
    
    print("📝 セッションログデバッグ情報")
    print(f"学生ID: {_global_api.student_id}")
    print(f"現在のセッションID: {_global_api.current_session_id}")
    print(f"セッションログ有効: {_global_api.session_logger is not None}")
    
    if _global_api.session_logger:
        print(f"ログバッファサイズ: {len(_global_api.session_logger.log_buffer)}")
        print(f"現在のセッション: {_global_api.session_logger.current_session}")
```

## パフォーマンス考慮事項

### 最適化設定

```python
# カスタム設定でSessionLogger初期化
from engine.session_logging import SessionLogger

logger = SessionLogger(
    log_dir="custom/log/path",
    max_log_files=50,      # ログファイル保持数
    buffer_size=500,       # バッファサイズ（メモリ使用量に影響）
    auto_flush_interval=60 # 自動フラッシュ間隔（秒）
)
```

### メモリ使用量監視

```python
def monitor_logging_performance():
    """ログシステムのパフォーマンス監視"""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    print(f"メモリ使用量: {memory_mb:.1f}MB")
    
    # ログディレクトリサイズ
    from pathlib import Path
    log_dir = Path("data/sessions")
    total_size = sum(f.stat().st_size for f in log_dir.glob("*"))
    
    print(f"ログディスク使用量: {total_size/1024/1024:.1f}MB")
```

このセッションログシステムにより、教師は学生の学習プロセスを詳細に把握し、データドリブンな教育支援を提供できます。また、学生自身も自分の学習パターンを客観的に分析できるようになります。