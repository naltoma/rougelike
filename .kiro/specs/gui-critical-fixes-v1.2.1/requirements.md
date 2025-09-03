# GUI Critical Fixes v1.2.1 - Requirements

## Overview

本要件書は、Python教育用ローグライクフレームワークのGUI実行制御システムにおける3つの重要なボタン機能不具合の修正要件を、EARS（Easy Approach to Requirements Syntax）形式で定義します。

## Functional Requirements

### FR-001: Step Button Single Action Execution
**Priority**: Critical  
**Category**: Core Functionality

#### EARS Format Requirements

**FR-001.1** - Step Button Single Action Response
- **WHEN** ユーザーがStep buttonを1回クリックした時
- **THEN** システムは1つのアクションのみを実行し、実行後に一時停止状態（PAUSED mode）に移行しなければならない
- **AND** 次のユーザー操作（Step, Continue, Pause, Reset, Stop）を受け付け可能状態になること

**FR-001.2** - Step Button Consistent Behavior  
- **WHILE** システムがPAUSED modeの時
- **WHEN** ユーザーがStep buttonを連続してクリックした時
- **THEN** 各クリックに対して必ず1つのアクションのみを実行すること
- **AND** 無限待機状態（infinite wait state）に入ってはならない
- **AND** 全アクション一括実行状態（full execution state）に入ってはならない

**FR-001.3** - Step Button State Recovery
- **IF** Step buttonクリック後にシステムが応答しない状態の時
- **THEN** 50ms以内に適切なエラーメッセージを表示し、PAUSED modeに復帰すること
- **AND** 次のユーザー操作を受け付け可能にすること

### FR-002: Pause Button Next Action Boundary Stop
**Priority**: High  
**Category**: Enhanced Functionality

#### EARS Format Requirements

**FR-002.1** - Pause During Continuous Execution
- **WHILE** システムがCONTINUOUS modeで実行中の時
- **WHEN** ユーザーがPause buttonをクリックした時
- **THEN** システムは現在実行中のアクションを完了し、次のアクション実行前に一時停止（PAUSED mode）しなければならない
- **AND** Step buttonと同等のタイミングでの一時停止を実現すること

**FR-002.2** - Pause Button Immediate Response Recognition
- **WHEN** ユーザーがPause buttonをクリックした時
- **THEN** システムは50ms以内にクリックを認識し、PAUSE_PENDING modeに移行すること
- **AND** 次のアクション境界での一時停止をスケジュールすること

**FR-002.3** - Pause Timing Accuracy
- **GIVEN** solve()関数内でPythonループ（for文、while文等）が実行中
- **WHEN** Pause buttonがクリックされた時
- **THEN** システムは正確にAPI呼び出し境界（turn_right(), move(), attack()等）で一時停止すること
- **AND** 中途半端な状態での停止を回避すること

### FR-003: Reset Button Complete System Reset
**Priority**: Critical  
**Category**: Core Functionality

#### EARS Format Requirements

**FR-003.1** - Complete System State Reset
- **WHEN** ユーザーがReset buttonをクリックした時
- **THEN** システムは以下の全ての状態を初期化すること：
  - ExecutionController状態のリセット（PAUSED modeに設定）
  - GameManager状態のリセット（プレイヤー位置、敵位置、アイテム状態の初期化）
  - SessionLog履歴のクリア
  - GUI表示の初期状態への復元

**FR-003.2** - Reset Button Immediate Response
- **WHEN** ユーザーがReset buttonをクリックした時
- **THEN** システムは100ms以内にリセット処理を開始すること
- **AND** リセット完了を視覚的にユーザーに通知すること

**FR-003.3** - Reset from Any State
- **GIVEN** システムが任意の実行状態（PAUSED, STEPPING, CONTINUOUS, COMPLETED, STOPPED）にある時
- **WHEN** Reset buttonがクリックされた時
- **THEN** 現在の実行を安全に中断し、完全な初期状態に復帰すること
- **AND** データ損失や状態不整合を発生させないこと

## Non-Functional Requirements

### NFR-001: Performance Requirements

#### NFR-001.1 - Button Response Time
- **REQUIREMENT**: 全てのボタン操作に対する応答時間は50ms以内であること
- **MEASUREMENT**: クリック検知からシステム応答開始までの時間
- **ACCEPTANCE**: 95%のケースで50ms以内の応答を実現すること

#### NFR-001.2 - Action Execution Time  
- **REQUIREMENT**: 単一アクション実行時間は100ms以内であること
- **MEASUREMENT**: API呼び出し開始から完了までの時間
- **ACCEPTANCE**: turn_right(), move(), attack()等の基本アクションが100ms以内で完了すること

#### NFR-001.3 - System Reset Time
- **REQUIREMENT**: Reset button実行による完全リセット時間は200ms以内であること
- **MEASUREMENT**: Reset buttonクリックから初期状態復帰完了までの時間
- **ACCEPTANCE**: 全状態のクリアと初期化が200ms以内で完了すること

### NFR-002: Reliability Requirements

#### NFR-002.1 - Button Operation Reliability
- **REQUIREMENT**: 100回連続操作での不具合発生率は1%未満であること
- **MEASUREMENT**: Step/Pause/Reset button各100回操作での異常動作回数
- **ACCEPTANCE**: 各ボタンで99%以上の正常動作を保証すること

#### NFR-002.2 - State Consistency Reliability
- **REQUIREMENT**: 任意のボタン操作シーケンスで状態不整合が発生しないこと
- **MEASUREMENT**: ランダムボタン操作1000回実行での状態検証
- **ACCEPTANCE**: 全ての操作シーケンスで期待される状態遷移を維持すること

### NFR-003: Usability Requirements

#### NFR-003.1 - Visual Feedback Consistency
- **REQUIREMENT**: 全てのボタン操作で適切な視覚的フィードバックを提供すること
- **MEASUREMENT**: ボタンクリック時のUI状態変化確認
- **ACCEPTANCE**: クリック、ホバー、無効状態での明確な視覚的差異を実現すること

#### NFR-003.2 - Error Message Clarity
- **REQUIREMENT**: ボタン操作エラー時に分かりやすい日本語エラーメッセージを表示すること
- **MEASUREMENT**: エラーメッセージの内容理解度テスト（初学者対象）
- **ACCEPTANCE**: Python初学者が内容を理解し、適切な対処を取れること

## Technical Requirements

### TR-001: ExecutionController Enhancement

#### TR-001.1 - Enhanced State Management
- **REQUIREMENT**: ExecutionMode enumにPAUSE_PENDINGとRESET状態を追加すること
- **SPECIFICATION**: 
  ```python
  class ExecutionMode(Enum):
      PAUSED = "paused"
      STEPPING = "stepping"
      CONTINUOUS = "continuous"
      PAUSE_PENDING = "pause_pending"  # 新規
      COMPLETED = "completed"  
      STOPPED = "stopped"
      RESET = "reset"  # 新規
  ```

#### TR-001.2 - Thread-Safe State Updates
- **REQUIREMENT**: 全ての状態更新操作はスレッドセーフであること
- **SPECIFICATION**: threading.Lockまたは同等の排他制御メカニズムを使用すること
- **ACCEPTANCE**: マルチスレッド環境での状態競合が発生しないこと

#### TR-001.3 - Action Tracking Enhancement  
- **REQUIREMENT**: ステップ実行での個別アクション追跡機能を実装すること
- **SPECIFICATION**: pending_action, action_completedフラグによる状態管理
- **ACCEPTANCE**: 各API呼び出しの開始・完了が正確に追跡されること

### TR-002: Wait Logic Redesign

#### TR-002.1 - Improved wait_for_action() Method
- **REQUIREMENT**: wait_for_action()メソッドを無限待機とフル実行の問題を解決するよう再実装すること
- **SPECIFICATION**:
  ```python
  def wait_for_action(self):
      if self.mode == ExecutionMode.STEPPING:
          if self.pending_action:
              self.pending_action = False
              return  # 1アクション実行許可
          else:
              self.mode = ExecutionMode.PAUSED
              while self.mode == ExecutionMode.PAUSED:
                  time.sleep(0.01)  # CPU使用率最適化
      elif self.mode == ExecutionMode.PAUSE_PENDING:
          self.mode = ExecutionMode.PAUSED
          while self.mode == ExecutionMode.PAUSED:
              time.sleep(0.01)
  ```

#### TR-002.2 - CPU Optimization
- **REQUIREMENT**: wait_for_action()でのCPU使用率を5%以下に抑制すること
- **SPECIFICATION**: 適切なsleep間隔（0.01秒推奨）とpygame.event.pump()呼び出し
- **ACCEPTANCE**: タスクマネージャーでのPython実行時CPU使用率測定

### TR-003: Reset System Implementation

#### TR-003.1 - ResetManager Class
- **REQUIREMENT**: 包括的なリセット機能を管理するResetManagerクラスを実装すること
- **SPECIFICATION**:
  ```python
  class ResetManager:
      def __init__(self, execution_controller, game_manager, session_logger, renderer):
          self.execution_controller = execution_controller
          self.game_manager = game_manager
          self.session_logger = session_logger
          self.renderer = renderer
      
      def full_reset(self):
          # ExecutionController, GameManager, SessionLogger, Renderer状態リセット
  ```

#### TR-003.2 - Memory Cleanup
- **REQUIREMENT**: リセット操作でメモリリークが発生しないこと
- **SPECIFICATION**: 適切なオブジェクト参照クリアとガベージコレクション
- **ACCEPTANCE**: リセット前後でメモリ使用量増加が5%以内であること

## Integration Requirements

### IR-001: GUI Event Integration

#### IR-001.1 - Event Processing Engine Integration
- **REQUIREMENT**: 既存EventProcessingEngineとの互換性を維持すること
- **SPECIFICATION**: button_pressed辞書への適切な状態反映
- **ACCEPTANCE**: マウスクリックとキーボードショートカット両方での動作保証

#### IR-001.2 - Pygame Event Loop Integration
- **REQUIREMENT**: main.pyのpygame event loopとの適切な連携を実現すること
- **SPECIFICATION**: pygame.event.get()での適切なイベント処理とUI更新
- **ACCEPTANCE**: GUI応答性の維持とフリーズ回避

### IR-002: Session Logging Integration

#### IR-002.1 - Enhanced Session Logging
- **REQUIREMENT**: ボタン操作を詳細にセッションログに記録すること
- **SPECIFICATION**: アクション種別、実行時間、結果状態のJSONL形式記録
- **ACCEPTANCE**: 学習分析用データとして活用可能な形式での記録

#### IR-002.2 - Reset Event Logging  
- **REQUIREMENT**: リセット操作を特別なイベントとしてログに記録すること
- **SPECIFICATION**: reset_event_timestamp, previous_state, reset_reasonの記録
- **ACCEPTANCE**: リセット頻度と学習パターンの分析に活用可能であること

## Acceptance Criteria

### AC-001: Step Button Verification

#### Test Case: Step Button Single Action
```python
# Given: ゲーム初期状態、ExecutionMode.PAUSED
# When: Step buttonを1回クリック
# Then: 
#   - 1つのアクションのみ実行される
#   - 実行後にExecutionMode.PAUSEDに戻る
#   - 次のボタン操作を受け付ける状態になる
#   - 無限待機状態に入らない
#   - 全アクション実行状態に入らない
```

#### Test Case: Step Button Multiple Clicks
```python  
# Given: ExecutionMode.PAUSED状態
# When: Step buttonを5回連続でクリック
# Then:
#   - 各クリックで1つずつアクションが実行される
#   - 合計5つのアクションが実行される
#   - 最終的にExecutionMode.PAUSEDで停止する
```

### AC-002: Pause Button Verification

#### Test Case: Pause During Continuous Execution
```python
# Given: solve()関数でループ実行中、ExecutionMode.CONTINUOUS
# When: 連続実行開始から2秒後にPause buttonをクリック
# Then:
#   - 現在実行中のアクションが完了する
#   - 次のアクション実行前にExecutionMode.PAUSEDになる
#   - Step buttonと同じタイミングで停止する
```

### AC-003: Reset Button Verification

#### Test Case: Complete System Reset
```python
# Given: ゲーム途中状態（プレイヤー移動済み、敵配置変更済み）
# When: Reset buttonをクリック
# Then:
#   - プレイヤー位置が初期位置に戻る
#   - 敵配置が初期状態に戻る
#   - SessionLogが空になる
#   - ExecutionMode.PAUSEDになる
#   - GUI表示が初期状態に戻る
```

## Verification Methods

### Manual Testing Protocol
1. **Step Button Test**: 10回連続クリックでの単一アクション実行確認
2. **Pause Button Test**: 連続実行中の5回一時停止操作確認  
3. **Reset Button Test**: 各ゲーム状態からのリセット動作確認
4. **Performance Test**: 各操作の応答時間測定（50ms, 100ms, 200ms基準）
5. **Reliability Test**: 100回連続操作での異常動作回数測定

### Automated Testing Framework
1. **Unit Tests**: ExecutionController状態遷移テスト
2. **Integration Tests**: GUI-ExecutionController連携テスト
3. **Performance Tests**: 応答時間・CPU使用率測定テスト
4. **Stress Tests**: 1000回連続操作耐久テスト

### User Acceptance Testing
1. **Python初学者テスト**: 実際の学習者による操作性確認
2. **インストラクターテスト**: 教育現場での実用性確認
3. **長時間使用テスト**: 30分連続使用での安定性確認

---

**Requirements Version**: 1.0  
**Last Updated**: 2025-09-02  
**Review Status**: Ready for Design Phase  
**Approval Required**: Design phase進行前に本要件書の承認が必要