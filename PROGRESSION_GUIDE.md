# 進捗管理システム使用ガイド

Python初学者向けローグライクフレームワークの学習進捗管理機能

## 概要

このフレームワークには、学生の学習進捗を自動的に追跡・分析する高度な進捗管理システムが組み込まれています。

### 主要機能

- **自動学習記録**: ゲームプレイ中のアクション、エラー、パフォーマンスを自動記録
- **スキルレベル評価**: 5つの異なるスキル領域での進捗追跡
- **学習分析**: 効率性、正確性、改善率などの詳細メトリクス
- **個人化推奨**: AI による個別の学習推奨事項
- **長期追跡**: JSON ファイルによる永続的なデータ保存

## スキルレベル評価システム

### 5つのスキル領域

1. **効率性 (Efficiency)**: 最適なターン数でゴールを達成する能力
2. **正確性 (Accuracy)**: エラーを避けて正確にプログラムする能力  
3. **速度 (Speed)**: 問題を迅速に解決する能力
4. **問題解決力 (Problem Solving)**: 独力で課題を解決する能力
5. **アルゴリズム品質 (Algorithm Quality)**: 高品質なアルゴリズムを作成する能力

### レベル段階

- **Beginner (初心者)**: 0-99 XP
- **Intermediate (中級者)**: 100-299 XP
- **Advanced (上級者)**: 300-599 XP
- **Expert (エキスパート)**: 600+ XP

## 使用方法

### 1. 基本セットアップ

```python
from engine.api import initialize_api, set_student_id

# 進捗管理を有効にしてAPI初期化
initialize_api("cui", enable_progression=True)

# 学生ID設定（必須）
set_student_id("student_001")
```

### 2. 自動進捗記録

ゲームプレイ中、以下が自動的に記録されます：

- 実行したアクション（移動、回転など）
- 発生したエラー  
- ゲーム結果（成功/失敗）
- 使用ターン数
- 実行時間

```python
# 通常のゲームプレイ
initialize_stage("stage01")
turn_right()
move()
# ... 全てのアクションが自動記録される
```

### 3. 進捗確認

```python
# 学習進捗サマリーを表示
show_progress_summary()

# 特定ステージの詳細レポート
stage_report = get_progress_report("stage01")
print(f"成功率: {stage_report['success_rate']:.1%}")

# AI からの学習推奨事項
recommendations = get_learning_recommendations()
for rec in recommendations:
    print(rec)
```

### 4. ヒント使用の記録

```python
# ヒント使用を明示的に記録
use_hint()
print("💡 攻略のコツ: 右手法で迷路を探索しましょう")
```

## データ構造

### 挑戦記録 (StageAttempt)

各ステージ挑戦ごとに記録される情報：

```json
{
  "stage_id": "stage01",
  "attempt_number": 1,
  "start_time": "2024-01-01T10:00:00",
  "end_time": "2024-01-01T10:02:30",
  "result": "won",
  "turns_used": 8,
  "max_turns": 20,
  "actions_taken": ["turn_right", "move", "move", ...],
  "errors_made": [],
  "hints_used": 0,
  "success": true
}
```

### スキル進捗 (SkillProgress)

各スキル領域の進捗：

```json
{
  "skill_type": "efficiency",
  "current_level": "intermediate",
  "experience_points": 150.0,
  "level_progress": 0.25
}
```

## 進捗分析メトリクス

### パフォーマンス評価

- **効率性スコア**: `1.0 - (使用ターン / 最大ターン)`
- **正確性スコア**: `1.0 - (エラー数 / 総アクション数)`
- **改善率**: 初回と最新の成功時パフォーマンス比較
- **一貫性スコア**: パフォーマンスの安定性

### 経験値獲得システム

成功時に各スキルで獲得する経験値：

- **効率性**: `効率性スコア × 50 XP`
- **正確性**: `正確性スコア × 40 XP`
- **問題解決力**: `基本30 XP + ヒントなしボーナス20 XP`
- **速度**: `(60秒 - 実行時間) / 60秒 × 35 XP`
- **アルゴリズム品質**: `(効率性+正確性)/2 × 45 XP`

## ファイル管理

### データ保存場所

```
data/progression/
├── student_001.json    # 学生ごとの進捗データ
├── student_002.json
└── ...
```

### JSON データ形式

```json
{
  "student_id": "student_001",
  "created_at": "2024-01-01T10:00:00",
  "last_updated": "2024-01-01T15:30:00",
  "stage_attempts": {
    "stage01": [/* 挑戦記録のリスト */],
    "stage02": [/* ... */]
  },
  "skills": {
    "efficiency": {/* スキル進捗 */},
    "accuracy": {/* ... */}
  }
}
```

## 教育的活用

### 1. 個別指導

```python
def check_student_progress(student_id):
    """学生の進捗をチェックして個別指導"""
    set_student_id(student_id)
    
    report = get_progress_report()
    
    # 苦手分野の特定
    low_skills = []
    for skill_name, skill_data in report['skills'].items():
        if skill_data['level'] == 'beginner' and skill_data['xp'] < 50:
            low_skills.append(skill_name)
    
    if low_skills:
        print(f"改善が必要な分野: {', '.join(low_skills)}")
    
    # 推奨事項表示
    recommendations = get_learning_recommendations()
    for rec in recommendations:
        print(f"推奨: {rec}")
```

### 2. クラス全体の分析

```python
def analyze_class_performance():
    """クラス全体の学習状況を分析"""
    students = ["student_001", "student_002", "student_003"]
    
    class_stats = {
        "total_attempts": 0,
        "average_success_rate": 0.0,
        "skill_averages": {}
    }
    
    for student_id in students:
        set_student_id(student_id)
        report = get_progress_report()
        
        class_stats["total_attempts"] += report.get("total_attempts", 0)
        # ... 統計処理
    
    print("📊 クラス全体の学習状況")
    print(f"総挑戦回数: {class_stats['total_attempts']}")
```

### 3. 学習進度の可視化

進捗データを外部ツール（Excel、Google Sheets など）にエクスポートして可視化：

```python
import json
from pathlib import Path

def export_progress_data(student_id, output_file):
    """進捗データをCSV形式でエクスポート"""
    progress_file = Path(f"data/progression/{student_id}.json")
    
    if progress_file.exists():
        with open(progress_file) as f:
            data = json.load(f)
        
        # CSV形式に変換してエクスポート
        # ... データ変換処理
```

## トラブルシューティング

### よくある問題

1. **進捗が記録されない**
   - 学生ID設定を確認: `set_student_id("your_id")`
   - 進捗管理が有効か確認: `initialize_api(enable_progression=True)`

2. **データファイルが見つからない**
   - `data/progression/` ディレクトリの存在確認
   - ファイルパーミッションの確認

3. **スキル経験値が増加しない**
   - ステージを成功でクリアしているか確認
   - ゲーム終了まで到達しているか確認

### デバッグ用コード

```python
def debug_progression():
    """進捗管理のデバッグ情報を表示"""
    from engine.api import _global_api
    
    print("📊 進捗管理デバッグ情報")
    print(f"学生ID: {_global_api.student_id}")
    print(f"進捗管理有効: {_global_api.progression_manager is not None}")
    
    if _global_api.progression_manager:
        print(f"現在のセッション: {_global_api.progression_manager.current_session}")
```

## サンプルコード

### 完全な学習セッション例

```python
#!/usr/bin/env python3
"""
完全な進捗管理つき学習セッション例
"""

from engine.api import *

def learning_session():
    # セットアップ
    initialize_api("cui", enable_progression=True)
    set_student_id("example_student")
    
    # ステージ1: 基本移動
    print("🎯 Stage01: 基本移動")
    if initialize_stage("stage01"):
        turn_right()
        for _ in range(4):
            move()
        turn_right()
        for _ in range(4):
            move()
    
    # ステージ2: 迷路探索
    print("\n🎯 Stage02: 迷路探索")
    if initialize_stage("stage02"):
        # 右手法アルゴリズム
        while not is_game_finished():
            info = see()
            
            if info['surroundings']['right'] != "wall":
                turn_right()
                move()
            elif info['surroundings']['front'] != "wall":
                move()
            else:
                turn_left()
    
    # 最終進捗確認
    print("\n📊 学習セッション完了")
    show_progress_summary()
    
    recommendations = get_learning_recommendations()
    if recommendations:
        print("\n💡 次回への推奨事項:")
        for rec in recommendations:
            print(f"  {rec}")

if __name__ == "__main__":
    learning_session()
```

この進捗管理システムにより、教師は学生の学習状況を詳細に把握し、個別化された指導を提供できます。また、学生自身も自分の成長を可視化して、モチベーション向上につなげることができます。