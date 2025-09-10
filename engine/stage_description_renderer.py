"""
ステージ説明表示システム
StageDescriptionRenderer - ステージ情報の学習者向け表示機能
"""

from typing import Optional, Dict, Any, List
import logging
from .stage_loader import StageLoader

logger = logging.getLogger(__name__)


class StageDescriptionRenderer:
    """ステージ説明表示クラス
    
    StageLoaderと統合し、学習者にとって理解しやすい形で
    ステージ説明とクリア条件を表示する。
    """
    
    def __init__(self, stage_loader: StageLoader):
        """初期化
        
        Args:
            stage_loader: 既存のステージローダー
        """
        self.stage_loader = stage_loader
        self.max_width = 80  # 説明文の最大幅
        logger.debug("StageDescriptionRenderer初期化完了")
    
    def display_stage_conditions(self, stage_id: str, student_id: Optional[str] = None) -> str:
        """ステージクリア条件表示機能
        
        Args:
            stage_id: 表示対象のステージID
            student_id: 学生ID（オプション）
        
        Returns:
            str: フォーマット済みの説明文
        """
        if not stage_id:
            raise ValueError("stage_idは必須です")
        
        try:
            # ステージデータの読み込み
            stage = self.stage_loader.load_stage(stage_id)
            
            # 説明文のフォーマット
            formatted_description = self.format_description_text(stage)
            
            logger.info(f"ステージ説明表示: {stage_id}")
            return formatted_description
            
        except FileNotFoundError:
            # フォールバック表示
            logger.warning(f"ステージファイルが見つかりません: {stage_id}")
            return self.display_fallback_message(stage_id)
        except Exception as e:
            logger.error(f"ステージ説明表示エラー: {stage_id} - {e}")
            return self.display_fallback_message(stage_id)
    
    def format_description_text(self, stage) -> str:
        """説明文フォーマット機能
        
        Args:
            stage: Stageオブジェクト
        
        Returns:
            str: フォーマット済みの説明文
        """
        lines = []
        
        # ヘッダー
        lines.append("=" * self.max_width)
        lines.append(f"📚 ステージ情報: {stage.title} ({stage.id})")
        lines.append("=" * self.max_width)
        lines.append("")
        
        # 基本説明
        lines.append("📖 ステージ説明:")
        description_lines = self._wrap_text(stage.description, self.max_width - 4)
        for line in description_lines:
            lines.append(f"   {line}")
        lines.append("")
        
        # ボード情報
        lines.append("🎯 ボード情報:")
        board_width, board_height = stage.board_size
        lines.append(f"   サイズ: {board_width} x {board_height}")
        lines.append(f"   スタート位置: ({stage.player_start.x}, {stage.player_start.y})")
        lines.append(f"   ゴール位置: ({stage.goal_position.x}, {stage.goal_position.y})")
        lines.append("")
        
        # 制約情報
        lines.append("⚡ 制約条件:")
        max_turns = getattr(stage, 'constraints', {}).get('max_turns', 100)
        lines.append(f"   最大ターン数: {max_turns}")
        
        # 使用可能なAPI
        allowed_apis = stage.allowed_apis if hasattr(stage, 'allowed_apis') else ["turn_left", "turn_right", "move"]
        lines.append(f"   使用可能なAPI: {', '.join(allowed_apis)}")
        lines.append("")
        
        # 敵情報（存在する場合）
        if hasattr(stage, 'enemies') and stage.enemies:
            lines.append("⚔️ 敵情報:")
            for i, enemy in enumerate(stage.enemies):
                if isinstance(enemy, dict):
                    pos = enemy.get('position', [0, 0])
                    enemy_type = enemy.get('type', 'normal')
                    lines.append(f"   敵{i+1}: {enemy_type} at ({pos[0]}, {pos[1]})")
            lines.append("")
        
        # アイテム情報（存在する場合）
        if hasattr(stage, 'items') and stage.items:
            lines.append("🎁 アイテム情報:")
            for i, item in enumerate(stage.items):
                if isinstance(item, dict):
                    pos = item.get('position', [0, 0])
                    item_name = item.get('name', 'unknown')
                    item_type = item.get('type', 'unknown')
                    lines.append(f"   {item_name} ({item_type}) at ({pos[0]}, {pos[1]})")
            lines.append("")
        
        # クリア条件（ステージ固有）
        lines.append("🏆 クリア条件:")
        victory_conditions = self._get_stage_specific_victory_conditions(stage)
        for condition in victory_conditions:
            lines.append(f"   {condition}")
        if max_turns < 100:
            lines.append(f"   {max_turns}ターン以内でクリアする")
        lines.append("")
        
        # ヒント（ステージ固有）
        lines.append("💡 ヒント:")
        hints = self._get_stage_specific_hints(stage)
        for i, hint in enumerate(hints, 1):
            lines.append(f"   {i}. {hint}")
        lines.append("")
        lines.append("=" * self.max_width)
        
        return "\n".join(lines)
    
    def display_fallback_message(self, stage_id: str) -> str:
        """フォールバック表示機能
        
        Args:
            stage_id: ステージID
        
        Returns:
            str: フォールバック表示メッセージ
        """
        lines = []
        
        lines.append("=" * self.max_width)
        lines.append(f"📚 ステージ情報: {stage_id}")
        lines.append("=" * self.max_width)
        lines.append("")
        
        lines.append("⚠️ ステージ説明を読み込めませんでした")
        lines.append("")
        
        lines.append("📖 一般的な情報:")
        lines.append("   このステージは基本的なローグライク学習ステージです。")
        lines.append("   利用可能なAPI: turn_left(), turn_right(), move(), see()")
        lines.append("")
        
        lines.append("🎯 基本的な目標:")
        lines.append("   1. プレイヤーをゴール位置まで移動させる")
        lines.append("   2. 壁や障害物を避けて進む")
        lines.append("   3. 制限ターン数内でクリアする")
        lines.append("")
        
        lines.append("💡 学習のヒント:")
        lines.append("   1. まずは基本的な移動から始めましょう")
        lines.append("   2. 段階的にプログラムを作成していきましょう")
        lines.append("   3. エラーが出たら落ち着いてデバッグしましょう")
        lines.append("")
        
        lines.append("=" * self.max_width)
        
        logger.info(f"フォールバック表示: {stage_id}")
        return "\n".join(lines)
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """テキストを指定幅で折り返し
        
        Args:
            text: 折り返し対象のテキスト
            width: 折り返し幅
        
        Returns:
            List[str]: 折り返し後の行のリスト
        """
        if not text:
            return [""]
        
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            # 現在の行に単語を追加した場合の長さをチェック
            test_line = current_line + " " + word if current_line else word
            
            if len(test_line) <= width:
                current_line = test_line
            else:
                # 現在の行を確定し、新しい行を開始
                if current_line:
                    lines.append(current_line)
                current_line = word
                
                # 単語自体が制限幅を超える場合は強制的に分割
                while len(current_line) > width:
                    lines.append(current_line[:width])
                    current_line = current_line[width:]
        
        # 最後の行を追加
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [""]
    
    def _get_stage_specific_victory_conditions(self, stage) -> List[str]:
        """ステージ固有の勝利条件を取得
        
        Args:
            stage: Stageオブジェクト
        
        Returns:
            List[str]: 勝利条件のリスト
        """
        conditions = []
        
        # ステージ固有の勝利条件
        if stage.id == "stage04":
            conditions.append("敵を倒す（attack()で攻撃）")
            conditions.append("ゴール位置に到達する")
        elif hasattr(stage, 'enemies') and stage.enemies:
            # 敵がいるステージは一般的に敵を倒す必要がある
            conditions.append("すべての敵を倒す")
            conditions.append("ゴール位置に到達する")
        else:
            # 通常のステージは移動のみ
            conditions.append("ゴール位置に到達する")
        
        return conditions
    
    def _get_stage_specific_hints(self, stage) -> List[str]:
        """ステージ固有のヒントを取得
        
        Args:
            stage: Stageオブジェクト
        
        Returns:
            List[str]: ヒントのリスト
        """
        hints = []
        
        # ステージ固有のヒント
        if stage.id == "stage04":
            hints.append("attack()関数を使って正面の敵を攻撃できます")
            hints.append("敵を倒してからゴールに向かいましょう")
            hints.append("プランを立ててから実装してみてください")
        elif hasattr(stage, 'enemies') and stage.enemies:
            # 敵がいるステージのヒント
            hints.append("敵に注意して移動しましょう")
            hints.append("attack()で敵を倒すことができます")
            hints.append("プランを立ててから実装してみてください")
        else:
            # 通常のステージのヒント
            hints.append("まずは基本的な移動から始めましょう")
            hints.append("プランを立ててから実装してみてください")
            if "see" in getattr(stage, 'allowed_apis', []):
                hints.append("必要に応じてsee()でマップの状況を確認できます")
        
        return hints
    
    def get_stage_summary(self, stage_id: str) -> Dict[str, Any]:
        """ステージサマリー情報の取得
        
        Args:
            stage_id: ステージID
        
        Returns:
            Dict[str, Any]: ステージサマリー情報
        """
        try:
            stage = self.stage_loader.load_stage(stage_id)
            
            return {
                "stage_id": stage.id,
                "title": stage.title,
                "description": stage.description,
                "board_size": stage.board_size,
                "max_turns": getattr(stage, 'constraints', {}).get('max_turns', 100),
                "allowed_apis": stage.allowed_apis if hasattr(stage, 'allowed_apis') else [],
                "has_enemies": bool(getattr(stage, 'enemies', [])),
                "has_items": bool(getattr(stage, 'items', [])),
                "status": "loaded"
            }
            
        except Exception as e:
            logger.error(f"ステージサマリー取得エラー: {stage_id} - {e}")
            return {
                "stage_id": stage_id,
                "title": f"ステージ{stage_id}",
                "description": "説明を読み込めませんでした",
                "board_size": (0, 0),
                "max_turns": 100,
                "allowed_apis": ["turn_left", "turn_right", "move"],
                "has_enemies": False,
                "has_items": False,
                "status": "error"
            }