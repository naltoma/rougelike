"""Core YAML management utilities for stage configuration files"""
import yaml
from pathlib import Path
from typing import Dict, Any, Union
import sys

# Add stage_generator to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from stage_generator.data_models import StageConfiguration, BoardConfiguration, PlayerConfiguration, GoalConfiguration, EnemyConfiguration, ItemConfiguration, ConstraintConfiguration


def load_stage_config(filepath: str) -> Dict[str, Any]:
    """Load and parse stage YAML file into dictionary"""
    file_path = Path(filepath)

    if not file_path.exists():
        raise FileNotFoundError(f"Stage file not found: {filepath}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValueError("YAML file is empty or invalid")

        return data

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format: {e}")


def save_stage_config(config: Union[StageConfiguration, Dict[str, Any]], filepath: str) -> bool:
    """Save stage configuration to YAML file"""
    try:
        file_path = Path(filepath)

        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert StageConfiguration to dict if needed
        if isinstance(config, StageConfiguration):
            data = _stage_config_to_dict(config)
        else:
            data = config

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

        return True

    except Exception as e:
        print(f"Error saving stage configuration: {e}")
        return False


def validate_schema(config: Dict[str, Any]) -> bool:
    """Validate YAML structure matches expected schema"""
    try:
        # Required top-level keys
        required_keys = ['id', 'title', 'description', 'board', 'player', 'goal', 'enemies', 'items', 'constraints']

        for key in required_keys:
            if key not in config:
                return False

        # Validate board structure
        board = config['board']
        board_required = ['size', 'grid', 'legend']
        if not all(key in board for key in board_required):
            return False

        if not isinstance(board['size'], list) or len(board['size']) != 2:
            return False

        if not isinstance(board['grid'], list):
            return False

        # Validate player structure
        player = config['player']
        player_required = ['start', 'direction']
        if not all(key in player for key in player_required):
            return False

        if not isinstance(player['start'], list) or len(player['start']) != 2:
            return False

        # Validate goal structure
        goal = config['goal']
        if 'position' not in goal:
            return False

        if not isinstance(goal['position'], list) or len(goal['position']) != 2:
            return False

        # Validate constraints
        constraints = config['constraints']
        constraints_required = ['max_turns', 'allowed_apis']
        if not all(key in constraints for key in constraints_required):
            return False

        if not isinstance(constraints['allowed_apis'], list):
            return False

        # Validate enemies and items are lists
        if not isinstance(config['enemies'], list):
            return False

        if not isinstance(config['items'], list):
            return False

        return True

    except Exception:
        return False


def _stage_config_to_dict(config: StageConfiguration) -> Dict[str, Any]:
    """Convert StageConfiguration object to dictionary for YAML serialization"""
    result = {
        'id': config.id,
        'title': config.title,
        'description': config.description,
        'board': {
            'size': list(config.board.size),
            'grid': config.board.grid,
            'legend': config.board.legend
        },
        'player': {
            'start': list(config.player.start),
            'direction': config.player.direction,
            'hp': config.player.hp,
            'max_hp': config.player.max_hp
        },
        'goal': {
            'position': list(config.goal.position)
        },
        'enemies': [_enemy_to_dict(enemy) for enemy in config.enemies],
        'items': [_item_to_dict(item) for item in config.items],
        'constraints': {
            'max_turns': config.constraints.max_turns,
            'allowed_apis': config.constraints.allowed_apis
        }
    }

    # Add optional player fields if different from defaults
    if config.player.attack_power != 30:
        result['player']['attack_power'] = config.player.attack_power

    # Add optional advanced features if present
    if config.victory_conditions:
        result['victory_conditions'] = config.victory_conditions
    if config.learning_objectives:
        result['learning_objectives'] = config.learning_objectives
    if config.hints:
        result['hints'] = config.hints
    if config.error_handling:
        result['error_handling'] = config.error_handling

    return result


def _enemy_to_dict(enemy: EnemyConfiguration) -> Dict[str, Any]:
    """Convert EnemyConfiguration to dictionary"""
    result = {
        'id': enemy.id,
        'type': enemy.type,
        'position': list(enemy.position),
        'direction': enemy.direction,
        'hp': enemy.hp,
        'max_hp': enemy.max_hp,
        'attack_power': enemy.attack_power
    }

    if enemy.behavior != "normal":
        result['behavior'] = enemy.behavior

    # Add optional advanced features if present
    if enemy.rage_threshold is not None:
        result['rage_threshold'] = enemy.rage_threshold
    if enemy.area_attack_range is not None:
        result['area_attack_range'] = enemy.area_attack_range
    if enemy.stage11_special is not None:
        result['stage11_special'] = enemy.stage11_special
    if enemy.special_conditions is not None:
        result['special_conditions'] = enemy.special_conditions
    if enemy.patrol_path is not None:
        result['patrol_path'] = [list(pos) for pos in enemy.patrol_path]
    if enemy.vision_range is not None:
        result['vision_range'] = enemy.vision_range

    return result


def _item_to_dict(item: ItemConfiguration) -> Dict[str, Any]:
    """Convert ItemConfiguration to dictionary"""
    result = {
        'id': item.id,
        'type': item.type,
        'position': list(item.position)
    }

    # Add optional fields if they exist
    if hasattr(item, 'name') and item.name is not None:
        result['name'] = item.name
    if hasattr(item, 'description') and item.description is not None:
        result['description'] = item.description
    if hasattr(item, 'value') and item.value is not None:
        result['value'] = item.value

    return result