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
            valid_types = ["normal", "large_2x2", "large_3x3", "special_2x3"]
            if enemy_type not in valid_types:
                raise StageValidationError(f"enemies[{i}].typeは {valid_types} のいずれかである必要があります: {enemy_type}")
    
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
            valid_types = ["weapon", "armor", "key", "potion"]
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
            
            valid_apis = ["turn_left", "turn_right", "move", "attack", "pickup", "see"]
            for api in allowed_apis:
                if api not in valid_apis:
                    raise StageValidationError(f"無効なAPI: {api}. 有効なAPI: {valid_apis}")
    
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
        
        # Stageオブジェクトの作成
        return Stage(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            board_size=(width, height),
            player_start=player_start,
            player_direction=player_direction,
            enemies=enemies,
            items=items,
            walls=walls,
            forbidden_cells=forbidden_cells,
            goal_position=goal_position,
            allowed_apis=allowed_apis,
            constraints=constraints
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
            "enemies": [],
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