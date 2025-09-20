"""
YAMLステージローダーシステム
StageLoaderクラスの実装
"""

import os
import yaml
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from . import (
    Position, Direction, Enemy, Item, Board, Stage,
    EnemyType, ItemType
)


class StageValidationError(Exception):
    """ステージバリデーションエラー"""
    pass


class StageLoader:
    """YAMLステージファイルローダー"""
    
    def __init__(self, stages_directory: str = "stages"):
        self.stages_directory = Path(stages_directory)
        self._required_fields = {
            "id", "title", "description", "board", "player", "goal"
        }
        self._board_required_fields = {"size", "grid"}
        self._player_required_fields = {"start", "direction"}
    
    def load_stage(self, stage_id: str) -> Stage:
        """指定されたステージIDのステージを読み込み"""
        stage_file = self.stages_directory / f"{stage_id}.yml"
        
        if not stage_file.exists():
            raise FileNotFoundError(f"ステージファイルが見つかりません: {stage_file}")
        
        try:
            with open(stage_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise StageValidationError(f"YAMLパースエラー: {e}")
        
        # ステージデータの検証
        self.validate_stage(data, stage_id)
        
        # ステージオブジェクトの構築
        return self._build_stage(data)
    
    def validate_stage(self, stage_data: Dict[str, Any], stage_id: str) -> None:
        """ステージデータの妥当性を検証"""
        if not isinstance(stage_data, dict):
            raise StageValidationError("ステージデータは辞書形式である必要があります")
        
        # 必須フィールドの存在チェック
        missing_fields = self._required_fields - set(stage_data.keys())
        if missing_fields:
            raise StageValidationError(f"必須フィールドが不足しています: {missing_fields}")
        
        # IDの整合性チェック
        if stage_data["id"] != stage_id:
            raise StageValidationError(f"ステージIDが一致しません: {stage_data['id']} != {stage_id}")
        
        # ボードデータの検証
        self._validate_board(stage_data["board"])
        
        # プレイヤーデータの検証
        self._validate_player(stage_data["player"])
        
        # ゴールの検証
        self._validate_goal(stage_data["goal"])
        
        # 敵データの検証（オプション）
        if "enemies" in stage_data:
            self._validate_enemies(stage_data["enemies"])
        
        # アイテムデータの検証（オプション）
        if "items" in stage_data:
            self._validate_items(stage_data["items"])
        
        # 制約の検証（オプション）
        if "constraints" in stage_data:
            self._validate_constraints(stage_data["constraints"])
    
    def _validate_board(self, board_data: Dict[str, Any]) -> None:
        """ボードデータの検証"""
        if not isinstance(board_data, dict):
            raise StageValidationError("boardデータは辞書形式である必要があります")
        
        missing_fields = self._board_required_fields - set(board_data.keys())
        if missing_fields:
            raise StageValidationError(f"boardに必須フィールドが不足しています: {missing_fields}")
        
        # サイズの検証
        size = board_data["size"]
        if not isinstance(size, list) or len(size) != 2:
            raise StageValidationError("board.sizeは [width, height] 形式である必要があります")
        
        width, height = size
        if not isinstance(width, int) or not isinstance(height, int):
            raise StageValidationError("board.sizeの値は整数である必要があります")
        
        if width <= 0 or height <= 0:
            raise StageValidationError("board.sizeの値は1以上である必要があります")
        
        # グリッドの検証
        grid = board_data["grid"]
        if not isinstance(grid, list):
            raise StageValidationError("board.gridはリスト形式である必要があります")
        
        if len(grid) != height:
            raise StageValidationError(f"grid行数がheight({height})と一致しません: {len(grid)}")
        
        for i, row in enumerate(grid):
            if not isinstance(row, str):
                raise StageValidationError(f"grid行{i}は文字列である必要があります")
            if len(row) != width:
                raise StageValidationError(f"grid行{i}の長さがwidth({width})と一致しません: {len(row)}")
    
    def _validate_player(self, player_data: Dict[str, Any]) -> None:
        """プレイヤーデータの検証"""
        if not isinstance(player_data, dict):
            raise StageValidationError("playerデータは辞書形式である必要があります")
        
        missing_fields = self._player_required_fields - set(player_data.keys())
        if missing_fields:
            raise StageValidationError(f"playerに必須フィールドが不足しています: {missing_fields}")
        
        # 開始位置の検証
        start = player_data["start"]
        if not isinstance(start, list) or len(start) != 2:
            raise StageValidationError("player.startは [x, y] 形式である必要があります")
        
        x, y = start
        if not isinstance(x, int) or not isinstance(y, int):
            raise StageValidationError("player.startの値は整数である必要があります")
        
        # 向きの検証
        direction = player_data["direction"]
        if direction not in ["N", "E", "S", "W"]:
            raise StageValidationError(f"player.directionは N/E/S/W のいずれかである必要があります: {direction}")
        
        # HP設定の検証（オプション）
        if "hp" in player_data:
            hp = player_data["hp"]
            if not isinstance(hp, int) or hp <= 0:
                raise StageValidationError("player.hpは正の整数である必要があります")
        
        # 最大HP設定の検証（オプション）
        if "max_hp" in player_data:
            max_hp = player_data["max_hp"]
            if not isinstance(max_hp, int) or max_hp <= 0:
                raise StageValidationError("player.max_hpは正の整数である必要があります")
        
        # HPと最大HPの関係性チェック
        if "hp" in player_data and "max_hp" in player_data:
            if player_data["hp"] > player_data["max_hp"]:
                raise StageValidationError("player.hpはplayer.max_hp以下である必要があります")
        
        # 攻撃力設定の検証（オプション）
        if "attack_power" in player_data:
            attack_power = player_data["attack_power"]
            if not isinstance(attack_power, int) or attack_power < 0:
                raise StageValidationError("player.attack_powerは0以上の整数である必要があります")
    
    def _validate_goal(self, goal_data: Dict[str, Any]) -> None:
        """ゴールデータの検証"""
        if not isinstance(goal_data, dict):
            raise StageValidationError("goalデータは辞書形式である必要があります")
        
        if "position" not in goal_data:
            raise StageValidationError("goalにpositionフィールドが必要です")
        
        position = goal_data["position"]
        if not isinstance(position, list) or len(position) != 2:
            raise StageValidationError("goal.positionは [x, y] 形式である必要があります")
        
        x, y = position
        if not isinstance(x, int) or not isinstance(y, int):
            raise StageValidationError("goal.positionの値は整数である必要があります")
    
    def _validate_enemies(self, enemies_data: List[Dict[str, Any]]) -> None:
        """敵データの検証"""
        if not isinstance(enemies_data, list):
            raise StageValidationError("enemiesはリスト形式である必要があります")
        
        for i, enemy_data in enumerate(enemies_data):
            if not isinstance(enemy_data, dict):
                raise StageValidationError(f"enemies[{i}]は辞書形式である必要があります")
            
            # 必須フィールドチェック
            required_fields = {"position", "type"}
            missing_fields = required_fields - set(enemy_data.keys())
            if missing_fields:
                raise StageValidationError(f"enemies[{i}]に必須フィールドが不足しています: {missing_fields}")
            
            # 位置の検証
            position = enemy_data["position"]
            if not isinstance(position, list) or len(position) != 2:
                raise StageValidationError(f"enemies[{i}].positionは [x, y] 形式である必要があります")
            
            # タイプの検証
            enemy_type = enemy_data["type"]
            valid_types = ["normal", "large_2x2", "large_3x3", "special_2x3", 
                          "goblin", "orc", "dragon", "boss"]
            if enemy_type not in valid_types:
                raise StageValidationError(f"enemies[{i}].typeは {valid_types} のいずれかである必要があります: {enemy_type}")
            
            # behavior フィールドの検証（オプション）
            if "behavior" in enemy_data:
                behavior = enemy_data["behavior"]
                valid_behaviors = ["guard", "patrol", "passive", "static", "stage11_special", "conditional"]
                if behavior not in valid_behaviors:
                    raise StageValidationError(f"enemies[{i}].behaviorは {valid_behaviors} のいずれかである必要があります: {behavior}")
            
            # v1.2.8 拡張属性の検証
            if enemy_type in ["large_2x2", "large_3x3"]:
                self._validate_large_enemy_attributes(enemy_data, i)
            elif enemy_type == "special_2x3":
                self._validate_special_enemy_attributes(enemy_data, i)
    
    def _validate_items(self, items_data: List[Dict[str, Any]]) -> None:
        """アイテムデータの検証"""
        if not isinstance(items_data, list):
            raise StageValidationError("itemsはリスト形式である必要があります")
        
        for i, item_data in enumerate(items_data):
            if not isinstance(item_data, dict):
                raise StageValidationError(f"items[{i}]は辞書形式である必要があります")
            
            # 必須フィールドチェック
            required_fields = {"position", "type", "name"}
            missing_fields = required_fields - set(item_data.keys())
            if missing_fields:
                raise StageValidationError(f"items[{i}]に必須フィールドが不足しています: {missing_fields}")
            
            # 位置の検証
            position = item_data["position"]
            if not isinstance(position, list) or len(position) != 2:
                raise StageValidationError(f"items[{i}].positionは [x, y] 形式である必要があります")
            
            # タイプの検証
            item_type = item_data["type"]
            valid_types = ["weapon", "armor", "key", "potion", "coin", "gem", "scroll"]
            if item_type not in valid_types:
                raise StageValidationError(f"items[{i}].typeは {valid_types} のいずれかである必要があります: {item_type}")
    
    def _validate_constraints(self, constraints_data: Dict[str, Any]) -> None:
        """制約データの検証"""
        if not isinstance(constraints_data, dict):
            raise StageValidationError("constraintsは辞書形式である必要があります")
        
        # max_turns の検証
        if "max_turns" in constraints_data:
            max_turns = constraints_data["max_turns"]
            if not isinstance(max_turns, int) or max_turns <= 0:
                raise StageValidationError("constraints.max_turnsは正の整数である必要があります")
        
        # allowed_apis の検証
        if "allowed_apis" in constraints_data:
            allowed_apis = constraints_data["allowed_apis"]
            if not isinstance(allowed_apis, list):
                raise StageValidationError("constraints.allowed_apisはリスト形式である必要があります")
            
            valid_apis = ["turn_left", "turn_right", "move", "attack", "pickup", "wait", "see", "get_stage_info"]
            for api in allowed_apis:
                if api not in valid_apis:
                    raise StageValidationError(f"無効なAPI: {api}. 有効なAPI: {valid_apis}")
    
    def _validate_large_enemy_attributes(self, enemy_data: Dict[str, Any], index: int) -> None:
        """大型敵の拡張属性検証"""
        # rage_threshold の検証（オプション）
        if "rage_threshold" in enemy_data:
            rage_threshold = enemy_data["rage_threshold"]
            if not isinstance(rage_threshold, (int, float)):
                raise StageValidationError(f"enemies[{index}].rage_thresholdは数値である必要があります")
            if not (0.0 <= rage_threshold <= 1.0):
                raise StageValidationError(f"enemies[{index}].rage_thresholdは0.0-1.0の範囲である必要があります: {rage_threshold}")
        
        # area_attack_range の検証（オプション）
        if "area_attack_range" in enemy_data:
            area_attack_range = enemy_data["area_attack_range"]
            if not isinstance(area_attack_range, int):
                raise StageValidationError(f"enemies[{index}].area_attack_rangeは整数である必要があります")
            if area_attack_range < 1:
                raise StageValidationError(f"enemies[{index}].area_attack_rangeは1以上である必要があります: {area_attack_range}")
        
        # HP関連の検証（オプション）
        if "hp" in enemy_data:
            hp = enemy_data["hp"]
            if not isinstance(hp, int) or hp <= 0:
                raise StageValidationError(f"enemies[{index}].hpは正の整数である必要があります: {hp}")
        
        if "max_hp" in enemy_data:
            max_hp = enemy_data["max_hp"]
            if not isinstance(max_hp, int) or max_hp <= 0:
                raise StageValidationError(f"enemies[{index}].max_hpは正の整数である必要があります: {max_hp}")
        
        # HPと最大HPの関係性チェック
        if "hp" in enemy_data and "max_hp" in enemy_data:
            if enemy_data["hp"] > enemy_data["max_hp"]:
                raise StageValidationError(f"enemies[{index}].hpはmax_hp以下である必要があります")
        
        # stage11_special フィールドの検証（オプション）
        if "stage11_special" in enemy_data:
            stage11_special = enemy_data["stage11_special"]
            if not isinstance(stage11_special, bool):
                raise StageValidationError(f"enemies[{index}].stage11_specialはbool型である必要があります")
    
    def _validate_special_enemy_attributes(self, enemy_data: Dict[str, Any], index: int) -> None:
        """特殊敵の拡張属性検証"""
        # special_conditions の検証（オプション）
        if "special_conditions" in enemy_data:
            conditions = enemy_data["special_conditions"]
            if not isinstance(conditions, dict):
                raise StageValidationError(f"enemies[{index}].special_conditionsは辞書形式である必要があります")
            
            # required_sequence の検証
            if "required_sequence" in conditions:
                sequence = conditions["required_sequence"]
                if not isinstance(sequence, list):
                    raise StageValidationError(f"enemies[{index}].special_conditions.required_sequenceはリスト形式である必要があります")
                
                valid_actions = ["move", "turn_left", "turn_right", "attack", "pickup", "wait", "see"]
                for j, action in enumerate(sequence):
                    if action not in valid_actions:
                        raise StageValidationError(f"enemies[{index}].special_conditions.required_sequence[{j}]は有効なアクション({valid_actions})である必要があります: {action}")
        
        # HP関連の検証（特殊敵は通常高HP）
        if "hp" in enemy_data:
            hp = enemy_data["hp"]
            if not isinstance(hp, int) or hp <= 0:
                raise StageValidationError(f"enemies[{index}].hpは正の整数である必要があります: {hp}")
        
        if "max_hp" in enemy_data:
            max_hp = enemy_data["max_hp"]
            if not isinstance(max_hp, int) or max_hp <= 0:
                raise StageValidationError(f"enemies[{index}].max_hpは正の整数である必要があります: {max_hp}")
        
        # 攻撃力の検証（特殊敵は通常高攻撃力）
        if "attack_power" in enemy_data:
            attack_power = enemy_data["attack_power"]
            if not isinstance(attack_power, int) or attack_power < 0:
                raise StageValidationError(f"enemies[{index}].attack_powerは0以上の整数である必要があります: {attack_power}")
    
    def _build_stage(self, data: Dict[str, Any]) -> Stage:
        """検証済みデータからStageオブジェクトを構築"""
        # ボード情報の抽出
        board_data = data["board"]
        width, height = board_data["size"]
        grid = board_data["grid"]
        
        # グリッドからポジション情報を抽出
        walls = []
        forbidden_cells = []
        
        # レジェンド定義（デフォルト）
        legend = board_data.get("legend", {
            "#": "wall",
            ".": "empty",
            "P": "player",
            "G": "goal",
            "X": "forbidden"
        })
        
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                pos = Position(x, y)
                if cell == "#" or (cell in legend and legend[cell] == "wall"):
                    walls.append(pos)
                elif cell == "X" or (cell in legend and legend[cell] == "forbidden"):
                    forbidden_cells.append(pos)
        
        # ボード作成
        board = Board(width, height, walls, forbidden_cells)
        
        # プレイヤー情報の抽出
        player_data = data["player"]
        player_start = Position(*player_data["start"])
        
        # 文字列から Direction への変換
        direction_map = {"N": Direction.NORTH, "E": Direction.EAST, "S": Direction.SOUTH, "W": Direction.WEST}
        player_direction = direction_map[player_data["direction"]]
        
        # プレイヤーのステータス情報の抽出（オプション）
        player_hp = player_data.get("hp")
        player_max_hp = player_data.get("max_hp")
        player_attack_power = player_data.get("attack_power")
        
        # ゴール情報の抽出
        goal_data = data["goal"]
        goal_position = Position(*goal_data["position"])
        
        # 敵情報の抽出
        enemies = []
        if "enemies" in data:
            for enemy_data in data["enemies"]:
                enemies.append(enemy_data)  # 辞書のまま保持（後でEnemyオブジェクトに変換）
        
        # アイテム情報の抽出
        items = []
        if "items" in data:
            for item_data in data["items"]:
                items.append(item_data)  # 辞書のまま保持（後でItemオブジェクトに変換）
        
        # 制約の抽出
        constraints = data.get("constraints", {})
        allowed_apis = constraints.get("allowed_apis", ["turn_left", "turn_right", "move"])
        max_turns = constraints.get("max_turns", 100)

        # 勝利条件の抽出
        victory_conditions = data.get("victory_conditions", [])

        # Stageオブジェクトの作成
        return Stage(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            board_size=(width, height),
            player_start=player_start,
            player_direction=player_direction,
            player_hp=player_hp,
            player_max_hp=player_max_hp,
            player_attack_power=player_attack_power,
            enemies=enemies,
            items=items,
            walls=walls,
            forbidden_cells=forbidden_cells,
            goal_position=goal_position,
            allowed_apis=allowed_apis,
            constraints=constraints,
            victory_conditions=victory_conditions
        )
    
    def get_available_stages(self) -> List[str]:
        """利用可能なステージIDのリストを取得"""
        if not self.stages_directory.exists():
            return []
        
        stage_files = list(self.stages_directory.glob("*.yml"))
        return [f.stem for f in stage_files]
    
    def create_stage_template(self, stage_id: str, output_path: Optional[str] = None) -> str:
        """ステージテンプレートを作成"""
        template = {
            "id": stage_id,
            "title": f"ステージ{stage_id}",
            "description": "新しいステージの説明",
            "board": {
                "size": [5, 5],
                "grid": [
                    ".....",
                    ".....",
                    "..#..",
                    ".....",
                    "....."
                ],
                "legend": {
                    "#": "wall",
                    ".": "empty",
                    "P": "player",
                    "G": "goal",
                    "X": "forbidden"
                }
            },
            "player": {
                "start": [0, 0],
                "direction": "N"
            },
            "goal": {
                "position": [4, 4]
            },
            "enemies": [
                # 通常敵の例
                {
                    "id": "normal_enemy",
                    "type": "normal",
                    "position": [2, 2],
                    "direction": "N",
                    "hp": 50,
                    "attack_power": 20
                },
                # 大型敵の例（コメントアウト）
                # {
                #     "id": "large_guardian",
                #     "type": "large_2x2",
                #     "position": [1, 1],
                #     "direction": "E",
                #     "hp": 150,
                #     "max_hp": 150,
                #     "attack_power": 30,
                #     "rage_threshold": 0.5,
                #     "area_attack_range": 2
                # },
                # 特殊敵の例（コメントアウト）
                # {
                #     "id": "conditional_boss",
                #     "type": "special_2x3",
                #     "position": [3, 3],
                #     "direction": "S",
                #     "hp": 10000,
                #     "max_hp": 10000,
                #     "attack_power": 10000,
                #     "special_conditions": {
                #         "required_sequence": ["move", "move", "attack"]
                #     }
                # }
            ],
            "items": [],
            "constraints": {
                "max_turns": 50,
                "allowed_apis": ["turn_left", "turn_right", "move"]
            }
        }
        
        # 出力パスの決定
        if output_path is None:
            output_path = self.stages_directory / f"{stage_id}.yml"
        else:
            output_path = Path(output_path)
        
        # ディレクトリが存在しない場合は作成
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # YAMLファイルに書き出し
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(template, f, default_flow_style=False, allow_unicode=True, indent=2)
        
        return str(output_path)


# エクスポート用
__all__ = ["StageLoader", "StageValidationError"]