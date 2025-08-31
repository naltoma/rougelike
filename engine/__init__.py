"""
Python初学者向けローグライク演習フレームワーク
ゲームエンジン - コアデータモデル定義
"""

from enum import Enum
from dataclasses import dataclass
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
    attack_power: int = 10
    
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
    
    def get_size(self):
        """敵のサイズを取得 (width, height)"""
        sizes = {
            EnemyType.NORMAL: (1, 1),
            EnemyType.LARGE_2X2: (2, 2),
            EnemyType.LARGE_3X3: (3, 3),
            EnemyType.SPECIAL_2X3: (2, 3)
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

__all__ = [
    "Direction", "GameStatus", "ItemType", "EnemyType",
    "Position", "Character", "Enemy", "Item", "Board",
    "GameState", "Stage", "LogEntry"
]