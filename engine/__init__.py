"""
Python初学者向けローグライク演習フレームワーク
ゲームエンジン - コアデータモデル定義
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class Direction(Enum):
    """プレイヤーと敵の向き"""
    NORTH = "N"  # 北（上）
    EAST = "E"   # 東（右）
    SOUTH = "S"  # 南（下）
    WEST = "W"   # 西（左）
    
    def turn_left(self):
        """左に90度回転"""
        turns = {
            Direction.NORTH: Direction.WEST,
            Direction.WEST: Direction.SOUTH,
            Direction.SOUTH: Direction.EAST,
            Direction.EAST: Direction.NORTH
        }
        return turns[self]
    
    def turn_right(self):
        """右に90度回転"""
        turns = {
            Direction.NORTH: Direction.EAST,
            Direction.EAST: Direction.SOUTH,
            Direction.SOUTH: Direction.WEST,
            Direction.WEST: Direction.NORTH
        }
        return turns[self]
    
    def get_offset(self):
        """向きに対応する座標オフセット(x, y)を取得"""
        offsets = {
            Direction.NORTH: (0, -1),  # 上
            Direction.EAST: (1, 0),    # 右
            Direction.SOUTH: (0, 1),   # 下
            Direction.WEST: (-1, 0)    # 左
        }
        return offsets[self]

class GameStatus(Enum):
    """ゲーム状態"""
    PLAYING = "playing"        # ゲーム中
    WON = "won"               # 勝利
    FAILED = "failed"         # 失敗
    TIMEOUT = "timeout"       # タイムアウト
    ERROR = "error"           # エラー発生

class ItemType(Enum):
    """アイテムの種類"""
    WEAPON = "weapon"         # 武器
    ARMOR = "armor"           # 防具
    KEY = "key"              # 鍵
    POTION = "potion"        # ポーション

class EnemyType(Enum):
    """敵の種類"""
    NORMAL = "normal"         # 通常敵
    LARGE_2X2 = "large_2x2"  # 大型敵 2x2
    LARGE_3X3 = "large_3x3"  # 大型敵 3x3
    SPECIAL_2X3 = "special_2x3"  # 特殊敵 2x3
    # v1.2.6: 攻撃システム統合 - 新敵タイプ
    GOBLIN = "goblin"         # ゴブリン（基本攻撃敵）
    ORC = "orc"               # オーク（中級攻撃敵）
    DRAGON = "dragon"         # ドラゴン（高級攻撃敵）
    BOSS = "boss"             # ボス（最高級敵）

class ExecutionMode(Enum):
    """実行モード"""
    PAUSED = "paused"         # 一時停止
    STEPPING = "stepping"     # ステップ実行
    STEP_EXECUTING = "step_executing"  # 🆕 v1.2.1: ステップ実行中（単一アクション実行状態）
    CONTINUOUS = "continuous" # 連続実行
    PAUSE_PENDING = "pause_pending"    # 🆕 v1.2.1: 一時停止待機（次アクション境界で停止予定）
    COMPLETED = "completed"   # 実行完了
    RESET = "reset"          # 🆕 v1.2.1: リセット処理中
    ERROR = "error"          # 🆕 v1.2.1: エラー状態

class TurnPhase(Enum):
    """ターンフェーズ - v1.2.6攻撃システム統合"""
    PLAYER = "player"         # プレイヤーターン
    ENEMY = "enemy"           # 敵ターン

@dataclass(frozen=True)
class Position:
    """座標位置"""
    x: int
    y: int
    
    def __post_init__(self):
        """バリデーション"""
        if not isinstance(self.x, int) or not isinstance(self.y, int):
            raise ValueError("座標は整数である必要があります")
    
    def move(self, direction):
        """指定した方向に1マス移動した新しい位置を返す"""
        dx, dy = direction.get_offset()
        return Position(self.x + dx, self.y + dy)
    
    def distance_to(self, other):
        """他の位置との距離を計算"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

@dataclass
class Character:
    """キャラクター（プレイヤー・敵共通）"""
    position: Position
    direction: Direction
    hp: int = 100
    max_hp: int = 100
    attack_power: int = 30
    
    def __post_init__(self):
        """バリデーション"""
        if self.hp < 0:
            raise ValueError("HPは0以上である必要があります")
        if self.max_hp <= 0:
            raise ValueError("最大HPは1以上である必要があります")
        if self.attack_power < 0:
            raise ValueError("攻撃力は0以上である必要があります")
    
    def is_alive(self):
        """生存判定"""
        return self.hp > 0
    
    def take_damage(self, damage):
        """ダメージを受ける。実際に受けたダメージ量を返す"""
        if damage < 0:
            return 0
        actual_damage = min(damage, self.hp)
        self.hp -= actual_damage
        return actual_damage
    
    def heal(self, amount):
        """回復する。実際に回復した量を返す"""
        if amount < 0:
            return 0
        actual_heal = min(amount, self.max_hp - self.hp)
        self.hp += actual_heal
        return actual_heal

@dataclass
class Enemy(Character):
    """敵キャラクター"""
    enemy_type: EnemyType = EnemyType.NORMAL
    behavior_pattern: str = "static"
    is_angry: bool = False
    vision_range: int = 3  # 視野範囲（マス数）
    vision_angle: int = 90  # 視野角度（度）前方90度
    alerted: bool = False  # プレイヤーを発見したかどうか
    patrol_path: List[Position] = None  # 巡回パス
    current_patrol_index: int = 0  # 現在の巡回インデックス
    alert_cooldown: int = 0  # 警戒状態のクールダウン（ターン数）
    last_seen_player: Position = None  # 最後にプレイヤーを見た位置
    
    def __post_init__(self):
        super().__post_init__()
        if self.patrol_path is None:
            self.patrol_path = []
    
    def get_size(self):
        """敵のサイズを取得 (width, height)"""
        sizes = {
            EnemyType.NORMAL: (1, 1),
            EnemyType.LARGE_2X2: (2, 2),
            EnemyType.LARGE_3X3: (3, 3),
            EnemyType.SPECIAL_2X3: (2, 3),
            # v1.2.6: 攻撃システム統合 - 新敵タイプサイズ
            EnemyType.GOBLIN: (1, 1),
            EnemyType.ORC: (1, 1),
            EnemyType.DRAGON: (2, 2),  # ドラゴンは大型
            EnemyType.BOSS: (2, 2)     # ボスも大型
        }
        return sizes[self.enemy_type]
    
    def get_occupied_positions(self):
        """敵が占有する全ての座標を取得"""
        width, height = self.get_size()
        positions = []
        for dx in range(width):
            for dy in range(height):
                positions.append(Position(self.position.x + dx, self.position.y + dy))
        return positions
    
    def can_see_player(self, player_position: Position, board=None) -> bool:
        """プレイヤーを視野範囲内で視認できるかどうか（get_vision_cellsと完全に同じ基準を使用）"""
        vision_cells = self.get_vision_cells(board=board)
        result = player_position in vision_cells
        return result
    
    def get_vision_cells(self, board=None) -> List[Position]:
        """視野範囲内のセル一覧を取得（壁による視線遮蔽を考慮）"""
        cells = []
        
        for distance in range(1, self.vision_range + 1):
            for offset in range(-distance, distance + 1):
                if self.direction == Direction.NORTH:
                    target_pos = Position(self.position.x + offset, self.position.y - distance)
                elif self.direction == Direction.SOUTH:
                    target_pos = Position(self.position.x + offset, self.position.y + distance)
                elif self.direction == Direction.EAST:
                    target_pos = Position(self.position.x + distance, self.position.y + offset)
                elif self.direction == Direction.WEST:
                    target_pos = Position(self.position.x - distance, self.position.y + offset)
                else:
                    continue
                
                # 視野角度内かチェック
                if abs(offset) <= distance:  # 90度視野角の近似
                    # 壁による視線遮蔽をチェック
                    has_los = board is None or self._has_line_of_sight(target_pos, board)
                    if has_los:
                        cells.append(target_pos)
        
        return cells
    
    def _has_line_of_sight(self, target_pos: Position, board) -> bool:
        """指定位置への視線が遮られていないかチェック"""
        # 簡易的な視線判定：直線上に壁があるかチェック
        start_x, start_y = self.position.x, self.position.y
        end_x, end_y = target_pos.x, target_pos.y
        
        # ブレゼンハムアルゴリズムの簡易版で視線をトレース
        dx = abs(end_x - start_x)
        dy = abs(end_y - start_y)
        
        x, y = start_x, start_y
        step_x = 1 if start_x < end_x else -1
        step_y = 1 if start_y < end_y else -1
        
        if dx > dy:
            err = dx / 2.0
            while x != end_x:
                x += step_x
                err -= dy
                if err < 0:
                    y += step_y
                    err += dx
                # 中間点が壁かチェック（目標地点は除く）
                if x != end_x or y != end_y:
                    check_pos = Position(x, y)
                    if check_pos in board.walls:
                        return False
        else:
            err = dy / 2.0
            while y != end_y:
                y += step_y
                err -= dx
                if err < 0:
                    x += step_x
                    err += dy
                # 中間点が壁かチェック（目標地点は除く）
                if x != end_x or y != end_y:
                    check_pos = Position(x, y)
                    if check_pos in board.walls:
                        return False
        
        return True
    
    def get_next_patrol_position(self) -> Optional[Position]:
        """次の巡回位置を取得"""
        if not self.patrol_path:
            return None
        
        # 次のインデックスを計算（現在位置の次の位置を目標とする）
        next_index = (self.current_patrol_index + 1) % len(self.patrol_path)
        return self.patrol_path[next_index]
    
    def advance_patrol(self) -> None:
        """巡回インデックスを進める"""
        if self.patrol_path:
            self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_path)

@dataclass
class Item:
    """アイテム"""
    position: Position
    item_type: ItemType
    name: str
    effect: Dict[str, int]
    auto_equip: bool = True
    
    def __post_init__(self):
        """バリデーション"""
        if not self.name:
            raise ValueError("アイテム名は必須です")
        if not isinstance(self.effect, dict):
            raise ValueError("効果は辞書形式である必要があります")

@dataclass
class Board:
    """ゲームボード"""
    width: int
    height: int
    walls: List[Position]
    forbidden_cells: List[Position]
    
    def __post_init__(self):
        """バリデーション"""
        if self.width <= 0 or self.height <= 0:
            raise ValueError("ボードサイズは1以上である必要があります")
    
    def is_valid_position(self, pos):
        """有効な座標かチェック"""
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height
    
    def is_wall(self, pos):
        """壁かどうかチェック"""
        return pos in self.walls
    
    def is_forbidden(self, pos):
        """移動不可マスかどうかチェック"""
        return pos in self.forbidden_cells
    
    def is_passable(self, pos):
        """通行可能かチェック"""
        return (self.is_valid_position(pos) and 
                not self.is_wall(pos) and 
                not self.is_forbidden(pos))

@dataclass
class GameState:
    """ゲームの現在状態"""
    player: Character
    enemies: List[Enemy]
    items: List[Item]
    board: Board
    turn_count: int = 0
    max_turns: int = 100
    status: GameStatus = GameStatus.PLAYING
    goal_position: Optional[Position] = None
    
    def __post_init__(self):
        """バリデーション"""
        if self.max_turns <= 0:
            raise ValueError("最大ターン数は1以上である必要があります")
        if self.turn_count < 0:
            raise ValueError("ターン数は0以上である必要があります")
    
    def is_game_over(self):
        """ゲーム終了判定"""
        return self.status != GameStatus.PLAYING
    
    def increment_turn(self):
        """ターン数を増加"""
        self.turn_count += 1
        if self.turn_count >= self.max_turns:
            self.status = GameStatus.TIMEOUT
    
    def check_goal_reached(self):
        """ゴール到達判定"""
        if self.goal_position is None:
            return False
        return self.player.position == self.goal_position
    
    def check_victory_conditions(self):
        """勝利条件チェック - v1.2.6攻撃システム統合"""
        # ゴール位置に到達していない場合は勝利ではない
        if not self.check_goal_reached():
            return False
        
        # 敵が残っている場合は勝利ではない（stage04-06の要件）
        alive_enemies = [enemy for enemy in self.enemies if enemy.is_alive()]
        if alive_enemies:
            return False
        
        return True
    
    def get_item_at(self, pos):
        """指定座標のアイテムを取得"""
        for item in self.items:
            if item.position == pos:
                return item
        return None
    
    def get_enemy_at(self, pos):
        """指定座標の敵を取得"""
        for enemy in self.enemies:
            if pos in enemy.get_occupied_positions():
                return enemy
        return None

@dataclass
class Stage:
    """ステージ定義"""
    id: str
    title: str
    description: str
    board_size: Tuple[int, int]
    player_start: Position
    player_direction: Direction
    enemies: List[Dict[str, Any]]
    items: List[Dict[str, Any]]
    walls: List[Position]
    forbidden_cells: List[Position]
    goal_position: Optional[Position]
    allowed_apis: List[str]
    constraints: Dict[str, Any]
    player_hp: Optional[int] = None  # ステージ固有のプレイヤーHP（Noneの場合はデフォルト値を使用）
    player_max_hp: Optional[int] = None  # ステージ固有の最大HP
    player_attack_power: Optional[int] = None  # ステージ固有の攻撃力
    
    def __post_init__(self):
        """バリデーション"""
        if not self.id:
            raise ValueError("ステージIDは必須です")
        if not self.title:
            raise ValueError("ステージタイトルは必須です")
        if self.board_size[0] <= 0 or self.board_size[1] <= 0:
            raise ValueError("ボードサイズは1以上である必要があります")

@dataclass
class LogEntry:
    """ログエントリ"""
    timestamp: datetime
    student_id: str
    stage_id: str
    action: str
    result: str
    turn_number: int
    game_state_hash: str
    
    def __post_init__(self):
        """バリデーション"""
        if not self.student_id:
            raise ValueError("学生IDは必須です")
        if not self.stage_id:
            raise ValueError("ステージIDは必須です")
        if not self.action:
            raise ValueError("アクションは必須です")
    
    def to_dict(self):
        """辞書形式に変換"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "student_id": self.student_id,
            "stage_id": self.stage_id,
            "action": self.action,
            "result": self.result,
            "turn_number": self.turn_number,
            "game_state_hash": self.game_state_hash
        }

@dataclass
class ExecutionState:
    """実行状態の管理"""
    mode: ExecutionMode = ExecutionMode.PAUSED
    sleep_interval: float = 1.0  # デフォルト1秒
    is_running: bool = False
    step_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    
    # 🆕 v1.2.1: 拡張フィールド
    current_action: Optional[str] = None          # 現在実行中のアクション名
    pause_pending: bool = False                   # 一時停止要求フラグ
    last_transition: Optional[datetime] = None    # 最終状態遷移時刻
    error_state: Optional[str] = None             # エラー状態詳細
    
    def __post_init__(self):
        """バリデーション"""
        if self.sleep_interval < 0:
            raise ValueError("sleep間隔は0以上である必要があります")
        if self.step_count < 0:
            raise ValueError("ステップ数は0以上である必要があります")
    
    def __str__(self):
        """文字列表現"""
        return f"ExecutionState(mode={self.mode.value}, steps={self.step_count}, running={self.is_running})"

# 🆕 v1.2.1: 新規データモデルクラス

@dataclass
class ExecutionStateDetail:
    """詳細な実行状態情報"""
    mode: ExecutionMode
    step_count: int
    is_running: bool
    current_action: Optional[str] = None
    pause_pending: bool = False
    last_transition: Optional[datetime] = None
    error_state: Optional[str] = None
    
    def __post_init__(self):
        """バリデーション"""
        if self.step_count < 0:
            raise ValueError("ステップ数は0以上である必要があります")

@dataclass
class PauseRequest:
    """一時停止要求の管理"""
    requested_at: datetime
    requester: str  # 'user' | 'system'
    target_boundary: str  # 'next_action' | 'immediate'
    fulfilled: bool = False
    
    def __post_init__(self):
        """バリデーション"""
        if self.requester not in ['user', 'system']:
            raise ValueError("requesterは'user'または'system'である必要があります")
        if self.target_boundary not in ['next_action', 'immediate']:
            raise ValueError("target_boundaryは'next_action'または'immediate'である必要があります")

@dataclass
class ResetResult:
    """リセット操作の結果"""
    success: bool
    reset_timestamp: datetime
    components_reset: List[str]
    errors: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """バリデーション"""
        if not isinstance(self.components_reset, list):
            raise ValueError("components_resetはリスト型である必要があります")

@dataclass
class StepResult:
    """ステップ実行の結果"""
    success: bool
    action_executed: str
    new_state: ExecutionMode
    execution_time_ms: float
    actions_executed: int = 0  # 🆕 v1.2.1: 実行されたアクション数
    error_message: Optional[str] = None  # 🆕 v1.2.1: エラーメッセージ
    
    def __post_init__(self):
        """バリデーション"""
        if self.execution_time_ms < 0:
            raise ValueError("実行時間は0以上である必要があります")

@dataclass
class ActionBoundary:
    """アクション境界の定義"""
    boundary_type: str  # 'api_call' | 'loop_iteration'
    action_name: str
    timestamp: datetime
    sequence_number: int
    
    def __post_init__(self):
        """バリデーション"""
        if self.boundary_type not in ['api_call', 'loop_iteration']:
            raise ValueError("boundary_typeは'api_call'または'loop_iteration'である必要があります")
        if self.sequence_number < 1:
            raise ValueError("sequence_numberは1以上である必要があります")

# ExecutionControlError例外クラス階層
class ExecutionControlError(Exception):
    """実行制御関連のエラー基底クラス"""
    pass

class StepExecutionError(ExecutionControlError):
    """ステップ実行エラー"""
    pass

class StepPauseException(ExecutionControlError):
    """ステップ実行一時停止例外"""
    pass
    
class PauseControlError(ExecutionControlError):
    """一時停止制御エラー"""
    pass
    
class ResetOperationError(ExecutionControlError):
    """リセット操作エラー"""
    pass

class StateTransitionError(ExecutionControlError):
    """状態遷移エラー"""
    pass

@dataclass  
class ActionHistoryEntry:
    """アクション履歴エントリ"""
    sequence: int
    action_name: str
    timestamp: datetime
    execution_result: Optional[Any] = None
    
    def __post_init__(self):
        """バリデーション"""
        if self.sequence < 1:
            raise ValueError("シーケンス番号は1以上である必要があります")
        if not self.action_name:
            raise ValueError("アクション名は必須です")
    
    def __str__(self):
        """文字列表現"""
        return f"{self.sequence}: {self.action_name}()"

# 🚀 v1.2.5: 7段階速度制御専用データモデル

@dataclass
class EnhancedExecutionState(ExecutionState):
    """7段階速度制御拡張実行状態"""
    # 7段階速度制御情報
    current_speed_multiplier: int = 2  # デフォルトをx2に統一
    speed_change_count: int = 0
    ultra_high_speed_active: bool = False
    precision_tolerance_ms: float = 5.0
    
    # 精度監視情報
    last_precision_check: Optional[datetime] = None
    precision_failure_count: int = 0
    
    def __post_init__(self):
        """拡張バリデーション"""
        super().__post_init__()
        valid_multipliers = [1, 2, 3, 4, 5, 10, 50]
        if self.current_speed_multiplier not in valid_multipliers:
            raise ValueError(f"速度倍率は{valid_multipliers}のいずれかである必要があります")
        if self.precision_tolerance_ms <= 0:
            raise ValueError("精度許容値は0より大きい必要があります")


@dataclass
class SpeedControlMetrics:
    """速度制御メトリクス"""
    session_id: str
    total_speed_changes: int = 0
    speed_distribution: Dict[int, float] = field(default_factory=dict)  # {multiplier: usage_time}
    ultra_speed_precision_stats: Dict[str, float] = field(default_factory=dict)
    average_speed_multiplier: float = 1.0
    max_speed_used: int = 1
    realtime_changes_count: int = 0
    
    def __post_init__(self):
        """バリデーション"""
        if not self.session_id:
            raise ValueError("セッションIDは必須です")
        if self.total_speed_changes < 0:
            raise ValueError("速度変更回数は0以上である必要があります")


@dataclass
class UltraSpeedPrecisionResult:
    """超高速精度測定結果"""
    target_interval_ms: float
    actual_interval_ms: float
    deviation_ms: float
    within_tolerance: bool
    measurement_timestamp: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """バリデーション"""
        if self.target_interval_ms <= 0:
            raise ValueError("目標間隔は0より大きい必要があります")
        if self.actual_interval_ms < 0:
            raise ValueError("実際の間隔は0以上である必要があります")


@dataclass
class SpeedTransitionEvent:
    """速度切替イベント"""
    from_multiplier: int
    to_multiplier: int
    transition_time_ms: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    is_realtime: bool = False
    
    def __post_init__(self):
        """バリデーション"""
        valid_multipliers = [1, 2, 3, 4, 5, 10, 50]
        if self.from_multiplier not in valid_multipliers:
            raise ValueError(f"変更前倍率は{valid_multipliers}のいずれかである必要があります")
        if self.to_multiplier not in valid_multipliers:
            raise ValueError(f"変更後倍率は{valid_multipliers}のいずれかである必要があります")
        if self.transition_time_ms < 0:
            raise ValueError("切替時間は0以上である必要があります")


# v1.2.5: 7段階速度制御専用例外クラス

class Enhanced7StageSpeedControlError(ExecutionControlError):
    """7段階速度制御関連エラー基底クラス"""
    pass


class InvalidSpeedMultiplierError(Enhanced7StageSpeedControlError):
    """無効な速度倍率エラー"""
    pass


class UltraHighSpeedError(Enhanced7StageSpeedControlError):
    """超高速実行エラー"""
    pass


class HighPrecisionTimingError(Enhanced7StageSpeedControlError):
    """高精度タイミングエラー"""
    pass


class RealTimeSpeedChangeError(Enhanced7StageSpeedControlError):
    """リアルタイム速度変更エラー"""
    pass


class ExecutionSyncError(Enhanced7StageSpeedControlError):
    """実行同期エラー"""
    pass


class SpeedDegradationError(Enhanced7StageSpeedControlError):
    """速度性能低下エラー"""
    pass


__all__ = [
    "Direction", "GameStatus", "ItemType", "EnemyType", "ExecutionMode",
    "Position", "Character", "Enemy", "Item", "Board",
    "GameState", "Stage", "LogEntry", "ExecutionState", "ActionHistoryEntry",
    # 🆕 v1.2.1: 新規データモデル
    "ExecutionStateDetail", "PauseRequest", "ResetResult", "StepResult", "ActionBoundary",
    # 🆕 v1.2.1: 例外クラス
    "ExecutionControlError", "StepExecutionError", "PauseControlError", 
    "ResetOperationError", "StateTransitionError",
    # 🚀 v1.2.5: 7段階速度制御データモデル
    "EnhancedExecutionState", "SpeedControlMetrics", "UltraSpeedPrecisionResult", 
    "SpeedTransitionEvent",
    # 🚀 v1.2.5: 7段階速度制御例外クラス
    "Enhanced7StageSpeedControlError", "InvalidSpeedMultiplierError", "UltraHighSpeedError",
    "HighPrecisionTimingError", "RealTimeSpeedChangeError", "ExecutionSyncError",
    "SpeedDegradationError"
]