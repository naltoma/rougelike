# Quickstart: A*アルゴリズムとゲームエンジン動作差異修正

## 目的
このガイドでは、A*アルゴリズムとゲームエンジン間の動作差異を検出・修正する機能の使用方法を説明します。

## 前提条件
- Python 3.11+がインストール済み
- 既存のローグライクフレームワークが動作可能
- `stages/generated_patrol_2025.yml`が存在

## クイックスタート手順

### 1. 現状の問題確認
```bash
# 既存のA*解法例を生成
python scripts/validate_stage.py --file stages/generated_patrol_2025.yml --solution

# ゲームエンジンで解法例を実行（失敗することを確認）
python main_hoge2.py
```

### 2. 状態差異検証の実行
```bash
# 両エンジンの実行ログを生成・比較
python src/stage_validator/state_validator.py \
    --stage stages/generated_patrol_2025.yml \
    --solution-file solution.txt \
    --compare-engines \
    --detailed-log
```

期待される出力:
```
=== State Validation Report ===
Comparing A* algorithm vs Game Engine execution

Step 5: CRITICAL difference detected
- Type: enemy_position
- A* enemy position: (3, 4)
- Game engine enemy position: (3, 5)
- Cause: Different patrol advancement timing

Step 8: MAJOR difference detected
- Type: player_position
- A* player position: (5, 3)
- Game engine player position: GAME_OVER
- Cause: Enemy rotation logic mismatch

Total differences: 12 critical, 3 major, 1 minor
```

### 3. 差異修正の適用
```bash
# 統一敵AIロジックを適用
python src/stage_validator/fix_astar_behavior.py \
    --config-update \
    --sync-enemy-movement \
    --fix-rotation-timing
```

### 4. 修正後の検証
```bash
# 修正後のA*で解法例を再生成
python scripts/validate_stage.py --file stages/generated_patrol_2025.yml --solution --fixed-ai

# 新しい解法例でゲームエンジン実行
# （今度は成功するはず）
python main_hoge2.py
```

## 主要機能

### 状態比較ログの詳細表示
```bash
python src/stage_validator/state_validator.py \
    --stage stages/generated_patrol_2025.yml \
    --verbose \
    --export-logs comparison_report.json
```

### 特定ステップのデバッグ
```bash
# ステップ8での状態を詳細分析
python src/stage_validator/debug_step.py \
    --step 8 \
    --show-enemy-states \
    --show-vision-cones \
    --show-patrol-paths
```

### カスタム解法例の検証
```bash
# 手動で作成した解法例をテスト
echo "move,turn_left,move,attack" > custom_solution.txt
python src/stage_validator/state_validator.py \
    --stage stages/generated_patrol_2025.yml \
    --solution-file custom_solution.txt \
    --compare-engines
```

## 成功判定基準

この機能が正常に動作する場合:

1. **差異検出**: A*とゲームエンジンの状態差異が正確に検出される
2. **解法一致**: 修正後のA*解法例がゲームエンジンで成功する
3. **ログ生成**: 各ステップの詳細状態が記録される
4. **設定統一**: 敵移動ロジックが両エンジンで一致する

## トラブルシューティング

### よくある問題

**問題**: A*解法例が生成されない
```bash
# ステージファイルの有効性確認
python scripts/validate_stage.py --file stages/generated_patrol_2025.yml --check-only
```

**問題**: 両エンジンで異なるエラーが発生
```bash
# デバッグモードで実行
python src/stage_validator/state_validator.py \
    --stage stages/generated_patrol_2025.yml \
    --debug-mode \
    --step-by-step
```

**問題**: 修正後も差異が残る
```bash
# 設定ファイルをリセット
python src/stage_validator/reset_config.py --restore-defaults
```

## 実行結果例

### 修正前（失敗ケース）
```
Step 1: Player (2,3) facing right, Enemy (4,5) patrolling
Step 2: Player moves to (3,3), Enemy rotates left
Step 3: Player moves to (4,3), Enemy moves to (4,4)
Step 5: GAME OVER - Player attacked by enemy
Result: FAILED
```

### 修正後（成功ケース）
```
Step 1: Player (2,3) facing right, Enemy (4,5) patrolling
Step 2: Player moves to (3,3), Enemy continues patrol
Step 3: Player moves to (4,3), Enemy rotates (takes full turn)
Step 5: Player reaches goal at (6,3)
Result: SUCCESS
```

これで、A*アルゴリズムとゲームエンジンの動作が完全に同期し、生成された解法例が確実にゲーム内で実行可能になります。