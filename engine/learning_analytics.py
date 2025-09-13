"""
v1.2.8学習支援アナリティクスシステム
LearningAnalyticsクラスの実装
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from enum import Enum
import json

from .session_data_models import StudentLogEntry
from .game_state import SpecialErrorHandler


class LearningPhase(Enum):
    """学習段階列挙型"""
    EXPLORATION = "exploration"      # 探索段階
    UNDERSTANDING = "understanding"  # 理解段階
    MASTERY = "mastery"             # 習得段階
    CHALLENGE = "challenge"         # 挑戦段階


class DifficultyLevel(Enum):
    """難易度レベル"""
    BASIC = "basic"           # 基本（stage01-03）
    INTERMEDIATE = "intermediate"  # 中級（stage04-07）
    ADVANCED = "advanced"     # 上級（stage08-10）
    SPECIAL = "special"       # 特殊（stage11-13）


@dataclass
class EnemyEncounterData:
    """敵遭遇データ"""
    enemy_type: str                    # normal, large_2x2, large_3x3, special_2x3
    enemy_id: str                      # 敵のユニークID
    encounter_turn: int                # 遭遇ターン
    encounter_position: Tuple[int, int] # 遭遇位置
    player_position: Tuple[int, int]   # プレイヤー位置
    enemy_hp: int                      # 敵のHP
    enemy_max_hp: int                  # 敵の最大HP
    enemy_mode: str                    # CALM, RAGE, HUNTING, TRANSITIONING
    rage_triggered: bool = False       # 怒り状態が発動したか
    area_attack_used: bool = False     # 範囲攻撃が使用されたか
    defeat_turn: Optional[int] = None  # 撃破ターン（撃破していない場合はNone）
    defeat_method: Optional[str] = None # 撃破方法（attack, special_sequence等）


@dataclass  
class SpecialStageProgress:
    """特殊ステージ進行状況"""
    stage_id: str                      # stage11, stage12, stage13
    learning_objectives: List[str]     # 学習目標リスト
    objectives_achieved: List[bool]    # 各目標の達成状況
    special_mechanics_used: List[str]  # 使用された特殊メカニズム
    error_patterns: List[Dict[str, Any]] # エラーパターンとヒント使用履歴
    condition_sequence_attempts: List[List[str]] = field(default_factory=list) # 条件シーケンス試行履歴
    hint_effectiveness: Dict[str, int] = field(default_factory=dict) # ヒント効果測定


@dataclass
class LearningAnalyticsEntry:
    """v1.2.8学習支援アナリティクスエントリ"""
    # 基本情報（既存のStudentLogEntryを拡張）
    student_log: StudentLogEntry
    
    # v1.2.8固有データ
    learning_phase: LearningPhase
    difficulty_level: DifficultyLevel
    enemy_encounters: List[EnemyEncounterData] = field(default_factory=list)
    special_stage_progress: Optional[SpecialStageProgress] = None
    
    # 学習支援機能使用状況
    see_command_usage: int = 0         # see()コマンド使用回数
    wait_command_usage: int = 0        # wait()コマンド使用回数
    strategic_thinking_indicators: int = 0 # 戦略的思考指標
    
    # パフォーマンス指標
    optimal_path_deviation: float = 0.0    # 最適経路からの逸脱度
    resource_management_score: float = 0.0  # リソース管理スコア
    enemy_ai_understanding: float = 0.0     # 敵AI理解度
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "student_log": {
                "student_id": self.student_log.student_id,
                "session_id": self.student_log.session_id,
                "stage": self.student_log.stage,
                "timestamp": self.student_log.timestamp.isoformat(),
                "level": self.student_log.level,
                "hp": self.student_log.hp,
                "max_hp": self.student_log.max_hp,
                "position": self.student_log.position
            },
            "learning_phase": self.learning_phase.value,
            "difficulty_level": self.difficulty_level.value,
            "enemy_encounters": [
                {
                    "enemy_type": enc.enemy_type,
                    "enemy_id": enc.enemy_id,
                    "encounter_turn": enc.encounter_turn,
                    "encounter_position": enc.encounter_position,
                    "player_position": enc.player_position,
                    "enemy_hp": enc.enemy_hp,
                    "enemy_max_hp": enc.enemy_max_hp,
                    "enemy_mode": enc.enemy_mode,
                    "rage_triggered": enc.rage_triggered,
                    "area_attack_used": enc.area_attack_used,
                    "defeat_turn": enc.defeat_turn,
                    "defeat_method": enc.defeat_method
                }
                for enc in self.enemy_encounters
            ],
            "special_stage_progress": (
                {
                    "stage_id": self.special_stage_progress.stage_id,
                    "learning_objectives": self.special_stage_progress.learning_objectives,
                    "objectives_achieved": self.special_stage_progress.objectives_achieved,
                    "special_mechanics_used": self.special_stage_progress.special_mechanics_used,
                    "error_patterns": self.special_stage_progress.error_patterns,
                    "condition_sequence_attempts": self.special_stage_progress.condition_sequence_attempts,
                    "hint_effectiveness": self.special_stage_progress.hint_effectiveness
                } if self.special_stage_progress else None
            ),
            "see_command_usage": self.see_command_usage,
            "wait_command_usage": self.wait_command_usage,
            "strategic_thinking_indicators": self.strategic_thinking_indicators,
            "optimal_path_deviation": self.optimal_path_deviation,
            "resource_management_score": self.resource_management_score,
            "enemy_ai_understanding": self.enemy_ai_understanding
        }


class LearningAnalytics:
    """v1.2.8学習支援アナリティクスシステム"""
    
    def __init__(self):
        self.current_entry: Optional[LearningAnalyticsEntry] = None
        self.analytics_history: List[LearningAnalyticsEntry] = []
        self.stage_learning_objectives = {
            "stage11": [
                "2x2大型敵のサイズと移動範囲を理解する",
                "怒り状態（HP50%以下）の視覚的変化を観察する", 
                "怒り状態時の範囲攻撃（1マス）を体験する",
                "大型敵との安全な戦闘距離を学ぶ",
                "see()による大型敵の状態確認方法を習得"
            ],
            "stage12": [
                "3x3大型敵の広い占有範囲を理解する",
                "怒り状態時の2マス範囲攻撃を体験する",
                "複数敵との戦闘における優先順位判断を学ぶ",
                "アイテム複数取得による戦力強化戦略",
                "巡回敵と固定敵の違いを活用した戦術"
            ],
            "stage13": [
                "2x3特殊敵の形状と占有範囲を理解する",
                "条件付き戦闘メカニズムを学習する",
                "特定アクション順序による敵撃破方法を習得",
                "複雑な戦略的思考と計画立案能力を養う",
                "最終ステージにふさわしい総合的なスキル統合"
            ]
        }
    
    def start_session(self, student_log: StudentLogEntry) -> LearningAnalyticsEntry:
        """新しい学習セッションを開始"""
        # 学習段階の決定
        learning_phase = self._determine_learning_phase(student_log.stage)
        
        # 難易度レベルの決定
        difficulty_level = self._determine_difficulty_level(student_log.stage)
        
        # 特殊ステージ進行状況の初期化
        special_progress = None
        if student_log.stage in ["stage11", "stage12", "stage13"]:
            objectives = self.stage_learning_objectives.get(student_log.stage, [])
            special_progress = SpecialStageProgress(
                stage_id=student_log.stage,
                learning_objectives=objectives,
                objectives_achieved=[False] * len(objectives),
                special_mechanics_used=[],
                error_patterns=[]
            )
        
        self.current_entry = LearningAnalyticsEntry(
            student_log=student_log,
            learning_phase=learning_phase,
            difficulty_level=difficulty_level,
            special_stage_progress=special_progress
        )
        
        return self.current_entry
    
    def record_enemy_encounter(self, enemy_data: Dict[str, Any], game_state: Any):
        """敵遭遇を記録"""
        if not self.current_entry:
            return
        
        encounter = EnemyEncounterData(
            enemy_type=enemy_data.get("enemy_type", "normal"),
            enemy_id=enemy_data.get("enemy_id", "unknown"),
            encounter_turn=enemy_data.get("turn", 0),
            encounter_position=enemy_data.get("enemy_position", (0, 0)),
            player_position=enemy_data.get("player_position", (0, 0)),
            enemy_hp=enemy_data.get("enemy_hp", 100),
            enemy_max_hp=enemy_data.get("enemy_max_hp", 100),
            enemy_mode=enemy_data.get("enemy_mode", "CALM")
        )
        
        self.current_entry.enemy_encounters.append(encounter)
    
    def record_special_error(self, error_type: str, message: str, hint: str):
        """特殊ステージのエラーとヒントを記録"""
        if not self.current_entry or not self.current_entry.special_stage_progress:
            return
        
        error_pattern = {
            "error_type": error_type,
            "message": message,
            "hint": hint,
            "timestamp": datetime.now().isoformat(),
            "turn": getattr(self.current_entry.student_log, "turn_count", 0)
        }
        
        self.current_entry.special_stage_progress.error_patterns.append(error_pattern)
    
    def record_command_usage(self, command: str):
        """コマンド使用を記録"""
        if not self.current_entry:
            return
        
        if command == "see":
            self.current_entry.see_command_usage += 1
        elif command == "wait":
            self.current_entry.wait_command_usage += 1
    
    def update_objective_achievement(self, objective_index: int, achieved: bool = True):
        """学習目標達成状況を更新"""
        if (not self.current_entry or 
            not self.current_entry.special_stage_progress or
            objective_index >= len(self.current_entry.special_stage_progress.objectives_achieved)):
            return
        
        self.current_entry.special_stage_progress.objectives_achieved[objective_index] = achieved
    
    def calculate_performance_metrics(self):
        """パフォーマンス指標を計算"""
        if not self.current_entry:
            return
        
        # 戦略的思考指標の計算
        self.current_entry.strategic_thinking_indicators = (
            self.current_entry.see_command_usage * 2 +  # 情報収集の重要性
            self.current_entry.wait_command_usage +     # 待機戦略の理解
            len([enc for enc in self.current_entry.enemy_encounters if enc.defeat_method == "strategic"])
        )
        
        # 敵AI理解度の計算
        total_encounters = len(self.current_entry.enemy_encounters)
        if total_encounters > 0:
            successful_defeats = len([enc for enc in self.current_entry.enemy_encounters if enc.defeat_turn is not None])
            self.current_entry.enemy_ai_understanding = successful_defeats / total_encounters
    
    def end_session(self) -> Optional[LearningAnalyticsEntry]:
        """セッションを終了して結果を保存"""
        if not self.current_entry:
            return None
        
        self.calculate_performance_metrics()
        self.analytics_history.append(self.current_entry)
        
        completed_entry = self.current_entry
        self.current_entry = None
        
        return completed_entry
    
    def _determine_learning_phase(self, stage: str) -> LearningPhase:
        """ステージから学習段階を決定"""
        stage_num = int(stage.replace("stage", "").lstrip("0"))
        
        if stage_num <= 3:
            return LearningPhase.EXPLORATION
        elif stage_num <= 7:
            return LearningPhase.UNDERSTANDING
        elif stage_num <= 10:
            return LearningPhase.MASTERY
        else:
            return LearningPhase.CHALLENGE
    
    def _determine_difficulty_level(self, stage: str) -> DifficultyLevel:
        """ステージから難易度レベルを決定"""
        stage_num = int(stage.replace("stage", "").lstrip("0"))
        
        if stage_num <= 3:
            return DifficultyLevel.BASIC
        elif stage_num <= 7:
            return DifficultyLevel.INTERMEDIATE
        elif stage_num <= 10:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.SPECIAL
    
    def get_learning_recommendations(self) -> List[str]:
        """学習推奨事項を生成"""
        if not self.current_entry:
            return []
        
        recommendations = []
        
        # see()コマンドの使用推奨
        if self.current_entry.see_command_usage < 3:
            recommendations.append("see()コマンドをもっと活用して状況を把握しましょう")
        
        # wait()コマンドの戦略的使用推奨
        if self.current_entry.wait_command_usage < 1 and self.current_entry.difficulty_level == DifficultyLevel.SPECIAL:
            recommendations.append("wait()コマンドを使って敵のタイミングを計りましょう")
        
        # 特殊ステージ固有の推奨
        if self.current_entry.special_stage_progress:
            achieved_count = sum(self.current_entry.special_stage_progress.objectives_achieved)
            total_count = len(self.current_entry.special_stage_progress.objectives_achieved)
            
            if achieved_count < total_count / 2:
                recommendations.append("学習目標を意識して段階的に挑戦してみましょう")
        
        return recommendations


# エクスポート用
__all__ = [
    "LearningPhase", "DifficultyLevel", "EnemyEncounterData", 
    "SpecialStageProgress", "LearningAnalyticsEntry", "LearningAnalytics"
]