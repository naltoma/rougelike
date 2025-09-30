# Data Model: A*アルゴリズムとゲームエンジン動作差異修正

## Core Entities

### ExecutionLog (実行ログ)
プレイヤーと敵の各ステップでの位置・向き情報を記録

**Fields:**
- `step_number`: int - ステップ番号（0から開始）
- `engine_type`: str - 実行エンジン識別子（"astar" | "game_engine"）
- `timestamp`: datetime - 実行タイムスタンプ
- `player_position`: tuple[int, int] - プレイヤー座標(x, y)
- `player_direction`: str - プレイヤー向き("up"|"down"|"left"|"right")
- `enemy_states`: list[EnemyState] - 全敵の状態リスト
- `action_taken`: str - 実行されたアクション("move"|"turn_left"|"turn_right"|"attack"|"pickup"|"wait")
- `game_over`: bool - ゲーム終了フラグ
- `victory`: bool - 勝利フラグ

**Validation Rules:**
- step_numberは連続した非負整数
- engine_typeは指定値のみ許可
- player_positionは有効なマップ座標内
- enemy_statesは空リスト可（敵なしステージ）

### EnemyState (敵状態)
個別敵エンティティの状態情報

**Fields:**
- `enemy_id`: str - 敵識別子（マップ上の一意ID）
- `position`: tuple[int, int] - 敵座標(x, y)
- `direction`: str - 敵の向き("up"|"down"|"left"|"right")
- `patrol_index`: int - パトロールインデックス（patrol型のみ）
- `alert_state`: str - 警戒状態("patrol"|"alert"|"chase")
- `vision_range`: int - 視野範囲
- `health`: int - 敵HP（attack可能敵のみ）
- `enemy_type`: str - 敵タイプ("patrol"|"static"|"large")

**State Transitions:**
- patrol → alert: プレイヤー発見時
- alert → chase: プレイヤー追跡開始時
- chase → patrol: プレイヤー見失い後のクールダウン完了時

### SolutionPath (解法例)
A*アルゴリズムが生成するプレイヤー行動シーケンス

**Fields:**
- `stage_file`: str - 対象ステージファイルパス
- `action_sequence`: list[str] - アクション列（順序付き）
- `generation_timestamp`: datetime - 生成タイムスタンプ
- `expected_success`: bool - A*による成功予測
- `actual_success`: bool - ゲームエンジンでの実際の結果
- `total_steps`: int - 総ステップ数
- `failure_step`: int | None - 失敗ステップ（成功時はNone）

**Validation Rules:**
- action_sequenceの各要素は有効なアクション名
- total_stepsはaction_sequenceの長さと一致
- failure_stepは0以上total_steps未満（設定時）

### StateDifference (差異レポート)
両エンジン間の実行結果比較結果

**Fields:**
- `comparison_id`: str - 比較セッション識別子
- `step_number`: int - 差異発生ステップ
- `difference_type`: str - 差異種別("player_position"|"enemy_position"|"game_state"|"action_result")
- `astar_value`: any - A*アルゴリズム側の値
- `engine_value`: any - ゲームエンジン側の値
- `severity`: str - 重要度("critical"|"major"|"minor")
- `description`: str - 差異の詳細説明

**Relationships:**
- StateDifference → ExecutionLog (多対多): 複数の実行ログから差異を検出
- SolutionPath → ExecutionLog (一対多): 解法例の実行が複数ログを生成

### ValidationConfig (検証設定)
システム動作設定の一元管理

**Fields:**
- `enemy_rotation_delay`: int - 敵回転に要するターン数
- `vision_check_timing`: str - 視覚チェックタイミング("before_action"|"after_action")
- `patrol_advancement_rule`: str - パトロール進行ルール("immediate"|"delayed")
- `action_execution_order`: list[str] - アクション実行順序定義
- `log_detail_level`: str - ログ詳細レベル("minimal"|"detailed"|"debug")

**Validation Rules:**
- 全フィールド必須、デフォルト値を持つ
- enemy_rotation_delayは1以上
- 列挙型フィールドは指定値のみ許可

## Data Flow

1. **解法生成**: A*アルゴリズム → SolutionPath生成
2. **両エンジン実行**: SolutionPath → ExecutionLog生成（A*用・ゲームエンジン用）
3. **差異検出**: ExecutionLog比較 → StateDifference生成
4. **修正適用**: StateDifference分析 → ValidationConfig調整