# Research: A*アルゴリズムとゲームエンジン動作差異修正

## 敵移動ロジックの差異分析

### Decision: マルチレイヤー行動同期・状態検証システム実装
A*パスファインディングアルゴリズムと実際のゲームエンジンの行動パターンに5つの主要な差異を特定し、統合的な同期システムで解決する。

### Rationale: 根本的な実行順序・状態同期・敵AI行動パターンの差異
1. **敵移動ロジックパターン**: A*は即座の方向転換+移動を許可、ゲームエンジンは「回転→移動」制約を強制
2. **ステップ同期問題**: 視覚システムタイミング、アクション順序、警戒状態管理の違い
3. **状態非同期原因**: パトロールインデックス計算、アイテム処理、移動判定ロジックの差異
4. **ログ・比較ギャップ**: ターンカウント、敵位置追跡、アイテム状態管理の不一致
5. **敵行動ロジック統合**: 戦闘解決、視野範囲、追跡vs.パトロールモードの差異

### Alternatives considered:
- **A*修正案**: 既存ステージ検証機能への影響大
- **ゲームエンジン修正案**: 教育フレームワークの学習進行に影響
- **行動ブリッジレイヤー案**: 新たなバグ導入リスク、根本的タイミング問題未解決

## 技術実装アプローチ

### Phase 1: 状態同期フレームワーク
```python
class StateValidator:
    def __init__(self, a_star_pathfinder, game_engine):
        self.pathfinder = a_star_pathfinder
        self.engine = game_engine
        self.sync_points = []

    def validate_turn_by_turn(self, solution_path):
        # 各アクションを両システムで同時実行
        # 各同期ポイントで状態比較
        for step, action in enumerate(solution_path):
            a_state = self.pathfinder.apply_single_action(action)
            g_state = self.engine.execute_single_action(action)
            self.compare_states(a_state, g_state, step)
```

### Phase 2: 敵行動統一システム
```python
class UnifiedEnemyAI:
    def __init__(self):
        self.rotation_system = GradualRotationController()
        self.vision_system = DirectionalVisionController()
        self.patrol_system = PatrolIndexController()

    def sync_behavior_patterns(self, a_star_enemy, game_enemy):
        # 両システムが同一のAIロジックを使用
        return self.apply_unified_behavior(a_star_enemy, game_enemy)
```

### Phase 3: ログ・デバッグフレームワーク
```python
class StateComparisonLogger:
    def log_divergence(self, step, a_state, g_state, action):
        divergence_report = {
            "step": step,
            "action": action.value,
            "player_pos_diff": a_state.player_pos != g_state.player.position,
            "enemy_diffs": self.compare_enemies(a_state.enemies, g_state.enemies),
            "item_diffs": self.compare_items(a_state.collected_items, g_state.items)
        }
        self.generate_debug_report(divergence_report)
```

### Phase 4: ターンベース状態マシン
```python
class TurnBasedStateMachine:
    """両システムが同一のターンベース実行に従うことを保証"""
    def execute_turn(self, player_action):
        # 1. アクション検証
        # 2. プレイヤーアクション実行
        # 3. 敵状態更新
        # 4. 勝利条件チェック
        # 5. 状態同期
        return self.synchronized_turn_result()
```

## 設計制約への対応

### main_*.py保護機能
- ユーザー演習ファイルの完全性保持
- 検証ロジックは独立モジュールで実装

### 設定一元化戦略
- `src/stage_validator/config.py`で敵移動ロジック設定統一
- 重複設定による動作不整合を防止

### 既存API互換性
- 現在の`validate_stage.py`インターフェース維持
- 新機能は拡張オプションとして提供