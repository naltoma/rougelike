# Stage Validator Quick Start Guide - v1.2.12

**A*アルゴリズムとゲームエンジンの動作差異検出・修正システム**

## 🚀 クイックスタート

### 1. 基本的なステージ検証

```bash
# 基本的なステージ検証
python scripts/validate_stage.py --file stages/stage01.yml

# 詳細な分析結果を表示
python scripts/validate_stage.py --file stages/stage01.yml --detailed

# 解法コード例を生成
python scripts/validate_stage.py --file stages/stage01.yml --solution
```

### 2. **NEW v1.2.12**: エンジン比較機能

```bash
# A*アルゴリズム vs ゲームエンジンの動作比較
python scripts/validate_stage.py --file stages/stage01.yml --compare-engines

# 比較結果をJSON形式で出力
python scripts/validate_stage.py --file stages/stage01.yml --compare-engines --format json
```

### 3. プログラム例: Stage Validator API使用

```python
#!/usr/bin/env python3
"""
Stage Validator API使用例 - v1.2.12
"""
from src.stage_validator import StateValidator, create_mock_engine
from src.stage_validator.models import get_global_config

# 設定とエンジンのセットアップ
config = get_global_config()
astar_engine = create_mock_engine(config)
game_engine = create_mock_engine(config)

# StateValidator作成
validator = StateValidator(astar_engine, game_engine, config)

# エンジン初期化
astar_engine.reset_stage("stages/stage01.yml")
game_engine.reset_stage("stages/stage01.yml")

# 解法パスで比較実行
solution_path = ["move", "turn_right", "move", "move"]
differences = validator.validate_turn_by_turn(solution_path)

# 結果表示
print(f"検出された差異: {len(differences)}件")
for diff in differences[:3]:  # 最初の3件表示
    print(f"  - ステップ{diff.step_number}: {diff.description}")
```

### 4. 設定管理とプロファイル

```python
#!/usr/bin/env python3
"""
設定管理例 - v1.2.12
"""
from src.stage_validator.config_manager import create_config_manager

# 設定マネージャー作成
config_manager = create_config_manager()

# デバッグプロファイル作成
debug_config = config_manager.create_profile_from_template('debug', 'debug')
print("デバッグプロファイル作成完了")

# プロファイル一覧表示
profiles = config_manager.list_profiles()
print(f"利用可能プロファイル: {profiles}")

# 設定サマリー表示
print(config_manager.get_config_summary())
```

### 5. デバッグロギング

```python
#!/usr/bin/env python3
"""
デバッグロギング例 - v1.2.12
"""
from src.stage_validator import create_debug_logger
from src.stage_validator.models import get_global_config

# デバッグロガー作成
config = get_global_config()
debug_logger = create_debug_logger(config)

# 比較セッション開始
session_id = debug_logger.start_comparison_session(
    "stages/stage01.yml",
    ["move", "turn_right", "move"]
)

# セッション完了とレポート生成
session_data = debug_logger.complete_session(session_id)
print(debug_logger.generate_summary_report(session_id))
```

## 🎯 実践的な使用例

### シナリオ1: A*解法がゲームで動作しない問題の診断

```bash
# ステップ1: 基本検証
python scripts/validate_stage.py --file problem_stage.yml --detailed

# ステップ2: エンジン比較で差異検出
python scripts/validate_stage.py --file problem_stage.yml --compare-engines

# ステップ3: 解法コード生成で動作確認
python scripts/validate_stage.py --file problem_stage.yml --solution --compare-engines
```

### シナリオ2: 大規模ステージのパフォーマンス検証

```bash
# タイムアウト時間を延長して検証
python scripts/validate_stage.py --file large_stage.yml --timeout 300 --compare-engines

# 最大ノード数を制限
python scripts/validate_stage.py --file large_stage.yml --max-nodes 1M --compare-engines

# JSON出力でパフォーマンス詳細確認
python scripts/validate_stage.py --file large_stage.yml --format json --compare-engines
```

### シナリオ3: 敵行動の同期問題デバッグ

```python
#!/usr/bin/env python3
"""
敵行動同期デバッグ例
"""
from src.stage_validator import StateValidator, AStarEngine, GameEngineWrapper
from src.stage_validator.models import ValidationConfig

# 詳細ログ設定
config = ValidationConfig(log_detail_level="debug", enable_debug_file_logging=True)

# 実エンジンでの比較 (依存関係解決後)
# astar_engine = AStarEngine(config)
# game_engine = GameEngineWrapper(config)

# 現在はMockEngineで動作確認
from src.stage_validator import create_mock_engine
astar_engine = create_mock_engine(config)
game_engine = create_mock_engine(config)

validator = StateValidator(astar_engine, game_engine, config)

# 敵が多いステージで詳細比較
astar_engine.reset_stage("stages/enemy_heavy_stage.yml")
game_engine.reset_stage("stages/enemy_heavy_stage.yml")

# 敵の行動が重要なソリューション
solution_path = ["wait", "wait", "move", "turn_left", "move", "attack"] * 5
differences = validator.validate_turn_by_turn(solution_path)

# 敵関連の差異のみ抽出
enemy_diffs = [d for d in differences if 'enemy' in d.description.lower()]
print(f"敵行動関連の差異: {len(enemy_diffs)}件")

for diff in enemy_diffs:
    print(f"  {diff.difference_type.value}: {diff.description}")
```

## 📊 出力例

### 基本検証出力
```
✅ Stage stages/stage01.yml validation successful
   📊 Solution found: 12 steps
   📋 Required APIs: move, turn_left, turn_right, see
   ⏱️  Validation time: 0.23s
   🎯 Reachability: 100% (goal accessible)
```

### エンジン比較出力
```
============================================================
🔍 ENGINE COMPARISON RESULTS
============================================================
📊 Solution Steps: 12
📊 Total Differences: 3
📝 Note: Demo using mock engines - A* integration in development

⚠️  Found 3 differences between engines:
  1. Step 5 (ENEMY_POSITION): Enemy guard1: A*=(5, 6), Game=(6, 6)
  2. Step 8 (PLAYER_DIRECTION): Player direction: A*=left, Game=down
  3. Step 10 (ENEMY_STATE): Enemy patrol2: A*=patrol, Game=alert

💡 Recommendation: Check enemy behavior synchronization
   Use --detailed flag for more information
```

### JSON出力例
```json
{
  "success": true,
  "stage_file": "stages/stage01.yml",
  "solution_length": 12,
  "validation_time": 0.23,
  "engine_comparison": {
    "total_differences": 3,
    "differences": [
      {
        "step_number": 5,
        "difference_type": "ENEMY_POSITION",
        "severity": "MEDIUM",
        "description": "Enemy guard1: A*=(5, 6), Game=(6, 6)"
      }
    ]
  },
  "required_apis": ["move", "turn_left", "turn_right", "see"]
}
```

## 🔧 高度な設定

### カスタム設定プロファイル

```python
# パフォーマンス重視設定
config_manager.create_profile_from_template('fast', 'performance')

# デバッグ重視設定
config_manager.create_profile_from_template('verbose', 'debug')

# 厳密検証設定
config_manager.create_profile_from_template('strict', 'strict')

# カスタム設定
custom_config = ValidationConfig(
    max_solution_steps=2000,
    enemy_rotation_delay=3,
    vision_check_timing="before_action",
    position_tolerance=0.0
)
config_manager.save_config(custom_config, 'my_custom')
```

### パフォーマンス調整

```bash
# 軽量実行（最小ログ、メモリ最適化）
python scripts/validate_stage.py --file stage.yml --compare-engines --format json

# 詳細デバッグ（全ログ、ファイル出力）
python scripts/validate_stage.py --file stage.yml --compare-engines --detailed

# 大規模ステージ対応
python scripts/validate_stage.py --file huge_stage.yml --timeout 600 --max-nodes unlimited
```

## 🐛 トラブルシューティング

### よくある問題と解決方法

**1. "A* pathfinding modules not available" エラー**
```bash
# 現在はMockEngine動作。実際のA*統合は今後実装予定
python scripts/validate_stage.py --file stages/stage01.yml --compare-engines
# → MockEngineでの動作デモを実行
```

**2. パフォーマンスが遅い**
```python
# パフォーマンス設定を使用
from src.stage_validator.config_manager import create_config_manager
config_manager = create_config_manager()
perf_config = config_manager.create_profile_from_template('performance', 'performance')
config_manager.load_config('performance')
```

**3. メモリ不足**
```python
# メモリ最適化を有効化
config = ValidationConfig(
    memory_optimization_enabled=True,
    log_detail_level="minimal",
    enable_debug_file_logging=False
)
```

## 📈 次のステップ

1. **実際のA*統合**: AStarEngineの依存関係解決
2. **実ステージテスト**: 複数ステージでの動作確認
3. **継続的統合**: テストスイートへの組み込み
4. **パフォーマンス最適化**: 大規模ステージでの最適化

---

Stage Validator v1.2.12 - A*アルゴリズムとゲームエンジンの完璧な同期を実現