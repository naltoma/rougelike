"""Data models for stage generation system"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Tuple, Dict, Set, Any


class StageType(Enum):
    """Enumeration of supported stage types"""
    MOVE = "move"        # Basic movement (stages 01-03 equivalent)
    ATTACK = "attack"    # Combat scenarios (stages 04-06 equivalent)
    PICKUP = "pickup"    # Item collection (stages 07-09 equivalent)
    PATROL = "patrol"    # Moving enemies (stage 10 equivalent)
    SPECIAL = "special"  # Large enemies, complex conditions (stages 11-13 equivalent)


@dataclass
class GenerationParameters:
    """Parameters for stage generation"""
    stage_type: StageType
    seed: int
    output_path: Optional[str] = None
    validate: bool = False

    def get_filename(self) -> str:
        """Generate filename: generated_[type]_[seed].yml"""
        return f"generated_{self.stage_type.value}_{self.seed}.yml"

    def get_stage_id(self) -> str:
        """Generate stage ID: generated_[type]_[seed]"""
        return f"generated_{self.stage_type.value}_{self.seed}"


@dataclass
class BoardConfiguration:
    """Board configuration for a stage"""
    size: Tuple[int, int]  # [width, height]
    grid: List[str]        # List of row strings
    legend: Dict[str, str] # Character to meaning mapping


@dataclass
class PlayerConfiguration:
    """Player configuration for a stage"""
    start: Tuple[int, int]     # [x, y] starting position
    direction: str             # N, S, E, W
    hp: int = 100             # Default HP
    max_hp: int = 100         # Default max HP
    attack_power: int = 30    # Default attack power


@dataclass
class GoalConfiguration:
    """Goal configuration for a stage"""
    position: Tuple[int, int]  # [x, y] goal position


@dataclass
class EnemyConfiguration:
    """Enemy configuration for a stage"""
    id: str
    type: str              # normal, large_2x2, large_3x3, special_2x3
    position: Tuple[int, int]
    direction: str
    hp: int
    max_hp: int
    attack_power: int
    behavior: str = "normal"
    vision_range: Optional[int] = None

    # Optional advanced features
    rage_threshold: Optional[float] = None
    area_attack_range: Optional[int] = None
    stage11_special: Optional[bool] = None
    special_conditions: Optional[Dict[str, Any]] = None
    patrol_path: Optional[List[Tuple[int, int]]] = None  # Patrol path for movement


@dataclass
class ItemConfiguration:
    """Item configuration for a stage"""
    id: str
    type: str
    position: Tuple[int, int]
    value: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ConstraintConfiguration:
    """Constraint configuration for a stage"""
    max_turns: int
    allowed_apis: List[str]


@dataclass
class StageConfiguration:
    """Complete YAML stage structure matching existing format"""
    id: str
    title: str
    description: str
    board: BoardConfiguration
    player: PlayerConfiguration
    goal: GoalConfiguration
    enemies: List[EnemyConfiguration]
    items: List[ItemConfiguration]
    constraints: ConstraintConfiguration

    # Optional advanced features (for special stages)
    victory_conditions: Optional[List[Dict[str, Any]]] = None
    learning_objectives: Optional[List[str]] = None
    hints: Optional[List[str]] = None
    error_handling: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StageConfiguration':
        """Create StageConfiguration from dictionary data"""
        # Parse board
        board = BoardConfiguration(
            size=tuple(data['board']['size']),
            grid=data['board']['grid'],
            legend=data['board']['legend']
        )

        # Parse player
        player = PlayerConfiguration(
            start=tuple(data['player']['start']),
            direction=data['player']['direction'],
            hp=data['player'].get('hp', 100),
            max_hp=data['player'].get('max_hp', 100),
            attack_power=data['player'].get('attack_power', 30)
        )

        # Parse goal
        goal = GoalConfiguration(
            position=tuple(data['goal']['position'])
        )

        # Parse enemies
        enemies = []
        for enemy_data in data.get('enemies', []):
            # Parse patrol_path if present
            patrol_path = None
            if 'patrol_path' in enemy_data:
                patrol_path = [tuple(pos) for pos in enemy_data['patrol_path']]

            enemy = EnemyConfiguration(
                id=enemy_data['id'],
                type=enemy_data['type'],
                position=tuple(enemy_data['position']),
                direction=enemy_data['direction'],
                hp=enemy_data['hp'],
                max_hp=enemy_data['max_hp'],
                attack_power=enemy_data['attack_power'],
                behavior=enemy_data.get('behavior', 'normal'),
                vision_range=enemy_data.get('vision_range'),
                rage_threshold=enemy_data.get('rage_threshold'),
                area_attack_range=enemy_data.get('area_attack_range'),
                stage11_special=enemy_data.get('stage11_special'),
                special_conditions=enemy_data.get('special_conditions'),
                patrol_path=patrol_path
            )
            enemies.append(enemy)

        # Parse items
        items = []
        for item_data in data.get('items', []):
            item = ItemConfiguration(
                id=item_data['id'],
                type=item_data['type'],
                position=tuple(item_data['position']),
                value=item_data.get('value'),
                name=item_data.get('name'),
                description=item_data.get('description')
            )
            items.append(item)

        # Parse constraints
        constraints = ConstraintConfiguration(
            max_turns=data['constraints']['max_turns'],
            allowed_apis=data['constraints']['allowed_apis']
        )

        return cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            board=board,
            player=player,
            goal=goal,
            enemies=enemies,
            items=items,
            constraints=constraints,
            victory_conditions=data.get('victory_conditions'),
            learning_objectives=data.get('learning_objectives'),
            hints=data.get('hints'),
            error_handling=data.get('error_handling')
        )


# Custom exceptions for error handling
class InvalidSeedError(ValueError):
    """Raised when seed value is out of acceptable range"""
    pass


class UnsupportedStageTypeError(ValueError):
    """Raised when stage type is unknown or invalid"""
    pass


class GenerationTimeoutError(Exception):
    """Raised when generation takes too long"""
    pass


class InvalidBoardConfigurationError(ValueError):
    """Raised when generated board violates constraints"""
    pass